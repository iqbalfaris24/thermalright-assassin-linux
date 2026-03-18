import hid
import time

VENDOR_ID = 0x0416
PRODUCT_ID = 0x8001

HEADER = "dadbdcdd000000000000000000000000fc0000ff"
NUMBER_OF_LEDS = 84

dev = hid.Device(VENDOR_ID, PRODUCT_ID)

def send(colors):
    message = "".join(colors)
    packet0 = bytes.fromhex(HEADER + message[:128-len(HEADER)])
    dev.write(packet0)

    packets = message[88:]
    for i in range(4):
        packet = bytes.fromhex("00" + packets[i*128:(i+1)*128])
        dev.write(packet)


print("Start inverse mapping...")

for i in range(30):
    # semua nyala putih
    colors = ["ffffff"] * NUMBER_OF_LEDS

    # matikan 1 LED
    colors[i] = "000000"

    send(colors)

    print(f"LED {i} (OFF)")
    time.sleep(4)

dev.close()