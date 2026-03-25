# Movement Calibration Results
## Fresh Battery (8.21V) - March 24, 2026

**Session:** 1:00 PM - 1:30 PM CDT  
**Battery:** 8.21V (fresh)  
**Pi Status:** No throttling (0x0)

---

## Rotation Calibration

### Power Requirements
- **Minimum reliable power:** 30
- **Power 28:** Inconsistent at battery <8.2V
- **Power 30:** Reliable rotation at 8.2V+

### Rotation Rate (Power 30)
- **Measured:** ~103 deg/sec
- **Method:** Multiple 90° turns with sonar verification

### Standard 90° Turn
- **Power:** 30
- **Duration:** 0.87 seconds
- **Verification:** Sonar distance changes confirm rotation

**Example test results:**
```
Test 1 (0.7s): 129.7cm -> 40.0cm (89.7cm change)
Test 2 (0.8s): 40.0cm -> 19.2cm (20.8cm change)
Test 3 (0.9s): 19.2cm -> 51.2cm (32.0cm change)
Test 4 (1.0s): 51.2cm -> 142.5cm (91.3cm change)
```

Pattern shows rotation through 4 walls of rectangular field.

---

## Key Insights

### Sonar as Ground Truth
- **Vision can fail** (same tag, same angle after rotation)
- **Sonar always changes** when rotating in field
- **Variation >10cm** = definite rotation
- **Variation >50cm** = significant rotation (likely 90°+)

### Battery Voltage Critical
- **>8.2V:** Motors work reliably, Pi stable
- **8.0-8.2V:** Marginal performance, Pi may throttle under load
- **<8.0V:** Motors unreliable, Pi throttles

### Power Recommendations
- **Rotation:** Power 30 minimum (not 28)
- **Forward drive:** Power 30+ (TBD - needs testing)
- **Search/centering:** Power 30 (not 22-25)

---

## Usage

### Standard 90° Turn Function
```python
def rotate_90_degrees(board, direction='right'):
    """
    Rotate 90° in place
    
    Args:
        board: BoardController instance
        direction: 'right' (clockwise) or 'left' (counter-clockwise)
    """
    if direction == 'right':
        board.set_motor_duty([(1, 30), (2, -30), (3, 30), (4, -30)])
    else:
        board.set_motor_duty([(1, -30), (2, 30), (3, -30), (4, 30)])
    
    time.sleep(0.87)
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
```

### Any Angle Turn
```python
def rotate_degrees(board, degrees, direction='right'):
    """
    Rotate specified degrees
    
    Args:
        board: BoardController instance
        degrees: Angle to rotate (positive value)
        direction: 'right' or 'left'
    """
    duration = degrees / 103.0  # 103 deg/sec at power 30
    
    if direction == 'right':
        board.set_motor_duty([(1, 30), (2, -30), (3, 30), (4, -30)])
    else:
        board.set_motor_duty([(1, -30), (2, 30), (3, -30), (4, 30)])
    
    time.sleep(duration)
    board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
```

---

## Next Steps

1. **Forward movement calibration** at power 30
2. **Update all navigation scripts** to use power 30
3. **Create movement utility module** with calibrated functions
4. **Test 8-tag tour** with new power/timing
5. **Document battery monitoring** requirements

---

## Comparison to Previous Calibration

**Day 7 Morning (7.96V battery):**
- Power 28: 0-1 deg/sec (failed)
- Power 30: Unknown (lost tracking)
- Pi throttling: 0x50000

**Day 7 Afternoon (8.21V battery):**
- Power 28: Unreliable
- Power 30: 103 deg/sec (works!)
- Pi throttling: 0x0

**Conclusion:** Battery voltage >8.2V is critical for reliable operation.
