"""
Memory Service – stores and retrieves personalized user context across sessions.
"""

import logging
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wellness import UserMemory

logger = logging.getLogger(__name__)


class MemoryService:
    async def store_memory(
        self, db: AsyncSession, user_id: UUID,
        memory_type: str, content: str, metadata: dict = None
    ):
        memory = UserMemory(
            user_id=user_id, memory_type=memory_type,
            content=content, metadata_json=metadata or {},
        )
        db.add(memory)
        await db.flush()
        return memory

    async def get_relevant_memories(
        self, db: AsyncSession, user_id: UUID, limit: int = 10
    ) -> Optional[str]:
        result = await db.execute(
            select(UserMemory)
            .where(UserMemory.user_id == user_id)
            .order_by(UserMemory.relevance_score.desc(), UserMemory.created_at.desc())
            .limit(limit)
        )
        memories = result.scalars().all()
        if not memories:
            return None

        memory_text = []
        for m in memories:
            memory_text.append(f"[{m.memory_type}] {m.content}")
        return "\n".join(memory_text)

    async def extract_and_store(self, db: AsyncSession, user_id: UUID, message: str):
        """Extract notable information from a user message and store as memory."""
        key_phrases = [
            "my name is", "i work", "i live", "i have", "i'm dealing with",
            "i struggle with", "my goal", "i want to", "i need",
            "i feel", "i've been", "my therapist", "my doctor",
        ]
        msg_lower = message.lower()
        for phrase in key_phrases:
            if phrase in msg_lower:
                await self.store_memory(
                    db, user_id, "fact",
                    message[:500], {"source": "conversation"}
                )
                break


memory_service = MemoryService()
