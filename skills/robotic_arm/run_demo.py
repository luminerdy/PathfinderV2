#!/usr/bin/env python3
"""
Robotic Arm Demo (Level 2: Named Positions)

Demonstrates arm control through named positions.
No inverse kinematics - just simple position names.

Usage:
    python3 run_demo.py

What you'll see:
    1. Move through named positions (rest, forward, pickup, home)
    2. Gripper control (open/close)
    3. Safe, pre-tested movements

This is the foundation - later skills add XYZ coordinates and IK.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board
from hardware.arm import Arm

def main():
    print("=" * 60)
    print("ROBOTIC ARM DEMO - Named Positions")
    print("=" * 60)
    print()
    print("This demo moves the arm through pre-defined positions.")
    print("Each position is safe and tested.")
    print()
    print("Press Ctrl+C to stop at any time.")
    print("-" * 60)
    print()
    
    board = get_board()
    arm = Arm(board)
    
    try:
        # Demo 1: Named Positions
        print("[Demo 1] Named Positions")
        print()
        
        positions = [
            ('home', 'Starting position'),
            ('rest', 'Compact, safe pose'),
            ('forward', 'Reach forward'),
            ('pickup', 'Low, ready to grab'),
            ('carry', 'Hold object while moving'),
            ('home', 'Return to start'),
        ]
        
        for pos_name, description in positions:
            print(f"  Moving to '{pos_name}' - {description}")
            arm.move_to_named(pos_name, duration=1.5)
            time.sleep(1.0)
        
        print("  [OK] Named positions complete!")
        print()
        time.sleep(1)
        
        # Demo 2: Gripper Control
        print("[Demo 2] Gripper Control")
        print()
        
        arm.move_to_named('forward', duration=1.5)
        time.sleep(0.5)
        
        print("  Opening gripper...")
        arm.open_gripper()
        time.sleep(1)
        
        print("  Closing gripper...")
        arm.close_gripper()
        time.sleep(1)
        
        print("  Partial grip (50%)...")
        arm.grip(force=0.5)
        time.sleep(1)
        
        print("  Opening again...")
        arm.open_gripper()
        time.sleep(1)
        
        print("  [OK] Gripper control complete!")
        print()
        time.sleep(1)
        
        # Demo 3: Relative Movement
        print("[Demo 3] Relative Movement")
        print()
        
        arm.move_to_named('home', duration=1.5)
        time.sleep(0.5)
        
        print("  Raising arm 30mm...")
        arm.raise_arm(30, duration=1.0)
        time.sleep(0.5)
        
        print("  Lowering arm 30mm...")
        arm.lower_arm(30, duration=1.0)
        time.sleep(0.5)
        
        print("  Extending arm 50mm...")
        arm.extend_arm(50, duration=1.0)
        time.sleep(0.5)
        
        print("  Retracting arm 50mm...")
        arm.retract_arm(50, duration=1.0)
        time.sleep(0.5)
        
        print("  [OK] Relative movement complete!")
        print()
        time.sleep(1)
        
        # Return to rest
        print("Returning to rest position...")
        arm.move_to_named('rest', duration=1.5)
        time.sleep(0.5)
        
        print()
        print("=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("What you learned:")
        print("  [OK] Named positions (home, rest, forward, pickup, carry)")
        print("  [OK] Gripper control (open, close, partial grip)")
        print("  [OK] Relative movement (raise, lower, extend, retract)")
        print()
        print("Next steps:")
        print("  - Try Level 1.5: python3 play_action.py shake_head")
        print("  - Try Level 3: XYZ coordinates (see SKILL.md)")
        print("  - Try Level 4: Pick-and-place programming")
        
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Return to safe position
        print("\nReturning to rest...")
        try:
            arm.move_to_named('rest', duration=1.0)
        except:
            pass
        print("Demo complete.")

if __name__ == "__main__":
    main()
