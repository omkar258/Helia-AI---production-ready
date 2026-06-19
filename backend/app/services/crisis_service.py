"""
Crisis Detection Service – detects signs of self-harm, suicidal ideation,
or severe distress and provides immediate safety resources.
"""

import logging
import re
from typing import Tuple, List

logger = logging.getLogger(__name__)

CRISIS_PATTERNS = [
    r"\b(kill\s*(my)?self|suicide|suicidal)\b",
    r"\b(end\s*(my|it\s*all)|want\s*to\s*die)\b",
    r"\b(self[\s-]?harm|cut\s*myself|hurt\s*myself)\b",
    r"\b(no\s*reason\s*to\s*live|better\s*off\s*dead)\b",
    r"\b(overdose|hang\s*myself)\b",
    r"\b(can'?t\s*go\s*on|give\s*up\s*on\s*life)\b",
    r"\b(goodbye\s*forever|final\s*goodbye)\b",
]

CRISIS_RESOURCES = [
    "National Suicide Prevention Lifeline: Call or text 988",
    "Crisis Text Line: Text HOME to 741741",
    "SAMHSA National Helpline: 1-800-662-4357",
    "Emergency: Call 911",
]

CRISIS_RESPONSE = (
    "I hear you, and your feelings are valid. I'm concerned about your safety. "
    "Please reach out to a crisis resource:\n\n"
    + "\n".join(f"- {r}" for r in CRISIS_RESOURCES)
    + "\n\nYou matter, and help is available."
)


class CrisisService:
    def detect_crisis_keywords(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    async def detect_crisis_ai(self, text: str) -> bool:
        try:
            from app.services.ai_engine import ai_engine
            result = await ai_engine.analyze_text(text, "crisis")
            return result.strip().upper().startswith("YES")
        except Exception as e:
            logger.error(f"AI crisis detection error: {e}")
            return False

    async def assess(self, text: str) -> Tuple[bool, str, List[str]]:
        keyword_crisis = self.detect_crisis_keywords(text)
        ai_crisis = False
        if keyword_crisis or len(text) > 50:
            ai_crisis = await self.detect_crisis_ai(text)
        is_crisis = keyword_crisis or ai_crisis
        if is_crisis:
            logger.warning("Crisis detected in user message.")
            return True, CRISIS_RESPONSE, CRISIS_RESOURCES
        return False, "", []


crisis_service = CrisisService()
