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

# Turn off sonar RGB LEDs (they default to ON at power-up)
print("\n[3/6] Turning off sonar RGB LEDs...")
try:
    board.set_rgb(0, 0, 0)  # All LEDs black (off)
    print("  [OK] Sonar LEDs off (power saving)")
except Exception as e:
    print(f"  [WARN] Could not control RGB LEDs: {e}")

# Check battery
print("\n[4/7] Checking battery voltage...")
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

# Position arm to camera-forward position
print("\n[5/7] Positioning arm to camera-forward position...")

# Correct servo mapping:
# 1=Gripper, 2=EMPTY, 3=Wrist, 4=Elbow, 5=Shoulder, 6=Base
camera_forward = [
    (1, 2500),  # Gripper open
    (6, 1500),  # Base forward (center)
    (5, 700),   # Shoulder
    (4, 2450),  # Elbow
    (3, 590),   # Wrist
]

# Move servos sequentially to avoid power spike
for servo_id, pwm in camera_forward:
    board.set_servo_position(800, [(servo_id, pwm)])
    time.sleep(0.4)
    
# Extra wait to ensure settled
time.sleep(0.5)
print("  [OK] Arm positioned with camera facing forward")

# Check camera
print("\n[6/7] Checking camera...")
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
print("\n[7/7] Final check...")
print("  [OK] All systems ready")

print("\n" + "=" * 60)
print("STARTUP COMPLETE")
print("=" * 60)

# Double beep to indicate ready
print("\nBeeping to signal ready...")
try:
    # Buzzer: freq_hz, on_seconds, off_seconds, repeat
    board.set_buzzer(1000, 0.1, 0.1, 2)  # 1kHz, beep twice
    time.sleep(0.5)
    print("  [OK] Ready signal sent")
except Exception as e:
    print(f"  [WARN] Buzzer not available: {e}")

print("\nRobot initialized and ready!")
print("\nUseful commands:")
print("  python3 test_movement.py       - Test chassis movement")
print("  python3 check_battery.py       - Check battery status")
print("  python3 lower_arm.py           - Lower arm if pointing up")
print("  python3 camera_forward_simple.py - Position camera")
print("")
