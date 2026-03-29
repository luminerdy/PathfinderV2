# Supply Chain Scramble — Quick Reference Card 🏭
*Print this. Tape it to your desk.*

---

## Scoring (counted at end of match)

| What | Points |
|------|--------|
| Block in **correct color** basket | **15 pts** |
| Block in **wrong color** basket | 3 pts |
| Block **on robot** at buzzer | 2 pts |
| Block on field | 0 pts |
| Through the passage | 3 pts each |
| Return to start zone | 3 pts each |
| **Autonomous** delivery (no human input) | **+10 pts per block** |
| All 9 sorted correctly | **+30 pts bonus** |
| GenAI code that works | +10 pts team bonus |
| Creative robot modification | +5 to +15 pts |

## Penalties

| What | Points |
|------|--------|
| Touch robot on field | -3 pts |
| Robot leaves field | -5 pts |
| Knock over barrier | -2 pts |
| >3 robots on field | -10 pts |
| Intentional ramming | -10 pts + 60 sec removal |

## Key Rules

- **3 robots max** on field at a time
- **Swap** robots in start zone only (tag-team!)
- **10 minute** matches
- **Modify your robot!** (storage bin, bumper, etc.)
- Control via SSH from Pi 500 (any method: manual, scripts, autonomous)

## Baskets

| Color | AprilTag |
|-------|----------|
| 🔵 Blue | Tag 578 (left) |
| 🟡 Yellow | Tag 579 (center) |
| 🔴 Red | Tag 580 (right) |

## Robot Cheat Sheet

```bash
# Connect
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder

# Battery check
python3 scripts/tools/check_battery.py

# EMERGENCY STOP
python3 -c "from lib.board import get_board; b=get_board(); b.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])"

# Drive demo
python3 skills/mecanum_drive/run_demo.py

# Pick up a block
python3 skills/bump_grab.py red

# Follow green line
python3 skills/line_following/run_demo.py

# Color delivery (full auto)
python3 skills/color_delivery.py red

# Web control (manual drive)
python3 web/web_control.py
# Browser: http://<ROBOT_IP>:8080
```

## Ask GenAI!

- "Analyze the scoring rules — what's the optimal 10-minute strategy?"
- "Write a script to pick up yellow blocks and deliver to tag 579"
- "My robot drifts right when driving straight — how to fix?"
- "Design a back storage bin to carry 3 blocks"

---

*Sort it. Ship it. Score it.* 🏭🤖🏆
