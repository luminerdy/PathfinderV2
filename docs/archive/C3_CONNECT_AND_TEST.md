# PathfinderV2 - Connect and Test

Quick setup and testing guide for PathfinderV2 robots.

---

## Prerequisites

- Robot is powered on
- Battery charged (> 7.5V)
- Development machine connected to same network
- SSH access configured

---

## 1. SSH Connection

```bash
ssh robot@<ROBOT_IP>
```

**Default credentials:**
- Username: `robot`
- Password: *(set during installation)*

---

## 2. Start Robot

Initialize the robot and set arm to starting position:

```bash
cd ~/code/pathfinder
python3 robot_startup.py
```

**Expected output:**
- Control board connected ✓
- Motors stopped ✓
- Battery voltage displayed ✓
- Arm positioned safely ✓
- Camera detected ✓
- Double beep when ready

---

## 3. Test Arm Servos

Test each servo individually to verify connections:

```bash
cd ~/code/pathfinder
python3 test_arm_servos.py
```

**Servo test order:**
1. Servo 5 (Gripper) - should open/close
2. Servo 4 (Wrist) - should rotate
3. Servo 3 (Elbow) - should bend
4. Servo 2 (Shoulder) - should raise/lower
5. Servo 1 (Base) - should rotate left/right

**Note:** If servos don't respond, there's a known issue with the clean-room servo protocol. Use the vendor code temporarily or debug the protocol.

---

## 4. Test Motor Connections

Test each motor individually:

```bash
cd ~/code/pathfinder
python3 test_motors.py
```

**Motor test order:**
1. Motor 1 (Front Left)
2. Motor 2 (Front Right)
3. Motor 3 (Rear Left)
4. Motor 4 (Rear Right)

Each motor runs for 2 seconds forward, then stops.

---

## 5. Demo Drive Movements

**Place robot on floor before running!**

```bash
cd ~/code/pathfinder
python3 test_movement.py
```

**Movement sequence:**
1. Forward (2 seconds)
2. Backward (2 seconds)
3. Strafe Right (2 seconds)
4. Strafe Left (2 seconds)
5. Rotate (2 seconds)

**Verify:**
- Robot moves in each direction
- Mecanum strafing works
- No wheel slip
- Smooth movement

---

## 6. Demo Arm Pickup

**CURRENTLY NOT WORKING** - Servo protocol issue

When fixed, will demonstrate:
1. Detect colored block
2. Approach block
3. Position gripper
4. Close gripper
5. Lift block
6. Place on back

---

## 7. Demo Camera and Web Interface

Start web server for remote control:

```bash
cd ~/code/pathfinder
python3 pathfinder.py --webserver
```

**Then open browser:**
```
http://<ROBOT_IP>:5000
```

**Controls:**
- ▲ Forward
- ▼ Backward
- ◀ Strafe Left
- ▶ Strafe Right
- ⟲ Turn Left
- ⟳ Turn Right
- ■ Stop

**Speed Sliders:**
- Move Speed: 10-100 (forward/backward/strafe)
- Turn Speed: 0.1-1.0 (rotation rate)

**Note:** High speeds (>80) may cause sluggish response. Start at 30-50 for testing.

---

## 8. VNC Connection (Optional)

For graphical desktop access:

```bash
# Enable VNC on robot (if not already enabled)
sudo raspi-config
# Interface Options → VNC → Enable

# From your machine, use VNC Viewer
# Connect to: <ROBOT_IP>:5900
```

---

## 9. Camera Test

Test camera within VNC or via SSH:

```bash
cd ~/code/pathfinder
python3 << 'EOF'
import cv2
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imwrite('camera_test.jpg', frame)
    print("Image saved: camera_test.jpg")
    print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
else:
    print("Camera failed")
cap.release()
EOF
```

**Check focus:**
- If blurry, rotate camera lens
- If black, remove lens cap
- Verify `flip: true/false` in `config.yaml` for correct orientation

---

## 10. Calibrate Servos (If Needed)

If arm position is incorrect at startup:

```bash
cd ~/code/pathfinder
python3 find_camera_position.py
```

**Interactive servo control:**
- `1+` / `1-` : Base rotation
- `2+` / `2-` : Shoulder up/down
- `3+` / `3-` : Elbow up/down
- `4+` / `4-` : Wrist up/down
- `5+` / `5-` : Gripper open/close
- `save` : Save positions and exit

**Normal startup position:**
- Base: Centered (1500)
- Shoulder: Lowered (1700)
- Elbow: Bent (1300)
- Wrist: Neutral (1500)
- Gripper: Open (1000)

---

## Quick Status Check

Anytime you want to check robot status:

```bash
cd ~/code/pathfinder
python3 robot_status.py
```

**Shows:**
- Battery voltage
- Camera detection
- USB devices
- Serial devices
- System info

---

## Troubleshooting

### Motors don't work
- Check battery > 7.5V
- Verify UART enabled: `dtparam=uart0=on` in `/boot/firmware/config.txt`
- Check `/dev/ttyAMA10` exists
- Run `python3 check_battery.py`

### Servos don't respond
- **Known issue:** Clean-room servo protocol doesn't match board expectations
- Servos trigger motor commands instead
- **Workaround:** Use vendor code temporarily or fix protocol

### Camera not detected
- Check USB connection
- Run `lsusb` to verify camera hardware
- Try `python3 robot_startup.py` to auto-detect

### Arm pointing up on startup
- Run `python3 lower_arm.py`
- Or manually position with `find_camera_position.py`

### Battery reads wrong voltage
- Protocol bug showing 8000+V
- Working on fix
- Motors still work, ignore reading for now

---

## Useful Scripts Reference

| Script | Purpose |
|--------|---------|
| `robot_startup.py` | Full startup sequence |
| `robot_status.py` | System status check |
| `test_movement.py` | Test all movements |
| `test_motors.py` | Test motors individually |
| `test_arm_servos.py` | Test servos individually |
| `check_battery.py` | Battery voltage |
| `lower_arm.py` | Lower arm safely |
| `camera_forward_simple.py` | Position camera |
| `find_camera_position.py` | Interactive servo tuning |

---

## Next Steps

Once testing complete:
1. Motor speed calibration: `python3 tools/calibrate_motors.py --full`
2. Field navigation: Set up AprilTags
3. Block detection: Place colored blocks
4. Vision-guided pickup: Test approach sequence

---

[Return to main README](README.md)
