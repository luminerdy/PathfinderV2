# Field Layout Guide

**Purpose:** How to build the competition field for Supply Chain Scramble

---

## Field Dimensions

- **Size:** 10 × 10 feet (3m × 3m)
- **Surface:** Interlocking foam tiles (dark gray/black)
- **Perimeter:** Flexible black landscape edging (49ft roll + 75 spikes), 4" tall
  - ⚠️ *Testing needed Apr 25: verify rigidity and robot boundary detection*

---

## Layout Diagram

```
              10 ft (3m)
    ┌─────────────────────────────┐
    │                             │
    │  ╔═══════════════════════╗  │  NORTH WALL
    │  ║  SCORING / DELIVERY   ║  │  Tags 578, 579
    │  ║  📦B    📦Y    📦R   ║  │
    │  ║  578    579    580    ║  │  Boxes under tags
    │  ╚═══════════════════════╝  │
    │                             │
  W │     ┌──────┐    ┌──────┐    │ E
  E │     │FIXED │    │PUSH  │    │ A    Tags 580, 581
  S │     │      │    │      │    │ S
  T │     └──────┘    └──────┘    │ T
    │                             │
  W │  ════╗            ╔════     │ W
  A │      ║  (passage) ║        │ A    Tags 584, 585
  L │  ════╝  ▓▓▓▓▓▓▓▓  ╚════   │ L
  L │         (green tape)        │ L
    │                             │
    │   🔴 🟡 🔵                  │  BLOCK ZONE
    │      🔴 🟡 🔵              │  many blocks (3 colors)
    │         🔴 🟡 🔵           │
    │                             │
    │  ┌─────┐┌─────┐┌─────┐     │  SOUTH WALL
    │  │ ST1 ││ ST2 ││ ST3 │     │  Tags 582, 583
    │  └─────┘└─────┘└─────┘     │  Start/swap zones
    └─────────────────────────────┘
```

---

## AprilTags

### Specifications
- **Family:** tag36h11
- **Size:** 10" × 10" (254mm) printed
- **Quantity:** 8 tags total
- **Mounting:** Tape to wall at **12-15 inches** above floor level
  - High enough for camera to see from across field
  - Low enough to be in camera frame when close

### Placement

| Wall | Tag IDs | Position |
|------|---------|----------|
| North | 578, 579 | Evenly spaced, above delivery boxes |
| East | 580, 581 | Evenly spaced |
| South | 582, 583 | Above start zones |
| West | 584, 585 | Evenly spaced |

**Spacing:** Tags should be ~3-4 feet apart on each wall, centered.

**Important:** Tags must be **flat against the wall** (not curled) and **well-lit** (no shadows across the tag).

### Printing
- Print on **white paper**, standard printer
- Ensure **white border** around black pattern (at least 1")
- Laminate if possible (durability)
- Source: [AprilTag generator](https://chev.me/arucogen/) — select tag36h11, IDs 578-585

---

## Delivery Boxes

### Specifications
- **Type:** 6"×6" unfinished wooden boxes (no paint/color coding)
  - [Amazon: 8-pack ~$22.99](https://a.co/d/0aKvlW4K)
- **Quantity:** 3 (one per zone/area)
- **Zone marking:** White tape on floor marks delivery areas — not the boxes themselves
- **Optional rollers:** Self-adhesive 360° caster wheels on underside
  - [Amazon: 24pc caster set](https://a.co/d/00kaBTgh)

### Mechanics
- Boxes are plain containers — zone identity comes from floor tape and AprilTags, not box color
- Blocks are loaded into or pushed up to the box
- With rollers: robot can push the box as a strategy

### Placement
- Along **north wall** (delivery zone)
- Centered under AprilTags:
  - Tag 578 → Box (left zone)
  - Tag 579 → Box (center zone)
  - Tag 580 → Box (right zone)
- White tape on floor marks each zone boundary

---

## Blocks

### Specifications
- **Quantity:** Many — multiple of each color (red, yellow, blue)
- **Size:** ~1.2" (30mm) cubes
- **Material:** Wood or plastic blocks

### Placement
- Scatter **randomly** in the block zone (south half of field)
- Not in neat rows — randomize each match
- At least 6" from walls (so robot can approach)
- At least 4" apart (so robot can target one at a time)

---

## Barriers

### Fixed Barrier (cannot be moved)
- **Material:** Corrugated cardboard boxes, 12"×4"×3"
  - [Amazon: 25-pack](https://a.co/d/05WVl2Vm)
- **Mounting:** Taped to floor — no pushing
- **Quantity:** 1-2
- **Purpose:** Fixed obstacles, forces path planning

### Pushable Barrier (foam pit cubes)
- **Material:** 5"×5"×5" foam pit blocks (light grey/black)
  - [Amazon: WINTECY 24pc set](https://a.co/d/0cYsjSSX)
- **Quantity:** Several
- **Purpose:** Strategic choice — push aside or navigate around?
- **⚠️ Sonar warning:** Foam absorbs sonar signal — do NOT rely on distance sensing near these. Use vision or AprilTags instead.
- **Note:** Provides some resistance when pushed — robot needs meaningful drive force

### Placement
- Middle zone of field (between baskets and blocks)
- **Do NOT block** line of sight to AprilTags (keep below tag height)
- Leave at least **14" gap** between barriers for passage
- Asymmetric placement (not perfectly centered — forces decisions)

---

## Passage (Green Tape Line)

### Specifications
- **Tape:** Lime green (fluorescent/neon) masking or electrical tape
- **Width:** ~1/2" to 1" tape
- **Length:** ~3-4 feet through the passage gap
- **Color:** Must be lime green (H=40-75 in HSV) — not regular green, not yellow-green

### Layout
- Runs through the **narrow gap** between two barriers
- Gap width: **~14 inches** (robot width ~10" + 2" clearance each side)
- Can include gentle curves (tests line following accuracy)
- Starts in block zone, ends near delivery zone

### Why Lime Green?
- Zero HSV overlap with red, blue, or yellow blocks
- High contrast on dark foam floor
- Robot's line follower is tuned for H=40-75
- **Dual purpose near foam barriers:** Since foam pit cubes absorb sonar, green tape laid through those areas gives robots a vision-based guidance path as an alternative to distance sensing

---

## Start / Swap Zones

### Specifications
- **Quantity:** 3 zones along south wall
- **Size:** ~18" × 18" each (fits one robot)
- **Marking:** Green tape square, or colored tape border
- **Spacing:** ~6" between zones

### Rules
- Robots must start here at match beginning
- Robot must be in start zone to swap (tag-team)
- Swapped robot enters from start zone

---

## Lighting

Good lighting is critical for camera performance:
- **Overhead fluorescent/LED** recommended
- **No harsh shadows** across the field (blocks become invisible in shadow)
- **No direct sunlight** through windows (washes out camera)
- Test camera detection under actual workshop lighting before the event

---

## Materials Checklist

| Item | Qty | Notes |
|------|-----|-------|
| Foam floor tiles | ~25 (2'×2') | 10×10 ft coverage |
| Black landscape edging (49ft) | 1 roll | Outer perimeter + spikes — ⚠️ test Apr 25 |
| AprilTags (printed) | 8 | tag36h11, IDs 578-585, 10"×10" |
| 6"×6" unfinished wooden boxes | 3 | Delivery containers — left unfinished, no color coding |
| Self-adhesive caster wheels | 1 set (24pc) | Optional: attach to boxes for rollability |
| White tape | 1 roll | Mark delivery zones and field areas |
| Colored blocks | many | Multiple red, yellow, blue (~1.2" cubes) |
| Fixed barriers (cardboard boxes) | 1-2 | 12"×4"×3", taped to floor |
| Foam pit cubes (5"×5"×5") | several | Pushable — ⚠️ sonar-absorbing! |
| Lime green tape | 1 roll | For passage line + start zones |
| Regular tape | 2 rolls | Mounting tags, securing walls |
| Overhead lighting | — | Even, no shadows |

---

## Setup Time

**Allow 30-45 minutes** for field setup:
1. Lay foam tiles (10 min)
2. Set up perimeter edging + spikes (10 min)
3. Mount AprilTags (5 min)
4. Place delivery boxes (2 min)
5. Lay green tape passage (5 min)
6. Mark start zones (3 min)
7. Place barriers (3 min)
8. Test: walk around field, check tag visibility from all angles (5 min)

**Tip:** Build the field the night before if possible. Save 30 minutes on workshop day.
