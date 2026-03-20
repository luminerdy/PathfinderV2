# Under-Voltage Warning Analysis

## Problem
Pi 5 shows under-voltage warning (⚡ lightning bolt icon) on boot, even though battery voltage appears OK.

## What It Means

**Under-voltage warning indicates:**
- Pi is not receiving stable 5V supply
- Voltage dropping below ~4.63V threshold
- Can cause throttling, instability, corruption

**This is SEPARATE from battery voltage!**
- Battery: 7-8V (measured at battery terminals)
- Regulated 5V: What the Pi actually sees
- Problem is in the voltage regulation, not the battery

## Root Cause Analysis

### Power Flow Path
```
18650 Batteries (7.4V nominal, 8.4V max)
    ↓
Control Board Voltage Regulator
    ↓
Raspberry Pi 5 (needs 5V @ 5A)
```

### Possible Issues

**1. Low Battery Voltage (Confirmed Issue)**
- Your robot: 6.87V battery
- Working robot: Fully charged (likely ~8.2V)
- Lower input voltage → harder to regulate 5V
- **Solution:** Charge battery to > 7.5V (ideally 8.0V+)

**2. Voltage Regulator Undersized**
- Pi 5 can draw up to 5A
- Expansion board regulator may be rated for less
- Especially under combined load (Pi + motors + servos)

**3. Shared Power Rail**
- Motors and Pi powered from same regulator
- Motor current spikes cause voltage sag on Pi rail
- Need separate regulators or bigger shared one

**4. Wiring/Connector Voltage Drop**
- Thin wires between battery and board
- Poor connections
- Each connection adds resistance

### Comparison with Working System

**Hiwonder robot (10.10.10.137):**
```bash
vcgencmd get_throttled
# Output: throttled=0x0  (No under-voltage!)
```

**Config differences:**
- Has `usb_max_current_enable=1` in config.txt
- Likely has fully charged battery
- Otherwise identical hardware

## Diagnostic Commands

### Check Current Throttling State
```bash
vcgencmd get_throttled
```

**Interpretation:**
```
0x0      = All good, no issues
0x50000  = Under-voltage occurred in past
0x50005  = Currently under-voltage + occurred in past
```

**Decode bits:**
- Bit 0: Under-voltage currently
- Bit 1: Frequency capped currently
- Bit 2: Throttled currently
- Bit 16: Under-voltage has occurred since boot
- Bit 17: Frequency cap has occurred
- Bit 18: Throttling has occurred

### Check Voltages
```bash
vcgencmd measure_volts core    # Core voltage
vcgencmd measure_volts sdram_c # SDRAM voltage
```

### Monitor in Real-Time
```bash
watch -n 1 'vcgencmd get_throttled && vcgencmd measure_volts'
```

### Check During Motor Operation
```bash
# Terminal 1: Monitor
watch -n 0.5 vcgencmd get_throttled

# Terminal 2: Run motors
python3 -c "
from hardware import Board
import time
board = Board()
print('Running motor...')
board.set_motor_duty(1, 70)
time.sleep(5)
board.set_motor_duty(1, 0)
"
```

## Solutions

### Immediate (Do This First)
1. **Charge battery fully** (to 8.0-8.4V)
2. **Add to `/boot/firmware/config.txt`:**
   ```ini
   usb_max_current_enable=1
   ```
3. **Test if warning persists**

### Short Term (If Warning Continues)
1. **Higher quality batteries**
   - Use high-discharge 18650s (20A+ rating)
   - Samsung 25R, Sony VTC6, etc.
   - Not generic/cheap cells

2. **Thicker power wiring**
   - Reduce voltage drop
   - Especially battery → board connection

3. **Add capacitors**
   - Large capacitor (1000-2200µF) near Pi input
   - Helps with voltage spikes/sags

### Medium Term (Hardware Modifications)
1. **Separate Pi power supply**
   - Dedicated buck converter for Pi (5V 5A minimum)
   - Motors powered separately
   - Prevents interference

2. **Upgrade expansion board**
   - Higher current voltage regulator
   - Or custom power distribution board

3. **Power sequencing**
   - Power Pi first, then motors
   - Prevents inrush current affecting Pi

### Long Term (Clean Design)
1. **Dual battery system**
   - One battery for Pi (7.4V → 5V)
   - One battery for motors (7.4V direct)
   - Complete isolation

2. **Supercapacitor bank**
   - Buffers high-current motor spikes
   - Keeps Pi voltage stable

## Battery Impact on Voltage Regulation

**Why low battery makes it worse:**

Linear voltage drop from battery to Pi:
```
8.4V battery → ~5.0V at Pi (0.4V headroom)  ✅ Good
7.4V battery → ~5.0V at Pi (2.4V headroom)  ✅ OK
6.8V battery → ~4.8V at Pi (1.8V headroom)  ⚠️ Marginal
6.5V battery → ~4.5V at Pi (1.5V headroom)  ❌ Under-voltage

Add motor load:
6.8V battery drops to 6.5V → Pi sees 4.5V → ❌ Warning!
```

**Voltage regulator efficiency:**
- Better efficiency at higher input voltage
- Struggles more as input approaches output
- 6.87V trying to make 5V = tough for regulator

## Testing Protocol

**When you install fresh batteries:**

1. **Before connecting Pi:**
   ```bash
   # Measure battery voltage
   python3 check_battery.py
   # Should be > 8.0V for new batteries
   ```

2. **After Pi boots:**
   ```bash
   # Check for throttling
   vcgencmd get_throttled
   # Should be 0x0
   ```

3. **During motor operation:**
   ```bash
   # Monitor in one terminal
   watch -n 0.5 vcgencmd get_throttled
   
   # Run motors in another
   # Watch if throttling appears
   ```

4. **Document results:**
   - Battery voltage: _____V
   - Throttling at idle: _____
   - Throttling with motors: _____
   - Under-voltage warnings: Yes/No

## Expected Results

**With fresh batteries (8.0-8.4V):**
- ✅ No under-voltage warnings
- ✅ `vcgencmd get_throttled` shows `0x0`
- ✅ Stable operation even with motors

**If warnings persist even with full battery:**
- ⚠️ Voltage regulator issue on expansion board
- Consider hardware modification (separate Pi power)
- Or reduce load (fewer motors simultaneously)

## Comparison Table

| Battery Voltage | Expected Pi Voltage | Status |
|----------------|---------------------|--------|
| 8.4V (full) | 5.0V | ✅ Excellent |
| 8.0V | 4.95-5.0V | ✅ Good |
| 7.5V | 4.9-5.0V | ✅ OK |
| 7.0V | 4.8-4.9V | ⚠️ Marginal |
| 6.8V (your test) | 4.7-4.8V | ⚠️ Warning likely |
| 6.5V | 4.5-4.7V | ❌ Under-voltage |

**With motor load:** Subtract 0.2-0.5V from above values.

## Hiwonder System Comparison

**Their system (no warnings):**
- `usb_max_current_enable=1` ✅
- Fully charged battery ✅
- Quality 18650 cells ✅
- `vcgencmd get_throttled` = `0x0` ✅

**Your system (warnings):**
- `usb_max_current_enable` missing ❌
- Battery at 6.87V ❌
- Same hardware otherwise ✅

**Conclusion:** Low battery is likely the main cause!

## Action Items

- [ ] Install fresh batteries (charge to 8.0-8.4V)
- [ ] Add `usb_max_current_enable=1` to config.txt
- [ ] Test with `vcgencmd get_throttled`
- [ ] Document before/after results
- [ ] If warnings persist, investigate regulator upgrade

## References

- **vcgencmd documentation:** [Raspberry Pi Docs](https://www.raspberrypi.com/documentation/computers/os.html#vcgencmd)
- **Under-voltage detection:** Pi 5 triggers at < 4.63V
- **Pi 5 power requirements:** 5V @ 5A (25W max)
- **Hiwonder config:** `usb_max_current_enable=1` present

---

**Most likely fix:** Fresh batteries + usb_max_current_enable=1  
**If that fails:** Separate Pi power supply needed  
**Test priority:** High (affects stability)
