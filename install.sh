#!/usr/bin/env bash

set -e

echo "Installing Thermalright LCD Driver..."

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/thermalright-lcd.service"
UDEV_FILE="/etc/udev/rules.d/99-thermalright-lcd.rules"

echo "Project directory:"
echo "$PROJECT_DIR"

# ----------------------------
# check python
# ----------------------------
if ! command -v python3 &> /dev/null
then
    echo "Python3 not found."
    exit 1
fi

# ----------------------------
# create virtualenv
# ----------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# ----------------------------
# install dependencies
# ----------------------------
echo "Installing dependencies..."

"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install hidapi psutil

# ----------------------------
# create udev rule
# ----------------------------
echo "Installing udev rule..."

sudo bash -c "cat > $UDEV_FILE" <<EOF
KERNEL=="hidraw*", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="8001", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

# ----------------------------
# create systemd service
# ----------------------------
echo "Creating systemd service..."

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Thermalright LCD Service
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStartPre=/bin/sleep 5
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/app.py

Restart=always
RestartSec=3
StartLimitInterval=0

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------
# reload systemd
# ----------------------------
echo "Reloading systemd..."

sudo systemctl daemon-reexec
sudo systemctl daemon-reload

# ----------------------------
# enable service
# ----------------------------
echo "Enabling service..."

sudo systemctl enable thermalright-lcd

# ----------------------------
# start service
# ----------------------------
echo "Starting service..."

sudo systemctl restart thermalright-lcd

echo ""
echo "====================================="
echo "Installation complete!"
echo "====================================="
echo ""

echo "Check service status:"
echo "systemctl status thermalright-lcd"

echo ""
echo "View logs:"
echo "journalctl -u thermalright-lcd -f"