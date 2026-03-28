#!/usr/bin/env python3
"""
Autonomous Pickup Demo (E5)

Full cycle: scan for block, drive to it, pick it up.

Usage:
    python3 run_demo.py            # Pick up any color
    python3 run_demo.py red        # Pick up red only

SAFETY: Robot will drive and move arm! Clear workspace.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.auto_pickup import auto_pickup

def main():
    color = None
    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 run_demo.py [red|blue|yellow]")
            sys.exit(1)

    print("=" * 60)
    print("AUTONOMOUS PICKUP DEMO")
    print("=" * 60)
    print()
    print("Target: %s" % (color or "any color"))
    print()
    print("This demo runs 3 phases:")
    print("  Phase 1: SCAN - Rotate to find block")
    print("  Phase 2: APPROACH - Drive to block (stop-look-drive)")
    print("  Phase 3: PICKUP - Lower arm, grab, lift")
    print()
    print("SAFETY:")
    print("  - Place a colored block 30-80cm from robot")
    print("  - Clear the workspace")
    print("  - Robot will rotate, drive, and move arm")
    print("  - Press Ctrl+C to emergency stop")
    print()
    input("Press Enter to start...")
    print()

    success = auto_pickup(color=color)

    print()
    if success:
        print("What you learned:")
        print("  [OK] State machine (scan -> approach -> pickup)")
        print("  [OK] Camera switching (forward view -> down view)")
        print("  [OK] Stop-look-drive (no motion blur)")
        print("  [OK] Full integration (D1 + D3 + D4 + E3 + E4)")
    else:
        print("Tips if it failed:")
        print("  - Better lighting (avoid harsh shadows)")
        print("  - Block closer (30-50cm ideal)")
        print("  - Check battery (>7.0V needed)")
        print("  - Try specific color: python3 run_demo.py red")

if __name__ == "__main__":
    main()
