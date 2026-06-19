"""
Mood schemas – request/response models for mood tracking.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class MoodLogCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=10)
    mood_label: str = Field(..., max_length=50)
    primary_emotion: Optional[str] = Field(None, max_length=50)
    contributing_factors: List[str] = []
    notes: Optional[str] = Field(None, max_length=2000)


class MoodLogResponse(BaseModel):
    id: UUID
    mood_score: int
    mood_label: str
    primary_emotion: Optional[str] = None
    contributing_factors: list = []
    notes: Optional[str] = None
    logged_at: datetime

    model_config = {"from_attributes": True}


class MoodTrendPoint(BaseModel):
    date: str
    avg_score: float
    dominant_emotion: Optional[str] = None
    log_count: int = 0


class MoodTrendsResponse(BaseModel):
    period: str  # "7d", "30d", "90d"
    trends: List[MoodTrendPoint]
    overall_average: float
    mood_distribution: dict = {}


class EmotionAnalytics(BaseModel):
    emotions: dict  # {"joy": 30, "sadness": 10, ...}
    top_factors: List[str]
    total_logs: int
    period: str
