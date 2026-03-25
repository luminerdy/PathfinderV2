#!/usr/bin/env python3
"""
Strafe Navigation — Mecanum-Based AprilTag Navigation

Uses mecanum wheels properly: simultaneous strafe + forward to
approach targets smoothly instead of stop-rotate-drive.

Inspired by PathfinderBot's pf_follow_me.py:
- Proportional control with deadbands
- Simultaneous lateral + forward movement
- Min/max speed clamps to overcome friction
- Sonar safety integration

This is how mecanum robots SHOULD navigate.
"""

import cv2
import math
import time
from pupil_apriltags import Detector
from lib.board_protocol import BoardController
from hardware.sonar import Sonar


class StrafeNavigator:
    """
    Navigate to AprilTags using mecanum strafe + forward simultaneously.
    
    Instead of: rotate to center → drive forward → repeat
    Does: strafe to center WHILE driving forward (smooth, fast)
    """
    
    # Camera parameters (estimated, TODO: calibrate properly)
    CAMERA_PARAMS = [500, 500, 320, 240]  # fx, fy, cx, cy
    TAG_SIZE = 0.254  # meters (10-inch tags)
    
    # Proportional control gains
    Kx = 150        # Lateral gain (strafe speed per meter of lateral error)
    Kz = 120        # Forward gain (forward speed per meter of distance error)
    
    # Deadbands — don't correct if error is smaller than this
    CENTER_TOLERANCE = 0.03   # meters (~1.2 inches lateral)
    DIST_TOLERANCE = 0.05     # meters (~2 inches distance)
    
    # Speed limits (motor duty)
    MAX_SPEED = 35      # Maximum motor power
    MIN_SPEED = 28      # Minimum to overcome friction (calibrated)
    
    # Target distance — how close to get to the tag
    TARGET_DISTANCE = 0.50    # meters (~20 inches, arm reach zone)
    
    # Sonar safety
    SONAR_STOP = 15      # cm — emergency stop
    SONAR_SLOW = 30      # cm — reduce speed
    
    # Tag loss timeout
    TAG_TIMEOUT = 1.5    # seconds — stop if no tag for this long
    
    def __init__(self, board=None, sonar=None):
        self.board = board or BoardController()
        self.sonar = sonar or Sonar()
        self.detector = Detector(families='tag36h11')
        self.camera = None
        self._last_tag_time = 0
    
    def _open_camera(self):
        """Open camera if not already open"""
        if self.camera is None or not self.camera.isOpened():
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            time.sleep(1.0)
    
    def _close_camera(self):
        """Release camera"""
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
    
    def _stop(self):
        """Stop all motors"""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
    def _drive(self, strafe, forward):
        """
        Drive with mecanum: simultaneous strafe + forward.
        
        Uses the correct mecanum wheel equations:
          FL = forward + strafe
          FR = forward - strafe  
          RL = forward - strafe
          RR = forward + strafe
        
        Args:
            strafe: lateral speed (positive = right, negative = left)
            forward: forward speed (positive = forward)
        """
        fl = int(forward + strafe)
        fr = int(forward - strafe)
        rl = int(forward - strafe)
        rr = int(forward + strafe)
        
        self.board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])
    
    def _clamp_speed(self, speed):
        """
        Clamp speed to valid range.
        If speed is non-zero, ensure it's at least MIN_SPEED (overcome friction).
        """
        if abs(speed) < 1:
            return 0
        
        sign = 1 if speed > 0 else -1
        magnitude = abs(speed)
        
        if magnitude < self.MIN_SPEED:
            magnitude = self.MIN_SPEED
        elif magnitude > self.MAX_SPEED:
            magnitude = self.MAX_SPEED
        
        return sign * magnitude
    
    def _detect_tags(self, frame, target_id=None):
        """
        Detect AprilTags and return closest (or specific) tag with pose.
        
        Args:
            frame: BGR image
            target_id: If set, only return this tag ID
            
        Returns:
            (tag_id, x, y, z, distance, angle) or (None, ...) if not found
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=self.CAMERA_PARAMS,
            tag_size=self.TAG_SIZE
        )
        
        if not tags:
            return None, 0, 0, 0, 0, 0
        
        # Filter by target ID if specified
        if target_id is not None:
            tags = [t for t in tags if t.tag_id == target_id]
            if not tags:
                return None, 0, 0, 0, 0, 0
        
        # Pick closest tag
        best = None
        best_dist = float('inf')
        
        for tag in tags:
            if tag.pose_t is not None:
                x = float(tag.pose_t[0][0])
                z = float(tag.pose_t[2][0])
                dist = math.sqrt(x*x + z*z)
                if dist < best_dist:
                    best_dist = dist
                    best = tag
        
        if best is None or best.pose_t is None:
            return None, 0, 0, 0, 0, 0
        
        x = float(best.pose_t[0][0])   # lateral (positive = right)
        y = float(best.pose_t[1][0])   # vertical
        z = float(best.pose_t[2][0])   # forward distance
        dist = math.sqrt(x*x + z*z)
        angle = math.degrees(math.atan2(x, z))
        
        return best.tag_id, x, y, z, dist, angle
    
    def navigate_to_tag(self, target_id=None, target_distance=None, 
                        timeout=30, callback=None):
        """
        Navigate to an AprilTag using strafe + forward simultaneously.
        
        Args:
            target_id: Specific tag to navigate to (None = closest)
            target_distance: How close to get (meters, default self.TARGET_DISTANCE)
            timeout: Max time in seconds
            callback: Optional function called each frame with (tag_id, dist, angle, action)
            
        Returns:
            dict with result info:
            {
                'success': bool,
                'tag_id': int or None,
                'final_distance': float,
                'final_angle': float,
                'iterations': int,
                'reason': str  ('reached', 'timeout', 'sonar_stop', 'no_tag')
            }
        """
        if target_distance is None:
            target_distance = self.TARGET_DISTANCE
        
        self._open_camera()
        self._last_tag_time = time.time()
        
        start_time = time.time()
        iteration = 0
        last_tag_id = None
        last_dist = 0
        last_angle = 0
        
        try:
            while time.time() - start_time < timeout:
                iteration += 1
                
                # Sonar safety check
                sonar_dist = self.sonar.get_distance()
                if sonar_dist and 0 < sonar_dist < self.SONAR_STOP:
                    self._stop()
                    return {
                        'success': False,
                        'tag_id': last_tag_id,
                        'final_distance': last_dist,
                        'final_angle': last_angle,
                        'iterations': iteration,
                        'reason': f'sonar_stop ({sonar_dist:.0f}cm)'
                    }
                
                # Get frame
                ret, frame = self.camera.read()
                if not ret:
                    continue
                
                # Detect tag
                tag_id, x, y, z, dist, angle = self._detect_tags(frame, target_id)
                
                if tag_id is None:
                    # No tag seen
                    if time.time() - self._last_tag_time > self.TAG_TIMEOUT:
                        self._stop()
                        return {
                            'success': False,
                            'tag_id': last_tag_id,
                            'final_distance': last_dist,
                            'final_angle': last_angle,
                            'iterations': iteration,
                            'reason': 'no_tag'
                        }
                    # Brief loss — keep coasting or stop
                    self._stop()
                    continue
                
                # Tag found — update tracking
                self._last_tag_time = time.time()
                last_tag_id = tag_id
                last_dist = dist
                last_angle = angle
                
                # Calculate errors
                error_x = x             # lateral error (meters, positive = tag is right)
                error_z = z - target_distance   # distance error (positive = too far)
                
                # Calculate motor commands with proportional control + deadbands
                if abs(error_x) > self.CENTER_TOLERANCE:
                    strafe = error_x * self.Kx
                else:
                    strafe = 0
                
                if abs(error_z) > self.DIST_TOLERANCE:
                    forward = error_z * self.Kz
                else:
                    forward = 0
                
                # Sonar speed limit
                if sonar_dist and 0 < sonar_dist < self.SONAR_SLOW:
                    forward = min(forward, self.MIN_SPEED)
                
                # Clamp speeds
                strafe = self._clamp_speed(strafe)
                forward = self._clamp_speed(forward)
                
                # Check if we've arrived
                if strafe == 0 and forward == 0:
                    self._stop()
                    
                    # Callback
                    if callback:
                        callback(tag_id, dist, angle, 'REACHED')
                    
                    return {
                        'success': True,
                        'tag_id': tag_id,
                        'final_distance': dist,
                        'final_angle': angle,
                        'iterations': iteration,
                        'reason': 'reached'
                    }
                
                # Drive
                self._drive(strafe, forward)
                
                # Callback for status reporting
                if callback and iteration % 10 == 0:
                    action = []
                    if forward != 0:
                        action.append(f'fwd={forward:.0f}')
                    if strafe != 0:
                        action.append(f'strafe={strafe:.0f}')
                    callback(tag_id, dist, angle, ' '.join(action))
                
                time.sleep(0.03)  # ~30 fps loop
            
            # Timeout
            self._stop()
            return {
                'success': False,
                'tag_id': last_tag_id,
                'final_distance': last_dist,
                'final_angle': last_angle,
                'iterations': iteration,
                'reason': 'timeout'
            }
        
        except KeyboardInterrupt:
            self._stop()
            return {
                'success': False,
                'tag_id': last_tag_id,
                'final_distance': last_dist,
                'final_angle': last_angle,
                'iterations': iteration,
                'reason': 'interrupted'
            }
        
        except Exception as e:
            self._stop()
            raise
    
    def search_and_navigate(self, target_id=None, search_timeout=10, 
                            nav_timeout=30, callback=None):
        """
        Search for a tag by rotating, then navigate to it.
        
        Args:
            target_id: Specific tag to find (None = any tag)
            search_timeout: Max seconds to search
            nav_timeout: Max seconds to navigate once found
            callback: Status callback
            
        Returns:
            Same dict as navigate_to_tag
        """
        self._open_camera()
        
        # Phase 1: Search by rotating
        start = time.time()
        
        while time.time() - start < search_timeout:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            tag_id, x, y, z, dist, angle = self._detect_tags(frame, target_id)
            
            if tag_id is not None:
                # Found it — stop rotation, start navigation
                self._stop()
                time.sleep(0.2)
                
                if callback:
                    callback(tag_id, dist, angle, f'FOUND at {dist:.2f}m')
                
                return self.navigate_to_tag(
                    target_id=tag_id,
                    timeout=nav_timeout,
                    callback=callback
                )
            
            # Keep searching — rotate
            self.board.set_motor_duty([(1, 28), (2, -28), (3, 28), (4, -28)])
            time.sleep(0.1)
        
        # Search failed
        self._stop()
        return {
            'success': False,
            'tag_id': None,
            'final_distance': 0,
            'final_angle': 0,
            'iterations': 0,
            'reason': 'search_timeout'
        }
    
    def tour(self, tag_sequence, target_distance=None, callback=None):
        """
        Visit a sequence of tags.
        
        Args:
            tag_sequence: List of tag IDs to visit in order
            target_distance: How close to get to each tag
            callback: Status callback
            
        Returns:
            List of result dicts (one per tag)
        """
        results = []
        
        for i, tag_id in enumerate(tag_sequence):
            if callback:
                callback(tag_id, 0, 0, f'SEARCHING ({i+1}/{len(tag_sequence)})')
            
            result = self.search_and_navigate(
                target_id=tag_id,
                callback=callback
            )
            
            results.append(result)
            
            if callback:
                status = 'OK' if result['success'] else result['reason']
                callback(tag_id, result['final_distance'], 
                        result['final_angle'], f'DONE: {status}')
            
            # Brief pause between tags
            time.sleep(0.3)
        
        return results
    
    def cleanup(self):
        """Release resources"""
        self._stop()
        self._close_camera()


def print_callback(tag_id, dist, angle, action):
    """Simple console callback"""
    print(f"  Tag {tag_id}: {dist:.2f}m, {angle:+.1f}deg - {action}")


if __name__ == '__main__':
    """Demo: Navigate to nearest tag using strafe navigation"""
    
    print("="*70)
    print("STRAFE NAVIGATION DEMO")
    print("="*70)
    print()
    print("Uses mecanum wheels properly:")
    print("  - Simultaneous strafe + forward")
    print("  - Proportional control with deadbands")
    print("  - Min/max speed clamps")
    print("  - Sonar safety")
    print()
    
    nav = StrafeNavigator()
    
    try:
        # Check battery
        mv = nav.board.get_battery()
        if mv:
            v = mv / 1000.0
            print(f"Battery: {v:.2f}V")
            if v < 8.0:
                print("WARNING: Battery low, may affect performance")
            print()
        
        print("Searching for any tag and navigating to it...")
        print()
        
        result = nav.search_and_navigate(callback=print_callback)
        
        print()
        print("="*70)
        print(f"Result: {'SUCCESS' if result['success'] else 'FAILED'}")
        print(f"  Tag: {result['tag_id']}")
        print(f"  Distance: {result['final_distance']:.2f}m")
        print(f"  Angle: {result['final_angle']:+.1f}deg")
        print(f"  Iterations: {result['iterations']}")
        print(f"  Reason: {result['reason']}")
        print("="*70)
    
    except KeyboardInterrupt:
        print("\nStopped")
    
    finally:
        nav.cleanup()
