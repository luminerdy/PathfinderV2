#!/usr/bin/env python3
"""
Robot Startup Sequence
Runs on boot to initialize robot to known good state
"""

import sys
import time
from lib.board_protocol import BoardController

print("=" * 60)
print("PATHFINDER ROBOT STARTUP SEQUENCE")
print("=" * 60)

# Initialize board
print("\n[1/6] Initializing control board...")
try:
    board = BoardController()
    time.sleep(0.5)
    print("  [OK] Control board connected")
except Exception as e:
    print(f"  [FAIL] Could not connect to board: {e}")
    sys.exit(1)

# Stop all motors
print("\n[2/6] Stopping all motors...")
board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
print("  [OK] All motors stopped")

# Check battery
print("\n[3/6] Checking battery voltage...")
try:
    # Battery reading comes from periodic SYS packets
    time.sleep(0.5)
    voltage = board.get_battery()
    if voltage and voltage < 100:  # Sanity check
        print(f"  Battery: {voltage:.2f}V")
        if voltage < 7.0:
            print("  [WARN] Battery low! Charge soon")
        elif voltage < 7.5:
            print("  [WARN] Battery getting low")
        else:
            print("  [OK] Battery good")
    else:
        print("  [WARN] Could not read battery voltage (got invalid reading)")
except Exception as e:
    print(f"  [WARN] Battery check failed: {e}")

# Position arm safely
print("\n[4/6] Positioning arm to safe rest position...")
safe_positions = [
    (2, 1700),  # Shoulder lowered
    (3, 1300),  # Elbow bent
    (4, 1500),  # Wrist neutral
    (1, 1500),  # Base centered
    (5, 1000),  # Gripper open
]

for servo_id, pwm in safe_positions:
    board.set_servo_position(400, [(servo_id, pwm)])
    time.sleep(0.3)
print("  [OK] Arm in safe rest position")

# Turn off RGB LEDs (power saving)
print("\n[5/6] Turning off RGB LEDs (power saving)...")
try:
    board.set_rgb(0, 0, 0)  # All black
    print("  [OK] RGB LEDs off")
except:
    print("  [WARN] Could not control RGB LEDs")

# Check camera
print("\n[6/6] Checking camera...")
import cv2
camera_found = False
for device in [0, 1, 2]:
    try:
        cap = cv2.VideoCapture(device)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"  [OK] Camera found on device {device}")
                print(f"       Resolution: {frame.shape[1]}x{frame.shape[0]}")
                camera_found = True
                cap.release()
                break
            cap.release()
    except:
        pass

if not camera_found:
    print("  [WARN] No camera detected")
    print("         Check USB connection if using USB camera")

# Startup complete
print("\n" + "=" * 60)
print("STARTUP COMPLETE")
print("=" * 60)

# Double beep to indicate ready
print("\nBeeping to signal ready...")
try:
    board.set_buzzer(100, 100)  # 100ms on, 100ms off
    time.sleep(0.3)
    board.set_buzzer(100, 100)
    time.sleep(0.3)
except:
    print("  (Buzzer not available)")

print("\nRobot initialized and ready!")
print("\nUseful commands:")
print("  python3 test_movement.py       - Test chassis movement")
print("  python3 check_battery.py       - Check battery status")
print("  python3 lower_arm.py           - Lower arm if pointing up")
print("  python3 camera_forward_simple.py - Position camera")
print("")
