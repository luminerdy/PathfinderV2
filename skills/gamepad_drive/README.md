# Gamepad Remote Control (D6) - Quick Reference

**Drive with Logitech F710 wireless gamepad**

## Setup
1. Plug F710 USB receiver into **Robot Pi**
2. Gamepad on, back switch to **X**
3. `sudo apt install python3-pygame joystick`
4. `python3 skills/gamepad_drive/gamepad_drive.py`

## Controls

| Control | Action |
|---------|--------|
| Left/Right sticks Y | Tank drive |
| Sticks X | Strafe (mecanum) |
| Right trigger | Forward (analog) |
| Left trigger | Backward (analog) |
| Right bumper | Turn right |
| Left bumper | Turn left |
| A | Camera forward |
| B | Camera down |
| Y | Nod yes |
| X | Shake no |
| D-pad Up | Pickup block |
| D-pad Down | Drop block |
| **Back** | **EMERGENCY STOP** |
| **Start** | **Quit** |

---
*Grab the controller and drive!* 🎮
