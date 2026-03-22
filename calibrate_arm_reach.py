#!/usr/bin/env python3
"""
Calibrate arm reach envelope - Find actual pickup zone
Determines how close robot needs to be to pickup blocks
"""

import sys
sys.path.append('/home/robot/code/pathfinder')

from hardware.arm import Arm
from lib.arm_inverse_kinematics import ArmIK
import time
import json

def test_reach_point(arm, ik, x, y, z, description):
    """Test if arm can reach a specific point"""
    print(f"\nTesting: {description}")
    print(f"Target: X={x}mm, Y={y}mm, Z={z}mm")
    
    try:
        # Calculate IK
        angles = ik.calculate(x, y, z)
        print(f"IK Solution: {angles}")
        
        # Try to move there
        arm.set_servos({
            6: angles['base'],
            5: angles['shoulder'],
            4: angles['elbow'],
            3: angles['wrist']
        })
        time.sleep(2)
        
        # Visual confirmation
        reachable = input("Can reach this point? (y/n): ").lower() == 'y'
        
        if reachable:
            # Measure actual position
            print("Measure gripper center from robot base:")
            actual_x = float(input("  Forward distance (mm): "))
            actual_y = float(input("  Side distance (mm, + = right): "))
            actual_z = float(input("  Height above floor (mm): "))
            
            error = ((actual_x - x)**2 + (actual_y - y)**2 + (actual_z - z)**2)**0.5
            
            return {
                'target': (x, y, z),
                'actual': (actual_x, actual_y, actual_z),
                'reachable': True,
                'error_mm': error,
                'angles': angles
            }
        else:
            reason = input("Why not reachable? (collision/out-of-range/servo-limit): ")
            return {
                'target': (x, y, z),
                'reachable': False,
                'reason': reason
            }
            
    except Exception as e:
        print(f"IK Error: {e}")
        return {
            'target': (x, y, z),
            'reachable': False,
            'reason': f'ik_error: {e}'
        }

def calibrate_pickup_zone():
    """Find the optimal pickup zone in front of robot"""
    
    print("="*60)
    print("ARM REACH CALIBRATION - PICKUP ZONE")
    print("="*60)
    print("\nThis will test arm reach at various positions")
    print("to find the optimal zone for block pickup.")
    print("\nMeasurements from robot base center:")
    print("  X = Forward (positive)")
    print("  Y = Side (positive = right)")
    print("  Z = Height above floor")
    print()
    
    arm = Arm()
    ik = ArmIK()
    
    # Block height on floor (adjust if needed)
    BLOCK_HEIGHT = 25  # mm (1 inch block = 25.4mm)
    
    # Test grid of positions
    test_points = [
        # Format: (x, y, z, description)
        # Very close
        (80, 0, BLOCK_HEIGHT, "Very close - center"),
        (80, 30, BLOCK_HEIGHT, "Very close - right"),
        (80, -30, BLOCK_HEIGHT, "Very close - left"),
        
        # Close (likely optimal)
        (100, 0, BLOCK_HEIGHT, "Close - center"),
        (100, 30, BLOCK_HEIGHT, "Close - right"),
        (100, -30, BLOCK_HEIGHT, "Close - left"),
        (100, 50, BLOCK_HEIGHT, "Close - far right"),
        (100, -50, BLOCK_HEIGHT, "Close - far left"),
        
        # Medium
        (130, 0, BLOCK_HEIGHT, "Medium - center"),
        (130, 30, BLOCK_HEIGHT, "Medium - right"),
        (130, -30, BLOCK_HEIGHT, "Medium - left"),
        
        # Far
        (150, 0, BLOCK_HEIGHT, "Far - center"),
        (150, 30, BLOCK_HEIGHT, "Far - right"),
        (150, -30, BLOCK_HEIGHT, "Far - left"),
        
        # Very far (probably out of range)
        (180, 0, BLOCK_HEIGHT, "Very far - center"),
        (200, 0, BLOCK_HEIGHT, "Max range - center"),
    ]
    
    results = []
    
    # Move to rest position first
    print("\nMoving to rest position...")
    arm.move_to_rest()
    time.sleep(2)
    
    for x, y, z, desc in test_points:
        result = test_reach_point(arm, ik, x, y, z, desc)
        results.append(result)
        
        # Return to rest between tests
        arm.move_to_rest()
        time.sleep(1)
    
    # Analysis
    print("\n" + "="*60)
    print("CALIBRATION RESULTS")
    print("="*60)
    
    reachable_points = [r for r in results if r.get('reachable')]
    unreachable_points = [r for r in results if not r.get('reachable')]
    
    print(f"\nReachable: {len(reachable_points)}/{len(results)} points")
    print(f"Unreachable: {len(unreachable_points)}/{len(results)} points")
    
    if reachable_points:
        print("\n✅ REACHABLE POSITIONS:")
        for r in reachable_points:
            x, y, z = r['target']
            error = r.get('error_mm', 0)
            print(f"  ({x:3d}, {y:3d}, {z:2d})mm - Error: {error:.1f}mm")
        
        # Find optimal zone
        center_points = [r for r in reachable_points if r['target'][1] == 0]  # Y = 0 (center)
        if center_points:
            distances = [r['target'][0] for r in center_points]
            min_dist = min(distances)
            max_dist = max(distances)
            optimal_dist = (min_dist + max_dist) // 2
            
            print(f"\n📍 PICKUP ZONE (center line):")
            print(f"  Minimum distance: {min_dist}mm")
            print(f"  Maximum distance: {max_dist}mm")
            print(f"  Optimal distance: {optimal_dist}mm")
            print(f"  Working range: {max_dist - min_dist}mm")
    
    if unreachable_points:
        print("\n❌ UNREACHABLE POSITIONS:")
        for r in unreachable_points:
            x, y, z = r['target']
            reason = r.get('reason', 'unknown')
            print(f"  ({x:3d}, {y:3d}, {z:2d})mm - {reason}")
    
    # Save results
    results_file = '/home/robot/code/pathfinder/arm_reach_calibration.json'
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'block_height': BLOCK_HEIGHT,
            'results': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")
    
    arm.cleanup()
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    if reachable_points:
        center_reachable = [r for r in reachable_points if r['target'][1] == 0]
        if center_reachable:
            distances = sorted([r['target'][0] for r in center_reachable])
            print(f"\n1. TARGET APPROACH DISTANCE: {distances[len(distances)//2]}mm")
            print(f"   (Robot should position gripper this far from block)")
            
        side_reachable = [r for r in reachable_points if r['target'][1] != 0]
        if side_reachable:
            max_side = max(abs(r['target'][1]) for r in side_reachable)
            print(f"\n2. LATERAL TOLERANCE: ±{max_side}mm")
            print(f"   (Block can be up to {max_side}mm off-center)")
            
        print(f"\n3. CHASSIS POSITIONING STRATEGY:")
        print(f"   - Navigate to block using camera")
        print(f"   - Stop when block is ~{distances[-1] if center_reachable else 150}mm away")
        print(f"   - Use mecanum to fine-tune lateral position")
        print(f"   - Verify block in reach zone before attempting pickup")

if __name__ == "__main__":
    try:
        calibrate_pickup_zone()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled by user")
        sys.exit(1)
