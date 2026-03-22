# Robot Positioning Strategy for Block Pickup

**Problem:** Arm has limited reach, camera can't see both AprilTags and floor blocks simultaneously

**Solution:** Multi-phase approach with camera mode switching

---

## 🎯 The Challenge

### **Physical Constraints:**
1. **Arm reach:** ~80-150mm from robot base
2. **Camera FOV:** Can point forward (tags) OR down (blocks), not both
3. **Block position:** On floor, requires close positioning
4. **Navigation:** Needs forward-facing camera for AprilTags

### **Cannot do both at once!**

---

## 📋 Three-Phase Approach

### **Phase 1: Coarse Navigation (AprilTag-Based)**

**Camera Mode:** NAVIGATION (forward-facing)

**Strategy:**
```
1. Detect AprilTag near target block
2. Navigate to tag using existing navigate_simple_forward.py
3. Stop at "approach zone" (measured distance from tag)
4. Robot is now in general vicinity of block
```

**Example:**
- Block is placed near Tag 1
- Robot navigates to Tag 1
- Stops when tag area = 15,000-20,000 pixels² (closer than navigation target)
- Robot is now ~50-80cm from tag
- Block should be visible when camera tilts down

**Key Parameters:**
- Target area: 15,000-20,000 px² (closer approach than navigation)
- Approach speed: 20-30 (slow, controlled)
- Final distance: ~50-80cm from tag

---

### **Phase 2: Camera Switch + Block Detection**

**Camera Mode:** BLOCK DETECTION (angled down)

**Strategy:**
```
1. SWITCH camera angle to floor view
   - Move wrist/elbow to point camera down
   - Wait for servos to settle (1-2 seconds)

2. Detect blocks in view
   - Run block detection
   - Find target color
   - Measure block position in frame

3. If block not visible:
   - Small search pattern (rotation or strafe)
   - Retry detection
   - If still not found → alert/retry from Phase 1
```

**Camera Position (from calibration):**
```python
BLOCK_DETECTION_MODE = {
    6: 1500,  # Base centered
    5: 1200,  # Shoulder down
    4: 1800,  # Elbow retracted
    3: 1200,  # Wrist down
    1: 2500   # Gripper open
}
```

**Detection Requirements:**
- Block must be in view
- Must have clear color detection
- Should estimate distance/angle

---

### **Phase 3: Fine Positioning (Visual Servoing)**

**Camera Mode:** Still BLOCK DETECTION

**Strategy:**
```
1. Calculate block offset from center:
   - Horizontal offset (X): Use mecanum strafe
   - Distance (depth): Use forward/backward
   - Angle: Use rotation

2. Move incrementally toward optimal pickup position:
   - Center block horizontally (strafe left/right)
   - Approach to target distance (forward/backward)
   - Small rotation if needed

3. Verify in "pickup zone":
   - Block center within ±30px of frame center (horizontal)
   - Block area = target size (distance check)
   - Arm can reach (validate with IK)
```

**Positioning Loop:**
```python
while not in_pickup_zone(block):
    # Calculate correction
    x_error = block['center_x'] - FRAME_CENTER_X
    distance = estimate_distance(block['area'])
    
    # Apply correction
    if abs(x_error) > 30:  # Not centered
        if x_error > 0:
            chassis.strafe_right(20)
        else:
            chassis.strafe_left(20)
        time.sleep(0.3)
        chassis.stop()
    
    elif distance > TARGET_DISTANCE:  # Too far
        chassis.move_forward(20)
        time.sleep(0.2)
        chassis.stop()
    
    elif distance < TARGET_DISTANCE:  # Too close
        chassis.move_backward(20)
        time.sleep(0.2)
        chassis.stop()
    
    else:
        # In position!
        break
    
    # Re-detect block
    block = detect_block(target_color)
```

**Target Metrics (from calibration):**
- Horizontal center: Frame_X ±30px
- Distance: Block area ~= target_area (from reach calibration)
- Angle: Robot facing block (not critical with mecanum)

---

## 🔄 Complete Sequence

### **Example: Pick Red Block Near Tag 1**

```python
def pickup_block_at_tag(tag_id, block_color):
    """Complete pickup sequence with positioning"""
    
    # PHASE 1: NAVIGATE TO TAG AREA
    print(f"Phase 1: Navigating to Tag {tag_id}...")
    
    # Camera in NAVIGATION mode (already there from startup)
    position_camera_navigation()
    
    # Navigate close to tag (not as close as usual)
    navigate_to_tag_close(tag_id, target_area=18000)  # Closer approach
    
    # PHASE 2: SWITCH TO BLOCK DETECTION
    print("Phase 2: Switching to block detection mode...")
    
    # Change camera angle
    position_camera_for_blocks()
    time.sleep(2)  # Let servos settle
    
    # Find block
    block = find_block_color(block_color, timeout=10)
    if not block:
        print("ERROR: Block not found after tag approach")
        return False
    
    print(f"Block detected: {block['color']} at ({block['center_x']}, {block['center_y']})")
    
    # PHASE 3: FINE POSITIONING
    print("Phase 3: Fine positioning for pickup...")
    
    # Position robot optimally
    success = position_for_pickup(block, target_area=PICKUP_TARGET_AREA)
    if not success:
        print("ERROR: Could not position for pickup")
        return False
    
    # Verify in reach
    if not verify_in_reach(block):
        print("ERROR: Block not in arm reach zone")
        return False
    
    # EXECUTE PICKUP
    print("Executing pickup...")
    pickup_success = execute_gripper_pickup(block)
    
    # RETURN TO NAVIGATION MODE
    print("Returning to navigation mode...")
    position_camera_navigation()
    
    return pickup_success
```

---

## 📐 Calibration Values (To Be Measured)

### **From Arm Reach Calibration:**
```python
# Run: calibrate_arm_reach.py
ARM_REACH_MIN = 80   # mm - closest pickup point
ARM_REACH_MAX = 150  # mm - farthest pickup point
ARM_REACH_OPTIMAL = 115  # mm - best reliability
LATERAL_TOLERANCE = 50  # mm - side-to-side tolerance
```

### **From Camera Mode Calibration:**
```python
# Run: test_camera_modes.py
NAVIGATION_CAMERA = {
    6: 1500, 5: 700, 4: 2450, 3: 590, 1: 2500
}

BLOCK_DETECTION_CAMERA = {
    6: 1500, 5: 1200, 4: 1800, 3: 1200, 1: 2500
}
```

### **From Distance Calibration:**
```python
# Relate block pixel area to real distance
# Example: block at 100mm = 5000 px²
#          block at 150mm = 2500 px²
#          block at 200mm = 1500 px²

DISTANCE_LOOKUP = {
    5000: 100,  # Area (px²) → Distance (mm)
    2500: 150,
    1500: 200
}
```

---

## 🧪 Testing Plan

### **Test 1: Camera Mode Switching (15 min)**
```bash
python3 test_camera_modes.py
```
- Validates camera angles
- Confirms visibility in each mode
- Saves optimal servo positions

### **Test 2: Arm Reach Envelope (30 min)**
```bash
python3 calibrate_arm_reach.py
```
- Measures actual pickup zone
- Tests 16 positions
- Determines optimal approach distance

### **Test 3: Distance Estimation (20 min)**
```bash
python3 calibrate_block_distance.py  # Create this next
```
- Place block at known distances
- Measure pixel area
- Build lookup table

### **Test 4: Integrated Positioning (1 hour)**
```bash
python3 test_integrated_positioning.py  # Create this next
```
- Full 3-phase sequence
- Tag approach → Camera switch → Block position
- Measure success rate

---

## 💡 Key Insights

### **Why This Works:**

1. **AprilTags for coarse navigation**
   - Large, visible from distance
   - Precise enough to get "close"
   - Doesn't need to be perfect

2. **Camera switching enables both tasks**
   - One camera, two modes
   - Quick servo movement (1-2 sec)
   - No hardware modification needed

3. **Mecanum drive for fine positioning**
   - Strafe to center block horizontally
   - Forward/back for distance
   - No need to turn (gripper is centered)

4. **IK validates reachability**
   - Before attempting pickup
   - Prevents failed grasp attempts
   - Saves time

### **Advantages over Alternatives:**

❌ **Single camera angle (compromise):** Can't see either task well  
❌ **Second camera:** Added complexity, cost, processing  
❌ **Guess and grab:** Low success rate, wastes time  
✅ **This approach:** Uses existing hardware optimally

---

## 📊 Expected Performance

### **Success Criteria:**

**Phase 1 (Tag Navigation):**
- Success rate: >90%
- Time: 30-60 seconds
- Final position: Within 50-80cm of tag

**Phase 2 (Block Detection):**
- Detection rate: >80% (if block present)
- Switch time: 2 seconds
- Search time: 5-10 seconds

**Phase 3 (Fine Positioning):**
- Centering accuracy: ±30px (±3cm real-world)
- Distance accuracy: ±20mm
- Positioning time: 10-20 seconds
- Success rate: >70%

**Overall Pickup Success:**
- Target: >60% on first attempt
- Time budget: 60-90 seconds total
- Includes all 3 phases

---

## 🎯 Implementation Priority

### **Immediate (This Session):**
1. ✅ Create calibration scripts (DONE)
2. 🔲 Run arm reach calibration
3. 🔲 Run camera mode calibration
4. 🔲 Document measured values

### **Next Session:**
1. Create distance lookup table
2. Implement position_for_pickup() function
3. Test integrated sequence
4. Refine based on results

### **Future Enhancement:**
1. Adaptive distance estimation (machine learning?)
2. Multiple block handling (queue)
3. Recovery from failures
4. Speed optimization

---

## 📝 Notes

- This strategy emerged from understanding physical constraints
- Robot positioning is AS IMPORTANT as arm IK
- Camera mode switching is the key enabler
- Mecanum drive makes fine positioning practical
- Calibration is essential (don't guess!)

---

**Status:** Strategy designed, calibration scripts ready  
**Next Step:** Run calibrations to get actual measurements  
**Owner:** Scotty + Pathfinder  
**Date:** March 22, 2026
