"""
CLIENT INTAKE QUESTIONNAIRE SYSTEM
Guides clients through structured questions before showing properties

Flow:
1. Client messages: "2 BHK Marina"
2. System: "Pehle kuch saval, fir perfect match dikhaunga!"
3. Q1: Rental or Buy?
4. Q2: Own use or Investment?
5. Q3: Timeline?
6. Q4: Preferred locations?
7. Q5: Budget?
8. Match with inventory → Show properties
"""

import logging
from enum import Enum
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger("CLIENT_INTAKE")


class ClientIntakeFlow:
    """
    5-Question Questionnaire to qualify clients properly
    Prevents wrong matches, saves time, improves conversion
    """

    # State machine for tracking where client is in questionnaire
    INTAKE_STATES = {
        "INITIAL": 0,           # Just messaged
        "Q1_RENTAL_ASKED": 1,   # Asked: Rental or Buy?
        "Q2_PURPOSE_ASKED": 2,  # Asked: Own or Investment?
        "Q3_TIMELINE_ASKED": 3, # Asked: Timeline?
        "Q4_LOCATION_ASKED": 4, # Asked: Preferred locations?
        "Q5_BUDGET_ASKED": 5,   # Asked: Budget?
        "COMPLETE": 6           # All answers collected
    }

    # ===================================================================
    # QUESTION 1: RENTAL OR BUY
    # ===================================================================
    @staticmethod
    def q1_rental_or_buy():
        """First question to understand intent"""
        return {
            "question_id": "Q1",
            "question_text": "Rental chahiye ya Buy karna hai? 🏠",
            "options": {
                "1": {
                    "display": "Rental (Monthly/Yearly)",
                    "value": "RENTAL",
                    "icon": "🔑"
                },
                "2": {
                    "display": "Buy (Own Property)",
                    "value": "BUY",
                    "icon": "🏡"
                }
            },
            "expected_responses": ["1", "2", "rental", "buy", "RENTAL", "BUY"],
            "help_text": "Just reply: 1 for Rental, 2 for Buy (or type the word)"
        }

    # ===================================================================
    # QUESTION 2: OWN USE OR INVESTMENT
    # ===================================================================
    @staticmethod
    def q2_own_or_investment():
        """Understand if personal use or investment strategy"""
        return {
            "question_id": "Q2",
            "question_text": "Apne raho ge ya investment ke liye? 💼",
            "options": {
                "1": {
                    "display": "Own Use (Main rhungi)",
                    "value": "OWN_USE",
                    "icon": "👨‍👩‍👧‍👦"
                },
                "2": {
                    "display": "Investment (Rental/ROI ke liye)",
                    "value": "INVESTMENT",
                    "icon": "💰"
                }
            },
            "expected_responses": ["1", "2", "own", "investment", "OWN_USE", "INVESTMENT"],
            "help_text": "1 for Own Use, 2 for Investment"
        }

    # ===================================================================
    # QUESTION 3: TIMELINE
    # ===================================================================
    @staticmethod
    def q3_timeline():
        """Understand urgency and closing timeline"""
        return {
            "question_id": "Q3",
            "question_text": "Timeline kya hai? ⏰\n\n1: Immediate (2-4 hafta)\n2: Soon (1-2 mahine)\n3: Flex (3-6 mahine)",
            "options": {
                "1": {
                    "display": "Immediate (2-4 weeks)",
                    "value": "IMMEDIATE",
                    "icon": "⚡"
                },
                "2": {
                    "display": "Soon (1-2 months)",
                    "value": "SOON",
                    "icon": "🚀"
                },
                "3": {
                    "display": "Flexible (3-6 months)",
                    "value": "FLEXIBLE",
                    "icon": "📅"
                }
            },
            "expected_responses": ["1", "2", "3", "immediate", "soon", "flex"],
            "help_text": "1 for Immediate, 2 for Soon, 3 for Flexible"
        }

    # ===================================================================
    # QUESTION 4: PREFERRED LOCATIONS
    # ===================================================================
    @staticmethod
    def q4_locations():
        """Where in Dubai does client want to look"""
        return {
            "question_id": "Q4",
            "question_text": "Dubai mein kaun se areas mein dekhna hai? 📍\n\nExample: Marina, Downtown, Business Bay, etc.",
            "options": {
                # Top 15 Dubai areas
                "1": {"display": "Marina", "value": "MARINA"},
                "2": {"display": "Downtown", "value": "DOWNTOWN"},
                "3": {"display": "Business Bay", "value": "BUSINESS_BAY"},
                "4": {"display": "JBR (Jumeirah Beach Residence)", "value": "JBR"},
                "5": {"display": "Deira", "value": "DEIRA"},
                "6": {"display": "Bur Dubai", "value": "BUR_DUBAI"},
                "7": {"display": "Al Barsha", "value": "AL_BARSHA"},
                "8": {"display": "Jumeirah", "value": "JUMEIRAH"},
                "9": {"display": "Palm Jumeirah", "value": "PALM"},
                "10": {"display": "Emirates Hills", "value": "EMIRATES_HILLS"},
                "11": {"display": "Arabian Ranches", "value": "ARABIAN_RANCHES"},
                "12": {"display": "Dubai Hills Estate", "value": "DUBAI_HILLS"},
                "13": {"display": "MBR City", "value": "MBR_CITY"},
                "14": {"display": "Dubai South", "value": "DUBAI_SOUTH"},
                "15": {"display": "Flexible (Any area)", "value": "FLEXIBLE"}
            },
            "expected_responses": "free_text",  # Client can type area names
            "help_text": "Type area names (can mention multiple: Marina, Downtown, etc.)",
            "allow_multiple": True
        }

    # ===================================================================
    # QUESTION 5: BUDGET
    # ===================================================================
    @staticmethod
    def q5_budget():
        """Understand budget to filter properties"""
        return {
            "question_id": "Q5",
            "question_text": "Budget kya hai (Monthly rent ya Buy price in AED)? 💰\n\nExample: 3000 rental, 500000 buy",
            "options": {
                "1": {"display": "< 2000/month (Budget)", "value": "0-2000"},
                "2": {"display": "2000-4000/month (Standard)", "value": "2000-4000"},
                "3": {"display": "4000-7000/month (Premium)", "value": "4000-7000"},
                "4": {"display": "> 7000/month (Luxury)", "value": "7000+"},
                "5": {"display": "< 200K (Budget Buy)", "value": "0-200000"},
                "6": {"display": "200K-500K (Standard Buy)", "value": "200000-500000"},
                "7": {"display": "500K-1M (Premium Buy)", "value": "500000-1000000"},
                "8": {"display": "> 1M (Luxury Buy)", "value": "1000000+"}
            },
            "expected_responses": "free_text",  # Client enters exact budget
            "help_text": "Type exact amount or select range",
            "allow_freetext": True
        }

    # ===================================================================
    # PARSE ANSWERS
    # ===================================================================
    @staticmethod
    def parse_q1_answer(user_response):
        """Parse answer to Q1: Rental or Buy"""
        response = user_response.upper().strip()
        
        if response in ["1", "RENTAL", "RENT"]:
            return {"answer": "RENTAL", "valid": True}
        elif response in ["2", "BUY", "SALE"]:
            return {"answer": "BUY", "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Please reply 1 for Rental or 2 for Buy"}

    @staticmethod
    def parse_q2_answer(user_response):
        """Parse answer to Q2: Own or Investment"""
        response = user_response.upper().strip()
        
        if response in ["1", "OWN", "OWN_USE", "PERSONAL"]:
            return {"answer": "OWN_USE", "valid": True}
        elif response in ["2", "INVESTMENT", "INVEST", "ROI"]:
            return {"answer": "INVESTMENT", "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Please reply 1 for Own Use or 2 for Investment"}

    @staticmethod
    def parse_q3_answer(user_response):
        """Parse answer to Q3: Timeline"""
        response = user_response.upper().strip()
        
        if response in ["1", "IMMEDIATE", "URGENT", "QUICK"]:
            return {"answer": "IMMEDIATE", "valid": True}
        elif response in ["2", "SOON", "MONTH"]:
            return {"answer": "SOON", "valid": True}
        elif response in ["3", "FLEX", "FLEXIBLE", "LATER"]:
            return {"answer": "FLEXIBLE", "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Please reply 1, 2, or 3"}

    @staticmethod
    def parse_q4_answer(user_response):
        """Parse answer to Q4: Locations (free text, multiple allowed)"""
        areas_list = [a.strip().upper() for a in user_response.split(',')]
        
        valid_areas = {
            "MARINA": "MARINA",
            "DOWNTOWN": "DOWNTOWN",
            "BUSINESS BAY": "BUSINESS_BAY",
            "JBR": "JBR",
            "DEIRA": "DEIRA",
            "BUR DUBAI": "BUR_DUBAI",
            "BARSHA": "AL_BARSHA",
            "JUMEIRAH": "JUMEIRAH",
            "PALM": "PALM",
            "EMIRATES HILLS": "EMIRATES_HILLS",
            "ARABIAN RANCHES": "ARABIAN_RANCHES",
            "DUBAI HILLS": "DUBAI_HILLS",
            "MBR CITY": "MBR_CITY",
            "DUBAI SOUTH": "DUBAI_SOUTH",
            "FLEXIBLE": "FLEXIBLE",
            "ANY": "FLEXIBLE"
        }
        
        matched_areas = []
        for area in areas_list:
            if area in valid_areas:
                matched_areas.append(valid_areas[area])
        
        if matched_areas:
            return {"answer": matched_areas, "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Areas not recognized. Try: Marina, Downtown, JBR, etc."}

    @staticmethod
    def parse_q5_answer(user_response):
        """Parse answer to Q5: Budget (flexible format)"""
        response = user_response.strip()
        
        # Try to extract numeric value
        import re
        numbers = re.findall(r'\d+', response)
        
        if numbers:
            budget = int(numbers[0])
            return {"answer": budget, "valid": True, "currency": "AED"}
        else:
            return {"answer": None, "valid": False, "error": "Please enter a number (e.g., 5000, 500000)"}

    # ===================================================================
    # BUILD COMPLETE PROFILE FROM ANSWERS
    # ===================================================================
    @staticmethod
    def build_client_profile(client_phone, q1, q2, q3, q4, q5):
        """
        Combine all 5 answers into client search profile
        Ready for matching with inventory
        """
        profile = {
            "client_phone": client_phone,
            "created_at": datetime.now().isoformat(),
            "intake_complete": True,
            
            # Answers
            "rental_or_buy": q1["answer"],
            "own_or_investment": q2["answer"],
            "timeline": q3["answer"],
            "preferred_locations": q4["answer"],  # List of areas
            "budget": q5["answer"],  # Numeric value in AED
            
            # Derived fields
            "property_type": "RENTAL" if q1["answer"] == "RENTAL" else "SALE",
            "client_type": "INVESTOR" if q2["answer"] == "INVESTMENT" else "END_USER",
            "urgency": q3["answer"],
            
            # Calculated ranges
            "budget_min": ClientIntakeFlow._get_budget_min(q1["answer"], q5["answer"]),
            "budget_max": ClientIntakeFlow._get_budget_max(q1["answer"], q5["answer"]),
        }
        
        logger.info(f"✅ Client profile built for {client_phone}")
        logger.info(f"   Type: {profile['rental_or_buy']} | Use: {profile['own_or_investment']} | Budget: {profile['budget']} AED")
        
        return profile

    @staticmethod
    def _get_budget_min(rental_or_buy, budget):
        """Calculate min budget (±20% flexibility)"""
        min_budget = Decimal(str(budget)) * Decimal("0.8")
        return float(min_budget)

    @staticmethod
    def _get_budget_max(rental_or_buy, budget):
        """Calculate max budget (±20% flexibility)"""
        max_budget = Decimal(str(budget)) * Decimal("1.2")
        return float(max_budget)

    # ===================================================================
    # NEXT QUESTION IN FLOW
    # ===================================================================
    @staticmethod
    def get_next_question(current_state):
        """
        Get next question based on current state
        Returns question dict or None if intake complete
        """
        if current_state == ClientIntakeFlow.INTAKE_STATES["INITIAL"]:
            return ClientIntakeFlow.q1_rental_or_buy()
        elif current_state == ClientIntakeFlow.INTAKE_STATES["Q1_RENTAL_ASKED"]:
            return ClientIntakeFlow.q2_own_or_investment()
        elif current_state == ClientIntakeFlow.INTAKE_STATES["Q2_PURPOSE_ASKED"]:
            return ClientIntakeFlow.q3_timeline()
        elif current_state == ClientIntakeFlow.INTAKE_STATES["Q3_TIMELINE_ASKED"]:
            return ClientIntakeFlow.q4_locations()
        elif current_state == ClientIntakeFlow.INTAKE_STATES["Q4_LOCATION_ASKED"]:
            return ClientIntakeFlow.q5_budget()
        else:
            return None  # Intake complete

    # ===================================================================
    # FLOW CONTROL
    # ===================================================================
    @staticmethod
    def advance_state(current_state):
        """Move to next state in intake flow"""
        state_progression = [
            ClientIntakeFlow.INTAKE_STATES["INITIAL"],
            ClientIntakeFlow.INTAKE_STATES["Q1_RENTAL_ASKED"],
            ClientIntakeFlow.INTAKE_STATES["Q2_PURPOSE_ASKED"],
            ClientIntakeFlow.INTAKE_STATES["Q3_TIMELINE_ASKED"],
            ClientIntakeFlow.INTAKE_STATES["Q4_LOCATION_ASKED"],
            ClientIntakeFlow.INTAKE_STATES["Q5_BUDGET_ASKED"],
            ClientIntakeFlow.INTAKE_STATES["COMPLETE"]
        ]
        
        try:
            current_index = state_progression.index(current_state)
            return state_progression[current_index + 1]
        except (ValueError, IndexError):
            return ClientIntakeFlow.INTAKE_STATES["COMPLETE"]
