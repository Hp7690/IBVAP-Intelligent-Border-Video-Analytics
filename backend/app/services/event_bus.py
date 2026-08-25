"""Event bus service for pub/sub messaging"""
import redis.asyncio as redis
import json
import logging
from typing import Callable, List

logger = logging.getLogger(__name__)


class EventBus:
    """Redis-based event bus for publishing and subscribing to events"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
        self.subscribers = {}
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def publish(self, channel: str, message: dict):
        """Publish message to channel"""
        try:
            await self.redis_client.publish(
                channel,
                json.dumps(message)
            )
        except Exception as e:
            logger.error(f"Error publishing to {channel}: {str(e)}")
    
    async def subscribe(self, channel: str, callback: Callable):
        """Subscribe to channel"""
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)
        logger.info(f"Subscribed to channel: {channel}")
    
    async def unsubscribe(self, channel: str, callback: Callable):
        """Unsubscribe from channel"""
        if channel in self.subscribers:
            self.subscribers[channel].remove(callback)
            logger.info(f"Unsubscribed from channel: {channel}")
    
    async def enqueue_alert(self, alert: dict):
        """Enqueue alert for processing"""
        try:
            await self.redis_client.rpush(
                "alerts_queue",
                json.dumps(alert)
            )
        except Exception as e:
            logger.error(f"Error enqueuing alert: {str(e)}")
    
    async def dequeue_alert(self) -> dict:
        """Dequeue alert from processing queue"""
        try:
            alert_data = await self.redis_client.lpop("alerts_queue")
            if alert_data:
                return json.loads(alert_data)
            return None
        except Exception as e:
            logger.error(f"Error dequeuing alert: {str(e)}")
            return None
