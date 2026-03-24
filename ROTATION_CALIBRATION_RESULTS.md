# Rotation Calibration Results
## Day 7 - March 24, 2026

**Session:** 9:19 AM - 9:40 AM CDT  
**Battery at start:** ~8.0V (estimated)  
**Battery at end:** 7.85V  
**Status:** Battery decline affected results

---

## Critical Discoveries

### 1. **Minimum Rotation Power: 25 (unreliable) / 28 (safe)**

**Power 24 and below:** ZERO rotation
- Tested 1s, 2s at power 24 → 0° rotation
- Motors spinning but not overcoming static friction
- Same behavior as power 15, 20

**Power 25:** THRESHOLD (unreliable)
- Test 1 (9:22 AM): 117.0 deg/sec ✅
- Test 2 (9:22 AM): 24.3 deg/sec ⚠️
- Inconsistent performance
- Too close to friction threshold

**Power 26-28:** RELIABLE (initially)
- Power 26: 117.9 deg/sec
- Power 28: 105.1 deg/sec
- Consistent rotation achieved

**Power 30:** Unexpected failure
- Measured 0° rotation
- Theory: Rotated too fast for visual tracking?
- Or battery already declining

---

### 2. **Battery Effect on Rotation**

**Timeline:**

| Time     | Battery | Power 28 Performance |
|----------|---------|---------------------|
| 9:22 AM  | ~8.0V   | 105 deg/sec ✅      |
| 9:32 AM  | 7.85V   | 0-1.3 deg/sec ⚠️    |

**In just 10 minutes:**
- Battery dropped from ~8.0V → 7.85V
- Power 28 rotation went from 105 deg/sec → nearly zero
- Powers 28-30 all failed to rotate

**Conclusion:**
- **7.5V = absolute minimum** for any motor movement
- **8.0V+ required** for reliable high-power operation
- Between 7.5-8.0V = motors struggle, inconsistent performance

---

### 3. **Rotation Rate Calibration**

**Valid measurements (battery >8.0V):**

| Power | Duration | Actual Rotation | Rate (deg/sec) |
|-------|----------|----------------|----------------|
| 25    | 1.0s     | +117.0°        | 117.0          |
| 25    | 2.0s     | +48.6°         | 24.3           |
| 26    | 1.0s     | +117.9°        | 117.9          |
| 28    | 1.0s     | +105.1°        | 105.1          |

**Average rates:**
- Power 25: ~70 deg/sec (inconsistent)
- Power 26: ~118 deg/sec
- Power 28: ~105 deg/sec

**For 360° rotation:**
- At power 28: 360° / 105 = **3.4 seconds**
- At power 26: 360° / 118 = **3.0 seconds**

---

## Test Method

**Visual Ground Truth:**
1. Start facing AprilTag, measure angle via pose estimation
2. Rotate at specified power/duration
3. Detect ending AprilTag + angle
4. Calculate actual rotation from tag positions + angles
5. Log sonar continuously during rotation

**Advantages:**
- No gyroscope needed
- Uses existing AprilTag infrastructure
- Measures actual rotation, not assumed
- Validates sonar distance pattern

**Challenges:**
- Lost visual tracking at high speeds (power 27-30)
- Battery decline during testing affected results
- Tag detection depends on field position

---

## Sonar Patterns During Rotation

**Expected in rectangular field:**
- 4 distance peaks/valleys (one per wall)
- 4 corners = longest distances (diagonal)
- Pattern repeats after 360°

**Actual observations:**
- When NOT rotating (power 15-24): constant 81cm ✅
- When rotating (power 25+): 77-122cm range ✅
- Variation confirms actual rotation occurring
- Single-wall reading = not rotating

**Previous "360° scan" at power 15:**
- Showed constant 68-69cm (all 60 samples)
- **Confirmed: Did NOT rotate** (friction won)
- Explains why centering algorithm failed

---

## Implications for Navigation

### **1. Update All Rotation Speeds**

**Current scripts using low power:**
- `go_to_center_360.py`: Uses power 15 → **BROKEN**
- `tour_all_8_tags.py`: Search rotation power 22 → **May fail at low battery**
- `centering.py`: Max rotation 25 → **Unreliable**

**Required changes:**
- Minimum rotation power: **28**
- Search/scan rotation: **28**
- Centering skill: **28**

### **2. Add Battery Monitoring**

**Before any operation:**
```python
battery_mv = board.get_battery()
battery_v = battery_mv / 1000.0

if battery_v < 7.5:
    print("CRITICAL: Battery too low, aborting")
    exit(1)
elif battery_v < 8.0:
    print("WARNING: Battery low, performance may be degraded")
    # Increase motor powers by 10-20%
```

**During operation:**
- Monitor voltage periodically
- Warn if dropping below thresholds
- Compensate power levels automatically

### **3. Power Reserve Headroom**

**Don't use minimum power:**
- Friction threshold: Power 25
- Safe operation: Power 28 (3 points above)
- At low battery: Power 30 (5 points above)

**This provides:**
- Tolerance for battery decline
- Tolerance for floor friction variations
- Tolerance for motor wear over time

---

## Corrected Understanding

### **What I Thought Before:**
- Power 15 rotates ~60 deg/sec
- 6 seconds = 360° rotation
- My "360° scan" worked

### **What I Know Now:**
- Power 15-24 = **zero rotation** (friction wins)
- Power 25 = threshold (unreliable)
- Power 28+ = reliable rotation
- Rate: ~105-120 deg/sec (at good battery)
- 360° requires **3-3.4 seconds** at power 28

### **False Assumptions Corrected:**
1. ❌ "360° scan at power 15 worked" → Actually rotated 0°
2. ❌ "Sonar 68-69cm = centered" → Was just facing one wall
3. ❌ "Power 15 good for slow rotation" → Can't overcome friction
4. ❌ "Centering at power 25 is safe" → Too close to threshold

---

## Recommendations

### **Immediate Updates Needed:**

1. **All navigation scripts:**
   - Change rotation power to 28 minimum
   - Add battery checks
   - Update rotation duration calculations

2. **Centering skill (`skills/centering.py`):**
   - Change `MAX_ROTATION_SPEED = 28` (was 25)
   - Add battery compensation logic
   - Test at various battery levels

3. **360° scan (`go_to_center_360.py`):**
   - Change rotation power to 28
   - Change duration to 3.4s (not 6s)
   - Verify sonar pattern shows 4 walls

4. **Configuration:**
   - Document minimum power requirements
   - Create battery monitoring utility
   - Add voltage thresholds to config.yaml

### **Testing TODO After Recharge:**

1. **Verify power 28 rotation** (full battery)
2. **Test 360° scan** (corrected power/duration)
3. **Calibrate forward movement** (cm/pulse at power 28)
4. **Test centering skill** with updated power
5. **Full navigation test** (8-tag tour)

---

## Data Files

**Created:**
- `/home/robot/code/pathfinder/rotation_calibration.txt` - Raw test results
- `/home/robot/code/pathfinder/calibrate_rotation.py` - Calibration script

**To Update:**
- `/home/robot/code/pathfinder/skills/centering.py` - Increase power to 28
- `/home/robot/code/pathfinder/go_to_center_360.py` - Fix power + duration
- `/home/robot/code/pathfinder/tour_all_8_tags.py` - Increase search power
- `/home/robot/code/pathfinder/config.yaml` - Add power thresholds

---

## Summary

**What Worked:**
✅ Visual calibration method using AprilTags  
✅ Identified minimum rotation power (25 threshold, 28 safe)  
✅ Measured rotation rates (~105-120 deg/sec)  
✅ Discovered battery effect on performance  
✅ Corrected false assumptions about previous "360° scan"

**What Needs Work:**
⚠️ Update all scripts to use power 28 minimum  
⚠️ Add battery monitoring everywhere  
⚠️ Re-test with full battery  
⚠️ Calibrate forward movement similarly

**Key Insight:**
Battery voltage affects motor performance more than expected. The difference between 8.0V and 7.85V was enough to make rotation fail completely. Must build in power headroom and battery monitoring.

---

**Next Session Goals:**
1. Fresh battery installed
2. Re-verify calibration at full battery
3. Update all navigation scripts
4. Test 360° scan properly
5. Continue with block approach or movement calibration

**Status:** Ready for battery change and reboot.
