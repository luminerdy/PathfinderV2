#!/bin/bash
# Install PathfinderV2 systemd services for auto-start on boot

set -e

echo "=================================================="
echo "PathfinderV2 Auto-Start Installation"
echo "=================================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo:"
    echo "  sudo bash install_services.sh"
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_DIR="/etc/systemd/system"

echo "Installing services..."

# Copy service files
cp "${SCRIPT_DIR}/systemd/pathfinder-startup.service" "$SERVICE_DIR/"
cp "${SCRIPT_DIR}/systemd/pathfinder-drive.service" "$SERVICE_DIR/"
cp "${SCRIPT_DIR}/systemd/pathfinder-servo.service" "$SERVICE_DIR/"

echo "✓ Service files copied"

# Reload systemd
systemctl daemon-reload
echo "✓ Systemd reloaded"

# Enable services
systemctl enable pathfinder-startup.service
systemctl enable pathfinder-drive.service
systemctl enable pathfinder-servo.service
echo "✓ Services enabled"

# Start services now (optional)
read -p "Start services now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    systemctl start pathfinder-startup.service
    sleep 3
    systemctl start pathfinder-drive.service
    systemctl start pathfinder-servo.service
    echo "✓ Services started"
fi

echo ""
echo "=================================================="
echo "Installation Complete!"
echo "=================================================="
echo ""
echo "Services installed:"
echo "  • pathfinder-startup.service - Robot initialization"
echo "  • pathfinder-drive.service   - Web drive (port 5000)"
echo "  • pathfinder-servo.service   - Servo control (port 5001)"
echo ""
echo "On next boot, robot will:"
echo "  1. Initialize hardware"
echo "  2. Position arm forward"
echo "  3. Start web interfaces"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status pathfinder-startup"
echo "  sudo systemctl status pathfinder-drive"
echo "  sudo systemctl status pathfinder-servo"
echo "  sudo journalctl -u pathfinder-startup -f"
echo ""
echo "To uninstall:"
echo "  sudo systemctl disable pathfinder-*.service"
echo "  sudo rm /etc/systemd/system/pathfinder-*.service"
echo "  sudo systemctl daemon-reload"
echo ""
