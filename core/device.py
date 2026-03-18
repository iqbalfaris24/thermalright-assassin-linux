import hid
import time

VENDOR_ID = 0x0416
PRODUCT_ID = 0x8001


class Device:
    def __init__(self):
        self.dev = None
        self.connect()

    def connect(self):
        while True:
            try:
                self.dev = hid.Device(VENDOR_ID, PRODUCT_ID)
                print("Device connected")
                break
            except Exception as e:
                print("Waiting for device...", e)
                time.sleep(2)

    def send(self, frame):
        try:
            message = "".join(frame)

            HEADER = "dadbdcdd000000000000000000000000fc0000ff"

            packet0 = bytes.fromhex(HEADER + message[:128-len(HEADER)])
            self.dev.write(packet0)

            packets = message[88:]
            for i in range(4):
                packet = bytes.fromhex("00" + packets[i*128:(i+1)*128])
                self.dev.write(packet)

        except Exception as e:
            print("Device error, reconnecting...", e)
            self.connect()

    def close(self):
        if self.dev:
            self.dev.close()