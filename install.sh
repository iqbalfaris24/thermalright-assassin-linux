#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_FILE="/etc/systemd/system/thermalright-lcd.service"
UDEV_FILE="/etc/udev/rules.d/99-thermalright-lcd.rules"

echo "====================================================="
echo "  Thermalright Assassin & System Monitor Installer   "
echo "====================================================="
echo "Project Directory: $PROJECT_DIR"
echo ""

# ----------------------------
# 1. Check Python3
# ----------------------------
if ! command -v python3 &> /dev/null; then
    echo "[!] Error: Python3 not found. Please install python3."
    exit 1
fi

# ----------------------------
# 2. Interactive Mode Selection
# ----------------------------
echo "Pilih opsi instalasi yang Anda inginkan:"
echo ""
echo "  [1] Standard Mode (Thermalright LCD Only) - [Default]"
echo "      • USB HID driver untuk LCD Cooler fisik"
echo "      • Web Control Panel konfigurasi LCD (/)"
echo "      • Dependensi ringan (hidapi, psutil, Flask)"
echo ""
echo "  [2] Full Suite Mode (Thermalright LCD + Full System Monitor)"
echo "      • Semua fitur Standard Mode"
echo "      • Realtime WebSocket Server (SocketIO)"
echo "      • Modern Web Dashboard (CPU 12-Thread, GPU AMD/Nvidia, RAM/Swap, Multi-Storage)"
echo "      • Single port unified server (/ & /dashboard/)"
echo ""

read -rp "Pilihan Anda [1/2] (Default: 1): " INSTALL_OPTION
INSTALL_OPTION=${INSTALL_OPTION:-1}

# ----------------------------
# 3. Setup Python Virtualenv
# ----------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating Python virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "[+] Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip

# ----------------------------
# 4. Install Dependencies
# ----------------------------
if [ "$INSTALL_OPTION" == "2" ]; then
    echo "[+] Installing Full Suite dependencies (Thermalright + WebSocket System Monitor)..."
    "$VENV_DIR/bin/pip" install hidapi psutil Flask flask-socketio flask-cors py-cpuinfo simple-websocket

    # Build Frontend UI jika Node.js & npm tersedia
    if [ -d "$PROJECT_DIR/dashboard-ui" ]; then
        if command -v npm &> /dev/null; then
            echo "[+] Building Dashboard UI (Vite / React)..."
            cd "$PROJECT_DIR/dashboard-ui"
            npm install
            npm run build
            cd "$PROJECT_DIR"
        else
            echo "[!] Warning: npm/node not found. Pastikan dashboard-ui/dist sudah ter-build."
        fi
    fi
else
    echo "[+] Installing Standard dependencies (Thermalright LCD Only)..."
    "$VENV_DIR/bin/pip" install hidapi psutil Flask
fi

# ----------------------------
# 5. Create Udev Rule
# ----------------------------
echo "[+] Installing udev rule for USB HID access..."
sudo bash -c "cat > $UDEV_FILE" <<EOF
KERNEL=="hidraw*", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="8001", MODE="0666"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger

# ----------------------------
# 6. Create Systemd Service
# ----------------------------
echo "[+] Creating systemd service ($SERVICE_FILE)..."
sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Thermalright LCD & System Monitor Service
After=multi-user.target network.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR
ExecStartPre=/bin/sleep 3
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/app.py
Restart=always
RestartSec=3
StartLimitInterval=0
Environment=PORT=5000

[Install]
WantedBy=multi-user.target
EOF

# ----------------------------
# 7. Reload and Restart Service
# ----------------------------
echo "[+] Reloading systemd and restarting service..."
sudo systemctl daemon-reload
sudo systemctl enable thermalright-lcd
sudo systemctl restart thermalright-lcd

echo ""
echo "====================================================="
echo "              Installation Complete!                 "
echo "====================================================="
echo ""
echo "• Web Control Panel LCD : http://localhost:5000/"
if [ "$INSTALL_OPTION" == "2" ]; then
echo "• Full System Dashboard : http://localhost:5000/dashboard/"
fi
echo ""
echo "Commands:"
echo "  • Check Status : systemctl status thermalright-lcd"
echo "  • View Logs    : journalctl -u thermalright-lcd -f"
echo "====================================================="
