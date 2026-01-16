"""
PROPERTY LISTING & INVENTORY MANAGEMENT ENGINE
Harshal DXB Marketplace

Handles:
1. Owner/Agent submitting property for listing
2. Verifying property details (no fake listings)
3. Adding to inventory (becomes searchable)
4. Managing property lifecycle (active, sold, inactive)
5. Commission calculation on successful sale/rent
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from boto3.dynamodb.conditions import Attr, Key
from database_manager import AGIDatabaseManager
import logging
import re

logger = logging.getLogger("LISTING_ENGINE")


class PropertyListingEngine:
    """
    OWNER/AGENT PROPERTY SUBMISSION SYSTEM:
    
    When someone says: "Mujhe apni property bechni/rent par deni hai"
    This engine handles the entire flow:
    1. Capture property details
    2. Verify legitimacy
    3. Add to inventory
    4. Make searchable for clients
    5. Track commission on sale
    """

    @staticmethod
    def detect_listing_intent(text):
        """Check if user wants to list/sell their property"""
        listing_keywords = [
            'apni property', 'bechni hai', 'rent par deni', 
            'sell karna hai', 'rental par dena',
            'property sell', 'property rent',
            'list kara', 'post karna', 'property list',
            'mera flat', 'mera apartment', 'mera villa',
            'apna ghar', 'apni property',
            'sell karo', 'rent lo',
            'marketing karo', 'promote karo'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in listing_keywords)

    @staticmethod
    def start_listing_flow(owner_phone, message):
        """
        STEP 1: Owner says "Mujhe apni property rent par deni hai"
        
        Response: Ask for property details in structured way
        """
        logger.info(f"📝 LISTING_FLOW_START: {owner_phone} wants to list property")
        
        # Check if owner is already registered (agent/client)
        owner_profile = AGIDatabaseManager.get_full_intel(owner_phone)
        
        listing_id = f"LIST-{uuid.uuid4().hex[:8].upper()}"
        
        # Store listing session
        listing_session = {
            'pk': listing_id,
            'owner_phone': owner_phone,
            'owner_type': owner_profile.get('type', 'UNKNOWN'),  # AGENT, CLIENT, OWNER
            'status': 'COLLECTING_DETAILS',  # COLLECTING_DETAILS → DETAILS_COMPLETE → VERIFICATION → ACTIVE
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat(),
            'property_details': {},
            'verification_status': 'PENDING',
            'step': 1  # Track which question we're on
        }
        
        try:
            AGIDatabaseManager.T_INVENTORY.put_item(Item=listing_session)
            logger.info(f"✅ Listing session created: {listing_id}")
        except Exception as e:
            logger.error(f"❌ Failed to create listing session: {str(e)}")
            return None
        
        # Return welcome message + first question
        response = f"""🏡 *HARSHAL PROPERTY LISTING*

Bilkul! Hum aapki property ko market mein laayenge! ✨

Kuch details chahiye hongi:

*Question 1/7:* 
Aapke property ke kaunse type hain?
📝 Options:
1️⃣ Apartment/Flat
2️⃣ Villa
3️⃣ Townhouse
4️⃣ Studio
5️⃣ Penthouse
6️⃣ Other

Apna answer dije number se (e.g., "1" for Apartment)

*Listing ID:* {listing_id}
*Time left:* 30 days
"""
        return response

    @staticmethod
    def process_listing_response(owner_phone, response_text):
        """
        STEP 2: Owner answers questions one by one
        
        Question sequence:
        Q1: Property type (Apartment, Villa, etc)
        Q2: Location (Marina, Downtown, etc)
        Q3: Bedrooms (1, 2, 3, etc)
        Q4: Price (for sale or rent)
        Q5: Furnishing (Furnished, Semi, Unfurnished)
        Q6: Amenities (Gym, Pool, Parking, etc)
        Q7: Photos/Documents (URL links)
        """
        
        # Find the active listing session for this owner
        try:
            response = AGIDatabaseManager.T_INVENTORY.query(
                KeyConditionExpression=Key('owner_phone').eq(owner_phone),
                FilterExpression=Attr('status').eq('COLLECTING_DETAILS')
            )
            
            if response['Count'] == 0:
                logger.warning(f"⚠️ No active listing session for {owner_phone}")
                return "❌ Koi active listing nahi. 'Mujhe property bechni hai' likho start karne ke liye."
            
            listing_session = response['Items'][0]
            listing_id = listing_session['pk']
            current_step = listing_session.get('step', 1)
            property_details = listing_session.get('property_details', {})
            
        except Exception as e:
            logger.error(f"❌ Failed to find listing session: {str(e)}")
            return "❌ System error. Please try again."
        
        # Process answer based on current step
        logger.info(f"📋 Processing step {current_step} for {listing_id}")
        
        if current_step == 1:
            # Property type
            property_types = {
                '1': 'APARTMENT',
                '2': 'VILLA',
                '3': 'TOWNHOUSE',
                '4': 'STUDIO',
                '5': 'PENTHOUSE',
                '6': 'OTHER'
            }
            
            property_type = property_types.get(response_text.strip(), None)
            
            if not property_type:
                return "❌ Valid answer nahi. 1-6 se koi ek select karo."
            
            property_details['property_type'] = property_type
            next_question = """*Question 2/7:*
Aapka property kaunse location mein hain?

📍 Popular areas:
1️⃣ Marina
2️⃣ Downtown
3️⃣ Dubai Hills Estate
4️⃣ Business Bay
5️⃣ JBR/JVC
6️⃣ Deira
7️⃣ Other (type area name)

Reply: 1-6 ya area name likho (e.g., "Barsha" ya "7")"""
            
        elif current_step == 2:
            # Location
            location_map = {
                '1': 'MARINA',
                '2': 'DOWNTOWN',
                '3': 'DUBAI_HILLS',
                '4': 'BUSINESS_BAY',
                '5': 'JBR_JVC',
                '6': 'DEIRA'
            }
            
            location = location_map.get(response_text.strip())
            
            if not location:
                # Custom location
                location = response_text.strip().upper()
                if len(location) < 3:
                    return "❌ Valid location likho (min 3 characters)"
            
            property_details['location'] = location
            next_question = """*Question 3/7:*
Aapka property kitne bedroom hain?

📝 Options:
1️⃣ Studio (0 BHK)
2️⃣ 1 Bedroom (1 BHK)
3️⃣ 2 Bedroom (2 BHK)
4️⃣ 3 Bedroom (3 BHK)
5️⃣ 4 Bedroom (4 BHK)
6️⃣ 5+ Bedroom (5+ BHK)

Reply: 1-6 ya exact number"""
            
        elif current_step == 3:
            # Bedrooms
            bed_map = {
                '1': 0,
                '2': 1,
                '3': 2,
                '4': 3,
                '5': 4,
                '6': 5
            }
            
            bedrooms = bed_map.get(response_text.strip())
            
            if bedrooms is None:
                try:
                    bedrooms = int(response_text.strip())
                    if bedrooms < 0 or bedrooms > 10:
                        return "❌ Bedrooms 0-10 ke beech honge"
                except:
                    return "❌ Valid number likho (1-5)"
            
            property_details['bedrooms'] = bedrooms
            next_question = """*Question 4/7:*
Aapka property SALE ke liye hai ya RENT ke liye?

1️⃣ SALE (Bechna hai)
2️⃣ RENTAL (Rent par dena hai)
3️⃣ BOTH (Dono options available)

Reply: 1, 2, ya 3"""
            
        elif current_step == 4:
            # Sale/Rent type
            type_map = {
                '1': 'SALE',
                '2': 'RENTAL',
                '3': 'BOTH'
            }
            
            prop_type = type_map.get(response_text.strip())
            
            if not prop_type:
                return "❌ 1, 2, ya 3 se choose karo"
            
            property_details['availability_type'] = prop_type
            next_question = """*Question 5/7:*
Aapka property ki PRICE kya hai?

📌 Format examples:
▪️ SALE: "2,500,000 AED" ya "2.5M"
▪️ RENT: "5,000 AED per month"
▪️ BOTH: "SALE: 2.5M, RENT: 5000"

Reply: Exact price likho"""
            
        elif current_step == 5:
            # Price
            parsed_price = PropertyListingEngine._parse_price(response_text)
            
            if not parsed_price:
                return "❌ Price properly likho. Example: '2.5M' ya '5000 per month'"
            
            property_details['price'] = parsed_price
            next_question = """*Question 6/7:*
Property ki FURNISHING kaisi hai?

1️⃣ Unfurnished (Khali)
2️⃣ Semi-Furnished (Kuch furniture)
3️⃣ Fully Furnished (Poora furnished)

Reply: 1, 2, ya 3"""
            
        elif current_step == 6:
            # Furnishing
            furnish_map = {
                '1': 'UNFURNISHED',
                '2': 'SEMI_FURNISHED',
                '3': 'FULLY_FURNISHED'
            }
            
            furnishing = furnish_map.get(response_text.strip())
            
            if not furnishing:
                return "❌ 1, 2, ya 3 se choose karo"
            
            property_details['furnishing'] = furnishing
            next_question = """*Question 7/7:*
Kaunse AMENITIES available hain?

📝 Examples:
▪️ Gym, Pool, Parking, Security, Garden, Balcony, etc.

Reply: Amenities likho comma-separated
(Example: "Gym, Pool, Parking, Security")"""
            
        elif current_step == 7:
            # Amenities
            amenities = [a.strip() for a in response_text.split(',')]
            property_details['amenities'] = amenities
            
            # All details collected! Now verify and add to inventory
            return PropertyListingEngine._verify_and_add_listing(
                listing_id, 
                owner_phone, 
                property_details
            )
        
        # Update listing session with new step
        try:
            AGIDatabaseManager.T_INVENTORY.update_item(
                Key={'pk': listing_id},
                UpdateExpression="SET property_details = :pd, #s = :step",
                ExpressionAttributeNames={'#s': 'step'},
                ExpressionAttributeValues={
                    ':pd': property_details,
                    ':step': current_step + 1
                }
            )
            logger.info(f"✅ Updated listing {listing_id} to step {current_step + 1}")
        except Exception as e:
            logger.error(f"❌ Failed to update listing: {str(e)}")
        
        return next_question

    @staticmethod
    def _parse_price(price_text):
        """Parse price from various formats"""
        import re
        
        # Remove spaces and convert to lowercase
        text = price_text.replace(' ', '').lower()
        
        # Try to find AED amount
        # Patterns: 2.5M, 2500000, 2,500,000, 5000/month, etc.
        
        # For sale prices
        sale_match = re.search(r'(\d+\.?\d*)\s*m(?:illion)?', text)
        if sale_match:
            return {
                'type': 'SALE',
                'amount': int(float(sale_match.group(1)) * 1_000_000)
            }
        
        # For monthly rent
        rent_match = re.search(r'(\d+)(?:k)?(?:/|per)\s*(?:month|monthly)', text)
        if rent_match:
            amount = int(rent_match.group(1))
            if 'k' in text[:rent_match.start()]:
                amount *= 1000
            return {
                'type': 'RENTAL',
                'amount': amount,
                'period': 'MONTHLY'
            }
        
        # Try plain number
        plain_match = re.search(r'(\d+)', text.replace(',', ''))
        if plain_match:
            amount = int(plain_match.group(1))
            # If > 100k, assume sale; else rent
            if amount > 100000:
                return {
                    'type': 'SALE',
                    'amount': amount
                }
            else:
                return {
                    'type': 'RENTAL',
                    'amount': amount,
                    'period': 'MONTHLY'
                }
        
        return None

    @staticmethod
    def _verify_and_add_listing(listing_id, owner_phone, property_details):
        """
        VERIFICATION STEP:
        Check for fake/suspicious listings before adding to inventory
        """
        
        logger.info(f"🔍 VERIFYING listing {listing_id}")
        
        # Fake listing detection
        suspicious_factors = []
        
        # Check 1: Price too low/high?
        price_info = property_details.get('price', {})
        if price_info.get('type') == 'SALE':
            amount = price_info.get('amount', 0)
            bedrooms = property_details.get('bedrooms', 0)
            location = property_details.get('location', 'DUBAI')
            
            # Very rough validation: 1BHK should be min 300K
            min_price_per_bhk = {
                'MARINA': 400000,
                'DOWNTOWN': 350000,
                'DUBAI_HILLS': 450000,
                'BUSINESS_BAY': 380000,
                'DEFAULT': 300000
            }
            
            min_expected = min_price_per_bhk.get(location, 300000) * (bedrooms or 1)
            
            if amount < min_expected * 0.5:  # 50% below market
                suspicious_factors.append("Price bahut kam hai (fake ho sakta hai)")
            
            if amount > min_expected * 5:  # 500% above market
                suspicious_factors.append("Price bahut zyada hai")
        
        # Check 2: Owner registered?
        owner_profile = AGIDatabaseManager.get_full_intel(owner_phone)
        if not owner_profile.get('is_verified'):
            suspicious_factors.append("Owner verified nahi hai - manual check needed")
        
        # Verification result
        if len(suspicious_factors) > 0:
            logger.warning(f"⚠️ SUSPICIOUS_LISTING {listing_id}: {suspicious_factors}")
            
            # Flag for manual review
            try:
                AGIDatabaseManager.T_INVENTORY.update_item(
                    Key={'pk': listing_id},
                    UpdateExpression="SET verification_status = :vs, suspicious_flags = :sf",
                    ExpressionAttributeValues={
                        ':vs': 'FLAGGED_FOR_REVIEW',
                        ':sf': suspicious_factors
                    }
                )
            except Exception as e:
                logger.error(f"❌ Failed to flag listing: {str(e)}")
            
            return f"""⚠️ *LISTING FLAGGED FOR REVIEW*

Aapka listing kuch suspicious factors ki wajah se manual review ke liye flag ho gaya hai:

{chr(10).join(['❌ ' + f for f in suspicious_factors])}

Hum jaldi (24 hours) review kar ke approve kar denge.
Admin contact: +971 XX XXX XXXX

Listing ID: {listing_id}"""
        
        # No red flags - add to inventory
        logger.info(f"✅ VERIFIED & ADDING TO INVENTORY: {listing_id}")
        
        inventory_record = {
            'pk': f"INV-{uuid.uuid4().hex[:8].upper()}",
            'listing_id': listing_id,
            'owner_phone': owner_phone,
            'property_type': property_details.get('property_type'),
            'location': property_details.get('location'),
            'bedrooms': property_details.get('bedrooms'),
            'furnishing': property_details.get('furnishing'),
            'amenities': property_details.get('amenities', []),
            'price': property_details.get('price'),
            'availability_type': property_details.get('availability_type'),
            'status': 'ACTIVE',  # ACTIVE, SOLD, RENTED, INACTIVE
            'created_at': datetime.now().isoformat(),
            'verification_status': 'APPROVED',
            'suspicious_flags': []
        }
        
        try:
            AGIDatabaseManager.T_INVENTORY.put_item(Item=inventory_record)
            AGIDatabaseManager.T_INVENTORY.update_item(
                Key={'pk': listing_id},
                UpdateExpression="SET #s = :st, verification_status = :vs",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':st': 'ACTIVE',
                    ':vs': 'APPROVED'
                }
            )
            
            logger.info(f"✅ LISTING ADDED TO INVENTORY: {inventory_record['pk']}")
            
            return f"""✅ *LISTING SUCCESSFULLY ADDED!*

🎉 Aapki property ab LIVE hai!

📍 *Property Details:*
▪️ Type: {property_details.get('property_type')}
▪️ Location: {property_details.get('location')}
▪️ Bedrooms: {property_details.get('bedrooms')} BHK
▪️ Price: {PropertyListingEngine._format_price(property_details.get('price'))}
▪️ Furnishing: {property_details.get('furnishing')}

🌟 *Next Steps:*
1. Clients ab search kar ke aapka property dekh sakta hain
2. Agar koi interested ho to hum directly contact karenge
3. Commission: Agar deal close ho to 60% aapka, 40% Harshal ka

*Listing ID:* {inventory_record['pk']}
*Status:* ACTIVE ✅

Questions? Text "help" karke puchho!"""
            
        except Exception as e:
            logger.error(f"❌ Failed to add listing to inventory: {str(e)}")
            return "❌ Listing add karne mein error aya. Ek dum se retry karo."

    @staticmethod
    def _format_price(price_info):
        """Format price for display"""
        if not price_info:
            return "N/A"
        
        price_type = price_info.get('type')
        amount = price_info.get('amount', 0)
        
        if price_type == 'SALE':
            if amount > 1000000:
                return f"AED {amount / 1000000:.1f}M"
            else:
                return f"AED {amount:,}"
        elif price_type == 'RENTAL':
            return f"AED {amount:,} per month"
        
        return f"AED {amount:,}"


class ListingManagementEngine:
    """
    LIFECYCLE MANAGEMENT:
    - Track which listings are active/sold/rented
    - Calculate commission
    - Update owner's portfolio
    """
    
    @staticmethod
    def mark_property_sold(listing_id, buyer_phone, sale_price, commission_paid):
        """Mark property as sold, calculate commission"""
        
        logger.info(f"💰 MARKING_SOLD: {listing_id} | Price: {sale_price}")
        
        try:
            # Get listing details
            response = AGIDatabaseManager.T_INVENTORY.get_item(Key={'pk': listing_id})
            
            if 'Item' not in response:
                logger.error(f"❌ Listing not found: {listing_id}")
                return False
            
            listing = response['Item']
            owner_phone = listing['owner_phone']
            
            # Update listing status
            AGIDatabaseManager.T_INVENTORY.update_item(
                Key={'pk': listing_id},
                UpdateExpression="SET #s = :status, buyer_phone = :buyer, final_sale_price = :price, closed_at = :now",
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':status': 'SOLD',
                    ':buyer': buyer_phone,
                    ':price': Decimal(str(sale_price)),
                    ':now': datetime.now().isoformat()
                }
            )
            
            # Record commission transaction
            AGIDatabaseManager.T_CLIENTS.update_item(
                Key={'pk': owner_phone},
                UpdateExpression="SET total_commission_earned = if_not_exists(total_commission_earned, :zero) + :commission",
                ExpressionAttributeValues={
                    ':zero': Decimal('0'),
                    ':commission': Decimal(str(commission_paid))
                }
            )
            
            logger.info(f"✅ PROPERTY_SOLD: {listing_id} | Commission: AED {commission_paid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to mark sold: {str(e)}")
            return False

    @staticmethod
    def get_owner_portfolio(owner_phone):
        """Get all listings by owner"""
        try:
            response = AGIDatabaseManager.T_INVENTORY.query(
                KeyConditionExpression=Key('owner_phone').eq(owner_phone)
            )
            
            listings = response.get('Items', [])
            
            # Categorize
            active = [l for l in listings if l.get('status') == 'ACTIVE']
            sold = [l for l in listings if l.get('status') == 'SOLD']
            rented = [l for l in listings if l.get('status') == 'RENTED']
            
            return {
                'total': len(listings),
                'active': len(active),
                'sold': len(sold),
                'rented': len(rented),
                'listings': listings
            }
        except Exception as e:
            logger.error(f"❌ Failed to get portfolio: {str(e)}")
            return None
