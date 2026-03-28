#!/usr/bin/env python3
"""
Camera Hardware Test (Level 1)

Quick test to verify camera is working.
Captures a few frames and saves one as test_frame.jpg.

Usage:
    python3 test_camera.py

No display window - good for SSH/headless testing.
"""

import cv2
import time

print("=" * 60)
print("CAMERA HARDWARE TEST")
print("=" * 60)
print()

# Try to open camera
print("[1/4] Opening camera...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("  [!!] ERROR: Could not open camera!")
    print()
    print("Troubleshooting:")
    print("  - Check USB connection")
    print("  - Run: ls /dev/video*")
    print("  - Try device 1 or 2: cv2.VideoCapture(1)")
    exit(1)

print("  [OK] Camera opened!")
print()

# Set resolution
print("[2/4] Configuring resolution...")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Read actual values (may differ from requested)
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(camera.get(cv2.CAP_PROP_FPS))

print(f"  Resolution: {width}x{height}")
print(f"  FPS: {fps}")
print()

# Capture test frames
print("[3/4] Capturing frames...")
for i in range(5):
    ret, frame = camera.read()
    if ret:
        print(f"  Frame {i+1}/5: {frame.shape[1]}x{frame.shape[0]}, {frame.shape[2]} channels")
    else:
        print(f"  Frame {i+1}/5: FAILED")
    time.sleep(0.1)

print()

# Save last frame
print("[4/4] Saving test image...")
if ret and frame is not None:
    cv2.imwrite('test_frame.jpg', frame)
    print("  [OK] Saved as: test_frame.jpg")
    print(f"  Size: {frame.shape[1]}x{frame.shape[0]}")
else:
    print("  [!!] No frame to save")

# Cleanup
camera.release()

print()
print("=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
print()
print("Camera is working!" if ret else "Camera test failed")
print()
