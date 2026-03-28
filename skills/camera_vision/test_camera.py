#!/usr/bin/env python3
"""
Camera Hardware Test (D4 - Level 1)

Quick test to verify camera is working.
Captures a few frames and saves one as test_frame.jpg.

No display window needed — works over SSH and headless.

Usage:
    python3 test_camera.py
"""

import cv2
import time

print("=" * 60)
print("CAMERA HARDWARE TEST")
print("=" * 60)
print()

# --- Step 1: Open camera ---
# VideoCapture(0) opens the first USB camera (/dev/video0).
# If you have multiple cameras, try 1 or 2.
print("[1/4] Opening camera...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("  [!!] ERROR: Could not open camera!")
    print()
    print("Troubleshooting:")
    print("  - Check USB connection (unplug and replug)")
    print("  - Run: ls /dev/video*  (should show video0)")
    print("  - Try device 1: cv2.VideoCapture(1)")
    print("  - Check permissions: sudo usermod -a -G video $USER")
    exit(1)

print("  [OK] Camera opened!")
print()

# --- Step 2: Configure resolution ---
# We request 640x480 but camera may give different actual values.
# Always check what you actually got.
print("[2/4] Configuring resolution...")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Read back actual values (camera decides what it can do)
width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(camera.get(cv2.CAP_PROP_FPS))

print("  Resolution: %dx%d" % (width, height))
print("  FPS: %d" % fps)
print()

# --- Step 3: Capture test frames ---
# First few frames are often dark (auto-exposure adjusting).
# We capture 5 to let the camera stabilize.
print("[3/4] Capturing frames...")
for i in range(5):
    ret, frame = camera.read()
    if ret:
        # frame.shape = (height, width, channels)
        # channels = 3 for BGR color, 1 for grayscale
        print("  Frame %d/5: %dx%d, %d channels" % (
            i + 1, frame.shape[1], frame.shape[0], frame.shape[2]))
    else:
        print("  Frame %d/5: FAILED" % (i + 1))
    time.sleep(0.1)

print()

# --- Step 4: Save last frame ---
# OpenCV saves in BGR format by default (what the camera gives us).
# JPEG quality is ~95% by default — good enough for testing.
print("[4/4] Saving test image...")
if ret and frame is not None:
    cv2.imwrite('test_frame.jpg', frame)
    print("  [OK] Saved as: test_frame.jpg")
    print("  Size: %dx%d" % (frame.shape[1], frame.shape[0]))
else:
    print("  [!!] No frame to save")

# Always release camera when done — other programs need access
camera.release()

print()
print("=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
print()
print("Camera is working!" if ret else "Camera test FAILED")
print()
