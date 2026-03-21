#!/usr/bin/env python3
"""
Move arm to camera-forward position
Uses servo positions that work (will tune interactively)
"""

from lib.board_protocol import BoardController
import time

print("Moving arm for camera to see forward...")
board = BoardController()
time.sleep(0.3)

# Stop motors
board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

# Move servos to camera-ready position
# These are starting guesses - adjust with find_camera_position.py
positions = [
    (1, 1500),  # Base - centered
    (5, 1000),  # Gripper - open (don't block camera)
    (2, 1100),  # Shoulder - adjust this
    (3, 1600),  # Elbow - adjust this  
    (4, 1800),  # Wrist - adjust this
]

print("Moving servos...")
for servo_id, pwm in positions:
    print(f"  Servo {servo_id}: {pwm}")
    board.set_servo_position(500, [(servo_id, pwm)])
    time.sleep(0.5)

# Beep
try:
    board.set_buzzer(100, 0)  # 100ms beep
except:
    pass

print("\n[OK] Done")
print("Check camera view - adjust positions with find_camera_position.py if needed")
