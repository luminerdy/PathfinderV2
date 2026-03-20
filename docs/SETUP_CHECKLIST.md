# PathfinderV2 Setup Checklist

Quick reference checklist for setting up a new robot.

## Pre-Setup

- [ ] Raspberry Pi 5 (4GB or 8GB)
- [ ] MicroSD card (32GB+) with fresh Pi OS
- [ ] MasterPi expansion board
- [ ] 2x 18650 batteries (charged > 7.5V)
- [ ] Battery charger
- [ ] USB camera (optional)
- [ ] I2C sonar sensor (optional)
- [ ] Internet connection

## OS Installation

- [ ] Flash Raspberry Pi OS (64-bit, Bookworm or newer)
- [ ] Enable SSH in imager settings
- [ ] Set hostname (e.g., `masterpi`)
- [ ] Configure WiFi (if needed)
- [ ] Insert SD card and boot Pi

## System Setup

```bash
# Update system
- [ ] sudo apt update
- [ ] sudo apt upgrade -y

# Install packages
- [ ] sudo apt install -y python3-pip python3-venv git i2c-tools v4l-utils libopencv-dev

# Add user to groups
- [ ] sudo usermod -a -G dialout,i2c,gpio,spi $USER
- [ ] Log out and back in
```

## Boot Configuration

```bash
# Edit config
- [ ] sudo nano /boot/firmware/config.txt

# Add these lines at end:
- [ ] dtparam=i2c_arm=on
- [ ] dtparam=uart0=on
- [ ] usb_max_current_enable=1

# Save and reboot
- [ ] sudo reboot
```

## Verify Hardware

```bash
# After reboot, check devices exist:
- [ ] ls -la /dev/ttyAMA0  # Should show device
- [ ] ls -la /dev/i2c-1    # Should show device
```

## Install PathfinderV2

```bash
# Clone repo
- [ ] cd ~ && mkdir -p code && cd code
- [ ] git clone https://github.com/luminerdy/PathfinderV2.git pathfinder
- [ ] cd pathfinder

# Install dependencies
- [ ] pip3 install -r requirements.txt --break-system-packages

# Wait ~5-10 minutes for installation
```

## Hardware Testing

```bash
# Check battery
- [ ] python3 check_battery.py
- [ ] Battery reads > 7.5V

# Test motor
- [ ] python3 -c "from hardware import Board; import time; b = Board(); b.set_motor_duty(1, 50); time.sleep(2); b.set_motor_duty(1, 0)"
- [ ] Motor 1 moved

# Test servo
- [ ] python3 -c "from hardware import Board; import time; b = Board(); b.set_servo_position(5, 500, 0.5); time.sleep(1); b.set_servo_position(5, 1500, 0.5)"
- [ ] Servo 5 moved

# Test buzzer
- [ ] python3 -c "from hardware import Board; b = Board(); b.set_buzzer(2000, 0.2, 0.2, 3)"
- [ ] Buzzer beeped

# Test RGB LEDs
- [ ] python3 -c "from hardware import Board; import time; b = Board(); b.set_rgb([(1,255,0,0), (2,255,0,0)]); time.sleep(1); b.set_rgb([(1,0,0,0), (2,0,0,0)])"
- [ ] LEDs lit red then off
```

## Demo Tests

```bash
- [ ] python3 pathfinder.py --demo d1_basic_drive
- [ ] Motors moved in patterns
- [ ] python3 pathfinder.py --demo d3_arm_basics  
- [ ] Servos moved through positions
```

## Optional: Camera + Sonar

```bash
# If camera connected:
- [ ] v4l2-ctl --list-devices
- [ ] Camera shows in list

# If sonar connected:
- [ ] i2cdetect -y 1
- [ ] Device at 0x77 shows
- [ ] python3 pathfinder.py --demo d2_sonar
- [ ] Distance readings appear
```

## Configuration (Optional)

```bash
# Servo calibration (if needed)
- [ ] Create Deviation.yaml
- [ ] Test and adjust servo offsets

# Custom config
- [ ] Edit config.yaml for your setup
```

## Success Criteria

**Minimum working robot:**
- ✅ Battery voltage reads correctly (> 7.5V)
- ✅ At least one motor moves
- ✅ At least one servo moves
- ✅ No Python errors during tests
- ✅ One demo runs successfully

**Fully operational robot:**
- ✅ All 4 motors working
- ✅ All 5 servos working
- ✅ Battery monitoring functional
- ✅ Buzzer and LEDs working
- ✅ All demos run without errors
- ✅ Camera working (if connected)
- ✅ Sonar working (if connected)

## Troubleshooting Quick Fixes

**Battery reads None:**
```bash
ls /dev/ttyAMA0 || echo "Add dtparam=uart0=on to config.txt"
```

**Motors don't move:**
```bash
python3 check_battery.py  # Must be > 7.5V
```

**Under-voltage warnings:**
```bash
# Charge battery and/or add to config.txt:
# usb_max_current_enable=1
```

**Import errors:**
```bash
cd ~/code/pathfinder
pip3 install -r requirements.txt --break-system-packages
```

## Documentation References

Quick links to docs:

- **Fresh install:** [FRESH_INSTALL.md](FRESH_INSTALL.md) - Complete step-by-step
- **Motor issues:** [MOTOR_SOLUTION.md](MOTOR_SOLUTION.md) - UART configuration fix
- **Battery:** [BATTERY_SAFETY.md](../BATTERY_SAFETY.md) - Voltage requirements
- **Power:** [POWER_REQUIREMENTS_ANALYSIS.md](POWER_REQUIREMENTS_ANALYSIS.md) - Is 2x 18650 enough?
- **Testing:** [TESTING.md](../TESTING.md) - Hardware test procedures
- **Results:** [TESTING_RESULTS.md](TESTING_RESULTS.md) - Verified working config

## Workshop Setup (Multiple Robots)

**For workshops with 10+ robots:**

1. Create master SD card image (follow checklist above)
2. Clone image to all SD cards using Raspberry Pi Imager
3. Change hostname on each robot: `sudo hostnamectl set-hostname robot-01`
4. Label physical robots with numbers
5. Test one robot from each batch
6. Keep spare charged batteries (3-4 sets per robot)
7. Print troubleshooting guide for students

## Time Estimates

- **Initial OS flash:** 10 minutes
- **System updates:** 10-15 minutes
- **Python packages:** 5-10 minutes
- **Testing:** 5-10 minutes
- **Total fresh setup:** 30-45 minutes
- **Clone from image:** 10 minutes + testing

---

**Version:** 1.0  
**Last Updated:** March 20, 2026  
**Status:** ✅ Verified on Pi 5 + Debian 13
