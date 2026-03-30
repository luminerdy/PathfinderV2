#!/usr/bin/env python3
"""
Full Autonomous Loop (⭐⭐⭐⭐ Expert)

Complete autonomous competition routine:
  1. Find nearest block of any color
  2. Pick it up
  3. Navigate to matching color basket
  4. Deliver
  5. Return to block zone
  6. REPEAT until time runs out or no blocks left

This is the endgame template. A working version of this can score
100+ points in a 10-minute match with autonomous bonus.

CUSTOMIZE: Change PRIORITIES for which colors to target first.
CUSTOMIZE: Adjust timing, power, and navigation parameters.
CUSTOMIZE: Add battery monitoring to return to start when low.

Usage:
    python3 full_auto.py              # Run autonomous loop
    python3 full_auto.py red          # Only target red blocks
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM
from skills.block_detect import BlockDetector

# ============================================================
# CUSTOMIZE THESE
# ============================================================

# Color priority: which blocks to target first
# Red in correct basket = 15 pts (same as others, but modify if scoring changes)
PRIORITIES = ['red', 'yellow', 'blue']

# Basket-to-tag mapping
BASKET_TAGS = {
    'blue':   578,
    'yellow': 579,
    'red':    580,
}

# Return point: tag to navigate to after delivery (back to block zone)
RETURN_TAG = 582    # South wall tag — near block zone / start zones

# Power and speed
DRIVE_POWER = 40
ROTATION_POWER = 35

# Battery — stop if too low
BATTERY_MIN = 7.2   # Return to start below this

# Timing
MAX_CYCLE_TIME = 120    # Max seconds per pickup-deliver cycle
MATCH_TIME = 600        # 10 minutes total (stop after this)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def move_arm(board, position, duration_ms=800):
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)

def get_voltage(board):
    for _ in range(3):
        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            return mv / 1000.0
        time.sleep(0.3)
    return 0

# Arm positions
POS_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_PICKUP  = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_GRAB    = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_LIFT    = [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_PLACE   = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]


# ============================================================
# REUSABLE STEPS (import or modify these)
# ============================================================

def scan_for_block(board, camera, detector, priorities):
    """Scan for blocks in priority order. Returns color or None."""
    move_arm(board, POS_FORWARD)
    
    for step in range(24):
        for _ in range(3): camera.read()
        ret, frame = camera.read()
        if not ret: continue
        
        for color in priorities:
            blocks = detector.detect(frame, colors=[color])
            if blocks and blocks[0].confidence >= 0.5:
                b = blocks[0]
                if abs(b.offset_from_center) < 80:
                    return color
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
    return None


def pickup_block(board, camera, detector, color):
    """Drive to block and grab it."""
    for _ in range(3): camera.read()
    ret, frame = camera.read()
    est = 30
    if ret:
        blocks = detector.detect(frame, colors=[color])
        if blocks: est = blocks[0].estimated_distance_mm / 10.0
    
    t = max(0.5, min((est + 5) / 15.0, 4.0))
    board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER-3),
                          (3, DRIVE_POWER), (4, DRIVE_POWER-3)])
    time.sleep(t)
    stop(board)
    
    board.set_motor_duty([(1, -30), (2, -30), (3, -30), (4, -30)])
    time.sleep(0.12)
    stop(board)
    time.sleep(0.3)
    
    move_arm(board, POS_PICKUP, 1000)
    time.sleep(0.5)
    move_arm(board, POS_GRAB, 400)
    time.sleep(0.5)
    move_arm(board, POS_LIFT, 1000)


def navigate_to_tag(board, camera, tag_id, tag_area_target=5000):
    """Navigate to an AprilTag. Returns True if reached."""
    import pupil_apriltags as apriltag
    
    move_arm(board, POS_LIFT)  # Keep holding block
    
    def detect(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        det = apriltag.Detector(families='tag36h11')
        return det.detect(gray)
    
    def area(tag):
        c = tag.corners
        a = 0
        for i in range(4):
            j = (i+1) % 4
            a += c[i][0]*c[j][1] - c[j][0]*c[i][1]
        return abs(a) / 2
    
    for cycle in range(100):
        stop(board)
        time.sleep(0.05)
        for _ in range(2): camera.read()
        ret, frame = camera.read()
        if not ret: continue
        
        tags = detect(frame)
        tag = None
        for t in tags:
            if t.tag_id == tag_id: tag = t; break
        
        if not tag:
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.20)
            stop(board)
            time.sleep(0.15)
            continue
        
        offset = tag.center[0] - 320
        a = area(tag)
        
        if a >= tag_area_target and abs(offset) < 100:
            stop(board)
            return True
        
        if abs(offset) > 100:
            d = 1 if offset > 0 else -1
            board.set_motor_duty([(1, ROTATION_POWER*d), (2, -ROTATION_POWER*d),
                                  (3, ROTATION_POWER*d), (4, -ROTATION_POWER*d)])
            time.sleep(min(0.10, abs(offset)/2000.0))
            stop(board)
        else:
            board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                                  (3, DRIVE_POWER), (4, DRIVE_POWER)])
            time.sleep(0.25)
    
    stop(board)
    return False


def deliver_block(board):
    """Gentle place into basket."""
    move_arm(board, POS_PLACE, 1200)
    time.sleep(0.3)
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(0.5)
    move_arm(board, POS_FORWARD, 1000)
    board.set_motor_duty([(1, -DRIVE_POWER), (2, -DRIVE_POWER),
                          (3, -DRIVE_POWER), (4, -DRIVE_POWER)])
    time.sleep(1.5)
    stop(board)


# ============================================================
# MAIN AUTONOMOUS LOOP
# ============================================================

def main():
    target_only = None
    if len(sys.argv) > 1:
        target_only = sys.argv[1].lower()
    
    priorities = [target_only] if target_only else PRIORITIES
    
    print("=" * 60)
    print("FULL AUTONOMOUS LOOP")
    print("Priorities: %s" % priorities)
    print("Match time: %d seconds" % MATCH_TIME)
    print("=" * 60)
    
    board = get_board()
    voltage = get_voltage(board)
    print("Battery: %.2fV" % voltage)
    
    if voltage > 0 and voltage < BATTERY_MIN:
        print("Battery too low!")
        return
    
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)
    detector = BlockDetector()
    
    match_start = time.time()
    blocks_delivered = 0
    
    try:
        while True:
            elapsed = time.time() - match_start
            remaining = MATCH_TIME - elapsed
            
            if remaining <= 0:
                print("\n  TIME'S UP!")
                break
            
            print("\n--- CYCLE %d (%.0fs remaining) ---" % (blocks_delivered + 1, remaining))
            
            # Battery check
            v = get_voltage(board)
            if v > 0 and v < BATTERY_MIN:
                print("  Battery low (%.2fV) — stopping" % v)
                break
            
            cycle_start = time.time()
            
            # STEP 1: Find block
            print("  Finding block...")
            color = scan_for_block(board, camera, detector, priorities)
            if not color:
                print("  No blocks found — done!")
                break
            
            basket_tag = BASKET_TAGS[color]
            print("  Found %s -> Tag %d" % (color.upper(), basket_tag))
            
            # STEP 2: Pickup
            print("  Picking up...")
            camera.release()
            pickup_block(board, None, detector, color)
            
            camera = cv2.VideoCapture(0)
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            time.sleep(1.0)
            
            # STEP 3: Navigate to basket
            print("  Navigating to %s basket..." % color)
            if navigate_to_tag(board, camera, basket_tag):
                # STEP 4: Deliver
                print("  Delivering...")
                camera.release()
                deliver_block(board)
                blocks_delivered += 1
                
                camera = cv2.VideoCapture(0)
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                time.sleep(1.0)
                
                cycle_time = time.time() - cycle_start
                print("  SCORED! (%s, %.1fs)" % (color.upper(), cycle_time))
            else:
                print("  Couldn't reach basket — dropping block")
                board.set_servo_position(500, [(1, 2500)])  # Open gripper
                time.sleep(0.5)
                move_arm(board, POS_FORWARD)
            
            # STEP 5: Return to block zone (optional — skip if time is short)
            if remaining > 60:
                print("  Returning to block zone...")
                navigate_to_tag(board, camera, RETURN_TAG, tag_area_target=3000)
    
    except KeyboardInterrupt:
        print("\nStopped")
    
    finally:
        stop(board)
        try: camera.release()
        except: pass
        
        elapsed = time.time() - match_start
        print()
        print("=" * 60)
        print("MATCH COMPLETE")
        print("  Blocks delivered: %d" % blocks_delivered)
        print("  Time: %.1f seconds" % elapsed)
        print("  Points (est): %d" % (blocks_delivered * 15))
        print("  Autonomous bonus: %d" % (blocks_delivered * 10))
        print("  TOTAL (est): %d" % (blocks_delivered * 25))
        print("=" * 60)


if __name__ == '__main__':
    main()
