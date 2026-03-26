"""
Board Controller — Platform Auto-Detection

Automatically selects the correct board driver based on
the Raspberry Pi model:
  - Pi 5: Serial protocol (lib/board_protocol.py)
  - Pi 4: I2C protocol (lib/board_pi4.py)

Usage:
    from lib.board import get_board
    board = get_board()
    board.set_motor_duty([(1, 30)])  # Works on both platforms
"""

import os


def detect_platform():
    """
    Detect which Raspberry Pi model we're running on.
    
    Returns:
        'pi5', 'pi4', or 'unknown'
    """
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
        
        if 'Pi 5' in model:
            return 'pi5'
        elif 'Pi 4' in model:
            return 'pi4'
        else:
            return 'unknown'
    except Exception:
        return 'unknown'


def get_board(**kwargs):
    """
    Get the appropriate BoardController for this platform.
    
    Returns:
        BoardController instance (Pi 5 serial or Pi 4 I2C)
    """
    platform = detect_platform()
    
    if platform == 'pi5':
        from lib.board_protocol import BoardController
        return BoardController(**kwargs)
    elif platform == 'pi4':
        from lib.board_pi4 import BoardController
        return BoardController(**kwargs)
    else:
        # Default to Pi 5 protocol (most likely for development)
        from lib.board_protocol import BoardController
        return BoardController(**kwargs)


# Quick access
PLATFORM = detect_platform()
