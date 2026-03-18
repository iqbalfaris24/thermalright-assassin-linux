import hid
import psutil
import time

VENDOR_ID = 0x0416
PRODUCT_ID = 0x8001

HEADER = "dadbdcdd000000000000000000000000fc0000ff"
NUMBER_OF_LEDS = 84

dev = hid.Device(VENDOR_ID, PRODUCT_ID)

digit_segments = {
0:["a","b","c","d","e","f"],
1:["b","c"],
2:["a","b","g","e","d"],
3:["a","b","g","c","d"],
4:["f","g","b","c"],
5:["a","f","g","c","d"],
6:["a","f","g","e","c","d"],
7:["a","b","c"],
8:["a","b","c","d","e","f","g"],
9:["a","b","c","d","f","g"],
}

digit_map = [
{"a":9,"b":10,"c":11,"d":12,"e":13,"f":14,"g":15},
{"a":16,"b":17,"c":18,"d":19,"e":20,"f":21,"g":22},
{"a":23,"b":24,"c":25,"d":26,"e":27,"f":28,"g":29},
]


def get_cpu_temp():
    temps = psutil.sensors_temperatures()

    # Ryzen (k10temp)
    if "k10temp" in temps:
        return int(temps["k10temp"][0].current)

    # fallback generic
    for name in temps:
        for entry in temps[name]:
            if entry.current:
                return int(entry.current)

    return 0


def draw_digit(colors, pos, num):
    if num < 0:
        return
    for seg in digit_segments[num]:
        colors[digit_map[pos][seg]] = "ffffff"


def send(colors):
    message = "".join(colors)

    packet0 = bytes.fromhex(HEADER + message[:128-len(HEADER)])
    dev.write(packet0)

    packets = message[88:]
    for i in range(4):
        packet = bytes.fromhex("00" + packets[i*128:(i+1)*128])
        dev.write(packet)


print("Start CPU temp display...")

while True:
    cpu_temp = get_cpu_temp()

    print("CPU:", cpu_temp)

    colors = ["000000"] * NUMBER_OF_LEDS

    # max 3 digit
    cpu_temp = min(cpu_temp, 999)

    digits = f"{cpu_temp:03}"

    for i, d in enumerate(digits):
        if d != "0" or i == 2:  # hide leading zero
            draw_digit(colors, i, int(d))

    # indicator
    colors[2] = "ffffff"  # CPU
    colors[6] = "ffffff"  # °C

    send(colors)

    time.sleep(3)