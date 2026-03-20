"""
Mecanum Wheel Kinematics
Clean-room implementation based on standard mecanum drive mathematics.

Mecanum wheel configuration:
    Front
  1 ↗  ↖ 2
  3 ↖  ↗ 4
    Rear

Motor numbering: 1=FL, 2=FR, 3=RL, 4=RR
Wheel angles: 45° to chassis axes
"""

import math
from typing import Tuple


class MecanumKinematics:
    """
    Mecanum drive inverse kinematics
    
    Converts desired motion (velocity, direction, rotation) to wheel speeds.
    Based on standard mecanum mathematics, not vendor-specific.
    """
    
    def __init__(self, wheelbase_mm: float = 67, track_width_mm: float = 59, 
                 wheel_diameter_mm: float = 65):
        """
        Initialize mecanum kinematics
        
        Args:
            wheelbase_mm: Distance between front and rear wheels (mm)
            track_width_mm: Distance between left and right wheels (mm)  
            wheel_diameter_mm: Wheel diameter (mm)
        """
        self.wheelbase = wheelbase_mm
        self.track = track_width_mm
        self.wheel_diameter = wheel_diameter_mm
        
        # Robot geometry factor (for rotation)
        # L = (wheelbase + track_width) / 2
        self.L = (wheelbase_mm + track_width_mm) / 2
        
    def inverse_kinematics(self, vx: float, vy: float, omega: float) -> Tuple[float, float, float, float]:
        """
        Convert desired robot motion to wheel velocities
        
        Mecanum wheel equations:
        v1 = vy + vx - omega * L  (Front Left)
        v2 = vy - vx + omega * L  (Front Right)
        v3 = vy - vx - omega * L  (Rear Left)
        v4 = vy + vx + omega * L  (Rear Right)
        
        Args:
            vx: Velocity in X direction (mm/s, positive = right)
            vy: Velocity in Y direction (mm/s, positive = forward)
            omega: Angular velocity (rad/s, positive = clockwise)
            
        Returns:
            (v1, v2, v3, v4) - Wheel velocities in mm/s
        """
        # Calculate wheel velocities
        v1 = vy + vx - omega * self.L  # Front Left
        v2 = vy - vx + omega * self.L  # Front Right  
        v3 = vy - vx - omega * self.L  # Rear Left
        v4 = vy + vx + omega * self.L  # Rear Right
        
        return (v1, v2, v3, v4)
        
    def polar_to_cartesian(self, velocity: float, direction_deg: float) -> Tuple[float, float]:
        """
        Convert polar coordinates to Cartesian
        
        Args:
            velocity: Speed in mm/s
            direction_deg: Direction in degrees (0 = forward, 90 = right)
            
        Returns:
            (vx, vy) in mm/s
        """
        direction_rad = math.radians(direction_deg)
        vx = velocity * math.cos(direction_rad)
        vy = velocity * math.sin(direction_rad)
        return (vx, vy)
        
    def set_velocity(self, velocity: float, direction_deg: float, 
                    rotation_rate: float) -> Tuple[int, int, int, int]:
        """
        High-level control: Set robot velocity in polar coordinates
        
        Args:
            velocity: Speed in mm/s (0-100 typical)
            direction_deg: Direction (0=forward, 90=right, 180=back, 270=left)
            rotation_rate: Rotation speed (-1.0 to 1.0, positive = clockwise)
            
        Returns:
            (duty1, duty2, duty3, duty4) - Motor duty cycles as integers
        """
        # Convert polar to Cartesian
        vx, vy = self.polar_to_cartesian(velocity, direction_deg)
        
        # Convert rotation rate to angular velocity
        # Normalize rotation_rate to rad/s
        omega = -rotation_rate * self.L  # Negative for proper direction
        
        # Calculate wheel velocities
        v1, v2, v3, v4 = self.inverse_kinematics(vx, vy, omega)
        
        # Convert to integer duty cycles (with inversion for motor orientation)
        # FL and RL motors reversed due to physical mounting
        duty1 = int(-v1)  # Front Left (reversed)
        duty2 = int(v2)   # Front Right
        duty3 = int(-v3)  # Rear Left (reversed)
        duty4 = int(v4)   # Rear Right
        
        return (duty1, duty2, duty3, duty4)


class MecanumChassis:
    """
    High-level mecanum chassis controller
    Combines kinematics with board control
    """
    
    def __init__(self, board=None, wheelbase: float = 67, track_width: float = 59,
                 wheel_diameter: float = 65):
        """
        Initialize chassis controller
        
        Args:
            board: BoardController instance (set externally if None)
            wheelbase: Wheelbase in mm
            track_width: Track width in mm  
            wheel_diameter: Wheel diameter in mm
        """
        self.board = board
        self.kinematics = MecanumKinematics(wheelbase, track_width, wheel_diameter)
        
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0
        
    def set_velocity(self, velocity: float, direction: float, angular_rate: float):
        """
        Set chassis velocity
        
        Args:
            velocity: Speed in mm/s
            direction: Direction in degrees  
            angular_rate: Rotation rate (-1.0 to 1.0)
        """
        if self.board is None:
            raise RuntimeError("Board not set - assign to board attribute")
            
        # Calculate wheel duties
        duties = self.kinematics.set_velocity(velocity, direction, angular_rate)
        
        # Send to motors
        motor_commands = [
            (1, duties[0]),
            (2, duties[1]),
            (3, duties[2]),
            (4, duties[3])
        ]
        self.board.set_motor_duty(motor_commands)
        
        # Save state
        self.velocity = velocity
        self.direction = direction
        self.angular_rate = angular_rate
        
    def reset_motors(self):
        """Stop all motors"""
        if self.board:
            self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        self.velocity = 0
        self.direction = 0
        self.angular_rate = 0
