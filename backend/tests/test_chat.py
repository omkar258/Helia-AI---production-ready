"""
Chat & AI Service Tests.
"""

import pytest


class TestCrisisDetection:
    """Test crisis detection patterns."""

    def test_detect_crisis_keywords_positive(self):
        from app.services.crisis_service import crisis_service
        assert crisis_service.detect_crisis_keywords("I want to kill myself") is True
        assert crisis_service.detect_crisis_keywords("thinking about suicide") is True
        assert crisis_service.detect_crisis_keywords("I want to end it all") is True

    def test_detect_crisis_keywords_negative(self):
        from app.services.crisis_service import crisis_service
        assert crisis_service.detect_crisis_keywords("I had a great day today") is False
        assert crisis_service.detect_crisis_keywords("I'm feeling a bit sad") is False
        assert crisis_service.detect_crisis_keywords("Work was stressful") is False


class TestSentimentService:
    """Test sentiment analysis."""

    def test_quick_sentiment_positive(self):
        from app.services.sentiment_service import sentiment_service
        score = sentiment_service.analyze_quick("I am so happy and grateful today!")
        assert score > 0

    def test_quick_sentiment_negative(self):
        from app.services.sentiment_service import sentiment_service
        score = sentiment_service.analyze_quick("I feel terrible and everything is awful")
        assert score < 0

    def test_sentiment_label(self):
        from app.services.sentiment_service import sentiment_service
        assert sentiment_service.sentiment_label(0.8) == "very positive"
        assert sentiment_service.sentiment_label(0.3) == "positive"
        assert sentiment_service.sentiment_label(0.0) == "neutral"
        assert sentiment_service.sentiment_label(-0.3) == "negative"
        assert sentiment_service.sentiment_label(-0.8) == "very negative"


class TestSchemas:
    """Test Pydantic schema validation."""

    def test_mood_log_score_validation(self):
        from app.schemas.mood import MoodLogCreate
        from pydantic import ValidationError

        # Valid
        mood = MoodLogCreate(mood_score=5, mood_label="okay")
        assert mood.mood_score == 5

        # Out of range
        with pytest.raises(ValidationError):
            MoodLogCreate(mood_score=11, mood_label="invalid")

        with pytest.raises(ValidationError):
            MoodLogCreate(mood_score=0, mood_label="invalid")

    def test_message_input_validation(self):
        from app.schemas.conversation import MessageInput
        from pydantic import ValidationError

        msg = MessageInput(message="Hello Helia!")
        assert msg.message == "Hello Helia!"

        with pytest.raises(ValidationError):
            MessageInput(message="")  # Too short
