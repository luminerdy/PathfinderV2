#!/usr/bin/env python3
"""
Line Following Controller

Follows a lime green tape line using camera + mecanum drive.

Usage:
    from skills.line_following.line_follower import LineFollower
    
    follower = LineFollower()
    result = follower.follow(timeout=30)
    follower.cleanup()
"""

import sys
import os
import cv2
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board


class LineFollower:
    """
    Follow a colored line on the floor using camera feedback.
    Uses proportional control for steering.
    """
    
    # Frame geometry
    FRAME_W = 640
    FRAME_H = 480
    CENTER_X = 320
    
    # ROI: full visible tape area (top half of frame)
    ROI_TOP_RATIO = 0.0    # See full tape ahead
    ROI_BOTTOM_RATIO = 0.5  # Bottom half is floor under robot
    
    # Weighted scan bands (steer by near, anticipate by far)
    NEAR_WEIGHT = 0.6      # Bottom of ROI (closest to robot)
    MID_WEIGHT = 0.3       # Middle of ROI
    FAR_WEIGHT = 0.1       # Top of ROI (furthest ahead)
    
    # Lime green HSV range (widened for varying lighting)
    HSV_LOWER = np.array([35, 50, 50])
    HSV_UPPER = np.array([85, 255, 255])
    
    # Control
    Kp = 0.30               # Proportional gain for steering (higher = tighter tracking)
    FORWARD_SPEED = 30      # Base forward speed (slower = more precise)
    MAX_STEER = 40          # Maximum steering correction
    MIN_MOTOR = 28          # Minimum motor speed (overcome friction)
    
    # Line detection
    MIN_LINE_RATIO = 0.005  # Minimum green pixel ratio to count as "line found"
    LOST_FRAMES = 15        # Frames without line before stopping
    
    # Morphology kernel
    KERNEL_SIZE = 5
    
    # Arm position for camera down
    ARM_CAMERA_DOWN = [(1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
    
    def __init__(self, board=None):
        self.board = board or get_board()
        self.camera = None
        self.kernel = np.ones((self.KERNEL_SIZE, self.KERNEL_SIZE), np.uint8)
    
    def _open_camera(self):
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.FRAME_W)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.FRAME_H)
            time.sleep(1.0)
    
    def _close_camera(self):
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
    
    def _stop(self):
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
    def _drive(self, forward, steer):
        """
        Drive with forward speed and steering correction.
        
        Args:
            forward: Base forward speed
            steer: Steering value (positive = turn right)
        """
        fl = int(forward + steer)
        fr = int(forward - steer)
        rl = int(forward + steer)
        rr = int(forward - steer)
        
        # Clamp
        def clamp(v):
            if abs(v) < self.MIN_MOTOR and v != 0:
                return self.MIN_MOTOR if v > 0 else -self.MIN_MOTOR
            return max(-100, min(100, v))
        
        self.board.set_motor_duty([
            (1, clamp(fl)), (2, clamp(fr)),
            (3, clamp(rl)), (4, clamp(rr))
        ])
    
    def _position_camera(self):
        """Move arm to camera-down position"""
        self.board.set_servo_position(800, self.ARM_CAMERA_DOWN)
        time.sleep(1.0)
    
    def detect_line(self, frame):
        """
        Detect lime green line in frame.
        
        Args:
            frame: BGR image (640x480)
            
        Returns:
            dict with keys:
                found: bool
                cx: centroid X (pixels)
                cy: centroid Y (pixels, relative to ROI)
                error: pixels from center (+ = right)
                ratio: green pixel ratio in ROI
                mask: binary mask (for debugging)
        """
        # Crop to ROI
        roi_top = int(self.FRAME_H * self.ROI_TOP_RATIO)
        roi_bottom = int(self.FRAME_H * self.ROI_BOTTOM_RATIO)
        roi = frame[roi_top:roi_bottom, :]
        
        # Convert to HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Threshold for lime green
        mask = cv2.inRange(hsv, self.HSV_LOWER, self.HSV_UPPER)
        
        # Clean up
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        
        # Calculate green pixel ratio
        green_pixels = cv2.countNonZero(mask)
        total_pixels = mask.shape[0] * mask.shape[1]
        ratio = green_pixels / total_pixels if total_pixels > 0 else 0
        
        if ratio < self.MIN_LINE_RATIO:
            return {
                'found': False, 'cx': 0, 'cy': 0,
                'error': 0, 'ratio': ratio, 'mask': mask
            }
        
        # Weighted scan: split ROI into 3 bands (far/mid/near)
        h = mask.shape[0]
        third = h // 3
        
        far_band = mask[0:third, :]           # Top = far ahead
        mid_band = mask[third:2*third, :]     # Middle
        near_band = mask[2*third:, :]         # Bottom = closest to robot
        
        def band_cx(band):
            M = cv2.moments(band)
            if M['m00'] > 0:
                return int(M['m10'] / M['m00'])
            return None
        
        far_cx = band_cx(far_band)
        mid_cx = band_cx(mid_band)
        near_cx = band_cx(near_band)
        
        # Weighted average (prefer near, use available bands)
        weighted_cx = 0
        total_weight = 0
        
        if near_cx is not None:
            weighted_cx += near_cx * self.NEAR_WEIGHT
            total_weight += self.NEAR_WEIGHT
        if mid_cx is not None:
            weighted_cx += mid_cx * self.MID_WEIGHT
            total_weight += self.MID_WEIGHT
        if far_cx is not None:
            weighted_cx += far_cx * self.FAR_WEIGHT
            total_weight += self.FAR_WEIGHT
        
        if total_weight == 0:
            return {
                'found': False, 'cx': 0, 'cy': 0,
                'error': 0, 'ratio': ratio, 'mask': mask
            }
        
        cx = int(weighted_cx / total_weight)
        cy = h // 2
        
        error = cx - self.CENTER_X
        
        return {
            'found': True, 'cx': cx, 'cy': cy,
            'error': error, 'ratio': ratio, 'mask': mask
        }
    
    def follow(self, timeout=30, position_camera=True, callback=None):
        """
        Follow the lime green line.
        
        Args:
            timeout: Max seconds to follow
            position_camera: Move arm to camera-down position first
            callback: Function(detection_dict, steer_value) called each frame
            
        Returns:
            dict with success, reason, frames, duration
        """
        self._open_camera()
        
        if position_camera:
            self._position_camera()
        
        start = time.time()
        frames = 0
        lost_count = 0
        
        try:
            while time.time() - start < timeout:
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                frames += 1
                detection = self.detect_line(frame)
                
                if not detection['found']:
                    lost_count += 1
                    
                    if lost_count > self.LOST_FRAMES:
                        self._stop()
                        return {
                            'success': True,
                            'reason': 'line_ended',
                            'frames': frames,
                            'duration': time.time() - start
                        }
                    
                    # Slow down while searching
                    self._drive(self.FORWARD_SPEED // 2, 0)
                    continue
                
                lost_count = 0
                
                # Proportional steering
                steer = detection['error'] * self.Kp
                steer = max(-self.MAX_STEER, min(self.MAX_STEER, steer))
                
                self._drive(self.FORWARD_SPEED, steer)
                
                if callback and frames % 5 == 0:
                    callback(detection, steer)
                
                time.sleep(0.02)  # ~50Hz loop
            
            self._stop()
            return {
                'success': False,
                'reason': 'timeout',
                'frames': frames,
                'duration': time.time() - start
            }
        
        except KeyboardInterrupt:
            self._stop()
            return {
                'success': False,
                'reason': 'interrupted',
                'frames': frames,
                'duration': time.time() - start
            }
        
        finally:
            self._stop()
    
    def cleanup(self):
        self._stop()
        self._close_camera()


if __name__ == '__main__':
    print("Use run_demo.py for the full demo, or:")
    print("  from line_follower import LineFollower")
    print("  follower = LineFollower()")
    print("  result = follower.follow()")
