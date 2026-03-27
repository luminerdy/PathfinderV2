# PathfinderV2 TODO List

**Prioritized tasks and enhancements**

---

## High Priority (Before Competition)

### Motor Calibration (IMPORTANT!)
- [ ] **Run motor speed calibration**
  ```bash
  python3 tools/calibrate_motors.py --full
  ```
- [ ] **Update min/max speeds in code**
  - `capabilities/pickup.py` - Update min_speed values
  - `capabilities/navigation.py` - Update min_speed values
- [ ] **Test on actual surface** (carpet vs floor affects speeds)
- [ ] **Document final values** in config or README

**Why:** Speeds 1-20 typically don't move robot (dead zone)  
**Impact:** Without calibration, fine positioning and slow approaches won't work

---

### Field Setup Testing

- [ ] **Print AprilTags** (IDs 0-3, 6"x6")
- [ ] **Build corner panels** (4x 2'x18" Coroplast)
- [ ] **Mount tags at 10" height**
- [ ] **Run field navigation tests**
  ```bash
  python3 -m tests.run_field_test
  ```
- [ ] **Verify all 4 tags detected** from center

**Timeline:** This weekend (per weekend testing checklist)

---

### Block Pickup Testing

- [ ] **Acquire 1" colored blocks** (red, blue, green)
- [ ] **Print/position AprilTag** near pickup zone
- [ ] **Test color detection** with actual blocks
- [ ] **Test pickup sequence**
  ```bash
  python3 demos/vision_pickup.py --color red
  ```
- [ ] **Find gripper maximum angle** (test at 0°, 15°, 30°, 45°)
- [ ] **Tune grasp height** if needed

**Dependencies:** Motor calibration (need min speeds working)

---

## Medium Priority (Nice to Have)

### Hardware Improvements

- [ ] **Connect sonar sensor** (currently code ready, hardware not connected)
- [ ] **Test sonar obstacle detection**
- [ ] **Battery voltage monitoring** during long runs
- [ ] **Gripper improvements** (rubber pads for better grip?)

### Software Enhancements

- [ ] **Servo calibration system**
  - Implement Deviation.yaml support
  - Auto-calibrate arm servos
- [ ] **Systemd auto-start service** (optional)
  ```bash
  systemctl enable pathfinder.service
  ```
- [ ] **Camera calibration** for better distance estimation
  - Checkerboard pattern
  - Calculate actual focal length
  - Improve 3D position accuracy

### Testing & Validation

- [ ] **Competition scenario end-to-end test**
  - Navigate to pickup zone (tag 10)
  - Pick up colored block
  - Navigate to delivery zone (tag 5)
  - Place block
  - Return to home
- [ ] **Multi-block pickup test** (3-5 blocks in sequence)
- [ ] **Long-duration test** (battery life, stability)

---

## Low Priority (Future Enhancements)

### Advanced Vision

- [ ] **YOLO object classification** (block vs non-block)
- [ ] **Custom YOLO training** for specific blocks
- [ ] **Depth camera support** (if upgrading hardware)
- [ ] **Visual odometry** for position tracking

### Advanced Navigation

- [ ] **Multi-tag triangulation** for precise localization
- [ ] **Path planning** with obstacles
- [ ] **A* or similar algorithm** for optimal routes
- [ ] **Kalman filter** for position smoothing

### Advanced Manipulation

- [ ] **Wrist servo control** (rotate gripper independently)
- [ ] **Grip force feedback** (detect if block held)
- [ ] **Stack blocks** (place on top of each other)
- [ ] **Push vs pickup** strategies

### Multi-Robot

- [ ] **Robot-to-robot communication** (share detected blocks)
- [ ] **Collision avoidance** between robots
- [ ] **Cooperative manipulation** (two robots, one block)
- [ ] **Task allocation** (which robot picks up which block)

### User Interface

- [ ] **Web dashboard** for monitoring
- [ ] **Live camera stream** to web
- [ ] **Remote control** via web interface
- [ ] **Telemetry display** (battery, position, state)

---

## Bugs & Issues

### Known Issues

- [ ] **Camera warnings on startup** (can be suppressed)
  ```
  VIDIOC_QUERY_CAP: Inappropriate ioctl for device
  ```
  - Low priority, doesn't affect functionality
  - Suppress in camera.py if annoying

### To Investigate

- [ ] **Battery reading reliability** (occasional None returns)
  - May need retry logic
  - Check board protocol timing
- [ ] **Mecanum drift during rotation** (slight lateral movement)
  - Normal for mecanum, but can be minimized
  - May need motor speed calibration per wheel
- [ ] **AprilTag detection distance limits** (how far is reliable?)
  - Document maximum working distance
  - Test with different tag sizes

---

## Documentation Needed

- [ ] **Quick start video** (30-second demo)
- [ ] **Competition setup guide** (field + robots + rules)
- [ ] **Student worksheets** (for educational use)
- [ ] **Troubleshooting FAQ** (common issues + fixes)
- [ ] **API reference** (auto-generated from docstrings?)

---

## Testing Checklist (Before Workshop)

### Phase 0: Hardware Validation
- [ ] Motor calibration complete
- [ ] All motors working
- [ ] All servos working  
- [ ] Camera functional
- [ ] Battery monitoring working
- [ ] Sonar connected (optional)

### Phase 1: Navigation
- [ ] Field with 4 AprilTags set up
- [ ] Tag detection working (all 4 visible)
- [ ] Navigate to each tag successfully
- [ ] Waypoint tour complete (0→1→2→3)
- [ ] Return to home working

### Phase 2: Pickup
- [ ] Color detection working (red, blue, green)
- [ ] AprilTag-assisted positioning accurate
- [ ] Angle alignment working
- [ ] Mecanum fine positioning working
- [ ] IK-based pickup reliable (>80% success)

### Phase 3: Integration
- [ ] Navigate + pickup in sequence
- [ ] Navigate + pickup + deliver
- [ ] Multiple blocks handled
- [ ] Error recovery working
- [ ] Battery lasts full round (5 minutes)

### Phase 4: Competition Ready
- [ ] 2-4 robots built and tested
- [ ] Field fully marked and tagged
- [ ] Scoring system ready
- [ ] Operator controls working (gamepad/web)
- [ ] Documentation complete
- [ ] Practice rounds successful

---

## Decision Points

### Still To Decide

- [ ] **Competition format** - Which scenario(s) to use?
  - Warehouse Sorting (simplest)
  - AprilTag Treasure Hunt
  - Line Following Relay
  - Multi-Robot Collaboration
- [ ] **Number of robots** - 2, 3, 4, or more?
- [ ] **Field size** - 6'x6', 8'x8', or 12'x12'?
- [ ] **Workshop timeline** - 5-6 weeks realistic?
- [ ] **Team size** - 2-3 students per robot or larger teams?

---

## Completed ✅

### Hardware
- ✅ All motors working (UART fix applied)
- ✅ All servos working
- ✅ Battery reading accurate (8.0V+)
- ✅ RGB LEDs functional
- ✅ Buzzer working
- ✅ Power saving (LEDs off on startup)

### Software Framework
- ✅ Modular architecture (hardware + capabilities + demos)
- ✅ Clean-room implementations (no vendor code)
- ✅ Git repository with full history
- ✅ Comprehensive documentation (18+ files)

### Navigation
- ✅ AprilTag detection
- ✅ Visual servoing navigation
- ✅ Multi-waypoint tours
- ✅ Field configuration system
- ✅ Autonomous test framework

### Pickup
- ✅ Color-based block detection (HSV)
- ✅ AprilTag-assisted 3D positioning
- ✅ Inverse kinematics (no hardcoded positions!)
- ✅ Block orientation detection
- ✅ Automatic angle alignment
- ✅ Mecanum fine positioning

### Testing
- ✅ Autonomous test runner
- ✅ Image capture for debugging
- ✅ Result reporting (markdown + JSON)
- ✅ Demo scripts for all features

### Documentation
- ✅ Setup guides (fresh install, quick start)
- ✅ Testing guides (weekend checklist, field tests)
- ✅ Feature guides (vision pickup, navigation, orientation)
- ✅ Competition planning (scenarios, roadmap)
- ✅ Motor calibration guide

---

## Quick Commands Reference

**Calibration:**
```bash
python3 tools/calibrate_motors.py --full
python3 check_battery.py
```

**Testing:**
```bash
python3 -m tests.run_field_test
python3 demos/vision_pickup.py --color red
```

**Demos:**
```bash
python3 pathfinder.py --demo d1  # Basic drive
python3 pathfinder.py --demo d2  # Sonar
python3 pathfinder.py --demo d3  # Arm basics
```

**Status:**
```bash
git status
git log --oneline -10
ls -lh test_results/
ls -lh pickup_images/
```

---

**Priority order: Calibration → Field Tests → Pickup Tests → Competition Integration**

Start with motor calibration - it affects everything else!
