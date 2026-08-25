"""Vehicle detection using YOLOv8"""
import logging
from typing import List
import numpy as np
from app.config import settings

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

logger = logging.getLogger(__name__)

VEHICLE_CLASSES = {
    2: "car",
    5: "bus",
    7: "truck",
    3: "motorcycle",
    4: "bicycle"
}


class VehicleDetector:
    """Detects and classifies vehicles in video frames"""
    
    def __init__(self, model_path: str = None):
        if YOLO is None:
            raise ImportError("YOLOv8 not installed")
        
        self.model_path = model_path or settings.YOLO_MODEL_PATH
        self.model = YOLO(self.model_path)
        self.confidence_threshold = settings.VEHICLE_DETECTION_THRESHOLD
        logger.info(f"Loaded vehicle detector from {self.model_path}")
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """Detect vehicles in frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of vehicle detections with classification
        """
        try:
            results = self.model(frame, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    if class_id in VEHICLE_CLASSES and box.conf > self.confidence_threshold:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detections.append({
                            "class": VEHICLE_CLASSES.get(class_id, "vehicle"),
                            "confidence": float(box.conf[0]),
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                            "track_id": None
                        })
            
            return detections
        except Exception as e:
            logger.error(f"Error in vehicle detection: {str(e)}")
            return []
