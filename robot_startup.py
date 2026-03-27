#!/usr/bin/env python3
"""
PathfinderV2 Robot Startup Sequence

Runs at boot to initialize robot to a known good state.
Works on both Pi 4 (I2C) and Pi 5 (serial) via auto-detection.

Actions:
  1. Connect to motor board
  2. Stop all motors
  3. Turn off sonar LEDs
  4. Position arm to camera-forward
  5. Check battery
  6. Check camera
  7. Beep to signal ready

Install as systemd service:
  sudo systemctl enable pathfinder-startup.service
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.board import get_board, PLATFORM

print("=" * 60)
print("PATHFINDER STARTUP")
print("Platform: %s" % PLATFORM)
print("=" * 60)

# 1. Connect to board
print("\n[1/7] Connecting to board...")
try:
    board = get_board()
    time.sleep(1)
    print("  OK")
except Exception as e:
    print("  FAIL: %s" % e)
    sys.exit(1)

# 2. Stop all motors
print("[2/7] Stopping motors...")
board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
print("  OK")

# 3. Turn off sonar LEDs
print("[3/7] LEDs off...")
try:
    board.set_rgb([(0, 0, 0, 0), (1, 0, 0, 0)])
    print("  OK")
except Exception:
    print("  SKIP (not critical)")

# 4. Position arm to camera-forward
print("[4/7] Arm to camera-forward...")
camera_forward = [
    (1, 2500),  # Gripper open
    (6, 1500),  # Base center
    (5, 700),   # Shoulder
    (4, 2450),  # Elbow
    (3, 590),   # Wrist
]
for servo_id, pwm in camera_forward:
    board.set_servo_position(800, [(servo_id, pwm)])
    time.sleep(0.4)
time.sleep(0.5)
print("  OK")

# 5. Check battery
print("[5/7] Battery...")
voltage = 0
for _ in range(5):
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        voltage = mv / 1000.0
        break
    time.sleep(0.3)

if voltage > 0:
    print("  %.2fV" % voltage)
    if voltage < 7.0:
        print("  WARNING: Battery low!")
else:
    print("  Could not read (check board power)")

# 6. Check camera
print("[6/7] Camera...")
try:
    import cv2
    cam = cv2.VideoCapture(0)
    time.sleep(0.5)
    ret, frame = cam.read()
    if ret:
        print("  %dx%d OK" % (frame.shape[1], frame.shape[0]))
    else:
        print("  No frame (check USB)")
    cam.release()
except Exception:
    print("  Not available")

# 7. Beep ready
print("[7/7] Ready beep...")
board.set_buzzer(1000, 0.1, 0.1, 2)
time.sleep(0.5)
print("  OK")

print()
print("=" * 60)
print("STARTUP COMPLETE")
print("=" * 60)
