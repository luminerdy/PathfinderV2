"""
D2 - Sonar Distance Detection
Introduction to ultrasonic sensor and obstacle detection
"""

import time
import logging

logger = logging.getLogger(__name__)


def run(robot):
    """
    D2 Demo: Sonar sensor and obstacle avoidance
    
    Teaches:
    - Distance measurement
    - Obstacle detection
    - RGB indicators
    - Collision avoidance
    """
    logger.info("=== D2: Sonar Demo ===")
    
    if robot.sonar is None:
        print("Error: Sonar not available")
        return
        
    try:
        # 1. Basic distance reading
        print("\n1. Reading distance (10 samples)...")
        for i in range(10):
            dist = robot.sonar.get_distance()
            if dist:
                print(f"   Sample {i+1}: {dist:.1f} cm")
                robot.sonar.set_distance_indicator()
            time.sleep(0.5)
            
        robot.sonar.rgb_off()
        time.sleep(1)
        
        # 2. Filtered distance
        print("\n2. Filtered distance measurement...")
        filtered = robot.sonar.get_filtered_distance(samples=10)
        if filtered:
            print(f"   Median distance: {filtered:.1f} cm")
        time.sleep(1)
        
        # 3. Obstacle detection test
        print("\n3. Obstacle detection test (20cm threshold)...")
        print("   Place hand in front of sensor...")
        for i in range(10):
            if robot.sonar.is_obstacle_detected(threshold=20):
                print(f"   OBSTACLE DETECTED at {robot.sonar.get_distance():.1f} cm!")
                robot.sonar.set_both_rgb((255, 0, 0))  # Red
            else:
                print(f"   Clear ({robot.sonar.get_distance():.1f} cm)")
                robot.sonar.set_both_rgb((0, 255, 0))  # Green
            time.sleep(0.5)
            
        robot.sonar.rgb_off()
        time.sleep(1)
        
        # 4. Motion detection
        print("\n4. Motion detection (wave hand for 2 seconds)...")
        if robot.sonar.detect_motion(threshold=5, duration=2):
            print("   Motion detected!")
        else:
            print("   No motion detected")
        time.sleep(1)
        
        # 5. Move with obstacle avoidance
        print("\n5. Forward movement with obstacle avoidance...")
        print("   Robot will stop if obstacle within 15cm")
        
        robot.movement.obstacle_threshold = 15
        robot.movement.enable_obstacle_avoidance = True
        
        success = robot.movement.move_forward(speed=40, duration=5.0, check_obstacles=True)
        
        if success:
            print("   Movement completed successfully")
        else:
            print("   Movement stopped - obstacle detected!")
            
        time.sleep(1)
        
        # 6. Autonomous exploration
        print("\n6. Autonomous exploration (15 seconds)...")
        print("   Robot will explore and avoid obstacles")
        robot.movement.explore(duration=15.0, speed=40)
        
        print("\nD2 Demo complete!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        robot.chassis.stop()
        robot.sonar.rgb_off()


if __name__ == '__main__':
    print("Run via: python pathfinder.py --demo d2_sonar")
