# Testing Log - Library and Bug Tracking

Live testing results on actual hardware (Pi 5, MasterPi robot).

## Date: 2026-03-19

### Hardware Configuration
- **Device:** `/dev/ttyAMA10` (not `/dev/ttyAMA0`)
- **Baud Rate:** `1000000` (not `115200`)
- **Platform:** Raspberry Pi 5 8GB

### Python Libraries Found Missing

#### 1. opencv-python (cv2)
**Error:** `ModuleNotFoundError: No module named 'cv2'`  
**Location:** `sdk/kinematics/transform.py`  
**Solution:** 
```bash
pip3 install opencv-python --break-system-packages
```
**Status:** ✅ Installed and working

#### 2. matplotlib
**Error:** `ModuleNotFoundError: No module named 'matplotlib'`  
**Location:** `sdk/kinematics/arm_move_ik.py`  
**Solution:** Commented out - not actually needed for robot operation  
**Status:** ✅ Fixed by commenting imports

#### 3. mpl_toolkits (matplotlib 3D)
**Error:** Would have occurred after matplotlib  
**Location:** `sdk/kinematics/arm_move_ik.py`  
**Solution:** Commented out - not needed  
**Status:** ✅ Fixed by commenting imports

### Code Bugs Found

#### 1. Missing Path import
**Error:** `NameError: name 'Path' is not defined`  
**Location:** `hardware/board.py`  
**Issue:** `from pathlib import Path` came after using `Path()`  
**Status:** ✅ Fixed - moved import to top

#### 2. SDK creating Board at module import
**Error:** Serial port error during import  
**Location:** `sdk/common/mecanum.py`  
**Issue:** `board = Board()` executed at module load time  
**Solution:** Changed to `board = None`  
**Status:** ✅ Fixed

#### 3. Missing Tuple import
**Error:** `NameError: name 'Tuple' is not defined`  
**Location:** `hardware/sonar.py`  
**Issue:** Used `Tuple` in type hints without importing  
**Status:** ✅ Fixed - added to imports

#### 4. Unicode characters in output
**Error:** `UnicodeEncodeError: 'latin-1' codec can't encode character '\u2713'`  
**Location:** `start_robot.py` and other scripts  
**Issue:** Checkmark characters (✓✗) don't work in some terminals  
**Status:** ⏳ To be fixed

#### 5. RGB LED method name
**Error:** `AttributeError: 'Board' object has no attribute 'set_colorful_leds'`  
**Location:** `hardware/board.py` line 122  
**Issue:** Method name doesn't match actual SDK (should be `set_rgb`)  
**Solution:** Changed to `board.set_rgb([(1, r, g, b), (2, r, g, b)])`  
**Status:** ✅ Fixed and tested working

### Hardware Tests Completed

✅ **Working:**
- Board serial connection
- Battery voltage reading (7.52V measured)
- Buzzer (beep confirmed)
- RGB LEDs (red, green, blue all working)
- Servo control (tested servo 5/gripper - smooth movement)
- Motor control (tested motor 1 - forward/backward working)
- Camera (640x480 capture working, first frame often fails - normal)
- Sonar (distance readings 369-372cm, RGB indicators working)

✅ **Demos Tested:**
- D1 Basic Drive ✅ (forward, backward, strafe, rotate, square pattern)
- D2 Sonar ✅ (distance readings, obstacle detection - minor format fix needed)
- D3 Arm Basics ✅ (all positions, IK, gripper, pick/place, gestures)

⏳ **Not Yet Tested:**
- E2 AprilTag demo (needs camera + AprilTag library)
- Full integrated test_hardware.py suite
- Vision system (YOLO object detection)
- Web UI
- Gamepad control

### Libraries Verified

From `requirements.txt`:
- [x] numpy ✅ (working - used by IK)
- [x] pyyaml ✅ (working - config loading)
- [x] opencv-python ✅ (working - camera + IK)
- [ ] opencv-contrib-python (not tested yet)
- [x] ultralytics ✅ (YOLOv11 installed, made optional)
- [ ] dt-apriltags or pupil-apriltags (not tested yet)
- [ ] flask, flask-cors (not tested yet - web UI)
- [ ] pygame (not tested yet - gamepad)
- [ ] inputs (not tested yet - gamepad)
- [x] pyserial ✅ (working - board communication)
- [ ] pillow (not tested yet)

### Next Testing Steps

1. Fix RGB LED method name
2. Remove Unicode characters from output
3. Test individual servos
4. Test individual motors
5. Run full `test_hardware.py` suite
6. Test camera capture
7. Test sonar distance reading
8. Update requirements.txt with actual needed versions

---

**Note:** This log tracks issues found during live hardware testing, not just documentation review.
