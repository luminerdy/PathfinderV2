# Motor Speed Calibration

**Finding minimum and maximum reliable motor speeds**

---

## The Problem

**Dead zone:** Motors need minimum voltage/PWM to overcome friction
- Speed 1-19: Motors buzz but don't move
- Speed 20+: Movement starts
- Exact threshold varies by robot, surface, battery voltage

**Maximum limit:** Too fast = unstable
- Wheel slip
- Loss of control
- Sensor lag
- Safety issues

**Result:** Need to know working range for each robot

---

## Quick Calibration

### Run Calibration Tool

```bash
cd ~/code/pathfinder

# Test minimum speeds only (5 minutes)
python3 tools/calibrate_motors.py --test-min

# Test maximum speeds only (5 minutes)
python3 tools/calibrate_motors.py --test-max

# Full calibration (10 minutes)
python3 tools/calibrate_motors.py --full
```

### What It Does

**Minimum speed test:**
1. Tries speed 5, 10, 15, 20...
2. Asks "Did robot move?"
3. Records first speed that works
4. Repeats for forward, strafe, rotate

**Maximum speed test:**
1. Tries increasing speeds
2. Asks "Still stable?"
3. Records last stable speed
4. Repeats for forward, strafe, rotate

---

## Example Session

```
$ python3 tools/calibrate_motors.py --full

Initializing robot...
✓ Robot ready

SAFETY NOTES:
  - Keep robot on floor (not table!)
  - Ensure large clear area
  - Be ready to catch robot if needed

Place robot on open floor. Press Enter to start...

=== MINIMUM SPEED TEST ===

--- Testing FORWARD minimum speed ---
Testing speed 5... Did robot move forward? [y/n]: n
Testing speed 10... Did robot move forward? [y/n]: n
Testing speed 15... Did robot move forward? [y/n]: n
Testing speed 20... Did robot move forward? [y/n]: y
✓ Minimum forward speed: 20

--- Testing STRAFE (sideways) minimum speed ---
Testing speed 5... Did robot strafe right? [y/n]: n
Testing speed 10... Did robot strafe right? [y/n]: n
Testing speed 15... Did robot strafe right? [y/n]: n
Testing speed 20... Did robot strafe right? [y/n]: n
Testing speed 25... Did robot strafe right? [y/n]: y
✓ Minimum strafe speed: 25

--- Testing ROTATION minimum speed ---
Testing rotation 0.1... Did robot rotate? [y/n]: n
Testing rotation 0.15... Did robot rotate? [y/n]: y
✓ Minimum rotation speed: 0.15

=== MAXIMUM SPEED TEST ===

--- Testing FORWARD maximum speed ---
Testing speed 30... Still stable? [y/n]: y
Testing speed 40... Still stable? [y/n]: y
Testing speed 50... Still stable? [y/n]: y
Testing speed 60... Still stable? [y/n]: y
Testing speed 70... Still stable? [y/n]: y
Testing speed 80... Still stable? [y/n]: y
Testing speed 90... Still stable? [y/n]: n
✓ Maximum forward speed: 80

(Similar for strafe and rotation...)

=== COMPLETE CALIBRATION RESULTS ===

Add to config.yaml:
```yaml
hardware:
  chassis:
    min_speed_forward: 20
    min_speed_strafe: 25
    min_speed_rotate: 0.15
    max_speed_forward: 80
    max_speed_strafe: 75
    max_speed_rotate: 0.7
```
```

---

## Manual Testing

If calibration tool doesn't work, test manually:

### Test Forward Minimum

```bash
python3 << 'EOF'
from hardware import Board, Chassis
import time

board = Board()
chassis = Chassis(board)

# Try different speeds
for speed in [5, 10, 15, 20, 25, 30]:
    print(f"Testing forward speed {speed}...")
    chassis.set_velocity(speed, 0, 0)
    time.sleep(2)
    chassis.stop()
    
    response = input("Did it move? [y/n]: ")
    if response == 'y':
        print(f"Minimum forward speed: {speed}")
        break
    time.sleep(1)

board.close()
EOF
```

### Test Strafe Minimum

```bash
python3 << 'EOF'
from hardware import Board, Chassis
import time

board = Board()
chassis = Chassis(board)

# Try different speeds
for speed in [5, 10, 15, 20, 25, 30, 35]:
    print(f"Testing strafe speed {speed}...")
    chassis.set_velocity(0, speed, 0)  # Strafe right
    time.sleep(2)
    chassis.stop()
    
    response = input("Did it strafe? [y/n]: ")
    if response == 'y':
        print(f"Minimum strafe speed: {speed}")
        break
    time.sleep(1)

board.close()
EOF
```

---

## Typical Values

**Based on MasterPi-style robots:**

| Movement | Minimum | Maximum | Notes |
|----------|---------|---------|-------|
| Forward  | 20-25   | 80-100  | Depends on surface |
| Strafe   | 25-30   | 75-90   | Mecanum less efficient |
| Rotate   | 0.15-0.2| 0.7-1.0 | Angular velocity |

**Factors affecting speed:**
- **Surface:** Carpet higher minimum than smooth floor
- **Battery:** Low battery = higher minimum needed
- **Wheel condition:** Worn wheels = less traction
- **Weight:** Heavier robot = higher minimum
- **Motor quality:** Varies by manufacturer

---

## Updating Code

### Method 1: Configuration File

Edit `config.yaml`:
```yaml
hardware:
  chassis:
    min_speed_forward: 20  # Your calibrated value
    min_speed_strafe: 25
    min_speed_rotate: 0.15
    max_speed_forward: 80
    max_speed_strafe: 75
    max_speed_rotate: 0.7
```

*(This requires updating chassis.py to read from config)*

### Method 2: Direct in Code

Edit `capabilities/pickup.py`:
```python
class VisualPickupController:
    def __init__(self, robot):
        # Speed limits (calibrated values)
        self.min_speed_forward = 20  # ← Your value
        self.min_speed_strafe = 25   # ← Your value
        self.min_speed_rotate = 0.15
        self.max_speed_forward = 80
        self.max_speed_strafe = 75
        self.max_speed_rotate = 0.7
```

Edit `capabilities/navigation.py`:
```python
class Navigator:
    def __init__(self, robot):
        # Speed limits
        self.min_speed = 20  # ← Your value
        self.max_speed = 80
        self.slow_speed = 20  # Must be >= min_speed
```

---

## Why This Matters

### Without Calibration

**Code tries speed 15:**
```python
chassis.set_velocity(15, 0, 0)  # Too slow!
# Motors buzz, robot doesn't move
# Timeout waiting for block to get closer
# Pickup fails
```

**Code tries speed 100:**
```python
chassis.set_velocity(100, 0, 0)  # Too fast!
# Robot overshoots
# Wheels slip
# Loses tracking of block
# Crashes into obstacles
```

### With Calibration

**Enforces minimum:**
```python
speed = max(min_speed, calculated_speed)
# Always >= 20, motors always move
```

**Enforces maximum:**
```python
speed = min(max_speed, calculated_speed)
# Never > 80, stays stable
```

**Result:**
- Reliable movement
- Predictable behavior
- Better success rates

---

## Current Code Status

**Speed limits already added to:**
- ✅ `capabilities/pickup.py` (min/max enforced)
- ✅ `capabilities/navigation.py` (min/max enforced)

**Default values (conservative):**
```python
min_speed_forward = 20
min_speed_strafe = 20
min_speed_rotate = 0.2
max_speed_forward = 80
max_speed_strafe = 80
max_speed_rotate = 0.8
```

**To customize:**
1. Run calibration tool
2. Update values in code
3. Test pickup and navigation
4. Adjust if needed

---

## Troubleshooting

### "Robot doesn't move during fine positioning"

**Cause:** Calculated speed below minimum

**Check:**
```python
# In pickup.py _fine_position_block()
print(f"Forward speed: {forward_speed}")
print(f"Strafe speed: {strafe_speed}")
print(f"Min forward: {self.min_speed_forward}")
```

**Fix:** Increase minimum speeds

### "Robot overshoots during approach"

**Cause:** Maximum speed too high

**Fix:** Reduce `max_speed_forward` by 10-20

### "Different on carpet vs floor"

**Expected!** Surface affects friction.

**Solution:** Calibrate for your primary surface, or:
```python
# Surface-dependent speeds
if surface == 'carpet':
    min_speed = 30
else:
    min_speed = 20
```

### "Strafe minimum higher than forward"

**Normal!** Mecanum strafing is less efficient than forward.

**Typical:** Forward min=20, Strafe min=25-30

---

## Advanced: Adaptive Speeds

**Future enhancement:** Auto-calibrate during operation

```python
def auto_calibrate_minimum(chassis):
    """
    Automatically find minimum speed
    """
    for speed in range(5, 51, 5):
        chassis.set_velocity(speed, 0, 0)
        time.sleep(1)
        
        # Check if moved (needs encoders or visual odometry)
        if detected_movement():
            return speed
    
    return 20  # Fallback
```

**Requires:**
- Motor encoders (not available on current robot)
- Visual odometry (possible with camera)
- IMU for rotation detection (not available)

---

## Summary

**Motor speed calibration:**

✅ **Find dead zone** - Speed below which motors don't move  
✅ **Find safe maximum** - Speed above which robot unstable  
✅ **Update code** - Enforce limits in navigation and pickup  
✅ **Test and refine** - Adjust based on real performance  

**Tools:**
```bash
# Automated calibration
python3 tools/calibrate_motors.py --full

# Manual testing
python3 -c "from hardware import *; ..."
```

**Typical values:**
- Forward min: 20-25
- Strafe min: 25-30
- Rotate min: 0.15-0.2

**Impact:**
- Reliable movement
- Better pickup success
- Smoother navigation

---

**Run calibration before serious testing!** 🤖⚡

Your specific robot + surface + battery combination determines optimal speeds.
