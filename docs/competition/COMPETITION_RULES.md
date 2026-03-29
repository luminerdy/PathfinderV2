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
    │                         │
    │   🧺B  🧺Y  🧺R        │  DELIVERY ZONE
    │   578   579   580       │  Colored baskets under AprilTags
    │                         │
    │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
    │                         │
    │  ╔═══╗     ┌────┐       │
    │  ║   ║     │    │       │  BARRIERS + PASSAGE
10  │  ║   ║ ▓▓▓ │    │       │  Green tape through narrow gap
ft  │  ╚═══╝     └────┘       │
    │                         │
    │─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│
    │                         │
    │   🔴 🟡 🔵  🔴 🟡 🔵   │  BLOCK ZONE
    │      🔴 🟡  🔵         │  9 blocks (3 per color)
    │                         │
    │  ┌─────┐┌─────┐┌─────┐ │  START ZONES
    │  │ ST1 ││ ST2 ││ ST3 │ │  One per active robot
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

| Action | Points |
|--------|--------|
| Block in **any** basket | 5 pts |
| Block in **correct color** basket | 15 pts (5 base + 10 color bonus) |
| Block **stored on robot** at buzzer | 2 pts |
| Block in **wrong color** basket | 3 pts |
| Block on field (not delivered) | 0 pts |

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

---

## Rules of Play

### General
1. Match starts and ends on the buzzer
2. All scoring is **end-of-match** (no live scoring needed)
3. Teams operate from their Pi 500 stations (not on the field)
4. Robots may be controlled by any legal method
5. Multiple team members can operate different robots simultaneously

### Robot Rules
1. Robots must start in a start zone
2. Robots must fit within the start zone at match start
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

## Schedule

### Workshop Day 1 (6 hours)
| Time | Activity |
|------|----------|
| 0:00-0:30 | Welcome, team formation, overview |
| 0:30-1:30 | Robot assembly + Pi 500 setup (parallel) |
| 1:30-2:00 | Connect and test (SSH, battery, motors) |
| 2:00-3:00 | Core skills (D1-D4: drive, sonar, arm, camera) |
| 3:00-3:15 | Break |
| 3:15-4:15 | Integration skills (E2-E6: navigation, detection, pickup, line follow) |
| 4:15-5:00 | Strategy planning + code customization |
| 5:00-6:00 | Practice matches (informal, test the field) |

### Workshop Day 2 (6 hours)
| Time | Activity |
|------|----------|
| 0:00-0:30 | Recap, final prep, battery check |
| 0:30-1:30 | Code refinement + robot modifications |
| 1:30-2:00 | Qualifying Round 1 (10 min per team) |
| 2:00-2:30 | Qualifying Round 2 |
| 2:30-2:45 | Break + scores announced |
| 2:45-3:30 | Semi-finals |
| 3:30-4:00 | Code iteration + strategy adjustment |
| 4:00-4:45 | FINALS |
| 4:45-5:15 | Awards + debrief |
| 5:15-6:00 | Open play + cleanup |

---

*Supply Chain Scramble: Sort it. Ship it. Score it.* 🏭🤖🏆
