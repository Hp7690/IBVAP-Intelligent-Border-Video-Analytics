"""Inference engine for real-time video analysis"""
import asyncio
import logging
import numpy as np
import cv2
from typing import List, Dict, Optional
from datetime import datetime
from app.config import settings
from app.ml.detection.human_detector import HumanDetector
from app.ml.detection.vehicle_detector import VehicleDetector
from app.ml.detection.face_detector import FaceDetector
from app.ml.detection.weapon_detector import WeaponDetector
from app.ml.detection.plate_detector import PlateDetector
from app.ml.anomaly.trajectory_analyzer import TrajectoryAnalyzer
from app.ml.pose.pose_estimator import PoseEstimator
from app.ml.night_mode import NightModeDetector

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Central inference engine for running all detections"""
    
    def __init__(self):
        logger.info("Initializing inference engine...")
        
        # Initialize detectors
        try:
            self.human_detector = HumanDetector()
            self.vehicle_detector = VehicleDetector()
            self.face_detector = FaceDetector()
            self.weapon_detector = WeaponDetector()
            self.plate_detector = PlateDetector()
        except Exception as e:
            logger.warning(f"Some detectors failed to initialize: {str(e)}")
        
        # Initialize analysis modules
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.pose_estimator = PoseEstimator()
        self.night_mode_detector = NightModeDetector()
        
        logger.info("Inference engine initialized")
    
    async def analyze_frame(
        self,
        camera_id: str,
        frame: np.ndarray
    ) -> Dict:
        """Analyze single frame for all detections
        
        Args:
            camera_id: Camera identifier
            frame: Input frame (BGR format)
            
        Returns:
            Analysis results with detections and alerts
        """
        timestamp = datetime.utcnow()
        results = {
            "camera_id": camera_id,
            "timestamp": timestamp,
            "detections": [],
            "alerts": [],
            "is_night_mode": False
        }
        
        try:
            # Check for night mode
            is_night = self.night_mode_detector.is_night_time(frame)
            results["is_night_mode"] = is_night
            
            if is_night:
                # Motion-triggered detection
                motion_detected, fg_mask = self.night_mode_detector.detect_motion(frame)
                if motion_detected:
                    # Enhance frame and run detection
                    enhanced_frame = self.night_mode_detector.enhance_low_light(frame)
                    detections = await self._run_detections(enhanced_frame, camera_id)
                else:
                    detections = []
            else:
                # Normal detection in daylight
                detections = await self._run_detections(frame, camera_id)
            
            results["detections"] = detections
            
            # Generate alerts from detections
            alerts = await self._generate_alerts(camera_id, detections, frame)
            results["alerts"] = alerts
            
        except Exception as e:
            logger.error(f"Error analyzing frame from {camera_id}: {str(e)}")
        
        return results
    
    async def _run_detections(
        self,
        frame: np.ndarray,
        camera_id: str
    ) -> List[Dict]:
        """Run all detection models on frame
        
        Args:
            frame: Input frame
            camera_id: Camera identifier
            
        Returns:
            List of detections
        """
        detections = []
        
        try:
            # Run detectors
            human_detections = self.human_detector.detect(frame)
            vehicle_detections = self.vehicle_detector.detect(frame)
            face_detections = self.face_detector.detect(frame)
            weapon_detections = self.weapon_detector.detect(frame)
            plate_detections = self.plate_detector.detect_plates(frame)
            
            # Combine detections
            detections.extend(human_detections)
            detections.extend(vehicle_detections)
            detections.extend(face_detections)
            detections.extend(weapon_detections)
            detections.extend(plate_detections)
            
        except Exception as e:
            logger.error(f"Error running detections: {str(e)}")
        
        return detections
    
    async def _generate_alerts(
        self,
        camera_id: str,
        detections: List[Dict],
        frame: np.ndarray
    ) -> List[Dict]:
        """Generate alerts based on detections
        
        Args:
            camera_id: Camera identifier
            detections: List of detections
            frame: Frame for snapshot
            
        Returns:
            List of alerts
        """
        alerts = []
        
        try:
            for detection in detections:
                det_class = detection.get("class")
                confidence = detection.get("confidence", 0)
                
                # Generate alert for each detection type
                if det_class == "person":
                    if confidence > settings.HUMAN_DETECTION_THRESHOLD:
                        alert = {
                            "alert_type": "human_detection",
                            "severity": "low",
                            "message": f"Human detected (confidence: {confidence:.2f})",
                            "confidence": confidence,
                            "metadata": detection
                        }
                        alerts.append(alert)
                
                elif det_class in ["car", "truck", "bus", "motorcycle", "bicycle"]:
                    if confidence > settings.VEHICLE_DETECTION_THRESHOLD:
                        alert = {
                            "alert_type": "vehicle_detection",
                            "severity": "low",
                            "message": f"Vehicle detected: {det_class} (confidence: {confidence:.2f})",
                            "confidence": confidence,
                            "metadata": detection
                        }
                        alerts.append(alert)
                
                elif det_class == "face":
                    if confidence > settings.FACE_DETECTION_THRESHOLD:
                        alert = {
                            "alert_type": "face_detected",
                            "severity": "medium",
                            "message": f"Unregistered face detected (confidence: {confidence:.2f})",
                            "confidence": confidence,
                            "metadata": detection
                        }
                        alerts.append(alert)
                
                elif det_class == "license_plate":
                    if confidence > settings.PLATE_DETECTION_THRESHOLD:
                        alert = {
                            "alert_type": "plate_detected",
                            "severity": "low",
                            "message": f"License plate detected (confidence: {confidence:.2f})",
                            "confidence": confidence,
                            "metadata": detection
                        }
                        alerts.append(alert)
                
                elif det_class in ["gun", "rifle", "pistol", "weapon"]:
                    if confidence > settings.WEAPON_DETECTION_THRESHOLD:
                        alert = {
                            "alert_type": "weapon_detected",
                            "severity": "critical",
                            "message": f"WEAPON DETECTED: {det_class} (confidence: {confidence:.2f})",
                            "confidence": confidence,
                            "metadata": detection
                        }
                        alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error generating alerts: {str(e)}")
        
        return alerts
