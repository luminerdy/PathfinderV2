# Motor Solution - Found!

## Problem
Motors don't work on our PathfinderV2 code, but work on Hiwonder image.

## Root Cause
**Missing UART0 configuration** in `/boot/firmware/config.txt`

## Investigation Results from Working Robot (10.10.10.137)

### System Configuration

**Serial Devices Present:**
```
/dev/ttyAMA0   - UART0 (connected to motor controller board)
/dev/ttyAMA10  - UART (for console/other)
/dev/serial0 -> ttyAMA10
```

**Boot Config (`/boot/firmware/config.txt`):**
```ini
dtparam=i2c_arm=on      # Required for I2C devices (sonar)
dtparam=uart0=on        # ← THIS IS THE KEY! Enables /dev/ttyAMA0
```

### Code That Works

Simple test that DOES work on Hiwonder image:
```python
from common.ros_robot_controller_sdk import Board
import time

board = Board()  # Defaults to /dev/ttyAMA0
board.enable_reception()

board.set_motor_duty([[1, 60]])
time.sleep(2)
board.set_motor_duty([[1, 0]])
```

### Services Running

**MasterPi Service (`/etc/systemd/system/masterpi.service`):**
```
ExecStart=/home/pi/MasterPi/MasterPi.py
```

Runs on boot, creates persistent Board instance:
- Creates `board = Board()`
- Calls `board.enable_reception()` twice
- Starts RPC server for remote control
- Starts MJPEG camera server
- Runs voltage monitoring thread

**Also Running:**
- `hw_button_scan.service` - Button handler (KEY1)
- `hw_remote.service` - Remote control
- `hw_wifi.service` - WiFi management

### NO ROS
Confirmed: No ROS installed. Pure Python + systemd services.

## Solution for Our Robot

### Step 1: Enable UART0 and USB Power

Edit `/boot/firmware/config.txt` and add:
```ini
dtparam=i2c_arm=on
dtparam=uart0=on
usb_max_current_enable=1
```

**Note:** `usb_max_current_enable=1` allows USB ports to draw more current, which may help with under-voltage warnings during high-load operation.

### Step 2: Reboot
```bash
sudo reboot
```

### Step 3: Verify
After reboot, check:
```bash
ls -la /dev/ttyAMA0  # Should exist now
```

### Step 4: Update Our Code

Change default device in `config.yaml`:
```yaml
hardware:
  board:
    serial_port: "/dev/ttyAMA0"  # Change from /dev/ttyAMA10
    baud_rate: 1000000
```

Or update `lib/ros_robot_controller_sdk.py` to use `/dev/ttyAMA0` by default (it already does).

### Step 5: Test

```bash
cd /home/robot/code/pathfinder
python3 -c "
from lib.ros_robot_controller_sdk import Board
import time

board = Board()  # Will use /dev/ttyAMA0
board.enable_reception()

print('Testing motor...')
board.set_motor_duty([[1, 60]])
time.sleep(2)
board.set_motor_duty([[1, 0]])
print('Done')
"
```

## Why This Works

**Pi 5 UART Configuration:**
- By default, only UART10 is enabled (ttyAMA10) for console
- Motor controller board is connected to UART0
- Need to explicitly enable UART0 with `dtparam=uart0=on`
- This creates `/dev/ttyAMA0` device node

**Hiwonder Pre-Configuration:**
- Their OS image already has `dtparam=uart0=on` configured
- This is why their code "just works"
- This is why `/dev/ttyAMA0` exists on their system

## Optional: Run MasterPi.py as Service

If you want the robot to auto-start like the Hiwonder image:

Create `/etc/systemd/system/pathfinder.service`:
```ini
[Unit]
Description=Pathfinder Robot Service
After=network.target

[Service]
Type=simple
User=robot
WorkingDirectory=/home/robot/code/pathfinder
ExecStart=/usr/bin/python3 /home/robot/code/pathfinder/pathfinder.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable pathfinder.service
sudo systemctl start pathfinder.service
```

## Testing Checklist

When back on the robot:

- [ ] Add `dtparam=uart0=on` to `/boot/firmware/config.txt`
- [ ] Add `dtparam=i2c_arm=on` (for sonar I2C)
- [ ] Reboot
- [ ] Verify `/dev/ttyAMA0` exists
- [ ] **CHECK BATTERY VOLTAGE FIRST!** (Must be > 7.5V)
- [ ] Test battery voltage reading
- [ ] Test motor with simple script (low duty cycle)
- [ ] Test servo
- [ ] Run full `test_hardware.py`
- [ ] Test all demos (D1, D2, D3)

## ⚠️ CRITICAL: Battery Requirements

**ALWAYS check battery voltage before running motors!**

**Voltage Requirements:**
- **Minimum for motors:** 7.5V
- **Minimum safe:** 7.0V  
- **Fully charged:** 8.4V (2x 4.2V lithium cells)
- **Critical low:** < 7.0V → CHARGE IMMEDIATELY

**Symptoms of Low Battery:**
- Robot shuts down when motors run (brownout protection)
- LEDs dim during operation
- Power cuts out completely (not graceful shutdown)
- Robot reboots immediately after power loss

**Why This Happens:**
1. Motors draw high current (several amps)
2. Low battery can't maintain voltage under load
3. Voltage drops below protection threshold (~6V)
4. Battery protection circuit cuts power instantly
5. Prevents over-discharge damage to lithium cells

**Protection is Working Correctly!** This saves your battery from damage.

## Success Criteria

When properly configured:
✅ Battery voltage reads correctly (not None)
✅ Motors respond to `set_motor_duty()`
✅ Servos respond to `pwm_servo_set_position()`
✅ All hardware tests pass

---

**Bottom Line:** Just need `dtparam=uart0=on` in boot config!
