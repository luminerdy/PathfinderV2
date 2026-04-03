#!/usr/bin/env python3
"""
Gamepad Remote Control (D6)

Drive robot with Logitech F710 wireless gamepad.
Tank-style sticks + mecanum strafing + trigger speed + arm actions.

Arm sequences ported from PathfinderBot V1 (pf_mecanum_gamepad_drive.py)
with vendor-tested servo positions for reliable pickup/drop.

Prerequisites:
  - F710 USB receiver plugged into Robot Pi
  - Gamepad on, back switch set to X (XInput)
  - pygame installed: sudo apt install python3-pygame

Usage:
    python3 gamepad_drive.py

Controls:
  Left stick Y:   Tank drive (right side — swapped to match wiring)
  Right stick Y:  Tank drive (left side — swapped to match wiring)
  Both sticks X:  Strafe left/right
  Right trigger:  Forward (analog speed)
  Left trigger:   Backward (analog speed)
  Right bumper:   Turn right in place
  Left bumper:    Turn left in place

  D-pad Up:       Pickup block (front)
  D-pad Down:     Backward drop block (into rear bin)
  D-pad Left:     Left side pickup
  D-pad Right:    Right side pickup

  A:              Look forward (reset arm)
  B:              Look sad
  Y:              Nod yes
  X:              Shake no

  Back:           EMERGENCY STOP
  Start:          Quit
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

try:
    import pygame
except ImportError:
    print("pygame not installed. Run: sudo apt install python3-pygame")
    sys.exit(1)

from lib.board import get_board
from lib.arm_positions import Arm

# === CONFIG ===
MAX_SPEED = 50          # Maximum motor duty cycle (0-100)
TURN_SPEED = 40         # In-place turn speed
DEADZONE = 0.15         # Ignore stick values below this
POLL_RATE = 50          # Hz (20ms per loop)


# === DRIVE HELPERS ===

def apply_deadzone(value):
    """Zero out small values (stick drift)."""
    if abs(value) < DEADZONE:
        return 0.0
    return value


def clamp(value, min_val, max_val):
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


# === MAIN ===

def main():
    print("=" * 50)
    print("GAMEPAD REMOTE CONTROL (D6)")
    print("=" * 50)
    print()
    print("Initializing robot hardware...")
    board = get_board()
    arm = Arm(board)

    # Arm to forward position
    arm.look_forward()

    print("Initializing gamepad...")
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("No gamepad detected!")
        print("  - USB receiver plugged into Robot Pi?")
        print("  - Gamepad powered on (green LED)?")
        print("  - Back switch set to X (not D)?")
        pygame.quit()
        sys.exit(1)

    gamepad = pygame.joystick.Joystick(0)
    gamepad.init()
    print("Gamepad: %s" % gamepad.get_name())
    print()
    print("Controls:")
    print("  Sticks:     Tank drive + strafe")
    print("  Triggers:   Forward/backward (analog)")
    print("  Bumpers:    Turn in place")
    print("  D-pad Up:   Pickup block (front)")
    print("  D-pad Down: Drop into rear bin")
    print("  D-pad Left: Left side pickup")
    print("  D-pad Right:Right side pickup")
    print("  A/B/X/Y:   Arm expressions")
    print("  Back:       STOP  |  Start: Quit")
    print()
    print("Ready -- drive!")
    print()

    running = True
    clock = pygame.time.Clock()

    try:
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Button presses
                elif event.type == pygame.JOYBUTTONDOWN:
                    button = event.button

                    # Back = emergency stop
                    if button == 6:
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        print("STOP!")

                    # Start = quit
                    elif button == 7:
                        print("Quit")
                        running = False

                    # A = look forward (reset arm)
                    elif button == 0:
                        print("Look forward")
                        arm.look_forward()

                    # B = look sad
                    elif button == 1:
                        print("Sad")
                        arm.look_sad()

                    # Y = nod yes
                    elif button == 3:
                        print("Yes!")
                        arm.say_yes()

                    # X = shake no
                    elif button == 2:
                        print("No!")
                        arm.say_no()

                # D-pad
                elif event.type == pygame.JOYHATMOTION:
                    hat = event.value

                    # D-pad Up = front pickup
                    if hat == (0, 1):
                        print("Front pickup sequence...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.pickup_front()

                    # D-pad Down = backward drop into bin
                    elif hat == (0, -1):
                        print("Backward drop sequence...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.backward_drop()

                    # D-pad Left = left side pickup
                    elif hat == (-1, 0):
                        print("Left side pickup...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.pickup_left()

                    # D-pad Right = right side pickup
                    elif hat == (1, 0):
                        print("Right side pickup...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        arm.pickup_right()

            # --- Continuous control (sticks + triggers) ---

            # Read axes (V1 note: left/right sticks are swapped to match motor wiring)
            left_y = apply_deadzone(gamepad.get_axis(1))    # Left stick Y
            right_y = apply_deadzone(gamepad.get_axis(3))   # Right stick Y
            left_x = apply_deadzone(gamepad.get_axis(0))    # Left stick X (strafe)

            # Triggers (axis 2 = left trigger, axis 5 = right trigger on F710)
            # Triggers range: -1 (released) to +1 (fully pressed)
            left_trigger = (gamepad.get_axis(2) + 1) / 2    # Normalize 0-1
            right_trigger = (gamepad.get_axis(5) + 1) / 2   # Normalize 0-1

            # Bumpers
            left_bumper = gamepad.get_button(4)
            right_bumper = gamepad.get_button(5)

            # Calculate motor speeds
            if left_bumper:
                # Turn left in place
                fl = -TURN_SPEED
                fr = TURN_SPEED
                rl = -TURN_SPEED
                rr = TURN_SPEED
            elif right_bumper:
                # Turn right in place
                fl = TURN_SPEED
                fr = -TURN_SPEED
                rl = TURN_SPEED
                rr = -TURN_SPEED
            elif right_trigger > 0.1:
                # Trigger forward (overrides sticks)
                speed = right_trigger * MAX_SPEED
                fl = fr = rl = rr = speed
            elif left_trigger > 0.1:
                # Trigger backward
                speed = left_trigger * MAX_SPEED
                fl = fr = rl = rr = -speed
            else:
                # Tank + strafe from sticks
                strafe = left_x * MAX_SPEED
                left_speed = -left_y * MAX_SPEED
                right_speed = -right_y * MAX_SPEED

                fl = left_speed + strafe
                fr = right_speed - strafe
                rl = left_speed - strafe
                rr = right_speed + strafe

            # Clamp and send
            fl = int(clamp(fl, -MAX_SPEED, MAX_SPEED))
            fr = int(clamp(fr, -MAX_SPEED, MAX_SPEED))
            rl = int(clamp(rl, -MAX_SPEED, MAX_SPEED))
            rr = int(clamp(rr, -MAX_SPEED, MAX_SPEED))

            board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])

            clock.tick(POLL_RATE)

    except KeyboardInterrupt:
        print("\nStopped")

    finally:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        arm.look_forward()
        pygame.quit()
        print("Motors stopped, gamepad released")


if __name__ == '__main__':
    main()
