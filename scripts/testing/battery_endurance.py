#!/usr/bin/env python3
"""
Battery Endurance Test

Drives robot in endless AprilTag-to-AprilTag navigation loop.
Logs battery voltage, time, and tag visits in real-time.
Runs until battery drops below minimum threshold.

Output: Real-time console + CSV log file for analysis.

Usage:
    python3 scripts/testing/battery_endurance.py

Stop: Ctrl+C (saves final log)
"""

import sys
import os
import cv2
import time
import math
import csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

from lib.board import get_board, PLATFORM

# === CONFIG ===

DRIVE_POWER = 40
ROTATION_POWER = 35
BATTERY_MIN = 7.0          # Stop test below this voltage
BATTERY_WARN = 7.3          # Warning threshold

# Tags to visit in order (cycle through these endlessly)
TAG_SEQUENCE = [578, 579, 580, 581, 580, 579]  # Sweep left to right and back

# Navigation parameters
CENTER_TOL = 80             # Pixels from center to count as "facing"
TARGET_TAG_AREA = 5000      # Tag area to count as "reached" (must drive toward tag, not just see it)
NAV_TIMEOUT = 45            # Seconds max per tag navigation (longer for actual driving)

# Log file
LOG_FILE = "/home/robot/pathfinder/battery_endurance_log.csv"

# === HELPERS ===

def stop(board):
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])


def get_voltage(board):
    """Read battery voltage, retry on glitch."""
    for _ in range(3):
        mv = board.get_battery()
        if mv and 5000 < mv < 20000:
            return mv / 1000.0
        time.sleep(0.3)
    return 0


def detect_tags(frame):
    """Detect AprilTags in frame."""
    try:
        import pupil_apriltags as apriltag
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detector = apriltag.Detector(families='tag36h11')
        return detector.detect(gray)
    except Exception:
        return []


def find_tag(tags, tag_id):
    """Find specific tag in detection list."""
    for t in tags:
        if t.tag_id == tag_id:
            return t
    return None


def tag_area(tag):
    """Calculate tag area from corners."""
    corners = tag.corners
    n = len(corners)
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    return abs(area) / 2


# === NAVIGATE TO TAG ===

def navigate_to_tag(board, camera, target_tag_id, timeout=NAV_TIMEOUT):
    """
    Navigate to a specific AprilTag.
    Returns True if reached, False if timeout/lost.
    """
    FRAME_CENTER = 320
    start = time.time()

    for cycle in range(200):
        if time.time() - start > timeout:
            return False

        stop(board)
        time.sleep(0.05)

        for _ in range(2):
            camera.read()
        ret, frame = camera.read()
        if not ret:
            continue

        tags = detect_tags(frame)
        tag = find_tag(tags, target_tag_id)

        if tag is None:
            # Rotate to search
            board.set_motor_duty([(1, ROTATION_POWER), (2, -ROTATION_POWER),
                                  (3, ROTATION_POWER), (4, -ROTATION_POWER)])
            time.sleep(0.20)
            stop(board)
            time.sleep(0.15)
            continue

        tx = tag.center[0]
        offset = tx - FRAME_CENTER
        area = tag_area(tag)

        # Reached?
        if area >= TARGET_TAG_AREA and abs(offset) < CENTER_TOL:
            stop(board)
            return True

        # Center on tag
        if abs(offset) > CENTER_TOL:
            d = 1 if offset > 0 else -1
            rot_time = min(0.10, abs(offset) / 2000.0)
            rot_time = max(0.04, rot_time)
            board.set_motor_duty([(1, ROTATION_POWER * d), (2, -ROTATION_POWER * d),
                                  (3, ROTATION_POWER * d), (4, -ROTATION_POWER * d)])
            time.sleep(rot_time)
            stop(board)
        else:
            # Drive toward tag — longer bursts to actually cover ground
            board.set_motor_duty([(1, DRIVE_POWER), (2, DRIVE_POWER),
                                  (3, DRIVE_POWER), (4, DRIVE_POWER)])
            time.sleep(0.25)

    stop(board)
    return False


# === MAIN ===

def endurance_test():
    board = get_board()

    # Camera forward
    board.set_servo_position(800, [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)])
    time.sleep(1.5)

    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    time.sleep(1.5)

    # Initial battery
    start_voltage = get_voltage(board)
    start_time = time.time()

    print("=" * 60)
    print("BATTERY ENDURANCE TEST")
    print("=" * 60)
    print("Start voltage: %.2fV" % start_voltage)
    print("Minimum voltage: %.2fV" % BATTERY_MIN)
    print("Tag sequence: %s" % TAG_SEQUENCE)
    print("Log file: %s" % LOG_FILE)
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    print("%-8s %-8s %-6s %-8s %-6s %s" % (
        "Time", "Voltage", "Tag", "Status", "Trips", "Rate"))
    print("-" * 60)

    # CSV log
    with open(LOG_FILE, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp', 'elapsed_sec', 'voltage', 'target_tag',
                         'status', 'total_tags', 'total_trips'])

        tag_index = 0
        total_tags_visited = 0
        total_trips = 0  # Complete sequence cycles

        try:
            while True:
                # Check battery
                voltage = get_voltage(board)
                elapsed = time.time() - start_time
                elapsed_min = elapsed / 60.0

                if voltage > 0 and voltage < BATTERY_MIN:
                    stop(board)
                    status = "BATTERY_LOW"
                    print("%-8s %-8s %-6s %-8s" % (
                        "%.1fm" % elapsed_min, "%.2fV" % voltage, "-", status))
                    writer.writerow([datetime.now().isoformat(), "%.1f" % elapsed,
                                     "%.2f" % voltage, "-", status,
                                     total_tags_visited, total_trips])
                    print()
                    print("BATTERY LOW — TEST COMPLETE")
                    break

                # Current target
                target_tag = TAG_SEQUENCE[tag_index]

                # Navigate
                reached = navigate_to_tag(board, camera, target_tag)

                # Log
                voltage_now = get_voltage(board)
                elapsed = time.time() - start_time
                elapsed_min = elapsed / 60.0
                status = "REACHED" if reached else "TIMEOUT"

                if reached:
                    total_tags_visited += 1

                # Calculate rate
                rate = ""
                if elapsed_min > 0.5 and total_tags_visited > 0:
                    rate = "%.1f tags/min" % (total_tags_visited / elapsed_min)

                print("%-8s %-8s %-6d %-8s %-6d %s" % (
                    "%.1fm" % elapsed_min,
                    "%.2fV" % voltage_now if voltage_now > 0 else "?.??V",
                    target_tag, status, total_tags_visited, rate))

                writer.writerow([datetime.now().isoformat(), "%.1f" % elapsed,
                                 "%.2f" % voltage_now, target_tag, status,
                                 total_tags_visited, total_trips])
                csvfile.flush()

                # Next tag
                if reached:
                    # Back up a bit before turning to next tag
                    board.set_motor_duty([(1, -DRIVE_POWER), (2, -DRIVE_POWER),
                                          (3, -DRIVE_POWER), (4, -DRIVE_POWER)])
                    time.sleep(0.8)
                    stop(board)
                    time.sleep(0.3)

                    tag_index = (tag_index + 1) % len(TAG_SEQUENCE)
                    if tag_index == 0:
                        total_trips += 1
                        print("  --- TRIP %d COMPLETE ---" % total_trips)

        except KeyboardInterrupt:
            stop(board)
            print("\n\nTest stopped by user")

        finally:
            stop(board)
            camera.release()

            # Summary
            elapsed = time.time() - start_time
            end_voltage = get_voltage(board)

            print()
            print("=" * 60)
            print("ENDURANCE TEST SUMMARY")
            print("=" * 60)
            print("Duration:       %.1f minutes" % (elapsed / 60.0))
            print("Start voltage:  %.2fV" % start_voltage)
            print("End voltage:    %.2fV" % (end_voltage if end_voltage > 0 else 0))
            print("Voltage drop:   %.2fV" % (start_voltage - end_voltage if end_voltage > 0 else 0))
            print("Tags visited:   %d" % total_tags_visited)
            print("Full trips:     %d" % total_trips)
            if elapsed > 0:
                print("Rate:           %.1f tags/min" % (total_tags_visited / (elapsed / 60.0)))
            print("Log saved:      %s" % LOG_FILE)
            print("=" * 60)


if __name__ == '__main__':
    try:
        endurance_test()
    except Exception as e:
        print("ERROR: %s" % e)
        import traceback
        traceback.print_exc()
    finally:
        try:
            board = get_board()
            stop(board)
        except:
            pass
