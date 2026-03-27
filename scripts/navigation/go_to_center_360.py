#!/usr/bin/env python3
"""
Go To Center - 360° Scan Method

Rotates slowly while scanning with sonar to build a distance map
of all walls, then moves toward the most open space (center).
"""

import time
import math
from lib.board import get_board as BoardController
from hardware.sonar import Sonar

print("="*70)
print("GO TO CENTER - 360° Scan Method")
print("="*70)
print()

# Config
ROTATION_SPEED = 28  # Minimum power to overcome friction (calibrated)
MOVE_SPEED = 28
TARGET_CENTER_DIST = 76  # cm (~2.5 ft from walls)
ROTATION_TIME = 3.4  # Time for 360° at ~105 deg/sec

# Initialize
board = BoardController()
sonar = Sonar()
time.sleep(0.5)

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def forward(duration):
    board.set_motor_duty([(1, MOVE_SPEED), (2, MOVE_SPEED), 
                          (3, MOVE_SPEED), (4, MOVE_SPEED)])
    time.sleep(duration)
    stop()

def backward(duration):
    board.set_motor_duty([(1, -MOVE_SPEED), (2, -MOVE_SPEED), 
                          (3, -MOVE_SPEED), (4, -MOVE_SPEED)])
    time.sleep(duration)
    stop()

def rotate_360_scan():
    """
    Rotate 360° slowly while collecting sonar data
    Returns list of (angle, distance) tuples
    """
    print("Performing 360° scan...")
    print("(Rotating slowly, sampling sonar)")
    print()
    
    samples = []
    
    # Start rotation
    board.set_motor_duty([(1, ROTATION_SPEED), (2, -ROTATION_SPEED),
                          (3, ROTATION_SPEED), (4, -ROTATION_SPEED)])
    
    # Collect samples for ~3.4 seconds (360° at ~105 deg/sec)
    # Calibrated: Power 28 rotates ~105 deg/sec
    start_time = time.time()
    sample_interval = 0.1  # 100ms between samples
    
    while time.time() - start_time < ROTATION_TIME:
        elapsed = time.time() - start_time
        angle = (elapsed / ROTATION_TIME) * 360  # Estimate current angle
        
        dist = sonar.get_distance()
        if dist and dist > 0:
            samples.append((angle, dist))
            print(f"  {angle:3.0f}°: {dist:3.0f} cm")
        
        time.sleep(sample_interval)
    
    stop()
    print()
    print(f"Collected {len(samples)} samples")
    print()
    
    return samples

def analyze_scan(samples):
    """
    Analyze 360° scan to find direction to move toward center
    
    Returns (direction_angle, move_distance) where:
      direction_angle: which way to move (0-360°)
      move_distance: how far to move (cm)
    """
    if len(samples) < 10:
        print("Not enough samples to analyze")
        return None, None
    
    # Find min and max distances
    min_dist = min(s[1] for s in samples)
    max_dist = max(s[1] for s in samples)
    avg_dist = sum(s[1] for s in samples) / len(samples)
    
    print("Scan Analysis:")
    print(f"  Min distance: {min_dist:.0f} cm (closest wall)")
    print(f"  Max distance: {max_dist:.0f} cm (farthest wall)")
    print(f"  Average: {avg_dist:.0f} cm")
    print()
    
    # Find the closest wall (where we need to move AWAY from)
    closest_angle = min(samples, key=lambda s: s[1])[0]
    closest_dist = min(samples, key=lambda s: s[1])[1]
    
    # Move in opposite direction (180° away from closest wall)
    move_direction = (closest_angle + 180) % 360
    
    # Calculate how far to move
    # If closest wall is at X cm, and we want to be TARGET cm from all walls,
    # move roughly (TARGET - X) cm away from it
    move_distance = max(0, TARGET_CENTER_DIST - closest_dist)
    
    print(f"Decision:")
    print(f"  Closest wall at {closest_angle:.0f}° ({closest_dist:.0f} cm)")
    print(f"  Move toward {move_direction:.0f}° for ~{move_distance:.0f} cm")
    print()
    
    return move_direction, move_distance

def rotate_to_direction(target_angle):
    """
    Rotate to face a specific direction (0-360°)
    Assumes we ended 360° scan facing same direction we started
    """
    # Normalize angle
    while target_angle >= 360:
        target_angle -= 360
    while target_angle < 0:
        target_angle += 360
    
    print(f"Rotating to face {target_angle:.0f}°...")
    
    # Simple: rotate for calculated time
    # Speed 28 = ~105°/sec (calibrated)
    rotation_time = target_angle / 105
    
    board.set_motor_duty([(1, ROTATION_SPEED), (2, -ROTATION_SPEED),
                          (3, ROTATION_SPEED), (4, -ROTATION_SPEED)])
    time.sleep(rotation_time)
    stop()
    time.sleep(0.5)
    
    print(f"Rotated for {rotation_time:.1f}s")
    print()

try:
    # PHASE 1: 360° Scan
    print("PHASE 1: Scanning environment")
    print("-" * 70)
    print()
    
    samples = rotate_360_scan()
    
    if not samples:
        print("No data collected, aborting")
        stop()
        exit(1)
    
    # PHASE 2: Analyze
    print("PHASE 2: Analyzing scan data")
    print("-" * 70)
    print()
    
    move_direction, move_distance = analyze_scan(samples)
    
    if move_direction is None:
        print("Could not determine direction")
        stop()
        exit(1)
    
    # PHASE 3: Move toward center
    print("PHASE 3: Moving toward center")
    print("-" * 70)
    print()
    
    # Rotate to face the direction
    rotate_to_direction(move_direction)
    
    # Move forward
    if move_distance > 5:  # Only move if significant
        move_time = move_distance / 30  # ~30 cm/sec
        print(f"Moving forward {move_distance:.0f} cm...")
        forward(move_time)
    else:
        print("Already roughly centered, no movement needed")
    
    print()
    print("="*70)
    print("CENTERING COMPLETE")
    print("="*70)
    print()
    print("Robot should now be closer to field center.")
    print("Run again to further refine position if needed.")
    print()

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
