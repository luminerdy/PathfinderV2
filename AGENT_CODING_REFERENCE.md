# PathfinderV2 — Agent Coding Reference

> Read this before writing any robot code. Use documented values — do not guess at method names, parameters, or tuned constants.

---

## Fleet

```json
{
  "buddy1":  {"ip": "10.10.10.142", "platform": "Pi 4 4GB", "os": "Raspberry Pi OS Bookworm", "ssh": "ssh robot@10.10.10.142", "role": "primary competition robot"},
  "buddy2":  {"ip": "10.10.10.127", "platform": "Pi 4", "os": "Debian 13.4 Trixie, Python 3.13.5", "role": "secondary robot"},
  "Pi500MC": {"ip": "10.10.10.141", "platform": "Pi 500", "os": "Raspberry Pi OS", "role": "mission control, stationary, wall power"}
}
```

---

## 1. Entry Point

```json
{
  "import": "from robot import Robot",
  "rule": "Always use Robot as a context manager — motors stop and hardware releases on exit, even on exception",
  "constructor": {
    "enable_camera": "bool, default True — set False to save startup time if camera not needed",
    "enable_sonar":  "bool, default True — set False if sonar not needed",
    "calibration_path": "str|None — path to .npz lens calibration file"
  },
  "startup_delays": {
    "board_stabilization": "0.5s on init",
    "camera_autoexposure": "1.5s on first open"
  },
  "success_signal": "beeps once on successful init",
  "avoid": "robot = Robot() without 'with' — no cleanup guarantee on crash"
}
```

```python
# Correct
with Robot() as robot:
    robot.status()
    robot.arm.camera_forward()
    robot.forward(35)
    time.sleep(1)
    robot.stop()

# Wrong — resource leak on crash
robot = Robot()
robot.forward(35)
```

---

## 2. Drive

```json
{
  "methods": {
    "robot.forward(power=35)":      "Drive forward",
    "robot.backward(power=35)":     "Drive backward",
    "robot.rotate_left(power=35)":  "Rotate in place, CCW",
    "robot.rotate_right(power=35)": "Rotate in place, CW",
    "robot.strafe_left(power=35)":  "Slide left (mecanum)",
    "robot.strafe_right(power=35)": "Slide right (mecanum)",
    "robot.stop()":                 "Stop all motors immediately",
    "robot.drive(fl, fr, rl, rr)":  "Low-level: duty cycle -100 to 100 per wheel (front-left, front-right, rear-left, rear-right)"
  },
  "tuned_power": {
    "min_reliable":        28,
    "default_autonomous":  35,
    "low_battery_nav":     40,
    "bump_grab_approach":  35,
    "strafe_nav_range":    "28-35"
  },
  "warnings": [
    "Below power 28 is inconsistent",
    "Strafing drifts forward/backward — use short bursts or correct with vision",
    "Below 7.5V motors slow and behavior degrades — check robot.battery_ok",
    "Stopping distance is nonzero — stop slightly early for precision placement"
  ]
}
```

---

## 3. Arm

Access via `robot.arm`. Camera is mounted on the arm — it moves when the arm moves.

```json
{
  "named_poses": {
    "robot.arm.camera_forward()": "Default navigation pose — call this before driving",
    "robot.arm.camera_down()":    "Tilt camera down for close block inspection",
    "robot.arm.carry()":          "Block in gripper, arm raised for driving",
    "robot.arm.look_forward()":   "V1 vendor reset pose — slightly different from camera_forward"
  },
  "gripper": {
    "robot.arm.gripper_open(duration_ms=400)":  "Open gripper",
    "robot.arm.gripper_close(duration_ms=400)": "Close gripper on block"
  },
  "pickup_sequences": {
    "robot.arm.pickup_front()":  "Reach down, grab, lift — robot must be centered on block, ~5-10cm away",
    "robot.arm.pickup_left()":   "Pick up block slightly left of center",
    "robot.arm.pickup_right()":  "Pick up block slightly right of center",
    "note": "All pickup sequences end with look_forward() automatically"
  },
  "drop_sequences": {
    "robot.arm.backward_drop()": "Fold arm over chassis, drop into rear-mounted bin — ~4 seconds total",
    "robot.arm.gentle_place()":  "Lower block to floor, open gripper, retract"
  },
  "low_level": {
    "robot.arm.move(position, duration_ms=800)":          "Move list of (servo_id, pulse_width) tuples simultaneously",
    "robot.arm.move_servo(servo_id, pulse, duration_ms=500)": "Move single servo",
    "servo_ids": {"1": "gripper", "3": "shoulder", "4": "elbow", "5": "wrist", "6": "base_rotate"},
    "pulse_range_us": "500-2500"
  },
  "expressions": {
    "robot.arm.say_yes()":   "Nod up and down",
    "robot.arm.say_no()":    "Shake side to side",
    "robot.arm.look_sad()":  "Arm droops"
  },
  "warnings": [
    "pickup_left/right have less repeatability than pickup_front",
    "backward_drop() takes ~4 seconds — plan timing accordingly"
  ]
}
```

---

## 4. Camera

Access via `robot.camera`. Initializes lazily when `enable_camera=True`.

```json
{
  "methods": {
    "robot.camera.get_frame()":     "Returns fresh BGR numpy array or None — flushes 3 stale frames, applies undistortion if calibrated. Slower.",
    "robot.camera.get_raw_frame()": "Returns frame without flushing or undistortion — use for streaming or when latency matters",
    "robot.camera.is_open()":       "bool — True if camera is active",
    "robot.camera.calibrated":      "bool — True if .npz calibration is loaded",
    "robot.camera.fx":              "focal length X in pixels",
    "robot.camera.fy":              "focal length Y in pixels",
    "robot.camera.camera_params":   "(fx, fy, cx, cy) tuple for AprilTag pose estimation"
  },
  "specs": {
    "resolution": "640x480",
    "device": "/dev/video0",
    "center": {"x": 320, "y": 240}
  },
  "warnings": [
    "CRITICAL: fx=500 is a hardcoded estimate — AprilTag distance calculations are ~50% inaccurate without a real .npz calibration file",
    "Allow 1.5s after camera open for auto-exposure to stabilize",
    "Detection is unreliable while moving — always use Stop-Scan-Decide pattern (see Patterns section)"
  ]
}
```

---

## 5. Sonar

Access via `robot.sonar`.

```json
{
  "methods": {
    "robot.sonar.get_distance()":              "Returns distance in mm (int) or None — range 0-5000mm",
    "robot.sonar.get_distance_cm()":           "Returns distance in cm (float) or None",
    "robot.sonar.set_led_color(r, g, b)":      "Set both LEDs to RGB color 0-255",
    "robot.sonar.set_led_by_distance(dist_mm)":"Auto-color LEDs by zone",
    "robot.sonar.update_leds()":               "Read distance, set LEDs automatically, return distance",
    "robot.sonar.off()":                       "Turn off LEDs"
  },
  "distance_zones_mm": {
    "safe_green":     "> 610",
    "caution_yellow": "305-610",
    "danger_red":     "150-305",
    "critical_red":   "< 150"
  },
  "warnings": [
    "Single readings are noisy — always use median of 5 samples before acting",
    "Small objects (foam blocks) may not reflect reliably",
    "Readings are unreliable during active turning",
    "i2cdetect does NOT show motor board at 0x7A on buddy2 — this is normal, use Python battery test instead"
  ]
}
```

---

## 6. Battery

```json
{
  "properties": {
    "robot.battery":    "float voltage (e.g. 7.86) or None",
    "robot.battery_ok": "bool — True if above minimum threshold"
  },
  "thresholds": {
    "Pi4_minimum_v":      7.0,
    "recommended_swap_v": 7.5
  },
  "behavior": {
    "7.0-7.5V": "Motors slow, behavior inconsistent",
    "7.86V":    "Drive power 40 required for reliable navigation",
    "runtime_light_min":   80,
    "matches_per_charge":  "7-8",
    "recharge_time_hr":    1
  }
}
```

---

## 7. Skills

### bump_grab — Pick Up a Block

```json
{
  "import":    "from skills.bump_grab import bump_grab",
  "signature": "bump_grab(robot, color) -> bool",
  "params":    {"color": "'red' | 'blue' | 'yellow'"},
  "returns":   "True if block grabbed, False if failed",
  "behavior":  "Rotate to find color → center block in frame → drive forward → block vanishes from camera = contact → backup → lower arm → close gripper → lift",
  "key_insight": "Camera is mounted on the arm. Block disappearing from camera frame is the contact signal — not distance.",
  "tuned": {
    "drive_power":          35,
    "rotation_power":       35,
    "center_tolerance_px":  80,
    "backup_time_s":        0.12
  }
}
```

### StrafeNavigator — Navigate to AprilTag Basket

```json
{
  "import":  "from skills.strafe_nav import StrafeNavigator",
  "init":    "nav = StrafeNavigator(robot)",
  "methods": {
    "nav.navigate_to_tag(target_id)": "Navigate to single tag → {'success': bool, 'tag_id': int, 'distance': float, 'reason': str}",
    "nav.search_and_navigate(target_id, search_timeout=15, nav_timeout=30)": "Rotate to search for tag, then navigate",
    "nav.tour(tag_sequence)":         "Visit multiple tags in sequence, e.g. [578, 579, 580]",
    "nav.cleanup()":                  "Always call when done"
  },
  "basket_tags": {"blue": 578, "yellow": 579, "red": 580},
  "tuned": {
    "lateral_gain_Kx":            120,
    "forward_gain_Kz":            100,
    "min_speed":                  28,
    "max_speed":                  35,
    "target_stop_distance_m":     0.55,
    "center_tolerance_lateral_m": 0.03,
    "center_tolerance_distance_m":0.05
  }
}
```

### color_delivery — Deliver Block to Matching Basket

```json
{
  "import":    "from skills.color_delivery import color_delivery",
  "signature": "color_delivery(robot, target_color) -> dict",
  "params":    {"target_color": "'red' | 'blue' | 'yellow'"},
  "returns":   "{'success': bool, 'block_color': str, 'basket_tag': int, 'details': str}",
  "behavior":  "Navigate to AprilTag basket matching target_color → backward_drop()"
}
```

### bin_collect — Multi-Block Rear Bin Collection

```json
{
  "import":    "from skills.bin_collect import bin_collect",
  "signature": "bin_collect(robot, count, color=None) -> int",
  "params": {
    "count": "number of blocks to collect",
    "color": "'red' | 'blue' | 'yellow' | None (any color)"
  },
  "returns":  "number of blocks successfully collected",
  "behavior": "Repeats: bump_grab → backward_drop"
}
```

### Deprecated — Do Not Use

```json
{
  "deprecated": ["auto_pickup", "block_approach", "block_pursue"],
  "replacement": "bump_grab for all three"
}
```

---

## 8. Patterns

Canonical, tested sequences. Use as-is or adapt.

### Pattern 1: Minimal Working Robot

```python
import time
from robot import Robot

with Robot() as robot:
    robot.status()
    robot.arm.camera_forward()
    robot.forward(35)
    time.sleep(1)
    robot.stop()
```

### Pattern 2: Stop-Scan-Decide

Camera detection is unreliable while moving. Always stop before scanning.

```python
import time
from robot import Robot

with Robot() as robot:
    robot.arm.camera_forward()
    robot.forward(35)
    time.sleep(0.5)
    robot.stop()
    time.sleep(0.2)              # let robot settle
    frame = robot.camera.get_frame()
    if frame is not None:
        pass                     # process frame and decide
```

### Pattern 3: Sonar Filtering

Never trust a single sonar reading for movement decisions.

```python
import time
from robot import Robot

def get_stable_distance(robot, samples=5):
    readings = []
    for _ in range(samples):
        d = robot.sonar.get_distance()
        if d is not None:
            readings.append(d)
        time.sleep(0.05)
    if not readings:
        return None
    readings.sort()
    return readings[len(readings) // 2]

with Robot() as robot:
    dist = get_stable_distance(robot)
    if dist and dist < 200:
        robot.stop()
```

### Pattern 4: Bump-Grab then Navigate to Basket

Core competition sequence — pick up a block, deliver to matching basket.

```python
import time
from robot import Robot
from skills.bump_grab import bump_grab
from skills.strafe_nav import StrafeNavigator

BASKET_TAGS = {'red': 580, 'blue': 578, 'yellow': 579}

with Robot() as robot:
    robot.arm.camera_forward()
    color = 'red'
    if bump_grab(robot, color=color):
        robot.arm.carry()
        time.sleep(0.5)
        nav = StrafeNavigator(robot)
        result = nav.navigate_to_tag(target_id=BASKET_TAGS[color])
        if result['success']:
            robot.arm.backward_drop()
        nav.cleanup()
```

### Pattern 5: Multi-Block Collection

```python
import time
from robot import Robot
from skills.bin_collect import bin_collect
from skills.strafe_nav import StrafeNavigator

with Robot() as robot:
    robot.arm.camera_forward()
    collected = bin_collect(robot, count=3, color='red')
    nav = StrafeNavigator(robot)
    result = nav.navigate_to_tag(target_id=580)
    if result['success']:
        robot.arm.backward_drop()
    nav.cleanup()
```

### Pattern 6: Battery Check Before Competition

```python
from robot import Robot

with Robot(enable_camera=False, enable_sonar=False) as robot:
    v = robot.battery
    if v:
        print(f"Battery: {v:.2f}V")
        if not robot.battery_ok:
            print("WARNING: Battery too low — swap before competing")
```

---

## 9. Operating Envelope

```json
{
  "drive_power": {
    "min_reliable":       28,
    "default":            35,
    "low_battery":        40,
    "bump_grab":          35,
    "strafe_nav":         "28-35"
  },
  "vision": {
    "frame_center":                 {"x": 320, "y": 240},
    "apriltag_drop_area_px":        3000,
    "apriltag_center_tolerance_px": 100,
    "bump_grab_center_tolerance_px":80,
    "focal_length_fx_fy_ESTIMATED": 500,
    "strafe_nav_stop_distance_m":   0.55,
    "NOTE": "fx=500 is ESTIMATED — AprilTag distance ~50% inaccurate without real .npz calibration"
  },
  "color_hsv": {
    "green_line": {"h": [35, 85], "s_min": 50, "v_min": 50},
    "NOTE": "Calibrate red/blue/yellow under event lighting before competition"
  },
  "sonar_zones_mm": {
    "safe":     "> 610",
    "caution":  "305-610",
    "danger":   "150-305",
    "critical": "< 150"
  },
  "timing_seconds": {
    "backward_drop":             4.0,
    "pickup_front":              5.0,
    "arm_pose_move_default":     0.9,
    "camera_autoexposure_settle":1.5,
    "board_stabilization":       0.5
  },
  "basket_tags": {"blue": 578, "yellow": 579, "red": 580},
  "battery": {
    "min_voltage_v":      7.0,
    "swap_threshold_v":   7.5,
    "runtime_light_min":  80,
    "matches_per_charge": "7-8"
  }
}
```

---

## 10. Do Not

| Don't | Do Instead | Why |
|---|---|---|
| `from skills.auto_pickup import ...` | `bump_grab` | Deprecated |
| `from skills.block_approach import ...` | `bump_grab` | Deprecated |
| `from skills.block_pursue import ...` | `bump_grab` | Deprecated |
| `robot = Robot()` without `with` | `with Robot() as robot:` | Resource leak on crash |
| Create `Camera`, `Sonar`, `board` directly | `robot.camera`, `robot.sonar`, `robot.board` | Second hardware instance conflicts with first |
| Trust a single sonar reading | Median of 5 readings | Noisy sensor |
| Process frames while driving | Stop → settle → scan → decide → move | Detection unreliable in motion |
| Use AprilTag distance for precision | Use pixel area as proxy | fx=500 estimate = ~50% distance error |
| Use `sys.path.insert()` hacks | Fix imports properly | 44 files had this — being cleaned up |
| Run `i2cdetect` to verify motor board on buddy2 | Use Python battery read test | 0x7A does not appear in i2cdetect on buddy2 — normal |

---

## 11. Imports

```python
from robot import Robot
import time

from skills.bump_grab import bump_grab
from skills.strafe_nav import StrafeNavigator
from skills.color_delivery import color_delivery
from skills.bin_collect import bin_collect
```

---

## 12. Open Issues

| Issue | Impact | Status |
|---|---|---|
| Camera not calibrated (fx=500 estimated) | AprilTag distance ~50% inaccurate | Open — real .npz from V1 needed |
| `competition.py` uses old `auto_pickup` | Not using Robot class | Needs refactor |
| 44 files use `sys.path.insert()` hacks | Import reliability varies by launch directory | Needs setup.py fix |
| buddy2 not fully validated with Robot class | May hit hardware differences | Test in progress |

---

## Related

```
robot-capabilities-and-constraints.md    Field testing framework and game design input
README.md                                Project overview
INSTALL.md                               Setup and dependencies
START_HERE.md                            Quick start
examples/robot_basics.py                 Working hardware examples
```
