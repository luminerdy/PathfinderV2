# Creating PathfinderV2 GitHub Repository

GitHub no longer supports password authentication for API access. Here are your options:

## Option 1: Create via GitHub Web (Easiest)

1. Go to https://github.com/new
2. Log in with:
   - Username: `luminerdy`
   - Password: `Lum1n3rdy#2026`
3. Fill in:
   - **Repository name**: `PathfinderV2`
   - **Description**: `Clean, modular Python framework for MasterPi humanoid robot - Built for STEM education and hands-on robotics workshops`
   - **Public** repository
   - **DO NOT** initialize with README (we already have one)
4. Click "Create repository"
5. GitHub will show you commands to push existing code

Then run these commands:

```bash
cd /home/robot/code/pathfinder

# Add the remote (replace YOUR_USERNAME if different)
git remote add origin https://github.com/luminerdy/PathfinderV2.git

# Rename branch to main
git branch -M main

# Push code
git push -u origin main
```

When prompted for credentials, use:
- Username: `luminerdy`
- Password: `Lum1n3rdy#2026` (or use a Personal Access Token if this fails)

## Option 2: Install GitHub CLI

```bash
# Install GitHub CLI
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
# Follow prompts, use HTTPS, authenticate via browser

# Create repository
cd /home/robot/code/pathfinder
gh repo create PathfinderV2 --public --source=. --remote=origin --push

# Description and other details can be set on GitHub web
```

## Option 3: Create Personal Access Token

If password doesn't work for git push:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "Pathfinder Robot"
4. Select scopes: `repo` (all)
5. Click "Generate token"
6. **COPY THE TOKEN** (you won't see it again)

Then use the token instead of password:

```bash
cd /home/robot/code/pathfinder
git remote add origin https://github.com/luminerdy/PathfinderV2.git
git branch -M main
git push -u origin main

# When prompted:
# Username: luminerdy
# Password: [paste token here, not password]
```

---

## Current Status

Your code is committed locally at `/home/robot/code/pathfinder/`

Git log:
```
commit 247a59f
Initial commit: Pathfinder V2 - Clean modular framework for MasterPi robot
- 22 files, 3928 lines of code
```

Once you create the repository and push, it will be live at:
**https://github.com/luminerdy/PathfinderV2**
