#!/usr/bin/env python3
"""
Interactive tool to find arm position that gives camera good floor view
Camera is backward and upside-down, so this helps find the right angle
"""

from lib.board_protocol import BoardController
import time

board = BoardController()

print("=== Find Camera Position ===")
print("Camera is BACKWARD and UPSIDE-DOWN on arm")
print("We need to find servo positions that let camera see floor in front")
print()

# Starting position
positions = {
    1: 1500,  # Base (center)
    2: 1500,  # Shoulder
    3: 1500,  # Elbow
    4: 1500,  # Wrist
    5: 1000   # Gripper (open, don't block view)
}

def move_servo(servo_id, position):
    """Move one servo"""
    positions[servo_id] = position
    board.set_servo_position(300, [(servo_id, position)])
    time.sleep(0.3)

def show_positions():
    """Display current positions"""
    print("\nCurrent positions:")
    print(f"  1-Base:     {positions[1]}")
    print(f"  2-Shoulder: {positions[2]}")
    print(f"  3-Elbow:    {positions[3]}")
    print(f"  4-Wrist:    {positions[4]}")
    print(f"  5-Gripper:  {positions[5]}")

# Start in neutral
print("Moving to neutral position...")
for servo_id in range(1, 6):
    move_servo(servo_id, positions[servo_id])

print("\nCommands:")
print("  1+ / 1-  : Base higher/lower")
print("  2+ / 2-  : Shoulder up/down")
print("  3+ / 3-  : Elbow up/down")
print("  4+ / 4-  : Wrist up/down")
print("  5+ / 5-  : Gripper close/open")
print("  show     : Show current positions")
print("  save     : Save current positions and exit")
print("  quit     : Exit without saving")
print()

try:
    while True:
        show_positions()
        cmd = input("\nCommand: ").strip()
        
        if cmd == 'quit':
            break
        elif cmd == 'show':
            continue
        elif cmd == 'save':
            print("\n=== SAVED POSITIONS ===")
            print("Add these to camera_ready.py:")
            print("positions = [")
            for servo_id in range(1, 6):
                print(f"    ({servo_id}, {positions[servo_id]}),")
            print("]")
            break
        elif len(cmd) >= 2:
            servo = cmd[0]
            direction = cmd[1]
            
            if servo in '12345' and direction in '+-':
                servo_id = int(servo)
                current = positions[servo_id]
                
                if direction == '+':
                    new_pos = min(2500, current + 50)
                else:
                    new_pos = max(500, current - 50)
                
                print(f"Moving servo {servo_id}: {current} -> {new_pos}")
                move_servo(servo_id, new_pos)
            else:
                print("Unknown command")
        else:
            print("Unknown command")
            
except KeyboardInterrupt:
    print("\nInterrupted")

print("\nLowering arm to safe position...")
move_servo(2, 1700)
move_servo(3, 1300)
print("Done")
