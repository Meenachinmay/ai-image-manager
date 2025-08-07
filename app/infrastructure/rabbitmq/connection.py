import aio_pika
import logging
from typing import Optional
from app.config import get_settings

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    def __init__(self):
        self.settings = get_settings()
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None

    async def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            self.connection = await aio_pika.connect_robust(
                self.settings.rabbitmq_url,
                reconnect_interval=self.settings.rabbitmq_reconnect_delay
            )

            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=self.settings.rabbitmq_prefetch_count)

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                name=self.settings.rabbitmq_exchange,
                type=aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            logger.info(
                f"Connected to RabbitMQ at {self.settings.rabbitmq_url.split('@')[1] if '@' in self.settings.rabbitmq_url else 'localhost'}")

        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self):
        """Close RabbitMQ connection."""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("Disconnected from RabbitMQ")