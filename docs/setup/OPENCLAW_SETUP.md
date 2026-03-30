# OpenClaw Setup (Optional)

**Purpose:** Give your team an AI coding partner that can read, write, and run code on your robot.

**This is optional.** You can also use browser-based ChatGPT/Claude, or no AI at all. OpenClaw is for teams that want a deeper AI integration.

---

## What Is OpenClaw?

OpenClaw is an AI agent that runs on your Pi 500 and connects to your robot over SSH — just like you do, but it can:

- Read and edit your robot's code
- Run scripts and see the output
- Debug errors ("why does my robot drift right?")
- Write new scripts ("make a block pickup routine")
- Analyze competition rules and suggest strategy
- Monitor battery and robot status

Think of it as a **team member who knows Python, robotics, and never gets tired.**

---

## Do I Need This?

| Approach | What You Use | Setup Time |
|----------|-------------|------------|
| No AI | Just code yourself | 0 min |
| Browser AI | ChatGPT/Claude in browser, copy-paste | 0 min |
| **OpenClaw** | AI agent on Pi 500 with robot access | 5-10 min |

**OpenClaw is best if you want:**
- AI that can directly test code on your robot
- Faster iteration (no copy-paste between browser and terminal)
- An always-available coding partner

**Skip OpenClaw if you prefer:**
- Writing all code yourself
- Using browser-based AI (works fine!)
- Keeping things simple

---

## Setup (5-10 minutes)

### Step 1: Check Node.js

OpenClaw requires Node.js. Check if it's installed:
```bash
node --version
# Need v18+ 
```

If not installed:
```bash
sudo apt install -y nodejs npm
```

### Step 2: Install OpenClaw

```bash
sudo npm install -g openclaw
```

### Step 3: Initialize

```bash
cd ~
openclaw init
```

This creates a workspace at `~/.openclaw/`

### Step 4: Configure API Key

You need an API key from Anthropic (Claude) or OpenAI (GPT):

```bash
openclaw config set anthropic.key YOUR_API_KEY_HERE
```

Ask your coach for the workshop API key, or use your own.

### Step 5: Configure Robot Connection

Tell OpenClaw how to reach your robot:

Create `~/.openclaw/workspace/TOOLS.md`:
```markdown
### Robot Connection
- SSH: robot@<ROBOT_IP>
- Password: (your robot's password)
- Code location: /home/robot/pathfinder
```

### Step 6: Start

```bash
openclaw gateway start
```

OpenClaw is now running! Connect via Telegram, Discord, or the web interface (ask your coach for details).

---

## What Can OpenClaw Do For You?

**During assembly:**
> "Explain what each servo does on the MasterPi arm"

**During exploration:**
> "Run the mecanum drive demo and tell me what happened"

**During coding:**
> "Write a Python script that finds blue blocks and drives to them"

**During competition:**
> "My robot keeps missing the block — look at bump_grab.py and suggest fixes"
> "Analyze the scoring rules — what should we prioritize in 10 minutes?"

**Debugging:**
> "SSH into my robot and check the battery"
> "Why does this error happen: ModuleNotFoundError: No module named 'skills'"

---

## Coach Notes

### Pre-Workshop Setup (if offering OpenClaw)

1. Install Node.js + OpenClaw on the Pi 500 SD card image
2. Create a shared API key with spending limits
3. Pre-configure `openclaw init` on each image
4. Teams only need to add the API key (or it's pre-loaded)

### Cost Management

- Use Claude Sonnet (not Opus) for lower cost
- Set per-key spending limits
- Estimate: ~$0.50-2.00 per team per hour
- 49 teams × 6 hours ≈ $150-600 depending on usage
- Cache helps reduce cost for repeated similar queries

### API Key Options

| Option | Pros | Cons |
|--------|------|------|
| One shared key | Simple setup | Shared rate limits |
| Per-house key (7) | Better rate limits | 7 keys to manage |
| Per-team key (49) | Full isolation | Lots of keys |
| BYOK (bring your own) | Zero cost to organizer | Some teams won't have one |

**Recommended:** One key per house (7 keys) with spending limits.

---

## Adding to SD Card Image

If pre-installing on the Pi 500 image:

```bash
# Install Node.js and OpenClaw
sudo apt install -y nodejs npm
sudo npm install -g openclaw

# Initialize workspace
openclaw init

# Pre-configure (facilitator adds API key before cloning)
# openclaw config set anthropic.key WORKSHOP_KEY_HERE
```

Add to the Pi 500 image build steps in [SD_CARD_IMAGES.md](SD_CARD_IMAGES.md).

---

*Your AI team member is ready. Ask it anything.* 🤖💬
