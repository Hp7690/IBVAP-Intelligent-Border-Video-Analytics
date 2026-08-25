"""Weapon/Gun detection using fine-tuned YOLOv8"""
import logging
from typing import List
import numpy as np
from app.config import settings

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

logger = logging.getLogger(__name__)


class WeaponDetector:
    """Detects weapons (guns, rifles, pistols) in video frames"""
    
    def __init__(self, model_path: str = None):
        if YOLO is None:
            raise ImportError("YOLOv8 not installed")
        
        # Use a specialized weapon detection model if available
        self.model_path = model_path or "models/weapon_detection.pt"
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Loaded weapon detector from {self.model_path}")
        except:
            logger.warning(f"Weapon detector model not found at {self.model_path}")
            self.model = None
        
        # Use higher confidence threshold for weapons (reduce false positives)
        self.confidence_threshold = settings.WEAPON_DETECTION_THRESHOLD
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """Detect weapons in frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of weapon detections with high confidence threshold
        """
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    if box.conf > self.confidence_threshold:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        class_name = self.model.names.get(int(box.cls[0]), "weapon")
                        
                        detections.append({
                            "class": class_name,
                            "confidence": float(box.conf[0]),
                            "bbox": [float(x1), float(y1), float(x2), float(y2)],
                            "severity": "critical"  # Weapons are always critical
                        })
            
            return detections
        except Exception as e:
            logger.error(f"Error in weapon detection: {str(e)}")
            return []
