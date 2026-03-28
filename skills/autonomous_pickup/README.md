# Autonomous Block Pickup (E5) - Quick Reference

**Complete cycle: Find block, drive to it, pick it up**

## Quick Start
```bash
cd /home/robot/pathfinder
python3 skills/auto_pickup.py           # Any color
python3 skills/auto_pickup.py red       # Red only
python3 skills/auto_pickup.py blue      # Blue only
```

## Three Phases
1. **SCAN** — Rotate 360deg, find block, face it (camera forward)
2. **APPROACH** — Stop-look-drive to block (camera down)
3. **PICKUP** — Lower arm, grab, lift, carry

## Integrates All Skills
- D1: Mecanum Drive (rotation, strafe, forward)
- D3: Robotic Arm (pickup sequence)
- D4: Camera Vision (frame capture)
- E3: Block Detection (HSV filtering)
- E4: Visual Servoing (closed-loop approach)

## Key Parameters
- Scan: 16 steps x 22deg = 360deg rotation
- Approach: Stop-look-drive, 30 motor power
- Pickup: Pre-tested arm positions (servo PWM)
- Battery check: >7.0V (Pi4), >8.1V (Pi5)

## Troubleshooting
- No block found: Check lighting, color ranges
- Block lost mid-approach: Increase tolerance
- Gripper misses: Recalibrate down-view center (350,350)
- Battery warning: Charge batteries!

---
*See it, drive to it, grab it!* 🤖🔴✊
