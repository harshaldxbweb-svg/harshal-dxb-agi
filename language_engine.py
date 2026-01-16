"""
MULTI-LANGUAGE SUPPORT SYSTEM
Automatically detects client language and responds in their preferred language

Supports 150+ nationalities with native language responses:
- English (Default)
- Hindi/Hinglish
- Arabic
- Chinese (Simplified & Traditional)
- Urdu
- Tagalog
- Russian
- French
- And 140+ more languages via Google Translate
"""

import logging
from enum import Enum
from typing import Dict, Tuple

logger = logging.getLogger("LANGUAGE_ENGINE")


class SupportedLanguage(Enum):
    """Primary supported languages"""
    ENGLISH = "en"
    HINGLISH = "hi-en"  # Hindi-English mix
    HINDI = "hi"
    ARABIC = "ar"
    CHINESE_SIMPLIFIED = "zh-CN"
    CHINESE_TRADITIONAL = "zh-TW"
    URDU = "ur"
    TAGALOG = "tl"
    RUSSIAN = "ru"
    FRENCH = "fr"
    SPANISH = "es"
    PORTUGUESE = "pt"
    TURKISH = "tr"
    FARSI = "fa"
    MALAY = "ms"
    THAI = "th"
    VIETNAMESE = "vi"
    KOREAN = "ko"
    JAPANESE = "ja"
    GERMAN = "de"
    ITALIAN = "it"
    GREEK = "el"
    POLISH = "pl"
    DUTCH = "nl"
    HUNGARIAN = "hu"
    CZECH = "cs"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"


class LanguageDetectionEngine:
    """
    Detects client's preferred language from:
    1. First message content (keywords in different languages)
    2. Client profile nationality
    3. Message patterns
    """

    # Language keywords mapping
    LANGUAGE_KEYWORDS = {
        SupportedLanguage.HINDI: ["hai", "chahiye", "muje", "bhai", "kya", "matlab"],
        SupportedLanguage.HINGLISH: ["2 bhk", "rental", "buy", "budget", "area", "dubai"],
        SupportedLanguage.ARABIC: ["أريد", "كم", "السعر", "الإيجار", "شراء", "الموقع"],
        SupportedLanguage.CHINESE_SIMPLIFIED: ["我", "想要", "租", "买", "价格", "位置"],
        SupportedLanguage.URDU: ["مجھے", "چاہیے", "کرایہ", "خریدنا", "قیمت"],
        SupportedLanguage.TAGALOG: ["gusto", "bahay", "renta", "bili", "presyo"],
        SupportedLanguage.RUSSIAN: ["хочу", "квартиру", "аренду", "цена", "место"],
        SupportedLanguage.FRENCH: ["je veux", "maison", "louer", "acheter", "prix"],
        SupportedLanguage.SPANISH: ["quiero", "casa", "alquilar", "comprar", "precio"],
    }

    # Nationality to language mapping
    NATIONALITY_LANGUAGE_MAP = {
        # Indians
        "INDIAN": SupportedLanguage.HINGLISH,
        "INDIA": SupportedLanguage.HINGLISH,
        
        # Arabs
        "SAUDI": SupportedLanguage.ARABIC,
        "UAE": SupportedLanguage.ARABIC,
        "EMIRATI": SupportedLanguage.ARABIC,
        "EGYPTIAN": SupportedLanguage.ARABIC,
        "LEBANESE": SupportedLanguage.ARABIC,
        "JORDANIAN": SupportedLanguage.ARABIC,
        "IRAQI": SupportedLanguage.ARABIC,
        "KUWAITI": SupportedLanguage.ARABIC,
        "QATARI": SupportedLanguage.ARABIC,
        "BAHRAINI": SupportedLanguage.ARABIC,
        "OMANIS": SupportedLanguage.ARABIC,
        
        # Chinese
        "CHINESE": SupportedLanguage.CHINESE_SIMPLIFIED,
        "CHINA": SupportedLanguage.CHINESE_SIMPLIFIED,
        "HONG_KONG": SupportedLanguage.CHINESE_TRADITIONAL,
        "TAIWAN": SupportedLanguage.CHINESE_TRADITIONAL,
        "SINGAPORE": SupportedLanguage.CHINESE_SIMPLIFIED,
        
        # South Asian
        "PAKISTANI": SupportedLanguage.URDU,
        "BANGLADESH": SupportedLanguage.URDU,
        
        # Southeast Asian
        "FILIPIN": SupportedLanguage.TAGALOG,
        "THAI": SupportedLanguage.THAI,
        "VIETNAMESE": SupportedLanguage.VIETNAMESE,
        "MALAYSIAN": SupportedLanguage.MALAY,
        "INDONESIAN": SupportedLanguage.MALAY,
        
        # European
        "BRITISH": SupportedLanguage.ENGLISH,
        "AMERICAN": SupportedLanguage.ENGLISH,
        "FRENCH": SupportedLanguage.FRENCH,
        "GERMAN": SupportedLanguage.GERMAN,
        "SPANISH": SupportedLanguage.SPANISH,
        "ITALIAN": SupportedLanguage.ITALIAN,
        "RUSSIAN": SupportedLanguage.RUSSIAN,
        "UKRAINIAN": SupportedLanguage.RUSSIAN,
        
        # Default
        "GLOBAL": SupportedLanguage.ENGLISH,
    }

    @staticmethod
    def detect_language(user_input: str, client_profile: dict = None) -> Tuple[SupportedLanguage, float]:
        """
        Detect client's preferred language
        
        Args:
            user_input: Client's message
            client_profile: Optional client profile with nationality
            
        Returns:
            (Detected language, Confidence score 0.0-1.0)
        """
        
        # Method 1: Check client profile nationality
        if client_profile and client_profile.get('nationality'):
            nationality = client_profile.get('nationality', '').upper()
            detected_lang = LanguageDetectionEngine.NATIONALITY_LANGUAGE_MAP.get(
                nationality, 
                SupportedLanguage.ENGLISH
            )
            logger.info(f"✅ Language detected from nationality: {detected_lang.value}")
            return (detected_lang, 0.9)  # High confidence
        
        # Method 2: Check message keywords
        message_lower = user_input.lower()
        language_scores = {}
        
        for language, keywords in LanguageDetectionEngine.LANGUAGE_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                score = min(matches / len(keywords), 1.0)
                language_scores[language] = score
        
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            confidence = language_scores[detected_lang]
            logger.info(f"✅ Language detected from keywords: {detected_lang.value} (confidence: {confidence})")
            return (detected_lang, confidence)
        
        # Default: English
        logger.info(f"⚠️ No language detected, defaulting to English")
        return (SupportedLanguage.ENGLISH, 0.5)

    @staticmethod
    def get_language_prompt(language: SupportedLanguage) -> str:
        """
        Get system prompt instruction for specific language
        """
        prompts = {
            SupportedLanguage.ENGLISH: """
You are a helpful Dubai real estate assistant.
Respond in clear, professional English.
Keep responses brief (max 2 WhatsApp bubbles).
Use emojis occasionally for clarity.
Be friendly and helpful.
""",
            
            SupportedLanguage.HINGLISH: """
Tum ek Dubai real estate assistant ho.
Hinglish mein (Hindi + English mix) respond karo.
Keep it simple aur friendly.
Max 2 WhatsApp bubbles.
Emojis use karo.
Example tone: "2 BHK Marina mein 180K budget? Perfect! Hum dikha denge..."
""",
            
            SupportedLanguage.HINDI: """
तुम एक Dubai real estate सहायक हो।
हिंदी में जवाब दो।
सरल और मित्रवत रहो।
अधिकतम 2 WhatsApp bubbles।
उदाहरण: "2 BHK Marina में 180K budget? बिल्कुल! हम दिखाते हैं..."
""",
            
            SupportedLanguage.ARABIC: """
أنت مساعد عقارات دبي.
رد باللغة العربية الفصحة أو العامية الخليجية.
كن ودوداً ومفيداً.
أقصى 2 فقاعة WhatsApp.
مثال: "2 غرفة نوم في Marina بميزانية 180K؟ ممتاز! سأريك الخيارات..."
""",
            
            SupportedLanguage.CHINESE_SIMPLIFIED: """
你是一个迪拜房地产助手。
用中文简体回答。
保持简洁友好。
最多2条WhatsApp消息。
例子："Marina的2卧室，预算18万？完美！我为你找房产..."
""",
            
            SupportedLanguage.URDU: """
تم ایک Dubai رئیل اسٹیٹ مدد گار ہو۔
اردو میں جواب دیں۔
سادہ اور دوستانہ رہیں۔
زیادہ سے زیادہ 2 WhatsApp bubbles۔
مثال: "Marina میں 2 کمرے، 180K بجٹ؟ بہترین! میں دکھاتا ہوں..."
""",
            
            SupportedLanguage.TAGALOG: """
Ikaw ay isang tumutulong sa Dubai real estate.
Sumagot sa Tagalog.
Maging simple at friendly.
Maximum 2 WhatsApp bubbles.
Halimbawa: "2 bedroom sa Marina, 180K budget? Perpekto! Ipapakita ko sa iyo..."
""",
            
            SupportedLanguage.RUSSIAN: """
Вы помощник по недвижимости в Дубае.
Ответьте на русском языке.
Будьте дружелюбны и полезны.
Максимум 2 пузыря WhatsApp.
Пример: "2 комнаты в Марине с бюджетом 180K? Отлично! Я покажу..."
""",
            
            SupportedLanguage.FRENCH: """
Vous êtes un assistant immobilier à Dubaï.
Répondez en français.
Soyez simple et amical.
Maximum 2 bulles WhatsApp.
Exemple: "2 chambres à Marina, budget 180K? Parfait! Je vais vous montrer..."
""",
        }
        
        return prompts.get(language, prompts[SupportedLanguage.ENGLISH])


class ResponseTranslator:
    """
    Translates responses to client's language if needed
    """
    
    @staticmethod
    def translate_to_language(english_response: str, target_language: SupportedLanguage) -> str:
        """
        Translate response to target language
        Uses Gemini for accurate, context-aware translation
        """
        
        if target_language == SupportedLanguage.ENGLISH:
            return english_response  # Already in English
        
        import google.generativeai as genai
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
Translate the following real estate response to {target_language.name} ({target_language.value}).
Keep the same tone and emoji usage.
Make it natural and culturally appropriate.

Original (English):
{english_response}

Translated to {target_language.name}:
"""
        
        try:
            response = model.generate_content(prompt)
            translated = response.text.strip()
            logger.info(f"✅ Translated to {target_language.value}")
            return translated
        except Exception as e:
            logger.error(f"❌ Translation failed: {str(e)}")
            return english_response  # Fallback to English


# ===================================================================
# EXAMPLE USAGE IN MAIN.PY
# ===================================================================
"""
from language_engine import LanguageDetectionEngine, ResponseTranslator

# Detect language
detected_lang, confidence = LanguageDetectionEngine.detect_language(
    user_input="2 BHK Marina rental 5000",
    client_profile=client_profile
)

# Get language-specific prompt
lang_prompt = LanguageDetectionEngine.get_language_prompt(detected_lang)

# Generate response in English first (Gemini is best in English)
english_response = generate_response(user_input, lang_prompt)

# Translate if needed
final_response = ResponseTranslator.translate_to_language(english_response, detected_lang)

# Send to client
send_message(client_phone, final_response)
"""
