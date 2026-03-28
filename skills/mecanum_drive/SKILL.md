# Skill: Mecanum Drive

**Difficulty:** ⭐ (Beginner - Foundation Skill)  
**Type:** Hardware Control  
**Prerequisites:** None (start here!)  
**Estimated Time:** 15-20 minutes  

---

## 📘 Overview

### What This Skill Does

Mecanum drive gives your robot **omnidirectional movement** - it can move forward, backward, left, right, diagonally, and rotate in place without turning. This is your robot's superpower compared to regular wheeled robots!

**What you'll learn:**
- How mecanum wheels work (45° rollers create multi-directional force)
- Motor control (duty cycle, direction, coordination)
- Movement patterns (forward, strafe, rotate, diagonal, curves)
- Coordinate systems (robot-centric vs world-centric movement)

### Real-World Applications

**In Industry:**
- **Warehouse robots:** AGVs (Automated Guided Vehicles) navigate tight aisles
- **Manufacturing:** Assembly line robots position precisely without rotating
- **Airports:** Baggage handling systems move in any direction
- **Hospitals:** Mobile robots deliver supplies through narrow hallways

**In Competition:**
- **FIRST Robotics:** Holonomic drive dominates field positioning
- **RoboCup:** Soccer robots strafe while facing the ball
- **Battlebot-style:** Quick directional changes for offense/defense

### Why Mecanum Wheels?

**Advantages:**
- ✅ Omnidirectional (move any direction instantly)
- ✅ No turning radius needed (great for tight spaces)
- ✅ Simultaneous translation + rotation (approach while facing target)
- ✅ Precise positioning (fine adjustments in any axis)

**Trade-offs:**
- ❌ ~30% efficiency loss (roller slip compared to standard wheels)
- ❌ More complex mechanics (more parts, higher friction)
- ❌ Sensitive to floor surface (smooth floors best)
- ❌ Requires perfect weight distribution (uneven weight = drift)

---

## 🚀 Quick Start (Run the Demo)

### Step 1: Prepare Robot

**Safety first:**
- Clear at least 6 feet of space around robot
- Robot on floor (not on table - it WILL move!)
- Battery charged (check voltage: should be >7.0V)
- Emergency stop ready (you = Ctrl+C)

### Step 2: Run the Demo

```bash
cd /home/robot/pathfinder/skills/mecanum_drive
python3 run_demo.py
```

**What happens:**

The robot demonstrates 8 movement patterns in sequence:

1. **Forward** (2 seconds)
2. **Backward** (2 seconds)
3. **Strafe Right** (2 seconds)
4. **Strafe Left** (2 seconds)
5. **Rotate Clockwise** (90°)
6. **Rotate Counter-Clockwise** (90°)
7. **Diagonal** (forward-right, 2 seconds)
8. **Square Pattern** (1-meter sides)

**Success looks like:**
- Robot moves smoothly in each direction
- Strafe is truly sideways (no forward/backward component)
- Rotation is in-place (no translation)
- Square pattern closes (returns to start point ±6 inches)

### Step 3: Understand What You Saw

**Key observations:**

**Strafe (sideways movement):**
- Robot moves left/right WITHOUT rotating
- This is impossible with standard wheels!
- Wheels spin in specific pattern to create lateral force

**Rotation in place:**
- Robot spins without moving forward/backward
- All 4 wheels contribute to rotation
- Useful for aligning with targets

**Diagonal movement:**
- Combines forward + strafe simultaneously
- Fastest path between two points (for mecanum)
- Natural motion, not "drive then turn then drive"

### Step 4: Troubleshooting

**"Robot doesn't move":**
- Check battery: `python3 ../../tests/battery_check.py`
- Verify motors: `python3 ../../tests/test_motors.py`
- Look for red LED on board (low voltage warning)

**"Robot moves but in wrong direction":**
- Motor wiring might be reversed (common on assembly)
- Check `config.yaml` → `motor_directions` settings
- Some motors may need inversion (1 → -1)

**"Strafe is crooked (robot rotates while strafing)":**
- Wheels not mounted correctly (45° angle matters!)
- Floor too slippery or too rough
- Weight distribution uneven (battery position)

**"Square pattern doesn't close":**
- Normal! Open-loop control drifts
- Better with: encoder wheels, IMU, or visual feedback
- For now: Good enough if within 6 inches

---

## 🔧 Implementation Guide (For Coders)

### How Mecanum Wheels Work

**Physical design:**
```
Each wheel has rollers at 45° to the wheel's axis.

     Wheel rotation
          ↓
    ╱╲╱╲╱╲╱╲   ← Rollers (45°)
    |      |
    
When wheel spins:
- Forward component: along wheel axis
- Lateral component: perpendicular (from rollers)
```

**4-wheel configuration:**
```
Front of robot (camera)
     ↑
  FL   FR      FL = Front-Left (↘ rollers)
   ↘ ↙         FR = Front-Right (↙ rollers)
   ↗ ↖         RL = Rear-Left (↗ rollers)
  RL   RR      RR = Rear-Right (↖ rollers)
```

**Force vectors:**

When FL wheel spins forward:
- Forward force: 0.707 (cos 45°)
- Rightward force: 0.707 (sin 45°)

By controlling all 4 wheels, we can combine forces to move in any direction!

### Inverse Kinematics Equations

**Desired motion → Wheel speeds**

Given:
- `vx` = strafe velocity (right is positive)
- `vy` = forward velocity (forward is positive)
- `ω` = rotation velocity (CCW is positive)
- `L` = wheelbase/2 (distance from center to wheel)

**Wheel speed equations:**
```python
FL = vy + vx + ω * L
FR = vy - vx - ω * L
RL = vy - vx + ω * L
RR = vy + vx - ω * L
```

**Derivation intuition:**
- **Forward (vy):** All wheels spin forward together
- **Strafe (vx):** FL/RR forward, FR/RL backward (creates lateral motion)
- **Rotate (ω):** Left wheels forward, right wheels backward (spin in place)

### Code Example (Basic Movement)

```python
from lib.board import get_board

board = get_board()

def drive_mecanum(vx, vy, omega, wheelbase=0.2):
    """
    Drive with mecanum wheels.
    
    Args:
        vx: Strafe speed (-100 to 100, positive = right)
        vy: Forward speed (-100 to 100, positive = forward)
        omega: Rotation speed (-100 to 100, positive = CCW)
        wheelbase: Robot wheelbase in meters (for rotation scaling)
    
    Returns:
        None (sends motor commands directly)
    """
    # Calculate wheel speeds
    L = wheelbase / 2
    fl = vy + vx + omega * L * 100  # Scale omega for duty cycle
    fr = vy - vx - omega * L * 100
    rl = vy - vx + omega * L * 100
    rr = vy + vx - omega * L * 100
    
    # Normalize if any wheel exceeds 100
    max_speed = max(abs(fl), abs(fr), abs(rl), abs(rr))
    if max_speed > 100:
        scale = 100 / max_speed
        fl *= scale
        fr *= scale
        rl *= scale
        rr *= scale
    
    # Send to motors (clamp to -100 to 100)
    board.set_motor_duty([
        (1, int(max(-100, min(100, fl)))),  # FL
        (2, int(max(-100, min(100, fr)))),  # FR
        (3, int(max(-100, min(100, rl)))),  # RL
        (4, int(max(-100, min(100, rr))))   # RR
    ])

# Examples:
drive_mecanum(0, 50, 0)    # Forward at 50% speed
drive_mecanum(50, 0, 0)    # Strafe right at 50%
drive_mecanum(0, 0, 30)    # Rotate CCW at 30%
drive_mecanum(50, 50, 0)   # Diagonal (forward-right) at 50%
```

### Configuration (config.yaml)

Tune these for your robot:

```yaml
mecanum_drive:
  # Speed limits (duty cycle 0-100)
  max_speed: 50       # Maximum speed for demos
  min_speed: 25       # Minimum to overcome friction
  
  # Motor inversions (if motors wired backward)
  # Set to -1 to reverse, 1 for normal
  motor_directions:
    front_left: 1     # Motor 1
    front_right: 1    # Motor 2
    rear_left: 1      # Motor 3
    rear_right: 1     # Motor 4
  
  # Robot dimensions (meters)
  wheelbase: 0.20     # Distance between left and right wheels
  track_width: 0.20   # Distance between front and back wheels
  wheel_diameter: 0.065  # Wheel diameter in meters
  
  # Movement durations (seconds) for demo
  demo_duration: 2.0  # How long each movement lasts
  demo_pause: 1.0     # Pause between movements
  
  # Square pattern parameters
  square_side: 1.0    # Side length in meters
  square_speed: 35    # Speed for square pattern
```

### Customization Ideas

**Beginner:**
- Change `max_speed` (make it faster or slower)
- Adjust `demo_duration` (longer movements to see better)
- Try different square sizes (`square_side`)

**Intermediate:**
- Add new patterns (triangle, circle, figure-8)
- Implement joystick control (read gamepad → drive)
- Log odometry (estimate position from wheel speeds)

**Advanced:**
- Forward kinematics (wheel speeds → robot velocity)
- Closed-loop control (use encoders to track actual position)
- Field-centric drive (move relative to field, not robot)
- Slip compensation (adjust for wheel slip on different surfaces)

---

## 🎓 Engineering Deep Dive (Advanced)

### Mecanum Wheel Mechanics

**Roller contact physics:**

Each roller contacts the ground at a single point. As the wheel rotates, different rollers make contact sequentially. The effective contact force is the vector sum of:

1. **Tangential component** (wheel rotation)
2. **Roller slip** (perpendicular to wheel axis)

**Force decomposition:**

For a roller at angle θ = 45° to wheel axis:

```
F_wheel = [F_x, F_y] where:
  F_x = F * cos(θ) = 0.707 * F  (along wheel axis)
  F_y = F * sin(θ) = 0.707 * F  (perpendicular)
```

**4-wheel force summation:**

```
Robot body forces:
F_x_robot = F_FL + F_FR + F_RL + F_RR (lateral)
F_y_robot = F_FL - F_FR - F_RL + F_RR (forward)
τ_robot = (F_FL - F_FR + F_RL - F_RR) * L (torque)
```

Where L = distance from center to wheel.

### Inverse Kinematics Derivation

**Problem:** Given desired robot velocity [vx, vy, ω], find wheel speeds [ω1, ω2, ω3, ω4].

**Coordinate frames:**
- Robot frame: Origin at robot center, +X right, +Y forward
- Wheel frame: Origin at wheel center, +X along wheel axis

**Transformation matrices:**

For each wheel position (xi, yi) and roller angle αi:

```
[ vwx ]   [ cos(αi)  sin(αi) ] [ vx - ω*yi ]
[ vwy ] = [-sin(αi)  cos(αi) ] [ vy + ω*xi ]
```

Where (vwx, vwy) is velocity in wheel frame.

**Wheel speed:**

```
ω_wheel = vwx / r
```

Where r = wheel radius.

**For standard mecanum (45° rollers, square wheelbase):**

```
FL = (vy + vx + ω*L) / r
FR = (vy - vx - ω*L) / r
RL = (vy - vx + ω*L) / r
RR = (vy + vx - ω*L) / r
```

**Matrix form:**

```
[ω_FL]   [1   1   L] [vy]
[ω_FR] = [1  -1  -L] [vx] * (1/r)
[ω_RL]   [1  -1   L] [ω ]
[ω_RR]   [1   1  -L]
```

### Forward Kinematics (Odometry)

**Problem:** Given measured wheel speeds, estimate robot velocity.

**Moore-Penrose pseudoinverse:**

```
[vy]       [ω_FL]
[vx] = M⁺ [ω_FR] * r
[ω ]       [ω_RL]
            [ω_RR]

where M⁺ = (MᵀM)⁻¹Mᵀ (pseudoinverse of kinematic matrix)
```

**For square wheelbase:**

```
vx = (ω_FL - ω_FR - ω_RL + ω_RR) * r / 4
vy = (ω_FL + ω_FR + ω_RL + ω_RR) * r / 4
ω  = (ω_FL - ω_FR + ω_RL - ω_RR) * r / (4*L)
```

**Odometry integration:**

```
x(t+dt) = x(t) + vx*cos(θ) - vy*sin(θ) * dt
y(t+dt) = y(t) + vx*sin(θ) + vy*cos(θ) * dt
θ(t+dt) = θ(t) + ω * dt
```

**Accuracy issues:**
- Wheel slip (especially on turns)
- Roller compliance (not perfect rigid contact)
- Weight distribution effects
- Floor surface variations

**Typical accuracy:** ±5-10% position error after 10 meters (without correction)

### Slip Analysis

**Why mecanum wheels slip:**

1. **Roller compliance:** Rollers deform under load
2. **Lateral friction:** Sideways forces exceed static friction
3. **Rotation coupling:** All 4 wheels must slip slightly to achieve pure strafe
4. **Floor interaction:** Smooth floors slip more than textured

**Effective efficiency:**

For pure strafe (vx only):
- Theoretical: 100% (perfect rollers)
- Actual: 65-75% (roller slip + friction)

For pure forward (vy only):
- Theoretical: 100%
- Actual: 85-95% (minor roller drag)

**Optimization strategies:**
- Heavier robot (more normal force, less slip)
- Textured floor (better grip)
- Compliant rollers (trade speed for traction)
- Predictive slip compensation (model + correct)

### Control Theory Extensions

**Open-loop (current implementation):**
- Set motor speeds, hope robot goes where expected
- No feedback, drift accumulates
- Simple, fast, good for demos

**Closed-loop improvements:**

1. **Encoder feedback:**
   - Measure actual wheel speeds
   - PID control to match desired speeds
   - Reduces motor variability

2. **IMU (Inertial Measurement Unit):**
   - Measure actual heading (gyroscope)
   - Correct rotation drift
   - Essential for straight-line accuracy

3. **Visual odometry:**
   - Track features in camera view
   - Estimate actual motion
   - Corrects all drift sources

4. **Sensor fusion (Kalman filter):**
   - Combine encoders + IMU + vision
   - Optimal state estimate
   - Production-grade localization

### Field-Centric Drive

**Problem:** Robot-centric drive feels weird when robot is rotated.

**Solution:** Transform desired motion to robot frame first.

```python
def drive_field_centric(field_vx, field_vy, omega, robot_heading):
    """
    Drive relative to field, not robot.
    
    Args:
        field_vx: Desired velocity in field X (right)
        field_vy: Desired velocity in field Y (forward)
        omega: Rotation speed (same as robot frame)
        robot_heading: Current robot angle (radians)
    
    Returns:
        (robot_vx, robot_vy, omega) in robot frame
    """
    cos_h = math.cos(robot_heading)
    sin_h = math.sin(robot_heading)
    
    # Rotation matrix transformation
    robot_vx = field_vx * cos_h + field_vy * sin_h
    robot_vy = -field_vx * sin_h + field_vy * cos_h
    
    return robot_vx, robot_vy, omega
```

**Use case:** Competition robots maintain field awareness (always know "forward" even when spinning).

### Research Topics

**For advanced students/engineers:**

1. **Optimal trajectory planning:**
   - Given start/end pose + obstacles, plan minimum-time path
   - Account for mecanum dynamics (acceleration limits, slip)
   - Reference: Holonomic trajectory generation (FRC papers)

2. **Model predictive control (MPC):**
   - Predict future states over horizon
   - Optimize control sequence
   - Handles constraints naturally

3. **Adaptive slip estimation:**
   - Learn slip model online
   - Adjust control based on observed performance
   - Machine learning approach: train neural net for slip prediction

4. **Multi-robot coordination:**
   - Formations with holonomic robots
   - Collision avoidance with omnidirectional escape
   - Reference: Distributed control papers

### Academic References

- **Mecanum wheel kinematics:** Taheri, H. et al. (2015). "Omnidirectional Mobile Robots." In: Springer Handbook of Robotics.
- **Odometry accuracy:** Borenstein, J. & Feng, L. (1996). "Measurement and Correction of Systematic Odometry Errors." IEEE Trans. Robotics.
- **Slip modeling:** Muir, P.F. & Neuman, C.P. (1987). "Kinematic Modeling of Wheeled Mobile Robots." J. Robotic Systems.
- **Field-centric drive:** FIRST Robotics resources: "Holonomic Drive Programming" (team documentation).

---

## Files in This Skill

```
mecanum_drive/
├── SKILL.md                # This file (all 4 sections)
├── run_demo.py             # Level 1: One-click demo
├── config.yaml             # Level 2: Configuration tuning
├── README.md               # Quick reference
└── diagrams/               # Visual aids
    ├── wheel_forces.png    # Force vector diagrams
    ├── robot_layout.png    # 4-wheel configuration
    └── movement_patterns.gif # Animated demo
```

---

*Master this first - all navigation skills build on mecanum control!* 🎯
