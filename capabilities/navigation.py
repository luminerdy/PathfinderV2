"""
Navigation Capability
AprilTag-based navigation and localization
"""

import time
import math
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NavigationResult:
    """Result of navigation attempt"""
    success: bool
    final_distance: Optional[float]
    time_taken: float
    reason: str
    path_log: List[dict]


class Navigator:
    """
    AprilTag-based navigation controller
    
    Uses visual servoing to navigate to AprilTag markers.
    No encoders needed - pure vision-based navigation.
    """
    
    def __init__(self, robot):
        """
        Initialize navigator
        
        Args:
            robot: PathfinderRobot instance with camera, chassis, vision
        """
        self.robot = robot
        self.camera = robot.camera
        self.chassis = robot.chassis
        self.vision = robot.vision
        
        # Navigation parameters (tunable)
        self.rotation_speed = 0.2  # Rotation speed for search
        self.approach_speed = 30    # Forward speed when approaching
        self.slow_distance = 500    # Slow down when closer than this (mm)
        self.slow_speed = 20        # Reduced speed when close (min 20)
        self.center_tolerance = 50  # Pixels from center considered "centered"
        self.max_attempts = 100     # Max control loop iterations
        
        # Speed limits (dead zone below ~20)
        self.min_speed = 20         # Motors don't move below this
        self.max_speed = 80         # Safe maximum
        
    def go_to_tag(self, tag_id: int, stop_distance: float = 300, 
                  timeout: float = 30.0) -> NavigationResult:
        """
        Navigate to AprilTag marker
        
        Uses visual servoing:
        1. Rotate to find tag
        2. Center tag in view (rotate)
        3. Approach until desired distance
        
        Args:
            tag_id: Target AprilTag ID
            stop_distance: Stop when this close (mm)
            timeout: Maximum time to spend (seconds)
        
        Returns:
            NavigationResult with success status and details
        """
        logger.info(f"Navigating to tag {tag_id}, target distance {stop_distance}mm")
        
        start_time = time.time()
        path_log = []
        
        # Search for tag
        tag = self._find_tag(tag_id, timeout=10.0)
        if not tag:
            return NavigationResult(
                success=False,
                final_distance=None,
                time_taken=time.time() - start_time,
                reason=f"Tag {tag_id} not found during search",
                path_log=path_log
            )
        
        # Visual servoing loop
        for attempt in range(self.max_attempts):
            # Check timeout
            if time.time() - start_time > timeout:
                return NavigationResult(
                    success=False,
                    final_distance=tag.distance_estimate if tag else None,
                    time_taken=time.time() - start_time,
                    reason="Timeout exceeded",
                    path_log=path_log
                )
            
            # Detect tag
            tags = self.vision.detect_apriltags()
            tag = self._find_tag_in_list(tags, tag_id)
            
            if not tag:
                # Lost tag - search
                logger.warning(f"Lost tag {tag_id}, searching...")
                self.chassis.set_velocity(0, 0, self.rotation_speed)
                time.sleep(0.5)
                self.chassis.stop()
                continue
            
            # Log current state
            path_log.append({
                'time': time.time() - start_time,
                'distance': tag.distance_estimate,
                'center_x': tag.center[0],
                'center_y': tag.center[1]
            })
            
            # Check if arrived
            if tag.distance_estimate < stop_distance:
                self.chassis.stop()
                logger.info(f"Arrived at tag {tag_id}! Distance: {tag.distance_estimate:.0f}mm")
                return NavigationResult(
                    success=True,
                    final_distance=tag.distance_estimate,
                    time_taken=time.time() - start_time,
                    reason="Success",
                    path_log=path_log
                )
            
            # Visual servoing control
            frame_center_x = self.camera.width // 2
            offset_x = tag.center[0] - frame_center_x
            
            # Centering (rotation)
            if abs(offset_x) > self.center_tolerance:
                # Turn to center tag
                turn_speed = -offset_x / 500.0  # Proportional control
                turn_speed = max(-0.5, min(0.5, turn_speed))  # Clamp
                self.chassis.set_velocity(0, 0, turn_speed)
                time.sleep(0.2)
                
            else:
                # Tag centered, approach
                # Use slow speed when close, but ensure above minimum
                if tag.distance_estimate < self.slow_distance:
                    speed = max(self.min_speed, self.slow_speed)
                else:
                    speed = self.approach_speed
                speed = min(speed, self.max_speed)  # Enforce maximum
                self.chassis.set_velocity(speed, 0, 0)
                time.sleep(0.2)
            
            self.chassis.stop()
            time.sleep(0.1)  # Small pause between iterations
        
        # Max attempts reached
        self.chassis.stop()
        return NavigationResult(
            success=False,
            final_distance=tag.distance_estimate if tag else None,
            time_taken=time.time() - start_time,
            reason="Max attempts reached",
            path_log=path_log
        )
    
    def _find_tag(self, tag_id: int, timeout: float = 10.0) -> Optional[object]:
        """
        Search for tag by rotating
        
        Args:
            tag_id: Tag to find
            timeout: Max search time
        
        Returns:
            Tag detection or None
        """
        start_time = time.time()
        
        logger.info(f"Searching for tag {tag_id}...")
        
        # Try current view first
        tags = self.vision.detect_apriltags()
        tag = self._find_tag_in_list(tags, tag_id)
        if tag:
            logger.info(f"Tag {tag_id} visible immediately")
            return tag
        
        # Rotate and search
        total_rotation = 0
        while time.time() - start_time < timeout:
            # Rotate increment
            self.chassis.set_velocity(0, 0, self.rotation_speed)
            time.sleep(0.5)
            self.chassis.stop()
            
            total_rotation += 0.5 * self.rotation_speed
            
            # Check again
            tags = self.vision.detect_apriltags()
            tag = self._find_tag_in_list(tags, tag_id)
            if tag:
                logger.info(f"Tag {tag_id} found after {total_rotation:.1f}s rotation")
                return tag
            
            time.sleep(0.1)
        
        logger.warning(f"Tag {tag_id} not found after {timeout}s search")
        return None
    
    def _find_tag_in_list(self, tags: List, tag_id: int) -> Optional[object]:
        """Find specific tag in detection list"""
        for tag in tags:
            if tag.id == tag_id:
                return tag
        return None
    
    def navigate_path(self, tag_sequence: List[int], stop_distance: float = 300) -> dict:
        """
        Navigate through sequence of tags
        
        Args:
            tag_sequence: List of tag IDs to visit in order
            stop_distance: Distance to stop at each tag (mm)
        
        Returns:
            Dict with results for each waypoint
        """
        logger.info(f"Navigating path: {' → '.join(map(str, tag_sequence))}")
        
        results = {
            'waypoints': [],
            'total_time': 0,
            'total_distance': 0,
            'success': True
        }
        
        start_time = time.time()
        
        for i, tag_id in enumerate(tag_sequence):
            logger.info(f"Waypoint {i+1}/{len(tag_sequence)}: Tag {tag_id}")
            
            result = self.go_to_tag(tag_id, stop_distance)
            results['waypoints'].append({
                'tag_id': tag_id,
                'success': result.success,
                'distance': result.final_distance,
                'time': result.time_taken,
                'reason': result.reason
            })
            
            if not result.success:
                logger.error(f"Failed at waypoint {i+1}: {result.reason}")
                results['success'] = False
                break
            
            # Brief pause at waypoint
            time.sleep(1.0)
        
        results['total_time'] = time.time() - start_time
        
        return results
    
    def estimate_position(self) -> Optional[Tuple[float, float, float]]:
        """
        Estimate robot position using visible AprilTags
        
        Returns:
            (x, y, heading) in field coordinates or None
            
        Note: Requires field configuration with known tag positions
        """
        # TODO: Implement triangulation from multiple tags
        # For now, just return None
        logger.warning("Position estimation not yet implemented")
        return None
