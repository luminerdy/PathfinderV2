# Competition Field Design V2

## "Supply Chain Scramble" — Final Field

### Design Philosophy

The field rewards **three tiers** of capability:
1. **Manual driving** — anyone can score some points (accessible)
2. **Smart scripting** — targeted automation multiplies points (rewarding)
3. **Full autonomy** — the only way to reach the top scores (aspirational)

Every Buddy capability has a scoring path. The field is designed so that
**doing things the hard way** (automation) is always worth more than the
easy way (driving), but the easy way still keeps you in the game.

---

## Field Layout (10 x 10 ft)

```
                        10 ft (3.05m)
  ══════════════════════════════════════════
  ║                 NORTH WALL              ║
  ║    [Tag 578]              [Tag 579]     ║
  ║                                         ║
  ║  ┌──────────────────────────────────┐   ║
  ║  │         DELIVERY DOCK            │   ║
  ║  │   🧺BLUE    🧺YELLOW    🧺RED   │   ║
  ║  │   (578)      (579)      (580)    │   ║
  ║  └──────────────────────────────────┘   ║
  ║                                         ║
  ║         ┌───────────────┐               ║
  ║         │  EXPRESS LANE │               ║
  ║         │  ▓▓▓▓▓▓▓▓▓▓▓ │  Green tape   ║
W ║         │  (follows S)  │  path with    ║ E
E ║         └───┤       ├───┘  one curve    ║ A
S ║             │       │                   ║ S
T ║   [Tag      │ 14"   │       [Tag        ║ T
  ║    584]     │ gap    │        585]       ║
W ║             │       │                   ║ W
A ║         ┌───┤       ├───┐               ║ A
L ║         │  FIXED BARRIER│               ║ L
L ║         │   (12" tall)  │               ║ L
  ║         └───────────────┘               ║
  ║                                         ║
  ║  ┌──────────────────────────────────┐   ║
  ║  │         WAREHOUSE FLOOR          │   ║
  ║  │                                  │   ║
  ║  │  🔴  🟡     🔵         🔴       │   ║
  ║  │       🔵  🟡    🔴              │   ║
  ║  │  🟡         🔵       EXPRESS     │   ║
  ║  │            ↗ PICKUP              │   ║
  ║  │   [Tag 580]  ZONE    [Tag 581]  │   ║
  ║  └──────────────────────────────────┘   ║
  ║                                         ║
  ║  ┌─ST1──┐  ┌─ST2──┐  ┌─ST3──┐         ║
  ║  │      │  │      │  │      │         ║
  ║  └──────┘  └──────┘  └──────┘         ║
  ║    [Tag 582]              [Tag 583]     ║
  ║                 SOUTH WALL              ║
  ══════════════════════════════════════════
```

---

## Zones

### 1. Warehouse Floor (South Half)
**What:** 9 blocks scattered randomly (3 red, 3 yellow, 3 blue)
**Plus:** 3 EXPRESS blocks in the Express Pickup Zone (see below)
**Purpose:** The supply. All blocks start here.

### 2. The Barrier Wall (Center)
A fixed barrier runs across the middle of the field with ONE passage through it.
- Barrier: 5" foam cubes, 2 high (10"), ~5 ft wide total
- Passage gap: 14" wide (robot is ~10")
- **Green tape line** runs through the passage and curves toward delivery dock

**Why it matters:**
- Manual drivers must thread a 14" gap — slow, careful, nerve-racking
- Line follower skill handles it automatically — fast, reliable
- Going AROUND the barrier means a long detour along the walls
- Tags 584/585 on east/west walls provide nav reference for the detour

### 3. Delivery Dock (North)
**Three colored baskets** under AprilTags along the north wall.
- Tag 578 = Blue basket (left)
- Tag 579 = Yellow basket (center)
- Tag 580 = Red basket (right)

Baskets are open-top, touching the wall. Robot drives up, lowers arm, drops.

### 4. Start / Swap Zones (South Wall)
Three 18"x18" zones. Robots enter/exit here. Battery swaps happen here.

### 5. Express Pickup Zone (NEW)
A marked area near Tag 581 (southeast corner) with **3 bonus EXPRESS blocks**
(marked with a dot or tape band — any color).
- These blocks are placed on a **4" raised platform** (foam block stack or small box)
- Robot must reach UP slightly to grab — tests arm precision
- Worth double points (see scoring)

---

## AprilTag Placement

| Location | Tag IDs | Height | Purpose |
|----------|---------|--------|---------|
| North wall | 578, 579 | 12" | Basket navigation (delivery targets) |
| East wall | 580, 581 | 12" | Detour nav + Express zone reference |
| South wall | 582, 583 | 12" | Start/home reference |
| West wall | 584, 585 | 12" | Detour nav reference |

Tags mounted at 12" center height — visible from anywhere on field when
standing above barrier height. Barrier is 10" tall, tags at 12" = always visible.

---

## Scoring (Revised for V2)

### Block Delivery

| Action | Points | Notes |
|--------|--------|-------|
| Block in CORRECT basket | **15** | Color match via vision |
| Block in ANY basket (wrong) | **3** | Bulldoze strategy works |
| Block on robot at buzzer | **2** | Partial credit |
| Block on field | **0** | |

### Express Blocks (elevated platform)

| Action | Points | Notes |
|--------|--------|-------|
| Express block in CORRECT basket | **25** | 15 base + 10 express bonus |
| Express block in ANY basket | **8** | 3 base + 5 express bonus |

### Navigation Bonuses

| Action | Points | Max |
|--------|--------|-----|
| Passage crossing (through barrier) | **3** | 6 (2 crossings) |
| Return to start zone after delivery | **3** | 27 (9 returns) |

### Automation Bonuses

| Action | Points | Notes |
|--------|--------|-------|
| **Autonomous delivery** (no human input) | **+10** per block | Must be hands-off from pickup to basket |
| **Autonomous color sort** | **+5** per block | Robot identifies color AND picks correct basket |
| **All 9 standard blocks sorted correctly** | **+30** | Team bonus |
| **Express block autonomous delivery** | **+15** per block | Stacks with express bonus |
| **Full warehouse clear** (all 12 blocks delivered) | **+50** | Only possible with express blocks |

### Strategy Bonuses

| Action | Points | Notes |
|--------|--------|-------|
| GenAI-assisted code that runs in match | **+10** | Show prompts, explain code |
| Creative robot modification | **+5 to +15** | Judge's choice |
| Multi-block run (2+ blocks per trip) | **+5** per trip | bin_collect or cart_push |

### Penalties

| Action | Points |
|--------|--------|
| Robot leaves field | **-5** |
| Human touches robot on field | **-3** |
| Too many robots on field (>3) | **-10** |
| Intentional ramming | **-10** + 60s removal |
| Knock over barrier section | **-2** |

---

## Score Analysis: Why Automation Wins

### Strategy A: Pure Manual (gamepad driving)
- Drive to block, bulldoze to nearest basket
- ~90 seconds per block (navigate gap manually, imprecise delivery)
- **6 blocks in 10 min** (realistic, no color matching)
- Score: 6 x 3 = **18 pts**

### Strategy B: Scripted Navigation
- Script drives to tag, human triggers pickup
- Use line follower through passage (faster than manual)
- Some color matching via preset baskets
- **7 blocks in 10 min**, 4 correct color
- Score: 4x15 + 3x3 + passage(6) = **75 pts**

### Strategy C: Semi-Autonomous
- bump_grab picks blocks, strafe_nav delivers, human selects targets
- Color detection chooses basket automatically
- **8 blocks in 10 min**, 6 correct, 4 autonomous
- Score: 6x15 + 2x3 + 4x10(auto) + 4x5(color) + passage(6) = **142 pts**

### Strategy D: Full Autonomous + Express
- Robot runs independently: scan, detect, grab, navigate, sort, deliver
- Handles express blocks (elevated pickup)
- Multi-block runs with bin_collect
- **All 12 blocks in 10 min**, all correct
- Score: 9x15 + 3x25 + 30(all sorted) + 12x10(auto) + 12x5(color sort) + 50(full clear) + 5(multi-block) = **440 pts**

**The gap:** Manual tops out around 18-40 pts. Full auto reaches 400+.
But here's the key — **Strategy B (75 pts) is achievable in 45 minutes of coding with GenAI help.** That's the sweet spot. Students see that a little automation goes a LONG way.

---

## How Each Buddy Skill Maps to Points

| Skill | What It Unlocks | Points Enabled |
|-------|----------------|----------------|
| **Mecanum drive** (D1) | Manual block pushing | 3 pts/block (bulldoze) |
| **Sonar** (D2) | Wall avoidance, safe passage | Fewer penalties |
| **Arm control** (D3) | Block pickup/place | 15 pts/block (vs 3 bulldoze) |
| **Camera** (D4) | Block detection, color ID | +5 color sort bonus |
| **AprilTag nav** (E2) | Targeted basket delivery | 15 pts correct basket |
| **Block detection** (E3) | Find blocks automatically | Enables autonomy |
| **Bump grab** (E5) | Reliable pickup | Enables autonomous delivery |
| **Line following** (E6) | Fast passage crossing | +3 per crossing, speed |
| **Color delivery** | Block to correct basket | 15 pts + 5 auto-sort |
| **Strafe nav** | Navigate to any tag | Efficient pathing |
| **Bin collect** | Multi-block per trip | +5 multi-block bonus |
| **Cart push** | Push loaded cart to basket | Creative modification bonus |
| **Full competition** (E7) | End-to-end cycle | +10 per autonomous delivery |

**Every skill we built has a direct scoring path.** Nothing is wasted.

---

## Field Construction

### Materials

| Item | Qty | Source | Est Cost |
|------|-----|--------|----------|
| Black foam tiles (2'x2') | 25 | Amazon/Harbor Freight | $40-60 |
| Black 5" foam cubes | 200 | Amazon (craft foam) | $50-80 |
| Baskets (red, yellow, blue) | 3 | Dollar store | $9 |
| Wood/plastic blocks (1.2") | 12 | Craft store, Amazon | $10 |
| Express platform (4" riser) | 1 | Foam block stack or small box | $5 |
| Lime green tape | 1 roll | Amazon (neon masking tape) | $6 |
| AprilTags (printed) | 8 | Self-print, laminate | $5 |
| Tape (mounting) | 2 rolls | Any | $5 |
| **Total per field** | | | **~$130-170** |

### Barrier Wall Construction

The barrier is the key field feature. Built from 5" foam cubes:
- **Bottom row:** ~12 cubes across (5 ft), with a 14" gap in the middle
- **Top row:** Same pattern, stacked on bottom row
- **Total height:** 10" (below AprilTag mounting height of 12")
- **Gap width:** 14" (2.8 cube widths)
- Hot-glue bottom cubes to a foam tile strip for stability
- Leave gap cubes unglued (can adjust gap width between matches)

### Express Platform

- Small box or stacked foam cubes, 4" tall
- Approximately 8"x6" surface area
- Place 3 blocks on top before each match
- Located near Tag 581 (southeast area)
- Stable enough that robot bump doesn't topple it

---

## Match Reset Checklist

Between matches (2-3 minutes):
- [ ] Return all 12 blocks to warehouse floor
- [ ] Scatter 9 standard blocks randomly (not in rows)
- [ ] Place 3 express blocks on elevated platform
- [ ] Empty all baskets
- [ ] Check barrier wall (restack any knocked cubes)
- [ ] Verify green tape line intact
- [ ] Confirm all 8 AprilTags visible

---

## Practice Field (Simplified)

Each house has 1 practice field (tape boundaries only):
- 10x10 ft area marked with tape on floor
- NO foam walls (save cost and setup time)
- 4 AprilTags on portable stands (cardboard boxes or chairs)
- 3 baskets + 9 blocks
- Optional: tape line on floor for line-follow practice
- NO barrier wall (teams practice skills individually)

**Cost per practice field:** ~$30 (tape, tags, baskets, blocks)

---

## Design Decisions & Rationale

**Why a barrier wall instead of scattered obstacles?**
It creates a clear choice: go through (requires line following or precise driving)
or go around (safe but slow). This rewards the line_follower skill specifically.

**Why express blocks on a raised platform?**
Tests arm precision beyond flat-floor pickup. Students who master arm positions
get a scoring advantage. Also teaches "different pickup strategies for different
situations" — real-world robotics thinking.

**Why so many automation bonuses?**
Without them, the optimal strategy is "drive fast, bulldoze everything into the
nearest basket" — which teaches nothing. The bonuses make automation always
worth more than speed alone, but leave bulldozing as a viable backup.

**Why 12 blocks (9 + 3 express)?**
9 standard = achievable for semi-auto teams in 10 minutes.
12 total = only possible with efficient automation. The +50 full-clear bonus
is the "stretch goal" that top teams chase.

**Why color sort bonus (+5) ON TOP of correct basket (+15)?**
It separates "human told robot which basket" (15 pts) from "robot figured out
the color itself" (15+5=20 pts). Rewards vision code specifically.

**Why multi-block bonus?**
bin_collect and cart_push are advanced skills. Without a bonus, single-block
trips are always simpler. The +5/trip bonus makes bin collection worth
the added complexity.
