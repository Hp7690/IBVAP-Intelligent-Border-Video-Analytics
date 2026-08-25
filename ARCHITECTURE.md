# IBVAP Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CCTV Camera Network                          │
│  (IP-based cameras at BOPs, checkpoints, border roads)           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Camera 1         Camera 2       Camera N
   (RTSP/HTTP)      (RTSP/HTTP)    (RTSP/HTTP)
         │               │               │
         └───────────────┼───────────────┘
                         │ Video Streams
         ┌───────────────▼───────────────┐
         │   Stream Ingestion Layer      │
         │  (FastAPI WebSocket Handler)  │
         └───────────────┬───────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Stream         Stream          Stream
    Worker 1       Worker 2        Worker N
    (Camera 1)     (Camera 2)      (Camera N)
        │                │                │
        └────────────────┼────────────────┘
                         │ Frame Processing
        ┌────────────────▼────────────────┐
        │   Inference Engine             │
        │  (Multi-model pipeline)        │
        │                                │
        │  ┌──────────────────────────┐  │
        │  │   YOLO v8 (Human,       │  │
        │  │   Vehicle, Weapon)      │  │
        │  ├──────────────────────────┤  │
        │  │   RetinaFace             │  │
        │  │   (Face Detection)       │  │
        │  ├──────────────────────────┤  │
        │  │   MediaPipe Pose         │  │
        │  │   (Behavior Analysis)    │  │
        │  ├──────────────────────────┤  │
        │  │   PaddleOCR              │  │
        │  │   (ANPR/Plate Reading)   │  │
        │  ├──────────────────────────┤  │
        │  │   Activity Detector      │  │
        │  │   (Anomaly Detection)    │  │
        │  ├──────────────────────────┤  │
        │  │   Night Mode Detector    │  │
        │  │   (Low-light Handling)   │  │
        │  └──────────────────────────┘  │
        │                                │
        └────────────────┬────────────────┘
                         │ Detection Results
        ┌────────────────▼────────────────┐
        │      Event Bus (Redis)         │
        │  Pub/Sub + Alert Queue         │
        │                                │
        │  Events Channel                │
        │  Alerts Queue                  │
        │  Analytics Stream              │
        └────────────────┬────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    Alert           Storage          Analytics
    Manager         Service          Engine
        │                │                │
        │         ┌──────┴──────┐        │
        │         │             │        │
        │      Local         S3/MinIO    │
        │      Storage       Storage     │
        │                                │
    WebSocket              Database
    Connections      (PostgreSQL)
        │                │
        └────────────────┼────────────────┐
                         │                │
        ┌────────────────▼────────────┐  │
        │   Backend API (FastAPI)    │  │
        │                            │  │
        │  • Alert Endpoints         │  │
        │  • Camera Management       │  │
        │  • Analytics              │  │
        │  • Admin Configuration    │  │
        │  • WebSocket Server       │  │
        └────────────────┬───────────┘  │
                         │               │
        ┌────────────────┼───────────────┐
        │                │               │
   Frontend (React)  Mobile App      3rd Party
   Dashboard          (Future)      Integration
        │                │               │
        └────────────────┴───────────────┘
```

## Component Architecture

### 1. Stream Ingestion Layer

**Purpose**: Connect to CCTV cameras and capture video streams

**Components**:
- `StreamWorker`: Manages single camera stream
- `StreamManager`: Orchestrates multiple workers
- Connection retry logic
- Frame buffering

**Technologies**:
- OpenCV for video capture
- FFmpeg for protocol handling
- Python asyncio for concurrency

```python
StreamWorker Flow:
  1. Connect to RTSP/HTTP stream
  2. Read frames from stream
  3. Skip frames (configurable interval)
  4. Pass to Inference Engine
  5. Handle disconnections with retry
```

### 2. Inference Engine

**Purpose**: Run all AI/ML models on video frames

**Models Pipeline**:

```
Frame Input
    │
    ├─→ [Night Mode Check]
    │   ├─ Night → Motion Trigger → Enhance → Detect
    │   └─ Day → Detect
    │
    ├─→ [Human Detection] (YOLOv8)
    │   └─ Track with DeepSORT/ByteTrack
    │
    ├─→ [Vehicle Detection] (YOLOv8)
    │   └─ Classify: Car/Truck/Bus/Bike
    │
    ├─→ [Face Detection] (RetinaFace)
    │   └─ Extract embeddings
    │
    ├─→ [Pose Estimation] (MediaPipe)
    │   └─ Analyze behavior
    │
    ├─→ [Plate Detection] (YOLO)
    │   └─ OCR with PaddleOCR
    │
    └─→ [Weapon Detection] (Fine-tuned YOLO)
        └─ High confidence threshold
```

**Performance**:
- Parallel detection (can run simultaneously)
- GPU acceleration for YOLO models
- CPU efficient pose estimation
- Batch processing when possible

### 3. Activity Detection Layer

**Purpose**: Detect suspicious behaviors and anomalies

**Algorithms**:

1. **Trajectory Analysis**
   - Track object centers over time
   - Detect fence approach (distance trending down)
   - Detect loitering (minimal movement)
   - Detect zigzag patterns (suspicious evasion)

2. **Pose-Based Detection**
   - Crawling: Head-to-feet vertical distance < 30%
   - Climbing: Arms elevated > 10% above shoulders
   - Running: Pose keypoint velocity high

3. **Zone-Based Detection**
   - Point-in-polygon algorithm
   - Intrusion detection (entering restricted zone)
   - Loitering detection (staying in zone)
   - Crossing detection (crossing boundary line)

### 4. Alert Management System

**Alert Flow**:

```
Detection Result
    │
    ├─→ Generate Alert Object
    │   ├─ Alert ID (UUID)
    │   ├─ Type (human/vehicle/intrusion/weapon)
    │   ├─ Severity (low/medium/high/critical)
    │   ├─ Confidence Score
    │   ├─ Snapshot/Clip URL
    │   └─ Timestamp
    │
    ├─→ Save to Database
    │   └─ PostgreSQL alerts table
    │
    ├─→ Publish to Event Bus
    │   └─ Redis Pub/Sub
    │
    ├─→ Alert Manager
    │   ├─ Check admin online status
    │   ├─ If online → WebSocket push
    │   └─ If offline → Queue for next login
    │
    └─→ Notifications (optional)
        ├─ Email
        ├─ SMS
        └─ Audible alert
```

**Alert Severity Levels**:
- **CRITICAL**: Weapons, intrusions
  - Immediate notification
  - Audible alert
  - Auto-escalation

- **HIGH**: Suspicious activity, climbing, unauthorized access
  - Push notification
  - Visual alert
  - Logged immediately

- **MEDIUM**: Unregistered faces, loitering
  - Dashboard alert
  - Stored for review
  - Analyzed for patterns

- **LOW**: General human/vehicle detection
  - Statistics only
  - Not pushed immediately
  - Aggregated in analytics

### 5. Database Schema

```sql
-- Cameras table
CREATE TABLE cameras (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    bop_id VARCHAR(50),  -- Border Out Post ID
    rtsp_url VARCHAR(1024),
    latitude FLOAT,
    longitude FLOAT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Zones (virtual fences)
CREATE TABLE zones (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) REFERENCES cameras(id),
    name VARCHAR(255),
    zone_type VARCHAR(50),  -- 'restricted', 'intrusion', 'loitering'
    coordinates JSON,  -- Polygon coordinates
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Alerts
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) REFERENCES cameras(id),
    alert_type VARCHAR(50),
    severity VARCHAR(20),  -- 'low', 'medium', 'high', 'critical'
    message TEXT,
    confidence FLOAT,
    snapshot_url VARCHAR(1024),
    video_clip_url VARCHAR(1024),
    metadata JSON,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Events (audit trail)
CREATE TABLE events (
    id VARCHAR(36) PRIMARY KEY,
    camera_id VARCHAR(36) REFERENCES cameras(id),
    event_type VARCHAR(50),
    description TEXT,
    data JSON,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Watchlist (for face recognition)
CREATE TABLE watchlist (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(50),  -- 'blacklist', 'whitelist', 'vip'
    face_embedding JSON,  -- Serialized vector
    metadata JSON,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. Redis Data Structures

```
Key Patterns:

alerts_queue          - List of pending alerts (FIFO)
events_channel        - Pub/Sub channel for events
alerts_channel        - Pub/Sub channel for alerts
camera:{id}:status    - String (online/offline)
camera:{id}:metrics   - Hash (FPS, latency, errors)
track:{id}            - Hash (centroid, velocity, age)
```

### 7. API Layer Architecture

**Request Flow**:

```
HTTP Request
    │
    ├─→ FastAPI Router
    │   ├─ Path matching
    │   └─ Parameter validation
    │
    ├─→ Authentication (JWT)
    │   └─ Token validation
    │
    ├─→ Authorization (RBAC)
    │   └─ Permission check
    │
    ├─→ Request Handler
    │   ├─ Business Logic
    │   ├─ Database Query
    │   └─ Service Call
    │
    ├─→ Response Serialization
    │   └─ Pydantic model
    │
    └─→ HTTP Response (JSON)
```

## Data Flow Examples

### Example 1: Human Detection and Alert

```
1. StreamWorker reads frame from camera
2. Pass to InferenceEngine.analyze_frame()
3. HumanDetector.detect() runs YOLOv8
4. Returns detections: [{class: 'person', confidence: 0.95, bbox: [...]}]
5. Trajectory updated for tracking
6. Check for suspicious activity
7. Generate AlertCreate object
8. Save to database
9. Publish to Redis 'alerts' channel
10. AlertManager receives event
11. Check if admin is online
12. Send WebSocket message to admin
13. Admin receives real-time alert on dashboard
```

### Example 2: Night-time Movement Detection

```
1. Frame received (low brightness)
2. InferenceEngine detects night mode
3. NightModeDetector.detect_motion() runs MOG2
4. Motion detected → Enhanced frame
5. Run lightweight detector on enhanced frame
6. Person/Vehicle detected
7. High confidence → Alert generated
8. Snapshot captured and stored
9. Alert sent to admin with snapshot URL
```

### Example 3: Weapon Detection

```
1. Frame received
2. WeaponDetector.detect() with high threshold (0.85)
3. Weapon detected (confidence: 0.92)
4. Generate CRITICAL alert
5. Save snapshot and create video clip
6. Publish to Redis
7. Play audible alert on admin dashboard
8. Push notification to all admins
9. Auto-escalate to command center
10. Log incident with full metadata
```

## Scalability Considerations

### Horizontal Scaling

```
Multiple Backend Instances:

┌─────────────────────────────────────┐
│     Load Balancer (Nginx/HAProxy)   │
└────────┬────────────────┬───────────┘
         │                │
    ┌────▼────┐      ┌───▼─────┐
    │Backend 1 │      │Backend 2 │
    │ Instance │      │ Instance │
    └────┬─────┘      └───┬──────┘
         │                │
    ┌────▼────────────────▼─────┐
    │  Shared Redis (Pub/Sub)   │
    │  Shared PostgreSQL DB      │
    └───────────────────────────┘

Benefits:
- Horizontal stream processing
- Distributed inference
- Shared alert queue
- Load distribution
```

### Vertical Scaling

```
GPU Acceleration:
- Multi-GPU support via NVIDIA Triton
- Model parallelism
- Batch inference optimization
- CUDA-optimized operations

Memory Optimization:
- Model quantization (INT8)
- Frame batching
- Efficient buffer management
- Memory pooling
```

## Security Architecture

```
┌─────────────────────────────────────┐
│        External Requests            │
└────────────────┬────────────────────┘
                 │
        ┌────────▼────────┐
        │ Firewall/WAF    │
        │ Rate Limiting   │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ TLS/SSL         │
        │ Encryption      │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ JWT Auth        │
        │ Token Validation│
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ RBAC            │
        │ Permission Check│
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ Input Validation│
        │ SQL Injection   │
        │ XSS Prevention  │
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │ API Handler     │
        │ Safe Operation  │
        └─────────────────┘
```

## Monitoring & Logging

```
Logging Strategy:

Application Logs:
- INFO: Normal operations
- WARNING: Anomalies, degradation
- ERROR: Failures, exceptions
- DEBUG: Detailed flow (development only)

Metrics Collected:
- Stream health (FPS, latency)
- Detection performance (accuracy, speed)
- Alert generation rate
- System resource usage (CPU, GPU, Memory)
- API response times
- Error rates

Visualization:
- Grafana dashboards
- Real-time metrics
- Historical trends
- Alerts on thresholds

Log Aggregation:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Centralized logging
- Full-text search
- Correlation analysis
```

## Disaster Recovery

```
Redundancy Levels:

1. Database Replication
   - Primary PostgreSQL
   - Replicated followers
   - Automatic failover

2. Redis Persistence
   - Periodic snapshots (RDB)
   - Write-ahead logging (AOF)
   - Quick recovery

3. Alert Persistence
   - Alerts saved to database
   - Offline queue in Redis
   - Delivered on reconnection

4. Stream Reconnection
   - Auto-reconnect on failure
   - Configurable retry limits
   - Connection pooling

5. Backup Strategy
   - Daily database backups
   - 30-day retention
   - Tested recovery procedures
```

## Performance Optimization

### Memory Management
- Object pooling for frame buffers
- Efficient numpy operations
- Garbage collection tuning
- Memory limits per worker

### CPU Optimization
- Frame skipping in low-priority streams
- Model lightweight versions
- Vectorized operations
- Async I/O for blocking operations

### GPU Optimization
- CUDA memory pooling
- Batch inference
- Mixed precision (FP16)
- Model quantization
- TensorRT optimization

### Network Optimization
- Frame compression
- Adaptive streaming quality
- WebSocket binary frames
- Connection pooling

---

**Architecture Version**: 1.0
**Last Updated**: 2026-08-25
