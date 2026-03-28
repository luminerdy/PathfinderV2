#!/usr/bin/env python3
"""
Sonar Sensors Demo (Level 1: Just Run It!)

Demonstrates 6 sonar capabilities:
1. Distance Reading (10 samples with RGB feedback)
2. Filtered Reading (median of 10 samples)
3. Obstacle Detection (red if <20cm, green if clear)
4. Range Zones (red/yellow/green for danger/caution/safe)
5. Safe Movement (drives forward, stops if obstacle)
6. Obstacle Avoidance (backs up and turns when blocked)

No code changes needed - just run and watch!

Usage:
    python3 run_demo.py

Safety:
    - Clear 6 feet of space in front of robot
    - Be ready to catch robot if it doesn't stop
    - Press Ctrl+C to emergency stop

Press Ctrl+C to stop at any time.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board
from hardware.sonar import Sonar

def main():
    print("=" * 60)
    print("SONAR SENSORS DEMONSTRATION")
    print("=" * 60)
    print()
    print("This demo shows 6 sonar capabilities.")
    print()
    print("SAFETY:")
    print("  - Clear 6 feet of space in front of robot")
    print("  - Be ready to catch if it doesn't stop")
    print("  - Press Ctrl+C to emergency stop")
    print()
    input("Press Enter to start demo...")
    print()
    
    board = get_board()
    sonar = Sonar()
    
    try:
        # Demo 1: Distance Reading
        print("[1/6] Distance Reading (10 samples)")
        print("  Watch RGB LEDs change color...")
        for i in range(10):
            dist = sonar.get_distance()
            if dist:
                print(f"    Sample {i+1}: {dist:.1f} cm")
                sonar.set_distance_indicator()
            time.sleep(0.5)
        sonar.rgb_off()
        time.sleep(2)
        
        # Demo 2: Filtered Reading
        print("\n[2/6] Filtered Reading (median of 10)")
        filtered = sonar.get_filtered_distance(samples=10)
        if filtered:
            print(f"    Median distance: {filtered:.1f} cm")
        time.sleep(2)
        
        # Demo 3: Obstacle Detection
        print("\n[3/6] Obstacle Detection Test")
        print("  Wave hand in front of sensor...")
        print("  Red LED = obstacle <20cm, Green = clear")
        for i in range(15):
            dist = sonar.get_distance()
            if sonar.is_obstacle_detected(threshold=20):
                print(f"    OBSTACLE at {dist:.1f} cm!" if dist else "    OBSTACLE!")
                sonar.set_both_rgb((255, 0, 0))
            else:
                print(f"    Clear ({dist:.1f} cm)" if dist else "    Clear")
                sonar.set_both_rgb((0, 255, 0))
            time.sleep(0.3)
        sonar.rgb_off()
        time.sleep(2)
        
        # Demo 4: Range Zones
        print("\n[4/6] Range Zones (red/yellow/green)")
        print("  Red (<15cm) = DANGER")
        print("  Yellow (15-30cm) = CAUTION")
        print("  Green (>30cm) = SAFE")
        print("  Move hand to see zones...")
        for i in range(15):
            dist = sonar.get_distance()
            if dist:
                if dist < 15:
                    zone = "DANGER"
                    sonar.set_both_rgb((255, 0, 0))
                elif dist < 30:
                    zone = "CAUTION"
                    sonar.set_both_rgb((255, 255, 0))
                else:
                    zone = "SAFE"
                    sonar.set_both_rgb((0, 255, 0))
                print(f"    {dist:.1f} cm - {zone}")
            time.sleep(0.3)
        sonar.rgb_off()
        time.sleep(2)
        
        # Demo 5: Safe Movement
        print("\n[5/6] Safe Movement Test")
        print("  Robot will drive forward at 35% speed")
        print("  Will STOP if obstacle detected <15cm")
        print("  Try blocking its path...")
        time.sleep(2)
        
        start_time = time.time()
        max_duration = 5.0
        speed = 35
        stop_threshold = 15
        
        while time.time() - start_time < max_duration:
            dist = sonar.get_distance()
            if dist and dist < stop_threshold:
                print(f"    STOPPING! Obstacle at {dist:.1f} cm")
                board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                sonar.set_both_rgb((255, 0, 0))
                break
            else:
                # Drive forward
                board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])
                sonar.set_both_rgb((0, 255, 0))
            time.sleep(0.05)
        
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        sonar.rgb_off()
        time.sleep(2)
        
        # Demo 6: Obstacle Avoidance
        print("\n[6/6] Obstacle Avoidance")
        print("  Robot will explore and avoid obstacles")
        print("  Block its path to see avoidance behavior")
        time.sleep(2)
        
        start_time = time.time()
        max_duration = 10.0
        speed = 30
        
        while time.time() - start_time < max_duration:
            dist = sonar.get_distance()
            
            if dist and dist < 20:
                # Obstacle! Back up and turn
                print(f"    Obstacle at {dist:.1f} cm - backing up...")
                # Back up
                board.set_motor_duty([(1, -30), (2, -30), (3, -30), (4, -30)])
                time.sleep(0.5)
                # Turn right
                print("    Turning right...")
                board.set_motor_duty([(1, 30), (2, -30), (3, 30), (4, -30)])
                time.sleep(0.6)
                board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                time.sleep(0.3)
            else:
                # Clear - drive forward
                board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])
            
            time.sleep(0.05)
        
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        sonar.rgb_off()
        
        print()
        print("=" * 60)
        print("DEMO COMPLETE!")
        print("=" * 60)
        print()
        print("What you just saw:")
        print("  [OK] Distance measurement (ultrasonic echo timing)")
        print("  [OK] RGB feedback (visual distance indicator)")
        print("  [OK] Obstacle detection (threshold logic)")
        print("  [OK] Range zones (danger/caution/safe)")
        print("  [OK] Safe movement (stops before collision)")
        print("  [OK] Avoidance behavior (backs up and turns)")
        print()
        print("Next steps:")
        print("  - Try editing config.yaml to change thresholds")
        print("  - Read SKILL.md to understand how ultrasonic works")
        print("  - Integrate with D1 (mecanum + sonar = safe navigation)")
        
        # Victory beep
        board.set_buzzer(1000, 0.1, 0.1, 2)
    
    except KeyboardInterrupt:
        print("\nDemo stopped by user (Ctrl+C)")
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        sonar.rgb_off()
        print("\nMotors stopped, LEDs off. Demo complete.")

if __name__ == "__main__":
    main()
