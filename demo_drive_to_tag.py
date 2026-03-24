#!/usr/bin/env python3
"""
Demo: Drive to AprilTag with Improved Centering

Shows navigation using the new proportional centering skill.
Finds a tag (not 581), centers on it, and drives to it.
"""

import cv2
import time
import math
from pupil_apriltags import Detector
from lib.board_protocol import BoardController
from hardware.sonar import Sonar
from skills.centering import CenteringController

print("="*70)
print("DRIVE TO APRILTAG - With Improved Centering")
print("="*70)
print()
print("Starting from Tag 581, finding another tag, and driving to it")
print()

# Config
TARGET_AREA = 25000
DRIVE_SPEED_FAST = 28
DRIVE_SPEED_MEDIUM = 24
DRIVE_SPEED_SLOW = 20
SONAR_STOP = 18

CAMERA_PARAMS = [500, 500, 320, 240]
TAG_SIZE = 0.254

# Initialize
board = BoardController()
sonar = Sonar()
camera = cv2.VideoCapture(0)
time.sleep(1.5)
detector = Detector(families='tag36h11')
centering = CenteringController(board)

# Position camera
print("Positioning camera forward...")
for sid, pos in [(1, 2500), (6, 1500), (5, 700), (4, 2450), (3, 590)]:
    board.set_servo_position(500, [(sid, pos)])
    time.sleep(0.3)
print("Ready!")
print()

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def forward(speed):
    board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])

try:
    # PHASE 1: Find a tag (not 581)
    print("PHASE 1: Searching for tag (excluding 581)...")
    print("-" * 70)
    
    target_tag = None
    for rotation in range(40):
        board.set_motor_duty([(1, 22), (2, -22), (3, 22), (4, -22)])
        time.sleep(0.2)
        stop()
        time.sleep(0.15)
        
        ret, frame = camera.read()
        if not ret:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray, estimate_tag_pose=True,
                               camera_params=CAMERA_PARAMS,
                               tag_size=TAG_SIZE)
        
        # Find any tag except 581
        for tag in tags:
            if tag.tag_id != 581 and tag.pose_t is not None:
                x = tag.pose_t[0][0]
                z = tag.pose_t[2][0]
                dist = math.sqrt(x**2 + z**2)
                angle = math.degrees(math.atan2(x, z))
                
                corners = tag.corners
                width = max(corners[:, 0]) - min(corners[:, 0])
                height = max(corners[:, 1]) - min(corners[:, 1])
                area = width * height
                
                print(f"\nFound Tag {tag.tag_id}!")
                print(f"  Distance: {dist:.2f}m ({dist*100:.0f}cm)")
                print(f"  Angle: {angle:+.1f}°")
                print(f"  Area: {area:.0f} px²")
                print()
                
                target_tag = tag.tag_id
                stop()
                time.sleep(0.5)
                break
        
        if target_tag:
            break
    
    if not target_tag:
        print("No tag found!")
        stop()
        camera.release()
        exit(1)
    
    # PHASE 2: Approach with centering
    print("PHASE 2: Approaching with proportional centering...")
    print("-" * 70)
    print()
    
    approach_count = 0
    
    while approach_count < 150:
        approach_count += 1
        
        # Sonar safety
        sonar_dist = sonar.get_distance()
        if sonar_dist is not None and sonar_dist > 0 and sonar_dist < SONAR_STOP:
            stop()
            print(f"\nSONAR STOP at {sonar_dist:.1f}cm")
            break
        
        # Get frame
        ret, frame = camera.read()
        if not ret:
            continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray, estimate_tag_pose=True,
                               camera_params=CAMERA_PARAMS,
                               tag_size=TAG_SIZE)
        
        # Find our target
        found_target = False
        for tag in tags:
            if tag.tag_id == target_tag:
                found_target = True
                
                # Get metrics
                corners = tag.corners
                width = max(corners[:, 0]) - min(corners[:, 0])
                height = max(corners[:, 1]) - min(corners[:, 1])
                area = width * height
                
                # Check if reached
                if area >= TARGET_AREA:
                    stop()
                    print(f"\nREACHED Tag {target_tag}!")
                    print(f"  Final area: {area:.0f} px²")
                    
                    if tag.pose_t is not None:
                        x = tag.pose_t[0][0]
                        z = tag.pose_t[2][0]
                        dist = math.sqrt(x**2 + z**2)
                        angle = math.degrees(math.atan2(x, z))
                        print(f"  Final distance: {dist:.2f}m ({dist*100:.0f}cm)")
                        print(f"  Final angle: {angle:+.1f}°")
                    
                    break
                
                # Get pose angle for centering
                if tag.pose_t is not None:
                    x = tag.pose_t[0][0]
                    z = tag.pose_t[2][0]
                    angle = math.degrees(math.atan2(x, z))
                    
                    # Decide: center or drive?
                    if not centering.is_centered_angle(angle):
                        # Need to center
                        centering.rotate_to_center(angle_deg=angle)
                        action = f"centering ({angle:+.1f}°)"
                    else:
                        # Centered, drive forward with speed control
                        if area > 15000:
                            speed = DRIVE_SPEED_SLOW
                        elif area > 10000:
                            speed = DRIVE_SPEED_MEDIUM
                        else:
                            speed = DRIVE_SPEED_FAST
                        
                        forward(speed)
                        action = f"driving (speed {speed})"
                    
                    if approach_count % 20 == 0:
                        print(f"[{approach_count}] Area {area:.0f} px², angle {angle:+.1f}° - {action}")
                else:
                    # No pose, use pixel offset
                    offset = tag.center[0] - 320
                    
                    if not centering.is_centered_pixels(tag.center[0]):
                        centering.rotate_to_center(target_x=tag.center[0])
                        action = f"centering (offset {offset:+.0f}px)"
                    else:
                        # Drive
                        if area > 15000:
                            speed = DRIVE_SPEED_SLOW
                        elif area > 10000:
                            speed = DRIVE_SPEED_MEDIUM
                        else:
                            speed = DRIVE_SPEED_FAST
                        
                        forward(speed)
                        action = f"driving (speed {speed})"
                    
                    if approach_count % 20 == 0:
                        print(f"[{approach_count}] Area {area:.0f} px², offset {offset:+.0f}px - {action}")
                
                break
        
        if not found_target:
            stop()
            print(f"\n[{approach_count}] Lost tag, stopping")
            break
        
        if area >= TARGET_AREA:
            break
        
        time.sleep(0.05)
    
    stop()
    print()
    print("="*70)
    print("NAVIGATION COMPLETE")
    print("="*70)
    print()
    print("New centering skill demonstrated:")
    print("  - Proportional speed based on angle")
    print("  - Damping prevents oscillation")
    print("  - Smooth approach with speed control")
    print("  - Much better than fixed-speed rotation!")

except KeyboardInterrupt:
    print("\n\nStopped by user")
    stop()

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    stop()

finally:
    stop()
    camera.release()
    print()
