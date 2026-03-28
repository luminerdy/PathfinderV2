#!/usr/bin/env python3
"""
Visual Servoing Demo (E4)

Demonstrates closed-loop approach to a colored block.
Robot drives toward the nearest visible block using camera feedback.

How it works:
  1. Camera detects block (using E3 block detection)
  2. Lock onto target (won't switch blocks mid-approach)
  3. Calculate error (block position vs frame center)
  4. Proportional control: error * Kp = motor speed
  5. Mecanum strafe + forward simultaneously
  6. Stop when block is at bottom of frame (pickup distance)

This is CLOSED-LOOP control — the robot corrects itself as it moves.
Compare to D1 (open-loop): "drive forward 2 seconds and hope."

Usage:
    python3 run_demo.py            # Approach any color
    python3 run_demo.py red        # Approach red only

SAFETY: Clear space in front of robot! Robot will drive forward.
"""

import sys
import os
import time

# Add project root for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.block_approach import BlockApproach


def callback(block, action):
    """Called periodically during approach to show progress.

    Args:
        block: BlockDetection object (color, position, distance)
        action: String describing current behavior (e.g., 'LOCKED', 'fwd=30')
    """
    print("  %s at (%d,%d) %.0fcm - %s" % (
        block.color, block.center_x, block.center_y,
        block.estimated_distance_mm / 10, action))


def main():
    """Drive toward nearest visible block using visual feedback."""

    # Parse optional color argument
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

    # BlockApproach handles the full control loop:
    #   - Opens camera, detects blocks each frame
    #   - Locks onto first target (tracks by position + color)
    #   - Proportional control: strafe to center, drive forward
    #   - Stops when block reaches TARGET_Y (bottom of frame = close)
    ba = BlockApproach()

    try:
        print("Approaching block...")
        print("-" * 40)

        # approach() runs the control loop until:
        #   - 'reached': block at pickup distance (success)
        #   - 'block_lost': target not seen for LOST_TIMEOUT seconds
        #   - 'timeout': exceeded max time (default 30s)
        #   - 'battery_low': voltage below threshold
        #   - 'interrupted': Ctrl+C pressed
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
        # Always stop motors and release camera
        ba.cleanup()


if __name__ == "__main__":
    main()
