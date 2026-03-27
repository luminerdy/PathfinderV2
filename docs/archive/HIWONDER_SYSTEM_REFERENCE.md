# Hiwonder MasterPi System Reference

Complete documentation of the Hiwonder factory image (10.10.10.137).

## System Information

- **Hostname:** raspberrypi
- **OS:** Raspberry Pi OS (Debian-based)
- **Kernel:** 6.6.74+rpt-rpi-2712
- **Python:** 3.11.2
- **Architecture:** aarch64 (64-bit ARM)
- **No ROS** - Pure Python implementation

## Boot Configuration

### `/boot/firmware/config.txt`
```ini
# I2C (for sonar and other sensors)
dtparam=i2c_arm=on

# UART0 (CRITICAL - enables /dev/ttyAMA0 for motor controller)
dtparam=uart0=on

# USB
usb_max_current_enable=1

# Video/Display
dtoverlay=vc4-kms-v3d
max_framebuffers=2
disable_fw_kms_setup=1
camera_auto_detect=1
display_auto_detect=1

# Performance
arm_boost=1
arm_64bit=1
disable_overscan=1

# Audio
dtparam=audio=on

# Other
auto_initramfs=1
avoid_warnings=1
```

### `/boot/firmware/cmdline.txt`
```
console=serial0,115200 console=tty1 root=PARTUUID=2074da14-02 rootfstype=ext4 fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles cfg80211.ieee80211_regdom=US
```

## Serial Devices

```
/dev/ttyAMA0   - UART0 (motor controller) - enabled by dtparam=uart0=on
/dev/ttyAMA10  - Console UART
/dev/serial0   - Symlink to ttyAMA10
```

**Default Board() uses `/dev/ttyAMA0` @ 1000000 baud**

## Systemd Services

### Core Robot Services

**masterpi.service**
```ini
[Service]
Type=simple
User=pi
Restart=always
RestartSec=5
ExecStart=/home/pi/MasterPi/MasterPi.py
```
Runs main robot control loop, RPC server, camera streaming.

**hw_button_scan.service**
```ini
ExecStart=/home/pi/hiwonder-toolbox/hw_button_scan.py
```
- Monitors GPIO buttons (KEY1=GPIO13, KEY2=GPIO23)
- KEY1 press: runs hardware_test.py (servo/motor test)
- KEY1 long-press (3s): resets WiFi config
- KEY2 long-press (3s): system halt

**hw_wifi.service**
```ini
ExecStart=/home/pi/hiwonder-toolbox/hw_wifi.py
```
Manages WiFi AP/STA modes, hotspot creation.

**hw_remote.service**
```ini
ExecStart=/home/pi/hiwonder-toolbox/hw_remote.py
```
Remote control interface.

**hw_find.service**
```ini
ExecStart=/home/pi/hiwonder-toolbox/hw_find.py
```
Device discovery/network finding.

## Python Packages

```
Flask==2.2.2
numpy==1.24.2
opencv-contrib-python==4.9.0.80
opencv-python==4.9.0.80
pygame==2.1.2
pyserial==3.5
PyYAML==6.0.1
ultralytics==8.1.2
```

## Directory Structure

```
/home/pi/MasterPi/
├── MasterPi.py              # Main entry point
├── rpc_server.py            # JSON-RPC server for remote control
├── mjpg_server.py           # MJPEG camera streaming
├── Camera.py                # Camera wrapper
├── Deviation.yaml           # Servo calibration offsets
├── lab_config.yaml          # Color detection HSV ranges
├── command                  # Command log
├── action_groups/           # Pre-recorded movement sequences
├── board_demo/
│   └── hardware_test.py     # Servo/motor self-test (KEY1 triggers this)
├── functions/               # Game modes/behaviors
│   ├── avoidance.py
│   ├── color_detect.py
│   ├── color_recognition.py
│   ├── color_sorting.py
│   ├── color_tracking.py
│   ├── color_warning.py
│   ├── face_recognition.py
│   ├── lab_adjust.py
│   ├── remote_control.py
│   ├── running.py
│   └── visual_patrol.py
├── masterpi_sdk/
│   ├── common_sdk/common/
│   │   ├── ros_robot_controller_sdk.py
│   │   ├── mecanum.py
│   │   ├── sonar.py
│   │   ├── misc.py
│   │   └── yaml_handle.py
│   └── common_sdk/kinematics/
│       └── arm_move_ik.py
├── mecanum_control/         # Mecanum drive control
├── CameraCalibration/       # Camera calibration tools
└── masterpi_pc_software/    # PC control software

/home/pi/hiwonder-toolbox/
├── hw_button_scan.py        # GPIO button handler
├── hw_find.py               # Device discovery
├── hw_remote.py             # Remote control
├── hw_wifi.py               # WiFi management
├── hiwonder_wifi_conf.py    # WiFi configuration
└── *.service                # Systemd unit files
```

## MasterPi.py Initialization Sequence

```python
# 1. Create global instances
AK = ArmIK()
board = Board()  # Defaults to /dev/ttyAMA0, 1000000 baud
board.enable_reception()

# 2. Create sonar
HWSONAR = Sonar.Sonar()  # I2C device

# 3. Call enable_reception AGAIN
board.enable_reception()

# 4. Start voltage detection thread
VD = threading.Thread(target=voltageDetection)
VD.daemon = True
VD.start()

# 5. Initialize modules and call set_board()
def startTruckPi():
    AK.board = board
    rpc_server.board = board
    rpc_server.AK = AK
    rpc_server.set_board()  # Called twice in code
    
    # Initialize sonar RGB
    HWSONAR.setRGBMode(0)
    HWSONAR.setPixelColor(0, (0,0,0))
    HWSONAR.setPixelColor(1, (0,0,0))
    
    # Distribute references
    RemoteControl.HWSONAR = HWSONAR
    Avoidance.HWSONAR = HWSONAR
    # ... etc
```

## set_board() Function (in rpc_server.py)

```python
def set_board():
    # Distribute board reference to all modules
    color_detect.board = board
    color_tracking.board = board
    color_sorting.board = board
    visual_patrol.board = board
    avoidance.board = board
    
    # Distribute ArmIK reference
    color_detect.AK = AK
    color_tracking.AK = AK
    color_sorting.AK = AK
    visual_patrol.AK = AK
    avoidance.AK = AK
    
    # Initialize default position
    color_detect.initMove()
    
    # BUZZER BEEP (might be initialization signal?)
    board.set_buzzer(1900, 0.3, 0.7, 1)
```

## GPIO Button Handler

**KEY1 (GPIO 13):**
- Short press: Runs `/home/pi/MasterPi/board_demo/hardware_test.py`
- Long press (3 sec): Resets WiFi config

**KEY2 (GPIO 23):**
- Long press (3 sec): System halt

```python
# From hw_button_scan.py
chip = gpiod.Chip('gpiochip4')
key1 = chip.get_line(13)  # KEY1
key2 = chip.get_line(23)  # KEY2

# On KEY1 short press:
os.system("python3 /home/pi/MasterPi/board_demo/hardware_test.py")
```

## Servo Calibration

### Deviation.yaml
```yaml
'1': 0      # Servo 1 offset
'3': 59     # Servo 3 offset
'4': 72     # Servo 4 offset
'5': 63     # Servo 5 offset
'6': -95    # Servo 6 offset
```

Applied in `rpc_server.py`:
```python
# Actual pulse = Control pulse + Deviation
pulses = int(map(angle, 90, -90, 500, 2500)) + deviation_data['{}'.format(servo_id)]
board.pwm_servo_set_position(duration, [[servo_id, pulses]])
```

## Color Detection Configuration

### lab_config.yaml
HSV ranges for color recognition:

```yaml
red:
  min: [31, 158, 130]
  max: [255, 255, 255]

blue:
  min: [37, 84, 35]
  max: [255, 255, 111]

green:
  min: [0, 0, 0]
  max: [200, 104, 235]

# ... etc
```

## RPC Server Interface

**Port:** Unknown (need to check)
**Protocol:** JSON-RPC over HTTP (Werkzeug)

**Example RPC Methods:**
```python
@dispatcher.add_method
def SetPWMServo(*args, **kwargs):
    # args: [duration_ms, servo1, pulse1, servo2, pulse2, ...]
    # Applies deviation corrections
    # Calls board.pwm_servo_set_position()

@dispatcher.add_method
def SetMovementAngle(angle):
    # Controls mecanum chassis movement
    # angle=-1: stop
    # else: move at 70 speed, specified angle
```

## User Permissions

```
pi : pi adm dialout cdrom sudo audio video plugdev games users input render netdev spi i2c gpio lpadmin
```

Key groups for hardware access:
- `dialout` - Serial ports
- `gpio` - GPIO access
- `spi` - SPI devices
- `i2c` - I2C devices

## Camera Configuration

- Auto-detection enabled in config.txt
- USB camera typically at /dev/video0
- MJPEG streaming via mjpg_server.py
- Resolution configurable in code

## Network Configuration

- AP mode by default (creates WiFi hotspot "WH-xxxxx")
- Can switch to STA mode (connect to existing WiFi)
- LED2 on expansion board:
  - Flashing = AP mode
  - Solid = STA mode
- Managed by hw_wifi.service

## Testing Notes

**Simple motor test (confirmed working on this system):**
```python
from common.ros_robot_controller_sdk import Board
import time

board = Board()  # Uses /dev/ttyAMA0
board.enable_reception()

board.set_motor_duty([[1, 60]])
time.sleep(2)
board.set_motor_duty([[1, 0]])
```

**Result:** Motor 1 ran for 2 seconds ✅

## Key Differences from Our PathfinderV2

| Aspect | Hiwonder | PathfinderV2 |
|--------|----------|--------------|
| UART device | /dev/ttyAMA0 | /dev/ttyAMA10 (before fix) |
| Boot config | dtparam=uart0=on ✅ | Missing ❌ |
| Structure | Flat imports | Nested sdk/ |
| Startup | systemd service | Manual run |
| RPC server | Built-in | Not implemented |
| Camera streaming | MJPEG server | Not implemented |
| Button handler | GPIO service | Not implemented |
| Servo calibration | Deviation.yaml | config.yaml |
| Color config | lab_config.yaml | Not implemented |

## What We Learned

1. **UART0 must be enabled** - `dtparam=uart0=on` is critical
2. **I2C must be enabled** - `dtparam=i2c_arm=on` for sonar
3. **Board instance is persistent** - Lives for entire program lifecycle
4. **enable_reception() called twice** - Not sure why, but they do it
5. **set_buzzer() might be init signal** - Called after board setup
6. **Servo offsets are essential** - Deviation.yaml corrects mechanical tolerances
7. **No ROS needed** - Pure Python works fine
8. **systemd services auto-start** - Robot ready on boot
9. **GPIO buttons** - Hardware testing via physical button
10. **JSON-RPC for remote control** - Web/app can control robot

## Next Steps for PathfinderV2

**Critical:**
- [ ] Add `dtparam=uart0=on` to boot config
- [ ] Add `dtparam=i2c_arm=on` to boot config
- [ ] Test motor functionality after reboot

**Optional Enhancements:**
- [ ] Implement deviation/calibration system
- [ ] Add systemd service for auto-start
- [ ] Implement GPIO button handler (KEY1 for self-test)
- [ ] Add RPC server for remote control
- [ ] Add MJPEG camera streaming
- [ ] Create color detection configs

## Reference Commands

**Test on Hiwonder system:**
```bash
ssh pi@10.10.10.137
# password: Fvdw4fs5

# Check services
systemctl status masterpi.service
systemctl status hw_button_scan.service

# View logs
journalctl -u masterpi.service -f

# Manual test
cd /home/pi/MasterPi
python3 board_demo/hardware_test.py
```

---

**Document generated:** 2026-03-20  
**Source system:** 10.10.10.137 (Hiwonder factory image)  
**Purpose:** Reference for PathfinderV2 development
