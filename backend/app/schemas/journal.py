"""
Journal schemas – request/response models for journal entries.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class JournalCreate(BaseModel):
    title: str = Field("Untitled Entry", max_length=255)
    content: str = Field(..., min_length=1, max_length=50000)
    tags: List[str] = []


class JournalUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, min_length=1, max_length=50000)
    tags: Optional[List[str]] = None


class JournalAnalyzeRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=50000)


class JournalResponse(BaseModel):
    id: UUID
    title: str
    content: str
    ai_analysis: Optional[str] = None
    mood_tag: Optional[str] = None
    detected_emotion: Optional[str] = None
    sentiment_score: Optional[float] = None
    tags: list = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JournalAnalysisResponse(BaseModel):
    analysis: str
    detected_emotion: str
    mood_tag: str
    sentiment_score: float
    suggestions: List[str] = []
