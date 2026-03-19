# System Dependencies

Complete list of system packages and libraries required for Pathfinder on a fresh Raspberry Pi OS installation.

## Base System Requirements

- **OS:** Raspberry Pi OS (64-bit recommended)
- **Python:** 3.9 or higher
- **Hardware:** Raspberry Pi 5 8GB (or Pi 4 4GB minimum)
- **Storage:** 16GB SD card minimum, 32GB recommended
- **Network:** Wi-Fi or Ethernet connection

## Step 1: Update System

```bash
sudo apt update
sudo apt upgrade -y
```

## Step 2: Install System Packages

### Essential Build Tools

```bash
sudo apt install -y \
    build-essential \
    cmake \
    pkg-config \
    git \
    wget \
    curl
```

### Python Development

```bash
sudo apt install -y \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-venv
```

### Serial Communication

Required for board communication:

```bash
sudo apt install -y \
    python3-serial \
    minicom \
    screen
```

### Camera Support

For USB cameras and Pi Camera:

```bash
sudo apt install -y \
    libcamera-dev \
    libcamera-apps \
    libcamera-tools \
    v4l-utils
```

### OpenCV Dependencies

Required for computer vision:

```bash
sudo apt install -y \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libleptonica-dev \
    libtesseract-dev
```

### Numeric/Scientific Libraries

For NumPy, SciPy, and math operations:

```bash
sudo apt install -y \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libatlas-base-dev
```

### Image Processing

For PIL/Pillow:

```bash
sudo apt install -y \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl-dev \
    tk-dev
```

### Networking (for Web UI)

```bash
sudo apt install -y \
    nginx \
    supervisor
```

Optional, for production deployment.

## Step 3: Configure Permissions

### Serial Port Access

Add user to dialout group for serial communication:

```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
```

**Reboot required** for group changes to take effect:

```bash
sudo reboot
```

### I2C/SPI (if needed)

Enable hardware interfaces:

```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Interface Options → SPI → Enable
# Interface Options → Serial Port → 
#   - Login shell: No
#   - Serial port hardware: Yes
```

Or via command line:

```bash
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial 2  # Hardware yes, console no
```

## Step 4: Install Python Packages

### Upgrade pip

```bash
pip3 install --upgrade pip
```

### Install Pathfinder Requirements

```bash
cd /home/robot/code/pathfinder
pip3 install -r requirements.txt --break-system-packages
```

**Note:** Use `--break-system-packages` flag on Raspberry Pi OS Bookworm+

This installs:
- numpy ✅ (required for SDK)
- pyyaml ✅ (required for config)
- opencv-python ✅ (REQUIRED - arm IK depends on this)
- opencv-contrib-python (optional, for advanced vision)
- ultralytics (YOLOv11 - downloads model on first use)
- dt-apriltags or pupil-apriltags (for AprilTag detection)
- flask, flask-cors (for web UI - optional)
- pygame, inputs (for gamepad - optional)
- pyserial ✅ (required for board communication)
- pillow (for image handling)

**Note:** Installation may take 15-30 minutes on Pi 5, longer on Pi 4.

**Known Issues:**
- matplotlib is imported by SDK but not needed - commented out in code
- System python3-opencv may conflict with pip opencv-python

## Step 5: Configure Camera

### For USB Camera

```bash
# List available cameras
v4l2-ctl --list-devices

# Test camera (replace /dev/video0 with your device)
v4l2-ctl --device=/dev/video0 --all

# Capture test image
libcamera-still -o test.jpg
```

Update `config.yaml`:
```yaml
hardware:
  camera:
    device: 0  # Usually 0, sometimes 1 or 2
```

### For Pi Camera (via libcamera)

```bash
# Test Pi Camera
libcamera-hello --info-text "fps"

# Capture image
libcamera-still -o test.jpg
```

If using Pi Camera, may need to use `picamera2` instead of OpenCV:

```bash
pip3 install picamera2
```

## Step 6: Verify Installation

### Test Python Imports

```bash
python3 -c "import numpy; print(f'NumPy {numpy.__version__}')"
python3 -c "import cv2; print(f'OpenCV {cv2.__version__}')"
python3 -c "import yaml; print('PyYAML OK')"
python3 -c "import serial; print('PySerial OK')"
python3 -c "from ultralytics import YOLO; print('YOLO OK')"
```

### Test Serial Port

```bash
python3 -c "
from sdk.common.ros_robot_controller_sdk import Board
board = Board()
print('Board connected!')
board.close()
"
```

### Test Camera

```bash
python3 -c "
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
print(f'Camera: {frame.shape if ret else \"Failed\"}')
cap.release()
"
```

## Troubleshooting

### ImportError: No module named 'cv2'

```bash
# Reinstall OpenCV
pip3 uninstall opencv-python opencv-contrib-python
pip3 install opencv-python opencv-contrib-python
```

### Serial port permission denied

```bash
# Check group membership
groups

# Should include 'dialout' and 'tty'
# If not, run:
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
sudo reboot
```

### Camera not found

```bash
# Check camera devices
ls -l /dev/video*

# Test with different device IDs
v4l2-ctl --list-devices

# For Pi Camera, ensure cable is connected correctly
vcgencmd get_camera
# Should show: supported=1 detected=1
```

### YOLO model download slow/fails

```bash
# Pre-download YOLO model
mkdir -p ~/.cache/ultralytics
cd ~/.cache/ultralytics
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov11n.pt
```

### Low memory issues (Pi 4)

```bash
# Increase swap size
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## Optional: Performance Optimization

### Overclock Pi 5 (if needed)

```bash
sudo nano /boot/firmware/config.txt

# Add:
# over_voltage=6
# arm_freq=2800

sudo reboot
```

**Warning:** Only if you have adequate cooling!

### Disable GUI (headless operation)

```bash
sudo raspi-config
# System Options → Boot / Auto Login → Console Autologin

# Or disable GUI:
sudo systemctl set-default multi-user.target
```

### Enable hardware acceleration

For faster OpenCV/video processing:

```bash
# Add to /boot/firmware/config.txt
gpu_mem=256
```

## Complete Installation Script

Save this as `install_dependencies.sh`:

```bash
#!/bin/bash
set -e

echo "Installing Pathfinder dependencies..."

# Update system
sudo apt update
sudo apt upgrade -y

# Essential tools
sudo apt install -y build-essential cmake pkg-config git wget curl

# Python
sudo apt install -y python3-dev python3-pip python3-setuptools python3-venv

# Serial
sudo apt install -y python3-serial minicom screen

# Camera
sudo apt install -y libcamera-dev libcamera-apps libcamera-tools v4l-utils

# OpenCV dependencies
sudo apt install -y \
    libopencv-dev python3-opencv \
    libatlas-base-dev libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libgtk-3-dev libhdf5-dev libleptonica-dev

# Numeric libraries
sudo apt install -y gfortran libopenblas-dev liblapack-dev

# Permissions
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# Upgrade pip
pip3 install --upgrade pip

echo ""
echo "System dependencies installed!"
echo "Next steps:"
echo "  1. Reboot: sudo reboot"
echo "  2. Install Python packages: pip3 install -r requirements.txt"
echo "  3. Test hardware: python3 test_hardware.py"
```

Make executable and run:

```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

## Estimated Installation Times

- **System packages:** 10-15 minutes
- **Python packages:** 15-30 minutes (Pi 5), 30-60 minutes (Pi 4)
- **Total:** 30-45 minutes on Pi 5

## Disk Space Requirements

- **Base OS:** ~5 GB
- **System packages:** ~2 GB
- **Python packages:** ~1.5 GB
- **YOLO models:** ~10 MB per model
- **Total minimum:** 10 GB
- **Recommended:** 16 GB+ for workspace and logs

---

**Last Updated:** March 2026  
**Tested On:** Raspberry Pi OS (64-bit), Debian version 12 (bookworm)
