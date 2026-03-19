# Hardware Testing Guide

This guide walks you through testing all robot components to verify proper assembly and connection.

## Prerequisites

- Robot assembled and powered on
- Raspberry Pi connected (SSH or direct)
- Battery charged (>7.0V recommended)
- All servos and motors plugged in

## Quick Start

### 1. Initialize Robot

This sets the arm to starting position and verifies basic connectivity:

```bash
cd /home/robot/code/pathfinder
python3 start_robot.py
```

**Expected behavior:**
- 2 beeps
- Battery voltage displayed
- Arm moves to home position
- Gripper opens
- 2 quick beeps + green LED
- Robot ready!

### 2. Run Full Hardware Test

Comprehensive test of all components:

```bash
cd /home/robot/code/pathfinder
python3 test_hardware.py
```

This runs 7 tests:
1. **Board Connection** - Buzzer, battery, RGB LEDs
2. **Motor Connections** - Each wheel motor individually
3. **Chassis Movement** - Forward, backward, strafe, rotate
4. **Arm Servos** - Each servo tested individually
5. **Arm Positioning** - Inverse kinematics test
6. **Camera** - Capture test frames
7. **Sonar** - Distance readings with LED indicators

## Individual Component Tests

### Test Motors Only

Wheels will spin in order: Front-Left, Front-Right, Rear-Left, Rear-Right

```python
from hardware import Board
import time

board = Board()

# Test each motor
motors = [(1, "FL"), (2, "FR"), (3, "RL"), (4, "RR")]
for motor_id, name in motors:
    print(f"Testing {name}...")
    board.set_motor_duty(motor_id, 30)
    time.sleep(1.5)
    board.set_motor_duty(motor_id, 0)
    time.sleep(0.5)

board.close()
```

**Verify:** Each motor spins in the correct location.

### Test Arm Servos Only

Servos move in order: Gripper, Wrist, Elbow, Shoulder, Base

```python
from hardware import Board
import time

board = Board()

servos = [
    (5, "Gripper"),
    (4, "Wrist"),
    (3, "Elbow"),
    (2, "Shoulder"),
    (1, "Base"),
]

for servo_id, name in servos:
    print(f"Testing {name}...")
    board.set_servo_position(servo_id, 1500, 0.5)  # Center
    time.sleep(0.8)
    board.set_servo_position(servo_id, 1800, 0.5)  # Move
    time.sleep(0.8)
    board.set_servo_position(servo_id, 1500, 0.5)  # Return
    time.sleep(0.5)

board.close()
```

**Verify:** Each servo moves smoothly without binding.

### Test Camera

```python
from hardware import Camera
import time

camera = Camera()
camera.open()

for i in range(10):
    frame = camera.read()
    if frame is not None:
        print(f"Frame {i+1}: {frame.shape}")
    time.sleep(0.2)

camera.close()
```

**Verify:** Frames captured successfully. Use VNC to view actual video.

### Test Sonar

```python
from hardware import Sonar
import time

sonar = Sonar()

for i in range(10):
    dist = sonar.get_distance()
    if dist:
        print(f"Distance: {dist:.1f} cm")
        sonar.set_distance_indicator()
    time.sleep(0.5)

sonar.rgb_off()
sonar.close()
```

**Verify:** 
- Distance readings make sense
- RGB LEDs change color (green=far, yellow=medium, red=close)

## Troubleshooting

### Board not connecting

```bash
# Check serial permissions
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# Reboot required
sudo reboot
```

### Motors not moving

- Check power switch is ON
- Verify battery voltage >6.8V
- Check motor connector polarity
- Verify motor IDs in config.yaml

### Servos not moving

- Check servo power (separate from Pi)
- Verify servo IDs match config.yaml
- Test individual servos with board.set_servo_position()
- Check Deviation.yaml for calibration offsets

### Camera not working

```bash
# List camera devices
v4l2-ctl --list-devices

# Try different device ID
# Edit config.yaml → hardware.camera.device
```

### Arm position incorrect at startup

The arm should look like this at home position:
- Base: centered
- Shoulder: angled up ~45°
- Elbow: slightly bent
- Wrist: level
- Gripper: open

If not, servo calibration may be needed:

```bash
# Edit servo offsets
nano /home/robot/code/pathfinder/Deviation.yaml

# Add offset values (in pulse width units)
# Example:
'1': 0     # Base
'2': 50    # Shoulder (adjust if tilted)
'3': -30   # Elbow
'4': 0     # Wrist
'5': 0     # Gripper
```

## Expected Test Results

### ✓ All Tests Pass

```
PASS - board
PASS - motors  
PASS - chassis
PASS - arm_servos
PASS - arm_ik
PASS - camera
PASS - sonar

Results: 7/7 tests passed

🎉 All tests passed! Robot is ready.
```

### ⚠ Partial Pass

If some tests fail:
1. Note which test failed
2. Check connections for that component
3. Run individual component test
4. Check troubleshooting section above

## Workshop Usage

For PathfinderBot workshops, run tests in this order:

1. **Assembly complete** → `start_robot.py`
2. **Verify connections** → `test_hardware.py` (motors and servos only)
3. **Before challenges** → Quick sonar and camera check
4. **After modifications** → Full test suite

## Next Steps

After hardware tests pass:

- Run workshop demos: `python3 pathfinder.py --demo d1_basic_drive`
- Calibrate camera for manipulation tasks
- Print AprilTags for navigation demos
- Set up course for competition

---

**Note:** All test scripts are non-destructive and safe to run multiple times.
