#!/usr/bin/env python3
"""
Navigate to AprilTag with Obstacle Avoidance (⭐⭐ Medium)

Drive to any AprilTag while using sonar to detect and strafe
around barriers. This is the foundation for all autonomous navigation.

How it works:
  1. Rotate to find the target AprilTag
  2. Drive toward it
  3. If sonar detects obstacle (<25cm), STRAFE sideways to avoid
  4. Resume driving toward tag
  5. Stop when close enough (tag fills enough of the frame)

Key concept: Mecanum strafe lets you slide sideways around barriers
without losing sight of the target tag. Regular wheels would need
to turn, drive, turn back — mecanum just slides.

CUSTOMIZE: Change target_tag to navigate to different locations.
CUSTOMIZE: Change OBSTACLE_DISTANCE for sensitivity to barriers.
CUSTOMIZE: Change STRAFE_TIME for how far to slide around obstacles.

Usage:
    python3 navigate_to_tag.py          # Default: tag 580
    python3 navigate_to_tag.py 578      # Navigate to tag 578
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board
from sdk.common.sonar import Sonar
import pupil_apriltags as apriltag

# ============================================================
# CUSTOMIZE THESE
# ============================================================

target_tag = 580            # Which tag to navigate to
DRIVE_POWER = 40            # Forward drive speed
STRAFE_POWER = 40           # Sideways strafe speed
ROTATION_POWER = 35         # Turning speed
OBSTACLE_DISTANCE = 250     # mm — strafe when closer than this (25cm)
OBSTACLE_CLEAR = 400        # mm — obstacle cleared when sonar reads this (40cm)
STRAFE_TIME = 0.3           # Seconds per strafe burst
STRAFE_DIRECTION = 1        # 1 = strafe right, -1 = strafe left
TARGET_TAG_AREA = 5000      # Tag area to count as "arrived"
CENTER_TOL = 100            # Pixels from center to count as "facing"
TIMEOUT = 60                # Max seconds to navigate

# ============================================================
# CORE FUNCTIONS
# ============================================================

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def strafe(board, direction, duration):
    """Strafe sideways. direction: 1=right, -1=left."""
    d = direction
    # Mecanum strafe: FL+RR same direction, FR+RL opposite
    board.set_motor_duty([(1, STRAFE_POWER * d), (2, -STRAFE_POWER * d),
                          (3, -STRAFE_POWER * d), (4, STRAFE_POWER * d)])
    time.sleep(duration)
    stop(board)

def drive_forward(board, duration=0.2):
    """Drive straight forward."""
    board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                          (3, DRIVE_POWER), (4, DRIVE_POWER)])
    time.sleep(duration)

def detect_tags(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    det = apriltag.Detector(families='tag36h11')
    return det.detect(gray)

def tag_area(tag):
    corners = tag.corners
    n = len(corners)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    return abs(area) / 2

def find_tag(tags, tag_id):
    for t in tags:
        if t.tag_id == tag_id:
            return t
    return None


# ============================================================
# MAIN NAVIGATION LOOP
# ============================================================

def navigate(board, camera, sonar, tag_id):
    """
    Navigate to a specific AprilTag, avoiding obstacles with sonar.

    Strategy:
      - If no obstacle: drive toward tag
      - If obstacle detected: strafe sideways until clear, then resume
      - If tag not visible: rotate to search
      - If tag close enough: ARRIVED
    """
    FRAME_CENTER = 320
    start = time.time()
    strafe_dir = STRAFE_DIRECTION  # Can alternate if stuck

    print("Navigating to Tag %d..." % tag_id)

    for cycle in range(500):
        if time.time() - start > TIMEOUT:
            print("  TIMEOUT")
            return False

        stop(board)
        time.sleep(0.05)

        # --- CHECK SONAR: Obstacle ahead? ---
        dist = sonar.getDistance()  # mm
        if dist and dist < OBSTACLE_DISTANCE:
            # Obstacle! Strafe around it
            print("  Cycle %d: OBSTACLE at %dmm — strafing %s" % (
                cycle, dist, "right" if strafe_dir > 0 else "left"))

            # Keep strafing until obstacle clears
            strafe_cycles = 0
            while dist and dist < OBSTACLE_CLEAR and strafe_cycles < 20:
                strafe(board, strafe_dir, STRAFE_TIME)
                time.sleep(0.1)
                dist = sonar.getDistance()
                strafe_cycles += 1

            print("    Cleared after %d strafes (sonar=%s)" % (
                strafe_cycles, "%dmm" % dist if dist else "?"))

            # Drive forward a bit to pass the obstacle
            drive_forward(board, 0.5)
            stop(board)
            continue

        # --- CHECK CAMERA: Where's the tag? ---
        for _ in range(2): camera.read()
        ret, frame = camera.read()
        if not ret:
            continue

        tags = detect_tags(frame)
        tag = find_tag(tags, tag_id)

        if tag is None:
            # Tag not visible — rotate to search
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.15)
            stop(board)
            time.sleep(0.15)
            continue

        # Tag found!
        tx = tag.center[0]
        offset = tx - FRAME_CENTER
        area = tag_area(tag)

        if cycle % 10 == 0:
            sonar_str = "%dmm" % dist if dist and dist < 5000 else "clear"
            print("  Cycle %d: Tag %d offset=%+d area=%.0f sonar=%s" % (
                cycle, tag_id, int(offset), area, sonar_str))

        # --- ARRIVED? ---
        if area >= TARGET_TAG_AREA and abs(offset) < CENTER_TOL:
            stop(board)
            print("  ARRIVED at Tag %d! (area=%.0f)" % (tag_id, area))
            return True

        # --- STEER toward tag ---
        if abs(offset) > CENTER_TOL:
            d = 1 if offset > 0 else -1
            rot_time = min(0.10, abs(offset) / 2000.0)
            rot_time = max(0.04, rot_time)
            board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                  (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
            time.sleep(rot_time)
            stop(board)
        else:
            # --- DRIVE toward tag ---
            drive_forward(board, 0.2)

    stop(board)
    return False


# ============================================================
# MAIN
# ============================================================

def main():
    # Allow tag ID from command line
    global target_tag
    if len(sys.argv) > 1:
        target_tag = int(sys.argv[1])

    print("=" * 50)
    print("NAVIGATE TO TAG %d (with obstacle avoidance)" % target_tag)
    print("=" * 50)

    board = get_board()
    sonar = Sonar()

    # Camera forward
    board.set_servo_position(800, [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)])
    time.sleep(1)

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    try:
        reached = navigate(board, camera, sonar, target_tag)
        print()
        if reached:
            print("SUCCESS — arrived at Tag %d!" % target_tag)
        else:
            print("FAILED — did not reach Tag %d" % target_tag)
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        stop(board)
        camera.release()

if __name__ == '__main__':
    main()
