import psutil
import glob
import os
import time
import shutil
import platform
import subprocess

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

_system_info_cache = {}


def get_cpu_info():
    """Mengambil informasi processor"""
    if 'processor' in _system_info_cache:
        return _system_info_cache['processor']

    brand_cpu = "CPU"
    try:
        if cpuinfo:
            info = cpuinfo.get_cpu_info()
            brand_cpu = info.get('brand_raw', platform.processor() or 'AMD / Intel Processor')
        else:
            brand_cpu = platform.processor() or 'CPU'
    except Exception:
        brand_cpu = platform.processor() or 'CPU'

    _system_info_cache['processor'] = brand_cpu
    return brand_cpu


def get_os_info():
    """Mengambil data OS lengkap (Distro name, version, kernel, hostname)"""
    if 'os_pretty' in _system_info_cache:
        return _system_info_cache

    os_name = "Linux"
    os_pretty = ""
    os_version_id = ""
    try:
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release') as f:
                lines = f.readlines()
                info = {}
                for line in lines:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        info[k] = v.strip('"\'')
                os_pretty = info.get('PRETTY_NAME', '')
                os_name = info.get('NAME', 'Linux')
                os_version_id = info.get('VERSION_ID', '')
    except Exception:
        pass

    kernel = platform.release()
    hostname = platform.node()

    _system_info_cache.update({
        'os': os_name,
        'os_pretty': os_pretty or f"{os_name} ({kernel})",
        'os_version': os_version_id,
        'kernel': kernel,
        'hostname': hostname,
    })
    return _system_info_cache


def get_uptime_data():
    """Menghitung waktu aktif sistem (Uptime)"""
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    days = int(uptime_seconds // (24 * 3600))
    hours = int((uptime_seconds % (24 * 3600)) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    return {
        'days': days,
        'hours': hours,
        'minutes': minutes,
        'seconds': int(uptime_seconds)
    }


def get_gpu_status():
    """Deteksi GPU AMD, Intel, atau NVIDIA"""
    gpu_data = {
        'name': 'AMD Radeon RX 580 / 570 Series',
        'vendor': 'AMD',
        'usage_percent': 0,
        'temperature': 0,
        'memory_percent': 0,
        'memory_used': 0,
        'memory_total': 0,
        'power_watts': 0,
        'clock_mhz': 0,
        'is_available': False
    }

    try:
        # Cek sysfs amdgpu
        busy_files = glob.glob('/sys/class/drm/card*/device/gpu_busy_percent')
        if busy_files:
            with open(busy_files[0], 'r') as f:
                gpu_data['usage_percent'] = int(f.read().strip())
                gpu_data['is_available'] = True

        mem_busy_files = glob.glob('/sys/class/drm/card*/device/mem_busy_percent')
        if mem_busy_files:
            with open(mem_busy_files[0], 'r') as f:
                gpu_data['memory_percent'] = int(f.read().strip())

        hwmon_paths = glob.glob('/sys/class/drm/card*/device/hwmon/hwmon*')
        if hwmon_paths:
            hw = hwmon_paths[0]
            temp_file = os.path.join(hw, 'temp1_input')
            if os.path.exists(temp_file):
                with open(temp_file, 'r') as f:
                    gpu_data['temperature'] = round(int(f.read().strip()) / 1000.0, 1)

            power_file = os.path.join(hw, 'power1_input')
            if os.path.exists(power_file):
                with open(power_file, 'r') as f:
                    gpu_data['power_watts'] = round(int(f.read().strip()) / 1000000.0, 1)

            freq_file = os.path.join(hw, 'freq1_input')
            if os.path.exists(freq_file):
                with open(freq_file, 'r') as f:
                    gpu_data['clock_mhz'] = int(int(f.read().strip()) / 1000000.0)

        if gpu_data['temperature'] == 0:
            temps = psutil.sensors_temperatures()
            if 'amdgpu' in temps and temps['amdgpu']:
                gpu_data['temperature'] = round(temps['amdgpu'][0].current, 1)
                gpu_data['is_available'] = True

    except Exception:
        pass

    if not gpu_data['is_available']:
        try:
            if shutil.which('nvidia-smi'):
                out = subprocess.run(
                    ['nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'],
                    capture_output=True, text=True, timeout=2
                ).stdout.strip()
                if out:
                    parts = [p.strip() for p in out.split(',')]
                    if len(parts) >= 5:
                        gpu_data['name'] = parts[0]
                        gpu_data['vendor'] = 'NVIDIA'
                        gpu_data['usage_percent'] = float(parts[1])
                        gpu_data['temperature'] = float(parts[2])
                        gpu_data['memory_used'] = round(float(parts[3]) / 1024, 2)
                        gpu_data['memory_total'] = round(float(parts[4]) / 1024, 2)
                        gpu_data['memory_percent'] = round((gpu_data['memory_used'] / gpu_data['memory_total']) * 100, 1)
                        gpu_data['is_available'] = True
        except Exception:
            pass

    return gpu_data


def get_all_storage_disks():
    """Autodetect dan filter seluruh physical storage & mounted partitions"""
    disks = []
    seen_mounts = set()
    ignored_fs = {'squashfs', 'tmpfs', 'devtmpfs', 'overlay', 'iso9660', 'ramfs'}
    ignored_mount_prefixes = {'/snap', '/var/lib/docker', '/run', '/sys', '/proc', '/dev'}

    for part in psutil.disk_partitions(all=False):
        if part.fstype in ignored_fs:
            continue
        if any(part.mountpoint.startswith(p) for p in ignored_mount_prefixes):
            continue
        if part.mountpoint in seen_mounts:
            continue

        try:
            usage = psutil.disk_usage(part.mountpoint)
            total_gb = usage.total / (1024**3)
            if total_gb < 0.5 and part.mountpoint != '/':
                continue

            label = part.mountpoint
            if part.mountpoint == '/':
                label = 'System Root (/)'
            elif part.mountpoint.startswith('/mnt/'):
                label = part.mountpoint.replace('/mnt/', '')
            elif part.mountpoint.startswith('/media/'):
                label = part.mountpoint.replace('/media/', '')

            disks.append({
                'device': part.device,
                'mount': part.mountpoint,
                'label': label,
                'fstype': part.fstype,
                'total': f"{total_gb:.2f}",
                'used': f"{(usage.used / (1024**3)):.2f}",
                'free': f"{(usage.free / (1024**3)):.2f}",
                'percent': round(usage.percent, 1)
            })
            seen_mounts.add(part.mountpoint)
        except Exception:
            continue

    disks.sort(key=lambda d: 0 if d['mount'] == '/' else 1)
    return disks


def get_full_system_status():
    """Mengumpulkan snapshot metrik sistem lengkap untuk WebSocket / Dashboard"""
    cpu_freq = psutil.cpu_freq()
    current_freq = (cpu_freq.current / 1000) if cpu_freq else 0.0
    min_freq = (cpu_freq.min / 1000) if (cpu_freq and cpu_freq.min) else 0.0
    max_freq = (cpu_freq.max / 1000) if (cpu_freq and cpu_freq.max) else 1.0

    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)
    load_avg = [round(x, 2) for x in psutil.getloadavg()] if hasattr(psutil, "getloadavg") else [0, 0, 0]

    # Sensor Suhu CPU (AMD k10temp / Intel coretemp / fallback)
    cpu_temp = "N/A"
    try:
        temps = psutil.sensors_temperatures()
        if 'k10temp' in temps and temps['k10temp']:
            cpu_temp = temps['k10temp'][0].current
        elif 'coretemp' in temps and temps['coretemp']:
            cpu_temp = temps['coretemp'][0].current
        else:
            for s_name, entries in temps.items():
                if entries and entries[0].current is not None:
                    cpu_temp = entries[0].current
                    break
    except Exception:
        pass

    # RAM & Swap
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Root Disk
    root_disk = psutil.disk_usage('/')

    # All Partitions & GPU
    all_disks = get_all_storage_disks()
    gpu = get_gpu_status()
    os_info = get_os_info()
    uptime = get_uptime_data()
    processor = get_cpu_info()

    return {
        'cpu': {
            'processor': processor,
            'current': f"{current_freq:.2f}",
            'min': f"{min_freq:.2f}",
            'max': f"{max_freq:.2f}",
            'temperature': f"{cpu_temp:.1f}" if isinstance(cpu_temp, (int, float)) else str(cpu_temp),
            'percent': round(cpu_percent, 1),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'load_avg': load_avg,
            'per_core': [round(p, 1) for p in cpu_percent_per_core],
        },
        'gpu': gpu,
        'memory': {
            'percent': round(mem.percent, 1),
            'total': f"{(mem.total / (1024**3)):.2f}",
            'used': f"{(mem.used / (1024**3)):.2f}",
            'available': f"{(mem.available / (1024**3)):.2f}",
            'swap_used': f"{(swap.used / (1024**3)):.2f}",
            'swap_total': f"{(swap.total / (1024**3)):.2f}",
            'swap_percent': round(swap.percent, 1),
        },
        'storage': {
            'percent': round(root_disk.percent, 1),
            'total': f"{(root_disk.total / (1024**3)):.2f}",
            'used': f"{(root_disk.used / (1024**3)):.2f}",
            'free': f"{(root_disk.free / (1024**3)):.2f}",
        },
        'disks': all_disks,
        'system_info': {
            'uptime': uptime,
            'os': os_info['os'],
            'os_pretty': os_info['os_pretty'],
            'os_version': os_info['os_version'],
            'kernel': os_info['kernel'],
            'hostname': os_info['hostname'],
        }
    }
