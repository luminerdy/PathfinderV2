#!/usr/bin/env python3
"""
Color-Matched Delivery

Pick up a colored block and deliver it to the matching colored basket.

Basket layout (mapped to AprilTags):
  Tag 578 = Blue basket
  Tag 579 = Yellow basket
  Tag 580 = Red basket

Usage (with Robot):
    from robot import Robot
    from skills.color_delivery import color_delivery
    robot = Robot()
    result = color_delivery(robot, target_color='red')

Usage (standalone):
    python3 color_delivery.py red
"""

import sys
import os
import cv2
import time
import math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from lib.arm_positions import Arm, POS_CAMERA_FORWARD, POS_CARRY
from skills.block_detect import BlockDetector

# === BASKET MAPPING ===
BASKET_TAGS = {
    'blue':   578,
    'yellow': 579,
    'red':    580,
}
TAG_TO_COLOR = {v: k for k, v in BASKET_TAGS.items()}

# === CONFIG ===
ROTATION_POWER = 35
DRIVE_POWER = 40
APPROACH_SPEED = 35
TARGET_TAG_AREA = 3000
CENTER_TOL = 100


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
    time.sleep(duration_ms / 1000.0 + 0.2)


def _get_fresh_frame(camera, flush=3):
    if hasattr(camera, 'get_frame'):
        return camera.get_frame(flush=flush)
    for _ in range(flush):
        camera.read()
    ret, frame = camera.read()
    return frame if ret else None


def _detect_tags(frame):
    try:
        from pupil_apriltags import Detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = Detector(families='tag36h11')
        return detector.detect(gray)
    except Exception:
        return []


def _find_tag(tags, tag_id):
    for t in tags:
        if t.tag_id == tag_id:
            return t
    return None


def _tag_area(tag):
    corners = tag.corners
    n = len(corners)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    return abs(area) / 2


# === NAVIGATE TO BASKET ===

def navigate_to_basket(robot, camera, target_tag_id):
    """Navigate to a basket's AprilTag.
    
    Args:
        robot: Robot instance or raw board
        camera: Camera or cv2.VideoCapture
        target_tag_id: AprilTag ID of target basket
    
    Returns:
        True if reached the tag.
    """
    print("  Navigating to Tag %d..." % target_tag_id)
    FRAME_CENTER = 320

    for cycle in range(100):
        _stop(robot)
        time.sleep(0.06)

        frame = _get_fresh_frame(camera, flush=2)
        if frame is None:
            continue

        tags = _detect_tags(frame)
        tag = _find_tag(tags, target_tag_id)

        if tag is None:
            if cycle % 10 == 0:
                print("    Cycle %d: Tag %d not visible, searching..." % (cycle, target_tag_id))
            _drive(robot, ROTATION_POWER, -ROTATION_POWER, ROTATION_POWER, -ROTATION_POWER)
            time.sleep(0.20)
            _stop(robot)
            time.sleep(0.2)
            continue

        tx = tag.center[0]
        offset = tx - FRAME_CENTER
        area = _tag_area(tag)

        if cycle % 5 == 0:
            print("    Cycle %d: Tag %d offset=%+d area=%.0f" % (cycle, target_tag_id, int(offset), area))

        if area >= TARGET_TAG_AREA and abs(offset) < CENTER_TOL:
            _stop(robot)
            print("    REACHED Tag %d (area=%.0f)" % (target_tag_id, area))
            return True

        if abs(offset) > CENTER_TOL:
            d = 1 if offset > 0 else -1
            rot_time = max(0.04, min(0.10, abs(offset) / 2000.0))
            _drive(robot, ROTATION_POWER * d, -ROTATION_POWER * d,
                   ROTATION_POWER * d, -ROTATION_POWER * d)
            time.sleep(rot_time)
            _stop(robot)
        else:
            speed = APPROACH_SPEED if area > TARGET_TAG_AREA / 2 else DRIVE_POWER
            _drive(robot, speed, speed, speed, speed)
            time.sleep(0.12)

    _stop(robot)
    print("    Timeout navigating to Tag %d" % target_tag_id)
    return False


# === DROP IN BASKET ===

def drop_in_basket(robot):
    """Open gripper to drop block, back up, return arm to forward."""
    board = _get_board(robot)
    print("  Dropping block in basket...")
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(0.8)

    print("  Backing up...")
    _drive(robot, -DRIVE_POWER, -DRIVE_POWER, -DRIVE_POWER, -DRIVE_POWER)
    time.sleep(1.0)
    _stop(robot)

    _move_arm(board, POS_CAMERA_FORWARD, 800)
    print("  DELIVERED!")


# === MAIN ENTRY POINTS ===

def color_delivery(robot_or_color=None, target_color=None):
    """
    Full color-matched delivery cycle.
    
    Accepts either:
        color_delivery(robot, target_color='red')
        color_delivery(target_color='red')
        color_delivery('red')
    
    Returns:
        dict with success, block_color, basket_tag, details
    """
    from robot import Robot as RobotClass

    if isinstance(robot_or_color, RobotClass):
        return _color_delivery_robot(robot_or_color, target_color)
    elif isinstance(robot_or_color, str):
        return _color_delivery_standalone(robot_or_color)
    else:
        return _color_delivery_standalone(target_color)


def _color_delivery_robot(robot, target_color=None):
    """Color delivery using Robot instance."""
    from skills.bump_grab import bump_grab

    print("=" * 60)
    print("COLOR-MATCHED DELIVERY")
    print("Target: %s" % (target_color or "any"))
    print("=" * 60)
    print()

    if not robot.battery_ok:
        print("BATTERY TOO LOW")
        return {'success': False, 'details': 'battery_low'}
    print("Battery: %.2fV" % robot.battery)

    # PHASE 1: Find block
    print()
    print("PHASE 1: Find block")
    print("-" * 40)

    robot.arm.camera_forward()
    time.sleep(0.5)

    detector = BlockDetector()
    colors_to_find = [target_color] if target_color else ['red', 'yellow', 'blue']
    block_color = None

    for step in range(24):
        frame = robot.camera.get_frame()
        if frame is None:
            continue

        for color in colors_to_find:
            blocks = detector.detect(frame, colors=[color])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                print("  Step %d: %s offset=%+d" % (step, color, b.offset_from_center))

                if abs(b.offset_from_center) < 80:
                    block_color = color
                    print("  FACING %s block!" % color.upper())
                    break

                d = 1 if b.offset_from_center > 0 else -1
                _drive(robot, ROTATION_POWER * d, -ROTATION_POWER * d,
                       ROTATION_POWER * d, -ROTATION_POWER * d)
                time.sleep(0.08 if abs(b.offset_from_center) < 150 else 0.15)
                _stop(robot)
                time.sleep(0.3)
                break

        if block_color:
            break

        _drive(robot, ROTATION_POWER, -ROTATION_POWER, ROTATION_POWER, -ROTATION_POWER)
        time.sleep(0.25)
        _stop(robot)
        time.sleep(0.3)

    if not block_color:
        print("  No block found")
        return {'success': False, 'details': 'no_block_found'}

    target_tag = BASKET_TAGS[block_color]
    print("  Block: %s -> Basket: Tag %d" % (block_color.upper(), target_tag))

    # PHASE 2: Pick up
    print()
    print("PHASE 2: Pick up %s block" % block_color)
    print("-" * 40)

    if not bump_grab(robot, color=block_color):
        return {'success': False, 'block_color': block_color, 'details': 'pickup_failed'}

    # PHASE 3: Navigate to basket
    print()
    print("PHASE 3: Navigate to %s basket (Tag %d)" % (block_color.upper(), target_tag))
    print("-" * 40)

    robot.arm.carry()
    time.sleep(0.5)

    # Arm to carry-but-camera-visible pose (gripper closed, arm up for camera view)
    board = _get_board(robot)
    _move_arm(board, [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)], 800)
    time.sleep(1.0)

    reached = navigate_to_basket(robot, robot.camera, target_tag)

    if not reached:
        return {'success': False, 'block_color': block_color, 'details': 'nav_failed'}

    # PHASE 4: Drop
    print()
    print("PHASE 4: Drop in %s basket" % block_color.upper())
    print("-" * 40)

    drop_in_basket(robot)

    print()
    print("=" * 60)
    print("SUCCESS! %s block -> Tag %d" % (block_color.upper(), target_tag))
    print("=" * 60)

    return {'success': True, 'block_color': block_color,
            'basket_tag': target_tag, 'details': 'delivered'}


def _color_delivery_standalone(target_color=None):
    """Legacy standalone color delivery."""
    from skills.bump_grab import bump_grab

    print("=" * 60)
    print("COLOR-MATCHED DELIVERY (standalone)")
    print("Target: %s" % (target_color or "any"))
    print("=" * 60)
    print()

    board = get_board()
    arm = Arm(board)
    battery_min = 7.0 if PLATFORM == 'pi4' else 8.1

    time.sleep(1)
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        v = mv / 1000.0
        print("Battery: %.2fV" % v)
        if v < battery_min:
            print("BATTERY TOO LOW")
            return {'success': False, 'details': 'battery_low'}

    # PHASE 1: Find block
    print()
    print("PHASE 1: Find block")
    print("-" * 40)

    arm.camera_forward()
    time.sleep(1.0)

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    detector = BlockDetector()
    colors_to_find = [target_color] if target_color else ['red', 'yellow', 'blue']
    block_color = None

    for step in range(24):
        frame = _get_fresh_frame(camera)
        if frame is None:
            continue

        for color in colors_to_find:
            blocks = detector.detect(frame, colors=[color])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                if abs(b.offset_from_center) < 80:
                    block_color = color
                    break
                d = 1 if b.offset_from_center > 0 else -1
                board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                      (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
                time.sleep(0.08 if abs(b.offset_from_center) < 150 else 0.15)
                board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                time.sleep(0.3)
                break

        if block_color:
            break
        board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                              (3, ROTATION_POWER), (4, -ROTATION_POWER)])
        time.sleep(0.25)
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        time.sleep(0.3)

    camera.release()

    if not block_color:
        return {'success': False, 'details': 'no_block_found'}

    target_tag = BASKET_TAGS[block_color]

    # PHASE 2: Pick up
    if not bump_grab(color=block_color):
        return {'success': False, 'block_color': block_color, 'details': 'pickup_failed'}

    # PHASE 3: Navigate
    arm.carry()
    time.sleep(0.5)
    _move_arm(board, [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)], 800)
    time.sleep(1.0)

    camera2 = cv2.VideoCapture(0)
    camera2.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera2.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.0)

    reached = navigate_to_basket(board, camera2, target_tag)
    camera2.release()

    if not reached:
        return {'success': False, 'block_color': block_color, 'details': 'nav_failed'}

    # PHASE 4: Drop
    drop_in_basket(board)

    return {'success': True, 'block_color': block_color,
            'basket_tag': target_tag, 'details': 'delivered'}


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
        try:
            board = get_board()
            board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        except:
            pass
