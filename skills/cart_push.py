#!/usr/bin/env python3
"""
Cart Push - Load blocks into a shopping cart and push it to a basket

Strategy:
  1. Position behind cart (cart between robot and basket)
  2. Pick up blocks and drop into cart (using bin_collect style arm rotation,
     but dropping forward into cart instead of backward into bin)
  3. Push cart toward target basket using AprilTag navigation
  4. Robot drives forward, cart slides ahead

The shopping cart sits in front of the robot. The robot's chassis
pushes it from behind. Load blocks by grabbing them and dropping
into the cart from above.

Usage:
    python3 cart_push.py push 580          # Push cart toward tag 580
    python3 cart_push.py load              # Load one block into cart
    python3 cart_push.py load 3            # Load 3 blocks into cart
    python3 cart_push.py full 580          # Load blocks then push to tag
    python3 cart_push.py --test-load       # Test loading arm positions

SAFETY: Robot will drive and move arm! Clear workspace.

== CALIBRATION NEEDED ==
ARM positions for "drop into cart in front" need tuning.
Run with --test-load to calibrate arm positions.

== CART SETUP ==
Place the shopping cart directly in front of the robot.
The robot will push from behind (chassis bumps cart).
Cart must be light enough for mecanum wheels to push.
"""

import sys
import os
import time
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from skills.bump_grab import (
    bump_grab, move_arm, stop,
    POS_CARRY, POS_CAMERA_FORWARD,
    scan_and_face, drive_to_contact, backup_and_grab,
    get_fresh_frame
)
from skills.block_detect import BlockDetector

# === CONFIG ===

DRIVE_POWER = 35
PUSH_POWER = 40       # Slightly higher to push cart + friction
ROTATION_POWER = 35
BATTERY_MIN = 7.0 if PLATFORM == 'pi4' else 8.1

# Arm position to drop block into cart (in front of robot)
# The cart is in front, so we need arm extended forward and high enough
# to clear the cart rim, then open gripper.
# Start from CARRY, raise shoulder, extend forward
# CALIBRATE THESE with --test-load
POS_OVER_CART = [(1, 1475), (3, 800), (4, 2100), (5, 1200), (6, 1500)]   # Forward, elevated
POS_DROP_CART = [(1, 2500), (3, 800), (4, 2100), (5, 1200), (6, 1500)]   # Open gripper

# AprilTag navigation for pushing
TAG_CENTER_TOLERANCE = 100   # Pixels from center
TAG_AREA_TARGET = 3000       # Stop pushing when tag is this big (close enough)


# === ARM TEST MODE ===

def test_load_positions(board):
    """Test arm positions for loading blocks into front cart.
    Run this with the cart placed in front of the robot.
    """
    print("CART LOAD POSITION TEST")
    print("=" * 40)
    print()
    print("Place the shopping cart directly in front of the robot.")
    print()

    print("1. Moving to CAMERA FORWARD (home)...")
    move_arm(board, POS_CAMERA_FORWARD, 1500)
    input("   Press Enter...")

    print("2. Moving to CARRY (simulating held block)...")
    move_arm(board, POS_CARRY, 1000)
    input("   Press Enter...")

    print("3. Moving OVER CART (arm forward + elevated)...")
    print("   Gripper should be above and over the cart opening!")
    move_arm(board, POS_OVER_CART, 1500)
    input("   Is gripper over the cart? Adjust POS_OVER_CART if not.")
    input("   Press Enter...")

    print("4. Opening gripper (DROP into cart)...")
    move_arm(board, POS_DROP_CART, 500)
    time.sleep(0.5)
    input("   Press Enter...")

    print("5. Returning to FORWARD...")
    move_arm(board, POS_CAMERA_FORWARD, 1500)

    print()
    print("DONE. Adjust POS_OVER_CART in this file if gripper")
    print("wasn't positioned over the cart opening.")


# === LOAD INTO CART ===

def load_into_cart(board):
    """After bump_grab picks up a block, drop it into the front cart.
    Assumes block is in CARRY position.
    """
    print("  Raising arm over cart...")
    move_arm(board, POS_OVER_CART, 1200)
    time.sleep(0.3)

    print("  Dropping block into cart...")
    move_arm(board, POS_DROP_CART, 500)
    time.sleep(0.3)

    print("  Returning arm to forward...")
    move_arm(board, POS_CAMERA_FORWARD, 1000)

    print("  BLOCK IN CART!")


# === PUSH TO TAG ===

def push_to_tag(board, tag_id):
    """Push cart toward an AprilTag by driving forward.

    Uses camera to find the tag, center on it, then drive forward
    pushing the cart ahead. Stops when tag area reaches target
    (meaning we're close enough to the basket).

    Args:
        tag_id: AprilTag ID to push toward (e.g. 580 for red basket)

    Returns:
        True if reached the tag area target
    """
    print("PUSHING CART TO TAG %d" % tag_id)
    print("-" * 40)

    # Import AprilTag detector
    try:
        from pupil_apriltags import Detector
    except ImportError:
        print("  ERROR: pupil_apriltags not installed")
        return False

    detector = Detector(families='tag36h11')

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    # Arm up and out of the way for clear camera view
    move_arm(board, POS_CAMERA_FORWARD, 800)

    try:
        for step in range(100):  # Max 100 navigation steps
            frame = get_fresh_frame(camera)
            if frame is None:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = detector.detect(gray)

            # Find our target tag
            target = None
            for tag in tags:
                if tag.tag_id == tag_id:
                    target = tag
                    break

            if target is None:
                # Rotate to search for tag
                print("  Step %d: Searching for tag %d..." % (step, tag_id))
                board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                      (3, ROTATION_POWER), (4, -ROTATION_POWER)])
                time.sleep(0.2)
                stop(board)
                time.sleep(0.3)
                continue

            # Tag found - get center and area
            cx = target.center[0]
            # Compute area from corners (quadrilateral)
            corners = target.corners
            # Shoelace formula
            n = len(corners)
            area = 0
            for i in range(n):
                j = (i + 1) % n
                area += corners[i][0] * corners[j][1]
                area -= corners[j][0] * corners[i][1]
            area = abs(area) / 2.0

            offset = cx - 320  # Center of 640px frame
            print("  Step %d: Tag %d at cx=%.0f, area=%.0f, offset=%+.0f" % (
                step, tag_id, cx, area, offset))

            # Close enough?
            if area >= TAG_AREA_TARGET:
                stop(board)
                print("  REACHED TAG %d (area %.0f >= %d)" % (tag_id, area, TAG_AREA_TARGET))
                return True

            # Center on tag first
            if abs(offset) > TAG_CENTER_TOLERANCE:
                d = 1 if offset > 0 else -1
                board.set_motor_duty([(1, 30 * d), (2, -30 * d),
                                      (3, 30 * d), (4, -30 * d)])
                time.sleep(0.1)
                stop(board)
                time.sleep(0.2)
                continue

            # Drive forward (push cart)
            board.set_motor_duty([(1, PUSH_POWER), (2, PUSH_POWER),
                                  (3, PUSH_POWER), (4, PUSH_POWER)])
            time.sleep(0.3)
            stop(board)
            time.sleep(0.3)

        print("  Timeout: didn't reach tag %d" % tag_id)
        return False

    finally:
        stop(board)
        camera.release()


# === MAIN COMMANDS ===

def cmd_load(count=1, color=None):
    """Load blocks into the cart (pick up + drop in)."""
    print("=" * 60)
    print("CART LOAD: %d x %s blocks" % (count, color or "any"))
    print("=" * 60)
    print()

    board = get_board()
    loaded = 0

    try:
        for i in range(count):
            print("--- Block %d of %d ---" % (i + 1, count))

            # Pick up block
            success = bump_grab(color=color)
            if not success:
                print("Pickup failed. Loaded %d blocks." % loaded)
                break

            # Drop into cart
            print()
            load_into_cart(board)
            loaded += 1
            print()

    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        stop(board)

    print("LOADED: %d / %d blocks into cart" % (loaded, count))
    return loaded


def cmd_push(tag_id):
    """Push cart toward a tag."""
    board = get_board()
    try:
        return push_to_tag(board, tag_id)
    finally:
        stop(board)


def cmd_full(tag_id, count=3, color=None):
    """Full cycle: load blocks into cart, then push to basket."""
    print("=" * 60)
    print("FULL CART CYCLE")
    print("Load %d blocks, push to tag %d" % (count, tag_id))
    print("=" * 60)
    print()

    loaded = cmd_load(count=count, color=color)

    if loaded == 0:
        print("No blocks loaded. Skipping push.")
        return False

    print()
    print("=" * 60)
    print("Loaded %d blocks. Pushing cart to tag %d..." % (loaded, tag_id))
    print("=" * 60)
    print()

    return cmd_push(tag_id)


# === CLI ===

if __name__ == '__main__':
    if '--test-load' in sys.argv:
        board = get_board()
        try:
            test_load_positions(board)
        finally:
            stop(board)
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 cart_push.py load [count] [color]     # Load blocks into cart")
        print("  python3 cart_push.py push <tag_id>            # Push cart to tag")
        print("  python3 cart_push.py full <tag_id> [count] [color]  # Load + push")
        print("  python3 cart_push.py --test-load              # Test arm positions")
        print()
        print("Basket tags: 578=Blue, 579=Yellow, 580=Red")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'load':
        count = 1
        color = None
        for arg in sys.argv[2:]:
            if arg.isdigit():
                count = int(arg)
            elif arg.lower() in ('red', 'blue', 'yellow'):
                color = arg.lower()
        cmd_load(count=count, color=color)

    elif command == 'push':
        if len(sys.argv) < 3:
            print("Usage: python3 cart_push.py push <tag_id>")
            sys.exit(1)
        tag_id = int(sys.argv[2])
        cmd_push(tag_id)

    elif command == 'full':
        if len(sys.argv) < 3:
            print("Usage: python3 cart_push.py full <tag_id> [count] [color]")
            sys.exit(1)
        tag_id = int(sys.argv[2])
        count = 3
        color = None
        for arg in sys.argv[3:]:
            if arg.isdigit():
                count = int(arg)
            elif arg.lower() in ('red', 'blue', 'yellow'):
                color = arg.lower()
        cmd_full(tag_id, count=count, color=color)

    else:
        print("Unknown command: %s" % command)
        print("Commands: load, push, full, --test-load")
        sys.exit(1)
