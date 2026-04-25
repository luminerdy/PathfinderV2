# A1 — Robot Pi OS Build Steps

**Purpose:** Create an SD card image for a PathfinderV2 competition robot.  
**Platform:** Raspberry Pi 4 (4GB+)  
**OS:** Raspberry Pi OS (Debian 13 Trixie, 64-bit) — see note below  
**Time:** ~30 minutes

> **OS Note:** As of April 2026, the latest Raspberry Pi OS ships with **Debian 13 (Trixie)**.  
> Previous docs referenced Bookworm (Debian 12). Steps are the same; version references updated below.  
> Tested on: Raspberry Pi 4 Model B, Debian 13.4 Trixie 64-bit, kernel 6.12.75, Python 3.13.5

---

## Overview

After completing these steps you will have an SD card that can be cloned for all competition robots. Each robot gets an identical image — only WiFi credentials and hostname change per robot.

**Materials:** see [BILL_OF_MATERIALS.md](BILL_OF_MATERIALS.md) in this folder for the robot/setup BOM.

---

## Step 1: Flash Base OS

### Download
- Go to https://www.raspberrypi.com/software/
- Download **Raspberry Pi Imager**

### Flash Settings
- **OS:** Raspberry Pi OS (64-bit) — latest (Trixie / Debian 13)
  - Lite (no desktop) is recommended for competition robots
  - Desktop is fine if students will use VNC
- **Storage:** Select your SD card (16GB minimum, 32GB recommended)

### Pre-Configure in Imager (gear icon / Ctrl+Shift+X)
- **Hostname:** `pathfinder` (change per robot later: pathfinder-01, pathfinder-02, etc.)
- **Enable SSH:** Yes (password authentication)
- **Username:** `robot`
- **Password:** (choose a standard password for all robots)
- **WiFi:** Configure your workshop network SSID and password
- **Locale:** Set timezone and keyboard layout

### Flash
Click **Write** and wait for completion.

> **Locale tip:** If you set locale to `en_US` during imaging but see locale warnings over SSH, the locale may not be fully generated. Fix with:
> ```bash
> sudo locale-gen en_US.UTF-8
> sudo update-locale LANG=en_US.UTF-8
> ```

---

## Step 2: Boot and Connect

1. Insert SD card into Pi 4
2. Power on
3. Wait ~60 seconds for first boot (filesystem expands)
4. Find the Pi on your network:
   ```bash
   # From another computer on the same network
   ping pathfinder.local
   # Or check your router's DHCP client list
   ```
5. SSH in:
   ```bash
   ssh robot@pathfinder.local
   # Or use the IP address
   ssh robot@<IP_ADDRESS>
   ```

---

## Step 3: System Updates

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

---

## Step 4: Enable Hardware Interfaces

### Enable I2C (for motor board and sonar)
```bash
sudo raspi-config nonint do_i2c 0
```

### Enable UART and Disable Bluetooth
The motor board communicates via UART at 1,000,000 baud. On Pi 4, Bluetooth uses the good UART (ttyAMA0) by default. We need to swap it.

```bash
# Edit boot config
sudo nano /boot/firmware/config.txt
```

Find the `[all]` section and ensure these lines are present:
```
[all]
enable_uart=1

# PathfinderV2: Free ttyAMA0 for motor board (1Mbaud)
dtoverlay=disable-bt
```

Disable Bluetooth services:
```bash
sudo systemctl disable hciuart bluetooth
sudo systemctl stop bluetooth
```

### Reboot
```bash
sudo reboot
```

### Verify After Reboot
```bash
# UART available (should point to ttyAMA0, NOT ttyS0)
ls -la /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0

# ttyAMA0 exists
ls /dev/ttyAMA0
# Should show: /dev/ttyAMA0

# I2C available
ls /dev/i2c-1
# Should show: /dev/i2c-1

# Bluetooth inactive
systemctl is-active bluetooth
# Should show: inactive
```

> **Note:** Before adding `dtoverlay=disable-bt`, `/dev/serial0` points to `ttyS0`. After adding it and rebooting, it correctly points to `ttyAMA0`. The motor board requires `ttyAMA0`.

---

## Step 5: Install Python Dependencies

### System Packages
```bash
sudo apt-get install -y python3-pip python3-dev i2c-tools git python3-opencv
```

> **Trixie note:** `python3-opencv` (4.10.0) is available via apt on Debian 13 Trixie and is the recommended install method — no pip needed for OpenCV.

### Python Packages
```bash
pip3 install --break-system-packages \
    pupil-apriltags \
    flask \
    pyserial \
    smbus2 \
    pyyaml \
    numpy
```

**Note:** `--break-system-packages` is required on Trixie/Bookworm (PEP 668). `numpy` and `flask` may already be present; pip will skip them if current.

### Verify Installation
```bash
python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python3 -c "from pupil_apriltags import Detector; print('AprilTags: OK')"
python3 -c "import flask; print('Flask: OK')"
python3 -c "import serial; print('PySerial: OK')"
python3 -c "import smbus2; print('SMBus2: OK')"
python3 -c "import yaml; print('PyYAML: OK')"
python3 -c "import numpy; print(f'NumPy: OK')"
```

All should print without errors.

> **Flask version warning:** Flask 3.1+ shows a deprecation warning when accessing `flask.__version__`. This is harmless — Flask is working correctly.

---

## Step 6: Install PathfinderV2

### Clone Repository
```bash
mkdir -p /home/robot/pathfinder
cd /home/robot/pathfinder
git clone https://github.com/luminerdy/PathfinderV2.git .
```

### Verify Clone
```bash
ls skills/
# Should show skill files including strafe_nav.py, block_detect.py, etc.
```

### Verify All Imports
```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board, PLATFORM
print(f'Platform: {PLATFORM}')
from skills.block_detect import BlockDetector
from skills.strafe_nav import StrafeNavigator
print('All imports OK!')
"
```

Should print:
```
Platform: pi4
All imports OK!
```

---

## Step 7: Verify User Permissions

The `robot` user should already have the correct groups from Raspberry Pi Imager. Verify:

```bash
groups robot
```

Must include: `dialout` `i2c` `gpio` `video`

If any are missing:
```bash
sudo usermod -a -G dialout,i2c,gpio,video robot
# Then logout and login again
```

**No sudo needed to run robot code** if groups are correct.

---

## Step 8: Test Hardware

**Important:** Robot must be assembled with batteries installed before this step.

### Battery
```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board
import time
board = get_board()
time.sleep(1)
for i in range(5):
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        print(f'Battery: {mv/1000:.2f}V')
        break
    time.sleep(0.3)
else:
    print('No battery reading — check motor board power')
"
```

### Buzzer
```bash
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(0.5)
board.set_buzzer(1000, 0.1, 0.1, 2)
print('You should hear 2 beeps')
"
```

### Servos
```bash
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(0.5)
board.set_servo_position(1000, [(1,2500),(3,590),(4,2450),(5,700),(6,1500)])
print('Arm should move to camera-forward position')
"
```

### Motors
```bash
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(0.5)
board.set_motor_duty([(1,30),(2,30),(3,30),(4,30)])
time.sleep(0.5)
board.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])
print('Robot should have moved forward briefly')
"
```

### Camera
```bash
python3 -c "
import cv2
cam = cv2.VideoCapture(0)
import time; time.sleep(1)
ret, frame = cam.read()
if ret: print(f'Camera: {frame.shape[1]}x{frame.shape[0]} OK')
else: print('Camera: FAILED — check USB connection')
cam.release()
"
```

> **GStreamer warning:** On Trixie you may see `GStreamer warning: Cannot query video position` — this is harmless, the camera works fine.

### Sonar
```bash
python3 -c "
from hardware.sonar import Sonar
import time
sonar = Sonar()
for i in range(3):
    d = sonar.get_distance()
    if d: print(f'Sonar: {d:.1f} cm')
    else: print('Sonar: No reading')
    time.sleep(0.3)
"
```

### Full Test (All at Once)
```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board, PLATFORM
from hardware.sonar import Sonar
import cv2, time

print('PathfinderV2 Hardware Test')
print('Platform:', PLATFORM)
print()

board = get_board()
time.sleep(1)

# Battery
for i in range(5):
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        print(f'Battery: {mv/1000:.2f}V')
        break
    time.sleep(0.3)
else:
    print('Battery: FAILED')

# Buzzer
board.set_buzzer(1000, 0.1, 0.1, 2)
print('Buzzer: Sent 2 beeps')

# Servos
board.set_servo_position(1000, [(1,2500),(3,590),(4,2450),(5,700),(6,1500)])
time.sleep(1.5)
print('Servos: Camera forward position set')

# Motors
board.set_motor_duty([(1,30),(2,30),(3,30),(4,30)])
time.sleep(0.3)
board.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])
print('Motors: Brief forward sent')

# Sonar
sonar = Sonar()
d = sonar.get_distance()
if d: print(f'Sonar: {d:.1f} cm')
else: print('Sonar: No reading')

# Camera
cam = cv2.VideoCapture(0)
time.sleep(1)
ret, frame = cam.read()
if ret:
    print(f'Camera: {frame.shape[1]}x{frame.shape[0]} OK')
    from pupil_apriltags import Detector
    det = Detector(families='tag36h11')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = det.detect(gray)
    print(f'AprilTags: {len(tags)} detected')
cam.release()

print()
print('Hardware test complete!')
"
```

---

## Step 9: Create Startup Service

Initializes the robot at boot: stops motors, turns off LEDs, positions arm forward, checks battery, beeps when ready.

```bash
sudo tee /etc/systemd/system/pathfinder-startup.service << 'EOF'
[Unit]
Description=PathfinderV2 Robot Startup
After=network.target

[Service]
Type=oneshot
User=robot
WorkingDirectory=/home/robot/pathfinder
ExecStart=/usr/bin/python3 /home/robot/pathfinder/robot_startup.py
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable pathfinder-startup.service
sudo systemctl start pathfinder-startup.service
```

---

## Step 10: Clone the Image

Once one SD card is fully set up and tested, clone it for all robots:

### On Linux/Mac
```bash
# Read from SD card
sudo dd if=/dev/sdX of=pathfinderv2.img bs=4M status=progress

# Write to new SD card
sudo dd if=pathfinderv2.img of=/dev/sdY bs=4M status=progress
```

### On Windows
Use **Win32 Disk Imager** or **balenaEtcher** to read/write the image.

### Per-Robot Changes After Cloning
Each robot needs a unique hostname:
```bash
sudo hostnamectl set-hostname pathfinder-01  # Change number per robot
```

WiFi credentials should already be set from Step 1. If different networks are needed:
```bash
sudo nmcli dev wifi connect "SSID" password "PASSWORD"
```

> **Trixie note:** Debian 13 Trixie uses NetworkManager by default. `wpa_supplicant.conf` may not be the right place to set WiFi — use `nmcli` or the desktop network manager instead.

---

## Quick Reference: What's Installed

| Component | Version | Purpose |
|-----------|---------|---------|
| Raspberry Pi OS | Debian 13 Trixie 64-bit | Base operating system |
| Kernel | 6.12.75 | Linux kernel |
| Python | 3.13.5 | Programming language |
| OpenCV | 4.10.0 | Computer vision (via apt) |
| pupil-apriltags | 1.0.4 | AprilTag detection |
| Flask | 3.1.1 | Web control interface |
| PySerial | 3.5 | Serial communication (Pi 5) |
| SMBus2 | 0.4.3 | I2C communication (Pi 4) |
| PyYAML | 6.0.2 | Configuration files |
| NumPy | 2.2.4 | Math operations |
| PathfinderV2 | Latest | Robot framework |

## Quick Reference: Hardware Interfaces

| Interface | Device | Config |
|-----------|--------|--------|
| UART (motor board) | `/dev/ttyAMA0` | `dtoverlay=disable-bt` |
| I2C (motor board) | `/dev/i2c-1` addr `0x7A` | `dtparam=i2c_arm=on` |
| I2C (sonar) | `/dev/i2c-1` addr `0x77` | Same bus |
| Camera | `/dev/video0` | USB camera |
| GPIO (buzzer) | Pin 31 | BOARD numbering |

---

## Troubleshooting

### No battery reading
- Check motor board power switch (must be ON)
- Check battery voltage (needs >7.0V)
- Try: `sudo i2cdetect -y 1` — should show `77` (sonar) and `7A` (board)

### Motors don't move
- Battery must be >7.0V
- Motor power minimum: 28-30 to overcome friction
- Check motor cables connected to board

### Camera not found
- Check USB cable
- Try: `ls /dev/video0`
- If locked: `lsof /dev/video0` — another process using it?
- GStreamer warning is harmless on Trixie

### UART not available / serial0 → ttyS0
- Bluetooth is still active — verify `dtoverlay=disable-bt` is in `/boot/firmware/config.txt` under `[all]`
- Verify `systemctl is-active bluetooth` returns `inactive`
- Must reboot after config change
- After fix: `ls -la /dev/serial0` should show `-> ttyAMA0`

### Permission denied on I2C
- User must be in `i2c` group: `groups robot`
- Fix: `sudo usermod -a -G i2c robot` then logout/login

### Locale warnings over SSH
- Harmless but can cause `perl` warnings in apt output
- Fix: `sudo locale-gen en_US.UTF-8 && sudo update-locale LANG=en_US.UTF-8`
- Then re-login

### WiFi config on Trixie
- Debian 13 uses NetworkManager, not wpa_supplicant
- Use `nmcli dev wifi connect "SSID" password "PASSWORD"` or the desktop GUI

---

*Created: March 26, 2026*  
*Updated: April 25, 2026 — Updated for Debian 13 Trixie; added locale fix, GStreamer note, WiFi via nmcli, verified versions*  
*Tested on: Raspberry Pi 4 Model B, Debian 13.4 Trixie 64-bit, kernel 6.12.75, Python 3.13.5*
