"""Face detection using RetinaFace"""
import logging
from typing import List
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)


class FaceDetector:
    """Detects faces in video frames"""
    
    def __init__(self):
        try:
            from retinaface import RetinaFace
            self.detector = RetinaFace
            logger.info("Loaded RetinaFace detector")
        except ImportError:
            logger.warning("RetinaFace not installed. Install with: pip install retinaface")
            self.detector = None
        
        self.confidence_threshold = settings.FACE_DETECTION_THRESHOLD
    
    def detect(self, frame: np.ndarray) -> List[dict]:
        """Detect faces in frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of face detections
        """
        if self.detector is None:
            return []
        
        try:
            detections = self.detector.detect_faces(frame)
            
            results = []
            if isinstance(detections, dict):
                for face_key, face_data in detections.items():
                    if "facial_area" in face_data:
                        x1, y1, x2, y2 = face_data["facial_area"]
                        confidence = face_data.get("score", 0)
                        
                        if confidence > self.confidence_threshold:
                            results.append({
                                "class": "face",
                                "confidence": float(confidence),
                                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                                "landmarks": face_data.get("landmarks", None)
                            })
            
            return results
        except Exception as e:
            logger.error(f"Error in face detection: {str(e)}")
            return []
