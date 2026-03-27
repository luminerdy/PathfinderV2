# IK-Based Block Pickup Guide

## Overview

**We don't hardcode servo positions!** Instead, we use **Inverse Kinematics (IK)** to calculate the exact servo angles needed to reach any (x, y, z) position.

## The IK System

### Files
- `lib/arm_inverse_kinematics.py` - IK solver (math)
- `capabilities/pickup.py` - Vision-guided pickup controller
- `test_pickup_ik.py` - Demonstration script

### How IK Works

**Input:** 3D position (x, y, z) in millimeters
- `x` = Forward/backward (0 = robot base)
- `y` = Left/right (0 = center)
- `z` = Height above ground

**Output:** Servo positions (pulse widths)
- Servo 1: Gripper (1475=closed, 2500=open)
- Servo 3: Wrist
- Servo 4: Elbow
- Servo 5: Shoulder
- Servo 6: Base rotation

**Math:** Uses law of cosines and trigonometry to solve for joint angles that put the gripper at the target position.

## Pickup Sequence

### 1. Pre-Grasp (Above Block)
```python
x, y, z = 200, 0, 100  # 20cm forward, centered, 10cm high
solution = ik.set_position(x, y, z)
for servo_id, pulse in solution:
    board.set_servo_position(500, [(servo_id, pulse)])
```

### 2. Open Gripper
```python
board.set_servo_position(500, [(1, 2500)])  # Servo 1 = gripper, 2500 = open
```

### 3. Lower to Grasp
```python
x, y, z = 200, 0, 20  # Same x/y, lower z (2cm above ground)
solution = ik.set_position(x, y, z)
for servo_id, pulse in solution:
    board.set_servo_position(500, [(servo_id, pulse)])
```

### 4. Close Gripper
```python
board.set_servo_position(500, [(1, 1475)])  # 1475 = fully closed
```

### 5. Lift Block
```python
x, y, z = 200, 0, 150  # Same x/y, higher z (15cm up)
solution = ik.set_position(x, y, z)
for servo_id, pulse in solution:
    board.set_servo_position(500, [(servo_id, pulse)])
```

## Getting Block Position

### Method 1: Vision Only (±20mm accuracy)
```python
from capabilities.vision import VisionSystem
vision = VisionSystem(camera, config)

# Detect blocks
frame = camera.read()
blocks = vision.detect_blocks(frame)

# Estimate position from camera
for block in blocks['red']:
    # Use image position + distance estimation
    # Less accurate but works without AprilTags
```

### Method 2: AprilTag Reference (±5mm accuracy)
```python
# Detect nearby AprilTag
tags = vision.detect_apriltags(frame)

# Use tag as known reference point
# Calculate block position relative to tag
# Much more accurate - recommended for competition
```

### Method 3: Manual Entry (Testing)
```python
# You know where the block is
x, y, z = 200, 0, 25  # Direct specification
```

## Example: Full Pickup

```python
from pathfinder import Pathfinder

robot = Pathfinder()

try:
    # 1. Detect block
    frame = robot.camera.read()
    blocks = robot.vision.detect_blocks(frame)
    
    if blocks['red']:
        block = blocks['red'][0]
        
        # 2. Calculate 3D position
        # (simplified - real version uses camera calibration)
        x = 200  # From distance estimation
        y = 0    # From horizontal offset
        z = 25   # Block height (1 inch)
        
        # 3. Execute pickup sequence
        # Pre-grasp
        solution = robot.arm.ik.set_position(x, y, 100)
        robot.arm.move_to_pose(solution)
        
        # Open gripper
        robot.arm.set_gripper(2500)
        
        # Lower
        solution = robot.arm.ik.set_position(x, y, 20)
        robot.arm.move_to_pose(solution)
        
        # Grasp
        robot.arm.set_gripper(1475)
        
        # Lift
        solution = robot.arm.ik.set_position(x, y, 150)
        robot.arm.move_to_pose(solution)
        
        print("Block picked up!")
    
finally:
    robot.cleanup()
```

## Testing IK Pickup

### Interactive Demo
```bash
python3 test_pickup_ik.py
```

This script:
1. Calculates positions for 200mm forward block
2. Shows IK solutions (servo angles)
3. Executes full pickup sequence
4. Explains each step

### What You'll See
```
[Step 1] PRE-GRASP POSITION (above block)
Target: (200, 0, 100) mm
IK Solution found:
  Servo 6: 1500 (90.0°)  ← Base (centered)
  Servo 5: 1234 (65.2°)  ← Shoulder (calculated)
  Servo 4: 1876 (122.8°) ← Elbow (calculated)
  Servo 3: 892 (34.8°)   ← Wrist (calculated)
```

Every servo position is **calculated from the target coordinates** - no hardcoding!

## Link Lengths (Measured)

The IK solver needs to know the arm geometry:

```python
self.L1 = 61.0   # Base to shoulder height
self.L2 = 43.5   # Shoulder to elbow length
self.L3 = 82.85  # Elbow to wrist length
self.L4 = 82.0   # Wrist to gripper center
```

These were measured from the physical robot. If your arm geometry is different, update `lib/arm_inverse_kinematics.py`.

## Reachable Workspace

The arm can't reach everywhere. Maximum reach:
```python
max_reach = L2 + L3 + L4 = 43.5 + 82.85 + 82.0 = 208.35mm
```

**Typical pickup positions:**
- Forward: 150-200mm
- Height: 20-150mm
- Side: ±50mm

If IK returns `None`, the target is unreachable.

## Vision-Guided Pickup System

The full system (`capabilities/pickup.py`) adds:

1. **Block Detection** - Find blocks by color
2. **AprilTag Positioning** - Accurate 3D localization
3. **Visual Servoing** - Approach block using camera feedback
4. **Mecanum Positioning** - Strafe to center block
5. **Orientation Alignment** - Rotate to match block angle
6. **IK Calculation** - Calculate arm pose
7. **Pickup Execution** - Execute sequence
8. **Verification** - Check if block was grasped

## Tunable Parameters

In `capabilities/pickup.py`:

```python
self.block_size_mm = 25           # 1 inch blocks
self.approach_distance_mm = 150   # Stop when block this far
self.pre_grasp_height_mm = 100    # Height above block
self.grasp_height_mm = 15         # Gripper center height
self.lift_height_mm = 150         # Lift height after grasp
```

Adjust these based on testing!

## Competition Use

### Scenario 1: AprilTag-Assisted Pickup
```python
# 1. Robot sees block and nearby AprilTag
# 2. Calculate accurate 3D position using tag reference
# 3. Approach block (visual servoing)
# 4. IK calculates arm pose
# 5. Execute pickup
# 6. Navigate to delivery zone
```

### Scenario 2: Vision-Only Pickup
```python
# 1. Robot sees block (no AprilTag)
# 2. Estimate position from camera (less accurate)
# 3. Approach block
# 4. IK calculates arm pose
# 5. Execute pickup
# 6. May need adjustment if position was off
```

### Scenario 3: Blind Pickup (Known Position)
```python
# 1. Robot knows block is at (x, y, z) from prior scan
# 2. Drive to position
# 3. IK calculates arm pose
# 4. Execute pickup (no vision feedback)
```

## Advantages of IK Approach

### ✅ Flexibility
- Works for **any** block position
- Easy to adjust heights and offsets
- Can pick from different angles

### ✅ No Calibration Hell
- Don't need to manually find 20 servo positions
- Just specify target coordinates
- Math does the rest

### ✅ Adaptability
- Works with different block sizes (just change `z`)
- Works with different approach angles
- Easy to add new pickup patterns

### ✅ Understandable
- Positions are in **real-world units** (mm)
- Easy to debug ("block at 200mm, arm should be at 200mm")
- Can visualize what the arm is doing

## Debugging IK Issues

### Problem: IK returns None
**Cause:** Target unreachable
**Fix:** Move closer or adjust target height

### Problem: Arm moves to wrong position
**Cause:** Link lengths incorrect
**Fix:** Measure actual arm and update `ArmIK.__init__()`

### Problem: Gripper misses block
**Cause:** Camera position estimation off
**Fix:** Use AprilTag reference or calibrate camera

### Problem: Block drops during pickup
**Cause:** Wrong grasp height or gripper timing
**Fix:** Adjust `grasp_height_mm` and add delays

## Next Steps

1. **Test IK demo:** `python3 test_pickup_ik.py`
2. **Verify link lengths** match your robot
3. **Test with real blocks** and measure accuracy
4. **Tune parameters** in `pickup.py`
5. **Add AprilTag reference** for better accuracy
6. **Run full autonomous pickup** test

## Summary

**The key insight:** You don't need to memorize servo positions. Just:
1. Know where the block is (vision)
2. Tell IK where you want the gripper
3. IK calculates servo angles
4. Execute the sequence

**It's that simple!** 🤖🎯
