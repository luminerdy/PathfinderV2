# Skill: AprilTag Navigation

**Difficulty:** ⭐⭐⭐ (Intermediate)  
**Type:** Autonomous Navigation  
**Prerequisites:** Basic drive control, camera setup  
**Estimated Time:** 30-45 minutes  

---

## 📘 Overview

### What This Skill Does

AprilTag Navigation enables your robot to **autonomously find and approach** fiducial markers (AprilTags) placed in the environment. Think of it as GPS for indoor robotics - the robot sees the tag, calculates where it is, and drives to it.

**What you'll learn:**
- Computer vision (tag detection)
- Pose estimation (where am I relative to the tag?)
- Proportional control (smooth approach)
- Mecanum drive kinematics (strafe while moving forward)

### Real-World Applications

**In Industry:**
- **Warehouse automation:** Robots navigate to tagged shelf locations
- **Manufacturing:** Automated guided vehicles (AGVs) follow tag waypoints
- **Inspection:** Drones navigate to tagged inspection points
- **Assembly:** Robots locate parts on tagged fixtures

**In Research:**
- Visual odometry (tracking robot position over time)
- SLAM (Simultaneous Localization and Mapping)
- Multi-robot coordination (shared reference frames)

### Why AprilTags?

**Advantages over other methods:**
- ✅ More robust than QR codes (works at angles, partial occlusion)
- ✅ Free and open-source (no licensing fees)
- ✅ Fast detection (real-time on Raspberry Pi)
- ✅ Provides 6-DOF pose (position + orientation in 3D space)
- ✅ Works in varied lighting (unlike some vision systems)

**Limitations:**
- ❌ Requires printed tags in environment (infrastructure needed)
- ❌ Limited range (tag size vs camera resolution trade-off)
- ❌ Sensitive to motion blur (need to stop or use high shutter speed)

---

## 🚀 Quick Start (Run the Demo)

### Step 1: Print AprilTag

Download and print tag36h11 family tags:
- **PDF:** `/home/robot/code/pathfinder/apriltags/tag36h11_singles.pdf`
- **Print size:** 8.5" x 11" (tag will be ~6-8 inches)
- **Tag ID:** 581 (we'll use this for the demo)

**Mounting:**
- Tape to wall at robot's camera height (~8-10 inches off ground)
- Make sure tag is flat and well-lit
- No glare or shadows on the tag

### Step 2: Run the Demo

```bash
cd /home/robot/pathfinder/skills/apriltag_navigation
python3 run_demo.py
```

**What happens:**
1. Camera opens and starts looking for tag 581
2. When found, robot calculates distance and angle
3. Robot approaches using mecanum strafe (smooth!)
4. Stops about 22 inches from the tag
5. Beeps when complete

**Success looks like:**
- Robot drives straight toward tag (even if slightly off-center)
- Smooth approach (no jerky stop-rotate-drive)
- Stops at consistent distance (within ±2 inches)

### Step 3: Troubleshooting

**"No tag detected":**
- Is tag printed clearly (not blurry)?
- Is tag in camera view (640x480 pixels)?
- Check lighting (no glare, no shadows)
- Try moving robot closer (start 3-5 feet away)

**"Robot doesn't move":**
- Check battery voltage (`battery_check.py`)
- Verify motors work (`test_drive.py`)
- Check if sonar is blocking (remove obstacles)

**"Robot approaches but doesn't center":**
- Calibrate camera (see Implementation Guide below)
- Adjust `Kx` gain in config (increase for stronger centering)

**"Robot crashes into tag":**
- Check `TARGET_DISTANCE` in config (increase it)
- Verify sonar is working (should stop at 15cm)

---

## 🔧 Implementation Guide (For Coders)

### How It Works

**Pipeline:**
```
Camera Frame → Grayscale → AprilTag Detector → Pose Estimation → Control Loop → Motors
```

**Key functions:**

#### 1. Tag Detection
```python
from pupil_apriltags import Detector

detector = Detector(families='tag36h11')
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
detections = detector.detect(gray, estimate_tag_pose=True, 
                             camera_params=CAMERA_PARAMS, 
                             tag_size=TAG_SIZE)
```

**Returns:** List of detected tags with:
- `tag_id` - Which tag (0-586 for tag36h11)
- `pose_t` - Translation vector [x, y, z] in meters
- `pose_R` - Rotation matrix (3x3)
- `corners` - Pixel coordinates of tag corners

#### 2. Pose Extraction
```python
x = pose_t[0][0]  # Lateral offset (meters, positive = tag is right)
y = pose_t[1][0]  # Vertical offset (usually ignored)
z = pose_t[2][0]  # Distance (meters, forward)
```

**Coordinate system:**
- **X-axis:** Left (-) to Right (+) from robot's perspective
- **Y-axis:** Down (-) to Up (+) (camera optical axis)
- **Z-axis:** Robot to tag (distance forward)

#### 3. Proportional Control
```python
# Calculate errors
lateral_error = x  # How far off-center
distance_error = z - TARGET_DISTANCE  # How far from target

# Calculate motor speeds (proportional control)
strafe_speed = Kx * lateral_error   # Lateral correction
forward_speed = Kz * distance_error  # Forward approach

# Apply deadbands (don't correct tiny errors)
if abs(lateral_error) < CENTER_TOLERANCE:
    strafe_speed = 0
if abs(distance_error) < DIST_TOLERANCE:
    forward_speed = 0
```

**Why proportional control?**
- Far away → fast approach
- Close → slow approach
- Off-center → strong correction
- Centered → minimal correction
- Result: Smooth, natural-looking movement

#### 4. Mecanum Drive
```python
def drive(strafe, forward):
    """
    Mecanum wheel equations:
    FL = forward + strafe
    FR = forward - strafe
    RL = forward - strafe
    RR = forward + strafe
    """
    fl = forward + strafe
    fr = forward - strafe
    rl = forward - strafe
    rr = forward + strafe
    
    board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])
```

**Why mecanum?**
- Can strafe (sideways) AND drive forward simultaneously
- No need to rotate to center, then drive forward
- Smooth, efficient approach

### Configuration (config.yaml)

Tune these parameters to match your setup:

```yaml
apriltag_navigation:
  # Camera calibration (run calibrate_camera.py to get these)
  camera_fx: 500  # Focal length X (pixels)
  camera_fy: 500  # Focal length Y (pixels)
  camera_cx: 320  # Principal point X (image center)
  camera_cy: 240  # Principal point Y (image center)
  
  # Tag specification
  tag_size: 0.254  # meters (10 inches = 0.254m)
  target_tag_id: 581  # Which tag to navigate to
  
  # Control gains (higher = stronger response)
  gain_lateral: 120   # Kx - strafe correction strength
  gain_forward: 100   # Kz - forward speed
  
  # Tolerances (when to stop correcting)
  center_tolerance: 0.03  # meters (~1.2 inches)
  distance_tolerance: 0.05  # meters (~2 inches)
  
  # Speed limits
  max_speed: 35   # Maximum motor duty
  min_speed: 28   # Minimum to overcome friction
  
  # Target approach distance
  target_distance: 0.55  # meters (~22 inches)
  
  # Safety (sonar)
  sonar_stop_distance: 15   # cm - emergency stop
  sonar_slow_distance: 30   # cm - reduce speed
```

### Customization Ideas

**Beginner:**
- Change `target_tag_id` to navigate to different tags
- Adjust `target_distance` (closer or farther approach)
- Tune `max_speed` (slower for testing, faster for competition)

**Intermediate:**
- Add multi-tag tour (visit tags in sequence)
- Implement tag-relative positioning (approach from specific angle)
- Log performance data (time to reach, accuracy, battery usage)

**Advanced:**
- Implement Kalman filter (smooth noisy pose estimates)
- Add visual odometry (track position between tags)
- Optimize control loop frequency (currently ~30 Hz)
- GPU acceleration for tag detection (if using Jetson)

---

## 🎓 Engineering Deep Dive (Advanced)

### Mathematical Foundation

#### Camera Model (Pinhole Camera)

AprilTag pose estimation requires camera intrinsic parameters. The camera projects 3D world points onto a 2D image plane:

```
[u]   [fx  0  cx] [X]
[v] = [ 0 fy cy] [Y]
[1]   [ 0  0  1] [Z]
```

Where:
- `(u, v)` = pixel coordinates
- `(X, Y, Z)` = 3D point in camera frame
- `fx, fy` = focal lengths (pixels)
- `cx, cy` = principal point (image center)

**To calibrate:** Use OpenCV's `calibrateCamera()` with chessboard pattern.

#### Pose Estimation (PnP - Perspective-n-Point)

Given:
- Known 3D coordinates of tag corners (square with `tag_size`)
- Detected 2D pixel coordinates of corners
- Camera intrinsic matrix

Solve for:
- Translation vector `t = [tx, ty, tz]` (position)
- Rotation matrix `R` (3x3 orientation)

**Algorithm:** Efficient Perspective-n-Point (EPnP) + RANSAC for outlier rejection

**Output pose:**
```python
# Translation (meters)
x = pose_t[0][0]  # Lateral (right is positive)
y = pose_t[1][0]  # Vertical (up is positive)
z = pose_t[2][0]  # Distance (forward)

# Rotation (convert to Euler angles if needed)
yaw, pitch, roll = rotation_matrix_to_euler(pose_R)
```

#### Control Theory (Proportional Control)

Simple P-controller:
```
u(t) = Kp * e(t)

where:
  u(t) = control output (motor speed)
  e(t) = error (desired - actual)
  Kp = proportional gain
```

**For AprilTag navigation:**
```python
# Lateral control (centering)
strafe_speed = Kx * (0 - x)  # Target is x=0 (centered)

# Forward control (distance)
forward_speed = Kz * (TARGET_DISTANCE - z)
```

**Stability analysis:**
- System is stable if Kp < critical gain
- Too low Kp → slow, sluggish response
- Too high Kp → oscillation, overshoot
- Empirical tuning: Start low, increase until slight oscillation, back off 20%

**Why not PID?**
- **I (Integral):** Not needed if steady-state error is acceptable
- **D (Derivative):** Adds noise sensitivity, mecanum friction provides natural damping
- **Simplicity:** P-only controller is easier to tune and understand

#### Mecanum Kinematics

Mecanum wheels have rollers at 45° to the wheel axis. This creates force components:

```
For each wheel:
  Forward component: F * cos(45°) = F/√2
  Lateral component: F * sin(45°) = F/√2
```

**4-wheel configuration:**
```
     FL    FR
      ↘  ↙     (roller angles)
      ↗  ↖
     RL    RR
```

**Inverse kinematics (desired velocity → wheel speeds):**
```
vx = strafe velocity (right is positive)
vy = forward velocity (forward is positive)
ω  = rotation velocity (CCW is positive)

FL = vy + vx + ω * L
FR = vy - vx - ω * L
RL = vy - vx + ω * L
RR = vy + vx - ω * L

where L = wheelbase/2
```

**For pure strafe + forward (no rotation):**
```
FL = forward + strafe
FR = forward - strafe
RL = forward - strafe
RR = forward + strafe
```

**Advantages:**
- Holonomic (can move in any direction without rotating)
- Simultaneous lateral + forward motion (smooth tag approach)
- No need to align before approaching

**Trade-offs:**
- Lower efficiency than standard wheels (~70% due to roller slip)
- More complex mechanics (more parts, higher friction)
- Sensitive to wheel alignment and friction differences

### Performance Optimization

#### Detection Speed

**Baseline:** ~30 FPS on Raspberry Pi 4
**Bottleneck:** AprilTag detection (CPU-bound)

**Optimizations:**
1. **Reduce resolution:** 640x480 → 320x240 (4x faster detection)
2. **Decimate:** `detector.detect(..., decimate=2.0)` - process every 2nd pixel
3. **ROI (Region of Interest):** Only detect in center of frame
4. **Skip frames:** Detect every 2-3 frames, use last known pose for others

**Example:**
```python
# Optimization: Detect at lower res
small_gray = cv2.resize(gray, (320, 240))
detections = detector.detect(small_gray, ...)
# Scale poses back to full resolution
for d in detections:
    d.pose_t *= 2  # 2x scale factor
```

#### Control Loop Frequency

**Current:** ~30 Hz (limited by camera frame rate)
**Sufficient for:** Most navigation tasks
**Could improve:** Faster camera (60+ FPS), hardware encoding

**Latency budget:**
- Camera capture: ~33ms (30 FPS)
- AprilTag detection: ~10ms (320x240)
- Control calculation: <1ms
- Motor command: ~1ms
- **Total:** ~45ms = ~22 Hz effective loop rate

**Good enough?** Yes for <1 m/s navigation speeds.

#### Accuracy

**Pose estimation error:**
- **Translation:** ±1-2 cm at 1m distance
- **Rotation:** ±2-5° at 1m distance
- **Improves with:** Larger tags, better camera calibration, closer distance
- **Degrades with:** Small tags, motion blur, oblique angles (>45°)

**Approach accuracy:**
- **Lateral:** ±1-3 cm (depends on `CENTER_TOLERANCE`)
- **Distance:** ±2-5 cm (depends on `DIST_TOLERANCE`)
- **Repeatability:** High (±1 cm) if environment and battery consistent

### Research Extensions

**For advanced students/engineers:**

1. **Kalman Filtering:** Smooth noisy pose estimates
   - State: [x, y, z, vx, vy, vz]
   - Measurement: AprilTag pose
   - Prediction: Dead reckoning from odometry
   - Reference: Thrun et al., "Probabilistic Robotics"

2. **Visual Odometry:** Track position between tags
   - Feature extraction (ORB, SIFT)
   - Feature matching across frames
   - Estimate camera motion (Essential matrix)
   - Reference: Scaramuzza & Fraundorfer, "Visual Odometry Tutorial"

3. **Multi-Tag Fusion:** Use multiple tags for better localization
   - SLAM (Simultaneous Localization and Mapping)
   - Bundle adjustment
   - Reference: AprilSAM (SLAM with AprilTags)

4. **Machine Learning:** Train tag detector on custom patterns
   - Dataset: Synthetic + real tag images
   - Model: CNN for corner detection
   - Reference: DeepTag (learned fiducial markers)

### Academic References

- **AprilTag:** Olson, E. (2011). "AprilTag: A robust and flexible visual fiducial system." ICRA.
- **AprilTag 2:** Wang, J. & Olson, E. (2016). "AprilTag 2: Efficient and robust fiducial detection." IROS.
- **PnP:** Lepetit et al. (2009). "EPnP: An Accurate O(n) Solution to the PnP Problem." IJCV.
- **Mecanum:** Diegel et al. (2002). "Improved Mecanum Wheel Design for Omni-directional Robots."

---

## Files in This Skill

```
apriltag_navigation/
├── SKILL.md                    # This file (all 4 sections)
├── run_demo.py                 # Level 1: One-click demo
├── config.yaml                 # Level 2: Configuration tuning
├── apriltag_nav_template.py    # Level 3: Fill-in-the-blanks
├── apriltag_nav.py             # Level 4: Full implementation
├── calibrate_camera.py         # Utility: Camera calibration
└── README.md                   # Quick reference
```

**Pick your entry point based on your skill level!**

---

*Need help? Check the troubleshooting section or ask a mentor.*  
*Ready for more? Try the template or full implementation!*
