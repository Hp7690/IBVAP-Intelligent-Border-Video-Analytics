"""License plate detection and ANPR"""
import logging
from typing import List, Tuple, Optional
import numpy as np
from app.config import settings

try:
    from ultralytics import YOLO
    from paddleocr import PaddleOCR
except ImportError:
    YOLO = None
    PaddleOCR = None

logger = logging.getLogger(__name__)

INDIAN_PLATE_PATTERN = r"^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$"  # Simplified pattern


class PlateDetector:
    """Detects license plates and performs OCR"""
    
    def __init__(self, plate_model_path: str = None):
        if YOLO is None or PaddleOCR is None:
            raise ImportError("Required dependencies not installed")
        
        self.plate_model_path = plate_model_path or "models/plate_detection.pt"
        try:
            self.plate_model = YOLO(self.plate_model_path)
            logger.info(f"Loaded plate detector from {self.plate_model_path}")
        except:
            logger.warning(f"Plate detector model not found at {self.plate_model_path}")
            self.plate_model = None
        
        # Initialize OCR engine
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')  # For Indian plates
            logger.info("Loaded PaddleOCR engine")
        except:
            self.ocr = None
            logger.warning("PaddleOCR engine failed to load")
        
        self.confidence_threshold = settings.PLATE_DETECTION_THRESHOLD
    
    def detect_plates(self, frame: np.ndarray) -> List[dict]:
        """Detect license plates in frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            List of plate detections
        """
        if self.plate_model is None:
            return []
        
        try:
            results = self.model(frame, conf=self.confidence_threshold)
            
            detections = []
            for result in results:
                for box in result.boxes:
                    if box.conf > self.confidence_threshold:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detections.append({
                            "class": "license_plate",
                            "confidence": float(box.conf[0]),
                            "bbox": [float(x1), float(y1), float(x2), float(y2)]
                        })
            
            return detections
        except Exception as e:
            logger.error(f"Error in plate detection: {str(e)}")
            return []
    
    def recognize_plate(self, plate_image: np.ndarray) -> Optional[str]:
        """Perform OCR on plate image
        
        Args:
            plate_image: Cropped plate image
            
        Returns:
            Recognized plate number or None
        """
        if self.ocr is None:
            return None
        
        try:
            result = self.ocr.ocr(plate_image, cls=True)
            if result and result[0]:
                plate_text = "".join([item[1][0] for item in result[0]])
                return plate_text.upper()
            return None
        except Exception as e:
            logger.error(f"Error in OCR: {str(e)}")
            return None
