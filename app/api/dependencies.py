from typing import Generator, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
import redis
from app.infrastructure.database.connection import get_db
from app.infrastructure.repositories.face_repository import FaceRepository
from app.infrastructure.storage.file_storage import FileStorage
from app.services.face_recognition_engine import FaceRecognitionEngine
from app.services.face_service import FaceService
from app.domain.interfaces.face_service_interface import IFaceService
from app.config import get_settings

settings = get_settings()


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client if configured."""
    if settings.use_redis_cache and settings.redis_url:
        return redis.from_url(settings.redis_url)
    return None


def get_face_service(db: Session = Depends(get_db)) -> IFaceService:
    """Dependency injection for face service."""
    repository = FaceRepository(db)
    storage = FileStorage(settings.upload_path)
    recognition_engine = FaceRecognitionEngine(
        tolerance=settings.face_tolerance,
        model=settings.face_encoding_model
    )
    redis_client = get_redis_client()

    return FaceService(
        repository=repository,
        storage=storage,
        recognition_engine=recognition_engine,
        redis_client=redis_client
    )