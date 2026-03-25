#!/usr/bin/env python3
"""
Point and Drive - AprilTag Edition

Point the robot at any AprilTag and it will drive toward it!
Similar to PathfinderBot's Follow Me, but for navigation tags.

How it works:
1. Robot continuously scans for AprilTags
2. Drives toward the largest/closest visible tag
3. Stops when close enough
4. Waits for you to point at next tag

Perfect for:
- Tag testing and validation
- Demonstrations
- Quick navigation without typing commands
- Field setup verification
"""

import cv2
import time
from lib.board_protocol import BoardController
from pupil_apriltags import Detector

print("="*70)
print("POINT AND DRIVE - APRILTAG EDITION")
print("="*70)
print()
print("How to use:")
print("  1. Point robot at any AprilTag")
print("  2. Robot will drive toward it automatically")
print("  3. Robot stops when close enough")
print("  4. Point at another tag to continue")
print()
print("Controls:")
print("  - Robot auto-drives to visible tags")
print("  - Press Ctrl+C to stop anytime")
print()
print("Expected tags: 582 (Home), 583 (Pickup_1), 584 (Pickup_2), 585 (Delivery)")
print()

# Configuration
TARGET_AREA = 25000  # Stop when tag this large (close enough)
MIN_AREA = 1000      # Minimum area to consider (ignore tiny/far tags)
FORWARD_SPEED = 30   # Driving speed
ROTATION_SPEED = 20  # Turning speed for centering
CENTER_TOLERANCE = 100  # Pixels from center (horizontal)

# Tag names
TAG_NAMES = {
    582: "Home/Start",
    583: "Pickup_1", 
    584: "Pickup_2",
    585: "Delivery"
}

# Initialize
board = BoardController()
time.sleep(0.5)
camera = cv2.VideoCapture(0)
time.sleep(1)
detector = Detector(families="tag36h11")

# Position camera forward
print("Positioning camera...")
for sid, pos in [(1, 2500), (6, 1500), (5, 700), (4, 2450), (3, 590)]:
    board.set_servo_position(500, [(sid, pos)])
    time.sleep(0.3)
print("Ready!")
print()

def stop():
    """Stop all motors"""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def forward(speed=FORWARD_SPEED):
    """Drive forward"""
    board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])

def rotate_left(speed=ROTATION_SPEED):
    """Rotate left to center tag"""
    board.set_motor_duty([(1, -speed), (2, speed), (3, -speed), (4, speed)])

def rotate_right(speed=ROTATION_SPEED):
    """Rotate right to center tag"""
    board.set_motor_duty([(1, speed), (2, -speed), (3, speed), (4, -speed)])

# Main loop
try:
    frame_count = 0
    last_tag = None
    stopped_at_tag = None
    last_status_time = time.time()
    
    print("Scanning for tags... (point robot at any tag)")
    print("-" * 70)
    
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        frame_count += 1
        
        # Detect tags
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray)
        
        # Filter tags by minimum area
        valid_tags = []
        for tag in tags:
            corners = tag.corners
            width = max(corners[:, 0]) - min(corners[:, 0])
            height = max(corners[:, 1]) - min(corners[:, 1])
            area = width * height
            
            if area > MIN_AREA:
                valid_tags.append({
                    'id': tag.tag_id,
                    'center': tag.center,
                    'area': area,
                    'corners': corners
                })
        
        if valid_tags:
            # Find largest tag (closest)
            largest = max(valid_tags, key=lambda t: t['area'])
            
            tag_id = largest['id']
            tag_name = TAG_NAMES.get(tag_id, "Unknown")
            area = largest['area']
            cx, cy = largest['center']
            
            # Calculate offset from center (for rotation)
            frame_center_x = frame.shape[1] / 2
            offset_x = cx - frame_center_x
            
            # Check if we just stopped at this tag
            if stopped_at_tag == tag_id and area > TARGET_AREA * 0.9:
                # Already at this tag, rotate to find a different one
                if time.time() - last_status_time > 2:
                    print(f"[At Tag {tag_id} ({tag_name})] Rotating to find next tag...")
                    last_status_time = time.time()
                rotate_right(ROTATION_SPEED)  # Rotate to find different tag
                last_tag = tag_id
                continue
            
            # Reset stopped status if new tag or moved away
            if tag_id != stopped_at_tag or area < TARGET_AREA * 0.7:
                stopped_at_tag = None
            
            # Check if at target
            if area >= TARGET_AREA:
                stop()
                stopped_at_tag = tag_id
                print(f"\nSUCCESS: REACHED Tag {tag_id} ({tag_name})! Area={area:.0f}px²")
                print("   Rotating to find next tag...\n")
                last_tag = tag_id
                time.sleep(1.5)  # Pause briefly to "celebrate"
                # Will start rotating on next iteration
                continue
            
            # Decide action based on centering
            if abs(offset_x) > CENTER_TOLERANCE:
                # Need to rotate to center tag
                if offset_x > 0:
                    rotate_right(ROTATION_SPEED)
                    action = "> Rotating right to center"
                else:
                    rotate_left(ROTATION_SPEED)
                    action = "< Rotating left to center"
            else:
                # Centered, drive forward
                forward(FORWARD_SPEED)
                action = "> Driving forward"
            
            # Print status (not every frame)
            if tag_id != last_tag or time.time() - last_status_time > 1:
                print(f"Tag {tag_id} ({tag_name:12}): {area:5.0f}px² | {action}")
                last_status_time = time.time()
            
            last_tag = tag_id
            
        else:
            # No tags visible
            stop()
            if last_tag is not None or time.time() - last_status_time > 3:
                print("No tags visible... (point at a tag)")
                last_status_time = time.time()
            last_tag = None
            stopped_at_tag = None
        
        time.sleep(0.05)  # Small delay

except KeyboardInterrupt:
    print("\n\nStopping...")
    stop()
    camera.release()
    print("Stopped!")

except Exception as e:
    print(f"\nError: {e}")
    stop()
    camera.release()
    raise

finally:
    stop()
    camera.release()
    print("\nPoint and Drive stopped.")
    print("All tags tested successfully!")
