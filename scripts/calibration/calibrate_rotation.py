#!/usr/bin/env python3
"""
Rotation Calibration

Uses AprilTags as visual ground truth to measure actual rotation.
Tests various motor powers and durations to build calibration table.

SETUP:
- Position robot in center of field
- Ensure at least 2 AprilTags are visible
- Run script

OUTPUT:
- Power + Duration → Actual Degrees
- Sonar distance pattern during rotation
- Calibration table for accurate rotation
"""

import cv2
import time
import math
from pupil_apriltags import Detector
from lib.board import get_board as BoardController
from lib.sonar import Sonar

print("="*70)
print("ROTATION CALIBRATION")
print("="*70)
print()

# Config
CAMERA_PARAMS = [500, 500, 320, 240]
TAG_SIZE = 0.254

# Test configurations: (power, duration)
# Focus on threshold range (24-30) with multiple durations
TESTS = [
    (24, 1.0),   # Below threshold?
    (24, 2.0),   # Longer duration
    (25, 1.0),   # At threshold?
    (25, 2.0),   # Verify consistency
    (26, 1.0),   # Above threshold?
    (27, 1.0),   # Higher
    (28, 1.0),   # Known to work
    (28, 2.0),   # 360° attempt (2x 105°/s = 210°)
    (28, 3.4),   # Should be ~360°
    (30, 1.0),   # Max speed
]

# Initialize
board = BoardController()
sonar = Sonar()
camera = cv2.VideoCapture(0)
time.sleep(1.5)
detector = Detector(families='tag36h11')

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def get_tag_angle():
    """
    Get current angle to nearest tag using pose estimation
    Returns (tag_id, angle_degrees, distance_meters)
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
        return best_tag.tag_id, angle, dist
    
    return None, None, None

def rotate_with_logging(power, duration):
    """
    Rotate at given power for duration, logging sonar
    Returns list of (time, sonar_distance) tuples
    """
    sonar_log = []
    
    # Start rotation
    board.set_motor_duty([(1, power), (2, -power),
                          (3, power), (4, -power)])
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        dist = sonar.get_distance()
        if dist and dist > 0:
            sonar_log.append((elapsed, dist))
        time.sleep(0.05)  # 20 samples/sec
    
    stop()
    
    return sonar_log

def calculate_rotation(start_tag, start_angle, end_tag, end_angle):
    """
    Calculate actual rotation from start/end measurements
    
    Handles:
    - Same tag seen before/after
    - Different tags seen (crossed field)
    - Multiple rotations
    """
    if start_tag == end_tag:
        # Same tag - simple angle difference
        rotation = end_angle - start_angle
        
        # Normalize to -180 to +180
        while rotation > 180:
            rotation -= 360
        while rotation < -180:
            rotation += 360
        
        return rotation
    else:
        # Different tags - need to account for tag positions
        # Tags are arranged: 578-585 clockwise
        # North: 578(L), 579(R)
        # East: 580(L), 581(R)
        # South: 582(L), 583(R)
        # West: 584(L), 585(R)
        
        tag_angles = {
            578: 0,    # North left
            579: 0,    # North right
            580: 90,   # East left
            581: 90,   # East right
            582: 180,  # South left
            583: 180,  # South right
            584: 270,  # West left
            585: 270,  # West right
        }
        
        if start_tag in tag_angles and end_tag in tag_angles:
            # Calculate rotation based on tag wall positions
            wall_rotation = tag_angles[end_tag] - tag_angles[start_tag]
            
            # Normalize
            while wall_rotation > 180:
                wall_rotation -= 360
            while wall_rotation < -180:
                wall_rotation += 360
            
            # Add the angle differences within each tag
            total_rotation = wall_rotation + (end_angle - start_angle)
            
            return total_rotation
        else:
            # Unknown tags, can't calculate
            return None

try:
    print("SETUP CHECK")
    print("-" * 70)
    print()
    
    # Initial tag detection
    tag_id, angle, dist = get_tag_angle()
    
    if tag_id is None:
        print("ERROR: No AprilTags visible!")
        print("Position robot so at least 2 tags are in view.")
        camera.release()
        exit(1)
    
    print(f"Initial position:")
    print(f"  Tag {tag_id} at {angle:+.1f}°, {dist:.2f}m")
    print()
    
    initial_sonar = sonar.get_distance()
    if initial_sonar:
        print(f"  Sonar: {initial_sonar:.0f}cm")
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
        
        # Get starting position
        start_tag, start_angle, start_dist = get_tag_angle()
        
        if start_tag is None:
            print("  ERROR: Lost visual tracking")
            print("  Skipping this test")
            print()
            continue
        
        print(f"  Before: Tag {start_tag} at {start_angle:+.1f}°")
        
        # Rotate with logging
        print(f"  Rotating at power {power} for {duration}s...")
        sonar_log = rotate_with_logging(power, duration)
        
        time.sleep(0.5)  # Settle
        
        # Get ending position
        end_tag, end_angle, end_dist = get_tag_angle()
        
        if end_tag is None:
            print("  ERROR: Lost visual tracking after rotation")
            print("  Skipping this test")
            print()
            continue
        
        print(f"  After:  Tag {end_tag} at {end_angle:+.1f}°")
        print()
        
        # Calculate actual rotation
        actual_rotation = calculate_rotation(start_tag, start_angle,
                                            end_tag, end_angle)
        
        if actual_rotation is not None:
            print(f"  RESULT: {actual_rotation:+.1f}° actual rotation")
            
            # Calculate degrees per second
            deg_per_sec = abs(actual_rotation) / duration
            print(f"  Rate: {deg_per_sec:.1f} deg/sec at power {power}")
            
            # Sonar analysis
            if sonar_log:
                sonar_dists = [s[1] for s in sonar_log]
                min_sonar = min(sonar_dists)
                max_sonar = max(sonar_dists)
                avg_sonar = sum(sonar_dists) / len(sonar_dists)
                
                print(f"  Sonar: {len(sonar_log)} samples, "
                      f"{min_sonar:.0f}-{max_sonar:.0f}cm "
                      f"(avg {avg_sonar:.0f}cm)")
            
            results.append({
                'power': power,
                'duration': duration,
                'actual_deg': actual_rotation,
                'deg_per_sec': deg_per_sec,
                'sonar_log': sonar_log,
            })
        else:
            print(f"  ERROR: Could not calculate rotation")
        
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
        print(f"{'Power':<8} {'Duration':<10} {'Actual°':<12} {'Rate (°/s)':<12}")
        print("-" * 70)
        
        for r in results:
            print(f"{r['power']:<8} {r['duration']:<10.1f} "
                  f"{r['actual_deg']:+<12.1f} {r['deg_per_sec']:<12.1f}")
        
        print()
        
        # Calculate average rates by power
        print("AVERAGE RATES BY POWER:")
        print("-" * 70)
        
        by_power = {}
        for r in results:
            p = r['power']
            if p not in by_power:
                by_power[p] = []
            by_power[p].append(r['deg_per_sec'])
        
        for power in sorted(by_power.keys()):
            rates = by_power[power]
            avg_rate = sum(rates) / len(rates)
            print(f"  Power {power}: {avg_rate:.1f} deg/sec "
                  f"(from {len(rates)} test(s))")
        
        print()
        
        # Save to file
        with open('/home/robot/code/pathfinder/rotation_calibration.txt', 'w') as f:
            f.write("ROTATION CALIBRATION RESULTS\n")
            f.write("="*70 + "\n\n")
            
            f.write("Power | Duration | Actual° | Rate(°/s)\n")
            f.write("-" * 70 + "\n")
            
            for r in results:
                f.write(f"{r['power']:>5} | {r['duration']:>8.1f} | "
                       f"{r['actual_deg']:>+7.1f} | {r['deg_per_sec']:>9.1f}\n")
            
            f.write("\n")
            f.write("Average rates by power:\n")
            for power in sorted(by_power.keys()):
                rates = by_power[power]
                avg_rate = sum(rates) / len(rates)
                f.write(f"  Power {power}: {avg_rate:.1f} deg/sec\n")
        
        print("Results saved to: rotation_calibration.txt")

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
