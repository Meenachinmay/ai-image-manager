from abc import ABC, abstractmethod
from typing import Optional, List
from fastapi import UploadFile
from ..models import ImageUploadResult, Person


class IFaceService(ABC):
    @abstractmethod
    async def process_image(
            self,
            file: UploadFile,
            person_name: Optional[str] = None
    ) -> ImageUploadResult:
        pass

    @abstractmethod
    async def get_all_persons(self) -> List[Person]:
        pass

    @abstractmethod
    async def get_person_by_name(self, name: str) -> Optional[Person]:
        pass

    @abstractmethod
    async def delete_person(self, person_id: int) -> bool:
        pass