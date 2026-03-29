# PathfinderV2

**Status: 🔧 IN DEVELOPMENT**  
**Latest Update:** March 27, 2026 (Day 10)

A Python framework for educational mobile robots with mecanum drive and robotic arms, running on Raspberry Pi 4 or Pi 5.

Built for STEM workshops, hands-on robotics learning, and autonomous competition scenarios.

## How It Works

PathfinderV2 uses two devices:

| Device | Role | What It Does |
|--------|------|-------------|
| **Pi 500** | Control Hub | Write code, run scripts, monitor camera, debug |
| **Robot (Pi 4)** | Mobile Platform | Drive, grab blocks, sense environment |

You sit at the Pi 500 and control the robot over SSH/WiFi. The robot runs headless.

## Quick Start

**First time?** Follow the [setup guides](docs/setup/) to image SD cards and connect.

**Already set up?** Connect from your Pi 500:
```bash
# SSH into robot from Pi 500
ssh robot@<ROBOT_IP>

# Check battery first!
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py

# Run the web control interface
python3 web/web_control.py
# Open browser on Pi 500: http://<robot-ip>:8080
```

**New to PathfinderV2?** Start with the [Getting Started Guide](START_HERE.md).

## What Works Today

### ✅ Navigation — Proven
- **100% success** on 8-tag AprilTag tour (tag36h11 family)
- Proportional centering with damping
- Sonar collision avoidance
- Calibrated turns (90° = 0.87s at power 30)

### ✅ Vision — Working
- AprilTag detection with pose estimation
- Block detection (red, blue, yellow via HSV filtering)
- Color space processing (BGR, RGB, HSV, Grayscale)
- Distance estimation from known object size

### ✅ Manipulation — Working
- 5-servo arm control (gripper, wrist, elbow, shoulder, base)
- Action group playback (pre-recorded sequences)
- Autonomous pickup (scan → approach → grab)
- Visual servoing with target lock

### ✅ Line Following — Working
- Lime green tape tracking with weighted scan
- Proportional steering through curves
- End-of-line detection

### ✅ Manual Control — Complete
- Web interface with live video and drive controls
- Servo sliders for arm positioning
- Battery monitoring

### 🔬 Beta (Working, Still Tuning)
- Autonomous pickup (E5 — may need multiple attempts)
- Line following (E6 — speed varies with battery voltage)

### ⚠️ In Progress
- E7: Full competition cycle (chain all skills into one routine)
- Delivery sequence (navigate to zone, release block)
- Workshop facilitator guide
- Competition scoring system

## Workshop Skills

PathfinderV2 includes **9 complete workshop skills**, each with:
- **SKILL.md** — 4 sections (Overview, Quick Start, Implementation, Deep Dive)
- **run_demo.py** — Executable demonstration
- **config.yaml** — Tunable parameters
- **README.md** — Quick reference card

**Dual-purpose design:** Same materials work for students (skip to Quick Start) and engineers (read Deep Dive).

### Hardware Foundation (D-Series)

| Skill | What You Learn | Demo |
|-------|---------------|------|
| [D1: Mecanum Drive](skills/mecanum_drive/) | Omnidirectional movement, 8 patterns | `python3 skills/mecanum_drive/run_demo.py` |
| [D2: Sonar Sensors](skills/sonar_sensors/) | Distance measurement, RGB feedback, obstacle avoidance | `python3 skills/sonar_sensors/run_demo.py` |
| [D3: Robotic Arm](skills/robotic_arm/) | Servo control, action groups, named positions | `python3 skills/robotic_arm/run_demo.py` |
| [D4: Camera Vision](skills/camera_vision/) | Capture, color spaces, HSV thresholding | `python3 skills/camera_vision/run_demo.py` |

### Integration Skills (E-Series)

| Skill | What You Learn | Demo |
|-------|---------------|------|
| [E2: AprilTag Navigation](skills/apriltag_navigation/) | Tag detection, pose estimation, autonomous tour | `python3 skills/apriltag_navigation/run_demo.py` |
| [E3: Block Detection](skills/block_detection/) | HSV pipeline, distance estimation, confidence scoring | `python3 skills/block_detection/run_demo.py` |
| [E4: Visual Servoing](skills/visual_servoing/) | Closed-loop control, target locking, approach | `python3 skills/visual_servoing/run_demo.py` |
| [E5: Autonomous Pickup](skills/autonomous_pickup/) | State machine, camera switching, pick-and-place | `python3 skills/autonomous_pickup/run_demo.py` |
| [E6: Line Following](skills/line_following/) | Weighted scan, proportional steering, curves | `python3 skills/line_following/run_demo.py` |

**Progression:** D1-D4 teach individual subsystems → E2-E6 combine them into autonomous behaviors.

## Architecture

```
PathfinderV2/
├── lib/                   # Core libraries
│   ├── board.py           # Platform auto-detect (Pi 4 I2C / Pi 5 serial)
│   ├── board_pi4.py       # Pi 4 I2C driver
│   ├── i2c_sonar.py       # Sonar sensor driver
│   ├── mecanum_kinematics.py
│   └── movement.py        # Calibrated movement functions
│
├── skills/                # Workshop skills (start here!)
│   ├── mecanum_drive/     # D1: Omnidirectional movement
│   ├── sonar_sensors/     # D2: Distance sensing + RGB
│   ├── robotic_arm/       # D3: Arm control + action groups
│   ├── camera_vision/     # D4: Camera + color processing
│   ├── apriltag_navigation/ # E2: Tag-based navigation
│   ├── block_detection/   # E3: Color block finding
│   ├── visual_servoing/   # E4: Vision-guided approach
│   ├── autonomous_pickup/ # E5: Full pickup cycle
│   ├── line_following/    # E6: Tape line tracking
│   ├── strafe_nav.py      # Mecanum navigation engine
│   ├── block_detect.py    # Block detection engine
│   ├── block_approach.py  # Visual approach with target lock
│   ├── auto_pickup.py     # Autonomous pickup state machine
│   └── centering.py       # Proportional centering controller
│
├── scripts/               # Runnable utilities
│   ├── calibration/       # Motor/rotation calibration
│   ├── navigation/        # Navigation demos and tours
│   ├── testing/           # Hardware tests
│   └── tools/             # Battery, camera, arm tools
│
├── web/                   # Web control interface
│   ├── web_control.py     # Flask server
│   └── templates/         # HTML interface
│
├── demos/                 # Legacy demos (D1-E2)
│
├── sdk/                   # Vendor board communication layer
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
├── START_HERE.md          # Getting started guide
└── PROJECT_STATUS.md      # What works, what doesn't
```

**Note:** `sdk/` contains adapted vendor libraries for board communication (Hiwonder). All `skills/`, `lib/`, and `scripts/` code is original.

## Platform

### Two-Device Setup
- **Pi 500 (Control Hub):** Raspberry Pi 500 keyboard computer — your desk, your code, your monitor
- **Robot (Pi 4):** Mobile platform on the field — motors, arm, camera, sonar
- **Connection:** SSH over WiFi (both devices on same network)
- **Why Pi 4 for robot?** 15W vs Pi 5's 25W — batteries last 2x longer

### Setup Guides
- [A1: Pi 500 OS Build](docs/setup/A1_PI500_OS_BUILD.md) — Image the control hub
- [A2: Robot Pi OS Build](docs/setup/A1_ROBOT_PI_OS_BUILD.md) — Image the robot
- [C1: Pi 500 Setup](docs/setup/C1_PI500_SETUP.md) — Connect monitor, WiFi
- [C2: Connect and Test](docs/setup/C2_CONNECT_AND_TEST.md) — SSH to robot, verify hardware

### Hardware
- **Drive:** Mecanum wheels (omnidirectional — forward, strafe, rotate, diagonal)
- **Arm:** 5 servos (gripper + 4-DOF: base, shoulder, elbow, wrist)
- **Vision:** USB camera (640x480 @ 30fps)
- **Sensors:** Ultrasonic sonar with RGB LED indicators
- **Power:** 2× 18650 batteries (7.4V nominal, 30-45 min runtime)

### Battery Safety
- **Minimum voltage:** 7.0V (Pi 4) or 8.2V (Pi 5)
- **Full charge:** 8.4V
- **Runtime:** 30-45 minutes per charge
- **Motor threshold:** Power 28+ needed to overcome friction

See [Battery Safety](BATTERY_SAFETY.md) for details.

### AprilTag Field
- **Family:** tag36h11
- **Tags:** 578-585 (8 tags, 2 per wall)
- **Size:** 10" × 10" (254mm)
- **Layout:** Clockwise — North, East, South, West

## Workshop Context

**2024:** [AutonomousEdgeRobotics](https://github.com/stemoutreach/AutonomousEdgeRobotics) — Intro workshop (assembly, Python, OpenCV)  
**2025:** PathfinderBot V1 — Team competition (navigation, challenges)  
**2026:** PathfinderV2 — Full autonomous competition (detect, grab, score, line follow)

**Target event:** 6-hour workshop + competition (July 28-29, 2026)  
**Audience:** Mixed — students and professional engineers  

## Development Timeline

| Day | Milestone |
|-----|-----------|
| 0 | Framework built from scratch (3-layer architecture) |
| 1-2 | Hardware bring-up, motor debugging (UART config fix) |
| 3-4 | Servo protocol, first autonomous navigation |
| 5-6 | Pose estimation, 8-tag field, 100% tour success |
| 7-8 | Web control, block detection, competition design |
| 9 | Pi 4 driver, platform auto-detect, power pivot |
| 10 | Mission control architecture, 9 workshop skills, line following |

## Credits

- **PathfinderV2:** Scotty (2026)
- **Previous workshops:** STEM Outreach Initiative (2024-2025)
- **AprilTag:** MIT
- **Development partner:** OpenClaw + Claude

## License

MIT License — Built for education and experimentation.
