#!/usr/bin/env python3
"""
Start Robot - Initialize and verify robot is ready

Usage:
    python3 start_robot.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.board import get_board, PLATFORM
from lib.arm_positions import Arm


def main():
    """Initialize robot to starting position."""
    print()
    print("=" * 50)
    print("  PATHFINDER ROBOT - STARTUP")
    print("=" * 50)

    try:
        print("\n1. Connecting to board...")
        board = get_board()
        print("   Platform: %s" % PLATFORM)

        time.sleep(1)
        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            v = mv / 1000.0
            status = "good" if v >= 7.5 else ("caution" if v >= 7.0 else "LOW!")
            print("   Battery: %.2fV (%s)" % (v, status))

        print("\n2. Startup beep...")
        try:
            board.set_buzzer(1)
            time.sleep(0.1)
            board.set_buzzer(0)
            time.sleep(0.2)
            board.set_buzzer(1)
            time.sleep(0.1)
            board.set_buzzer(0)
        except Exception:
            pass

        print("\n3. Initializing arm...")
        arm = Arm(board)
        arm.camera_forward()
        arm.gripper_open()
        time.sleep(0.5)

        print("\n4. Robot ready!")
        try:
            from lib.sonar import Sonar
            sonar = Sonar()
            sonar.set_led_color(0, 255, 0)  # Green = ready
            time.sleep(2)
            sonar.off()
        except Exception:
            pass

        print()
        print("=" * 50)
        print("  STARTUP COMPLETE")
        print("=" * 50)
        print()

    except Exception as e:
        print("\nFAIL: %s" % e)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
