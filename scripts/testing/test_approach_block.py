#!/usr/bin/env python3
"""
Test vision-guided approach to colored block
Uses camera + mecanum drive to approach a block
"""

import cv2
import numpy as np
from lib.board import get_board as BoardController
import time

# Color detection parameters
COLORS = {
    'red': [(0, 100, 100), (10, 255, 255)],
    'red2': [(170, 100, 100), (180, 255, 255)],
}

def detect_block(frame, color='red'):
    """Detect colored block in frame"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Create mask
    lower, upper = COLORS[color]
    mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
    
    # For red, combine both ranges
    if color == 'red':
        mask2 = cv2.inRange(hsv, np.array(COLORS['red2'][0]), np.array(COLORS['red2'][1]))
        mask = cv2.bitwise_or(mask, mask2)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return None
    
    # Get largest contour
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    
    if area < 100:
        return None
    
    # Get center
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None
    
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])
    
    return {
        'center': (cx, cy),
        'area': area,
        'contour': largest
    }

print("=" * 60)
print("VISION-GUIDED BLOCK APPROACH TEST")
print("=" * 60)
print("\nTarget: RED block")
print("Robot will approach the block using camera feedback")
print()

# Initialize
board = BoardController()
cap = cv2.VideoCapture(0)
time.sleep(0.5)

# Constants
IMAGE_CENTER_X = 320  # 640 / 2
IMAGE_CENTER_Y = 240  # 480 / 2
TARGET_AREA = 2000    # Stop when block is this large
DEADZONE = 50         # Pixels - don't correct if within this
SPEED = 25            # Motor speed

print("Starting approach sequence...\n")

try:
    iteration = 0
    while iteration < 20:  # Max 20 iterations
        iteration += 1
        
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame")
            break
        
        # Detect block
        block = detect_block(frame, 'red')
        
        if not block:
            # Debug: why no detection?
            import numpy as np
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask1 = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
            mask2 = cv2.inRange(hsv, np.array([170, 100, 100]), np.array([180, 255, 255]))
            mask = cv2.bitwise_or(mask1, mask2)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print(f"[{iteration}] No block returned but {len(contours)} red contours found")
            break
        
        # Calculate offsets
        cx, cy = block['center']
        area = block['area']
        offset_x = cx - IMAGE_CENTER_X
        offset_y = cy - IMAGE_CENTER_Y
        
        print(f"[{iteration}] Block at ({cx},{cy}) area={area:.0f} offset=({offset_x:+4d},{offset_y:+4d})")
        
        # Check if close enough
        if area >= TARGET_AREA:
            print(f"\n[OK] ARRIVED! Block area {area:.0f} >= target {TARGET_AREA}")
            break
        
        # SIMPLE TEST: Just drive straight forward toward any detected block
        # No turning, no strafing - just approach
        
        forward = 0
        
        # If block detected and not close enough, drive forward
        if area < TARGET_AREA:
            forward = SPEED
        
        # All wheels same speed = straight forward
        fl = forward
        fr = forward
        rl = forward
        rr = forward
        
        # Limit to reasonable range
        fl = max(-50, min(50, fl))
        fr = max(-50, min(50, fr))
        rl = max(-50, min(50, rl))
        rr = max(-50, min(50, rr))
        
        print(f"  Motors: FL={fl:+3.0f} FR={fr:+3.0f} RL={rl:+3.0f} RR={rr:+3.0f}")
        
        board.set_motor_duty([
            (1, fl),  # Front left
            (2, fr),  # Front right
            (3, rl),  # Rear left
            (4, rr)   # Rear right
        ])
        
        # Wait before next iteration
        time.sleep(0.3)
    
    # Stop motors
    print("\nStopping motors...")
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
except KeyboardInterrupt:
    print("\n\nInterrupted by user")
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

finally:
    cap.release()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
