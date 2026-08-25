"""Human detection using YOLOv8"""
import logging
from typing import List, Tuple
import numpy as np
from app.config import settings

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

logger = logging.getLogger(__name__)


class HumanDetector:
    """Detects humans in video frames"""
    
    def __init__(self, model_path: str = None):
        if YOLO is None:
            raise ImportError("YOLOv8 not installed. Install with: pip install ultralytics")
        
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.model = YOLO(self.model_path)
        self.confidence_threshold = settings.HUMAN_DETECTION_THRESHOLD
        logger.info(f"Loaded human detector from {self.model_path}")
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """Detect humans in frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of detections with bounding boxes and confidence scores
        """
        try:
            results = self.model(frame, conf=self.confidence_threshold, classes=0)  # Class 0 = person
            
            detections = []
            for result in results:
                for box in result.boxes:
                    if box.conf > self.confidence_threshold:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detections.append({
                            "class": "person",
                            "confidence": float(box.conf[0]),
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                            "track_id": None  # Will be assigned by tracker
                        })
            
            return detections
        except Exception as e:
            logger.error(f"Error in human detection: {str(e)}")
            return []
