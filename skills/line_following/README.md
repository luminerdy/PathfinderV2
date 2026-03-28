# Line Following (E6) - Quick Reference

**Follow a lime green tape line using camera + mecanum drive**

## Quick Start

### Test detection only (no driving):
```bash
python3 test_line_detect.py
```

### Follow the line:
```bash
python3 run_demo.py
```

## API
```python
from skills.line_following.line_follower import LineFollower

follower = LineFollower()
result = follower.follow(timeout=30)
# result['success'], result['reason'], result['frames']
follower.cleanup()

# Detection only (no driving):
detection = follower.detect_line(frame)
# detection['found'], detection['cx'], detection['error'], detection['ratio']
```

## How It Works
1. Camera points down (arm repositioned)
2. Crop to bottom third of frame (ROI)
3. HSV threshold for lime green (H=40-75)
4. Find centroid of green pixels
5. Proportional steering (error * Kp)
6. Stop when line ends (green ratio drops)

## Key Parameters
- HSV: [40,100,100] to [75,255,255] (lime green)
- Kp: 0.15 (steering gain)
- Forward speed: 25
- ROI: Bottom 35% of frame

## Why Lime Green?
- Far from red (H=0-10), blue (H=100-130), yellow (H=20-40)
- High contrast on gray floor
- No conflict with block detection

---
*Follow the line, stay on track!* 🟢
