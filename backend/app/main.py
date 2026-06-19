"""
Helia AI – FastAPI Application Entry Point
Initializes the app, middleware, routes, and startup events.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import auth, chat, journal, mood, wellness, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: initialize database tables
    await init_db()

    # Initialize RAG service (loads FAISS index + embeddings model)
    from app.services.rag_service import rag_service
    await rag_service.initialize()

    yield

    # Shutdown: cleanup if needed


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Mental Well-being Assistant powered by AI",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat & AI"])
app.include_router(journal.router, prefix="/api/v1/journal", tags=["Journal"])
app.include_router(mood.router, prefix="/api/v1/mood", tags=["Mood Tracking"])
app.include_router(wellness.router, prefix="/api/v1/wellness", tags=["Wellness"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "message": "Welcome to Helia AI – Your Intelligent Mental Well-being Assistant",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
