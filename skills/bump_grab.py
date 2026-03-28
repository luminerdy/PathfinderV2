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

Usage:
    python3 bump_grab.py              # Any color
    python3 bump_grab.py red          # Red only
    python3 bump_grab.py yellow       # Yellow only
"""

import sys
import os
import cv2
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from skills.block_detect import BlockDetector

# === CONFIG ===

ROTATION_POWER = 35
DRIVE_POWER = 45          # Needs real torque especially at low battery
CENTER_TOLERANCE = 80     # Pixels from center to count as "centered"
VANISH_FRAMES = 4         # Frames without detection = "contact"
BACKUP_TIME = 0.25        # Seconds to back up after contact (~1 inch)
BACKUP_POWER = 30

BATTERY_MIN = 7.0 if PLATFORM == 'pi4' else 8.1

# Arm positions
POS_CAMERA_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_PICKUP_DOWN    = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]  # Gripper OPEN
POS_PICKUP_GRAB    = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]  # Gripper CLOSED
POS_LIFT           = [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CARRY          = [(1, 1475), (3, 569), (4, 2400), (5, 809), (6, 1500)]

FRAME_CENTER_X = 320


# === HELPERS ===

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def move_arm(board, position, duration_ms=800):
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)


def get_fresh_frame(camera, flush=3):
    """Flush buffer and get clean frame."""
    for _ in range(flush):
        camera.read()
    ret, frame = camera.read()
    return frame if ret else None


# === PHASE 1: SCAN - Find and face a block ===

def scan_and_face(board, camera, detector, color=None):
    """
    Rotate to find a block and face it (center in frame).
    
    Returns:
        True if facing a block within CENTER_TOLERANCE.
    """
    print("PHASE 1: Scan and face block")
    print("-" * 40)
    
    move_arm(board, POS_CAMERA_FORWARD, 800)
    time.sleep(0.5)
    
    for step in range(24):
        frame = get_fresh_frame(camera)
        if frame is None:
            continue
        
        colors = [color] if color else None
        blocks = detector.detect(frame, colors=colors)
        
        if blocks:
            b = blocks[0]
            offset = b.offset_from_center
            
            print("  Step %d: %s at %dcm, offset=%+dpx" % (
                step, b.color, b.estimated_distance_mm / 10, offset))
            
            # Centered enough?
            if abs(offset) < CENTER_TOLERANCE:
                print("  FACING BLOCK")
                return True
            
            # Rotate toward block
            if offset < 0:
                board.set_motor_duty([(1, -ROTATION_POWER), (2, ROTATION_POWER),
                                      (3, -ROTATION_POWER), (4, ROTATION_POWER)])
            else:
                board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                      (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            
            # Shorter rotation when close to centered
            duration = 0.08 if abs(offset) < 150 else 0.15
            time.sleep(duration)
            stop(board)
            time.sleep(0.3)
        else:
            # Blind rotate to search
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.25)
            stop(board)
            time.sleep(0.3)
    
    print("  No block found")
    return False


# === PHASE 2: DRIVE WITH CAMERA TRACKING ===

# Camera tilt range (servo 5 = shoulder)
TILT_FORWARD = 700     # Camera looks ahead (block far away)
TILT_DOWN = 1200       # Camera looks at floor (block at robot)
TILT_TARGET_Y = 300    # Keep block at this Y position by tilting

# When servo 5 reaches this value AND block is centered, block is at gripper
TILT_GRAB_READY = 1150


def drive_with_tracking(board, camera, detector, color=None):
    """
    Drive toward block while gradually tilting camera down to keep
    the block in view the entire approach.
    
    Two proportional controllers running together:
      Horizontal: block offset → steer left/right (motors)
      Vertical:   block Y position → tilt camera up/down (servo 5)
    
    When camera is tilted fully down AND block is centered = grab position.
    
    Returns:
        True if block is in grab position.
    """
    print("PHASE 2: Drive with camera tracking")
    print("-" * 40)
    
    current_tilt = TILT_FORWARD  # Start looking ahead
    vanish_count = 0
    
    for cycle in range(100):  # ~20 seconds max
        # Stop briefly for clean frame
        stop(board)
        time.sleep(0.08)
        
        frame = get_fresh_frame(camera, flush=2)
        if frame is None:
            continue
        
        colors = [color] if color else None
        blocks = detector.detect(frame, colors=colors)
        
        if not blocks:
            vanish_count += 1
            if vanish_count >= 6:
                # Block completely lost
                stop(board)
                if current_tilt > TILT_GRAB_READY:
                    # Camera was tilted far down — block is probably at robot
                    print("  Cycle %d: Block vanished at tilt %d - CONTACT!" % (
                        cycle, current_tilt))
                    return True
                else:
                    print("  Cycle %d: Block lost (tilt=%d, not close enough)" % (
                        cycle, current_tilt))
                    # Tilt back up to try to find it
                    current_tilt = max(TILT_FORWARD, current_tilt - 100)
                    board.set_servo_position(300, [(5, current_tilt)])
                    time.sleep(0.3)
            else:
                # Brief loss — keep driving slowly
                board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                                      (3, DRIVE_POWER), (4, DRIVE_POWER)])
                time.sleep(0.08)
            continue
        
        vanish_count = 0
        b = blocks[0]
        
        # === VERTICAL: Tilt camera to keep block at target Y ===
        # Block too low in frame (y > target) → tilt down more
        # Block too high in frame (y < target) → tilt up
        y_error = b.center_y - TILT_TARGET_Y
        tilt_adjust = int(y_error * 0.8)  # Proportional gain for tilt
        
        new_tilt = current_tilt + tilt_adjust
        new_tilt = max(TILT_FORWARD, min(TILT_DOWN, new_tilt))
        
        if abs(new_tilt - current_tilt) > 10:
            current_tilt = new_tilt
            board.set_servo_position(200, [(5, current_tilt)])
        
        if cycle % 5 == 0:
            print("  Cycle %d: %s (%d,%d) area=%d tilt=%d" % (
                cycle, b.color, b.center_x, b.center_y, b.area, current_tilt))
        
        # === CHECK: Grab ready? ===
        # Camera tilted down far enough AND block centered = in position
        if current_tilt >= TILT_GRAB_READY and abs(b.offset_from_center) < CENTER_TOLERANCE:
            stop(board)
            print("  Cycle %d: GRAB READY (tilt=%d, offset=%+d)" % (
                cycle, current_tilt, b.offset_from_center))
            return True
        
        # === HORIZONTAL: Steer to center block ===
        offset = b.offset_from_center
        
        if abs(offset) > CENTER_TOLERANCE:
            d = 1 if offset > 0 else -1
            board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                  (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
            time.sleep(0.06)
            stop(board)
        else:
            # Drive forward
            board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                                  (3, DRIVE_POWER), (4, DRIVE_POWER)])
            time.sleep(0.12)
    
    stop(board)
    print("  Timeout - block not reached")
    return False


# === PHASE 3: BACKUP AND GRAB ===

def backup_and_grab(board):
    """
    Back up slightly (block was bumped/pushed into position),
    then lower arm with gripper open, close, lift.
    """
    print("PHASE 3: Backup and grab")
    print("-" * 40)
    
    # Back up ~1 inch to create clearance for gripper
    print("  Backing up...")
    board.set_motor_duty([(1, -BACKUP_POWER), (2, -BACKUP_POWER),
                          (3, -BACKUP_POWER), (4, -BACKUP_POWER)])
    time.sleep(BACKUP_TIME)
    stop(board)
    time.sleep(0.3)
    
    # Lower arm with gripper OPEN (learned: must be open to go around block)
    print("  Lowering arm (gripper open)...")
    move_arm(board, POS_PICKUP_DOWN, 1000)
    time.sleep(0.5)
    
    # Close gripper around block
    print("  Grabbing...")
    move_arm(board, POS_PICKUP_GRAB, 400)
    time.sleep(0.5)
    
    # Lift
    print("  Lifting...")
    move_arm(board, POS_LIFT, 1000)
    time.sleep(0.5)
    
    # Carry position
    print("  Carry position...")
    move_arm(board, POS_CARRY, 800)
    
    print("  GRAB COMPLETE")


# === MAIN ===

def bump_grab(color=None):
    """
    Full bump-and-grab pickup cycle.
    
    Args:
        color: 'red', 'blue', 'yellow', or None for any
        
    Returns:
        True if block grabbed (probable), False if failed
    """
    print("=" * 60)
    print("BUMP AND GRAB")
    print("Platform: %s" % PLATFORM)
    print("Target: %s" % (color or "any color"))
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
            return False
    print()
    
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)
    
    detector = BlockDetector()
    
    try:
        # Phase 1: Find and face block
        if not scan_and_face(board, camera, detector, color):
            print("\nFAILED: No block found")
            return False
        print()
        
        # Phase 2: Drive with camera tracking (tilts down as we approach)
        if not drive_with_tracking(board, camera, detector, color):
            print("\nFAILED: Could not reach block")
            return False
        print()
        
        # Phase 3: Backup and grab
        camera.release()  # Release before arm movement
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
        stop(board)
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
