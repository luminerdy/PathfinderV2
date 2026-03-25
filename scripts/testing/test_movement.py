#!/usr/bin/env python3
"""
Simple movement test - no camera or sonar needed
"""

from pathfinder import Pathfinder
import time

print("Initializing robot...")
robot = Pathfinder()
robot.initialize(enable_camera=False, enable_sonar=False, enable_monitoring=False)

print("\n[OK] Robot ready!")
print("\nTesting basic movements...")
print("(Watch the robot!)\n")

try:
    # Test 1: Forward
    print("1. Moving FORWARD (2 seconds)...")
    robot.chassis.set_velocity(30, 0, 0)  # Forward at speed 30
    time.sleep(2)
    robot.chassis.stop()
    time.sleep(1)
    
    # Test 2: Backward
    print("2. Moving BACKWARD (2 seconds)...")
    robot.chassis.set_velocity(30, 180, 0)  # Backward
    time.sleep(2)
    robot.chassis.stop()
    time.sleep(1)
    
    # Test 3: Strafe Right
    print("3. STRAFE RIGHT (2 seconds)...")
    robot.chassis.set_velocity(30, 90, 0)  # Right
    time.sleep(2)
    robot.chassis.stop()
    time.sleep(1)
    
    # Test 4: Strafe Left
    print("4. STRAFE LEFT (2 seconds)...")
    robot.chassis.set_velocity(30, 270, 0)  # Left
    time.sleep(2)
    robot.chassis.stop()
    time.sleep(1)
    
    # Test 5: Rotate
    print("5. ROTATE (2 seconds)...")
    robot.chassis.set_velocity(0, 0, 0.3)  # Rotate
    time.sleep(2)
    robot.chassis.stop()
    
    print("\n[OK] Movement test complete!")
    
except KeyboardInterrupt:
    print("\n\nTest interrupted")
    robot.chassis.stop()

finally:
    robot.shutdown()
    print("Done")
