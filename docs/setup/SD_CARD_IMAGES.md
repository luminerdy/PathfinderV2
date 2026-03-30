# SD Card Images — Pre-Built for Workshop

**Purpose:** Pre-image all SD cards before workshop day so teams start in minutes, not hours.

Two images needed per team: one for the Pi 500 (control hub), one for the Robot (Pi 4).

**Scale:** 49 teams = 49 robot SD cards + 49 Pi 500 SD cards = **98 cards total.**

---

## Why Pre-Build?

| Without pre-built | With pre-built |
|-------------------|----------------|
| 30 min OS install per device | Insert card, boot, done |
| WiFi config during workshop | WiFi already configured |
| Dependency installs fail on slow WiFi | Everything pre-installed |
| 1+ hour before teams can start | 5 minutes to first SSH |

**Pre-building saves 1-2 hours per team on workshop day.**

---

## Image 1: Pi 500 (Control Hub)

### Build Steps

1. **Image base OS:**
   - Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
   - Choose OS: **Raspberry Pi OS (64-bit) Desktop**
   - Advanced settings (gear icon):
     - Hostname: `pi500-template`
     - Enable SSH (password auth)
     - Username: `robot`
     - Password: `R4spb3rry` (or your workshop standard)
     - WiFi: Your workshop network SSID + password
     - Timezone: Your timezone
   - Write to SD card

2. **Boot and install dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-opencv python3-pip python3-pygame sshpass joystick
   pip3 install pupil-apriltags numpy --break-system-packages
   ```

3. **Clone workshop repo:**
   ```bash
   cd ~
   git clone https://github.com/luminerdy/PathfinderV2.git
   ```

4. **Add workshop files to desktop:**
   ```bash
   # Quick-access links on desktop
   ln -s ~/PathfinderV2/START_HERE.md ~/Desktop/START_HERE.md
   ln -s ~/PathfinderV2/docs/competition/QUICK_REFERENCE.md ~/Desktop/QUICK_REFERENCE.md
   ln -s ~/PathfinderV2/docs/competition/COMPETITION_RULES.md ~/Desktop/COMPETITION_RULES.md
   ```

5. **Test:**
   ```bash
   cd ~/PathfinderV2
   python3 -c "import cv2; import pupil_apriltags; import pygame; print('All dependencies OK')"
   ```

6. **Clone for each team:**
   - Shut down Pi 500
   - Remove SD card
   - Use Raspberry Pi Imager or `dd` to clone the card
   - For each clone, boot and change hostname:
     ```bash
     sudo hostnamectl set-hostname pi500-team1
     # Repeat with team2, team3, etc.
     ```

### What's on the Pi 500 Image

| Item | Purpose |
|------|---------|
| Raspberry Pi OS Desktop | Visual interface |
| Python 3 + OpenCV + pygame | Run scripts + gamepad |
| SSH + sshpass | Connect to robot |
| pupil-apriltags | AprilTag detection (for testing) |
| PathfinderV2 repo | All skills, docs, competition rules |
| Desktop shortcuts | START_HERE, Quick Reference, Rules |

---

## Image 2: Robot Pi (Pi 4)

### Build Steps

1. **Image base OS:**
   - Raspberry Pi Imager
   - Choose OS: **Raspberry Pi OS (64-bit) Desktop**
   - Advanced settings:
     - Hostname: `robot-template`
     - Enable SSH
     - Username: `robot`
     - Password: `R4spb3rry` (same as Pi 500 for simplicity)
     - WiFi: Workshop network
     - Timezone: Your timezone
   - Write to SD card

2. **Boot and install robot dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-opencv python3-pip python3-smbus i2c-tools
   pip3 install pupil-apriltags numpy smbus2 flask --break-system-packages
   ```

3. **Enable I2C:**
   ```bash
   sudo raspi-config nonint do_i2c 0
   ```

4. **Clone and setup robot code:**
   ```bash
   cd ~
   git clone https://github.com/luminerdy/PathfinderV2.git pathfinder
   ```

5. **Install startup service:**
   ```bash
   sudo cp ~/pathfinder/systemd/pathfinder-startup.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable pathfinder-startup.service
   ```

6. **Test (with robot hardware connected):**
   ```bash
   cd ~/pathfinder
   python3 -c "from lib.board import get_board; print('Board OK')"
   python3 scripts/tools/check_battery.py
   ```

7. **Clone for each team:**
   - Same process as Pi 500
   - Change hostname per team:
     ```bash
     sudo hostnamectl set-hostname robot-team1
     ```

### What's on the Robot Image

| Item | Purpose |
|------|---------|
| Raspberry Pi OS | Robot OS |
| Python 3 + OpenCV + Flask | Vision + web control |
| I2C + smbus2 | Motor/servo communication |
| pupil-apriltags | Navigation |
| PathfinderV2 code | All skills + scripts |
| Startup service | Auto-init on boot (beep when ready) |

---

## Naming Convention

| House | Team | Pi 500 Hostname | Robot Hostname |
|-------|------|----------------|----------------|
| 1 | 1 | pi500-h1t1 | robot-h1t1 |
| 1 | 2 | pi500-h1t2 | robot-h1t2 |
| ... | ... | ... | ... |
| 7 | 49 | pi500-h7t7 | robot-h7t7 |

**Naming:** `h1t1` = House 1, Team 1. Each house has its own WiFi network or VLAN to avoid cross-house interference.

**Static IPs recommended** — each house gets its own subnet (e.g., House 1 = 10.1.x.x, House 2 = 10.2.x.x).

---

## Workshop Day Checklist

Before teams arrive:
- [ ] All Pi 500 SD cards imaged and tested
- [ ] All Robot SD cards imaged and tested
- [ ] WiFi network up and tested
- [ ] All devices can ping each other
- [ ] SSH from each Pi 500 to its paired robot verified
- [ ] Batteries charged (2 sets per robot minimum)
- [ ] Spare SD cards available (things happen)
- [ ] Competition field set up (tags, baskets, blocks, barriers, tape)

---

## Troubleshooting

**Card won't boot:**
- Re-image with Raspberry Pi Imager
- Try different SD card (bad cards are common)

**WiFi won't connect:**
- Check SSID/password in `/etc/wpa_supplicant/wpa_supplicant.conf`
- 5GHz vs 2.4GHz? Pi 500 supports both, Pi 4 supports both

**SSH refused:**
- `sudo systemctl enable ssh && sudo systemctl start ssh`

**Robot code missing:**
- `cd ~ && git clone https://github.com/luminerdy/PathfinderV2.git pathfinder`
