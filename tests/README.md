# Tests

Hardware and feature test scripts are in `scripts/testing/`.

## Quick Hardware Test

```bash
cd /home/robot/pathfinder
python3 robot_startup.py
```

If all 7 steps pass and you hear 2 beeps, the robot is working.

## Individual Tests

All scripts in `scripts/testing/` work on both Pi 4 and Pi 5.

```bash
cd /home/robot/pathfinder
python3 scripts/testing/test_motors.py
python3 scripts/testing/test_arm_servos.py
python3 scripts/testing/find_apriltag.py
python3 scripts/testing/test_block_detection.py
```
