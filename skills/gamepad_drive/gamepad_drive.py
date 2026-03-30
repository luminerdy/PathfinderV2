#!/usr/bin/env python3
"""
Gamepad Remote Control (D6)

Drive robot with Logitech F710 wireless gamepad.
Tank-style sticks + mecanum strafing + trigger speed + arm actions.

Prerequisites:
  - F710 USB receiver plugged into Robot Pi
  - Gamepad on, back switch set to X (XInput)
  - pygame installed: sudo apt install python3-pygame

Usage:
    python3 gamepad_drive.py

Controls:
  Left stick Y:   Tank drive (left side)
  Right stick Y:  Tank drive (right side)
  Both sticks X:  Strafe left/right
  Right trigger:  Forward (analog)
  Left trigger:   Backward (analog)
  Right bumper:   Turn right
  Left bumper:    Turn left
  D-pad Up:       Pickup block
  D-pad Down:     Drop block
  A:              Camera forward
  B:              Camera down
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

# === CONFIG ===
MAX_SPEED = 50          # Maximum motor duty cycle (0-100)
TURN_SPEED = 40         # In-place turn speed
DEADZONE = 0.15         # Ignore stick values below this
POLL_RATE = 50          # Hz (20ms per loop)

# Arm positions
POS_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_DOWN    = [(1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
POS_PICKUP  = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_GRAB    = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_LIFT    = [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_DROP    = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]


def apply_deadzone(value):
    """Zero out small values (stick drift)."""
    if abs(value) < DEADZONE:
        return 0.0
    return value


def clamp(value, min_val, max_val):
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def main():
    print("Initializing robot hardware...")
    board = get_board()

    # Arm to forward position
    board.set_servo_position(800, POS_FORWARD)
    time.sleep(1)

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
    print("Ready -- drive with sticks, triggers, bumpers!")
    print("Back = STOP, Start = Quit")
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

                    # A = camera forward
                    elif button == 0:
                        board.set_servo_position(800, POS_FORWARD)
                        print("Camera forward")

                    # B = camera down
                    elif button == 1:
                        board.set_servo_position(800, POS_DOWN)
                        print("Camera down")

                    # Y = nod yes
                    elif button == 3:
                        for _ in range(3):
                            board.set_servo_position(200, [(5, 900)])
                            time.sleep(0.3)
                            board.set_servo_position(200, [(5, 700)])
                            time.sleep(0.3)
                        print("Yes!")

                    # X = shake no
                    elif button == 2:
                        for _ in range(3):
                            board.set_servo_position(200, [(6, 1300)])
                            time.sleep(0.3)
                            board.set_servo_position(200, [(6, 1700)])
                            time.sleep(0.3)
                        board.set_servo_position(200, [(6, 1500)])
                        print("No!")

                # D-pad
                elif event.type == pygame.JOYHATMOTION:
                    hat = event.value
                    # D-pad up = pickup
                    if hat == (0, 1):
                        print("Pickup sequence...")
                        board.set_servo_position(1000, POS_PICKUP)
                        time.sleep(1.5)
                        board.set_servo_position(400, POS_GRAB)
                        time.sleep(0.8)
                        board.set_servo_position(1000, POS_LIFT)
                        time.sleep(1.5)
                        print("Picked up!")

                    # D-pad down = drop
                    elif hat == (0, -1):
                        print("Drop sequence...")
                        board.set_servo_position(1000, POS_DROP)
                        time.sleep(1.5)
                        board.set_servo_position(500, [(1, 2500)])
                        time.sleep(0.5)
                        board.set_servo_position(800, POS_FORWARD)
                        time.sleep(1)
                        print("Dropped!")

            # --- Continuous control (sticks + triggers) ---

            # Read axes
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
        board.set_servo_position(800, POS_FORWARD)
        pygame.quit()
        print("Motors stopped, gamepad released")


if __name__ == '__main__':
    main()
