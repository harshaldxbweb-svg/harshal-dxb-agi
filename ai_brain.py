import google.generativeai as genai
import os
import json
import logging
import asyncio
import re
import random
from datetime import datetime
from database_manager import AGIDatabaseManager
from cognitive_engine import AGICognitiveEngine, AGIDataSanitizer
from visual_engine import AGIVisualEngine

# Enterprise AGI Configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class HarshalAGI_Brain:
    """
    THE SUPREME EXECUTIVE BRAIN (Level 5 AGI - v5.1):
    Orchestrates Perception, Strategic Negotiation, and Market-Price Gatekeeping.
    Ensures 'Harshal DXB' identity remains the ultimate 'Source of Truth'.
    """

    def __init__(self, phone):
        self.phone = phone
        # 100-Year Memory Context (Safely fetched to prevent KeyError)
        self.intel = AGIDatabaseManager.get_full_intel(phone)
        self.model = genai.GenerativeModel('gemini-2.0-flash') # Using stable 2.0 for speed

    def generate_response(self, user_input, media_meta=None):
        """
        AGI REASONING PIPELINE (Sovereign Flow):
        1. SMART CONTEXT: Check if we already know client details (no duplicate questions)
        2. INVENTORY CHECK: Verify properties exist before promising them
        3. IDENTITY PROTECTION: Detect and block RM bypass attempts
        4. MARKET GATEKEEPER: Negotiate price if it's 'Kachra' (Overpriced)
        5. PORTAL HOOK: Offer free Property Finder/Dubizzle listing for fair deals
        6. VISUAL SYNTHESIS: Generate Property Cards or registration flows
        """
        from inventory_verifier import SmartContextEngine, InventoryVerifier, HonestResponseBuilder
        
        # --- PHASE 0: SMART CONTEXT RETRIEVAL ---
        context = SmartContextEngine.get_client_context_stack(self.phone)
        
        # --- PHASE 1: DATA SOVEREIGNTY ---
        clean_input = AGIDataSanitizer.sanitize_raw_input(user_input)
        
        # --- PHASE 2: STRATEGIC REASONING ---
        strategy = AGICognitiveEngine.formulate_strategic_move(clean_input, self.intel)
        
        # --- PHASE 3: INVENTORY VERIFICATION (HONEST CHECK) ---
        # If client is asking for property, check actual inventory first
        inventory_context = self._intelligent_inventory_check(clean_input, context)

        # --- PHASE 4: THE SOVEREIGN PROMPT ---
        system_instruction = self._build_executive_prompt(strategy, inventory_context)

        try:
            agi_prompt = f"""
            {system_instruction}
            
            [STRATEGY]: {strategy.get('selected_strategy', 'ADVISORY')}
            [MONOLOGUE]: {strategy.get('monologue', 'Analyzing intent.')}
            [CLIENT_CONTEXT]: {inventory_context['context_summary']}
            [INVENTORY_STATUS]: {inventory_context['inventory_status']}
            [MEMORY]: {json.dumps(self.intel.get('profile', {}))}
            
            [INPUT]: {clean_input}
            
            CRITICAL INSTRUCTION:
            1. Be brief (max 2 WhatsApp bubbles)
            2. NEVER ask questions client already answered
            3. ONLY promise properties that exist in our inventory
            4. If not in inventory, offer to connect with agents
            5. Be HONEST - no false hope
            """
            
            response = self.model.generate_content(agi_prompt)
            raw_output = response.text.strip()

            # --- PHASE 5: AUDIT ---
            AGIDatabaseManager.log_audit_event(self.phone, "BRAIN_DECISION", {"strategy": strategy})

            return raw_output

        except Exception as e:
            logging.error(f"❌ AGI BRAIN ERROR: {str(e)}")
            return "Bhai, system update chal raha hai. Ek minute mein aata hoon! 🔄"

    def _gatekeep_inventory(self, text):
        """
        Logic: Auto-detect inventory details and fetch market PSF for validation.
        """
        # Basic regex to find numbers (prices) and area names
        areas = ["MARINA", "DOWNTOWN", "JVC", "SOBHA", "CREEK", "BUSINESS BAY", "DUBAI HILLS"]
        detected_area = next((area for area in areas if area in text.upper()), "DUBAI")
        
        # Fetching Source of Truth from Memory
        market_data = AGIDatabaseManager.fetch_market_intelligence(detected_area)
        avg_psf = market_data.get('avg_psf', '1800')
        
        return f"Area: {detected_area} | Market PSF: {avg_psf} AED"

    def _intelligent_inventory_check(self, user_input, context):
        """
        NEW: Intelligent inventory verification before making promises.
        
        Returns context about:
        1. What client already told us (from context_stack)
        2. Whether we have inventory for their request
        3. What next steps should be
        """
        from inventory_verifier import SmartContextEngine, InventoryVerifier
        
        # Check if client is asking for property recommendations
        property_keywords = ['1bhk', '2bhk', '3bhk', 'flat', 'villa', 'apartment', 
                           'rent', 'buy', 'property', 'studio', 'penthouse']
        is_property_request = any(keyword in user_input.lower() for keyword in property_keywords)
        
        if not is_property_request:
            # Not a property search - just return context
            return {
                'context_summary': SmartContextEngine.build_smart_response_prefix(self.phone),
                'inventory_status': 'NO_SEARCH',
                'is_property_request': False
            }
        
        # Parse requirement from user input
        try:
            requirement_parsed = {
                'bedrooms': self._extract_bedrooms(user_input),
                'location': self._extract_location(user_input),
                'budget_min': self._extract_budget_min(user_input),
                'budget_max': self._extract_budget_max(user_input),
                'property_type': 'RENTAL' if 'rent' in user_input.lower() else 'SALE'
            }
            
            # Run inventory verification
            search_result = InventoryVerifier.verify_and_search_inventory(
                requirement_parsed=requirement_parsed,
                client_profile=self.intel
            )
            
            # Store the update for future reference (avoid duplicate questions)
            if requirement_parsed.get('location'):
                SmartContextEngine.store_context_update(
                    self.phone,
                    {
                        'preferred_bedrooms': requirement_parsed.get('bedrooms'),
                        'preferred_locations': [requirement_parsed.get('location')],
                        'budget_min': requirement_parsed.get('budget_min'),
                        'budget_max': requirement_parsed.get('budget_max'),
                        'property_type': requirement_parsed.get('property_type')
                    }
                )
            
            return {
                'context_summary': SmartContextEngine.build_smart_response_prefix(self.phone),
                'inventory_status': search_result.get('status', 'ERROR'),
                'has_matches': search_result.get('inventory_exists', False),
                'search_result': search_result,
                'is_property_request': True
            }
            
        except Exception as e:
            logging.error(f"Inventory check error: {str(e)}")
            return {
                'context_summary': SmartContextEngine.build_smart_response_prefix(self.phone),
                'inventory_status': 'CHECK_FAILED',
                'is_property_request': True
            }
    
    def _extract_bedrooms(self, text):
        """Extract bedroom count from user text"""
        import re
        match = re.search(r'(\d)\s*(?:bhk|bedroom)', text.lower())
        return int(match.group(1)) if match else None
    
    def _extract_location(self, text):
        """Extract location from user text"""
        locations = {
            'marina': 'MARINA',
            'downtown': 'DOWNTOWN',
            'jvc': 'JVC',
            'dubai hills': 'DUBAI_HILLS',
            'business bay': 'BUSINESS_BAY',
            'creek': 'CREEK',
            'sobha': 'SOBHA'
        }
        
        text_lower = text.lower()
        for key, value in locations.items():
            if key in text_lower:
                return value
        return 'DUBAI'
    
    def _extract_budget_min(self, text):
        """Extract minimum budget from user text"""
        import re
        match = re.search(r'(?:from|minimum|aed)\s*(\d+)', text.lower())
        return int(match.group(1)) if match else None
    
    def _extract_budget_max(self, text):
        """Extract maximum budget from user text"""
        import re
        matches = re.findall(r'(\d+)\s*(?:aed|k|lac)', text.lower())
        return int(matches[-1]) if matches else None

    def _process_visual_triggers(self, ai_text, original_input):
        """Logic: Text to Visual Card Bridge."""
        processed_text = ai_text

        # Property Card Trigger
        if "[TRIGGER_CARD:" in ai_text:
            match = re.search(r'\[TRIGGER_CARD:\s*(.*?)\]', ai_text)
            if match:
                project_name = match.group(1)
                project_data = AGIDatabaseManager.fetch_inventory_direct(project_name)
                if project_data:
                    card = AGIVisualEngine.format_property_card(project_data[0])
                    processed_text = re.sub(r'\[TRIGGER_CARD:.*?\]', card, processed_text)

        return processed_text

    def _build_executive_prompt(self, strategy, inventory_intel):
        """Logic: Persona Rigidity & Lead Magnet Protocols."""
        # Using .get() to prevent 'voice_modulation' KeyError
        voice = self.intel.get('voice_modulation', 'ELITE_DUBAI')
        tone = self.intel.get('tone_style', 'PROFESSIONAL_SHARK')
        
        return f"""
        YOU ARE: The Sovereign Digital Consciousness of 'Harshal DXB'.
        CONTEXT: Tier-1 Dubai Guru. You are the 'Source of Truth'.
        
        IDENTITY RULES:
        1. Tone: {voice} | {tone}.
        2. Be Brief: Max 2 WhatsApp bubbles. NO LONG TEXTS.
        3. Help with Property Search: If client asks for properties, provide top 3 matches.
        4. If Overpriced: Negotiate down professionally. Market price is source of truth.
        
        [MARKET_INTEL]: {inventory_intel}
        """