#!/usr/bin/env python3
"""
Cart Push - Load blocks into a shopping cart and push it to a basket

Strategy:
  1. Pick up blocks and drop into cart (arm forward + elevated)
  2. Push cart toward target basket using AprilTag navigation
  3. Robot drives forward, cart slides ahead

Usage (with Robot):
    from robot import Robot
    from skills.cart_push import cart_load, cart_push, cart_full
    robot = Robot()
    cart_load(robot, count=3, color='red')
    cart_push(robot, tag_id=580)

Usage (standalone):
    python3 cart_push.py load 3 red
    python3 cart_push.py push 580
    python3 cart_push.py full 580 3 red
    python3 cart_push.py --test-load

SAFETY: Robot will drive and move arm! Clear workspace.

== CALIBRATION NEEDED ==
POS_OVER_CART positions need tuning with actual cart.
Run with --test-load to calibrate.
"""

import sys
import os
import time
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from lib.arm_positions import Arm, POS_CAMERA_FORWARD
from skills.block_detect import BlockDetector

# === CONFIG ===

PUSH_POWER = 40
ROTATION_POWER = 35

# Arm position to drop block into cart (in front of robot)
# CALIBRATE with --test-load
POS_OVER_CART = [(1, 1475), (3, 800), (4, 2100), (5, 1200), (6, 1500)]
POS_DROP_CART = [(1, 2500), (3, 800), (4, 2100), (5, 1200), (6, 1500)]

TAG_CENTER_TOLERANCE = 100
TAG_AREA_TARGET = 3000


# === HELPERS ===

def _stop(robot):
    if hasattr(robot, 'stop'):
        robot.stop()
    else:
        robot.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def _drive(robot, fl, fr, rl, rr):
    if hasattr(robot, 'drive'):
        robot.drive(fl, fr, rl, rr)
    else:
        robot.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])


def _get_board(robot):
    return robot.board if hasattr(robot, 'board') else robot


def _move_arm(board, position, duration_ms=800):
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.1)


def _get_fresh_frame(camera, flush=3):
    if hasattr(camera, 'get_frame'):
        return camera.get_frame(flush=flush)
    for _ in range(flush):
        camera.read()
    ret, frame = camera.read()
    return frame if ret else None


# === LOAD INTO CART ===

def load_into_cart(robot):
    """After pickup, drop block into front cart."""
    board = _get_board(robot)
    print("  Raising arm over cart...")
    _move_arm(board, POS_OVER_CART, 1200)
    time.sleep(0.3)
    print("  Dropping block into cart...")
    _move_arm(board, POS_DROP_CART, 500)
    time.sleep(0.3)
    print("  Returning arm to forward...")
    _move_arm(board, POS_CAMERA_FORWARD, 1000)
    print("  BLOCK IN CART!")


# === PUSH TO TAG ===

def push_to_tag(robot, tag_id):
    """Push cart toward an AprilTag.
    
    Args:
        robot: Robot instance or raw board
        tag_id: AprilTag ID (e.g. 580 for red basket)
    
    Returns:
        True if reached target area.
    """
    board = _get_board(robot)
    print("PUSHING CART TO TAG %d" % tag_id)
    print("-" * 40)
    
    try:
        from pupil_apriltags import Detector
    except ImportError:
        print("  ERROR: pupil_apriltags not installed")
        return False
    
    detector = Detector(families='tag36h11')
    
    # Use robot's camera if available
    own_camera = False
    if hasattr(robot, 'camera') and robot.camera and robot.camera.is_open():
        camera = robot.camera
    else:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(1.5)
        own_camera = True
    
    _move_arm(board, POS_CAMERA_FORWARD, 800)
    
    try:
        for step in range(100):
            frame = _get_fresh_frame(camera)
            if frame is None:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = detector.detect(gray)
            
            target = None
            for tag in tags:
                if tag.tag_id == tag_id:
                    target = tag
                    break
            
            if target is None:
                print("  Step %d: Searching for tag %d..." % (step, tag_id))
                _drive(robot, ROTATION_POWER, -ROTATION_POWER,
                       ROTATION_POWER, -ROTATION_POWER)
                time.sleep(0.2)
                _stop(robot)
                time.sleep(0.3)
                continue
            
            cx = target.center[0]
            corners = target.corners
            n = len(corners)
            area = 0
            for i in range(n):
                j = (i + 1) % n
                area += corners[i][0] * corners[j][1]
                area -= corners[j][0] * corners[i][1]
            area = abs(area) / 2.0
            
            offset = cx - 320
            print("  Step %d: Tag %d cx=%.0f area=%.0f offset=%+.0f" % (
                step, tag_id, cx, area, offset))
            
            if area >= TAG_AREA_TARGET:
                _stop(robot)
                print("  REACHED TAG %d (area %.0f)" % (tag_id, area))
                return True
            
            if abs(offset) > TAG_CENTER_TOLERANCE:
                d = 1 if offset > 0 else -1
                _drive(robot, 30 * d, -30 * d, 30 * d, -30 * d)
                time.sleep(0.1)
                _stop(robot)
                time.sleep(0.2)
                continue
            
            _drive(robot, PUSH_POWER, PUSH_POWER, PUSH_POWER, PUSH_POWER)
            time.sleep(0.3)
            _stop(robot)
            time.sleep(0.3)
        
        print("  Timeout: didn't reach tag %d" % tag_id)
        return False
    
    finally:
        _stop(robot)
        if own_camera:
            camera.release()


# === HIGH-LEVEL COMMANDS ===

def cart_load(robot, count=1, color=None):
    """Load blocks into cart (pick up + drop in)."""
    from skills.bump_grab import bump_grab
    
    print("=" * 60)
    print("CART LOAD: %d x %s blocks" % (count, color or "any"))
    print("=" * 60)
    print()
    
    loaded = 0
    try:
        for i in range(count):
            print("--- Block %d of %d ---" % (i + 1, count))
            if bump_grab(robot, color=color):
                load_into_cart(robot)
                loaded += 1
                print()
            else:
                print("Pickup failed.")
                break
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        _stop(robot)
    
    print("LOADED: %d / %d blocks" % (loaded, count))
    return loaded


def cart_push(robot, tag_id):
    """Push cart toward a tag."""
    return push_to_tag(robot, tag_id)


def cart_full(robot, tag_id, count=3, color=None):
    """Full cycle: load blocks into cart, then push to basket."""
    print("=" * 60)
    print("FULL CART CYCLE: %d blocks -> tag %d" % (count, tag_id))
    print("=" * 60)
    print()
    
    loaded = cart_load(robot, count=count, color=color)
    
    if loaded == 0:
        print("No blocks loaded. Skipping push.")
        return False
    
    print()
    print("Loaded %d blocks. Pushing to tag %d..." % (loaded, tag_id))
    return cart_push(robot, tag_id)


# === ARM TEST MODE ===

def test_load_positions():
    """Test arm positions for cart loading."""
    board = get_board()
    arm = Arm(board)
    
    print("CART LOAD POSITION TEST")
    print("=" * 40)
    
    print("1. Camera forward...")
    arm.camera_forward()
    input("   Press Enter...")
    
    print("2. Carry (simulating block)...")
    arm.carry()
    input("   Press Enter...")
    
    print("3. Over cart...")
    _move_arm(board, POS_OVER_CART, 1500)
    input("   Gripper over cart? Press Enter...")
    
    print("4. Drop...")
    _move_arm(board, POS_DROP_CART, 500)
    input("   Press Enter...")
    
    print("5. Forward...")
    arm.camera_forward()
    print("DONE.")


# === CLI ===

if __name__ == '__main__':
    if '--test-load' in sys.argv:
        try:
            test_load_positions()
        finally:
            get_board().set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        sys.exit(0)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 cart_push.py load [count] [color]")
        print("  python3 cart_push.py push <tag_id>")
        print("  python3 cart_push.py full <tag_id> [count] [color]")
        print("  python3 cart_push.py --test-load")
        print()
        print("Basket tags: 578=Blue, 579=Yellow, 580=Red")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Standalone mode — create Robot
    try:
        from robot import Robot
        robot = Robot()
    except Exception:
        print("Robot init failed, using standalone mode")
        robot = None
    
    try:
        if command == 'load':
            count = 1
            color = None
            for arg in sys.argv[2:]:
                if arg.isdigit(): count = int(arg)
                elif arg.lower() in ('red', 'blue', 'yellow'): color = arg.lower()
            if robot:
                cart_load(robot, count=count, color=color)
            else:
                print("Need Robot for cart_load")
        
        elif command == 'push':
            tag_id = int(sys.argv[2])
            if robot:
                cart_push(robot, tag_id)
            else:
                print("Need Robot for cart_push")
        
        elif command == 'full':
            tag_id = int(sys.argv[2])
            count = 3
            color = None
            for arg in sys.argv[3:]:
                if arg.isdigit(): count = int(arg)
                elif arg.lower() in ('red', 'blue', 'yellow'): color = arg.lower()
            if robot:
                cart_full(robot, tag_id, count=count, color=color)
            else:
                print("Need Robot for cart_full")
        
        else:
            print("Unknown command: %s" % command)
    
    finally:
        if robot:
            robot.shutdown()
