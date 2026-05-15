# PathfinderV2 — Agent Coding Reference

## Purpose

This document is the primary reference for any agent or LLM writing Python code for the PathfinderV2 robot platform. It covers the Python API, hardware capabilities, proven code patterns, and known constraints.

Read this before writing any robot code. Do not guess at method names, parameters, or values — use what is documented here.

---

## Robot Fleet

| Robot | IP | Platform | OS | Status |
|---|---|---|---|---|
| buddy1 | 10.10.10.142 | Pi 4 4GB | Raspberry Pi OS (Bookworm) | Primary competition robot |
| buddy2 | 10.10.10.127 | Pi 4 | Debian 13.4 Trixie, Python 3.13.5 | Secondary robot |
| Pi500MC | 10.10.10.141 | Pi 500 | Raspberry Pi OS | Mission control (stationary, wall power) |

SSH: `ssh robot@10.10.10.142`

---

## 1. Setup and Entry Point

### Import

```python
from robot import Robot
```

`robot.py` lives at the repository root. Skills live in `skills/`. Libraries live in `lib/`.

### The Robot Context Manager

Always use `Robot` as a context manager. This ensures motors stop and hardware releases cleanly on exit, even if an exception occurs.

```python
with Robot() as robot:
    robot.status()
    robot.forward(35)
    time.sleep(1)
    robot.stop()
# Motors stopped, camera released automatically
```

Never do this — resource leak on crash:

```python
robot = Robot()       # Wrong — no cleanup guarantee
robot.forward(35)
```

### Constructor Parameters

```python
Robot(
    enable_camera=True,      # Open camera on init (default True)
    enable_sonar=True,       # Initialize sonar (default True)
    calibration_path=None    # Path to .npz calibration file (default None)
)
```

Disable hardware you don't need to save startup time and resources:

```python
with Robot(enable_camera=False) as robot:
    # Drive-only code, no camera overhead
```

### Startup Behavior

- Board stabilization: 0.5 second delay on init
- Camera auto-exposure: 1.5 second delay on first open
- Beeps once on successful init

---

## 2. Drive System

### High-Level Methods

```python
robot.forward(power=35)       # Drive forward
robot.backward(power=35)      # Drive backward
robot.rotate_left(power=35)   # Rotate in place, counterclockwise
robot.rotate_right(power=35)  # Rotate in place, clockwise
robot.strafe_left(power=35)   # Slide left (mecanum)
robot.strafe_right(power=35)  # Slide right (mecanum)
robot.stop()                  # Stop all motors immediately
```

### Low-Level Motor Control

```python
robot.drive(fl, fr, rl, rr)
# fl = front-left motor duty (-100 to 100)
# fr = front-right
# rl = rear-left
# rr = rear-right
```

### Tuned Power Values

| Motion | Minimum Reliable | Recommended | Notes |
|---|---|---|---|
| Forward / Backward | ~28 | 35 | Below 28 is inconsistent |
| Rotate | 30 | 35 | |
| Strafe | 30 | 35 | May drift forward/backward |
| Autonomous navigation | 35 | 40 | Use 40 at ~7.8V battery |

### Drive Constraints

- Mecanum wheels allow forward, backward, rotate, and strafe simultaneously
- Strafing drifts slightly forward/backward — use short strafe bursts or correct with vision
- Stopping distance is small but nonzero; stop slightly early for precision placement
- Battery drain below ~7.5V causes motors to slow and behave inconsistently

---

## 3. Arm and Gripper

Access via `robot.arm`.

### Named Poses

```python
robot.arm.camera_forward()    # Default navigation pose — call this before driving
robot.arm.camera_down()       # Tilt camera down for close block inspection
robot.arm.carry()             # Block in gripper, arm raised for driving
robot.arm.look_forward()      # V1 vendor reset pose (slightly different from camera_forward)
```

### Gripper

```python
robot.arm.gripper_open(duration_ms=400)    # Open gripper
robot.arm.gripper_close(duration_ms=400)   # Close gripper on block
```

### Pickup Sequences

```python
robot.arm.pickup_front()    # Reach down, grab block, lift. Robot must be centered on block.
robot.arm.pickup_left()     # Pick up block slightly left of center
robot.arm.pickup_right()    # Pick up block slightly right of center
```

All pickup sequences end with `look_forward()` automatically.

### Drop / Place Sequences

```python
robot.arm.backward_drop()    # Fold arm over chassis, drop into rear-mounted bin (~4 sec)
robot.arm.gentle_place()     # Lower block to floor, open gripper, retract
```

### Low-Level Arm Control

```python
robot.arm.move(position, duration_ms=800)
# position = list of (servo_id, pulse_width) tuples
# Moves all servos in list, waits for completion

robot.arm.move_servo(servo_id, pulse, duration_ms=500)
# Move single servo
# servo_id: 1=gripper, 3=shoulder, 4=elbow, 5=wrist, 6=base_rotate
# pulse: 500-2500 (microseconds)
```

### Expressions

```python
robot.arm.say_yes()     # Nod up and down
robot.arm.say_no()      # Shake side to side
robot.arm.look_sad()    # Arm droops
```

### Arm Constraints

- Camera is mounted on the arm/gripper — the camera moves when the arm moves
- `pickup_front()` requires block to be directly in front and close (~5-10cm)
- `backward_drop()` takes ~4 seconds total — plan timing accordingly
- Side pickup sequences (`pickup_left`, `pickup_right`) have less repeatability than front pickup

---

## 4. Camera

Access via `robot.camera`. Camera is a property — it initializes lazily if `enable_camera=True`.

### Getting Frames

```python
frame = robot.camera.get_frame()
# Returns: OpenCV BGR image (numpy array), or None on failure
# Flushes 3 stale frames before capture to get a fresh image
# Applies lens undistortion if calibration data is loaded

frame = robot.camera.get_raw_frame()
# Faster — no frame flushing, no undistortion
# Use for streaming or when latency matters more than freshness
```

### Camera Properties

```python
robot.camera.is_open()       # bool — True if camera is active
robot.camera.calibrated      # bool — True if .npz calibration loaded
robot.camera.fx              # Focal length X (pixels)
robot.camera.fy              # Focal length Y (pixels)
robot.camera.camera_params   # Tuple: (fx, fy, cx, cy) for AprilTag pose estimation
```

### Default Camera Specs

- Resolution: 640 × 480
- Device: /dev/video0
- Frame center: x=320, y=240

### Camera Constraints

**IMPORTANT: Camera calibration is estimated.** `fx=500` is a hardcoded estimate across all code unless a real `.npz` calibration file is provided. This affects AprilTag distance calculations by roughly 50%. Treat AprilTag distance estimates as approximate until real calibration data is loaded.

- Camera requires stopping the robot for reliable detection — see Stop-Scan-Decide pattern below
- Allow 1.5 seconds after `camera.open()` for auto-exposure to stabilize
- `get_frame()` is slower than `get_raw_frame()` due to the 3-frame flush

---

## 5. Sonar (Ultrasonic Sensor)

Access via `robot.sonar`.

### Getting Distance

```python
distance_mm = robot.sonar.get_distance()
# Returns: distance in millimeters (int), or None on error
# Range: 0–5000mm

distance_cm = robot.sonar.get_distance_cm()
# Returns: distance in centimeters (float), or None on error
```

### LED Control

```python
robot.sonar.set_led_color(r, g, b)          # Set both LEDs to RGB color (0-255)
robot.sonar.set_led_by_distance(dist_mm)    # Auto color: green/yellow/red by zone
robot.sonar.update_leds()                   # Read distance and set LEDs automatically — returns distance
robot.sonar.off()                           # Turn off LEDs
```

### Distance Zones

| Zone | Distance | LED Color |
|---|---|---|
| Safe | > 610mm (24 in) | Green |
| Caution | 305–610mm (12–24 in) | Yellow |
| Danger | 150–305mm (6–12 in) | Red |
| Critical | < 150mm (6 in) | Red |

### Sonar Constraints

- Single readings are noisy — filter before using for decisions (see Sonar Filtering pattern)
- Small objects (foam blocks) may not reflect reliably
- Readings are unreliable during active turning
- `i2cdetect` does NOT show the motor board at 0x7A on buddy2 — this is normal

---

## 6. Battery and Power

```python
voltage = robot.battery         # float voltage (e.g. 7.86), or None
ok = robot.battery_ok           # True if above minimum threshold
```

| Platform | Minimum Voltage | Recommended Swap |
|---|---|---|
| Pi 4 (buddy1, buddy2) | 7.0V | < 7.5V during competition |
| Pi 5 (decommissioned) | 8.1V | — |

**Battery behavior:**

- At 7.0–7.5V: motors begin to slow, behavior becomes inconsistent
- At 7.86V: drive power 40 is required for reliable autonomous navigation
- Estimated runtime: ~80 minutes light use; 7–8 competition matches per charge
- Battery recharge: check with charger — plan ~1 hour per charge cycle

---

## 7. Skills

Skills are higher-level behaviors that accept a `Robot` instance. Import from the `skills/` directory.

### bump_grab — Pick Up a Block

```python
from skills.bump_grab import bump_grab

success = bump_grab(robot, color='red')
# color: 'red', 'blue', 'yellow'
# Returns: True if block grabbed, False if failed

# Also accepts:
success = bump_grab(robot, color='blue')
success = bump_grab(robot, color='yellow')
```

**What it does:** Rotates to find the color, centers the block in frame, drives forward until the block vanishes from camera (= contact), backs up, lowers arm with gripper open, closes gripper, lifts.

**Key insight:** The camera is mounted on the arm. When the robot drives close enough, the block disappears from the camera frame — that disappearance is the contact signal, not a distance measurement.

**Tuned parameters:**
- Drive power: 35
- Rotation power: 35
- Center tolerance: 80 pixels
- Backup time: 0.12 seconds

### StrafeNavigator — Navigate to an AprilTag

```python
from skills.strafe_nav import StrafeNavigator

nav = StrafeNavigator(robot)

# Navigate to a single tag
result = nav.navigate_to_tag(target_id=580)
# result = {'success': bool, 'tag_id': int, 'distance': float, 'reason': str}

# Search by rotating, then navigate
result = nav.search_and_navigate(target_id=580, search_timeout=15, nav_timeout=30)

# Visit multiple tags in sequence
result = nav.tour(tag_sequence=[578, 579, 580])

nav.cleanup()    # Always call cleanup when done
```

**Basket tag mapping:**

| Color | AprilTag ID |
|---|---|
| Blue | 578 |
| Yellow | 579 |
| Red | 580 |

**Tuned parameters:**
- Lateral gain (Kx): 120
- Forward gain (Kz): 100
- Min speed: 28 (motor duty)
- Max speed: 35 (motor duty)
- Target stop distance: 0.55m from tag
- Center tolerance: 0.03m lateral, 0.05m distance

### color_delivery — Deliver Block to Matching Basket

```python
from skills.color_delivery import color_delivery

result = color_delivery(robot, target_color='red')
# target_color: 'red', 'blue', 'yellow'
# Returns: dict with {'success': bool, 'block_color': str, 'basket_tag': int, 'details': str}
```

**What it does:** Navigates to the AprilTag basket that matches the target color, drops block via `backward_drop()`.

### bin_collect — Multi-Block Rear Bin Collection

```python
from skills.bin_collect import bin_collect

count = bin_collect(robot, count=3, color='yellow')
# count: number of blocks to collect
# color: 'red', 'blue', 'yellow', or None for any color
# Returns: number of blocks successfully collected
```

**What it does:** Repeats: bump_grab → backward_drop. Collects multiple blocks into the rear-mounted bin.

### Deprecated Skills — Do Not Use

These files exist in `skills/` but are deprecated and should not be used in new code:

- `auto_pickup.py` — replaced by `bump_grab`
- `block_approach.py` — replaced by `bump_grab`
- `block_pursue.py` — replaced by `bump_grab`

---

## 8. Proven Code Patterns

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
    
    # Move toward area of interest
    robot.forward(35)
    time.sleep(0.5)
    robot.stop()
    
    # Stop — then scan
    time.sleep(0.2)  # Let robot settle
    frame = robot.camera.get_frame()
    
    if frame is not None:
        # process frame and decide
        pass
    
    # Move again based on decision
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
    return readings[len(readings) // 2]  # median

with Robot() as robot:
    dist = get_stable_distance(robot)
    if dist and dist < 200:
        robot.stop()
```

### Pattern 4: Bump-Grab then Navigate to Basket

The core competition sequence — pick up a block, deliver it to the matching basket.

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
        robot.arm.carry()          # Raise arm for safe driving
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
    
    # Collect 3 red blocks into rear bin
    collected = bin_collect(robot, count=3, color='red')
    print(f"Collected {collected} blocks")
    
    # Navigate to red basket and dump
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
    else:
        print("Battery reading unavailable")
```

---

## 9. Operating Envelope (Tested Values)

These are confirmed working values from real robot testing. Use these as starting points.

### Drive

| Parameter | Value | Notes |
|---|---|---|
| Minimum reliable forward power | 28 | Below this is inconsistent |
| Default autonomous power | 35 | Good for most situations |
| Navigation power at low battery | 40 | Required at ~7.8V |
| bump_grab drive power | 35 | Tuned for block approach |
| StrafeNavigator speed range | 28–35 | Motor duty |

### Vision

| Parameter | Value | Notes |
|---|---|---|
| Camera frame center | x=320, y=240 | 640×480 resolution |
| AprilTag drop distance | ~3000 pixel area | Tag fills frame = stop |
| AprilTag center tolerance | 100 pixels | Left/right |
| bump_grab center tolerance | 80 pixels | For block centering |
| Estimated focal length (fx=fy) | 500 | ESTIMATED — not calibrated |
| StrafeNavigator target distance | 0.55m | From tag face |

### Color Detection (HSV Ranges)

| Color | H min | H max | S min | V min | Notes |
|---|---|---|---|---|---|
| Green/line | 35 | 85 | 50 | 50 | Line following |

Run calibration tests for red, blue, yellow under event lighting before the competition.

### Sonar

| Zone | Distance |
|---|---|
| Safe (green) | > 610mm |
| Caution (yellow) | 305–610mm |
| Danger (red) | 150–305mm |
| Critical | < 150mm |

### Timing

| Action | Duration |
|---|---|
| `backward_drop()` | ~4 seconds |
| `pickup_front()` | ~5 seconds |
| Arm pose move (default) | 0.9 seconds (800ms + 0.1s) |
| Camera auto-exposure settle | 1.5 seconds |
| Board stabilization on init | 0.5 seconds |

---

## 10. What Not To Do

| Don't | Do Instead | Why |
|---|---|---|
| `from skills.auto_pickup import auto_pickup` | Use `bump_grab` | Deprecated, unreliable |
| `from skills.block_approach import ...` | Use `bump_grab` | Deprecated |
| `from skills.block_pursue import ...` | Use `bump_grab` | Deprecated |
| `robot = Robot()` without `with` | `with Robot() as robot:` | Resource leak on crash |
| Create `board`, `Camera`, or `Sonar` directly in skill code | Use `robot.board`, `robot.camera`, `robot.sonar` | Single hardware instance — creating a second conflicts |
| Trust a single sonar reading | Collect median of 5 readings | Sonar is noisy |
| Process camera frames while driving | Stop → settle → scan → decide → move | Detection is unreliable in motion |
| Rely on AprilTag distance for precision without calibration | Use tag pixel area as a proxy | fx=500 is estimated, ~50% distance error |
| Use `sys.path.insert()` hacks | Fix imports or use the package properly | 44 files had this — it's being cleaned up |
| Run `i2cdetect` to verify motor board on buddy2 | Use Python battery read test | Motor board at 0x7A does not appear in i2cdetect on buddy2 — this is normal |

---

## 11. Frequently Used Imports

```python
# Core
from robot import Robot
import time

# Skills
from skills.bump_grab import bump_grab
from skills.strafe_nav import StrafeNavigator
from skills.color_delivery import color_delivery
from skills.bin_collect import bin_collect

# Libraries (use via robot instance, not direct import in most cases)
from lib.camera import Camera
from lib.sonar import Sonar
from lib.arm_positions import Arm
```

---

## 12. Known Open Issues

These affect code behavior and should inform decisions when writing new code:

| Issue | Impact | Status |
|---|---|---|
| Camera not calibrated (fx=500 estimated) | AprilTag distance ~50% inaccurate | Open — real .npz from V1 needed |
| `competition.py` uses old `auto_pickup` pattern | Competition routine is not using Robot class | Needs refactor |
| 44 files use `sys.path.insert()` hacks | Import reliability varies by launch directory | Needs `setup.py` fix |
| buddy2 not fully validated with Robot class | May hit hardware differences | Test in progress |

---

## Related Documents

```
robot-capabilities-and-constraints.md    Field testing framework and game design input
README.md                                Project overview (reflects March 2026 state)
INSTALL.md                               Setup and dependency installation
START_HERE.md                            Quick start guide
examples/robot_basics.py                 Working code examples for all hardware
```
