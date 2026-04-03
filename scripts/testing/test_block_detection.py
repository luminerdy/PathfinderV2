#!/usr/bin/env python3
"""
Test Block Detection on Real Field
Shows what blocks the robot can see
"""

import cv2
import time
import yaml
from skills.block_detect import BlockDetector  # was: capabilities.vision

def main():
    print("=" * 60)
    print("BLOCK DETECTION TEST")
    print("=" * 60)
    
    # Load config
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    time.sleep(0.5)
    
    # Initialize vision
    vision = VisionSystem(camera, config['vision'])
    
    print("\nCapturing image...")
    ret, frame = camera.read()
    if not ret:
        print("ERROR: Could not capture frame")
        return
    
    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")
    
    # Detect blocks by color
    print("\nDetecting blocks...")
    
    all_blocks = {}
    min_area = 100  # Filter out tiny noise
    
    for color in ['red', 'blue', 'green', 'yellow', 'purple']:
        contours = vision.detect_color(frame, color)
        # Filter by minimum area
        filtered = [c for c in contours if cv2.contourArea(c) > min_area]
        all_blocks[color] = filtered
    
    # Report findings
    print("\n" + "=" * 60)
    print("DETECTION RESULTS")
    print("=" * 60)
    
    total = 0
    for color in ['red', 'blue', 'green', 'yellow', 'purple']:
        count = len(all_blocks.get(color, []))
        if count > 0:
            print(f"\n{color.upper()}: {count} block(s)")
            for i, contour in enumerate(all_blocks[color], 1):
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                center_x = x + w // 2
                center_y = y + h // 2
                
                print(f"  Block {i}:")
                print(f"    Center: ({center_x}, {center_y}) pixels")
                print(f"    Area: {area:.0f} pixels²")
                print(f"    Width: {w} pixels")
                print(f"    Height: {h} pixels")
                
                # Rough distance estimate (assuming 25mm block)
                # Larger area = closer
                if area > 3000:
                    distance = "CLOSE (ready to pickup)"
                elif area > 1500:
                    distance = "MEDIUM (approach needed)"
                else:
                    distance = "FAR (drive forward)"
                print(f"    Distance: {distance}")
            total += count
    
    if total == 0:
        print("\nNO BLOCKS DETECTED")
        print("\nTroubleshooting:")
        print("  - Are blocks in camera view?")
        print("  - Is lighting sufficient?")
        print("  - Are colors distinct enough?")
    else:
        print(f"\n{total} total block(s) detected!")
    
    # Save annotated image
    print("\nSaving annotated image...")
    annotated = frame.copy()
    
    # Draw rectangles for each detected block
    colors_rgb = {
        'red': (0, 0, 255),
        'blue': (255, 0, 0),
        'green': (0, 255, 0),
        'yellow': (0, 255, 255),
        'purple': (255, 0, 255)
    }
    
    for color, contours in all_blocks.items():
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(annotated, (x, y), (x+w, y+h), colors_rgb[color], 2)
            cv2.putText(annotated, color, (x, y-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors_rgb[color], 2)
    
    filename = f'blocks_detected_{int(time.time())}.jpg'
    cv2.imwrite(filename, annotated)
    print(f"Saved: {filename}")
    
    # Also save raw image for comparison
    raw_filename = f'blocks_raw_{int(time.time())}.jpg'
    cv2.imwrite(raw_filename, frame)
    print(f"Saved: {raw_filename}")
    
    camera.release()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
    
    if total > 0:
        print("\nNext steps:")
        print("  1. Check annotated image to verify detections")
        print("  2. If blocks detected, try: python3 test_approach_smart.py")
        print("  3. For full pickup test: python3 test_pickup_ik.py")
    else:
        print("\nAdjust lighting or block positions and try again")


if __name__ == '__main__':
    main()
