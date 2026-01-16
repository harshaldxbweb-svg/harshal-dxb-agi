"""
INVENTORY VERIFIER & SMART CONTEXT ENGINE
Harshal DXB - Honest Inventory Matching System

Rules:
1. NO FAKE PROMISES - Only show properties that actually exist in inventory
2. NO DUPLICATE QUESTIONS - Use existing client profile data
3. SMART CONTEXT - Remember what client already told us
4. HONEST RESPONSES - If we don't have it, say so directly
"""

import logging
from decimal import Decimal
from datetime import datetime
from database_manager import AGIDatabaseManager

logger = logging.getLogger("INVENTORY_VERIFIER")


class InventoryVerifier:
    """
    TRUTH KEEPER: Ensures we never promise fake properties or false hope.
    Only respond with properties that actually exist in our inventory.
    """

    @staticmethod
    def verify_and_search_inventory(requirement_parsed, client_profile):
        """
        HONEST SEARCH:
        1. Check if property exists in OUR inventory (Harshal's own listings)
        2. If found → Return directly (no auction needed, 100% Harshal commission)
        3. If NOT found → Return "NOT_IN_INVENTORY" + prepare for auction

        Args:
            requirement_parsed: {
                'bedrooms': 2,
                'location': 'MARINA',
                'budget_min': 80000,
                'budget_max': 120000,
                'property_type': 'RENTAL'
            }
            client_profile: Full client history from database

        Returns:
            {
                'status': 'FOUND' | 'NOT_FOUND' | 'PARTIAL_MATCH',
                'properties': [...],  # If FOUND
                'inventory_exists': True/False,
                'recommendation': str,
                'next_action': 'DIRECT_MATCH' | 'CREATE_AUCTION' | 'REFINE_CRITERIA'
            }
        """

        location = requirement_parsed.get('location', 'DUBAI')
        bedrooms = requirement_parsed.get('bedrooms')
        bathrooms = requirement_parsed.get('bathrooms')
        budget_min = requirement_parsed.get('budget_min')
        budget_max = requirement_parsed.get('budget_max')
        property_type = requirement_parsed.get('property_type', 'RENTAL')

        logger.info(
            f"🔍 INVENTORY SEARCH: {location} | {bedrooms}BHK | "
            f"{property_type} | AED {budget_min}-{budget_max}"
        )

        # STEP 1: Exact match search in OUR inventory
        exact_matches = InventoryVerifier._search_exact_match(
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            location=location,
            budget_min=budget_min,
            budget_max=budget_max,
            property_type=property_type
        )

        if exact_matches:
            logger.info(f"✅ FOUND {len(exact_matches)} properties in OUR inventory")
            return {
                'status': 'FOUND',
                'inventory_exists': True,
                'properties': exact_matches,
                'count': len(exact_matches),
                'next_action': 'DIRECT_MATCH',
                'recommendation': f"✅ Great news! We have {len(exact_matches)} verified options for you in {location}.",
                'source': 'HARSHAL_INVENTORY'
            }

        # STEP 2: Partial match (close to criteria)
        partial_matches = InventoryVerifier._search_partial_match(
            bedrooms=bedrooms,
            location=location,
            budget_range=(budget_min, budget_max),
            property_type=property_type
        )

        if partial_matches:
            logger.info(f"⚠️ PARTIAL: Found {len(partial_matches)} close matches")
            return {
                'status': 'PARTIAL_MATCH',
                'inventory_exists': True,
                'properties': partial_matches,
                'count': len(partial_matches),
                'next_action': 'SHOW_CLOSE_MATCHES',
                'recommendation': f"We found {len(partial_matches)} similar properties. Want to see them?",
                'source': 'HARSHAL_INVENTORY'
            }

        # STEP 3: NOT in our inventory - will create auction
        logger.info(f"❌ NOT IN INVENTORY: Will create auction for local agents")
        return {
            'status': 'NOT_FOUND',
            'inventory_exists': False,
            'properties': [],
            'count': 0,
            'next_action': 'CREATE_AUCTION',
            'recommendation': f"We don't have this exact property right now, but our local {location} agents do! Let me connect you with verified agents.",
            'source': 'AUCTION_REQUIRED'
        }

    @staticmethod
    def _search_exact_match(bedrooms, bathrooms, location, budget_min, budget_max, property_type):
        """
        Exact match: Check our inventory table for properties that fit criteria EXACTLY
        """
        try:
            response = AGIDatabaseManager.T_INVENTORY.query(
                KeyConditionExpression='location = :loc',
                FilterExpression=(
                    Attr('bedrooms').eq(bedrooms) &
                    Attr('property_type').eq(property_type) &
                    Attr('price').between(
                        Decimal(str(budget_min)) if budget_min else 0,
                        Decimal(str(budget_max)) if budget_max else Decimal('999999999')
                    ) &
                    Attr('is_active').eq(True) &
                    Attr('is_harshal_owned').eq(True)
                ),
                ExpressionAttributeValues={':loc': location}
            )

            properties = response.get('Items', [])
            logger.info(f"✅ Exact match query returned {len(properties)} properties")
            return properties

        except Exception as e:
            logger.error(f"❌ Exact match search failed: {str(e)}")
            return []

    @staticmethod
    def _search_partial_match(bedrooms, location, budget_range, property_type):
        """
        Partial match: Look for properties close to criteria
        (e.g., 2 BHK instead of 3 BHK, slightly higher price)
        """
        try:
            # Flexible matching: ±1 bedroom, ±20% price tolerance
            bedroom_variants = [bedrooms - 1, bedrooms, bedrooms + 1]
            budget_min, budget_max = budget_range
            price_tolerance = Decimal(str(budget_max * 0.2))

            response = AGIDatabaseManager.T_INVENTORY.query(
                KeyConditionExpression='location = :loc',
                FilterExpression=(
                    Attr('bedrooms').is_in(bedroom_variants) &
                    Attr('property_type').eq(property_type) &
                    Attr('price').between(
                        Decimal(str(budget_min - price_tolerance)) if budget_min else 0,
                        Decimal(str(budget_max + price_tolerance))
                    ) &
                    Attr('is_active').eq(True) &
                    Attr('is_harshal_owned').eq(True)
                ),
                ExpressionAttributeValues={':loc': location}
            )

            properties = response.get('Items', [])
            logger.info(f"⚠️ Partial match query returned {len(properties)} close properties")
            return properties

        except Exception as e:
            logger.error(f"⚠️ Partial match search failed: {str(e)}")
            return []


class SmartContextEngine:
    """
    MEMORY KEEPER: Tracks what client already told us.
    Never ask the same question twice. Use existing context.
    """

    @staticmethod
    def get_client_context_stack(client_phone):
        """
        Retrieve what the client has already told us in previous conversations.
        
        Returns:
            {
                'bedrooms': 2,
                'location': ['MARINA', 'JVC'],
                'budget': {'min': 80000, 'max': 120000},
                'timeline': '3 months',
                'property_type': 'RENTAL',
                'already_provided': [list of questions answered],
                'skip_questions': [list of questions to NOT ask]
            }
        """
        try:
            client_data = AGIDatabaseManager.get_full_intel(client_phone)

            # Build context stack from existing profile
            context_stack = client_data.get('context_stack', [])
            profile = client_data.get('profile', {})

            return {
                'bedrooms': profile.get('preferred_bedrooms'),
                'location': profile.get('preferred_locations', []),
                'budget': {
                    'min': profile.get('budget_min'),
                    'max': profile.get('budget_max')
                },
                'timeline': profile.get('timeline'),
                'property_type': profile.get('property_type', 'RENTAL'),
                'nationality': profile.get('nationality'),
                'already_provided': context_stack,
                'skip_questions': SmartContextEngine._determine_skip_questions(profile)
            }

        except Exception as e:
            logger.error(f"❌ Context retrieval failed: {str(e)}")
            return {}

    @staticmethod
    def _determine_skip_questions(profile):
        """
        Based on profile data, determine which questions we already have answers for.
        Don't ask these again!
        """
        skip = []

        if profile.get('preferred_bedrooms'):
            skip.append("BEDROOMS_QUESTION")  # "1 BHK, 2 BHK, 3 BHK?"

        if profile.get('preferred_locations'):
            skip.append("LOCATION_QUESTION")  # "Which area?"

        if profile.get('budget_min') and profile.get('budget_max'):
            skip.append("BUDGET_QUESTION")  # "What's your budget?"

        if profile.get('timeline'):
            skip.append("TIMELINE_QUESTION")  # "How soon?"

        if profile.get('property_type'):
            skip.append("RENT_OR_BUY_QUESTION")  # "Rental or buy?"

        return skip

    @staticmethod
    def should_ask_question(client_phone, question_type):
        """
        Intelligent check: Should we ask this question?
        
        Returns:
            {
                'should_ask': True/False,
                'reason': 'Already knows this' | 'New info needed' | 'Update needed',
                'existing_value': value if already known
            }
        """
        context = SmartContextEngine.get_client_context_stack(client_phone)

        # Question types and their check logic
        checks = {
            'BEDROOMS_QUESTION': {
                'has_value': bool(context.get('bedrooms')),
                'existing': context.get('bedrooms')
            },
            'LOCATION_QUESTION': {
                'has_value': bool(context.get('location')),
                'existing': context.get('location')
            },
            'BUDGET_QUESTION': {
                'has_value': bool(context.get('budget', {}).get('min')),
                'existing': context.get('budget')
            },
            'TIMELINE_QUESTION': {
                'has_value': bool(context.get('timeline')),
                'existing': context.get('timeline')
            },
            'RENT_OR_BUY_QUESTION': {
                'has_value': bool(context.get('property_type')),
                'existing': context.get('property_type')
            }
        }

        check = checks.get(question_type, {'has_value': False, 'existing': None})

        return {
            'should_ask': not check['has_value'],
            'reason': 'Already answered' if check['has_value'] else 'New question needed',
            'existing_value': check['existing'] if check['has_value'] else None
        }

    @staticmethod
    def build_smart_response_prefix(client_phone):
        """
        Build a personalized response intro that shows we remember them.
        
        Example:
        "Priya, looking for 2 BHK in Marina within 100K? Let me find verified options..."
        """
        context = SmartContextEngine.get_client_context_stack(client_phone)
        client_data = AGIDatabaseManager.get_full_intel(client_phone)

        name = client_data.get('profile', {}).get('first_name', 'Friend')
        bedrooms = context.get('bedrooms', 'any')
        location = context.get('location', ['any area'])
        budget = context.get('budget', {})

        if isinstance(location, list) and location:
            location_text = location[0] if len(location) == 1 else f"{location[0]} & others"
        else:
            location_text = 'any area'

        budget_text = ''
        if budget.get('min') and budget.get('max'):
            budget_text = f"within AED {budget['min']:,.0f}-{budget['max']:,.0f}"
        elif budget.get('max'):
            budget_text = f"up to AED {budget['max']:,.0f}"

        # Build personalized greeting
        prefix = f"{name}, looking for {bedrooms} BHK in {location_text}"
        if budget_text:
            prefix += f" {budget_text}"
        prefix += "? "

        return prefix

    @staticmethod
    def store_context_update(client_phone, update_dict):
        """
        When client provides new info, store it immediately.
        Next time we won't ask about this.
        """
        try:
            client_data = AGIDatabaseManager.get_full_intel(client_phone)
            profile = client_data.get('profile', {})

            # Update profile with new data
            profile.update(update_dict)

            # Update in database
            AGIDatabaseManager.T_CLIENTS.update_item(
                Key={'pk': client_phone},
                UpdateExpression='SET #profile = :profile, updated_at = :now',
                ExpressionAttributeNames={'#profile': 'profile'},
                ExpressionAttributeValues={
                    ':profile': profile,
                    ':now': datetime.now().isoformat()
                }
            )

            logger.info(f"✅ Context updated for {client_phone}: {list(update_dict.keys())}")
            return True

        except Exception as e:
            logger.error(f"❌ Context store failed: {str(e)}")
            return False


class HonestResponseBuilder:
    """
    Build HONEST responses: No false promises, just truth.
    """

    @staticmethod
    def build_search_response(client_phone, requirement_parsed, search_result):
        """
        Build response based on what we actually found.
        
        Args:
            search_result: Output from InventoryVerifier.verify_and_search_inventory()
        
        Returns:
            {
                'response_text': str,
                'has_matches': bool,
                'next_action': str,
                'properties': list
            }
        """

        status = search_result.get('status')
        recommendation = search_result.get('recommendation')
        count = search_result.get('count', 0)
        properties = search_result.get('properties', [])
        source = search_result.get('source')

        # Get personalized prefix with existing context
        prefix = SmartContextEngine.build_smart_response_prefix(client_phone)

        if status == 'FOUND':
            # ✅ WE HAVE IT - Show properties directly
            response = f"{prefix}\n\n✅ {recommendation}\n\n"

            # Show first 3 properties
            for idx, prop in enumerate(properties[:3], 1):
                prop_desc = HonestResponseBuilder._format_property_brief(prop)
                response += f"{idx}. {prop_desc}\n"

            response += "\n📍 Which one interests you?"

            return {
                'response_text': response,
                'has_matches': True,
                'next_action': 'SHOW_PROPERTIES',
                'properties': properties[:3]
            }

        elif status == 'PARTIAL_MATCH':
            # ⚠️ CLOSE OPTIONS - Show near-matches
            response = f"{prefix}\n\n"
            response += f"🤔 {recommendation}\n\n"
            response += f"Here are {count} similar options:\n"

            for idx, prop in enumerate(properties[:3], 1):
                prop_desc = HonestResponseBuilder._format_property_brief(prop)
                response += f"{idx}. {prop_desc}\n"

            response += "\n Would one of these work?"

            return {
                'response_text': response,
                'has_matches': True,
                'next_action': 'SHOW_CLOSE_MATCHES',
                'properties': properties[:3]
            }

        else:
            # ❌ NOT IN INVENTORY - Create auction
            response = f"{prefix}\n\n"
            response += f"🔍 {recommendation}\n\n"
            response += (
                "I'm connecting you with the best verified agents in {location} "
                "right now. They'll send you verified listings within 5 minutes.\n\n"
                "No middleman, no fake properties - just honest deals! ✅"
            ).format(location=requirement_parsed.get('location', 'the area'))

            return {
                'response_text': response,
                'has_matches': False,
                'next_action': 'CREATE_AUCTION',
                'properties': []
            }

    @staticmethod
    def _format_property_brief(property_item):
        """Format property info concisely for response"""
        try:
            beds = property_item.get('bedrooms', '?')
            baths = property_item.get('bathrooms', '?')
            price = property_item.get('price', '?')
            area = property_item.get('location', '?')
            name = property_item.get('project_name', 'Project')

            return (
                f"{name}: {beds}BHK/{baths}Bath | "
                f"AED {price:,.0f} | {area}"
            )
        except:
            return "Property details available"
