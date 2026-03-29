# PathfinderV2 - Project Status

**Last Updated:** March 29, 2026 (Day 12)
**Status:** 🔧 In Development — Competition cycle proven, color-matched delivery working, Pi 500 integrated

---

## What's Proven (Tested and Working)

### Autonomous Navigation ✅
- **100% success** on 8-tag tour (578-585, tag36h11)
- Proportional centering with damping (any angle/offset)
- Speed control (fast when far, slow when close)
- Sonar safety (backup from walls, emergency stop at 18cm)
- Re-search recovery (rotates to find lost tags)
- 360° sonar scan (field mapping, wall detection)
- Calibrated 90° turns (0.87s at power 30, verified by sonar)

### Vision ✅
- AprilTag detection with pose estimation (distance in meters, angle in degrees)
- Camera params: fx=500, fy=500, cx=320, cy=240
- Tag size: 254mm (10 inches)
- Red block detection (HSV filtering)
- Real-time processing at 640×480

### Manual Control ✅
- Web interface: live video + drive + arm + battery monitoring
- Adjustable motor power (0-50)
- Save/load arm positions
- Battery safety checks

### Hardware ✅
- Mecanum omnidirectional drive
- 5-DOF arm (Claw=1, Wrist=3, Elbow=4, Shoulder=5, Base=6)
- Sonar (94 Hz sample rate, I2C address 0x77)
- USB camera (640×480 @ 30fps)

---

## What's In Progress

### Block Detection ⚠️
- Red/Blue/Yellow: All working via HSV pipeline (Day 10)
- Confidence scoring filters false positives
- Distance estimation from known block size
- HSV ranges may need tuning per lighting environment

### Competition Routine ⚠️
- Full cycle proven: grab → line follow → gentle place on scoring zone ✅
- Color-matched delivery: block → matching colored basket via AprilTag ✅
- Autonomous approach still inconsistent (~50% from distance)
- Pre-positioned pickup reliable (100%)

---

## What's Not Done

- Reliable autonomous block approach from any distance
- Competition scoring system (automated)
- Gamepad control (Logitech F710)
- Workshop facilitator guide (curriculum wrapper)
- Multi-robot support

---

## Power Analysis (Day 7)

**Battery:** 2× 18650 (7.4V nominal, 8.4V max)

| Voltage | Status | Motors | Pi 5 |
|---------|--------|--------|------|
| >8.2V | Good | Reliable at power 30 | Stable |
| 8.0-8.2V | Marginal | Inconsistent | May throttle |
| 7.5-8.0V | Low | Fail at power 28 | Throttles |
| <7.5V | Critical | All fail | Heavy throttling |

**Key finding:** Pi 5 requires 5V/5A (25W), 67% more than Pi 4. The voltage regulator struggles under combined Pi + motor load at <8.2V.

**Decision (Day 9):** Pi 4 is the competition platform. Works reliably at 7.0V+ with no throttling. Same code runs on both via `lib/board.py` auto-detection.

**Runtime:** 30-45 minutes per charge

---

## Calibration Data

### Rotation (Power 30, Battery >8.2V)
- Rate: 103 deg/sec
- 90° turn: 0.87 seconds
- Minimum power: 30 (below 25: friction wins)

### Navigation Parameters
- TARGET_AREA: 25,000 px² (~50cm stop distance)
- MIN_AREA: 2,000 px² (minimum detection)
- DRIVE_SPEED: 28 (far), 24 (medium), 20 (close)
- SEARCH_SPEED: 28
- CENTER_TOLERANCE: 80 px (±80 from frame center)
- SONAR_STOP: 18cm (emergency)

---

## Development Timeline

| Day | Date | Milestone |
|-----|------|-----------|
| 0 | Mar 18 | Framework created |
| 1 | Mar 19 | Hardware testing |
| 2 | Mar 20 | Motor breakthrough (UART0) |
| 3 | Mar 21 | Servo breakthrough (1-based indexing) |
| 4 | Mar 22 | Navigation + sonar fix |
| 5 | Mar 23 PM | Tag migration, 5/5 navigation tests |
| 6 | Mar 23 EVE | 8-tag field, pose estimation, 87% tour |
| 7 | Mar 24 | Centering skill, 100% tour, power analysis, web control |
| 8 | Mar 25 | Block approach development |
| 9 | Mar 26 | Pi 4 driver, platform auto-detect, power pivot |
| 10 | Mar 27 | Mission control, 9 workshop skills, line following |
| 11 | Mar 28 | First competition score, bump-grab, gentle place |
| 12 | Mar 29 | Color-matched basket delivery, Pi 500 integration |

**130+ commits** across 12 days.

---

## Critical Path to Competition-Ready

1. ✅ Navigate reliably (100% tag tour)
2. ✅ Drive to block (visual servoing with target lock)
3. ✅ Pick up block (bump-grab from sweet spot, 3-phase autonomous)
4. ✅ Follow line to zone (lime green tape, weighted scan, curves)
5. ✅ Deliver to zone (gentle place — lower arm, release at floor)
6. ✅ Color-matched delivery (block → matching colored basket via AprilTag)
7. → Reliable autonomous approach from any distance
