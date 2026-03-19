"""
D1 - Basic Drive
Introduction to mecanum drive movement
"""

import time
import logging

logger = logging.getLogger(__name__)


def run(robot):
    """
    D1 Demo: Basic mecanum drive patterns
    
    Teaches:
    - Forward/backward movement
    - Left/right strafing
    - Rotation in place
    - Diagonal movement
    """
    logger.info("=== D1: Basic Drive Demo ===")
    
    speed = 50  # mm/s
    duration = 2.0  # seconds
    
    try:
        # 1. Forward
        print("\n1. Moving forward...")
        robot.movement.move_forward(speed, duration)
        time.sleep(1)
        
        # 2. Backward
        print("2. Moving backward...")
        robot.movement.move_backward(speed, duration)
        time.sleep(1)
        
        # 3. Strafe right
        print("3. Strafing right...")
        robot.movement.strafe_right(speed, duration)
        time.sleep(1)
        
        # 4. Strafe left
        print("4. Strafing left...")
        robot.movement.strafe_left(speed, duration)
        time.sleep(1)
        
        # 5. Rotate clockwise
        print("5. Rotating clockwise...")
        robot.movement.rotate(90, speed=0.5)
        time.sleep(1)
        
        # 6. Rotate counterclockwise
        print("6. Rotating counterclockwise...")
        robot.movement.rotate(-90, speed=0.5)
        time.sleep(1)
        
        # 7. Diagonal movement
        print("7. Moving diagonally (forward-right)...")
        robot.chassis.forward_right(speed)
        time.sleep(duration)
        robot.chassis.stop()
        time.sleep(1)
        
        # 8. Square pattern
        print("8. Executing square pattern...")
        robot.movement.square(side_length=2.0, speed=speed)
        
        print("\nD1 Demo complete!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        robot.chassis.stop()


if __name__ == '__main__':
    print("Run via: python pathfinder.py --demo d1_basic_drive")
