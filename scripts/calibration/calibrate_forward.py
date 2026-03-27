#!/usr/bin/env python3
"""
Forward Movement Calibration

Uses AprilTags to measure actual distance traveled.
Tests various motor powers and durations to build calibration table.

METHOD:
1. Measure distance to tag (pose estimation)
2. Drive forward at specified power/duration
3. Measure new distance to tag
4. Calculate actual distance traveled
5. Build power → cm/sec calibration table
"""

import cv2
import time
import math
from pupil_apriltags import Detector
from lib.board import get_board as BoardController

print("="*70)
print("FORWARD MOVEMENT CALIBRATION")
print("="*70)
print()

# Config
CAMERA_PARAMS = [500, 500, 320, 240]
TAG_SIZE = 0.254

# Test configurations: (power, duration)
TESTS = [
    (28, 0.5),   # Baseline power, short
    (28, 1.0),   # Baseline power, medium
    (28, 2.0),   # Baseline power, long
    (30, 0.5),   # Higher power
    (30, 1.0),   # Higher power
    (35, 0.5),   # Even higher
]

# Initialize
board = BoardController()
camera = cv2.VideoCapture(0)
time.sleep(1.5)
detector = Detector(families='tag36h11')

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def get_distance_to_tag():
    """
    Get distance to nearest tag using pose estimation
    Returns (tag_id, distance_meters, angle_degrees)
    """
    ret, frame = camera.read()
    if not ret:
        return None, None, None
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True,
                          camera_params=CAMERA_PARAMS,
                          tag_size=TAG_SIZE)
    
    if not tags:
        return None, None, None
    
    # Use closest tag
    best_tag = None
    best_dist = float('inf')
    
    for tag in tags:
        if tag.pose_t is not None:
            x = tag.pose_t[0][0]
            z = tag.pose_t[2][0]
            dist = math.sqrt(x**2 + z**2)
            if dist < best_dist:
                best_dist = dist
                best_tag = tag
    
    if best_tag and best_tag.pose_t is not None:
        x = best_tag.pose_t[0][0]
        z = best_tag.pose_t[2][0]
        angle = math.degrees(math.atan2(x, z))
        dist = math.sqrt(x**2 + z**2)
        return best_tag.tag_id, dist, angle
    
    return None, None, None

def forward(power, duration):
    """Drive forward at given power for duration"""
    board.set_motor_duty([(1, power), (2, power), 
                          (3, power), (4, power)])
    time.sleep(duration)
    stop()

try:
    print("SETUP CHECK")
    print("-" * 70)
    print()
    
    # Initial check
    tag_id, dist, angle = get_distance_to_tag()
    
    if tag_id is None:
        print("ERROR: No AprilTags visible!")
        print("Position robot facing a tag with clear path.")
        camera.release()
        exit(1)
    
    print(f"Initial position:")
    print(f"  Tag {tag_id} at {dist:.2f}m ({dist*100:.0f}cm), angle {angle:+.1f}°")
    print()
    
    # Battery check
    mv = board.get_battery()
    if mv:
        v = mv / 1000.0
        print(f"  Battery: {v:.2f}V")
        if v < 8.0:
            print("  WARNING: Battery low, results may vary")
    print()
    
    print("Ready to calibrate!")
    print()
    input("Press ENTER to start calibration tests...")
    print()
    
    # Run calibration tests
    results = []
    
    for i, (power, duration) in enumerate(TESTS):
        print("="*70)
        print(f"TEST {i+1}/{len(TESTS)}: Power={power}, Duration={duration}s")
        print("="*70)
        print()
        
        # Get starting distance
        start_tag, start_dist, start_angle = get_distance_to_tag()
        
        if start_tag is None:
            print("  ERROR: Lost visual tracking")
            print("  Skipping this test")
            print()
            continue
        
        print(f"  Before: Tag {start_tag} at {start_dist:.2f}m ({start_dist*100:.0f}cm)")
        
        if abs(start_angle) > 10:
            print(f"  WARNING: Off-center by {start_angle:+.1f}° (may affect accuracy)")
        
        # Drive forward
        print(f"  Driving at power {power} for {duration}s...")
        forward(power, duration)
        
        time.sleep(0.5)  # Settle
        
        # Get ending distance
        end_tag, end_dist, end_angle = get_distance_to_tag()
        
        if end_tag is None:
            print("  ERROR: Lost visual tracking after movement")
            print("  Skipping this test")
            print()
            continue
        
        print(f"  After:  Tag {end_tag} at {end_dist:.2f}m ({end_dist*100:.0f}cm)")
        print()
        
        # Calculate actual movement
        if start_tag == end_tag:
            # Same tag - simple distance difference
            movement_m = start_dist - end_dist  # Positive = moved toward tag
            movement_cm = movement_m * 100
            
            print(f"  RESULT: Moved {movement_cm:+.1f} cm")
            
            # Calculate speed
            speed_cm_per_sec = abs(movement_cm) / duration
            print(f"  Speed: {speed_cm_per_sec:.1f} cm/sec at power {power}")
            
            results.append({
                'power': power,
                'duration': duration,
                'movement_cm': movement_cm,
                'speed_cm_per_sec': speed_cm_per_sec,
            })
        else:
            print(f"  ERROR: Different tags (was {start_tag}, now {end_tag})")
            print(f"  Cannot calculate distance accurately")
        
        print()
        time.sleep(1)  # Pause between tests
    
    # Print summary
    print()
    print("="*70)
    print("CALIBRATION SUMMARY")
    print("="*70)
    print()
    
    if not results:
        print("No successful calibrations!")
    else:
        print(f"Successfully calibrated {len(results)}/{len(TESTS)} tests")
        print()
        print("CALIBRATION TABLE:")
        print("-" * 70)
        print(f"{'Power':<8} {'Duration':<10} {'Movement':<12} {'Speed (cm/s)':<12}")
        print("-" * 70)
        
        for r in results:
            print(f"{r['power']:<8} {r['duration']:<10.1f} "
                  f"{r['movement_cm']:+<12.1f} {r['speed_cm_per_sec']:<12.1f}")
        
        print()
        
        # Calculate average speeds by power
        print("AVERAGE SPEEDS BY POWER:")
        print("-" * 70)
        
        by_power = {}
        for r in results:
            p = r['power']
            if p not in by_power:
                by_power[p] = []
            by_power[p].append(r['speed_cm_per_sec'])
        
        for power in sorted(by_power.keys()):
            speeds = by_power[power]
            avg_speed = sum(speeds) / len(speeds)
            print(f"  Power {power}: {avg_speed:.1f} cm/sec "
                  f"(from {len(speeds)} test(s))")
        
        print()
        
        # Save to file
        with open('/home/robot/code/pathfinder/forward_calibration.txt', 'w') as f:
            f.write("FORWARD MOVEMENT CALIBRATION RESULTS\n")
            f.write("="*70 + "\n\n")
            
            f.write("Power | Duration | Movement(cm) | Speed(cm/s)\n")
            f.write("-" * 70 + "\n")
            
            for r in results:
                f.write(f"{r['power']:>5} | {r['duration']:>8.1f} | "
                       f"{r['movement_cm']:>+11.1f} | {r['speed_cm_per_sec']:>10.1f}\n")
            
            f.write("\n")
            f.write("Average speeds by power:\n")
            for power in sorted(by_power.keys()):
                speeds = by_power[power]
                avg_speed = sum(speeds) / len(speeds)
                f.write(f"  Power {power}: {avg_speed:.1f} cm/sec\n")
        
        print("Results saved to: forward_calibration.txt")

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
