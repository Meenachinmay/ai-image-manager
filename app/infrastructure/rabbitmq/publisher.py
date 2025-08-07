import json
import logging
from typing import Any, Dict
from datetime import datetime
import aio_pika
from app.config import get_settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self, connection):
        self.connection = connection
        self.settings = get_settings()

    async def publish_event(self, routing_key: str, event_data: Dict[str, Any]):
        """Publish an event to RabbitMQ."""
        try:
            message_body = json.dumps(event_data, default=str)

            message = aio_pika.Message(
                body=message_body.encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            await self.connection.exchange.publish(
                message=message,
                routing_key=routing_key
            )

            logger.info(f"Published event to {routing_key}: {event_data.get('event_id', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise

    async def publish_face_recognized(self, image_id: str, result: Dict[str, Any]):
        """Publish face recognition result."""
        event_data = {
            "event_id": f"face_{image_id}",
            "event_type": "face.recognition",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "image_id": image_id,
                "faces_found": result.get("faces_found", 0),
                "processing_ms": result.get("processing_ms", 0),
                "person_name": result.get("person_name"),
                "confidence": result.get("confidence", 0.0),
                "message": result.get("message", ""),
                "success": result.get("success", False)
            }
        }

        await self.publish_event("face.recognition", event_data)

    async def publish_data_saved(self, image_id: str, success: bool, storage_url: str = None, error: str = None):
        """Publish data saved event."""
        event_data = {
            "event_id": f"saved_{image_id}",
            "event_type": "data.saved",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "image_id": image_id,
                "saved_at": datetime.utcnow().isoformat(),
                "success": success,
                "storage_url": storage_url,
                "error": error
            }
        }

        await self.publish_event("data.saved", event_data)