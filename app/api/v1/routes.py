from fastapi import APIRouter
from app.api.v1.handlers.face_handler import router as face_router
from app.api.v1.handlers.health_handler import router as health_router

api_router = APIRouter()

# Include all handlers
api_router.include_router(health_router)
api_router.include_router(face_router)