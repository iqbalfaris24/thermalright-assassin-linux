import json
import os

DEFAULT_CONFIG = {
    "display_mode": "alternate",  # cpu | gpu | alternate
    "alternate_interval": 3,

    "temperature_unit": "celsius",
    "hide_leading_zero": True,

    "cpu_sensor": "k10temp",
    "gpu_sensor": "amdgpu",

    "device": {
        "vendor_id": "0x0416",
        "product_id": "0x8001",
        "led_count": 84
    }
}


def load_config(path="config.json"):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG

    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG