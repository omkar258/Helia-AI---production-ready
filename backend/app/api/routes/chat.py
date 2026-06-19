"""
Chat Routes – AI conversation endpoints with RAG, emotion detection, and crisis support.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.conversation import (
    MessageInput, MessageResponse,
    ConversationSummary, ConversationDetail,
)
from app.services.ai_engine import ai_engine
from app.services.rag_service import rag_service
from app.services.emotion_service import emotion_service
from app.services.sentiment_service import sentiment_service
from app.services.crisis_service import crisis_service
from app.services.memory_service import memory_service

router = APIRouter()


@router.post("/message", response_model=MessageResponse)
async def send_message(
    data: MessageInput,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message to Helia AI and get a response."""
    # Step 1: Crisis check
    is_crisis, crisis_response, crisis_resources = await crisis_service.assess(data.message)

    # Step 2: Get or create conversation
    conversation = None
    if data.conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == data.conversation_id,
                Conversation.user_id == current_user.id,
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation:
        conversation = Conversation(
            user_id=current_user.id,
            title=data.message[:50] + ("..." if len(data.message) > 50 else ""),
            messages=[],
        )
        db.add(conversation)
        await db.flush()

    # Step 3: RAG retrieval
    rag_context = await rag_service.retrieve(data.message)

    # Step 4: Get user memories
    user_memories = await memory_service.get_relevant_memories(db, current_user.id)

    # Step 5: Generate AI response
    if is_crisis:
        ai_response = crisis_response
    else:
        ai_response = await ai_engine.generate_response(
            data.message,
            conversation_history=conversation.messages,
            rag_context=rag_context,
            user_memories=user_memories,
        )

    # Step 6: Emotion & sentiment analysis
    emotion = await emotion_service.detect_emotion(data.message)
    sentiment = sentiment_service.analyze_quick(data.message)

    # Step 7: Update conversation
    messages = list(conversation.messages) if conversation.messages else []
    messages.append({"role": "user", "content": data.message})
    messages.append({"role": "assistant", "content": ai_response})
    conversation.messages = messages
    conversation.detected_emotion = emotion
    conversation.sentiment_score = sentiment
    conversation.crisis_flagged = is_crisis

    # Step 8: Store user memory
    await memory_service.extract_and_store(db, current_user.id, data.message)

    await db.flush()
    await db.refresh(conversation)

    return MessageResponse(
        conversation_id=conversation.id,
        user_message=data.message,
        ai_response=ai_response,
        detected_emotion=emotion,
        sentiment_score=sentiment,
        crisis_detected=is_crisis,
        crisis_resources=crisis_resources if is_crisis else None,
    )


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all conversations for the current user."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    return [
        ConversationSummary(
            id=c.id, title=c.title,
            detected_emotion=c.detected_emotion,
            sentiment_score=c.sentiment_score,
            crisis_flagged=c.crisis_flagged,
            created_at=c.created_at, updated_at=c.updated_at,
            message_count=len(c.messages) if c.messages else 0,
        )
        for c in conversations
    ]


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific conversation with full message history."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetail.model_validate(conversation)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a conversation."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    await db.delete(conversation)
