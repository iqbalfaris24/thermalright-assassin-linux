NUMBER_OF_LEDS = 84

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

def blank_frame():
    return ["000000"] * NUMBER_OF_LEDS

def get_temp_color(temp, color_map):
    try:
        temp = int(temp)
    except:
        temp = 0

    for item in color_map:
        if temp <= item["max"]:
            c = item.get("color","ffffff")
            if isinstance(c,str) and len(c) == 6:
                return c.lower()

    return "ffffff"

def sanitize_color(color):
    if not isinstance(color,str):
        return "ffffff"

    color = color.lower().replace("#","")

    if len(color) == 3:
        color = "".join([c*2 for c in color])

    if len(color) != 6:
        return "ffffff"

    try:
        int(color,16)
    except:
        return "ffffff"

    return color

def render_value(value, mode="cpu", unit="celsius", color="ffffff", is_usage=False, hide_leading_zero=True):

    frame = ["000000"] * NUMBER_OF_LEDS

    try:
        value = int(value)
    except:
        value = 0

    if value < 0:
        value = 0
    if value > 999:
        value = 999

    color = sanitize_color(color)

    digits = f"{value:03}"

    for i,d in enumerate(digits):

        if hide_leading_zero and i < 2 and d == "0":
            continue

        segs = digit_segments[int(d)]

        for seg in segs:
            idx = digit_map[i][seg]
            frame[idx] = color

    if mode == "cpu":
        frame[2] = color
    elif mode == "gpu":
        frame[4] = color

    if is_usage:
        frame[8] = color
    else:
        if unit == "celsius":
            frame[6] = color
        else:
            frame[7] = color

    return frame