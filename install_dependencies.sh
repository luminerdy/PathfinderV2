#!/bin/bash
# Pathfinder System Dependencies Installation Script
# Run on fresh Raspberry Pi OS installation

set -e

echo "=================================="
echo "  Pathfinder Dependency Installer"
echo "=================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "ERROR: Do not run this script as root/sudo"
   echo "Run as regular user: ./install_dependencies.sh"
   exit 1
fi

echo "This will install all required system packages."
echo "Estimated time: 20-30 minutes"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Update system
echo ""
echo "[1/8] Updating system..."
sudo apt update
sudo apt upgrade -y

# Essential tools
echo ""
echo "[2/8] Installing build tools..."
sudo apt install -y build-essential cmake pkg-config git wget curl

# Python development
echo ""
echo "[3/8] Installing Python development packages..."
sudo apt install -y python3-dev python3-pip python3-setuptools python3-venv

# Serial communication
echo ""
echo "[4/8] Installing serial communication tools..."
sudo apt install -y python3-serial minicom screen

# Camera support
echo ""
echo "[5/8] Installing camera support..."
sudo apt install -y libcamera-dev libcamera-apps libcamera-tools v4l-utils

# OpenCV dependencies
echo ""
echo "[6/8] Installing OpenCV dependencies..."
sudo apt install -y \
    libopencv-dev python3-opencv \
    libatlas-base-dev libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libgtk-3-dev libhdf5-dev libleptonica-dev libtesseract-dev

# Numeric libraries
echo ""
echo "[7/8] Installing numeric/scientific libraries..."
sudo apt install -y gfortran libopenblas-dev liblapack-dev

# Configure permissions
echo ""
echo "[8/8] Configuring user permissions..."
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip3 install --upgrade pip

# Summary
echo ""
echo "=================================="
echo "  Installation Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. REBOOT (required for permissions): sudo reboot"
echo "  2. After reboot, install Python packages:"
echo "     cd /home/robot/code/pathfinder"
echo "     pip3 install -r requirements.txt"
echo "  3. Test hardware:"
echo "     python3 test_hardware.py"
echo ""
echo "See DEPENDENCIES.md for troubleshooting."
echo ""
