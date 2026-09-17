from flask import Flask, request, jsonify, render_template, send_from_directory
import json
import os
import threading
import time

from core.device import Device
from core.renderer import render_value, get_temp_color
from core.sensor import get_cpu_temp, get_gpu_temp, get_cpu_usage

# Optional: System Monitor Module (Full Dashboard & WebSocket)
try:
    from flask_socketio import SocketIO
    from flask_cors import CORS
    from core.system_monitor import get_full_system_status
    SOCKETIO_AVAILABLE = True
except ImportError:
    SocketIO = None
    CORS = None
    get_full_system_status = None
    SOCKETIO_AVAILABLE = False

app = Flask(__name__)
if SOCKETIO_AVAILABLE and CORS:
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*")
else:
    socketio = None

CONFIG_FILE = "config.json"
device = None
DASHBOARD_DIST_DIR = os.path.join(os.path.dirname(__file__), "dashboard-ui", "dist")


# =========================
# CONFIG HANDLER
# =========================

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "display_mode": "cpu",
            "alternate_interval": 3,
            "temperature_unit": "celsius",
            "color_mode": "static",
            "color": "ff0000",
            "cpu_sensor": "k10temp",
            "gpu_sensor": "amdgpu",
            "temp_color_map": [
                {"max": 30, "color": "00ffff"},
                {"max": 50, "color": "00ff00"},
                {"max": 70, "color": "ffff00"},
                {"max": 90, "color": "ff8800"},
                {"max": 999, "color": "ff0000"}
            ]
        }
        save_config(default_config)
        return default_config

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# DEVICE CONNECTION
# =========================

def connect_device():
    global device
    try:
        device = Device()
        print("Thermalright LCD connected successfully")
    except Exception as e:
        print("Thermalright LCD not found or failed to connect:", e)
        device = None


# =========================
# LCD LOOP
# =========================

def lcd_loop():
    global device
    connect_device()

    last_switch = time.time()
    current_mode = "cpu"

    while True:
        try:
            config = load_config()
            mode = config.get("display_mode", "cpu")
            alt_interval = config.get("alternate_interval", 3)
            unit = config.get("temperature_unit", "celsius")
            color_mode = config.get("color_mode", "static")
            static_color = config.get("color", "ff0000")
            cpu_sensor = config.get("cpu_sensor", "k10temp")
            gpu_sensor = config.get("gpu_sensor", "amdgpu")

            if mode == "alternate":
                if time.time() - last_switch > alt_interval:
                    current_mode = "gpu" if current_mode == "cpu" else "cpu"
                    last_switch = time.time()
                active_mode = current_mode
            else:
                active_mode = mode

            if active_mode == "cpu":
                value = get_cpu_temp(cpu_sensor)
                mode_type = "cpu"
            elif active_mode == "gpu":
                value = get_gpu_temp(gpu_sensor)
                mode_type = "gpu"
            elif active_mode == "cpu_usage":
                value = get_cpu_usage()
                mode_type = "cpu_usage"
            else:
                value = get_cpu_temp(cpu_sensor)
                mode_type = "cpu"

            if color_mode == "temperature":
                color = get_temp_color(value, config.get("temp_color_map", []))
            else:
                color = static_color

            frame = render_value(value, mode=mode_type, unit=unit, color=color)

            if device:
                device.send(frame)

        except Exception as e:
            print("LCD Loop error:", e)

        time.sleep(1)


# =========================
# WEBSOCKET REALTIME EMITTER
# =========================

def ws_background_thread():
    """Background worker untuk emit status hardware secara realtime via WebSocket"""
    while True:
        try:
            if SOCKETIO_AVAILABLE and socketio and get_full_system_status:
                status = get_full_system_status()
                socketio.emit('status_update', status)
        except Exception as e:
            print("WebSocket background worker error:", e)
        time.sleep(2)


# =========================
# FLASK HTTP ROUTES
# =========================

@app.route("/")
def index():
    config = load_config()
    return render_template("index.html", config=config, full_dashboard=SOCKETIO_AVAILABLE)


@app.route("/config", methods=["GET", "POST"])
def config_api():
    if request.method == "GET":
        return jsonify(load_config())
    data = request.json
    save_config(data)
    return jsonify({"status": "ok"})


@app.route("/api/sensors")
def sensors_api():
    """Real-time sensor data for LCD preview"""
    try:
        config = load_config()
        cpu_sensor = config.get("cpu_sensor", "k10temp")
        gpu_sensor = config.get("gpu_sensor", "amdgpu")
        return jsonify({
            "cpu_temp": get_cpu_temp(cpu_sensor),
            "gpu_temp": get_gpu_temp(gpu_sensor),
            "cpu_usage": get_cpu_usage()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/system")
def system_metrics_api():
    """Endpoint REST JSON lengkap untuk seluruh status sistem"""
    if get_full_system_status:
        return jsonify(get_full_system_status())
    return jsonify({"error": "Full system monitor module not loaded"}), 404


# =========================
# DASHBOARD SPA ROUTES (VITE)
# =========================

@app.route("/dashboard")
@app.route("/dashboard/")
def serve_dashboard_root():
    return send_from_directory(DASHBOARD_DIST_DIR, "index.html")

@app.route("/dashboard/<path:filename>")
def serve_dashboard_static(filename):
    file_path = os.path.join(DASHBOARD_DIST_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(DASHBOARD_DIST_DIR, filename)
    return send_from_directory(DASHBOARD_DIST_DIR, "index.html")


# =========================
# SOCKETIO EVENT HANDLERS
# =========================

if SOCKETIO_AVAILABLE and socketio:
    @socketio.on('connect')
    def handle_ws_connect():
        print("WebSocket client connected to Thermalright Dashboard")
        if get_full_system_status:
            socketio.emit('status_update', get_full_system_status())

    @socketio.on('disconnect')
    def handle_ws_disconnect():
        print("WebSocket client disconnected")


# =========================
# MAIN ENTRY
# =========================

def start_background_workers():
    # LCD hardware background thread
    lcd_thread = threading.Thread(target=lcd_loop, daemon=True)
    lcd_thread.start()

    # WebSocket status update thread (jika SocketIO aktif)
    if SOCKETIO_AVAILABLE:
        ws_thread = threading.Thread(target=ws_background_thread, daemon=True)
        ws_thread.start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Thermalright Service on port {port} (Full Suite: {SOCKETIO_AVAILABLE})")
    start_background_workers()

    if SOCKETIO_AVAILABLE and socketio:
        socketio.run(app, host="0.0.0.0", port=port, debug=False, allow_unsafe_werkzeug=True)
    else:
        app.run(host="0.0.0.0", port=port, debug=False)
