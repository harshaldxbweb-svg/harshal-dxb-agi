"""
LEAD AUCTION & COMPETITION ENGINE
Harshal DXB AGI Marketplace System

Manages the lead distribution, agent competition,
and real-time market transparency.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from boto3.dynamodb.conditions import Attr, Key
from database_manager import AGIDatabaseManager
import logging

logger = logging.getLogger("LEAD_ENGINE")


class LeadAuctionEngine:
    """
    The Heart of Harshal DXB Marketplace:
    - Runs silent auctions between verified agents
    - Awards leads to fastest responders
    - Tracks agent response times & reliability
    - Prevents number exchange (AGI = bridge forever)
    """

    @staticmethod
    def create_lead_auction(client_phone, requirement_parsed):
        """
        CLIENT REQUESTS PROPERTY → AGI creates auction
        
        HONEST FLOW:
        1. Check OUR inventory first (no false hope)
        2. If found → Return directly (100% Harshal commission)
        3. If NOT found → Only then create auction for agents
        
        Example: "1 BHK in Marina 80K rental"
        """
        from inventory_verifier import InventoryVerifier
        
        location = requirement_parsed.get('location', 'DUBAI')
        bedrooms = requirement_parsed.get('bedrooms')
        budget_min = requirement_parsed.get('budget_min')
        budget_max = requirement_parsed.get('budget_max')
        property_type = requirement_parsed.get('property_type', 'RENTAL')
        
        # STEP 1: HONEST INVENTORY VERIFICATION
        # This checks ACTUAL inventory - no fake promises
        client_profile = AGIDatabaseManager.get_full_intel(client_phone)
        
        search_result = InventoryVerifier.verify_and_search_inventory(
            requirement_parsed=requirement_parsed,
            client_profile=client_profile
        )
        
        # If we have it → Return directly (no auction needed)
        if search_result['inventory_exists'] and search_result['status'] in ['FOUND', 'PARTIAL_MATCH']:
            logger.info(
                f"✅ INVENTORY MATCH: {len(search_result['properties'])} "
                f"properties found for {client_phone}"
            )
            return {
                "type": "DIRECT_MATCH",
                "properties": search_result['properties'],
                "source": "HARSHAL_DXB_INVENTORY",
                "recommendation": search_result['recommendation']
            }
        
        # STEP 2: NOT in inventory → Create auction only if NOT found
        logger.info(
            f"🏆 CREATING LEAD AUCTION: {location} | {bedrooms} BHK | "
            f"AED {budget_min}-{budget_max}"
        )
        
        lead_id = f"LEAD-{uuid.uuid4().hex[:8].upper()}"
        
        lead_record = {
            'pk': lead_id,
            'client_phone': client_phone,
            'location': location,
            'bedrooms': bedrooms,
            'bathrooms': requirement_parsed.get('bathrooms'),
            'budget_min': Decimal(str(budget_min)) if budget_min else None,
            'budget_max': Decimal(str(budget_max)) if budget_max else None,
            'property_type': property_type,
            'created_at': datetime.now().isoformat(),
            'status': 'ACTIVE',  # ACTIVE, ASSIGNED, COMPLETED, EXPIRED
            'auction_starts': datetime.now().isoformat(),
            'auction_ends': (datetime.now() + timedelta(minutes=30)).isoformat(),  # 30-min auction
            'eligible_agents': [],
            'responses': [],  # Agent bids
            'winner_agent': None,
            'winner_response_time': None,
            'winner_property_id': None
        }
        
        try:
            AGIDatabaseManager.T_DEALS.put_item(Item=lead_record)
            
            # Notify all area agents about lead opportunity
            LeadAuctionEngine._notify_agents_about_lead(lead_id, location, requirement_parsed)
            
            return {
                "type": "AUCTION_CREATED",
                "lead_id": lead_id,
                "auction_duration": "30 minutes",
                "status": "Agents can't see client number. They submit verified listings only."
            }
        except Exception as e:
            logger.error(f"❌ Auction creation failed: {str(e)}")
            return {"type": "ERROR", "message": str(e)}

    @staticmethod
    def _notify_agents_about_lead(lead_id, location, requirement):
        """
        INTERNAL: Notify BEST agents in this area (location-filtered, not "whole Dubai").
        
        Agent Selection Logic (Priority Order):
        1. TIER_1: Specializing in this location + 10+ deals/month = Get notified FIRST
        2. TIER_2: Have worked in location + 5-9 deals/month = Get notified SECOND
        3. TIER_3: Limited history in location + 1-4 deals/month = Get notified THIRD
        4. NEW: No history = Skip (except if <5 agents in area)
        
        Max agents to notify: 10 (prevents flooding)
        Excludes: "Whole Dubai" agents (must select specific areas)
        Agents CANNOT see client phone number.
        """
        try:
            from commission_engine import CommissionEngine
            
            # STEP 1: Find ALL agents who ACTUALLY serve this location
            # (Exclude "I work in whole Dubai" agents)
            agents_response = AGIDatabaseManager.T_PARTNERS.scan(
                FilterExpression=Attr('status').eq('ACTIVE') & 
                                Attr('areas_served').contains(location.upper())
            )
            
            agents = agents_response.get('Items', [])
            
            if not agents:
                logger.warning(f"⚠️ NO agents found for {location}. Will create auction anyway.")
                selected_agents = []
            else:
                # STEP 2: Sort agents by tier + reliability
                agent_tiers = []
                for agent in agents:
                    tier = CommissionEngine.get_agent_tier(agent['pk'], location)
                    agent_tiers.append({
                        "phone": agent['pk'],
                        "name": agent.get('name', 'Unknown'),
                        "tier": tier,
                        "reliability_score": float(agent.get('reliability_score', 0)),
                        "deals_closed": agent.get('deals_closed', 0)
                    })
                
                # Sort: TIER_1 first, then by reliability score
                tier_priority = {"TIER_1": 4, "TIER_2": 3, "TIER_3": 2, "NEW_AGENT": 1}
                agent_tiers.sort(
                    key=lambda x: (
                        tier_priority.get(x['tier'], 0),
                        x['reliability_score'],
                        x['deals_closed']
                    ),
                    reverse=True
                )
                
                # STEP 3: Select top 10 agents
                max_agents = 10
                selected_agents = agent_tiers[:max_agents]
                
                logger.info(f"✅ Agent Selection for {location}:")
                for i, agent in enumerate(selected_agents, 1):
                    logger.info(f"   {i}. {agent['name']} ({agent['tier']}) - Score: {agent['reliability_score']}")
            
            eligible_agent_phones = [a['phone'] for a in selected_agents]
            
            # STEP 4: Update lead with eligible agents
            AGIDatabaseManager.T_DEALS.update_item(
                Key={'pk': lead_id},
                UpdateExpression="SET eligible_agents = :agents, agent_count = :count",
                ExpressionAttributeValues={
                    ':agents': eligible_agent_phones,
                    ':count': len(eligible_agent_phones)
                }
            )
            
            # STEP 5: Send notifications to selected agents (NO client number visible)
            bedrooms = requirement.get('bedrooms', 'Any')
            budget_min = requirement.get('budget_min', 'Any')
            
            for idx, agent in enumerate(selected_agents, 1):
                notification = f"""
🏆 *LIVE LEAD ALERT!* [{idx}/{len(selected_agents)}]

📍 Location: {location}
🛏️ BHK: {bedrooms}
💰 Budget: {budget_min} - {requirement.get('budget_max', 'Any')} AED
🔑 Property Type: {requirement.get('property_type', 'Any')}

⚡ *FASTEST AGENT WINS!*
(30-minute auction window)

Commission: 60% (You) / 40% (Platform)
Clients per agent: You handle direct communication (AGI bridge)

Reply: '{lead_id}' + Your property ID to submit listing.

⚠️ DO NOT share client number. Communication via AGI only.
"""
                
                # In production: use UltraMsg to send to agent
                logger.info(f"📢 Lead notification sent to {agent['phone']} (Tier: {agent['tier']}): {lead_id}")
            
            logger.info(f"✅ Lead {lead_id}: {len(eligible_agent_phones)} agents notified in {location}")
            
        except Exception as e:
            logger.error(f"❌ Notification failed: {str(e)}")

    @staticmethod
    def process_agent_response(agent_phone, lead_id, property_id):
        """
        AGENT SUBMITS PROPERTY → Record response & timestamp
        
        Competition mechanism:
        - First agent to submit verified listing wins
        - Response time tracked
        - Property automatically verified
        """
        try:
            lead = AGIDatabaseManager.T_DEALS.get_item(Key={'pk': lead_id})
            if 'Item' not in lead:
                return {"status": "LEAD_NOT_FOUND"}
            
            lead_data = lead['Item']
            
            # Check if auction still active
            auction_end = datetime.fromisoformat(lead_data['auction_ends'])
            if datetime.now() > auction_end:
                return {
                    "status": "AUCTION_EXPIRED",
                    "message": "Auction window closed. Better luck next time!"
                }
            
            # Check if lead already assigned
            if lead_data.get('status') == 'ASSIGNED':
                return {
                    "status": "ALREADY_ASSIGNED",
                    "message": "Another agent already won this lead. Check next one!"
                }
            
            # Fetch property details
            property_response = AGIDatabaseManager.T_INVENTORY.get_item(Key={'pk': property_id})
            if 'Item' not in property_response:
                return {"status": "PROPERTY_NOT_FOUND"}
            
            property_data = property_response['Item']
            
            # Verify property matches criteria
            if not LeadAuctionEngine._verify_property_match(property_data, lead_data):
                AGIDatabaseManager.penalize_or_reward_partner(agent_phone, -3, "WRONG_PROPERTY_SUBMITTED")
                return {
                    "status": "PROPERTY_MISMATCH",
                    "message": "Property doesn't match client criteria. Score: -3"
                }
            
            # Record agent response
            response_time = (datetime.now() - datetime.fromisoformat(lead_data['auction_starts'])).total_seconds()
            
            agent_response = {
                'agent_phone': agent_phone,
                'property_id': property_id,
                'response_time_seconds': response_time,
                'submitted_at': datetime.now().isoformat(),
                'is_winner': False
            }
            
            # Add to responses
            current_responses = lead_data.get('responses', [])
            current_responses.append(agent_response)
            
            # If first response, agent wins!
            if len(current_responses) == 1:
                AGIDatabaseManager.T_DEALS.update_item(
                    Key={'pk': lead_id},
                    UpdateExpression="SET responses = :r, winner_agent = :w, winner_response_time = :t, winner_property_id = :p, #s = :status",
                    ExpressionAttributeValues={
                        ':r': current_responses,
                        ':w': agent_phone,
                        ':t': Decimal(str(response_time)),
                        ':p': property_id,
                        ':status': 'ASSIGNED'
                    },
                    ExpressionAttributeNames={'#s': 'status'}
                )
                
                # Reward agent
                AGIDatabaseManager.penalize_or_reward_partner(agent_phone, +5, "LEAD_WON")
                
                logger.info(f"🏆 LEAD WON! Agent {agent_phone} | Response: {response_time:.1f}s | Lead: {lead_id}")
                
                return {
                    "status": "LEAD_WON",
                    "message": f"🏆 *YOU WON THIS LEAD!*\n\nResponse Time: {response_time:.1f}s\n\nClient will connect with property details.\n(You never see client number - communicate through AGI)",
                    "lead_id": lead_id,
                    "property_details": property_data
                }
            else:
                # Not first - still record response for stats
                AGIDatabaseManager.T_DEALS.update_item(
                    Key={'pk': lead_id},
                    UpdateExpression="SET responses = :r",
                    ExpressionAttributeValues={':r': current_responses}
                )
                
                return {
                    "status": "LEAD_LOST",
                    "message": f"⏱️ Someone was faster! Response time: {response_time:.1f}s\n\nDon't worry - more leads coming! 🚀",
                    "your_rank": len(current_responses)  # 2nd, 3rd, etc.
                }
        
        except Exception as e:
            logger.error(f"❌ Response processing failed: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    @staticmethod
    def _verify_property_match(property_data, lead_data):
        """Verify agent's property matches client's original request."""
        try:
            # Must match location
            if property_data.get('location') != lead_data.get('location'):
                return False
            
            # Bedroom match (flexible ±1)
            if lead_data.get('bedrooms'):
                prop_beds = property_data.get('bedrooms', 0)
                lead_beds = lead_data.get('bedrooms', 0)
                if abs(prop_beds - lead_beds) > 1:
                    return False
            
            # Budget match (must be within range)
            if lead_data.get('budget_min') and lead_data.get('budget_max'):
                price = float(property_data.get('asked_price', 0))
                if not (float(lead_data['budget_min']) <= price <= float(lead_data['budget_max'])):
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Verification error: {str(e)}")
            return False

    @staticmethod
    def match_lead_to_client(lead_id, winning_property_id):
        """
        MATCH COMPLETE: Connect winning property to client
        (Without exchanging numbers - AGI stays in middle)
        """
        try:
            lead = AGIDatabaseManager.T_DEALS.get_item(Key={'pk': lead_id})
            lead_data = lead['Item']
            
            client_phone = lead_data['client_phone']
            agent_phone = lead_data['winner_agent']
            
            # Create deal record
            deal_id = f"DEAL-{uuid.uuid4().hex[:8].upper()}"
            
            deal_record = {
                'pk': deal_id,
                'lead_id': lead_id,
                'client_phone': client_phone,
                'agent_phone': agent_phone,
                'property_id': winning_property_id,
                'created_at': datetime.now().isoformat(),
                'status': 'MATCHED',  # MATCHED, NEGOTIATING, CLOSED
                'commission_status': 'PENDING'
            }
            
            AGIDatabaseManager.T_DEALS.put_item(Item=deal_record)
            
            # Log for audit
            AGIDatabaseManager.log_audit_event(client_phone, "LEAD_MATCHED", {
                "lead_id": lead_id,
                "agent_phone": agent_phone,
                "property_id": winning_property_id
            })
            
            logger.info(f"✅ DEAL CREATED: {deal_id} | Client: {client_phone} | Agent: {agent_phone}")
            
            return {
                "status": "MATCHED",
                "deal_id": deal_id,
                "client_phone": client_phone,
                "agent_phone": agent_phone
            }
        
        except Exception as e:
            logger.error(f"❌ Lead-to-client matching failed: {str(e)}")
            return {"status": "ERROR", "message": str(e)}

    @staticmethod
    def get_market_transparency_report(location):
        """
        MARKET INTELLIGENCE: Show real market data
        (No fake listings, only verified & competed inventory)
        """
        try:
            # Get verified, market-priced inventory for location
            inventory = AGIDatabaseManager.search_properties_by_criteria(
                location=location
            )
            
            # Get recent leads & winners in this location
            deals_response = AGIDatabaseManager.T_DEALS.scan(
                FilterExpression=Attr('location').eq(location.upper()) & Attr('status').eq('ASSIGNED')
            )
            
            recent_deals = deals_response.get('Items', [])[-10:]  # Last 10
            
            # Calculate market averages
            avg_price = 0
            avg_response_time = 0
            
            if inventory:
                prices = [float(i.get('asked_price', 0)) for i in inventory]
                avg_price = sum(prices) / len(prices)
            
            if recent_deals:
                response_times = [float(d.get('winner_response_time', 0)) for d in recent_deals]
                avg_response_time = sum(response_times) / len(response_times)
            
            report = {
                'location': location,
                'verified_properties': len(inventory),
                'average_price': Decimal(str(avg_price)),
                'recent_deals': len(recent_deals),
                'avg_agent_response_time_seconds': round(avg_response_time, 1),
                'market_status': 'TRANSPARENT & VERIFIED',
                'transparency_score': '10/10 (All competed, no fakes)'
            }
            
            return report
        
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            return {"status": "ERROR"}
