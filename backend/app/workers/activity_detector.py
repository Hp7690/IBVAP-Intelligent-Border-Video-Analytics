"""Activity detector for suspicious behavior detection"""
import logging
import numpy as np
from typing import Dict, List, Optional
from app.ml.anomaly.trajectory_analyzer import TrajectoryAnalyzer
from app.ml.pose.pose_estimator import PoseEstimator

logger = logging.getLogger(__name__)


class ActivityDetector:
    """Detects suspicious activities based on pose and trajectory"""
    
    def __init__(self):
        self.trajectory_analyzer = TrajectoryAnalyzer()
        self.pose_estimator = PoseEstimator()
    
    async def detect_suspicious_activity(
        self,
        frame: np.ndarray,
        detections: List[Dict],
        zones: List[Dict] = None
    ) -> List[Dict]:
        """Detect suspicious activities
        
        Args:
            frame: Input frame
            detections: List of person detections
            zones: List of restricted/intrusion zones
            
        Returns:
            List of suspicious activity alerts
        """
        alerts = []
        
        try:
            for detection in detections:
                if detection.get("class") == "person":
                    track_id = detection.get("track_id")
                    bbox = detection.get("bbox")
                    
                    if bbox:
                        # Get center point
                        x1, y1, x2, y2 = bbox
                        center = ((x1 + x2) / 2, (y1 + y2) / 2)
                        
                        # Update trajectory
                        if track_id:
                            self.trajectory_analyzer.update_trajectory(track_id, center)
                            
                            # Check for suspicious patterns
                            if self.trajectory_analyzer.detect_loitering(track_id):
                                alerts.append({
                                    "alert_type": "loitering",
                                    "severity": "medium",
                                    "message": f"Person loitering detected (Track ID: {track_id})",
                                    "track_id": track_id
                                })
                            
                            if self.trajectory_analyzer.detect_zigzag_pattern(track_id):
                                alerts.append({
                                    "alert_type": "suspicious_movement",
                                    "severity": "high",
                                    "message": f"Suspicious zigzag pattern detected (Track ID: {track_id})",
                                    "track_id": track_id
                                })
                        
                        # Estimate pose for behavior analysis
                        pose_result = self.pose_estimator.estimate(frame)
                        if pose_result:
                            landmarks = pose_result.get("landmarks")
                            
                            if self.pose_estimator.is_lying_down(landmarks):
                                alerts.append({
                                    "alert_type": "crawling",
                                    "severity": "high",
                                    "message": "Person crawling detected",
                                    "track_id": track_id
                                })
                            
                            if self.pose_estimator.is_climbing(landmarks):
                                alerts.append({
                                    "alert_type": "climbing",
                                    "severity": "high",
                                    "message": "Person climbing detected",
                                    "track_id": track_id
                                })
                    
                    # Check zone violations
                    if zones:
                        zone_alerts = self._check_zone_violations(detection, zones)
                        alerts.extend(zone_alerts)
        
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {str(e)}")
        
        return alerts
    
    def _check_zone_violations(
        self,
        detection: Dict,
        zones: List[Dict]
    ) -> List[Dict]:
        """Check if detection violates any zone restrictions
        
        Args:
            detection: Detection result
            zones: List of zones
            
        Returns:
            Zone violation alerts
        """
        alerts = []
        
        try:
            bbox = detection.get("bbox")
            if not bbox:
                return alerts
            
            x1, y1, x2, y2 = bbox
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            for zone in zones:
                if not zone.get("enabled"):
                    continue
                
                zone_type = zone.get("zone_type")
                coordinates = zone.get("coordinates")
                
                # Check if point is inside polygon
                if self._point_in_polygon(center_x, center_y, coordinates):
                    if zone_type == "intrusion":
                        alerts.append({
                            "alert_type": "intrusion",
                            "severity": "high",
                            "message": f"Intrusion detected in zone: {zone.get('name')}",
                            "zone_id": zone.get("id")
                        })
                    elif zone_type == "restricted":
                        alerts.append({
                            "alert_type": "restricted_zone_violation",
                            "severity": "high",
                            "message": f"Restricted zone violation: {zone.get('name')}",
                            "zone_id": zone.get("id")
                        })
        
        except Exception as e:
            logger.error(f"Error checking zone violations: {str(e)}")
        
        return alerts
    
    @staticmethod
    def _point_in_polygon(x: float, y: float, polygon: List) -> bool:
        """Check if point is inside polygon using ray casting
        
        Args:
            x: X coordinate
            y: Y coordinate
            polygon: List of [x, y] coordinates
            
        Returns:
            True if point is inside polygon
        """
        if not polygon or len(polygon) < 3:
            return False
        
        inside = False
        p1x, p1y = polygon[0]
        
        for i in range(1, len(polygon)):
            p2x, p2y = polygon[i]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
