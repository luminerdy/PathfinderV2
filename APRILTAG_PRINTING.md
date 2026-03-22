# AprilTag Printing Guide

## What to Print

You need **4 AprilTags** for the corner field configuration:

- **Tag ID: 0** (Northwest corner)
- **Tag ID: 1** (Northeast corner)
- **Tag ID: 2** (Southeast corner)
- **Tag ID: 3** (Southwest corner)

**Tag Family:** tag36h11 (standard)  
**Size:** 6 inches x 6 inches  
**Paper:** 8.5" x 11" white paper  

## Download Pre-Generated Tags

### Option 1: MIT AprilTag Images (Recommended)
https://github.com/AprilRobotics/apriltag-imgs/tree/master/tag36h11

**Direct links:**
- Tag 0: https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_00000.png
- Tag 1: https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_00001.png
- Tag 2: https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_00002.png
- Tag 3: https://raw.githubusercontent.com/AprilRobotics/apriltag-imgs/master/tag36h11/tag36_11_00003.png

### Option 2: Online Generator
https://chev.me/arucogen/

**Settings:**
- Dictionary: AprilTag (tag36h11)
- Marker ID: 0, 1, 2, 3
- Marker size: 150mm (6 inches)
- Download as PNG or PDF

## Printing Instructions

### 1. Download Images
Save all 4 PNG files to your computer

### 2. Print Settings
- **Paper size:** 8.5" x 11" (Letter)
- **Orientation:** Portrait
- **Scale:** Fit to page OR manually scale to 6"
- **Color:** Black and white (grayscale OK)
- **Quality:** High quality / Best

### 3. Verify Size
After printing, **measure the tag!**
- Black square border should be **exactly 6 inches**
- Use a ruler to verify
- If wrong, adjust print scaling and reprint

### 4. Prepare for Mounting
**Option A: Laminate**
- Laminate the printed page for durability
- Protects from dirt and moisture

**Option B: Mount on Coroplast**
- Cut 2' x 18" Coroplast panels (one per corner)
- Glue or tape tag to center of panel
- Provides rigid backing

**Option C: Cardboard**
- Mount on stiff cardboard
- Cheaper but less durable

## Field Layout

```
6 ft x 6 ft field

         TAG 0 (North)
             ↓
      ┌──────────────┐
      │              │
TAG 3 →  FIELD    ← TAG 1
(West)│              │(East)
      │              │
      └──────────────┘
             ↑
         TAG 2 (South)

         6 ft x 6 ft
```

**Mounting:**
- **Height:** 10 inches above floor (center of tag)
- **Position:** One tag per wall, **centered**
- **Orientation:** Tag upright (not rotated)
- **Flat against wall:** No wrinkles or bends

## Tag Placement Details

### Tag 0 - North Wall (Top)
- **Center of north wall** (3 ft from each corner)
- 10" high
- Faces south (into field)

### Tag 1 - East Wall (Right)
- **Center of east wall** (3 ft from each corner)
- 10" high
- Faces west (into field)

### Tag 2 - South Wall (Bottom)
- **Center of south wall** (3 ft from each corner)
- 10" high
- Faces north (into field)

### Tag 3 - West Wall (Left)
- **Center of west wall** (3 ft from each corner)
- 10" high
- Faces east (into field)

## Testing Tags

After mounting, test detection:

```bash
cd ~/code/pathfinder
python3 find_apriltag.py
```

The robot will rotate and search for tags. You should see output like:

```
[SUCCESS] Found 1 tag(s) after 3.2s
  Tag ID: 0
  Center: (320, 240) pixels
  Offset from center: 0 pixels
  Estimated angle: 0.0° from forward
```

If tags not detected:
- Check lighting (avoid glare/shadows)
- Verify tags are flat (no wrinkles)
- Ensure 10" height is correct
- Try moving robot closer to wall

## Troubleshooting

### Tags not detected
- **Too far away:** Move robot closer (within 6 feet)
- **Bad lighting:** Add light or reduce glare
- **Wrong size:** Remeasure and verify 6 inches
- **Wrong family:** Must be tag36h11
- **Wrinkled:** Tags must be perfectly flat

### Robot sees wrong tag ID
- Double-check which file you printed
- Verify tag number in corner of image

### Inconsistent detection
- Tags may be at slight angle
- Ensure mounted perpendicular to floor
- Check for shadows or reflections

## Quick Checklist

- [ ] Downloaded tags 0, 1, 2, 3 (PNG files)
- [ ] Printed at correct size (6" black square)
- [ ] Measured with ruler to verify
- [ ] Mounted on rigid backing
- [ ] Positioned at corners of field
- [ ] Height is 10 inches (center of tag)
- [ ] Tags face inward toward field
- [ ] Tested with `python3 find_apriltag.py`
- [ ] Robot successfully detects all 4 tags

## Next Steps

Once tags are mounted:
1. Test tag detection: `python3 find_apriltag.py`
2. Run autonomous navigation test: `python3 tests/run_field_test.py`
3. Test localization while holding block: `python3 find_apriltag_with_block.py`

---

**Ready to give your robot eyes!** 🤖👁️
