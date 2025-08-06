from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
import redis
from app.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])
settings = get_settings()


@router.get("/")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "face-recognition-api"}


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Check if service is ready (DB and Redis connections)."""
    status = {"database": False, "redis": False}

    # Check database
    try:
        db.execute("SELECT 1")
        status["database"] = True
    except Exception as e:
        pass

    # Check Redis
    if settings.use_redis_cache:
        try:
            r = redis.from_url(settings.redis_url)
            r.ping()
            status["redis"] = True
        except Exception as e:
            pass
    else:
        status["redis"] = True  # Not required

    is_ready = all(status.values())

    return {
        "ready": is_ready,
        "checks": status
    }