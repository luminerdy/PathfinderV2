#!/usr/bin/env python3
"""
Test individual motors
Tests each wheel motor one at a time to verify connections
"""

from lib.board_protocol import BoardController
import time

print("=" * 60)
print("PATHFINDER MOTOR TEST")
print("=" * 60)
print("\nThis will test each motor individually")
print("Verify each wheel spins in the correct direction\n")

board = BoardController()
time.sleep(0.5)

motors = [
    (1, "Front Left"),
    (2, "Front Right"),
    (3, "Rear Left"),
    (4, "Rear Right")
]

print("Starting motor tests...\n")

for motor_id, name in motors:
    print(f"Testing Motor {motor_id} ({name})...")
    print(f"  Running forward for 2 seconds...")
    
    # Run motor forward
    board.set_motor_duty([(motor_id, 40)])
    time.sleep(2)
    
    # Stop motor
    board.set_motor_duty([(motor_id, 0)])
    print(f"  Stopped")
    
    time.sleep(1)

print("\n" + "=" * 60)
print("MOTOR TEST COMPLETE")
print("=" * 60)
print("\nVerify:")
print("  - All motors ran")
print("  - Each wheel spun forward")
print("  - No unusual noise or binding")
print("")
