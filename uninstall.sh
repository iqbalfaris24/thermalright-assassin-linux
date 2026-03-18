#!/usr/bin/env bash

set -e

echo "Uninstalling Thermalright LCD Driver..."

SERVICE_NAME="thermalright-lcd"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
UDEV_FILE="/etc/udev/rules.d/99-thermalright-lcd.rules"

# ----------------------------
# stop service
# ----------------------------
echo "Stopping service..."
sudo systemctl stop $SERVICE_NAME || true

# ----------------------------
# disable service
# ----------------------------
echo "Disabling service..."
sudo systemctl disable $SERVICE_NAME || true

# ----------------------------
# remove service file
# ----------------------------
if [ -f "$SERVICE_FILE" ]; then
    echo "Removing systemd service..."
    sudo rm -f "$SERVICE_FILE"
fi

# ----------------------------
# reload systemd
# ----------------------------
echo "Reloading systemd..."
sudo systemctl daemon-reload
sudo systemctl daemon-reexec

# ----------------------------
# remove udev rule
# ----------------------------
if [ -f "$UDEV_FILE" ]; then
    echo "Removing udev rule..."
    sudo rm -f "$UDEV_FILE"
fi

# ----------------------------
# reload udev
# ----------------------------
echo "Reloading udev..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "====================================="
echo "Uninstall complete!"
echo "====================================="
echo ""

echo "Optional cleanup:"
echo "- Remove virtualenv: rm -rf venv"