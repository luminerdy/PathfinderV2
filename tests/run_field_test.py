#!/usr/bin/env python3
"""
Autonomous Field Test Runner

Usage:
    python3 -m tests.run_field_test --field wall_field_6x6
    python3 -m tests.run_field_test --field corner_field_6x6
    python3 -m tests.run_field_test --list-fields
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.field_config import get_field_config, AVAILABLE_FIELDS, print_field_info
from tests.autonomous_tests import AutonomousTestSuite


def setup_logging(verbose=False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def list_available_fields():
    """Print available field configurations"""
    print("\nAvailable field configurations:\n")
    for name, config in AVAILABLE_FIELDS.items():
        print(f"  {name:20s} - {config.description}")
        print(f"  {'':20s}   Size: {config.size_ft[0]}' x {config.size_ft[1]}', Tags: {config.get_tag_count()}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Run autonomous field tests with AprilTag navigation"
    )
    parser.add_argument(
        '--field',
        type=str,
        default='wall_field_6x6',
        help='Field configuration to use (default: wall_field_6x6)'
    )
    parser.add_argument(
        '--list-fields',
        action='store_true',
        help='List available field configurations and exit'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='test_results',
        help='Output directory for test results (default: test_results)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose logging'
    )
    parser.add_argument(
        '--battery-check',
        action='store_true',
        default=True,
        help='Check battery before starting (default: True)'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if args.list_fields:
        list_available_fields()
        return 0
    
    # Get field config
    try:
        field_config = get_field_config(args.field)
    except ValueError as e:
        print(f"\nError: {e}")
        print("\nUse --list-fields to see available configurations")
        return 1
    
    # Print field info
    print_field_info(field_config)
    
    # Battery check
    if args.battery_check:
        print("Checking battery...")
        try:
            from hardware import Board
            board = Board()
            import time
            time.sleep(0.5)
            voltage = board.get_battery()
            if voltage:
                v = voltage / 1000.0
                print(f"Battery: {v:.2f}V")
                if v < 7.3:
                    print("⚠️  Battery low! Charge recommended before testing.")
                    response = input("Continue anyway? [y/N]: ")
                    if response.lower() != 'y':
                        print("Aborted.")
                        return 1
            else:
                print("⚠️  Could not read battery voltage")
        except Exception as e:
            print(f"⚠️  Battery check failed: {e}")
            print("Continuing anyway...")
    
    # Initialize robot
    print("\nInitializing robot...")
    try:
        # Import Pathfinder
        from pathfinder import Pathfinder
        
        robot = Pathfinder()
        robot.initialize(enable_camera=True, enable_sonar=True, enable_monitoring=False)
        
        # Navigator should be initialized automatically if camera is enabled
        if not hasattr(robot, 'navigator') or robot.navigator is None:
            print("⚠️  Navigator not initialized (camera may be disabled)")
            return 1
        
        print("✅ Robot initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize robot: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Create test suite
    print("\nCreating test suite...")
    test_suite = AutonomousTestSuite(robot, field_config, args.output)
    
    # Confirmation
    print("\n" + "="*60)
    print("READY TO START AUTONOMOUS TESTING")
    print("="*60)
    print(f"\nField: {field_config.name}")
    print(f"Tags to test: {field_config.get_all_tags()}")
    print(f"Expected duration: 2-5 minutes")
    print(f"Results will be saved to: {test_suite.run_dir}")
    print("\nRobot will:")
    print("  1. Scan for all AprilTags (360° rotation)")
    print("  2. Navigate to each tag individually")
    print("  3. Complete a full waypoint tour")
    print("  4. Return to home position")
    print("\n⚠️  Make sure field is clear and robot has room to move!")
    print()
    
    response = input("Start testing? [Y/n]: ")
    if response.lower() == 'n':
        print("Aborted.")
        robot.shutdown()
        return 0
    
    # Run tests
    try:
        print("\n🤖 Starting autonomous test suite...\n")
        summary = test_suite.run_all_tests()
        
        # Print summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success rate: {100*summary['passed']/summary['total_tests']:.1f}%")
        print(f"Total time: {summary['total_time']:.1f}s")
        print(f"\nResults: {test_suite.run_dir}")
        print(f"Report: {test_suite.run_dir / 'report.md'}")
        print("="*60 + "\n")
        
        # Cleanup
        robot.shutdown()
        
        return 0 if summary['failed'] == 0 else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        robot.chassis.stop()
        robot.shutdown()
        return 130
    
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        robot.chassis.stop()
        robot.shutdown()
        return 1


if __name__ == '__main__':
    sys.exit(main())
