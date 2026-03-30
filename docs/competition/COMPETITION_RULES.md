# PathfinderV2 Competition Rules

## "Supply Chain Scramble" 🏭

### The Story

**Year 2035. The last mile went autonomous.**

Your company just won a contract to run the new automated sorting facility at the regional distribution center. Problem: you have 6 hours to get your fleet operational before the first shipment arrives.

**The facility:**
- A 10×10 foot warehouse floor
- Three color-coded shipping containers along the loading dock
- Navigation beacons on every wall
- Narrow aisles between shelving
- One main conveyor corridor

**The shipment:**
- 9 packages in three categories:
  - 🔴 **Red** = Priority Express
  - 🟡 **Yellow** = Standard Delivery
  - 🔵 **Blue** = Economy

**Your job:** Sort every package into the correct shipping container. Priority Express to red. Standard to yellow. Economy to blue. Wrong container? The customer gets the wrong order. That costs you.

**The catch:** You're not alone. Six other logistics companies share the same warehouse floor. Same packages. Same containers. First come, first served. Only 3 robots can operate at a time — manage your fleet wisely.

**Your advantage:** You have an AI partner. Use it to write sorting algorithms, optimize routes, and debug your fleet in real-time. The companies that leverage AI effectively will sort faster, smarter, and win the contract.

**The clock is ticking. The shipment arrives in 10 minutes.**

*Sort it. Ship it. Score it.*

---

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

## Structure

### Participants
- **147 participants** total
- **49 teams** of 3 people (randomly assigned)
- **7 houses** of 7 teams each

### What's a Team?
- **3 people** + **1 robot** + **1 Pi 500**
- Your team builds, programs, and operates your robot
- All 3 members work together — no rigid roles

### What's a House?
- **7 teams** competing together on **one field**
- Each house has its own competition field + practice field
- **3 robots on the field** at a time (from any 3 teams in the house)
- **4 robots in the pit** (charging, coding, modifying)
- Teams tag-team swap robots on and off the field

### Roles (Flexible Within Team)
Teams of 3 self-organize:
- **Builder/Modifier** — Robot assembly, physical modifications
- **Coder** — Writing/modifying scripts on Pi 500
- **Operator/Strategist** — Driving, deciding what to target
- (In practice, everyone does everything)

---

## Match Format

### Match Duration
- **10 minutes** per match

### Robots on Field
- **Maximum 3 robots** on field at any time (from any teams in the house)
- Remaining robots stay in the **pit area** (charging, coding, modifying)
- Any team can have their robot on the field — first come, first served

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

### Strategy Is Up to You

There are many ways to score points. Some require code. Some require building. Some require both. Some require neither.

Read the scoring table carefully. Think about:
- What scores the most points?
- What can your team do in 10 minutes?
- How do 3 robots work together?
- When should you swap a robot?
- Is it better to deliver fast or deliver accurately?
- What role does the passage play?

**Tip:** Use GenAI to analyze the scoring rules and help develop your strategy.

---

## Rules of Play

### General
1. Match starts and ends on the buzzer
2. All scoring is **end-of-match** (no live scoring needed)
3. Teams operate from their Pi 500 stations (not on the field)
4. Robots may be controlled by any legal method
5. Multiple team members can operate different robots simultaneously

### Robot Modifications
1. Teams are **encouraged** to modify their robots
2. Materials provided: tape, cardboard, zip ties, rubber bands, foam board
3. How you use them is up to you
4. Constraints:
   - Must fit within 12" × 12" × 12" (including modifications)
   - No sharp edges or projectiles
   - Must not damage the field or other robots
   - Must still fit in start zone

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

Robot assembly takes ~2 hours. GenAI compresses everything else so teams maximize competition time. No formal lectures — learn by doing.

**Pre-work (facilitator):** SD cards pre-imaged, WiFi configured, batteries charged.

### Phase 1: Build (2 hours)

| Time | Group A (3-4 people) | Group B (2-3 people) |
|------|---------------------|---------------------|
| 0:00-0:15 | Welcome, team formation, hand out rules | Same |
| 0:15-2:00 | **Robot assembly** (B1 guide) | **Pi 500 setup** + study rules with GenAI |
| | Follow assembly instructions | "Analyze these rules — what's our strategy?" |
| | Mechanical build, wiring, servos | Set up SSH, explore repo, run demos |

**While building:** Group B uses GenAI to understand rules, plan strategy, and start writing code. By the time the robot is assembled, they have a plan.

### Phase 2: Connect + Explore (45 min)

| Time | Activity | GenAI Role |
|------|----------|-----------|
| 2:00-2:15 | Connect Pi 500 to robot (SSH, battery check) | "Why won't SSH connect?" |
| 2:15-2:45 | Explore robot skills — run demos, test hardware | "Explain this script" / "Make it faster" |

Teams run through START_HERE.md skills at their own pace. Fast teams jump ahead to autonomous scripts. Slower teams focus on manual control.

### Phase 3: Prepare to Compete (45 min)

| Time | Activity | GenAI Role |
|------|----------|-----------|
| 2:45-3:00 | **Robot modifications** (storage bin, funnel, bumper) | "Design a V-funnel for block pickup" |
| 3:00-3:15 | **Strategy + code customization** | "Write a script to sort red blocks to tag 580" |
| 3:15-3:30 | **Practice match** (10 min, informal, test the field) | "My robot missed the block — debug this" |

### Phase 4: Competition! (2 hours)

| Time | Activity |
|------|----------|
| 3:30-3:45 | Break + final strategy |
| 3:45-4:15 | **QUALIFYING ROUND 1** (10 min match) |
| 4:15-4:45 | Score + code iteration + mods + battery swap |
| 4:45-5:15 | **QUALIFYING ROUND 2 / FINALS** (10 min match) |
| 5:15-5:45 | Final scoring, awards ceremony |
| 5:45-6:00 | Debrief + cleanup |

### GenAI Throughout

**GenAI isn't a bonus — it's how teams keep pace.** In 6 hours, there's no time to learn Python from scratch. Teams that prompt well:
- Understand rules faster (strategy from minute 1)
- Write code faster (scripts generated, not hand-coded)
- Debug faster ("why does my robot drift right?")
- Iterate between rounds ("optimize for speed, not accuracy")

**Teams that don't use GenAI** will spend most of their time on manual control. That's fine — bulldozing still scores points. But autonomous deliveries (+10 pts each) require code, and code requires either experience or a good AI partner.

---

*Supply Chain Scramble: Sort it. Ship it. Score it.* 🏭🤖🏆
