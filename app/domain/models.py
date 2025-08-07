from dataclasses import dataclass, field  # 'field' with lowercase 'f'
from datetime import datetime
from typing import Optional, List, Dict, Any
import numpy as np


@dataclass
class Person:
    id: Optional[int] = None
    name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FaceEncoding:
    id: Optional[int] = None
    person_id: int = 0
    encoding: np.ndarray = field(default_factory=lambda: np.array([]))
    image_path: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ImageUploadResult:
    success: bool
    person_name: Optional[str] = None
    confidence: float = 0.0
    image_path: str = ""
    message: str = ""
    is_new_person: bool = False


# RabbitMQ Event Models
@dataclass
class BaseEvent:
    event_id: str
    event_type: str
    timestamp: str
    data: Dict[str, Any]


@dataclass
class ImageReceivedEventData:
    image_id: str
    image_data: str  # base64 encoded
    file_name: str
    file_size: int
    mime_type: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FaceRecognitionEventData:
    image_id: str
    faces_found: int
    processing_ms: int
    results: List[Dict[str, Any]]
    person_name: Optional[str] = None
    confidence: float = 0.0
    message: str = ""


@dataclass
class DataSavedEventData:
    image_id: str
    saved_at: str
    success: bool
    storage_url: Optional[str] = None
    error: Optional[str] = None