#!/usr/bin/env python3
"""
Start Robot - Initialize and verify robot is ready
Similar to PathfinderBot's pf_start_robot.py
"""

import sys
import time
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from hardware import Board, Arm

# Load config
with open(Path(__file__).parent / 'config.yaml', 'r') as f:
    config = yaml.safe_load(f)


def main():
    """Initialize robot to starting position"""
    print("\n" + "="*50)
    print("  PATHFINDER ROBOT - STARTUP")
    print("="*50)
    
    try:
        # Initialize board
        print("\n1. Connecting to board...")
        hw_config = config['hardware']
        board = Board(
            device=hw_config['board']['serial_port'],
            baudrate=hw_config['board']['baud_rate']
        )
        print("   OK Board connected")
        
        # Check battery
        voltage = board.get_battery_voltage()
        if voltage:
            print(f"   Battery: {voltage:.2f}V", end="")
            if voltage < 6.8:
                print(" WARN LOW!")
            elif voltage < 7.0:
                print(" (caution)")
            else:
                print(" (good)")
        
        # Startup beep
        print("\n2. Running startup sequence...")
        board.beep(0.1)
        time.sleep(0.2)
        board.beep(0.1)
        
        # Initialize arm
        print("\n3. Initializing arm...")
        arm = Arm(board)
        
        print("   Moving to home position...")
        arm.home(duration=2.5)
        
        print("   Opening gripper...")
        arm.open_gripper(duration=1.0)
        time.sleep(1)
        
        # Ready signal
        print("\n4. Robot ready!")
        board.set_rgb(0, 255, 0)  # Green = ready
        board.beep(0.05)
        time.sleep(0.1)
        board.beep(0.05)
        time.sleep(2)
        board.rgb_off()
        
        board.close()
        
        print("\n" + "="*50)
        print("  OK STARTUP COMPLETE")
        print("="*50)
        print("\nRobot is initialized and ready for operation.")
        print("Arm is in home position with gripper open.\n")
        
    except Exception as e:
        print(f"\nFAIL Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
