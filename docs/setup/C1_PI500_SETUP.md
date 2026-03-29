# C1: Pi 500 Setup

**Purpose:** Connect your Pi 500 to a monitor and prepare it as your team's control hub

The Pi 500 is a keyboard computer — the keyboard IS the computer. You just need a monitor and mouse.

---

## Materials Needed

- Raspberry Pi 500 (with SD card already imaged — see [A1](A1_PI500_OS_BUILD.md))
- Portable monitor
- Micro HDMI to HDMI adapter
- USB mouse
- Power supply (USB-C)

## Step 1: Connect Hardware

```
[Monitor] ←HDMI→ [Micro HDMI Adapter] ←→ [Pi 500 HDMI port]
[Mouse] ←USB→ [Pi 500 USB port]
[Power] ←USB-C→ [Pi 500 power port]
```

The Pi 500's keyboard is built-in — no separate keyboard needed.

## Step 2: Power On

1. Plug in power
2. Wait for desktop to appear (~30 seconds)
3. If prompted for password, enter the one set during imaging

## Step 3: Connect to WiFi

1. Click the network icon in the top-right taskbar
2. Select your workshop WiFi network
3. Enter password if required
4. Verify: open terminal (Ctrl+Alt+T) and run:
   ```bash
   ping -c 3 google.com
   ```

## Step 4: Open Terminal

You'll use the terminal for everything in this workshop:

- **Menu bar:** Click the terminal icon in the top taskbar
- **Keyboard shortcut:** Ctrl+Alt+T

Practice opening a terminal now. You'll be using it constantly.

## Step 5: Verify Workshop Repo

```bash
cd ~/PathfinderV2
ls skills/
```

You should see folders like `mecanum_drive/`, `sonar_sensors/`, `camera_vision/`, etc.

If the repo isn't there:
```bash
cd ~
git clone https://github.com/luminerdy/PathfinderV2.git
```

---

## Pi 500 Quick Reference

| Action | How |
|--------|-----|
| Open terminal | Ctrl+Alt+T |
| SSH to robot | `ssh robot@<robot-ip>` |
| Copy file to robot | `scp file.py robot@<robot-ip>:/home/robot/pathfinder/` |
| View robot camera | Open browser: `http://<robot-ip>:8080` |
| Edit code | `nano filename.py` or use Thonny (GUI editor) |
| Run Python | `python3 script.py` |
| Stop a running script | Ctrl+C |

---

## Important: Do NOT Change the Hostname

Your Pi 500 hostname identifies your team. The facilitator set it during imaging. Changing it can cause network conflicts.

---

**Next:** [C2: Connect to Robot](C2_CONNECT_AND_TEST.md) (SSH from Pi 500 to your robot)
