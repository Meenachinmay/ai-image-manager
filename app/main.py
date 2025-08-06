from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.v1.routes import api_router
from app.infrastructure.database.connection import engine
from app.infrastructure.database.models import Base
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create database tables
Base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

app = FastAPI(
    title="Face Recognition Service",
    description="AI-powered face recognition backend service",
    version="1.0.0",
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with prefix
app.include_router(api_router, prefix=settings.api_prefix)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Face Recognition Service starting up...")
    logger.info(f"Upload path: {settings.upload_path}")
    logger.info(f"Database URL: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'local'}")
    logger.info(f"Redis enabled: {settings.use_redis_cache}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Face Recognition Service shutting down...")


@app.get("/")
async def root():
    return {
        "message": "Face Recognition Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health/"
    }