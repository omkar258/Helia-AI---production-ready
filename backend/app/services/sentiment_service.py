"""
Sentiment Analysis Service – scores text sentiment on a -1.0 to 1.0 scale.
Uses TextBlob as fast fallback, Llama 3.1 for nuanced analysis.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SentimentService:
    """Analyzes text sentiment using TextBlob and optionally Llama 3.1."""

    def analyze_quick(self, text: str) -> float:
        """Fast sentiment analysis using TextBlob (-1.0 to 1.0)."""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            return round(blob.sentiment.polarity, 3)
        except Exception as e:
            logger.error(f"TextBlob sentiment error: {e}")
            return 0.0

    async def analyze_deep(self, text: str) -> float:
        """Deep sentiment analysis using Llama 3.1 (-1.0 to 1.0)."""
        try:
            from app.services.ai_engine import ai_engine
            result = await ai_engine.analyze_text(text, "sentiment")

            # Parse the numeric response
            score = float(result.strip())
            return max(-1.0, min(1.0, round(score, 3)))
        except (ValueError, TypeError):
            # Fall back to TextBlob if LLM doesn't return a clean number
            return self.analyze_quick(text)
        except Exception as e:
            logger.error(f"Deep sentiment error: {e}")
            return self.analyze_quick(text)

    def sentiment_label(self, score: float) -> str:
        """Convert sentiment score to human-readable label."""
        if score >= 0.5:
            return "very positive"
        elif score >= 0.1:
            return "positive"
        elif score > -0.1:
            return "neutral"
        elif score > -0.5:
            return "negative"
        else:
            return "very negative"


sentiment_service = SentimentService()
