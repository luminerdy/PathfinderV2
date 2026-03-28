# Skill: Autonomous Block Pickup (E5)

**Difficulty:** ⭐⭐⭐ (Advanced - Full Integration)  
**Type:** Vision + Drive + Arm Coordination  
**Prerequisites:** D1 (Drive), D3 (Arm), D4 (Camera), E3 (Detection), E4 (Servoing)  
**Estimated Time:** 30-40 minutes  

---

## Overview

### What This Skill Does

**Complete autonomous cycle: Find a block, drive to it, pick it up.** This integrates everything — mecanum drive, camera vision, block detection, visual servoing, and arm control — into one coordinated behavior.

**What you'll learn:**
- State machine design (phases of operation)
- Sensor fusion (camera + arm positions)
- Camera switching (forward view → down view)
- Motion planning (scan → approach → pickup)
- Error recovery (lost target, timeout)

### The Three Phases

```
PHASE 1: SCAN               PHASE 2: APPROACH           PHASE 3: PICKUP
                             
Camera: Forward              Camera: Down                Arm sequence
Arm: Tucked up              Arm: Looking down            
                             
    [Rotate]                 [Stop-Look-Drive]           [Lower]
    [Detect block]           [Center on block]           [Grab]
    [Face it]                [Drive forward]             [Lift]
                             [Arrive at block]           [Carry]
```

### Real-World Applications

- **Amazon warehouses:** Kiva robots pick items from shelves
- **Recycling plants:** Sort materials by color/type
- **Agriculture:** Fruit picking robots
- **Manufacturing:** Part sorting and assembly
- **Competition robotics:** FIRST Tech Challenge game piece scoring

### Why This Is Hard

1. **Camera offset:** Forward camera sees far, but can't see directly below robot
2. **Motion blur:** Moving robot = blurry images = missed detections
3. **Coordinate switch:** Block position in forward view != position in down view
4. **Gripper alignment:** Block must be precisely positioned for successful grab
5. **Battery management:** All systems drawing power simultaneously

---

## Quick Start

### Step 1: Run Full Autonomous Pickup

```bash
cd /home/robot/pathfinder
python3 skills/auto_pickup.py
```

**Or target a specific color:**
```bash
python3 skills/auto_pickup.py red
python3 skills/auto_pickup.py blue
python3 skills/auto_pickup.py yellow
```

**Before running:**
- Place a colored block 30-80cm in front of robot
- Clear path between robot and block
- Ensure good lighting (no harsh shadows)
- Check battery (>7.0V for Pi4)

**What you'll see:**
```
PHASE 1: Scan for block
  Step 3: red at 45cm offset=+20px
  FACING BLOCK

PHASE 2: Approach block
  Cycle 5: red (340,180) err=(+10,-170)
  Cycle 12: red (345,310) err=(+15,-40)
  ARRIVED

PHASE 3: Pickup
  Lowering arm...
  Grabbing...
  Lifting...
  PICKUP COMPLETE

SUCCESS - Check if robot is holding a block!
```

### Step 2: Understand the Output

**Phase 1 output:**
- `Step N:` — Rotation step (16 steps = ~360 degrees)
- `red at 45cm` — Block detected at estimated distance
- `offset=+20px` — 20 pixels right of center
- `FACING BLOCK` — Block roughly centered, proceed to Phase 2

**Phase 2 output:**
- `Cycle N:` — Approach iteration
- `(340,180)` — Block position in frame (pixels)
- `err=(+10,-170)` — Error from target position
- `ARRIVED` — Block in position for pickup

**Phase 3 output:**
- Sequential arm positions (pre-tested on hardware)
- `PICKUP COMPLETE` — Gripper closed, block lifted

---

## Implementation Guide (For Coders)

### Level 2: Use auto_pickup Function

```python
from skills.auto_pickup import auto_pickup

# Pick up any color
success = auto_pickup()

# Pick up specific color
success = auto_pickup(color='red')
```

### Level 3: Understand the State Machine

**Phase 1: Scan**
```python
def scan_for_block(board, camera, detector, color=None):
    """
    Rotate with camera forward to find a block.
    """
    # Position arm for forward-looking camera
    move_arm(board, POS_CAMERA_FORWARD)
    
    for step in range(16):  # 16 x 22deg = ~360deg
        # Capture and detect
        frame = get_fresh_frame(camera)
        blocks = detect_blocks(detector, frame, color)
        
        if blocks and abs(blocks[0].offset_from_center) < 100:
            return True  # Found and facing it!
        
        # Rotate ~22 degrees
        rotate_in_place(board, degrees=22)
    
    return False  # No block found
```

**Phase 2: Approach (Stop-Look-Drive)**
```python
def approach_block(board, camera, detector, color=None):
    """
    Drive to block using stop-look-drive strategy.
    Camera pointed down to see block below robot.
    """
    move_arm(board, POS_CAMERA_DOWN)
    
    for cycle in range(40):
        # STOP (no motion blur)
        stop(board)
        time.sleep(0.2)
        
        # LOOK (detect while stationary)
        frame = get_fresh_frame(camera)
        blocks = detect_blocks(detector, frame, color)
        
        if not blocks:
            search_rotation()  # Lost target, search
            continue
        
        block = blocks[0]
        error_x = block.center_x - DOWN_VIEW_CENTER_X
        error_y = DOWN_VIEW_TARGET_Y - block.center_y
        
        # ARRIVED?
        if abs(error_x) < tolerance and abs(error_y) < tolerance:
            return True
        
        # DRIVE (short burst)
        if abs(error_x) > tolerance:
            rotate_to_center(error_x)
        else:
            drive_forward(duration_based_on_distance)
    
    return False  # Timeout
```

**Phase 3: Pickup**
```python
def pickup_block(board):
    """
    Pre-recorded arm sequence: lower, grab, lift.
    """
    move_arm(board, POS_PICKUP_READY, 1000)  # Lower arm
    move_arm(board, POS_PICKUP_GRAB, 400)    # Close gripper
    move_arm(board, POS_PICKUP_LIFT, 1000)   # Lift
    move_arm(board, POS_CARRY, 800)          # Carry position
```

### Level 3: Camera Switching Strategy

**Problem:** One camera, two views needed

**Forward view** (arm tucked up):
```
Camera sees: Far (30-100cm)
Good for: Finding blocks, initial detection
Limitation: Can't see directly below robot
```

**Down view** (arm angled down):
```
Camera sees: Near (5-30cm below robot)
Good for: Precise positioning for pickup
Limitation: Limited field of view
```

**Arm positions that change camera angle:**
```python
POS_CAMERA_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CAMERA_DOWN    = [(1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)]
                                                          ^^^^
                                                    Shoulder angle changes!
```

**The handoff:**
1. Forward view detects block at ~45cm
2. Robot rotates to face block
3. Switch to down view (change shoulder servo)
4. Block appears in down view (different pixel position!)
5. Use down-view calibration to center and approach

### Level 4: Build Custom Pickup Sequence

```python
def custom_pickup(board, camera, detector, target_color):
    """Build your own pickup strategy."""
    
    # 1. Scan (customize rotation strategy)
    # ...
    
    # 2. Approach (customize speed, tolerance)
    # ...
    
    # 3. Custom arm sequence
    # Tune these positions for your block size/shape:
    POSITIONS = {
        'ready':  [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)],
        'grab':   [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)],
        'lift':   [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)],
        'carry':  [(1, 1558), (3, 569), (4, 2400), (5, 809), (6, 1500)],
    }
    
    for name, pos in POSITIONS.items():
        print('  %s...' % name)
        board.set_servo_position(800, pos)
        time.sleep(1.0)
```

---

## Engineering Deep Dive (Advanced)

### State Machine Design

**Why phases instead of one big loop?**

1. **Separation of concerns:** Each phase has one job
2. **Testable:** Run phases independently (`scan_for_block()` alone)
3. **Recoverable:** If approach fails, go back to scan
4. **Debuggable:** Know exactly where it failed

**State transitions:**
```
IDLE → SCAN → [block found?]
                 Yes → APPROACH → [arrived?]
                 |                   Yes → PICKUP → [grabbed?]
                 |                   |                Yes → SUCCESS
                 |                   |                No → APPROACH (retry)
                 |                   No (lost) → SCAN (retry)
                 No → FAILED (no blocks visible)
```

### Stop-Look-Drive vs Continuous Approach

**Stop-Look-Drive (our implementation):**
```
Advantages:
  + No motion blur (detect while stopped)
  + More reliable detection
  + Simpler control logic

Disadvantages:
  - Slower (stop every 0.2s)
  - Jerky motion
  - Block could move between stops
```

**Continuous (BlockApproach class):**
```
Advantages:
  + Smooth motion
  + Faster approach
  + Real-time tracking

Disadvantages:
  - Motion blur at close range
  - More complex control
  - Harder to debug
```

**Hybrid strategy (optimal):**
```python
distance = estimate_distance(block)

if distance > 30:  # cm
    # Far: continuous approach (speed matters)
    use_block_approach(block)
elif distance > 10:
    # Medium: slow continuous
    use_block_approach(block, max_speed=20)
else:
    # Close: stop-look-drive (precision matters)
    use_stop_look_drive(block)
```

### Camera-Arm Coordination

**The "blind spot" problem:**
- Camera on arm sees forward when arm is up
- Need to see directly below for pickup
- Solution: Change arm angle to point camera down

**Calibration needed:**
```
Forward view block at x=350 → appears at x=350 in down view? NO!

Camera forward: Block at center (320, 240) means "directly ahead"
Camera down: Block at (350, 350) means "below robot, ready for pickup"

These are DIFFERENT coordinate systems!
Calibrate by: placing block, switching views, noting position shift
```

### Error Recovery Strategies

**Block lost during approach:**
1. Stop immediately
2. Wait 1 second (block might reappear)
3. Rotate slowly (search pattern)
4. If still lost after 5 cycles → restart from scan

**Battery low:**
```python
voltage = board.get_battery() / 1000
if voltage < BATTERY_MIN:
    # Retract arm to safe position
    move_arm(board, POS_CAMERA_FORWARD)
    stop(board)
    return 'battery_low'
```

**Approach timeout:**
- Max 30 seconds per approach
- If exceeded, target may have moved
- Return to scan phase

---

## Configuration

```yaml
autonomous_pickup:
  # Phase 1: Scan
  scan_steps: 16           # Rotation steps (16 = ~360deg)
  scan_tolerance: 100      # Max offset to consider "facing" (pixels)
  
  # Phase 2: Approach  
  approach_cycles: 40      # Max approach iterations
  motor_power: 30
  rotation_power: 30
  down_view_center_x: 350  # Calibrated center in down view
  down_view_target_y: 350  # Target Y for "arrived"
  x_tolerance: 80          # Horizontal tolerance (pixels)
  y_tolerance: 50          # Vertical tolerance (pixels)
  
  # Phase 3: Arm positions (servo PWM values)
  camera_forward: [2500, 590, 2450, 700, 1500]   # [grip, wrist, elbow, shoulder, base]
  camera_down:    [2500, 590, 2450, 1214, 1500]
  pickup_ready:   [1558, 830, 2170, 2410, 1500]
  pickup_grab:    [1475, 830, 2170, 2410, 1500]
  pickup_lift:    [1475, 590, 2450, 700, 1500]
  carry:          [1558, 569, 2400, 809, 1500]
  
  # Safety
  battery_min_pi4: 7.0
  battery_min_pi5: 8.1
  timeout: 30
```

---

## Files

```
autonomous_pickup/
  SKILL.md           # This file
  README.md          # Quick reference

Existing code (already on robot):
  /home/robot/pathfinder/skills/auto_pickup.py     # Full autonomous pickup
  /home/robot/pathfinder/skills/block_detect.py    # Block detection
  /home/robot/pathfinder/skills/block_approach.py  # Visual approach
  /home/robot/pathfinder/skills/centering.py       # Centering controller
```

---

*The grand integration: See it, drive to it, grab it!* 🤖🔴✊
