#!/usr/bin/env python3
"""
Block Detection Demo (E3)

Detect colored blocks using HSV color filtering.
Shows detection pipeline results without driving.

Usage:
    python3 run_demo.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import cv2
from skills.block_detect import BlockDetector

print("=" * 60)
print("BLOCK DETECTION DEMO")
print("=" * 60)
print()
print("Colors: red, blue, yellow")
print("Block size: 30mm (1.2 inches)")
print()

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(1.5)

detector = BlockDetector()

print("[1/3] Single frame detection")
print("-" * 40)

ret, frame = camera.read()
if not ret:
    print("  [!!] Could not capture frame")
    sys.exit(1)

blocks = detector.detect(frame)

if blocks:
    print("  Detected %d block(s):" % len(blocks))
    for b in blocks[:5]:
        print("    %s: %.0fcm away, %dx%dpx, offset=%+dpx, conf=%.2f" % (
            b.color, b.estimated_distance_mm / 10,
            b.width, b.height,
            b.offset_from_center, b.confidence))
    if len(blocks) > 5:
        print("    ... and %d more" % (len(blocks) - 5))
else:
    print("  No blocks detected")
    print("  (Place a colored block in view and try again)")

print()
print("[2/3] Color breakdown")
print("-" * 40)

for color in ['red', 'blue', 'yellow']:
    color_blocks = detector.detect(frame, colors=[color])
    print("  %s: %d detection(s)" % (color, len(color_blocks)))

print()
print("[3/3] Saving annotated frame")
print("-" * 40)

if blocks:
    annotated = detector.annotate_frame(frame.copy(), blocks)
else:
    annotated = frame

cv2.imwrite('block_detection_result.jpg', annotated)
print("  Saved: block_detection_result.jpg")

camera.release()

print()
print("=" * 60)
print("DEMO COMPLETE")
print("=" * 60)
print()
print("What you learned:")
print("  [OK] HSV color thresholding detects blocks by color")
print("  [OK] Distance estimated from apparent pixel size")
print("  [OK] Confidence scoring filters false positives")
print("  [OK] Multiple colors detected simultaneously")
print()
print("Next: E4 Visual Servoing (drive toward detected blocks)")
