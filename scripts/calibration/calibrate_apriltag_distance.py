#!/usr/bin/env python3
"""
AprilTag Distance Calibration
Uses sonar to measure actual distance and correlate with tag pixel size
"""

import cv2
import time
import json
from lib.board import get_board as BoardController
from pupil_apriltags import Detector
from hardware.sonar import Sonar

print("=" * 60)
print("APRILTAG DISTANCE CALIBRATION")
print("=" * 60)
print("\nThis script will:")
print("  1. Detect AprilTag in camera view")
print("  2. Measure actual distance with sonar")
print("  3. Measure tag size in pixels")
print("  4. Build calibration table")
print("\nPosition robot facing AprilTag on wall")
print("We'll measure at different distances\n")

# Initialize hardware
board = BoardController()
time.sleep(0.5)

camera = cv2.VideoCapture(0)
time.sleep(1)

sonar = Sonar()
detector = Detector(families="tag16h5")

# Position camera
print("Positioning camera forward...")
for servo_id, pulse in [(1, 2500), (6, 1500), (5, 700), (4, 2450), (3, 590)]:
    board.set_servo_position(500, [(servo_id, pulse)])
    time.sleep(0.3)
print("  [OK] Camera positioned\n")

def stop_motors():
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def drive_backward(duration):
    """Back up"""
    board.set_motor_duty([(1, -30), (2, -30), (3, -30), (4, -30)])
    time.sleep(duration)
    stop_motors()

def drive_forward(duration):
    """Move forward"""
    board.set_motor_duty([(1, 30), (2, 30), (3, 30), (4, 30)])
    time.sleep(duration)
    stop_motors()

def measure_tag_and_distance():
    """
    Measure tag pixel size and sonar distance
    
    Returns:
        (tag_id, pixel_area, distance_cm, tag_corners) or None
    """
    # Capture frame
    ret, frame = camera.read()
    if not ret:
        return None
    
    # Detect tag
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)
    
    if not tags:
        return None
    
    tag = tags[0]
    
    # Calculate tag pixel area
    corners = tag.corners
    width_px = max(corners[:, 0]) - min(corners[:, 0])
    height_px = max(corners[:, 1]) - min(corners[:, 1])
    area_px = width_px * height_px
    
    # Measure sonar distance
    distance_cm = sonar.get_distance()
    
    if distance_cm is None or distance_cm < 5 or distance_cm > 400:
        return None
    
    return (tag.tag_id, area_px, distance_cm, corners)

# Calibration data
calibration_data = []

print("=" * 60)
print("CALIBRATION SEQUENCE")
print("=" * 60)

# Start close, back up incrementally
print("\nStarting calibration...")
print("Robot should be close to tag (20-30 cm)")
print("Starting in 3 seconds...\n")

time.sleep(3)

num_measurements = 10
backup_increment = 1.0  # seconds

for measurement in range(num_measurements):
    print(f"\n[Measurement {measurement + 1}/{num_measurements}]")
    
    # Wait for robot to settle
    time.sleep(0.5)
    
    # Take multiple readings for accuracy
    readings = []
    for reading in range(3):
        result = measure_tag_and_distance()
        if result:
            readings.append(result)
        time.sleep(0.1)
    
    if not readings:
        print("  [X] No tag detected or sonar failed")
        continue
    
    # Average the readings
    tag_id = readings[0][0]
    avg_area = sum(r[1] for r in readings) / len(readings)
    avg_distance = sum(r[2] for r in readings) / len(readings)
    
    print(f"  Tag ID: {tag_id}")
    print(f"  Pixel area: {avg_area:.0f} px²")
    print(f"  Sonar distance: {avg_distance:.1f} cm")
    
    # Calculate tag width in pixels (approximate)
    corners = readings[0][3]
    width_px = max(corners[:, 0]) - min(corners[:, 0])
    print(f"  Tag width: {width_px:.0f} px")
    
    # Store data
    calibration_data.append({
        'measurement': measurement + 1,
        'tag_id': int(tag_id),
        'pixel_area': float(avg_area),
        'pixel_width': float(width_px),
        'distance_cm': float(avg_distance),
        'distance_mm': float(avg_distance * 10)
    })
    
    # Back up for next measurement (if not last)
    if measurement < num_measurements - 1:
        print(f"  Backing up {backup_increment}s...")
        drive_backward(backup_increment)

# Save calibration data
print("\n" + "=" * 60)
print("CALIBRATION COMPLETE")
print("=" * 60)

if calibration_data:
    # Save to JSON
    filename = f'apriltag_distance_calibration_{int(time.time())}.json'
    with open(filename, 'w') as f:
        json.dump(calibration_data, f, indent=2)
    
    print(f"\nSaved {len(calibration_data)} measurements to: {filename}")
    
    # Print summary table
    print("\n" + "=" * 60)
    print("CALIBRATION TABLE")
    print("=" * 60)
    print(f"{'Distance (cm)':<15} {'Pixel Area':<15} {'Pixel Width':<15}")
    print("-" * 45)
    
    for entry in sorted(calibration_data, key=lambda x: x['distance_cm']):
        print(f"{entry['distance_cm']:<15.1f} {entry['pixel_area']:<15.0f} {entry['pixel_width']:<15.0f}")
    
    # Calculate relationship
    print("\n" + "=" * 60)
    print("DISTANCE ESTIMATION FORMULA")
    print("=" * 60)
    
    # Simple inverse relationship: area = k / distance²
    # Or: distance = sqrt(k / area)
    
    if len(calibration_data) >= 3:
        # Calculate average k value
        k_values = [d['pixel_area'] * (d['distance_cm'] ** 2) for d in calibration_data]
        k_avg = sum(k_values) / len(k_values)
        
        print(f"\nEstimated relationship:")
        print(f"  distance_cm = sqrt({k_avg:.0f} / pixel_area)")
        print(f"\nOr:")
        print(f"  pixel_area = {k_avg:.0f} / (distance_cm²)")
        
        # Test the formula
        print("\nFormula accuracy test:")
        print(f"{'Actual (cm)':<15} {'Estimated (cm)':<15} {'Error (%)':<15}")
        print("-" * 45)
        
        for entry in calibration_data:
            estimated = (k_avg / entry['pixel_area']) ** 0.5
            error = abs(estimated - entry['distance_cm']) / entry['distance_cm'] * 100
            print(f"{entry['distance_cm']:<15.1f} {estimated:<15.1f} {error:<15.1f}")
        
        # Save formula constants
        formula_file = 'apriltag_distance_formula.json'
        with open(formula_file, 'w') as f:
            json.dump({
                'k_constant': float(k_avg),
                'formula': 'distance_cm = sqrt(k_constant / pixel_area)',
                'tag_family': 'tag16h5',
                'tag_size_inches': 6,
                'calibration_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'num_measurements': len(calibration_data)
            }, f, indent=2)
        
        print(f"\nFormula saved to: {formula_file}")
    
    print("\n" + "=" * 60)
    print("Use this data for approach control!")
    print("Example:")
    print("  if pixel_area > 40000:")
    print("      # Too close! (~20-30cm)")
    print("  elif pixel_area > 20000:")
    print("      # Good distance (~40-50cm)")
    print("  else:")
    print("      # Too far, drive forward")
    print("=" * 60)
else:
    print("\nNo measurements collected!")

stop_motors()
camera.release()
