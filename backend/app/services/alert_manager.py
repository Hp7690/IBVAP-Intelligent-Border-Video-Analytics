"""Alert manager service"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import WebSocket
from app.services.event_bus import EventBus
from app.models.schemas import AlertType, AlertSeverity

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alert distribution to connected admin sessions"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.active_connections: Dict[str, List[WebSocket]] = {}  # admin_id -> [websockets]
        self.alert_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.is_running = False
    
    async def start(self):
        """Start alert manager"""
        self.is_running = True
        asyncio.create_task(self._process_alerts())
        logger.info("Alert manager started")
    
    async def stop(self):
        """Stop alert manager"""
        self.is_running = False
        logger.info("Alert manager stopped")
    
    async def subscribe(self, admin_id: str, websocket: WebSocket):
        """Subscribe admin to alerts"""
        if admin_id not in self.active_connections:
            self.active_connections[admin_id] = []
        self.active_connections[admin_id].append(websocket)
        logger.info(f"Admin {admin_id} subscribed to alerts")
    
    async def unsubscribe(self, admin_id: str):
        """Unsubscribe admin from alerts"""
        if admin_id in self.active_connections:
            del self.active_connections[admin_id]
        logger.info(f"Admin {admin_id} unsubscribed from alerts")
    
    async def publish_alert(self, alert: dict):
        """Publish alert to connected admins"""
        try:
            await self.alert_queue.put(alert)
        except asyncio.QueueFull:
            logger.warning("Alert queue is full, alert dropped")
            # Store in persistent queue
            await self.event_bus.enqueue_alert(alert)
    
    async def _process_alerts(self):
        """Process queued alerts and send to connected admins"""
        while self.is_running:
            try:
                alert = await asyncio.wait_for(
                    self.alert_queue.get(),
                    timeout=1.0
                )
                
                # Send to all connected admins
                await self._broadcast_alert(alert)
                
                # Publish to Redis event bus
                await self.event_bus.publish("alerts", alert)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {str(e)}")
    
    async def _broadcast_alert(self, alert: dict):
        """Broadcast alert to all connected admins"""
        disconnected_admins = []
        
        for admin_id, websockets in self.active_connections.items():
            for websocket in websockets:
                try:
                    await websocket.send_json({
                        "type": "alert",
                        "data": alert,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error sending alert to admin {admin_id}: {str(e)}")
                    disconnected_admins.append(admin_id)
        
        # Clean up disconnected admins
        for admin_id in set(disconnected_admins):
            if admin_id in self.active_connections:
                del self.active_connections[admin_id]
    
    async def get_queued_alerts(self, limit: int = 50) -> List[dict]:
        """Get alerts from persistent queue"""
        alerts = []
        for _ in range(limit):
            alert = await self.event_bus.dequeue_alert()
            if alert:
                alerts.append(alert)
            else:
                break
        return alerts
    
    def is_admin_online(self, admin_id: str) -> bool:
        """Check if admin is currently online"""
        return admin_id in self.active_connections and len(self.active_connections[admin_id]) > 0
