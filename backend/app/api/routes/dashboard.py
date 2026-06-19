"""
Dashboard Routes – aggregated analytics, weekly reports, and progress tracking.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.journal import JournalEntry
from app.models.mood import MoodLog
from app.models.wellness import WellnessPlan
from app.schemas.wellness import DashboardOverview, WeeklyReport, ProgressMetrics
from app.services.mood_service import mood_service

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = current_user.id
    now = datetime.now(timezone.utc)

    # Counts
    convos = await db.execute(select(func.count(Conversation.id)).where(Conversation.user_id == uid))
    journals = await db.execute(select(func.count(JournalEntry.id)).where(JournalEntry.user_id == uid))
    moods = await db.execute(select(func.count(MoodLog.id)).where(MoodLog.user_id == uid))
    active_plans = await db.execute(
        select(func.count(WellnessPlan.id)).where(
            and_(WellnessPlan.user_id == uid, WellnessPlan.status == "active")
        )
    )

    # 7-day avg mood
    since_7d = now - timedelta(days=7)
    avg7 = await db.execute(
        select(func.avg(MoodLog.mood_score)).where(
            and_(MoodLog.user_id == uid, MoodLog.logged_at >= since_7d)
        )
    )
    # 30-day avg mood
    since_30d = now - timedelta(days=30)
    avg30 = await db.execute(
        select(func.avg(MoodLog.mood_score)).where(
            and_(MoodLog.user_id == uid, MoodLog.logged_at >= since_30d)
        )
    )

    # Dominant emotion (last 30 days)
    emotion_result = await db.execute(
        select(MoodLog.primary_emotion, func.count(MoodLog.id).label("cnt"))
        .where(and_(MoodLog.user_id == uid, MoodLog.logged_at >= since_30d, MoodLog.primary_emotion.isnot(None)))
        .group_by(MoodLog.primary_emotion)
        .order_by(func.count(MoodLog.id).desc())
        .limit(1)
    )
    dominant_row = emotion_result.first()

    streak = await mood_service.get_streak(db, uid)

    avg_7d_val = avg7.scalar()
    avg_30d_val = avg30.scalar()

    # Determine trend
    if avg_7d_val and avg_30d_val:
        if avg_7d_val > avg_30d_val + 0.5:
            trend = "improving"
        elif avg_7d_val < avg_30d_val - 0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "stable"

    return DashboardOverview(
        total_conversations=convos.scalar() or 0,
        total_journal_entries=journals.scalar() or 0,
        total_mood_logs=moods.scalar() or 0,
        current_streak=streak,
        avg_mood_7d=round(avg_7d_val, 1) if avg_7d_val else None,
        avg_mood_30d=round(avg_30d_val, 1) if avg_30d_val else None,
        dominant_emotion=dominant_row[0] if dominant_row else None,
        active_wellness_plans=active_plans.scalar() or 0,
        recent_mood_trend=trend,
    )


@router.get("/weekly-report", response_model=WeeklyReport)
async def weekly_report(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=7)

    # Mood summary
    result = await db.execute(
        select(MoodLog).where(
            and_(MoodLog.user_id == current_user.id, MoodLog.logged_at >= week_start)
        )
    )
    mood_logs = result.scalars().all()

    mood_summary = {}
    emotion_breakdown = {}
    if mood_logs:
        scores = [m.mood_score for m in mood_logs]
        mood_summary = {
            "average": round(sum(scores) / len(scores), 1),
            "highest": max(scores), "lowest": min(scores), "entries": len(scores),
        }
        for m in mood_logs:
            if m.primary_emotion:
                emotion_breakdown[m.primary_emotion] = emotion_breakdown.get(m.primary_emotion, 0) + 1

    # Conversation and journal counts
    conv_count = await db.execute(
        select(func.count(Conversation.id)).where(
            and_(Conversation.user_id == current_user.id, Conversation.created_at >= week_start)
        )
    )
    journal_count = await db.execute(
        select(func.count(JournalEntry.id)).where(
            and_(JournalEntry.user_id == current_user.id, JournalEntry.created_at >= week_start)
        )
    )

    return WeeklyReport(
        week_start=week_start.strftime("%Y-%m-%d"),
        week_end=now.strftime("%Y-%m-%d"),
        mood_summary=mood_summary,
        emotion_breakdown=emotion_breakdown,
        conversations_count=conv_count.scalar() or 0,
        journal_entries_count=journal_count.scalar() or 0,
        key_insights=["Keep up your journaling habit!", "Your mood has been consistent this week."],
        ai_recommendations=["Try a new mindfulness exercise", "Connect with a friend this week"],
    )


@router.get("/progress", response_model=ProgressMetrics)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = current_user.id

    # Wellness completion
    result = await db.execute(
        select(WellnessPlan).where(WellnessPlan.user_id == uid)
    )
    plans = result.scalars().all()
    completed = sum(1 for p in plans if p.status == "completed")
    total = len(plans)
    completion_pct = (completed / total * 100) if total > 0 else 0

    # Consistency score (based on mood logging frequency)
    streak = await mood_service.get_streak(db, uid)
    consistency = min(streak * 10, 100)

    return ProgressMetrics(
        wellness_completion=round(completion_pct, 1),
        mood_improvement=None,
        consistency_score=float(consistency),
        milestones=[
            {"name": "First Chat", "achieved": True},
            {"name": "7-Day Streak", "achieved": streak >= 7},
            {"name": "30-Day Streak", "achieved": streak >= 30},
        ],
    )
