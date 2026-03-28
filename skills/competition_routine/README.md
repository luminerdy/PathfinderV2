# Competition Routine (E7) - Quick Reference

**Full autonomous scoring cycle: find → grab → follow → score**

## Quick Start
```bash
python3 run_demo.py              # One cycle, any color
python3 run_demo.py red          # Target red blocks
python3 run_demo.py blue 3       # Three cycles, blue blocks
```

## Four Phases
1. **PICKUP** — Scan 360deg, approach block, grab it (E3+E4+E5)
2. **FIND LINE** — Rotate to find lime green tape
3. **FOLLOW** — Drive along tape to scoring zone (E6)
4. **DELIVER** — Open gripper, release block, back up

## Integrates All Skills
D1 (drive) + D3 (arm) + D4 (camera) + E3 (detect) + E4 (servoing) + E5 (pickup) + E6 (line follow)

## Error Recovery
- Block not found → full 360 scan, then give up
- Block lost → search rotation
- Line not found → 360 scan
- Battery low → abort safely

## Scoring
- 10 points per block delivered
- +5 bonus for correct color zone
- -3 penalty for dropped blocks

---
*The grand integration: find it, grab it, score it!* 🏆
