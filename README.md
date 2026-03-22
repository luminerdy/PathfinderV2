# Pathfinder Robot Framework

**Status: ✅ WORKSHOP-READY**  
**Latest Update:** March 22, 2026

A complete, tested Python framework for educational mobile robots with mecanum drive and robotic arms, running on **Raspberry Pi 5 8GB**.

Built for STEM education, hands-on robotics workshops, and autonomous competition scenarios.

**🎯 Fully operational with autonomous navigation, vision-guided control, and web interfaces!**

📊 **[VIEW COMPLETE PROJECT STATUS](PROJECT_STATUS.md)** - Detailed accomplishments & capabilities

## Features

### Hardware Abstraction Layer
- **Board**: Servo, motor, LED, buzzer, sensor control
- **Chassis**: Mecanum drive with omnidirectional movement
- **Arm**: 5-DOF arm (base, shoulder, elbow, wrist, gripper) with inverse kinematics
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

### ⚡ Fresh Install?

**Setting up a new robot?** Follow the complete guide:
- 📋 **[Setup Checklist](docs/SETUP_CHECKLIST.md)** - Quick checklist format
- 📖 **[Fresh Install Guide](docs/FRESH_INSTALL.md)** - Detailed step-by-step

### Installation (Existing Pi OS)

```bash
cd /home/robot/code/pathfinder

# Install dependencies
pip3 install -r requirements.txt

# That's it! All SDK components are included locally in lib/
```

**See [INSTALL.md](INSTALL.md) for detailed installation instructions.**

### ⚠️ IMPORTANT: Battery Safety

**ALWAYS check battery voltage before running motors!**

```bash
# Quick check
python3 check_battery.py

# Or in code
python3 -c "from hardware import Board; b = Board(); print(f'{b.get_battery()/1000:.2f}V')"
```

**Voltage Requirements:**
- **Minimum for motors:** 7.5V
- **Fully charged:** 8.4V
- **Below 7.0V:** Charge immediately (risk of brownout during operation)

See [BATTERY_SAFETY.md](BATTERY_SAFETY.md) for details.

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
# Initialize robot (startup sequence)
python3 start_robot.py

# Test all hardware
python3 test_hardware.py

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
├── sdk/                  # Embedded hardware SDK (self-contained)
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
├── start_robot.py        # Startup initialization
├── test_hardware.py      # Hardware test suite
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

- **Mobile robot platform** with servo-driven arm and mecanum wheels
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

See [DEPENDENCIES.md](DEPENDENCIES.md) for complete system requirements and installation guide.  
See `requirements.txt` for Python package list.

## Documentation

### 🚀 Getting Started
- **[Setup Checklist](docs/SETUP_CHECKLIST.md)** - Quick setup reference
- **[Fresh Install Guide](docs/FRESH_INSTALL.md)** - Complete step-by-step for new Pi OS
- **[Installation Guide](INSTALL.md)** - Detailed installation instructions
- **[Testing Guide](TESTING.md)** - Hardware testing procedures

### ⚡ Hardware & Power
- **[Battery Safety](BATTERY_SAFETY.md)** - Voltage requirements, charging, safety
- **[Motor Solution](docs/MOTOR_SOLUTION.md)** - UART configuration fix for motors
- **[Power Requirements](docs/POWER_REQUIREMENTS_ANALYSIS.md)** - Is 2x 18650 enough?
- **[Power Warnings](docs/POWER_WARNING_ANALYSIS.md)** - Under-voltage troubleshooting
- **[Shutdown Analysis](docs/SHUTDOWN_BUG_ANALYSIS.md)** - Brownout protection explained

### 📊 Testing & Results
- **[Testing Results](docs/TESTING_RESULTS.md)** - Verified working configuration
- **[Testing Log](TESTING_LOG.md)** - Hardware test history

### 🔧 Development
- **[Dependencies](DEPENDENCIES.md)** - System requirements and packages
- **[Implementation Checklist](docs/IMPLEMENTATION_CHECKLIST.md)** - Development roadmap

### 📚 Reference
- **[Hardware System Reference](docs/reference/HARDWARE_SYSTEM_REFERENCE.md)** - Complete system analysis
- **[Session Summary](docs/reference/SESSION_SUMMARY_2026-03-20.md)** - Development history

## Troubleshooting

### Motors Don't Work
1. Check battery voltage: `python3 check_battery.py` (must be > 7.5V)
2. Verify UART0 enabled: `ls /dev/ttyAMA0` (should exist)
3. See [Motor Solution Guide](docs/MOTOR_SOLUTION.md)

### Under-Voltage Warnings
1. Charge battery to > 7.5V
2. Use high-discharge 18650 cells (20A+ rating)
3. See [Battery Safety Guide](BATTERY_SAFETY.md)

### Camera Not Working
- Expected if camera not connected (warnings can be ignored)
- If connected: `v4l2-ctl --list-devices`

### More Help
- Check [Fresh Install Guide](docs/FRESH_INSTALL.md) - Troubleshooting section
- Review [Testing Results](docs/TESTING_RESULTS.md) - Verified working config

## License

MIT License - Built for education and experimentation.

## Credits

- **Pathfinder Robot**: Scotty (2026)
- **PathfinderBot Workshop**: STEM Outreach Initiative (2024)
- **YOLOv11**: Ultralytics
- **AprilTag**: MIT

---

**Pathfinder** 🤖 - Navigate. Learn. Build.
