#!/usr/bin/env python3
"""
Hardware Test Suite
Tests all robot components to verify proper connection.

Usage:
    python3 test_hardware.py              # Run all tests
    python3 test_hardware.py --robot      # Use Robot class
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM


def test_board():
    """Test board connection and battery."""
    print("\n" + "=" * 50)
    print("TEST 1: Board Connection")
    print("=" * 50)

    try:
        board = get_board()
        print("  Platform: %s" % PLATFORM)
        time.sleep(1)

        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            print("  Battery: %.2fV" % (mv / 1000.0))
            print("  PASS")
        else:
            print("  Battery reading: %s (unexpected)" % mv)
            print("  WARN")
        return board
    except Exception as e:
        print("  FAIL: %s" % e)
        return None


def test_motors(board):
    """Test each motor briefly."""
    print("\n" + "=" * 50)
    print("TEST 2: Motors")
    print("=" * 50)

    try:
        for motor_id in [1, 2, 3, 4]:
            print("  Motor %d: forward..." % motor_id)
            board.set_motor_duty([(motor_id, 30)])
            time.sleep(0.3)
            board.set_motor_duty([(motor_id, 0)])
            time.sleep(0.2)
        print("  PASS (check if all 4 wheels moved)")
    except Exception as e:
        print("  FAIL: %s" % e)
    finally:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def test_servos(board):
    """Test arm servos."""
    print("\n" + "=" * 50)
    print("TEST 3: Arm Servos")
    print("=" * 50)

    try:
        from lib.arm_positions import Arm
        arm = Arm(board)

        print("  Camera forward...")
        arm.camera_forward()
        time.sleep(0.5)

        print("  Say yes...")
        arm.say_yes()
        time.sleep(0.5)

        print("  Camera forward...")
        arm.camera_forward()

        print("  PASS (check if arm moved)")
    except Exception as e:
        print("  FAIL: %s" % e)


def test_sonar():
    """Test sonar distance sensor."""
    print("\n" + "=" * 50)
    print("TEST 4: Sonar")
    print("=" * 50)

    try:
        from lib.sonar import Sonar
        sonar = Sonar()
        time.sleep(0.3)

        readings = []
        for i in range(5):
            d = sonar.get_distance()
            if d is not None:
                readings.append(d)
                print("  Reading %d: %dmm (%.1fcm)" % (i + 1, d, d / 10.0))
            else:
                print("  Reading %d: None" % (i + 1))
            time.sleep(0.2)

        if readings:
            avg = sum(readings) / len(readings)
            print("  Average: %.0fmm (%.1fcm)" % (avg, avg / 10.0))
            print("  PASS")
        else:
            print("  WARN: No valid readings")

        sonar.off()
    except Exception as e:
        print("  FAIL: %s" % e)


def test_camera():
    """Test camera capture."""
    print("\n" + "=" * 50)
    print("TEST 5: Camera")
    print("=" * 50)

    try:
        from lib.camera import Camera
        cam = Camera()
        cam.open()

        frame = cam.get_frame()
        if frame is not None:
            print("  Frame: %dx%d" % (frame.shape[1], frame.shape[0]))
            print("  Calibrated: %s" % cam.calibrated)
            print("  fx=%.0f fy=%.0f" % (cam.fx, cam.fy))
            print("  PASS")
        else:
            print("  FAIL: No frame captured")

        cam.release()
    except Exception as e:
        print("  FAIL: %s" % e)


def main():
    print("PathfinderV2 Hardware Test Suite")
    print("Platform: %s" % PLATFORM)
    print()

    board = test_board()
    if board is None:
        print("\nBoard connection failed. Cannot continue.")
        sys.exit(1)

    test_motors(board)
    test_servos(board)
    test_sonar()
    test_camera()

    # Stop everything
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])

    print("\n" + "=" * 50)
    print("ALL TESTS COMPLETE")
    print("=" * 50)


if __name__ == '__main__':
    main()
