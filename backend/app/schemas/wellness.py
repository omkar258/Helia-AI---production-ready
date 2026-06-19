"""
Wellness schemas – request/response models for wellness plans and recommendations.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


class WellnessPlanCreate(BaseModel):
    plan_type: str = Field(..., max_length=100)


class WellnessPlanUpdate(BaseModel):
    progress: Optional[dict] = None
    status: Optional[str] = Field(None, pattern=r"^(active|completed|paused)$")


class WellnessPlanResponse(BaseModel):
    id: UUID
    plan_type: str
    recommendations: list = []
    goals: list = []
    progress: dict = {}
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    category: str  # "exercise", "mindfulness", "social", "sleep", "nutrition"
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    estimated_duration: Optional[str] = None


class WellnessRecommendations(BaseModel):
    recommendations: List[RecommendationResponse]
    based_on: str  # description of what data drove these recommendations
    generated_at: datetime


class DashboardOverview(BaseModel):
    total_conversations: int
    total_journal_entries: int
    total_mood_logs: int
    current_streak: int  # days of consecutive mood logging
    avg_mood_7d: Optional[float] = None
    avg_mood_30d: Optional[float] = None
    dominant_emotion: Optional[str] = None
    active_wellness_plans: int
    recent_mood_trend: str  # "improving", "stable", "declining"


class WeeklyReport(BaseModel):
    week_start: str
    week_end: str
    mood_summary: dict
    emotion_breakdown: dict
    conversations_count: int
    journal_entries_count: int
    key_insights: List[str]
    ai_recommendations: List[str]


class ProgressMetrics(BaseModel):
    wellness_completion: float  # percentage
    mood_improvement: Optional[float] = None  # percentage change
    consistency_score: float  # 0-100
    milestones: List[dict]
