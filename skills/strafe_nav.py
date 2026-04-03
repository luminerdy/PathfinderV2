#!/usr/bin/env python3
"""
Strafe Navigation -- Mecanum-Based AprilTag Navigation

Uses mecanum wheels properly: simultaneous strafe + forward to
approach targets smoothly instead of stop-rotate-drive.

Inspired by PathfinderBot's pf_follow_me.py:
- Proportional control with deadbands
- Simultaneous lateral + forward movement
- Min/max speed clamps to overcome friction
- Sonar safety integration

Usage (with Robot):
    from robot import Robot
    from skills.strafe_nav import StrafeNavigator
    robot = Robot()
    nav = StrafeNavigator(robot)
    result = nav.navigate_to_tag(target_id=580)

Usage (standalone):
    python3 strafe_nav.py
"""

import cv2
import math
import time

from pupil_apriltags import Detector
from lib.board import get_board, PLATFORM


class StrafeNavigator:
    """
    Navigate to AprilTags using mecanum strafe + forward simultaneously.

    Instead of: rotate to center -> drive forward -> repeat
    Does: strafe to center WHILE driving forward (smooth, fast)
    """

    # Camera parameters (estimated, TODO: calibrate properly)
    CAMERA_PARAMS = [500, 500, 320, 240]  # fx, fy, cx, cy
    TAG_SIZE = 0.254  # meters (10-inch tags)

    # Proportional control gains
    Kx = 120        # Lateral gain
    Kz = 100        # Forward gain

    # Deadbands
    CENTER_TOLERANCE = 0.03   # meters
    DIST_TOLERANCE = 0.05     # meters

    # Speed limits (motor duty)
    MAX_SPEED = 35
    MIN_SPEED = 28

    # Target distance
    TARGET_DISTANCE = 0.55    # meters

    # Sonar safety
    SONAR_STOP = 15      # cm
    SONAR_SLOW = 30      # cm
    SONAR_BACKUP = 50    # cm

    # Tag loss timeout
    TAG_TIMEOUT = 1.5    # seconds

    # Angle limits for strafe
    MAX_STRAFE_ANGLE = 20  # degrees

    def __init__(self, robot=None):
        """
        Initialize navigator.

        Args:
            robot: Robot instance (preferred) or None for standalone
        """
        self._robot = robot
        self._own_camera = False
        self._own_sonar = False

        if robot and hasattr(robot, 'board'):
            self.board = robot.board
        else:
            self.board = get_board()

        # Sonar
        self.sonar = None
        if robot and hasattr(robot, 'sonar') and robot.sonar:
            self.sonar = robot.sonar
        else:
            try:
                from lib.sonar import Sonar
                self.sonar = Sonar()
                self._own_sonar = True
            except Exception:
                pass

        # Camera
        self.camera = None
        if robot and hasattr(robot, 'camera') and robot.camera:
            self._camera_obj = robot.camera
        else:
            self._camera_obj = None

        # Use robot's camera params if calibrated
        if self._camera_obj and hasattr(self._camera_obj, 'camera_params'):
            self.CAMERA_PARAMS = list(self._camera_obj.camera_params)

        self.detector = Detector(families='tag36h11')
        self._last_tag_time = 0

    def _open_camera(self):
        """Open camera if not already open."""
        if self._camera_obj and self._camera_obj.is_open():
            self.camera = self._camera_obj
            return

        if self.camera is None or (hasattr(self.camera, 'isOpened') and not self.camera.isOpened()):
            self.camera = cv2.VideoCapture(0)
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            time.sleep(1.0)
            self._own_camera = True

    def _close_camera(self):
        """Release camera only if we opened it."""
        if self._own_camera and self.camera and hasattr(self.camera, 'release'):
            self.camera.release()
            self.camera = None

    def _stop(self):
        """Stop all motors."""
        if self._robot and hasattr(self._robot, 'stop'):
            self._robot.stop()
        else:
            self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

    def _drive(self, strafe, forward):
        """Drive with mecanum: simultaneous strafe + forward."""
        fl = int(forward + strafe)
        fr = int(forward - strafe)
        rl = int(forward - strafe)
        rr = int(forward + strafe)

        if self._robot and hasattr(self._robot, 'drive'):
            self._robot.drive(fl, fr, rl, rr)
        else:
            self.board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])

    def _get_sonar_distance(self):
        """Get sonar distance in cm, or None."""
        if self.sonar is None:
            return None
        d = self.sonar.get_distance()
        if d is None:
            return None
        return d / 10.0 if d > 100 else d  # Handle mm vs cm

    def _get_frame(self):
        """Get a frame from whichever camera source we have."""
        if self._camera_obj and hasattr(self._camera_obj, 'get_raw_frame'):
            return self._camera_obj.get_raw_frame()
        if self.camera:
            ret, frame = self.camera.read()
            return frame if ret else None
        return None

    def _clamp_speed(self, speed):
        """Clamp speed to valid range with minimum threshold."""
        if abs(speed) < 1:
            return 0
        sign = 1 if speed > 0 else -1
        magnitude = min(max(abs(speed), self.MIN_SPEED), self.MAX_SPEED)
        return sign * magnitude

    def _detect_tags(self, frame, target_id=None):
        """Detect AprilTags and return closest or specific tag with pose."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=self.CAMERA_PARAMS,
            tag_size=self.TAG_SIZE
        )

        if not tags:
            return None, 0, 0, 0, 0, 0

        if target_id is not None:
            tags = [t for t in tags if t.tag_id == target_id]
            if not tags:
                return None, 0, 0, 0, 0, 0

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

        x = float(best.pose_t[0][0])
        y = float(best.pose_t[1][0])
        z = float(best.pose_t[2][0])
        dist = math.sqrt(x*x + z*z)
        angle = math.degrees(math.atan2(x, z))

        return best.tag_id, x, y, z, dist, angle

    def check_battery(self, min_voltage=None):
        """Check battery. Returns (voltage, ok)."""
        if self._robot and hasattr(self._robot, 'battery'):
            v = self._robot.battery
            if v is None:
                return 0, False
            if min_voltage is None:
                min_voltage = self._robot.battery_min
            return v, v >= min_voltage

        if min_voltage is None:
            min_voltage = 7.0 if PLATFORM == 'pi4' else 8.1
        mv = self.board.get_battery()
        if not mv:
            return 0, False
        v = mv / 1000.0
        return v, v >= min_voltage

    def navigate_to_tag(self, target_id=None, target_distance=None,
                        timeout=30, callback=None):
        """
        Navigate to an AprilTag using strafe + forward simultaneously.

        Args:
            target_id: Specific tag to navigate to (None = closest)
            target_distance: How close to get (meters)
            timeout: Max time in seconds
            callback: Optional function(tag_id, dist, angle, action)

        Returns:
            dict with success, tag_id, final_distance, final_angle, iterations, reason
        """
        if target_distance is None:
            target_distance = self.TARGET_DISTANCE

        voltage, ok = self.check_battery()
        if not ok:
            return {
                'success': False, 'tag_id': None,
                'final_distance': 0, 'final_angle': 0,
                'iterations': 0, 'reason': 'battery_low (%.2fV)' % voltage
            }

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

                sonar_dist = self._get_sonar_distance()
                if sonar_dist and 0 < sonar_dist < self.SONAR_STOP:
                    self._stop()
                    return {
                        'success': False, 'tag_id': last_tag_id,
                        'final_distance': last_dist, 'final_angle': last_angle,
                        'iterations': iteration, 'reason': 'sonar_stop (%.0fcm)' % sonar_dist
                    }

                frame = self._get_frame()
                if frame is None:
                    continue

                tag_id, x, y, z, dist, angle = self._detect_tags(frame, target_id)

                if tag_id is None:
                    if time.time() - self._last_tag_time > self.TAG_TIMEOUT:
                        self._stop()
                        return {
                            'success': False, 'tag_id': last_tag_id,
                            'final_distance': last_dist, 'final_angle': last_angle,
                            'iterations': iteration, 'reason': 'no_tag'
                        }
                    self._stop()
                    continue

                self._last_tag_time = time.time()
                last_tag_id = tag_id
                last_dist = dist
                last_angle = angle

                error_x = x
                error_z = z - target_distance

                if abs(angle) > self.MAX_STRAFE_ANGLE:
                    rot_speed = self.MIN_SPEED if angle > 0 else -self.MIN_SPEED
                    self.board.set_motor_duty([
                        (1, rot_speed), (2, -rot_speed),
                        (3, rot_speed), (4, -rot_speed)
                    ])
                    time.sleep(0.1)
                    continue

                strafe = error_x * self.Kx if abs(error_x) > self.CENTER_TOLERANCE else 0
                forward = error_z * self.Kz if abs(error_z) > self.DIST_TOLERANCE else 0

                if sonar_dist and 0 < sonar_dist < self.SONAR_SLOW:
                    forward = min(forward, self.MIN_SPEED)

                strafe = self._clamp_speed(strafe)
                forward = self._clamp_speed(forward)

                if strafe == 0 and forward == 0:
                    self._stop()
                    if callback:
                        callback(tag_id, dist, angle, 'REACHED')
                    return {
                        'success': True, 'tag_id': tag_id,
                        'final_distance': dist, 'final_angle': angle,
                        'iterations': iteration, 'reason': 'reached'
                    }

                self._drive(strafe, forward)

                if callback and iteration % 10 == 0:
                    parts = []
                    if forward != 0: parts.append('fwd=%.0f' % forward)
                    if strafe != 0: parts.append('strafe=%.0f' % strafe)
                    callback(tag_id, dist, angle, ' '.join(parts))

                time.sleep(0.03)

            self._stop()
            return {
                'success': False, 'tag_id': last_tag_id,
                'final_distance': last_dist, 'final_angle': last_angle,
                'iterations': iteration, 'reason': 'timeout'
            }

        except KeyboardInterrupt:
            self._stop()
            return {
                'success': False, 'tag_id': last_tag_id,
                'final_distance': last_dist, 'final_angle': last_angle,
                'iterations': iteration, 'reason': 'interrupted'
            }
        except Exception:
            self._stop()
            raise

    def search_and_navigate(self, target_id=None, search_timeout=15,
                            nav_timeout=30, callback=None):
        """Search for a tag by rotating, then navigate to it."""
        self._open_camera()

        sonar_dist = self._get_sonar_distance()
        if sonar_dist and 0 < sonar_dist < self.SONAR_BACKUP:
            if callback:
                callback(0, 0, 0, 'BACKUP (sonar %.0fcm)' % sonar_dist)
            self.board.set_motor_duty([(1, -30), (2, -30), (3, -30), (4, -30)])
            time.sleep(1.0)
            self._stop()
            time.sleep(0.3)

        start = time.time()
        while time.time() - start < search_timeout:
            frame = self._get_frame()
            if frame is None:
                continue

            tag_id, x, y, z, dist, angle = self._detect_tags(frame, target_id)

            if tag_id is not None:
                self._stop()
                time.sleep(0.2)
                if callback:
                    callback(tag_id, dist, angle, 'FOUND at %.2fm' % dist)
                return self.navigate_to_tag(
                    target_id=tag_id, timeout=nav_timeout, callback=callback
                )

            self.board.set_motor_duty([(1, 30), (2, -30), (3, 30), (4, -30)])
            time.sleep(0.15)
            self._stop()
            time.sleep(0.1)

        self._stop()
        return {
            'success': False, 'tag_id': None,
            'final_distance': 0, 'final_angle': 0,
            'iterations': 0, 'reason': 'search_timeout'
        }

    def tour(self, tag_sequence, target_distance=None, callback=None):
        """Visit a sequence of tags. Retries failed tags once."""
        results = []
        for i, tag_id in enumerate(tag_sequence):
            if callback:
                callback(tag_id, 0, 0, 'SEARCHING (%d/%d)' % (i+1, len(tag_sequence)))

            result = self.search_and_navigate(
                target_id=tag_id, search_timeout=15, callback=callback
            )

            if not result['success']:
                if callback:
                    callback(tag_id, 0, 0, 'RETRY (%d/%d)' % (i+1, len(tag_sequence)))
                self.board.set_motor_duty([(1, -30), (2, -30), (3, -30), (4, -30)])
                time.sleep(0.8)
                self._stop()
                time.sleep(0.3)
                result = self.search_and_navigate(
                    target_id=tag_id, search_timeout=15, callback=callback
                )

            results.append(result)
            if callback:
                status = 'OK' if result['success'] else result['reason']
                callback(tag_id, result['final_distance'],
                         result['final_angle'], 'DONE: %s' % status)
            time.sleep(0.3)
        return results

    def cleanup(self):
        """Release resources."""
        self._stop()
        self._close_camera()


def print_callback(tag_id, dist, angle, action):
    """Simple console callback."""
    print("  Tag %s: %.2fm, %+.1fdeg - %s" % (tag_id, dist, angle, action))


if __name__ == '__main__':
    print("=" * 70)
    print("STRAFE NAVIGATION DEMO")
    print("=" * 70)
    print()

    # Try Robot first, fall back to standalone
    try:
        from robot import Robot
        robot = Robot(enable_camera=True)
        nav = StrafeNavigator(robot)
        print("Using Robot instance")
    except Exception:
        nav = StrafeNavigator()
        robot = None
        print("Standalone mode")

    try:
        voltage, ok = nav.check_battery()
        print("Battery: %.2fV %s" % (voltage, "" if ok else "(LOW)"))
        print()
        print("Searching for any tag...")
        print()

        result = nav.search_and_navigate(callback=print_callback)

        print()
        print("=" * 70)
        print("Result: %s" % ('SUCCESS' if result['success'] else 'FAILED'))
        print("  Tag: %s" % result['tag_id'])
        print("  Distance: %.2fm" % result['final_distance'])
        print("  Angle: %+.1fdeg" % result['final_angle'])
        print("  Reason: %s" % result['reason'])
        print("=" * 70)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        nav.cleanup()
        if robot:
            robot.shutdown()
