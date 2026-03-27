#!/usr/bin/env python3
"""
Autonomous AprilTag Tour

Behavior:
1. Look forward for AprilTag
2. If tag visible, drive to it
3. When reached, turn and scan for another tag
4. Repeat forever!

Perfect for:
- Testing all field tags
- Continuous demonstration
- Field validation
"""

import cv2
import time
from lib.board import get_board as BoardController
from pupil_apriltags import Detector

print("="*70)
print("AUTONOMOUS APRILTAG TOUR")
print("="*70)
print()
print("Behavior:")
print("  1. Look forward for AprilTag")
print("  2. Drive to it when seen")
print("  3. When reached, scan for different tag")
print("  4. Repeat!")
print()
print("Press Ctrl+C to stop")
print()

# Configuration
TARGET_AREA = 25000      # Stop when this close
MIN_AREA = 1500          # Minimum to start approach
DRIVE_SPEED = 30         # Forward speed
SCAN_SPEED = 25          # Rotation speed for scanning
CENTER_TOLERANCE = 80    # Centering precision

TAG_NAMES = {
    582: "Home",
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

# Position camera
print("Positioning camera forward...")
for sid, pos in [(1, 2500), (6, 1500), (5, 700), (4, 2450), (3, 590)]:
    board.set_servo_position(500, [(sid, pos)])
    time.sleep(0.3)

print("Ready! Starting tour...\n")

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def forward(speed=DRIVE_SPEED):
    board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])

def rotate_right(speed=SCAN_SPEED):
    board.set_motor_duty([(1, speed), (2, -speed), (3, speed), (4, -speed)])

def rotate_left(speed=SCAN_SPEED):
    board.set_motor_duty([(1, -speed), (2, speed), (3, -speed), (4, speed)])

# State machine
STATE_LOOKING = "looking"
STATE_APPROACHING = "approaching"
STATE_SCANNING = "scanning"

state = STATE_LOOKING
current_tag = None
last_tag_reached = None
scan_start_time = None
last_print = time.time()

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            continue
        
        # Detect tags
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray)
        
        # Find valid tags
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
                    'area': area
                })
        
        # STATE: LOOKING FORWARD
        if state == STATE_LOOKING:
            if valid_tags:
                # Found a tag!
                tag = max(valid_tags, key=lambda t: t['area'])
                current_tag = tag['id']
                tag_name = TAG_NAMES.get(current_tag, "Unknown")
                
                print(f"Tag {current_tag} ({tag_name}) spotted! Area={tag['area']:.0f}px")
                print(f"  -> Driving to Tag {current_tag}")
                state = STATE_APPROACHING
            else:
                # No tag, just wait
                stop()
                if time.time() - last_print > 3:
                    print("[Looking forward for tags...]")
                    last_print = time.time()
        
        # STATE: APPROACHING TAG
        elif state == STATE_APPROACHING:
            # Find current tag
            tag = None
            for t in valid_tags:
                if t['id'] == current_tag:
                    tag = t
                    break
            
            if tag:
                area = tag['area']
                cx, cy = tag['center']
                frame_center_x = frame.shape[1] / 2
                offset_x = cx - frame_center_x
                
                # Check if reached
                if area >= TARGET_AREA:
                    stop()
                    tag_name = TAG_NAMES.get(current_tag, "Unknown")
                    print(f"\nREACHED Tag {current_tag} ({tag_name})! Area={area:.0f}px")
                    print(f"  -> Scanning for different tag...\n")
                    
                    last_tag_reached = current_tag
                    state = STATE_SCANNING
                    scan_start_time = time.time()
                    continue
                
                # Center and approach
                if abs(offset_x) > CENTER_TOLERANCE:
                    # Rotate to center
                    if offset_x > 0:
                        rotate_right(20)
                        action = "centering right"
                    else:
                        rotate_left(20)
                        action = "centering left"
                else:
                    # Drive forward
                    forward(DRIVE_SPEED)
                    action = "driving"
                
                # Status
                if time.time() - last_print > 1:
                    print(f"  Tag {current_tag}: {area:5.0f}px ({action})")
                    last_print = time.time()
            
            else:
                # Lost tag during approach
                print(f"  Lost Tag {current_tag}, continuing forward...")
                forward(DRIVE_SPEED)
        
        # STATE: SCANNING FOR NEW TAG
        elif state == STATE_SCANNING:
            # Rotate and look for a DIFFERENT tag
            rotate_right(SCAN_SPEED)
            
            # Find different tag
            different_tags = [t for t in valid_tags if t['id'] != last_tag_reached]
            
            if different_tags:
                # Found a different tag!
                tag = max(different_tags, key=lambda t: t['area'])
                current_tag = tag['id']
                tag_name = TAG_NAMES.get(current_tag, "Unknown")
                
                stop()
                print(f"Found Tag {current_tag} ({tag_name})! Area={tag['area']:.0f}px")
                print(f"  -> Driving to Tag {current_tag}")
                
                state = STATE_APPROACHING
                time.sleep(0.5)  # Brief pause
            
            else:
                # Still scanning
                if time.time() - last_print > 2:
                    elapsed = int(time.time() - scan_start_time)
                    print(f"  [Scanning... {elapsed}s]")
                    last_print = time.time()
                
                # Timeout after 20 seconds - go back to looking
                if time.time() - scan_start_time > 20:
                    print("  Scan timeout, looking forward again")
                    stop()
                    state = STATE_LOOKING
                    last_tag_reached = None
        
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nStopping tour...")
    stop()
    camera.release()
    print("Tour stopped!")

finally:
    stop()
    camera.release()
