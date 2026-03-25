# Power Requirements Summary
## PathfinderV2 with Raspberry Pi 5

**Last Updated:** March 24, 2026  
**Platform:** MasterPi with Raspberry Pi 5 8GB

---

## Battery Voltage Thresholds

### Operational Status by Voltage

| Voltage | Status | Motor Performance | Pi Status | Recommendation |
|---------|--------|------------------|-----------|----------------|
| **>8.3V** | Excellent | Reliable at all powers | Stable | Full operation OK |
| **8.2-8.3V** | Good | Reliable at power 30+ | Stable | Normal operation |
| **8.0-8.2V** | Marginal | Inconsistent power 28 | May throttle under load | Watch carefully |
| **7.5-8.0V** | Low | Power 28 fails, 30 unreliable | Throttles under motor load | Replace soon |
| **<7.5V** | Critical | Motors fail | Heavy throttling | Replace immediately |

### Observed Behavior

**At 8.21V (Fresh batteries):**
- ✅ Power 30 rotation: 103 deg/sec
- ✅ Pi throttling: 0x0 (clean)
- ✅ Motors responsive and reliable

**At 7.96V (Declining):**
- ⚠️ Power 28 rotation: 0-1 deg/sec (fails)
- ⚠️ Pi throttling: 0x50000 (under-voltage occurred)
- ⚠️ Motors unreliable, high power needed

**At 7.73V (Current - Low):**
- ❌ Expected: Power 30 may be insufficient
- ⚠️ Pi may throttle under sustained motor load
- ⚠️ 5-15 minutes runtime remaining

---

## Minimum Motor Power Requirements

### Rotation (In-Place Turn)

| Battery Voltage | Minimum Power | Notes |
|----------------|---------------|-------|
| >8.2V | 28-30 | Power 30 recommended for consistency |
| 8.0-8.2V | 30 | Power 28 unreliable |
| 7.5-8.0V | 35+ | May fail entirely |
| <7.5V | Not reliable | Replace batteries |

**Calibrated Rate (Power 30, >8.2V):**
- ~103 deg/sec
- 90° turn = 0.87 seconds

### Forward Movement

| Battery Voltage | Minimum Power | Speed (est.) |
|----------------|---------------|--------------|
| >8.2V | 30 | ~30-50 cm/sec (needs calibration) |
| 8.0-8.2V | 35+ | Reduced speed |
| 7.5-8.0V | 40+ | Very slow/unreliable |
| <7.5V | Not reliable | Replace batteries |

**Observed (7.96V battery):**
- Power 28: 0-6 cm/sec (barely moves)
- Power 30: 44 cm/sec (works but inconsistent)

### Why Power 30 Minimum?

**Static Friction Threshold:**
- Power 24 and below: Motors spin but don't overcome friction
- Power 25-27: Inconsistent (works sometimes, fails others)
- Power 28: Works at >8.2V, fails below
- **Power 30:** Reliable threshold with safety margin

**Battery Voltage Effect:**
- As battery drains, effective motor power decreases
- Power 28 at 8.2V ≈ Power 25 at 7.8V (equivalent output)
- Using Power 30 provides headroom for battery decline

---

## Raspberry Pi 5 Power Requirements

### Official Specification
- **Input:** 5V via USB-C Power Delivery
- **Current:** 5A (25W maximum)
- **Minimum:** ~4.75V to avoid throttling

### Power Distribution Issue

**Problem:**
When all 4 motors engage at high power (28-30), the Pi can experience under-voltage even when battery reports adequate voltage (>7.5V).

**Evidence:**
```
Battery (board sensor): 7.96V
Pi throttle flags: 0x50000
  - Bit 16: Under-voltage has occurred
  - Bit 18: Throttling has occurred
```

**Hypothesis:**
The voltage regulator (battery → Pi 5V supply) cannot adequately supply both:
1. Motor controller + 4 motors at power 28-30
2. Raspberry Pi 5 at required 5V/5A

**Impact:**
- Pi throttles CPU when under-voltage detected
- May affect computer vision processing speed
- May affect real-time motor control
- Unpredictable behavior as battery drains

---

## Recommended Operating Ranges

### For Reliable Operation
- **Battery voltage:** >8.2V (check before missions)
- **Motor power (rotation):** 30
- **Motor power (forward):** 30+
- **Replace batteries when:** <8.0V

### For Extended Operation
- **Start voltage:** >8.3V (fresh batteries)
- **End voltage:** 8.0V (replace before hitting this)
- **Expected runtime:** 30-45 minutes at >8.2V

### For Testing/Calibration
- **Minimum voltage:** 8.2V
- **Check Pi throttling:** Before and after tests
- **Monitor voltage:** Every 10-15 minutes during extended sessions

---

## Battery Monitoring

### Pre-Flight Check
```python
from lib.movement import check_battery

voltage, ok = check_battery(board, min_voltage=8.2)
if not ok:
    print(f"Battery low: {voltage:.2f}V - Replace before operation")
    exit(1)
```

### During Operation
```python
# Check every 10-15 minutes or between missions
voltage, ok = check_battery(board, min_voltage=8.0)
if not ok:
    print(f"Battery declining: {voltage:.2f}V")
    # Increase motor powers by 10-20%
    # OR end mission and replace batteries
```

### Pi Throttling Check
```bash
vcgencmd get_throttled
# 0x0 = OK
# 0x50000 = Under-voltage occurred (replace batteries)
```

---

## Power Budget Estimation

### Typical Current Draw

**Idle (Pi only):**
- ~2-3A @ 5V

**4 Motors @ Power 30:**
- Estimated: 4-6A total @ 7.5-8.5V
- Peak: Higher during acceleration

**Combined:**
- Motors: 4-6A @ 8V = 32-48W
- Pi: 2-3A @ 5V = 10-15W (from regulator)
- **Total system:** ~50-65W peak

### Battery Capacity

**Typical 2S LiPo (7.4V nominal, 8.4V max):**
- Capacity: 2000-3000mAh typical
- Energy: 15-25 Wh

**Runtime estimate:**
- At 50W average: 15Wh / 50W = ~18 minutes
- At 30W average (mixed idle/movement): ~30-50 minutes

**Observed:**
- Fresh batteries (8.21V) → Low batteries (7.73V) in ~2 hours of testing
- Heavy motor use accelerates drain significantly

---

## Recommendations for Hiwonder

1. **Document minimum battery voltage:** >8.2V (not 7.5V)
2. **Pi 5 power requirements:** Verify regulator can supply 5V/5A + motors
3. **Voltage monitoring:** Add low-battery warning at 8.0V
4. **Power recommendations:** Suggest higher capacity batteries for Pi 5 platforms
5. **Calibration:** Provide motor power calibration for different battery levels

---

## Current Status (March 24, 2026 - 3:38 PM)

- **Battery:** 7.73V (LOW)
- **Pi throttling:** 0x0 (clean, no recent motor load)
- **Recommendation:** Replace batteries before next operation
- **Runtime remaining:** 5-15 minutes (unreliable)

---

## Key Takeaways

1. **Battery voltage >8.2V is critical** for reliable operation
2. **Power 30 minimum** for rotation and forward movement
3. **Pi 5 requires more power** than Pi 4 (5V/5A vs 5V/3A)
4. **Monitor battery voltage** regularly during operation
5. **Replace batteries proactively** at 8.0V, don't wait for failure
