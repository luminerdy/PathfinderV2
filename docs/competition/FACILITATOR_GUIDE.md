# Facilitator Guide

**Purpose:** Everything the workshop facilitator needs to run Supply Chain Scramble

---

## Before Workshop Day

### 2 Weeks Before
- [ ] Order materials (blocks, baskets, foam tiles, tape, barriers)
- [ ] Print AprilTags (tag36h11, IDs 578-585, 10"×10", 8 copies)
- [ ] Confirm participant count and team assignments (3-4 per team)
- [ ] Confirm room setup (power outlets, tables, WiFi)
- [ ] Test WiFi bandwidth (all devices connecting simultaneously)

### 1 Week Before
- [ ] Image all SD cards (see [SD Card Images](../setup/SD_CARD_IMAGES.md))
- [ ] Test every Pi 500 → Robot SSH connection
- [ ] Charge all batteries (2 sets per robot minimum)
- [ ] Print competition rules (1 per team) + quick reference cards
- [ ] Print scoring sheets (see below)
- [ ] Prepare modification materials (tape, cardboard, zip ties, rubber bands, foam board)
- [ ] Prepare robot assembly kits (if not pre-assembled)

### Night Before / Morning Of
- [ ] Build competition field (see [Field Layout](FIELD_LAYOUT.md)) — 30-45 min
- [ ] Place all AprilTags, verify visibility from all angles
- [ ] Test one robot on the field (drive, sonar, camera, arm)
- [ ] Set up team tables (Pi 500, monitor, mouse, power strip per team)
- [ ] Place modification materials on each table
- [ ] Print and place competition rules/quick reference at each station
- [ ] Charge spare batteries
- [ ] Have spare SD cards ready

---

## Workshop Day Schedule (6 Hours)

### Phase 1: Build (2 hours)

| Time | Activity | Facilitator Action |
|------|----------|--------------------|
| 0:00 | Welcome, form teams | Introduce theme, hand out rules |
| 0:05 | Split teams: Group A builds, Group B sets up Pi 500 | Float between groups |
| 0:15 | Assembly begins | Help with tricky assembly steps |
| 0:15 | Pi 500 group: read rules, plan strategy with GenAI | Answer questions about rules |
| 1:30 | Assembly wrapping up | Help teams connect Pi 500 to robot |
| 1:45 | All teams: SSH connected, battery checked | Verify every team has SSH working |

**Common issues:**
- WiFi not connecting → check SSID/password, 2.4 vs 5GHz
- SSH refused → `sudo systemctl start ssh` on robot
- Servos not moving → check servo cable connections
- Motors reversed → swap motor wire plugs (or invert in config)

### Phase 2: Connect + Explore (45 min)

| Time | Activity | Facilitator Action |
|------|----------|--------------------|
| 2:00 | Teams run hardware tests (C2 guide) | Walk around, verify each team |
| 2:15 | Teams explore skills (START_HERE.md) | Answer questions, show demos |
| 2:30 | Teams try autonomous scripts | Help debug, suggest GenAI use |

**Key checkpoint:** Every team must have:
- [ ] SSH working
- [ ] Motors moving
- [ ] Camera capturing
- [ ] Battery > 7.5V

### Phase 3: Prepare (45 min)

| Time | Activity | Facilitator Action |
|------|----------|--------------------|
| 2:45 | Robot modifications (materials on tables) | Let teams discover — don't suggest designs |
| 3:00 | Code customization + strategy | Help with Python/GenAI questions |
| 3:15 | Practice match (10 min, informal) | Run the timer, explain field rules |
| 3:25 | Break | Reset field for competition |

**Practice match purpose:** Teams see the field, discover problems, see other teams' ideas. This drives 90% of the iteration that follows.

### Phase 4: Competition (2 hours)

| Time | Activity | Facilitator Action |
|------|----------|--------------------|
| 3:30 | Final prep (5 min) | Reset field (scatter blocks, check baskets) |
| 3:35 | **QUALIFYING ROUND 1** (10 min) | Run timer, field judge, note penalties |
| 3:45 | Score Round 1, announce results | Use scoring sheet |
| 3:55 | Code iteration + mods (20 min) | Help teams debug, encourage GenAI |
| 4:15 | Reset field | Scatter blocks randomly, check baskets |
| 4:20 | **QUALIFYING ROUND 2** (10 min) | Same as Round 1 |
| 4:30 | Score, select finalists | Top 2 teams advance (or all if 3 teams) |
| 4:40 | Finals prep (10 min) | Teams make final adjustments |
| 4:50 | Reset field | Fresh block placement |
| 4:55 | **FINALS** (10 min) | Full energy, encourage spectating |
| 5:05 | Final scoring | Take time, be accurate |
| 5:15 | **Awards ceremony** | Announce scores, superlatives |
| 5:30 | Debrief + cleanup | What did teams learn? |

---

## Running a Match

### Pre-Match (2 min)
1. Scatter 9 blocks randomly in block zone
2. Place baskets at north wall under correct tags
3. Verify barriers in position
4. Teams place up to 3 robots in start zones
5. Verify all robots powered on

### During Match (10 min)
1. Say "3, 2, 1, GO!" — start timer
2. Teams operate from Pi 500 stations (no one on the field)
3. Watch for penalties:
   - Robot leaves field → -5 pts (mark it)
   - Human touches robot on field → -3 pts
   - More than 3 robots on field → -10 pts, remove one
   - Intentional ramming → -10 pts, robot removed 60 sec
4. Note passage crossings (3 pts each)
5. Note robot returns to start zone (3 pts each)
6. Allow robot swaps in start zone (tag-team)

### Post-Match Scoring (3 min)
1. "STOP!" — all robots stop immediately
2. Count blocks in each basket:
   - Check color match (correct basket = 15 pts, wrong = 3 pts)
3. Check robots for blocks:
   - In gripper = 2 pts
   - In storage bin = 2 pts each
4. Add navigation points (passage crossings + returns)
5. Add bonus points:
   - Autonomous deliveries observed: +10 pts each
   - All 9 sorted correctly: +30 pts
   - GenAI code used: +10 pts (ask teams to show)
   - Creative modification: +5 to +15 pts (judge discretion)
6. Subtract penalties
7. Announce score

---

## Scoring Sheet

Print one per match:

```
SUPPLY CHAIN SCRAMBLE — SCORING SHEET

Match: ______  Team: ____________  Date: ________

BLOCKS IN BASKETS:
  Blue basket (578):  ___ blue (×15) + ___ other (×3) = ___
  Yellow basket (579): ___ yellow (×15) + ___ other (×3) = ___
  Red basket (580):   ___ red (×15) + ___ other (×3) = ___

BLOCKS ON ROBOTS:
  Gripper/bin: ___ blocks × 2 pts = ___

NAVIGATION:
  Passage crossings: ___ × 3 pts = ___
  Returns to start:  ___ × 3 pts = ___

BONUSES:
  Autonomous deliveries: ___ × 10 pts = ___
  All 9 sorted correctly:  ☐ +30 pts  = ___
  GenAI code used:         ☐ +10 pts  = ___
  Creative modification:   ___ pts    = ___

PENALTIES:
  Left field:     ___ × -5 pts = ___
  Touched robot:  ___ × -3 pts = ___
  >3 robots:      ___ × -10 pts = ___
  Ramming:        ___ × -10 pts = ___

TOTAL: ___________
```

---

## When Things Go Wrong

| Problem | Solution |
|---------|----------|
| Robot won't move | Check battery (>7.0V), check SSH connection |
| Robot spinning in circles | Motor wires swapped, or code bug |
| Camera not working | `ls /dev/video*`, unplug/replug USB, reboot robot |
| SSH drops | WiFi issue, reconnect, check robot is powered |
| Battery dies mid-match | Swap in start zone (that's what tag-team is for!) |
| Robot stuck on barrier | 10-second rule: if stuck, team must back it out or it gets moved |
| Code crashes, motors keep running | SSH in, run emergency stop, or power cycle robot |
| Block stuck under robot | Leave it — scoring is end-of-match only |
| Team frustrated | Remind them: bulldozing is a valid strategy! Manual control is fine! |
| All teams stuck | Hint: "What if you could guide blocks toward the gripper?" (vague, not specific) |

### Emergency Stop (for facilitator)

If a robot is out of control:
```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
python3 -c "from lib.board import get_board; b=get_board(); b.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])"
```

Or just **unplug the battery** (fastest).

---

## Awards Suggestions

| Award | For |
|-------|-----|
| 🏆 **Champions** | Highest total score |
| 🤖 **Best Autonomous** | Most autonomous deliveries |
| 🧠 **Best AI Integration** | Most effective GenAI use |
| 🔧 **Best Engineering** | Most creative robot modification |
| 🏎️ **Speed Demons** | Fastest single delivery |
| 🤝 **Best Teamwork** | Judge's choice for collaboration |
| 💪 **Most Resilient** | Overcame the most setbacks |

---

## Post-Workshop

- [ ] Collect all robots, Pi 500s, batteries
- [ ] Back up any team code worth keeping (interesting solutions)
- [ ] Take down field
- [ ] Debrief notes: what worked, what didn't, what to change
- [ ] Thank volunteers/judges
