#!/usr/bin/env python3
"""
Color Space Demo (D4 - Level 3)

Demonstrates different color space conversions and why HSV
is better than BGR for color detection.

Key concept: HSV separates COLOR (Hue) from BRIGHTNESS (Value).
This means a red block looks "red" (same Hue) whether it's in
bright light or shadow. In BGR, the same block has completely
different values under different lighting.

Outputs saved as images (no display window needed):
    original_bgr.jpg    - OpenCV's default (Blue-Green-Red)
    converted_rgb.jpg   - Normal human perception (Red-Green-Blue)
    grayscale.jpg       - Single channel (black & white)
    hsv.jpg             - Hue-Saturation-Value
    red_mask.jpg        - Binary mask showing detected red pixels

Usage:
    python3 color_spaces.py
"""

import cv2
import numpy as np

print("=" * 60)
print("COLOR SPACE DEMO")
print("=" * 60)
print()

# Open camera and capture one frame
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Capturing frame...")
ret, frame = camera.read()
camera.release()

if not ret:
    print("ERROR: Failed to capture frame")
    exit(1)

print("Captured: %dx%d" % (frame.shape[1], frame.shape[0]))
print()

# --- Convert to different color spaces ---
print("Converting to color spaces...")
print()

# 1. BGR (OpenCV default)
# OpenCV stores images as Blue-Green-Red, not RGB.
# Historical reason: early camera hardware stored bytes in BGR order.
bgr = frame
cv2.imwrite('original_bgr.jpg', bgr)
print("[1/4] BGR (Blue-Green-Red)")
print("      OpenCV's default color space")
print("      Saved: original_bgr.jpg")
print()

# 2. RGB (swap red and blue channels)
# This is what humans expect — Red-Green-Blue.
# Note: saving RGB with cv2.imwrite will look wrong because
# imwrite expects BGR input. The file is for comparison only.
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
cv2.imwrite('converted_rgb.jpg', rgb)
print("[2/4] RGB (Red-Green-Blue)")
print("      Normal human perception")
print("      Note: Will look color-swapped when viewed (expected)")
print("      Saved: converted_rgb.jpg")
print()

# 3. Grayscale (single channel)
# Converts 3-channel color to 1-channel intensity.
# Formula: gray = 0.299*R + 0.587*G + 0.114*B (weighted by human perception)
# Uses: Edge detection, faster processing (1/3 the data)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
cv2.imwrite('grayscale.jpg', gray)
print("[3/4] Grayscale")
print("      Single channel (black & white)")
print("      Uses: Edge detection, faster processing")
print("      Saved: grayscale.jpg")
print()

# 4. HSV (Hue-Saturation-Value)
# THE KEY COLOR SPACE FOR ROBOTICS:
#   H (Hue):        0-180, the actual color (red=0, green=60, blue=120)
#   S (Saturation):  0-255, color purity (0=gray, 255=vivid)
#   V (Value):       0-255, brightness (0=black, 255=bright)
#
# Why HSV > BGR for detection:
#   Bright red in BGR: (0, 0, 255)
#   Dark red in BGR:   (0, 0, 80)   <- Totally different values!
#   Bright red in HSV: (0, 255, 255)
#   Dark red in HSV:   (0, 255, 80) <- Same Hue! Only brightness differs.
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
cv2.imwrite('hsv.jpg', hsv)
print("[4/4] HSV (Hue-Saturation-Value)")
print("      Best for color detection")
print("      H = color (0-180), S = purity (0-255), V = brightness (0-255)")
print("      Saved: hsv.jpg")
print()

# --- Bonus: Color detection example ---
# Demonstrate the practical use: find red objects in the frame.
# We define a range of HSV values that match "red" and create a binary mask.
print("=" * 60)
print("COLOR DETECTION EXAMPLE")
print("=" * 60)
print()
print("Detecting red objects...")

# Red in HSV wraps around: H=0-10 is red, H=160-180 is also red.
# We just use the low end here for simplicity.
lower_red = np.array([0, 100, 100])    # Minimum H, S, V for "red"
upper_red = np.array([10, 255, 255])   # Maximum H, S, V for "red"

# inRange creates a binary mask: white (255) where pixel is in range, black (0) elsewhere
mask = cv2.inRange(hsv, lower_red, upper_red)
cv2.imwrite('red_mask.jpg', mask)

# Count how many pixels matched
red_pixels = cv2.countNonZero(mask)
total_pixels = frame.shape[0] * frame.shape[1]
percent = (red_pixels / total_pixels) * 100

print("Red pixels: %d / %d (%.1f%%)" % (red_pixels, total_pixels, percent))
print("Saved: red_mask.jpg (white = red detected)")
print()

print("=" * 60)
print("DEMO COMPLETE!")
print("=" * 60)
print()
print("Files created:")
print("  - original_bgr.jpg    (OpenCV default)")
print("  - converted_rgb.jpg   (human perception)")
print("  - grayscale.jpg       (single channel)")
print("  - hsv.jpg             (color detection)")
print("  - red_mask.jpg        (binary detection result)")
print()
print("Compare these images to understand color spaces!")
print("Key takeaway: Use HSV for color detection (Hue is lighting-independent)")
