#!/usr/bin/env python3
"""
Visual Servoing Navigation to AprilTag
Continuously corrects heading while approaching to keep tag centered
"""

import cv2
import time
import math
from lib.board_protocol import BoardController
from pupil_apriltags import Detector

print("="*60)
print("VISUAL SERVOING APRILTAG NAVIGATION")
print("="*60)

# Control parameters
Kp_rotation = 0.15    # Proportional gain for rotation (tune this!)
Kp_forward = 0.08     # Proportional gain for forward speed
TARGET_AREA = 30000   # Stop when tag this large
CENTER_TOLERANCE = 20 # Pixels - "close enough" to center
MIN_AREA = 500        # Minimum detectable area
MAX_ITERATIONS = 100  # Safety limit

board = BoardController()
time.sleep(0.5)
camera = cv2.VideoCapture(0)
time.sleep(1)
detector = Detector(families="tag16h5")

print("\nPositioning camera...")
for sid, p in [(1,2500), (6,1500), (5,700), (4,2450), (3,590)]:
    board.set_servo_position(500, [(sid, p)])
    time.sleep(0.3)
print("Ready!\n")

def stop():
    board.set_motor_duty([(1,0), (2,0), (3,0), (4,0)])

def set_drive_speeds(left_speed, right_speed):
    """
    Differential drive - different left/right speeds for turning while driving
    
    Args:
        left_speed: Speed for left wheels (-100 to 100)
        right_speed: Speed for right wheels (-100 to 100)
    """
    # Clamp to valid range
    left_speed = max(-100, min(100, left_speed))
    right_speed = max(-100, min(100, right_speed))
    
    board.set_motor_duty([
        (1, left_speed),   # Front left
        (2, right_speed),  # Front right
        (3, left_speed),   # Rear left
        (4, right_speed)   # Rear right
    ])

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
    center_y = tag.center[1]
    
    # Calculate error from image center
    error_x = center_x - 320  # Horizontal offset
    error_y = center_y - 240  # Vertical offset (not used for now)
    
    return {
        'id': tag.tag_id,
        'area': area,
        'center_x': center_x,
        'center_y': center_y,
        'error_x': error_x,
        'frame': frame
    }

def search_for_tag():
    """Rotate to find a tag"""
    print("Searching for tag...")
    
    for attempt in range(20):
        print(f"  Attempt {attempt+1}/20...", end="")
        
        # Rotate
        set_drive_speeds(25, -25)
        time.sleep(0.5)
        stop()
        time.sleep(0.3)
        
        info = get_tag_info()
        if info:
            print(f" FOUND tag {info['id']}!")
            return info
        else:
            print(" no tag")
    
    return None

def visual_servo_approach(initial_info):
    """
    Approach tag using visual servoing
    Continuously adjusts heading to keep tag centered
    """
    print(f"\nApproaching tag {initial_info['id']} with visual servoing...")
    print(f"Target area: {TARGET_AREA} pixels²")
    print("\nControl law:")
    print("  rotation_speed = Kp_rotation * error_x")
    print("  forward_speed = base_speed - abs(rotation_speed)")
    print()
    
    iteration = 0
    lost_count = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        
        # Get current tag position
        info = get_tag_info()
        
        if not info:
            lost_count += 1
            print(f"  [{iteration}] Tag lost ({lost_count}/3)")
            
            if lost_count >= 3:
                print("  Tag lost too many times, aborting")
                stop()
                return False
            
            # Stop and wait
            stop()
            time.sleep(0.3)
            continue
        
        lost_count = 0  # Reset lost counter
        
        area = info['area']
        error_x = info['error_x']
        
        # Check if reached target
        if area >= TARGET_AREA:
            print(f"\n  [{iteration}] TARGET REACHED! Area={area:.0f}")
            cv2.imwrite(f"visual_servo_reached_{int(time.time())}.jpg", info['frame'])
            stop()
            return True
        
        # Check if tag too small (too far)
        if area < MIN_AREA:
            print(f"  [{iteration}] Tag too small ({area:.0f}), can't approach safely")
            stop()
            return False
        
        # Visual servoing control law
        # Rotation speed proportional to horizontal error
        rotation_speed = Kp_rotation * error_x
        
        # Base forward speed - reduce when rotating a lot
        base_forward_speed = 35
        forward_speed = base_forward_speed - abs(rotation_speed) * 0.5
        
        # Make sure we're always moving forward
        forward_speed = max(20, forward_speed)
        
        # Calculate differential drive speeds
        left_speed = forward_speed - rotation_speed
        right_speed = forward_speed + rotation_speed
        
        # Clamp speeds
        left_speed = max(-100, min(100, left_speed))
        right_speed = max(-100, min(100, right_speed))
        
        # Apply control
        set_drive_speeds(left_speed, right_speed)
        
        # Status every 5 iterations
        if iteration % 5 == 0:
            centered = "CENTERED" if abs(error_x) < CENTER_TOLERANCE else f"off by {error_x:.0f}px"
            print(f"  [{iteration}] area={area:.0f}, {centered}, L={left_speed:.0f} R={right_speed:.0f}")
        
        # Control loop rate
        time.sleep(0.1)
    
    print(f"\n  Max iterations reached")
    stop()
    return False

# Main navigation
try:
    # Step 1: Find tag
    initial_info = search_for_tag()
    
    if not initial_info:
        print("\nNo tag found!")
    else:
        # Step 2: Approach with visual servoing
        success = visual_servo_approach(initial_info)
        
        if success:
            print("\n" + "="*60)
            print("NAVIGATION SUCCESS!")
            print("="*60)
            print("\nRobot successfully approached AprilTag")
            print("using continuous visual servoing control")
        else:
            print("\nNavigation failed")

except KeyboardInterrupt:
    print("\n\nStopped by user")
finally:
    stop()
    camera.release()
    print("\nMotors stopped")
