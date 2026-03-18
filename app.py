from flask import Flask, request, jsonify, render_template
import json
import os
import threading
import time

from core.device import Device
from core.renderer import render_value
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
            "color": "ff0000",
            "cpu_sensor": "k10temp",
            "gpu_sensor": "amdgpu"
        }

        save_config(default_config)
        return default_config

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# LCD DRIVER LOOP
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
            color = config.get("color", "ff0000")

            cpu_sensor = config.get("cpu_sensor", "k10temp")
            gpu_sensor = config.get("gpu_sensor", "amdgpu")

            # -----------------
            # CPU TEMP
            # -----------------
            if mode == "cpu":

                val = get_cpu_temp(cpu_sensor)

                frame = render_value(
                    value=val,
                    mode="cpu",
                    unit=unit,
                    color=color
                )

                device.send(frame)

                time.sleep(interval)

            # -----------------
            # GPU TEMP
            # -----------------
            elif mode == "gpu":

                val = get_gpu_temp(gpu_sensor)

                frame = render_value(
                    value=val,
                    mode="gpu",
                    unit=unit,
                    color=color
                )

                device.send(frame)

                time.sleep(interval)

            # -----------------
            # CPU USAGE
            # -----------------
            elif mode == "cpu_usage":

                val = get_cpu_usage()

                frame = render_value(
                    value=val,
                    mode="cpu",
                    unit=unit,
                    color=color,
                    is_usage=True
                )

                device.send(frame)

                time.sleep(interval)

            # -----------------
            # ALTERNATE MODE
            # -----------------
            else:

                cpu_temp = get_cpu_temp(cpu_sensor)

                frame = render_value(
                    value=cpu_temp,
                    mode="cpu",
                    unit=unit,
                    color=color
                )

                device.send(frame)

                time.sleep(interval)

                gpu_temp = get_gpu_temp(gpu_sensor)

                frame = render_value(
                    value=gpu_temp,
                    mode="gpu",
                    unit=unit,
                    color=color
                )

                device.send(frame)

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
# START APP
# =========================

def start_background():

    thread = threading.Thread(
        target=lcd_loop,
        daemon=True
    )

    thread.start()


if __name__ == "__main__":

    print("Starting Thermalright LCD Service")

    start_background()

    app.run(
        host="0.0.0.0",
        port=5000
    )