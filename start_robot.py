#!/usr/bin/env python3
"""
Start Robot - Boot initialization and hardware verification

Usage:
    python3 start_robot.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.board import get_board, PLATFORM
from lib.arm_positions import Arm


def check(label, ok, detail=''):
    mark = 'OK  ' if ok else 'FAIL'
    line = '  [%s] %s' % (mark, label)
    if detail:
        line += ' -- ' + detail
    print(line)
    return ok


def main():
    print()
    print('=' * 50)
    print('  PATHFINDER ROBOT -- STARTUP')
    print('=' * 50)

    passed = 0
    failed = 0

    # --- Board ---
    print('\nBoard')
    try:
        board = get_board()
        check('board', True, PLATFORM)
        passed += 1
    except Exception as e:
        check('board', False, str(e))
        print('\nFATAL: board init failed, cannot continue')
        sys.exit(1)

    # Stop motors immediately on boot
    try:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    except Exception:
        pass

    # --- Battery ---
    print('\nBattery')
    try:
        time.sleep(0.5)
        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            v = mv / 1000.0
            if v >= 7.5:
                detail = '%.2fV -- good' % v
                ok = True
            elif v >= 7.0:
                detail = '%.2fV -- caution' % v
                ok = True
            else:
                detail = '%.2fV -- LOW!' % v
                ok = False
            check('battery', ok, detail)
            if ok:
                passed += 1
            else:
                failed += 1
        else:
            check('battery', False, 'no reading')
            failed += 1
    except Exception as e:
        check('battery', False, str(e))
        failed += 1

    # Startup beep
    try:
        board.set_buzzer(1000, 0.1, 0.1, 1)
    except Exception:
        pass

    # --- Arm ---
    print('\nArm')
    try:
        arm = Arm(board)
        arm.camera_forward()
        arm.gripper_open()
        time.sleep(0.5)
        check('arm', True, 'camera_forward + gripper open')
        passed += 1
    except Exception as e:
        check('arm', False, str(e))
        failed += 1

    # --- Sonar ---
    print('\nSonar')
    sonar = None
    try:
        from lib.sonar import Sonar
        sonar = Sonar()
        d = sonar.get_distance()
        if d is not None:
            check('sonar', True, '%dmm (%.1fcm)' % (d, d / 10.0))
            passed += 1
        else:
            check('sonar', False, 'no distance reading')
            failed += 1
    except Exception as e:
        check('sonar', False, str(e))
        failed += 1

    # --- Camera ---
    print('\nCamera')
    camera = None
    try:
        from lib.camera import Camera
        camera = Camera()
        camera.open()
        frame = camera.get_frame()
        if frame is not None:
            h, w = frame.shape[:2]
            check('camera', True, '%dx%d' % (w, h))
            passed += 1
        else:
            check('camera', False, 'no frame captured')
            failed += 1
    except Exception as e:
        check('camera', False, str(e))
        failed += 1
    finally:
        if camera:
            camera.release()
            camera = None

    # --- Summary ---
    print()
    print('=' * 50)
    all_ok = (failed == 0)
    if all_ok:
        print('  STARTUP COMPLETE -- %d/%d checks passed' % (passed, passed + failed))
    else:
        print('  STARTUP COMPLETE -- %d passed, %d FAILED' % (passed, failed))
    print('=' * 50)
    print()

    # --- Feedback ---
    if all_ok:
        # 2 quick beeps + green LEDs for 5 sec then off
        try:
            board.set_buzzer(1000, 0.1, 0.15, 2)
        except Exception:
            pass
        try:
            if sonar:
                sonar.set_led_color(0, 255, 0)
                time.sleep(5)
                sonar.off()
        except Exception:
            pass
    else:
        # 5 slow beeps + red LEDs stay on -- robot needs attention
        try:
            board.set_buzzer(1000, 0.3, 0.3, 5)
        except Exception:
            pass
        try:
            if sonar:
                sonar.set_led_color(255, 0, 0)
            # LEDs stay on -- no sonar.off()
        except Exception:
            pass


if __name__ == '__main__':
    main()
