"""
Robotic Arm Control
Provides inverse kinematics and position control for the MasterPi arm
"""

import sys
import time
import logging
from typing import Optional, Tuple, Dict

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sdk.kinematics.arm_move_ik import ArmIK as BaseArmIK

from .board import Board

logger = logging.getLogger(__name__)


class Arm:
    """
    Robotic arm controller with inverse kinematics
    5-DOF arm (base, shoulder, elbow, wrist, gripper)
    
    Servos:
        1: Base rotation
        2: Shoulder
        3: Elbow  
        4: Wrist
        5: Gripper
    """
    
    # Named positions (x, y, z in mm)
    POSITIONS = {
        'home': (0, 150, 100),
        'rest': (0, 100, 50),
        'pickup': (0, 200, 20),
        'carry': (0, 100, 150),
        'drop': (0, 180, 50),
        'forward': (0, 200, 100),
        'up': (0, 100, 200),
    }
    
    def __init__(self, board: Board):
        """
        Initialize arm controller
        
        Args:
            board: Board instance for servo control
        """
        self.board = board
        self._ik = BaseArmIK()
        self._ik.board = board._board
        
        self._current_position = None
        self._current_pitch = 0
        self._gripper_state = 0  # 0 = open, 90 = closed
        
        logger.info("Arm initialized")
        
    # ===== Position Control =====
    
    def move_to(self, x: float, y: float, z: float, pitch: float = None, 
                duration: float = 1.0) -> bool:
        """
        Move arm to XYZ position using inverse kinematics
        
        Args:
            x: X coordinate in mm (left/right, 0 = center)
            y: Y coordinate in mm (forward/back)
            z: Z coordinate in mm (height)
            pitch: Gripper pitch angle in degrees (optional, will auto-find)
            duration: Movement duration in seconds
            
        Returns:
            True if successful, False if position unreachable
        """
        try:
            # Convert to cm for IK solver
            coords = (x / 10.0, y / 10.0, z / 10.0)
            
            if pitch is not None:
                # Use specified pitch
                result = self._ik.setPitchRange(coords, pitch, pitch, 1)
            else:
                # Auto-find pitch in reasonable range
                result = self._ik.setPitchRange(coords, -90, 90, 5)
                
            if not result:
                logger.warning(f"Position ({x}, {y}, {z}) unreachable")
                return False
                
            servos, actual_pitch = result
            
            # Execute movement
            self._ik.servosMove(
                [servos['servo3'], servos['servo4'], servos['servo5'], servos['servo6']], 
                int(duration * 1000)
            )
            
            self._current_position = (x, y, z)
            self._current_pitch = actual_pitch
            
            return True
            
        except Exception as e:
            logger.error(f"Error moving arm: {e}")
            return False
            
    def move_to_named(self, position_name: str, duration: float = 1.0) -> bool:
        """
        Move to a named position
        
        Args:
            position_name: Name from POSITIONS dict
            duration: Movement duration in seconds
            
        Returns:
            True if successful
        """
        if position_name not in self.POSITIONS:
            logger.warning(f"Unknown position: {position_name}")
            return False
            
        x, y, z = self.POSITIONS[position_name]
        return self.move_to(x, y, z, duration=duration)
        
    def home(self, duration: float = 1.5):
        """Move to home position"""
        return self.move_to_named('home', duration)
        
    def rest(self, duration: float = 1.0):
        """Move to rest position (low, safe)"""
        return self.move_to_named('rest', duration)
        
    # ===== Relative Movement =====
    
    def move_relative(self, dx: float = 0, dy: float = 0, dz: float = 0, 
                     duration: float = 1.0) -> bool:
        """
        Move relative to current position
        
        Args:
            dx, dy, dz: Offset in mm
            duration: Movement duration
            
        Returns:
            True if successful
        """
        if self._current_position is None:
            logger.warning("Current position unknown, move to absolute position first")
            return False
            
        x, y, z = self._current_position
        return self.move_to(x + dx, y + dy, z + dz, duration=duration)
        
    def raise_arm(self, distance: float = 20, duration: float = 0.5):
        """Raise arm by distance (mm)"""
        return self.move_relative(dz=distance, duration=duration)
        
    def lower_arm(self, distance: float = 20, duration: float = 0.5):
        """Lower arm by distance (mm)"""
        return self.move_relative(dz=-distance, duration=duration)
        
    def extend_arm(self, distance: float = 20, duration: float = 0.5):
        """Extend arm forward"""
        return self.move_relative(dy=distance, duration=duration)
        
    def retract_arm(self, distance: float = 20, duration: float = 0.5):
        """Retract arm backward"""
        return self.move_relative(dy=-distance, duration=duration)
        
    # ===== Gripper Control =====
    
    def set_gripper(self, position: float, duration: float = 0.5):
        """
        Set gripper position
        
        Args:
            position: 0 = fully open, 1 = fully closed
            duration: Movement duration
        """
        position = max(0, min(1, position))
        pulse = int(500 + position * 2000)  # 500 (open) to 2500 (closed)
        
        self.board.set_servo_position(5, pulse, duration)  # Assuming servo 5 is gripper
        self._gripper_state = position
        
    def open_gripper(self, duration: float = 0.5):
        """Fully open gripper"""
        self.set_gripper(0, duration)
        
    def close_gripper(self, duration: float = 0.5):
        """Fully close gripper"""
        self.set_gripper(1, duration)
        
    def grip(self, force: float = 0.7, duration: float = 0.5):
        """Close gripper with specified force (0-1)"""
        self.set_gripper(force, duration)
        
    # ===== Pick and Place =====
    
    def pick_sequence(self, x: float, y: float, z: float, 
                     approach_height: float = 50) -> bool:
        """
        Execute pick sequence
        
        Args:
            x, y, z: Target position
            approach_height: Height to approach from
            
        Returns:
            True if successful
        """
        try:
            # Open gripper
            self.open_gripper()
            time.sleep(0.5)
            
            # Approach from above
            if not self.move_to(x, y, z + approach_height, duration=1.0):
                return False
            time.sleep(0.3)
            
            # Lower to target
            if not self.move_to(x, y, z, duration=0.8):
                return False
            time.sleep(0.3)
            
            # Close gripper
            self.close_gripper()
            time.sleep(0.5)
            
            # Lift
            if not self.move_to(x, y, z + approach_height, duration=0.8):
                return False
            time.sleep(0.3)
            
            return True
            
        except Exception as e:
            logger.error(f"Pick sequence failed: {e}")
            return False
            
    def place_sequence(self, x: float, y: float, z: float, 
                      approach_height: float = 50) -> bool:
        """
        Execute place sequence
        
        Args:
            x, y, z: Target position
            approach_height: Height to approach from
            
        Returns:
            True if successful
        """
        try:
            # Approach from above
            if not self.move_to(x, y, z + approach_height, duration=1.0):
                return False
            time.sleep(0.3)
            
            # Lower to target
            if not self.move_to(x, y, z, duration=0.8):
                return False
            time.sleep(0.3)
            
            # Open gripper
            self.open_gripper()
            time.sleep(0.5)
            
            # Retract
            if not self.move_to(x, y, z + approach_height, duration=0.8):
                return False
            time.sleep(0.3)
            
            return True
            
        except Exception as e:
            logger.error(f"Place sequence failed: {e}")
            return False
            
    # ===== Direct Servo Control =====
    
    def set_servo_angle(self, servo_id: int, angle: float, duration: float = 0.5):
        """
        Directly control servo angle (for calibration/testing)
        
        Args:
            servo_id: Servo ID (3-6)
            angle: Angle in degrees (-90 to 90)
            duration: Movement duration
        """
        # Convert angle to pulse width (assuming standard servo)
        pulse = int(1500 + angle * (2000 / 180))
        pulse = max(500, min(2500, pulse))
        
        self.board.set_servo_position(servo_id, pulse, duration)
        
    # ===== State Queries =====
    
    @property
    def position(self) -> Optional[Tuple[float, float, float]]:
        """Current XYZ position"""
        return self._current_position
        
    @property
    def pitch(self) -> float:
        """Current gripper pitch angle"""
        return self._current_pitch
        
    @property
    def gripper_position(self) -> float:
        """Current gripper position (0-1)"""
        return self._gripper_state
        
    @property
    def is_gripping(self) -> bool:
        """Check if gripper is closed"""
        return self._gripper_state > 0.5
