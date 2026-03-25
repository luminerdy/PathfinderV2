#!/usr/bin/env python3
"""
Exploring AprilTag Pose Estimation

I want to understand what data I'm getting from AprilTags beyond pixel area.
Let me see what pose information is available and what it means.
"""

import cv2
import time
import math
from pupil_apriltags import Detector
import numpy as np

print("="*70)
print("APRILTAG POSE EXPLORATION")
print("="*70)
print()
print("I'm going to look at tags and see what data I can extract...")
print()

# Camera parameters (need these for pose estimation)
# These are estimates - might need calibration later
CAMERA_PARAMS = {
    'fx': 500,  # Focal length x (pixels)
    'fy': 500,  # Focal length y (pixels)
    'cx': 320,  # Principal point x (image center)
    'cy': 240,  # Principal point y (image center)
}

# Tag size in meters (10 inches = 0.254 meters)
TAG_SIZE = 0.254

# Initialize
camera = cv2.VideoCapture(0)
time.sleep(1)

# Create detector WITH pose estimation enabled
detector = Detector(
    families='tag36h11',
    nthreads=1,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25,
    debug=0
)

print("Camera ready. Looking for tags...")
print("-" * 70)
print()

try:
    scan_count = 0
    found_tags = {}
    
    while scan_count < 100:  # Scan for ~5 seconds
        ret, frame = camera.read()
        if not ret:
            continue
        
        scan_count += 1
        
        # Detect tags
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect WITH pose estimation
        tags = detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=[
                CAMERA_PARAMS['fx'],
                CAMERA_PARAMS['fy'],
                CAMERA_PARAMS['cx'],
                CAMERA_PARAMS['cy']
            ],
            tag_size=TAG_SIZE
        )
        
        for tag in tags:
            tag_id = tag.tag_id
            
            # Basic info I already use
            corners = tag.corners
            center = tag.center
            width = max(corners[:, 0]) - min(corners[:, 0])
            height = max(corners[:, 1]) - min(corners[:, 1])
            area = width * height
            
            # NEW: Pose estimation data
            pose = tag.pose_t  # Translation vector
            rotation = tag.pose_R  # Rotation matrix
            
            if pose is not None and tag_id not in found_tags:
                # Extract position
                x = pose[0][0]  # Left/right from tag
                y = pose[1][0]  # Up/down from tag
                z = pose[2][0]  # Distance forward from tag
                
                # Calculate distance
                distance = math.sqrt(x**2 + y**2 + z**2)
                
                # Calculate angle (yaw) - how far off-center am I?
                angle_rad = math.atan2(x, z)
                angle_deg = math.degrees(angle_rad)
                
                print(f"TAG {tag_id} DETECTED:")
                print(f"  Basic Info:")
                print(f"    Center: ({center[0]:.0f}, {center[1]:.0f}) pixels")
                print(f"    Size: {width:.0f}x{height:.0f} pixels")
                print(f"    Area: {area:.0f} pixels²")
                print()
                print(f"  Pose Estimation:")
                print(f"    Position: x={x:.3f}m, y={y:.3f}m, z={z:.3f}m")
                print(f"    Distance: {distance:.3f} meters ({distance*100:.1f} cm)")
                print(f"    Angle: {angle_deg:.1f}° (+ = I'm right of tag, - = left)")
                print(f"    Height offset: {y:.3f}m ({y*100:.1f} cm)")
                print()
                
                # Store for later
                found_tags[tag_id] = {
                    'distance': distance,
                    'angle': angle_deg,
                    'x': x,
                    'y': y,
                    'z': z,
                    'area': area
                }
                
                print("-" * 70)
                print()
        
        time.sleep(0.05)
    
    camera.release()
    
    print()
    print("="*70)
    print("SUMMARY OF WHAT I LEARNED:")
    print("="*70)
    print()
    
    if found_tags:
        print(f"I detected {len(found_tags)} unique tag(s):")
        print()
        
        for tag_id, data in sorted(found_tags.items()):
            print(f"Tag {tag_id}:")
            print(f"  Distance: {data['distance']:.2f}m ({data['distance']*100:.0f}cm)")
            print(f"  Angle: {data['angle']:+.1f}°")
            print(f"  Pixel area: {data['area']:.0f} px²")
            print(f"  Position: ({data['x']:.2f}, {data['y']:.2f}, {data['z']:.2f})m")
            print()
        
        print("What this means:")
        print("  - I can know my EXACT distance (not just pixel area!)")
        print("  - I can know my angle relative to the tag")
        print("  - I can approach at specific distances/angles")
        print("  - I can 'park' precisely in front of tags")
        print()
        print("This is MUCH more precise than my current 'pixel area' approach!")
        
    else:
        print("No tags detected. I need to be positioned where I can see them.")
    
    print()
    print("="*70)

except KeyboardInterrupt:
    print("\n\nStopped exploration.")
    camera.release()

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    camera.release()

finally:
    camera.release()
