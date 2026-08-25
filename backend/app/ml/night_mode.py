"""Night-time detection enhancement"""
import logging
import numpy as np
import cv2
from typing import Tuple

logger = logging.getLogger(__name__)


class NightModeDetector:
    """Handles detection in low-light/IR footage"""
    
    def __init__(self, motion_threshold: int = 25, min_contour_area: int = 100):
        self.motion_threshold = motion_threshold
        self.min_contour_area = min_contour_area
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=False
        )
    
    def detect_motion(self, frame: np.ndarray) -> Tuple[bool, np.ndarray]:
        """Detect motion using background subtraction (MOG2)
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            (motion_detected, foreground_mask)
        """
        try:
            # Apply MOG2 background subtraction
            fg_mask = self.background_subtractor.apply(frame)
            
            # Morphological operations to clean up noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
            fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Check if significant motion detected
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) > self.min_contour_area:
                    motion_detected = True
                    break
            
            return motion_detected, fg_mask
        except Exception as e:
            logger.error(f"Error in motion detection: {str(e)}")
            return False, None
    
    def enhance_low_light(self, frame: np.ndarray) -> np.ndarray:
        """Enhance low-light frame for better detection
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Enhanced frame
        """
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge and convert back to BGR
            enhanced_lab = cv2.merge([l, a, b])
            enhanced_frame = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced_frame
        except Exception as e:
            logger.error(f"Error in low-light enhancement: {str(e)}")
            return frame
    
    def is_night_time(self, frame: np.ndarray) -> bool:
        """Detect if frame is from night-time/low-light
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            True if frame appears to be low-light
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate mean brightness
            brightness = np.mean(gray)
            
            # If average brightness is below threshold, it's night time
            return brightness < 100
        except Exception as e:
            logger.error(f"Error in night detection: {str(e)}")
            return False
