"""Domain interfaces module."""
from app.domain.interfaces.face_service_interface import IFaceService
from app.domain.interfaces.face_repository_interface import IFaceRepository

__all__ = ["IFaceService", "IFaceRepository"]