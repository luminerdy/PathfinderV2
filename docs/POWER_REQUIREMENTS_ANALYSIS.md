# Power Requirements Analysis: Is 2x 18650 Enough?

## TL;DR

**For educational/workshop use: YES** ✅  
**For competitive robotics/heavy duty: MARGINAL** ⚠️

## Power Budget Breakdown

### Raspberry Pi 5
- **Idle:** 3-5W (0.7-1.0A @ 5V)
- **Typical load:** 10-15W (2-3A @ 5V)
- **Peak:** 25W (5A @ 5V)
- **From 7.4V battery:** 3.4A peak draw

### 4x DC Motors (Mecanum Wheels)
- **Per motor stall:** 2-3A @ 7.4V = 15-22W
- **Per motor running:** 0.5-1A @ 7.4V = 4-7W
- **All 4 at 50% speed:** ~6A @ 7.4V = 44W
- **All 4 at 100% (worst case):** ~12A @ 7.4V = 89W

### 5x PWM Servos (Robotic Arm)
- **Per servo idle:** ~0.1A @ 7.4V = 0.7W
- **Per servo moving (light load):** ~0.5A @ 7.4V = 3.7W
- **Per servo moving (heavy load):** ~1-2A @ 7.4V = 7-15W
- **All 5 moving simultaneously:** 5-10A @ 7.4V = 37-74W

### Peripherals
- **Camera:** ~0.5A @ 5V = 2.5W (via Pi USB)
- **Sonar (I2C):** ~0.1A @ 3.3V = 0.3W
- **RGB LEDs:** ~0.2A @ 5V = 1W
- **Buzzer:** ~0.1A @ 5V = 0.5W
- **Total peripherals:** ~4W

### Power Budget Summary

| Scenario | Pi | Motors | Servos | Other | Total | Current @ 7.4V |
|----------|----|---------|---------|---------|---------|--------------------|
| **Idle** | 5W | 0W | 0.7W | 1W | 6.7W | 0.9A |
| **Light use** | 10W | 22W | 18W | 4W | 54W | 7.3A |
| **Typical** | 15W | 44W | 18W | 4W | 81W | 11A |
| **Heavy** | 20W | 66W | 37W | 4W | 127W | 17A |
| **Peak** | 25W | 89W | 74W | 4W | 192W | 26A |

## 18650 Battery Specifications

### Typical 18650 Cells

**Capacity:**
- Budget cells: 1500-2000mAh
- Standard cells: 2000-2500mAh
- Premium cells: 2500-3500mAh

**Discharge Rating:**
- Budget cells: 5-10A continuous (NOT SUITABLE)
- Standard cells: 10-15A continuous (MARGINAL)
- High-discharge cells: 20-30A continuous (RECOMMENDED)

**Examples of High-Discharge Cells:**
- Samsung 25R: 2500mAh, 20A continuous
- Sony VTC6: 3000mAh, 15A continuous (30A burst)
- LG HG2: 3000mAh, 20A continuous
- Samsung 30Q: 3000mAh, 15A continuous

### 2x 18650 in Series (7.4V Nominal)

**Voltage:**
- Fully charged: 8.4V (2x 4.2V)
- Nominal: 7.4V (2x 3.7V)
- Minimum safe: 6.0V (2x 3.0V)

**Current capability = Weakest cell**
- Both cells in series must handle full current
- Limited by lowest-rated cell

## Runtime Estimates

**Using Samsung 25R (2500mAh, 20A):**

| Usage Scenario | Current Draw | Runtime | Notes |
|----------------|--------------|---------|-------|
| Idle (no motors) | 0.9A | ~2.8 hours | Sensors + Pi only |
| Light use | 7.3A | ~21 minutes | Gentle movements |
| Typical workshop | 11A | ~14 minutes | Normal operation |
| Heavy use | 17A | ~9 minutes | Aggressive driving |
| Peak (all max) | 26A | ~6 minutes | **Exceeds safe limit!** |

**Important:** Runtime reduces as battery voltage drops due to voltage sag under load.

## Is 2x 18650 Enough?

### ✅ YES for:
- **Educational workshops** (15-20 min sessions)
- **Demonstrations** (short bursts)
- **Development/testing** (can recharge between tests)
- **Light autonomous operation** (gentle movements)

### ⚠️ MARGINAL for:
- **Extended operation** (>20 minutes continuous)
- **Aggressive driving** (high speed, quick turns)
- **Heavy loads** (lifting objects with arm)
- **Competitive robotics** (needs more headroom)

### ❌ NOT ENOUGH for:
- **All components at max simultaneously** (26A exceeds 20A rating)
- **Continuous heavy operation** (< 10 min runtime)
- **Hot/cold environments** (reduces battery capacity)

## Voltage Regulator Considerations

**Expansion board voltage regulator:**
- Input: 6.0-8.4V (battery voltage)
- Output: 5.0V (for Pi)
- **Current rating unknown** (likely 3-5A)

**Problem at low battery:**
- 6.5V input → 5.0V output = 1.5V drop
- Low efficiency, high heat
- Struggles under load

**Better with full battery:**
- 8.4V input → 5.0V output = 3.4V drop
- Better efficiency
- More stable under load

**Motor voltage:**
- Motors likely powered directly from battery (7.4V)
- Not regulated
- Performance varies with battery voltage

## Recommendations

### Immediate (Use What You Have)

1. **Use HIGH-DISCHARGE 18650 cells**
   - Samsung 25R, Sony VTC6, LG HG2
   - NOT generic Amazon/eBay cells
   - Cost: $5-8 per cell vs $2-3 generic

2. **Power management in code:**
   ```python
   # Don't do this:
   all_motors(100%)  # Too much current!
   all_servos_move()
   
   # Do this instead:
   motors(50%)       # Moderate speed
   time.sleep(0.1)   # Brief movements
   motors(0%)        # Stop between actions
   ```

3. **Avoid simultaneous peaks:**
   - Move arm THEN drive
   - Or drive slowly while arm moves
   - Never all motors + all servos at max

4. **Keep battery charged:**
   - Start each session > 8.0V
   - Stop at 7.0V minimum
   - 15-20 minute sessions

### Medium Term (Better Performance)

1. **Larger capacity cells:**
   - 3000-3500mAh vs 2500mAh
   - 20-30% more runtime
   - ~$8-10 per cell

2. **Add more cells in parallel:**
   ```
   Current: 2S1P (2 series, 1 parallel)
   Upgrade: 2S2P (2 series, 2 parallel)
   Result: Double capacity AND current rating
   ```
   - 4x 18650 cells total
   - Still 7.4V nominal, 8.4V max
   - But 2x capacity (5000mAh) and 2x current (40A)
   - Cost: 2x batteries ($30-40)

3. **Better voltage regulator:**
   - Higher current rating (5A+)
   - Buck converter with good efficiency
   - Separate Pi power from motor power

### Long Term (Production Design)

1. **Higher voltage system (3S):**
   ```
   3x 18650 in series = 11.1V nominal, 12.6V max
   - More efficient voltage regulation
   - More motor torque/speed
   - Requires different expansion board
   ```

2. **Dual battery system:**
   ```
   Battery 1: 2S 18650 for Pi (via regulator)
   Battery 2: 2S 18650 for motors (direct)
   - Complete isolation
   - No interference
   - Can optimize each separately
   ```

3. **LiPo instead of 18650:**
   ```
   2S 3000mAh LiPo pack
   - Higher discharge rate (30C = 90A capable!)
   - Lighter weight
   - Flatter discharge curve
   - But: More dangerous, needs care
   ```

## Hiwonder's Design Choice

**Why Hiwonder uses 2x 18650:**

**Pros:**
- ✅ Sufficient for 15-20 min sessions
- ✅ Removable/swappable (vs built-in LiPo)
- ✅ Standard cells (easy to replace)
- ✅ Safer than LiPo (for education)
- ✅ Cost-effective
- ✅ Readily available worldwide

**Cons:**
- ⚠️ Limited runtime
- ⚠️ Voltage sag under heavy load
- ⚠️ Must use quality cells
- ⚠️ Need charging between sessions

**For educational workshops: Good trade-off!**

## Testing Your Current Setup

**When you install fresh batteries, test this:**

```python
from hardware import Board
import time

board = Board()

# Measure voltage progression
print("Battery load test:")

# Idle
v1 = board.get_battery() / 1000.0
print(f"1. Idle: {v1:.2f}V")
time.sleep(2)

# Light load (one motor, low speed)
board.set_motor_duty(1, 30)
time.sleep(2)
v2 = board.get_battery() / 1000.0
print(f"2. One motor 30%: {v2:.2f}V (drop: {v1-v2:.2f}V)")
board.set_motor_duty(1, 0)
time.sleep(2)

# Medium load (all motors, moderate speed)
board.set_motor_duty([(1,50), (2,50), (3,50), (4,50)])
time.sleep(2)
v3 = board.get_battery() / 1000.0
print(f"3. All motors 50%: {v3:.2f}V (drop: {v1-v3:.2f}V)")
board.set_motor_duty([(1,0), (2,0), (3,0), (4,0)])
time.sleep(2)

# Recovery
v4 = board.get_battery() / 1000.0
print(f"4. Recovery: {v4:.2f}V (recovered: {v4-v3:.2f}V)")

print("\nAnalysis:")
if v1-v3 < 0.3:
    print("✅ Excellent - minimal voltage sag")
elif v1-v3 < 0.5:
    print("✅ Good - acceptable voltage sag")
elif v1-v3 < 0.8:
    print("⚠️  Moderate - consider higher capacity")
else:
    print("❌ Excessive sag - need better batteries")
```

**Expected results with good cells:**
- Idle → 30% motor: 0.1-0.2V drop
- Idle → 50% all motors: 0.3-0.5V drop
- Recovery: Returns to within 0.1V of idle

**If you see > 0.8V drop:**
- Cells are low quality or degraded
- Upgrade to high-discharge cells

## Final Answer

**Is 2x 18650 enough?**

**For PathfinderBot workshop use: YES** ✅

**Requirements:**
- Use HIGH-DISCHARGE cells (20A+ rating)
- Keep batteries charged (> 8.0V start)
- Smart power management in code
- 15-20 minute session design
- Multiple battery sets for all-day workshops

**Not enough for:**
- All-day continuous operation
- Peak power everything simultaneously
- Competitive robotics (need more headroom)

**Upgrade path if needed:**
- 2S2P (4 cells) = 2x capacity + current
- Higher voltage (3S) = better efficiency
- Dual battery system = isolation

---

**Bottom line:** The Hiwonder design is appropriate for educational use with proper battery management. Fresh, quality cells should eliminate your issues!
