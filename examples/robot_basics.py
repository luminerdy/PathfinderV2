#!/usr/bin/env python3
"""
Robot Basics — How to use the Robot class

Shows the new pattern: create ONE robot, pass it around.
No more scattered board/camera/sonar creation in every file.

Run on Buddy:
    cd /home/robot/pathfinder
    python3 examples/robot_basics.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from robot import Robot


def example_status():
    """Check robot status."""
    robot = Robot(enable_camera=False)
    robot.status()
    robot.shutdown()


def example_arm():
    """Cycle through arm poses."""
    with Robot(enable_camera=False, enable_sonar=False) as robot:
        print("Camera forward...")
        robot.arm.camera_forward()
        time.sleep(1)

        print("Say yes...")
        robot.arm.say_yes()
        time.sleep(1)

        print("Say no...")
        robot.arm.say_no()
        time.sleep(1)

        print("Look sad...")
        robot.arm.look_sad()
        time.sleep(1)

        print("Back to forward...")
        robot.arm.look_forward()


def example_drive():
    """Drive a square (1 second each side)."""
    with Robot(enable_camera=False) as robot:
        print("Driving a square...")

        robot.forward(35)
        time.sleep(1)
        robot.stop()
        time.sleep(0.3)

        robot.strafe_right(35)
        time.sleep(1)
        robot.stop()
        time.sleep(0.3)

        robot.backward(35)
        time.sleep(1)
        robot.stop()
        time.sleep(0.3)

        robot.strafe_left(35)
        time.sleep(1)
        robot.stop()

        print("Done!")


def example_camera():
    """Take a photo and check for blocks."""
    with Robot(enable_sonar=False) as robot:
        robot.arm.camera_forward()
        time.sleep(0.5)

        frame = robot.camera.get_frame()
        if frame is not None:
            print("Frame captured: %dx%d" % (frame.shape[1], frame.shape[0]))
            print("Camera calibrated: %s" % robot.camera.calibrated)
            print("Focal length: fx=%.0f fy=%.0f" % (robot.camera.fx, robot.camera.fy))

            # Use with block detection
            from skills.block_detect import BlockDetector
            detector = BlockDetector()
            blocks = detector.detect(frame)
            print("Blocks found: %d" % len(blocks))
            for b in blocks:
                print("  %s at (%d,%d) dist=%.0fmm" % (
                    b.color, b.center_x, b.center_y, b.estimated_distance_mm))
        else:
            print("Camera capture failed!")


def example_compose():
    """
    Compose skills — the whole point of the Robot class.
    
    This is what competition code looks like:
    Create robot once, call skills in sequence.
    """
    with Robot() as robot:
        robot.status()

        # Check battery first
        if not robot.battery_ok:
            print("Battery too low!")
            return

        # Skills would work like this (uncomment to actually run):
        # from skills.bump_grab import bump_grab
        # from skills.strafe_nav import strafe_nav
        #
        # # Grab a block
        # if bump_grab(robot, color='red'):
        #     # Drop into rear bin
        #     robot.arm.backward_drop()
        #
        #     # Navigate to red basket
        #     strafe_nav(robot, tag_id=580)
        #
        #     # Dump
        #     robot.arm.gentle_place()

        print("Composition example (dry run) complete!")


if __name__ == '__main__':
    examples = {
        'status': example_status,
        'arm': example_arm,
        'drive': example_drive,
        'camera': example_camera,
        'compose': example_compose,
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("Robot basics examples:")
        print()
        for name, func in examples.items():
            print("  python3 examples/robot_basics.py %s" % name)
            print("    %s" % func.__doc__.strip().split('\n')[0])
            print()
