#!/usr/bin/env python3
"""
Manual pickup of red block
Uses servo control to pick up block seen in camera
"""

import time
from lib.board_protocol import BoardController

def main():
    print("=" * 60)
    print("MANUAL RED BLOCK PICKUP")
    print("=" * 60)
    
    board = BoardController()
    time.sleep(0.5)
    
    # Red block is at (509, 87) - upper right area
    # It's close (7853 pixels²)
    
    print("\n[Step 1] Position arm extended forward and low")
    print("Starting from camera-forward, moving to pickup position...")
    
    # Camera forward base position
    # Servo 6: 1500 (base forward)
    # Servo 5: 700 (shoulder)
    # Servo 4: 2450 (elbow)
    # Servo 3: 590 (wrist)
    
    # For pickup, we need:
    # - Base slightly right (block is at x=509, right of center 320)
    # - Arm extended forward
    # - Lower height
    
    print("  Opening gripper...")
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(1)
    
    print("  Positioning base (slight right turn)...")
    # Block at 509 pixels, center is 320, so 189 pixels right
    # Rough estimate: turn base right
    board.set_servo_position(800, [(6, 1350)])  # Turn right from 1500
    time.sleep(1)
    
    print("  Extending arm forward and down...")
    # Lower shoulder, extend elbow more, angle wrist down
    positions = [
        (5, 1200),  # Shoulder more forward/down
        (4, 2200),  # Elbow extended
        (3, 800),   # Wrist angled down
    ]
    
    for servo_id, pulse in positions:
        board.set_servo_position(800, [(servo_id, pulse)])
        time.sleep(0.5)
    
    time.sleep(1)
    
    print("\n[Step 2] Waiting 2 seconds to settle...")
    time.sleep(2)
    
    print("\n[Step 3] Closing gripper...")
    board.set_servo_position(500, [(1, 1475)])  # Close
    time.sleep(1.5)
    
    print("\n[Step 4] Lifting block...")
    # Raise shoulder
    board.set_servo_position(800, [(5, 700)])
    time.sleep(1)
    
    print("\n" + "=" * 60)
    print("PICKUP ATTEMPT COMPLETE!")
    print("=" * 60)
    print("\nDid it work?")
    print("  - If yes: Block should be held in gripper")
    print("  - If no: Adjust positions and try again")
    
    print("\nWaiting 3 seconds, then returning to camera position...")
    time.sleep(3)
    
    # Return to camera forward
    print("\nReturning to camera-forward position...")
    board.set_servo_position(500, [(1, 2500)])  # Open gripper
    time.sleep(1)
    
    camera_forward = [
        (6, 1500),  # Base center
        (5, 700),   # Shoulder
        (4, 2450),  # Elbow
        (3, 590),   # Wrist
    ]
    
    for servo_id, pulse in camera_forward:
        board.set_servo_position(500, [(servo_id, pulse)])
        time.sleep(0.3)
    
    print("Done!")


if __name__ == '__main__':
    main()
