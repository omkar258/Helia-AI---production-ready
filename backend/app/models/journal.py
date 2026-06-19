"""
JournalEntry model – stores user journal entries with AI analysis.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, JSON, Text, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="Untitled Entry")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    ai_analysis: Mapped[str] = mapped_column(Text, nullable=True)
    mood_tag: Mapped[str] = mapped_column(String(50), nullable=True)
    detected_emotion: Mapped[str] = mapped_column(String(50), nullable=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="journal_entries")

    def __repr__(self):
        return f"<JournalEntry {self.id} – {self.title}>"
