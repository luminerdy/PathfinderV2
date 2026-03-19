"""
Movement Controller
High-level movement behaviors and navigation
"""

import time
import logging
import math
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class MovementController:
    """
    High-level movement control and navigation
    """
    
    def __init__(self, chassis, sonar=None):
        """
        Initialize movement controller
        
        Args:
            chassis: Chassis instance
            sonar: Optional Sonar instance for obstacle avoidance
        """
        self.chassis = chassis
        self.sonar = sonar
        
        # Safety settings
        self.obstacle_threshold = 15  # cm
        self.enable_obstacle_avoidance = True
        
        logger.info("Movement controller initialized")
        
    # ===== Timed Movement =====
    
    def move_forward(self, speed: float = 50, duration: float = 1.0,
                    check_obstacles: bool = True) -> bool:
        """
        Move forward for duration
        
        Args:
            speed: Speed (mm/s)
            duration: Duration in seconds
            check_obstacles: Enable obstacle checking
            
        Returns:
            True if completed, False if stopped early
        """
        if check_obstacles and not self._check_forward_clear():
            logger.warning("Obstacle detected, movement aborted")
            return False
            
        self.chassis.forward(speed)
        
        # Monitor during movement
        elapsed = 0
        dt = 0.1
        while elapsed < duration:
            if check_obstacles and not self._check_forward_clear():
                self.chassis.stop()
                logger.warning("Obstacle detected during movement")
                return False
            time.sleep(dt)
            elapsed += dt
            
        self.chassis.stop()
        return True
        
    def move_backward(self, speed: float = 50, duration: float = 1.0) -> bool:
        """Move backward for duration"""
        self.chassis.backward(speed)
        time.sleep(duration)
        self.chassis.stop()
        return True
        
    def strafe_right(self, speed: float = 50, duration: float = 1.0) -> bool:
        """Strafe right for duration"""
        self.chassis.strafe_right(speed)
        time.sleep(duration)
        self.chassis.stop()
        return True
        
    def strafe_left(self, speed: float = 50, duration: float = 1.0) -> bool:
        """Strafe left for duration"""
        self.chassis.strafe_left(speed)
        time.sleep(duration)
        self.chassis.stop()
        return True
        
    def rotate(self, angle: float, speed: float = 0.5) -> bool:
        """
        Rotate by angle (degrees)
        
        Args:
            angle: Rotation angle (positive = clockwise)
            speed: Rotation speed (0-1)
            
        Returns:
            True when complete
        """
        # Estimate duration (rough)
        duration = abs(angle) / 90.0
        
        if angle > 0:
            self.chassis.rotate_clockwise(speed)
        else:
            self.chassis.rotate_counterclockwise(speed)
            
        time.sleep(duration)
        self.chassis.stop()
        return True
        
    # ===== Pattern Movement =====
    
    def square(self, side_length: float = 1.0, speed: float = 50):
        """
        Move in a square pattern
        
        Args:
            side_length: Side length in seconds
            speed: Movement speed
        """
        for _ in range(4):
            self.move_forward(speed, side_length)
            time.sleep(0.3)
            self.rotate(90, 0.5)
            time.sleep(0.3)
            
    def circle(self, duration: float = 5.0, speed: float = 50, 
              clockwise: bool = True):
        """
        Move in a circle
        
        Args:
            duration: Circle duration
            speed: Movement speed
            clockwise: Direction
        """
        rotation = 0.5 if clockwise else -0.5
        self.chassis.set_velocity(speed, 90 if clockwise else 270, rotation)
        time.sleep(duration)
        self.chassis.stop()
        
    def figure_eight(self, duration: float = 10.0, speed: float = 50):
        """Move in figure-8 pattern"""
        half = duration / 2
        self.circle(half, speed, clockwise=True)
        time.sleep(0.5)
        self.circle(half, speed, clockwise=False)
        
    # ===== Obstacle Avoidance =====
    
    def explore(self, duration: float = 30.0, speed: float = 40):
        """
        Autonomous exploration with obstacle avoidance
        
        Args:
            duration: Exploration duration
            speed: Movement speed
        """
        start = time.time()
        
        while time.time() - start < duration:
            if self._check_forward_clear():
                # Move forward
                self.chassis.forward(speed)
                time.sleep(0.5)
            else:
                # Obstacle - turn random direction
                self.chassis.stop()
                time.sleep(0.2)
                
                # Back up
                self.move_backward(speed, 0.5)
                time.sleep(0.2)
                
                # Turn (alternate left/right)
                import random
                angle = random.choice([70, 90, 110])
                self.rotate(angle if random.random() > 0.5 else -angle)
                time.sleep(0.3)
                
        self.chassis.stop()
        
    def wall_follow(self, duration: float = 20.0, speed: float = 40, 
                   side: str = 'left'):
        """
        Follow wall on left or right side
        
        Args:
            duration: Following duration
            speed: Movement speed
            side: 'left' or 'right'
        """
        start = time.time()
        target_distance = 20  # cm from wall
        
        while time.time() - start < duration:
            dist = self.sonar.get_distance() if self.sonar else None
            
            if dist is None:
                self.chassis.forward(speed)
            elif dist < target_distance - 5:
                # Too close, turn away
                if side == 'left':
                    self.chassis.set_velocity(speed, 45, 0)  # Forward-right
                else:
                    self.chassis.set_velocity(speed, 315, 0)  # Forward-left
            elif dist > target_distance + 5:
                # Too far, turn toward wall
                if side == 'left':
                    self.chassis.set_velocity(speed, 315, 0)  # Forward-left
                else:
                    self.chassis.set_velocity(speed, 45, 0)  # Forward-right
            else:
                # Good distance, go straight
                self.chassis.forward(speed)
                
            time.sleep(0.1)
            
        self.chassis.stop()
        
    # ===== Visual Tracking =====
    
    def track_target(self, get_target_pos: Callable, duration: float = 10.0, 
                    speed: float = 50):
        """
        Track visual target
        
        Args:
            get_target_pos: Function that returns (x, y) or None
            duration: Tracking duration
            speed: Movement speed
        """
        start = time.time()
        frame_center_x = 320  # Assume 640x480
        
        while time.time() - start < duration:
            target = get_target_pos()
            
            if target is None:
                # Lost target, stop and search
                self.chassis.stop()
                time.sleep(0.5)
                self.rotate(30)  # Small search rotation
                continue
                
            x, y = target
            
            # Calculate error from center
            error = x - frame_center_x
            
            if abs(error) < 50:
                # Centered, move forward
                self.chassis.forward(speed)
            else:
                # Turn toward target
                rotation = -error / frame_center_x * 0.5
                self.chassis.set_velocity(speed * 0.7, 0, rotation)
                
            time.sleep(0.1)
            
        self.chassis.stop()
        
    # ===== Helper Methods =====
    
    def _check_forward_clear(self) -> bool:
        """Check if forward path is clear"""
        if not self.enable_obstacle_avoidance or self.sonar is None:
            return True
            
        dist = self.sonar.get_distance()
        return dist is None or dist > self.obstacle_threshold
        
    def emergency_stop(self):
        """Immediate stop"""
        self.chassis.stop()
        logger.warning("Emergency stop triggered")
