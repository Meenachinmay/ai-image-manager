import asyncio
import logging
import signal
import sys
from app.config import get_settings
from app.infrastructure.database.connection import engine, SessionLocal
from app.infrastructure.database.models import Base
from app.infrastructure.rabbitmq import RabbitMQConnection, RabbitMQConsumer, RabbitMQPublisher
from app.infrastructure.rabbitmq.handlers import EventHandlers
from app.services.face_service import FaceService
from app.infrastructure.repositories.face_repository import FaceRepository
from app.infrastructure.storage.file_storage import FileStorage
from app.services.face_recognition_engine import FaceRecognitionEngine
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


class FaceRecognitionWorker:
    def __init__(self):
        self.rabbitmq_connection = None
        self.rabbitmq_consumer = None
        self.rabbitmq_publisher = None
        self.shutdown_event = asyncio.Event()

    async def setup(self):
        """Initialize all services and connections."""
        logger.info("Initializing Face Recognition Worker...")

        # Create database tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")

        # Initialize RabbitMQ
        self.rabbitmq_connection = RabbitMQConnection()
        await self.rabbitmq_connection.connect()
        logger.info("Connected to RabbitMQ")

        # Create publisher
        self.rabbitmq_publisher = RabbitMQPublisher(self.rabbitmq_connection)

        # Create consumer
        self.rabbitmq_consumer = RabbitMQConsumer(self.rabbitmq_connection)

        # Initialize services
        db = SessionLocal()
        repository = FaceRepository(db)
        storage = FileStorage(settings.upload_path)
        recognition_engine = FaceRecognitionEngine(
            tolerance=settings.face_tolerance,
            model=settings.face_encoding_model
        )

        # Initialize Redis if configured
        redis_client = None
        if settings.use_redis_cache and settings.redis_url:
            try:
                redis_client = redis.from_url(settings.redis_url)
                redis_client.ping()
                logger.info("Connected to Redis")
            except Exception as e:
                logger.warning(f"Could not connect to Redis: {e}")

        # Create face service
        face_service = FaceService(
            repository=repository,
            storage=storage,
            recognition_engine=recognition_engine,
            redis_client=redis_client
        )

        # Create event handlers
        event_handlers = EventHandlers(face_service, self.rabbitmq_publisher)

        # Register handlers
        self.rabbitmq_consumer.register_handler("image.received", event_handlers.handle_image_received)

        logger.info("Worker setup completed")

    async def run(self):
        """Main worker loop."""
        try:
            await self.setup()

            logger.info("Starting to consume messages...")

            # Start consuming messages
            consumer_task = asyncio.create_task(self.rabbitmq_consumer.start_consuming())

            # Wait for shutdown signal
            await self.shutdown_event.wait()

            # Cancel consumer task
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            logger.error(f"Worker error: {e}")
            raise
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up...")

        if self.rabbitmq_connection:
            await self.rabbitmq_connection.disconnect()

        logger.info("Cleanup completed")

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown_event.set()


async def main():
    """Main entry point."""
    worker = FaceRecognitionWorker()

    # Setup signal handlers
    signal.signal(signal.SIGINT, worker.handle_shutdown)
    signal.signal(signal.SIGTERM, worker.handle_shutdown)

    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())