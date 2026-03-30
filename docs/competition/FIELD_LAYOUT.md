# Field Layout Guide

**Purpose:** How to build the competition field for Supply Chain Scramble

---

## Field Dimensions

- **Size:** 10 × 10 feet (3m × 3m)
- **Surface:** Interlocking foam tiles (dark gray/black)
- **Walls:** Foam board, cardboard, or PVC panels — 18-24" tall

---

## Layout Diagram

```
              10 ft (3m)
    ┌─────────────────────────────┐
    │                             │
    │  ╔═══════════════════════╗  │  NORTH WALL
    │  ║  SCORING / DELIVERY   ║  │  Tags 578, 579
    │  ║  🧺B    🧺Y    🧺R   ║  │
    │  ║  578    579    580    ║  │  Baskets under tags
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
    │      🔴 🟡 🔵              │  9 blocks scattered
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
| North | 578, 579 | Evenly spaced, above baskets |
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

## Baskets

### Specifications
- **Quantity:** 3 (one per color)
- **Type:** Small plastic shopping baskets or bins
- **Colors:** Red, Yellow, Blue
  - Use colored baskets, or white baskets with colored tape/paper
- **Size:** ~12" × 8" × 6" (large enough for 3+ blocks)

### Placement
- Along **north wall** (delivery zone)
- Centered under AprilTags:
  - Tag 578 → Blue basket (left)
  - Tag 579 → Yellow basket (center)
  - Tag 580 → Red basket (right)
- Baskets touching the wall (robot drives up and drops)

---

## Blocks

### Specifications
- **Quantity:** 9 total (3 red, 3 yellow, 3 blue)
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
- **Size:** ~18" long × 6" wide × 12" tall
- **Material:** Heavy box filled with books/sand, or clamped foam board
- **Quantity:** 1-2
- **Purpose:** Forces path planning — robot must go around

### Pushable Barrier (can be bulldozed)
- **Size:** ~12" long × 4" wide × 8" tall
- **Material:** Lightweight cardboard box (empty or lightly filled)
- **Quantity:** 1-2
- **Purpose:** Strategic choice — push aside or navigate around?

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
| Wall panels | 8-12 | Foam board or cardboard, 18-24" tall |
| AprilTags (printed) | 8 | tag36h11, IDs 578-585, 10"×10" |
| Colored baskets | 3 | Red, yellow, blue |
| Colored blocks | 9 | 3 red, 3 yellow, 3 blue (~1.2" cubes) |
| Fixed barriers | 1-2 | Heavy boxes, 12" tall |
| Pushable barriers | 1-2 | Light cardboard, 8" tall |
| Lime green tape | 1 roll | For passage line + start zones |
| Regular tape | 2 rolls | Mounting tags, securing walls |
| Overhead lighting | — | Even, no shadows |

---

## Setup Time

**Allow 30-45 minutes** for field setup:
1. Lay foam tiles (10 min)
2. Set up walls (10 min)
3. Mount AprilTags (5 min)
4. Place baskets (2 min)
5. Lay green tape passage (5 min)
6. Mark start zones (3 min)
7. Place barriers (3 min)
8. Test: walk around field, check tag visibility from all angles (5 min)

**Tip:** Build the field the night before if possible. Save 30 minutes on workshop day.
