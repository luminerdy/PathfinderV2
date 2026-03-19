# Pathfinder Quick Reference

## Command Line

```bash
# Run interactive mode
python3 pathfinder.py

# Run a demo
python3 pathfinder.py --demo d1_basic_drive
python3 pathfinder.py --demo d2_sonar
python3 pathfinder.py --demo d3_arm_basics
python3 pathfinder.py --demo e2_apriltag

# Disable components
python3 pathfinder.py --no-camera
python3 pathfinder.py --no-sonar
python3 pathfinder.py --no-monitoring

# Test hardware
python3 test_hardware.py --all
python3 test_hardware.py --board
python3 test_hardware.py --camera
```

## Python API

### Initialize Robot

```python
from pathfinder import Pathfinder

# Standard initialization
robot = Pathfinder()
robot.initialize()

# Context manager (recommended)
with Pathfinder() as robot:
    # Your code here
    pass
```

### Movement

```python
# Basic movement
robot.chassis.forward(speed=50)
robot.chassis.backward(speed=50)
robot.chassis.strafe_right(speed=50)
robot.chassis.strafe_left(speed=50)
robot.chassis.rotate_clockwise(rate=0.5)
robot.chassis.stop()

# Timed movement
robot.movement.move_forward(speed=50, duration=2.0)
robot.movement.rotate(angle=90, speed=0.5)

# Patterns
robot.movement.square(side_length=2.0, speed=50)
robot.movement.circle(duration=5.0, speed=50)

# Obstacle avoidance
robot.movement.explore(duration=30.0, speed=40)
```

### Arm Control

```python
# Named positions
robot.arm.home()
robot.arm.rest()
robot.arm.move_to_named('pickup')

# XYZ movement
robot.arm.move_to(x=0, y=150, z=100, duration=1.0)

# Relative movement
robot.arm.raise_arm(distance=30)
robot.arm.extend_arm(distance=50)

# Gripper
robot.arm.open_gripper()
robot.arm.close_gripper()
robot.arm.grip(force=0.7)

# Pick and place
robot.arm.pick_sequence(x=0, y=200, z=20)
robot.arm.place_sequence(x=80, y=180, z=30)
```

### Vision

```python
# Get frame
frame = robot.camera.read()

# AprilTag detection
tags = robot.vision.detect_apriltags(frame)
tag = robot.vision.find_apriltag(frame, tag_id=0)

# YOLO detection
objects = robot.vision.detect_objects(frame)
block = robot.vision.find_object(frame, 'block')

# Color detection
blob = robot.vision.detect_color(frame, 'red')

# Annotate frame
annotated = robot.vision.annotate_frame(frame)
```

### Manipulation

```python
# Visual pick
robot.manipulation.pick_by_color('red')
robot.manipulation.pick_by_apriltag(tag_id=1)
robot.manipulation.pick_by_yolo('block')

# Transfer
robot.manipulation.transfer_object(
    from_pos=(0, 200, 20),
    to_pos=(80, 180, 30)
)

# Sorting
counts = robot.manipulation.sort_by_color(
    colors=['red', 'blue', 'green'],
    positions={
        'red': (100, 150, 30),
        'blue': (0, 150, 30),
        'green': (-100, 150, 30)
    },
    duration=60.0
)
```

### Sensors

```python
# Direct reading
voltage = robot.board.get_battery_voltage()
distance = robot.sonar.get_distance()

# Monitoring system
state = robot.sensors.get_state()
print(state.battery_voltage)
print(state.distance)

# Callbacks
def low_battery(voltage):
    print(f"Battery low: {voltage}V")

robot.sensors.register_callback('low_battery', low_battery)
```

### Utilities

```python
# Status
robot.status()

# Emergency stop
robot.chassis.stop()
robot.movement.emergency_stop()

# Beep
robot.board.beep(duration=0.1)

# RGB LEDs
robot.board.set_rgb(r=255, g=0, b=0)
robot.sonar.set_both_rgb((0, 255, 0))
```

## Configuration

Edit `config.yaml`:

```yaml
hardware:
  chassis:
    max_speed: 100
  camera:
    width: 640
    height: 480

vision:
  yolo:
    model: "yolov11n.pt"
    confidence: 0.5

safety:
  voltage_min: 6.8
  sonar_emergency_stop: 10
```

## Common Issues

### Board not connecting
```bash
sudo usermod -a -G dialout $USER
sudo reboot
```

### Camera not found
```bash
v4l2-ctl --list-devices
# Update config.yaml device: 0 (or 1, 2)
```

### Slow YOLO inference
Use smaller model: `yolov11n.pt` (nano)
Reduce camera resolution in config

### Import errors
```bash
# Check Hiwonder SDK path
ls /home/pi/MasterPi/masterpi_sdk/
```

## File Locations

| Item | Path |
|------|------|
| Framework | `/home/robot/code/pathfinder/` |
| Main script | `pathfinder.py` |
| Config | `config.yaml` |
| Hardware | `hardware/*.py` |
| Capabilities | `capabilities/*.py` |
| Demos | `demos/*.py` |
| Test script | `test_hardware.py` |

## Workshop Demos

| Demo | Description | Duration |
|------|-------------|----------|
| D1 | Basic Drive | 5 min |
| D2 | Sonar | 5 min |
| D3 | Arm Basics | 10 min |
| E2 | AprilTag | 15 min |

## Safety Thresholds

| Sensor | Warning | Critical |
|--------|---------|----------|
| Battery | 7.0V | 6.8V |
| Distance | 20cm | 10cm |

## Servo IDs

| ID | Component |
|----|-----------|
| 1 | Base rotation |
| 2 | Shoulder |
| 3 | Elbow |
| 4 | Wrist |
| 5 | Gripper |

## Motor IDs

| ID | Location |
|----|----------|
| 1 | Front left |
| 2 | Front right |
| 3 | Rear left |
| 4 | Rear right |

---

**Pathfinder** 🤖 - `/home/robot/code/pathfinder/`
