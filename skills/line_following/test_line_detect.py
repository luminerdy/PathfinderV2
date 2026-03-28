#!/usr/bin/env python3
"""
Line Detection Test (no driving)

Tests lime green line detection from camera.
Saves annotated image showing detected line and centroid.

Usage:
    python3 test_line_detect.py
"""

import sys
import os
import cv2
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board
from skills.line_following.line_follower import LineFollower

print("=" * 60)
print("LINE DETECTION TEST")
print("=" * 60)
print()

board = get_board()
follower = LineFollower(board)

# Position camera down
print("[1/4] Positioning camera down...")
board.set_servo_position(800, LineFollower.ARM_CAMERA_DOWN)
time.sleep(1.5)

# Open camera
print("[2/4] Opening camera...")
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(1.0)

# Capture and detect
print("[3/4] Detecting line...")
print()

results = []
for i in range(5):
    ret, frame = camera.read()
    if not ret:
        continue
    
    detection = follower.detect_line(frame)
    results.append(detection)
    
    if i == 0:
        if detection['found']:
            print("  Line FOUND!")
            print("    Centroid: (%d, %d)" % (detection['cx'], detection['cy']))
            print("    Error: %+d pixels from center" % detection['error'])
            print("    Green ratio: %.2f%%" % (detection['ratio'] * 100))
            
            if detection['error'] < -50:
                print("    Position: LINE IS LEFT (robot should steer left)")
            elif detection['error'] > 50:
                print("    Position: LINE IS RIGHT (robot should steer right)")
            else:
                print("    Position: LINE IS CENTERED (go straight)")
        else:
            print("  No line detected")
            print("    Green ratio: %.3f%%" % (detection['ratio'] * 100))
            print("    (Place lime green tape on floor in camera view)")
    
    time.sleep(0.2)

# Save annotated image
print()
print("[4/4] Saving annotated image...")

if ret and frame is not None:
    annotated = frame.copy()
    
    # Draw ROI boundary
    roi_top = int(480 * LineFollower.ROI_TOP_RATIO)
    roi_bottom = int(480 * LineFollower.ROI_BOTTOM_RATIO)
    cv2.line(annotated, (0, roi_top), (640, roi_top), (255, 255, 0), 2)
    cv2.line(annotated, (0, roi_bottom), (640, roi_bottom), (255, 255, 0), 2)
    cv2.putText(annotated, "ROI", (5, roi_top + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
    
    # Draw center line
    cv2.line(annotated, (320, roi_top), (320, roi_bottom), (128, 128, 128), 1)
    
    # Draw detection
    if detection['found']:
        # Centroid (adjusted to full frame coordinates)
        cx = detection['cx']
        cy = detection['cy'] + int(480 * LineFollower.ROI_TOP_RATIO)
        cv2.circle(annotated, (cx, cy), 10, (0, 255, 0), 3)
        cv2.line(annotated, (320, cy), (cx, cy), (0, 0, 255), 2)
        cv2.putText(annotated, "err=%+d" % detection['error'], (cx + 15, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    
    cv2.imwrite('line_detect_result.jpg', annotated)
    print("  Saved: line_detect_result.jpg")
    
    # Also save mask
    if results and results[-1]['mask'] is not None:
        cv2.imwrite('line_mask.jpg', results[-1]['mask'])
        print("  Saved: line_mask.jpg (green pixels = white)")

camera.release()

# Return arm to rest
board.set_servo_position(800, [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)])

print()
print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print()

found_count = sum(1 for r in results if r['found'])
print("Detection: %d/%d frames found line" % (found_count, len(results)))
if found_count > 0:
    avg_error = sum(r['error'] for r in results if r['found']) / found_count
    print("Avg error: %+.0f pixels" % avg_error)
