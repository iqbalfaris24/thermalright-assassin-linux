import psutil


def get_cpu_temp(sensor_name="k10temp"):
    temps = psutil.sensors_temperatures()

    if sensor_name in temps:
        return int(temps[sensor_name][0].current)

    for name in temps:
        for entry in temps[name]:
            if entry.current:
                return int(entry.current)

    return 0


def get_gpu_temp(sensor_name="amdgpu"):
    temps = psutil.sensors_temperatures()

    if sensor_name in temps:
        return int(temps[sensor_name][0].current)

    return 0

def get_cpu_usage():
    return int(psutil.cpu_percent(interval=None))

def get_gpu_usage():
    # basic fallback (AMD belum selalu support usage via psutil)
    return 0
