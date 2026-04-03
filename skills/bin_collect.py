#!/usr/bin/env python3
"""
Bin Collect - Pick up blocks and drop them into a rear-mounted bin

Strategy:
  1. Use bump_grab to pick up a block (front camera, forward arm)
  2. Fold arm backward over chassis (vendor positions)
  3. Open gripper to drop block into bin
  4. Fold arm back to forward, ready for next pickup

Usage (with Robot):
    from robot import Robot
    from skills.bin_collect import bin_collect
    robot = Robot()
    bin_collect(robot, count=3, color='yellow')

Usage (standalone):
    python3 bin_collect.py 3 yellow
    python3 bin_collect.py --test-arm

SAFETY: Robot will drive and move arm! Clear workspace.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib.board import get_board, PLATFORM
from lib.arm_positions import Arm


# === MAIN FUNCTIONS ===

def drop_in_bin(robot):
    """Fold arm backward and drop block into rear bin.
    
    Args:
        robot: Robot instance (uses robot.arm)
    """
    if hasattr(robot, 'arm') and isinstance(robot.arm, Arm):
        print("  Folding arm backward over bin...")
        robot.arm.backward_drop()
        print("  BLOCK IN BIN!")
    else:
        # Fallback for raw board
        board = robot.board if hasattr(robot, 'board') else robot
        from lib.arm_positions import POS_BACKWARD_FOLD, POS_BACKWARD_DROP, POS_CAMERA_FORWARD
        board.set_servo_position(2000, POS_BACKWARD_FOLD)
        time.sleep(2.3)
        board.set_servo_position(500, POS_BACKWARD_DROP)
        time.sleep(0.7)
        board.set_servo_position(1500, POS_CAMERA_FORWARD)
        time.sleep(1.6)
        print("  BLOCK IN BIN!")


def bin_collect(robot_or_count=None, count=1, color=None):
    """
    Collect blocks into rear-mounted bin.
    
    Accepts either:
        bin_collect(robot, count=3, color='red')   # Robot-based
        bin_collect(count=3, color='red')           # Standalone
    
    Returns:
        Number of blocks successfully collected.
    """
    from robot import Robot as RobotClass
    
    if isinstance(robot_or_count, RobotClass):
        return _bin_collect_robot(robot_or_count, count, color)
    elif isinstance(robot_or_count, int):
        return _bin_collect_standalone(robot_or_count, color)
    else:
        return _bin_collect_standalone(count, color)


def _bin_collect_robot(robot, count=1, color=None):
    """Collect blocks using Robot instance."""
    from skills.bump_grab import bump_grab
    
    print("=" * 60)
    print("BIN COLLECT")
    print("Platform: %s" % robot.platform)
    print("Target: %d x %s blocks" % (count, color or "any color"))
    print("=" * 60)
    print()
    
    if not robot.battery_ok:
        print("BATTERY TOO LOW")
        return 0
    print("Battery: %.2fV" % robot.battery)
    print()
    
    collected = 0
    
    try:
        for i in range(count):
            print("-" * 40)
            print("BLOCK %d of %d" % (i + 1, count))
            print("-" * 40)
            print()
            
            if not bump_grab(robot, color=color):
                print("Pickup failed. Stopping collection.")
                break
            
            print()
            drop_in_bin(robot)
            collected += 1
            print()
            
            if not robot.battery_ok:
                print("BATTERY LOW - stopping collection")
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        robot.stop()
    
    print()
    print("=" * 60)
    print("COLLECTED %d / %d blocks" % (collected, count))
    print("=" * 60)
    return collected


def _bin_collect_standalone(count=1, color=None):
    """Standalone bin collect (creates own hardware)."""
    from skills.bump_grab import bump_grab
    
    print("=" * 60)
    print("BIN COLLECT (standalone)")
    print("Platform: %s" % PLATFORM)
    print("Target: %d x %s blocks" % (count, color or "any color"))
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
            return 0
    print()
    
    collected = 0
    
    try:
        for i in range(count):
            print("-" * 40)
            print("BLOCK %d of %d" % (i + 1, count))
            print("-" * 40)
            
            if not bump_grab(color=color):
                print("Pickup failed.")
                break
            
            print()
            print("  Backward drop...")
            arm.backward_drop()
            print("  BLOCK IN BIN!")
            collected += 1
            print()
            
            mv = board.get_battery()
            if mv and 5000 < mv < 20000 and mv / 1000.0 < battery_min:
                print("BATTERY LOW")
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    finally:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
    print("COLLECTED %d / %d blocks" % (collected, count))
    return collected


# === ARM TEST MODE ===

def test_arm_positions():
    """Test arm positions for bin drop calibration."""
    board = get_board()
    arm = Arm(board)
    
    print("ARM POSITION TEST")
    print("=" * 40)
    print()
    
    print("1. Camera forward...")
    arm.camera_forward()
    input("   Press Enter...")
    
    print("2. Carry position...")
    arm.carry()
    input("   Press Enter...")
    
    print("3. Backward fold over bin...")
    arm.backward_drop()
    input("   Press Enter...")
    
    print("4. Back to forward...")
    arm.look_forward()
    
    print("DONE.")


# === CLI ===

if __name__ == '__main__':
    if '--test-arm' in sys.argv:
        try:
            test_arm_positions()
        finally:
            board = get_board()
            board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        sys.exit(0)
    
    count = 1
    color = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            count = int(arg)
        elif arg.lower() in ('red', 'blue', 'yellow'):
            color = arg.lower()
    
    bin_collect(count=count, color=color)
