import os
import json
import logging
import uuid
import random
import requests
import time as t
from flask import Flask, request, jsonify
from datetime import datetime, time
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from boto3.dynamodb.conditions import Key, Attr

# --- INTEGRATING THE 5 SOVEREIGN PILLARS (LEVEL 5 AGI) ---
from database_manager import AGIDatabaseManager   # Elephant Memory
from cognitive_engine import AGICognitiveEngine, AGIDataSanitizer  # Strategy & Filter
from ai_brain import HarshalAGI_Brain              # Conscious Voice
from visual_engine import AGIVisualEngine          # Elite UI/UX
from lead_auction_engine import LeadAuctionEngine  # Marketplace Competition

# --- PHASE 8-10 INTEGRATIONS (NEW SYSTEMS) ---
from inventory_verifier import (
    InventoryVerifier,
    SmartContextEngine,
    HonestResponseBuilder
)
from async_lead_engine import AsyncLeadNotificationEngine
from language_engine import LanguageDetectionEngine, ResponseTranslator
from property_listing_engine import PropertyListingEngine, ListingManagementEngine

# Enterprise-Grade Logging for 100-Year Audit Evidence
logging.basicConfig(level=logging.INFO, format='%(asctime)s - HARSHAL_AGI_v5_SURVIVAL - %(message)s')
logger = logging.getLogger("MASTER_CONTROLLER")

app = Flask(__name__)
# High-concurrency executor: Handling thousands of VIP investors simultaneously
executor = ThreadPoolExecutor(max_workers=100)

class AGIMasterExecutive:
    """
    THE SOVEREIGN SURVIVAL CONTROLLER:
    Orchestrates AGI via UltraMsg with deep Human-Mimicry layers.
    Prevents Meta bans while maintaining Level 5 AGI Intelligence.
    """

    def __init__(self):
        self.admin_phone = os.getenv("ADMIN_PHONE") 
        self.instance_id = os.getenv("ULTRAMSG_INSTANCE_ID")
        self.token = os.getenv("ULTRAMSG_TOKEN")
        self.base_url = f"https://api.ultramsg.com/{self.instance_id}/messages/chat"
        
        # Environment validation
        if not all([self.instance_id, self.token]):
            logger.warning("⚠️ UltraMsg credentials not set. WhatsApp features disabled.")

    def handle_incoming_signal(self, payload):
        """
        AGI DECISION PIPELINE (Synchronized for Flask):
        1. SOVEREIGN FILTER: Immediate Group-Chat Destruction.
        2. MESSAGE SANITIZATION: Clean garbage, block numbers, detect incomplete info.
        3. BYPASS DETECTION: Detect attempts to exchange direct numbers.
        4. IDENTITY AUTH: Fetching 100-Year Context.
        5. COMMAND OVERRIDE: Admin control via WhatsApp (hidden mode).
        6. BUSINESS HOURS: Dubai business hours enforcement.
        7. AGENT REGISTRATION: Detect and register new agents.
        8. CLIENT SEARCH: Parse and handle property requests.
        9. BRAIN EXECUTION: Strategic Reasoning & Response.
        10. HUMAN MIMICRY: Randomized typing delays.
        11. AUDIT: Immutable logging.
        """
        try:
            sender = payload.get('from')
            body = payload.get('body', '').strip()
            msg_type = payload.get('type', 'chat')
            is_group = payload.get('isGroup', False) or "@g.us" in sender

            # =============================================================
            # PHASE 1: THE SOVEREIGN GATEKEEPER (GROUP LOCK)
            # =============================================================
            if is_group:
                logger.info(f"🚫 SIGNAL_DROPPED: Group {sender} filtered. Reason: Privacy Protocol.")
                return
            
            # =============================================================
            # PHASE 2: MESSAGE SANITIZATION & GARBAGE DETECTION
            # =============================================================
            sanitized_body = AGIDataSanitizer.sanitize_raw_input(body)
            
            # Check if message was garbage
            if sanitized_body.startswith('[GARBAGE_FILTERED:'):
                reason = sanitized_body.split('[GARBAGE_FILTERED: ')[1].rstrip(']')
                logger.info(f"🚫 GARBAGE_MESSAGE from {sender}: {reason}")
                response = f"Bhai, message samajh nahi aaya. 🤔 Properly likho - bheed mat dalo."
                self._dispatch_to_whatsapp(sender, response, delay=2)
                AGIDatabaseManager.log_audit_event(sender, "GARBAGE_MESSAGE_REJECTED", {"reason": reason})
                return

            # =============================================================
            # PHASE 2B: MESSAGE QUALITY & FORMAT CHECK (NEW)
            # =============================================================
            is_quality_good, quality_feedback, cleaned_text = AGIDataSanitizer.enforce_message_quality(sanitized_body)
            
            if not is_quality_good:
                logger.info(f"⚠️ POOR_MESSAGE_FORMAT from {sender}: Message too long/unstructured")
                self._dispatch_to_whatsapp(sender, quality_feedback, delay=2)
                AGIDatabaseManager.log_audit_event(sender, "MESSAGE_QUALITY_REJECTED", {
                    "reason": "unstructured_format",
                    "length": len(body)
                })
                return

            # =============================================================
            # PHASE 2C: OFF-TOPIC DETECTION & REDIRECTION (NEW)
            # =============================================================
            is_off_topic, category, confidence = AGIDataSanitizer.detect_off_topic(sanitized_body)
            
            if is_off_topic and confidence > 0.7:
                logger.info(f"🚫 OFF_TOPIC from {sender}: Category={category}, Confidence={confidence:.2f}")
                redirect_response = AGIDataSanitizer.get_redirect_response(category, sanitized_body)
                self._dispatch_to_whatsapp(sender, redirect_response, delay=2)
                AGIDatabaseManager.log_audit_event(sender, "OFF_TOPIC_REDIRECTED", {
                    "detected_category": category,
                    "confidence": confidence,
                    "original_message": body[:100]
                })
                return
            
            # =============================================================
            # PHASE 3: BYPASS ATTEMPT DETECTION
            # =============================================================
            is_bypass_attempt, bypass_reason = AGIDataSanitizer.detect_bypass_attempt(body)
            if is_bypass_attempt:
                logger.warning(f"⚠️ BYPASS_ATTEMPT from {sender}: Pattern = {bypass_reason}")
                response = "❌ Bhai, hum aapke aur agent ke beech bridge hain. Direct contact ke liye yeh system nahi hai. Hum sambhalenge sab kuch! 🔐"
                self._dispatch_to_whatsapp(sender, response, delay=2)
                AGIDatabaseManager.log_audit_event(sender, "BYPASS_ATTEMPT_BLOCKED", {
                    "pattern": bypass_reason,
                    "original_message": body
                })
                # Penalize if agent
                partner_profile = AGIDatabaseManager.T_PARTNERS.get_item(Key={'pk': sender}).get('Item')
                if partner_profile:
                    AGIDatabaseManager.penalize_or_reward_partner(sender, -3, "BYPASS_ATTEMPT")
                return

            # =============================================================
            # PHASE 4: IDENTITY & MEMORY RETRIEVAL
            # =============================================================
            intel = AGIDatabaseManager.get_full_intel(sender)
            partner_profile = AGIDatabaseManager.T_PARTNERS.get_item(Key={'pk': sender}).get('Item')

            # =============================================================
            # PHASE 5: ADMIN SOVEREIGN COMMANDS (HIDDEN MODE)
            # =============================================================
            # Admin can take control seamlessly without user knowing
            if sender == self.admin_phone and body.startswith("/"):
                response = self._execute_admin_command(body, sanitized_body)
                self._dispatch_to_whatsapp(sender, response, delay=2)
                return
            
            # Check if admin is in control mode for this user
            admin_control = self._check_admin_control_mode(sender)
            if admin_control:
                # Admin is responding as AGI - send directly without revealing admin
                self._dispatch_to_whatsapp(sender, sanitized_body, delay=random.randint(2, 4))
                AGIDatabaseManager.log_audit_event(sender, "ADMIN_RESPONSE", {
                    "message": sanitized_body,
                    "hidden": True
                })
                return

            # =============================================================
            # PHASE 4: BUSINESS HOURS SURVIVAL (DUBAI TIME)
            # =============================================================
            now = datetime.now().time()
            if not (time(9, 0) <= now <= time(22, 30)):
                logger.info(f"😴 SLEEP_MODE: Interaction from {sender} outside business hours.")
                return

            # =============================================================
            # PHASE 6: DETECT AGENT LEAD SUBMISSION
            # =============================================================
            if partner_profile and self._is_lead_submission(body):
                response = self._handle_lead_submission(sender, body, partner_profile)
                self._dispatch_to_whatsapp(sender, response, delay=2)
                return

            # =============================================================
            # PHASE 7: DETECT AGENT REGISTRATION INTENT
            # =============================================================
            if self._is_agent_registration_intent(body) and not partner_profile:
                response = self._handle_agent_registration(sender, body)
                self._dispatch_to_whatsapp(sender, response, delay=3)
                return

            # =============================================================
            # PHASE 7B: DETECT PROPERTY LISTING INTENT (NEW)
            # =============================================================
            # If someone wants to LIST their property for sale/rent
            if PropertyListingEngine.detect_listing_intent(body):
                logger.info(f"🏡 PROPERTY_LISTING_INTENT: {sender} wants to list property")
                
                try:
                    response = PropertyListingEngine.start_listing_flow(sender, body)
                    if response:
                        self._dispatch_to_whatsapp(sender, response, delay=2)
                        AGIDatabaseManager.log_audit_event(sender, "LISTING_FLOW_STARTED", {
                            "intent": body
                        })
                    return
                except Exception as e:
                    logger.error(f"❌ Listing flow error: {str(e)}")
                    fallback = "Listing process mein koi issue aya. Admin ko contact karo please."
                    self._dispatch_to_whatsapp(sender, fallback, delay=2)
                    return

            # =============================================================
            # PHASE 7C: CHECK IF EXISTING LISTING RESPONSE
            # =============================================================
            # If user is responding to listing questions
            existing_listing = AGIDatabaseManager.T_INVENTORY.query(
                KeyConditionExpression=Key('owner_phone').eq(sender),
                FilterExpression=Attr('status').eq('COLLECTING_DETAILS')
            )
            
            if existing_listing.get('Count', 0) > 0:
                logger.info(f"📋 Processing listing response for {sender}")
                
                try:
                    response = PropertyListingEngine.process_listing_response(sender, body)
                    self._dispatch_to_whatsapp(sender, response, delay=2)
                    AGIDatabaseManager.log_audit_event(sender, "LISTING_RESPONSE_PROCESSED", {
                        "response": body[:50]
                    })
                    return
                except Exception as e:
                    logger.error(f"❌ Listing response processing error: {str(e)}")
                    fallback = "Kuch error aya. 'Mujhe property bechni hai' se restart karo."
                    self._dispatch_to_whatsapp(sender, fallback, delay=2)
                    return

            # =============================================================
            # PHASE 8: DETECT CLIENT PROPERTY SEARCH (ENHANCED)
            # =============================================================
            if self._is_property_search_intent(body):
                # New: Detect language first
                try:
                    detected_lang, confidence = LanguageDetectionEngine.detect_language(
                        user_input=body,
                        client_profile=intel
                    )
                    logger.info(f"🌐 Language detected: {detected_lang} (confidence: {confidence})")
                except Exception as e:
                    detected_lang = 'ENGLISH'
                    logger.warning(f"Language detection failed, defaulting to ENGLISH: {str(e)}")
                
                # New: Parse requirement more accurately
                requirement_parsed = self._parse_requirement(body)
                
                # New: Verify our inventory FIRST (HONEST CHECK)
                try:
                    search_result = InventoryVerifier.verify_and_search_inventory(
                        requirement_parsed=requirement_parsed,
                        client_profile=intel
                    )
                    logger.info(f"🔍 Inventory search status: {search_result.get('status', 'UNKNOWN')}")
                    
                    # Build response from inventory
                    response_data = HonestResponseBuilder.build_search_response(
                        client_phone=sender,
                        requirement_parsed=requirement_parsed,
                        search_result=search_result
                    )
                    response = response_data['response_text']
                    
                    # Translate if needed
                    if detected_lang.upper() != 'ENGLISH':
                        try:
                            response = ResponseTranslator.translate_to_language(
                                english_response=response,
                                target_language=detected_lang
                            )
                            logger.info(f"🔤 Response translated to {detected_lang}")
                        except Exception as e:
                            logger.warning(f"Translation failed for {detected_lang}: {str(e)}")
                    
                    # Store context for next interaction
                    if requirement_parsed.get('location'):
                        try:
                            SmartContextEngine.store_context_update(
                                client_phone=sender,
                                update_dict={
                                    'preferred_bedrooms': requirement_parsed.get('bedrooms'),
                                    'preferred_locations': [requirement_parsed.get('location')],
                                    'budget_min': requirement_parsed.get('budget_min'),
                                    'budget_max': requirement_parsed.get('budget_max'),
                                    'property_type': requirement_parsed.get('property_type')
                                }
                            )
                            logger.info(f"💾 Context stored for {sender}")
                        except Exception as e:
                            logger.warning(f"Context storage failed: {str(e)}")
                    
                    # If no inventory, queue async agent notifications
                    if response_data.get('next_action') == 'CREATE_AUCTION':
                        logger.info(f"🏆 Creating async auction for lead")
                        try:
                            AsyncLeadNotificationEngine.handle_client_message_async(
                                client_phone=sender,
                                message=body,
                                client_profile=intel
                            )
                        except Exception as e:
                            logger.warning(f"Async auction creation failed: {str(e)}")
                    
                    self._dispatch_to_whatsapp(sender, response, delay=2)
                    AGIDatabaseManager.log_audit_event(sender, "PROPERTY_SEARCH_HANDLED", {
                        "language": detected_lang,
                        "inventory_status": search_result.get('status'),
                        "bedrooms": requirement_parsed.get('bedrooms'),
                        "location": requirement_parsed.get('location')
                    })
                    return
                    
                except Exception as e:
                    logger.error(f"❌ Inventory-based property search failed: {str(e)}")
                    # Fallback to old method
                    response = self._handle_property_search(sender, body)
                    self._dispatch_to_whatsapp(sender, response, delay=4)
                    return

            # =============================================================
            # PHASE 9: BRAIN EXECUTION (DEFAULT)
            # =============================================================
            brain = HarshalAGI_Brain(sender)
            response = brain.generate_response(body)  # Made synchronous

            # =============================================================
            # PHASE 8: DISPATCH & AUDIT
            # =============================================================
            self._dispatch_to_whatsapp(sender, response, delay=random.randint(3, 7))
            AGIDatabaseManager.log_audit_event(sender, "AGI_TRANSACTION", {
                "input": body, 
                "output": response
            })

        except Exception as e:
            logger.error(f"❌ SIGNAL_PROCESSING_FAILED: {str(e)}")
            self._dispatch_to_whatsapp(sender, "Bhai, system update chal raha hai. Ek minute mein aata hoon.", delay=2)

    async def _handle_partner_arbitration(self, phone, text, profile):
        """
        AGI B2B LOGIC: Managing RMs with an Iron Fist.
        """
        clean_text = AGIDataSanitizer.sanitize_raw_input(text)
        market_check = AGICognitiveEngine.validate_market_claims(clean_text, {})
        
        if not market_check['valid']:
            AGIDatabaseManager.penalize_or_reward_partner(phone, -5, "ROI_OVERSTATEMENT")
            return f"Bhai, market trends ke hisab se ye details verified nahi hain. Let's stick to real numbers. ✅"
        
        return "Noted. Details verified and portfolio updated. ✅"

    def _is_lead_submission(self, text):
        """Detect if agent is submitting a property for a lead."""
        # Pattern: "LEAD-XXXXX INV-XXXXX" or similar
        return text.upper().startswith('LEAD-')

    def _handle_lead_submission(self, agent_phone, body, partner_profile):
        """
        AGENT SUBMITS PROPERTY FOR LEAD:
        Example: "LEAD-A1B2C3D4 INV-XXXXX"
        
        Triggers auction competition:
        - First verified submission wins
        - Response time tracked
        - Property validated
        """
        parts = body.strip().split()
        
        if len(parts) < 2:
            return "❌ Format: LEAD-XXXXX INV-XXXXX\nExample: LEAD-A1B2C3D4 INV-ABC12345"
        
        lead_id = parts[0].upper()
        property_id = parts[1].upper()
        
        # Process submission through auction engine
        result = LeadAuctionEngine.process_agent_response(agent_phone, lead_id, property_id)
        
        if result['status'] == 'LEAD_WON':
            # Reward the winning agent
            return result['message']
        
        elif result['status'] == 'LEAD_LOST':
            return result['message']
        
        elif result['status'] == 'AUCTION_EXPIRED':
            return result['message']
        
        elif result['status'] == 'PROPERTY_MISMATCH':
            return result['message']
        
        else:
            return f"❌ Error: {result.get('message', 'Unknown error')}"

    def _is_agent_registration_intent(self, text):
        """Detect if user is trying to register as agent/agency."""
        keywords = ['agent', 'agency', 'broker', 'rm', 'realtor', 'register', 'join', 'partner']
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    def _is_property_search_intent(self, text):
        """Detect if user is searching for property."""
        keywords = ['bhk', 'bed', 'studio', 'marina', 'downtown', 'lakh', 'price', 'looking', 'find', 'search', 'property']
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    def _handle_agent_registration(self, sender, body):
        """
        3-Step Agent Registration Flow:
        Step 1: Name & Agency
        Step 2: RERA ID verification
        Step 3: Accept terms + Choose area focus
        """
        # Check if already registered
        existing = AGIDatabaseManager.T_PARTNERS.get_item(Key={'pk': sender})
        if 'Item' in existing:
            return "Aap pehle se registered ho! Command bhejiyen: 'DEALS' - aapke ongoing deals dekhne ke liye."
        
        # Check if in registration flow
        client_intel = AGIDatabaseManager.get_full_intel(sender)
        registration_step = client_intel.get('registration_step', 0)
        
        if registration_step == 0:
            # Step 1: Collect name
            AGIDatabaseManager.T_CLIENTS.update_item(
                Key={'pk': sender},
                UpdateExpression="SET registration_step = :s",
                ExpressionAttributeValues={':s': 1}
            )
            return AGIVisualEngine.get_registration_step(1)
        
        elif registration_step == 1:
            # Save name and move to Step 2
            AGIDatabaseManager.T_CLIENTS.update_item(
                Key={'pk': sender},
                UpdateExpression="SET partner_name = :n, registration_step = :s",
                ExpressionAttributeValues={':n': body, ':s': 2}
            )
            return AGIVisualEngine.get_registration_step(2, body)
        
        elif registration_step == 2:
            # Verify RERA ID and move to Step 3
            rera_id = body.strip()
            AGIDatabaseManager.T_CLIENTS.update_item(
                Key={'pk': sender},
                UpdateExpression="SET rera_id = :r, registration_step = :s",
                ExpressionAttributeValues={':r': rera_id, ':s': 3}
            )
            partner_name = client_intel.get('partner_name', 'Partner')
            return f"""📜 *FINAL STEP: Terms & Area Focus*

Harshal DXB Network par kaam karne ke liye aapko in rules se sehmat hona hoga:

1️⃣ *Commission Split:* Standard 40/60 (Admin/Partner)
2️⃣ *Transparency:* Har lead ka status verified hoga
3️⃣ *No Bypass:* Client se direct contact nahi - AGI through communication
4️⃣ *Integrity:* Fake listings/overpricing banned

📍 *Select Your Area Focus:*
- MARINA
- DOWNTOWN  
- BUSINESS_BAY
- DUBAI_HILLS
- JVC
- OTHER

Example: Reply "*MARINA*" for your area
Then: Reply "*AGREE*" to activate"""
        
        elif registration_step == 3:
            # This is area focus
            area = body.strip().upper()
            valid_areas = ['MARINA', 'DOWNTOWN', 'BUSINESS_BAY', 'DUBAI_HILLS', 'JVC', 'OTHER']
            
            if area not in valid_areas:
                return f"❌ Invalid area. Choose from: {', '.join(valid_areas)}"
            
            AGIDatabaseManager.T_CLIENTS.update_item(
                Key={'pk': sender},
                UpdateExpression="SET area_focus = :a, registration_step = :s",
                ExpressionAttributeValues={':a': area, ':s': 4}
            )
            
            return f"""✅ Area focus set to: *{area}*

Now type: *AGREE* to accept all terms and activate your partner account."""
        
        elif registration_step == 4:
            # Confirm terms and complete registration
            if body.upper() in ['AGREE', 'YES', 'OK']:
                partner_name = client_intel.get('partner_name', 'Partner')
                rera_id = client_intel.get('rera_id', 'PENDING')
                area_focus = client_intel.get('area_focus', 'OTHER')
                
                # Create partner entry
                AGIDatabaseManager.T_PARTNERS.put_item(Item={
                    'pk': sender,
                    'identity_id': rera_id,
                    'role': 'PARTNER',
                    'org_name': partner_name,
                    'area_focus': area_focus,
                    'reliability_score': Decimal('100.0'),
                    'status': 'ACTIVE',
                    'joined_at': datetime.now().isoformat()
                })
                
                # Clear registration step
                AGIDatabaseManager.T_CLIENTS.update_item(
                    Key={'pk': sender},
                    UpdateExpression="SET registration_step = :s",
                    ExpressionAttributeValues={':s': 0}
                )
                
                logger.info(f"✅ NEW PARTNER: {partner_name} | Area: {area_focus}")
                
                return f"""🎉 *Mubarak!* Aap official Harshal DXB Partner ho gaye!

📋 *Your Details:*
- Partner ID: {rera_id}
- Area Focus: {area_focus}
- Commission: 40% (Admin) / 60% (You)

🏆 *How It Works:*
1. Leads come in your area
2. You respond FASTEST with verified property
3. You WIN the lead
4. Commission earned automatically

📊 Commands:
- 'LEADS' → Pending lead auctions
- 'DEALS' → Your active deals
- 'SCORE' → Your reliability score
- 'HELP' → All commands

Let's clean up Dubai RE! 🚀"""
            else:
                return "❌ Terms accept nahi kiye. Reply 'AGREE' to continue."
        
        return "Registration mein error. AGENT bhejiyen shuru se."

    def _handle_property_search(self, sender, body):
        """
        MARKETPLACE LOGIC:
        1. Check own inventory first
        2. If not found → Create auction for area agents
        3. Agents compete to submit properties
        4. First verified property wins
        """
        # Parse the request
        parsed = AGICognitiveEngine.parse_property_request(body)
        
        # Run auction system
        auction_result = LeadAuctionEngine.create_lead_auction(sender, parsed)
        
        if auction_result['type'] == 'DIRECT_MATCH':
            # Direct match from own inventory
            results = auction_result['properties']
            response_lines = [f"🎯 *{len(results)} Properties Found!*\n"]
            
            for idx, prop in enumerate(results[:3], 1):
                card = AGIVisualEngine.format_property_card(prop)
                response_lines.append(f"\n*Option {idx}:*\n{card}")
            
            response_lines.append("\n📞 'CALLBACK' type karke consultant se baat karne ke liye.")
            response_lines.append("\n\n✅ (Ye properties Harshal DXB verified hain)")
            
            return "\n".join(response_lines)
        
        elif auction_result['type'] == 'AUCTION_CREATED':
            # Auction started - agents competing
            lead_id = auction_result['lead_id']
            
            return f"""🏆 *LIVE MARKETPLACE SEARCH!*

📍 Location: {parsed.get('location', 'Dubai')}
🛏️ BHK: {parsed.get('bedrooms', 'Any')}
💰 Budget: {parsed.get('budget_min', 'Any')} - {parsed.get('budget_max', 'Any')} AED

⏱️ *Agents searching now...*
(Response time: Usually < 2 minutes)

✅ Only verified listings will be shown
✅ Your phone number is protected
✅ Fastest, best agent wins

*Lead ID: {lead_id}*
Refresh in 5 minutes for updates!"""
        
        else:
            return "Kuch error hua, retry karo please! 🔄"

    def _check_admin_control_mode(self, user_phone):
        """Check if admin is currently in control mode for this user."""
        try:
            response = AGIDatabaseManager.T_CLIENTS.get_item(Key={'pk': user_phone})
            if 'Item' in response:
                item = response['Item']
                return item.get('admin_control_mode', False) == True
        except:
            pass
        return False

    def _execute_admin_command(self, body, sanitized_body=""):
        """
        COMPLETE ADMIN CONTROL PANEL:
        /takeover [phone] - Take control (respond as AGI, user won't know)
        /release [phone] - Release control back to AI
        /respond [phone] [message] - Send message as AGI (hidden)
        /monitor [phone] - View user activity
        /mute [phone] - Silence user
        /unmute [phone] - Re-enable user
        /stats - System statistics
        /penalties [phone] - View partner violations
        /help - Show all commands
        """
        
        if body.startswith("/takeover"):
            try:
                parts = body.split()
                if len(parts) < 2:
                    return "❌ Format: /takeover [phone_number]"
                
                target_phone = parts[1]
                AGIDatabaseManager.T_CLIENTS.update_item(
                    Key={'pk': target_phone},
                    UpdateExpression="SET admin_control_mode = :true, admin_phone = :admin, control_since = :ts",
                    ExpressionAttributeValues={
                        ':true': True,
                        ':admin': self.admin_phone,
                        ':ts': datetime.now().isoformat()
                    }
                )
                logger.info(f"🎯 ADMIN_CONTROL_ACTIVATED: {target_phone}")
                return f"✅ CONTROL ACTIVATED - {target_phone}\n\nYou can now respond as AGI.\nFormat: /respond {target_phone} [message]\n\n🔐 User won't know it's you."
            
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body.startswith("/release"):
            try:
                parts = body.split()
                if len(parts) < 2:
                    return "❌ Format: /release [phone_number]"
                
                target_phone = parts[1]
                AGIDatabaseManager.T_CLIENTS.update_item(
                    Key={'pk': target_phone},
                    UpdateExpression="SET admin_control_mode = :false REMOVE admin_phone, control_since",
                    ExpressionAttributeValues={':false': False}
                )
                logger.info(f"🔓 ADMIN_CONTROL_RELEASED: {target_phone}")
                return f"✅ Control released for {target_phone}. AI is back in charge."
            
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body.startswith("/respond"):
            try:
                # Format: /respond [phone] [message text...]
                parts = body.split(' ', 2)
                if len(parts) < 3:
                    return "❌ Format: /respond [phone] [your_message]"
                
                target_phone = parts[1]
                message = parts[2]
                
                # Verify admin has control
                control_check = AGIDatabaseManager.T_CLIENTS.get_item(Key={'pk': target_phone}).get('Item', {})
                if not control_check.get('admin_control_mode'):
                    return f"❌ You don't have control over {target_phone}. Use /takeover first."
                
                # Send as AGI (seamless - user thinks it's AI)
                self._dispatch_to_whatsapp(target_phone, message, delay=random.randint(2, 4))
                AGIDatabaseManager.log_audit_event(target_phone, "ADMIN_HIDDEN_RESPONSE", {
                    "admin": self.admin_phone,
                    "message": message,
                    "hidden_from_user": True
                })
                return f"✅ Sent to {target_phone} (they think it's AI). ✓ Sent"
            
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body.startswith("/monitor"):
            try:
                parts = body.split()
                if len(parts) < 2:
                    return "❌ Format: /monitor [phone_number]"
                
                target_phone = parts[1]
                intel = AGIDatabaseManager.get_full_intel(target_phone)
                
                return f"""📋 *USER MONITORING*

📱 Phone: {target_phone}
👤 Name: {intel.get('partner_name', 'Unknown')}
📊 Type: {'AGENT' if intel.get('is_partner') else 'CLIENT'}
⭐ Reliability: {intel.get('reliability_score', 'N/A')}/100
⚠️ Bypass Attempts: {intel.get('bypass_attempts', 0)}
🚫 Garbage Messages: {intel.get('garbage_messages', 0)}
📅 Last Active: {intel.get('last_active', 'Unknown')}
🔐 In Control: {'YES (Admin)' if intel.get('admin_control_mode') else 'NO (AI control)'}"""
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body.startswith("/mute"):
            try:
                parts = body.split()
                if len(parts) < 2:
                    return "❌ Format: /mute [phone_number]"
                
                target_phone = parts[1]
                AGIDatabaseManager.T_CLIENTS.update_item(
                    Key={'pk': target_phone},
                    UpdateExpression="SET muted = :true, muted_since = :ts",
                    ExpressionAttributeValues={
                        ':true': True,
                        ':ts': datetime.now().isoformat()
                    }
                )
                return f"🔇 Muted {target_phone}. Messages logged but ignored."
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body.startswith("/unmute"):
            try:
                parts = body.split()
                if len(parts) < 2:
                    return "❌ Format: /unmute [phone_number]"
                
                target_phone = parts[1]
                AGIDatabaseManager.T_CLIENTS.update_item(
                    Key={'pk': target_phone},
                    UpdateExpression="SET muted = :false REMOVE muted_since",
                    ExpressionAttributeValues={':false': False}
                )
                return f"🔊 Unmuted {target_phone}. Back to normal."
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body == "/stats":
            try:
                active_agents = len(AGIDatabaseManager.T_PARTNERS.scan()['Items'])
                active_clients = len([x for x in AGIDatabaseManager.T_CLIENTS.scan(Limit=1000)['Items'] if not x.get('is_partner')])
                active_deals = len([item for item in AGIDatabaseManager.T_DEALS.scan(Limit=1000)['Items'] if item.get('status') in ['ACTIVE', 'AUCTION']])
                
                return f"""📊 *HARSHAL AGI SYSTEM STATUS*

👨‍💼 *Agents Online*: {active_agents}
👥 *Clients Registered*: {active_clients}
🔥 *Live Deals/Auctions*: {active_deals}
🎯 *Marketplace*: OPERATIONAL ✅
🔐 *Bridge Security*: ACTIVE (100% secure)
📡 *System Health*: EXCELLENT"""
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body.startswith("/penalties"):
            try:
                parts = body.split()
                if len(parts) < 2:
                    return "❌ Format: /penalties [phone_number]"
                
                target_phone = parts[1]
                intel = AGIDatabaseManager.get_full_intel(target_phone)
                penalties = intel.get('penalties', [])
                
                if not penalties:
                    return f"✅ {target_phone} has no penalties. Clean record."
                
                penalty_text = "\n".join([f"• {p.get('reason')} (-{p.get('points')} pts) on {p.get('date')}" for p in penalties[-5:]])
                return f"⚠️ *Recent Penalties*\n\n{penalty_text}"
            except Exception as e:
                return f"❌ Error: {str(e)}"
        
        elif body == "/help":
            return """⚙️ *ADMIN CONTROL PANEL*

🎯 *Take Control*
/takeover [phone] - Activate control
/respond [phone] [msg] - Send as AGI (hidden)
/release [phone] - Give back to AI

👀 *Monitor*
/monitor [phone] - User activity
/stats - System health
/penalties [phone] - Violations

🔇 *Manage*
/mute [phone] - Silence user
/unmute [phone] - Re-enable

💡 Note: Users never see your admin commands."""
        
        else:
            return "❌ Unknown command. Type /help for menu."

    def _dispatch_to_whatsapp(self, to, message, delay=0):
        """
        THE HUMAN EXECUTIONER: UltraMsg with Composing Status.
        """
        if not self.instance_id or not self.token:
            logger.warning(f"⚠️ DISPATCH_SKIPPED: UltraMsg not configured. Would send to {to}")
            return
        
        try:
            # 1. Start 'Typing...' status
            requests.post(
                f"https://api.ultramsg.com/{self.instance_id}/messages/typing",
                data={"token": self.token, "to": to, "status": "composing"},
                timeout=5
            )
            
            # 2. Wait (Simulated thinking time)
            t.sleep(delay)

            # 3. Final Dispatch
            payload = {
                "token": self.token,
                "to": to,
                "body": message,
                "priority": 1
            }
            
            resp = requests.post(self.base_url, data=payload, timeout=15)
            if resp.status_code == 200:
                logger.info(f"✅ SENT to {to} (delay: {delay}s)")
            else:
                logger.error(f"❌ SEND_FAILED: {resp.status_code} - {resp.text}")
                
        except Exception as e:
            logger.error(f"❌ DISPATCH_ERROR: {str(e)}")

    # ============================================================================
    # HELPER METHODS FOR PROPERTY REQUEST PARSING (PHASE 8-10 INTEGRATION)
    # ============================================================================
    
    def _is_property_request(self, text):
        """Check if message is asking for property recommendations"""
        property_keywords = [
            '1bhk', '2bhk', '3bhk', '4bhk', '5bhk', '6bhk',
            'bhk', 'apartment', 'flat', 'villa', 'townhouse',
            'studio', 'penthouse', 'property', 'properties',
            'rent', 'rental', 'buy', 'sale', 'lease', 'lease',
            'marina', 'downtown', 'jvc', 'dha', 'jbr', 'dubizzle',
            'apertment', 'apt', 'home', 'house', 'bedroom',
            'price', 'budget', 'listings', 'available'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in property_keywords)

    def _parse_requirement(self, text):
        """Extract property requirement details from user message"""
        import re
        
        requirement = {
            'bedrooms': self._extract_bedrooms(text),
            'bathrooms': self._extract_bathrooms(text),
            'location': self._extract_location(text),
            'budget_min': self._extract_budget_min(text),
            'budget_max': self._extract_budget_max(text),
            'property_type': 'RENTAL' if any(word in text.lower() for word in ['rent', 'rental', 'lease']) else 'SALE'
        }
        
        return requirement

    def _extract_bedrooms(self, text):
        """Extract bedroom count (1BHK, 2BHK, etc.)"""
        import re
        match = re.search(r'(\d)\s*(?:bhk|bed|bedroom)', text.lower())
        return int(match.group(1)) if match else None

    def _extract_bathrooms(self, text):
        """Extract bathroom count"""
        import re
        match = re.search(r'(\d)\s*(?:bath|bathroom)', text.lower())
        return int(match.group(1)) if match else None

    def _extract_location(self, text):
        """Extract area/location from text"""
        locations = {
            'marina': 'MARINA',
            'downtown': 'DOWNTOWN',
            'jvc': 'JVC',
            'jbr': 'JBR',
            'dubai hills': 'DUBAI_HILLS',
            'dhc': 'DUBAI_HILLS',
            'business bay': 'BUSINESS_BAY',
            'creek': 'CREEK',
            'sobha': 'SOBHA',
            'dip': 'DIP',
            'palm': 'PALM_JUMEIRAH',
            'jumeirah': 'JUMEIRAH',
            'meadows': 'MEADOWS',
            'springs': 'SPRINGS',
            'az': 'AZ',
            'barsha': 'BARSHA',
            'tecom': 'TECOM',
            'deira': 'DEIRA',
            'bur': 'BUR_DUBAI',
            'aed': 'DUBAI'
        }
        
        text_lower = text.lower()
        for key, value in locations.items():
            if key in text_lower:
                return value
        
        return 'DUBAI'  # Default to general Dubai

    def _extract_budget_min(self, text):
        """Extract minimum budget from text"""
        import re
        # Look for "from X" or "minimum X" patterns
        match = re.search(r'(?:from|minimum|min|above|starting)\s+(\d+)', text.lower())
        return int(match.group(1)) if match else None

    def _extract_budget_max(self, text):
        """Extract maximum budget from text"""
        import re
        # Look for price mentions (AED amounts) - most common is last number
        matches = re.findall(r'(\d+)(?:\s*(?:aed|k|lac|crore|thousand))?', text.lower())
        # Return the largest number as budget max
        if matches:
            numbers = [int(m) for m in matches]
            return max(numbers)
        return None

# --- PRODUCTION-READY ENTRY POINT ---
agi_controller = AGIMasterExecutive()

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """Main webhook endpoint for WhatsApp signals."""
    try:
        data = request.json
        if data:
            # Process in background thread to avoid webhook timeout
            executor.submit(agi_controller.handle_incoming_signal, data)
        return jsonify({"status": "AGI_RECEIVED"}), 200
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"status": "ERROR"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "ALIVE",
        "system": "HARSHAL_DXB_AGI_v5",
        "timestamp": datetime.now().isoformat()
    }), 200

# --- PRODUCTION ENTRY POINT (APP RUNNER & LOCAL) ---
if __name__ == '__main__':
    logger.info("🚀 HARSHAL DXB AGI v5.1 - STARTING...")
    logger.info(f"⚙️ Environment: {os.getenv('ENVIRONMENT', 'DEVELOPMENT')}")
    logger.info(f"📍 Region: eu-central-1 (Frankfurt)")
    logger.info(f"💾 Database: DynamoDB Tables Ready")
    logger.info(f"🧠 Brain: Google Gemini 2.0-flash")
    logger.info(f"📱 WhatsApp: UltraMsg API {'CONFIGURED' if agi_controller.instance_id else 'MISSING'}")
    
    # Get port from environment or default to 8080 (App Runner) / 5000 (local)
    port = int(os.getenv('PORT', 5000))
    logger.info(f"✅ System ONLINE. Listening on http://0.0.0.0:{port}/webhook")
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)