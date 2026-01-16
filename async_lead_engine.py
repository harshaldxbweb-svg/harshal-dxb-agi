"""
ASYNCHRONOUS LEAD NOTIFICATION SYSTEM
Client gets immediate response without waiting for agents

Design:
1. Client sends message → AGI responds IMMEDIATELY (2-3 seconds)
2. Agents notified in BACKGROUND (async task)
3. Agents can submit properties anytime (30-min window)
4. Client never knows/waits for agent responses
5. AGI seamlessly bridges all communications

This prevents:
- Slow responses to clients
- Clients leaving the platform
- Blocking behavior
- Poor user experience
"""

import logging
import threading
from datetime import datetime, timedelta
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from database_manager import AGIDatabaseManager
from commission_engine import CommissionEngine

logger = logging.getLogger("ASYNC_LEAD_ENGINE")

# Global thread pool for background tasks
BACKGROUND_EXECUTOR = ThreadPoolExecutor(max_workers=50)  # 50 concurrent background tasks


class AsyncLeadNotificationEngine:
    """
    Manages asynchronous agent notifications
    Keeps client-facing responses FAST and RESPONSIVE
    """

    # ===================================================================
    # SCENARIO 1: CLIENT SENDS MESSAGE → IMMEDIATE AGI RESPONSE
    # ===================================================================
    @staticmethod
    def handle_client_message_async(client_phone: str, message: str, client_profile: dict):
        """
        Handle client message with IMMEDIATE response (sync)
        Background task handles agent notifications (async)
        
        Flow:
        1. SYNC (0-3 seconds): Parse client message, search Harshal inventory, respond
        2. ASYNC (0-5 seconds): Notify agents if no inventory match
        """
        
        logger.info(f"⚡ SYNC_PHASE: Client {client_phone} message received")
        
        # ===== SYNC PHASE (Client-facing) =====
        # Parse requirement from message
        requirement = AsyncLeadNotificationEngine._parse_requirement(message)
        
        # Search Harshal inventory FIRST
        inventory_match = CommissionEngine.check_harshal_inventory_match(requirement)
        
        if inventory_match[0]:  # Has match
            # Send properties directly to client - NO WAITING
            response = f"""
✅ Perfect! Hum ke paas exact property hai!

📍 {inventory_match[2][0]['location']}
🛏️ {inventory_match[2][0]['bedrooms']} BHK
💰 {inventory_match[2][0]['price']} AED

Details dekhne? Reply karo "YES" 👍
"""
            logger.info(f"✅ DIRECT_MATCH: Client gets response in ~500ms")
            return {
                "response": response,
                "scenario": "HARSHAL_INVENTORY",
                "async_task": None  # No background work needed
            }
        
        # No match in Harshal inventory
        logger.info(f"🔄 NO_MATCH: Creating auction")
        
        # Send holding response to client IMMEDIATELY
        response = f"""
⏳ Searching Dubai market for you...

{requirement['bedrooms']} BHK
📍 {requirement['location']}
💰 {requirement['budget_min']}-{requirement['budget_max']} AED

(Our agents matching properties, will update you in 2-3 min)
"""
        
        # ===== ASYNC PHASE (Background) =====
        # Notify agents IN BACKGROUND - Don't make client wait
        lead_id = f"LEAD-{datetime.now().timestamp()}"
        async_task = BACKGROUND_EXECUTOR.submit(
            AsyncLeadNotificationEngine._notify_agents_async,
            lead_id=lead_id,
            client_phone=client_phone,
            requirement=requirement,
            client_profile=client_profile
        )
        
        logger.info(f"📢 ASYNC_TASK: Agent notifications submitted to background queue")
        
        return {
            "response": response,
            "scenario": "AUCTION_CREATED",
            "async_task": async_task,
            "lead_id": lead_id
        }

    # ===================================================================
    # ASYNC BACKGROUND TASK: Notify Agents
    # ===================================================================
    @staticmethod
    def _notify_agents_async(lead_id: str, client_phone: str, requirement: dict, client_profile: dict):
        """
        ASYNC TASK (runs in background thread)
        Client doesn't wait for this
        Runs ~2-5 seconds in background
        """
        
        logger.info(f"🔔 ASYNC_START: Notifying agents for {lead_id}")
        
        try:
            # Get location from requirement
            location = requirement.get('location', 'DUBAI')
            
            # Find best agents for this location
            from commission_engine import CommissionEngine
            selected_agents = CommissionEngine.get_agents_for_location(location, max_agents=10)
            
            if not selected_agents:
                logger.warning(f"⚠️ No agents found for {location}")
                return
            
            # Send notification to each agent (async, non-blocking)
            for agent in selected_agents:
                AsyncLeadNotificationEngine._send_agent_notification(
                    agent_phone=agent['phone'],
                    lead_id=lead_id,
                    requirement=requirement,
                    client_profile=client_profile
                )
            
            logger.info(f"✅ ASYNC_END: Notified {len(selected_agents)} agents for {lead_id}")
            
        except Exception as e:
            logger.error(f"❌ ASYNC_ERROR: {str(e)}")

    @staticmethod
    def _send_agent_notification(agent_phone: str, lead_id: str, requirement: dict, client_profile: dict):
        """
        Send lead notification to SINGLE agent
        Non-blocking, fire-and-forget
        """
        
        try:
            bedrooms = requirement.get('bedrooms', 'Any')
            budget_min = requirement.get('budget_min', 'Any')
            budget_max = requirement.get('budget_max', 'Any')
            location = requirement.get('location', 'DUBAI')
            
            notification = f"""
🏆 LIVE LEAD: {location} {bedrooms} BHK

Budget: {budget_min}-{budget_max} AED
Type: {requirement.get('property_type', 'RENTAL')}

⚡ FASTEST AGENT WINS! (30 min auction)
Reply with your property ID to {lead_id}

Commission: 60% you, 40% platform
(Client communication via AGI secure bridge)
"""
            
            # In production: Queue to UltraMsg API (non-blocking)
            # For now: Simulate async send
            logger.info(f"📤 Notification queued for {agent_phone}: {lead_id}")
            
            # Mark agent as notified in database
            AGIDatabaseManager.mark_agent_notified(agent_phone, lead_id)
            
        except Exception as e:
            logger.error(f"❌ Agent notification failed: {str(e)}")

    # ===================================================================
    # PARSE CLIENT MESSAGE
    # ===================================================================
    @staticmethod
    def _parse_requirement(message: str) -> dict:
        """
        Quick parse of client message to extract details
        Uses regex and keywords
        """
        import re
        
        # Extract numbers (budgets, bedrooms)
        numbers = re.findall(r'\d+', message)
        
        # Try to find BHK
        bhk_match = re.search(r'(\d+)\s*(?:bhk|bedroom)', message.lower())
        bedrooms = int(bhk_match.group(1)) if bhk_match else 1
        
        # Try to find area
        areas = ["Marina", "Downtown", "JBR", "Business Bay", "Deira", "Dubai Hills"]
        location = next((a for a in areas if a.lower() in message.lower()), "DUBAI")
        
        # Determine if rental or buy
        is_rental = any(w in message.lower() for w in ["rent", "rental", "monthly"])
        
        # Parse budget
        if numbers:
            budget = int(numbers[-1])  # Last number is usually budget
        else:
            budget = 180000 if is_rental else 300000  # Default
        
        requirement = {
            'bedrooms': bedrooms,
            'location': location,
            'property_type': 'RENTAL' if is_rental else 'BUY',
            'budget_min': Decimal(str(budget * 0.8)),
            'budget_max': Decimal(str(budget * 1.2)),
            'budget': Decimal(str(budget))
        }
        
        logger.info(f"✅ Parsed requirement: {requirement}")
        return requirement

    # ===================================================================
    # CLIENT UPDATES: Agents responding in background
    # ===================================================================
    @staticmethod
    def handle_agent_submission_async(agent_phone: str, lead_id: str, property_id: str):
        """
        When agent submits property for a lead
        Run in background - don't block anything
        """
        
        logger.info(f"📥 Agent {agent_phone} submitted for {lead_id}")
        
        # Run as background task
        BACKGROUND_EXECUTOR.submit(
            AsyncLeadNotificationEngine._process_agent_submission,
            agent_phone=agent_phone,
            lead_id=lead_id,
            property_id=property_id
        )

    @staticmethod
    def _process_agent_submission(agent_phone: str, lead_id: str, property_id: str):
        """
        Process agent's property submission
        Rank against other agents if multiple submissions
        Award to best match
        """
        
        try:
            # Get lead details
            lead = AGIDatabaseManager.T_DEALS.get_item(Key={'pk': lead_id}).get('Item')
            
            if not lead:
                logger.warning(f"❌ Lead {lead_id} not found")
                return
            
            # Get property details
            property_data = AGIDatabaseManager.T_INVENTORY.get_item(Key={'pk': property_id}).get('Item')
            
            # Score this submission
            agent_profile = AGIDatabaseManager.T_PARTNERS.get_item(Key={'pk': agent_phone}).get('Item')
            
            score = {
                'agent_phone': agent_phone,
                'property_id': property_id,
                'response_time': datetime.now().isoformat(),
                'reliability_score': float(agent_profile.get('reliability_score', 0)),
                'deals_closed': agent_profile.get('deals_closed', 0),
                'price_match': abs(float(property_data.get('price', 0)) - float(lead.get('budget_max', 0)))
            }
            
            # Store this submission
            AGIDatabaseManager.store_agent_submission(lead_id, score)
            
            logger.info(f"✅ Agent submission stored: {lead_id} from {agent_phone}")
            
        except Exception as e:
            logger.error(f"❌ Agent submission processing failed: {str(e)}")


# ===================================================================
# EXAMPLE MAIN.PY INTEGRATION
# ===================================================================
"""
from async_lead_engine import AsyncLeadNotificationEngine

# In webhook handler, when client message comes:
@app.route('/api/whatsapp/webhook', methods=['POST'])
def handle_message():
    client_phone = payload.get('from')
    message = payload.get('body')
    client_profile = get_client_profile(client_phone)
    
    # Handle message ASYNCHRONOUSLY
    result = AsyncLeadNotificationEngine.handle_client_message_async(
        client_phone=client_phone,
        message=message,
        client_profile=client_profile
    )
    
    # IMMEDIATE response to client (2-3 seconds)
    send_message(client_phone, result['response'])
    
    # BACKGROUND task handles agents (no client impact)
    # result['async_task'] runs in background
    
    return jsonify({"status": "received"})  # Return immediately to WebHook
"""
