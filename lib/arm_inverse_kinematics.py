"""
5-DOF Robotic Arm Inverse Kinematics
Clean-room implementation based on standard robotics mathematics.

Arm configuration:
- Servo 1: Base rotation
- Servo 3: Shoulder
- Servo 4: Elbow  
- Servo 5: Wrist/Gripper
- Servo 6: (Alternative base or unused)

Link lengths and geometry determined through measurement and testing.
IK solution uses geometric approach (not DH parameters).
"""

import math
import numpy as np
from typing import Tuple, Optional, List


class ArmIK:
    """
    Inverse kinematics solver for 5-DOF robotic arm
    
    Uses 2D IK in sagittal plane + base rotation for 3D positioning.
    Based on standard robotics principles, not vendor-specific code.
    """
    
    def __init__(self):
        """Initialize arm IK with measured link lengths"""
        # Link lengths (mm) - measured from physical robot
        self.L1 = 61.0   # Base to shoulder height
        self.L2 = 43.5   # Shoulder to elbow length
        self.L3 = 82.85  # Elbow to wrist length
        self.L4 = 82.0   # Wrist to end effector length
        
        # Servo angle limits (degrees)
        self.servo_limits = {
            1: (0, 180),      # Base rotation
            3: (0, 180),      # Shoulder
            4: (0, 180),      # Elbow
            5: (0, 180),      # Wrist/Gripper
            6: (0, 180),      # Optional
        }
        
        # Current servo positions (pulse width)
        self.servos = {
            1: 1500,
            3: 1500,
            4: 1500,
            5: 1500,
            6: 1500,
        }
        
    def pulse_to_angle(self, pulse: int) -> float:
        """
        Convert servo pulse width to angle
        
        Args:
            pulse: Pulse width (500-2500)
            
        Returns:
            Angle in degrees (0-180)
        """
        # Linear mapping: 500μs = 0°, 2500μs = 180°
        angle = (pulse - 500) * 180.0 / 2000.0
        return max(0, min(180, angle))
        
    def angle_to_pulse(self, angle: float) -> int:
        """
        Convert angle to servo pulse width
        
        Args:
            angle: Angle in degrees (0-180)
            
        Returns:
            Pulse width (500-2500)
        """
        # Linear mapping: 0° = 500μs, 180° = 2500μs
        pulse = int(500 + angle * 2000.0 / 180.0)
        return max(500, min(2500, pulse))
        
    def solve_2d_ik(self, x: float, z: float) -> Optional[Tuple[float, float, float]]:
        """
        Solve 2D IK for arm in sagittal plane
        
        Uses law of cosines to find elbow angle, then calculates shoulder and wrist.
        
        Args:
            x: Horizontal distance from base (mm)
            z: Vertical height from base (mm)
            
        Returns:
            (theta_shoulder, theta_elbow, theta_wrist) in degrees, or None if unreachable
        """
        # Adjust for base height
        z_adj = z - self.L1
        
        # Distance from shoulder to target
        r = math.sqrt(x**2 + z_adj**2)
        
        # Check if target is reachable
        max_reach = self.L2 + self.L3 + self.L4
        if r > max_reach or r < abs(self.L2 - self.L3 - self.L4):
            return None
            
        # Solve for elbow angle using law of cosines
        # c² = a² + b² - 2ab*cos(C)
        # For our case: r² = L2² + L3² - 2*L2*L3*cos(elbow_angle)
        cos_elbow = (self.L2**2 + self.L3**2 - r**2) / (2 * self.L2 * self.L3)
        cos_elbow = max(-1, min(1, cos_elbow))  # Clamp to valid range
        elbow_angle = math.degrees(math.acos(cos_elbow))
        
        # Solve for shoulder angle
        alpha = math.atan2(z_adj, x)  # Angle to target
        beta = math.acos((self.L2**2 + r**2 - self.L3**2) / (2 * self.L2 * r))
        shoulder_angle = math.degrees(alpha + beta)
        
        # Wrist angle to keep end effector level
        wrist_angle = 180 - shoulder_angle - elbow_angle
        
        return (shoulder_angle, elbow_angle, wrist_angle)
        
    def set_position(self, x: float, y: float, z: float, 
                    alpha: float = 0) -> Optional[List[Tuple[int, int]]]:
        """
        Solve IK for 3D target position
        
        Args:
            x: Forward/back position (mm)
            y: Left/right position (mm)  
            z: Height (mm)
            alpha: End effector roll angle (degrees)
            
        Returns:
            List of (servo_id, pulse_width) tuples, or None if unreachable
        """
        # Base rotation to reach Y coordinate
        base_angle = math.degrees(math.atan2(y, x))
        base_angle = 90 + base_angle  # Adjust for servo zero position
        
        # Distance in XZ plane
        r_xy = math.sqrt(x**2 + y**2)
        
        # Solve 2D IK in XZ plane
        solution = self.solve_2d_ik(r_xy, z)
        if solution is None:
            return None
            
        shoulder_angle, elbow_angle, wrist_angle = solution
        
        # Convert to servo angles (adjust for mounting orientation)
        servo1_angle = base_angle
        servo3_angle = shoulder_angle
        servo4_angle = elbow_angle
        servo5_angle = wrist_angle
        
        # Clamp to limits
        servo1_angle = max(0, min(180, servo1_angle))
        servo3_angle = max(0, min(180, servo3_angle))
        servo4_angle = max(0, min(180, servo4_angle))
        servo5_angle = max(0, min(180, servo5_angle))
        
        # Convert to pulse widths
        servos = [
            (1, self.angle_to_pulse(servo1_angle)),
            (3, self.angle_to_pulse(servo3_angle)),
            (4, self.angle_to_pulse(servo4_angle)),
            (5, self.angle_to_pulse(servo5_angle)),
        ]
        
        # Update state
        for servo_id, pulse in servos:
            self.servos[servo_id] = pulse
            
        return servos
        
    def get_position(self) -> Tuple[float, float, float]:
        """
        Forward kinematics - calculate end effector position from current angles
        
        Returns:
            (x, y, z) position in mm
        """
        # Get current angles
        base = self.pulse_to_angle(self.servos[1])
        shoulder = self.pulse_to_angle(self.servos[3])
        elbow = self.pulse_to_angle(self.servos[4])
        
        # Calculate position in 2D (XZ plane)
        x_2d = (self.L2 * math.cos(math.radians(shoulder)) + 
                self.L3 * math.cos(math.radians(shoulder + elbow)))
        z = (self.L1 + 
             self.L2 * math.sin(math.radians(shoulder)) + 
             self.L3 * math.sin(math.radians(shoulder + elbow)))
        
        # Rotate to 3D based on base angle
        base_rad = math.radians(base - 90)
        x = x_2d * math.cos(base_rad)
        y = x_2d * math.sin(base_rad)
        
        return (x, y, z)
        
    def set_servo_angle(self, servo_id: int, angle: float) -> int:
        """
        Set single servo to angle
        
        Args:
            servo_id: Servo ID (1, 3, 4, 5, 6)
            angle: Angle in degrees (0-180)
            
        Returns:
            Pulse width
        """
        angle = max(0, min(180, angle))
        pulse = self.angle_to_pulse(angle)
        self.servos[servo_id] = pulse
        return pulse
