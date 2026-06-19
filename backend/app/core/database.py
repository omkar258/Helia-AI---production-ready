"""
Helia AI – Database Engine & Session Management
Supports async PostgreSQL (asyncpg) and async SQLite (aiosqlite).
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


db_url = settings.EFFECTIVE_DATABASE_URL
is_sqlite = db_url.startswith("sqlite")

# Engine kwargs differ between PostgreSQL and SQLite
engine_kwargs = {
    "echo": settings.DEBUG,
}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })

# Create async engine
engine = create_async_engine(db_url, **engine_kwargs)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency that provides an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables (for development only; use Alembic in production)."""
    # Import all models so they register with Base.metadata
    from app.models import User, Conversation, JournalEntry, MoodLog, WellnessPlan, UserMemory  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db_type = "SQLite" if is_sqlite else "PostgreSQL"
    print(f"[OK] Database tables created ({db_type})")
