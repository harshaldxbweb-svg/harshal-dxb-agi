"""
AGENT REGISTRATION SYSTEM
WhatsApp-based onboarding for agents, agencies, developers, RMs

Registration entities:
- AGENT: Individual real estate agent
- AGENCY: Company with multiple agents
- DEVELOPER: Project developer/property owner
- RM: Relationship manager (corporate clients)
"""

import logging
from enum import Enum
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger("AGENT_REGISTRATION")


class EntityType(Enum):
    """Types of entities that can register"""
    AGENT = "AGENT"
    AGENCY = "AGENCY"
    DEVELOPER = "DEVELOPER"
    RM = "RM"


class AgentRegistrationFlow:
    """
    5-Step Registration Flow on WhatsApp
    Guides entities through onboarding
    """

    # Registration states
    REGISTRATION_STATES = {
        "INITIAL": 0,           # User says "register"
        "Q1_ENTITY_TYPE_ASKED": 1,      # What are you? Agent/Agency/Developer/RM?
        "Q2_BASIC_INFO_ASKED": 2,       # Name, phone, email
        "Q3_AREA_SELECTION_ASKED": 3,   # Which areas do you work in?
        "Q4_VERIFICATION_ASKED": 4,     # RERA ID, company docs
        "Q5_TERMS_AGREED": 5,           # Accept commission terms
        "COMPLETE": 6                   # Registration done, pending admin approval
    }

    # ===================================================================
    # QUESTION 1: WHAT ARE YOU?
    # ===================================================================
    @staticmethod
    def q1_entity_type():
        """First question: Type of entity"""
        return {
            "question_id": "Q1_REG",
            "question_text": "Tum kya ho? 👤\n\n1: Individual Agent\n2: Agency (Company)\n3: Developer (Projects)\n4: RM (Enterprise/Bulk Buyer)",
            "options": {
                "1": {
                    "display": "Individual Agent",
                    "value": EntityType.AGENT.value,
                    "icon": "👨‍💼"
                },
                "2": {
                    "display": "Agency/Company",
                    "value": EntityType.AGENCY.value,
                    "icon": "🏢"
                },
                "3": {
                    "display": "Developer/Project Owner",
                    "value": EntityType.DEVELOPER.value,
                    "icon": "🏗️"
                },
                "4": {
                    "display": "RM (Enterprise)",
                    "value": EntityType.RM.value,
                    "icon": "🤝"
                }
            },
            "expected_responses": ["1", "2", "3", "4", "AGENT", "AGENCY", "DEVELOPER", "RM"],
            "help_text": "Reply 1, 2, 3, or 4"
        }

    # ===================================================================
    # QUESTION 2: BASIC INFO
    # ===================================================================
    @staticmethod
    def q2_basic_info(entity_type):
        """Collect name, phone, email based on entity type"""
        
        if entity_type == EntityType.AGENT.value:
            question_text = "Apna details do:\nFull Name:"
        elif entity_type == EntityType.AGENCY.value:
            question_text = "Agency details:\nCompany Name:"
        elif entity_type == EntityType.DEVELOPER.value:
            question_text = "Developer details:\nProject/Company Name:"
        else:  # RM
            question_text = "RM details:\nName/Organization:"
        
        return {
            "question_id": "Q2_REG",
            "question_text": question_text,
            "entity_type": entity_type,
            "fields_required": ["name", "phone", "email"],
            "expected_responses": "free_text",
            "help_text": "Send: Name | Phone | Email"
        }

    # ===================================================================
    # QUESTION 3: AREA SELECTION
    # ===================================================================
    @staticmethod
    def q3_area_selection(entity_type):
        """Which areas does entity work in"""
        
        if entity_type == EntityType.AGENT.value:
            question_text = "Kaun se areas mein kam karte ho? 📍\n(Min 1, Max 3 areas)\n\nExample: Marina, Downtown, JBR"
        elif entity_type == EntityType.AGENCY.value:
            question_text = "Agency kis areas main operate karti hai? (Max 5)\n\nExample: Marina, Downtown, Deira, JBR, Business Bay"
        elif entity_type == EntityType.DEVELOPER.value:
            question_text = "Projects kis areas main ho? 📍\n\nExample: Downtown, Business Bay, Dubai Hills"
        else:  # RM
            question_text = "Kaun se areas mein focus karte ho?\n(Flexible selected if all Dubai)"
        
        return {
            "question_id": "Q3_REG",
            "question_text": question_text,
            "entity_type": entity_type,
            "available_areas": [
                "MARINA", "DOWNTOWN", "BUSINESS_BAY", "JBR", "DEIRA",
                "BUR_DUBAI", "AL_BARSHA", "JUMEIRAH", "PALM", "EMIRATES_HILLS",
                "ARABIAN_RANCHES", "DUBAI_HILLS", "MBR_CITY", "DUBAI_SOUTH"
            ],
            "max_areas": 5 if entity_type == EntityType.AGENCY.value else (3 if entity_type == EntityType.AGENT.value else 10),
            "expected_responses": "free_text_multiple",
            "help_text": "Type area names separated by comma"
        }

    # ===================================================================
    # QUESTION 4: VERIFICATION
    # ===================================================================
    @staticmethod
    def q4_verification(entity_type):
        """Verification documents based on entity type"""
        
        if entity_type == EntityType.AGENT.value:
            question_text = "Aapka RERA ID kya hai?\n(If local agent, type 'LOCAL' - we trust local dealers!)"
            required_docs = ["RERA_ID_OR_LOCAL"]
        
        elif entity_type == EntityType.AGENCY.value:
            question_text = "Agency ka RERA Certificate number:"
            required_docs = ["RERA_CERTIFICATE", "COMPANY_REGISTRATION"]
        
        elif entity_type == EntityType.DEVELOPER.value:
            question_text = "Developer ka registration number (Project ID, DLD registration):"
            required_docs = ["DLD_REGISTRATION", "PROJECT_LICENSE"]
        
        else:  # RM
            question_text = "RM ka company registration:\n(If individual, just say 'INDIVIDUAL')"
            required_docs = ["COMPANY_REG_OR_ID"]
        
        return {
            "question_id": "Q4_REG",
            "question_text": question_text,
            "entity_type": entity_type,
            "required_docs": required_docs,
            "expected_responses": "free_text",
            "help_text": "Send RERA ID, company number, or 'LOCAL'/'INDIVIDUAL'",
            "note": "All types accepted. RERA = instant approval, Local/Individual = 24hr admin review"
        }

    # ===================================================================
    # QUESTION 5: ACCEPT TERMS
    # ===================================================================
    @staticmethod
    def q5_commission_terms(entity_type):
        """Commission structure & terms"""
        
        if entity_type == EntityType.AGENT.value:
            commission_text = "Agent Commission: 60% of deal commission\nMin deal: 1K AED (rental), 4K AED (sale)\nFees: 0% (Harshal keeps it simple!)"
        
        elif entity_type == EntityType.AGENCY.value:
            commission_text = "Agency Commission: 50% (you split among agents)\nMin deal: 2K AED\nFees: 0% (Platform is commission-free)"
        
        elif entity_type == EntityType.DEVELOPER.value:
            commission_text = "Developer Commission: 70% of commission pool\nMin deal: 10K AED per unit\nYou keep 70%, Harshal 30% (platform fee)"
        
        else:  # RM
            commission_text = "RM Commission: 50% of commission pool\nMin deal: 5K AED\nYou + Harshal split 50-50 (transparent model)"
        
        question_text = f"{commission_text}\n\nAccept these terms? Reply YES to proceed"
        
        return {
            "question_id": "Q5_REG",
            "question_text": question_text,
            "entity_type": entity_type,
            "expected_responses": ["YES", "yes", "Y", "AGREE", "OK"],
            "help_text": "Reply YES to accept",
            "terms": {
                "breach_penalty": "Reliability score -10 points",
                "number_exchange": "BANNED (we're bridge forever)",
                "payment_timeline": "Within 7 days of deal close",
                "dispute_resolution": "Admin arbitration"
            }
        }

    # ===================================================================
    # PARSE ANSWERS
    # ===================================================================
    @staticmethod
    def parse_q1_answer(user_response):
        """Parse entity type"""
        response = user_response.upper().strip()
        
        mapping = {
            "1": EntityType.AGENT.value,
            "2": EntityType.AGENCY.value,
            "3": EntityType.DEVELOPER.value,
            "4": EntityType.RM.value,
            "AGENT": EntityType.AGENT.value,
            "AGENCY": EntityType.AGENCY.value,
            "DEVELOPER": EntityType.DEVELOPER.value,
            "RM": EntityType.RM.value
        }
        
        if response in mapping:
            return {"answer": mapping[response], "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Please reply 1, 2, 3, or 4"}

    @staticmethod
    def parse_q2_answer(user_response):
        """Parse name | phone | email"""
        parts = [p.strip() for p in user_response.split('|')]
        
        if len(parts) >= 3:
            return {
                "answer": {
                    "name": parts[0],
                    "phone": parts[1],
                    "email": parts[2]
                },
                "valid": True
            }
        else:
            return {
                "answer": None,
                "valid": False,
                "error": "Send: Name | Phone | Email (separated by |)"
            }

    @staticmethod
    def parse_q3_answer(user_response):
        """Parse area selections"""
        areas = [a.strip().upper() for a in user_response.split(',')]
        
        valid_areas = {
            "MARINA": "MARINA",
            "DOWNTOWN": "DOWNTOWN",
            "BUSINESS BAY": "BUSINESS_BAY",
            "JBR": "JBR",
            "DEIRA": "DEIRA",
            # ... etc
        }
        
        matched = [valid_areas.get(a, a) for a in areas if a]
        
        if matched:
            return {"answer": matched, "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Areas not recognized"}

    @staticmethod
    def parse_q4_answer(user_response):
        """Parse verification"""
        response = user_response.strip().upper()
        
        # Accept RERA ID, LOCAL, or any verification string
        if response in ["LOCAL", "INDIVIDUAL"] or len(response) > 3:
            return {"answer": response, "valid": True}
        else:
            return {"answer": None, "valid": False, "error": "Please provide verification info or type LOCAL"}

    @staticmethod
    def parse_q5_answer(user_response):
        """Parse YES/NO for terms"""
        response = user_response.upper().strip()
        
        if response in ["YES", "Y", "AGREE", "OK"]:
            return {"answer": True, "valid": True}
        else:
            return {"answer": False, "valid": False, "error": "Please reply YES to accept terms"}

    # ===================================================================
    # BUILD REGISTRATION PROFILE
    # ===================================================================
    @staticmethod
    def build_registration_profile(phone, q1, q2, q3, q4, q5):
        """Create entity profile from all answers"""
        
        profile = {
            "phone": phone,
            "entity_type": q1["answer"],
            "name": q2["answer"]["name"],
            "contact_phone": q2["answer"]["phone"],
            "email": q2["answer"]["email"],
            "areas_served": q3["answer"],
            "verification_id": q4["answer"],
            "terms_accepted": q5["answer"],
            
            # Metadata
            "registered_at": datetime.now().isoformat(),
            "status": "PENDING_ADMIN_APPROVAL",  # Admin reviews non-RERA agents
            "reliability_score": Decimal("100"),  # Start at 100, decrease for violations
            "deals_closed": 0,
            "last_active": datetime.now().isoformat()
        }
        
        # RERA agents get instant approval
        if q4["answer"] and "RERA" in q4["answer"].upper():
            profile["status"] = "ACTIVE"
            profile["approval_method"] = "AUTO_RERA"
            logger.info(f"✅ RERA agent {phone} AUTO-APPROVED")
        else:
            profile["approval_method"] = "MANUAL_ADMIN"
            logger.info(f"⏳ Local agent {phone} pending admin review")
        
        return profile

    # ===================================================================
    # COMPLETE REGISTRATION
    # ===================================================================
    @staticmethod
    def complete_registration(phone, profile):
        """
        Store registration in database
        Notify admin if needed
        """
        from database_manager import AGIDatabaseManager
        
        # Store in T_PARTNERS table
        AGIDatabaseManager.T_PARTNERS.put_item(Item=profile)
        
        logger.info(f"✅ Registration complete for {phone} ({profile['entity_type']})")
        
        if profile["status"] == "PENDING_ADMIN_APPROVAL":
            # Notify admin
            return {
                "status": "pending",
                "message": f"Registration received! Admin will approve within 24 hours. 👍",
                "reference": phone
            }
        else:
            # Instant activation
            return {
                "status": "active",
                "message": f"Welcome to Harshal! You're now LIVE. Start getting leads! 🚀",
                "areas": profile["areas_served"],
                "commission": "60% (agents)" if profile["entity_type"] == "AGENT" else "Custom"
            }
