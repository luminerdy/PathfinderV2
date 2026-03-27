# Robot Shutdown During Motor Operation - Analysis

## Problem Report
Robot shuts down unexpectedly when running motors.

## Possible Causes

### 1. Low Battery / Voltage Sag (Most Likely)
**Symptoms:**
- Shutdown during motor operation
- Motors draw high current → voltage drops
- If voltage < 6V, Pi may brown out

**Check:**
- Battery voltage before testing
- Hiwonder docs say: "When voltage < 7V, battery is low"
- LED on expansion board dims when low power

**Solution:**
- Charge battery fully before testing
- Monitor voltage during operation
- Add voltage check before motor commands

### 2. KEY2 Button (GPIO 23) Accidental Press
**How it works:**
```python
# From hw_button_scan.py
if key2.get_value() == 0:  # Button pressed
    time.sleep(0.05)
    if key2.get_value() == 0:
        count += 1
        if count == 60 and not key2_pressed:  # 3 seconds
            count = 0
            key2_pressed = True
            print('sudo halt')
            os.system('sudo halt')  # ← SHUTDOWN!
```

**Trigger:** Hold KEY2 for 3 seconds → `sudo halt`

**Could happen if:**
- Button stuck
- Vibration from motors triggers it
- Wiring short to ground

### 3. Brownout Protection
**Pi 5 behavior:**
- Under-voltage detection
- Automatic shutdown to prevent corruption
- Voltage regulator on expansion board might not provide enough current

### 4. Current Overload
**If multiple motors run simultaneously:**
- Combined current exceeds board capacity
- Protection circuit trips
- Board shuts down power

## Diagnostics

### Check Battery Voltage
```python
from common.ros_robot_controller_sdk import Board
board = Board()
board.enable_reception()

volt = board.get_battery()
if volt:
    print(f"Battery: {volt}mV = {volt/1000.0:.2f}V")
    if volt < 7000:
        print("⚠️ LOW BATTERY - CHARGE NOW!")
    elif volt < 7500:
        print("⚠️ Battery getting low")
    else:
        print("✓ Battery OK")
```

**Note:** Can't run this while MasterPi.py service is running (serial port conflict).

### Check Button State
```python
import gpiod
import time

chip = gpiod.Chip('gpiochip4')
key2 = chip.get_line(23)
key2.request(consumer="test", type=gpiod.LINE_REQ_DIR_IN, 
             flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)

for i in range(10):
    if key2.get_value() == 0:
        print(f"⚠️ KEY2 is PRESSED (or shorted to ground!)")
    else:
        print(f"✓ KEY2 is released")
    time.sleep(0.5)
```

### Monitor Voltage During Motor Test
Need to:
1. Stop masterpi.service temporarily
2. Run custom script that logs voltage + motor state
3. Detect voltage sag

```python
from common.ros_robot_controller_sdk import Board
import time

board = Board()
board.enable_reception()

print("Starting voltage monitoring...")
for i in range(10):
    volt = board.get_battery()
    if volt:
        v = volt/1000.0
        print(f"Before motors: {v:.2f}V")
    time.sleep(0.5)

print("\nRunning motor...")
board.set_motor_duty([[1, 60]])

for i in range(5):
    volt = board.get_battery()
    if volt:
        v = volt/1000.0
        print(f"During motor: {v:.2f}V")
        if v < 6.5:
            print("⚠️ VOLTAGE SAG DETECTED!")
    time.sleep(0.5)

board.set_motor_duty([[1, 0]])
print("Motor stopped")
```

## Hiwonder Documentation Says

From documentation analysis:
> "When the voltage is less than 7V, the battery power is low and needs to be charged as soon as possible."

> "During device operation, if the LED1 and LED2 lights dim and remain constantly on, it indicates that the power supply is low and needs to be charged."

## Solutions

### Short Term
1. **Fully charge battery** before testing
2. **Check battery voltage** before running motors
3. **Test one motor at a time** (lower current draw)
4. **Watch for dim LEDs** on expansion board
5. **Avoid KEY2 button** during operation

### Medium Term
1. **Add voltage monitoring** to our code
2. **Pre-flight check** refuses to run if voltage < 7.2V
3. **Automatic motor stop** if voltage drops during operation
4. **Visual/audio warning** for low battery

### Long Term
1. **Better power management**
   - Gradual motor acceleration (reduce inrush current)
   - Never run all motors at 100% simultaneously
   - Power budget system
2. **Battery capacity upgrade**
   - Larger mAh cells
   - Better quality 18650s
3. **Separate motor power**
   - Dedicated battery for motors
   - Pi powered separately
   - Eliminates voltage sag affecting Pi

## Testing Protocol

**Before ANY motor test:**
```
1. Check battery voltage > 7.5V
2. Verify KEY2 button not stuck
3. Start with LOW duty cycle (30-40%)
4. Gradually increase if stable
5. Monitor for LED dimming
6. Have finger on power switch
```

**If shutdown occurs:**
```
1. Check battery voltage immediately after restart
2. If < 7V → low battery was the cause
3. If > 7.5V → investigate button/hardware
4. Check system logs: journalctl -b -1 (previous boot)
```

## For PathfinderV2

**Add safety checks:**
```python
class Robot:
    MINIMUM_VOLTAGE = 7.2  # Volts
    
    def check_battery(self):
        volt = self.board.get_battery()
        if volt is None:
            raise RuntimeError("Cannot read battery voltage")
        v = volt / 1000.0
        if v < self.MINIMUM_VOLTAGE:
            raise RuntimeError(f"Battery too low: {v:.2f}V (need >{self.MINIMUM_VOLTAGE}V)")
        return v
    
    def move(self, ...):
        self.check_battery()  # Check before movement
        # ... motor commands
```

## Action Items

- [ ] Check current battery voltage on robot
- [ ] Test KEY2 button (is it working? stuck?)
- [ ] Run voltage monitoring during motor test
- [ ] Add battery check to PathfinderV2
- [ ] Document minimum voltage requirement
- [ ] Create pre-flight check script

---

**Most likely cause:** Low battery causing voltage sag during motor operation.  
**Quick fix:** Charge battery fully before testing.  
**Permanent fix:** Add voltage monitoring and safety checks.
