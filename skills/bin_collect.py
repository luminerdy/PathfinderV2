#!/usr/bin/env python3
"""
Bin Collect - Pick up blocks and drop them into a rear-mounted bin

Strategy:
  1. Use bump_grab to pick up a block (front camera, forward arm)
  2. Rotate arm base to rear (servo 6 -> over the bin)
  3. Open gripper to drop block into bin
  4. Rotate arm back to forward, ready for next pickup

The bin is a small container mounted on the robot's back.
This lets the robot collect multiple blocks before making
a delivery run to the basket.

Usage:
    python3 bin_collect.py              # Collect one block
    python3 bin_collect.py 3            # Collect 3 blocks
    python3 bin_collect.py 3 yellow     # Collect 3 yellow blocks

SAFETY: Robot will drive and move arm! Clear workspace.

== CALIBRATION NEEDED ==
ARM_REAR_BASE must be tuned so the gripper hangs over the bin.
Run with --test-arm to cycle arm positions without driving.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from skills.bump_grab import (
    bump_grab, move_arm, stop,
    POS_CARRY, POS_CAMERA_FORWARD
)

# === CONFIG ===

# Arm position over rear bin — folds backward using shoulder/elbow/wrist
# No base rotation needed! From vendor backward_drop_block()
# Servo 6 stays at 1500 (center) the whole time
POS_OVER_BIN = [(1, 1500), (3, 2400), (4, 700), (5, 1700), (6, 1500)]

# Drop into bin: open gripper while over bin (vendor uses 2020 to release)
POS_DROP_IN_BIN = [(1, 2020), (3, 2400), (4, 700), (5, 1700), (6, 1500)]

# Return to forward after drop
POS_RETURN_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]

BATTERY_MIN = 7.0 if PLATFORM == 'pi4' else 8.1


# === ARM TEST MODE ===

def test_arm_positions(board):
    """Cycle through arm positions to calibrate bin drop.
    Run this to find the right ARM_REAR_BASE value.
    """
    print("ARM POSITION TEST")
    print("=" * 40)
    print()
    print("Arm folds backward using shoulder/elbow/wrist (no base rotation)")
    print()

    # Start from camera forward (safe known position)
    print("1. Moving to CAMERA FORWARD (home position)...")
    move_arm(board, POS_CAMERA_FORWARD, 1500)
    input("   Press Enter to continue...")

    # Go to carry (still forward)
    print("2. Moving to CARRY (simulating held block)...")
    move_arm(board, POS_CARRY, 1000)
    input("   Press Enter to continue...")

    # Fold arm backward over bin
    print("3. Folding arm BACKWARD over bin...")
    print("   Watch where the gripper ends up relative to the bin!")
    move_arm(board, POS_OVER_BIN, 2000)
    input("   Is the gripper over the bin? Press Enter to continue...")

    # Open gripper (simulating drop)
    print("4. Opening gripper (DROP)...")
    move_arm(board, POS_DROP_IN_BIN, 500)
    time.sleep(0.5)
    input("   Press Enter to continue...")

    # Return to forward
    print("5. Returning to FORWARD...")
    move_arm(board, POS_RETURN_FORWARD, 1500)

    print()
    print("DONE. Adjust POS_OVER_BIN servo values if gripper")
    print("wasn't positioned over the bin at step 3.")


# === DROP INTO BIN ===

def drop_in_bin(board):
    """Fold arm backward over chassis and drop block into bin.
    Assumes block is currently in CARRY position.
    No base rotation — arm folds back using shoulder/elbow/wrist.
    """
    print("  Folding arm backward over bin...")
    move_arm(board, POS_OVER_BIN, 2000)
    time.sleep(0.3)

    print("  Releasing block into bin...")
    move_arm(board, POS_DROP_IN_BIN, 500)
    time.sleep(0.5)

    print("  Returning arm to forward...")
    move_arm(board, POS_RETURN_FORWARD, 1500)

    print("  BLOCK IN BIN!")


# === MAIN ===

def bin_collect(count=1, color=None):
    """
    Collect blocks into rear-mounted bin.

    Args:
        count: Number of blocks to collect
        color: 'red', 'blue', 'yellow', or None for any

    Returns:
        Number of blocks successfully collected
    """
    print("=" * 60)
    print("BIN COLLECT")
    print("Platform: %s" % PLATFORM)
    print("Target: %d x %s blocks" % (count, color or "any color"))
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
            return 0
    print()

    collected = 0

    try:
        for i in range(count):
            print("-" * 40)
            print("BLOCK %d of %d" % (i + 1, count))
            print("-" * 40)
            print()

            # Phase 1: Pick up block using bump_grab
            success = bump_grab(color=color)
            if not success:
                print("Pickup failed. Stopping collection.")
                break

            # Phase 2: Drop into rear bin
            print()
            drop_in_bin(board)
            collected += 1
            print()

            # Check battery before next cycle
            mv = board.get_battery()
            if mv and 5000 < mv < 20000:
                v = mv / 1000.0
                print("Battery: %.2fV" % v)
                if v < BATTERY_MIN:
                    print("BATTERY LOW - stopping collection")
                    break

    except KeyboardInterrupt:
        print("\nInterrupted")

    finally:
        stop(board)

    print()
    print("=" * 60)
    print("COLLECTED %d / %d blocks" % (collected, count))
    print("=" * 60)
    return collected


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--test-arm']

    if '--test-arm' in sys.argv:
        board = get_board()
        try:
            test_arm_positions(board)
        finally:
            stop(board)
        sys.exit(0)

    count = 1
    color = None

    for arg in args:
        if arg.isdigit():
            count = int(arg)
        elif arg.lower() in ('red', 'blue', 'yellow'):
            color = arg.lower()
        else:
            print("Usage: python3 bin_collect.py [count] [red|blue|yellow] [--test-arm]")
            sys.exit(1)

    bin_collect(count=count, color=color)
