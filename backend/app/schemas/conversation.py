"""
Conversation schemas – request/response models for chat interactions.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class MessageInput(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID] = None  # None = new conversation


class MessageResponse(BaseModel):
    conversation_id: UUID
    user_message: str
    ai_response: str
    detected_emotion: Optional[str] = None
    sentiment_score: Optional[float] = None
    crisis_detected: bool = False
    crisis_resources: Optional[List[str]] = None


class ConversationSummary(BaseModel):
    id: UUID
    title: str
    detected_emotion: Optional[str] = None
    sentiment_score: Optional[float] = None
    crisis_flagged: bool = False
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    id: UUID
    title: str
    messages: list = []
    summary: Optional[str] = None
    detected_emotion: Optional[str] = None
    sentiment_score: Optional[float] = None
    crisis_flagged: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
