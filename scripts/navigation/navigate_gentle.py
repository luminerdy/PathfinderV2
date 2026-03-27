#!/usr/bin/env python3
"""
Gentle Visual Servoing Navigation
Small, slow movements to keep tag in view
"""

import cv2
import time
from lib.board import get_board as BoardController
from pupil_apriltags import Detector

print("="*60)
print("GENTLE APRILTAG NAVIGATION")
print("="*60)
print("Strategy: Small movements, frequent checks")
print("="*60)

# Gentle control parameters
ROTATION_INCREMENT = 0.08    # ULTRA small rotation steps (seconds)
DRIVE_INCREMENT = 0.25       # Very small drive steps (seconds)
SETTLE_TIME = 0.5            # Wait for camera to stabilize
SPEED_ROTATION = 18          # ULTRA slow rotation speed  
SPEED_DRIVE = 25             # Slow drive speed
CENTER_TOLERANCE = 60        # Pixels - acceptable centering error (wider tolerance)
TARGET_AREA = 28000          # Target distance
MAX_ITERATIONS = 150         # More iterations for gradual approach

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

def rotate_tiny(direction, duration=ROTATION_INCREMENT):
    """Tiny rotation step"""
    if direction == 'right':
        board.set_motor_duty([(1,SPEED_ROTATION), (2,-SPEED_ROTATION), 
                              (3,SPEED_ROTATION), (4,-SPEED_ROTATION)])
    else:  # left
        board.set_motor_duty([(1,-SPEED_ROTATION), (2,SPEED_ROTATION),
                              (3,-SPEED_ROTATION), (4,SPEED_ROTATION)])
    time.sleep(duration)
    stop()

def drive_tiny(duration=DRIVE_INCREMENT):
    """Tiny forward step"""
    board.set_motor_duty([(1,SPEED_DRIVE), (2,SPEED_DRIVE), 
                          (3,SPEED_DRIVE), (4,SPEED_DRIVE)])
    time.sleep(duration)
    stop()

def get_tag_info():
    """Get tag info with retries"""
    # Try a few times in case of temporary glitch
    for attempt in range(3):
        ret, frame = camera.read()
        if not ret:
            time.sleep(0.1)
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray)
        
        if tags:
            tag = tags[0]
            corners = tag.corners
            area = (max(corners[:,0])-min(corners[:,0])) * \
                   (max(corners[:,1])-min(corners[:,1]))
            error_x = tag.center[0] - 320
            
            return {
                'id': tag.tag_id,
                'area': area,
                'error_x': error_x,
                'center_x': tag.center[0],
                'frame': frame
            }
        
        if attempt < 2:
            time.sleep(0.1)
    
    return None

def search_for_tag():
    """Gentle search rotation"""
    print("Searching for tag (gentle rotation)...")
    
    for attempt in range(25):
        info = get_tag_info()
        if info:
            print(f"\nFOUND: Tag {info['id']}, area={info['area']:.0f}")
            return info
        
        print(f"  {attempt+1}/25", end="\r")
        rotate_tiny('right', 0.3)
        time.sleep(SETTLE_TIME)
    
    return None

def backup_tiny(duration=0.3):
    """Tiny backward step"""
    board.set_motor_duty([(1,-SPEED_DRIVE), (2,-SPEED_DRIVE), 
                          (3,-SPEED_DRIVE), (4,-SPEED_DRIVE)])
    time.sleep(duration)
    stop()

def gentle_center(info, max_iterations=30):
    """
    Gently center tag in view
    Returns True if centered, False if lost
    """
    print(f"\nCentering on tag (gentle corrections)...")
    
    for iteration in range(max_iterations):
        # Check tag
        info = get_tag_info()
        if not info:
            print(f"  [{iteration+1}] Lost tag!")
            return False
        
        error_x = info['error_x']
        
        # Already centered?
        if abs(error_x) < CENTER_TOLERANCE:
            print(f"  [{iteration+1}] Centered! (error: {error_x:.0f}px)")
            return True
        
        # Decide correction
        if abs(error_x) > 100:
            # Larger error - slightly longer step
            duration = ROTATION_INCREMENT * 1.5
        else:
            # Small error - tiny step
            duration = ROTATION_INCREMENT
        
        direction = 'right' if error_x > 0 else 'left'
        
        if iteration % 5 == 0:
            print(f"  [{iteration+1}] error={error_x:.0f}px, rotating {direction}")
        
        # Make tiny correction
        rotate_tiny(direction, duration)
        
        # Wait for stabilization
        time.sleep(SETTLE_TIME)
    
    return False

def gentle_approach(info):
    """
    Gently approach tag
    Re-center after each forward step
    """
    print(f"\nApproaching tag (gentle steps)...")
    print(f"Target area: {TARGET_AREA} pixels²\n")
    
    for iteration in range(MAX_ITERATIONS):
        # Check tag
        info = get_tag_info()
        if not info:
            print(f"  [{iteration+1}] Lost tag! Stopping.")
            return False
        
        area = info['area']
        error_x = info['error_x']
        
        # Reached target?
        if area >= TARGET_AREA:
            print(f"\n  [{iteration+1}] TARGET REACHED! Area={area:.0f}")
            cv2.imwrite(f"gentle_nav_success_{int(time.time())}.jpg", info['frame'])
            return True
        
        # Is it well-centered before driving?
        if abs(error_x) > CENTER_TOLERANCE * 1.5:
            # Need to center first
            if iteration % 10 == 0:
                print(f"  [{iteration+1}] Re-centering (off by {error_x:.0f}px)")
            
            direction = 'right' if error_x > 0 else 'left'
            rotate_tiny(direction, ROTATION_INCREMENT * 0.8)
            time.sleep(SETTLE_TIME)
            continue
        
        # Tag centered, safe to drive forward
        if iteration % 10 == 0:
            print(f"  [{iteration+1}] area={area:.0f}, centered, inching forward")
        
        # Tiny forward step
        drive_tiny(DRIVE_INCREMENT)
        
        # Wait for stabilization
        time.sleep(SETTLE_TIME)
    
    print(f"\n  Max iterations reached")
    return False

# Main
try:
    # Search
    info = search_for_tag()
    if not info:
        print("\nNo tag found")
    else:
        # Check if too close
        if info['area'] > TARGET_AREA * 3:
            print(f"\nTag VERY close (area={info['area']:.0f})!")
            print("Backing up to safe distance...")
            
            for i in range(10):
                backup_tiny(0.5)
                time.sleep(SETTLE_TIME)
                
                info = get_tag_info()
                if not info:
                    print(f"  Lost tag while backing up")
                    break
                
                if info['area'] < TARGET_AREA * 2:
                    print(f"  Good distance (area={info['area']:.0f})")
                    break
        
        # Center
        info = get_tag_info()
        if not info:
            print("\nLost tag")
        else:
            centered = gentle_center(info)
        if not centered:
            print("\nFailed to center")
        else:
            # Approach
            success = gentle_approach(info)
            if success:
                print("\n" + "="*60)
                print("SUCCESS!")
                print("="*60)
                print("Reached tag with gentle navigation")
            else:
                print("\nApproach failed")

except KeyboardInterrupt:
    print("\n\nStopped")
finally:
    stop()
    camera.release()
    print("Done")
