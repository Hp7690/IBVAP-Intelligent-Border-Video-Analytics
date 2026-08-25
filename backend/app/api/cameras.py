"""Cameras API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import Camera, Zone, get_db
from app.models.schemas import CameraResponse, CameraCreate, ZoneResponse, ZoneCreate

router = APIRouter()


@router.post("/", response_model=CameraResponse)
async def create_camera(
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    """Create a new camera"""
    db_camera = Camera(
        id=camera.id,
        name=camera.name,
        location=camera.location,
        bop_id=camera.bop_id,
        rtsp_url=camera.rtsp_url,
        http_url=camera.http_url,
        latitude=camera.latitude,
        longitude=camera.longitude,
        resolution=camera.resolution,
        fps=camera.fps
    )
    
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    
    return db_camera


@router.get("/", response_model=List[CameraResponse])
async def get_cameras(db: Session = Depends(get_db)):
    """Get all cameras"""
    cameras = db.query(Camera).filter(Camera.active == True).all()
    return cameras


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: str,
    db: Session = Depends(get_db)
):
    """Get specific camera by ID"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera


@router.put("/{camera_id}")
async def update_camera(
    camera_id: str,
    camera: CameraCreate,
    db: Session = Depends(get_db)
):
    """Update camera configuration"""
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    db_camera.name = camera.name
    db_camera.location = camera.location
    db_camera.rtsp_url = camera.rtsp_url
    db_camera.fps = camera.fps
    
    db.commit()
    db.refresh(db_camera)
    
    return db_camera


@router.post("/{camera_id}/zones", response_model=ZoneResponse)
async def create_zone(
    camera_id: str,
    zone: ZoneCreate,
    db: Session = Depends(get_db)
):
    """Create a virtual zone for camera"""
    camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    import uuid
    zone_id = str(uuid.uuid4())
    
    db_zone = Zone(
        id=zone_id,
        camera_id=camera_id,
        name=zone.name,
        zone_type=zone.zone_type,
        coordinates=zone.coordinates,
        enabled=zone.enabled
    )
    
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    
    return db_zone


@router.get("/{camera_id}/zones", response_model=List[ZoneResponse])
async def get_zones(
    camera_id: str,
    db: Session = Depends(get_db)
):
    """Get all zones for camera"""
    zones = db.query(Zone).filter(Zone.camera_id == camera_id).all()
    return zones
