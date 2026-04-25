# Buddy Robot Physical Specifications

## Chassis Dimensions (Hiwonder MasterPi)

| Measurement | Metric | Imperial |
|-------------|--------|----------|
| **Length** (front to back) | 185mm | 7.3" |
| **Width** (wheel to wheel) | 162mm | 6.4" |
| **Height** (arm up) | 347mm | 13.7" |
| **Weight** | 1.1kg | 2.4 lb |
| **Wheelbase** | ~140mm | ~5.5" |
| **Ground clearance** | ~15mm | ~0.6" |

**With modifications (12" cube rule):**
- Max allowed: 305 x 305 x 305mm (12" x 12" x 12")
- Clearance beyond stock: ~120mm each direction

## Arm Specifications

| Measurement | Value | Notes |
|-------------|-------|-------|
| **DOF** | 4 + gripper | Shoulder, elbow, wrist rotate, wrist pitch, gripper |
| **Reach (forward)** | ~200mm / 8" | Fully extended from chassis center |
| **Reach (down)** | Floor level | Touches ground for block pickup |
| **Gripper opening** | ~50mm / 2" | Sized for ~30mm blocks |
| **Lift capacity** | Light objects only | 30mm wood/plastic cubes |
| **Pickup height** | 0mm (floor) | Standard block pickup |
| **Max pickup height** | ~100mm / 4" | Shoulder raised, limited |

## Sensors

| Sensor | Range | Resolution | Notes |
|--------|-------|------------|-------|
| **Camera** | 640x480 | ~60deg FOV | On gripper/end of arm |
| **Sonar** | 20-4000mm | ~1mm | Forward-facing, RGB LEDs |
| Sonar safe zone | >610mm (24") | | Green LED |
| Sonar caution | 150-610mm (6-24") | | Yellow LED |
| Sonar danger | <150mm (6") | | Red LED |

## Performance (Measured)

| Metric | Value | Conditions |
|--------|-------|------------|
| **Max forward speed** | ~30 cm/s | Power 50, fresh batteries |
| **Cruising speed** | ~15 cm/s | Power 35, sustained |
| **Line follow speed** | ~10 cm/s | Power 30, with steering corrections |
| **90-degree turn** | ~1.5s | In place, power 40 |
| **Full E7 cycle** | 23s | Scan, grab, line follow, deliver (pre-positioned) |
| **Block pickup** | ~5s | Bump grab sequence |
| **Arm move** | ~1-2s | Position to position |

## Battery

| Metric | Value |
|--------|-------|
| **Type** | 2x 18650 Li-ion |
| **Voltage** | 7.4V nominal, 8.4V full, 7.0V cutoff |
| **Endurance** | 79.6 min at power 45 (continuous driving) |
| **Competition estimate** | 7-8 matches (10 min each) per charge |
| **Decline pattern** | Gradual, no cliff |

## Detection Ranges (Measured)

| Target | Max Detection | Reliable Range | Notes |
|--------|--------------|----------------|-------|
| **AprilTag (10")** | ~3m / 10ft | ~2m / 6.5ft | tag36h11, fx=500 estimated |
| **Block (30mm)** | ~80cm / 32" | ~40cm / 16" | HSV color detection |
| **Block bump grab** | ~50cm / 20" | Start approach distance | Drives until block vanishes |
| **Basket (tag area)** | area ~3000px | ~30-40cm / 12-16" | Drop distance trigger |
| **Sonar obstacle** | 4m | 24" safe / 6" danger | |

## Field-Critical Dimensions

These are what matter for field design:

| Question | Answer |
|----------|--------|
| **Minimum passage width** | 8" (robot 6.4" + 0.8" each side) |
| **Comfortable passage** | 10-12" (allows some drift) |
| **Challenge passage** | 14" (needs precision or line following) |
| **Arm reach beyond chassis** | ~4" forward from front edge |
| **Camera sees tags from** | Full field (10ft) at 10" tag size |
| **Camera sees blocks from** | ~32" max, ~16" reliable |
| **Time to cross 10ft field** | ~10s at cruise, ~20s with nav |
| **Blocks per trip (gripper)** | 1 |
| **Blocks per trip (bin)** | 2-3 (rear bin modification) |
| **Blocks per trip (cart)** | 3-5 (cart push modification) |

---

*Source: Hiwonder MasterPi specs + PathfinderV2 testing (Days 1-16)*
*Last updated: April 3, 2026*
