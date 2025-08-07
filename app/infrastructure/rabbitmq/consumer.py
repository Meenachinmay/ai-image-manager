import json
import logging
from typing import Dict, Callable
import aio_pika
from app.config import get_settings

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(self, connection):
        self.connection = connection
        self.settings = get_settings()
        self.handlers: Dict[str, Callable] = {}
        self.queue = None

    def register_handler(self, routing_key: str, handler: Callable):
        """Register a handler for a specific routing key."""
        self.handlers[routing_key] = handler
        logger.info(f"Registered handler for routing key: {routing_key}")

    async def start_consuming(self):
        """Start consuming messages from the queue."""
        try:
            # Declare queue
            self.queue = await self.connection.channel.declare_queue(
                name=self.settings.rabbitmq_queue_name,
                durable=True
            )

            # Bind queue to exchange with routing keys
            for routing_key in self.handlers.keys():
                await self.queue.bind(
                    exchange=self.connection.exchange,
                    routing_key=routing_key
                )
                logger.info(f"Bound queue to routing key: {routing_key}")

            # Start consuming
            async with self.queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        await self._process_message(message)

        except Exception as e:
            logger.error(f"Error in consumer: {e}")
            raise

    async def _process_message(self, message: aio_pika.IncomingMessage):
        """Process a single message."""
        try:
            routing_key = message.routing_key
            body = json.loads(message.body.decode())

            logger.info(f"Received message with routing key: {routing_key}")

            # Get handler for routing key
            handler = self.handlers.get(routing_key)
            if handler:
                await handler(body)
                logger.info(f"Successfully processed message: {body.get('event_id', 'unknown')}")
            else:
                logger.warning(f"No handler found for routing key: {routing_key}")

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Re-raise to trigger message requeue if needed
            raise