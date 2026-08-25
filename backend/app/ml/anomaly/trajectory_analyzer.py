"""Trajectory analysis for anomaly detection"""
import logging
from typing import List, Dict, Tuple
import numpy as np
from collections import defaultdict, deque
from app.config import settings

logger = logging.getLogger(__name__)


class TrajectoryAnalyzer:
    """Analyzes object trajectories to detect anomalies"""
    
    def __init__(self, max_history: int = 30):
        self.trajectories: Dict[int, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.max_history = max_history
    
    def update_trajectory(self, track_id: int, center: Tuple[float, float]):
        """Update trajectory for tracked object
        
        Args:
            track_id: Unique track identifier
            center: (x, y) center coordinate
        """
        self.trajectories[track_id].append(center)
    
    def get_trajectory(self, track_id: int) -> List[Tuple[float, float]]:
        """Get trajectory history for object
        
        Args:
            track_id: Unique track identifier
            
        Returns:
            List of (x, y) coordinates
        """
        return list(self.trajectories.get(track_id, []))
    
    def detect_fence_approach(self, track_id: int, fence_line_y: int) -> bool:
        """Detect if object is approaching fence line
        
        Args:
            track_id: Unique track identifier
            fence_line_y: Y-coordinate of fence line
            
        Returns:
            True if object is moving toward fence
        """
        trajectory = self.get_trajectory(track_id)
        if len(trajectory) < 5:
            return False
        
        # Check if object is moving toward fence
        recent_y = [point[1] for point in trajectory[-5:]]
        if abs(recent_y[-1] - fence_line_y) < abs(recent_y[0] - fence_line_y):
            return True
        return False
    
    def detect_loitering(self, track_id: int, threshold: float = 50.0) -> bool:
        """Detect if object is loitering in place
        
        Args:
            track_id: Unique track identifier
            threshold: Max distance for loitering detection
            
        Returns:
            True if object is loitering
        """
        trajectory = self.get_trajectory(track_id)
        if len(trajectory) < 10:
            return False
        
        # Calculate distance between first and last point
        first_point = np.array(trajectory[0])
        last_point = np.array(trajectory[-1])
        distance = np.linalg.norm(last_point - first_point)
        
        return distance < threshold
    
    def detect_zigzag_pattern(self, track_id: int) -> bool:
        """Detect suspicious zigzag movement pattern
        
        Args:
            track_id: Unique track identifier
            
        Returns:
            True if object shows zigzag pattern
        """
        trajectory = self.get_trajectory(track_id)
        if len(trajectory) < 10:
            return False
        
        # Calculate direction changes
        direction_changes = 0
        for i in range(1, len(trajectory) - 1):
            vec1 = np.array(trajectory[i]) - np.array(trajectory[i-1])
            vec2 = np.array(trajectory[i+1]) - np.array(trajectory[i])
            
            # Calculate angle between vectors
            cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2) + 1e-6)
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            
            if angle > np.pi / 3:  # 60 degree change
                direction_changes += 1
        
        return direction_changes > len(trajectory) / 3  # More than 1/3 of points show direction change
