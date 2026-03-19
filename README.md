# Pathfinder Robot Framework

A clean, modular Python framework for the **MasterPi** humanoid robot running on **Raspberry Pi 5 8GB**.

Built for STEM education, hands-on robotics workshops, and AI/vision experimentation.

## Features

### Hardware Abstraction Layer
- **Board**: Servo, motor, LED, buzzer, sensor control
- **Chassis**: Mecanum drive with omnidirectional movement
- **Arm**: 4-DOF arm with inverse kinematics and gripper
- **Camera**: OpenCV capture with streaming
- **Sonar**: Ultrasonic distance sensor with RGB indicators

### Capabilities Layer
- **Movement**: High-level navigation, patterns, obstacle avoidance
- **Vision**: AprilTag detection, YOLOv11 object detection, color tracking
- **Manipulation**: Pick-and-place, visual servoing, sorting
- **Sensors**: Centralized monitoring with safety callbacks

### API Layer
- **WebUI**: Rich web dashboard (planned)
- **Gamepad**: Controller support (planned)
- **Streaming**: MJPEG video stream (planned)

## Quick Start

### Installation

```bash
cd /home/robot/code/pathfinder

# Install dependencies
pip3 install -r requirements.txt

# That's it! All SDK components are included locally in sdk/
```

### Basic Usage

```python
from pathfinder import Pathfinder

# Initialize robot
robot = Pathfinder()
robot.initialize()

# Move forward
robot.movement.move_forward(speed=50, duration=2.0)

# Wave
robot.manipulation.wave()

# Check sensors
robot.status()

# Shutdown
robot.shutdown()
```

### Context Manager

```python
from pathfinder import Pathfinder

with Pathfinder() as robot:
    robot.movement.square(side_length=2.0, speed=50)
    robot.arm.wave()
```

### Command Line

```bash
# Run interactive mode
python3 pathfinder.py

# Run a demo
python3 pathfinder.py --demo d1_basic_drive
python3 pathfinder.py --demo d2_sonar
python3 pathfinder.py --demo d3_arm_basics
python3 pathfinder.py --demo e2_apriltag

# Disable components
python3 pathfinder.py --no-camera --no-sonar
```

## Workshop Demos

Progressive learning demos following the PathfinderBot workshop pattern:

### Basic (D-series)
- **D1**: Basic Drive - Mecanum movement patterns
- **D2**: Sonar - Distance sensing and obstacle avoidance
- **D3**: Arm Basics - Positions, IK, gripper control

### Advanced (E-series)
- **E1**: Camera - Video capture and streaming (TODO)
- **E2**: AprilTag - Tag detection and navigation
- **E3**: Arm Advanced - Complex manipulation (TODO)
- **E4**: YOLO Detection - Object recognition (TODO)
- **E5**: Color Sorting - Visual sorting challenge (TODO)

## Architecture

```
pathfinder/
├── hardware/              # Hardware abstraction
│   ├── board.py          # Servo, motor, LED, buzzer control
│   ├── chassis.py        # Mecanum drive
│   ├── arm.py            # Arm with IK
│   ├── camera.py         # Camera capture
│   └── sonar.py          # Ultrasonic sensor
│
├── capabilities/         # High-level behaviors
│   ├── movement.py       # Navigation and patterns
│   ├── vision.py         # AprilTag + YOLO + color tracking
│   ├── manipulation.py   # Pick-and-place operations
│   └── sensors.py        # Sensor monitoring
│
├── sdk/                  # Embedded Hiwonder SDK (self-contained)
│   ├── common/           # Board control, mecanum, sonar
│   └── kinematics/       # Arm inverse kinematics
│
├── api/                  # Control interfaces (TODO)
│   ├── webserver.py      # REST API + WebUI
│   ├── gamepad.py        # Gamepad controller
│   └── streaming.py      # Video streaming
│
├── demos/                # Workshop demos
│   ├── d1_basic_drive.py
│   ├── d2_sonar.py
│   ├── d3_arm_basics.py
│   └── e2_apriltag.py
│
├── pathfinder.py         # Main entry point
├── config.yaml           # Robot configuration
├── Deviation.yaml        # Servo calibration
└── requirements.txt      # Python dependencies
```

## Configuration

Edit `config.yaml` to customize:
- Hardware settings (servos, motors, camera)
- Vision parameters (AprilTag, YOLO)
- Safety thresholds (voltage, distance)
- Movement presets
- Arm positions

## Examples

### Movement

```python
# Basic movement
robot.chassis.forward(speed=50)
robot.chassis.strafe_right(speed=50)
robot.chassis.rotate_clockwise(rate=0.5)

# Patterns
robot.movement.square(side_length=2.0, speed=50)
robot.movement.circle(duration=5.0, speed=50)
robot.movement.figure_eight(duration=10.0, speed=50)

# Obstacle avoidance
robot.movement.explore(duration=30.0, speed=40)
robot.movement.wall_follow(duration=20.0, side='left')
```

### Arm Control

```python
# Named positions
robot.arm.home()
robot.arm.move_to_named('pickup')

# XYZ movement
robot.arm.move_to(x=50, y=150, z=100, duration=1.0)

# Relative movement
robot.arm.raise_arm(30)
robot.arm.extend_arm(50)

# Pick and place
robot.arm.pick_sequence(x=0, y=200, z=20)
robot.arm.place_sequence(x=80, y=180, z=30)
```

### Vision

```python
# AprilTag detection
detections = robot.vision.detect_apriltags(frame)
tag = robot.vision.find_apriltag(frame, tag_id=0)

# YOLO object detection
objects = robot.vision.detect_objects(frame)
block = robot.vision.find_object(frame, 'block')

# Color tracking
red_blob = robot.vision.detect_color(frame, 'red')
```

### Manipulation

```python
# Pick by color
robot.manipulation.pick_by_color('red')

# Pick at AprilTag
robot.manipulation.pick_by_apriltag(tag_id=1)

# Pick by YOLO
robot.manipulation.pick_by_yolo('block')

# Color sorting
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

### Sensor Monitoring

```python
# Get sensor state
state = robot.sensors.get_state()
print(f"Battery: {state.battery_voltage}V")
print(f"Distance: {state.distance}cm")

# Register callbacks
def low_battery_alert(voltage):
    print(f"WARNING: Battery low ({voltage}V)")
    robot.board.beep()

robot.sensors.register_callback('low_battery', low_battery_alert)

# Start monitoring
robot.sensors.start()
```

## Safety Features

- **Voltage monitoring**: Alerts on low battery
- **Obstacle detection**: Automatic stop on collision risk
- **Sensor monitoring**: Continuous health checks
- **Emergency stop**: `robot.chassis.stop()` and `robot.movement.emergency_stop()`

## Development

### Adding a New Demo

```python
# demos/my_demo.py
import logging

logger = logging.getLogger(__name__)

def run(robot):
    """My custom demo"""
    logger.info("=== My Demo ===")
    
    try:
        # Your code here
        robot.movement.move_forward(50, 2.0)
        robot.arm.wave()
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        robot.chassis.stop()
```

Run: `python3 pathfinder.py --demo my_demo`

### Extending Capabilities

Subclass or add methods to capability modules:

```python
# capabilities/movement.py
class MovementController:
    def my_custom_pattern(self):
        # Your pattern here
        pass
```

## Hardware Requirements

- **MasterPi robot** (Hiwonder)
- **Raspberry Pi 5 8GB** (or Pi 4 4GB+)
- **USB Camera** (or Pi Camera via libcamera)
- **Ultrasonic sensor** (HC-SR04 or compatible)
- **Power supply** (7.4V LiPo recommended)

## Dependencies

- Python 3.9+
- OpenCV 4.8+
- Ultralytics YOLOv11
- AprilTag detector (dt-apriltags or pupil-apriltags)
- PyYAML, NumPy, PySerial

See `requirements.txt` for full list.

## License

MIT License - Built for education and experimentation.

## Credits

- **Pathfinder Robot**: Scotty (2026)
- **PathfinderBot Workshop**: STEM Outreach Initiative (2024)
- **MasterPi Platform**: Hiwonder
- **YOLOv11**: Ultralytics
- **AprilTag**: MIT

---

**Pathfinder** 🤖 - Navigate. Learn. Build.
