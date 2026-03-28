#!/usr/bin/env python3
"""
AprilTag Navigation Demo (Level 1: Just Run It!)

This is the simplest way to use AprilTag navigation.
Just run this script and watch the robot find and approach tag 581.

No code changes needed - everything is pre-configured.

Usage:
    python3 run_demo.py

What it does:
    1. Opens camera
    2. Looks for AprilTag ID 581
    3. When found, approaches to ~22 inches
    4. Stops and beeps when complete

Press Ctrl+C to stop at any time.
"""

import sys
import os

# Add parent directory to path so we can import from skills
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.strafe_nav import StrafeNavigator

def main():
    print("=" * 60)
    print("APRILTAG NAVIGATION DEMO")
    print("=" * 60)
    print()
    print("Looking for AprilTag ID 581...")
    print("Make sure:")
    print("  - Tag is printed and mounted on wall")
    print("  - Tag is at robot's camera height (~8-10 inches)")
    print("  - Good lighting, no glare on tag")
    print("  - Robot is 3-5 feet from tag")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 60)
    print()
    
    # Create navigator
    nav = StrafeNavigator()
    
    try:
        # Navigate to tag 581
        success = nav.navigate_to_tag(
            tag_id=581,
            target_distance=0.55,  # ~22 inches
            timeout=30.0           # Give up after 30 seconds
        )
        
        if success:
            print()
            print("=" * 60)
            print("SUCCESS! Reached tag 581")
            print("=" * 60)
            
            # Victory beep
            nav.board.set_buzzer(1000, 0.1, 0.1, 2)
            
        else:
            print()
            print("=" * 60)
            print("TIMEOUT: Could not reach tag 581")
            print("=" * 60)
            print()
            print("Troubleshooting:")
            print("  - Is tag visible in camera view?")
            print("  - Try moving robot closer")
            print("  - Check lighting (no glare)")
            print("  - Verify tag is ID 581")
    
    except KeyboardInterrupt:
        print()
        print("Stopped by user (Ctrl+C)")
    
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always stop motors and close camera
        nav._stop()
        nav._close_camera()
        print()
        print("Demo complete.")

if __name__ == "__main__":
    main()
