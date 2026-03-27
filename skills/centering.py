#!/usr/bin/env python3
"""
Centering Skill - Universal target centering for navigation

Works for both AprilTags and blocks using proportional control.
Uses pose angle when available, falls back to pixel offset.
"""

import math
from lib.board import get_board
BoardController = None  # Use get_board() instead

class CenteringController:
    """
    Proportional centering controller
    
    Handles centering on any visual target (AprilTag, block, etc.)
    using either pose angle or pixel offset.
    """
    
    def __init__(self, board=None):
        """
        Initialize centering controller
        
        Args:
            board: BoardController instance (optional, creates if None)
        """
        self.board = board if board else get_board()
        
        # Tuning parameters
        self.PIXEL_TOLERANCE = 40       # ±40px is "centered enough"
        self.ANGLE_TOLERANCE = 5.0      # ±5° is "centered enough" (was 3.0)
        
        # Rotation speed limits (calibrated Day 7)
        self.MIN_ROTATION_SPEED = 28    # Minimum to overcome friction (calibrated)
        self.MAX_ROTATION_SPEED = 28    # Use constant reliable speed
        
        # Proportional gain (tuning parameter)
        self.ANGLE_GAIN = 0.5           # Speed per degree (reduced from 0.8)
        self.PIXEL_GAIN = 0.03          # Speed per pixel (reduced from 0.05)
        
        # Estimated rotation rate (deg/sec at power 28, calibrated)
        self.ROTATION_RATE = 105        # degrees per second at power 28
        
        # Damping factor (reduce speed when getting close)
        self.DAMPING_THRESHOLD = 10     # Start damping below this angle
        self.DAMPING_FACTOR = 0.6       # Multiply speed by this when close
        
        self.frame_center_x = 320       # 640/2
    
    def is_centered_angle(self, angle_deg):
        """
        Check if target is centered by angle
        
        Args:
            angle_deg: Angle offset in degrees (+ = right, - = left)
            
        Returns:
            bool: True if centered within tolerance
        """
        return abs(angle_deg) < self.ANGLE_TOLERANCE
    
    def is_centered_pixels(self, target_x):
        """
        Check if target is centered by pixel position
        
        Args:
            target_x: Target X position in frame (0-640)
            
        Returns:
            bool: True if centered within tolerance
        """
        offset = target_x - self.frame_center_x
        return abs(offset) < self.PIXEL_TOLERANCE
    
    def calculate_rotation(self, angle_deg=None, target_x=None):
        """
        Calculate rotation needed to center target
        
        Args:
            angle_deg: Pose angle in degrees (preferred)
            target_x: Pixel X position (fallback)
            
        Returns:
            tuple: (speed, duration, direction)
                speed: Motor speed (0-100)
                duration: Time in seconds
                direction: 'right', 'left', or None if centered
        """
        # Prefer angle-based centering (more accurate)
        if angle_deg is not None:
            if self.is_centered_angle(angle_deg):
                return 0, 0, None
            
            # Proportional speed based on angle
            base_speed = min(
                self.MIN_ROTATION_SPEED + abs(angle_deg) * self.ANGLE_GAIN,
                self.MAX_ROTATION_SPEED
            )
            
            # Apply damping when close to center (prevent oscillation)
            if abs(angle_deg) < self.DAMPING_THRESHOLD:
                speed = base_speed * self.DAMPING_FACTOR
            else:
                speed = base_speed
            
            # Estimate duration based on angle and speed
            # Use conservative estimate (undershoot slightly better than overshoot)
            duration = abs(angle_deg) / self.ROTATION_RATE * 0.8  # 80% of calculated
            
            # Direction
            direction = 'right' if angle_deg > 0 else 'left'
            
            return int(speed), duration, direction
        
        # Fall back to pixel-based centering
        elif target_x is not None:
            offset = target_x - self.frame_center_x
            
            if self.is_centered_pixels(target_x):
                return 0, 0, None
            
            # Proportional speed based on offset
            speed = min(
                self.MIN_ROTATION_SPEED + abs(offset) * self.PIXEL_GAIN,
                self.MAX_ROTATION_SPEED
            )
            
            # Estimate duration (less accurate than angle)
            # Assume ~200 pixels per second of rotation
            duration = abs(offset) / 200
            
            # Direction
            direction = 'right' if offset > 0 else 'left'
            
            return int(speed), duration, direction
        
        else:
            raise ValueError("Must provide either angle_deg or target_x")
    
    def rotate_to_center(self, angle_deg=None, target_x=None):
        """
        Execute rotation to center target
        
        Args:
            angle_deg: Pose angle in degrees (preferred)
            target_x: Pixel X position (fallback)
            
        Returns:
            str: Status message
        """
        speed, duration, direction = self.calculate_rotation(angle_deg, target_x)
        
        if direction is None:
            return "Already centered"
        
        # Execute rotation
        if direction == 'right':
            self.board.set_motor_duty([(1, speed), (2, -speed), 
                                       (3, speed), (4, -speed)])
        else:  # left
            self.board.set_motor_duty([(1, -speed), (2, speed), 
                                       (3, -speed), (4, speed)])
        
        # Wait for rotation
        import time
        time.sleep(duration)
        
        # Stop
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        
        return f"Rotated {direction} (speed {speed}, {duration:.2f}s)"
    
    def center_on_tag(self, tag, verbose=False):
        """
        Center on an AprilTag detection
        
        Args:
            tag: AprilTag detection object
            verbose: Print status messages
            
        Returns:
            bool: True if centered, False if rotation applied
        """
        # Try pose angle first
        if hasattr(tag, 'pose_t') and tag.pose_t is not None:
            x = tag.pose_t[0][0]
            z = tag.pose_t[2][0]
            angle = math.degrees(math.atan2(x, z))
            
            if verbose:
                print(f"Centering on Tag {tag.tag_id} using pose angle: {angle:+.1f}°")
            
            result = self.rotate_to_center(angle_deg=angle)
            
            if verbose:
                print(f"  {result}")
            
            return "Already centered" in result
        
        # Fall back to pixel position
        else:
            target_x = tag.center[0]
            
            if verbose:
                offset = target_x - self.frame_center_x
                print(f"Centering on Tag {tag.tag_id} using pixels: offset {offset:+.0f}px")
            
            result = self.rotate_to_center(target_x=target_x)
            
            if verbose:
                print(f"  {result}")
            
            return "Already centered" in result
    
    def center_on_block(self, block_center_x, verbose=False):
        """
        Center on a detected block
        
        Args:
            block_center_x: X position of block center (0-640)
            verbose: Print status messages
            
        Returns:
            bool: True if centered, False if rotation applied
        """
        offset = block_center_x - self.frame_center_x
        
        if verbose:
            print(f"Centering on block: offset {offset:+.0f}px")
        
        result = self.rotate_to_center(target_x=block_center_x)
        
        if verbose:
            print(f"  {result}")
        
        return "Already centered" in result


# Convenience function for quick use
def center_on_target(angle_deg=None, target_x=None, board=None):
    """
    Quick centering function
    
    Args:
        angle_deg: Pose angle (preferred)
        target_x: Pixel X position (fallback)
        board: BoardController instance
        
    Returns:
        bool: True if was already centered
    """
    controller = CenteringController(board)
    result = controller.rotate_to_center(angle_deg, target_x)
    return "Already centered" in result
