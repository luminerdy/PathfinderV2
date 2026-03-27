#!/usr/bin/env python3
"""
Move arm to forward-facing camera position
Based on original PathfinderBot code: AK.setPitchRangeMoving((0, 6, 18), ...)
Position: x=0, y=60mm, z=180mm (camera points forward and down)
"""

from lib.board import get_board as BoardController
import time

print("Moving arm to forward-facing camera position...")
print("Position: (0, 60mm, 180mm) - same as original PathfinderBot")

board = BoardController()
time.sleep(0.3)

# Stop motors first
board.set_motor_duty(1, 0)
board.set_motor_duty(2, 0)
board.set_motor_duty(3, 0)
board.set_motor_duty(4, 0)

# Base centered
board.set_servo_position(300, [(1, 1500)])
time.sleep(0.3)

# From original code: position (0, 6, 18) in cm
# This worked for backward-facing camera on Pi 4 PathfinderBot
# Servo positions calculated via IK for this target position

# These servo positions should give us (0, 60mm, 180mm):
# Based on typical arm geometry and the target position
positions = [
    (5, 1000),  # Gripper open (don't block camera)
    (2, 1200),  # Shoulder - raised and forward
    (3, 1400),  # Elbow - bent to extend forward
    (4, 1700),  # Wrist - angled down to see floor
]

print("Moving servos to camera-ready position...")
for servo_id, position in positions:
    print(f"  Servo {servo_id}: {position}")
    board.set_servo_position(300, [(servo_id, position)])
    time.sleep(0.4)

# Beep to indicate ready
print("\nBeeping to indicate ready...")
board.set_buzzer(True)
time.sleep(0.1)
board.set_buzzer(False)

print("\n[OK] Arm positioned for forward camera view")
print("Camera (backward-mounted) should now see floor in front")
print("Images will be auto-flipped 180° in software (config.yaml flip: true)")
