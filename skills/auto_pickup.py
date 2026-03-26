#!/usr/bin/env python3
"""
Autonomous Block Pickup — No LLM, No SSH, Pure Python

Run on robot directly:
  cd /home/robot/pathfinder
  python3 skills/auto_pickup.py

Does everything:
  1. Scan for blocks (rotate with camera forward)
  2. Face the block
  3. Switch to camera down
  4. Stop-look-drive to block (short bursts, detect while stopped)
  5. Lower arm, grab, lift
  6. Return to camera forward (carrying block)

Handles:
  - Motion blur (only detect while stopped)
  - Camera offset between forward/down views
  - False positives (filter top of frame, min confidence)
  - Battery check
"""

import sys
import os
import cv2
import time

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from skills.block_detect import BlockDetector

# ===== CONFIG =====

MOTOR_POWER = 30
ROTATION_POWER = 30

# Camera-down view: block centered in forward view appears at ~x=350 in down view
# Calibrated from real test: forward offset=+30px → down view x=350
DOWN_VIEW_CENTER_X = 350
DOWN_VIEW_TARGET_Y = 350

DOWN_VIEW_X_TOL = 80
DOWN_VIEW_Y_TOL = 50
DOWN_VIEW_MIN_Y = 50      # Ignore detections above this (false positives from walls)

# Arm positions (tested on real hardware)
POS_CAMERA_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CAMERA_DOWN    = [(1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
POS_PICKUP_READY   = [(1, 1558), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_PICKUP_GRAB    = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_PICKUP_LIFT    = [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CARRY          = [(1, 1558), (3, 569), (4, 2400), (5, 809), (6, 1500)]

BATTERY_MIN = 7.0 if PLATFORM == 'pi4' else 8.1


# ===== HELPERS =====

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def move_arm(board, position, duration_ms=800):
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)

def get_fresh_frame(camera, flush=3):
    """Flush buffer and get a fresh frame"""
    for _ in range(flush):
        camera.read()
    ret, frame = camera.read()
    return frame if ret else None

def detect_blocks(detector, frame, color=None, min_y=0):
    """Detect blocks, optionally filter by color and min Y position"""
    colors = [color] if color else None
    blocks = detector.detect(frame, colors=colors)
    if min_y > 0:
        blocks = [b for b in blocks if b.center_y > min_y]
    return blocks

def check_battery(board):
    """Check battery, return voltage or exit if too low"""
    time.sleep(0.5)
    for _ in range(5):
        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            v = mv / 1000.0
            if v < BATTERY_MIN:
                print("BATTERY TOO LOW: %.2fV (min %.1fV)" % (v, BATTERY_MIN))
                sys.exit(1)
            return v
        time.sleep(0.3)
    print("WARNING: Could not read battery")
    return 0


# ===== PHASE 1: SCAN =====

def scan_for_block(board, camera, detector, color=None):
    """
    Rotate with camera forward to find a block.
    Returns True if block found and robot is facing it.
    """
    print("PHASE 1: Scan for block")
    print("-" * 40)
    
    move_arm(board, POS_CAMERA_FORWARD, 800)
    time.sleep(0.5)
    
    for step in range(16):  # ~360 degrees
        frame = get_fresh_frame(camera)
        if frame is None:
            continue
        
        blocks = detect_blocks(detector, frame, color)
        
        if blocks:
            b = blocks[0]
            print("  Step %d: %s at %dcm offset=%+dpx" % (
                step, b.color, b.estimated_distance_mm / 10,
                b.offset_from_center))
            
            # Block roughly centered?
            if abs(b.offset_from_center) < 100:
                print("  FACING BLOCK")
                return True
        
        # Rotate ~22 degrees
        board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                              (3, ROTATION_POWER), (4, -ROTATION_POWER)])
        time.sleep(0.2)
        stop(board)
        time.sleep(0.3)
    
    print("  No block found")
    return False


# ===== PHASE 2: APPROACH =====

def approach_block(board, camera, detector, color=None):
    """
    Stop-look-drive approach with camera down.
    Drives in short bursts, detects only while stopped.
    Returns True if block reached.
    """
    print("PHASE 2: Approach block")
    print("-" * 40)
    
    move_arm(board, POS_CAMERA_DOWN, 800)
    time.sleep(0.5)
    
    lost_count = 0
    
    for cycle in range(40):
        # STOP
        stop(board)
        time.sleep(0.2)
        
        # LOOK
        frame = get_fresh_frame(camera)
        if frame is None:
            continue
        
        blocks = detect_blocks(detector, frame, color, min_y=DOWN_VIEW_MIN_Y)
        
        if not blocks:
            lost_count += 1
            if lost_count > 5:
                # Search by rotating
                print("  Cycle %d: Lost, searching..." % cycle)
                board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                      (3, ROTATION_POWER), (4, -ROTATION_POWER)])
                time.sleep(0.15)
                stop(board)
                lost_count = 0
            continue
        
        lost_count = 0
        b = blocks[0]
        
        error_x = b.center_x - DOWN_VIEW_CENTER_X
        error_y = DOWN_VIEW_TARGET_Y - b.center_y
        
        print("  Cycle %d: %s (%d,%d) err=(%+d,%+d)" % (
            cycle, b.color, b.center_x, b.center_y, error_x, error_y))
        
        # ARRIVED?
        if abs(error_x) < DOWN_VIEW_X_TOL and abs(error_y) < DOWN_VIEW_Y_TOL:
            print("  ARRIVED")
            return True
        
        # MOVE (short burst)
        if abs(error_x) > DOWN_VIEW_X_TOL:
            # Rotate to center
            d = 1 if error_x > 0 else -1
            board.set_motor_duty([(1, MOTOR_POWER * d), (2, -MOTOR_POWER * d),
                                  (3, MOTOR_POWER * d), (4, -MOTOR_POWER * d)])
            time.sleep(0.06)
            stop(board)
        elif error_y > 0:
            # Drive forward
            if b.center_y > 300:
                dur = 0.08
            elif b.center_y > 200:
                dur = 0.15
            elif b.center_y > 100:
                dur = 0.25
            else:
                dur = 0.4
            board.set_motor_duty([(1, MOTOR_POWER), (2, MOTOR_POWER),
                                  (3, MOTOR_POWER), (4, MOTOR_POWER)])
            time.sleep(dur)
            stop(board)
    
    print("  Approach timeout")
    return False


# ===== PHASE 3: PICKUP =====

def pickup_block(board):
    """Lower arm, grab, lift."""
    print("PHASE 3: Pickup")
    print("-" * 40)
    
    print("  Lowering arm...")
    move_arm(board, POS_PICKUP_READY, 1000)
    time.sleep(0.5)
    
    print("  Grabbing...")
    move_arm(board, POS_PICKUP_GRAB, 400)
    time.sleep(0.3)
    
    print("  Lifting...")
    move_arm(board, POS_PICKUP_LIFT, 1000)
    time.sleep(0.5)
    
    print("  Carry position...")
    move_arm(board, POS_CARRY, 800)
    
    print("  PICKUP COMPLETE")


# ===== MAIN =====

def auto_pickup(color=None):
    """
    Full autonomous pickup cycle.
    
    Args:
        color: 'red', 'blue', 'yellow', or None for any
    """
    print("=" * 60)
    print("AUTONOMOUS BLOCK PICKUP")
    print("Platform: %s" % PLATFORM)
    print("Target: %s" % (color or "any color"))
    print("=" * 60)
    print()
    
    board = get_board()
    voltage = check_battery(board)
    print("Battery: %.2fV" % voltage)
    print()
    
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)
    
    detector = BlockDetector()
    
    try:
        # Phase 1: Scan
        if not scan_for_block(board, camera, detector, color):
            print()
            print("FAILED: No block found during scan")
            return False
        print()
        
        # Phase 2: Approach
        if not approach_block(board, camera, detector, color):
            print()
            print("FAILED: Could not reach block")
            return False
        print()
        
        # Phase 3: Pickup
        pickup_block(board)
        
        print()
        print("=" * 60)
        print("SUCCESS — Check if robot is holding a block!")
        print("=" * 60)
        return True
    
    except KeyboardInterrupt:
        print("\nInterrupted")
        return False
    
    except Exception as e:
        print("ERROR: %s" % e)
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        stop(board)
        camera.release()


if __name__ == '__main__':
    # Parse optional color argument
    color = None
    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 auto_pickup.py [red|blue|yellow]")
            sys.exit(1)
    
    auto_pickup(color)
