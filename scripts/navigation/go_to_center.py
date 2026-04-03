#!/usr/bin/env python3
"""
Go To Center - Navigate to field center

Uses sonar to measure distance from walls and positions robot
roughly in the center of the 6x6 ft field (center = 3ft = 91cm from each wall).
"""

import time
from lib.board import get_board as BoardController
from lib.sonar import Sonar

print("="*70)
print("GO TO CENTER")
print("="*70)
print()
print("Field: 6ft x 6ft (182cm x 182cm)")
print("Center zone: ~2.5ft (76cm) from each wall")
print("Robot body: ~10 inches (25cm) long")
print("Tolerance: +-30cm (acceptable range: 46-106cm)")
print()

# Config
TARGET_DISTANCE = 76  # cm (2.5 feet, adjusted for robot size)
TOLERANCE = 30        # cm (acceptable range)
MIN_DIST = TARGET_DISTANCE - TOLERANCE  # 46cm
MAX_DIST = TARGET_DISTANCE + TOLERANCE  # 106cm

MOVE_SPEED = 28
ROTATION_SPEED = 25

# Initialize
board = BoardController()
sonar = Sonar()
time.sleep(0.5)

def stop():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def forward(duration):
    """Drive forward for duration seconds"""
    board.set_motor_duty([(1, MOVE_SPEED), (2, MOVE_SPEED), 
                          (3, MOVE_SPEED), (4, MOVE_SPEED)])
    time.sleep(duration)
    stop()

def backward(duration):
    """Drive backward for duration seconds"""
    board.set_motor_duty([(1, -MOVE_SPEED), (2, -MOVE_SPEED), 
                          (3, -MOVE_SPEED), (4, -MOVE_SPEED)])
    time.sleep(duration)
    stop()

def rotate_90():
    """Rotate roughly 90 degrees clockwise"""
    board.set_motor_duty([(1, ROTATION_SPEED), (2, -ROTATION_SPEED),
                          (3, ROTATION_SPEED), (4, -ROTATION_SPEED)])
    time.sleep(1.3)  # ~90 degrees at speed 25
    stop()
    time.sleep(0.5)

def measure_distance():
    """Get sonar distance with multiple samples"""
    readings = []
    for i in range(5):
        dist = sonar.get_distance()
        if dist and dist > 0:
            readings.append(dist)
        time.sleep(0.1)
    
    if readings:
        return sum(readings) / len(readings)
    return None

def adjust_to_center():
    """Adjust position to be at target distance from wall"""
    dist = measure_distance()
    
    if not dist:
        print("  No sonar reading")
        return False
    
    print(f"  Current: {dist:.0f}cm", end="")
    
    if dist < MIN_DIST:
        # Too close, back up
        cm_needed = TARGET_DISTANCE - dist
        duration = cm_needed / 30  # ~30cm/sec at speed 28
        print(f" -> Too close, backing up {cm_needed:.0f}cm")
        backward(duration)
        time.sleep(0.5)
        
        # Verify
        new_dist = measure_distance()
        if new_dist:
            print(f"  After: {new_dist:.0f}cm")
        return True
        
    elif dist > MAX_DIST:
        # Too far, move forward
        cm_needed = dist - TARGET_DISTANCE
        duration = cm_needed / 30
        print(f" -> Too far, moving forward {cm_needed:.0f}cm")
        forward(duration)
        time.sleep(0.5)
        
        # Verify
        new_dist = measure_distance()
        if new_dist:
            print(f"  After: {new_dist:.0f}cm")
        return True
        
    else:
        # Good!
        print(f" -> OK (within +-{TOLERANCE}cm)")
        return True

try:
    print("Starting centering sequence...")
    print("Will check 4 walls (North, East, South, West)")
    print()
    
    walls = ['North', 'East', 'South', 'West']
    
    for i, wall in enumerate(walls):
        print(f"{i+1}. {wall} Wall:")
        
        success = adjust_to_center()
        
        if not success:
            print(f"  Failed to measure {wall} wall")
        
        # Rotate to next wall (except after last one)
        if i < 3:
            print(f"  Rotating to {walls[i+1]} wall...")
            rotate_90()
            time.sleep(0.5)
        
        print()
    
    # Final position check
    print("="*70)
    print("FINAL POSITION CHECK")
    print("="*70)
    print()
    
    # Measure all 4 walls
    print("Measuring all 4 walls...")
    distances = []
    
    for i, wall in enumerate(walls):
        dist = measure_distance()
        if dist:
            distances.append(dist)
            status = "OK" if MIN_DIST <= dist <= MAX_DIST else "OFF"
            print(f"  {wall}: {dist:.0f}cm [{status}]")
        else:
            print(f"  {wall}: No reading")
        
        if i < 3:
            rotate_90()
            time.sleep(0.3)
    
    print()
    
    if distances:
        avg_dist = sum(distances) / len(distances)
        variance = max(distances) - min(distances)
        
        print(f"Average distance: {avg_dist:.0f}cm (target: {TARGET_DISTANCE}cm)")
        print(f"Variance: {variance:.0f}cm (difference between min/max)")
        print()
        
        if MIN_DIST <= avg_dist <= MAX_DIST and variance < 60:
            print("SUCCESS: Roughly centered in field!")
        elif MIN_DIST <= avg_dist <= MAX_DIST:
            print("PARTIAL: Centered distance, but variance high")
        else:
            print("INCOMPLETE: Still off-center, may need iteration")
    else:
        print("Could not measure field position")
    
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
    print("="*70)
