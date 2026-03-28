#!/usr/bin/env python3
"""
Camera Vision Demo (Level 2)

Live video display with FPS counter and snapshot capability.

Usage:
    python3 run_demo.py

Controls:
    'q' - Quit
    's' - Save snapshot
    'f' - Toggle FPS display

Note: Requires display (X11). For headless, use test_camera.py instead.
"""

import cv2
import time
import os

print("=" * 60)
print("CAMERA VISION DEMO")
print("=" * 60)
print()
print("Controls:")
print("  'q' - Quit")
print("  's' - Save snapshot")
print("  'f' - Toggle FPS display")
print()
print("Starting camera...")
print()

# Open camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open camera!")
    print("Check USB connection and run: ls /dev/video*")
    exit(1)

# Configure
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Camera: {width}x{height}")
print("Press 'q' in video window to quit")
print()

# State
show_fps = True
snapshot_count = 0
prev_time = time.time()

try:
    while True:
        ret, frame = camera.read()
        
        if not ret:
            print("Failed to capture frame")
            break
        
        # Calculate FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if curr_time > prev_time else 0
        prev_time = curr_time
        
        # Draw info on frame
        if show_fps:
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"{width}x{height}", (10, height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display
        cv2.imshow('Camera Vision', frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            print("Quit requested")
            break
        
        elif key == ord('s'):
            snapshot_count += 1
            filename = f"snapshot_{snapshot_count:03d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
        
        elif key == ord('f'):
            show_fps = not show_fps
            print(f"FPS display: {'ON' if show_fps else 'OFF'}")

except KeyboardInterrupt:
    print("\nInterrupted by user")

finally:
    camera.release()
    cv2.destroyAllWindows()
    print()
    print("Camera closed.")
    if snapshot_count > 0:
        print(f"Saved {snapshot_count} snapshot(s)")
