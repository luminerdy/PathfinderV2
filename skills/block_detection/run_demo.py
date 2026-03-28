#!/usr/bin/env python3
"""
Block Detection Demo (E3)

Detect colored blocks using HSV color filtering.
Shows detection pipeline results without driving.

Pipeline: Camera -> HSV convert -> Color threshold -> Contours -> Filter -> Detect

Usage:
    python3 run_demo.py
"""

import sys
import os
import time

# Add project root so we can import from skills/ and lib/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import cv2
from skills.block_detect import BlockDetector


def main():
    """Run block detection demo: capture frame, detect blocks, show results."""

    print("=" * 60)
    print("BLOCK DETECTION DEMO")
    print("=" * 60)
    print()
    print("Colors: red, blue, yellow")
    print("Block size: 30mm (1.2 inches)")
    print()

    # --- Open camera ---
    # Device 0 = first USB camera. Change to 1 or 2 if you have multiple.
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Camera needs ~1.5s to auto-adjust exposure and white balance.
    # Without this delay, first frames are often dark or green-tinted.
    time.sleep(1.5)

    # BlockDetector handles the full HSV pipeline:
    #   BGR -> HSV -> threshold per color -> morphology cleanup -> contour finding
    detector = BlockDetector()

    # --- Demo 1: Detect all blocks in a single frame ---
    print("[1/3] Single frame detection")
    print("-" * 40)

    ret, frame = camera.read()
    if not ret:
        print("  [!!] Could not capture frame")
        sys.exit(1)

    # detect() returns a list of BlockDetection objects, sorted nearest-first.
    # Each has: color, center_x, center_y, width, height, area,
    #           aspect_ratio, offset_from_center, estimated_distance_mm, confidence
    blocks = detector.detect(frame)

    if blocks:
        print("  Detected %d block(s):" % len(blocks))
        for b in blocks[:5]:
            # offset_from_center: positive = block is right of frame center
            # estimated_distance_mm: calculated from known block size (30mm)
            #   using pinhole model: distance = (focal_length * real_size) / pixel_size
            print("    %s: %.0fcm away, %dx%dpx, offset=%+dpx, conf=%.2f" % (
                b.color, b.estimated_distance_mm / 10,
                b.width, b.height,
                b.offset_from_center, b.confidence))
        if len(blocks) > 5:
            print("    ... and %d more" % (len(blocks) - 5))
    else:
        print("  No blocks detected")
        print("  (Place a colored block in view and try again)")

    # --- Demo 2: Break down detections by color ---
    # This shows how to filter for specific colors.
    # Useful when you only care about one color (e.g., "find red blocks").
    print()
    print("[2/3] Color breakdown")
    print("-" * 40)

    for color in ['red', 'blue', 'yellow']:
        color_blocks = detector.detect(frame, colors=[color])
        print("  %s: %d detection(s)" % (color, len(color_blocks)))

    # --- Demo 3: Save annotated image ---
    # annotate_frame() draws bounding boxes, color labels, and distance
    # on the image. Useful for debugging and understanding what the robot sees.
    print()
    print("[3/3] Saving annotated frame")
    print("-" * 40)

    if blocks:
        # .copy() so we don't modify the original frame
        annotated = detector.annotate_frame(frame.copy(), blocks)
    else:
        annotated = frame

    cv2.imwrite('block_detection_result.jpg', annotated)
    print("  Saved: block_detection_result.jpg")

    # Always release the camera when done — other programs can't access it otherwise
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


if __name__ == "__main__":
    main()
