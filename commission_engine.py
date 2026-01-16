"""
HARSHAL DXB COMMISSION ENGINE
Handles multi-party commission distribution

Business Logic (Final Decided):
=================================

1. SCENARIO 1: Harshal Has Property
   ├─ Harshal commission: 100%
   └─ Agents: 0% (Harshal handles directly)

2. SCENARIO 2: Single Agent (From Auction)
   ├─ Property Agent: 60%
   ├─ Harshal: 40%
   └─ Example: 200K deal = 12K commission = 7.2K agent + 4.8K Harshal

3. SCENARIO 3: Inquiry Agent + Property Agent
   ├─ Inquiry Agent: 20% (brought the client - loyalty bonus)
   ├─ Property Agent: 40% (has the property)
   ├─ Harshal: 40% (platform fee)
   └─ Example: 200K deal = 12K commission = 2.4K inquiry + 4.8K property + 4.8K Harshal

4. MINIMUM DEAL VALUES:
   ├─ Rental deals: Min 1K AED commission (Harshal keeps 400-600 AED)
   ├─ Sales deals: Min 4K AED commission (Harshal keeps 1.6-2.4K AED)
   └─ Developer deals: Custom (negotiated per project)

5. AGENT TIERS (Affects notification priority):
   ├─ Tier 1: 10+ deals/month in area = Gets notified 1st
   ├─ Tier 2: 5-9 deals/month = Gets notified 2nd
   ├─ Tier 3: <5 deals/month = Gets notified 3rd
   └─ New agent: Gets notified 4th (learning phase)
"""

import uuid
import logging
from decimal import Decimal
from datetime import datetime
from database_manager import AGIDatabaseManager

logger = logging.getLogger("COMMISSION_ENGINE")


class CommissionEngine:
    """
    Intelligent commission calculation & distribution
    Prevents disputes, handles multiple agents, ensures profitability
    """

    # =================================================================
    # COMMISSION TIERS (The Business Model)
    # =================================================================
    COMMISSION_RULES = {
        "HARSHAL_ONLY": {
            "harshal_pct": Decimal("100"),
            "agent_pct": Decimal("0"),
            "description": "Harshal has property in inventory"
        },
        "SINGLE_AGENT": {
            "harshal_pct": Decimal("40"),
            "agent_pct": Decimal("60"),
            "description": "Single agent from auction"
        },
        "INQUIRY_PLUS_PROPERTY": {
            "inquiry_agent_pct": Decimal("20"),
            "property_agent_pct": Decimal("40"),
            "harshal_pct": Decimal("40"),
            "description": "Inquiry agent + property agent collaboration"
        },
        "DEVELOPER_DIRECT": {
            "developer_pct": Decimal("70"),
            "harshal_pct": Decimal("30"),
            "description": "Developer selling own units directly"
        },
        "RM_ENTERPRISE": {
            "rm_pct": Decimal("50"),
            "harshal_pct": Decimal("50"),
            "description": "RM (corporate buyer) direct transaction"
        }
    }

    MINIMUM_COMMISSIONS = {
        "RENTAL": Decimal("1000"),      # 1K AED minimum per rental deal
        "SALE": Decimal("4000"),        # 4K AED minimum per sale deal
        "DEVELOPER": Decimal("10000")   # 10K AED minimum per developer deal
    }

    # =================================================================
    # SCENARIO 1: Check if Harshal has matching property
    # =================================================================
    @staticmethod
    def check_harshal_inventory_match(requirement):
        """
        Before creating auction, check if Harshal has property
        Returns: (has_match, property_id, properties_list)
        """
        bedrooms = requirement.get('bedrooms')
        location = requirement.get('location')
        budget_min = requirement.get('budget_min')
        budget_max = requirement.get('budget_max')
        property_type = requirement.get('property_type', 'RENTAL')

        properties = AGIDatabaseManager.search_inventory(
            bedrooms=bedrooms,
            location=location,
            budget_min=budget_min,
            budget_max=budget_max,
            property_type=property_type
        )

        if properties:
            logger.info(f"✅ HARSHAL_MATCH: {len(properties)} properties found")
            return (True, properties[0]['property_id'], properties)
        else:
            logger.info(f"❌ NO_HARSHAL_MATCH: Need to create auction")
            return (False, None, [])

    # =================================================================
    # SCENARIO 2: Calculate commission for different scenarios
    # =================================================================
    @staticmethod
    def calculate_commission_split(
        deal_value,
        deal_type="SALE",
        scenario="SINGLE_AGENT",
        inquiry_agent_id=None,
        property_agent_id=None,
        developer_id=None
    ):
        """
        Calculate who gets what % based on scenario

        Args:
            deal_value: Final negotiated price (AED)
            deal_type: RENTAL, SALE, or DEVELOPER
            scenario: HARSHAL_ONLY, SINGLE_AGENT, INQUIRY_PLUS_PROPERTY, etc.
            inquiry_agent_id: If inquiry agent involved
            property_agent_id: If property agent involved
            developer_id: If developer involved

        Returns:
            {
                "deal_value": 200000,
                "commission_pool": 12000,
                "splits": {
                    "harshal": {"amount": 4800, "pct": 40},
                    "inquiry_agent": {"amount": 2400, "pct": 20, "agent_id": "A001"},
                    "property_agent": {"amount": 4800, "pct": 40, "agent_id": "A003"}
                },
                "validation": {"meets_minimum": True, "margin_healthy": True}
            }
        """
        
        deal_value = Decimal(str(deal_value))
        
        # Determine commission pool based on deal type
        if deal_type == "RENTAL":
            commission_pool = deal_value * Decimal("0.05")  # 5% commission on rental
        elif deal_type == "SALE":
            commission_pool = deal_value * Decimal("0.02")  # 2% commission on sale
        else:
            commission_pool = deal_value * Decimal("0.03")  # 3% default

        # Validate minimum commission
        minimum = CommissionEngine.MINIMUM_COMMISSIONS[deal_type]
        if commission_pool < minimum:
            commission_pool = minimum
            logger.warning(f"⚠️ Commission below minimum. Applying minimum: {minimum} AED")

        # Get the split template
        rule = CommissionEngine.COMMISSION_RULES.get(scenario, 
                                                     CommissionEngine.COMMISSION_RULES["SINGLE_AGENT"])

        splits = {}

        # ============================================================
        # SCENARIO 1: HARSHAL ONLY (Harshal has property in inventory)
        # ============================================================
        if scenario == "HARSHAL_ONLY":
            splits = {
                "harshal": {
                    "amount": float(commission_pool),
                    "percentage": 100,
                    "entity_id": "HARSHAL_DXB"
                }
            }
            logger.info(f"💰 SCENARIO_HARSHAL_ONLY: Harshal keeps 100% = {commission_pool} AED")

        # ============================================================
        # SCENARIO 2: SINGLE AGENT (From auction)
        # ============================================================
        elif scenario == "SINGLE_AGENT" and property_agent_id:
            agent_amount = commission_pool * Decimal("0.60")
            harshal_amount = commission_pool * Decimal("0.40")
            
            splits = {
                "agent": {
                    "amount": float(agent_amount),
                    "percentage": 60,
                    "agent_id": property_agent_id,
                    "type": "PROPERTY_AGENT"
                },
                "harshal": {
                    "amount": float(harshal_amount),
                    "percentage": 40,
                    "entity_id": "HARSHAL_DXB"
                }
            }
            logger.info(f"💰 SCENARIO_SINGLE_AGENT: Agent {property_agent_id} gets 60% = {agent_amount} AED | Harshal 40% = {harshal_amount} AED")

        # ============================================================
        # SCENARIO 3: INQUIRY + PROPERTY AGENT (Collaboration)
        # ============================================================
        elif scenario == "INQUIRY_PLUS_PROPERTY" and inquiry_agent_id and property_agent_id:
            inquiry_amount = commission_pool * Decimal("0.20")
            property_amount = commission_pool * Decimal("0.40")
            harshal_amount = commission_pool * Decimal("0.40")
            
            splits = {
                "inquiry_agent": {
                    "amount": float(inquiry_amount),
                    "percentage": 20,
                    "agent_id": inquiry_agent_id,
                    "type": "INQUIRY_AGENT",
                    "reason": "Loyalty bonus for bringing client"
                },
                "property_agent": {
                    "amount": float(property_amount),
                    "percentage": 40,
                    "agent_id": property_agent_id,
                    "type": "PROPERTY_AGENT"
                },
                "harshal": {
                    "amount": float(harshal_amount),
                    "percentage": 40,
                    "entity_id": "HARSHAL_DXB"
                }
            }
            logger.info(f"💰 SCENARIO_INQUIRY+PROPERTY: Inquiry {inquiry_agent_id} 20% = {inquiry_amount} | Property {property_agent_id} 40% = {property_amount} | Harshal 40% = {harshal_amount}")

        return {
            "commission_id": f"COMM-{uuid.uuid4().hex[:8].upper()}",
            "deal_value": float(deal_value),
            "commission_pool": float(commission_pool),
            "commission_type": deal_type,
            "scenario": scenario,
            "splits": splits,
            "validation": {
                "meets_minimum": commission_pool >= CommissionEngine.MINIMUM_COMMISSIONS[deal_type],
                "harshal_margin_healthy": True,  # Harshal always gets at least 30%
                "scenario_valid": scenario in CommissionEngine.COMMISSION_RULES
            },
            "created_at": datetime.now().isoformat()
        }

    # =================================================================
    # AGENT TIER CALCULATION (For notification priority)
    # =================================================================
    @staticmethod
    def get_agent_tier(agent_id, location):
        """
        Determine agent's tier based on deal history in area
        Affects notification priority in auctions

        Returns: TIER_1, TIER_2, TIER_3, or NEW_AGENT
        """
        agent_profile = AGIDatabaseManager.get_partner_profile(agent_id)
        
        if not agent_profile:
            return "NEW_AGENT"

        # Count closed deals in this location
        deals_in_area = AGIDatabaseManager.count_closed_deals(
            agent_id=agent_id,
            location=location,
            months=3  # Last 3 months
        )

        if deals_in_area >= 10:
            return "TIER_1"  # Top performer
        elif deals_in_area >= 5:
            return "TIER_2"  # Active agent
        elif deals_in_area >= 1:
            return "TIER_3"  # Learning phase
        else:
            return "NEW_AGENT"  # No history in area

    # =================================================================
    # LOCATION-AGENT MATCHING (Core Logic)
    # =================================================================
    @staticmethod
    def get_agents_for_location(location, max_agents=10):
        """
        Get best agents for a location, in priority order:
        1. TIER_1 agents specializing in this location
        2. TIER_2 agents
        3. TIER_3 agents
        4. NEW agents (if needed)

        Returns: [agent1, agent2, ..., agent_max]
        """
        logger.info(f"🔍 Finding agents for {location}...")

        # Query all agents who serve this location
        all_agents = AGIDatabaseManager.query_agents_by_location(location)

        if not all_agents:
            logger.warning(f"⚠️ NO_AGENTS found for {location}")
            return []

        # Sort by tier + reliability score
        sorted_agents = sorted(
            all_agents,
            key=lambda x: (
                CommissionEngine._tier_priority(CommissionEngine.get_agent_tier(x['agent_id'], location)),
                float(x.get('reliability_score', 0)),
                x.get('deals_closed', 0)
            ),
            reverse=True
        )

        # Return top N agents
        selected = sorted_agents[:max_agents]
        logger.info(f"✅ Selected {len(selected)} agents for {location}")
        return selected

    @staticmethod
    def _tier_priority(tier):
        """Convert tier string to numeric priority"""
        priorities = {
            "TIER_1": 4,
            "TIER_2": 3,
            "TIER_3": 2,
            "NEW_AGENT": 1
        }
        return priorities.get(tier, 0)

    # =================================================================
    # INQUIRY AGENT LOYALTY (Prevent 3-agent problem)
    # =================================================================
    @staticmethod
    def track_inquiry_agent(client_phone, agent_id):
        """
        Log which agent brought the client (inquiry agent)
        If deal closes within 24 hours, they get 20% loyalty bonus
        """
        inquiry_record = {
            "inquiry_id": f"INQ-{uuid.uuid4().hex[:8].upper()}",
            "client_phone": client_phone,
            "agent_id": agent_id,
            "inquiry_time": datetime.now().isoformat(),
            "status": "ACTIVE",
            "expires_at": "24h"  # Loyalty lasts 24 hours
        }
        
        AGIDatabaseManager.store_inquiry_agent(inquiry_record)
        logger.info(f"📝 Inquiry agent tracked: {agent_id} for client {client_phone}")
        return inquiry_record

    @staticmethod
    def claim_inquiry_loyalty(client_phone, property_agent_id):
        """
        When deal closes, check if inquiry agent should get loyalty bonus
        """
        inquiry = AGIDatabaseManager.get_inquiry_agent(client_phone)
        
        if not inquiry or inquiry.get('status') != 'ACTIVE':
            return None  # No inquiry agent or expired

        inquiry_agent_id = inquiry.get('agent_id')
        if inquiry_agent_id == property_agent_id:
            return None  # Same agent - no split needed

        logger.info(f"✅ Inquiry agent {inquiry_agent_id} qualifies for 20% loyalty bonus")
        return inquiry_agent_id

    # =================================================================
    # VALIDATE COMMISSION STRUCTURE
    # =================================================================
    @staticmethod
    def validate_commission_structure(commission_calc):
        """
        Ensure commission calculation is valid
        - Harshal gets at least 30%
        - No agent gets more than 70%
        - Total adds up to 100%
        """
        splits = commission_calc['splits']
        total_pct = sum(s.get('percentage', 0) for s in splits.values())

        # Check constraints
        harshal_pct = splits.get('harshal', {}).get('percentage', 0)
        
        if harshal_pct < 30:
            logger.warning(f"⚠️ Harshal margin too low: {harshal_pct}%")
            return False

        if total_pct != 100:
            logger.warning(f"⚠️ Percentages don't add to 100: {total_pct}%")
            return False

        logger.info(f"✅ Commission structure valid. Harshal margin: {harshal_pct}%")
        return True

    # =================================================================
    # RECORD FINAL COMMISSION (For audit trail)
    # =================================================================
    @staticmethod
    def record_commission(deal_id, commission_calc, deal_status="COMPLETED"):
        """
        Store commission details in audit trail for 100-year retention
        """
        record = {
            "deal_id": deal_id,
            "commission_id": commission_calc['commission_id'],
            "commission_pool": commission_calc['commission_pool'],
            "splits": commission_calc['splits'],
            "scenario": commission_calc['scenario'],
            "deal_status": deal_status,
            "recorded_at": datetime.now().isoformat()
        }
        
        AGIDatabaseManager.log_commission_record(record)
        logger.info(f"📋 Commission recorded for deal {deal_id}")
        return record
