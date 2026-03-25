#!/usr/bin/env python3
"""
Exploring Sonar for Navigation Safety

I have a working sonar sensor, but I'm not using it during navigation!
Let me figure out how to integrate it for obstacle avoidance and safety.
"""

import time
from hardware.sonar import Sonar
from lib.board_protocol import BoardController

print("="*70)
print("SONAR NAVIGATION EXPLORATION")
print("="*70)
print()
print("I want to understand how sonar can make my navigation safer...")
print()

# Initialize
sonar = Sonar()
board = BoardController()
time.sleep(0.5)

print("Testing sonar readings...")
print("-" * 70)
print()

try:
    # Test 1: Baseline readings
    print("TEST 1: What do I see right now?")
    readings = []
    for i in range(10):
        dist = sonar.get_distance()
        if dist > 0:
            readings.append(dist)
        time.sleep(0.1)
    
    if readings:
        avg_dist = sum(readings) / len(readings)
        min_dist = min(readings)
        max_dist = max(readings)
        
        print(f"  Current readings:")
        print(f"    Average: {avg_dist:.1f} cm")
        print(f"    Range: {min_dist:.1f} - {max_dist:.1f} cm")
        print(f"    Samples: {len(readings)}/10")
        
        if avg_dist < 30:
            print(f"  WARNING:  Something close ahead! ({avg_dist:.1f}cm)")
        elif avg_dist < 50:
            print(f"  WARNING:  Obstacle detected at {avg_dist:.1f}cm")
        else:
            print(f"  OK: Clear ahead ({avg_dist:.1f}cm)")
    else:
        print("  ERROR: No valid readings - sonar may not be working")
    
    print()
    print("-" * 70)
    print()
    
    # Test 2: Drive forward with sonar monitoring
    print("TEST 2: What happens if I drive forward with sonar monitoring?")
    print("  (Simulating navigation with obstacle detection)")
    print()
    
    # Check initial distance
    initial_dist = sonar.get_distance()
    print(f"  Starting distance: {initial_dist:.1f} cm")
    
    if initial_dist < 40:
        print(f"  WARNING:  Too close to start! Need >{40}cm clearance")
        print("  Skipping forward test")
    else:
        print(f"  OK: Safe to test forward movement")
        print()
        print("  Driving forward slowly for 2 seconds...")
        print("  Monitoring sonar for obstacles...")
        print()
        
        # Drive forward with monitoring
        board.set_motor_duty([(1, 25), (2, 25), (3, 25), (4, 25)])
        
        start_time = time.time()
        obstacle_detected = False
        
        while time.time() - start_time < 2.0:
            dist = sonar.get_distance()
            elapsed = time.time() - start_time
            
            if dist > 0:
                print(f"    {elapsed:.1f}s: {dist:.1f} cm", end="")
                
                if dist < 20:
                    print(" WARNING:  STOP! Obstacle <20cm!")
                    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
                    obstacle_detected = True
                    break
                elif dist < 30:
                    print(" WARNING:  Warning: Getting close!")
                else:
                    print(" OK:")
            
            time.sleep(0.2)
        
        # Stop
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        
        final_dist = sonar.get_distance()
        print()
        print(f"  Final distance: {final_dist:.1f} cm")
        
        if obstacle_detected:
            print(f"  Result: OBSTACLE DETECTED - stopped automatically!")
        else:
            print(f"  Result: Completed test safely")
    
    print()
    print("-" * 70)
    print()
    
    # Test 3: What thresholds make sense?
    print("TEST 3: What distance thresholds should I use?")
    print()
    
    current_dist = sonar.get_distance()
    print(f"  Current distance: {current_dist:.1f} cm")
    print()
    print("  Suggested thresholds:")
    print("    <15 cm: EMERGENCY STOP (too close!)")
    print("    <20 cm: STOP (obstacle detected)")
    print("    <30 cm: SLOW DOWN (approaching obstacle)")
    print("    <50 cm: CAUTION (something ahead)")
    print("    >50 cm: SAFE (clear path)")
    print()
    
    if current_dist < 15:
        status = "EMERGENCY - Too close!"
    elif current_dist < 20:
        status = "STOP - Obstacle detected"
    elif current_dist < 30:
        status = "SLOW - Approaching obstacle"
    elif current_dist < 50:
        status = "CAUTION - Something ahead"
    else:
        status = "SAFE - Clear path"
    
    print(f"  My current status: {status}")
    
    print()
    print("="*70)
    print("WHAT I LEARNED:")
    print("="*70)
    print()
    
    print("Sonar capabilities:")
    print("  OK: Can detect obstacles ahead")
    print("  OK: Updates fast enough for navigation (~5Hz)")
    print("  OK: Good range for close obstacles (<1m)")
    print()
    
    print("How I could use it:")
    print("  1. SAFETY: Stop before hitting walls/obstacles")
    print("  2. NAVIGATION: Slow down when approaching objects")
    print("  3. TAG LOSS: Stop if I lose sight of tag + obstacle ahead")
    print("  4. BOUNDARY: Detect field edges")
    print()
    
    print("Integration ideas:")
    print("  - Check sonar during forward movement")
    print("  - Stop if <20cm obstacle detected")
    print("  - Slow down if <30cm")
    print("  - Combine with vision for smarter behavior")
    print()
    
    print("This would make me MUCH safer during autonomous navigation!")
    print()

except KeyboardInterrupt:
    print("\n\nStopped exploration.")
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

finally:
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    print("Motors stopped, exploration complete.")
