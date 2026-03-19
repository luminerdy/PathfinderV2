#!/usr/bin/env python3
"""
Hardware Test Script
Quick diagnostics for Pathfinder robot components
"""

import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_board():
    """Test board connection and basic functions"""
    print("\n=== Testing Board ===")
    try:
        from hardware import Board
        
        board = Board()
        print("✓ Board connected")
        
        # Test buzzer
        print("  Testing buzzer...")
        board.beep(0.1)
        time.sleep(0.3)
        print("✓ Buzzer working")
        
        # Test battery
        voltage = board.get_battery_voltage()
        if voltage:
            print(f"✓ Battery: {voltage:.2f}V")
        else:
            print("✗ Battery reading failed")
            
        # Test RGB
        print("  Testing RGB LEDs...")
        colors = [(255,0,0), (0,255,0), (0,0,255), (0,0,0)]
        for color in colors:
            board.set_rgb(*color)
            time.sleep(0.3)
        print("✓ RGB LEDs working")
        
        board.close()
        return True
        
    except Exception as e:
        print(f"✗ Board test failed: {e}")
        return False


def test_camera():
    """Test camera capture"""
    print("\n=== Testing Camera ===")
    try:
        from hardware import Camera
        import cv2
        
        cam = Camera()
        cam.open()
        print("✓ Camera opened")
        
        # Capture frames
        print("  Capturing frames...")
        success = 0
        for i in range(5):
            frame = cam.read()
            if frame is not None:
                success += 1
            time.sleep(0.1)
            
        if success >= 3:
            print(f"✓ Camera capturing ({success}/5 frames)")
            
            # Show preview
            print("  Showing preview (press 'q' to close)...")
            for _ in range(50):
                frame = cam.read()
                if frame is not None:
                    cv2.imshow('Camera Test', frame)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
            cv2.destroyAllWindows()
        else:
            print(f"✗ Camera capture unreliable ({success}/5)")
            
        cam.close()
        return success >= 3
        
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False


def test_sonar():
    """Test sonar sensor"""
    print("\n=== Testing Sonar ===")
    try:
        from hardware import Sonar
        
        sonar = Sonar()
        print("✓ Sonar initialized")
        
        # Test distance readings
        print("  Reading distance (10 samples)...")
        readings = []
        for i in range(10):
            dist = sonar.get_distance()
            if dist is not None:
                readings.append(dist)
                print(f"    {i+1}: {dist:.1f} cm")
            else:
                print(f"    {i+1}: No reading")
            time.sleep(0.2)
            
        if len(readings) >= 5:
            avg = sum(readings) / len(readings)
            print(f"✓ Sonar working (avg: {avg:.1f} cm, {len(readings)}/10 readings)")
        else:
            print(f"✗ Sonar unreliable ({len(readings)}/10 readings)")
            
        # Test RGB
        print("  Testing RGB indicators...")
        colors = [(255,0,0), (0,255,0), (0,0,255), (0,0,0)]
        for color in colors:
            sonar.set_both_rgb(color)
            time.sleep(0.3)
        print("✓ RGB indicators working")
        
        sonar.close()
        return len(readings) >= 5
        
    except Exception as e:
        print(f"✗ Sonar test failed: {e}")
        return False


def test_chassis():
    """Test chassis movement"""
    print("\n=== Testing Chassis ===")
    print("WARNING: Robot will move!")
    input("Press Enter to continue or Ctrl+C to skip...")
    
    try:
        from hardware import Board, Chassis
        
        board = Board()
        chassis = Chassis(board)
        print("✓ Chassis initialized")
        
        # Test basic movements
        tests = [
            ("Forward", lambda: chassis.forward(30)),
            ("Backward", lambda: chassis.backward(30)),
            ("Strafe right", lambda: chassis.strafe_right(30)),
            ("Strafe left", lambda: chassis.strafe_left(30)),
            ("Rotate CW", lambda: chassis.rotate_clockwise(0.3)),
            ("Rotate CCW", lambda: chassis.rotate_counterclockwise(0.3)),
        ]
        
        for name, movement in tests:
            print(f"  Testing {name}...")
            movement()
            time.sleep(1.0)
            chassis.stop()
            time.sleep(0.5)
            
        print("✓ Chassis tests complete")
        
        chassis.stop()
        board.close()
        return True
        
    except Exception as e:
        print(f"✗ Chassis test failed: {e}")
        return False


def test_arm():
    """Test arm movement"""
    print("\n=== Testing Arm ===")
    print("WARNING: Arm will move!")
    input("Press Enter to continue or Ctrl+C to skip...")
    
    try:
        from hardware import Board, Arm
        
        board = Board()
        arm = Arm(board)
        print("✓ Arm initialized")
        
        # Test named positions
        positions = ['home', 'rest', 'forward', 'home']
        for pos in positions:
            print(f"  Moving to {pos}...")
            arm.move_to_named(pos, duration=1.5)
            time.sleep(1.0)
            
        # Test gripper
        print("  Testing gripper...")
        arm.open_gripper()
        time.sleep(1.0)
        arm.close_gripper()
        time.sleep(1.0)
        arm.open_gripper()
        time.sleep(0.5)
        
        print("✓ Arm tests complete")
        
        arm.rest()
        board.close()
        return True
        
    except Exception as e:
        print(f"✗ Arm test failed: {e}")
        return False


def test_vision():
    """Test vision system"""
    print("\n=== Testing Vision ===")
    try:
        from hardware import Camera
        from capabilities import VisionSystem
        import yaml
        import cv2
        
        # Load config
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
            
        cam = Camera()
        cam.open()
        
        vision = VisionSystem(cam, config['vision'])
        print("✓ Vision system initialized")
        
        print("\nTesting AprilTag detection...")
        print("  Show AprilTag to camera (press 'q' to continue)...")
        
        detected_any = False
        for _ in range(100):
            frame = cam.read()
            if frame is None:
                continue
                
            tags = vision.detect_apriltags(frame)
            display = vision.draw_apriltags(frame, tags)
            
            if tags:
                detected_any = True
                cv2.putText(display, f"Tags: {len(tags)}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(display, "No tags detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                           
            cv2.imshow('AprilTag Test', display)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
                
        cv2.destroyAllWindows()
        
        if detected_any:
            print("✓ AprilTag detection working")
        else:
            print("⚠ No AprilTags detected (may need tags)")
            
        print("\nTesting YOLO detection...")
        print("  Press 'q' to continue...")
        
        for _ in range(100):
            frame = cam.read()
            if frame is None:
                continue
                
            objects = vision.detect_objects(frame)
            display = vision.draw_objects(frame, objects)
            
            cv2.putText(display, f"Objects: {len(objects)}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                       
            cv2.imshow('YOLO Test', display)
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
                
        cv2.destroyAllWindows()
        print("✓ YOLO detection tested")
        
        cam.close()
        return True
        
    except Exception as e:
        print(f"✗ Vision test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run hardware tests"""
    parser = argparse.ArgumentParser(description='Test Pathfinder hardware')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--board', action='store_true', help='Test board only')
    parser.add_argument('--camera', action='store_true', help='Test camera only')
    parser.add_argument('--sonar', action='store_true', help='Test sonar only')
    parser.add_argument('--chassis', action='store_true', help='Test chassis only')
    parser.add_argument('--arm', action='store_true', help='Test arm only')
    parser.add_argument('--vision', action='store_true', help='Test vision only')
    
    args = parser.parse_args()
    
    # Default to all if nothing specified
    if not any([args.all, args.board, args.camera, args.sonar, 
                args.chassis, args.arm, args.vision]):
        args.all = True
        
    print("="*50)
    print("  Pathfinder Hardware Test")
    print("="*50)
    
    results = {}
    
    try:
        if args.all or args.board:
            results['Board'] = test_board()
            
        if args.all or args.camera:
            results['Camera'] = test_camera()
            
        if args.all or args.sonar:
            results['Sonar'] = test_sonar()
            
        if args.all or args.chassis:
            results['Chassis'] = test_chassis()
            
        if args.all or args.arm:
            results['Arm'] = test_arm()
            
        if args.all or args.vision:
            results['Vision'] = test_vision()
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        
    # Summary
    print("\n" + "="*50)
    print("  Test Summary")
    print("="*50)
    for component, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{component:15} {status}")
    print("="*50)
    
    # Overall result
    if results:
        passed = sum(results.values())
        total = len(results)
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
            return 0
        else:
            print("⚠ Some tests failed - check above for details")
            return 1
    else:
        print("No tests run")
        return 0


if __name__ == '__main__':
    sys.exit(main())
