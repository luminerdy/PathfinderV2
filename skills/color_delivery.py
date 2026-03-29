#!/usr/bin/env python3
"""
Color-Matched Delivery

Pick up a colored block and deliver it to the matching colored basket.

Basket layout (mapped to AprilTags):
  Tag 578 = Blue basket   (far left)
  Tag 579 = Yellow basket (center-left)
  Tag 580 = Red basket    (center-right)

Strategy:
  1. Scan field for blocks
  2. Pick up a block (bump_grab)
  3. Remember block color
  4. Navigate to matching AprilTag
  5. Drive close to basket
  6. Drop block into basket (open gripper from carry height)

Usage:
    python3 color_delivery.py           # Any block, match to basket
    python3 color_delivery.py red       # Red block to red basket
"""

import sys
import os
import cv2
import time
import math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from skills.block_detect import BlockDetector

# === BASKET MAPPING ===
# AprilTag ID → basket color
BASKET_TAGS = {
    'blue':   578,
    'yellow': 579,
    'red':    580,
}

# Reverse lookup
TAG_TO_COLOR = {v: k for k, v in BASKET_TAGS.items()}

# === CONFIG ===
ROTATION_POWER = 35
DRIVE_POWER = 40
APPROACH_SPEED = 35       # Slower when close to basket

# How close to drive to the tag before dropping (target area in pixels)
# Larger area = closer. ~4000 = about 30-40cm from wall
TARGET_TAG_AREA = 3000

# Arm positions
POS_CAMERA_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CARRY = [(1, 1475), (3, 569), (4, 2400), (5, 809), (6, 1500)]

BATTERY_MIN = 7.0 if PLATFORM == 'pi4' else 8.1


# === HELPERS ===

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def move_arm(board, position, duration_ms=800):
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)


def detect_tags(frame):
    """Detect AprilTags in frame. Returns list of detections."""
    try:
        import pupil_apriltags as apriltag
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = apriltag.Detector(families='tag36h11')
        return detector.detect(gray)
    except Exception:
        return []


def find_tag(tags, tag_id):
    """Find a specific tag in detection list."""
    for t in tags:
        if t.tag_id == tag_id:
            return t
    return None


def tag_area(tag):
    """Calculate approximate area of detected tag (pixel area)."""
    # Use the 4 corners to estimate area
    corners = tag.corners
    # Shoelace formula
    n = len(corners)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    return abs(area) / 2


# === NAVIGATE TO BASKET ===

def navigate_to_tag(board, camera, target_tag_id):
    """
    Navigate to a specific AprilTag by:
    1. Rotate to find the tag
    2. Center on it
    3. Drive toward it until close enough

    Returns:
        True if reached the tag area.
    """
    print("  Navigating to Tag %d..." % target_tag_id)

    FRAME_CENTER = 320
    CENTER_TOL = 100  # Wider tolerance — basket is big, don't need pixel-perfect

    for cycle in range(100):
        stop(board)
        time.sleep(0.06)

        # Capture
        for _ in range(2):
            camera.read()
        ret, frame = camera.read()
        if not ret:
            continue

        tags = detect_tags(frame)
        tag = find_tag(tags, target_tag_id)

        if tag is None:
            # Tag not visible — rotate to search
            if cycle % 10 == 0:
                print("    Cycle %d: Tag %d not visible, searching..." % (cycle, target_tag_id))
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.20)
            stop(board)
            time.sleep(0.2)
            continue

        # Tag found
        tx = tag.center[0]
        offset = tx - FRAME_CENTER
        area = tag_area(tag)

        if cycle % 5 == 0:
            print("    Cycle %d: Tag %d at x=%d offset=%+d area=%.0f" % (
                cycle, target_tag_id, int(tx), int(offset), area))

        # Close enough?
        if area >= TARGET_TAG_AREA and abs(offset) < CENTER_TOL:
            stop(board)
            print("    REACHED Tag %d (area=%.0f)" % (target_tag_id, area))
            return True

        # Center on tag first
        if abs(offset) > CENTER_TOL:
            d = 1 if offset > 0 else -1
            rot_time = min(0.10, abs(offset) / 2000.0)
            rot_time = max(0.04, rot_time)
            board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                  (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
            time.sleep(rot_time)
            stop(board)
        else:
            # Drive toward tag
            speed = APPROACH_SPEED if area > TARGET_TAG_AREA / 2 else DRIVE_POWER
            board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])
            time.sleep(0.12)

    stop(board)
    print("    Timeout navigating to Tag %d" % target_tag_id)
    return False


# === DROP IN BASKET ===

def drop_in_basket(board):
    """
    Drop block into basket from carry height.
    Just open the gripper — block falls in.
    """
    print("  Dropping block in basket...")
    # Open gripper — block falls from carry position
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(0.8)

    # Back up from basket
    print("  Backing up...")
    board.set_motor_duty([(1, -DRIVE_POWER), (2, -DRIVE_POWER),
                          (3, -DRIVE_POWER), (4, -DRIVE_POWER)])
    time.sleep(1.0)
    stop(board)

    # Return arm to forward
    move_arm(board, POS_CAMERA_FORWARD, 800)

    print("  DELIVERED!")


# === MAIN ===

def color_delivery(target_color=None):
    """
    Full color-matched delivery cycle.

    If target_color specified, only picks up that color.
    Otherwise picks up nearest block of any competition color.

    Returns:
        dict with success, block_color, basket_tag, details
    """
    print("=" * 60)
    print("COLOR-MATCHED DELIVERY")
    print("Target: %s" % (target_color or "any"))
    print("=" * 60)
    print()

    board = get_board()

    # Battery check
    time.sleep(1)
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        v = mv / 1000.0
        print("Battery: %.2fV" % v)
        if v < BATTERY_MIN:
            print("BATTERY TOO LOW")
            return {'success': False, 'details': 'battery_low'}

    # === PHASE 1: FIND AND IDENTIFY BLOCK ===
    print()
    print("PHASE 1: Find block")
    print("-" * 40)

    move_arm(board, POS_CAMERA_FORWARD, 800)
    time.sleep(1.0)

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    detector = BlockDetector()

    # Scan for blocks
    block_color = None
    colors_to_find = [target_color] if target_color else ['red', 'yellow', 'blue']

    for step in range(24):
        for _ in range(3):
            camera.read()
        ret, frame = camera.read()
        if not ret:
            continue

        for color in colors_to_find:
            blocks = detector.detect(frame, colors=[color])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                print("  Step %d: %s at offset=%+d dist=%.0fcm" % (
                    step, color, b.offset_from_center, b.estimated_distance_mm / 10))

                if abs(b.offset_from_center) < 80:
                    block_color = color
                    print("  FACING %s block!" % color.upper())
                    break

                # Rotate toward
                d = 1 if b.offset_from_center > 0 else -1
                board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                      (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
                time.sleep(0.08 if abs(b.offset_from_center) < 150 else 0.15)
                stop(board)
                time.sleep(0.3)
                break

        if block_color:
            break

        # Blind rotate to search
        board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                              (3, ROTATION_POWER), (4, -ROTATION_POWER)])
        time.sleep(0.25)
        stop(board)
        time.sleep(0.3)

    if not block_color:
        camera.release()
        print("  No block found")
        return {'success': False, 'details': 'no_block_found'}

    target_tag = BASKET_TAGS[block_color]
    print("  Block: %s -> Basket: Tag %d" % (block_color.upper(), target_tag))

    # === PHASE 2: PICK UP BLOCK ===
    print()
    print("PHASE 2: Pick up %s block" % block_color)
    print("-" * 40)

    camera.release()

    # Use bump_grab
    from skills.bump_grab import bump_grab
    grabbed = bump_grab(color=block_color)

    if not grabbed:
        print("  Pickup failed")
        return {'success': False, 'block_color': block_color, 'details': 'pickup_failed'}

    # === PHASE 3: NAVIGATE TO MATCHING BASKET ===
    print()
    print("PHASE 3: Navigate to %s basket (Tag %d)" % (block_color.upper(), target_tag))
    print("-" * 40)

    # Arm to carry position (block held)
    move_arm(board, POS_CARRY, 800)
    time.sleep(0.5)

    # Switch to forward camera for navigation
    move_arm(board, [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)], 800)
    time.sleep(1.0)

    camera2 = cv2.VideoCapture(0)
    camera2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.0)

    reached = navigate_to_tag(board, camera2, target_tag)
    camera2.release()

    if not reached:
        print("  Could not reach basket")
        return {'success': False, 'block_color': block_color, 'details': 'nav_failed'}

    # === PHASE 4: DROP IN BASKET ===
    print()
    print("PHASE 4: Drop in %s basket" % block_color.upper())
    print("-" * 40)

    drop_in_basket(board)

    print()
    print("=" * 60)
    print("SUCCESS! %s block -> %s basket (Tag %d)" % (
        block_color.upper(), block_color, target_tag))
    print("=" * 60)

    return {
        'success': True,
        'block_color': block_color,
        'basket_tag': target_tag,
        'details': 'delivered'
    }


if __name__ == '__main__':
    color = None
    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 color_delivery.py [red|blue|yellow]")
            sys.exit(1)

    try:
        color_delivery(target_color=color)
    except Exception as e:
        print("ERROR: %s" % e)
    finally:
        # ALWAYS stop motors on exit (safety)
        try:
            board = get_board()
            stop(board)
        except:
            pass
