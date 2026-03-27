# PathfinderV2

**Status: 🔧 IN DEVELOPMENT**
**Latest Update:** March 26, 2026

A Python framework for educational mobile robots with mecanum drive and robotic arms, running on Raspberry Pi 4 or Pi 5.

Built for STEM education, hands-on robotics workshops, and autonomous competition scenarios.

## What Works Today

### ✅ Autonomous Navigation — Proven
- **100% success rate** on 8-tag AprilTag tour (tag36h11 family)
- Proportional centering with damping (handles any angle)
- Speed control (adaptive based on distance)
- Sonar safety (collision avoidance)
- Re-search recovery (finds lost tags)
- 360° sonar scan for field mapping
- Calibrated turns (90° = 0.87s at power 30)

### ✅ Vision System — Working
- AprilTag detection with pose estimation (distance, angle)
- Red block detection (HSV color filtering)
- Real-time camera feed (640x480 @ 30fps)

### ✅ Manual Control — Complete
- Web interface with live video, drive controls, servo sliders
- Adjustable motor power
- Save/load arm positions
- Battery monitoring

### ✅ Hardware — Verified
- Mecanum omnidirectional drive
- 5-DOF robotic arm (Claw, Wrist, Elbow, Shoulder, Base)
- Sonar distance sensor
- USB camera

### ⚠️ In Progress
- Block approach (drive to block on floor)
- Automated pickup sequence
- Blue/yellow block detection (HSV tuning needed)

### ❌ Not Yet Implemented
- Full pickup → navigate → deliver cycle
- Competition scoring system
- Gamepad control
- Workshop curriculum

## Quick Start

```bash
cd /home/robot/code/pathfinder
pip3 install -r requirements.txt
```

### Check Battery First!
```bash
python3 scripts/tools/check_battery.py
```

**Battery Requirements:**
- **Pi 4 (competition): >7.0V** for reliable operation
- **Pi 5 (development): >8.2V** (Pi 5 draws more power)
- Below 7.0V: Replace batteries immediately

### Run the Web Control Interface
```bash
python3 web/web_control.py
# Open in browser: http://10.10.10.134:8080
```

### Run the 8-Tag Tour
```bash
python3 scripts/navigation/tour_all_8_tags.py
```

## Architecture

```
pathfinder/
├── lib/                   # Core libraries
│   ├── board.py           # Platform auto-detect (Pi 4 I2C / Pi 5 serial)
│   ├── i2c_sonar.py       # Sonar sensor driver
│   ├── mecanum_kinematics.py
│   ├── arm_inverse_kinematics.py
│   └── movement.py        # Calibrated movement functions
│
├── hardware/              # Hardware abstraction
│   ├── board.py           # Board wrapper
│   ├── chassis.py         # Mecanum drive
│   ├── arm.py             # 5-DOF arm with IK
│   ├── camera.py          # OpenCV capture
│   └── sonar.py           # Ultrasonic sensor
│
├── skills/                # Autonomous behaviors
│   └── centering.py       # Proportional target centering
│
├── scripts/               # Runnable scripts
│   ├── calibration/       # Motor/rotation/arm calibration
│   ├── exploration/       # Sensor exploration
│   ├── navigation/        # Navigation demos and tours
│   ├── testing/           # Hardware and feature tests
│   └── tools/             # Utilities (battery, camera, arm positioning)
│
├── web/                   # Web control interface
│   ├── web_control.py     # Flask server
│   └── templates/         # HTML interface
│
├── demos/                 # Workshop demos (progressive learning)
│   ├── d1_basic_drive.py
│   ├── d2_sonar.py
│   ├── d3_arm_basics.py
│   └── e2_apriltag.py
│
├── sdk/                   # Embedded hardware SDK
│   ├── common/            # Board control, mecanum, sonar
│   └── kinematics/        # Arm inverse kinematics
│
├── docs/                  # Documentation
│   ├── setup/             # Installation guides
│   ├── hardware/          # Hardware reference
│   ├── calibration/       # Calibration results
│   └── reference/         # Technical reference
│
├── config.yaml            # Robot configuration
├── robot_startup.py       # Boot initialization
└── pathfinder.py          # Main entry point
```

## Hardware

### AprilTag Field Setup
- **Family:** tag36h11
- **Tag IDs:** 578-585 (8 tags, 2 per wall)
- **Size:** 10" × 10" (254mm)
- **Layout:** Clockwise — North (578,579), East (580,581), South (582,583), West (584,585)
- **Spacing:** ±12" from wall center

### Servo Mapping
| Servo | Function | Range |
|-------|----------|-------|
| 1 | Claw (Gripper) | 1475 (closed) – 2500 (open) |
| 3 | Wrist | 500 – 2500 |
| 4 | Elbow | 500 – 2500 |
| 5 | Shoulder | 500 – 2500 |
| 6 | Base (rotation) | 500 – 2500 (1500 = center) |

Note: Servo 2 does not exist on this platform.

### Power Requirements
- **Battery:** 2× 18650 (3.7V nominal, 8.4V fully charged)
- **Minimum voltage:** >7.0V (Pi 4) or >8.2V (Pi 5)
- **Pi 5 requirement:** 5V / 5A (25W) — 67% more than Pi 4
- **Runtime:** 30-45 minutes per charge
- **Motor minimum power:** 30 (below ~25, static friction wins)

See [Power Requirements](docs/calibration/POWER_REQUIREMENTS.md) for detailed analysis.

## Documentation

### Setup
- [A1: Robot Pi OS Build](docs/setup/A1_ROBOT_PI_OS_BUILD.md) — Complete SD card image creation
- [Installation Guide](INSTALL.md) — Quick install reference
- [Battery Safety](BATTERY_SAFETY.md) — Voltage requirements and charging

### Calibration
- [Movement Calibration](docs/calibration/MOVEMENT_CALIBRATION.md) — Rotation and drive rates
- [Rotation Calibration](docs/calibration/ROTATION_CALIBRATION_RESULTS.md) — Detailed test results
- [Power Requirements](docs/calibration/POWER_REQUIREMENTS.md) — Voltage thresholds

### Reference
- [Hardware System Reference](docs/reference/HARDWARE_SYSTEM_REFERENCE.md) — Complete system analysis

## Competition Context

Designed for 6-hour STEM events:
- 30-45 minute battery cycles
- 8-12 battery swaps per event
- Tasks must fit in 30-minute windows
- Teams build, calibrate, and compete

## Development

**Day 0-4:** Framework, hardware, motor/servo breakthroughs
**Day 5-6:** AprilTag navigation, 8-tag field, smart approach (87% → 100%)
**Day 7:** Centering skill, power analysis, movement calibration, web control
**Day 8+:** Block approach, pickup sequence, competition tasks

74 commits across 8 days of development.

## Credits

- **PathfinderV2:** Scotty (2026)
- **PathfinderBot Workshop:** STEM Outreach Initiative (2024)
- **AprilTag:** MIT

## License

MIT License — Built for education and experimentation.
