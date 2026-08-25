"""Alerts API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.models.database import Alert, get_db
from app.models.schemas import AlertResponse, AlertCreate, AlertSeverity

router = APIRouter()


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    import uuid
    alert_id = str(uuid.uuid4())
    
    db_alert = Alert(
        id=alert_id,
        camera_id=alert.camera_id,
        alert_type=alert.alert_type.value,
        severity=alert.severity.value,
        message=alert.message,
        confidence=alert.confidence,
        snapshot_url=alert.snapshot_url,
        video_clip_url=alert.video_clip_url,
        metadata=alert.metadata,
        created_at=datetime.utcnow()
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    camera_id: str = Query(None),
    severity: AlertSeverity = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    query = db.query(Alert)
    
    if camera_id:
        query = query.filter(Alert.camera_id == camera_id)
    
    if severity:
        query = query.filter(Alert.severity == severity.value)
    
    # Get last 24 hours by default
    yesterday = datetime.utcnow() - timedelta(days=1)
    query = query.filter(Alert.created_at >= yesterday)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Get specific alert by ID"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.put("/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Mark alert as read"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    alert.is_read = True
    db.commit()
    
    return {"status": "success", "message": "Alert marked as read"}


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Delete alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    
    return {"status": "success", "message": "Alert deleted"}
