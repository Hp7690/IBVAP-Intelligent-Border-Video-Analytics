"""Main FastAPI application"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.config import settings
from app.api import alerts, cameras, analytics, admin
from app.services.event_bus import EventBus
from app.services.alert_manager import AlertManager

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
event_bus: EventBus = None
alert_manager: AlertManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    global event_bus, alert_manager
    
    event_bus = EventBus(settings.REDIS_URL)
    alert_manager = AlertManager(event_bus)
    
    await event_bus.connect()
    await alert_manager.start()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await alert_manager.stop()
    await event_bus.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Based Intelligent Video Analytics Platform for Border Surveillance",
    lifespan=lifespan,
    debug=settings.DEBUG
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
)


# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "redis": "connected" if event_bus else "disconnected",
            "database": "connected",
            "gpu": "available" if settings.GPU_ENABLED else "disabled"
        }
    }


# API Routes
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


# WebSocket endpoint for real-time alerts
@app.websocket("/ws/alerts/{admin_id}")
async def websocket_alerts(websocket: WebSocket, admin_id: str):
    """WebSocket endpoint for real-time alert streaming"""
    await websocket.accept()
    logger.info(f"Admin {admin_id} connected to alerts WebSocket")
    
    try:
        # Subscribe admin to alerts
        await alert_manager.subscribe(admin_id, websocket)
        
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        logger.info(f"Admin {admin_id} disconnected from alerts WebSocket")
        await alert_manager.unsubscribe(admin_id)
    except Exception as e:
        logger.error(f"WebSocket error for admin {admin_id}: {str(e)}")
        await alert_manager.unsubscribe(admin_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
