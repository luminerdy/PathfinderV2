# Skill: Sonar Sensors

**Difficulty:** ⭐ (Beginner - Hardware Skill)  
**Type:** Sensor Reading & Obstacle Detection  
**Prerequisites:** D1 (Mecanum Drive recommended)  
**Estimated Time:** 15-20 minutes  

---

## 📘 Overview

### What This Skill Does

Sonar sensors use **ultrasonic sound waves** to measure distance, just like bats navigate in the dark! Your robot uses this to detect obstacles, avoid collisions, and make safe autonomous decisions.

**What you'll learn:**
- How ultrasonic sensors work (echo time = distance)
- Reading sensor data (distance in centimeters)
- Threshold logic (stop, slow, go decisions)
- Visual feedback (RGB LEDs show distance)
- Sensor filtering (deal with noise and outliers)

### Real-World Applications

**In Industry:**
- **Autonomous vehicles:** Park assist, blind-spot detection
- **Warehouse robots:** Collision avoidance, pallet detection
- **Drones:** Landing assistance, obstacle detection
- **Manufacturing:** Part presence detection, gap measurement

**In Everyday Life:**
- **Parking sensors** in your car (beep when close to wall)
- **Automatic doors** (detect when someone approaches)
- **Trash cans** (open lid when hand detected)
- **Water level sensors** in tanks

### Why Ultrasonic Sensors?

**Advantages:**
- ✅ Simple and cheap (~$2-5 per sensor)
- ✅ Works in any lighting (day, night, total darkness)
- ✅ Measures actual distance (not just "something there")
- ✅ Good range (2cm to 4+ meters)
- ✅ No calibration needed (works out of box)

**Limitations:**
- ❌ Narrow beam angle (~15°, can miss small objects)
- ❌ Soft/angled surfaces reflect poorly (foam, carpet)
- ❌ Slow update rate (~20-50ms per reading)
- ❌ Interference from other ultrasonic sources
- ❌ Minimum range (can't see <2cm, too close)

---

## 🚀 Quick Start (Run the Demo)

### Step 1: Understand the Hardware

**Your robot has:**
- **Ultrasonic sensor** (front of robot, looks like two "eyes")
  - Transmitter: Sends 40kHz sound pulse
  - Receiver: Listens for echo
- **RGB LEDs** (two lights near sensor)
  - Visual feedback: Red = close, Yellow = medium, Green = far

**How it works:**
1. Sensor sends ultrasonic "ping" (like shouting "hello!")
2. Sound bounces off objects
3. Sensor hears echo and measures time
4. Distance = (speed of sound × time) / 2

### Step 2: Run the Demo

```bash
cd /home/robot/pathfinder/skills/sonar_sensors
python3 run_demo.py
```

**What happens:**

The robot demonstrates 6 sonar capabilities:

1. **Distance Reading** (10 samples, 0.5s apart)
   - Shows distance in centimeters
   - RGB changes color (red → yellow → green)

2. **Filtered Reading** (average of 10 samples)
   - Removes outliers and noise
   - More accurate than single reading

3. **Obstacle Detection** (20cm threshold)
   - Red LED = obstacle within 20cm
   - Green LED = clear, safe to move
   - Demo: Wave hand in front of sensor

4. **Range Zones** (3 zones: danger, caution, safe)
   - Red (<15cm) = DANGER - emergency stop
   - Yellow (15-30cm) = CAUTION - slow down
   - Green (>30cm) = SAFE - full speed

5. **Movement with Safety** (drives forward, stops if obstacle)
   - Robot moves forward at 40% speed
   - Stops automatically if obstacle detected
   - Demo: Put hand in path, robot stops

6. **Obstacle Avoidance** (turn away from obstacles)
   - Robot drives forward
   - If obstacle ahead, backs up and turns
   - Explores area autonomously

**Success looks like:**
- Distance readings are accurate (measure with ruler, compare)
- RGB colors change based on distance
- Robot stops before hitting obstacle
- Avoidance behavior works (backs up and turns)

### Step 3: Try It Yourself

**Interactive test:**
1. Run the demo
2. During distance reading, move hand closer/farther
3. Watch RGB change color (red → yellow → green)
4. During obstacle detection, wave hand to trigger red
5. During movement, block robot's path (it should stop!)

**RGB LED quick test:**
```bash
# Test RGB LEDs separately (no movement)
cd /home/robot/pathfinder
python3 -c "
from hardware.sonar import Sonar
import time

sonar = Sonar()
colors = [
    ('RED', (255, 0, 0)),
    ('GREEN', (0, 255, 0)),
    ('BLUE', (0, 0, 255)),
    ('YELLOW', (255, 255, 0)),
]

for name, color in colors:
    print(name)
    sonar.set_both_rgb(color)
    time.sleep(1)

sonar.rgb_off()
print('RGB test complete!')
"
```

**What you should see:**
- LEDs glow RED for 1 second
- Then GREEN for 1 second
- Then BLUE for 1 second
- Then YELLOW for 1 second
- Then turn OFF

If LEDs don't light, check troubleshooting section below.

### Step 4: Troubleshooting

**"Distance always shows 400cm" (max range):**
- No object in front (sensor sees "infinity")
- Object too far away (>4m)
- Object at steep angle (sound misses)
- Soft surface (carpet, foam) absorbs sound

**"Distance readings are jumpy/noisy":**
- Normal! Ultrasonic has ~±1cm variation
- Use filtered reading (averages 10 samples)
- Smooth floor = better readings than carpet

**"RGB LEDs don't light up":**
- Check connections (RGB cable plugged in?)
- Verify in code: `sonar.set_both_rgb(...)` called?
- Test with: `python3 -c "from hardware.sonar import Sonar; import time; s = Sonar(); s.set_both_rgb((255,0,0)); time.sleep(2); s.rgb_off()"`
- **Common fix:** If error `'I2CSonar' object has no attribute 'setPixelColor'`, the method name needs to be `set_pixel_color` (snake_case) not `setPixelColor` (camelCase)

**"Robot doesn't stop for obstacles":**
- Threshold too close (increase to 20-30cm)
- Sensor blocked (check mounting)
- Code issue (check `check_obstacles=True` enabled)

**"Readings are wildly wrong (negative, huge, NaN)":**
- Sensor connection loose
- Interference from another ultrasonic source nearby
- Hardware fault (try backup robot)

---

## 🔧 Implementation Guide (For Coders)

### How Ultrasonic Sensors Work

**Physics:**
```
Sound pulse → Travels to object → Bounces back → Received

Speed of sound in air: ~343 m/s (20°C)
Distance = (speed × time) / 2

(Divide by 2 because sound travels there AND back)
```

**Trigger-Echo protocol:**
1. Send 10µs HIGH pulse on trigger pin
2. Sensor emits 8-cycle 40kHz sound burst
3. Echo pin goes HIGH
4. Wait for echo to return
5. Echo pin goes LOW
6. Measure pulse width = round-trip time

**Example calculation:**
```
Echo pulse width: 1000 µs (1 millisecond)
Distance = (343 m/s × 0.001 s) / 2
         = 0.1715 meters
         = 17.15 cm
```

### Code Example (Basic Distance Reading)

```python
from hardware.sonar import Sonar

sonar = Sonar()

# Single reading
distance = sonar.get_distance()
print(f"Distance: {distance:.1f} cm")

# Filtered reading (median of 10 samples)
distance = sonar.get_filtered_distance(samples=10)
print(f"Filtered: {distance:.1f} cm")

# Check if obstacle within threshold
if sonar.is_obstacle_detected(threshold=20):
    print("OBSTACLE DETECTED!")
    sonar.set_both_rgb((255, 0, 0))  # Red
else:
    print("Clear")
    sonar.set_both_rgb((0, 255, 0))  # Green
```

### RGB LED Color Coding

**Standard distance indicators:**
```python
def set_distance_indicator(distance):
    """
    Color-code distance for visual feedback.
    
    Red: <15cm (danger zone, emergency stop)
    Yellow: 15-30cm (caution zone, slow down)
    Green: >30cm (safe zone, full speed)
    """
    if distance < 15:
        sonar.set_both_rgb((255, 0, 0))  # Red
    elif distance < 30:
        sonar.set_both_rgb((255, 255, 0))  # Yellow
    else:
        sonar.set_both_rgb((0, 255, 0))  # Green
```

**Custom colors:**
```python
# Set both LEDs to same color
sonar.set_both_rgb((255, 0, 0))  # Red
sonar.set_both_rgb((0, 255, 0))  # Green
sonar.set_both_rgb((0, 0, 255))  # Blue
sonar.set_both_rgb((255, 255, 0))  # Yellow
sonar.set_both_rgb((255, 0, 255))  # Purple/Magenta
sonar.set_both_rgb((0, 255, 255))  # Cyan
sonar.set_both_rgb((255, 255, 255))  # White

# Set each LED individually (advanced)
sonar.set_rgb(0, (255, 0, 0))  # LED 0 = Red
sonar.set_rgb(1, (0, 255, 0))  # LED 1 = Green

# Turn off
sonar.rgb_off()  # Both LEDs off
```

**RGB LED Test (verify working):**
```python
# Quick test: cycle through colors
from hardware.sonar import Sonar
import time

sonar = Sonar()
colors = [
    ("RED", (255, 0, 0)),
    ("GREEN", (0, 255, 0)),
    ("BLUE", (0, 0, 255)),
    ("YELLOW", (255, 255, 0)),
]

for name, color in colors:
    print(name)
    sonar.set_both_rgb(color)
    time.sleep(1)

sonar.rgb_off()
print("Test complete!")
```

**Implementation Note (Pi 4 I2C):**

The RGB LEDs are controlled via I2C on the Pi 4. The correct method name is `set_pixel_color()` (snake_case), not `setPixelColor()` (camelCase). If you see an AttributeError, the code needs updating:

```python
# CORRECT (snake_case):
self._sonar.set_pixel_color(0, (255, 0, 0))
self._sonar.show()

# WRONG (camelCase - will fail on Pi 4):
self._sonar.setPixelColor(0, (255, 0, 0))
self._sonar.show()
```

This has been fixed in the workshop code, but if you're working with older code or custom implementations, use snake_case method names.

### Sensor Filtering (Dealing with Noise)

**Problem:** Single readings are noisy (±1-2cm variation)

**Solutions:**

**1. Median filter (best for outliers):**
```python
def get_filtered_distance(samples=10):
    """Take multiple readings, return median."""
    readings = []
    for _ in range(samples):
        dist = get_distance()
        if dist and dist > 0:
            readings.append(dist)
        time.sleep(0.01)
    
    if readings:
        return statistics.median(readings)
    return None
```

**2. Moving average (smooth over time):**
```python
class SonarFilter:
    def __init__(self, window_size=5):
        self.window = []
        self.window_size = window_size
    
    def update(self, distance):
        self.window.append(distance)
        if len(self.window) > self.window_size:
            self.window.pop(0)
        return sum(self.window) / len(self.window)
```

**3. Outlier rejection (ignore bad readings):**
```python
def is_valid_reading(distance, min_range=2, max_range=400):
    """Reject physically impossible readings."""
    return distance and min_range <= distance <= max_range
```

### Configuration (config.yaml)

Tune for your environment:

```yaml
sonar:
  # Distance thresholds (centimeters)
  danger_zone: 15      # Red - emergency stop
  caution_zone: 30     # Yellow - slow down
  safe_zone: 50        # Green - full speed
  
  # Sensor parameters
  max_range: 400       # Maximum valid reading (cm)
  min_range: 2         # Minimum valid reading (cm)
  timeout: 0.05        # Echo timeout (seconds)
  
  # Filtering
  filter_samples: 10   # How many samples to average
  outlier_threshold: 50  # Reject readings > 50cm different
  
  # RGB LED colors (R, G, B values 0-255)
  colors:
    danger: [255, 0, 0]    # Red
    caution: [255, 255, 0]  # Yellow
    safe: [0, 255, 0]      # Green
    off: [0, 0, 0]         # LEDs off
  
  # Movement safety
  stop_distance: 15    # Emergency stop if closer (cm)
  slow_distance: 30    # Reduce speed if closer (cm)
  check_interval: 0.1  # How often to check while moving (seconds)
```

### Customization Ideas

**Beginner:**
- Change threshold distances (make danger zone bigger/smaller)
- Customize RGB colors (blue instead of green?)
- Adjust filter samples (more = smoother, slower)

**Intermediate:**
- Add sound alerts (beep when obstacle close)
- Log distance over time (plot in graph)
- Multi-zone detection (left, center, right if multiple sensors)
- Integrate with D1 (stop movement when obstacle)

**Advanced:**
- Kalman filter (optimal sensor fusion)
- Object tracking (follow moving object)
- Mapping (build 2D map by scanning while rotating)
- Multi-sensor fusion (combine sonar + camera + IMU)

---

## 🎓 Engineering Deep Dive (Advanced)

### Ultrasonic Physics

**Sound propagation:**
```
Wavelength λ = v / f

where:
  v = speed of sound = 343 m/s (at 20°C)
  f = frequency = 40,000 Hz (40 kHz)
  
λ = 343 / 40000 = 0.00857 m = 8.57 mm
```

**Why 40 kHz?**
- Above human hearing (20 Hz - 20 kHz)
- Good balance: low enough for decent range, high enough for resolution
- Standard frequency (cheap transducers available)

**Beam pattern:**
- Typical: 15° cone angle
- Objects outside cone not detected
- Small objects may be missed
- Larger objects detected more reliably

### Distance Calculation Accuracy

**Sources of error:**

1. **Temperature dependence:**
```
v = 331.3 + 0.6 * T (m/s)

where T = temperature in °C

At 0°C:  v = 331 m/s  (distance measured 3.5% short)
At 20°C: v = 343 m/s  (calibration reference)
At 40°C: v = 355 m/s  (distance measured 3.5% long)
```

**Temperature compensation:**
```python
def compensate_temperature(raw_distance, temp_celsius):
    """Adjust distance for temperature."""
    v_actual = 331.3 + 0.6 * temp_celsius
    v_calibrated = 343  # Assumed during calibration
    return raw_distance * (v_actual / v_calibrated)
```

2. **Timing resolution:**
- Arduino/Pi GPIO: ~1 µs resolution
- 1 µs error = ±0.017 cm distance error
- Acceptable for most applications

3. **Surface properties:**
- Hard, flat surfaces: Best reflection
- Soft surfaces (foam, cloth): Absorb sound
- Angled surfaces: Reflect away from sensor
- Rounded surfaces: Scatter reflection

### Sensor Characteristics

**Specifications (typical HC-SR04):**
- Operating voltage: 5V DC
- Operating current: 15 mA
- Frequency: 40 kHz
- Range: 2 cm to 400 cm
- Accuracy: ±3 mm (ideal conditions)
- Measuring angle: ~15°
- Trigger pulse: 10 µs
- Echo pulse: 150 µs to 25 ms

**Update rate:**
```
Minimum cycle time = range / (speed of sound / 2) + processing

For 4m range:
t = 4 / (343/2) + overhead
  ≈ 23 ms + 2 ms
  = 25 ms
  
Max update rate ≈ 40 Hz
```

**Practical rate:** 20 Hz (50 ms between readings) recommended to avoid crosstalk.

### Signal Processing

**Median filter (code from earlier):**

**Why median > mean for sonar?**
- Outliers are common (stray reflections, interference)
- Median is robust to outliers
- Mean is pulled by extreme values

**Example:**
```
Readings: [18, 19, 18, 350, 19, 18, 19]  (one bad reading)
Mean: (18+19+18+350+19+18+19)/7 = 65.9 cm  (Way off!)
Median: sort → [18, 18, 18, 19, 19, 19, 350] → 19 cm (Good!)
```

**Kalman filter (optimal estimator):**

For advanced users: Combine sonar + motion model for best estimate.

```python
class SonarKalman:
    """1D Kalman filter for sonar distance."""
    def __init__(self, process_var=1.0, measurement_var=4.0):
        self.x = 0  # State estimate (distance)
        self.P = 100  # Estimate uncertainty
        self.Q = process_var  # Process noise
        self.R = measurement_var  # Measurement noise
    
    def predict(self, velocity_estimate=0, dt=0.05):
        """Predict next state."""
        self.x = self.x + velocity_estimate * dt
        self.P = self.P + self.Q
    
    def update(self, measurement):
        """Update with measurement."""
        K = self.P / (self.P + self.R)  # Kalman gain
        self.x = self.x + K * (measurement - self.x)
        self.P = (1 - K) * self.P
        return self.x
```

### Multi-Sensor Configurations

**Single sensor (front):**
- Simple, cheap
- Detects only straight ahead
- Blind to sides and rear

**Three sensors (front, left, right):**
- 180° coverage
- Can detect which side obstacle is on
- Turn away from obstacle

**Array (5+ sensors, pan-tilt, or rotating):**
- Full 360° coverage
- Build 2D occupancy map
- SLAM (Simultaneous Localization and Mapping)

**Example: Rotating sensor:**
```python
def scan_environment(num_angles=36):
    """
    Rotate robot and scan environment.
    Returns: List of (angle, distance) tuples
    """
    scan = []
    for i in range(num_angles):
        angle = i * (360 / num_angles)
        distance = sonar.get_filtered_distance()
        scan.append((angle, distance))
        
        # Rotate 10°
        board.set_motor_duty([(1, 20), (2, -20), (3, 20), (4, -20)])
        time.sleep(0.05)
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        time.sleep(0.1)
    
    return scan
```

### Obstacle Avoidance Algorithms

**1. Simple threshold (current implementation):**
```
if distance < threshold:
    stop()
```
- Pros: Simple, works
- Cons: Reactive, no planning

**2. Potential field:**
```
Repulsive force from obstacles
Attractive force toward goal

F_repulsive = k / distance²  (gets stronger as closer)
F_attractive = k * distance_to_goal

v_robot = F_attractive + sum(F_repulsive)
```

**3. Vector Field Histogram (VFH):**
- Build polar histogram of obstacles
- Find valleys (clear directions)
- Choose valley closest to goal direction

**4. Dynamic Window Approach (DWA):**
- Consider robot dynamics (can't turn instantly)
- Simulate multiple trajectories
- Choose safest + most goal-directed

### Research Topics

**For advanced students/engineers:**

1. **SLAM with sonar:**
   - Scan environment while moving
   - Build map + track position simultaneously
   - Reference: FastSLAM algorithm

2. **Object recognition:**
   - Analyze reflection patterns
   - Classify objects (wall, person, furniture)
   - Machine learning on echo signatures

3. **Multi-robot coordination:**
   - Ultrasonic communication (one robot "pings", others receive)
   - Relative positioning
   - Collision avoidance between robots

4. **Sensor fusion:**
   - Combine sonar + camera + IMU
   - Complementary strengths (sonar in dark, camera for detail)
   - Kalman filter / particle filter

### Academic References

- **Ultrasonic ranging:** Carullo, A. & Parvis, M. (2001). "An ultrasonic sensor for distance measurement in automotive applications." IEEE Sensors Journal.
- **Obstacle avoidance:** Borenstein, J. & Koren, Y. (1991). "The vector field histogram-fast obstacle avoidance for mobile robots." IEEE Trans. Robotics.
- **Sonar SLAM:** Leonard, J.J. & Durrant-Whyte, H.F. (1991). "Mobile robot localization by tracking geometric beacons." IEEE Trans. Robotics.
- **Sensor fusion:** Thrun, S. et al. (2005). "Probabilistic Robotics." MIT Press. (Chapter 6: Sonar sensors)

---

## Files in This Skill

```
sonar_sensors/
├── SKILL.md                # This file (all 4 sections)
├── run_demo.py             # Level 1: One-click demo
├── config.yaml             # Level 2: Configuration tuning
├── LEARNING_OUTCOMES.md    # Observable outcomes + assessment
├── README.md               # Quick reference
└── diagrams/               # Visual aids
    ├── how_sonar_works.png # Sound pulse diagram
    ├── beam_pattern.png    # 15° cone visualization
    └── threshold_zones.png # Red/yellow/green zones
```

---

*Learn to sense the world - safety first!* 🔊
