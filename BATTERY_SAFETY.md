# Battery Safety and Voltage Requirements

## Critical Information

⚠️ **ALWAYS check battery voltage before running motors!**

### Voltage Thresholds

| Voltage | Status | Action |
|---------|--------|--------|
| > 8.0V | Excellent | Full operation OK |
| 7.5-8.0V | Good | Normal operation OK |
| 7.0-7.5V | Low | Light operation only, charge soon |
| 6.5-7.0V | Critical | No motor operation, charge now |
| < 6.5V | Emergency | Shutdown and charge immediately |

### What Happens at Low Voltage

**Example from testing (2026-03-20):**
- Idle voltage: 6.87V
- Motor started: Voltage dropped below protection threshold
- Result: Instant power cutoff (brownout protection)
- Robot rebooted when motor stopped (voltage recovered)

**This is CORRECT behavior!** The protection circuit is saving your battery from over-discharge damage.

## How to Check Battery

### Method 1: Via Python
```python
from hardware import Board

board = Board()
volt_mv = board.get_battery()

if volt_mv:
    volts = volt_mv / 1000.0
    print(f"Battery: {volts:.2f}V")
    
    if volts < 6.5:
        print("🔴 EMERGENCY - Charge immediately!")
    elif volts < 7.0:
        print("🔴 CRITICAL - No motor operation!")
    elif volts < 7.5:
        print("🟡 LOW - Charge soon")
    elif volts < 8.0:
        print("🟢 OK - Normal operation")
    else:
        print("🟢 EXCELLENT - Fully charged")
else:
    print("❌ Cannot read battery voltage")
```

### Method 2: Visual Indicators
- **LED brightness:** Dim LEDs = low battery
- **Expansion board LEDs:** Watch LED1 and LED2
- If they dim during operation → battery is low

### Method 3: Check Before Each Session
```bash
cd /home/robot/code/pathfinder
python3 -c "
from hardware import Board
import sys
board = Board()
volt = board.get_battery()
if volt:
    v = volt/1000.0
    print(f'Battery: {v:.2f}V')
    if v < 7.5:
        print('⚠️ Battery too low for motor operation!')
        sys.exit(1)
    else:
        print('✓ Battery OK')
        sys.exit(0)
else:
    print('❌ Cannot read voltage')
    sys.exit(1)
"
```

## Why Brownout Protection Exists

**Lithium-ion batteries (18650 cells):**
- Nominal voltage: 3.7V per cell
- Fully charged: 4.2V per cell
- Safe minimum: 3.0V per cell
- Damage threshold: < 2.5V per cell

**Two cells in series:**
- Fully charged: 8.4V
- Nominal: 7.4V
- Safe minimum: 6.0V
- **Protection cuts at ~6.0-6.5V** to prevent cell damage

**Over-discharge damage:**
- Reduced capacity
- Internal resistance increases
- Risk of thermal runaway
- Shortened lifespan
- Potential fire hazard

**The protection circuit is your friend!** It prevents expensive battery damage.

## Charging Procedure

**From Hiwonder documentation:**

1. Remove battery from robot
2. Insert 18650 cells into charger (check polarity!)
3. Connect charger to 5V 3A power supply
4. Charging indicator: Red = charging, Green = complete
5. Typical charge time: ~5 hours from empty
6. **Do not leave charging continuously** - unplug when complete

**Battery Specifications:**
- 2x 18650 lithium-ion cells
- Series connection (7.4V nominal)
- Typical capacity: 2000-3000mAh (depends on cells)
- Protection circuit built into battery holder

## Motor Current Draw

**Typical current consumption:**
- Idle (Pi + sensors): ~1-2A
- One motor at 50% duty: ~2-3A
- All four motors at 100%: ~10-12A peak
- Servos moving: ~0.5-1A per servo

**Battery capacity example:**
- 2500mAh battery
- Running all motors at 50%: ~6A draw
- Runtime: 2500mAh / 6000mA = ~25 minutes
- **But voltage sag limits this to ~15 minutes realistically**

## Best Practices

### Before Each Session
1. Check battery voltage > 7.5V
2. If < 7.5V → charge first
3. Start with low motor speeds (30-50%)
4. Gradually increase if stable

### During Operation
1. Watch for LED dimming
2. Monitor battery voltage if possible
3. If brownout occurs → charge battery
4. Avoid sustained high-speed operation

### After Operation
1. Check battery voltage
2. If < 7.2V → charge before next use
3. Store at ~50% charge (7.4V) if not using for weeks

### Battery Care
- Don't over-discharge (< 6.0V)
- Don't overcharge (> 8.4V)
- Store in cool, dry place
- Check for swelling/damage
- Replace if capacity drops significantly

## Adding Voltage Checks to Code

### Pre-flight Check Function
```python
def preflight_check(board, minimum_voltage=7.5):
    """
    Check if robot is safe to operate.
    Raises RuntimeError if battery too low.
    """
    volt_mv = board.get_battery()
    
    if volt_mv is None:
        raise RuntimeError("Cannot read battery voltage")
    
    volts = volt_mv / 1000.0
    print(f"Battery: {volts:.2f}V", end=" ")
    
    if volts < minimum_voltage:
        print(f"❌ TOO LOW (need >{minimum_voltage}V)")
        raise RuntimeError(
            f"Battery too low: {volts:.2f}V "
            f"(minimum {minimum_voltage}V required)"
        )
    else:
        print("✓ OK")
        return volts
```

### Use in Movement Code
```python
from capabilities.movement import Movement
from hardware import Board

board = Board()
movement = Movement(board)

# Check before any motor operation
preflight_check(board, minimum_voltage=7.5)

# Now safe to move
movement.forward(speed=50)
```

### Continuous Monitoring (Optional)
```python
import threading
import time

def voltage_monitor(board, threshold=7.0, callback=None):
    """Background thread to monitor voltage."""
    while True:
        volt = board.get_battery()
        if volt:
            v = volt / 1000.0
            if v < threshold:
                print(f"\n⚠️ LOW VOLTAGE: {v:.2f}V")
                if callback:
                    callback(v)
        time.sleep(5)  # Check every 5 seconds

# Start monitoring thread
monitor = threading.Thread(
    target=voltage_monitor, 
    args=(board, 7.0, lambda v: print("Consider stopping soon!"))
)
monitor.daemon = True
monitor.start()
```

## Troubleshooting

**Problem:** Robot shuts down when motors run
- **Cause:** Battery voltage too low
- **Solution:** Charge battery to > 7.5V

**Problem:** Battery reads None
- **Cause:** Board not initialized or serial connection issue
- **Solution:** Check board connection, enable_reception()

**Problem:** Voltage drops rapidly during operation
- **Cause:** Battery near end of life or low capacity
- **Solution:** Replace 18650 cells with high-quality ones

**Problem:** Robot works but suddenly dies after 5 minutes
- **Cause:** Battery capacity degraded
- **Solution:** Replace battery cells

## Recommended Equipment

**Battery Charger:**
- Dual-bay 18650 charger
- 5V input (USB or wall adapter)
- LED indicators
- ~$10-15

**Spare Batteries:**
- High-quality 18650 cells (Samsung, Panasonic, LG)
- Minimum 2500mAh capacity
- Protected cells (built-in safety circuit)
- ~$5-8 per cell

**Voltage Tester:**
- Multimeter (check actual voltage)
- USB voltage meter (monitor during charging)
- ~$10-20

## Summary

✅ **Always check battery > 7.5V before motor operation**  
✅ **Brownout protection is good** - it saves your battery  
✅ **Charge promptly when voltage drops**  
✅ **Monitor during operation**  
✅ **Replace degraded cells**  

**Battery safety is not optional!** It protects your hardware and prevents fire hazards.

---

**Reference:** Based on testing 2026-03-20 where 6.87V battery caused instant brownout during motor operation.
