"""API handlers module."""
from app.api.v1.handlers.face_handler import router as face_router
from app.api.v1.handlers.health_handler import router as health_router

__all__ = ["face_router", "health_router"]