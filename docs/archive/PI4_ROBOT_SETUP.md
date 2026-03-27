# Pi 4 Robot Setup Guide
## PathfinderV2 — Fresh Robot Configuration

**Last Updated:** March 25, 2026  
**Tested On:** Raspberry Pi 4 Model B Rev 1.5  
**OS:** Raspberry Pi OS (Bookworm, 64-bit)

---

## Prerequisites

- Raspberry Pi 4 (4GB+ recommended)
- MasterPi robot platform assembled
- SD card with Raspberry Pi OS flashed (64-bit)
- WiFi network configured
- SSH enabled
- I2C enabled

---

## Step 1: Boot Config — Enable UART0

The motor board communicates at 1,000,000 baud via UART. On Pi 4, Bluetooth
uses ttyAMA0 by default. We need to disable Bluetooth to free it.

```bash
sudo nano /boot/firmware/config.txt
```

Add at the end (under `[all]`):

```
enable_uart=1

# PathfinderV2: Free ttyAMA0 for motor board (1Mbaud)
dtoverlay=disable-bt
```

Disable Bluetooth services:

```bash
sudo systemctl disable hciuart
sudo systemctl disable bluetooth
```

**Reboot required:**
```bash
sudo reboot
```

After reboot, verify:
```bash
ls /dev/ttyAMA0    # Should exist
```

### Why This Is Needed

| Without disable-bt | With disable-bt |
|-------------------|-----------------|
| `/dev/ttyAMA0` → Bluetooth | `/dev/ttyAMA0` → GPIO pins (motor board) |
| `/dev/ttyS0` → GPIO (can't do 1Mbaud) | Bluetooth disabled |
| **Motor board won't work** | **Motor board works** |

---

## Step 2: Enable I2C

Needed for sonar sensor (address 0x77).

```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

Or add to `/boot/firmware/config.txt`:
```
dtparam=i2c_arm=on
```

Verify:
```bash
ls /dev/i2c-1    # Should exist
```

---

## Step 3: Install Python Dependencies

```bash
# Core packages (may already be installed)
pip3 install --break-system-packages flask pyserial smbus2 numpy

# Vision packages
pip3 install --break-system-packages opencv-python-headless pupil-apriltags
```

**Note:** `--break-system-packages` is required on Bookworm (PEP 668).

### Verify Installation

```bash
python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python3 -c "from pupil_apriltags import Detector; print('AprilTags: OK')"
python3 -c "import flask; print(f'Flask: {flask.__version__}')"
python3 -c "import serial; print('PySerial: OK')"
python3 -c "import smbus2; print('SMBus2: OK')"
```

---

## Step 4: Clone Repository

```bash
mkdir -p /home/robot/code
cd /home/robot/code
git clone https://github.com/luminerdy/PathfinderV2.git pathfinder
```

### Verify Clone

```bash
cd /home/robot/code/pathfinder
ls skills/    # Should show arm_control.py, block_detect.py, etc.
```

### Verify All Imports

```bash
cd /home/robot/code/pathfinder
python3 -c "
from lib.board_protocol import BoardController
from skills.block_detect import BlockDetector
from skills.arm_control import ArmController
from skills.strafe_nav import StrafeNavigator
print('All imports OK!')
"
```

---

## Step 5: Test Hardware

### Battery Check

```bash
cd /home/robot/code/pathfinder
python3 -c "
from lib.board_protocol import BoardController
import time
board = BoardController()
time.sleep(2)
for i in range(5):
    mv = board.get_battery()
    if mv:
        print(f'Battery: {mv/1000:.2f}V')
        break
    time.sleep(0.5)
else:
    print('No battery reading - check motor board power switch')
"
```

**Expected:** Battery voltage (7.0-8.4V range)

### Buzzer Test

```bash
cd /home/robot/code/pathfinder
python3 -c "
from lib.board_protocol import BoardController
import time
board = BoardController()
time.sleep(1)
board.set_buzzer(1000, 0.2, 0.1, 2)
print('Did you hear two beeps?')
"
```

### Servo Test

```bash
cd /home/robot/code/pathfinder
python3 -c "
from lib.board_protocol import BoardController
import time
board = BoardController()
time.sleep(1)
# Move to camera-forward position
board.set_servo_position(1000, [(1,2500),(3,590),(4,2450),(5,700),(6,1500)])
print('Arm should move to camera-forward position')
"
```

### Motor Test

```bash
cd /home/robot/code/pathfinder
python3 -c "
from lib.board_protocol import BoardController
import time
board = BoardController()
time.sleep(1)
# Brief forward movement
board.set_motor_duty([(1,30),(2,30),(3,30),(4,30)])
time.sleep(0.5)
board.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])
print('Robot should have moved forward briefly')
"
```

### Camera Test

```bash
cd /home/robot/code/pathfinder
python3 -c "
import cv2
cam = cv2.VideoCapture(0)
ret, frame = cam.read()
if ret:
    print(f'Camera: {frame.shape[1]}x{frame.shape[0]} OK')
else:
    print('Camera: FAILED')
cam.release()
"
```

### Sonar Test

```bash
cd /home/robot/code/pathfinder
python3 -c "
from hardware.sonar import Sonar
import time
sonar = Sonar()
for i in range(3):
    d = sonar.get_distance()
    if d:
        print(f'Distance: {d:.1f} cm')
    time.sleep(0.3)
"
```

---

## Step 6: Run Web Control

```bash
cd /home/robot/code/pathfinder/web
python3 web_control.py
```

Open in browser: `http://<robot-ip>:8080`

**Verify:**
- [ ] Live video feed visible
- [ ] Battery voltage displayed
- [ ] Servo sliders move arm
- [ ] Drive buttons work (with adequate battery)

---

## Step 7: Optional — Startup Service

Create a systemd service to position the arm at boot:

```bash
sudo nano /etc/systemd/system/pathfinder-startup.service
```

```ini
[Unit]
Description=PathfinderV2 Robot Startup Sequence
After=network.target

[Service]
Type=oneshot
User=robot
WorkingDirectory=/home/robot/code/pathfinder
ExecStart=/usr/bin/python3 /home/robot/code/pathfinder/robot_startup.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable pathfinder-startup.service
sudo systemctl start pathfinder-startup.service
```

---

## Troubleshooting

### No battery reading / Board not responding

- **Check motor board power switch** (must be ON)
- **Check serial connection:** `ls /dev/ttyAMA0` (must exist)
- **Check baud rate:** Board uses 1,000,000 baud
- **Check UART config:** `grep disable-bt /boot/firmware/config.txt`

### Motors don't move

- **Battery voltage:** Must be >8.2V for Pi 5, likely >7.5V for Pi 4
- **Motor power:** Minimum power 28-30 to overcome friction
- **Check Pi throttling:** `vcgencmd get_throttled` (should be 0x0)

### Camera not found

- **Check USB connection:** `ls /dev/video0`
- **Check if locked:** `lsof /dev/video0` (another process using it?)

### Import errors

- **Wrong directory:** Must run from `/home/robot/code/pathfinder`
- **Missing packages:** Re-run pip install command from Step 3

---

## Pi 4 vs Pi 5 Differences

| Item | Pi 4 | Pi 5 |
|------|------|------|
| UART port | `/dev/ttyAMA0` (need disable-bt) | `/dev/ttyAMA0` (need uart0 overlay) |
| Power draw | 5V/3A (15W) | 5V/5A (25W) |
| Battery threshold | ~7.5V (estimated) | >8.2V (proven) |
| Motor reliability | Better (less voltage sag) | Marginal at <8.2V |
| Packages | Need `--break-system-packages` | Need `--break-system-packages` |
| Performance | Adequate for vision | Faster (not needed) |

---

## Quick Setup Checklist

- [ ] Flash Raspberry Pi OS (64-bit, Bookworm)
- [ ] Enable SSH
- [ ] Enable I2C
- [ ] Configure WiFi
- [ ] Add `dtoverlay=disable-bt` to boot config
- [ ] Disable hciuart and bluetooth services
- [ ] Reboot
- [ ] Verify `/dev/ttyAMA0` exists
- [ ] Install Python packages (opencv, apriltags, flask, etc.)
- [ ] Clone PathfinderV2 repo
- [ ] Verify all imports
- [ ] Test battery reading
- [ ] Test buzzer
- [ ] Test servos
- [ ] Test motors
- [ ] Test camera
- [ ] Test sonar
- [ ] Run web control interface
- [ ] Optional: Enable startup service

---

*This guide was created while setting up a Pi 4 buddy robot on March 25, 2026.*
*Steps verified on Raspberry Pi 4 Model B Rev 1.5 with Raspberry Pi OS Bookworm 64-bit.*
