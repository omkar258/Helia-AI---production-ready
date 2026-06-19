"""
Mood Routes – mood logging and trend analytics.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.mood import MoodLog
from app.schemas.mood import MoodLogCreate, MoodLogResponse, MoodTrendsResponse, EmotionAnalytics
from app.services.mood_service import mood_service

router = APIRouter()


@router.post("/log", response_model=MoodLogResponse, status_code=status.HTTP_201_CREATED)
async def log_mood(
    data: MoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Log a mood entry."""
    mood_log = MoodLog(
        user_id=current_user.id,
        mood_score=data.mood_score,
        mood_label=data.mood_label,
        primary_emotion=data.primary_emotion,
        contributing_factors=data.contributing_factors,
        notes=data.notes,
    )
    db.add(mood_log)
    await db.flush()
    await db.refresh(mood_log)
    return MoodLogResponse.model_validate(mood_log)


@router.get("/logs", response_model=list[MoodLogResponse])
async def get_mood_logs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all mood logs for the current user."""
    from sqlalchemy import select
    result = await db.execute(
        select(MoodLog)
        .where(MoodLog.user_id == current_user.id)
        .order_by(MoodLog.logged_at.desc())
        .limit(100)
    )
    return [MoodLogResponse.model_validate(m) for m in result.scalars().all()]


@router.get("/trends", response_model=MoodTrendsResponse)
async def get_mood_trends(
    period: str = "7d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get mood trends over a period (7d, 30d, 90d)."""
    result = await mood_service.get_trends(db, current_user.id, period)
    return MoodTrendsResponse(**result)


@router.get("/analytics", response_model=EmotionAnalytics)
async def get_emotion_analytics(
    period: str = "30d",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get emotion analytics over a period."""
    result = await mood_service.get_emotion_analytics(db, current_user.id, period)
    return EmotionAnalytics(**result)
