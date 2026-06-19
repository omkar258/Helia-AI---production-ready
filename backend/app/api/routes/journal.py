"""
Journal Routes – CRUD and AI analysis for journal entries.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.journal import JournalEntry
from app.schemas.journal import (
    JournalCreate, JournalUpdate, JournalAnalyzeRequest,
    JournalResponse, JournalAnalysisResponse,
)
from app.services.ai_engine import ai_engine
from app.services.emotion_service import emotion_service
from app.services.sentiment_service import sentiment_service

router = APIRouter()


@router.post("/entries", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
async def create_entry(
    data: JournalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    emotion = await emotion_service.detect_emotion(data.content)
    sentiment = sentiment_service.analyze_quick(data.content)
    mood_tag = sentiment_service.sentiment_label(sentiment)

    entry = JournalEntry(
        user_id=current_user.id, title=data.title, content=data.content,
        detected_emotion=emotion, sentiment_score=sentiment, mood_tag=mood_tag,
        tags=data.tags,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return JournalResponse.model_validate(entry)


@router.get("/entries", response_model=list[JournalResponse])
async def list_entries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
    )
    return [JournalResponse.model_validate(e) for e in result.scalars().all()]


@router.get("/entries/{entry_id}", response_model=JournalResponse)
async def get_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return JournalResponse.model_validate(entry)


@router.put("/entries/{entry_id}", response_model=JournalResponse)
async def update_entry(
    entry_id: UUID, data: JournalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if data.title is not None:
        entry.title = data.title
    if data.content is not None:
        entry.content = data.content
        entry.detected_emotion = await emotion_service.detect_emotion(data.content)
        entry.sentiment_score = sentiment_service.analyze_quick(data.content)
        entry.mood_tag = sentiment_service.sentiment_label(entry.sentiment_score)
    if data.tags is not None:
        entry.tags = data.tags

    await db.flush()
    await db.refresh(entry)
    return JournalResponse.model_validate(entry)


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entry(
    entry_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JournalEntry).where(
            JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id
        )
    )
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    await db.delete(entry)


@router.post("/analyze", response_model=JournalAnalysisResponse)
async def analyze_journal(
    data: JournalAnalyzeRequest,
    current_user: User = Depends(get_current_user),
):
    analysis = await ai_engine.analyze_text(data.content, "journal")
    emotion = await emotion_service.detect_emotion(data.content)
    sentiment = sentiment_service.analyze_quick(data.content)
    mood_tag = sentiment_service.sentiment_label(sentiment)

    return JournalAnalysisResponse(
        analysis=analysis, detected_emotion=emotion,
        mood_tag=mood_tag, sentiment_score=sentiment,
        suggestions=["Continue journaling regularly", "Reflect on patterns in your entries"],
    )
