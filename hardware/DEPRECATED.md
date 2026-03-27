# hardware/ — DEPRECATED

**Status:** This layer is NOT used by working code.

All proven code (strafe navigation, centering, web control, block detection)
uses `lib/board.get_board()` (auto-detects Pi 4 I2C or Pi 5 serial).

**Correct imports for new code:**
```python
from lib.board import get_board    # Auto-detects Pi 4 or Pi 5
from hardware.sonar import Sonar   # Sonar wrapper is still good
from skills.strafe_nav import StrafeNavigator
from skills.block_detect import BlockDetector
from skills.centering import CenteringController
```

**Do NOT use:**
- `hardware/arm.py` — Wrong servo mapping (partially fixed, unreliable)
- `hardware/board.py` — Thin wrapper, adds nothing over BoardController
- `hardware/chassis.py` — Use lib/movement.py or skills/strafe_nav.py instead
- `hardware/camera.py` — Use cv2.VideoCapture(0) directly

**Exception:**
- `hardware/sonar.py` — This IS used and works correctly

**The real architecture is:**
```
lib/board.py           — Platform auto-detect entry point (proven)
lib/i2c_sonar.py       — Sonar I2C driver (proven)
lib/movement.py        — Calibrated movement functions (proven)
hardware/sonar.py      — Sonar abstraction (proven)
skills/strafe_nav.py   — Navigation (proven)
skills/block_detect.py — Block detection (proven)
skills/centering.py    — Centering (proven, partially superseded by strafe_nav)
```
