# Skill: Camera Vision

**Difficulty:** ⭐⭐ (Intermediate - Computer Vision Basics)  
**Type:** Sensor Input & Image Processing  
**Prerequisites:** None (foundation skill)  
**Estimated Time:** 20-25 minutes  

---

## 📘 Overview

### What This Skill Does

Learn to **capture, display, and process** camera images for computer vision tasks. This is the foundation for all vision-based autonomous behaviors (navigation, object detection, tracking).

**What you'll learn:**
- Camera basics (resolution, FPS, color spaces)
- Image capture and saving
- Display video feed (live preview)
- Color spaces (BGR, RGB, HSV, Grayscale)
- Basic image processing (brightness, contrast, blur, edges)

### Real-World Applications

**In Industry:**
- **Quality control:** Inspect parts for defects
- **Autonomous vehicles:** See road, lanes, obstacles
- **Agriculture:** Count crops, detect disease
- **Security:** Facial recognition, motion detection
- **Medical:** X-ray/MRI analysis, surgical guidance

**In Robotics:**
- **Navigation:** AprilTag detection, visual odometry
- **Manipulation:** Find and grab objects
- **Tracking:** Follow people, balls, or targets
- **Inspection:** Check assembly, read gauges

### Why Computer Vision?

**Advantages:**
- ✅ Rich information (color, shape, texture, depth)
- ✅ Passive sensing (doesn't emit signals like sonar)
- ✅ Works at distance (see far objects)
- ✅ Human-interpretable (we see the same image)

**Limitations:**
- ❌ Lighting dependent (dark = blind, glare = washed out)
- ❌ Computationally expensive (image processing is slow)
- ❌ Requires calibration (camera distortion, perspective)
- ❌ Ambiguity (2D image, lost depth information)

---

## 🚀 Quick Start

### Step 1: Test Camera Hardware

**Check if camera is connected:**
```bash
ls /dev/video*
# Should show: /dev/video0 (or video1, video2...)
```

**Quick capture test:**
```bash
cd /home/robot/pathfinder/skills/camera_vision
python3 test_camera.py
```

**What happens:**
- Camera opens
- Captures 5 frames
- Saves as `test_frame.jpg`
- Shows resolution and FPS

**Success = You see "Camera test complete!" and test_frame.jpg exists**

### Step 2: Live Video Feed

**View camera in real-time:**
```bash
python3 run_demo.py
```

**What you'll see:**
1. Live video window (640x480 default)
2. FPS counter (top-left)
3. Resolution displayed
4. Press 'q' to quit
5. Press 's' to save snapshot

**Troubleshooting:**
- "No camera found" → Check USB connection, run `ls /dev/video*`
- "Permission denied" → Add user to video group: `sudo usermod -a -G video $USER`
- Black screen → Camera blocked or wrong device index
- Blurry → Clean lens, check focus ring

### Step 3: Color Space Demo

**See different color representations:**
```bash
python3 color_spaces.py
```

**What you'll see:**
- Original (BGR)
- RGB (swapped red/blue)
- Grayscale (black & white)
- HSV (Hue-Saturation-Value)

**Why this matters:**
- **BGR:** OpenCV's default (Blue-Green-Red)
- **RGB:** Normal human perception (Red-Green-Blue)
- **Grayscale:** Simple, fast processing (1 channel vs 3)
- **HSV:** Best for color detection (separates color from brightness)

---

## 🔧 Implementation Guide (For Coders)

### Level 1: Capture and Save Image

**Single frame capture:**
```python
import cv2

# Open camera
camera = cv2.VideoCapture(0)

# Set resolution
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Capture frame
ret, frame = camera.read()

if ret:
    # Save image
    cv2.imwrite('captured.jpg', frame)
    print(f"Saved image: {frame.shape[1]}x{frame.shape[0]}")

# Release camera
camera.release()
```

**Resolution options:**
```python
# Low res (fast, small files)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Standard (balanced)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# High res (slow, large files, more detail)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
```

### Level 2: Live Video Display

**Continuous capture and display:**
```python
import cv2

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = camera.read()
    
    if not ret:
        break
    
    # Display frame
    cv2.imshow('Camera', frame)
    
    # Wait 1ms, check for 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
```

**Add FPS counter:**
```python
import time

prev_time = time.time()

while True:
    ret, frame = camera.read()
    
    # Calculate FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    
    # Draw FPS on frame
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Camera', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

### Level 3: Color Space Conversion

**Convert between color spaces:**
```python
import cv2

camera = cv2.VideoCapture(0)
ret, frame = camera.read()

# BGR (OpenCV default - Blue, Green, Red)
bgr = frame  # Already BGR

# RGB (Red, Green, Blue - normal human perception)
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

# Grayscale (single channel, black & white)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

# HSV (Hue, Saturation, Value - best for color detection)
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# Save all versions
cv2.imwrite('bgr.jpg', bgr)
cv2.imwrite('rgb.jpg', rgb)
cv2.imwrite('gray.jpg', gray)
cv2.imwrite('hsv.jpg', hsv)
```

**Why HSV for color detection:**
```python
# Problem with BGR: Brightness affects color
# Bright red: (0, 0, 255)
# Dark red: (0, 0, 100)  # Different!

# Solution: HSV separates color (H) from brightness (V)
# Red (bright): H=0, S=255, V=255
# Red (dark):   H=0, S=255, V=100  # Same hue!

# Detect red objects regardless of lighting:
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
lower_red = np.array([0, 100, 100])    # H, S, V minimums
upper_red = np.array([10, 255, 255])   # H, S, V maximums
mask = cv2.inRange(hsv, lower_red, upper_red)  # Binary mask
```

### Level 4: Image Processing Operations

**Common operations:**
```python
import cv2
import numpy as np

ret, frame = camera.read()

# 1. Brightness adjustment
bright = cv2.add(frame, np.array([50.0]))  # Increase by 50

# 2. Contrast adjustment
contrast = cv2.multiply(frame, np.array([1.5]))  # 1.5x contrast

# 3. Blur (noise reduction)
blur = cv2.GaussianBlur(frame, (15, 15), 0)  # 15x15 kernel

# 4. Edge detection
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
edges = cv2.Canny(gray, 100, 200)  # Low/high thresholds

# 5. Thresholding (binary image)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# 6. Color thresholding (find specific color)
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
lower = np.array([0, 100, 100])  # Red lower bound
upper = np.array([10, 255, 255])  # Red upper bound
mask = cv2.inRange(hsv, lower, upper)
```

### Configuration (config.yaml)

```yaml
camera:
  # Hardware
  device: 0  # /dev/video0 (try 1, 2 if 0 doesn't work)
  
  # Resolution
  width: 640
  height: 480
  
  # Performance
  fps: 30  # Target frames per second
  
  # Image processing
  flip: false  # Flip 180° if camera mounted upside-down
  mirror: false  # Mirror horizontally
  
  # Auto-exposure settings
  auto_exposure: true  # Let camera adjust exposure
  exposure: -1  # Manual exposure value (-1 = auto)
  
  # White balance
  auto_white_balance: true
  
  # Focus (if adjustable)
  auto_focus: true
  focus: -1  # Manual focus value (-1 = auto)

# Color detection ranges (HSV)
colors:
  red:
    lower: [0, 100, 100]
    upper: [10, 255, 255]
  
  green:
    lower: [40, 50, 50]
    upper: [80, 255, 255]
  
  blue:
    lower: [100, 100, 100]
    upper: [130, 255, 255]
  
  yellow:
    lower: [20, 100, 100]
    upper: [30, 255, 255]

# Image save settings
save:
  format: "jpg"  # jpg, png, bmp
  quality: 90  # JPEG quality (0-100)
  directory: "/home/robot/pathfinder/captured_images"
```

---

## 🎓 Engineering Deep Dive (Advanced)

### Camera Hardware Basics

**CCD vs CMOS sensors:**
- **CCD:** Higher quality, more expensive, used in professional cameras
- **CMOS:** Cheaper, lower power, used in webcams/phones (our camera)

**Resolution:**
```
640x480   = VGA   = 307,200 pixels
1280x720  = 720p  = 921,600 pixels (3x VGA)
1920x1080 = 1080p = 2,073,600 pixels (6.75x VGA)

Higher resolution:
  + More detail, better for small objects
  - Slower processing, more memory
```

**Frame rate:**
```
30 FPS = 33ms per frame (smooth for human eye)
60 FPS = 16ms per frame (very smooth, good for fast motion)
15 FPS = 66ms per frame (choppy but usable)

Higher FPS:
  + Catch fast-moving objects, less motion blur
  - More CPU, more data to process
```

### Color Spaces In Depth

**BGR (OpenCV Default):**
- 3 channels: Blue, Green, Red (8 bits each)
- Range: 0-255 per channel
- Total: 16.7 million colors (256³)

**Why BGR not RGB?**
- Historical: Early frame buffers stored Blue first
- OpenCV kept this convention for compatibility

**HSV (Hue, Saturation, Value):**
```
Hue (H):        0-180 (color, circular)
  0-10:    Red
  20-30:   Yellow
  40-80:   Green
  100-130: Blue
  140-170: Purple

Saturation (S): 0-255 (color purity)
  0:   Grayscale (no color)
  255: Pure color

Value (V):      0-255 (brightness)
  0:   Black
  255: Maximum brightness
```

**Why HSV for detection:**
1. Lighting invariance (H channel doesn't change with brightness)
2. Easy thresholding (set H range for color)
3. Handles shadows/highlights better

### Image Processing Algorithms

**Gaussian Blur:**
```
Kernel: 2D Gaussian distribution
Purpose: Noise reduction, smoothing

cv2.GaussianBlur(image, (ksize, ksize), sigma)
  ksize: Kernel size (odd number, e.g., 5, 15, 31)
  sigma: Standard deviation (0 = auto-calculate)

Larger kernel = more blur = slower
```

**Canny Edge Detection:**
```
Steps:
1. Gaussian blur (noise reduction)
2. Gradient calculation (Sobel operator)
3. Non-maximum suppression (thin edges)
4. Hysteresis thresholding (strong/weak edges)

cv2.Canny(gray, low_threshold, high_threshold)
  low: 100 (typical)
  high: 200 (2x-3x low)

Good for: Shape detection, line following
```

**Thresholding:**
```
Binary threshold:
  if pixel > threshold:
      output = 255 (white)
  else:
      output = 0 (black)

Uses: Foreground/background separation, text OCR
```

### Camera Calibration

**Distortion types:**
1. **Radial:** Barrel/pincushion (straight lines curve)
2. **Tangential:** Lens not parallel to sensor

**Calibration process:**
1. Print chessboard pattern
2. Capture 10-20 images at different angles
3. Detect corners: `cv2.findChessboardCorners()`
4. Compute calibration: `cv2.calibrateCamera()`
5. Save camera matrix and distortion coefficients
6. Undistort images: `cv2.undistort()`

**When to calibrate:**
- Precise measurements (distance, size)
- AprilTag pose estimation (accuracy)
- 3D reconstruction
- Not needed for simple color detection

### Performance Optimization

**Reduce resolution:**
```python
# Process at 320x240, display at 640x480
small = cv2.resize(frame, (320, 240))
# ... process small ...
result = cv2.resize(result, (640, 480))
```

**ROI (Region of Interest):**
```python
# Only process center 50% of image
h, w = frame.shape[:2]
roi = frame[h//4:3*h//4, w//4:3*w//4]
```

**Frame skipping:**
```python
frame_count = 0
while True:
    ret, frame = camera.read()
    frame_count += 1
    
    # Only process every 3rd frame
    if frame_count % 3 == 0:
        # Heavy processing here
        detect_objects(frame)
```

---

## Files in This Skill

```
camera_vision/
├── SKILL.md           # This file
├── test_camera.py     # Level 1: Test hardware
├── run_demo.py        # Level 2: Live video + save
├── color_spaces.py    # Level 3: Color conversions
├── config.yaml        # Configuration
└── README.md          # Quick reference
```

---

*See the world through robot eyes!* 📷
