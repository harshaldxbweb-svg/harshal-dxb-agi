import boto3
import uuid
import logging
import json
import os
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal

# --- HARSHAL DXB AGI: GLOBAL INFRASTRUCTURE ---
# Region-agnostic resource for Frankfurt (eu-central-1) support.
# No hardcoded sessions to prevent "Invalid Token" errors.
dynamodb = boto3.resource('dynamodb')

class AGIDatabaseManager:
    """
    LEVEL 5 AGI PERSISTENCE SYSTEM (Sovereign Edition v5.1):
    The 'Elephant Memory' of Harshal DXB. Handles 100-year audit trails, 
    Psychological archetypes, and the Market-Price Gatekeeper logic.
    """
    
    # Core Sovereign Tables
    T_CLIENTS = dynamodb.Table('DXB_AGI_Clients_v5')       # Psychological DNA & Context
    T_PARTNERS = dynamodb.Table('DXB_AGI_Partners_v5')     # Agent/RM Reliability & Trust
    T_INVENTORY = dynamodb.Table('DXB_AGI_Inventory_v5')   # The Digital Asset Storehouse
    T_MARKET = dynamodb.Table('DXB_AGI_Market_Trends_v5')  # Real-time Dubai ROI & Price Index
    T_DEALS = dynamodb.Table('DXB_AGI_Deals_v5')           # Negotiation Lifecycle
    T_AUDIT = dynamodb.Table('DXB_AGI_Audit_v5')           # Immutable Legal Evidence

    # =============================================================
    # 1. THE ELEPHANT MEMORY (CRASH-PROOF & SHATIR)
    # =============================================================
    @staticmethod
    def get_full_intel(phone):
        """
        Logic: Infinite Recall. Fetches identity and psychological DNA.
        FIXED: Added 'voice_modulation', 'tone_style', and 'admin_control'.
        """
        try:
            response = AGIDatabaseManager.T_CLIENTS.get_item(Key={'pk': phone})
            
            if 'Item' not in response:
                # Naya investor profile with ALL AGI Keys included
                new_investor = {
                    'pk': phone,
                    'created_at': datetime.now().isoformat(),
                    'comm_policy': 'MAX_2_BUBBLES',
                    'voice_modulation': 'ELITE_DUBAI',   # AGI Personality Key
                    'tone_style': 'PROFESSIONAL_SHARK',   # AGI Voice Key
                    'preferred_language': 'AUTO',
                    'admin_control': False,              # Ghost Mode Toggle
                    'profile': {
                        'nationality': 'DETECTING',
                        'investor_archetype': 'UNKNOWN', # Shark, Turtle, Whale
                        'personality_vibe': 'NEUTRAL',
                        'trust_level': Decimal('100.0'),
                        'family_context': '', 
                        'budget_evolution': []
                    },
                    'context_stack': [],                 # Last 10 conversation topics
                    'is_alive': True
                }
                AGIDatabaseManager.T_CLIENTS.put_item(Item=new_investor)
                return new_investor
            
            return response['Item']
        except Exception as e:
            logging.error(f"❌ DB_FETCH_FATAL: {str(e)}")
            return {}

    # =============================================================
    # 2. THE MARKET-PRICE GATEKEEPER (NEGOTIATION LOGIC)
    # =============================================================
    @staticmethod
    def log_inventory_signal(phone, project_name, unit_details, price):
        """
        Logic: Inventory Acquisition & Filtering.
        Tracks if the property is 'Market Priced' and eligible for free portals.
        """
        inventory_id = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        # Initial Assessment (AI will update this after negotiation)
        inventory_item = {
            'pk': inventory_id,
            'owner_phone': phone,
            'project_name': project_name,
            'unit': unit_details,
            'asked_price': Decimal(str(price)),
            'is_market_priced': False,          # Default: AI must negotiate first
            'portal_opt_in': False,             # Has client agreed to free listing?
            'listing_status': 'NEGOTIATION',    # Stages: NEGOTIATION, LIVE_ON_PORTALS, SOLD
            'market_valuation_ref': {},         # Snap-shot of area rates at time of listing
            'created_at': datetime.now().isoformat()
        }
        
        AGIDatabaseManager.T_INVENTORY.put_item(Item=inventory_item)
        return inventory_id

    @staticmethod
    def update_listing_sovereignty(inventory_id, market_priced=True, portal_agreement=True):
        """Logic: Elevates a 'Kachra' listing to a 'Elite' portal listing."""
        AGIDatabaseManager.T_INVENTORY.update_item(
            Key={'pk': inventory_id},
            UpdateExpression="SET is_market_priced = :mp, portal_opt_in = :po, listing_status = :s",
            ExpressionAttributeValues={
                ':mp': market_priced,
                ':po': portal_agreement,
                ':s': 'READY_FOR_PORTAL' if market_priced else 'NEGOTIATION'
            }
        )

    # =============================================================
    # 3. IDENTITY PROTECTION (ANTI-BYPASS)
    # =============================================================
    @staticmethod
    def secure_partner_vault(phone, identity_id, role, org_name):
        """Logic: Prevents RMs/Agents from using multiple numbers for one ID."""
        try:
            duplicate_check = AGIDatabaseManager.T_PARTNERS.scan(
                FilterExpression=Attr('identity_id').eq(identity_id)
            ).get('Items', [])

            if duplicate_check and duplicate_check[0]['pk'] != phone:
                return {"status": "SECURITY_BREACH", "reason": "ID_MAP_CONFLICT"}

            partner_entry = {
                'pk': phone,
                'identity_id': identity_id,
                'role': role,
                'org': org_name,
                'reliability_score': Decimal('100.0'),
                'status': 'ACTIVE',
                'joined_at': datetime.now().isoformat()
            }
            AGIDatabaseManager.T_PARTNERS.put_item(Item=partner_entry)
            return {"status": "SUCCESS"}
        except Exception:
            return {"status": "ERROR"}

    # =============================================================
    # 4. MARKET INTEL & AUDIT
    # =============================================================
    @staticmethod
    def fetch_market_intelligence(area_name):
        """Fetches the ultimate source of truth for Dubai Area Pricing."""
        try:
            res = AGIDatabaseManager.T_MARKET.get_item(Key={'area_pk': area_name.upper()})
            return res.get('Item', {"avg_roi": "7.5%", "status": "High Growth", "avg_psf": "1800"})
        except Exception:
            return {"avg_roi": "7.5%", "avg_psf": "1600"}

    @staticmethod
    def log_audit_event(entity_pk, event_type, metadata):
        """100-Year Immutable Evidence Store."""
        try:
            AGIDatabaseManager.T_AUDIT.put_item(Item={
                'pk': f"AUDIT#{uuid.uuid4().hex}",
                'entity_pk': entity_pk,
                'event': event_type,
                'data': metadata,
                'timestamp': datetime.now().isoformat()
            })
        except Exception:
            pass

    @staticmethod
    def fetch_inventory_direct(project_name):
        """
        Logic: Search inventory by project name.
        Returns matching properties for visual card generation.
        """
        try:
            response = AGIDatabaseManager.T_INVENTORY.scan(
                FilterExpression=Attr('project_name').contains(project_name)
            )
            return response.get('Items', [])
        except Exception:
            return []

    @staticmethod
    def search_properties_by_criteria(bedrooms=None, location=None, budget_min=None, budget_max=None):
        """
        Logic: Advanced property search filtering multiple criteria.
        Returns properties matching client requirements.
        """
        try:
            # Build filter expression
            filter_expr = Attr('is_market_priced').eq(True)  # Only market-priced listings
            
            if location:
                filter_expr = filter_expr & Attr('location').eq(location)
            
            if bedrooms is not None:
                filter_expr = filter_expr & Attr('bedrooms').eq(bedrooms)
            
            if budget_min and budget_max:
                filter_expr = filter_expr & Attr('asked_price').between(
                    Decimal(str(budget_min)), 
                    Decimal(str(budget_max))
                )
            
            response = AGIDatabaseManager.T_INVENTORY.scan(
                FilterExpression=filter_expr,
                Limit=10  # Return top 10 results
            )
            
            return response.get('Items', [])
        except Exception as e:
            logging.error(f"Search failed: {str(e)}")
            return []

    @staticmethod
    def penalize_or_reward_partner(phone, points, reason):
        """
        Logic: Adjust RM/Agent reliability score.
        Negative points for violations, positive for good deals.
        """
        try:
            partner = AGIDatabaseManager.T_PARTNERS.get_item(Key={'pk': phone})
            if 'Item' not in partner:
                return False
            
            current_score = float(partner['Item'].get('reliability_score', Decimal('100')))
            new_score = max(0, min(100, current_score + points))  # Clamp 0-100
            
            AGIDatabaseManager.T_PARTNERS.update_item(
                Key={'pk': phone},
                UpdateExpression="SET reliability_score = :score, last_penalty_reason = :reason",
                ExpressionAttributeValues={
                    ':score': Decimal(str(new_score)),
                    ':reason': reason
                }
            )
            
            logging.info(f"Partner {phone} score updated: {current_score} → {new_score} ({reason})")
            return True
        except Exception as e:
            logging.error(f"Penalty update failed: {str(e)}")
            return False