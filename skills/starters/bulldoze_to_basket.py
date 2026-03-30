#!/usr/bin/env python3
"""
Bulldoze to Basket (⭐ Easy)

Simplest scoring strategy: drive straight at a basket,
pushing any blocks in your path. No arm needed.

How it works:
  1. Face a basket (find AprilTag on north wall)
  2. Drive forward at full speed
  3. Whatever blocks are in the way get pushed into/near the basket
  4. Back up, repeat from a different angle

Scores: 3-5 pts per block that ends up in a basket.
Not elegant, but it works.

CUSTOMIZE: Change target_tag to aim at different baskets.
CUSTOMIZE: Change DRIVE_POWER for speed vs control.
CUSTOMIZE: Add sonar checks to avoid getting stuck on barriers.

Usage:
    python3 bulldoze_to_basket.py
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board
import pupil_apriltags as apriltag

# ============================================================
# CUSTOMIZE THESE
# ============================================================

target_tag = 580        # Which basket? 578=blue, 579=yellow, 580=red
DRIVE_POWER = 40        # How fast to bulldoze (30=gentle, 50=aggressive)
DRIVE_TIME = 3.0        # How long to drive per push (seconds)
NUM_PUSHES = 3          # How many pushes before stopping
ROTATION_POWER = 35     # Turn speed

# ============================================================
# DON'T CHANGE BELOW (unless you know what you're doing)
# ============================================================

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def detect_tags(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    det = apriltag.Detector(families='tag36h11')
    return det.detect(gray)

def find_and_face_tag(board, camera, tag_id):
    """Rotate until we see the target tag and it's roughly centered."""
    CENTER = 320
    TOLERANCE = 100

    for step in range(24):
        for _ in range(2): camera.read()
        ret, frame = camera.read()
        if not ret:
            continue

        tags = detect_tags(frame)
        for t in tags:
            if t.tag_id == tag_id:
                offset = t.center[0] - CENTER
                if abs(offset) < TOLERANCE:
                    print("  Facing tag %d" % tag_id)
                    return True
                # Rotate toward tag
                d = 1 if offset > 0 else -1
                board.set_motor_duty([(1, ROTATION_POWER*d), (2, -ROTATION_POWER*d),
                                      (3, ROTATION_POWER*d), (4, -ROTATION_POWER*d)])
                time.sleep(0.08)
                stop(board)
                time.sleep(0.2)
                break
        else:
            # Tag not visible, blind rotate
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.2)
            stop(board)
            time.sleep(0.2)

    print("  Could not find tag %d" % tag_id)
    return False

def bulldoze(board):
    """Drive forward for DRIVE_TIME seconds, pushing everything in the way."""
    print("  BULLDOZE! (%.1fs at power %d)" % (DRIVE_TIME, DRIVE_POWER))
    board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                          (3, DRIVE_POWER), (4, DRIVE_POWER)])
    time.sleep(DRIVE_TIME)
    stop(board)

def backup(board):
    """Back up to reset for next push."""
    print("  Backing up...")
    board.set_motor_duty([(1, -DRIVE_POWER), (2, -DRIVE_POWER),
                          (3, -DRIVE_POWER), (4, -DRIVE_POWER)])
    time.sleep(2.0)
    stop(board)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 50)
    print("BULLDOZE TO BASKET")
    print("Target: Tag %d" % target_tag)
    print("=" * 50)

    board = get_board()

    # Camera forward
    board.set_servo_position(800, [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)])
    time.sleep(1)

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    try:
        for push in range(NUM_PUSHES):
            print("\nPush %d/%d:" % (push + 1, NUM_PUSHES))

            # Face the basket
            if find_and_face_tag(board, camera, target_tag):
                # Charge!
                bulldoze(board)
                # Back up for next run
                backup(board)
            else:
                print("  Skipping — can't find basket")

        print("\nDone! Check if any blocks made it into the basket.")

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        stop(board)
        camera.release()

if __name__ == '__main__':
    main()
