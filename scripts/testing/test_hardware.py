#!/usr/bin/env python3
"""
Hardware Test Suite
Tests all robot components to verify proper connection
"""

import sys
import time
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from hardware import Board, Chassis, Arm, Camera, Sonar

# Load config
with open(Path(__file__).parent / 'config.yaml', 'r') as f:
    config = yaml.safe_load(f)
hw_config = config['hardware']


def test_board():
    """Test board connection"""
    print("\n" + "="*50)
    print("TEST 1: Board Connection")
    print("="*50)
    
    try:
        board = Board(
            device=hw_config['board']['serial_port'],
            baudrate=hw_config['board']['baud_rate']
        )
        print("OK Board connected successfully")
        
        # Test buzzer
        print("  Testing buzzer...")
        board.beep(0.1)
        time.sleep(0.3)
        board.beep(0.1)
        print("  OK Buzzer working (did you hear 2 beeps?)")
        
        # Test battery voltage
        voltage = board.get_battery_voltage()
        if voltage:
            print(f"  OK Battery voltage: {voltage:.2f}V")
            if voltage < 6.8:
                print("  WARN WARNING: Battery voltage low!")
        else:
            print("  WARN Could not read battery voltage")
            
        # Test RGB LEDs
        print("  Testing RGB LEDs...")
        board.set_rgb(255, 0, 0)  # Red
        time.sleep(0.5)
        board.set_rgb(0, 255, 0)  # Green
        time.sleep(0.5)
        board.set_rgb(0, 0, 255)  # Blue
        time.sleep(0.5)
        board.rgb_off()
        print("  OK RGB LEDs working (did you see red/green/blue?)")
        
        board.close()
        return True
        
    except Exception as e:
        print(f"FAIL Board test failed: {e}")
        return False


def test_motors(board):
    """Test motor connections"""
    print("\n" + "="*50)
    print("TEST 2: Motor Connections")
    print("="*50)
    print("Testing each motor individually...")
    print("Motors will spin in order: Front-Left, Front-Right, Rear-Left, Rear-Right")
    
    try:
        motors = [
            (1, "Front-Left"),
            (2, "Front-Right"),
            (3, "Rear-Left"),
            (4, "Rear-Right")
        ]
        
        for motor_id, name in motors:
            print(f"\n  Testing {name} (Motor {motor_id})...")
            board.set_motor_duty(motor_id, 30)  # 30% forward
            time.sleep(1.5)
            board.set_motor_duty(motor_id, 0)
            time.sleep(0.5)
            
        board.stop_motors()
        print("\nOK All motors tested")
        print("  Verify each motor spun in the correct location")
        return True
        
    except Exception as e:
        print(f"FAIL Motor test failed: {e}")
        board.stop_motors()
        return False


def test_chassis(board):
    """Test chassis movement patterns"""
    print("\n" + "="*50)
    print("TEST 3: Chassis Movement")
    print("="*50)
    print("WARN Place robot on floor before continuing!")
    input("Press Enter when ready...")
    
    try:
        chassis = Chassis(board)
        
        movements = [
            ("Forward", lambda: chassis.forward(40)),
            ("Backward", lambda: chassis.backward(40)),
            ("Strafe Right", lambda: chassis.strafe_right(40)),
            ("Strafe Left", lambda: chassis.strafe_left(40)),
            ("Rotate Clockwise", lambda: chassis.rotate_clockwise(0.4)),
            ("Rotate Counter-clockwise", lambda: chassis.rotate_counterclockwise(0.4)),
        ]
        
        for name, move_func in movements:
            print(f"\n  Testing: {name}")
            move_func()
            time.sleep(2.0)
            chassis.stop()
            time.sleep(1.0)
            
        print("\nOK Chassis movement test complete")
        print("  Verify robot moved correctly in each direction")
        return True
        
    except Exception as e:
        print(f"FAIL Chassis test failed: {e}")
        if 'chassis' in locals():
            chassis.stop()
        return False


def test_arm_servos(board):
    """Test arm servo connections"""
    print("\n" + "="*50)
    print("TEST 4: Arm Servos")
    print("="*50)
    print("Testing each servo individually...")
    
    try:
        # Test servos 1-5 (base, shoulder, elbow, wrist, gripper)
        servos = [
            (5, "Gripper", 1500, 2000),
            (4, "Wrist", 1500, 1800),
            (3, "Elbow", 1500, 1800),
            (2, "Shoulder", 1500, 1800),
            (1, "Base", 1500, 1800),
        ]
        
        for servo_id, name, center, test_pos in servos:
            print(f"\n  Testing {name} (Servo {servo_id})...")
            board.set_servo_position(servo_id, center, 0.5)
            time.sleep(0.8)
            board.set_servo_position(servo_id, test_pos, 0.5)
            time.sleep(0.8)
            board.set_servo_position(servo_id, center, 0.5)
            time.sleep(0.5)
            
        print("\nOK All servos tested")
        print("  Verify each servo moved correctly")
        return True
        
    except Exception as e:
        print(f"FAIL Arm servo test failed: {e}")
        return False


def test_arm_positions():
    """Test arm movement with inverse kinematics"""
    print("\n" + "="*50)
    print("TEST 5: Arm Positioning (IK)")
    print("="*50)
    
    try:
        board = Board()
        arm = Arm(board)
        
        print("  Moving to home position...")
        arm.home(duration=2.0)
        time.sleep(1)
        
        positions = [
            ('rest', 1.5),
            ('forward', 1.5),
            ('up', 1.5),
            ('home', 1.5),
        ]
        
        for pos_name, duration in positions:
            print(f"  Moving to: {pos_name}")
            arm.move_to_named(pos_name, duration=duration)
            time.sleep(1)
            
        print("  Testing gripper...")
        arm.open_gripper()
        time.sleep(1)
        arm.close_gripper()
        time.sleep(1)
        arm.open_gripper()
        time.sleep(0.5)
        
        print("  Returning to rest position...")
        arm.rest()
        
        board.close()
        print("\nOK Arm positioning test complete")
        return True
        
    except Exception as e:
        print(f"FAIL Arm positioning test failed: {e}")
        return False


def test_camera():
    """Test camera connection"""
    print("\n" + "="*50)
    print("TEST 6: Camera")
    print("="*50)
    
    try:
        camera = Camera()
        
        print("  Opening camera...")
        if not camera.open():
            print("FAIL Failed to open camera")
            return False
            
        print("  OK Camera opened")
        
        print("  Capturing test frames...")
        for i in range(5):
            frame = camera.read()
            if frame is None:
                print(f"  WARN Frame {i+1}: Failed to capture")
            else:
                print(f"  OK Frame {i+1}: {frame.shape} captured")
            time.sleep(0.2)
            
        camera.close()
        print("\nOK Camera test complete")
        print("  Note: Use VNC or display to view actual camera feed")
        return True
        
    except Exception as e:
        print(f"FAIL Camera test failed: {e}")
        return False


def test_sonar():
    """Test sonar sensor"""
    print("\n" + "="*50)
    print("TEST 7: Sonar Distance Sensor")
    print("="*50)
    
    try:
        sonar = Sonar()
        
        print("  Taking 10 distance readings...")
        for i in range(10):
            dist = sonar.get_distance()
            if dist:
                print(f"  Reading {i+1}: {dist:.1f} cm")
                sonar.set_distance_indicator()
            else:
                print(f"  Reading {i+1}: No reading")
            time.sleep(0.5)
            
        sonar.rgb_off()
        sonar.close()
        print("\nOK Sonar test complete")
        print("  Verify RGB LEDs changed color based on distance")
        return True
        
    except Exception as e:
        print(f"FAIL Sonar test failed: {e}")
        return False


def main():
    """Run all hardware tests"""
    print("\n" + "="*60)
    print("  PATHFINDER HARDWARE TEST SUITE")
    print("="*60)
    print("\nThis will test all robot hardware components.")
    print("Make sure robot is powered on and connected.\n")
    
    input("Press Enter to start tests...")
    
    results = {}
    
    # Test 1: Board
    results['board'] = test_board()
    
    if results['board']:
        # Keep board open for motor and servo tests
        board = Board()
        
        # Test 2: Motors
        results['motors'] = test_motors(board)
        
        # Test 3: Chassis
        results['chassis'] = test_chassis(board)
        
        # Test 4: Arm Servos
        results['arm_servos'] = test_arm_servos(board)
        
        board.close()
    else:
        results['motors'] = False
        results['chassis'] = False
        results['arm_servos'] = False
        
    # Test 5: Arm IK
    results['arm_ik'] = test_arm_positions()
    
    # Test 6: Camera
    results['camera'] = test_camera()
    
    # Test 7: Sonar
    results['sonar'] = test_sonar()
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "OK PASS" if passed else "FAIL FAIL"
        print(f"{status:8} - {test_name}")
        
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Robot is ready.")
    else:
        print("\nWARN Some tests failed. Check connections and try again.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
