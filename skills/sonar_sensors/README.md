# Sonar Sensors Skill - Quick Reference

**Learn distance sensing and obstacle detection**

---

## Quick Start

```bash
cd /home/robot/pathfinder/skills/sonar_sensors
python3 run_demo.py
```

**What you'll see:** 6 sonar demos (distance, filtering, detection, zones, safe movement, avoidance)

**Time:** 15-20 minutes

---

## Learning Outcomes

After this skill, you can:
- ✅ **Explain** how ultrasonic sensors work (sound echo timing)
- ✅ **Read** distance values in centimeters
- ✅ **Implement** threshold logic (stop/slow/go)
- ✅ **Use** RGB LEDs for visual feedback
- ✅ **Filter** noisy sensor data (median, average)

**Assessment:** Robot stops before hitting obstacle, RGB shows correct colors

---

## Files

| File | Level | Purpose |
|------|-------|---------|
| `SKILL.md` | All | Complete documentation (4 sections) |
| `run_demo.py` | 1 | One-click 6-demo showcase |
| `config.yaml` | 2 | Tune thresholds, colors, safety |
| `README.md` | - | This file |

---

## Troubleshooting

**Readings always 400cm:**
- Normal if no object (sensor sees "infinity")
- Object too far away (>4 meters)

**Noisy readings:**
- Increase filter_samples in config
- Use filtered reading instead of single

**RGB doesn't light:**
- Check cable connections
- Quick test: `cd /home/robot/pathfinder && python3 -c "from hardware.sonar import Sonar; import time; s = Sonar(); s.set_both_rgb((255,0,0)); time.sleep(2); s.rgb_off()"`
- Should see RED for 2 seconds then off
- If error about `setPixelColor`, method name needs to be `set_pixel_color` (snake_case)

---

## Next Skills

- **D3: Robotic Arm** - Add manipulation
- **E2: AprilTag Navigation** + Sonar = Safe autonomous navigation
- **E4: Visual Servoing** - Camera + Sonar for precise approach

---

*Safety first - let sensors guide the way!* 🔊
