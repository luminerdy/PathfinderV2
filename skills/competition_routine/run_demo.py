#!/usr/bin/env python3
"""
Competition Routine Demo (E7)

Full autonomous scoring cycle:
  Phase 1: Find and pick up a colored block
  Phase 2: Find the lime green tape line
  Phase 3: Follow line to scoring zone
  Phase 4: Release block (deliver/score)

This chains E3 + E4 + E5 + E6 into one complete competition cycle.

Usage:
    python3 run_demo.py              # One cycle, any color
    python3 run_demo.py red          # One cycle, red blocks only
    python3 run_demo.py red 3        # Three cycles, red blocks

SAFETY: Robot will drive, rotate, and move arm! Clear the field.
"""

import sys
import os

# Add project root for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.competition_routine.competition import competition_cycle


def main():
    """Run competition routine demo."""

    # Parse arguments
    color = None
    cycles = 1

    if len(sys.argv) > 1:
        color = sys.argv[1].lower()
        if color not in ('red', 'blue', 'yellow'):
            print("Usage: python3 run_demo.py [red|blue|yellow] [cycles]")
            sys.exit(1)

    if len(sys.argv) > 2:
        try:
            cycles = int(sys.argv[2])
        except ValueError:
            print("Usage: python3 run_demo.py [red|blue|yellow] [cycles]")
            sys.exit(1)

    print("=" * 60)
    print("COMPETITION ROUTINE DEMO (E7)")
    print("=" * 60)
    print()
    print("Target: %s" % (color or "any color"))
    print("Cycles: %d" % cycles)
    print()
    print("4 phases per cycle:")
    print("  1. PICKUP  - Scan, approach, grab block")
    print("  2. FIND LINE - Rotate to find green tape")
    print("  3. FOLLOW  - Drive along tape to scoring zone")
    print("  4. DELIVER - Open gripper, release block, back up")
    print()
    print("SAFETY:")
    print("  - Clear the field (robot will drive and rotate)")
    print("  - Place colored blocks in the arena")
    print("  - Ensure green tape line is on the floor")
    print("  - Press Ctrl+C for emergency stop")
    print()
    input("Press Enter to start...")
    print()

    total_success = 0

    for cycle_num in range(1, cycles + 1):
        if cycles > 1:
            print()
            print("========== CYCLE %d/%d ==========" % (cycle_num, cycles))

        result = competition_cycle(color=color)

        print()
        print("=" * 60)
        if result['success']:
            print("CYCLE %d: SUCCESS! (%.1fs)" % (cycle_num, result['time_taken']))
            total_success += 1
        else:
            print("CYCLE %d: STOPPED at phase '%s'" % (cycle_num, result['phase_reached']))
            print("  Reason: %s" % result['details'])
        print("=" * 60)

    if cycles > 1:
        print()
        print("FINAL SCORE: %d/%d cycles completed" % (total_success, cycles))

    print()
    print("What you learned:")
    print("  [OK] State machine (4 phases with transitions)")
    print("  [OK] Skill chaining (E3+E4+E5+E6 in sequence)")
    print("  [OK] Error recovery (each phase can fail gracefully)")
    print("  [OK] Battery awareness (checks before starting)")


if __name__ == "__main__":
    main()
