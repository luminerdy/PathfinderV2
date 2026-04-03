#!/usr/bin/env python3
"""
Quick battery voltage check for PathfinderV2 robot.

Usage:
    python3 check_battery.py           # Display voltage
    python3 check_battery.py --strict  # Exit 1 if < 7.5V (for scripts)
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM


def check_battery(strict=False, minimum_voltage=7.5):
    """Check battery voltage and display status."""
    try:
        board = get_board()
        time.sleep(0.5)
        volt_mv = board.get_battery()

        if volt_mv is None or not (5000 < volt_mv < 20000):
            print("ERROR: Cannot read battery voltage")
            if strict:
                sys.exit(1)
            return None

        volts = volt_mv / 1000.0

        if volts < 6.5:
            status, message, safe = "RED EMERGENCY", "Charge immediately!", False
        elif volts < 7.0:
            status, message, safe = "RED CRITICAL", "No motor operation. Charge now!", False
        elif volts < 7.5:
            status, message, safe = "YELLOW LOW", "Charge soon. Light operation only.", False
        elif volts < 8.0:
            status, message, safe = "GREEN OK", "Normal operation permitted.", True
        else:
            status, message, safe = "GREEN EXCELLENT", "Fully charged and ready!", True

        print("Platform: %s" % PLATFORM)
        print("Battery:  %.2fV" % volts)
        print("Status:   %s" % status)
        print("Note:     %s" % message)

        if strict and not safe:
            print("\nERROR: Battery below minimum (%.1fV)" % minimum_voltage)
            sys.exit(1)

        return volts

    except Exception as e:
        print("ERROR: %s" % e)
        if strict:
            sys.exit(1)
        return None


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv
    print("PathfinderV2 Battery Check")
    print("-" * 40)
    voltage = check_battery(strict=strict_mode)
