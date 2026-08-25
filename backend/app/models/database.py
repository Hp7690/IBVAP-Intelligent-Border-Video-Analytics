"""Database models for IBVAP"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Camera(Base):
    """Camera model"""
    __tablename__ = "cameras"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    bop_id = Column(String)  # Border Out Post ID
    rtsp_url = Column(String)
    http_url = Column(String)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    resolution = Column(String, default="1920x1080")
    fps = Column(Integer, default=25)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    zones = relationship("Zone", back_populates="camera")
    alerts = relationship("Alert", back_populates="camera")


class Zone(Base):
    """Virtual zone/fence configuration"""
    __tablename__ = "zones"
    
    id = Column(String, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.id"))
    name = Column(String)
    zone_type = Column(String)  # "restricted", "intrusion", "loitering"
    coordinates = Column(JSON)  # Polygon coordinates
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    camera = relationship("Camera", back_populates="zones")


class Alert(Base):
    """Alert model"""
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.id"))
    alert_type = Column(String, index=True)  # "human", "vehicle", "intrusion", "weapon", etc.
    severity = Column(String)  # "low", "medium", "high", "critical"
    message = Column(String)
    confidence = Column(Float)
    snapshot_url = Column(String, nullable=True)
    video_clip_url = Column(String, nullable=True)
    metadata = Column(JSON)  # Additional data: person_count, vehicle_type, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    camera = relationship("Camera", back_populates="alerts")


class Event(Base):
    """Event log model"""
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, index=True)
    camera_id = Column(String, ForeignKey("cameras.id"))
    event_type = Column(String, index=True)
    description = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class WatchlistEntry(Base):
    """Watchlist entry for face recognition"""
    __tablename__ = "watchlist"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)  # "blacklist", "whitelist", "vip"
    face_embedding = Column(JSON)  # Serialized embedding vector
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
