# A1: Pi 500 OS Build

**Purpose:** Create the SD card image for the Raspberry Pi 500 (team control hub)

The Pi 500 is your **command center** — you'll use it to write code, SSH into the robot, monitor camera feeds, and run all workshop scripts. The robot runs headless; you control everything from here.

---

## Materials Needed

- Raspberry Pi 500 kit (keyboard computer)
- microSD card (32GB+ recommended)
- USB mouse
- Portable monitor + Micro HDMI to HDMI adapter
- Power supply (USB-C, included with Pi 500 kit)
- Another computer with internet (for imaging the SD card)

## Step 1: Download Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your computer
2. Insert microSD card into your computer
3. Open Raspberry Pi Imager
4. Choose OS: **Raspberry Pi OS (64-bit)** — Desktop version
5. Choose Storage: Select your microSD card
6. Click the **gear icon** (⚙️) for advanced settings:
   - Set hostname: `pi500-teamX` (replace X with team number)
   - Enable SSH (password authentication)
   - Set username: `robot`
   - Set password: (your choice, document it!)
   - Configure WiFi: Enter your workshop network SSID and password
   - Set locale: Your timezone
7. Click **Write** and wait for completion

## Step 2: First Boot

1. Insert SD card into Pi 500
2. Connect monitor via Micro HDMI adapter
3. Connect USB mouse
4. Plug in power — Pi 500 will boot to desktop

## Step 3: Verify Setup

Open a terminal (Ctrl+Alt+T) and verify:

```bash
# Check hostname
hostname
# Should show: pi500-teamX

# Check WiFi
ping -c 3 google.com
# Should succeed

# Check Python
python3 --version
# Should show Python 3.11+

# Check SSH is running
sudo systemctl status ssh
# Should show: active (running)
```

## Step 4: Install Workshop Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-opencv python3-pip sshpass

# Install Python packages
pip3 install pupil-apriltags numpy --break-system-packages

# Clone the workshop repository
cd ~
git clone https://github.com/luminerdy/PathfinderV2.git
cd PathfinderV2
```

## Step 5: Note Your IP Address

```bash
hostname -I
# Example: 10.10.10.141
```

Write this down — other teams don't need it, but you'll use it for troubleshooting.

---

## What's on the Pi 500

After setup, your Pi 500 has:

| Item | Purpose |
|------|---------|
| Raspberry Pi OS Desktop | Visual interface for coding and monitoring |
| Python 3 + OpenCV | Run and edit workshop scripts |
| SSH client | Connect to robot remotely |
| PathfinderV2 repo | All workshop skills, guides, and code |
| Terminal | Command line for SSH, git, python |

## What's NOT on the Pi 500

- No motor/servo drivers (those are on the robot)
- No hardware SDK (robot only)
- No camera access to robot camera (use SSH + web interface)

The Pi 500 is the **brain**. The robot is the **body**. They talk over WiFi.

---

## Pre-Built Option

For workshops, the facilitator can pre-image all SD cards to save time:

1. Build one Pi 500 image following steps above
2. Use Raspberry Pi Imager to clone the SD card
3. Change hostname on each clone (`pi500-team1`, `pi500-team2`, etc.)
4. Pre-connect to workshop WiFi

This skips 15-20 minutes of setup per team.

---

**Next:** [C1: Pi 500 Setup](C1_PI500_SETUP.md) (connect to monitor and configure)
