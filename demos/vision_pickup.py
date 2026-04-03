#!/usr/bin/env python3
"""
Vision-Guided Pickup Demo
AprilTag-assisted block pickup using inverse kinematics

Usage:
    python3 demos/vision_pickup.py --color red
    python3 demos/vision_pickup.py --color blue --tag 0
    python3 demos/vision_pickup.py --color red --no-tag  # Without AprilTag
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pathfinder import Pathfinder
# DEPRECATED: from capabilities.pickup import VisualPickupController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Vision-guided block pickup demo")
    parser.add_argument(
        '--color',
        type=str,
        default='red',
        choices=['red', 'blue', 'green', 'yellow'],
        help='Block color to pick up (default: red)'
    )
    parser.add_argument(
        '--tag',
        type=int,
        default=None,
        help='AprilTag ID to use as reference (default: any visible tag)'
    )
    parser.add_argument(
        '--no-tag',
        action='store_true',
        help='Disable AprilTag-assisted positioning (less accurate)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Detect only, don\'t execute pickup'
    )
    parser.add_argument(
        '--no-align',
        action='store_true',
        help='Disable automatic alignment to block angle'
    )
    parser.add_argument(
        '--max-angle',
        type=float,
        default=30,
        help='Maximum block angle to attempt pickup (degrees, default: 30)'
    )
    parser.add_argument(
        '--no-mecanum-position',
        action='store_true',
        help='Disable mecanum fine positioning (strafing)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("Vision-Guided Pickup Demo")
    print("="*60)
    print(f"Target: {args.color} block")
    print(f"AprilTag assist: {'OFF' if args.no_tag else 'ON'}")
    if args.tag is not None:
        print(f"Reference tag: {args.tag}")
    print("="*60 + "\n")
    
    # Initialize robot
    print("Initializing robot...")
    try:
        robot = Pathfinder()
        robot.initialize(enable_camera=True, enable_sonar=False, enable_monitoring=False)
        
        # Create pickup controller
        pickup = VisualPickupController(robot)
        
        # Configure alignment
        if args.no_align:
            pickup.align_to_block = False
            print("⚠️  Block alignment disabled")
        pickup.max_misalignment_degrees = args.max_angle
        
        # Configure mecanum positioning
        if args.no_mecanum_position:
            pickup.use_mecanum_positioning = False
            print("⚠️  Mecanum fine positioning disabled")
        
        print("✅ Robot ready!\n")
        
    except Exception as e:
        print(f"❌ Failed to initialize robot: {e}")
        return 1
    
    # Setup instructions
    print("SETUP:")
    print(f"1. Place {args.color} block on floor in front of robot")
    print(f"2. Block should be 1 inch (25mm) cube")
    if not args.no_tag:
        print(f"3. Place AprilTag near block (6\" tag recommended)")
        print(f"   - Tag should be visible to camera")
        print(f"   - Tag provides reference for accurate positioning")
    print()
    
    input("Press Enter when ready to start...")
    
    # Execute pickup
    try:
        print("\n🤖 Starting pickup sequence...\n")
        
        result = pickup.pickup_block(
            color=args.color,
            use_tag=not args.no_tag,
            tag_id=args.tag
        )
        
        # Print results
        print("\n" + "="*60)
        print("PICKUP RESULT")
        print("="*60)
        print(f"Success: {'✅ YES' if result.success else '❌ NO'}")
        print(f"Reason: {result.reason}")
        if result.block_position:
            x, y, z = result.block_position
            print(f"Block position: x={x:.1f}mm, y={y:.1f}mm, z={z:.1f}mm")
        print(f"Time taken: {result.time_taken:.1f}s")
        print(f"Images saved: {len(result.images)}")
        for img_path in result.images:
            print(f"  - {img_path}")
        print("="*60 + "\n")
        
        # Shutdown
        robot.shutdown()
        
        return 0 if result.success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        robot.chassis.stop()
        robot.shutdown()
        return 130
    
    except Exception as e:
        print(f"\n❌ Pickup failed: {e}")
        import traceback
        traceback.print_exc()
        robot.chassis.stop()
        robot.shutdown()
        return 1


if __name__ == '__main__':
    sys.exit(main())
