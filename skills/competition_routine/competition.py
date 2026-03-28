#!/usr/bin/env python3
"""
Competition Routine (E7) - Full Autonomous Scoring Cycle

Chains all skills into one complete cycle:
  1. PICKUP:  Scan for block → approach → grab (E5)
  2. FIND LINE: Rotate to find lime green tape
  3. FOLLOW:  Follow green line to scoring zone (E6)
  4. DELIVER: Open gripper to release block
  5. RETURN:  Back up from scoring zone

This is the grand integration — D1 + D3 + D4 + E3 + E4 + E5 + E6
all working together in one autonomous routine.

State machine:
  IDLE → PICKUP → FIND_LINE → FOLLOW → DELIVER → RETURN → (repeat or done)

Error recovery:
  - Block not found → rotate full 360, try again, then give up
  - Block lost mid-approach → restart pickup phase
  - Line not found → rotate 360 to search
  - Battery low → abort safely (retract arm, stop motors)

Usage:
    python3 competition.py            # One full cycle, any color
    python3 competition.py red        # Target red blocks only
    python3 competition.py red 3      # 3 cycles targeting red
"""

import sys
import os
import cv2
import time

# Add project root for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM
from skills.block_detect import BlockDetector
from skills.line_following.line_follower import LineFollower


# === CONFIGURATION ===

# Motor speeds
MOTOR_POWER = 30
ROTATION_POWER = 35  # Must be high enough to overcome friction (28 too weak)

# Battery thresholds
BATTERY_MIN = 7.0 if PLATFORM == 'pi4' else 8.1

# Arm positions (tested on real hardware)
POS_CAMERA_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CAMERA_DOWN    = [(1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
POS_PICKUP_READY   = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]  # Gripper OPEN while lowering
POS_PICKUP_GRAB    = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]  # Then close to grab
POS_PICKUP_LIFT    = [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CARRY          = [(1, 1558), (3, 569), (4, 2400), (5, 809), (6, 1500)]

# Down-view approach parameters
DOWN_VIEW_CENTER_X = 350
DOWN_VIEW_TARGET_Y = 350
DOWN_VIEW_X_TOL = 80
DOWN_VIEW_Y_TOL = 50
DOWN_VIEW_MIN_Y = 50


# === HELPER FUNCTIONS ===

def stop(board):
    """Stop all motors immediately."""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def move_arm(board, position, duration_ms=800):
    """Move arm to position and wait for completion."""
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.2)


def get_fresh_frame(camera, flush=3):
    """Flush camera buffer and get a clean frame (no motion blur)."""
    for _ in range(flush):
        camera.read()
    ret, frame = camera.read()
    return frame if ret else None


def check_battery(board):
    """Check battery voltage. Returns voltage or exits if too low."""
    time.sleep(0.5)
    for _ in range(5):
        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            v = mv / 1000.0
            if v < BATTERY_MIN:
                print("  [!!] BATTERY LOW: %.2fV (min %.1fV)" % (v, BATTERY_MIN))
                return v, False
            return v, True
        time.sleep(0.3)
    print("  [!!] Could not read battery")
    return 0, True  # Continue if can't read (might be a glitch)


# === PHASE 1: PICKUP (from auto_pickup.py logic) ===

def scan_for_block(board, camera, detector, color=None):
    """
    Rotate with camera forward to find a block.
    
    Returns:
        True if block found and robot is roughly facing it.
    """
    print("  Scanning for blocks...")
    move_arm(board, POS_CAMERA_FORWARD, 800)
    time.sleep(0.5)

    for step in range(24):  # Up to 24 steps to find and face block
        frame = get_fresh_frame(camera)
        if frame is None:
            continue

        colors = [color] if color else None
        blocks = detector.detect(frame, colors=colors)

        if blocks:
            b = blocks[0]
            print("    Step %d: %s at %dcm, offset=%+dpx" % (
                step, b.color, b.estimated_distance_mm / 10,
                b.offset_from_center))

            # Block roughly centered? (within 100px of center)
            if abs(b.offset_from_center) < 100:
                print("    FACING BLOCK")
                return True

            # Rotate TOWARD the block (negative offset = block is left = rotate left)
            if b.offset_from_center < 0:
                # Block is left, rotate left (negative motor 1&3)
                board.set_motor_duty([(1, -ROTATION_POWER), (2, ROTATION_POWER),
                                      (3, -ROTATION_POWER), (4, ROTATION_POWER)])
            else:
                # Block is right, rotate right
                board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                      (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            
            # Shorter rotation when close to centered
            duration = 0.10 if abs(b.offset_from_center) < 200 else 0.20
            time.sleep(duration)
            stop(board)
            time.sleep(0.3)
        else:
            # No block visible — blind rotate to search
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.25)
            stop(board)
            time.sleep(0.4)

    print("    No block found/centered after scan")
    return False


def approach_block(board, camera, detector, color=None):
    """
    Stop-look-drive approach with camera down.
    Drives in short bursts, detects only while stopped (no motion blur).
    
    Returns:
        True if block is in pickup position.
    """
    print("  Approaching block...")
    move_arm(board, POS_CAMERA_DOWN, 800)
    time.sleep(0.5)

    lost_count = 0

    for cycle in range(40):
        # STOP (eliminates motion blur for detection)
        stop(board)
        time.sleep(0.2)

        # LOOK (capture clean frame while stationary)
        frame = get_fresh_frame(camera)
        if frame is None:
            continue

        colors = [color] if color else None
        blocks = detector.detect(frame, colors=colors)
        # Filter false positives in camera-down view:
        #   - Ignore very top of frame (walls/far objects above y=30)
        #   - Require minimum confidence (floor gives low-conf noise)
        blocks = [b for b in blocks
                  if b.center_y > 30
                  and b.confidence >= 0.3]

        if not blocks:
            lost_count += 1
            if lost_count > 3:
                # Search by rotating — alternate direction every other search
                direction = 1 if (lost_count // 3) % 2 == 0 else -1
                if lost_count % 3 == 0:
                    print("    Cycle %d: Lost block, searching..." % cycle)
                board.set_motor_duty([(1, ROTATION_POWER * direction),
                                      (2, -ROTATION_POWER * direction),
                                      (3, ROTATION_POWER * direction),
                                      (4, -ROTATION_POWER * direction)])
                time.sleep(0.20)
                stop(board)
                time.sleep(0.3)
                if lost_count > 15:
                    lost_count = 0  # Reset to keep trying
            continue

        lost_count = 0
        b = blocks[0]

        error_x = b.center_x - DOWN_VIEW_CENTER_X
        error_y = DOWN_VIEW_TARGET_Y - b.center_y

        if cycle % 5 == 0:
            print("    Cycle %d: %s at (%d,%d) err=(%+d,%+d)" % (
                cycle, b.color, b.center_x, b.center_y, error_x, error_y))

        # ARRIVED? Block at target position
        if abs(error_x) < DOWN_VIEW_X_TOL and abs(error_y) < DOWN_VIEW_Y_TOL:
            print("    ARRIVED at block")
            return True

        # DRIVE (short burst based on distance)
        if abs(error_x) > DOWN_VIEW_X_TOL:
            # Rotate to center block horizontally
            # Scale rotation duration by how far off-center the block is
            d = 1 if error_x > 0 else -1
            rot_duration = min(0.20, abs(error_x) / 1500.0)  # Longer for bigger offsets
            rot_duration = max(0.06, rot_duration)
            board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                  (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
            time.sleep(rot_duration)
            stop(board)
        elif error_y > 0:
            # Drive forward (shorter bursts when closer to target)
            # Block at top of frame = far → longer burst
            # Block near target Y = close → tiny burst
            if b.center_y > 300:
                dur = 0.08  # Very close, tiny adjustment
            elif b.center_y > 200:
                dur = 0.15
            elif b.center_y > 100:
                dur = 0.30  # Moderate distance
            else:
                dur = 0.50  # Block at top of frame, drive more
            board.set_motor_duty([(1, MOTOR_POWER), (2, MOTOR_POWER),
                                  (3, MOTOR_POWER), (4, MOTOR_POWER)])
            time.sleep(dur)
            stop(board)

    print("    Approach timeout")
    return False


def pickup_block(board):
    """Execute pre-tested arm sequence: lower, grab, lift, carry."""
    print("  Picking up block...")

    print("    Lowering arm...")
    move_arm(board, POS_PICKUP_READY, 1000)
    time.sleep(0.5)

    print("    Grabbing...")
    move_arm(board, POS_PICKUP_GRAB, 400)
    time.sleep(0.3)

    print("    Lifting...")
    move_arm(board, POS_PICKUP_LIFT, 1000)
    time.sleep(0.5)

    print("    Carry position...")
    move_arm(board, POS_CARRY, 800)

    print("    PICKUP COMPLETE")


# === PHASE 2: FIND LINE ===

def find_green_line(board, camera, follower):
    """
    Rotate to find the lime green tape line.
    Uses LineFollower's detection to check each angle.
    
    Returns:
        True if line found.
    """
    print("  Searching for green line...")
    
    # Position camera down to see the floor.
    # Keep gripper closed (servo 1 = 1475) while repositioning other servos.
    # This lets us look at the floor while still holding the block.
    camera_down_with_block = [(1, 1475), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
    move_arm(board, camera_down_with_block, 800)
    time.sleep(1.0)

    for step in range(16):  # ~360 degrees
        frame = get_fresh_frame(camera)
        if frame is None:
            continue

        detection = follower.detect_line(frame)
        if detection['found']:
            print("    Found line at step %d (green=%.1f%%)" % (
                step, detection['ratio'] * 100))
            return True

        # Rotate ~22 degrees
        board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                              (3, ROTATION_POWER), (4, -ROTATION_POWER)])
        time.sleep(0.2)
        stop(board)
        time.sleep(0.3)

    print("    Line not found after 360 scan")
    return False


# === PHASE 3: DELIVER ===

def deliver_block(board):
    """Open gripper to release block, then back up."""
    print("  Delivering block...")

    # Open gripper to release
    print("    Opening gripper...")
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(0.8)

    # Back up from scoring zone
    print("    Backing up...")
    board.set_motor_duty([(1, -MOTOR_POWER), (2, -MOTOR_POWER),
                          (3, -MOTOR_POWER), (4, -MOTOR_POWER)])
    time.sleep(1.5)
    stop(board)

    # Return arm to rest
    move_arm(board, POS_CAMERA_FORWARD, 800)

    print("    DELIVERY COMPLETE")


# === MAIN COMPETITION ROUTINE ===

def competition_cycle(color=None, verbose=True):
    """
    Run one full competition cycle:
      1. Find and pick up a block
      2. Find the green line
      3. Follow line to scoring zone
      4. Deliver (release block)
    
    Args:
        color: Target block color ('red', 'blue', 'yellow') or None for any
        verbose: Print status messages
        
    Returns:
        dict with success, phase_reached, time_taken, details
    """
    start_time = time.time()
    result = {
        'success': False,
        'phase_reached': 'init',
        'time_taken': 0,
        'color': None,
        'details': ''
    }

    board = get_board()
    
    # Battery check
    voltage, ok = check_battery(board)
    if verbose:
        print("Battery: %.2fV" % voltage)
    if not ok:
        result['details'] = 'battery_low'
        return result

    # Open camera (shared across all phases)
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    detector = BlockDetector()
    follower = LineFollower(board)
    follower.camera = camera  # Share camera instance

    try:
        # === PHASE 1: PICKUP ===
        # Use the proven auto_pickup module which handles the full
        # scan → face → camera-down → stop-look-drive → grab sequence.
        # It was tuned on real hardware and handles the camera-down
        # field of view limitations better than our custom approach.
        if verbose:
            print()
            print("PHASE 1: PICKUP (using auto_pickup)")
            print("-" * 40)

        result['phase_reached'] = 'pickup'
        
        # Release shared camera — auto_pickup manages its own
        camera.release()
        
        from skills.auto_pickup import auto_pickup as run_pickup
        pickup_ok = run_pickup(color=color)
        
        # Reopen camera for phases 2-4
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(1.0)
        follower.camera = camera
        
        if not pickup_ok:
            result['details'] = 'pickup_failed'
            return result
        
        result['color'] = color or 'unknown'

        # === PHASE 2: FIND LINE ===
        if verbose:
            print()
            print("PHASE 2: FIND LINE")
            print("-" * 40)

        result['phase_reached'] = 'find_line'
        if not find_green_line(board, camera, follower):
            result['details'] = 'line_not_found'
            return result

        # === PHASE 3: FOLLOW LINE ===
        if verbose:
            print()
            print("PHASE 3: FOLLOW LINE")
            print("-" * 40)

        result['phase_reached'] = 'follow'
        
        def follow_callback(detection, steer):
            if verbose:
                print("    cx=%3d err=%+4d steer=%+5.1f" % (
                    detection['cx'], detection['error'], steer))

        # Override follower's arm position to keep gripper closed while following
        follower.ARM_CAMERA_DOWN = [(1, 1475), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
        
        follow_result = follower.follow(
            timeout=20,
            position_camera=False,  # Already in camera-down from find_line
            search_first=False,     # Already found the line
            callback=follow_callback
        )

        if follow_result['reason'] not in ('line_ended', 'timeout'):
            result['details'] = 'follow_failed: %s' % follow_result['reason']
            return result

        # === PHASE 4: DELIVER ===
        if verbose:
            print()
            print("PHASE 4: DELIVER")
            print("-" * 40)

        result['phase_reached'] = 'deliver'
        deliver_block(board)

        # === SUCCESS ===
        result['success'] = True
        result['phase_reached'] = 'complete'
        result['time_taken'] = time.time() - start_time
        result['details'] = 'full_cycle_complete'

        return result

    except KeyboardInterrupt:
        stop(board)
        result['details'] = 'interrupted'
        return result

    except Exception as e:
        stop(board)
        result['details'] = 'error: %s' % str(e)
        import traceback
        traceback.print_exc()
        return result

    finally:
        stop(board)
        result['time_taken'] = time.time() - start_time
        camera.release()


# === ENTRY POINT ===

if __name__ == '__main__':
    # Parse arguments
    color = None
    cycles = 1

    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 competition.py [red|blue|yellow] [cycles]")
            sys.exit(1)

    if len(sys.argv) > 2:
        cycles = int(sys.argv[2])

    print("=" * 60)
    print("COMPETITION ROUTINE (E7)")
    print("=" * 60)
    print()
    print("Target: %s" % (color or "any color"))
    print("Cycles: %d" % cycles)
    print("Platform: %s" % PLATFORM)
    print()

    total_success = 0

    for cycle_num in range(1, cycles + 1):
        if cycles > 1:
            print()
            print("========== CYCLE %d/%d ==========" % (cycle_num, cycles))

        result = competition_cycle(color=color)

        print()
        print("=" * 60)
        if result['success']:
            print("CYCLE %d: SUCCESS! (%.1fs)" % (cycle_num, result['time_taken']))
            total_success += 1
        else:
            print("CYCLE %d: FAILED at %s (%s)" % (
                cycle_num, result['phase_reached'], result['details']))
        print("=" * 60)

    if cycles > 1:
        print()
        print("FINAL SCORE: %d/%d cycles completed" % (total_success, cycles))
