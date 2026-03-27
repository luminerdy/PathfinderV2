#!/usr/bin/env python3
"""
Test individual arm servos
Tests each servo one at a time to verify connections

NOTE: Currently not working due to servo protocol issue
Servo commands trigger motors instead of servos
"""

from lib.board import get_board as BoardController
import time

print("=" * 60)
print("PATHFINDER ARM SERVO TEST")
print("=" * 60)
print("\n⚠️  WARNING: Servo protocol currently broken!")
print("Servo commands may trigger motors instead of servos")
print("This is a known issue being debugged\n")

response = input("Continue anyway? (y/n): ")
if response.lower() != 'y':
    print("Test cancelled")
    exit(0)

board = BoardController()
time.sleep(0.5)

servos = [
    (5, "Gripper", 1000, 1500),     # Open to neutral
    (4, "Wrist", 1300, 1700),       # Down to up
    (3, "Elbow", 1200, 1600),       # Extended to bent
    (2, "Shoulder", 1400, 1800),    # Down to up
    (1, "Base", 1300, 1700),        # Left to right
]

print("\nStarting servo tests...\n")
print("Watch the arm - each servo should move individually\n")

for servo_id, name, pos1, pos2 in servos:
    print(f"Testing Servo {servo_id} ({name})...")
    
    print(f"  Moving to position {pos1}...")
    board.set_servo_position(800, [(servo_id, pos1)])
    time.sleep(2)
    
    print(f"  Moving to position {pos2}...")
    board.set_servo_position(800, [(servo_id, pos2)])
    time.sleep(2)
    
    print(f"  Centering at 1500...")
    board.set_servo_position(800, [(servo_id, 1500)])
    time.sleep(2)
    
    print()

print("=" * 60)
print("SERVO TEST COMPLETE")
print("=" * 60)
print("\nExpected behavior:")
print("  5 (Gripper): Should have opened and closed")
print("  4 (Wrist): Should have moved up and down")
print("  3 (Elbow): Should have extended and bent")
print("  2 (Shoulder): Should have raised and lowered")
print("  1 (Base): Should have rotated left and right")
print("\nIf servos didn't move or motors moved instead:")
print("  → Servo protocol bug confirmed")
print("  → Use vendor code temporarily")
print("  → Or help debug lib/board_protocol.py")
print("")
