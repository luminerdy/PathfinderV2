#!/usr/bin/env python3
"""
Robotic Arm Demo (D3 - Level 2: Named Positions)

Demonstrates arm control through pre-defined servo positions.
Each position is a set of PWM values for the 5 servos.

Servo mapping:
  Servo 1: Gripper/Claw  (1475=closed, 2500=open)
  Servo 3: Wrist          (500-2500, controls pitch)
  Servo 4: Elbow          (500-2500, bends arm)
  Servo 5: Shoulder       (500-2500, raises/lowers arm)
  Servo 6: Base           (500-2500, 1500=center, rotates left/right)
  Note: Servo 2 does not exist on this platform.

Usage:
    python3 run_demo.py
"""

import sys
import os
import time

# Add project root for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board

# Named positions: pre-tested servo PWM values that are safe
# Format: list of (servo_id, pwm_value) tuples
# These were calibrated on real hardware — don't change unless you test first!
POSITIONS = {
    'rest': {
        'description': 'Compact, safe pose (arm tucked)',
        'servos': [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)],
    },
    'home': {
        'description': 'Neutral starting position (arm centered)',
        'servos': [(1, 2500), (3, 1200), (4, 1500), (5, 1500), (6, 1500)],
    },
    'forward': {
        'description': 'Reach forward (arm extended)',
        'servos': [(1, 2500), (3, 1200), (4, 1800), (5, 1200), (6, 1500)],
    },
    'pickup': {
        'description': 'Low position, ready to grab (arm down)',
        'servos': [(1, 2500), (3, 590), (4, 2450), (5, 1200), (6, 1500)],
    },
    'carry': {
        'description': 'Hold object while moving (gripper closed, arm up)',
        'servos': [(1, 1475), (3, 1000), (4, 1800), (5, 800), (6, 1500)],
    },
}


def move_to(board, position_name, duration_ms=1000):
    """Move arm to a named position.

    Args:
        board: Board controller from get_board()
        position_name: Key from POSITIONS dict
        duration_ms: Time in milliseconds to reach position (slower = smoother)
    """
    pos = POSITIONS[position_name]
    # set_servo_position moves all listed servos simultaneously
    # over the given duration — hardware handles interpolation
    board.set_servo_position(duration_ms, pos['servos'])
    # Wait for movement to complete, plus a small buffer
    time.sleep(duration_ms / 1000.0 + 0.3)


def main():
    """Demonstrate arm positions, gripper control, and base rotation."""

    print("=" * 60)
    print("ROBOTIC ARM DEMO - Named Positions")
    print("=" * 60)
    print()
    print("This demo moves the arm through pre-defined positions.")
    print("Each position is safe and tested on real hardware.")
    print()
    print("Press Ctrl+C to stop at any time.")
    print("-" * 60)
    print()

    # get_board() auto-detects Pi 4 (I2C) vs Pi 5 (serial)
    board = get_board()

    try:
        # --- Demo 1: Named Positions ---
        # Move through a sequence of pre-tested positions.
        # Each position is a set of servo PWM values that won't cause collision.
        print("[Demo 1] Named Positions")
        print()

        sequence = ['home', 'rest', 'forward', 'pickup', 'carry', 'home']

        for pos_name in sequence:
            pos = POSITIONS[pos_name]
            print("  Moving to '%s' - %s" % (pos_name, pos['description']))
            move_to(board, pos_name, duration_ms=1500)

        print("  [OK] Named positions complete!")
        print()
        time.sleep(0.5)

        # --- Demo 2: Gripper Control ---
        # Gripper is Servo 1: PWM 2500 = fully open, 1475 = fully closed.
        # Values between give partial grip (useful for fragile objects).
        print("[Demo 2] Gripper Control")
        print()

        move_to(board, 'forward', duration_ms=1500)

        print("  Opening gripper (PWM 2500)...")
        board.set_servo_position(500, [(1, 2500)])
        time.sleep(1)

        print("  Closing gripper (PWM 1475)...")
        board.set_servo_position(500, [(1, 1475)])
        time.sleep(1)

        # Partial grip: interpolate between open (2500) and closed (1475)
        # 50% = 2500 - (2500-1475)*0.5 = 1988
        partial_pwm = int(2500 - (2500 - 1475) * 0.5)
        print("  Partial grip 50%% (PWM %d)..." % partial_pwm)
        board.set_servo_position(500, [(1, partial_pwm)])
        time.sleep(1)

        print("  Opening again...")
        board.set_servo_position(500, [(1, 2500)])
        time.sleep(1)

        print("  [OK] Gripper control complete!")
        print()
        time.sleep(0.5)

        # --- Demo 3: Base Rotation ---
        # Servo 6 rotates the entire arm. 1500 = center.
        # Lower values = rotate left, higher = rotate right.
        print("[Demo 3] Base Rotation")
        print()

        move_to(board, 'home', duration_ms=1000)

        print("  Rotating left (PWM 1200)...")
        board.set_servo_position(800, [(6, 1200)])
        time.sleep(1)

        print("  Rotating right (PWM 1800)...")
        board.set_servo_position(800, [(6, 1800)])
        time.sleep(1)

        print("  Back to center (PWM 1500)...")
        board.set_servo_position(800, [(6, 1500)])
        time.sleep(1)

        print("  [OK] Base rotation complete!")
        print()

        # --- Return to rest ---
        print("Returning to rest position...")
        move_to(board, 'rest', duration_ms=1500)

        print()
        print("=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("What you learned:")
        print("  [OK] Named positions (home, rest, forward, pickup, carry)")
        print("  [OK] Gripper control (open=2500, closed=1475, partial grip)")
        print("  [OK] Base rotation (servo 6: left, center, right)")
        print("  [OK] Servo PWM: 500-2500 range, 1500=center for most servos")
        print()
        print("Next steps:")
        print("  - Try action groups: python3 play_action.py shake_head")
        print("  - Read SKILL.md for IK and pick-and-place programming")

    except KeyboardInterrupt:
        print("\n\nDemo stopped by user (Ctrl+C)")

    except Exception as e:
        print("\n\nERROR: %s" % e)
        import traceback
        traceback.print_exc()

    finally:
        # Always return to rest — prevents arm from staying in awkward position
        # that could strain servos or tip the robot
        print("\nReturning to rest...")
        try:
            move_to(board, 'rest', duration_ms=1000)
        except Exception:
            pass
        print("Done.")


if __name__ == "__main__":
    main()
