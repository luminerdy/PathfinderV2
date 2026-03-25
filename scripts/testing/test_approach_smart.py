#!/usr/bin/env python3
"""
Smart vision-guided approach test
If block is too close, backs up first, then approaches
"""

import cv2
import numpy as np
from lib.board_protocol import BoardController
import time

def detect_red_block(frame):
    """Detect red block and return info"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Red has two ranges
    mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
    mask2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
    mask = cv2.bitwise_or(mask1, mask2)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    
    if area < 100:
        return None
    
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return {'center': (cx, cy), 'area': area}

print("=" * 60)
print("SMART VISION-GUIDED APPROACH")
print("=" * 60)

board = BoardController()
cap = cv2.VideoCapture(0)
time.sleep(0.5)

# Constants
TARGET_AREA = 3000      # Desired final size
TOO_CLOSE_AREA = 2500   # Back up if larger than this
SPEED = 30

print("\nPhase 1: Checking initial position...")

ret, frame = cap.read()
if not ret:
    print("[ERROR] Cannot read camera")
    exit(1)

block = detect_red_block(frame)

if not block:
    print("[ERROR] No red block visible - position robot to see red blocks")
    cap.release()
    exit(1)

initial_area = block['area']
cx, cy = block['center']
print(f"Red block detected: area={initial_area:.0f} at ({cx},{cy})")

# Decide action
if initial_area > TOO_CLOSE_AREA:
    print(f"\nTOO CLOSE (area {initial_area:.0f} > {TOO_CLOSE_AREA})")
    print("Phase 2: Backing up...")
    
    # Back up for 2 seconds
    print("  Reversing...")
    board.set_motor_duty([(1, -SPEED), (2, -SPEED), (3, -SPEED), (4, -SPEED)])
    time.sleep(2)
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    time.sleep(0.5)
    
    # Check new position
    ret, frame = cap.read()
    block = detect_red_block(frame)
    if block:
        print(f"  New position: area={block['area']:.0f}")
    else:
        print("  Lost block while backing up!")

print(f"\nPhase 3: Approaching target...")
print(f"Will stop when area reaches {TARGET_AREA}")

iteration = 0
while iteration < 30:
    iteration += 1
    
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Camera read failed")
        break
    
    block = detect_red_block(frame)
    
    if not block:
        print(f"[{iteration}] Block lost - stopping")
        break
    
    area = block['area']
    cx, cy = block['center']
    offset_x = cx - 320
    
    print(f"[{iteration}] area={area:5.0f} at ({cx:3d},{cy:3d}) offset_x={offset_x:+4d}")
    
    # Check if arrived
    if area >= TARGET_AREA:
        print(f"\n[SUCCESS] Reached target! Final area: {area:.0f}")
        break
    
    # Simple forward movement
    board.set_motor_duty([(1, SPEED), (2, SPEED), (3, SPEED), (4, SPEED)])
    time.sleep(0.2)

# Stop
board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
cap.release()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
