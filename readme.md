## Thermalright LCD Linux Driver

Thermalright LCD Linux Ubuntu Driver Minimal for Thermalright Assassin X 120R Digital CPU cooler LCD.

---

## Features

* Display **CPU temperature**
* Display **GPU temperature**
* Display **Alternating temperature**
* Display **CPU usage mode**
* **Web UI controller**
* Configurable display settings
* Automatic **systemd service**
* **Auto reconnect** if device not ready during boot
* Lightweight and modular architecture

---

## Currently tested with:

* **Cooler:** Thermalright Assassin X 120R Digital
* **CPU:** AMD Ryzen
* **GPU:** AMD Radeon

---

## Web UI

A simple web interface is included for controlling the display settings.

The Web UI allows you to change:

* Display mode
* Temperature unit
* Alternate interval
* LED color

Once saved, the configuration updates automatically without restarting the service.

Default address:

http://localhost:5000
*Port can be changed in the app.py file

---

## Supported Display Modes

```
cpu
gpu
alternate
cpu_usage
```

---

## INSTALLATION

Clone the repository:

```
git clone https://github.com/iqbalfaris24/thermalright-assassin-linux.git
cd thermalright-assassin-linux
```

Run installer:

```
chmod +x install.sh
./install.sh
```

The installer will automatically:

* Create Python virtual environment
* Install dependencies
* Install systemd service
* Install udev rules
* Enable auto start at boot

---

## RUNNING MANUALLY

If you want to run without systemd:

```
python app.py
```

---

## Service Control

Check service status:

```
systemctl status thermalright-lcd
```

Restart service:

```
sudo systemctl restart thermalright-lcd
```

View logs:

```
journalctl -u thermalright-lcd -f
```


---

## CONFIGURATION

The system uses `config.json` as the main configuration file.

Example configuration:

```
{
  "display_mode": "alternate",
  "alternate_interval": 3,
  "temperature_unit": "celsius",
  "hide_leading_zero": true,
  "color": "ffffff",
  "cpu_sensor": "k10temp",
  "gpu_sensor": "amdgpu"
}
```

Configuration changes made from the Web UI are automatically applied without restarting the service.

---
## Acknowledgements

Special thanks to the project below which helped provide insight into the device communication protocol:

https://github.com/raffa0001/Peerless_assassin_and_CLI_UI

---
## FUTURE IDEAS

Possible improvements:

* Temperature based LED color gradient
* LCD brightness control
* Clock display mode
* GPU usage mode

---

## LICENSE

MIT License