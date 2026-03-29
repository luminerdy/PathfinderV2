# PathfinderV2 Competition Rules

## "Supply Chain Scramble" 🏭

Your team runs a logistics operation. Colored packages (blocks) must be sorted and delivered to the correct shipping containers (baskets). Navigate obstacles, manage your robot fleet, and outscore the competition.

---

## The Field

### Dimensions
- **10 × 10 feet** (foam tile floor)
- Bordered by walls on all sides

### Layout

```
              10 ft
    ┌─────────────────────────┐
    │  ╔═══════════════════╗  │
    │  ║  SCORING AREA     ║  │  Judges count blocks here
    │  ║  🧺B  🧺Y  🧺R   ║  │  at end of match
    │  ║  578   579   580  ║  │  Colored baskets under AprilTags
    │  ╚═══════════════════╝  │
    │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
    │                         │
    │  ╔═══╗     ┌────┐       │
    │  ║   ║     │    │       │  BARRIERS + PASSAGE
10  │  ║   ║ ▓▓▓ │    │       │  Green tape through narrow gap
ft  │  ╚═══╝     └────┘       │  (~14" wide)
    │                         │
    │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
    │                         │
    │   🔴 🟡 🔵  🔴 🟡 🔵   │  BLOCK ZONE
    │      🔴 🟡  🔵         │  9 blocks (3 per color)
    │                         │  scattered randomly
    │  ┌─────┐┌─────┐┌─────┐ │  START / SWAP ZONES
    │  │ ST1 ││ ST2 ││ ST3 │ │  Robots enter/exit here
    └──┴─────┴┴─────┴┴─────┴──┘

    SOUTH WALL (Tags 582, 583)
```

### Field Elements

| Element | Description |
|---------|-------------|
| **AprilTags** | 8 tags (tag36h11), 2 per wall, 10"×10" printed |
| **Baskets** | 3 colored shopping baskets (red, yellow, blue) along north wall |
| **Blocks** | 9 blocks total: 3 red, 3 yellow, 3 blue (~1.2" cubes) |
| **Barriers** | 2-3 obstacles, 4-8" thick, 12-18" tall (below AprilTag height) |
| **Passage** | Narrow gap (~14" wide) with green tape line through it |
| **Start Zones** | 3 marked zones along south wall (one per active robot) |

### Barrier Rules
- Barriers **do not block** line of sight to AprilTags (kept below tag height)
- Some barriers are **fixed** (heavy — cannot be moved)
- Some barriers are **pushable** (lightweight — robot can bulldoze through)
- Knocking over a barrier = -2 points

---

## Teams

### Team Size
- **6-7 members** per team
- **6-7 robots** per team

### Roles (Flexible)
Teams self-organize. Common roles:
- **Pit Crew** — Battery swaps, robot modifications, charging
- **Coders** — Writing/modifying scripts on Pi 500
- **Operators** — Running robots from Pi 500 via SSH
- **Strategist** — Deciding which blocks to target, when to swap

---

## Match Format

### Match Duration
- **10 minutes** per match

### Robots on Field
- **Maximum 3 robots** on field per team at any time
- Remaining robots stay in the **pit area** (off-field)

### Match Flow

```
0:00   START — Up to 3 robots enter from start zones
       Teams command robots from Pi 500s via SSH
       Robots collect blocks, navigate field, deliver to baskets

5:00   MID-MATCH — Optional strategy adjustment
       Battery swaps, code changes in pit

10:00  STOP — All robots stop immediately
       Blocks scored where they are
       Robots carrying blocks: block scores as "stored on robot"
```

---

## Robot Operations

### Control Methods (All Legal)
Teams choose how to control their robots:

| Method | Description | Bonus |
|--------|-------------|-------|
| **Manual SSH** | Type commands in terminal | None |
| **Web interface** | Drive with browser controls | None |
| **Scripted** | Run pre-written Python scripts | None |
| **Semi-autonomous** | Scripts with human oversight | None |
| **Fully autonomous** | Robot runs independently | +10 pts per autonomous delivery |

### Tag-Team Robot Swaps

- Robot must be in **start zone** to swap
- Drive robot to start zone → physically pick up → place fresh robot
- **No limit** on number of swaps
- If robot was carrying a block, block **drops at swap point**
- Robots in the pit can be:
  - Charging batteries
  - Getting code updates
  - Being physically modified
  - Waiting as backup

### Battery Management
- Robots use 2× 18650 batteries (30-45 min runtime)
- Teams manage their own battery supply
- Dead robot on field? Drive it to start zone and swap, or pick it up (-3 pts)

---

## Scoring

### Block Delivery (Scored at End of Match)

Blocks are counted in the **Scoring Area** — the baskets along the north wall.

| Action | Points |
|--------|--------|
| Block in **correct color** basket | 15 pts (5 base + 10 color bonus) |
| Block in **any** basket (wrong color) | 3 pts |
| Block **stored on robot** at buzzer | 2 pts per block on robot |
| Block **in robot's storage bin** at buzzer | 2 pts per block |
| Block on field (not delivered) | 0 pts |

**Counting method:** At the buzzer, judges count blocks in each basket by color. Blocks on robots (in gripper or storage bin) count as "stored." Simple — no live scoring technology needed.

### Navigation Points

| Action | Points |
|--------|--------|
| Robot crosses through the passage | 3 pts (per crossing, max 6) |
| Robot returns to start zone after delivery | 3 pts (per return) |

### Bonus Points

| Action | Points |
|--------|--------|
| **Fully autonomous** delivery (no human input) | +10 pts per block |
| **All 9 blocks** sorted to correct baskets | +30 pts team bonus |
| **GenAI-assisted** code that works in match | +10 pts team bonus |
| **Creative robot modification** (judge's choice) | +5 to +15 pts |
| **Pushed basket** to strategic location | +5 pts |

### Penalties

| Action | Points |
|--------|--------|
| Robot leaves field boundary | -5 pts |
| Human touches robot on field (not in start zone) | -3 pts per touch |
| More than 3 robots on field simultaneously | -10 pts, immediately remove one |
| Intentional ramming of another team's robot | -10 pts, robot removed for 60 sec |
| Knocking over a barrier | -2 pts |

### Score Summary

**Maximum theoretical:** ~295 pts
- 9 blocks × 15 pts = 135
- All correct bonus = 30
- 9 autonomous deliveries × 10 = 90
- Passage crossings = 18
- Returns to start = 27
- GenAI bonus = 10

**Realistic competitive score:** 60-120 pts

---

## Strategies

### Beginner: "The Bulldozer"
- Just push blocks toward baskets
- No arm skill needed
- 5 pts per block (any basket)
- Easy but slow and imprecise

### Intermediate: "Pick and Place"
- Use arm to grab blocks
- Carry to any nearby basket
- 5-15 pts per block depending on color match
- Needs arm calibration

### Advanced: "Color Sorter"
- Identify block color before picking up
- Navigate to matching basket via AprilTag
- 15 pts per block + possible full sort bonus
- Needs vision + navigation + arm integration

### Advanced+: "The Hoarder"
- Modify robot with storage bin on back
- Pick up 2-3 blocks per trip (load onto back)
- One delivery trip drops all blocks at once
- Fewer trips = more time for collecting
- Needs creative arm sequencing (pick up → load to back → repeat)

### Expert: "Full Auto Fleet"
- Autonomous robots running scripts
- Tag-team swaps for battery management
- Multiple robots operating simultaneously
- +10 pts per autonomous delivery
- Maximum possible score

### Meta: "The Passage Master"
- Control the narrow passage
- Line follow through quickly while others go around
- Block opponents (carefully — no ramming)
- Extra navigation points

### Meta: "The Specialist Fleet"
- Robot 1: "Bulldozer" — pushes blocks to baskets (no arm needed)
- Robot 2: "Precision" — picks up and color-sorts
- Robot 3: "Storage" — back bin, collects multiple blocks per trip
- Different modifications on different robots!

---

## Rules of Play

### General
1. Match starts and ends on the buzzer
2. All scoring is **end-of-match** (no live scoring needed)
3. Teams operate from their Pi 500 stations (not on the field)
4. Robots may be controlled by any legal method
5. Multiple team members can operate different robots simultaneously

### Robot Modifications
1. Teams are **encouraged** to modify their robots!
2. Approved modifications:
   - **Storage bin** on back (carry multiple blocks per trip)
   - **Bumper/scoop** on front (better bulldozing)
   - **Block guide rails** (help align blocks for pickup)
   - **Flag/marker** (team identification)
3. Materials provided: tape, cardboard, zip ties, rubber bands, 3D printed parts
4. Modifications must not:
   - Exceed 12" × 12" × 12" total robot size
   - Include projectiles or sharp edges
   - Damage the field or other robots

**Storage strategy:** A robot with a back bin can pick up 2-3 blocks before making one delivery trip — fewer trips = more time!

### Robot Rules
1. Robots must start in a start zone
2. Robots must fit within the start zone at match start (including modifications)
3. No weapons, no intentional damage to other robots or field
4. Robots may push moveable barriers and blocks
5. Robots may NOT push other teams' robots intentionally

### Human Interaction
1. Humans may **not enter the field** during a match
2. Exception: robot swap in start zone (reach in to swap)
3. Any other touch of a robot on field = -3 pts penalty
4. Programming/commanding from Pi 500 is unlimited

### Tie Breaking
1. First tiebreaker: Most correctly color-sorted blocks
2. Second tiebreaker: Most autonomous deliveries
3. Third tiebreaker: Fewest penalties

---

## Field Setup Checklist

### Before Each Match
- [ ] 9 blocks placed in block zone (3 red, 3 yellow, 3 blue)
- [ ] Blocks randomly scattered (not in neat rows)
- [ ] 3 baskets in position along north wall
- [ ] Barriers in standard positions
- [ ] Green tape intact through passage
- [ ] All 8 AprilTags visible and undamaged
- [ ] Start zones clearly marked
- [ ] Timer ready (10 minutes)

### Equipment Per Team
- [ ] 6-7 assembled robots with batteries
- [ ] 6-7 charged battery sets (plus spares)
- [ ] 1-2 Pi 500 stations with monitors
- [ ] WiFi connectivity verified
- [ ] SSH access to all robots tested

---

## Judging

### Judges Needed
- **1 Head Judge** — Final scoring decisions, bonus points
- **1 Field Judge** — Watches for penalties, robot-out-of-bounds
- **1 Scorekeeper** — Tallies points after each match

### After Each Match
1. All robots stop
2. Field judge notes any robots carrying blocks
3. Scorekeeper counts:
   - Blocks in each basket (by color)
   - Blocks on robots
   - Passage crossings observed
   - Penalties observed
4. Head judge awards bonus points
5. Score announced

---

## GenAI Usage

### Encouraged!
Teams are encouraged to use GenAI tools (ChatGPT, Claude, Copilot, etc.) during the workshop and competition.

### How to Earn GenAI Bonus
1. Show the GenAI conversation/prompts used
2. The generated code must **actually run** during the match
3. Explain what the code does (understanding, not just copy-paste)
4. Judges award up to 10 pts for effective GenAI use

### Examples
- "Write a Python script to navigate from AprilTag 582 to 578"
- "Modify block detection to prioritize red blocks"
- "Optimize line following speed for the passage"
- "Create a strategy that avoids the passage entirely"

---

## Schedule (6 Hours)

GenAI is the force multiplier. Teams don't need to learn Python from scratch — they ask AI to write scripts, explain code, and debug issues. This compresses learning so more time goes to competing.

| Time | Activity | GenAI Role |
|------|----------|-----------|
| 0:00-0:15 | Welcome, teams, rules overview | "Analyze these rules, what's the best strategy?" |
| 0:15-1:00 | Robot assembly + Pi 500 setup (parallel) | — |
| 1:00-1:20 | Connect and test (SSH, battery, motors) | "Why won't my robot connect?" |
| 1:20-2:00 | Explore skills (D1-D4: drive, sonar, arm, camera) | "Explain what this script does" |
| 2:00-2:15 | Break | |
| 2:15-2:45 | Integration skills (navigation, detection, pickup) | "Write a script to pick up red blocks" |
| 2:45-3:15 | Strategy + robot modifications + code customization | "Design a storage bin for 3 blocks" |
| 3:15-3:45 | Practice match (10 min, informal) | "My robot drifts right, how do I fix it?" |
| 3:45-4:00 | Break + strategy revision | |
| 4:00-4:30 | **QUALIFYING ROUND** (10 min match) | |
| 4:30-5:00 | Code iteration + battery swap + modifications | "Optimize my delivery route" |
| 5:00-5:30 | **FINALS** (10 min match) | |
| 5:30-6:00 | Scoring, awards, debrief | |

**Key insight:** Teams that use GenAI effectively will iterate faster, debug quicker, and have more polished autonomous routines by competition time.

---

*Supply Chain Scramble: Sort it. Ship it. Score it.* 🏭🤖🏆
