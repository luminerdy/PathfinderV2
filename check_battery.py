#!/usr/bin/env python3
"""
Quick battery voltage check for PathfinderV2 robot.

Usage:
    python3 check_battery.py           # Display voltage
    python3 check_battery.py --strict  # Exit 1 if < 7.5V (for scripts)
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from hardware import Board


def check_battery(strict=False, minimum_voltage=7.5):
    """
    Check battery voltage and display status.
    
    Args:
        strict: If True, exit with code 1 if voltage too low
        minimum_voltage: Minimum acceptable voltage (default 7.5V)
    
    Returns:
        Voltage in volts, or None if cannot read
    """
    try:
        board = Board()
        import time
        time.sleep(0.5)  # Wait for board initialization
        volt_mv = board.get_battery()
        
        if volt_mv is None:
            print("ERROR: Cannot read battery voltage")
            print("   Check that board is connected and powered")
            if strict:
                sys.exit(1)
            return None
        
        volts = volt_mv / 1000.0
        
        # Determine status
        if volts < 6.5:
            status = "RED EMERGENCY"
            message = "Charge immediately! Risk of battery damage!"
            safe = False
        elif volts < 7.0:
            status = "RED CRITICAL"
            message = "No motor operation allowed. Charge now!"
            safe = False
        elif volts < 7.5:
            status = "YELLOW LOW"
            message = "Charge soon. Light operation only."
            safe = False
        elif volts < 8.0:
            status = "GREEN OK"
            message = "Normal operation permitted."
            safe = True
        else:
            status = "GREEN EXCELLENT"
            message = "Fully charged and ready!"
            safe = True
        
        # Display results
        print(f"Battery: {volts:.2f}V")
        print(f"Status:  {status}")
        print(f"Note:    {message}")
        
        # Exit based on strict mode
        if strict and not safe:
            print(f"\nERROR: Battery below minimum ({minimum_voltage}V)")
            sys.exit(1)
        
        # Turn off sonar LEDs (power saving)
        board.set_rgb(0, 0, 0)  # All LEDs off
        board.close()
        return volts
        
    except Exception as e:
        print(f"ERROR: Error checking battery: {e}")
        if strict:
            sys.exit(1)
        return None


if __name__ == "__main__":
    strict_mode = "--strict" in sys.argv or "-s" in sys.argv
    
    print("PathfinderV2 Battery Check")
    print("-" * 40)
    
    voltage = check_battery(strict=strict_mode)
    
    if voltage and voltage >= 7.5:
        print("\nOK: Ready for operation")
        sys.exit(0)
    elif voltage:
        print("\nWARNING: Charge battery before motor operation")
        sys.exit(0 if not strict_mode else 1)
    else:
        sys.exit(1)
