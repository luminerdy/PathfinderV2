# Fresh Robot OS Installation Guide

Complete setup instructions for PathfinderV2 on a fresh Raspberry Pi OS installation.

## Prerequisites

**Hardware:**
- Raspberry Pi 5 (8GB recommended, 4GB minimum)
- MicroSD card (32GB+ recommended)
- MasterPi expansion board (or compatible motor controller)
- 2x 18650 batteries (high-discharge, 20A+ rating)
- USB camera (optional, for vision)
- I2C ultrasonic sensor (optional)

**Software:**
- Fresh Raspberry Pi OS (Bookworm or newer)
- Internet connection for setup

## Step-by-Step Setup

### 1. Flash Raspberry Pi OS

**Download Raspberry Pi Imager:**
- https://www.raspberrypi.com/software/

**Flash OS:**
1. Insert microSD card
2. Open Raspberry Pi Imager
3. Choose: "Raspberry Pi OS (64-bit)" (Bookworm or Trixie)
4. Select your microSD card
5. Click gear icon → Configure:
   - Set hostname: `masterpi` (or your choice)
   - Enable SSH
   - Set username/password
   - Configure WiFi (optional)
6. Write to SD card
7. Insert SD card into Pi 5

### 2. Initial Pi Setup

**First boot:**
```bash
# SSH into Pi (or use monitor/keyboard)
ssh pi@masterpi.local

# Update system
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    i2c-tools \
    v4l-utils \
    libopencv-dev
```

### 3. Enable Hardware Interfaces

**Critical: Edit boot configuration**

```bash
sudo nano /boot/firmware/config.txt
```

Add these lines at the end:

```ini
# PathfinderV2 - Enable hardware interfaces
dtparam=i2c_arm=on          # For I2C sensors (sonar)
dtparam=uart0=on            # For motor controller (REQUIRED!)
usb_max_current_enable=1    # USB power delivery
```

**Save (Ctrl+O, Enter) and exit (Ctrl+X)**

**Reboot:**
```bash
sudo reboot
```

### 4. Verify Hardware After Reboot

**Check UART0:**
```bash
ls -la /dev/ttyAMA0
# Should show: crw-rw---- 1 root dialout 204, 64 ...
```

**Check I2C:**
```bash
ls -la /dev/i2c-1
# Should show: crw-rw---- 1 root i2c 89, 1 ...
```

**Add user to hardware groups:**
```bash
sudo usermod -a -G dialout,i2c,gpio,spi $USER
# Log out and back in for groups to take effect
```

### 5. Install PathfinderV2

**Clone repository:**
```bash
cd ~
mkdir -p code
cd code
git clone https://github.com/luminerdy/PathfinderV2.git pathfinder
cd pathfinder
```

**Install Python dependencies:**
```bash
# Install with pip (recommended)
pip3 install -r requirements.txt --break-system-packages

# OR create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Wait for installation to complete** (~5-10 minutes on Pi 5)

### 6. Test Installation

**Check battery voltage:**
```bash
cd ~/code/pathfinder
python3 check_battery.py
```

Expected output:
```
PathfinderV2 Battery Check
----------------------------------------
Battery: 8.XX V
Status:  GREEN EXCELLENT
Note:    Fully charged and ready!

OK: Ready for operation
```

**If battery reads None:**
- Check physical connections (expansion board to Pi)
- Verify `/dev/ttyAMA0` exists
- Check battery is installed and powered on

**Test motor:**
```bash
python3 -c "
from hardware import Board
import time
board = Board()
print('Motor test - watch robot!')
board.set_motor_duty(1, 50)
time.sleep(2)
board.set_motor_duty(1, 0)
print('Done!')
"
```

**Test servo:**
```bash
python3 -c "
from hardware import Board
import time
board = Board()
print('Servo test - watch arm!')
board.set_servo_position(5, 500, 0.5)
time.sleep(1)
board.set_servo_position(5, 2000, 0.5)
time.sleep(1)
board.set_servo_position(5, 1500, 0.5)
print('Done!')
"
```

### 7. Run Demo Programs

**D1 - Basic Drive:**
```bash
python3 pathfinder.py --demo d1_basic_drive
```

**D2 - Sonar (if connected):**
```bash
python3 pathfinder.py --demo d2_sonar
```

**D3 - Arm Basics:**
```bash
python3 pathfinder.py --demo d3_arm_basics
```

## Troubleshooting

### Battery Voltage Reads None

**Cause:** UART0 not enabled or board not connected

**Fix:**
1. Check `/dev/ttyAMA0` exists: `ls -la /dev/ttyAMA0`
2. If missing: Add `dtparam=uart0=on` to `/boot/firmware/config.txt`
3. Reboot: `sudo reboot`
4. Check physical connections

### Motors Don't Move

**Check battery voltage first:**
```bash
python3 check_battery.py
```

**If battery < 7.5V:**
- Charge batteries before testing
- Low voltage causes brownout during motor operation

**If battery OK but motors silent:**
- Check motor wires connected to expansion board
- Verify expansion board powered on
- Test with simple motor command (see Step 6)

### Under-Voltage Warnings (⚡ icon)

**Cause:** Battery voltage too low or high current draw

**Fix:**
1. **Charge battery to > 7.5V** (most common)
2. Add `usb_max_current_enable=1` to config.txt (if not present)
3. Use high-discharge 18650 cells (20A+ rating)
4. Check physical power connections

**See:** [BATTERY_SAFETY.md](../BATTERY_SAFETY.md) for details

### Camera Not Working

**Expected:** Camera warnings on boot if not connected

**If camera IS connected:**
```bash
# Check camera detected
v4l2-ctl --list-devices

# Test camera
python3 -c "
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(f'Camera OK: {ret}')
cap.release()
"
```

### I2C Sonar Not Reading

**Check I2C devices:**
```bash
i2cdetect -y 1
```

Should show device at address `0x77`.

**If not detected:**
- Check sonar physically connected
- Verify `dtparam=i2c_arm=on` in config.txt
- Check wiring (SDA, SCL, VCC, GND)

## Configuration Files

### config.yaml

Main robot configuration at `~/code/pathfinder/config.yaml`:

```yaml
hardware:
  board:
    serial_port: "/dev/ttyAMA0"
    baud_rate: 1000000
    
  chassis:
    wheel_base: 67        # mm
    track_width: 59       # mm
    wheel_diameter: 65    # mm
    
  camera:
    device: 0
    width: 640
    height: 480
    fps: 30

vision:
  yolo:
    model: "yolo11n.pt"
    confidence: 0.5
```

### Deviation.yaml (Optional)

Create for servo calibration:

```yaml
# Servo offsets (pulse width adjustments)
'1': 0      # Base
'3': 0      # Shoulder  
'4': 0      # Elbow
'5': 0      # Wrist/Gripper
'6': 0      # Base rotate
```

Run calibration to adjust these values for your specific robot.

## Next Steps

**After successful installation:**

1. **Calibrate servos** (if needed) - see [TESTING.md](../TESTING.md)
2. **Test all demos** - verify full functionality
3. **Workshop deployment** - PathfinderV2 is ready!

**For development:**
- Explore API in `capabilities/` directory
- Create custom demos in `demos/` directory
- Add skills to `api/` for web/gamepad control

## Reference Documentation

- **[INSTALL.md](../INSTALL.md)** - Detailed installation steps
- **[BATTERY_SAFETY.md](../BATTERY_SAFETY.md)** - Power requirements and safety
- **[MOTOR_SOLUTION.md](MOTOR_SOLUTION.md)** - Motor troubleshooting
- **[TESTING.md](../TESTING.md)** - Hardware testing procedures
- **[README.md](../README.md)** - Project overview

## Support

**Issues or questions:**
- GitHub: https://github.com/luminerdy/PathfinderV2/issues
- Check existing docs in `/docs` directory
- Review [HIWONDER_SYSTEM_REFERENCE.md](reference/HIWONDER_SYSTEM_REFERENCE.md) for Hiwonder compatibility

---

**Last Updated:** March 20, 2026  
**Tested On:** Raspberry Pi 5 8GB, Debian 13 (Trixie)  
**Status:** ✅ Verified working
