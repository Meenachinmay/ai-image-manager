from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional, Set


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/face_recognition_local"

    # Redis
    redis_url: Optional[str] = "redis://localhost:6379"
    use_redis_cache: bool = True

    # RabbitMQ settings
    rabbitmq_url: str = "amqp://admin:admin123@localhost:5672/"
    rabbitmq_exchange: str = "image_processing"
    rabbitmq_exchange_type: str = "topic"
    rabbitmq_queue_name: str = "face_recognition_queue"
    rabbitmq_prefetch_count: int = 1
    rabbitmq_reconnect_delay: int = 5

    # Upload settings
    upload_path: str = "./uploads"
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: Set[str] = Field(
        default_factory=lambda: {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    )

    # Face recognition settings
    face_encoding_model: str = "hog"  # 'hog' is faster, 'cnn' is more accurate
    face_tolerance: float = 0.6

    # Worker settings
    worker_name: str = "face_recognition_worker"
    log_level: str = "INFO"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()