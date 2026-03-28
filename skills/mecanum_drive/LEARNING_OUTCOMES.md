# D1: Mecanum Drive - Learning Outcomes

**Skill:** D1 - Mecanum Drive (Foundation)  
**Difficulty:** ⭐ Beginner  
**Time:** 15-20 minutes  

---

## Learning Outcomes (Observable & Measurable)

### Knowledge (Cognitive - Remember/Understand)

**After completing D1, participants can:**

1. **Explain** how mecanum wheels work
   - Describe the 45° roller configuration
   - Explain force vector decomposition
   - Identify which wheels create which motions

2. **Define** key concepts
   - Motor duty cycle (0-100%)
   - Omnidirectional movement
   - Robot-centric coordinate system

3. **Identify** the 4 wheel positions
   - Front-Left, Front-Right, Rear-Left, Rear-Right
   - Which motors control which wheels
   - Normal vs inverted motor directions

### Skills (Psychomotor - Apply/Analyze)

4. **Control** robot movement in all directions
   - Forward and backward
   - Strafe left and right
   - Rotate clockwise and counter-clockwise
   - Diagonal movement (combined motions)

5. **Tune** configuration parameters
   - Adjust speed limits (max/min)
   - Modify movement durations
   - Correct motor direction inversions

6. **Execute** movement patterns
   - Drive in straight lines
   - Strafe sideways without rotation
   - Rotate in place without translation
   - Complete square pattern (±6 inches accuracy)

7. **Debug** common issues
   - Diagnose "robot doesn't move" (battery, motors)
   - Fix wrong direction (motor inversions)
   - Troubleshoot crooked strafe (wheel mounting, weight)
   - Interpret battery voltage readings

### Problem-Solving (Cognitive - Analyze/Evaluate)

8. **Analyze** robot behavior
   - Observe movement and identify problems
   - Compare expected vs actual motion
   - Determine which wheel(s) causing issues

9. **Evaluate** performance
   - Assess smoothness of movement
   - Judge accuracy of square pattern (close enough?)
   - Compare different speed settings (trade-offs)

10. **Design** simple movement sequences
    - Plan path from A to B using mecanum capabilities
    - Combine forward, strafe, rotate for efficient motion
    - Optimize for speed vs accuracy

### Attitudes (Affective)

11. **Demonstrate** safety awareness
    - Check battery before operating
    - Maintain clear space around robot
    - Use emergency stop (Ctrl+C) when needed

12. **Practice** systematic approach
    - Follow instructions step-by-step
    - Test one change at a time (config tuning)
    - Document what works and what doesn't

13. **Show** resilience
    - Try again when robot misbehaves
    - Ask for help when truly stuck
    - Learn from mistakes (motor inversions happen!)

---

## Assessment Methods

### Formative Assessment (During Learning)

**Observation checklist:**
- [ ] Runs demo successfully (no errors)
- [ ] Robot moves in all 8 patterns
- [ ] Student can identify which movement is which
- [ ] Student explains why strafe is special (can't do with normal wheels)

**Questioning:**
- "Why do mecanum wheels have rollers at 45°?" (expect: creates lateral force)
- "What happens if one motor is inverted?" (expect: rotation during strafe)
- "How would you make robot go diagonally?" (expect: combine forward + strafe)

**Hands-on tasks:**
- "Change max speed to 70 and run again" (can edit config)
- "Make robot go slower" (tune config, re-run)
- "Fix this: robot goes backward when told forward" (invert motors)

### Summative Assessment (Proof of Learning)

**Demonstration:**
Student successfully:
1. Runs demo without assistance
2. Robot completes all 8 movements
3. Square pattern closes within 6 inches
4. Student can stop robot (emergency stop)

**Verbal explanation:**
Student can explain (1-2 minutes):
- What mecanum wheels are
- Why they enable omnidirectional movement
- One advantage and one disadvantage

**Troubleshooting challenge:**
Given intentional problem, student can:
- Diagnose issue (e.g., one motor inverted)
- Propose solution (edit config)
- Test fix (run demo, verify)

**Configuration task:**
Student can:
- Edit `config.yaml` to change speed from 50 to 35
- Run demo and observe difference
- Explain what changed (slower movement)

---

## Success Criteria

### Minimum (Pass)
- ✅ Demo runs without crashing
- ✅ Robot moves in at least 6/8 patterns correctly
- ✅ Student can explain mecanum wheel basics
- ✅ Student aware of safety (battery check, clear space)

### Target (Proficient)
- ✅ All 8 patterns work correctly
- ✅ Square pattern closes within 6 inches
- ✅ Student can tune config and see results
- ✅ Student can debug one common problem (motor inversion)

### Stretch (Advanced)
- ✅ Student explains force vectors and kinematics
- ✅ Student designs custom movement pattern (triangle, circle)
- ✅ Student optimizes for specific goal (speed vs accuracy)
- ✅ Student helps peer troubleshoot their robot

---

## Common Misconceptions to Address

**Misconception 1:** "Mecanum wheels are just faster/better than normal wheels"
**Reality:** Trade-off: Omnidirectional capability costs ~30% efficiency

**Misconception 2:** "Strafe is just diagonal movement"
**Reality:** True strafe is pure sideways (no forward/backward component)

**Misconception 3:** "Motors need different code for different movements"
**Reality:** Same motor control, just different combinations create different motions

**Misconception 4:** "Square pattern should be perfect"
**Reality:** Open-loop control drifts, ±6 inches is good for demo

**Misconception 5:** "If robot doesn't work, something is broken"
**Reality:** Often just configuration (motor inversions, battery low)

---

## Differentiation by Skill Level

### For Struggling Students
**Focus:** Level 1 only (run demo, observe)
**Support:** Pair with advanced student, extra time
**Goal:** Understand WHAT mecanum does (not HOW it works)
**Assessment:** Can run demo, identify movements by name

### For Typical Students
**Focus:** Levels 1-2 (demo + config tuning)
**Support:** Facilitator available for questions
**Goal:** Control robot, tune parameters, basic debugging
**Assessment:** Complete all 8 patterns, fix one problem

### For Advanced Students
**Focus:** Levels 2-4 (config, code understanding, extensions)
**Support:** Point to Deep Dive section, encourage exploration
**Goal:** Understand kinematics, design custom patterns, optimize
**Assessment:** Explain equations, create novel movement, help peers

### For Engineers (Non-Coders)
**Focus:** Level 2 (configuration tuning) + theory
**Support:** Read Deep Dive, focus on physics/math
**Goal:** Understand mechanics and trade-offs
**Assessment:** Justify design decisions, evaluate alternatives

### For Engineers (Coders)
**Focus:** Levels 2-4 (study code, optimize, extend)
**Support:** Challenge them with extensions
**Goal:** Implement field-centric drive or odometry
**Assessment:** Working extension, documented approach

---

## Integration with Workshop Flow

### Prerequisite Skills
**None** - This is the starting skill!

### Builds Foundation For
- **D2: Sonar** - Add sensors to movement
- **D3: Arm** - Coordinate arm while moving
- **E2: AprilTag Navigation** - Autonomous mecanum control
- **E4: Visual Servoing** - Approach targets with strafing
- **E5: Autonomous Pickup** - Navigate + manipulate

### Time Allocation (6-hour workshop)
**Hour 1 (30 minutes):**
- Introduction (5 min): What is mecanum, why special
- Demo run (10 min): Watch all 8 patterns
- Discussion (5 min): Q&A, safety, next steps
- Hands-on (10 min): Students run on their robots

**For students:** This is enough, move to D2  
**For engineers:** Additional 15-30 min for config tuning and theory

---

## Facilitator Notes

### Common Student Questions

**Q: "Why do the wheels have those funny rollers?"**
A: "The 45° rollers let force push sideways, not just forward. That's how strafe works!"

**Q: "Can we make it go faster?"**
A: "Yes! Edit config.yaml, change max speed. But too fast = loses traction."

**Q: "Why doesn't the square close perfectly?"**
A: "No sensors measuring position, so small errors add up. That's what encoders/vision fix!"

**Q: "What if one wheel is backward?"**
A: "Robot will spin when trying to strafe. Fix: edit config, invert that motor."

### Setup Checklist

Before session:
- [ ] All robots charged (>7.5V)
- [ ] Clear floor space (6 feet per robot)
- [ ] Backup robots ready (in case of hardware failure)
- [ ] Config files pre-loaded on all robots
- [ ] Test run on demo robot (verify it works!)

During session:
- [ ] Safety briefing first (battery, space, emergency stop)
- [ ] Show demo on your robot before students try
- [ ] Circulate and observe (catch issues early)
- [ ] Have motor inversion fix ready (very common!)

After session:
- [ ] Collect observations (which part was confusing?)
- [ ] Note common issues (update troubleshooting guide)
- [ ] Assess outcomes (did they meet criteria?)

---

*Clear outcomes + measurable assessment = effective learning!* 📚
