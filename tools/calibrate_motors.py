#!/usr/bin/env python3
"""
Motor Speed Calibration Utility

Finds minimum and maximum reliable motor speeds for mecanum chassis.

Usage:
    python3 tools/calibrate_motors.py --test-min
    python3 tools/calibrate_motors.py --test-max
    python3 tools/calibrate_motors.py --full
"""

import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.board import get_board  # was: from hardware import Board, Chassis


def test_minimum_speed(chassis: Chassis):
    """
    Find minimum motor speed that actually moves robot
    
    Tests speeds from 0-50 to find threshold where movement starts
    """
    print("\n" + "="*60)
    print("MINIMUM SPEED TEST")
    print("="*60)
    print("\nThis test will slowly increase motor speed until robot moves.")
    print("Watch the robot carefully!")
    print()
    
    input("Place robot on open floor. Press Enter to start...")
    
    results = {
        'forward': None,
        'strafe': None,
        'rotate': None
    }
    
    # Test forward movement
    print("\n--- Testing FORWARD minimum speed ---")
    for speed in range(5, 51, 5):
        print(f"Testing speed {speed}...", end=" ")
        chassis.set_velocity(speed, 0, 0)
        time.sleep(1.5)
        chassis.stop()
        
        response = input("Did robot move forward? [y/n]: ")
        if response.lower() == 'y':
            results['forward'] = speed
            print(f"✓ Minimum forward speed: {speed}")
            break
        
        time.sleep(0.5)
    
    if not results['forward']:
        print("⚠️  No movement detected up to speed 50!")
    
    # Test strafe (mecanum)
    print("\n--- Testing STRAFE (sideways) minimum speed ---")
    for speed in range(5, 51, 5):
        print(f"Testing speed {speed}...", end=" ")
        chassis.set_velocity(0, speed, 0)
        time.sleep(1.5)
        chassis.stop()
        
        response = input("Did robot strafe right? [y/n]: ")
        if response.lower() == 'y':
            results['strafe'] = speed
            print(f"✓ Minimum strafe speed: {speed}")
            break
        
        time.sleep(0.5)
    
    if not results['strafe']:
        print("⚠️  No strafe movement detected up to speed 50!")
    
    # Test rotation
    print("\n--- Testing ROTATION minimum speed ---")
    for speed in [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]:
        print(f"Testing rotation {speed}...", end=" ")
        chassis.set_velocity(0, 0, speed)
        time.sleep(1.5)
        chassis.stop()
        
        response = input("Did robot rotate? [y/n]: ")
        if response.lower() == 'y':
            results['rotate'] = speed
            print(f"✓ Minimum rotation speed: {speed}")
            break
        
        time.sleep(0.5)
    
    if not results['rotate']:
        print("⚠️  No rotation detected up to 0.5!")
    
    # Summary
    print("\n" + "="*60)
    print("MINIMUM SPEED RESULTS")
    print("="*60)
    print(f"Forward:  {results['forward'] or 'NOT FOUND'}")
    print(f"Strafe:   {results['strafe'] or 'NOT FOUND'}")
    print(f"Rotate:   {results['rotate'] or 'NOT FOUND'}")
    print()
    
    if all(results.values()):
        print("RECOMMENDED CONFIG:")
        print(f"  chassis.min_speed_forward = {results['forward']}")
        print(f"  chassis.min_speed_strafe = {results['strafe']}")
        print(f"  chassis.min_speed_rotate = {results['rotate']}")
    
    return results


def test_maximum_speed(chassis: Chassis):
    """
    Find maximum safe motor speed
    
    Tests increasing speeds to find where robot becomes unstable
    """
    print("\n" + "="*60)
    print("MAXIMUM SPEED TEST")
    print("="*60)
    print("\nThis test will increase speed until robot is unstable.")
    print("⚠️  CAUTION: Robot may move fast! Keep clear!")
    print()
    
    input("Ensure large clear area. Press Enter to start...")
    
    results = {
        'forward': None,
        'strafe': None,
        'rotate': None
    }
    
    # Test forward
    print("\n--- Testing FORWARD maximum speed ---")
    print("Stop test when robot:")
    print("  - Becomes hard to control")
    print("  - Wheels slip significantly")
    print("  - Movement is jerky/unstable")
    print()
    
    for speed in range(30, 101, 10):
        print(f"Testing speed {speed}...", end=" ")
        
        # Short burst
        chassis.set_velocity(speed, 0, 0)
        time.sleep(0.8)
        chassis.stop()
        time.sleep(1)
        
        response = input("Still stable? [y/n]: ")
        if response.lower() == 'n':
            results['forward'] = speed - 10  # Previous speed was max
            print(f"✓ Maximum forward speed: {results['forward']}")
            break
    
    if not results['forward']:
        results['forward'] = 100
        print(f"✓ Maximum forward speed: 100 (no issues found)")
    
    # Test strafe
    print("\n--- Testing STRAFE maximum speed ---")
    for speed in range(30, 101, 10):
        print(f"Testing speed {speed}...", end=" ")
        
        # Short burst right
        chassis.set_velocity(0, speed, 0)
        time.sleep(0.8)
        chassis.stop()
        time.sleep(1)
        
        response = input("Still stable? [y/n]: ")
        if response.lower() == 'n':
            results['strafe'] = speed - 10
            print(f"✓ Maximum strafe speed: {results['strafe']}")
            break
    
    if not results['strafe']:
        results['strafe'] = 100
        print(f"✓ Maximum strafe speed: 100 (no issues found)")
    
    # Test rotation
    print("\n--- Testing ROTATION maximum speed ---")
    for speed in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        print(f"Testing rotation {speed}...", end=" ")
        
        # Short rotation
        chassis.set_velocity(0, 0, speed)
        time.sleep(0.8)
        chassis.stop()
        time.sleep(1)
        
        response = input("Still stable? [y/n]: ")
        if response.lower() == 'n':
            # Find previous value
            prev_speed = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            idx = prev_speed.index(speed)
            results['rotate'] = prev_speed[idx-1] if idx > 0 else 0.3
            print(f"✓ Maximum rotation speed: {results['rotate']}")
            break
    
    if not results['rotate']:
        results['rotate'] = 1.0
        print(f"✓ Maximum rotation speed: 1.0 (no issues found)")
    
    # Summary
    print("\n" + "="*60)
    print("MAXIMUM SPEED RESULTS")
    print("="*60)
    print(f"Forward:  {results['forward']}")
    print(f"Strafe:   {results['strafe']}")
    print(f"Rotate:   {results['rotate']}")
    print()
    print("RECOMMENDED CONFIG:")
    print(f"  chassis.max_speed_forward = {results['forward']}")
    print(f"  chassis.max_speed_strafe = {results['strafe']}")
    print(f"  chassis.max_speed_rotate = {results['rotate']}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Calibrate motor speeds")
    parser.add_argument('--test-min', action='store_true', help='Test minimum speeds')
    parser.add_argument('--test-max', action='store_true', help='Test maximum speeds')
    parser.add_argument('--full', action='store_true', help='Run both tests')
    
    args = parser.parse_args()
    
    if not (args.test_min or args.test_max or args.full):
        parser.print_help()
        return 1
    
    # Initialize
    print("Initializing robot...")
    board = Board()
    chassis = Chassis(board)
    
    print("✓ Robot ready")
    print()
    print("SAFETY NOTES:")
    print("  - Keep robot on floor (not table!)")
    print("  - Ensure large clear area")
    print("  - Be ready to catch robot if needed")
    print("  - Battery should be > 7.5V")
    print()
    
    try:
        min_results = None
        max_results = None
        
        if args.test_min or args.full:
            min_results = test_minimum_speed(chassis)
        
        if args.test_max or args.full:
            max_results = test_maximum_speed(chassis)
        
        # Final summary
        if args.full:
            print("\n" + "="*60)
            print("COMPLETE CALIBRATION RESULTS")
            print("="*60)
            print("\nAdd to config.yaml:")
            print("```yaml")
            print("hardware:")
            print("  chassis:")
            print(f"    min_speed_forward: {min_results['forward'] if min_results else 20}")
            print(f"    min_speed_strafe: {min_results['strafe'] if min_results else 20}")
            print(f"    min_speed_rotate: {min_results['rotate'] if min_results else 0.2}")
            print(f"    max_speed_forward: {max_results['forward'] if max_results else 80}")
            print(f"    max_speed_strafe: {max_results['strafe'] if max_results else 80}")
            print(f"    max_speed_rotate: {max_results['rotate'] if max_results else 0.8}")
            print("```")
        
        board.close()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        chassis.stop()
        board.close()
        return 130


if __name__ == '__main__':
    sys.exit(main())
