#!/usr/bin/env python3
"""
Block Pursue — Continuous drive + arm tracking

Drives toward a block while continuously adjusting the arm/camera
angle to keep the block in view. As the block gets closer (moves
down in frame), the arm tilts further down until it's directly
above the block in pickup position.

This replaces the separate scan → approach → lower arm sequence
with a single continuous motion.

The shoulder servo (S5) controls camera angle AND arm position:
  S5 = 700  → Camera forward (see field)
  S5 = 1214 → Camera down (see floor, block at top of frame)
  S5 = 1694 → Block close (block filling frame)
  S5 = 2410 → Arm at floor (pickup position)

We interpolate S5 based on block's Y position in frame:
  Block Y ~50-100 (top)    → S5 ~1214 (looking down at distant block)
  Block Y ~200-300 (mid)   → S5 ~1500 (tracking, getting closer)
  Block Y ~350-420 (bottom)→ S5 ~1900 (very close, arm reaching)
  Block Y >420             → S5 ~2410 (at block, ready to grab)
"""

import cv2
import math
import time
from lib.board import get_board
BoardController = None  # Use get_board() instead
from skills.block_detect import BlockDetector


class BlockPursuer:
    """
    Continuously drive toward a block while tracking with arm.
    """
    
    # Frame
    FRAME_W = 640
    FRAME_H = 480
    CENTER_X = 320
    
    # Target: block at center-bottom means we're on top of it
    TARGET_Y = 400
    X_TOLERANCE = 50
    Y_TOLERANCE = 30
    
    # Speed
    MAX_SPEED = 28
    MIN_SPEED = 28
    Kx = 0.12
    Ky = 0.08
    
    # Arm interpolation: map block Y position → shoulder servo (S5)
    # (y_position, s5_value)
    ARM_MAP = [
        (50,  1214),   # Block at top of frame → camera down
        (150, 1400),   # Getting closer
        (250, 1550),   # Mid frame
        (350, 1750),   # Close
        (420, 2000),   # Very close
        (460, 2410),   # At block → arm at floor
    ]
    
    # Other servos stay fixed during pursuit
    ARM_FIXED = {1: 2500, 3: 590, 4: 2450, 6: 1500}  # Gripper open, wrist/elbow/base fixed
    
    # Tracking (wider radius because arm tilt shifts the view)
    LOCK_RADIUS = 200
    LOST_TIMEOUT = 2.0
    TIMEOUT = 30
    MIN_BATTERY = None
    
    def __init__(self, board=None):
        self.board = board or get_board()
        self.detector = BlockDetector()
        self.camera = None
        self._last_seen = 0
        self._locked_x = 0
        self._locked_y = 0
        self._locked_color = None
        self._is_locked = False
        self._current_s5 = 1214  # Start at camera_down
    
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
    
    def _drive(self, strafe, forward):
        fl = int(forward + strafe)
        fr = int(forward - strafe)
        rl = int(forward - strafe)
        rr = int(forward + strafe)
        self.board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])
    
    def _clamp(self, speed):
        if abs(speed) < 1:
            return 0
        sign = 1 if speed > 0 else -1
        mag = min(max(abs(speed), self.MIN_SPEED), self.MAX_SPEED)
        return sign * mag
    
    def _interpolate_s5(self, block_y):
        """
        Map block Y position in frame to shoulder servo value.
        Linear interpolation between ARM_MAP points.
        """
        # Clamp to range
        if block_y <= self.ARM_MAP[0][0]:
            return self.ARM_MAP[0][1]
        if block_y >= self.ARM_MAP[-1][0]:
            return self.ARM_MAP[-1][1]
        
        # Find segment
        for i in range(len(self.ARM_MAP) - 1):
            y0, s0 = self.ARM_MAP[i]
            y1, s1 = self.ARM_MAP[i + 1]
            if y0 <= block_y <= y1:
                t = (block_y - y0) / (y1 - y0)
                return int(s0 + (s1 - s0) * t)
        
        return self.ARM_MAP[-1][1]
    
    def _update_arm(self, block_y):
        """Smoothly move arm to track block position"""
        target_s5 = self._interpolate_s5(block_y)
        
        # Only update if significantly different (avoid servo chatter)
        # Larger threshold = smoother, less view disruption
        if abs(target_s5 - self._current_s5) > 50:
            self._current_s5 = target_s5
            # Move shoulder only — other servos stay fixed
            self.board.set_servo_position(200, [(5, target_s5)])
    
    def _find_locked(self, blocks):
        if not blocks:
            return None
        if not self._is_locked:
            return blocks[0]
        
        best = None
        best_dist = float('inf')
        for b in blocks:
            if self._locked_color and b.color != self._locked_color:
                continue
            dx = b.center_x - self._locked_x
            dy = b.center_y - self._locked_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < best_dist and dist < self.LOCK_RADIUS:
                best_dist = dist
                best = b
        return best
    
    def pursue(self, color=None, timeout=None, callback=None):
        """
        Pursue a block: drive toward it while arm tracks continuously.
        
        Returns when block is at bottom of frame (arm pointing at it)
        or on timeout/loss.
        """
        if timeout is None:
            timeout = self.TIMEOUT
        
        # Battery check
        min_bat = self.MIN_BATTERY
        if min_bat is None:
            try:
                from lib.board import PLATFORM
                min_bat = 7.0 if PLATFORM == 'pi4' else 8.1
            except ImportError:
                min_bat = 7.5
        
        mv = self.board.get_battery()
        if mv and mv / 1000.0 < min_bat:
            return {'success': False, 'reason': 'battery_low'}
        
        self._open_camera()
        self._is_locked = False
        self._last_seen = time.time()
        self._current_s5 = 1214
        
        # Start in camera_down position
        servos = [(sid, pos) for sid, pos in self.ARM_FIXED.items()]
        servos.append((5, 1214))
        self.board.set_servo_position(800, servos)
        time.sleep(1)
        
        start = time.time()
        iteration = 0
        last_x, last_y = 0, 0
        last_color = None
        
        try:
            while time.time() - start < timeout:
                iteration += 1
                
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                colors = [color] if color else None
                all_blocks = self.detector.detect(frame, colors=colors)
                block = self._find_locked(all_blocks)
                
                if block is None:
                    if time.time() - self._last_seen > self.LOST_TIMEOUT:
                        self._stop()
                        return {
                            'success': False, 'color': last_color,
                            'final_x': last_x, 'final_y': last_y,
                            'final_s5': self._current_s5,
                            'iterations': iteration,
                            'reason': 'block_lost'
                        }
                    self._stop()
                    continue
                
                # Lock / update
                if not self._is_locked:
                    self._locked_x = block.center_x
                    self._locked_y = block.center_y
                    self._locked_color = block.color
                    self._is_locked = True
                    if callback:
                        callback(block, self._current_s5,
                                "LOCKED %s at %dcm" % (block.color, block.estimated_distance_mm/10))
                else:
                    self._locked_x = block.center_x
                    self._locked_y = block.center_y
                
                self._last_seen = time.time()
                last_x = block.center_x
                last_y = block.center_y
                last_color = block.color
                
                # Calculate errors
                error_x = block.center_x - self.CENTER_X
                error_y = self.TARGET_Y - block.center_y
                
                # Update arm position based on block Y
                # Only tilt arm when block is horizontally centered
                if abs(error_x) < self.X_TOLERANCE * 1.5:
                    self._update_arm(block.center_y)
                
                if abs(error_x) < self.X_TOLERANCE and abs(error_y) < self.Y_TOLERANCE:
                    self._stop()
                    if callback:
                        callback(block, self._current_s5, "ARRIVED")
                    return {
                        'success': True, 'color': block.color,
                        'final_x': block.center_x, 'final_y': block.center_y,
                        'final_s5': self._current_s5,
                        'iterations': iteration,
                        'reason': 'reached'
                    }
                
                # Drive
                kx = self.Kx * 0.5 if block.estimated_distance_mm < 300 else self.Kx
                ky = self.Ky * 0.5 if block.estimated_distance_mm < 300 else self.Ky
                
                strafe = self._clamp(error_x * kx)
                forward = self._clamp(error_y * ky) if error_y > 0 else 0
                
                # Rotate if at edge
                if block.center_x < 80 or block.center_x > 560:
                    rot = self.MIN_SPEED if block.center_x > self.CENTER_X else -self.MIN_SPEED
                    self.board.set_motor_duty([(1,rot),(2,-rot),(3,rot),(4,-rot)])
                    time.sleep(0.1)
                    continue
                
                # Center first
                if abs(error_x) > self.X_TOLERANCE * 2:
                    forward = 0
                
                self._drive(strafe, forward)
                
                if callback and iteration % 15 == 0:
                    parts = []
                    if forward:
                        parts.append("fwd=%d" % forward)
                    if strafe:
                        parts.append("str=%d" % strafe)
                    callback(block, self._current_s5,
                            "%s S5=%d" % (' '.join(parts) if parts else 'center', self._current_s5))
                
                time.sleep(0.03)
            
            self._stop()
            return {
                'success': False, 'color': last_color,
                'final_x': last_x, 'final_y': last_y,
                'final_s5': self._current_s5,
                'iterations': iteration,
                'reason': 'timeout'
            }
        
        except KeyboardInterrupt:
            self._stop()
            return {'success': False, 'reason': 'interrupted'}
        
        finally:
            self._stop()
    
    def cleanup(self):
        self._stop()
        self._close_camera()


if __name__ == '__main__':
    print("=" * 60)
    print("BLOCK PURSUE - Continuous drive + arm tracking")
    print("=" * 60)
    
    pursuer = BlockPursuer()
    
    def cb(block, s5, action):
        print("  %s (%d,%d) S5=%d - %s" % (
            block.color, block.center_x, block.center_y, s5, action))
    
    try:
        result = pursuer.pursue(callback=cb)
        print()
        print("Result: %s" % ("SUCCESS" if result.get('success') else "FAILED"))
        print("  Reason: %s" % result.get('reason'))
        print("  Final S5: %s" % result.get('final_s5'))
    finally:
        pursuer.cleanup()
