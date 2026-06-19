"""
Mood Service – mood tracking analytics and trend calculations.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mood import MoodLog

logger = logging.getLogger(__name__)


class MoodService:
    async def get_trends(self, db: AsyncSession, user_id: UUID, period: str = "7d") -> dict:
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(period, 7)
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db.execute(
            select(MoodLog)
            .where(and_(MoodLog.user_id == user_id, MoodLog.logged_at >= since))
            .order_by(MoodLog.logged_at)
        )
        logs = result.scalars().all()

        if not logs:
            return {"period": period, "trends": [], "overall_average": 0, "mood_distribution": {}}

        # Group by date
        daily = {}
        for log in logs:
            date_key = log.logged_at.strftime("%Y-%m-%d")
            if date_key not in daily:
                daily[date_key] = {"scores": [], "emotions": []}
            daily[date_key]["scores"].append(log.mood_score)
            if log.primary_emotion:
                daily[date_key]["emotions"].append(log.primary_emotion)

        trends = []
        for date_key, data in daily.items():
            avg = sum(data["scores"]) / len(data["scores"])
            dominant = max(set(data["emotions"]), key=data["emotions"].count) if data["emotions"] else None
            trends.append({
                "date": date_key, "avg_score": round(avg, 1),
                "dominant_emotion": dominant, "log_count": len(data["scores"]),
            })

        all_scores = [log.mood_score for log in logs]
        overall_avg = sum(all_scores) / len(all_scores)

        # Mood distribution
        mood_dist = {}
        for log in logs:
            mood_dist[log.mood_label] = mood_dist.get(log.mood_label, 0) + 1

        return {
            "period": period, "trends": trends,
            "overall_average": round(overall_avg, 1), "mood_distribution": mood_dist,
        }

    async def get_emotion_analytics(self, db: AsyncSession, user_id: UUID, period: str = "30d") -> dict:
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(period, 30)
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await db.execute(
            select(MoodLog)
            .where(and_(MoodLog.user_id == user_id, MoodLog.logged_at >= since))
        )
        logs = result.scalars().all()

        emotions = {}
        factors_count = {}
        for log in logs:
            if log.primary_emotion:
                emotions[log.primary_emotion] = emotions.get(log.primary_emotion, 0) + 1
            if log.contributing_factors:
                for factor in log.contributing_factors:
                    factors_count[factor] = factors_count.get(factor, 0) + 1

        top_factors = sorted(factors_count, key=factors_count.get, reverse=True)[:5]

        return {
            "emotions": emotions, "top_factors": top_factors,
            "total_logs": len(logs), "period": period,
        }

    async def get_streak(self, db: AsyncSession, user_id: UUID) -> int:
        result = await db.execute(
            select(MoodLog)
            .where(MoodLog.user_id == user_id)
            .order_by(MoodLog.logged_at.desc())
        )
        logs = result.scalars().all()
        if not logs:
            return 0

        streak = 0
        current_date = datetime.now(timezone.utc).date()
        logged_dates = set(log.logged_at.date() for log in logs)

        while current_date in logged_dates or (streak == 0 and (current_date - timedelta(days=1)) in logged_dates):
            if current_date in logged_dates:
                streak += 1
            elif streak == 0:
                current_date -= timedelta(days=1)
                continue
            else:
                break
            current_date -= timedelta(days=1)

        return streak


mood_service = MoodService()
