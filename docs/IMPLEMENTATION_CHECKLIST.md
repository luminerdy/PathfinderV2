# PathfinderV2 Implementation Checklist

Based on Hiwonder system analysis. Priority order.

## 🔥 CRITICAL - Must Have (Motor Functionality)

- [ ] **Add to `/boot/firmware/config.txt`:**
  ```ini
  dtparam=i2c_arm=on
  dtparam=uart0=on
  ```
- [ ] **Reboot and verify:**
  ```bash
  ls -la /dev/ttyAMA0  # Should exist
  ls -la /dev/i2c-1    # Should exist
  ```
- [ ] **⚠️ CHECK BATTERY FIRST:**
  ```python
  from lib.ros_robot_controller_sdk import Board
  board = Board()
  volt = board.get_battery()
  if volt: print(f"Battery: {volt/1000.0:.2f}V")
  # MUST be > 7.5V for motor operation!
  ```
- [ ] **Test basic motor (only if battery > 7.5V):**
  ```python
  board.enable_reception()
  board.set_motor_duty([[1, 60]])
  ```
- [ ] **Update documentation** (INSTALL.md, DEPENDENCIES.md, add BATTERY_SAFETY.md)

## ⚡ HIGH PRIORITY - Core Functionality

- [ ] **Servo calibration system**
  - Create `Deviation.yaml` for servo offsets
  - Implement calibration tool
  - Apply offsets in servo commands
  
- [ ] **Battery voltage monitoring**
  - Verify `get_battery()` returns values (not None)
  - Add voltage display/logging
  - Low battery warning

- [ ] **Hardware self-test**
  - Port `hardware_test.py` logic to our framework
  - Test all servos in sequence
  - Test all motors
  - Add to `test_hardware.py`

- [ ] **GPIO button handler** (optional but useful)
  - KEY1 (GPIO 13): Self-test
  - KEY2 (GPIO 23): Shutdown
  - Create systemd service

## 📦 MEDIUM PRIORITY - Enhanced Features

- [ ] **Systemd auto-start service**
  - Create `/etc/systemd/system/pathfinder.service`
  - Enable on boot
  - Test restart on failure

- [ ] **Color detection configuration**
  - Create `color_config.yaml` with HSV ranges
  - Calibration tool for color learning
  - Pre-configured colors: red, blue, green, yellow

- [ ] **Camera streaming**
  - MJPEG server for web viewing
  - WebRTC for lower latency (future)
  - FPS/resolution configuration

- [ ] **Remote control interface**
  - JSON-RPC server (like Hiwonder)
  - REST API (simpler alternative)
  - WebSocket for real-time control

## 🎯 LOW PRIORITY - Nice to Have

- [ ] **Web UI**
  - Control panel
  - Live camera feed
  - Status monitoring
  - Configuration editor

- [ ] **Gamepad support**
  - PS4/Xbox controller
  - Movement mapping
  - Arm control
  - Already have `api/gamepad.py` stub

- [ ] **WiFi management**
  - AP/STA mode switching
  - WiFi config via web
  - Like `hw_wifi.service`

- [ ] **Action groups**
  - Record/playback movement sequences
  - Store in YAML
  - Trigger via RPC

- [ ] **Advanced vision modes**
  - Face detection/recognition
  - AprilTag navigation (have E2 demo)
  - Visual patrol
  - Color tracking/sorting

## 📝 Documentation Updates Needed

- [ ] **INSTALL.md**
  - Add boot config steps
  - GPIO permissions
  - I2C/UART verification

- [ ] **DEPENDENCIES.md**
  - Add gpiod library
  - Add smbus2 for I2C
  - System requirements

- [ ] **TESTING.md**
  - Add battery check
  - Add GPIO button test
  - Add I2C sonar test

- [ ] **README.md**
  - Update "Works on Pi 5" note
  - Add "Tested on Pi 500" note
  - Hardware requirements section

- [ ] **Create CALIBRATION.md**
  - Servo deviation procedure
  - Color threshold tuning
  - Camera calibration

## 🔄 Code Refactoring (Future)

- [ ] **Consistent error handling**
  - Try/except around hardware calls
  - Graceful degradation
  - Error logging

- [ ] **Configuration consolidation**
  - Single `config.yaml` vs multiple files
  - Environment variables
  - Command-line overrides

- [ ] **Logging system**
  - Structured logging
  - Log rotation
  - Debug/Info/Error levels

- [ ] **Unit tests**
  - Hardware mocking
  - Capability tests
  - Integration tests

## Comparison Matrix

| Feature | Hiwonder | PathfinderV2 | Status |
|---------|----------|--------------|--------|
| Motor control | ✅ | ❌ Blocked by UART | Fix pending |
| Servo control | ✅ | ❌ Same issue | Fix pending |
| Sonar (I2C) | ✅ | ❌ Needs I2C enable | Fix pending |
| Camera | ✅ | ✅ Works | Done |
| Battery voltage | ✅ | ❌ Same issue | Fix pending |
| RGB LEDs | ✅ | ✅ Works | Done |
| Buzzer | ✅ | ❓ Not tested | Test pending |
| Servo calibration | ✅ | ❌ | Not implemented |
| Auto-start | ✅ | ❌ | Not implemented |
| GPIO buttons | ✅ | ❌ | Not implemented |
| Remote control | ✅ | ❌ | Not implemented |
| MJPEG streaming | ✅ | ❌ | Not implemented |
| Color detection | ✅ | ✅ Code ready | Config needed |
| AprilTag | ❓ | ✅ Demo exists | Not tested |
| YOLOv11 | ✅ | ✅ Installed | Not tested |
| Documentation | ⚠️ Chinese/English | ✅ English | Better |

## Timeline Estimate

**Phase 1: Get Motors Working (1 hour)**
- Boot config edit
- Reboot
- Testing
- Documentation

**Phase 2: Core Features (4-6 hours)**
- Servo calibration
- Hardware self-test
- Battery monitoring
- GPIO buttons

**Phase 3: Enhanced Features (1-2 days)**
- Systemd service
- Remote control API
- Camera streaming
- Color config

**Phase 4: Polish (1-2 days)**
- Web UI
- Gamepad support
- Advanced vision
- Documentation

## Success Criteria

**Minimum Viable Robot:**
- ✅ Motors move
- ✅ Servos move
- ✅ Battery reads correctly
- ✅ All demos run (D1, D2, D3)
- ✅ Documentation complete

**Production Ready:**
- ✅ All above
- ✅ Auto-starts on boot
- ✅ Self-test button works
- ✅ Remote control API
- ✅ Camera streaming
- ✅ Calibration tools

**Workshop Ready:**
- ✅ All above
- ✅ Student-friendly documentation
- ✅ Troubleshooting guide
- ✅ Example projects
- ✅ Web UI for non-coders

---

**Next Action:** Fix boot config and test on robot!
