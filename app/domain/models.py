from dataclasses import dataclass, field  # 'field' with lowercase 'f'
from datetime import datetime
from typing import Optional, List
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