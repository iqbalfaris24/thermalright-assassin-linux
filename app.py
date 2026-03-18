from flask import Flask, request, jsonify
import threading
import time
import json

from core.sensor import get_cpu_temp, get_gpu_temp, get_cpu_usage
from core.renderer import render_value
from core.device import Device
from core.config import load_config

app = Flask(__name__)
device = Device()

CONFIG_FILE = "config.json"


# =========================
# LCD LOOP (BACKGROUND)
# =========================
def lcd_loop():
    last_config = None

    while True:
        config = load_config()

        if config != last_config:
            print("Config updated:", config)
            last_config = config

        mode = config.get("display_mode", "alternate")
        interval = config.get("alternate_interval", 3)
        unit = config.get("temperature_unit", "celsius")
        color = config.get("color", "ffffff")
        cpu_sensor = config.get("cpu_sensor", "k10temp")
        gpu_sensor = config.get("gpu_sensor", "amdgpu")

        try:
            if mode == "cpu":
                val = get_cpu_temp(cpu_sensor)
                frame = render_value(val, "cpu", unit, color)
                device.send(frame)

            elif mode == "gpu":
                val = get_gpu_temp(gpu_sensor)
                frame = render_value(val, "gpu", unit, color)
                device.send(frame)

            elif mode == "cpu_usage":
                val = get_cpu_usage()
                frame = render_value(val, "cpu", unit, color, is_usage=True)
                device.send(frame)

            else:
                val = get_cpu_temp(cpu_sensor)
                frame = render_value(val, "cpu", unit, color)
                device.send(frame)

                time.sleep(interval)

                val = get_gpu_temp(gpu_sensor)
                frame = render_value(val, "gpu", unit, color)
                device.send(frame)

        except Exception as e:
            print("Loop error:", e)

        time.sleep(interval)


# =========================
# WEB API
# =========================
def load_cfg():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_cfg(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/config", methods=["GET"])
def get_config():
    return jsonify(load_cfg())


@app.route("/config", methods=["POST"])
def update_config():
    data = request.json
    save_cfg(data)
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Thermalright LCD Control</title>
            <style>
                :root {
                    --primary: #6366f1;
                    --primary-hover: #4f46e5;
                    --bg-gradient: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
                }
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: var(--bg-gradient);
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }
                .container {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 30px 40px;
                    border-radius: 16px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    width: 100%;
                    max-width: 350px;
                }
                h2 {
                    text-align: center;
                    color: #1f2937;
                    margin-top: 0;
                    margin-bottom: 25px;
                    font-weight: 700;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                label {
                    display: block;
                    font-size: 14px;
                    font-weight: 600;
                    color: #4b5563;
                    margin-bottom: 8px;
                }
                select, input[type="number"], input[type="text"] {
                    width: 100%;
                    padding: 10px 12px;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    font-size: 15px;
                    box-sizing: border-box;
                    outline: none;
                    transition: border-color 0.2s;
                }
                select:focus, input[type="number"]:focus, input[type="text"]:focus {
                    border-color: var(--primary);
                }
                .color-picker-wrapper {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                input[type="color"] {
                    -webkit-appearance: none;
                    border: none;
                    width: 45px;
                    height: 45px;
                    border-radius: 8px;
                    cursor: pointer;
                    padding: 0;
                    background: none;
                }
                input[type="color"]::-webkit-color-swatch-wrapper {
                    padding: 0;
                }
                input[type="color"]::-webkit-color-swatch {
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                }
                .hex-input {
                    display: flex;
                    align-items: center;
                    flex-grow: 1;
                    border: 1px solid #d1d5db;
                    border-radius: 8px;
                    padding: 0 12px;
                    background: white;
                }
                .hex-input span {
                    color: #6b7280;
                    font-weight: bold;
                }
                .hex-input input {
                    border: none;
                    padding-left: 5px;
                    font-family: monospace;
                    text-transform: uppercase;
                }
                .hex-input input:focus {
                    border: none;
                    outline: none;
                }
                .hex-input:focus-within {
                    border-color: var(--primary);
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background-color: var(--primary);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background-color 0.2s, transform 0.1s;
                    margin-top: 10px;
                }
                button:hover {
                    background-color: var(--primary-hover);
                }
                button:active {
                    transform: scale(0.98);
                }
            </style>
        </head>
        <body>

            <div class="container">
                <h2>Thermalright LCD</h2>

                <form id="form">
                    <div class="form-group">
                        <label>Display Mode</label>
                        <select id="display_mode">
                            <option value="cpu">CPU Temperature</option>
                            <option value="gpu">GPU Temperature</option>
                            <option value="alternate">Alternate Temperature</option>
                            <option value="cpu_usage">CPU Usage</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Alternate Interval (s)</label>
                        <input id="alternate_interval" type="number" value="3" min="1"/>
                    </div>

                    <div class="form-group">
                        <label>Temperature Unit</label>
                        <select id="temperature_unit">
                            <option value="celsius">Celsius</option>
                            <option value="fahrenheit">Fahrenheit</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Theme Color</label>
                        <div class="color-picker-wrapper">
                            <input type="color" id="colorPicker" value="#ffffff">
                            <div class="hex-input">
                                <span>#</span>
                                <input type="text" id="colorText" value="ffffff" maxlength="6">
                            </div>
                        </div>
                    </div>

                    <button type="button" onclick="saveData()">Save Settings</button>
                </form>
            </div>

            <script>
            // Sinkronisasi Color Picker ke Text Input
            const colorPicker = document.getElementById('colorPicker');
            const colorText = document.getElementById('colorText');

            colorPicker.addEventListener('input', function() {
                colorText.value = this.value.substring(1).toLowerCase();
            });

            // Sinkronisasi Text Input ke Color Picker
            colorText.addEventListener('input', function() {
                let hex = this.value;
                // Validasi format hex (hanya biarkan karakter hex yang valid)
                hex = hex.replace(/[^0-9a-fA-F]/g, '');
                this.value = hex;
                
                if (hex.length === 6) {
                    colorPicker.value = '#' + hex;
                }
            });

            async function saveData() {
                const btn = document.querySelector('button');
                const originalText = btn.innerText;
                btn.innerText = "Saving...";

                const data = {
                    display_mode: document.getElementById('display_mode').value,
                    alternate_interval: parseInt(document.getElementById('alternate_interval').value),
                    temperature_unit: document.getElementById('temperature_unit').value,
                    color: colorText.value, // Mengirimkan nilai hex tanpa '#' sesuai script aslinya
                    cpu_sensor: "k10temp",
                    gpu_sensor: "amdgpu"
                };

                try {
                    await fetch('/config', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    btn.innerText = "Saved!";
                    btn.style.backgroundColor = "#10b981"; // Ubah tombol jadi hijau
                    
                    setTimeout(() => {
                        btn.innerText = originalText;
                        btn.style.backgroundColor = "";
                    }, 2000);
                } catch (error) {
                    alert("Failed to save data!");
                    btn.innerText = originalText;
                }
            }
            </script>
        </body>
        </html>
        """

# =========================
# START
# =========================
if __name__ == "__main__":
    t = threading.Thread(target=lcd_loop, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=5000)