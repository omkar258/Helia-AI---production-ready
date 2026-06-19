"""
Emotion Detection Service – identifies primary emotions from text using AI.
"""

import logging
from typing import Optional
from app.services.ai_engine import ai_engine

logger = logging.getLogger(__name__)

VALID_EMOTIONS = [
    "joy", "sadness", "anger", "fear", "surprise",
    "disgust", "trust", "anticipation", "neutral"
]


class EmotionService:
    """Detects emotions from text using Llama 3.1."""

    async def detect_emotion(self, text: str) -> str:
        """Detect the primary emotion in the given text."""
        try:
            result = await ai_engine.analyze_text(text, "emotion")
            emotion = result.lower().strip().rstrip(".")

            # Validate against known emotions
            if emotion in VALID_EMOTIONS:
                return emotion

            # Try to match partial response
            for valid in VALID_EMOTIONS:
                if valid in emotion:
                    return valid

            return "neutral"
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return "neutral"

    async def detect_emotions_batch(self, texts: list) -> list:
        """Detect emotions for multiple texts."""
        results = []
        for text in texts:
            emotion = await self.detect_emotion(text)
            results.append(emotion)
        return results


emotion_service = EmotionService()
