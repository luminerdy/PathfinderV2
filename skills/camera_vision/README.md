# Camera Vision Skill - Quick Reference

**Capture, display, and process camera images**

---

## Quick Start

### Level 1: Test Hardware
```bash
python3 test_camera.py
```
Captures 5 frames, saves test_frame.jpg

### Level 2: Live Video
```bash
python3 run_demo.py
```
Live feed with FPS, press 'q' to quit, 's' for snapshot

### Level 3: Color Spaces
```bash
python3 color_spaces.py
```
Saves BGR, RGB, Grayscale, HSV examples

---

## Learning Outcomes

After this skill, you can:
- ✅ **Capture** images from camera
- ✅ **Display** live video feed
- ✅ **Convert** between color spaces (BGR, RGB, HSV, Gray)
- ✅ **Detect** colors using HSV thresholding
- ✅ **Process** images (blur, edges, threshold)

**Assessment:** Capture image, detect red object, explain HSV

---

## Color Spaces Quick Reference

**BGR:** OpenCV default (Blue-Green-Red)  
**RGB:** Human perception (Red-Green-Blue)  
**Grayscale:** Single channel, fast processing  
**HSV:** Best for color detection (Hue-Saturation-Value)

---

## Troubleshooting

**No camera:**
- Check: `ls /dev/video*`
- Try device 1 or 2

**Permission denied:**
- `sudo usermod -a -G video $USER`
- Re-login

**Black screen:**
- Camera covered?
- Wrong device index?

---

## Next Skills

- **E2: AprilTag Navigation** - Uses camera for tags
- **E3: Block Detection** - Color detection + tracking
- **E5: Autonomous Pickup** - Vision + arm integration

---

*See the world through robot eyes!* 📷
