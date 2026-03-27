#!/usr/bin/env python3
"""
Block Approach — Drive to a block using vision tracking with target lock

Strategy:
1. Detect colored block in camera frame
2. LOCK onto specific block (remember position + color)
3. Track locked target frame-to-frame (match nearest to last position)
4. Strafe to center block horizontally (cx -> 320)
5. Drive forward until block is at bottom-center of frame (cy -> ~420)
6. Stop — block is in front of robot at pickup distance

Target lock prevents jumping between blocks mid-approach.
"""

import cv2
import math
import time
from lib.board import get_board
BoardController = None  # Use get_board() instead
from skills.block_detect import BlockDetector, BlockDetection


class BlockApproach:
    """
    Drive toward a detected block using mecanum strafe + forward.
    Locks onto a specific target and tracks it frame-to-frame.
    """
    
    # Frame geometry
    FRAME_W = 640
    FRAME_H = 480
    CENTER_X = 320
    TARGET_Y = 420          # Block at bottom = close enough
    
    # Tolerances (pixels)
    X_TOLERANCE = 40
    Y_TOLERANCE = 30
    
    # Speed control
    MAX_SPEED = 30
    MIN_SPEED = 28
    
    # Proportional gains
    Kx = 0.15              # Strafe gain
    Ky = 0.10              # Forward gain
    
    # Target lock
    LOCK_RADIUS = 120       # Max pixels a locked target can move between frames
    
    # Safety
    TIMEOUT = 30
    LOST_TIMEOUT = 2.0
    MIN_BATTERY = None      # Auto: Pi4=7.0, Pi5=8.1
    
    def __init__(self, board=None):
        self.board = board or get_board()
        self.detector = BlockDetector()
        self.camera = None
        self._last_seen = 0
        
        # Target lock state
        self._locked_x = 0
        self._locked_y = 0
        self._locked_color = None
        self._is_locked = False
    
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
        """Mecanum drive: strafe + forward simultaneously"""
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
    
    def _find_locked_target(self, blocks):
        """
        Find the detection that best matches our locked target.
        
        If not locked yet, returns the nearest block.
        If locked, returns the detection closest to last known position
        (within LOCK_RADIUS). Returns None if target lost.
        """
        if not blocks:
            return None
        
        if not self._is_locked:
            # Not locked yet — pick nearest block
            return blocks[0]  # Already sorted by distance
        
        # Locked — find detection closest to last known position
        best = None
        best_dist = float('inf')
        
        for b in blocks:
            # Must match color
            if self._locked_color and b.color != self._locked_color:
                continue
            
            # Distance from last known position
            dx = b.center_x - self._locked_x
            dy = b.center_y - self._locked_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < best_dist and dist < self.LOCK_RADIUS:
                best_dist = dist
                best = b
        
        return best
    
    def _lock_target(self, block):
        """Lock onto a specific block"""
        self._locked_x = block.center_x
        self._locked_y = block.center_y
        self._locked_color = block.color
        self._is_locked = True
    
    def _update_lock(self, block):
        """Update lock position to current detection"""
        self._locked_x = block.center_x
        self._locked_y = block.center_y
    
    def _reset_lock(self):
        """Release target lock"""
        self._is_locked = False
        self._locked_x = 0
        self._locked_y = 0
        self._locked_color = None
    
    def approach(self, color=None, timeout=None, callback=None):
        """
        Approach the nearest visible block with target locking.
        
        First detection locks the target. Subsequent frames track
        only that specific block (by position + color). If the locked
        target is lost for LOST_TIMEOUT seconds, approach fails.
        
        Args:
            color: Target color ('red', 'blue', 'yellow') or None for any
            timeout: Max seconds
            callback: Function(block, action_str) called periodically
            
        Returns:
            dict with success, color, final_x, final_y, iterations, reason
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
        if mv:
            v = mv / 1000.0
            if v < min_bat:
                return {
                    'success': False, 'color': None,
                    'final_x': 0, 'final_y': 0,
                    'iterations': 0,
                    'reason': f'battery_low ({v:.2f}V)'
                }
        
        self._open_camera()
        self._reset_lock()
        self._last_seen = time.time()
        
        start = time.time()
        iteration = 0
        last_color = None
        last_x, last_y = 0, 0
        
        try:
            while time.time() - start < timeout:
                iteration += 1
                
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Detect all blocks of target color
                colors = [color] if color else None
                all_blocks = self.detector.detect(frame, colors=colors)
                
                # Find our locked target (or nearest if not locked yet)
                block = self._find_locked_target(all_blocks)
                
                if block is None:
                    # Target lost
                    if time.time() - self._last_seen > self.LOST_TIMEOUT:
                        self._stop()
                        return {
                            'success': False, 'color': last_color,
                            'final_x': last_x, 'final_y': last_y,
                            'iterations': iteration,
                            'reason': 'block_lost'
                        }
                    self._stop()
                    continue
                
                # Lock onto target (first detection) or update position
                if not self._is_locked:
                    self._lock_target(block)
                    if callback:
                        callback(block, f'LOCKED ({block.color} at {block.estimated_distance_mm/10:.0f}cm)')
                else:
                    self._update_lock(block)
                
                self._last_seen = time.time()
                last_color = block.color
                last_x = block.center_x
                last_y = block.center_y
                
                # Calculate errors
                error_x = block.center_x - self.CENTER_X
                error_y = self.TARGET_Y - block.center_y
                
                # Check if arrived
                if abs(error_x) < self.X_TOLERANCE and abs(error_y) < self.Y_TOLERANCE:
                    self._stop()
                    if callback:
                        callback(block, 'REACHED')
                    return {
                        'success': True, 'color': block.color,
                        'final_x': block.center_x, 'final_y': block.center_y,
                        'iterations': iteration,
                        'reason': 'reached'
                    }
                
                # Calculate speeds (reduce gains for close blocks)
                dist_cm = block.estimated_distance_mm / 10
                kx = self.Kx * 0.5 if dist_cm < 30 else self.Kx
                ky = self.Ky * 0.7 if dist_cm < 30 else self.Ky
                
                strafe = self._clamp(error_x * kx)
                forward = self._clamp(error_y * ky) if error_y > 0 else 0
                
                # If block near edge of frame, rotate in place to bring it center
                if block.center_x < 80 or block.center_x > 560:
                    rot_dir = self.MIN_SPEED if block.center_x > self.CENTER_X else -self.MIN_SPEED
                    self.board.set_motor_duty([
                        (1, rot_dir), (2, -rot_dir),
                        (3, rot_dir), (4, -rot_dir)
                    ])
                    time.sleep(0.1)
                    continue
                
                # Center first before driving forward
                if abs(error_x) > self.X_TOLERANCE * 2:
                    forward = 0
                
                self._drive(strafe, forward)
                
                # Callback
                if callback and iteration % 10 == 0:
                    parts = []
                    if forward:
                        parts.append(f'fwd={forward:.0f}')
                    if strafe:
                        parts.append(f'strafe={strafe:.0f}')
                    callback(block, ' '.join(parts) if parts else 'centering')
                
                time.sleep(0.03)
            
            self._stop()
            return {
                'success': False, 'color': last_color,
                'final_x': last_x, 'final_y': last_y,
                'iterations': iteration,
                'reason': 'timeout'
            }
        
        except KeyboardInterrupt:
            self._stop()
            return {
                'success': False, 'color': last_color,
                'final_x': last_x, 'final_y': last_y,
                'iterations': iteration,
                'reason': 'interrupted'
            }
        
        finally:
            self._stop()
    
    def cleanup(self):
        self._stop()
        self._close_camera()


def print_callback(block, action):
    print(f"  {block.color} at ({block.center_x},{block.center_y}) "
          f"{block.estimated_distance_mm/10:.0f}cm - {action}")


if __name__ == '__main__':
    print("=" * 60)
    print("BLOCK APPROACH WITH TARGET LOCK")
    print("=" * 60)
    print()
    
    approach = BlockApproach()
    
    mv = approach.board.get_battery()
    if mv:
        print(f"Battery: {mv/1000:.2f}V")
        print()
    
    try:
        result = approach.approach(callback=print_callback)
        
        print()
        ok = result['success']
        print(f"Result: {'SUCCESS' if ok else 'FAILED'}")
        print(f"  Color: {result['color']}")
        print(f"  Position: ({result['final_x']}, {result['final_y']})")
        print(f"  Reason: {result['reason']}")
    
    except KeyboardInterrupt:
        print("\nStopped")
    
    finally:
        approach.cleanup()
