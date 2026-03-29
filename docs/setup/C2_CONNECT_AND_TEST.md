# C2: Connect Pi 500 to Robot and Test

**Purpose:** Establish SSH connection from your Pi 500 to the robot, verify all hardware works

This is the critical step — once connected, you control the robot entirely from your Pi 500.

---

## Prerequisites

- Pi 500 is powered on, connected to WiFi ([C1](C1_PI500_SETUP.md))
- Robot is powered on with charged batteries (>7.0V)
- Both devices on the same WiFi network
- You know the robot's IP address (check robot's display or ask facilitator)

## Architecture

```
┌──────────────────┐     WiFi/SSH      ┌──────────────────┐
│    Pi 500         │ ──────────────── │    Robot (Pi 4)   │
│  (Control Hub)    │                   │  (Mobile Platform)│
│                   │                   │                   │
│  - Write code     │   SSH commands    │  - Motors         │
│  - Run scripts    │ ───────────────► │  - Arm/servos     │
│  - Monitor        │                   │  - Camera         │
│  - Debug          │   Camera feed     │  - Sonar          │
│  - Strategize     │ ◄─────────────── │  - Batteries      │
└──────────────────┘                   └──────────────────┘
     Your desk                              On the floor
```

**You sit at the Pi 500. The robot moves on the field. Everything happens over SSH.**

---

## Step 1: Find the Robot's IP

Ask your facilitator, or check the robot's display. Example: `10.10.10.142`

## Step 2: SSH Connection

Open a terminal on your Pi 500:

```bash
ssh robot@10.10.10.142
```

- Replace `10.10.10.142` with your robot's actual IP
- Username: `robot`
- Password: (provided by facilitator)
- Type `yes` if asked about fingerprint

**Success looks like:**
```
robot@MasterPi4:~ $
```

You're now ON the robot. Every command you type runs on the robot.

## Step 3: Check Battery

**Do this FIRST every time you connect!**

```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board
import time
board = get_board()
time.sleep(2)
mv = board.get_battery()
if mv and 5000 < mv < 20000:
    v = mv / 1000.0
    print('Battery: %.2fV' % v)
    if v < 7.0: print('WARNING: Replace batteries!')
    elif v < 7.5: print('Low - replace soon')
    else: print('Good')
"
```

**Battery guide:**
| Voltage | Status | Action |
|---------|--------|--------|
| >8.0V | Full | Good to go |
| 7.5-8.0V | OK | Monitor closely |
| 7.0-7.5V | Low | Replace soon |
| <7.0V | Critical | Replace NOW |

## Step 4: Test Motors

```bash
cd /home/robot/pathfinder
python3 skills/mecanum_drive/run_demo.py
```

**Watch the robot!** It should move in 8 patterns: forward, backward, strafe, rotate, diagonals, square.

**If motors don't move:**
- Check battery (>7.0V needed)
- Are wheels touching the ground?
- Try higher power scripts

## Step 5: Test Arm

```bash
python3 skills/robotic_arm/run_demo.py
```

The arm should move through several positions and test the gripper.

## Step 6: Test Camera

```bash
python3 skills/camera_vision/test_camera.py
```

Should report `Camera: 640x480` and save a test image.

**View the camera feed in a browser:**
From your Pi 500's browser, open:
```
http://10.10.10.142:8080
```
(Replace with your robot's IP)

## Step 7: Test Sonar

```bash
python3 -c "
from sdk.common.sonar import Sonar
s = Sonar()
d = s.getDistance()
print('Sonar: %.0f mm' % d)
"
```

Put your hand in front of the robot and run again — distance should change.

---

## Working with Two Terminals

You'll often want multiple SSH sessions:

**Terminal 1:** Running a script on the robot
**Terminal 2:** Monitoring or editing

Open a new terminal tab on your Pi 500 (Ctrl+Shift+T) and SSH again:
```bash
ssh robot@10.10.10.142
```

## Copying Files

**Pi 500 → Robot:**
```bash
# From Pi 500 terminal (NOT SSH'd into robot)
scp ~/PathfinderV2/my_script.py robot@10.10.10.142:/home/robot/pathfinder/skills/
```

**Robot → Pi 500:**
```bash
# From Pi 500 terminal
scp robot@10.10.10.142:/home/robot/pathfinder/test_frame.jpg ~/
```

## Editing Code

**Option A: Edit on Pi 500, copy to robot**
```bash
# On Pi 500
nano ~/PathfinderV2/skills/my_script.py
# Then copy
scp ~/PathfinderV2/skills/my_script.py robot@10.10.10.142:/home/robot/pathfinder/skills/
```

**Option B: Edit directly on robot via SSH**
```bash
# While SSH'd into robot
nano /home/robot/pathfinder/skills/my_script.py
```

**Option C: Use VNC for full remote desktop**
```bash
# From Pi 500 browser or VNC viewer
# Connect to robot-ip:5900
```

---

## Troubleshooting

**"Connection refused":**
- Is the robot powered on?
- Are both devices on the same WiFi?
- Check robot IP: `ping 10.10.10.142`

**"Permission denied":**
- Wrong password? Ask facilitator
- Username must be `robot` (lowercase)

**Robot not responding to commands:**
- Battery dead? Check voltage
- SSH session frozen? Close terminal, reconnect

**Camera not working:**
- Run `ls /dev/video*` on the robot
- If no video0, unplug/replug USB camera

---

## Connection Cheat Sheet

```bash
# Connect
ssh robot@<ROBOT_IP>

# Check battery
python3 -c "from lib.board import get_board; import time; b=get_board(); time.sleep(2); mv=b.get_battery(); print('%.2fV' % (mv/1000.0) if mv and 5000<mv<20000 else 'error')"

# Emergency stop (if robot is moving unexpectedly)
python3 -c "from lib.board import get_board; b=get_board(); b.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])"

# Copy file to robot
scp file.py robot@<ROBOT_IP>:/home/robot/pathfinder/

# View camera
# Open browser: http://<ROBOT_IP>:8080
```

---

**You're connected!** Now head to [START_HERE.md](../../START_HERE.md) to begin the workshop skills.
