import hid

VENDOR_ID = 0x0416
PRODUCT_ID = 0x8001

HEADER = "dadbdcdd000000000000000000000000fc0000ff"
NUMBER_OF_LEDS = 84

dev = hid.Device(VENDOR_ID, PRODUCT_ID)

colors = ["000000"] * NUMBER_OF_LEDS

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

def draw_digit(pos, num):
    for seg in digit_segments[num]:
        colors[digit_map[pos][seg]] = "ffffff"

# tampilkan 34
draw_digit(1,3)
draw_digit(2,4)

# indicator
colors[2] = "ffffff"   # CPU
colors[6] = "ffffff"   # Celsius

message = "".join(colors)

packet0 = bytes.fromhex(HEADER + message[:128-len(HEADER)])
dev.write(packet0)

packets = message[88:]

for i in range(4):
    packet = bytes.fromhex("00" + packets[i*128:(i+1)*128])
    dev.write(packet)

dev.close()