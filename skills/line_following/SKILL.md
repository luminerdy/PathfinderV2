# Skill: Line Following (E6)

**Difficulty:** ⭐⭐⭐ (Advanced - Vision + Drive Integration)  
**Type:** Closed-Loop Path Tracking  
**Prerequisites:** D1 (Mecanum Drive), D4 (Camera Vision)  
**Estimated Time:** 25-30 minutes  

---

## Overview

### What This Skill Does

Follow a **lime green tape line** on the floor using camera feedback. The camera sees the line, calculates its position relative to the robot's center, and steers to stay on track. This is **closed-loop path following** — the same concept self-driving cars use.

**What you'll learn:**
- Line detection using HSV color filtering
- Centroid calculation (where is the line?)
- Proportional steering (P-controller)
- Region of interest (ROI) for efficiency
- End-of-line detection (when to stop)
- Intersection handling (optional: which way to turn)

### Real-World Applications

- **Warehouse robots:** Follow painted floor lines between stations
- **Factory AGVs:** Automated Guided Vehicles follow magnetic/optical lines
- **Self-driving cars:** Lane detection and keeping
- **Agricultural robots:** Follow crop rows
- **Hospital delivery:** Robots follow floor paths between departments

### How It Works

```
Camera Frame (pointed down)
    |
    v
Crop to ROI (bottom third of frame — road ahead)
    |
    v
Convert to HSV
    |
    v
Threshold for lime green (create binary mask)
    |
    v
Find centroid of green pixels (center of mass)
    |
    v
Calculate error (centroid vs frame center)
    |
    v
Proportional steering (error * Kp = turn speed)
    |
    v
Mecanum drive (forward + steering correction)
```

### Why Lime Green?

| Color | HSV Hue | Conflict Risk | Floor Contrast |
|-------|---------|---------------|----------------|
| Red tape | 0-10 | Overlaps red blocks! | Good |
| Orange tape | 5-15 | Overlaps red blocks! | Good |
| Blue tape | 100-130 | Overlaps blue blocks! | Good |
| **Lime green** | **45-65** | **None!** | **Excellent** |

Lime green has maximum HSV separation from all three block colors (red, blue, yellow) AND high contrast against a gray floor.

---

## Quick Start

### Step 1: Test Line Detection

```bash
cd /home/robot/pathfinder/skills/line_following
python3 test_line_detect.py
```

**What happens:**
1. Camera captures frame (pointed down)
2. Detects lime green pixels
3. Calculates line centroid
4. Reports position (left/center/right)
5. Saves annotated image

**Before running:**
- Lay lime green tape on the floor in a line or curve
- Position robot so camera can see the tape
- Arm should be in "camera down" position

### Step 2: Run Line Following Demo

```bash
cd /home/robot/pathfinder/skills/line_following
python3 run_demo.py
```

**What happens:**
1. Camera points down (arm repositioned)
2. Detects lime green line
3. Robot drives forward, steering to follow line
4. Stops when line ends or timeout

**SAFETY:** Robot will drive! Clear the path and be ready with Ctrl+C.

### Step 3: Tuning

If robot oscillates (wobbles back and forth):
- Decrease `Kp` in config.yaml (less aggressive steering)

If robot loses the line on curves:
- Increase `Kp` (more aggressive steering)
- Decrease `forward_speed` (slower = more time to react)

---

## Implementation Guide (For Coders)

### Level 2: Use LineFollower Class

```python
from skills.line_following.line_follower import LineFollower

follower = LineFollower()

# Follow until line ends or timeout
result = follower.follow(timeout=30)

if result['success']:
    print('Reached end of line!')
else:
    print('Stopped: %s' % result['reason'])

follower.cleanup()
```

### Level 3: Understand Line Detection

**Step 1: Capture and crop to ROI**
```python
ret, frame = camera.read()

# Only look at bottom third (road immediately ahead)
height = frame.shape[0]  # 480
roi = frame[height * 2 // 3:, :]  # rows 320-480
# This is 160 pixels tall x 640 wide
```

**Why crop?**
- Top of frame = far away (less relevant for steering)
- Bottom = close (what robot needs to steer by NOW)
- Less pixels to process = faster
- Reduces false positives from distant objects

**Step 2: HSV threshold for lime green**
```python
hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

# Lime green tape
lower_green = np.array([40, 100, 100])
upper_green = np.array([75, 255, 255])
mask = cv2.inRange(hsv, lower_green, upper_green)

# Clean up noise
kernel = np.ones((5, 5), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
```

**Step 3: Find centroid (center of mass)**
```python
# Moments give us the centroid
M = cv2.moments(mask)

if M['m00'] > 0:  # m00 = total white pixel area
    cx = int(M['m10'] / M['m00'])  # X centroid
    cy = int(M['m01'] / M['m00'])  # Y centroid
    line_found = True
else:
    line_found = False  # No green pixels = no line
```

**Step 4: Calculate steering error**
```python
frame_center = 320  # 640 / 2

if line_found:
    error = cx - frame_center  # Positive = line is right
    # error = -200 → line far left, steer left
    # error = 0    → line centered, go straight
    # error = +200 → line far right, steer right
```

**Step 5: Proportional control**
```python
Kp = 0.15  # Proportional gain
forward_speed = 25  # Base forward speed

steer = error * Kp  # Steering correction

# Mecanum: forward + rotation
fl = int(forward_speed + steer)
fr = int(forward_speed - steer)
rl = int(forward_speed + steer)
rr = int(forward_speed - steer)

board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])
```

### Level 3: End-of-Line Detection

**How to know when the line ends:**
```python
green_pixels = cv2.countNonZero(mask)
total_pixels = mask.shape[0] * mask.shape[1]
green_ratio = green_pixels / total_pixels

# Thresholds
MIN_LINE_RATIO = 0.01   # Below this = no line visible (0.5% of ROI)

if green_ratio < MIN_LINE_RATIO:
    consecutive_lost += 1
    if consecutive_lost > 10:  # Lost for 10+ frames
        stop()
        return 'line_ended'
else:
    consecutive_lost = 0
```

### Level 4: Advanced Line Following

**Multiple scan lines (better for curves):**
```python
# Instead of one centroid, scan at 3 heights
# Near (bottom), mid, far (top of ROI)
near_row = roi[140:160, :]  # Bottom strip
mid_row = roi[70:90, :]     # Middle strip
far_row = roi[0:20, :]      # Top strip

# Calculate centroid for each strip
near_cx = find_centroid(near_row, mask)
mid_cx = find_centroid(mid_row, mask)
far_cx = find_centroid(far_row, mask)

# Weighted steering: near matters most
error = near_cx * 0.6 + mid_cx * 0.3 + far_cx * 0.1 - frame_center
```

**Intersection detection:**
```python
# If green area suddenly doubles, might be an intersection
if green_ratio > INTERSECTION_THRESHOLD:
    # Multiple line segments detected
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        print('Intersection detected!')
        # Decision: go left, right, or straight
```

---

## Engineering Deep Dive (Advanced)

### PID vs P-Only Control

**P-only (our implementation):**
```
steer = Kp * error

Pros: Simple, fast, easy to tune
Cons: Steady-state error on curves, can oscillate
```

**PD (proportional-derivative):**
```
steer = Kp * error + Kd * (error - prev_error) / dt

Pros: Anticipates curves (derivative = rate of change)
Cons: Amplifies noise (derivative of noisy signal = more noise)
```

**PID (full):**
```
integral += error * dt
steer = Kp * error + Ki * integral + Kd * derivative

Pros: Eliminates steady-state error (integral accumulates bias)
Cons: Integral windup, harder to tune, overkill for simple line following
```

**For line following: P-only is usually enough.** Camera feedback at 30fps provides natural damping. Add D-term only if oscillation is a problem.

### Scan Line Analysis

**Why bottom of frame is most important:**
```
Frame top:     Far away    → Steering info for future
Frame middle:  Medium      → Where robot will be soon
Frame bottom:  Close       → Where robot IS right now

For steering: React to what's close (bottom)
For planning: Look ahead (top) to anticipate curves
```

**Weighted scan lines approximate "look-ahead":**
- Near (60%): Immediate correction
- Mid (30%): Short-term planning
- Far (10%): Curve anticipation

### Lighting Robustness

**Problem:** Indoor lighting varies (fluorescent flicker, shadows, windows)

**HSV advantage:** Hue channel is relatively stable under lighting changes

**Additional robustness:**
```python
# Adaptive thresholding: adjust V range based on frame brightness
avg_brightness = np.mean(frame[:,:,2])  # V channel average

if avg_brightness < 80:  # Dark
    v_min = 60
elif avg_brightness > 200:  # Very bright
    v_min = 150
else:
    v_min = 100  # Normal
```

### Tape vs Painted Lines

**Tape:**
- Consistent color (manufactured)
- Raised surface (shadows at edges)
- Can peel (temporary)
- Easy to reposition

**Paint:**
- May vary in thickness/color
- Flat (no shadow edges)
- Permanent
- Cheaper for large areas

**For workshops: Tape is ideal** (reusable, repositionable, consistent color)

### Speed vs Accuracy Tradeoff

```
Slow (speed=15):
  + Smooth following
  + Handles tight curves
  + More time to process
  - Boring to watch
  - Slow competition time

Fast (speed=40):
  + Exciting to watch
  + Fast competition time
  - Overshoots curves
  - May lose line
  - Needs higher Kp (more aggressive)

Sweet spot: speed=25, Kp=0.15 (tune from here)
```

---

## Configuration

See `config.yaml` for all tunable parameters.

---

## Files

```
line_following/
  SKILL.md              # This file
  run_demo.py           # Follow the line (with safety)
  test_line_detect.py   # Test detection only (no driving)
  line_follower.py      # LineFollower class
  config.yaml           # Tunable parameters
  README.md             # Quick reference
```

---

*Follow the line, stay on track!* 🟢
