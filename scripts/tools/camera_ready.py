#!/usr/bin/env python3
"""
Position arm so camera points forward and down to see blocks on floor
Camera is mounted on arm, so arm position = camera angle
"""

from lib.board import get_board as BoardController
import time

print("Positioning arm for camera view of floor blocks...")
board = BoardController()
time.sleep(0.3)

# Camera-ready position: arm extended forward, angled down to see floor
# This should give camera a good view of blocks in front of robot
positions = [
    (1, 1500),  # Base - centered (camera points forward)
    (5, 1000),  # Gripper - open (so it doesn't block camera)
    (2, 1400),  # Shoulder - forward and down
    (3, 1600),  # Elbow - extended forward
    (4, 1200),  # Wrist - angled down to see floor
]

print("Moving to camera-ready position...")
for servo_id, position in positions:
    print(f"  Servo {servo_id}...")
    board.set_servo_position(500, [(servo_id, position)])
    time.sleep(0.4)

print("\n[OK] Camera should now see floor in front of robot")
print("  - Arm extended forward")
print("  - Angled down toward floor")
print("  - Gripper open (doesn't block view)")
print("\nReady to detect blocks!")
