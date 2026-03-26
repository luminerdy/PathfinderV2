#!/usr/bin/env python3
"""
Block Approach — Drive to a block using vision tracking

Strategy:
1. Detect colored block in camera frame
2. Strafe to center block horizontally (cx → 320)
3. Drive forward until block is at bottom-center of frame (cy → ~440)
4. Stop — block is in front of robot at pickup distance

When block is at center-bottom of frame, it's directly
in front of the robot within arm reach.
"""

import cv2
import time
from lib.board_protocol import BoardController
from skills.block_detect import BlockDetector


class BlockApproach:
    """
    Drive toward a detected block using mecanum strafe + forward.
    Tracks block position in frame and stops when block is
    at center-bottom (pickup position).
    """
    
    # Frame geometry
    FRAME_W = 640
    FRAME_H = 480
    CENTER_X = 320          # Horizontal center
    TARGET_Y = 420          # Target Y position (near bottom = close)
    
    # Tolerances (pixels)
    X_TOLERANCE = 40        # Horizontal centering tolerance
    Y_TOLERANCE = 30        # Vertical (distance) tolerance
    
    # Speed control
    MAX_SPEED = 30          # Maximum motor power
    MIN_SPEED = 28          # Minimum to overcome friction
    
    # Proportional gains
    Kx = 0.15               # Strafe gain (speed per pixel of horizontal error)
    Ky = 0.10               # Forward gain (speed per pixel of vertical error)
    
    # Safety
    TIMEOUT = 30            # Max seconds
    LOST_TIMEOUT = 2.0      # Stop if block lost for this long
    MIN_BATTERY = None      # Auto-detect: Pi 4 = 7.0V, Pi 5 = 8.1V
    
    def __init__(self, board=None):
        self.board = board or BoardController()
        self.detector = BlockDetector()
        self.camera = None
        self._last_seen = 0
    
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
        """Clamp speed: zero stays zero, otherwise min-max"""
        if abs(speed) < 1:
            return 0
        sign = 1 if speed > 0 else -1
        mag = min(max(abs(speed), self.MIN_SPEED), self.MAX_SPEED)
        return sign * mag
    
    def approach(self, color=None, timeout=None, callback=None):
        """
        Approach the nearest visible block.
        
        Drives forward while keeping block centered horizontally.
        Stops when block reaches bottom-center of frame.
        
        Args:
            color: Target color ('red', 'blue', 'yellow') or None for any
            timeout: Max seconds (default self.TIMEOUT)
            callback: Function(block, action_str) called each frame
            
        Returns:
            dict with:
                success: bool
                color: str or None
                final_x: int (pixel)
                final_y: int (pixel) 
                iterations: int
                reason: str
        """
        if timeout is None:
            timeout = self.TIMEOUT
        
        # Battery check (platform-aware threshold)
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
                
                # Detect blocks
                block = self.detector.find_nearest(frame, color=color)
                
                if block is None:
                    # Block lost
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
                
                # Reject detection if it jumped too far (likely different object)
                if last_x > 0 and last_y > 0:
                    dx = abs(block.center_x - last_x)
                    dy = abs(block.center_y - last_y)
                    if dx > 150 or dy > 150:
                        # Detection jumped — ignore this frame
                        continue
                
                # Block found
                self._last_seen = time.time()
                last_color = block.color
                last_x = block.center_x
                last_y = block.center_y
                
                # Calculate errors
                error_x = block.center_x - self.CENTER_X    # + = block is right
                error_y = self.TARGET_Y - block.center_y     # + = block is above target (too far)
                
                # Check if arrived (block at center-bottom)
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
                
                # Calculate speeds
                strafe = self._clamp(error_x * self.Kx)
                forward = self._clamp(error_y * self.Ky) if error_y > 0 else 0
                
                # Don't drive forward if not centered enough
                if abs(error_x) > self.X_TOLERANCE * 2:
                    forward = 0  # Center first, then drive
                
                # Drive
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
            
            # Timeout
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
    print("="*70)
    print("BLOCK APPROACH DEMO")
    print("="*70)
    print()
    print("Target: Block at center-bottom of frame (320, 420)")
    print("Method: Strafe to center, drive forward until close")
    print()
    
    approach = BlockApproach()
    
    mv = approach.board.get_battery()
    if mv:
        print(f"Battery: {mv/1000:.2f}V")
        print()
    
    try:
        print("Approaching nearest block...")
        print()
        
        result = approach.approach(callback=print_callback)
        
        print()
        print(f"Result: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"  Color: {result['color']}")
        print(f"  Position: ({result['final_x']}, {result['final_y']})")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Reason: {result['reason']}")
    
    except KeyboardInterrupt:
        print("\nStopped")
    
    finally:
        approach.cleanup()
