# Autonomous Testing Framework

Self-validating tests using AprilTag visual feedback. Tests can run without human intervention and generate comprehensive reports with images.

## Quick Start

### 1. Setup Field

**Wall-mounted AprilTags (Recommended):**
- 6'x6' field with white Coroplast walls (18" tall)
- AprilTags at 10" height (camera level)
- Tags: 6"x6" recommended (4"x4" minimum)
- Family: tag36h11
- Good lighting, no glare

**Default configuration (wall_field_6x6):**
```
     6 ft
   ┌─[1]────[2]─┐
   │            │
6  [0]         [3]
ft │            │
   │            │
   └─[4]────[5]─┘
```

- North wall: Tags 1, 2
- East wall: Tag 3
- South wall: Tags 4, 5
- West wall: Tag 0

### 2. Print AprilTags

**Generate tags:**
- Online: https://chev.me/arucogen/
  - Family: tag36h11
  - IDs: 0-5
  - Size: 6" (150mm)
  
**Or use Python:**
```bash
pip3 install apriltag-gen
python3 -c "
from apriltag_gen import generate
for i in range(6):
    generate('tag36h11', i, f'tag_{i}.png', 150)  # 150mm = ~6 inches
"
```

**Print:**
- Black & white
- Actual size (no scaling!)
- On cardstock or laminate
- Mount on Coroplast at 10" height

### 3. Run Tests

**List available field configurations:**
```bash
cd ~/code/pathfinder
python3 -m tests.run_field_test --list-fields
```

**Run test suite:**
```bash
python3 -m tests.run_field_test --field wall_field_6x6
```

**Custom output directory:**
```bash
python3 -m tests.run_field_test --field wall_field_6x6 --output my_tests
```

**Verbose logging:**
```bash
python3 -m tests.run_field_test --field wall_field_6x6 -v
```

### 4. Review Results

After testing completes, check:

```
test_results/
└── run_YYYYMMDD_HHMMSS/
    ├── report.md           # Markdown report with summary
    ├── results.json        # Machine-readable results
    └── images/             # Captured images
        ├── tag_detection_survey_angle_000.jpg
        ├── tag_detection_survey_angle_030.jpg
        ├── navigate_to_tag_1_before.jpg
        ├── navigate_to_tag_1_after.jpg
        └── ...
```

**View report:**
```bash
cat test_results/run_*/report.md
```

Or open `report.md` in any markdown viewer.

## Test Suite

### Test 1: Tag Detection Survey
- Rotates 360° at center
- Detects all visible AprilTags
- Validates: All expected tags found
- Duration: ~30 seconds

### Test 2: Navigate to Tag (per tag)
- Navigates to each tag individually
- Uses visual servoing (center + approach)
- Validates: Arrival within target distance
- Duration: ~15-30 seconds per tag

### Test 3: Waypoint Tour
- Navigates sequential path through all tags
- Tests multi-waypoint navigation
- Validates: Complete tour without failures
- Duration: ~1-3 minutes

### Test 4: Return to Home
- Navigates back to home tag (Tag 0)
- Validates: Successful return
- Duration: ~15-30 seconds

**Total duration: 2-5 minutes**

## Field Configurations

### wall_field_6x6 (Default)
6'x6' field with 6 wall-mounted tags (recommended)

### corner_field_6x6
6'x6' field with 4 corner-mounted tags (simple setup)

### simple_test
Minimal 3-tag setup for basic testing

## Success Criteria

Tests validate themselves using AprilTag feedback:

**Tag Detection:**
- All expected tags detected during 360° scan

**Navigation:**
- Final distance < target distance × 1.2
- Target tag visible at end
- Navigation completed within timeout

**Path Following:**
- All waypoints reached successfully
- No navigation failures

## Troubleshooting

**"Tag not found during search"**
- Check tag is visible from center position
- Verify lighting (no glare)
- Increase tag size
- Check tag ID matches field config

**"Timeout exceeded"**
- Reduce target stop distance
- Check robot can move (battery > 7.5V)
- Verify field has clear paths

**"Navigator not initialized"**
- Camera must be enabled
- Check camera connected: `ls /dev/video*`
- Try: `python3 -c "from hardware import Camera; c = Camera(); c.open()"`

**Battery low warning**
- Charge batteries (need > 7.3V for reliable operation)
- Or continue with caution

## Customization

### Create Custom Field

Edit `tests/field_config.py`:

```python
MY_FIELD = FieldConfig(
    name="my_custom_field",
    description="My custom test setup",
    size_ft=(8, 8),
    tag_height_in=12,
    tag_size_in=6,
    walls=[
        WallConfig(
            name="north",
            length_ft=8,
            tags=[0, 1, 2],
            position="top"
        ),
        # ... more walls
    ]
)

AVAILABLE_FIELDS["my_custom_field"] = MY_FIELD
```

Then run:
```bash
python3 -m tests.run_field_test --field my_custom_field
```

### Adjust Navigation Parameters

Edit `capabilities/navigation.py`:

```python
class Navigator:
    def __init__(self, robot):
        # ...
        self.rotation_speed = 0.2     # Search rotation speed
        self.approach_speed = 30      # Forward speed
        self.slow_distance = 500      # Slow down threshold (mm)
        self.slow_speed = 15          # Slow approach speed
        self.center_tolerance = 50    # Centering tolerance (pixels)
```

## Architecture

```
tests/
├── __init__.py              # Package marker
├── README.md                # This file
├── field_config.py          # Field layouts
├── autonomous_tests.py      # Test suite implementation
└── run_field_test.py        # Main test runner

capabilities/
└── navigation.py            # AprilTag navigation controller
```

**Key classes:**

- `Navigator` - Visual servoing navigation
- `FieldConfig` - Test field definition
- `AutonomousTestSuite` - Self-validating tests
- `NavigationResult` - Navigation outcome

## Future Enhancements

**Planned:**
- [ ] Position estimation via triangulation
- [ ] Obstacle avoidance integration
- [ ] Block detection tests (YOLO)
- [ ] Pickup/place validation
- [ ] Multi-robot coordination tests
- [ ] Performance benchmarking
- [ ] Automated camera calibration check

## Notes

- **No encoders needed** - Pure vision-based navigation
- **Self-validating** - Uses AprilTag feedback to verify success
- **Comprehensive logs** - Images + data for debugging
- **Easy setup** - Just print tags and tape to walls
- **Repeatable** - Consistent test conditions

## Examples

**Basic test run:**
```bash
$ python3 -m tests.run_field_test --field wall_field_6x6

Field: wall_field_6x6
Description: 6x6 ft field with wall-mounted AprilTags at 10 inch height
Size: 6.0' x 6.0'
Tag height: 10"
Tag size: 6"
Total tags: 6

Walls:
  north           (6.0') - Tags: [1, 2]
  east            (6.0') - Tags: [3]
  south           (6.0') - Tags: [4, 5]
  west            (6.0') - Tags: [0]

Checking battery...
Battery: 8.02V
✅ Robot initialized

READY TO START AUTONOMOUS TESTING

Start testing? [Y/n]: y

🤖 Starting autonomous test suite...

>>> Test: tag_detection_survey
    Result: ✅ PASS
    Tags seen: [0, 1, 2, 3, 4, 5]
    Time: 28.3s

>>> Test: navigate_to_tag_0
    Result: ✅ PASS
    Distance: 1250mm → 285mm (target: 300mm)
    Time: 12.1s

[... more tests ...]

TEST SUMMARY
Total tests: 10
Passed: 10 ✅
Failed: 0 ❌
Success rate: 100.0%
Total time: 142.8s

Results: test_results/run_20260320_153045
Report: test_results/run_20260320_153045/report.md
```

---

**Ready to test!** 🤖📊
