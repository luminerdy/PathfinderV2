#!/usr/bin/env python3
"""
Quick script to lower arm to safe rest position
Use after initialization if arm is pointing up
"""

from lib.board import get_board as BoardController
import time

print("Lowering arm to safe rest position...")
board = BoardController()
time.sleep(0.3)

# Safe rest position
# Servo positions: 500-2500 (1500 = center)
positions = [
    (2, 1700),  # Shoulder - lowered
    (3, 1300),  # Elbow - bent
    (4, 1500),  # Wrist - neutral
    (1, 1500),  # Base - centered
    (5, 1000),  # Gripper - open
]

print("Moving to rest position...")
for servo_id, position in positions:
    board.set_servo_position(500, [(servo_id, position)])
    time.sleep(0.3)

print("[OK] Arm lowered and safe")
