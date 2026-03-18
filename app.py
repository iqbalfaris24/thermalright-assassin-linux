from flask import Flask, request, jsonify, render_template
import json
import os
import threading
import time

from core.device import Device
from core.renderer import render_value, get_temp_color
from core.sensor import get_cpu_temp, get_gpu_temp, get_cpu_usage

app = Flask(__name__)

CONFIG_FILE = "config.json"
device = None


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

    while device is None:

        try:

            device = Device()

            print("LCD device connected")

        except Exception as e:

            print("Device not ready, retrying...", e)

            time.sleep(5)


# =========================
# COLOR RESOLVER
# =========================

def resolve_color(value, config):

    mode = config.get("color_mode", "static")

    if mode == "temperature":

        return get_temp_color(
            value,
            config.get("temp_color_map", [])
        )

    return config.get("color", "ff0000")


# =========================
# RENDER HELPER
# =========================

def render_and_send(value, mode, unit, color):

    frame = render_value(
        value=value,
        mode=mode,
        unit=unit,
        color=color
    )

    device.send(frame)


# =========================
# LCD DRIVER LOOP
# =========================

def lcd_loop():

    global device

    connect_device()

    last_config = None

    while True:

        try:

            config = load_config()

            if config != last_config:

                print("Config updated:", config)

                last_config = config

            mode = config.get("display_mode", "cpu")
            interval = config.get("alternate_interval", 3)
            unit = config.get("temperature_unit", "celsius")

            cpu_sensor = config.get("cpu_sensor", "k10temp")
            gpu_sensor = config.get("gpu_sensor", "amdgpu")


            # =========================
            # CPU MODE
            # =========================

            if mode == "cpu":

                val = get_cpu_temp(cpu_sensor)

                color = resolve_color(val, config)

                render_and_send(val, "cpu", unit, color)

                time.sleep(interval)


            # =========================
            # GPU MODE
            # =========================

            elif mode == "gpu":

                val = get_gpu_temp(gpu_sensor)

                color = resolve_color(val, config)

                render_and_send(val, "gpu", unit, color)

                time.sleep(interval)


            # =========================
            # CPU USAGE
            # =========================

            elif mode == "cpu_usage":

                val = get_cpu_usage()

                color = config.get("color", "ff0000")

                frame = render_value(
                    value=val,
                    mode="cpu",
                    unit=unit,
                    color=color,
                    is_usage=True
                )

                device.send(frame)

                time.sleep(interval)


            # =========================
            # ALTERNATE MODE
            # =========================

            else:

                cpu_temp = get_cpu_temp(cpu_sensor)

                cpu_color = resolve_color(cpu_temp, config)

                render_and_send(cpu_temp, "cpu", unit, cpu_color)

                time.sleep(interval)

                gpu_temp = get_gpu_temp(gpu_sensor)

                gpu_color = resolve_color(gpu_temp, config)

                render_and_send(gpu_temp, "gpu", unit, gpu_color)

                time.sleep(interval)


        except Exception as e:

            print("LCD loop error:", e)

            device = None

            connect_device()


# =========================
# WEB ROUTES
# =========================

@app.route("/")
def index():

    config = load_config()

    return render_template(
        "index.html",
        config=config
    )


@app.route("/config", methods=["GET", "POST"])
def config_api():

    if request.method == "GET":

        return jsonify(load_config())

    data = request.json

    save_config(data)

    return jsonify({"status": "ok"})


# =========================
# START BACKGROUND THREAD
# =========================

def start_background():

    thread = threading.Thread(
        target=lcd_loop,
        daemon=True
    )

    thread.start()


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("Starting Thermalright LCD Service")

    start_background()

    app.run(
        host="0.0.0.0",
        port=5000,
        # debug=True,
        # use_reloader=True
    )