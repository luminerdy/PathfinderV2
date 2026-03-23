# Point and Drive - AprilTag Edition

**Interactive AprilTag navigation demo**

Point your robot at any AprilTag and watch it drive there automatically!

---

## 🎯 What It Does

This script makes the robot:
1. **Continuously scan** for AprilTags
2. **Auto-drive** toward any visible tag
3. **Auto-center** the tag (rotates if tag is off-center)
4. **Stop** when close enough (area > 25,000 px²)
5. **Wait** for you to point at next tag

Perfect for:
- ✅ Testing all field tags quickly
- ✅ Verifying tag detection ranges
- ✅ Demonstrating autonomous navigation
- ✅ Field setup validation
- ✅ Workshop demonstrations

---

## 🚀 How to Use

### **Step 1: Run the Script**

```bash
cd /home/robot/code/pathfinder
python3 point_and_drive_apriltag.py
```

**You'll see:**
```
======================================================================
POINT AND DRIVE - APRILTAG EDITION
======================================================================

How to use:
  1. Point robot at any AprilTag
  2. Robot will drive toward it automatically
  3. Robot stops when close enough
  4. Point at another tag to continue

Expected tags: 582 (Home), 583 (Pickup_1), 584 (Pickup_2), 585 (Delivery)

Positioning camera...
Ready!

Scanning for tags... (point robot at any tag)
----------------------------------------------------------------------
```

### **Step 2: Point at a Tag**

**Physically point** the robot toward any AprilTag on the field.

**The robot will:**
- Detect the tag
- Show status: `Tag 583 (Pickup_1): 5000px² | → Driving forward`
- Drive toward it
- Auto-center if needed: `↺ Rotating left to center`
- Stop when close: `✅ REACHED Tag 583 (Pickup_1)! Area=27000px²`

### **Step 3: Point at Another Tag**

**While robot is stopped:**
- Manually rotate/push robot to point at different tag
- Robot detects new tag and drives to it
- Repeat for all tags!

### **Step 4: Stop When Done**

Press **Ctrl+C** to stop the script.

---

## 🎮 What You'll See

### **Normal Operation:**

```
Tag 583 (Pickup_1   ): 3500px² | → Driving forward
Tag 583 (Pickup_1   ): 5200px² | → Driving forward
Tag 583 (Pickup_1   ): 8900px² | ↻ Rotating right to center
Tag 583 (Pickup_1   ): 12000px² | → Driving forward
Tag 583 (Pickup_1   ): 18500px² | → Driving forward
Tag 583 (Pickup_1   ): 24200px² | → Driving forward

✅ REACHED Tag 583 (Pickup_1)! Area=27500px²
   Point at another tag to continue...

[Stopped at Tag 583 (Pickup_1)] Point at different tag to continue
```

### **When You Point at New Tag:**

```
Tag 584 (Pickup_2   ): 6200px² | → Driving forward
Tag 584 (Pickup_2   ): 9800px² | ↺ Rotating left to center
Tag 584 (Pickup_2   ): 14500px² | → Driving forward

✅ REACHED Tag 584 (Pickup_2)! Area=26400px²
   Point at another tag to continue...
```

### **No Tags Visible:**

```
No tags visible... (point at a tag)
```

---

## 📊 Testing All 4 Tags

### **Suggested Workflow:**

**1. Start in center of field**
- Point at Tag 582 (North wall)
- Robot drives there
- ✅ Tag 582 tested

**2. Rotate 90° clockwise**
- Point at Tag 583 (East wall)
- Robot drives there
- ✅ Tag 583 tested

**3. Rotate 90° clockwise**
- Point at Tag 584 (South wall)
- Robot drives there
- ✅ Tag 584 tested

**4. Rotate 90° clockwise**
- Point at Tag 585 (West wall)
- Robot drives there
- ✅ Tag 585 tested

**Total time:** ~2-3 minutes to test all 4 tags!

---

## ⚙️ How It Works (Behind the Scenes)

### **Detection:**
```python
detector = Detector(families="tag36h11")
tags = detector.detect(gray_frame)
```

### **Decision Logic:**

**If tag detected:**
1. Calculate tag area (width × height in pixels)
2. Check if tag is centered (within ±100px of frame center)
3. **If not centered:** Rotate to center
4. **If centered:** Drive forward
5. **If area ≥ 25,000px²:** STOP (at target!)

**If no tag:**
- Stop and wait

### **Auto-Centering:**
```python
if offset_x > CENTER_TOLERANCE:
    rotate_right()  # Tag on right, turn right
elif offset_x < -CENTER_TOLERANCE:
    rotate_left()   # Tag on left, turn left
else:
    drive_forward() # Centered, go!
```

---

## 🎛️ Configuration (Advanced)

You can adjust these values in the script:

```python
TARGET_AREA = 25000       # Stop distance (larger = closer)
MIN_AREA = 1000           # Ignore tiny/far tags
FORWARD_SPEED = 30        # Driving speed
ROTATION_SPEED = 20       # Turning speed
CENTER_TOLERANCE = 100    # Centering precision (px)
```

**To stop closer to tags:**
```python
TARGET_AREA = 35000  # Stops very close
```

**To stop farther away:**
```python
TARGET_AREA = 15000  # Stops at medium distance
```

---

## 🔍 Troubleshooting

### **Robot doesn't move:**
- ✅ Check battery voltage (needs >7.5V)
- ✅ Verify tag is visible in camera view
- ✅ Make sure tag is tag36h11 family (IDs 582-585)
- ✅ Tag might be too small (too far away)

### **Robot rotates but doesn't drive forward:**
- Tag is off-center (this is normal)
- Wait for robot to center it
- Will drive forward once centered

### **"No tags visible" even when pointing at tag:**
- Tag might be too far (try moving closer)
- Check lighting (tags need good contrast)
- Verify tag is flat (not wrinkled/bent)

### **Robot stops far from tag:**
- Tag area not reaching 25,000 px²
- Tag might be too small (6" instead of 10")
- Increase TARGET_AREA to require closer approach

### **Robot drives past tag:**
- Tag area exceeds target while robot still moving
- Normal behavior, will stop soon
- Reduce FORWARD_SPEED for more precise stopping

---

## 🎓 Educational Value

### **For Students:**

**This demo shows:**
1. **Computer vision** - Real-time tag detection
2. **Feedback control** - Centering and distance control
3. **State machines** - Searching → Centering → Approaching → Stopped
4. **Autonomous behavior** - No human driving needed
5. **Sensor-based navigation** - Uses only camera input

### **For Workshops:**

**Great for:**
- ✅ First autonomous demo (very visual)
- ✅ Testing field setup quickly
- ✅ Showing tag detection range
- ✅ Comparing old vs new tags
- ✅ Debugging navigation issues

---

## 📈 Expected Performance

### **With 10" tag36h11 tags:**

| Distance | Area (px²) | Behavior |
|----------|-----------|----------|
| 3-4m | 2,000-5,000 | Detected, drives forward |
| 2-3m | 5,000-10,000 | Good detection, steady drive |
| 1.5-2m | 10,000-20,000 | Excellent, may rotate to center |
| 1-1.5m | 20,000-30,000 | Very close, stops soon |
| <1m | 30,000+ | **STOP** - at target! |

---

## 🆚 Comparison to PathfinderBot "Follow Me"

### **PathfinderBot Follow Me:**
- Follows **people** (YOLO person detection)
- Tracks largest person in view
- Continuous following behavior
- For demonstrations and fun

### **Point and Drive AprilTag:**
- Drives to **navigation markers** (AprilTags)
- Seeks largest tag in view
- Stops at target (not continuous)
- For navigation testing and field validation

### **Both:**
- ✅ Auto-drive toward target
- ✅ Auto-center target
- ✅ No manual control needed
- ✅ Great for demos

---

## 🎯 Use Cases

### **1. Field Setup Validation:**
Run this script to verify:
- All 4 tags are visible from field center
- Tags are at correct heights
- Tags are properly mounted
- Detection ranges are good

### **2. Tag Performance Testing:**
Measure:
- Detection ranges for each tag
- Final stop distances
- Approach speeds
- Centering accuracy

### **3. Workshop Demonstrations:**
Show students:
- Autonomous navigation in action
- Computer vision working
- Robot decision-making
- Feedback control loops

### **4. Competition Preparation:**
Verify:
- Robot can reach all scoring zones
- Navigation is reliable
- Tags are competition-ready
- Field layout is correct

---

## 💡 Tips

### **For Best Results:**
1. **Start in field center** - Can see multiple tags
2. **Point clearly** - Robot needs tag in view
3. **Wait for stop** - Let robot complete each approach
4. **Good lighting** - Helps tag detection
5. **Flat tags** - Wrinkled tags harder to detect

### **For Demonstrations:**
1. **Show all 4 tags** - Quick tour of field
2. **Explain as it runs** - Point out detection, centering, stopping
3. **Compare to manual** - Show how much easier this is
4. **Let students try** - They can point robot at tags

---

## 🔗 Related Scripts

**Other navigation tools:**
- `navigate_simple_forward.py` - Navigate to specific tag ID
- `test_drive_to_tags.py` - Multi-tag waypoint tour
- `find_apriltag_with_block.py` - Navigate while holding block

**Testing tools:**
- `test_new_tags.py` - Tag detection test with live view
- `calibrate_apriltag_distance.py` - Distance calibration

---

## ✅ Summary

**Point and Drive** is the easiest way to:
- ✅ Test all AprilTags on field
- ✅ Verify navigation working
- ✅ Demonstrate autonomous behavior
- ✅ Validate field setup

**Just point and watch it go!** 🚀

---

*Created: March 23, 2026*  
*Based on PathfinderBot Follow Me concept*  
*Adapted for AprilTag navigation*
