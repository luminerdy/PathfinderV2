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

# === CONFIG ===
MAX_SPEED = 50          # Maximum motor duty cycle (0-100)
TURN_SPEED = 40         # In-place turn speed
DEADZONE = 0.15         # Ignore stick values below this
POLL_RATE = 50          # Hz (20ms per loop)


# === ARM SEQUENCES (from V1 vendor-tested positions) ===
# These use Board.set_servo_position(duration_ms, [(servo_id, pulse), ...])
# Servo IDs: 1=gripper, 3=shoulder, 4=elbow, 5=wrist, 6=base rotation
# Pulse range: 500-2500 (1500=center for rotation servos)

def move_arm(board, position, duration_ms=800):
    """Move arm to position and wait for completion."""
    board.set_servo_position(duration_ms, position)
    time.sleep(duration_ms / 1000.0 + 0.1)


def look_forward(board):
    """Reset arm to standard forward-looking pose."""
    board.set_servo_position(500, [(1, 1500)])     # Gripper neutral
    board.set_servo_position(1000, [(3, 700)])     # Shoulder
    board.set_servo_position(1000, [(4, 2425)])    # Elbow
    board.set_servo_position(1000, [(5, 790)])     # Wrist
    board.set_servo_position(1000, [(6, 1500)])    # Base center
    time.sleep(1)


def look_sad(board):
    """Sad expression — arm droops down."""
    board.set_servo_position(1000, [(3, 800)])
    board.set_servo_position(1000, [(4, 2500)])
    board.set_servo_position(1000, [(5, 1900)])
    board.set_servo_position(1000, [(6, 1500)])
    time.sleep(0.5)
    board.set_servo_position(1000, [(3, 600)])


def say_yes(board):
    """Nod the arm up and down."""
    board.set_servo_position(1000, [(4, 2425)])
    board.set_servo_position(1000, [(5, 790)])
    board.set_servo_position(2000, [(3, 590)])
    time.sleep(0.2)
    for _ in range(3):
        board.set_servo_position(200, [(3, 500)])
        time.sleep(0.2)
        board.set_servo_position(200, [(3, 900)])
        time.sleep(0.2)
    board.set_servo_position(200, [(3, 700)])


def say_no(board):
    """Shake the arm side to side."""
    board.set_servo_position(1000, [(4, 2425)])
    board.set_servo_position(1000, [(5, 790)])
    time.sleep(0.2)
    for _ in range(3):
        board.set_servo_position(200, [(6, 1300)])
        time.sleep(0.2)
        board.set_servo_position(200, [(6, 1700)])
        time.sleep(0.2)
    board.set_servo_position(200, [(6, 1500)])
    time.sleep(0.2)


def pickup_block(board):
    """Front pickup — reach down, grab block, lift.
    
    Vendor-tested sequence from PathfinderBot V1.
    Robot must be positioned with block directly in front.
    Keep people clear of arm during sequence!
    """
    print("  Pickup: Reaching down...")
    # Start from forward pose with gripper neutral
    board.set_servo_position(2000, [(1, 1500)])     # Gripper half-open
    board.set_servo_position(2000, [(3, 590)])      # Shoulder up
    board.set_servo_position(2000, [(4, 2500)])     # Elbow
    board.set_servo_position(2000, [(5, 700)])      # Wrist
    board.set_servo_position(2000, [(6, 1500)])     # Base center

    # Lower wrist toward ground
    board.set_servo_position(1000, [(5, 1818)])
    time.sleep(1)

    # Position for grab
    board.set_servo_position(300, [(4, 2023)])
    board.set_servo_position(300, [(5, 2091)])
    time.sleep(0.3)

    # Open gripper wide
    board.set_servo_position(400, [(1, 1932)])
    time.sleep(0.4)

    # Lower shoulder, extend wrist to reach block
    print("  Pickup: Grabbing...")
    board.set_servo_position(800, [(3, 750)])
    board.set_servo_position(800, [(5, 2364)])
    time.sleep(0.8)

    # Close gripper on block
    board.set_servo_position(300, [(1, 1455)])
    board.set_servo_position(300, [(5, 2318)])
    time.sleep(0.3)

    # Lift block
    print("  Pickup: Lifting...")
    board.set_servo_position(1000, [(5, 1841)])
    time.sleep(1)

    look_forward(board)
    print("  Pickup complete!")


def backward_drop_block(board):
    """Drop block into rear-mounted bin.
    
    Folds arm backward over chassis using shoulder/elbow/wrist.
    No base rotation — arm reaches over the top.
    Vendor-tested sequence from PathfinderBot V1.
    """
    print("  Backward drop: Folding arm back...")
    # Fold arm backward (gripper stays closed)
    board.set_servo_position(2000, [(1, 1500)])     # Gripper closed
    board.set_servo_position(2000, [(3, 2400)])     # Shoulder back
    board.set_servo_position(2000, [(4, 700)])      # Elbow inverted
    board.set_servo_position(2000, [(5, 1700)])     # Wrist adjusted
    time.sleep(2)

    # Open gripper to release block into bin
    print("  Backward drop: Releasing...")
    board.set_servo_position(2000, [(1, 2020)])
    time.sleep(2.1)

    look_forward(board)
    print("  Backward drop complete!")


def left_pickup_block(board):
    """Pick up block from left side.
    
    Rotates base to left (servo 6=2500), reaches down, grabs.
    Vendor-tested sequence from PathfinderBot V1.
    """
    print("  Left pickup: Reaching left...")
    board.set_servo_position(1000, [(1, 2020)])     # Gripper open
    board.set_servo_position(1000, [(3, 800)])      # Shoulder
    board.set_servo_position(1000, [(4, 2020)])     # Elbow
    board.set_servo_position(1000, [(5, 2091)])     # Wrist
    board.set_servo_position(1000, [(6, 2500)])     # Base full left
    time.sleep(1)

    # Lower and grab
    print("  Left pickup: Grabbing...")
    board.set_servo_position(800, [(3, 900)])
    board.set_servo_position(800, [(5, 2364)])
    time.sleep(0.8)

    # Close gripper
    board.set_servo_position(500, [(1, 1455)])
    board.set_servo_position(300, [(5, 2300)])
    time.sleep(0.3)

    # Lift
    print("  Left pickup: Lifting...")
    board.set_servo_position(1000, [(5, 1841)])
    time.sleep(1)

    look_forward(board)
    print("  Left pickup complete!")


def right_pickup_block(board):
    """Pick up block from right side.
    
    Rotates base to right (servo 6=500), reaches down, grabs.
    Vendor-tested sequence from PathfinderBot V1.
    """
    print("  Right pickup: Reaching right...")
    board.set_servo_position(1000, [(1, 2020)])     # Gripper open
    board.set_servo_position(1000, [(3, 800)])      # Shoulder
    board.set_servo_position(1000, [(4, 1800)])     # Elbow (different from left!)
    board.set_servo_position(1000, [(5, 2091)])     # Wrist
    board.set_servo_position(1000, [(6, 500)])      # Base full right
    time.sleep(1)

    # Lower and grab
    print("  Right pickup: Grabbing...")
    board.set_servo_position(800, [(3, 800)])
    board.set_servo_position(800, [(5, 2450)])
    time.sleep(0.8)

    # Close gripper
    board.set_servo_position(500, [(1, 1455)])
    board.set_servo_position(300, [(5, 2318)])
    time.sleep(0.3)

    # Lift
    print("  Right pickup: Lifting...")
    board.set_servo_position(1000, [(5, 1841)])
    time.sleep(1)

    look_forward(board)
    print("  Right pickup complete!")


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

    # Arm to forward position
    look_forward(board)

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
                        look_forward(board)

                    # B = look sad
                    elif button == 1:
                        print("Sad")
                        look_sad(board)

                    # Y = nod yes
                    elif button == 3:
                        print("Yes!")
                        say_yes(board)

                    # X = shake no
                    elif button == 2:
                        print("No!")
                        say_no(board)

                # D-pad
                elif event.type == pygame.JOYHATMOTION:
                    hat = event.value

                    # D-pad Up = front pickup
                    if hat == (0, 1):
                        print("Front pickup sequence...")
                        # Stop motors during arm movement
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        pickup_block(board)

                    # D-pad Down = backward drop into bin
                    elif hat == (0, -1):
                        print("Backward drop sequence...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        backward_drop_block(board)

                    # D-pad Left = left side pickup
                    elif hat == (-1, 0):
                        print("Left side pickup...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        left_pickup_block(board)

                    # D-pad Right = right side pickup
                    elif hat == (1, 0):
                        print("Right side pickup...")
                        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                        right_pickup_block(board)

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
        look_forward(board)
        pygame.quit()
        print("Motors stopped, gamepad released")


if __name__ == '__main__':
    main()
