# Mecanum Drive Skill - Quick Reference

**Foundation skill - start here!**

---

## Quick Start

```bash
cd /home/robot/pathfinder/skills/mecanum_drive
python3 run_demo.py
```

**What you'll see:** 8 movement patterns (forward, strafe, rotate, diagonal, square)

**Time:** 15-20 minutes

---

## Learning Outcomes

After this skill, you can:
- ✅ **Explain** why mecanum wheels have 45° rollers
- ✅ **Control** robot in all directions
- ✅ **Implement** movement patterns
- ✅ **Tune** speed limits for your floor
- ✅ **Debug** motor direction issues

**Assessment:** Drive square pattern successfully

---

## Files

| File | Level | Purpose |
|------|-------|---------|
| `SKILL.md` | All | Complete documentation (4 sections) |
| `run_demo.py` | 1 | One-click demo (no code changes) |
| `config.yaml` | 2 | Tune parameters (speeds, timing) |
| `README.md` | - | This file |

---

## Troubleshooting

**Robot doesn't move:**
- Check battery: `python3 ../../tests/battery_check.py`
- Test motors: `python3 ../../tests/test_motors.py`

**Wrong direction:**
- Edit `config.yaml` → `motor_directions`
- Set problem motors to `-1` (inverted)

**Strafe is crooked:**
- Check wheel mounting (45° roller angle)
- Verify weight distribution (battery centered)

---

## Next Skills

After mastering mecanum drive, try:

- **D2: Sonar Sensors** - Add obstacle detection
- **D3: Robotic Arm** - Control servos and gripper
- **E2: AprilTag Navigation** - Autonomous movement!

---

*Master movement first - everything builds on this!* 🎯
