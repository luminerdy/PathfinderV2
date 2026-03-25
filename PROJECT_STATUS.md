# PathfinderV2 - Project Status

**Last Updated:** March 25, 2026 (Day 8)
**Status:** 🔧 In Development — Navigation proven, pickup next

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

### Block Approach ⚠️
- Manual block pickup achieved (Day 7 evening via web control)
- Automated sequence not yet developed
- Camera-down angle needed for floor block tracking
- Blocks too low for sonar — vision only

### Block Detection ⚠️
- Red: Working
- Blue/Yellow: HSV tuning needed

---

## What's Not Done

- Full pickup → navigate → deliver cycle
- Competition scoring system
- Gamepad control
- Workshop curriculum
- Blue/yellow block detection

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

**74 commits** across 8 days.

---

## Critical Path to Competition-Ready

1. ✅ Navigate reliably (100% tag tour)
2. → Drive to block (center and approach)
3. → Pick up block (reliable grip sequence)
4. → Deliver to zone (navigate with block)
5. → Repeat within 30-min battery window
