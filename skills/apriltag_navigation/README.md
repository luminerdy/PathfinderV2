# AprilTag Navigation Skill

**Quick Reference Card**

---

## Choose Your Level

### 🟢 Level 1: Just Run It (Beginners)
**File:** `run_demo.py`  
**What:** Pre-built demo, no code changes needed  
**Time:** 5 minutes

```bash
python3 run_demo.py
```

### 🟡 Level 2: Tune Parameters (Non-Coders)
**File:** `config.yaml`  
**What:** Edit configuration values, no coding  
**Time:** 15 minutes

1. Edit `config.yaml` (change target_tag_id, speeds, etc.)
2. Run `run_demo.py` again to see changes

### 🟠 Level 3: Fill in the Blanks (Learning to Code)
**File:** `apriltag_nav_template.py`  
**What:** Complete the TODO sections  
**Time:** 30-45 minutes

1. Read `SKILL.md` Implementation Guide
2. Open `apriltag_nav_template.py`
3. Search for `???` and fill in your code
4. Run and test

### 🔴 Level 4: Full Implementation (Advanced)
**File:** `apriltag_nav.py`  
**What:** Read and understand the complete implementation  
**Time:** 1-2 hours

1. Study `SKILL.md` Engineering Deep Dive
2. Read `apriltag_nav.py` (full implementation)
3. Modify and extend for your needs

---

## Quick Troubleshooting

**Problem:** "No module named 'pupil_apriltags'"  
**Solution:** `pip3 install pupil-apriltags`

**Problem:** "No tag detected"  
**Solution:** 
- Print tag from `apriltags/tag36h11_singles.pdf`
- Ensure tag is flat, well-lit, in camera view
- Start 3-5 feet away

**Problem:** "Robot doesn't move"  
**Solution:**
- Check battery: `python3 ../../tests/battery_check.py`
- Test motors: `python3 ../../tests/test_drive.py`

**Problem:** "ImportError: cannot import name 'get_board'"  
**Solution:** Run from correct directory or fix Python path

---

## Files

| File | Level | Purpose |
|------|-------|---------|
| `SKILL.md` | All | Complete documentation (4 sections) |
| `run_demo.py` | 1 | One-click demo |
| `config.yaml` | 2 | Tune parameters |
| `apriltag_nav_template.py` | 3 | Learning template |
| `apriltag_nav.py` | 4 | Full implementation |
| `calibrate_camera.py` | Util | Camera calibration tool |
| `README.md` | - | This file |

---

## Next Skills

After mastering AprilTag Navigation, try:

- **Block Detection** - Find colored blocks using computer vision
- **Visual Servoing** - Approach objects using camera feedback
- **Multi-Tag Tour** - Visit multiple tags in sequence
- **Autonomous Pickup** - Navigate + detect + grab blocks

---

*Questions? Read SKILL.md or ask a mentor!*
