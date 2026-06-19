"""
Helia AI – Application Configuration
Loads settings from environment variables using Pydantic Settings.
Supports PostgreSQL (production) and SQLite (local development).
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application-wide settings loaded from .env file."""

    # --- App ---
    APP_NAME: str = "Helia AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # --- Database ---
    POSTGRES_USER: str = "helia_user"
    POSTGRES_PASSWORD: str = "change_me_in_production"
    POSTGRES_DB: str = "helia_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = ""  # Will be computed

    # --- JWT ---
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- LLM Provider ---
    LLM_PROVIDER: str = "groq"  # "groq" or "ollama"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # --- Ollama (fallback / local) ---
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # --- Performance / Optimization ---
    DISABLE_RAG: bool = False


    @property
    def LLM_MODEL(self) -> str:
        """Return the model name for the active provider."""
        if self.LLM_PROVIDER == "groq":
            return self.GROQ_MODEL
        return self.OLLAMA_MODEL

    # --- CORS ---
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    CORS_ORIGINS_STR: str = ""  # Comma-separated list of allowed origins

    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = [self.FRONTEND_URL, "http://localhost:3000", "http://localhost:3001"]
        if self.CORS_ORIGINS_STR:
            origins.extend([o.strip() for o in self.CORS_ORIGINS_STR.split(",") if o.strip()])
        return list(set(origins))

    @property
    def EFFECTIVE_DATABASE_URL(self) -> str:
        """Return the database URL, falling back to SQLite if PostgreSQL is unreachable."""
        if self.DATABASE_URL and self.DATABASE_URL.startswith("sqlite"):
            return self.DATABASE_URL

        # Build PostgreSQL URL
        pg_url = self.DATABASE_URL or f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        # Normalize: Render gives postgresql://, we need postgresql+asyncpg://
        if pg_url.startswith("postgresql://"):
            pg_url = pg_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif pg_url.startswith("postgres://"):
            pg_url = pg_url.replace("postgres://", "postgresql+asyncpg://", 1)

        if self._test_postgres_connection():
            return pg_url

        # Fallback to SQLite
        db_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sqlite_path = os.path.join(db_dir, "helia_dev.db")
        print(f"[WARNING] PostgreSQL unavailable. Using SQLite: {sqlite_path}")
        return f"sqlite+aiosqlite:///{sqlite_path}"

    def _test_postgres_connection(self) -> bool:
        """Quick check if PostgreSQL is reachable."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((self.POSTGRES_HOST, self.POSTGRES_PORT))
            s.close()
            if result != 0:
                return False
            # Port is open, try actual connection
            try:
                import psycopg2
                conn = psycopg2.connect(
                    host=self.POSTGRES_HOST, port=self.POSTGRES_PORT,
                    user=self.POSTGRES_USER, password=self.POSTGRES_PASSWORD,
                    dbname=self.POSTGRES_DB, connect_timeout=2,
                )
                conn.close()
                return True
            except Exception:
                return False
        except Exception:
            return False

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton settings instance
settings = Settings()
