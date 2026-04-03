#!/usr/bin/env python3
"""
Tour All 8 Tags - Point, Drive, Repeat

Cycles through all 8 tags (578-585) in order:
1. Point to tag (rotate to find it)
2. Drive to it
3. Move to next tag
4. Repeat!
"""

import cv2
import time
import math
from lib.board import get_board as BoardController
from lib.sonar import Sonar
from pupil_apriltags import Detector

print("="*70)
print("8-TAG TOUR - Point, Drive, Next!")
print("="*70)
print()

# Tag sequence
TAG_SEQUENCE = [578, 579, 580, 581, 582, 583, 584, 585]
TAG_NAMES = {
    578: "North Left",
    579: "North Right", 
    580: "East Left",
    581: "East Right",
    582: "South Left",
    583: "South Right",
    584: "West Left",
    585: "West Right"
}

TARGET_AREA = 25000
MIN_AREA = 2000
DRIVE_SPEED = 28
SEARCH_SPEED = 28  # Increased from 22 (calibrated minimum for rotation)
SONAR_STOP = 18  # cm
CENTER_TOLERANCE = 80  # pixels from center (640/2 = 320)

# Camera params for pose
CAMERA_PARAMS = [500, 500, 320, 240]
TAG_SIZE = 0.254

# Initialize
board = BoardController()
sonar = Sonar()
time.sleep(0.5)

camera = cv2.VideoCapture(0)
time.sleep(1)
detector = Detector(families='tag36h11')

# Position camera
print("Positioning camera...")
for sid, pos in [(1, 2500), (6, 1500), (5, 700), (4, 2450), (3, 590)]:
    board.set_servo_position(500, [(sid, pos)])
    time.sleep(0.3)
print("Ready!")
print()

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def forward(speed=DRIVE_SPEED):
    board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])

def rotate_right(speed=SEARCH_SPEED):
    board.set_motor_duty([(1, speed), (2, -speed), (3, speed), (4, -speed)])

tags_visited = 0

try:
    for target_tag in TAG_SEQUENCE:
        tag_name = TAG_NAMES[target_tag]
        print(f"\n{'='*70}")
        print(f"TARGET: Tag {target_tag} ({tag_name})")
        print(f"{'='*70}\n")
        
        # PHASE 1: Find the tag
        print(f"Searching for Tag {target_tag}...")
        found = False
        search_count = 0
        
        while search_count < 40 and not found:
            search_count += 1
            
            # Rotate a bit, then STOP to check
            rotate_right(SEARCH_SPEED)
            time.sleep(0.2)
            stop()
            time.sleep(0.15)
            
            ret, frame = camera.read()
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = detector.detect(gray)
            
            # Look for our target tag
            for tag in tags:
                if tag.tag_id == target_tag:
                    corners = tag.corners
                    width = max(corners[:, 0]) - min(corners[:, 0])
                    height = max(corners[:, 1]) - min(corners[:, 1])
                    area = width * height
                    
                    if area > MIN_AREA:
                        print(f"  Found! Area: {area:.0f} px²")
                        found = True
                        time.sleep(0.3)
                        break
            
            if found:
                break
        
        if not found:
            print(f"  Could not find Tag {target_tag}, skipping...")
            continue
        
        # PHASE 2: Check if already too close
        sonar_dist = sonar.get_distance()
        if sonar_dist is not None and sonar_dist > 0 and sonar_dist < 60:
            print(f"  Already close to wall ({sonar_dist:.0f}cm), backing up first...")
            board.set_motor_duty([(1, -28), (2, -28), (3, -28), (4, -28)])
            time.sleep(1.5)
            stop()
            time.sleep(0.5)
            new_dist = sonar.get_distance()
            if new_dist is not None and new_dist > 0:
                print(f"  Now at {new_dist:.0f}cm")
            else:
                print(f"  Backed up (sonar reading unclear)")
        
        # PHASE 3: Approach the tag
        print(f"Approaching Tag {target_tag}...")
        approach_count = 0
        
        while approach_count < 100:
            approach_count += 1
            
            # Check sonar safety
            sonar_dist = sonar.get_distance()
            if sonar_dist is not None and sonar_dist > 0 and sonar_dist < SONAR_STOP:
                stop()
                print(f"  SONAR STOP at {sonar_dist:.1f}cm")
                break
            
            ret, frame = camera.read()
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = detector.detect(gray)
            
            # Find our target tag
            target_found = False
            for tag in tags:
                if tag.tag_id == target_tag:
                    target_found = True
                    corners = tag.corners
                    width = max(corners[:, 0]) - min(corners[:, 0])
                    height = max(corners[:, 1]) - min(corners[:, 1])
                    area = width * height
                    
                    # Get tag center position
                    center_x = tag.center[0]
                    frame_center_x = 320  # 640/2
                    offset_x = center_x - frame_center_x
                    
                    # Check if reached
                    if area >= TARGET_AREA:
                        stop()
                        print(f"  REACHED Tag {target_tag}! Area: {area:.0f} px²")
                        tags_visited += 1
                        time.sleep(1)
                        break
                    
                    # Decide action: CENTER first, then APPROACH
                    if abs(offset_x) > CENTER_TOLERANCE:
                        # Tag is off-center - rotate to center it
                        if offset_x > 0:
                            # Tag on right, rotate right
                            rotate_right(18)
                            action = "centering right"
                        else:
                            # Tag on left, rotate left
                            board.set_motor_duty([(1, -18), (2, 18), (3, -18), (4, 18)])
                            action = "centering left"
                    else:
                        # Tag centered - drive forward with speed control
                        if area > 15000:
                            speed = 20  # SLOW when very close
                        elif area > 10000:
                            speed = 24  # Medium when close
                        else:
                            speed = DRIVE_SPEED  # Full speed when far
                        
                        forward(speed)
                        action = f"driving (speed {speed})"
                    
                    if approach_count % 20 == 0:
                        print(f"  {area:.0f} px², offset {offset_x:+.0f}px - {action}")
                    
                    break
            
            if not target_found:
                # Lost tag - try to re-find it
                stop()
                print(f"  Lost tag, re-searching...")
                
                # Quick search
                for rescan in range(10):
                    rotate_right(18)
                    time.sleep(0.15)
                    stop()
                    time.sleep(0.1)
                    
                    ret, frame = camera.read()
                    if ret:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        tags = detector.detect(gray)
                        for tag in tags:
                            if tag.tag_id == target_tag:
                                corners = tag.corners
                                width = max(corners[:, 0]) - min(corners[:, 0])
                                height = max(corners[:, 1]) - min(corners[:, 1])
                                area = width * height
                                print(f"  Re-found! {area:.0f} px²")
                                target_found = True
                                time.sleep(0.3)
                                break
                    if target_found:
                        break
                
                if not target_found:
                    print(f"  Could not re-find Tag {target_tag}")
                    break
            
            if area >= TARGET_AREA:
                break
            
            time.sleep(0.05)
        
        print(f"Tag {target_tag} complete!")
    
    stop()
    
    print("\n" + "="*70)
    print("TOUR COMPLETE!")
    print("="*70)
    print(f"Tags visited: {tags_visited}/{len(TAG_SEQUENCE)}")
    
    if tags_visited == len(TAG_SEQUENCE):
        print("\nSUCCESS - Visited all 8 tags!")
    else:
        print(f"\nPartial tour - {tags_visited} tags reached")
    print()

except KeyboardInterrupt:
    print("\n\nTour stopped by user")
    stop()

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    stop()

finally:
    stop()
    camera.release()
    print("Tour ended.")
