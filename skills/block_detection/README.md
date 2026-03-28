# Block Detection (E3) - Quick Reference

**Detect colored blocks using HSV color filtering**

## Quick Start
```bash
cd /home/robot/pathfinder
python3 skills/block_detect.py
```
Place colored block in view, see detection output.

## API
```python
from skills.block_detect import BlockDetector

detector = BlockDetector()
blocks = detector.detect(frame)              # All colors
blocks = detector.detect(frame, ['red'])     # Red only
nearest = detector.find_nearest(frame, 'red') # Nearest red

# Each block has:
# .color, .center_x, .center_y, .width, .height
# .offset_from_center, .estimated_distance_mm, .confidence
```

## Color Ranges (HSV)
- Red: H=0-10 + H=160-180
- Blue: H=100-130
- Yellow: H=20-40

## Pipeline
Camera -> HSV -> Threshold -> Morphology -> Contours -> Filter -> Detect

## Next Skills
- E4: Visual Servoing (drive toward detected blocks)
- E5: Autonomous Pickup (detect + drive + grab)

---
*Find the blocks!* 🔴🔵🟡
