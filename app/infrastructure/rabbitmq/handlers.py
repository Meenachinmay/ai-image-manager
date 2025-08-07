import base64
import logging
import time
from typing import Dict, Any
from app.services.face_service import FaceService

logger = logging.getLogger(__name__)


class EventHandlers:
    def __init__(self, face_service: FaceService, publisher):
        self.face_service = face_service
        self.publisher = publisher

    async def handle_image_received(self, event: Dict[str, Any]):
        """
        Handle image.received event from Go API Gateway.

        Expected event structure from Go:
        {
            "event_id": "uuid",
            "event_type": "image.received",
            "timestamp": "RFC3339 timestamp",
            "data": {
                "image_id": "uuid",
                "image_data": "base64 encoded string",
                "file_name": "example.jpg",
                "file_size": 123456,
                "mime_type": "image/jpeg",
                "user_id": "user123",
                "name": "John Doe",  // Optional - for new person registration
                "metadata": {}
            }
        }
        """
        start_time = time.time()

        try:
            # Extract event metadata
            event_id = event.get("event_id")
            event_type = event.get("event_type")
            timestamp = event.get("timestamp")

            # Extract the actual data payload
            data = event.get("data", {})

            logger.info(f"Processing event {event_id} of type {event_type} from {timestamp}")

            # Extract ImageReceivedEventData fields
            image_id = data.get("image_id")
            image_data_base64 = data.get("image_data")
            filename = data.get("file_name")  # Note: Go uses file_name with underscore
            file_size = data.get("file_size")
            mime_type = data.get("mime_type")
            user_id = data.get("user_id")
            person_name = data.get("name")  # For new person registration
            metadata = data.get("metadata", {})

            # Validate required fields
            if not image_id:
                logger.error("Missing required field: image_id")
                return

            if not image_data_base64:
                logger.error(f"Missing image data for image_id: {image_id}")
                await self._publish_error(image_id, "No image data provided")
                return

            logger.info(
                f"Processing image {image_id}: filename={filename}, size={file_size}, mime={mime_type}, user={user_id}, person_name={person_name}")

            # Decode base64 image
            try:
                image_bytes = base64.b64decode(image_data_base64)
                logger.debug(f"Decoded image size: {len(image_bytes)} bytes")
            except Exception as e:
                logger.error(f"Failed to decode base64 for image {image_id}: {e}")
                await self._publish_error(image_id, "Invalid base64 image data")
                return

            # Process image using face service
            logger.info(f"Starting face recognition for image {image_id}")
            result = await self.face_service.process_image_from_event(
                image_bytes=image_bytes,
                filename=filename or "unknown.jpg",
                person_name=person_name,  # Will be None if not registering
                image_id=image_id
            )

            # Calculate processing time
            processing_ms = int((time.time() - start_time) * 1000)

            # Log result
            if result.get("success"):
                logger.info(
                    f"Face recognition successful for {image_id}: "
                    f"person={result.get('person_name')}, "
                    f"confidence={result.get('confidence'):.2%}, "
                    f"is_new={result.get('is_new_person')}, "
                    f"time={processing_ms}ms"
                )
            else:
                logger.warning(
                    f"Face recognition failed for {image_id}: "
                    f"{result.get('message')}, time={processing_ms}ms"
                )

            # Publish face.recognized event (matching Go's FaceRecognitionEventData)
            await self._publish_face_recognized(image_id, result, processing_ms)

            # Publish data.saved event (matching Go's DataSavedEventData)
            if result.get("success"):
                await self._publish_data_saved(
                    image_id=image_id,
                    success=True,
                    storage_url=result.get("image_path")
                )
            else:
                await self._publish_data_saved(
                    image_id=image_id,
                    success=False,
                    error=result.get("message", "Face recognition failed")
                )

        except Exception as e:
            logger.error(f"Unexpected error processing image event: {e}", exc_info=True)

            # Try to publish error event
            if 'image_id' in locals():
                await self._publish_error(image_id, str(e))
            raise

    async def _publish_face_recognized(self, image_id: str, result: Dict[str, Any], processing_ms: int):
        """Publish face.recognized event matching Go's structure."""
        # Build results array matching Go's FaceRecognitionResult
        results = []
        if result.get("success") and result.get("faces_found", 0) > 0:
            results.append({
                "face_id": f"face_{image_id}",  # Generate a face ID
                "confidence": result.get("confidence", 0.0),
                "bounding_box": {
                    "x": 0,
                    "y": 0,
                    "width": 0,
                    "height": 0
                },
                "attributes": {
                    "person_name": result.get("person_name"),
                    "is_new_person": result.get("is_new_person", False)
                }
            })

        # Create FaceRecognitionEventData
        face_data = {
            "image_id": image_id,
            "faces_found": result.get("faces_found", 0),
            "processing_ms": processing_ms,
            "results": results
        }

        # Publish with the same wrapper structure as Go
        await self.publisher.publish_event("face.recognition", face_data)

    async def _publish_data_saved(self, image_id: str, success: bool, storage_url: str = None, error: str = None):
        """Publish data.saved event matching Go's structure."""
        from datetime import datetime

        # Create DataSavedEventData
        saved_data = {
            "image_id": image_id,
            "saved_at": datetime.utcnow().isoformat(),
            "success": success,
            "storage_url": storage_url,
            "error": error
        }

        # Publish with the same wrapper structure as Go
        await self.publisher.publish_event("data.saved", saved_data)

    async def _publish_error(self, image_id: str, error: str):
        """Helper to publish error event."""
        await self._publish_data_saved(
            image_id=image_id,
            success=False,
            error=error
        )