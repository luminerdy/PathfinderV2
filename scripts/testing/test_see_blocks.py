#!/usr/bin/env python3
"""
Simple Block Detection Test
Shows what blocks robot can see
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
        camera.release()
        return
    
    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")
    
    # Detect each color
    print("\n" + "=" * 60)
    print("DETECTION RESULTS")
    print("=" * 60)
    
    colors_to_check = ['red', 'blue', 'green', 'yellow', 'purple']
    detections = {}
    total = 0
    
    for color in colors_to_check:
        result = vision.detect_color(frame, color, min_area=500)
        if result:
            x, y, radius = result
            detections[color] = (x, y, radius)
            total += 1
            
            print(f"\n{color.upper()} BLOCK DETECTED:")
            print(f"  Position: ({x}, {y}) pixels")
            print(f"  Size: {int(radius*2)} pixels diameter")
            
            # Estimate distance from size
            area = 3.14159 * radius * radius
            if area > 3000:
                distance = "CLOSE (ready to pickup)"
            elif area > 1500:
                distance = "MEDIUM (approach needed)"  
            else:
                distance = "FAR (drive forward)"
            print(f"  Distance: {distance}")
            print(f"  Area: {int(area)} pixels²")
    
    if total == 0:
        print("\nNO BLOCKS DETECTED")
        print("\nTroubleshooting:")
        print("  - Are blocks in camera view?")
        print("  - Is lighting sufficient?")
        print("  - Try adjusting HSV ranges in config.yaml")
    else:
        print(f"\n{total} block(s) detected!")
    
    # Save annotated image
    print("\nSaving images...")
    annotated = frame.copy()
    
    colors_rgb = {
        'red': (0, 0, 255),
        'blue': (255, 0, 0),
        'green': (0, 255, 0),
        'yellow': (0, 255, 255),
        'purple': (255, 0, 255)
    }
    
    for color, (x, y, radius) in detections.items():
        # Draw circle around detected block
        cv2.circle(annotated, (x, y), int(radius), colors_rgb[color], 2)
        cv2.circle(annotated, (x, y), 3, colors_rgb[color], -1)  # Center dot
        # Label
        cv2.putText(annotated, color.upper(), (x-30, y-int(radius)-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors_rgb[color], 2)
    
    # Save files
    timestamp = int(time.time())
    annotated_file = f'blocks_detected_{timestamp}.jpg'
    raw_file = f'blocks_raw_{timestamp}.jpg'
    
    cv2.imwrite(annotated_file, annotated)
    cv2.imwrite(raw_file, frame)
    
    print(f"  Annotated: {annotated_file}")
    print(f"  Raw: {raw_file}")
    
    camera.release()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
    
    if total > 0:
        print("\nNext steps:")
        print("  1. Check annotated image to verify detections")
        print("  2. Try approaching a block: python3 test_approach_smart.py")
        print("  3. Test IK pickup: python3 test_pickup_ik.py")


if __name__ == '__main__':
    main()
