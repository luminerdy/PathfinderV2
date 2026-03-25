# PathfinderV2 Team Competition — Draft Design

**Status:** DRAFT — Work in progress
**Last Updated:** March 25, 2026

---

## Overview

Three robots per team. 7 teams. 5-minute rounds. Indoor, 12×12 ft field with barriers, passageways, and colored blocks. Mixed mode: manual driving + autonomous capabilities. Teams that automate score faster.

---

## Field Layout

### Dimensions
- **Field:** 12 ft × 12 ft
- **Barriers:** ~12 inches tall (must block robot camera line-of-sight)
- **Passageways:** 18 inches wide (fits one robot)
- **Blocks:** 1.2 inch cubes, 3 colors (red, blue, yellow)
- **AprilTags:** tag36h11 family, on walls, barriers, and scoring zones

### Zone Design

```
12 ft
┌─────────────────────────────────────────────┐
│              ZONE A                         │
│  [T1] [T2]                                 │
│      🟥 🟦 🟨          ║                   │
│                        ║ BARRIER (12")      │
│      ◉ START A    ═════╝                    │
│ ─────────────────╗     PASS    ╔────────────│
│   BARRIER        ║    (18")    ║   BARRIER  │
│ ─────────────────╝             ╚────────────│
│      ◉ START C    ═════╗                    │
│                        ║                    │
│      🟥 🟦 🟨          ║ BARRIER            │
│  [T5] [T6]            ║                    │
│              ZONE C    ║    ZONE B          │
│                        ║  [T3] [T4]        │
│                        ║   🟥 🟦 🟨        │
│                        ║                    │
│                        ║   ◉ START B        │
│    ┌──────────┐                             │
│    │ SCORING  │         ┌──────────┐        │
│    │ ZONE 1   │         │ SCORING  │        │
│    │ (Tags)   │         │ ZONE 2   │        │
│    └──────────┘         └──────────┘        │
└─────────────────────────────────────────────┘
```

### Key Design Decisions

**Tall barriers (12"):**
- Blocks camera line-of-sight between zones
- Prevents tag confusion (robot only sees tags in its own zone)
- Forces use of passageways for zone-to-zone movement
- Creates the "transfer" mechanic — blocks must be lifted over

**3 isolated zones:**
- Each robot starts in its own zone
- Each zone has its own AprilTags for navigation
- Each zone has 3 blocks (1 of each color)
- Robots can move between zones through passageways

**Scoring zones:**
- Located in accessible area
- Marked with AprilTags
- Where blocks must be delivered for points

---

## Blocks

### Specifications
- **Size:** 1.2 inches (~30mm) cubes
- **Colors:** Red, Blue, Yellow
- **Quantity:** 9 per round (3 per zone, 1 of each color)
- **Material:** Wood or foam (must be grippable)

### Detection Challenge
At 1.2 inches, blocks are small:
- At 1 meter: ~8 pixels wide (nearly invisible)
- At 30 cm: ~25 pixels wide (detectable)
- At 15 cm: ~50 pixels wide (reliable detection)

**Implication:** Robots must be close to detect blocks. Camera-down position required for floor scanning.

---

## Scoring

### Block Delivery

Points scale with detection difficulty — harder to detect = more points.

| Action | Points | Why |
|--------|--------|-----|
| 🟥 Red block delivered | **5 pts** | Easiest to detect (highest contrast) |
| 🟦 Blue block delivered | **10 pts** | Medium difficulty |
| 🟨 Yellow block delivered | **15 pts** | Hardest to detect (lighting glare) |
| Any block transferred through barrier window | **2× points** | Coordination bonus |
| Complete color set (R+B+Y in same scoring zone) | **+25 bonus** | Strategy reward |

**Strategy tension:**
- Safe play: Grab red blocks fast (easy, 5 pts each)
- Skilled play: Go for yellow (hard to detect, 15 pts each)
- One yellow = three reds — teams that tune detection get rewarded

### Maximum Theoretical Score
- 3 red (15) + 3 blue (30) + 3 yellow (45) = 90 pts solo
- With transfers (2×): up to 180 pts
- With color set bonus: +25 = 205 pts theoretical max
- Realistic good team: 30-60 pts
- Great team: 80-120 pts

### Timing
- **Round duration:** 5 minutes
- **No time bonus** — just score as many points as possible

### No Penalties For
- Wrong navigation (just wastes time)
- Failed pickups (just wastes time)
- Time spent in the wrong zone

### Penalties

| Violation | Penalty |
|-----------|---------|
| Robot leaves field boundary | −5 pts |
| Knocking over barrier | −10 pts |
| Manual intervention (touching robot) | −5 pts per touch |
| Block thrown (not placed) in scoring zone | Does not count |

---

## Robot Modes

Teams can use any combination of manual and autonomous control.

| Mode | Description | Competitive Edge |
|------|-------------|-----------------|
| **Full Manual** | Gamepad/web drive everything | Every team can do this on day one |
| **Manual + Auto Pickup** | Drive to block, press button for auto pickup | Faster, more reliable pickup |
| **Manual + Auto Navigate** | Press button to drive to AprilTag automatically | Faster delivery |
| **Full Autonomous** | Robot finds blocks, picks up, delivers by itself | Maximum speed, hardest to build |

**Design principle:** The more you automate, the faster you go. But manual always works as a fallback.

---

## Team Structure

### 7 Teams × 3 Robots = 21 Robots

**Suggested team roles (flexible):**

| Role | Responsibility |
|------|---------------|
| **Driver(s)** | Manual control during competition |
| **Programmer(s)** | Tuning automation, camera calibration |
| **Strategist** | Decides block priorities, zone assignments, transfers |

Teams decide their own structure. Some may have all programmers, others all drivers.

### Robot Roles on Field

| Role | Strategy |
|------|----------|
| **Collector** | Grabs blocks in own zone, delivers to scoring zone |
| **Runner** | Navigates fastest route, focuses on high-value blocks |
| **Transferrer** | Works barrier — lifts blocks over for bonus points |

---

## Event Timeline (6 Hours)

| Time | Activity | Notes |
|------|----------|-------|
| **0:00–1:00** | Assembly + Setup | Build robots, connect, test basic movement |
| **1:00–2:00** | Drive + Sensors | Mecanum drive, sonar, camera basics |
| **2:00–3:00** | Navigation + Arm | AprilTag navigation, arm control, pickup practice |
| **3:00–4:00** | Strategy + Practice | Learn rules, plan strategy, 3 practice rounds |
| **4:00–5:00** | Qualifying | Each team runs 2-3 rounds, best score counts |
| **5:00–6:00** | Finals | Top teams, bracket elimination |

### Round Logistics
- **5 min round + 3 min reset = 8 min per team**
- **Qualifying:** 7 teams × 3 attempts = 21 rounds = ~2.8 hours
- **Finals:** 4 teams × 2-3 rounds = ~40 min

### Field Reset (3 minutes)
- 9 blocks placed on marked positions (tape on floor)
- 3 robots placed at starting positions (one per zone)
- Timer reset
- 2 volunteers can reset in under 3 minutes

---

## Workshop Progression

### What We Provide
- Complete robot framework (Python)
- Web control interface (drive + arm + video)
- AprilTag navigation library
- Block detection (color filtering)
- Example pickup sequence
- Example autonomous routines
- Workshop guides (numbered, progressive)

### What Teams Customize
- Color detection tuning (lighting varies)
- Pickup positions (calibrate for their robot)
- Strategy (which blocks, what order, transfers?)
- Speed/power tuning
- Optional: Custom autonomous routines

### Sample Code Teams Get

```python
# Manual mode with auto-pickup button
robot.drive(gamepad)          # Manual drive
robot.auto_pickup()           # One-button: scan → approach → grab → lift

# Navigate to scoring zone
robot.navigate_to_tag(583)    # Drive to AprilTag 583

# Drop block
robot.arm.drop()              # Open gripper, return to camera-forward

# Full autonomous cycle
robot.auto_cycle()            # Find block → pickup → deliver → repeat
```

---

## Field Construction

### Materials

| Item | Quantity | Est. Cost |
|------|----------|-----------|
| PVC pipes or tape for boundaries | 48 ft | $20-40 |
| Foam board barriers (12" tall) | ~20 ft total | $15-25 |
| Cardboard boxes (obstacles) | 4-6 | $5-10 |
| Printed AprilTags (card stock) | ~20 tags | $5 |
| Wooden/foam blocks (1.2" cubes, 3 colors) | 9+ spares | $10-20 |
| Tape for scoring zones and block positions | 1 roll | $5 |
| **Total** | | **$60-105** |

### AprilTag Placement
- 2 tags per wall (8 total on field boundary)
- 1-2 tags per barrier (navigation reference)
- 1-2 tags per scoring zone (delivery target)
- Total: ~16-20 tags

---

## Open Questions

1. **Transfer mechanic:** Is lifting over a 12" barrier realistic with 1.2" blocks? May need a "transfer slot" or "window" in the barrier instead.

2. **Block visibility:** 1.2" blocks are hard to see. Should we use larger blocks (2-3 inches) for reliability?

3. **Scoring display:** Manual scorekeeping (whiteboard) vs automated (camera watching scoring zone)?

4. **Battery management:** 21 robots × 4-6 battery sets = 84-126 batteries. Charging logistics?

5. **Robot differentiation:** Do all robots run identical code, or can teams modify?

6. **Practice field:** Do teams get a practice field during tutorials, or only the competition field?

7. **Tiebreaker:** If scores are equal, fastest completion time? Or head-to-head round?

---

## Next Steps

### Development
1. Strafe-based navigation (smooth mecanum movement)
2. Camera-down block detection (1.2" blocks on floor)
3. Automated pickup sequence
4. Web interface with mode buttons (manual/auto toggle)
5. Competition scoring display

### Event Planning
1. Finalize field dimensions and barrier design
2. Source blocks (1.2" wood cubes, 3 colors)
3. Print AprilTags
4. Create 1-page rules poster
5. Build practice field
6. Create workshop guides (W1-W7)
7. Battery charging logistics plan

---

*This is a living document. Update as design evolves.*
