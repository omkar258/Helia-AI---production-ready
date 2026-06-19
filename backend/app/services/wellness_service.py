"""
Wellness Recommendation Service – generates personalized wellness plans.
"""

import logging
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mood import MoodLog
from app.models.wellness import WellnessPlan

logger = logging.getLogger(__name__)

DEFAULT_RECOMMENDATIONS = {
    "low_mood": [
        {"category": "mindfulness", "title": "5-Minute Breathing Exercise", "description": "Practice box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s. Repeat 5 times.", "priority": "high", "estimated_duration": "5 min"},
        {"category": "exercise", "title": "Gentle Walk", "description": "Take a 15-minute walk outside. Focus on what you see, hear, and feel.", "priority": "high", "estimated_duration": "15 min"},
        {"category": "social", "title": "Reach Out", "description": "Send a message to someone you trust. Connection helps.", "priority": "medium", "estimated_duration": "5 min"},
    ],
    "anxiety": [
        {"category": "mindfulness", "title": "Grounding Exercise (5-4-3-2-1)", "description": "Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.", "priority": "high", "estimated_duration": "5 min"},
        {"category": "exercise", "title": "Progressive Muscle Relaxation", "description": "Tense and release each muscle group for 5 seconds, from toes to head.", "priority": "high", "estimated_duration": "10 min"},
        {"category": "sleep", "title": "Wind-Down Routine", "description": "30 min before bed: no screens, dim lights, warm tea, gentle stretching.", "priority": "medium", "estimated_duration": "30 min"},
    ],
    "general": [
        {"category": "mindfulness", "title": "Daily Gratitude", "description": "Write down 3 things you're grateful for today.", "priority": "medium", "estimated_duration": "5 min"},
        {"category": "exercise", "title": "Movement Break", "description": "Stand up, stretch, and do 10 jumping jacks or a quick dance.", "priority": "low", "estimated_duration": "3 min"},
        {"category": "nutrition", "title": "Hydration Check", "description": "Drink a glass of water. Aim for 8 glasses today.", "priority": "low", "estimated_duration": "1 min"},
    ],
}


class WellnessService:
    async def get_recommendations(self, db: AsyncSession, user_id: UUID) -> dict:
        from datetime import timedelta
        since = datetime.now(timezone.utc) - timedelta(days=7)
        result = await db.execute(
            select(MoodLog).where(and_(MoodLog.user_id == user_id, MoodLog.logged_at >= since))
        )
        logs = result.scalars().all()

        if not logs:
            recs = DEFAULT_RECOMMENDATIONS["general"]
            based_on = "general wellness (no recent mood data)"
        else:
            avg_mood = sum(l.mood_score for l in logs) / len(logs)
            emotions = [l.primary_emotion for l in logs if l.primary_emotion]
            has_anxiety = any(e in ["fear", "anticipation"] for e in emotions)

            if avg_mood < 4:
                recs = DEFAULT_RECOMMENDATIONS["low_mood"]
                based_on = f"low average mood ({avg_mood:.1f}/10) over the past 7 days"
            elif has_anxiety:
                recs = DEFAULT_RECOMMENDATIONS["anxiety"]
                based_on = "detected anxiety-related emotions in recent mood logs"
            else:
                recs = DEFAULT_RECOMMENDATIONS["general"]
                based_on = f"stable mood ({avg_mood:.1f}/10) – maintaining wellness"

        return {
            "recommendations": recs,
            "based_on": based_on,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def generate_plan(self, db: AsyncSession, user_id: UUID, plan_type: str) -> dict:
        try:
            from app.services.ai_engine import ai_engine
            prompt = (
                f"Create a 7-day wellness plan for someone focusing on: {plan_type}. "
                f"Include 3 daily goals and 5 specific recommendations. "
                f"Format as JSON with keys: goals (list of strings), recommendations (list of strings)."
            )
            response = await ai_engine.generate_response(prompt)

            import json
            try:
                plan_data = json.loads(response)
                goals = plan_data.get("goals", [f"Focus on {plan_type} daily"])
                recommendations = plan_data.get("recommendations", [])
            except json.JSONDecodeError:
                goals = [f"Practice {plan_type} techniques daily", "Track your progress", "Be patient with yourself"]
                recommendations = [response[:500]]

        except Exception as e:
            logger.error(f"Plan generation error: {e}")
            goals = [f"Practice {plan_type} techniques daily", "Track your progress", "Be patient with yourself"]
            recommendations = ["Start with small, achievable steps each day."]

        return {"goals": goals, "recommendations": recommendations}


wellness_service = WellnessService()
