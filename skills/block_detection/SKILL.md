# Skill: Block Detection (E3)

**Difficulty:** ⭐⭐ (Intermediate - Computer Vision Application)  
**Type:** Vision + Color Detection  
**Prerequisites:** D4 (Camera Vision)  
**Estimated Time:** 20-25 minutes  

---

## Overview

### What This Skill Does

Detect colored blocks on the floor using **HSV color filtering**. Returns block position, estimated distance, color, and confidence. This is the foundation for all autonomous manipulation tasks.

**What you'll learn:**
- HSV color thresholding (separate color from brightness)
- Contour detection (find object boundaries)
- Distance estimation from known object size
- Confidence scoring (filter false positives)
- Multi-color detection (red, blue, yellow)

### Real-World Applications

- **Warehouse sorting:** Identify packages by color/label
- **Agriculture:** Detect ripe fruit (color change)
- **Recycling:** Sort materials by visual properties
- **Quality control:** Reject parts with wrong color
- **FIRST Robotics:** Game piece detection (every season)

### How It Works (Pipeline)

```
Camera Frame (BGR)
    |
    v
Convert to HSV (separate color from brightness)
    |
    v
Color Threshold (create binary mask for target color)
    |
    v
Morphology (clean up noise: open + close)
    |
    v
Find Contours (detect blob boundaries)
    |
    v
Filter (area, aspect ratio, confidence)
    |
    v
Distance Estimation (known size + focal length)
    |
    v
BlockDetection objects (color, position, distance, confidence)
```

---

## Quick Start

### Step 1: Run Detection Demo

```bash
cd /home/robot/pathfinder
python3 skills/block_detect.py
```

**What happens:**
1. Camera captures 5 frames
2. Detects red, blue, and yellow blocks
3. Shows color, distance, pixel offset, confidence
4. Saves annotated frame as `block_detect_result.jpg`

**Try this:**
- Place a colored block 30-50cm in front of camera
- Run detection
- Move block closer/farther, watch distance change
- Try different colors

**Success = You detect a block with correct color and reasonable distance!**

### Step 2: Understand the Output

```
Detected 1 block(s):
  red: 25cm away, 48x45px, offset=+15px, conf=0.80
```

**What each field means:**
- **red:** Detected color (from HSV thresholding)
- **25cm:** Estimated distance (from pixel size + known block width)
- **48x45px:** Bounding box size in pixels
- **offset=+15px:** Pixels right of center (+) or left (-)
- **conf=0.80:** Detection confidence (0.0-1.0)

### Step 3: Test Multiple Colors

Place blocks of different colors and run:
```bash
python3 -c "
import cv2, time, sys
sys.path.insert(0, '.')
from skills.block_detect import BlockDetector

camera = cv2.VideoCapture(0)
time.sleep(1.5)
detector = BlockDetector()

ret, frame = camera.read()
blocks = detector.detect(frame)

print('Detected %d blocks:' % len(blocks))
for b in blocks:
    print('  %s: %.0fcm, conf=%.2f, offset=%+dpx' % (
        b.color, b.estimated_distance_mm/10, b.confidence, b.offset_from_center))

camera.release()
"
```

---

## Implementation Guide (For Coders)

### Level 2: Use the BlockDetector Class

```python
from skills.block_detect import BlockDetector

# Create detector (detects all colors by default)
detector = BlockDetector()

# Detect all blocks
blocks = detector.detect(frame)

# Detect only red blocks
red_blocks = detector.detect(frame, colors=['red'])

# Find nearest block of any color
nearest = detector.find_nearest(frame)

# Find nearest red block
nearest_red = detector.find_nearest(frame, color='red')

# Draw detection boxes on frame
annotated = detector.annotate_frame(frame, blocks)
cv2.imwrite('detected.jpg', annotated)
```

### Level 3: Understand HSV Thresholding

**Why HSV instead of BGR?**

```python
# Problem: Same red block under different lighting
# Bright room: BGR = (0, 0, 255)  -- pure red
# Dim room:    BGR = (0, 0, 80)   -- dark red
# Different BGR values for SAME object!

# Solution: HSV separates color (H) from brightness (V)
# Bright room: HSV = (0, 255, 255)  -- H=0 (red)
# Dim room:    HSV = (0, 255, 80)   -- H=0 (still red!)
# Same Hue regardless of lighting!
```

**Color ranges (tuned for indoor lighting):**

```python
COLOR_RANGES = {
    'red': [
        {'lower': (0, 80, 50), 'upper': (10, 255, 255)},    # Low hue red
        {'lower': (160, 80, 50), 'upper': (180, 255, 255)},  # High hue red (wraps!)
    ],
    'blue': [
        {'lower': (100, 60, 50), 'upper': (130, 255, 255)},
    ],
    'yellow': [
        {'lower': (20, 80, 50), 'upper': (40, 255, 255)},
    ],
}
```

**Why red has TWO ranges:**
- Hue is circular (0-180)
- Red wraps around: H=0 and H=180 are both red
- Need two ranges to catch both ends

**Tuning tips:**
- **Too many false positives:** Increase S_min (require more saturated color)
- **Missing detections:** Decrease S_min and V_min (accept dimmer objects)
- **Wrong color:** Adjust H range (use color_spaces.py to check actual values)

### Level 3: Distance Estimation

**Pinhole camera model:**
```
pixel_width = (focal_length * real_width) / distance

Rearranged:
distance = (focal_length * real_width) / pixel_width
```

**Our values:**
```python
FOCAL_LENGTH = 500   # pixels (estimated for 640x480)
BLOCK_SIZE = 30      # mm (1.2 inch blocks)

# Example: Block appears 50px wide
distance = (500 * 30) / 50 = 300mm = 30cm
```

**Accuracy:**
- Close range (<30cm): +/- 3cm (good)
- Medium range (30-60cm): +/- 8cm (acceptable)
- Far range (>60cm): +/- 15cm (rough estimate)
- Accuracy depends on: block orientation, lens distortion, HSV precision

### Level 4: Build Custom Detector

```python
import cv2
import numpy as np

def detect_custom_color(frame, h_low, h_high, s_min=80, v_min=50):
    """
    Detect objects of a custom color.
    
    Args:
        frame: BGR image
        h_low, h_high: Hue range (0-180)
        s_min: Minimum saturation
        v_min: Minimum value (brightness)
    
    Returns:
        List of (center_x, center_y, area) tuples
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    lower = np.array([h_low, s_min, v_min])
    upper = np.array([h_high, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    # Clean up noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    
    results = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 30:  # Skip tiny blobs
            continue
        
        M = cv2.moments(c)
        if M['m00'] > 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            results.append((cx, cy, area))
    
    return sorted(results, key=lambda r: r[2], reverse=True)
```

---

## Engineering Deep Dive (Advanced)

### Morphological Operations

**Why we need cleanup:**
- Raw HSV thresholding produces noisy masks
- Specular highlights create false positives
- Shadow edges create gaps in real objects

**Opening (erosion then dilation):**
```
Purpose: Remove small noise blobs
Effect: Deletes objects smaller than kernel
kernel = np.ones((3, 3))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
```

**Closing (dilation then erosion):**
```
Purpose: Fill small holes in objects
Effect: Connects nearby regions
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
```

### Contour Analysis

**Finding contours:**
```python
contours, hierarchy = cv2.findContours(
    mask,
    cv2.RETR_EXTERNAL,     # Only outer contours (ignore holes)
    cv2.CHAIN_APPROX_SIMPLE # Compress straight segments
)
```

**Contour properties:**
```python
area = cv2.contourArea(contour)     # Pixel area
perimeter = cv2.arcLength(contour, True)  # Edge length
x, y, w, h = cv2.boundingRect(contour)   # Bounding box

# Aspect ratio (squareness)
aspect = min(w, h) / max(w, h)  # 1.0 = square, 0.0 = line

# Circularity
circularity = 4 * pi * area / (perimeter^2)  # 1.0 = circle

# Solidity (convex hull fill ratio)
hull = cv2.convexHull(contour)
solidity = area / cv2.contourArea(hull)
```

### Confidence Scoring

**Multi-factor confidence:**
```
confidence = base_score
    * aspect_penalty     (penalize non-square shapes)
    * area_penalty       (penalize very small detections)
    * size_penalty       (penalize unreasonably large detections)

Result: 0.0 (definitely noise) to 1.0 (definitely a block)
Threshold: 0.3 minimum (tuned from real-world testing)
```

### Camera Calibration for Distance

**For better distance accuracy:**
1. Place block at known distances (10cm, 20cm, 30cm, 50cm)
2. Measure pixel width at each distance
3. Calculate focal length: `f = (pixel_width * distance) / real_width`
4. Average the results: This is your calibrated focal length
5. Update `FOCAL_LENGTH` in config

---

## Configuration

```yaml
# Color ranges (HSV)
colors:
  red:
    ranges:
      - lower: [0, 80, 50]
        upper: [10, 255, 255]
      - lower: [160, 80, 50]
        upper: [180, 255, 255]
  blue:
    ranges:
      - lower: [100, 60, 50]
        upper: [130, 255, 255]
  yellow:
    ranges:
      - lower: [20, 80, 50]
        upper: [40, 255, 255]

# Detection parameters
detection:
  focal_length: 500
  block_size_mm: 30
  min_area: 30
  max_area: 5000
  min_aspect_ratio: 0.4
  min_confidence: 0.3
  frame_width: 640
  frame_height: 480
```

---

## Files

```
block_detection/
  SKILL.md           # This file
  README.md          # Quick reference

Existing code (already on robot):
  /home/robot/pathfinder/skills/block_detect.py    # BlockDetector class
  /home/robot/pathfinder/skills/centering.py       # CenteringController
```

---

*Find the blocks, know the colors, estimate the distance!* 🔴🔵🟡
