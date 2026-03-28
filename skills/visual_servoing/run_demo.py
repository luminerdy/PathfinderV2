#!/usr/bin/env python3
"""
Visual Servoing Demo (E4)

Demonstrates closed-loop approach to a colored block.
Robot drives toward the nearest visible block using camera feedback.

Usage:
    python3 run_demo.py            # Approach any color
    python3 run_demo.py red        # Approach red only

SAFETY: Clear space in front of robot! Robot will drive forward.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.block_approach import BlockApproach

def callback(block, action):
    print("  %s at (%d,%d) %.0fcm - %s" % (
        block.color, block.center_x, block.center_y,
        block.estimated_distance_mm / 10, action))

def main():
    color = None
    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 run_demo.py [red|blue|yellow]")
            sys.exit(1)

    print("=" * 60)
    print("VISUAL SERVOING DEMO")
    print("=" * 60)
    print()
    print("Target: %s" % (color or "any color"))
    print()
    print("SAFETY: Robot will drive toward the block!")
    print("  - Place a colored block 30-80cm in front")
    print("  - Clear the path")
    print("  - Press Ctrl+C to stop")
    print()
    input("Press Enter to start...")
    print()

    ba = BlockApproach()

    try:
        print("Approaching block...")
        print("-" * 40)
        result = ba.approach(color=color, callback=callback)

        print()
        print("=" * 60)
        if result['success']:
            print("SUCCESS - Reached %s block!" % result['color'])
        else:
            print("STOPPED - Reason: %s" % result['reason'])

        print("  Final position: (%d, %d)" % (result['final_x'], result['final_y']))
        print("  Iterations: %d" % result['iterations'])
        print("=" * 60)
        print()
        print("What you learned:")
        print("  [OK] Closed-loop control (camera feedback corrects errors)")
        print("  [OK] Target locking (tracks one specific block)")
        print("  [OK] Proportional control (error * gain = motor speed)")
        print("  [OK] Mecanum strafe (center + advance simultaneously)")

    except KeyboardInterrupt:
        print("\n\nStopped by user")

    finally:
        ba.cleanup()

if __name__ == "__main__":
    main()
