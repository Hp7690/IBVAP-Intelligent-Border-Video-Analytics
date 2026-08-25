"""Pose estimation for behavioral analysis"""
import logging
from typing import List, Dict, Optional
import numpy as np

try:
    import mediapipe as mp
except ImportError:
    mp = None

logger = logging.getLogger(__name__)


class PoseEstimator:
    """Estimates human pose for behavioral analysis"""
    
    def __init__(self):
        if mp is None:
            raise ImportError("MediaPipe not installed. Install with: pip install mediapipe")
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("Loaded MediaPipe Pose estimator")
    
    def estimate(self, frame: np.ndarray) -> Optional[Dict]:
        """Estimate pose in frame
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            Pose landmarks or None
        """
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(rgb_frame)
            
            if results.pose_landmarks:
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append({
                        "x": landmark.x,
                        "y": landmark.y,
                        "z": landmark.z,
                        "visibility": landmark.visibility
                    })
                return {
                    "landmarks": landmarks,
                    "confidence": results.pose_landmarks
                }
            return None
        except Exception as e:
            logger.error(f"Error in pose estimation: {str(e)}")
            return None
    
    def is_lying_down(self, landmarks: List[Dict]) -> bool:
        """Detect if person is lying down (crawling)
        
        Args:
            landmarks: List of pose landmarks
            
        Returns:
            True if person appears to be lying down
        """
        if not landmarks or len(landmarks) < 17:
            return False
        
        # Check vertical distance between head and feet
        head_y = landmarks[0]["y"]  # Nose
        left_ankle_y = landmarks[15]["y"]
        right_ankle_y = landmarks[16]["y"]
        
        vertical_distance = abs(head_y - max(left_ankle_y, right_ankle_y))
        
        # If vertical distance is small, person is likely lying down
        return vertical_distance < 0.3
    
    def is_climbing(self, landmarks: List[Dict]) -> bool:
        """Detect if person appears to be climbing
        
        Args:
            landmarks: List of pose landmarks
            
        Returns:
            True if pose suggests climbing
        """
        if not landmarks or len(landmarks) < 17:
            return False
        
        # Check if arms are raised and legs are positioned for climbing
        left_shoulder_y = landmarks[11]["y"]
        right_shoulder_y = landmarks[12]["y"]
        left_elbow_y = landmarks[13]["y"]
        right_elbow_y = landmarks[14]["y"]
        
        # If elbows are significantly higher than shoulders, arms are raised
        arms_raised = (left_elbow_y < left_shoulder_y - 0.1 and 
                       right_elbow_y < right_shoulder_y - 0.1)
        
        return arms_raised
