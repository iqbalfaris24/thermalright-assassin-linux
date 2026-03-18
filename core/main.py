import time
from sensor import get_cpu_temp, get_gpu_temp, get_cpu_usage
from renderer import render_value
from device import Device
from config import load_config

def main():
    device = Device()
    last_config = None

    print("Starting Thermalright LCD...")

    try:
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

            if mode == "cpu":
                cpu_temp = get_cpu_temp(cpu_sensor)
                frame = render_value(cpu_temp, "cpu", unit, color)
                device.send(frame)
                time.sleep(interval)

            elif mode == "gpu":
                gpu_temp = get_gpu_temp(gpu_sensor)
                frame = render_value(gpu_temp, "gpu", unit, color)
                device.send(frame)
                time.sleep(interval)

            elif mode == "cpu_usage":
                val = get_cpu_usage()
                frame = render_value(val, "cpu", unit, color, is_usage=True)
                device.send(frame)
                time.sleep(interval)

            else:
                cpu_temp = get_cpu_temp(cpu_sensor)
                frame = render_value(cpu_temp, "cpu", unit, color)
                device.send(frame)

                time.sleep(interval)

                gpu_temp = get_gpu_temp(gpu_sensor)
                frame = render_value(gpu_temp, "gpu", unit, color)
                device.send(frame)

                time.sleep(interval)

    except KeyboardInterrupt:
        print("Stopping...")
        device.close()


if __name__ == "__main__":
    main()