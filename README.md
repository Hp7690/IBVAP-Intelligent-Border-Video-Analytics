# IBVAP - Intelligent Border Video Analytics Platform

An AI-Based Intelligent Video Analytics Platform for Border Surveillance using existing CCTV Infrastructure.

## Overview

IBVAP transforms standard IP-based CCTV cameras into an intelligent surveillance network using AI and Computer Vision. It eliminates the need for expensive dedicated surveillance hardware while providing advanced security capabilities.

## Key Features

### 1. **Real-time Alert System**
- WebSocket/SSE-based push notifications to admin dashboard
- Alert persistence (Redis/Database) for offline admins
- Multi-camera event aggregation
- Alert payload: camera ID, BOP location, event type, timestamp, confidence, snapshot/clip URL

### 2. **Human Detection & Tracking**
- Real-time person detection and tracking
- DeepSORT/ByteTrack for multi-object tracking
- Trajectory analysis for behavior prediction

### 3. **Vehicle Detection & Classification**
- YOLOv8-based vehicle detection
- Classification: Car, Truck, Bike, Motorcycle
- Real-time capability on modest hardware

### 4. **Automatic Number Plate Recognition (ANPR)**
- Two-stage pipeline: Plate localization → OCR
- YOLO fine-tuned plate detection
- PaddleOCR/EasyOCR for Indian plate recognition
- Indian plate format validation

### 5. **Face Detection & Recognition**
- RetinaFace/MediaPipe for fast detection
- ArcFace/FaceNet embeddings for identification
- FAISS-based watchlist matching
- Restricted zone tracking

### 6. **Suspicious Activity Detection**
- Pose estimation (MediaPipe Pose/YOLO-Pose)
- Rule-based logic: crawling, climbing, running, loitering
- Trajectory anomaly detection
- Fence-approach pattern recognition
- Explainable alerts (rule-based, not black-box)

### 7. **Night-time Movement Detection**
- IR/Low-light footage handling
- Motion trigger via background subtraction (MOG2)
- Low-light enhancement (Histogram Equalization/Zero-DCE)
- Efficient frame-by-frame processing

### 8. **Intrusion Detection**
- Virtual fence configuration
- Zone-based alerts
- Boundary crossing detection
- Perimeter protection

### 9. **Gun/Weapon Detection**
- Fine-tuned YOLOv8 on firearm datasets
- High confidence thresholding
- Critical severity alerts with audible notifications
- Auto-escalation to incident dashboard

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CCTV Cameras (IP-Based)                  │
└────────────────────┬────────────────────────────────────────┘
                     │ RTMP/RTSP/HTTP Streams
┌────────────────────▼────────────────────────────────────────┐
│                 Stream Ingestion Service                     │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼──┐  ┌──────▼───┐  ┌────▼──────┐
│ Worker 1 │  │ Worker 2 │  │ Worker N  │
│(Stream A)│  │(Stream B)│  │(Stream N) │
└───────┬──┘  └──────┬───┘  └────┬──────┘
        │            │            │
        └────────────┼────────────┘
                     │ (Events)
        ┌────────────▼────────────┐
        │      Event Bus (Redis)  │
        └────────────┬────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   ┌────▼──┐  ┌──────▼──┐  ┌─────▼────┐
   │Alert  │  │ Storage │  │Analytics │
   │Manager│  │ Service │  │ Engine   │
   └───┬───┘  └──────┬──┘  └─────┬────┘
       │             │            │
       └─────────────┼────────────┘
                     │
        ┌────────────▼─────────────┐
        │    Backend API (FastAPI) │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │  Frontend Dashboard (React)
        │  + WebSocket Connection  │
        └──────────────────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI (async, WebSocket support)
- **Video Processing**: OpenCV, FFmpeg
- **ML Models**: YOLOv8, MediaPipe, RetinaFace, PaddleOCR
- **Tracking**: DeepSORT, ByteTrack
- **Event Bus**: Redis (Pub/Sub)
- **Database**: PostgreSQL (alerts, configurations, events)
- **Cache**: Redis
- **Deployment**: Docker, Kubernetes
- **GPU Inference**: NVIDIA Triton, TensorRT

### Frontend
- **Framework**: React 18
- **Real-time**: Socket.io/WebSocket
- **UI Components**: Material-UI or Tailwind CSS
- **State Management**: Redux/Zustand
- **Charts**: Chart.js, Plotly
- **Mapping**: Leaflet (for BOP locations)

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose / Kubernetes
- **Message Queue**: Redis Streams
- **Storage**: MinIO/S3 (video clips, snapshots)
- **Logging**: ELK Stack / Grafana Loki
- **Monitoring**: Prometheus + Grafana

## Project Structure

```
IBVAP/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── alerts.py
│   │   │   ├── cameras.py
│   │   │   ├── analytics.py
│   │   │   └── admin.py
│   │   ├── models/
│   │   │   ├── database.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── stream_ingestion.py
│   │   │   ├── event_bus.py
│   │   │   ├── alert_manager.py
│   │   │   └── storage.py
│   │   ├── workers/
│   │   │   ├── stream_worker.py
│   │   │   ├── inference_engine.py
│   │   │   └── activity_detector.py
│   │   └── ml/
│   │       ├── detection/
│   │       │   ├── human_detector.py
│   │       │   ├── vehicle_detector.py
│   │       │   ├── face_detector.py
│   │       │   ├── weapon_detector.py
│   │       │   └── plate_detector.py
│   │       ├── tracking/
│   │       │   ├── deepsort_tracker.py
│   │       │   └── bytetrack_tracker.py
│   │       ├── anpr/
│   │       │   ├── plate_localization.py
│   │       │   └── ocr_engine.py
│   │       ├── pose/
│   │       │   └── pose_estimator.py
│   │       ├── anomaly/
│   │       │   ├── trajectory_analyzer.py
│   │       │   └── behavior_classifier.py
│   │       └── utils.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── AlertPanel.jsx
│   │   │   ├── CameraGrid.jsx
│   │   │   ├── EventLog.jsx
│   │   │   ├── Analytics.jsx
│   │   │   └── Map.jsx
│   │   ├── pages/
│   │   │   ├── Admin.jsx
│   │   │   ├── Reports.jsx
│   │   │   └── Settings.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── websocket.js
│   │   │   └── auth.js
│   │   ├── store/
│   │   │   └── slices/
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+
- NVIDIA GPU (optional, for faster inference)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hp7690/IBVAP-Intelligent-Border-Video-Analytics.git
   cd IBVAP-Intelligent-Border-Video-Analytics
   ```

2. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the dashboard**
   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## Features Breakdown

### 1. Real-time Alert System
- WebSocket push notifications
- Alert queuing for offline sessions
- Multi-severity levels
- Auto-escalation for critical events

### 2. Concurrent Stream Processing
- One worker per stream
- Independent event publishing
- Non-blocking alert generation
- Horizontal scalability

### 3. Night-time Detection
- Motion-triggered detection
- Low-light enhancement
- Reduced compute overhead
- IR footage optimization

### 4. Suspicious Activity
- Pose-based behavior analysis
- Trajectory anomaly detection
- Fence-approach alerts
- Loitering detection

### 5. ANPR Pipeline
- Plate detection & localization
- OCR with confidence scoring
- Indian plate format validation
- Cross-reference vehicle database

### 6. Gun Detection
- High-confidence thresholding
- Audible + visual alerts
- Incident escalation
- Evidence capture

## Configuration

Edit `backend/app/config.py` for:
- Model paths and confidence thresholds
- Alert severity levels
- Zone definitions and virtual fences
- API rate limits
- Redis/Database credentials

## Deployment

### Docker Compose (Development)
```bash
docker-compose -f docker-compose.yml up
```

### Kubernetes (Production)
```bash
kubectl apply -f k8s/
```

## Performance Metrics

- **Stream Processing**: 25-30 FPS per stream (1080p, RTX 3080)
- **Alert Latency**: < 500ms
- **Detection Accuracy**: 
  - Human: 95%+ (YOLO)
  - Vehicle: 92%+
  - Face: 98%+ (RetinaFace)
  - Plate: 85%+ (OCR dependent on image quality)
  - Weapon: 88%+ (dataset dependent)

## Security Considerations

- Role-based access control (RBAC)
- JWT authentication
- Encrypted video storage
- Audit logging
- Rate limiting
- Data retention policies

## Roadmap

- [ ] Multi-language OCR support
- [ ] Person re-identification (ReID)
- [ ] Crowd density estimation
- [ ] Behavioral anomaly detection with deep learning
- [ ] Mobile admin app
- [ ] Advanced analytics & predictive alerts
- [ ] Integration with national databases

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file

## Support

For issues, feature requests, or questions:
- Create an issue on GitHub
- Contact: support@ibvap.dev

## Acknowledgments

- YOLOv8 (Ultralytics)
- MediaPipe (Google)
- DeepSORT
- PaddleOCR
- RetinaFace

---

**Built with ❤️ for Border Security**
