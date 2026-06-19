"""
MoodLog model – tracks daily mood entries with contributing factors.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, DateTime, JSON, Text, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class MoodLog(Base):
    __tablename__ = "mood_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mood_score: Mapped[int] = mapped_column(Integer, nullable=False)
    mood_label: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_emotion: Mapped[str] = mapped_column(String(50), nullable=True)
    contributing_factors: Mapped[list] = mapped_column(JSON, default=list)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="mood_logs")

    def __repr__(self):
        return f"<MoodLog {self.mood_label} ({self.mood_score}/10)>"
