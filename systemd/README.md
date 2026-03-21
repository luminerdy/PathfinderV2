# PathfinderV2 Auto-Start Services

Systemd services for automatic robot startup on boot.

## Services

### pathfinder-startup.service
- **Purpose:** Initialize hardware and position arm
- **Type:** One-shot (runs once at boot)
- **What it does:**
  - Connects to control board
  - Stops motors
  - Checks battery
  - Positions arm to camera-forward
  - Turns off RGB LEDs (power saving)
  - Beeps when ready

### pathfinder-drive.service
- **Purpose:** Web-based drive control with camera
- **Port:** 5000
- **Features:**
  - Live camera stream
  - Drive controls (forward/back/strafe/rotate)
  - Speed slider
  - Battery status
- **Auto-restart:** Yes (if crashes)

### pathfinder-servo.service
- **Purpose:** Web-based servo control
- **Port:** 5001
- **Features:**
  - Individual servo sliders
  - Preset positions (Rest, Camera Forward)
  - Safety limits
  - Real-time position display
- **Auto-restart:** Yes (if crashes)

## Installation

```bash
cd ~/code/pathfinder
sudo bash install_services.sh
```

The installer will:
1. Copy service files to `/etc/systemd/system/`
2. Reload systemd
3. Enable services for auto-start
4. Optionally start services immediately

## Usage

### Check Status
```bash
sudo systemctl status pathfinder-startup
sudo systemctl status pathfinder-drive
sudo systemctl status pathfinder-servo
```

### View Logs
```bash
# Startup logs
sudo journalctl -u pathfinder-startup -f

# Drive interface logs
sudo journalctl -u pathfinder-drive -f

# Servo interface logs
sudo journalctl -u pathfinder-servo -f
```

### Manual Control
```bash
# Start services
sudo systemctl start pathfinder-startup
sudo systemctl start pathfinder-drive
sudo systemctl start pathfinder-servo

# Stop services
sudo systemctl stop pathfinder-drive
sudo systemctl stop pathfinder-servo

# Restart services
sudo systemctl restart pathfinder-drive
```

### Disable Auto-Start
```bash
sudo systemctl disable pathfinder-startup
sudo systemctl disable pathfinder-drive
sudo systemctl disable pathfinder-servo
```

## Boot Sequence

1. **System boots**
2. **pathfinder-startup** runs → arm positions forward
3. **pathfinder-drive** starts → web interface on :5000
4. **pathfinder-servo** starts → servo control on :5001
5. **Robot ready!** Access via browser

## After Reboot

Just power on the robot and wait ~30 seconds.

Then open browser:
- **Drive:** `http://<ROBOT_IP>:5000`
- **Servos:** `http://<ROBOT_IP>:5001`

No manual intervention needed!

## Troubleshooting

### Services won't start
```bash
# Check if enabled
systemctl is-enabled pathfinder-startup

# Check for errors
sudo journalctl -u pathfinder-startup --no-pager
```

### Web interface not accessible
```bash
# Check if service running
sudo systemctl status pathfinder-drive

# Check port
sudo netstat -tlnp | grep 5000
```

### Camera not working
- Check USB connection
- Battery voltage > 7.5V
- Camera device exists: `ls /dev/video*`

### Arm doesn't position
- Check startup logs for errors
- Battery voltage > 7.5V
- Servos connected properly

## Uninstall

```bash
sudo systemctl stop pathfinder-drive pathfinder-servo
sudo systemctl disable pathfinder-startup pathfinder-drive pathfinder-servo
sudo rm /etc/systemd/system/pathfinder-*.service
sudo systemctl daemon-reload
```

## Development

When testing changes, stop the services first:

```bash
sudo systemctl stop pathfinder-drive pathfinder-servo
```

Then run manually:
```bash
python3 web_drive.py   # Test drive interface
python3 web_servo.py   # Test servo interface
```

Restart services when done:
```bash
sudo systemctl start pathfinder-drive pathfinder-servo
```
