"""
D3 - Basic Arm Movements
Introduction to robotic arm control and inverse kinematics
"""

import time
import logging

logger = logging.getLogger(__name__)


def run(robot):
    """
    D3 Demo: Basic arm movements and positions
    
    Teaches:
    - Named positions (home, rest, pickup, etc.)
    - XYZ coordinate movement
    - Relative movement
    - Gripper control
    """
    logger.info("=== D3: Arm Basics Demo ===")
    
    try:
        # 1. Named positions
        print("\n1. Moving through named positions...")
        
        positions = ['home', 'rest', 'forward', 'up', 'carry', 'home']
        for pos in positions:
            print(f"   Moving to: {pos}")
            robot.arm.move_to_named(pos, duration=1.5)
            time.sleep(1)
            
        # 2. XYZ movement
        print("\n2. Moving to specific XYZ coordinates...")
        coordinates = [
            (0, 150, 100, "Center"),
            (40, 150, 100, "Right"),
            (-40, 150, 100, "Left"),
            (0, 200, 80, "Forward-Low"),
            (0, 100, 150, "Back-High"),
        ]
        
        for x, y, z, name in coordinates:
            print(f"   {name}: ({x}, {y}, {z})")
            robot.arm.move_to(x, y, z, duration=1.2)
            time.sleep(0.8)
            
        robot.arm.home()
        time.sleep(1)
        
        # 3. Relative movement
        print("\n3. Relative movements from home...")
        robot.arm.home()
        time.sleep(1)
        
        print("   Raise arm 30mm")
        robot.arm.raise_arm(30, duration=1.0)
        time.sleep(0.5)
        
        print("   Lower arm 30mm")
        robot.arm.lower_arm(30, duration=1.0)
        time.sleep(0.5)
        
        print("   Extend arm 50mm")
        robot.arm.extend_arm(50, duration=1.0)
        time.sleep(0.5)
        
        print("   Retract arm 50mm")
        robot.arm.retract_arm(50, duration=1.0)
        time.sleep(1)
        
        # 4. Gripper control
        print("\n4. Gripper control...")
        
        print("   Opening gripper")
        robot.arm.open_gripper()
        time.sleep(1)
        
        print("   Closing gripper")
        robot.arm.close_gripper()
        time.sleep(1)
        
        print("   Partial grip (50%)")
        robot.arm.grip(force=0.5)
        time.sleep(1)
        
        print("   Opening gripper")
        robot.arm.open_gripper()
        time.sleep(1)
        
        # 5. Pick and place demo
        print("\n5. Pick and place sequence...")
        
        # Move to pickup position
        print("   Moving to pickup position")
        robot.arm.move_to_named('pickup', duration=1.5)
        time.sleep(0.5)
        
        # Execute pick sequence
        print("   Executing pick sequence")
        robot.arm.pick_sequence(0, 200, 20, approach_height=50)
        time.sleep(1)
        
        # Move to place position
        print("   Moving to place position")
        robot.arm.move_to(80, 180, 100, duration=1.5)
        time.sleep(0.5)
        
        # Execute place sequence
        print("   Executing place sequence")
        robot.arm.place_sequence(80, 180, 30, approach_height=50)
        time.sleep(1)
        
        # 6. Gestures
        print("\n6. Fun gestures...")
        
        print("   Waving...")
        robot.manipulation.wave()
        time.sleep(1)
        
        print("   Dancing...")
        robot.manipulation.dance()
        time.sleep(1)
        
        # Return home
        print("\n   Returning home...")
        robot.arm.home()
        
        print("\nD3 Demo complete!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        robot.arm.rest()


if __name__ == '__main__':
    print("Run via: python pathfinder.py --demo d3_arm_basics")
