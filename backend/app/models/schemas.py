"""Pydantic schemas for API validation"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AlertSeverity(str, Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types"""
    HUMAN_DETECTION = "human_detection"
    VEHICLE_DETECTION = "vehicle_detection"
    INTRUSION = "intrusion"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    NIGHT_MOVEMENT = "night_movement"
    FACE_DETECTED = "face_detected"
    PLATE_DETECTED = "plate_detected"
    WEAPON_DETECTED = "weapon_detected"
    LOITERING = "loitering"
    CLIMBING = "climbing"
    CROSSING = "crossing"


class CameraCreate(BaseModel):
    """Camera creation schema"""
    id: str
    name: str
    location: str
    bop_id: str
    rtsp_url: str
    http_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resolution: str = "1920x1080"
    fps: int = 25


class CameraResponse(CameraCreate):
    """Camera response schema"""
    active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ZoneCreate(BaseModel):
    """Zone creation schema"""
    name: str
    zone_type: str  # "restricted", "intrusion", "loitering"
    coordinates: List[tuple]  # [[x1,y1], [x2,y2], ...]
    enabled: bool = True


class ZoneResponse(ZoneCreate):
    """Zone response schema"""
    id: str
    camera_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    """Alert creation schema"""
    camera_id: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    confidence: float = Field(ge=0, le=1)
    snapshot_url: Optional[str] = None
    video_clip_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertResponse(AlertCreate):
    """Alert response schema"""
    id: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventResponse(BaseModel):
    """Event response schema"""
    id: str
    camera_id: str
    event_type: str
    description: str
    data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DetectionResult(BaseModel):
    """Detection result schema"""
    object_type: str  # "person", "vehicle", "face", "plate", "weapon"
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    metadata: Optional[Dict[str, Any]] = None


class FrameAnalysisResult(BaseModel):
    """Frame analysis result schema"""
    camera_id: str
    timestamp: datetime
    detections: List[DetectionResult]
    alerts: List[AlertCreate]
    anomalies: Optional[List[Dict[str, Any]]] = None
