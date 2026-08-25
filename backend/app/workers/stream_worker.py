"""Stream ingestion worker for processing video streams"""
import asyncio
import logging
from typing import Optional, Callable
import cv2
import numpy as np
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class StreamWorker:
    """Worker process for ingesting and processing video stream from single camera"""
    
    def __init__(
        self,
        camera_id: str,
        stream_url: str,
        frame_callback: Callable,
        reconnect_attempts: int = 5
    ):
        self.camera_id = camera_id
        self.stream_url = stream_url
        self.frame_callback = frame_callback
        self.reconnect_attempts = reconnect_attempts
        self.is_running = False
        self.cap = None
        self.frame_count = 0
        self.skip_interval = settings.FRAME_SKIP_INTERVAL
    
    async def start(self):
        """Start stream ingestion worker"""
        self.is_running = True
        logger.info(f"Starting stream worker for camera {self.camera_id}")
        asyncio.create_task(self._process_stream())
    
    async def stop(self):
        """Stop stream ingestion worker"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        logger.info(f"Stopped stream worker for camera {self.camera_id}")
    
    async def _process_stream(self):
        """Main stream processing loop"""
        reconnect_count = 0
        
        while self.is_running and reconnect_count < self.reconnect_attempts:
            try:
                # Open video stream
                self.cap = cv2.VideoCapture(self.stream_url)
                
                if not self.cap.isOpened():
                    raise Exception(f"Failed to open stream: {self.stream_url}")
                
                logger.info(f"Connected to stream for camera {self.camera_id}")
                reconnect_count = 0
                
                # Process frames
                while self.is_running:
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        raise Exception("Failed to read frame")
                    
                    # Skip frames for performance
                    if self.frame_count % self.skip_interval == 0:
                        # Process frame asynchronously
                        await self.frame_callback(self.camera_id, frame)
                    
                    self.frame_count += 1
                    
                    # Release CPU
                    await asyncio.sleep(0.001)
                
            except Exception as e:
                logger.error(f"Stream error for camera {self.camera_id}: {str(e)}")
                reconnect_count += 1
                
                if self.cap:
                    self.cap.release()
                
                # Wait before reconnecting
                await asyncio.sleep(5 * reconnect_count)
        
        if reconnect_count >= self.reconnect_attempts:
            logger.error(f"Max reconnect attempts reached for camera {self.camera_id}")
            self.is_running = False
