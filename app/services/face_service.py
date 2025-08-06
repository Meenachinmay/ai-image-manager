from typing import Optional, List
from pathlib import Path  # THIS IMPORT WAS MISSING!
from fastapi import UploadFile
import redis
import numpy as np
from app.domain.interfaces.face_service_interface import IFaceService
from app.domain.interfaces.face_repository_interface import IFaceRepository
from app.domain.models import ImageUploadResult, Person, FaceEncoding
from app.services.face_recognition_engine import FaceRecognitionEngine
from app.infrastructure.storage.file_storage import FileStorage
from app.config import get_settings
from app.core.exceptions import ValidationError


class FaceService(IFaceService):
    def __init__(
            self,
            repository: IFaceRepository,
            storage: FileStorage,
            recognition_engine: FaceRecognitionEngine,
            redis_client: Optional[redis.Redis] = None
    ):
        self.repository = repository
        self.storage = storage
        self.recognition_engine = recognition_engine
        self.redis_client = redis_client
        self.settings = get_settings()

    async def process_image(
            self,
            file: UploadFile,
            person_name: Optional[str] = None
    ) -> ImageUploadResult:
        """Process uploaded image for face recognition."""

        # Validate file
        if not file.filename:
            raise ValidationError("No filename provided")

        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.settings.allowed_extensions:
            raise ValidationError(f"File type {file_ext} not allowed")

        # Read file content
        content = await file.read()

        # Check file size
        if len(content) > self.settings.max_upload_size:
            raise ValidationError("File size exceeds maximum allowed")

        # Extract face encoding
        face_encoding = self.recognition_engine.extract_face_encoding(content)

        if face_encoding is None:
            return ImageUploadResult(
                success=False,
                person_name=None,
                confidence=0.0,
                image_path="",
                message="No face detected in the image"
            )

        # If person name is provided, this is a new person registration
        if person_name:
            return await self._register_new_person(person_name, face_encoding, content, file_ext)
        else:
            return await self._identify_person(face_encoding, content, file_ext)

    async def _register_new_person(
            self,
            name: str,
            face_encoding: np.ndarray,
            image_data: bytes,
            file_ext: str
    ) -> ImageUploadResult:
        """Register a new person with their face encoding."""

        # Check if person already exists
        existing_person = await self.repository.get_person_by_name(name)

        if existing_person:
            # Add another encoding for existing person
            person = existing_person
        else:
            # Create new person
            person = await self.repository.create_person(name)

        # Save image to storage
        image_path = self.storage.save_image(image_data, name, file_ext)

        # Save face encoding to database
        await self.repository.save_face_encoding(
            person_id=person.id,
            encoding=face_encoding,
            image_path=image_path
        )

        # Clear cache if using Redis
        if self.redis_client:
            self.redis_client.delete("face_encodings_cache")

        return ImageUploadResult(
            success=True,
            person_name=name,
            confidence=1.0,
            image_path=image_path,
            message=f"Successfully registered {name}",
            is_new_person=not existing_person
        )

    async def _identify_person(
            self,
            face_encoding: np.ndarray,
            image_data: bytes,
            file_ext: str
    ) -> ImageUploadResult:
        """Identify a person from their face encoding."""

        # Get all face encodings from cache or database
        all_encodings = await self._get_cached_encodings()

        if not all_encodings:
            return ImageUploadResult(
                success=False,
                person_name=None,
                confidence=0.0,
                image_path="",
                message="No registered faces in the system"
            )

        # Prepare encodings for comparison
        known_encodings = [enc.encoding for enc in all_encodings]

        # Compare faces
        is_match, match_index, confidence = self.recognition_engine.compare_faces(
            known_encodings,
            face_encoding
        )

        if not is_match:
            return ImageUploadResult(
                success=False,
                person_name=None,
                confidence=0.0,
                image_path="",
                message="Face not recognized"
            )

        # Get matched person
        matched_encoding = all_encodings[match_index]
        person = await self.repository.get_person_by_id(matched_encoding.person_id)

        if not person:
            return ImageUploadResult(
                success=False,
                person_name=None,
                confidence=0.0,
                image_path="",
                message="Person record not found"
            )

        # Save image to the person's folder
        image_path = self.storage.save_image(image_data, person.name, file_ext)

        # Optionally save this new encoding as well
        await self.repository.save_face_encoding(
            person_id=person.id,
            encoding=face_encoding,
            image_path=image_path
        )

        # Clear cache
        if self.redis_client:
            self.redis_client.delete("face_encodings_cache")

        return ImageUploadResult(
            success=True,
            person_name=person.name,
            confidence=confidence,
            image_path=image_path,
            message=f"Recognized as {person.name} with {confidence:.2%} confidence"
        )

    async def _get_cached_encodings(self) -> List[FaceEncoding]:
        """Get face encodings from cache or database."""
        if self.redis_client:
            # Try to get from cache
            cached = self.redis_client.get("face_encodings_cache")
            if cached:
                # Deserialize from cache
                # Note: This is simplified, you'd need proper serialization for numpy arrays
                pass

        # Get from database
        encodings = await self.repository.get_all_face_encodings()

        # Cache for future use (with TTL)
        if self.redis_client and encodings:
            # Serialize and cache (simplified)
            self.redis_client.setex("face_encodings_cache", 300, "serialized_data")

        return encodings

    async def get_all_persons(self) -> List[Person]:
        """Get all registered persons."""
        return await self.repository.get_all_persons()

    async def get_person_by_name(self, name: str) -> Optional[Person]:
        """Get a person by name."""
        return await self.repository.get_person_by_name(name)

    async def delete_person(self, person_id: int) -> bool:
        """Delete a person and their data."""
        person = await self.repository.get_person_by_id(person_id)
        if not person:
            return False

        # Delete from database
        success = await self.repository.delete_person(person_id)

        if success:
            # Delete person's folder
            self.storage.delete_person_folder(person.name)

            # Clear cache
            if self.redis_client:
                self.redis_client.delete("face_encodings_cache")

        return success