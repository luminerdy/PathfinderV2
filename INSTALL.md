# Installation

For complete setup instructions, see:

- **[A1: Robot Pi OS Build](docs/setup/A1_ROBOT_PI_OS_BUILD.md)** — Full SD card image creation guide
- **[Battery Safety](BATTERY_SAFETY.md)** — Voltage requirements and charging

## Quick Install (if OS is already set up)

```bash
# Clone repository
mkdir -p /home/robot/pathfinder
cd /home/robot/pathfinder
git clone https://github.com/luminerdy/PathfinderV2.git .

# Install Python packages
pip3 install --break-system-packages \
    opencv-python-headless pupil-apriltags flask pyserial smbus2 pyyaml numpy

# Verify
python3 -c "from lib.board import get_board, PLATFORM; print('Platform:', PLATFORM)"
```

## Hardware Requirements

- Raspberry Pi 4 (4GB+) — competition platform
- Raspberry Pi 5 (8GB) — development only (power issues with motors)
- MasterPi robot platform
- 2x 18650 batteries (>7.0V for Pi 4, >8.2V for Pi 5)
- USB camera
- AprilTags (tag36h11, 10 inch, IDs 578-585)

## Servo Mapping

| Servo | Function | Range |
|-------|----------|-------|
| 1 | Claw/Gripper | 1475 (closed) – 2500 (open) |
| 2 | Does not exist | — |
| 3 | Wrist | 500 – 2500 |
| 4 | Elbow | 500 – 2500 |
| 5 | Shoulder | 500 – 2500 |
| 6 | Base rotation | 500 – 2500 (1500 = center) |
