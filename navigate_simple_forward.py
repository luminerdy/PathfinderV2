#!/usr/bin/env python3
"""
Simple Forward Navigation
If tag visible -> drive forward
Don't worry about perfect centering
"""

import cv2
import time
from lib.board_protocol import BoardController
from pupil_apriltags import Detector

print("="*60)
print("SIMPLE FORWARD NAVIGATION")
print("="*60)
print("Rule: See tag? Drive toward it.")
print("="*60)

TARGET_AREA = 25000
SPEED_FORWARD = 30
SPEED_SEARCH = 20

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

def forward(speed=SPEED_FORWARD):
    board.set_motor_duty([(1,speed), (2,speed), (3,speed), (4,speed)])

def search_rotate():
    board.set_motor_duty([(1,SPEED_SEARCH), (2,-SPEED_SEARCH), 
                          (3,SPEED_SEARCH), (4,-SPEED_SEARCH)])

print("Searching for tag...")
tag_found = False
search_count = 0

while search_count < 50:
    search_count += 1
    
    # Capture
    ret, frame = camera.read()
    if not ret:
        continue
    
    # Detect
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)
    
    if tags:
        # TAG FOUND - LOCK ON!
        tag = tags[0]
        corners = tag.corners  
        area = (max(corners[:,0])-min(corners[:,0])) * (max(corners[:,1])-min(corners[:,1]))
        
        print(f"\nTag {tag.tag_id} detected! Area={area:.0f}")
        print("Starting approach...\n")
        
        approach_count = 0
        lost_count = 0
        
        while approach_count < 80:
            approach_count += 1
            
            # Check tag
            ret, frame = camera.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                tags = detector.detect(gray)
                
                if tags:
                    # Tag visible!
                    lost_count = 0
                    tag = tags[0]
                    corners = tag.corners
                    area = (max(corners[:,0])-min(corners[:,0])) * (max(corners[:,1])-min(corners[:,1]))
                    
                    # Check if reached
                    if area > TARGET_AREA:
                        stop()
                        print(f"\n[{approach_count}] TARGET REACHED! Area={area:.0f}")
                        cv2.imwrite(f"success_{int(time.time())}.jpg", frame)
                        print("\n" + "="*60)
                        print("SUCCESS!")
                        print("="*60)
                        camera.release()
                        exit()
                    
                    # Still approaching - drive forward
                    forward(SPEED_FORWARD)
                    
                    if approach_count % 10 == 0:
                        print(f"[{approach_count}] Area={area:.0f}, driving forward")
                    
                    time.sleep(0.15)  # Short loop delay
                    
                else:
                    # Tag not visible
                    lost_count += 1
                    
                    if lost_count > 5:
                        # Lost for too long
                        stop()
                        print(f"\n[{approach_count}] Lost tag, re-searching")
                        time.sleep(0.3)
                        break
                    else:
                        # Keep driving briefly
                        forward(SPEED_FORWARD)
                        time.sleep(0.1)
        
        # After approach loop, search again
        print("\nSearching again...")
    
    else:
        # No tag - keep searching
        search_rotate()
        
        if search_count % 10 == 0:
            print(f"  Searching... {search_count}/50")
        
        time.sleep(0.15)

stop()
camera.release()
print("\nNo tag found or reached")
