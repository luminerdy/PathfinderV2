"""
Mecanum Chassis Control
Provides omnidirectional movement control for mecanum drive platforms
"""

import sys
import math
import logging
from typing import Tuple

from lib.mecanum_kinematics import MecanumKinematics as BaseMecanum

from .board import Board

logger = logging.getLogger(__name__)


class Chassis:
    """
    Mecanum chassis controller for omnidirectional movement
    
    Coordinate system:
        0° = forward (Y+)
        90° = right (X+)
        180° = backward (Y-)
        270° = left (X-)
    """
    
    def __init__(self, board: Board, wheel_base: float = 67, track_width: float = 59, 
                 wheel_diameter: float = 65):
        """
        Initialize chassis controller
        
        Args:
            board: Board instance for motor control
            wheel_base: Distance between front and rear wheels (mm)
            track_width: Distance between left and right wheels (mm)
            wheel_diameter: Wheel diameter (mm)
        """
        self.board = board
        self._kinematics = BaseMecanum(wheelbase_mm=wheel_base, track_width_mm=track_width, 
                                        wheel_diameter_mm=wheel_diameter)
        
        self._max_speed = 100  # mm/s
        self._current_velocity = 0
        self._current_direction = 0
        self._current_rotation = 0
        
        logger.info("Chassis initialized")
        
    # ===== Basic Movement =====
    
    def set_velocity(self, velocity: float, direction: float = 0, rotation: float = 0):
        """
        Set chassis velocity using polar coordinates
        
        Args:
            velocity: Speed in mm/s (0-100) OR motor duty (-100 to 100)
            direction: Direction in degrees (0=forward, 90=right, 180=back, 270=left)
            rotation: Rotation rate (-1.0 to 1.0, positive = counter-clockwise)
        """
        # Convert polar to cartesian
        vx = velocity * math.cos(math.radians(direction))  # Forward component
        vy = velocity * math.sin(math.radians(direction))  # Strafe component
        omega = rotation * 50  # Scale rotation to motor range
        
        # Get wheel speeds from kinematics
        v1, v2, v3, v4 = self._kinematics.inverse_kinematics(vx, vy, omega)
        
        # Send to motors (convert to duty cycle)
        self.board.set_motor_duty(1, int(v1))  # Front left
        self.board.set_motor_duty(2, int(v2))  # Front right
        self.board.set_motor_duty(3, int(v3))  # Rear left
        self.board.set_motor_duty(4, int(v4))  # Rear right
        
        self._current_velocity = velocity
        self._current_direction = direction
        self._current_rotation = rotation
        
    def stop(self):
        """Stop all movement"""
        self.board.set_motor_duty(1, 0)
        self.board.set_motor_duty(2, 0)
        self.board.set_motor_duty(3, 0)
        self.board.set_motor_duty(4, 0)
        self._current_velocity = 0
        self._current_direction = 0
        self._current_rotation = 0
        
    # ===== Directional Movement =====
    
    def forward(self, speed: float = 50):
        """Move forward"""
        self.set_velocity(speed, 0)
        
    def backward(self, speed: float = 50):
        """Move backward"""
        self.set_velocity(speed, 180)
        
    def strafe_right(self, speed: float = 50):
        """Strafe right"""
        self.set_velocity(speed, 90)
        
    def strafe_left(self, speed: float = 50):
        """Strafe left"""
        self.set_velocity(speed, 270)
        
    def rotate_clockwise(self, rate: float = 0.5):
        """Rotate clockwise in place"""
        self.set_velocity(0, 0, rate)
        
    def rotate_counterclockwise(self, rate: float = 0.5):
        """Rotate counterclockwise in place"""
        self.set_velocity(0, 0, -rate)
        
    # ===== Diagonal Movement =====
    
    def forward_right(self, speed: float = 50):
        """Move forward-right diagonal"""
        self.set_velocity(speed, 45)
        
    def forward_left(self, speed: float = 50):
        """Move forward-left diagonal"""
        self.set_velocity(speed, 315)
        
    def backward_right(self, speed: float = 50):
        """Move backward-right diagonal"""
        self.set_velocity(speed, 135)
        
    def backward_left(self, speed: float = 50):
        """Move backward-left diagonal"""
        self.set_velocity(speed, 225)
        
    # ===== Cartesian Movement =====
    
    def set_cartesian(self, vx: float, vy: float, rotation: float = 0):
        """
        Set velocity using Cartesian coordinates
        
        Args:
            vx: Velocity in X direction (mm/s, positive = right)
            vy: Velocity in Y direction (mm/s, positive = forward)
            rotation: Rotation rate (-1.0 to 1.0)
        """
        # Convert cartesian to polar
        velocity = math.sqrt(vx*vx + vy*vy)
        direction = math.degrees(math.atan2(vy, vx))
        self.set_velocity(velocity, direction, rotation)
        
    # ===== Advanced Movement =====
    
    def arc_move(self, speed: float, radius: float, angle: float):
        """
        Move in an arc
        
        Args:
            speed: Linear speed (mm/s)
            radius: Arc radius (mm)
            angle: Arc angle in degrees (positive = clockwise)
        """
        # Calculate rotation rate based on radius
        # ω = v / r
        if radius == 0:
            self.rotate_clockwise(1.0 if angle > 0 else -1.0)
            return
            
        angular_velocity = speed / radius
        rotation = angular_velocity * (1 if angle > 0 else -1)
        rotation = max(-1.0, min(1.0, rotation))
        
        # Direction perpendicular to rotation
        direction = 90 if angle > 0 else 270
        
        self.set_velocity(speed, direction, rotation)
        
    # ===== State Queries =====
    
    @property
    def velocity(self) -> float:
        """Current velocity (mm/s)"""
        return self._current_velocity
        
    @property
    def direction(self) -> float:
        """Current direction (degrees)"""
        return self._current_direction
        
    @property
    def rotation(self) -> float:
        """Current rotation rate"""
        return self._current_rotation
        
    @property
    def is_moving(self) -> bool:
        """Check if chassis is moving"""
        return self._current_velocity > 0 or abs(self._current_rotation) > 0.01
        
    @property
    def max_speed(self) -> float:
        """Maximum speed (mm/s)"""
        return self._max_speed
        
    @max_speed.setter
    def max_speed(self, speed: float):
        """Set maximum speed"""
        self._max_speed = max(0, min(100, speed))
