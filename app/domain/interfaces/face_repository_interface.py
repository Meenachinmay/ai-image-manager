from abc import ABC, abstractmethod
from typing import Optional, List
import numpy as np
from ..models import Person, FaceEncoding


class IFaceRepository(ABC):
    @abstractmethod
    async def create_person(self, name: str) -> Person:
        pass

    @abstractmethod
    async def get_person_by_id(self, person_id: int) -> Optional[Person]:
        pass

    @abstractmethod
    async def get_person_by_name(self, name: str) -> Optional[Person]:
        pass

    @abstractmethod
    async def get_all_persons(self) -> List[Person]:
        pass

    @abstractmethod
    async def save_face_encoding(
            self,
            person_id: int,
            encoding: np.ndarray,
            image_path: str
    ) -> FaceEncoding:
        pass

    @abstractmethod
    async def get_all_face_encodings(self) -> List[FaceEncoding]:
        pass

    @abstractmethod
    async def delete_person(self, person_id: int) -> bool:
        pass