# Skill: Visual Servoing (E4)

**Difficulty:** ⭐⭐⭐ (Advanced - Control + Vision Integration)  
**Type:** Closed-Loop Vision-Guided Motion  
**Prerequisites:** D1 (Mecanum Drive), D4 (Camera), E3 (Block Detection)  
**Estimated Time:** 25-30 minutes  

---

## Overview

### What This Skill Does

**Drive the robot toward a target using real-time camera feedback.** The camera sees the target, calculates error, and adjusts motor speed continuously. This is **closed-loop control** — the robot corrects itself as it moves.

**What you'll learn:**
- Visual servoing concept (camera-in-the-loop control)
- Proportional control (P-controller for centering)
- Target locking (track one specific object)
- Error calculation (pixel offset → motor command)
- Approach strategies (center first, then advance)

### Real-World Applications

- **Self-driving cars:** Lane following, obstacle avoidance
- **Drones:** Landing on a target pad
- **Industrial robots:** Conveyor belt tracking
- **Mars rovers:** Visual navigation to rock samples
- **Warehouse robots:** Navigate to specific shelf location

### Open-Loop vs Closed-Loop

**Open-loop (D1 Mecanum Drive):**
```
Command → Motors → Hope for the best
"Drive forward 2 seconds" — no correction if drifting
```

**Closed-loop (Visual Servoing):**
```
Command → Motors → Camera sees result → Correct → Repeat
"Drive toward red block" — continuously adjusts to stay on target
```

**Why closed-loop is better:**
- Handles wheel slip, uneven floors, battery changes
- Adapts to moving targets
- Self-correcting (errors don't accumulate)
- Works without precise calibration

---

## Quick Start

### Step 1: Block Approach Demo

```bash
cd /home/robot/pathfinder
python3 skills/block_approach.py
```

**What happens:**
1. Camera detects nearest block
2. **Locks onto target** (won't switch to different block mid-approach)
3. Strafes to center block in frame (left/right)
4. Drives forward until block is close (bottom of frame)
5. Stops when block is at pickup distance

**Place a colored block 30-80cm in front of robot before running!**

### Step 2: Centering Demo

```bash
cd /home/robot/pathfinder
python3 -c "
from skills.centering import CenteringController
from skills.block_detect import BlockDetector
from lib.board import get_board
import cv2, time

board = get_board()
camera = cv2.VideoCapture(0)
time.sleep(1.5)

detector = BlockDetector()
centering = CenteringController(board)

ret, frame = camera.read()
blocks = detector.detect(frame)

if blocks:
    b = blocks[0]
    print('%s block at x=%d (offset=%+dpx)' % (b.color, b.center_x, b.offset_from_center))
    centering.center_on_block(b.center_x, verbose=True)
else:
    print('No blocks detected')

camera.release()
"
```

**What happens:**
- Detects nearest block
- Calculates pixel offset from center
- Rotates robot to center the block in frame

### Step 3: Watch the Control Loop

Run approach with verbose callback:
```bash
cd /home/robot/pathfinder
python3 -c "
from skills.block_approach import BlockApproach

def callback(block, action):
    print('  %s at (%d,%d) %dcm - %s' % (
        block.color, block.center_x, block.center_y,
        block.estimated_distance_mm/10, action))

ba = BlockApproach()
try:
    result = ba.approach(callback=callback)
    print()
    print('Result: %s (%s)' % ('SUCCESS' if result['success'] else 'FAILED', result['reason']))
finally:
    ba.cleanup()
"
```

**Watch the output to see:**
- Target lock engaging
- Strafe corrections (centering)
- Forward movement (approaching)
- Speed reduction when close
- Final "REACHED" when arrived

---

## Implementation Guide (For Coders)

### Level 2: Use BlockApproach Class

```python
from skills.block_approach import BlockApproach

approach = BlockApproach()

# Approach any visible block
result = approach.approach()

# Approach only red blocks
result = approach.approach(color='red')

# With timeout
result = approach.approach(color='blue', timeout=15)

# Check result
if result['success']:
    print('Reached %s block!' % result['color'])
else:
    print('Failed: %s' % result['reason'])
    # Reasons: 'block_lost', 'timeout', 'battery_low', 'interrupted'

approach.cleanup()
```

### Level 3: Understand the Control Loop

**The approach loop runs at ~30Hz:**

```python
while not reached and not timeout:
    # 1. Capture frame
    ret, frame = camera.read()
    
    # 2. Detect blocks
    blocks = detector.detect(frame, colors=[target_color])
    
    # 3. Find locked target (or nearest if not locked)
    block = find_locked_target(blocks)
    
    if block is None:
        stop()  # Lost target
        continue
    
    # 4. Calculate errors
    error_x = block.center_x - 320  # Pixels from center
    error_y = 420 - block.center_y  # Pixels from bottom target
    
    # 5. Proportional control
    strafe = clamp(error_x * Kx)    # Left/right correction
    forward = clamp(error_y * Ky)   # Forward speed
    
    # 6. Drive
    mecanum_drive(strafe, forward)
    
    # 7. Check if arrived
    if abs(error_x) < tolerance_x and abs(error_y) < tolerance_y:
        stop()
        return SUCCESS
```

**Key parameters:**
```python
Kx = 0.15          # Strafe gain (pixels → motor speed)
Ky = 0.10          # Forward gain
X_TOLERANCE = 40   # Centered enough (pixels)
Y_TOLERANCE = 30   # Close enough (pixels)
TARGET_Y = 420     # Block at bottom of frame = pickup distance
MAX_SPEED = 30     # Safety limit
MIN_SPEED = 28     # Minimum to overcome friction
```

### Level 3: Target Locking

**Problem:** Multiple blocks visible. Robot switches between them mid-approach.

**Solution: Target lock**
```python
# First detection: LOCK onto this specific block
lock_target(block)  # Remember position + color

# Subsequent frames: Find the SAME block
# Match by: closest to last known position + same color
for b in all_blocks:
    if b.color != locked_color:
        continue
    distance_from_last = sqrt((b.x - locked_x)^2 + (b.y - locked_y)^2)
    if distance_from_last < LOCK_RADIUS:  # 120px max movement between frames
        return b  # Same target!

# If no match within radius: target lost
```

**Why it works:**
- Blocks don't teleport between frames (30fps = ~33ms between captures)
- Same color + nearby position = same physical block
- LOCK_RADIUS of 120px handles normal movement

### Level 4: Tuning the Controller

**If robot oscillates (wobbles left-right):**
- Decrease Kx (less aggressive centering)
- Increase X_TOLERANCE (accept wider centering)

**If robot approaches too slowly:**
- Increase Ky (more aggressive forward drive)
- Increase MAX_SPEED

**If robot overshoots (passes the block):**
- Decrease Ky
- Reduce forward speed when close (already implemented: `ky * 0.7` when <30cm)

**If robot loses target frequently:**
- Increase LOCK_RADIUS (allow bigger position jumps)
- Increase LOST_TIMEOUT (wait longer before giving up)
- Check lighting (shadows cause intermittent detection)

---

## Engineering Deep Dive (Advanced)

### Visual Servoing Theory

**Image-Based Visual Servoing (IBVS):**
- Error defined in image space (pixels)
- No 3D model needed
- Our approach: IBVS with proportional control

**Position-Based Visual Servoing (PBVS):**
- Error defined in 3D space (meters)
- Requires camera calibration + 3D model
- More accurate but more complex

**We use IBVS because:**
- Simpler (no 3D reconstruction needed)
- Robust to calibration errors
- Fast (no heavy computation)
- Good enough for block pickup (±3cm accuracy)

### Proportional Control (P-Controller)

```
output = Kp * error

where:
  Kp = proportional gain
  error = target - current
  output = motor command
```

**Properties:**
- Fast response (proportional to error)
- Steady-state error (never quite reaches zero)
- Can oscillate if Kp too high
- Simple to implement and tune

**Why not PID?**
- P-only works well for our case
- Visual feedback at 30Hz provides natural damping
- Adding I (integral) could cause windup during lost frames
- Adding D (derivative) helps but adds complexity

### Mecanum Strafe for Centering

**Why strafe instead of rotate?**

Approach with rotation:
```
See block left → Rotate left → Now facing block but moved sideways
→ Drive forward → Block might drift out of view
```

Approach with strafe:
```
See block left → Strafe left (while facing forward)
→ Block stays in view → Continue forward
→ Simultaneous centering + approach!
```

**Mecanum advantage:** Strafe + forward simultaneously = smooth, efficient approach

### Motion Blur Handling

**Problem:** Camera captures blurry frames while robot is moving

**Two strategies:**

**1. Continuous (our BlockApproach):**
- Accept some blur
- Higher frame rate compensates
- Works for slow approach speeds

**2. Stop-Look-Drive (our auto_pickup.py):**
```
Stop → Wait 200ms → Capture frame → Detect → Drive short burst → Repeat
```
- No motion blur (stopped during detection)
- Slower overall
- More reliable at close range

**When to use each:**
- Far from target (>30cm): Continuous (speed matters)
- Close to target (<30cm): Stop-look-drive (precision matters)

---

## Configuration

```yaml
visual_servoing:
  # Control gains
  Kx: 0.15              # Strafe proportional gain
  Ky: 0.10              # Forward proportional gain
  
  # Tolerances (pixels)
  x_tolerance: 40       # Centered enough
  y_tolerance: 30       # Close enough
  target_y: 420         # Block at bottom = pickup distance
  
  # Speed limits
  max_speed: 30
  min_speed: 28
  
  # Target lock
  lock_radius: 120      # Max pixel movement between frames
  lost_timeout: 2.0     # Seconds before declaring lost
  
  # Safety
  approach_timeout: 30  # Max seconds for approach
  close_range_gain: 0.7 # Reduce speed when <30cm
```

---

## Files

```
visual_servoing/
  SKILL.md           # This file
  README.md          # Quick reference

Existing code (already on robot):
  /home/robot/pathfinder/skills/block_approach.py  # BlockApproach (continuous)
  /home/robot/pathfinder/skills/centering.py       # CenteringController
  /home/robot/pathfinder/skills/auto_pickup.py     # Stop-look-drive approach
```

---

*See the target, correct the error, reach the goal!* 🎯
