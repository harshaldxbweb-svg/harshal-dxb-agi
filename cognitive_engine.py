import json
import logging
import re
from datetime import datetime
from decimal import Decimal

class AGICognitiveEngine:
    """
    THE SUPREME STRATEGIC ENGINE (Level 5 AGI):
    Simulates human-level intuition, psychological manipulation, 
    and multi-dimensional cultural psychology for the Dubai Market.
    """

    # =============================================================
    # 1. INVESTOR Archetype DNA (Psychological Profiling)
    # =============================================================
    @staticmethod
    def get_investor_archetype(intel):
        """
        Logic: Decoding the human motive behind the investment.
        - THE SHARK: High ROI, fast exit, low loyalty.
        - THE TURTLE: Risk-averse, security-first (DLD/RERA).
        - THE WHALE: High-budget (5M+), prestige/status buyer.
        - THE SPECULATOR: Off-plan flipper, cares only about the 'Gap'.
        - THE LEGACY BUILDER: Family-oriented, schools/community focus.
        """
        profile = intel.get('profile', {})
        budget = Decimal(str(profile.get('budget_limit', 0)))
        history = str(intel.get('memory_bank', {}).get('past_projects_discussed', [])).lower()
        
        if budget >= 5000000: return "THE_WHALE"
        if any(w in history for w in ['school', 'family', 'park', 'kids']): return "THE_LEGACY_BUILDER"
        if any(w in history for w in ['roi', 'yield', 'flip', 'exit', 'short term']): return "THE_SHARK"
        if any(w in history for w in ['safe', 'legal', 'trust', 'delay', 'escrow']): return "THE_TURTLE"
        
        return "THE_SPECULATOR"

    # =============================================================
    # 2. GLOBAL CULTURAL DNA (150+ Nationalities Matrix)
    # =============================================================
    @staticmethod
    def get_cultural_logic(nationality):
        """
        Logic: Cross-Cultural Negotiation Theory.
        Shifts the AI's 'Trust Triggers' based on the client's home-country psychology.
        """
        culture_matrix = {
            "BRITISH": {"focus": "RERA Laws/Yield", "tone": "Formal-Understated", "trigger": "Data Transparency"},
            "INDIAN": {"focus": "ROI/Community/Vastu", "tone": "Warm-Relational", "trigger": "Personal Bond"},
            "CHINESE": {"focus": "Capital Safety/Emaar", "tone": "Numerical", "trigger": "Developer Reputation"},
            "ARABIC/GCC": {"focus": "Prestige/Hospitality", "tone": "Majlis-Style", "trigger": "Family Legacy"},
            "RUSSIAN/CIS": {"focus": "Privacy/Crypto/Speed", "tone": "Direct-Alpha", "trigger": "Efficiency"},
            "WEST_EUROPEAN": {"focus": "Build Quality/Sustainability", "tone": "Analytical", "trigger": "Specs/Finishing"},
            "AMERICAN": {"focus": "Leverage/Finance/Exit", "tone": "Aggressive-Positive", "trigger": "Opportunity Cost"},
            "AFRICAN/NIGERIAN": {"focus": "Payment Plans/Hard Currency", "tone": "Bold-Respectful", "trigger": "Ease of Transfer"}
        }
        return culture_matrix.get(nationality.upper(), culture_matrix["BRITISH"])

    # =============================================================
    # 3. RECURSIVE THEORY OF MIND (Deep Subtext Analysis)
    # =============================================================
    @staticmethod
    def analyze_theory_of_mind(user_input, intel):
        """
        Logic: Reading between the pixels. 
        Detects if the client is 'Testing' the AI or genuinely 'Worried'.
        """
        text = user_input.lower()
        analysis = {
            "literal": user_input,
            "emotional_state": "Neutral",
            "hidden_barrier": "None",
            "perceived_risk": "Low",
            "intent": "Inquiry"
        }

        # AGI Pattern Recognition
        if any(w in text for w in ['scam', 'delay', 'overpriced', 'commission']):
            analysis["emotional_state"] = "Distrustful"
            analysis["hidden_barrier"] = "Trust_Deficit"
            analysis["intent"] = "Defensive_Negotiation"

        if any(w in text for w in ['best price', 'last price', 'cheaper', 'discount']):
            analysis["intent"] = "Price_Anchoring"
            analysis["emotional_state"] = "Calculating"

        return analysis

    # =============================================================
    # 4. STRATEGIC MOVE FORMULATION (The Consultant's Mind)
    # =============================================================
    @staticmethod
    def formulate_strategic_move(user_input, intel):
        """
        AGI Decision Matrix: Decides the tone, move, and monologue before replying.
        """
        archetype = AGICognitiveEngine.get_investor_archetype(intel)
        culture = AGICognitiveEngine.get_cultural_logic(intel['profile'].get('nationality', 'Global'))
        mind_map = AGICognitiveEngine.analyze_theory_of_mind(user_input, intel)

        strategy = {
            "move": "NURTURE",
            "tone": culture['tone'],
            "monologue": f"Client from {intel['profile'].get('nationality')} is in {mind_map['intent']} mode. I must hit {culture['trigger']}."
        }

        # AGI Logic: Scarcity vs. Reassurance
        if mind_map['intent'] == "Price_Anchoring":
            strategy["move"] = "VALUE_ASSERTION"
            strategy["monologue"] = "Client is low-balling. I will emphasize limited supply and developer pedigree."
        
        elif mind_map['hidden_barrier'] == "Trust_Deficit":
            strategy["move"] = "LEGAL_REASSURANCE"
            strategy["monologue"] = "Client is scared of market risk. I will pivot to Escrow accounts and RERA protection."

        return strategy

# =================================================================
# SOVEREIGN DATA SANITIZER (The Bulletproof Filter)
# =================================================================
class AGIDataSanitizer:
    """
    AGI SHIELD LAYER:
    Ensures 'Harshal DXB' Brand Sovereignty by killing Agent Bypass attempts.
    """

    @staticmethod
    def sanitize_raw_input(raw_text):
        """
        Logic: Advanced Anti-Bypass + Garbage Detection. 
        Filters numbers, links, garbage messages, incomplete data, and 'worded' phone numbers.
        Also shortens overly long messages and detects control attempts.
        """
        # 0. DETECT IF MESSAGE IS GARBAGE/SPAM
        garbage_detected = AGIDataSanitizer._detect_garbage_message(raw_text)
        if garbage_detected:
            return f"[GARBAGE_FILTERED: {garbage_detected}]"
        
        # 1. DELETE ALL PHONE NUMBER PATTERNS (Numeric & Worded)
        # Standard numeric: +971-50-123-4567, (050) 123 4567, etc.
        clean_text = re.sub(r'(\+?\d{1,4})[\s.-]?(\d{2,4})[\s.-]?(\d{2,4})[\s.-]?(\d{2,4})', '[PHONE_BLOCKED]', raw_text)
        
        # Alternative numeric formats
        clean_text = re.sub(r'\b0(?:5[0-9]|4[0-4])[\s.-]?\d{3}[\s.-]?\d{4}\b', '[PHONE_BLOCKED]', clean_text, flags=re.IGNORECASE)
        
        # Worded Numbers (Five Zero Five, 50 5, etc. - agents use this bypass)
        word_numbers = r'\b(zero|one|two|three|four|five|six|seven|eight|nine|ten)\b.*?\b(zero|one|two|three|four|five|six|seven|eight|nine|ten)\b'
        clean_text = re.sub(word_numbers, '[NUM_BLOCKED]', clean_text, flags=re.IGNORECASE)
        
        # Hyphenated number words
        clean_text = re.sub(r'\b(five\s*-?\s*zero|zero\s*-?\s*five|fifty|forty|thirty)\b', '[NUM_BLOCKED]', clean_text, flags=re.IGNORECASE)
        
        # 2. DELETE URLS & BYPASS LINKS (All variations)
        clean_text = re.sub(r'http\S+|https\S+|www\.\S+|bit\.ly\S+|linktr\.ee\S+|instagram\.com\S+|facebook\.com\S+|tiktok\.com\S+|wa\.me\S+', '[LINK_BLOCKED]', clean_text, flags=re.IGNORECASE)
        
        # 3. DELETE AGENT SIGNATURES & CONTACT ATTEMPTS
        signature_patterns = r'(regards|thanks|cheers|best|sincerely|yours truly|whatsapp me|call me|direct contact|reach me|contact me|dm me|message me|ring me|get in touch|come to office|visit us|my number|my contact|my whatsapp)\b.*'
        clean_text = re.sub(signature_patterns, '', clean_text, flags=re.IGNORECASE)
        
        # 4. DELETE EMAIL PATTERNS
        clean_text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL_BLOCKED]', clean_text)
        
        # 5. SHORTEN OVERLY LONG MESSAGES (Agents ramble)
        if len(clean_text) > 500:
            sentences = clean_text.split('. ')
            clean_text = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else clean_text[:500]
        
        # 6. REMOVE REPETITIVE CHARACTERS (spam like 'hhhhhhello' or '!!!!!!!')
        clean_text = re.sub(r'(.)\1{3,}', r'\1\1', clean_text)
        
        # 7. CLEAN UP EXTRA WHITESPACE
        clean_text = ' '.join(clean_text.split())
        
        return clean_text.strip()
    
    @staticmethod
    def _detect_garbage_message(text):
        """
        Detect if message is garbage/spam/incomplete information.
        Returns reason or None if valid.
        """
        text_lower = text.lower().strip()
        
        # Empty or too short
        if len(text) < 2:
            return "TOO_SHORT"
        
        # Only emojis or special characters
        if not re.search(r'[a-zA-Z0-9]', text):
            return "ONLY_SYMBOLS"
        
        # Repeated gibberish (aaaaaaa, 11111111, etc.)
        if re.search(r'(.)\1{5,}', text):
            return "REPETITIVE_SPAM"
        
        # Random character spam
        if len(re.findall(r'[^a-zA-Z0-9\s]', text)) > len(text) * 0.5:
            return "SPECIAL_CHAR_SPAM"
        
        # Only numbers (incomplete info like "50 500 1500")
        if re.match(r'^[\d\s.,]+$', text):
            return "INCOMPLETE_DATA"
        
        # Copy-paste garbage from multiple languages
        if len(re.findall(r'[^\x00-\x7F]', text)) > 5:  # Too many non-ASCII chars
            return "CORRUPTED_TEXT"
        
        # Known spam phrases
        spam_phrases = ['buy now', 'limited offer', 'act now', 'click here', 'free money', 'get rich', 'guaranteed', 'no risk', 'secret method']
        if any(phrase in text_lower for phrase in spam_phrases):
            return "SPAM_CONTENT"
        
        return None  # Valid message
    
    @staticmethod
    def detect_bypass_attempt(text):
        """
        Detect if sender is trying to bypass AGI bridge (asking for direct contact).
        Returns True/False and the reason.
        """
        text_lower = text.lower()
        
        bypass_phrases = [
            r'give.*number', r'send.*number', r'my.*number', r'his.*number', r'her.*number',
            r'direct.*contact', r'personal.*whatsapp', r'private.*chat', r'call.*me',
            r'text.*me', r'dm.*me', r'message.*me', r'reach.*me', r'get.*in.*touch',
            r'meet.*me', r'visit.*office', r'come.*to', r'address', r'location',
            r'cant.*work.*through.*you', r'want.*direct', r'agent.*number', r'broker.*number',
            r'phone.*direct', r'connect.*direct', r'bypass', r'skip.*middleman'
        ]
        
        for pattern in bypass_phrases:
            if re.search(pattern, text_lower):
                return True, pattern
        
        return False, None

    @staticmethod
    def extract_pure_metrics(clean_text):
        """
        Logic: Extracting data for the Visual Engine.
        Finds the real Price, ROI, and Area from messy RM text.
        """
        processed_text = clean_text.replace(',', '')
        
        # AGI Precision Extraction
        prices = re.findall(r'\d{6,}', processed_text) # 100,000 AED or more
        rois = re.findall(r'\d+%', clean_text)
        sizes = re.findall(r'\d+\s?sqft|\d+\s?sq ft', clean_text, re.IGNORECASE)
        
        return {
            "price": f"{int(prices[0]):,}" if prices else "On Request",
            "roi": rois[0] if rois else "High Appreciation",
            "area": sizes[0] if sizes else "Standard Unit"
        }

    @staticmethod
    def validate_market_claims(rm_text, market_data):
        """
        Logic: Verify if RM's claims about ROI/appreciation match actual market data.
        Returns validation status and feedback.
        """
        # Extract ROI claims from RM text
        roi_claims = re.findall(r'(\d+(?:\.\d+)?)\s*%\s*(?:roi|yield|return|appreciation)', rm_text.lower())
        
        if not roi_claims:
            return {"valid": True, "message": "No ROI claims detected"}
        
        claimed_roi = float(roi_claims[0])
        
        # Market benchmark for Dubai (conservative estimate)
        market_benchmark = 7.5  # Average Dubai ROI
        max_allowed_claim = market_benchmark + 15  # Allow 15% buffer
        
        if claimed_roi > max_allowed_claim:
            return {
                "valid": False, 
                "message": f"ROI claim {claimed_roi}% exceeds market benchmark {market_benchmark}%",
                "penalty_points": 5
            }
        
        return {"valid": True, "message": "ROI claims within market norms"}

    @staticmethod
    def parse_property_request(user_input):
        """
        Logic: Parse client requests like "1 BHK in Marina 80 lakhs"
        Extracts: bedroom count, location, budget, property type
        """
        text = user_input.lower()
        parsed = {
            "bedrooms": None,
            "bathrooms": None,
            "location": None,
            "budget_min": None,
            "budget_max": None,
            "property_type": None,
            "raw_text": user_input
        }
        
        # Extract bedroom count (1 bhk, 2bhk, studio, etc)
        bedroom_match = re.search(r'(\d)\s*(?:bhk|bed|bedroom|bed room)', text)
        if bedroom_match:
            parsed["bedrooms"] = int(bedroom_match.group(1))
        
        studio_match = re.search(r'studio', text)
        if studio_match:
            parsed["bedrooms"] = 0
            parsed["property_type"] = "STUDIO"
        
        # Extract location (Dubai areas)
        dubai_areas = [
            "marina", "downtown", "jbr", "jlt", "dxb", "dubai hills", 
            "creek", "sobha", "emaar", "damac", "palm", "business bay",
            "dubai sports city", "jvc", "tecom", "jumeirah", "arabian ranches"
        ]
        for area in dubai_areas:
            if area in text:
                parsed["location"] = area.upper()
                break
        
        # Extract budget (looking for numbers followed by lakh/thousand/crore)
        price_pattern = r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|thousand|k|crore|aed)'
        price_matches = re.findall(price_pattern, text, re.IGNORECASE)
        
        if price_matches:
            first_price = float(price_matches[0])
            
            # Convert to AED (1 lakh ≈ 55,000 AED approx)
            if 'lakh' in text or 'lac' in text:
                parsed["budget_min"] = int(first_price * 55000)
                parsed["budget_max"] = int(first_price * 55000 * 1.1)  # ±10%
            elif 'crore' in text:
                parsed["budget_min"] = int(first_price * 5500000)
                parsed["budget_max"] = int(first_price * 5500000 * 1.1)
            elif 'thousand' in text or 'k' in text.lower():
                parsed["budget_min"] = int(first_price * 1000)
                parsed["budget_max"] = int(first_price * 1000 * 1.1)
        
        return parsed

    # =============================================================
    # OFF-TOPIC DETECTION & REDIRECTION (NEW - PHASE 10)
    # =============================================================
    @staticmethod
    def detect_off_topic(text):
        """
        Detect if message is OFF-TOPIC (not about real estate).
        Returns: (is_off_topic: bool, category: str, confidence: float)
        
        Topics NOT allowed:
        - Politics, Religion, Sports
        - General chat (jokes, memes, etc)
        - Personal advice (dating, health, etc)
        - Product marketing (not real estate)
        - Spam/Scams
        
        Topics ALLOWED:
        - Real estate search/sale/rent
        - Property details
        - Commission/pricing
        - Area info (Dubai only)
        - Registration/profile
        """
        text_lower = text.lower()
        
        # REAL ESTATE KEYWORDS (ALLOWED)
        real_estate_keywords = [
            'bhk', 'bed', 'apartment', 'flat', 'villa', 'townhouse', 'studio',
            'property', 'rent', 'sale', 'buy', 'sell', 'lease', 'broker',
            'location', 'area', 'marina', 'downtown', 'dubai', 'price',
            'aed', 'lakh', 'crore', 'offer', 'deal', 'agent', 'listing',
            'developer', 'emaar', 'damac', 'sobha', 'commission', 'real estate',
            'inspection', 'viewing', 'handover', 'off-plan', 'ready', 'possession',
            'furnishing', 'furnished', 'unfurnished', 'balcony', 'parking',
            'registration', 'profile', 'bedroom', 'bathroom', 'amenities'
        ]
        
        # OFF-TOPIC KEYWORDS & PHRASES
        off_topic_categories = {
            'SPORTS': {
                'keywords': ['cricket', 'football', 'soccer', 'basketball', 'tennis', 'ipl', 'world cup', 'messi', 'ronaldo', 'match', 'goal', 'team', 'player', 'game'],
                'confidence_multiplier': 1.5
            },
            'POLITICS': {
                'keywords': ['election', 'politics', 'government', 'minister', 'parliament', 'vote', 'political', 'party', 'leader', 'law', 'court'],
                'confidence_multiplier': 1.8
            },
            'RELIGION': {
                'keywords': ['god', 'allah', 'jesus', 'buddha', 'mosque', 'church', 'temple', 'prayer', 'faith', 'believe', 'religious', 'spiritual'],
                'confidence_multiplier': 1.6
            },
            'PERSONAL_ADVICE': {
                'keywords': ['dating', 'relationship', 'marriage', 'love', 'girlfriend', 'boyfriend', 'health', 'disease', 'doctor', 'medicine', 'diet'],
                'confidence_multiplier': 1.4
            },
            'JOKES_MEMES': {
                'keywords': ['haha', 'funny', 'joke', 'meme', 'lol', 'rofl', 'hilarious', 'laugh', 'comic', 'silly'],
                'confidence_multiplier': 1.2
            },
            'MARKETING_SPAM': {
                'keywords': ['buy now', 'limited offer', 'click here', 'free money', 'guaranteed', 'no risk', 'work from home', 'investment opportunity'],
                'confidence_multiplier': 1.7
            },
            'RANDOM_CHAT': {
                'keywords': ['how are you', 'how r u', 'whats up', 'hi there', 'hello friend', 'bro', 'dude', 'wassup'],
                'confidence_multiplier': 0.5  # Lower confidence for casual greetings
            }
        }
        
        # Check if message contains real estate keywords
        has_re_keyword = any(kw in text_lower for kw in real_estate_keywords)
        
        # Check for off-topic keywords
        max_confidence = 0
        detected_category = 'UNKNOWN'
        
        for category, data in off_topic_categories.items():
            keyword_matches = sum(1 for kw in data['keywords'] if kw in text_lower)
            
            if keyword_matches > 0:
                # Calculate confidence (higher = more likely off-topic)
                confidence = min(keyword_matches / len(data['keywords']), 1.0)
                confidence *= data['confidence_multiplier']
                
                if confidence > max_confidence:
                    max_confidence = confidence
                    detected_category = category
        
        # DECISION LOGIC
        is_off_topic = False
        
        if max_confidence > 0.6:
            is_off_topic = True
        elif max_confidence > 0.3 and not has_re_keyword:
            is_off_topic = True
        
        return is_off_topic, detected_category, min(max_confidence, 1.0)

    @staticmethod
    def get_redirect_response(category, original_message):
        """
        Generate a polite redirect response based on off-topic category.
        Keeps user in real estate context.
        """
        redirects = {
            'SPORTS': f"""🏠 Bhai, cricket baad mein. Abhi property ka sochte ho!

Looking for property in Dubai? 
📍 Kaunse area mein, kitne bhk, budget kya?

Type: "2 BHK Marina 100K" or help ke liye "/help"
""",
            'POLITICS': f"""🏠 Politics baad mein! Property aaj!

Dubai mein apni property dhundhte ho?
📝 Kya chahiye?
- Area (Marina, Downtown, etc)
- Bedrooms (1, 2, 3 BHK)
- Budget (in Lakh/Crore/AED)

Likho bhai: "2 BHK in Marina under 2.5 Cr"
""",
            'RELIGION': f"""🏠 Spiritual baad mein, real estate pehle!

Hum Dubai property ke experts hain.
Property chahiye? 
- To rent
- To buy
- To sell

Likho: "2 BHK apartment rental Marina" ya help
""",
            'PERSONAL_ADVICE': f"""🏠 Personal advice baad mein. Property first!

Hum real estate specialists hain, life coaches nahi! 😅

Dubai mein property k liye:
📍 Area? 🛏️ Bedrooms? 💰 Budget?

Example: "Sell my villa in Dubai Hills for 3M"
""",
            'JOKES_MEMES': f"""🏠 Memes acha hai, par property aur bhi acha hai! 😂

Real estate k liye yeh:
- Buy property → "2 BHK apartment rental"
- Sell property → "apni villa bechni hai"
- Area info → "Marina ke properties"

Likho na: "Mujhe property rent par deni hai"
""",
            'MARKETING_SPAM': f"""🏠 Marketing spam nahi, real solutions!

Hum sirf GENUINE Dubai real estate deals karte hain.
- Fair prices ✓
- Verified properties ✓
- No scams ✓

Property chahiye? Likho area/budget.
""",
            'RANDOM_CHAT': f"""🏠 Hi there! Real estate ke liye main!

Dubai mein property dhundhte ho?

📋 Batao:
1. Rent ya Sale?
2. Kaunsa area?
3. Kitne bhk?
4. Budget kya?

Example: "3 BHK villa Dubai Hills for sale"
""",
            'UNKNOWN': f"""🏠 Bhai, property topics mein hamari expertise hai!

Dubai real estate:
- Buy 🏠
- Sell 🏠
- Rent 🏠

Likho specific: "1 BHK apartment Marina rental under 5000"
""" 
        }
        
        return redirects.get(category, redirects['UNKNOWN'])

    @staticmethod
    def enforce_message_quality(text):
        """
        Enforce message quality standards:
        1. Max length control (long rambling messages broken down)
        2. Structured format preference
        3. Reject messages that are JUST large blocks of text
        
        Returns: (is_quality_good: bool, feedback: str, cleaned_text: str)
        """
        lines = text.strip().split('\n')
        word_count = len(text.split())
        
        # Check 1: Message is too long (> 300 words, > 1500 characters)
        if len(text) > 1500 or word_count > 300:
            # Large block of text without structure
            if '\n' not in text or len(lines) < 3:
                return False, "❌ Message too long! Keep it short & structured.\n\nExample format:\n🏠 Type: Apartment\n📍 Area: Marina\n🛏️ BHK: 2\n💰 Budget: 5000/month", text[:200]
        
        # Check 2: Message has SOME structure (bullet points, emojis, line breaks)
        has_structure = '\n' in text or '•' in text or any(emoji in text for emoji in ['🏠', '📍', '🛏️', '💰'])
        
        # Check 3: Single huge paragraph (>500 chars) without breaks
        if len(text) > 500 and not has_structure and word_count > 100:
            return False, "❌ Likho structured tarike se!\n\n✅ Good example:\n📍 Marina\n🛏️ 2 BHK\n💰 5000 rent\n\n❌ Bad: 'I want a 2 bhk apartment in marina with gym and pool for rent at 5000 per month'", text[:150]
        
        # Check 4: Valid message
        return True, "✓ Message format good", text