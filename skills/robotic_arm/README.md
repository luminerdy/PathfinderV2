# Robotic Arm Skill - Quick Reference

**Control a 5-servo robotic arm for manipulation tasks**

---

## Quick Start Levels

### Level 1A: Web UI (Visual, No Code)
```bash
cd /home/robot/pathfinder/web
python3 app.py
# Open browser: http://10.10.10.142:5000/servo
```
Move sliders, see arm respond!

### Level 1.5: Action Groups (Pre-Recorded)
```bash
python3 play_action.py shake_head
python3 play_action.py stand
```
Play back pre-recorded sequences.

### Level 2: Named Positions (Python)
```bash
python3 run_demo.py
```
Move through safe, pre-defined positions.

---

## Learning Outcomes

After this skill, you can:
- ✅ **Explain** what each servo does (base, shoulder, elbow, wrist, gripper)
- ✅ **Control** servos via web UI or Python
- ✅ **Use** named positions for quick positioning
- ✅ **Play** action groups (pre-recorded sequences)
- ✅ **Program** pick-and-place sequences (Level 4)

---

## Hardware Reference

**5 Servos:**
1. Gripper (1475=closed, 2500=open)
3. Wrist (500-2500)
4. Elbow (500-2500)
5. Shoulder (500-2500)
6. Base (500-2500)

*Note: Servo 2 doesn't exist*

---

## Troubleshooting

**Servo doesn't move:**
- Check PWM range (500-2500)
- Verify servo ID (no servo 2!)

**Arm hits itself:**
- Use named positions (pre-tested safe)
- Move through waypoints

**Gripper won't close:**
- Object too large?
- Try max force: `arm.grip(force=1.0)`

---

## Next Skills

- **E3: Block Detection** - Find objects to grab
- **E5: Autonomous Pickup** - Vision + arm integration

---

*Position, grab, manipulate!* 🦾
