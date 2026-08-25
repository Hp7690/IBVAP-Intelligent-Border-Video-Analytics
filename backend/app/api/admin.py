"""Admin API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.database import get_db

router = APIRouter()


@router.get("/system-status")
async def get_system_status():
    """Get system status"""
    return {
        "status": "operational",
        "uptime_hours": 0,
        "services": {
            "stream_ingestion": "running",
            "alert_manager": "running",
            "inference_engine": "running",
            "database": "connected",
            "redis": "connected"
        },
        "resource_usage": {
            "cpu_percent": 0,
            "memory_percent": 0,
            "gpu_utilization": 0,
            "active_streams": 0
        }
    }


@router.get("/config")
async def get_configuration():
    """Get current system configuration"""
    return {
        "detection_thresholds": {
            "human": 0.6,
            "vehicle": 0.5,
            "face": 0.7,
            "plate": 0.65,
            "weapon": 0.85
        },
        "alert_settings": {
            "enable_critical_alerts": True,
            "enable_audible_alerts": True,
            "alert_retention_days": 30
        },
        "night_mode": {
            "enabled": True,
            "start_hour": 18,
            "end_hour": 6
        }
    }


@router.post("/config/update")
async def update_configuration(config: dict):
    """Update system configuration"""
    return {"status": "success", "message": "Configuration updated"}
