#!/usr/bin/env python3
"""
Movement Utility Functions - Calibrated Movement

Provides calibrated rotation and movement functions based on
empirical testing with fresh batteries (8.2V+).

Calibration: March 24, 2026
- Power 30 rotation: ~103 deg/sec
- 90° turn: 0.87 seconds
- Battery requirement: >8.2V for reliable operation
"""

import time
from lib.board_protocol import BoardController

# Calibration constants (Power 30, Battery 8.2V+)
ROTATION_POWER = 30
ROTATION_RATE = 103  # deg/sec
TURN_90_DURATION = 0.87  # seconds

def stop(board):
    """Stop all motors"""
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

def rotate_90(board, direction='right'):
    """
    Rotate 90 degrees in place
    
    Args:
        board: BoardController instance
        direction: 'right' (clockwise) or 'left' (counter-clockwise)
    
    Calibrated for Power 30, Battery >8.2V
    Duration: 0.87 seconds
    """
    if direction == 'right':
        # Clockwise rotation
        board.set_motor_duty([
            (1, ROTATION_POWER),   # Front-left forward
            (2, -ROTATION_POWER),  # Front-right backward
            (3, ROTATION_POWER),   # Rear-left forward
            (4, -ROTATION_POWER)   # Rear-right backward
        ])
    else:
        # Counter-clockwise rotation
        board.set_motor_duty([
            (1, -ROTATION_POWER),  # Front-left backward
            (2, ROTATION_POWER),   # Front-right forward
            (3, -ROTATION_POWER),  # Rear-left backward
            (4, ROTATION_POWER)    # Rear-right forward
        ])
    
    time.sleep(TURN_90_DURATION)
    stop(board)

def rotate_degrees(board, degrees, direction='right'):
    """
    Rotate specified number of degrees
    
    Args:
        board: BoardController instance
        degrees: Angle to rotate (positive value, 0-360)
        direction: 'right' (clockwise) or 'left' (counter-clockwise)
    
    Calibrated for Power 30, Battery >8.2V
    Rate: ~103 deg/sec
    """
    # Calculate duration based on calibrated rotation rate
    duration = abs(degrees) / ROTATION_RATE
    
    if direction == 'right':
        board.set_motor_duty([
            (1, ROTATION_POWER),
            (2, -ROTATION_POWER),
            (3, ROTATION_POWER),
            (4, -ROTATION_POWER)
        ])
    else:
        board.set_motor_duty([
            (1, -ROTATION_POWER),
            (2, ROTATION_POWER),
            (3, -ROTATION_POWER),
            (4, ROTATION_POWER)
        ])
    
    time.sleep(duration)
    stop(board)

def rotate_180(board):
    """
    Rotate 180 degrees (turn around)
    
    Args:
        board: BoardController instance
    
    Uses right rotation for consistency.
    Duration: 2 x 90° = 1.74 seconds
    """
    rotate_90(board, 'right')
    time.sleep(0.1)  # Small pause between turns
    rotate_90(board, 'right')

def rotate_360(board):
    """
    Rotate 360 degrees (full circle)
    
    Args:
        board: BoardController instance
    
    Duration: 360 / 103 = 3.5 seconds
    """
    rotate_degrees(board, 360, 'right')

# Forward movement functions (TODO: needs calibration)
def forward(board, power=30, duration=1.0):
    """
    Drive forward
    
    Args:
        board: BoardController instance
        power: Motor power (30+ recommended for battery >8.2V)
        duration: Time to drive (seconds)
    
    NOTE: Speed (cm/sec) not yet calibrated
    """
    board.set_motor_duty([
        (1, power),
        (2, power),
        (3, power),
        (4, power)
    ])
    time.sleep(duration)
    stop(board)

def backward(board, power=30, duration=1.0):
    """
    Drive backward
    
    Args:
        board: BoardController instance
        power: Motor power (30+ recommended)
        duration: Time to drive (seconds)
    """
    board.set_motor_duty([
        (1, -power),
        (2, -power),
        (3, -power),
        (4, -power)
    ])
    time.sleep(duration)
    stop(board)

def strafe_right(board, power=30, duration=1.0):
    """
    Strafe right (mecanum wheels)
    
    Args:
        board: BoardController instance
        power: Motor power
        duration: Time to strafe (seconds)
    """
    board.set_motor_duty([
        (1, power),   # Front-left forward
        (2, -power),  # Front-right backward
        (3, -power),  # Rear-left backward
        (4, power)    # Rear-right forward
    ])
    time.sleep(duration)
    stop(board)

def strafe_left(board, power=30, duration=1.0):
    """
    Strafe left (mecanum wheels)
    
    Args:
        board: BoardController instance
        power: Motor power
        duration: Time to strafe (seconds)
    """
    board.set_motor_duty([
        (1, -power),  # Front-left backward
        (2, power),   # Front-right forward
        (3, power),   # Rear-left forward
        (4, -power)   # Rear-right backward
    ])
    time.sleep(duration)
    stop(board)

# Battery check helper
def check_battery(board, min_voltage=8.2):
    """
    Check if battery voltage is adequate
    
    Args:
        board: BoardController instance
        min_voltage: Minimum acceptable voltage (default 8.2V)
    
    Returns:
        (voltage, is_adequate) tuple
    """
    mv = board.get_battery()
    if not mv:
        return None, False
    
    voltage = mv / 1000.0
    is_adequate = voltage >= min_voltage
    
    return voltage, is_adequate

if __name__ == '__main__':
    # Demo usage
    print("Movement Utility Demo")
    print("="*50)
    print()
    
    board = BoardController()
    
    # Check battery
    voltage, ok = check_battery(board)
    if voltage:
        print(f"Battery: {voltage:.2f}V")
        if ok:
            print("Status: OK for calibrated movement")
        else:
            print("WARNING: Battery low, calibration may not be accurate")
    print()
    
    print("Available functions:")
    print("  rotate_90(board, direction='right')")
    print("  rotate_degrees(board, degrees, direction='right')")
    print("  rotate_180(board)")
    print("  rotate_360(board)")
    print("  forward(board, power=30, duration=1.0)")
    print("  backward(board, power=30, duration=1.0)")
    print("  strafe_right(board, power=30, duration=1.0)")
    print("  strafe_left(board, power=30, duration=1.0)")
    print()
