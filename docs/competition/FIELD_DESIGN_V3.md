# Competition Field Design V3: "The Optimizer's Dilemma"

## Design Philosophy

The field looks simple. The scoring looks simple. But the **optimal strategy
is a combinatorial puzzle** that rewards AI-assisted analysis.

Human intuition says: "grab blocks, deliver blocks, go fast."
AI analysis reveals: "the ORDER you do things, the ROUTES you take, and
the COMBINATIONS you attempt completely change your ceiling."

The field has **hidden multipliers, decaying bonuses, route-dependent scoring,
and risk/reward zones** that interact in ways too complex to reason about
manually in 45 minutes — but a GenAI can model in 5 minutes.

---

## Field Layout (10 x 10 ft)

```
                          10 ft
    ╔═══════════════════════════════════════╗
    ║                NORTH WALL             ║
    ║       [Tag 578]        [Tag 579]      ║
    ║                                       ║
    ║  ┌─DOCK A─┐  ┌─DOCK B─┐  ┌─DOCK C─┐ ║
    ║  │ 🧺BLUE │  │🧺YELLOW│  │ 🧺RED  │ ║
    ║  │  (578)  │  │ (579)  │  │ (580)  │ ║
    ║  └────╥────┘  └────╥───┘  └───╥────┘ ║
    ║       ║            ║          ║       ║
    ║  ─ ─ ║─ ─SURGE LINE║─ ─ ─ ─ ─║─ ─ ─ ║  (green tape, 7ft)
    ║       ║            ║          ║       ║
    ║   ┌───╨────────────╨──────────╨───┐   ║
    ║   │         CORRIDOR              │   ║
W   ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │   ║  E
E   ║   │  (green tape through center)  │   ║  A
S   ║   └──────┤  14"  ├───────────────┘   ║  S
T   ║  [Tag    │  gap  │         [Tag      ║  T
    ║   584]   │  WEST │          585]     ║
W   ║          ├───────┤                   ║  W
A   ║   ┌──────┤  14"  ├───────────────┐   ║  A
L   ║   │      │  gap  │               │   ║  L
L   ║   │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  │   ║  L
    ║   │  (green tape through center)  │   ║
    ║   │         CORRIDOR              │   ║
    ║   └───╥────────────╥──────────╥───┘   ║
    ║       ║            ║          ║       ║
    ║  ┌─ZONE 1─┐  ┌─ZONE 2─┐  ┌─ZONE 3─┐ ║
    ║  │ 🔴🔴🔴 │  │ 🟡🟡🟡 │  │ 🔵🔵🔵 │ ║
    ║  │ sorted  │  │ sorted  │  │ sorted  │ ║
    ║  └────────┘  └────────┘  └────────┘  ║
    ║                                       ║
    ║  ┌─ST1──┐  ┌──ST2──┐  ┌──ST3──┐     ║
    ║  └──────┘  └───────┘  └──────┘      ║
    ║       [Tag 582]        [Tag 583]      ║
    ║                SOUTH WALL             ║
    ╚═══════════════════════════════════════╝
```

---

## The Twist: Blocks Start Pre-Sorted (Wrong)

Unlike V1/V2, blocks don't start scattered randomly.

**Zone 1 (southwest):** 3 RED blocks
**Zone 2 (south center):** 3 YELLOW blocks
**Zone 3 (southeast):** 3 BLUE blocks

The blocks are pre-sorted BY COLOR into zones — but the **zones don't
match the docks.** This is deliberate. The naive strategy is obvious but wrong.

**Dock A** (northwest) = BLUE basket (Tag 578)
**Dock B** (north center) = YELLOW basket (Tag 579)
**Dock C** (northeast) = RED basket (Tag 580)

So:
- Red blocks are in Zone 1 (far left) → Red dock is Dock C (far right)
- Yellow blocks are in Zone 2 (center) → Yellow dock is Dock B (center) ✓
- Blue blocks are in Zone 3 (far right) → Blue dock is Dock A (far left)

**Red and Blue are CROSS-FIELD deliveries. Only Yellow is straight ahead.**

---

## The Corridor

A foam-cube barrier wall runs EAST-WEST across the middle of the field.
Two passages (14" wide each) allow transit — one on the west side, one on
the east side.

**Green tape lines** run through both passages and connect to a
**Surge Line** (a horizontal green tape line near the docks).

The corridor creates a routing puzzle:
- West passage is closer to Zone 1 (red blocks)
- East passage is closer to Zone 3 (blue blocks)
- Center has NO passage — you must choose a side
- The Surge Line connects both passages near the docks

---

## Scoring Rules

### Base Delivery

| Action | Points |
|--------|--------|
| Block in CORRECT dock | **10** |
| Block in WRONG dock | **2** |
| Block on robot at buzzer | **1** |
| Block on field | **0** |

Base points are intentionally LOW. The real points come from multipliers.

### Time Decay Multiplier (The Clock Pressure)

Every delivery gets a **time multiplier** based on WHEN it's delivered:

| Delivery Window | Multiplier |
|-----------------|------------|
| 0:00 - 2:00 (first 2 min) | **x4** |
| 2:01 - 4:00 | **x3** |
| 4:01 - 6:00 | **x2** |
| 6:01 - 8:00 | **x1.5** |
| 8:01 - 10:00 | **x1** |

A correct delivery in the first 2 minutes = 10 x 4 = **40 pts**.
The same delivery after 8 minutes = 10 x 1 = **10 pts**.

**This means the first 3-4 blocks matter MORE than the last 3-4.**
Speed to first delivery is critical. Human intuition says "get all 9 right."
Math says "get the first 4 fast, even if imperfect."

### Streak Bonus (Consecutive Correct)

Consecutive correct-color deliveries earn escalating bonuses:

| Streak | Bonus |
|--------|-------|
| 2 in a row | +5 |
| 3 in a row | +15 |
| 4 in a row | +30 |
| 5 in a row | +50 |
| 6+ in a row | +50 + 25 per additional |

**A wrong delivery resets the streak to 0.**

This creates a tension: rush to deliver fast (time multiplier) or be
accurate to build streaks? The optimal answer depends on your reliability
rate, which is a MATH problem.

### Automation Tier Bonuses

| Delivery Method | Bonus Per Block |
|-----------------|-----------------|
| Manual (gamepad/keyboard) | +0 |
| Scripted (human triggers) | +3 |
| Semi-auto (human selects target) | +5 |
| Full auto (no human input) | +10 |
| Full auto + vision color ID | +15 |

These bonuses are **also multiplied by the time decay**.
Full auto + vision in the first 2 min = +15 x 4 = +60 bonus on TOP of the
40 pts base. **One perfect early autonomous delivery = 100 pts.**

### Route Bonuses

| Action | Points |
|--------|--------|
| Passage crossing (line follow) | +5 per crossing |
| Surge Line traversal | +3 (follow surge line between docks) |
| Return to start zone | +2 per return |
| Opposite-side passage (enter west, exit east or vice versa) | +8 |

The **opposite-side passage** bonus is key: if you enter the west
passage going north and exit the east passage going south (or vice versa),
you get +8. This requires crossing the entire corridor zone — only
efficient with line following + strafe nav.

### Combo Bonuses (End of Match)

| Achievement | Bonus |
|-------------|-------|
| All 3 of one color correct | +20 per color |
| All 9 correct | +100 |
| Perfect streak (9 consecutive correct) | +150 |
| Full clear in under 5 min | +200 |
| 3+ blocks via multi-block trip | +15 per trip |

### Penalties

| Action | Points |
|--------|--------|
| Robot out of bounds | -10 |
| Human touches robot on field | -5 |
| Knock over barrier cube | -3 |
| Intentional ramming | -15 + 60s removal |
| Block knocked out of dock | -5 (it was scored, now isn't) |

---

## Why Only AI Can Optimize This

### The Combinatorial Problem

With 9 blocks, 3 zones, 2 passages, and time-decaying multipliers,
the number of possible strategies is enormous:

**Decisions per trip:**
- Which zone to visit? (3 choices)
- Which color to grab? (up to 3)
- Which passage to use? (2 choices)
- Which dock to deliver to? (3 choices, but 1 is correct)
- Single or multi-block? (2 choices)
- Speed vs accuracy tradeoff? (continuous)

**That's ~108 possible orderings for 9 blocks**, and the score for each
depends on execution time, reliability rate, streak maintenance, and
route efficiency. No human can evaluate this in 45 minutes.

### The Hidden Optimal Strategy (Spoiler — AI Discovers This)

The obvious strategy: "Grab nearest block, deliver to correct dock, repeat."
This scores ~150-200 pts.

**The AI-discovered strategy:**

1. **Start with YELLOW** (Zone 2, center). Yellow dock is straight ahead
   (Dock B). Shortest path = fastest first delivery = x4 multiplier.
   3 yellows first = 30 x4/x3/x3 = 120 + streak(2nd=5, 3rd=15) = **140 pts**.

2. **Then do BLUE** (Zone 3, east). Blue dock is Dock A (far left).
   Use EAST passage north, deliver, then cross via Surge Line to Dock A.
   Gets opposite-side bonus (+8) on return via west passage.
   3 blues = 30 x2/x2/x2 + streak(4th=30, 5th=50, 6th=50) = **190 pts running**.

3. **Then RED** (Zone 1, west). Red dock is Dock C (far right).
   West passage north, Surge Line east to Dock C.
   3 reds = 30 x1.5/x1/x1 + streak(7th=75, 8th=100, 9th=125) = **330 pts**.
   Plus all-correct (+100) and per-color (+60) = **490 pts**.

4. **With automation bonuses on top:** +15 x multiplier per block.
   Early autos worth +60 each. **Total ceiling: ~800+ pts.**

**Compare to naive "grab nearest, deliver nearest":**
- Breaks streak constantly (wrong colors mixed)
- Misses time multiplier (slow first delivery)
- No route bonuses (random passage usage)
- Score: ~150-200 pts

**The AI insight:** Do all of one color before switching. Start with the
easiest path (yellow = straight ahead). Maintain streak at all costs.
The streak bonus growth is EXPONENTIAL — blocks 7-8-9 are worth more
than blocks 1-5 combined IF the streak is unbroken.

**But there's a counter-strategy the AI also finds:**
If your reliability is <80%, streaks will break. The math says: at 70%
accuracy, you should SKIP color matching entirely, deliver all 9 as fast as
possible to wrong docks (2 pts each x high multipliers), and maximize
automation bonuses instead. This scores ~180 pts vs ~120 for "trying and
failing" at color matching.

**The REAL optimal depends on your measured accuracy rate.** That's a
parameter only testing + analysis can determine.

---

## How Each Skill Enables Points

| Skill | Points Unlocked | Strategic Value |
|-------|----------------|-----------------|
| **Mecanum** | 2 pts/block (bulldoze) | Floor: always available |
| **Arm control** | 10 pts/block (pickup) | 5x better than bulldoze |
| **AprilTag nav** | Correct dock targeting | Enables color match (10 vs 2) |
| **Block detection** | Auto color ID | +15 automation tier |
| **Bump grab** | Reliable pickup | Enables streaks (no misses) |
| **Line following** | Passage crossing | +5/crossing + speed |
| **Strafe nav** | Efficient routing | Time multiplier optimization |
| **Color delivery** | Correct dock selection | Streak building |
| **Bin collect** | Multi-block runs | +15/trip + time savings |
| **Sonar** | Wall avoidance | Fewer penalties (-3 each) |

### The Skill Synergy Map

```
                    ┌─────────────┐
                    │  FULL AUTO  │  +15/block
                    │  + VISION   │  x time multiplier
                    └──────┬──────┘
                           │ requires ALL of:
              ┌────────────┼────────────┐
              v            v            v
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │  Block   │ │  Bump    │ │  Color   │
        │  Detect  │ │  Grab    │ │ Delivery │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
        ┌────v─────┐ ┌────v─────┐ ┌────v─────┐
        │  Camera  │ │   Arm    │ │ AprilTag │
        │  Vision  │ │ Control  │ │   Nav    │
        └────┬─────┘ └────┬─────┘ └────┬─────┘
             │            │            │
             └────────────┼────────────┘
                          v
                   ┌──────────────┐
                   │ Mecanum Drive│
                   │   (base)     │
                   └──────────────┘
```

Each layer unlocks exponentially more points. Drive alone = 2/block.
Add arm = 10/block. Add nav = correct dock. Add vision = auto bonus.
Add speed = time multiplier. **The stack is multiplicative, not additive.**

---

## Match Flow Example (Optimal Play)

```
TIME   ACTION                              PTS  RUNNING
0:00   Start in ST2. Drive north to Zone 2.
0:15   Bump grab YELLOW #1.                         0
0:35   Line follow through west passage.    +5      5
0:50   Strafe to Dock B (Tag 579).
0:55   Drop yellow in yellow dock.          40     45   (10 x4 multiplier)
       Auto+vision bonus.                  +60    105   (15 x4)
1:10   Return south through east passage.   +8    113   (opposite side!)
1:15   Surge line traversal.                +3    116
1:25   Bump grab YELLOW #2.
1:45   West passage north.                  +5    121
1:55   Dock B delivery.                     30    151   (10 x3) + streak 2 (+5)
       Auto+vision.                        +45    196
2:10   East passage south.                  +8    204
2:25   Bump grab YELLOW #3.
2:50   West passage north.                  +5    209
3:00   Dock B delivery.                     30    239   (10 x3) + streak 3 (+15)
       Auto+vision.                        +45    284
       All yellow correct!                 +20    304
...
       (continue with blue, then red)
...
10:00  BUZZER
       All 9 correct: +100
       9 consecutive: +150
       Per-color complete: +60 (3x20)
       THEORETICAL MAX: ~800+
```

---

## Judging: How to Track Time Multipliers

**Simple method:** Timer calls out windows.
- Buzzer/bell at 2:00, 4:00, 6:00, 8:00
- Scorekeeper notes which window each delivery happens in
- Multiply at end

**Scoring sheet has columns:**

| Block # | Color | Dock | Correct? | Window | Multi | Base | Auto | Route | Total |
|---------|-------|------|----------|--------|-------|------|------|-------|-------|
| 1 | Yellow | B | Yes | 0-2 | x4 | 40 | 60 | 5 | 105 |
| 2 | Yellow | B | Yes | 0-2 | x4 | 40 | 45 | 8 | 93 |
| ... | | | | | | | | | |

Streak tracking: simple tally marks. Reset on wrong delivery.

---

## Field Construction

Same materials as V2 plus:

| Item | Change from V2 |
|------|----------------|
| Barrier wall | Now runs EAST-WEST with 2 passages (west + east) |
| Green tape | 2 passage lines + 1 surge line (near docks) |
| Block zones | 3 marked zones (tape squares) in south half |
| Express platform | REMOVED (complexity is in scoring, not terrain) |
| Timer/bell | Need audible markers at 2 min intervals |

**Total field cost:** ~$130-150 (same as V2)

---

## Why This Design Works for the Workshop

### For Students Who Don't Code
- Manual driving still scores (2 pts/block)
- Time multiplier rewards hustle
- Can improve between rounds by trying scripts

### For Students Who Script a Little
- Even basic "drive to tag X" automation gets +3/block
- Line following through passage = free +5 per trip
- Score jumps from ~30 to ~100+ with minimal code

### For Students Using GenAI to Analyze Strategy
- "Here are the scoring rules. What's the optimal block order?"
- GenAI immediately identifies: yellow first, maintain streaks, time pressure
- This is the +10 GenAI bonus AND the actual winning strategy
- **Using AI to think, not just to code**

### For Advanced Students
- Full autonomy + vision + streak maintenance
- Multi-block optimization (bin_collect 3 yellows in one trip?)
- Route optimization (which passage, surge line usage)
- Reliability math (is color matching worth the streak risk?)

**The field teaches that AI isn't just for writing code —
it's for making decisions that are too complex for intuition alone.**
