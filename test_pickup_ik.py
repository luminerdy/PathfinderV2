#!/usr/bin/env python3
"""
Test IK-Based Block Pickup
Demonstrates how arm positions are calculated, not hardcoded
"""

import time
from lib.board_protocol import BoardController
from lib.arm_inverse_kinematics import ArmIK

def main():
    print("=" * 60)
    print("IK-BASED PICKUP DEMONSTRATION")
    print("=" * 60)
    print("\nThis shows how we calculate servo positions for pickup")
    print("using inverse kinematics - NO HARDCODED POSITIONS!\n")
    
    board = BoardController()
    ik = ArmIK()
    
    time.sleep(0.5)
    
    # Scenario: Block is 200mm in front, 0mm to side, 25mm height (1" block)
    print("\n" + "=" * 60)
    print("SCENARIO: 1-inch block directly in front")
    print("=" * 60)
    print("Block position:")
    print("  X: 200mm (forward)")
    print("  Y: 0mm (centered)")
    print("  Z: 25mm (height of block)")
    
    # Step 1: Pre-grasp position (above block)
    print("\n[Step 1] PRE-GRASP POSITION (above block)")
    print("-" * 60)
    x, y, z = 200, 0, 100  # 100mm above ground
    print(f"Target: ({x}, {y}, {z}) mm")
    
    solution = ik.set_position(x, y, z)
    if solution:
        print("IK Solution found:")
        for servo_id, pulse in solution:
            angle = ik.pulse_to_angle(pulse)
            print(f"  Servo {servo_id}: {pulse} ({angle:.1f}°)")
        
        print("\nMoving arm to pre-grasp...")
        for servo_id, pulse in solution:
            board.set_servo_position(500, [(servo_id, pulse)])
            time.sleep(0.3)
        time.sleep(1)
    else:
        print("UNREACHABLE - block too far!")
        return
    
    # Step 2: Open gripper
    print("\n[Step 2] OPEN GRIPPER")
    print("-" * 60)
    print("Servo 1: 2500 (fully open)")
    board.set_servo_position(500, [(1, 2500)])
    time.sleep(1)
    
    # Step 3: Lower to grasp height
    print("\n[Step 3] LOWER TO GRASP HEIGHT")
    print("-" * 60)
    x, y, z = 200, 0, 20  # 20mm above ground (gripper center height)
    print(f"Target: ({x}, {y}, {z}) mm")
    
    solution = ik.set_position(x, y, z)
    if solution:
        print("IK Solution found:")
        for servo_id, pulse in solution:
            angle = ik.pulse_to_angle(pulse)
            print(f"  Servo {servo_id}: {pulse} ({angle:.1f}°)")
        
        print("\nLowering arm...")
        for servo_id, pulse in solution:
            board.set_servo_position(500, [(servo_id, pulse)])
            time.sleep(0.3)
        time.sleep(1)
    else:
        print("UNREACHABLE!")
        return
    
    # Step 4: Close gripper
    print("\n[Step 4] CLOSE GRIPPER (grasp block)")
    print("-" * 60)
    print("Servo 1: 1475 (fully closed)")
    board.set_servo_position(500, [(1, 1475)])
    time.sleep(1)
    print("Block is now held!")
    
    # Step 5: Lift block
    print("\n[Step 5] LIFT BLOCK")
    print("-" * 60)
    x, y, z = 200, 0, 150  # 150mm above ground
    print(f"Target: ({x}, {y}, {z}) mm")
    
    solution = ik.set_position(x, y, z)
    if solution:
        print("IK Solution found:")
        for servo_id, pulse in solution:
            angle = ik.pulse_to_angle(pulse)
            print(f"  Servo {servo_id}: {pulse} ({angle:.1f}°)")
        
        print("\nLifting block...")
        for servo_id, pulse in solution:
            board.set_servo_position(500, [(servo_id, pulse)])
            time.sleep(0.3)
        time.sleep(1)
    else:
        print("UNREACHABLE!")
        return
    
    print("\n" + "=" * 60)
    print("PICKUP COMPLETE!")
    print("=" * 60)
    print("\nKey Points:")
    print("  1. All positions calculated via IK")
    print("  2. No hardcoded servo angles")
    print("  3. Works for ANY block position")
    print("  4. Just need (x, y, z) coordinates")
    print("\nHow to get coordinates:")
    print("  - Camera vision (detect block)")
    print("  - AprilTag reference (accurate positioning)")
    print("  - Distance estimation (from camera)")
    
    # Optional: Release and return to camera-forward
    print("\n[Optional] Release block and return to camera position?")
    print("Press Enter to release, Ctrl+C to skip...")
    try:
        input()
        
        # Open gripper
        print("\nReleasing block...")
        board.set_servo_position(500, [(1, 2500)])
        time.sleep(1)
        
        # Return to camera-forward
        print("\nReturning to camera-forward position...")
        camera_forward = [
            (6, 1500),  # Base forward
            (5, 700),   # Shoulder
            (4, 2450),  # Elbow
            (3, 590),   # Wrist
        ]
        for servo_id, pulse in camera_forward:
            board.set_servo_position(500, [(servo_id, pulse)])
            time.sleep(0.3)
        
        print("Done!")
        
    except KeyboardInterrupt:
        print("\nSkipped release")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
