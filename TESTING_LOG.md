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
**Issue:** Method name doesn't match actual SDK  
**Status:** ⏳ To investigate actual method name

### Hardware Tests Completed

✅ **Working:**
- Board serial connection
- Battery voltage reading (7.52V measured)
- Buzzer (beep confirmed)

⏳ **Not Yet Tested:**
- RGB LEDs (method name issue)
- Servos (1-5)
- Motors (1-4)
- Camera
- Sonar
- Arm inverse kinematics
- Chassis movement

### Libraries Still to Verify

From `requirements.txt`, not yet tested:
- [ ] numpy
- [ ] pyyaml  
- [ ] opencv-contrib-python
- [ ] ultralytics (YOLOv11)
- [ ] dt-apriltags or pupil-apriltags
- [ ] flask, flask-cors
- [ ] pygame
- [ ] inputs
- [ ] pyserial ✅ (working)
- [ ] pillow

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
