#!/usr/bin/env python3
"""
Bump and Grab - Simple block pickup using forward camera only

Strategy:
  1. SCAN:   Rotate to face a colored block (forward camera)
  2. CENTER: Strafe/rotate to center block in frame
  3. DRIVE:  Drive forward slowly, watching block grow in frame
  4. DETECT CONTACT: When block vanishes from view = we've reached it
  5. BACKUP: Back up ~1 inch (create gripper clearance)
  6. GRAB:   Lower arm (gripper open), close gripper, lift

Why this works:
  - No depth estimation needed (contact = block vanished from view)
  - Bumping the block squares it up for clean grip
  - Forward camera only (no camera-down transition needed!)
  - Works at any battery voltage

Usage (new — with Robot):
    from robot import Robot
    from skills.bump_grab import bump_grab
    robot = Robot()
    bump_grab(robot, color='red')

Usage (standalone — backward compat):
    python3 bump_grab.py red
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from skills.block_detect import BlockDetector
from lib.arm_positions import (
    Arm, POS_CAMERA_FORWARD, POS_PICKUP_DOWN, POS_PICKUP_GRAB,
    POS_LIFT, POS_CARRY, POS_PLACE_DOWN, POS_PLACE_OPEN
)

# === CONFIG ===

ROTATION_POWER = 35
DRIVE_POWER = 35
CENTER_TOLERANCE = 80
VANISH_FRAMES = 4
BACKUP_TIME = 0.12
BACKUP_POWER = 30
FRAME_CENTER_X = 320


# === HELPERS ===

def _stop(robot):
    """Stop motors — works with Robot or raw board."""
    if hasattr(robot, 'stop'):
        robot.stop()
    else:
        robot.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def _drive(robot, fl, fr, rl, rr):
    """Set motors — works with Robot or raw board."""
    if hasattr(robot, 'drive'):
        robot.drive(fl, fr, rl, rr)
    else:
        robot.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])


def _get_board(robot):
    """Get the raw board from Robot or return board directly."""
    return robot.board if hasattr(robot, 'board') else robot


def _move_arm(board, position, duration_ms=800):
    """Move arm to position and wait."""
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)


def _get_fresh_frame(camera, flush=3):
    """Flush buffer and get clean frame. Works with Camera or cv2.VideoCapture."""
    if hasattr(camera, 'get_frame'):
        return camera.get_frame(flush=flush)
    # Raw cv2.VideoCapture
    for _ in range(flush):
        camera.read()
    ret, frame = camera.read()
    return frame if ret else None


def gentle_place(robot):
    """Place block gently on the floor.
    
    Args:
        robot: Robot instance or raw board
    """
    board = _get_board(robot)
    print("  Placing block gently...")
    _move_arm(board, POS_PLACE_DOWN, 1200)
    time.sleep(0.3)
    _move_arm(board, POS_PLACE_OPEN, 500)
    time.sleep(0.3)
    _move_arm(board, POS_CAMERA_FORWARD, 1000)
    print("    PLACED!")


# === PHASE 1: SCAN ===

def scan_and_face(robot, camera, detector, color=None):
    """
    Rotate to find a block and face it.
    
    Args:
        robot: Robot instance or raw board
        camera: Camera instance or cv2.VideoCapture
        detector: BlockDetector instance
        color: Target color or None for any
    
    Returns:
        True if facing a block within CENTER_TOLERANCE.
    """
    board = _get_board(robot)
    print("PHASE 1: Scan and face block")
    print("-" * 40)
    
    _move_arm(board, POS_CAMERA_FORWARD, 800)
    time.sleep(0.5)
    
    for step in range(24):
        frame = _get_fresh_frame(camera)
        if frame is None:
            continue
        
        colors = [color] if color else None
        blocks = detector.detect(frame, colors=colors)
        
        if blocks:
            b = blocks[0]
            offset = b.offset_from_center
            
            print("  Step %d: %s at %dcm, offset=%+dpx" % (
                step, b.color, b.estimated_distance_mm / 10, offset))
            
            if abs(offset) < CENTER_TOLERANCE:
                print("  FACING BLOCK")
                return True
            
            d = 1 if offset > 0 else -1
            _drive(robot, ROTATION_POWER * d, -ROTATION_POWER * d,
                   ROTATION_POWER * d, -ROTATION_POWER * d)
            
            duration = 0.08 if abs(offset) < 150 else 0.15
            time.sleep(duration)
            _stop(robot)
            time.sleep(0.3)
        else:
            _drive(robot, ROTATION_POWER, -ROTATION_POWER,
                   ROTATION_POWER, -ROTATION_POWER)
            time.sleep(0.25)
            _stop(robot)
            time.sleep(0.3)
    
    print("  No block found")
    return False


# === PHASE 2: DRIVE TO CONTACT ===

def drive_to_contact(robot, camera, detector, color=None):
    """
    Drive forward toward block using timed drive.
    
    Args:
        robot: Robot instance or raw board
        camera: Camera instance or cv2.VideoCapture
        detector: BlockDetector
        color: Target color or None
    
    Returns:
        True if driven to estimated block position.
    """
    board = _get_board(robot)
    print("PHASE 2: Drive to contact")
    print("-" * 40)
    
    # Try sonar for starting distance
    start_dist = 2000  # Default 200cm
    try:
        if hasattr(robot, 'sonar') and robot.sonar:
            d = robot.sonar.get_distance()
            if d and d < 5000:
                start_dist = d
        else:
            from lib.sonar import Sonar
            sonar = Sonar()
            time.sleep(0.3)
            d = sonar.get_distance()
            if d and d < 5000:
                start_dist = d
    except Exception:
        pass
    
    print("  Sonar start: %.0fcm from wall" % (start_dist / 10.0))
    
    # Estimate block distance from camera
    frame = _get_fresh_frame(camera)
    target_travel = 30
    
    if frame is not None:
        colors = [color] if color else None
        blocks = detector.detect(frame, colors=colors)
        if blocks:
            est_dist = blocks[0].estimated_distance_mm / 10.0
            target_travel = est_dist + 5
            print("  Block estimated at %.0fcm, target travel: %.0fcm" % (est_dist, target_travel))
    
    drive_time = (target_travel + 5) / 15.0
    drive_time = max(0.5, min(drive_time, 5.0))
    
    DRIFT_COMPENSATION = 3
    print("  Driving straight %.1fs (est %.0fcm)..." % (drive_time, target_travel))
    _drive(robot, DRIVE_POWER, DRIVE_POWER - DRIFT_COMPENSATION,
           DRIVE_POWER, DRIVE_POWER - DRIFT_COMPENSATION)
    time.sleep(drive_time)
    _stop(robot)
    print("  CONTACT (timed drive)")
    return True


# === PHASE 3: BACKUP AND GRAB ===

def backup_and_grab(robot):
    """
    Back up slightly, then lower arm, close gripper, lift.
    
    Args:
        robot: Robot instance or raw board
    """
    board = _get_board(robot)
    print("PHASE 3: Backup and grab")
    print("-" * 40)
    
    print("  Tiny backup...")
    _drive(robot, -BACKUP_POWER, -BACKUP_POWER, -BACKUP_POWER, -BACKUP_POWER)
    time.sleep(0.12)
    _stop(robot)
    time.sleep(0.3)
    
    print("  Lowering arm (gripper open)...")
    _move_arm(board, POS_PICKUP_DOWN, 1000)
    time.sleep(0.5)
    
    # Visual alignment
    print("  Visual alignment...")
    # Use robot's camera if available, otherwise open new one
    own_camera = False
    if hasattr(robot, 'camera') and robot.camera and robot.camera.is_open():
        cam = robot.camera
    else:
        cam = cv2.VideoCapture(0)
        time.sleep(0.5)
        own_camera = True
    
    detector = BlockDetector()
    for adjust in range(8):
        frame = _get_fresh_frame(cam)
        if frame is None:
            break
        
        blocks = detector.detect(frame)
        if blocks:
            b = blocks[0]
            offset = b.offset_from_center
            print("    Block at (%d,%d) offset=%+d" % (b.center_x, b.center_y, offset))
            
            if abs(offset) < 80:
                print("    Aligned!")
                break
            
            d = 1 if offset > 0 else -1
            rot_time = max(0.05, min(0.15, abs(offset) / 2000.0))
            _drive(robot, 35 * d, -35 * d, 35 * d, -35 * d)
            time.sleep(rot_time)
            _stop(robot)
            time.sleep(0.3)
        else:
            print("    No block visible")
            break
    
    if own_camera:
        cam.release()
    
    print("  Grabbing...")
    _move_arm(board, POS_PICKUP_GRAB, 400)
    time.sleep(0.5)
    
    print("  Lifting...")
    _move_arm(board, POS_LIFT, 1000)
    time.sleep(0.5)
    
    print("  Carry position...")
    _move_arm(board, POS_CARRY, 800)
    
    print("  GRAB COMPLETE")


# === MAIN ENTRY POINTS ===

def bump_grab(robot_or_color=None, color=None):
    """
    Full bump-and-grab pickup cycle.
    
    Accepts either:
        bump_grab(robot, color='red')   # New Robot-based API
        bump_grab(color='red')          # Legacy standalone
        bump_grab('red')                # Legacy positional
    
    Returns:
        True if block grabbed, False if failed.
    """
    # Detect calling convention
    from robot import Robot as RobotClass
    
    if isinstance(robot_or_color, RobotClass):
        return _bump_grab_robot(robot_or_color, color)
    elif isinstance(robot_or_color, str):
        return _bump_grab_standalone(robot_or_color)
    else:
        return _bump_grab_standalone(color)


def _bump_grab_robot(robot, color=None):
    """Bump-and-grab using Robot instance (no internal hardware creation)."""
    print("=" * 60)
    print("BUMP AND GRAB")
    print("Platform: %s" % robot.platform)
    print("Target: %s" % (color or "any color"))
    print("=" * 60)
    print()
    
    if not robot.battery_ok:
        print("BATTERY TOO LOW")
        return False
    print("Battery: %.2fV" % robot.battery)
    print()
    
    detector = BlockDetector()
    
    try:
        if not scan_and_face(robot, robot.camera, detector, color):
            print("\nFAILED: No block found")
            return False
        print()
        
        if not drive_to_contact(robot, robot.camera, detector, color):
            print("\nFAILED: Could not reach block")
            return False
        print()
        
        backup_and_grab(robot)
        
        print()
        print("=" * 60)
        print("SUCCESS - Check if robot is holding a block!")
        print("=" * 60)
        return True
    
    except KeyboardInterrupt:
        print("\nInterrupted")
        return False
    except Exception as e:
        print("\nERROR: %s" % e)
        import traceback
        traceback.print_exc()
        return False
    finally:
        _stop(robot)


def _bump_grab_standalone(color=None):
    """Legacy standalone bump-and-grab (creates own hardware)."""
    print("=" * 60)
    print("BUMP AND GRAB (standalone)")
    print("Platform: %s" % PLATFORM)
    print("Target: %s" % (color or "any color"))
    print("=" * 60)
    print()
    
    board = get_board()
    
    time.sleep(1)
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        v = mv / 1000.0
        print("Battery: %.2fV" % v)
        battery_min = 7.0 if PLATFORM == 'pi4' else 8.1
        if v < battery_min:
            print("BATTERY TOO LOW")
            return False
    print()
    
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)
    
    detector = BlockDetector()
    
    try:
        if not scan_and_face(board, camera, detector, color):
            print("\nFAILED: No block found")
            return False
        print()
        
        if not drive_to_contact(board, camera, detector, color):
            print("\nFAILED: Could not reach block")
            return False
        print()
        
        camera.release()
        backup_and_grab(board)
        
        print()
        print("=" * 60)
        print("SUCCESS - Check if robot is holding a block!")
        print("=" * 60)
        return True
    
    except KeyboardInterrupt:
        print("\nInterrupted")
        return False
    except Exception as e:
        print("\nERROR: %s" % e)
        import traceback
        traceback.print_exc()
        return False
    finally:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        try:
            camera.release()
        except:
            pass


if __name__ == '__main__':
    color = None
    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 bump_grab.py [red|blue|yellow]")
            sys.exit(1)
    
    bump_grab(color)
