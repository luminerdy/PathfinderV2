# Systemd Services

## pathfinder-startup.service

Runs at boot. Initializes robot to known good state:
- Stops motors
- Turns off LEDs
- Positions arm camera-forward
- Checks battery
- Beeps twice when ready

### Install
```bash
sudo cp systemd/pathfinder-startup.service /etc/systemd/system/
sudo systemctl enable pathfinder-startup
sudo systemctl start pathfinder-startup
```

### Check
```bash
sudo systemctl status pathfinder-startup
sudo journalctl -u pathfinder-startup --no-pager
```

## Web Control

Start manually when needed (not a boot service):
```bash
cd /home/robot/pathfinder
python3 web/web_control.py
# Open: http://<ROBOT_IP>:8080
```

Works on both Pi 4 and Pi 5 via auto-detection.
