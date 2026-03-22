#!/usr/bin/env python3
"""
Simple AprilTag Navigation
Uses empirical pixel area thresholds (no sonar needed)
"""

import cv2
import time
from lib.board_protocol import BoardController
from pupil_apriltags import Detector

print("="*60)
print("APRILTAG NAVIGATION - EMPIRICAL VERSION")
print("="*60)

# Empirical thresholds from testing
TARGET_AREA = 35000  # Stop when tag this large (close but not too close)
TOO_CLOSE = 50000    # Too close, back up
TOO_FAR = 5000       # Very far, need to approach

board = BoardController()
time.sleep(0.5)
camera = cv2.VideoCapture(0)
time.sleep(1)
detector = Detector(families="tag16h5")

# Position camera
print("\nPositioning camera...")
for sid, p in [(1,2500), (6,1500), (5,700), (4,2450), (3,590)]:
    board.set_servo_position(500, [(sid, p)])
    time.sleep(0.3)
print("Ready!\n")

def stop():
    board.set_motor_duty([(1,0), (2,0), (3,0), (4,0)])

def rotate_right(t):
    board.set_motor_duty([(1,25), (2,-25), (3,25), (4,-25)])
    time.sleep(t)
    stop()

def rotate_left(t):
    board.set_motor_duty([(1,-25), (2,25), (3,-25), (4,25)])
    time.sleep(t)
    stop()

def forward(t, speed=30):
    board.set_motor_duty([(1,speed), (2,speed), (3,speed), (4,speed)])
    time.sleep(t)
    stop()

def backward(t):
    board.set_motor_duty([(1,-30), (2,-30), (3,-30), (4,-30)])
    time.sleep(t)
    stop()

def get_tag_info():
    """Get tag detection info"""
    ret, frame = camera.read()
    if not ret:
        return None
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)
    
    if not tags:
        return None
    
    tag = tags[0]
    corners = tag.corners
    area = (max(corners[:,0])-min(corners[:,0])) * (max(corners[:,1])-min(corners[:,1]))
    center_x = tag.center[0]
    offset = center_x - 320
    
    return {
        'id': tag.tag_id,
        'area': area,
        'offset': offset,
        'frame': frame
    }

def navigate_to_tag():
    """Complete navigation sequence"""
    
    # STEP 1: Search for tag
    print("STEP 1: Searching for tag...")
    for attempt in range(20):
        print(f"  Search {attempt+1}/20...", end="")
        
        rotate_right(0.5)
        time.sleep(0.3)
        
        info = get_tag_info()
        if info:
            print(f" FOUND tag {info['id']}!")
            cv2.imwrite(f"nav_found_{int(time.time())}.jpg", info['frame'])
            break
        else:
            print(" no tag")
    
    if not info:
        print("\nNo tag found after full rotation!")
        return False
    
    print(f"\nTarget: Tag {info['id']}")
    
    # STEP 2: Center on tag
    print("\nSTEP 2: Centering on tag...")
    for iteration in range(10):
        info = get_tag_info()
        if not info:
            print("  Lost tag!")
            return False
        
        print(f"  Offset: {info['offset']:.0f}px", end="")
        
        if abs(info['offset']) < 30:
            print(" - Centered!")
            break
        
        # Calculate rotation time
        rot_time = min(abs(info['offset'])/200, 1.0)
        
        if info['offset'] > 0:
            print(f" - rotate right {rot_time:.2f}s")
            rotate_right(rot_time)
        else:
            print(f" - rotate left {rot_time:.2f}s")
            rotate_left(rot_time)
        
        time.sleep(0.3)
    
    # STEP 3: Approach to target distance
    print("\nSTEP 3: Approaching tag...")
    print(f"  Target area: {TARGET_AREA} pixels")
    
    for iteration in range(20):
        info = get_tag_info()
        if not info:
            print("  Lost tag!")
            return False
        
        area = info['area']
        
        # Check distance
        if area > TOO_CLOSE:
            print(f"  Area {area:.0f} - TOO CLOSE, backing up")
            backward(0.3)
        elif area > TARGET_AREA:
            print(f"  Area {area:.0f} - TARGET REACHED!")
            cv2.imwrite(f"nav_reached_{int(time.time())}.jpg", info['frame'])
            break
        elif area < TOO_FAR:
            print(f"  Area {area:.0f} - very far, driving forward")
            forward(0.8)
        else:
            print(f"  Area {area:.0f} - approaching")
            forward(0.4)
        
        time.sleep(0.3)
    
    print("\n" + "="*60)
    print(f"SUCCESS! Reached tag {info['id']}")
    print("="*60)
    return True

# Run navigation
try:
    success = navigate_to_tag()
    
    if success:
        print("\nNavigation complete!")
        
        # Option: try to find another tag
        print("\nBacking up to find another tag...")
        backward(2.0)
        time.sleep(0.5)
        
        print("\nRotating to search...")
        rotate_right(3.0)
        
        print("\nReady for another navigation run!")
    else:
        print("\nNavigation failed")

except KeyboardInterrupt:
    print("\n\nStopped by user")
finally:
    stop()
    camera.release()
    print("\nMotors stopped, camera released")
