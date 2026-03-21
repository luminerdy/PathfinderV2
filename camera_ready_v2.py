#!/usr/bin/env python3
"""
Position arm so BACKWARD-FACING camera can see forward
Camera is mounted backward and upside down on arm
So we need to position arm so camera faces the blocks
"""

from lib.board_protocol import BoardController
import time

print("Camera hardware: mounted BACKWARD and UPSIDE DOWN")
print("Positioning arm so backward camera sees forward...")
board = BoardController()
time.sleep(0.3)

# Since camera faces backward, we need arm to angle back/up
# Camera should look over robot toward floor in front
positions = [
    (1, 1500),  # Base - centered
    (5, 1000),  # Gripper - open
    (2, 800),   # Shoulder - RAISED (camera on back of arm)
    (3, 800),   # Elbow - RAISED
    (4, 2000),  # Wrist - TILTED UP (camera faces back and down)
]

print("Moving to camera-ready position...")
for servo_id, position in positions:
    print(f"  Servo {servo_id}...")
    board.set_servo_position(500, [(servo_id, position)])
    time.sleep(0.4)

print("\n[OK] Camera (backward-facing) should now see floor in front")
print("  NOTE: Images will be upside down in software")
print("  Will need to flip 180 degrees in code")
print("\nReady to detect blocks!")
