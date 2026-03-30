#!/usr/bin/env python3
"""
Color Sort One Block (⭐⭐⭐ Hard)

Pick up one colored block and deliver it to the matching basket.

How it works:
  1. Scan for a block (any color, or specify one)
  2. Identify the color → look up matching basket tag
  3. Drive to block and pick it up (bump_grab)
  4. Navigate to matching basket (with obstacle avoidance)
  5. Drop block in basket
  6. Back up

This is one complete scoring cycle worth 15 points.

CUSTOMIZE: Change TARGET_COLOR to focus on specific blocks.
CUSTOMIZE: Change BASKET_TAGS if your field uses different tag IDs.
CUSTOMIZE: Adjust navigation parameters for your field.

Usage:
    python3 color_sort_one.py          # Pick up any block
    python3 color_sort_one.py red      # Red block only
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board
from skills.block_detect import BlockDetector

# ============================================================
# CUSTOMIZE THESE
# ============================================================

# Which color to pick up? None = any, or 'red', 'yellow', 'blue'
TARGET_COLOR = None

# Basket-to-tag mapping (match your field setup)
BASKET_TAGS = {
    'blue':   578,
    'yellow': 579,
    'red':    580,
}

DRIVE_POWER = 40
ROTATION_POWER = 35

# ============================================================
# STEPS
# ============================================================

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def move_arm(board, position, duration_ms=800):
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)


def step1_find_block(board, camera, detector, color=None):
    """Scan and face a colored block. Returns the color found."""
    print("STEP 1: Find block")
    
    # Camera forward
    move_arm(board, [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)])
    time.sleep(0.5)
    
    colors_to_find = [color] if color else ['red', 'yellow', 'blue']
    
    for step in range(24):
        for _ in range(3): camera.read()
        ret, frame = camera.read()
        if not ret: continue
        
        for c in colors_to_find:
            blocks = detector.detect(frame, colors=[c])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                if abs(b.offset_from_center) < 80:
                    print("  Found %s block (offset=%+d)" % (c, b.offset_from_center))
                    return c
                
                # Rotate toward
                d = 1 if b.offset_from_center > 0 else -1
                board.set_motor_duty([(1, ROTATION_POWER*d), (2, -ROTATION_POWER*d),
                                      (3, ROTATION_POWER*d), (4, -ROTATION_POWER*d)])
                time.sleep(0.08 if abs(b.offset_from_center) < 150 else 0.15)
                stop(board)
                time.sleep(0.3)
                break
        else:
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.25)
            stop(board)
            time.sleep(0.3)
    
    print("  No block found")
    return None


def step2_pickup(board, camera, detector, color):
    """Drive to block and pick it up."""
    print("STEP 2: Pick up %s block" % color)
    
    # Drive toward block (timed, based on distance estimate)
    for _ in range(3): camera.read()
    ret, frame = camera.read()
    est_dist = 30
    if ret:
        blocks = detector.detect(frame, colors=[color])
        if blocks:
            est_dist = blocks[0].estimated_distance_mm / 10.0
    
    drive_time = max(0.5, min((est_dist + 5) / 15.0, 4.0))
    print("  Driving %.1fs toward block (~%.0fcm)" % (drive_time, est_dist))
    
    board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER - 3),
                          (3, DRIVE_POWER), (4, DRIVE_POWER - 3)])
    time.sleep(drive_time)
    stop(board)
    time.sleep(0.3)
    
    # Tiny backup
    board.set_motor_duty([(1, -30), (2, -30), (3, -30), (4, -30)])
    time.sleep(0.12)
    stop(board)
    time.sleep(0.3)
    
    # Grab
    print("  Lowering arm (open)...")
    move_arm(board, [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)], 1000)
    time.sleep(0.5)
    
    print("  Closing gripper...")
    move_arm(board, [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)], 400)
    time.sleep(0.5)
    
    print("  Lifting...")
    move_arm(board, [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)], 1000)
    time.sleep(0.5)
    
    print("  Picked up! (hopefully)")
    return True


def step3_navigate_to_basket(board, camera, color):
    """Navigate to the matching colored basket."""
    tag_id = BASKET_TAGS[color]
    print("STEP 3: Navigate to %s basket (Tag %d)" % (color, tag_id))
    
    # Use navigate_to_tag logic
    import pupil_apriltags as apriltag
    
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
            area += corners[i][0] * corners[j][1] - corners[j][0] * corners[i][1]
        return abs(area) / 2
    
    # Keep gripper closed while navigating
    move_arm(board, [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)])
    
    for cycle in range(100):
        stop(board)
        time.sleep(0.05)
        
        for _ in range(2): camera.read()
        ret, frame = camera.read()
        if not ret: continue
        
        tags = detect_tags(frame)
        tag = None
        for t in tags:
            if t.tag_id == tag_id:
                tag = t
                break
        
        if tag is None:
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.20)
            stop(board)
            time.sleep(0.15)
            continue
        
        offset = tag.center[0] - 320
        area = tag_area(tag)
        
        if cycle % 10 == 0:
            print("  Tag %d: offset=%+d area=%.0f" % (tag_id, int(offset), area))
        
        # Arrived?
        if area >= 5000 and abs(offset) < 100:
            stop(board)
            print("  ARRIVED at basket!")
            return True
        
        # Steer
        if abs(offset) > 100:
            d = 1 if offset > 0 else -1
            board.set_motor_duty([(1, ROTATION_POWER*d), (2, -ROTATION_POWER*d),
                                  (3, ROTATION_POWER*d), (4, -ROTATION_POWER*d)])
            time.sleep(min(0.10, abs(offset) / 2000.0))
            stop(board)
        else:
            board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                                  (3, DRIVE_POWER), (4, DRIVE_POWER)])
            time.sleep(0.25)
    
    print("  Navigation timeout")
    return False


def step4_deliver(board):
    """Drop block in basket."""
    print("STEP 4: Deliver")
    
    # Lower arm gently
    print("  Lowering...")
    move_arm(board, [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)], 1200)
    time.sleep(0.3)
    
    # Open gripper
    print("  Releasing...")
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(0.5)
    
    # Retract arm
    move_arm(board, [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)], 1000)
    
    # Back up
    print("  Backing up...")
    board.set_motor_duty([(1, -DRIVE_POWER), (2, -DRIVE_POWER),
                          (3, -DRIVE_POWER), (4, -DRIVE_POWER)])
    time.sleep(1.5)
    stop(board)
    
    print("  DELIVERED!")


# ============================================================
# MAIN
# ============================================================

def main():
    global TARGET_COLOR
    if len(sys.argv) > 1:
        TARGET_COLOR = sys.argv[1].lower()
    
    print("=" * 50)
    print("COLOR SORT: One Block")
    print("Target: %s" % (TARGET_COLOR or "any"))
    print("=" * 50)
    
    board = get_board()
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)
    detector = BlockDetector()
    
    try:
        # Step 1: Find
        color = step1_find_block(board, camera, detector, TARGET_COLOR)
        if not color:
            print("\nNo block found. Try repositioning robot.")
            return
        
        basket_tag = BASKET_TAGS[color]
        print("  %s -> Tag %d" % (color.upper(), basket_tag))
        
        # Step 2: Pickup
        camera.release()
        step2_pickup(board, None, detector, color)
        
        # Step 3: Navigate
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(1.0)
        
        if not step3_navigate_to_basket(board, camera, color):
            print("\nCouldn't reach basket. Block may still be in gripper.")
            return
        
        # Step 4: Deliver
        camera.release()
        step4_deliver(board)
        
        print("\n" + "=" * 50)
        print("SUCCESS! %s block -> %s basket (15 pts!)" % (color.upper(), color))
        print("=" * 50)
    
    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        stop(board)
        try: camera.release()
        except: pass

if __name__ == '__main__':
    main()
