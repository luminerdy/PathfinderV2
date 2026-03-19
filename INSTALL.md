# Pathfinder Installation Guide

## Prerequisites

### Hardware
- Educational humanoid robot platform with Raspberry Pi 5 8GB
- USB camera or Pi Camera
- Ultrasonic sensor (HC-SR04)
- 7.4V LiPo battery

### Software
- Raspberry Pi OS (64-bit recommended)
- Python 3.9 or higher
- No external dependencies - all SDK code included!

## Step 1: Clone or Copy Code

```bash
# If using git
cd /home/robot/code
git clone <repository-url> pathfinder

# Or copy from existing location
# (code already exists at /home/robot/code/pathfinder)
```

## Step 2: Install System Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install OpenCV dependencies
sudo apt install -y \
    python3-opencv \
    libopencv-dev \
    python3-pip \
    python3-dev \
    build-essential

# Install camera support
sudo apt install -y \
    libcamera-dev \
    libcamera-apps

# Install serial support (if not already)
sudo apt install -y python3-serial
```

## Step 3: Install Python Dependencies

```bash
cd /home/robot/code/pathfinder

# Upgrade pip
pip3 install --upgrade pip

# Install requirements
pip3 install -r requirements.txt

# Note: This may take 10-15 minutes on Pi 5
# YOLOv11 will download model weights on first run
```

## Step 4: Configure Hardware

Edit `config.yaml`:

```bash
nano config.yaml
```

Verify settings match your hardware:
- Serial port (usually `/dev/ttyAMA0`)
- Camera device (usually `0`)
- Servo IDs and ranges
- Wheel dimensions

## Step 5: Test Installation

### Test hardware connection

```bash
python3 -c "
from hardware import Board
board = Board()
print('Board connected!')
board.beep(0.1)
board.close()
"
```

### Test camera

```bash
python3 -c "
from hardware import Camera
import cv2
cam = Camera()
cam.open()
frame = cam.read()
print(f'Frame captured: {frame.shape if frame is not None else None}')
cam.close()
"
```

### Test pathfinder

```bash
# Quick status check
python3 pathfinder.py --no-camera --no-sonar
# Press Ctrl+C to exit
```

## Step 6: Run First Demo

```bash
# Basic movement demo
python3 pathfinder.py --demo d1_basic_drive

# If successful, robot should:
# - Beep once
# - Move arm to home position
# - Execute movement patterns
# - Stop and beep again
```

## Troubleshooting

### "Board not found" or serial errors

```bash
# Check serial port permissions
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# Reboot required
sudo reboot
```

### Camera not working

```bash
# Check camera devices
v4l2-ctl --list-devices

# Try different device ID in config.yaml
# Usually 0, sometimes 1 or 2
```

### Import errors

```bash
# Verify SDK imports work
cd /home/robot/code/pathfinder
python3 -c "
from sdk.common.ros_robot_controller_sdk import Board
print('SDK import successful')
"
```

### YOLOv11 slow or crashing

```bash
# Use smaller model (already default in config.yaml)
# yolov11n.pt (nano) is fastest on Pi 5

# For even faster inference, consider:
# - Reducing camera resolution
# - Lowering confidence threshold
# - Using fewer classes
```

### Servo calibration needed

If arm movements are inaccurate:

```bash
# Edit Deviation.yaml in project root
nano /home/robot/code/pathfinder/Deviation.yaml

# Adjust servo offsets as needed
# Format: 'servo_id': offset_value
```

## Optional: Enable Services

### Auto-start on boot (optional)

```bash
# Create systemd service
sudo nano /etc/systemd/system/pathfinder.service
```

Add:
```ini
[Unit]
Description=Pathfinder Robot Service
After=network.target

[Service]
Type=simple
User=robot
WorkingDirectory=/home/robot/code/pathfinder
ExecStart=/usr/bin/python3 /home/robot/code/pathfinder/pathfinder.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable pathfinder.service
sudo systemctl start pathfinder.service
```

## Next Steps

1. **Run all demos** to verify functionality
2. **Calibrate camera offset** for accurate manipulation
3. **Test AprilTag detection** with printed tags
4. **Train custom YOLO model** for workshop objects
5. **Build workshop course** with blocks and tags

## Workshop Preparation

For running PathfinderBot workshops:

1. **Print AprilTags**: Use family `tag36h11`, IDs 0-10
2. **Prepare colored blocks**: Red, blue, green for sorting
3. **Test course layout**: Verify robot can navigate safely
4. **Charge batteries**: Full charge before each session
5. **Backup SD cards**: Clone working images

## Support

- **Documentation**: See `README.md`
- **GitHub**: (repository link)
- **Issues**: (issue tracker link)
- **PathfinderBot Workshop**: https://github.com/stemoutreach/PathfinderBot

---

Installation complete! Run `python3 pathfinder.py --demo d1_basic_drive` to start.
