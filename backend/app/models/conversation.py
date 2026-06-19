"""
Conversation model – stores chat sessions between user and Helia AI.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Boolean, DateTime, JSON, Text, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    messages: Mapped[list] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    detected_emotion: Mapped[str] = mapped_column(String(50), nullable=True)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    crisis_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation {self.id} – {self.title}>"
