# Battery Safety

## Quick Check

```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(1)
for i in range(5):
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        v = mv / 1000.0
        print('Battery: %.2fV' % v)
        if v < 7.0: print('CRITICAL - Replace now!')
        elif v < 7.5: print('LOW - Replace soon')
        else: print('OK')
        break
    time.sleep(0.3)
"
```

---

## Voltage Thresholds

### Pi 4 (Competition Robot)

| Voltage | Status | What Works |
|---------|--------|-----------|
| > 8.0V | Excellent | Everything reliable |
| 7.5-8.0V | Good | Motors, servos, vision all work |
| 7.0-7.5V | Low | Still works but replace soon |
| < 7.0V | Critical | Replace immediately |

### Pi 5 (Development Robot)

| Voltage | Status | What Works |
|---------|--------|-----------|
| > 8.2V | Good | Everything reliable |
| 8.0-8.2V | Marginal | Motors inconsistent, Pi may throttle |
| 7.5-8.0V | Low | Motors fail, Pi throttles |
| < 7.5V | Critical | Crashes, servo glitches |

**Why the difference:** Pi 5 draws 5V/5A (25W) vs Pi 4's 5V/3A (15W). The voltage regulator can't supply both Pi 5 and motors at lower battery voltages.

---

## Battery Specifications

- **Type:** 2x 18650 lithium-ion cells (series)
- **Fully charged:** 8.4V (4.2V per cell)
- **Nominal:** 7.4V (3.7V per cell)
- **Safe minimum:** 6.0V (3.0V per cell)
- **Typical capacity:** 2500-3500mAh
- **Runtime:** 30-45 minutes at full operation

---

## Competition Battery Strategy

**6-hour event with 30-45 minute battery cycles:**
- Need 8-12 battery sets per robot
- 21 robots = 168-252 battery sets total
- Start charging used sets immediately
- Label batteries with charge status

**Quick swap procedure:**
1. Power off robot
2. Remove battery holder
3. Swap cells (check polarity!)
4. Power on
5. Wait for 2 beeps (startup complete)
6. Verify voltage > 7.5V

---

## What Happens at Low Voltage

**Under load (all 4 motors):**
- Battery voltage sags 0.2-0.5V below resting voltage
- Pi 5 at 7.9V resting → 7.4V under load → Pi throttles → motors fail
- Pi 4 at 7.9V resting → 7.5V under load → still works fine

**Brownout protection:**
- Built-in circuit cuts power at ~6.0-6.5V
- Prevents cell damage from over-discharge
- Robot reboots when motors stop (voltage recovers)
- **This is correct behavior — the protection is saving your batteries**

---

## Charging

1. Remove cells from robot
2. Insert into charger (check polarity!)
3. Red LED = charging, Green = complete
4. Typical charge time: 4-5 hours from empty
5. Do not leave charging unattended overnight

---

## Best Practices

- **Check voltage before every session**
- **Replace at 7.5V** (Pi 4) or **8.0V** (Pi 5)
- **Keep spare sets charged and ready**
- **Store at ~7.4V** (50% charge) if not using for weeks
- **Use quality cells** (Samsung, Panasonic, LG — not cheap knockoffs)
- **Inspect for swelling** — swollen cells are dangerous, dispose safely
