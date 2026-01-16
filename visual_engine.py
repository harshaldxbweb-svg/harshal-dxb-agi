import json
from decimal import Decimal

class AGIVisualEngine:
    """
    THE VISUAL COMMAND CENTER (Level 5 AGI):
    Responsible for converting raw neural data into elite WhatsApp experiences.
    Ensures 'Harshal DXB' brand sovereignty in every pixel.
    """

    # =============================================================
    # 1. ELITE PROPERTY CARD (The Revenue Driver)
    # =============================================================
    @staticmethod
    def format_property_card(project_data, market_context=None):
        """
        Logic: Visual Psychological Framing. 
        Converts raw project details into a high-conversion property card.
        """
        name = project_data.get('project_name', 'EXCLUSIVE OPPORTUNITY').upper()
        dev = project_data.get('developer', 'Elite Developer')
        loc = project_data.get('location', 'Dubai')
        price = project_data.get('starting_price', 'Request Pricing')
        roi = project_data.get('roi_avg', 'High Yield')
        handover = project_data.get('handover_date', 'Coming Soon')
        
        # Currency formatting for Dubai (AED)
        formatted_price = f"{int(price):,}" if str(price).isdigit() else price

        card = [
            f"🏗️ *{name}*",
            f"🏢 _Developed by {dev}_",
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            f"📍 *Location:* {loc}",
            f"💰 *Starting Price:* {formatted_price} AED",
            f"📈 *Expected ROI:* {roi}%",
            f"🔑 *Handover:* {handover}",
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            "",
            "*Why this Investment?*",
            f"✅ {project_data.get('usp_1', 'Prime Strategic Location')}",
            f"✅ {project_data.get('usp_2', 'Investor-Friendly Payment Plan')}",
            f"✅ {project_data.get('usp_3', 'High Capital Appreciation Potential')}",
            "",
            "🔗 _Reply with 'BROCHURE' for the full PDF & Floor Plans._",
            "📞 _Reply with 'CALLBACK' to speak with a Senior Consultant._"
        ]
        return "\n".join(card)

    # =============================================================
    # 2. SOVEREIGN PARTNER REGISTRATION (RM/Agent Flow)
    # =============================================================
    @staticmethod
    def get_registration_step(step, partner_name=None):
        """
        Logic: Professional Onboarding State-Machine.
        Forces the 40/60 Split and Integrity rules upfront.
        """
        steps = {
            1: [
                "🤝 *MARHABA! Welcome to the Harshal DXB Partner Network.*",
                "",
                "Humein khushi hai ki aap Dubai ke sabse intelligent real estate ecosystem se judna chahte hain.",
                "",
                "👉 *STEP 1:* Please apna *Full Name* aur *Agency Name* type karke bhejiye."
            ],
            2: [
                f"✅ Shukriya {partner_name}!",
                "",
                "🆔 *STEP 2: Identity Verification*",
                "",
                "Security aur Fraud prevention ke liye, please apna *Emirates ID* ya *RERA Card Number* bhejiye.",
                "",
                "⚠️ _Note: Yeh ID aapke number ke saath permanent link ho jayegi._"
            ],
            3: [
                "📜 *FINAL STEP: Terms of Business*",
                "",
                "Harshal DXB Network par kaam karne ke liye aapko in rules se sehmat hona hoga:",
                "",
                "1️⃣ *Commission Split:* Standard 40/60 (Admin/Partner) share.",
                "2️⃣ *Transparency:* Har deal ka status yahan update karna hoga.",
                "3️⃣ *No Bypass:* Client se direct contact ki koshish karne par ID block ho jayegi.",
                "4️⃣ *Integrity:* Market price se upar quote karna mana hai.",
                "",
                "✅ *Reply 'AGREE' to activate your Partner ID.*"
            ]
        }
        return "\n".join(steps.get(step, ["System Error in Flow."]))

    # =============================================================
    # 3. DYNAMIC PAYMENT PLAN VISUALIZER
    # =============================================================
    @staticmethod
    def format_payment_plan(plan_data):
        """
        Logic: Complex Financial Simplification.
        Converts multi-tiered payment milestones into a clear table.
        """
        rows = [
            f"📊 *OFFICIAL PAYMENT PLAN*",
            f"Project: {plan_data.get('project', 'Select Project')}",
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            f"🔹 *Booking:* {plan_data.get('booking', '10%')}",
            "---"
        ]
        
        milestones = plan_data.get('milestones', [])
        for m in milestones:
            rows.append(f"• {m['percentage']}% — {m['event']}")
            
        rows.append("---")
        rows.append(f"🏁 *On Handover:* {plan_data.get('on_handover', '40%')}")
        rows.append("\n_All payments are via Escrow Account for your security._")
        
        return "\n".join(rows)

    # =============================================================
    # 4. ADMIN COGNITIVE SYNOPSIS (The Dashboard for Harshal)
    # =============================================================
    @staticmethod
    def format_admin_synopsis(client_phone, analysis, raw_msg):
        """
        Logic: Admin-Only Intelligence.
        Shows Harshal what the AI is thinking 'Behind the Scenes'.
        """
        synopsis = [
            "🧠 *AGI COGNITIVE INSIGHT*",
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            f"👤 *Client:* {client_phone}",
            f"🌍 *Culture:* {analysis.get('cultural_filter', 'Global')}",
            f"🎯 *Motive:* {analysis.get('hidden_motive', 'Inquiry')}",
            f"🎭 *Archetype:* {analysis.get('archetype', 'Unknown')}",
            "---",
            f"💬 *Original Msg:* \"{raw_msg}\"",
            "---",
            "🤖 *AI STATUS:* Responding as per Strategy.",
            "🛠️ _Reply with /takeover to pause the AGI._"
        ]
        return "\n".join(synopsis)

    # =============================================================
    # 5. DATA SANITIZATION FEEDBACK (Truth Reporting)
    # =============================================================
    @staticmethod
    def format_sanitized_report(original_msg, sanitized_msg):
        """
        Logic: Showing the cleaning process.
        Useful for internal audits to see what the RM tried to bypass.
        """
        report = [
            "🛡️ *DATA INTEGRITY REPORT*",
            "---",
            "*Original Input:*",
            f"_{original_msg}_",
            "",
            "*Sanitized (Harshal DXB Style):*",
            f"*{sanitized_msg}*",
            "",
            "✅ _Bypass links and contact info have been neutralized._"
        ]
        return "\n".join(report)

    # =============================================================
    # 6. DYNAMIC INVESTMENT SUMMARY
    # =============================================================
    @staticmethod
    def format_investment_summary(data):
        """
        Logic: High-level ROI and Appreciation Forecast.
        """
        summary = [
            "📈 *INVESTMENT POTENTIAL ANALYSIS*",
            "▬▬▬▬▬▬▬▬▬▬▬▬▬▬",
            f"📍 *Area:* {data.get('area')}",
            f"💰 *Current Price:* {data.get('price')} AED",
            f"📅 *5-Year Growth:* {data.get('growth', '15-20%')} (Forecasted)",
            f"💵 *Rental Yield:* {data.get('yield', '7-9%')} Net",
            "---",
            "*Expert Opinion:*",
            "Yeh area 'Under-valued' hai, naye Metro line ki wajah se yahan prices tezi se badhenge.",
            "",
            "🚀 _Wanna book a VIP unit? Reply 'BOOK'._"
        ]
        return "\n".join(summary)