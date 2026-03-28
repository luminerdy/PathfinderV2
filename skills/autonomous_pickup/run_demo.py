#!/usr/bin/env python3
"""
Autonomous Pickup Demo (E5) [Beta]

Full cycle: scan for block, drive to it, pick it up.

Three phases:
  Phase 1 - SCAN:     Rotate 360deg with camera forward, find block, face it
  Phase 2 - APPROACH:  Switch to camera-down, stop-look-drive to block
  Phase 3 - PICKUP:    Lower arm, close gripper, lift

Key design decisions:
  - Stop-look-drive (not continuous) because motion blur kills small block
    detection. Robot stops, captures clean frame, detects, drives short burst.
  - Camera switching: forward view for finding blocks at distance, down view
    for precise positioning at close range. Different coordinate systems!
  - Target lock: once we pick a block, we track it by position+color so we
    don't switch targets mid-approach.

Usage:
    python3 run_demo.py            # Pick up any color
    python3 run_demo.py red        # Pick up red only

SAFETY: Robot will drive and move arm! Clear workspace.
"""

import sys
import os

# Add project root for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.auto_pickup import auto_pickup


def main():
    """Run full autonomous pickup: scan, approach, grab."""

    # Parse optional color argument
    color = None
    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 run_demo.py [red|blue|yellow]")
            sys.exit(1)

    print("=" * 60)
    print("AUTONOMOUS PICKUP DEMO [Beta]")
    print("=" * 60)
    print()
    print("Target: %s" % (color or "any color"))
    print()
    print("This demo runs 3 phases:")
    print("  Phase 1: SCAN     - Rotate to find block (camera forward)")
    print("  Phase 2: APPROACH  - Drive to block (camera down, stop-look-drive)")
    print("  Phase 3: PICKUP    - Lower arm, grab, lift")
    print()
    print("SAFETY:")
    print("  - Place a colored block 30-80cm from robot")
    print("  - Clear the workspace (robot will rotate and drive)")
    print("  - Press Ctrl+C to emergency stop")
    print()
    input("Press Enter to start...")
    print()

    # auto_pickup() orchestrates the full state machine:
    #   1. Positions arm for forward camera view
    #   2. Rotates up to 360deg looking for blocks
    #   3. Faces the nearest block
    #   4. Switches arm to camera-down view
    #   5. Stop-look-drive approach (short motor bursts between detections)
    #   6. Executes pre-tested arm positions: ready -> grab -> lift -> carry
    #
    # Returns True if block was picked up, False if any phase failed.
    # Common failure reasons: no block found, block lost during approach,
    # battery too low, timeout exceeded.
    success = auto_pickup(color=color)

    print()
    if success:
        print("What you learned:")
        print("  [OK] State machine design (phases with clear transitions)")
        print("  [OK] Camera switching (forward view -> down view)")
        print("  [OK] Stop-look-drive (no motion blur for detection)")
        print("  [OK] Full integration (D1 + D3 + D4 + E3 + E4)")
    else:
        print("Tips if it failed:")
        print("  - Better lighting (avoid harsh shadows on blocks)")
        print("  - Block closer to start (30-50cm ideal)")
        print("  - Check battery: need >7.0V for Pi 4")
        print("  - Try specific color: python3 run_demo.py red")
        print("  - Multiple attempts may be needed [Beta]")


if __name__ == "__main__":
    main()
