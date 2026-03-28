# Visual Servoing (E4) - Quick Reference

**Drive toward targets using real-time camera feedback**

## Quick Start
```bash
cd /home/robot/pathfinder
python3 skills/block_approach.py
```
Place colored block 30-80cm away, robot drives to it!

## API
```python
from skills.block_approach import BlockApproach

ba = BlockApproach()
result = ba.approach(color='red')  # or 'blue', 'yellow', None
# result['success'], result['color'], result['reason']
ba.cleanup()
```

## How It Works
1. Camera detects block
2. Lock onto target (won't switch blocks)
3. Calculate error (pixel offset from center/bottom)
4. Proportional control (error * gain = motor speed)
5. Strafe + forward simultaneously (mecanum advantage)
6. Stop when block at pickup distance

## Key Parameters
- Kx=0.15 (strafe gain), Ky=0.10 (forward gain)
- Target: block at y=420 (bottom of frame)
- Tolerance: +/-40px horizontal, +/-30px vertical

## Next: E5 Autonomous Pickup (add arm grab!)

---
*See target, correct, reach!* 🎯
