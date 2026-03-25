#!/usr/bin/env python3
"""
Test Centering Skill

Tests the proportional centering controller on real AprilTags.
Shows improvement over fixed-speed rotation.
"""

import cv2
import time
import math
from pupil_apriltags import Detector
from skills.centering import CenteringController

print("="*70)
print("CENTERING SKILL TEST")
print("="*70)
print()
print("Testing proportional centering on AprilTags")
print("Will center on any visible tag using pose angle")
print()

# Initialize
camera = cv2.VideoCapture(0)
time.sleep(1.5)
detector = Detector(families='tag36h11')
centering = CenteringController()

# Camera params
CAMERA_PARAMS = [500, 500, 320, 240]
TAG_SIZE = 0.254

print("Looking for tags...\n")

# Find a tag
for scan in range(20):
    ret, frame = camera.read()
    if not ret:
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True,
                           camera_params=CAMERA_PARAMS,
                           tag_size=TAG_SIZE)
    
    if tags:
        tag = tags[0]  # Use first tag
        
        print(f"Found Tag {tag.tag_id}")
        print()
        
        # Show initial state
        if tag.pose_t is not None:
            x = tag.pose_t[0][0]
            z = tag.pose_t[2][0]
            angle = math.degrees(math.atan2(x, z))
            dist = math.sqrt(x**2 + z**2)
            print(f"Initial state:")
            print(f"  Angle: {angle:+.1f}°")
            print(f"  Distance: {dist:.2f}m")
            print(f"  Centered: {centering.is_centered_angle(angle)}")
        else:
            offset = tag.center[0] - 320
            print(f"Initial state:")
            print(f"  Pixel offset: {offset:+.0f}px")
            print(f"  Centered: {centering.is_centered_pixels(tag.center[0])}")
        print()
        
        # Calculate rotation needed
        if tag.pose_t is not None:
            speed, duration, direction = centering.calculate_rotation(angle_deg=angle)
        else:
            speed, duration, direction = centering.calculate_rotation(target_x=tag.center[0])
        
        if direction:
            print(f"Rotation plan:")
            print(f"  Direction: {direction}")
            print(f"  Speed: {speed}")
            print(f"  Duration: {duration:.2f}s")
            print()
            
            # Execute centering
            print("Centering...")
            was_centered = centering.center_on_tag(tag, verbose=False)
            
            # Check result
            time.sleep(0.5)
            ret, frame = camera.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                tags = detector.detect(gray, estimate_tag_pose=True,
                                       camera_params=CAMERA_PARAMS,
                                       tag_size=TAG_SIZE)
                
                if tags and tags[0].tag_id == tag.tag_id:
                    new_tag = tags[0]
                    
                    if new_tag.pose_t is not None:
                        x = new_tag.pose_t[0][0]
                        z = new_tag.pose_t[2][0]
                        new_angle = math.degrees(math.atan2(x, z))
                        
                        print()
                        print(f"Result:")
                        print(f"  New angle: {new_angle:+.1f}°")
                        print(f"  Improvement: {abs(angle) - abs(new_angle):+.1f}°")
                        print(f"  Centered: {centering.is_centered_angle(new_angle)}")
                        
                        if abs(new_angle) < abs(angle):
                            print()
                            print("SUCCESS: Better centered!")
                        else:
                            print()
                            print("Hmm: Angle got worse (may need tuning)")
                    else:
                        new_offset = new_tag.center[0] - 320
                        print()
                        print(f"Result:")
                        print(f"  New offset: {new_offset:+.0f}px")
                        print(f"  Improvement: {abs(offset) - abs(new_offset):+.0f}px")
                        print(f"  Centered: {centering.is_centered_pixels(new_tag.center[0])}")
                else:
                    print()
                    print("Tag lost after rotation")
        else:
            print("Already perfectly centered!")
        
        break
    
    time.sleep(0.1)
else:
    print("No tags found")

camera.release()
print()
print("="*70)
print("Test complete")
print()
print("The centering skill uses:")
print("  - Proportional speed (larger offset = faster rotation)")
print("  - Pose angle when available (most accurate)")
print("  - Pixel offset as fallback")
print("  - Friction-aware minimum speed")
print()
print("This should work better than fixed-speed rotation!")
