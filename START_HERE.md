# Getting Started with PathfinderV2

Welcome! This guide walks you through PathfinderV2 from first power-on to autonomous competition.

**Time needed:** 2-3 hours for the full path (or 15 minutes per skill if you pick and choose)

---

## Before You Start

### What You Need
- Raspberry Pi 4 robot with mecanum wheels, arm, camera, and sonar
- 2× 18650 batteries (charged to 8.0V+)
- Computer on same network (for web interface)
- Colored blocks (red, blue, yellow — ~1.2 inch / 30mm)
- Lime green tape (for line following)
- AprilTags printed (tag36h11, IDs 578-585, 10" size) — optional for navigation

### Check Your Robot
```bash
# SSH into robot or open terminal
cd PathfinderV2

# Check battery (do this FIRST every time!)
python3 scripts/tools/check_battery.py
# Need: >7.0V for Pi 4, >8.2V for Pi 5

# Quick hardware test
python3 scripts/testing/test_hardware.py
```

---

## Learning Path

### Choose your path:

**Path A: Full workshop (recommended)**
Follow skills in order: D1 → D2 → D3 → D4 → E2 → E3 → E4 → E5 → E6

**Path B: Just want to drive**
Start with D1 (Mecanum Drive), then try E2 (AprilTag Navigation)

**Path C: Vision focus**
Start with D4 (Camera), then E3 (Block Detection), then E4 (Visual Servoing)

**Path D: Jump to the cool stuff**
Run E5 (Autonomous Pickup) or E6 (Line Following) directly — just know what you're watching

---

## Step 1: Drive the Robot (D1)

**Time:** 10 minutes  
**What:** Learn how mecanum wheels enable omnidirectional movement

```bash
python3 skills/mecanum_drive/run_demo.py
```

Watch the robot move in 8 patterns: forward, backward, strafe left/right, rotate, diagonals, and a square.

**Want more?** Read `skills/mecanum_drive/SKILL.md`

---

## Step 2: Sense the World (D2)

**Time:** 10 minutes  
**What:** Ultrasonic distance sensing with visual RGB feedback

```bash
python3 skills/sonar_sensors/run_demo.py
```

Put your hand in front of the sonar and watch the RGB LEDs change color (green → yellow → red as you get closer).

**Want more?** Read `skills/sonar_sensors/SKILL.md`

---

## Step 3: Control the Arm (D3)

**Time:** 15 minutes  
**What:** Move servos, play action groups, learn named positions

**Option A — Visual (no code):**
```bash
python3 web/web_control.py
# Open browser: http://<robot-ip>:8080
# Use servo sliders to move the arm
```

**Option B — Action groups:**
```bash
python3 skills/robotic_arm/play_action.py stand
python3 skills/robotic_arm/play_action.py shake_head
```

**Option C — Python demo:**
```bash
python3 skills/robotic_arm/run_demo.py
```

**Want more?** Read `skills/robotic_arm/SKILL.md`

---

## Step 4: See Through Robot Eyes (D4)

**Time:** 10 minutes  
**What:** Camera capture, color spaces, and HSV color detection

```bash
# Test camera works
python3 skills/camera_vision/test_camera.py

# See color space conversions (saves 5 images)
python3 skills/camera_vision/color_spaces.py
```

**Want more?** Read `skills/camera_vision/SKILL.md`

---

## Step 5: Navigate Autonomously (E2)

**Time:** 15 minutes  
**Requires:** AprilTags posted on walls

```bash
python3 skills/apriltag_navigation/run_demo.py
```

Robot detects AprilTags, estimates distance and angle, then drives to each one.

**Want more?** Read `skills/apriltag_navigation/SKILL.md`

---

## Step 6: Find Colored Blocks (E3)

**Time:** 10 minutes  
**Requires:** Colored blocks in view

```bash
python3 skills/block_detection/run_demo.py
```

Camera detects red, blue, and yellow blocks using HSV color filtering. Shows color, distance, and confidence for each detection.

**Want more?** Read `skills/block_detection/SKILL.md`

---

## Step 7: Drive to a Target (E4)

**Time:** 15 minutes  
**Requires:** Colored block 30-80cm in front of robot

```bash
python3 skills/visual_servoing/run_demo.py
```

Robot locks onto a block and drives toward it using real-time camera feedback. This is **closed-loop control** — it corrects itself as it moves.

**Safety:** Robot will drive! Clear the path.

**Want more?** Read `skills/visual_servoing/SKILL.md`

---

## Step 8: Autonomous Pickup (E5) `[Beta]`

**Time:** 15 minutes  
**Requires:** Colored block on floor, clear workspace  
**Note:** Working but may need multiple attempts. Lighting and block placement affect reliability.

```bash
python3 skills/autonomous_pickup/run_demo.py
# Or target a specific color:
python3 skills/autonomous_pickup/run_demo.py red
```

The grand integration: robot scans for a block, drives to it, and picks it up. Three phases: **Scan → Approach → Pickup.**

**Safety:** Robot will rotate, drive, and move arm!

**Want more?** Read `skills/autonomous_pickup/SKILL.md`

---

## Step 9: Follow the Line (E6) `[Beta]`

**Time:** 10 minutes  
**Requires:** Lime green tape on floor  
**Note:** Working through straights and curves. Speed may need tuning based on battery voltage.

```bash
# Test detection first (no driving)
python3 skills/line_following/test_line_detect.py

# Follow the line
python3 skills/line_following/run_demo.py
```

Robot follows a lime green tape line through straights and curves, stopping when the line ends.

**Safety:** Robot will drive along the tape!

**Want more?** Read `skills/line_following/SKILL.md`

---

## What's Next?

After completing the skills, you're ready for competition:

1. **Combine skills** — Navigate to area, find block, pick it up, follow line to scoring zone
2. **Tune parameters** — Edit `config.yaml` files to optimize for your field
3. **Build strategies** — Which blocks score most? Shortest path? Battery management?
4. **Compete!** — Full autonomous scoring cycle

---

## Skill Reference Card

| Skill | Type | Time | Key Concept |
|-------|------|------|-------------|
| D1: Mecanum Drive | Hardware | 10 min | Omnidirectional movement |
| D2: Sonar Sensors | Hardware | 10 min | Distance sensing + feedback |
| D3: Robotic Arm | Hardware | 15 min | Servo control + sequences |
| D4: Camera Vision | Hardware | 10 min | Color spaces + HSV |
| E2: AprilTag Nav | Integration | 15 min | Autonomous navigation |
| E3: Block Detection | Integration | 10 min | Color-based object finding |
| E4: Visual Servoing | Integration | 15 min | Closed-loop approach |
| E5: Auto Pickup | Integration | 15 min | Full integration |
| E6: Line Following | Integration | 10 min | Path tracking |

**Total:** ~2 hours for all 9 skills

---

## Troubleshooting

**Robot doesn't move:**
- Check battery: `python3 scripts/tools/check_battery.py` (need >7.0V)
- Motor power too low (try speed 35+, fresh batteries need less)

**Camera not working:**
- Check: `ls /dev/video*` (should see video0)
- USB connection loose?

**AprilTags not detected:**
- Good lighting? (no harsh shadows)
- Tags big enough? (need 10" for reliable detection)
- Right family? (tag36h11, IDs 578-585)

**Block detection unreliable:**
- Lighting matters — avoid shadows on blocks
- Adjust HSV ranges in `skills/block_detection/config.yaml`

**Line following loses the line:**
- Lime green tape only (not regular green)
- Adjust HSV range in `skills/line_following/config.yaml`
- Curves too tight? Slow down in config

---

## Each Skill Has 4 Depth Levels

**Don't have time to read everything? That's fine.**

Every SKILL.md has the same structure:

1. **📘 Overview** — What it does, why it matters (2 min read)
2. **🚀 Quick Start** — Run the demo, see it work (5 min)
3. **🔧 Implementation** — Understand the code, modify it (15 min)
4. **🎓 Deep Dive** — Math, physics, control theory (30+ min)

**Skip to the level you need.** Students: start at Quick Start. Engineers: jump to Deep Dive.

---

*Built for learning. Start anywhere, go as deep as you want.* 🤖
