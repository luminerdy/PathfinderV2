#!/usr/bin/env python3
"""
Color Space Demo (Level 3)

Demonstrates different color space conversions.
Saves examples as image files (no display window needed).

Usage:
    python3 color_spaces.py

Outputs:
    original_bgr.jpg
    converted_rgb.jpg
    grayscale.jpg
    hsv.jpg
"""

import cv2
import numpy as np

print("=" * 60)
print("COLOR SPACE DEMO")
print("=" * 60)
print()

# Open camera
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Capturing frame...")
ret, frame = camera.read()
camera.release()

if not ret:
    print("ERROR: Failed to capture frame")
    exit(1)

print(f"Captured: {frame.shape[1]}x{frame.shape[0]}")
print()

# Convert to different color spaces
print("Converting to color spaces...")
print()

# 1. BGR (OpenCV default)
bgr = frame
cv2.imwrite('original_bgr.jpg', bgr)
print("[1/4] BGR (Blue-Green-Red)")
print("      OpenCV's default color space")
print("      Saved: original_bgr.jpg")
print()

# 2. RGB (swap red and blue channels)
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# Save RGB as BGR so it displays correctly
cv2.imwrite('converted_rgb.jpg', rgb)
print("[2/4] RGB (Red-Green-Blue)")
print("      Normal human perception")
print("      Note: Looks wrong if viewed in BGR-expecting software")
print("      Saved: converted_rgb.jpg")
print()

# 3. Grayscale
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
cv2.imwrite('grayscale.jpg', gray)
print("[3/4] Grayscale")
print("      Single channel (black & white)")
print("      Uses: Edge detection, faster processing")
print("      Saved: grayscale.jpg")
print()

# 4. HSV (Hue-Saturation-Value)
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
cv2.imwrite('hsv.jpg', hsv)
print("[4/4] HSV (Hue-Saturation-Value)")
print("      Best for color detection")
print("      Hue = color (0-180)")
print("      Saturation = purity (0-255)")
print("      Value = brightness (0-255)")
print("      Saved: hsv.jpg")
print()

# Bonus: Color detection example
print("=" * 60)
print("COLOR DETECTION EXAMPLE")
print("=" * 60)
print()
print("Detecting red objects...")

# Define red color range in HSV
lower_red = np.array([0, 100, 100])
upper_red = np.array([10, 255, 255])

# Create mask
mask = cv2.inRange(hsv, lower_red, upper_red)
cv2.imwrite('red_mask.jpg', mask)

# Count red pixels
red_pixels = cv2.countNonZero(mask)
total_pixels = frame.shape[0] * frame.shape[1]
percent = (red_pixels / total_pixels) * 100

print(f"Red pixels: {red_pixels:,} / {total_pixels:,} ({percent:.1f}%)")
print("Saved: red_mask.jpg (white = red detected)")
print()

print("=" * 60)
print("DEMO COMPLETE!")
print("=" * 60)
print()
print("Files created:")
print("  - original_bgr.jpg")
print("  - converted_rgb.jpg")
print("  - grayscale.jpg")
print("  - hsv.jpg")
print("  - red_mask.jpg")
print()
print("Compare these images to understand color spaces!")
