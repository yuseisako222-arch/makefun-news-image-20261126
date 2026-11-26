"""Render the 26 November world news front page as PNG on standard output."""

import sys
from functools import lru_cache
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, PngImagePlugin
except ModuleNotFoundError as exc:
    if exc.name == "PIL":
        sys.exit(69)
    raise


TITLE = "THE WORLD IN ONE DAY"
DATE = "THURSDAY · 26 NOVEMBER 2026"
DEK = "Eight stories, one page — the day the world happened."

# Each entry supplies the place, headline, and body printed on the page.
STORIES = [
    (
        "Egypt",
        "FUEL TANKER FIRE KILLS AT LEAST 30 ON CAIRO RING ROAD",
        "A fuel tanker overturned and caught fire on Cairo's ring road in the Al-Warraq area of Giza on Wednesday, killing at least 30 people and injuring more than a dozen, Egypt's health ministry said.",
    ),
    (
        "United States",
        "US PROPOSES NEW TARIFFS ON 14 TRADING PARTNERS",
        "The United States proposed new country-specific tariffs on 14 trading partners, including China, the European Union, Japan and India, a move that would lift total US tariffs on Chinese goods to about 45 percent. Japan protested its new rate.",
    ),
    (
        "Saudi Arabia",
        "HOUTHIS CLAIM ATTACK ON SAUDI REFINERY AT RAS TANURA",
        "Yemen's Houthis said they attacked Saudi Arabia's Ras Tanura refinery and Jizan port, while the Saudi-led coalition said it intercepted the attacks following its strike on Hodeidah. Oil prices climbed on supply worries.",
    ),
    (
        "Ukraine",
        "UKRAINE HITS RUSSIAN AIRBASE AS MISSILES STRIKE KYIV",
        "Ukraine said its strike on Russia's Savasleyka airbase in the Nizhny Novgorod region hit five military jets, as Russian ballistic missiles struck Kyiv, hitting a shopping mall and injuring seven people.",
    ),
    (
        "Sudan",
        "RSF DRONE ATTACKS KILL AT LEAST 19 IN SUDAN'S BLUE NILE",
        "Drone attacks by Sudan's paramilitary Rapid Support Forces killed at least 19 people in Blue Nile state, a rights group said, in the latest strike of the country's civil war.",
    ),
    (
        "North Korea",
        "KIM VOWS MORE NUCLEAR WEAPONS AFTER SNUBBING TRUMP",
        "North Korean leader Kim Jong Un inspected nuclear materials production facilities and vowed to build more nuclear weapons, state media said, after ignoring a diplomatic overture from US President Donald Trump.",
    ),
    (
        "Colombia",
        "ABOUT 30 HOSTAGES RESCUED AFTER CARTAGENA STANDOFF",
        "Colombian police rescued about 30 hostages after an 18-hour standoff in the Caribbean city of Cartagena, officials said. One gunman was killed in the operation.",
    ),
    (
        "SPACE",
        "SPACE: FIRST FOREIGN ASTRONAUT BOARDS TIANGONG",
        "Pakistan's Muhammad Zeeshan Ali boarded China's Tiangong space station after arriving aboard Shenzhou 24, becoming the first foreign astronaut to join the station — a milestone Pakistan celebrated as its first person in orbit.",
    ),
]

# City, longitude, latitude, badge center, and side for the city label.
PINS = [
    ("Cairo", 31.24, 30.04, (552, 221), "left"),
    ("Washington", -77.04, 38.90, (277, 194), "left"),
    ("Ras Tanura", 50.16, 26.64, (674, 243), "right"),
    ("Kyiv", 30.52, 50.45, (623, 178), "right"),
    ("Damazin", 34.36, 11.79, (628, 279), "right"),
    ("Pyongyang", 125.75, 39.03, (864, 199), "right"),
    ("Cartagena", -75.55, 10.42, (280, 267), "left"),
]

FIGURES = [
    ("KILLED IN CAIRO TANKER FIRE", "30+"),
    ("TRADING PARTNERS FACING NEW US TARIFFS", "14"),
    ("KILLED IN SUDAN DRONE ATTACKS", "19+"),
    ("HOSTAGES RESCUED IN CARTAGENA", "30"),
    ("RUSSIAN JETS HIT AT SAVASLEYKA", "5"),
]

TICKER = [
    "SAUDI-LED COALITION SAYS IT INTERCEPTED HOUTHI ATTACKS AFTER HODEIDAH STRIKE",
    "EXPLOSION NEAR TANKER WEST OF DUBAI; CREW SAFE, CAUSE UNKNOWN",
    "TWO LIBYAN SOLDIERS KILLED IN UKRAINIAN ATTACK ON RUSSIAN VESSELS IN BENGHAZI",
    "MUSK PLEDGES TWO SPACEX SHARES FOR EVERY CHILD IN AMERICA",
    "NEARLY 300,000 US CUSTOMERS WITHOUT POWER AS OUTAGES SPREAD",
    "SIX DEAD IN PLANE CRASH OFF SOUTHERN US COAST, COAST GUARD SAYS",
    "SOLOMON ISLANDS AND AUSTRALIA SIGN DEAL BARRING FOREIGN BASES",
    "OVER 20 TRAPPED IN FLOODED ILLEGAL GOLD MINE IN INDONESIA",
    "NORTH KOREA ORDERS SWISS DIPLOMATIC OFFICE IN PYONGYANG CLOSED",
    "LIVERPOOL BEAT CLUB BRUGGE 3-0 IN THE CHAMPIONS LEAGUE",
]

# Simplified exterior coastlines. Each group is a ring of lon/lat pairs.
LAND = """
-179 54  -166 56  -158 58  -151 58  -141 60  -134 58  -129 53
-124 49  -124 42  -121 37  -117 33  -113 29  -110 24  -113 28
-114 31  -108 30  -105 24  -101 20  -93 17  -88 20  -87 16
-83 12  -79 9  -83 9  -88 14  -94 17  -97 21  -97 27
-90 29  -84 30  -81 26  -80 29  -81 32  -76 35  -74 40
-69 42  -66 45  -61 46  -65 48  -60 51  -62 55  -65 59
-72 62  -78 60  -78 55  -82 53  -86 55  -90 57  -95 61
-90 65  -94 68  -102 69  -110 68  -117 70  -127 70  -135 69
-145 70  -155 71  -164 69  -168 66  -163 63  -166 60  -175 56

-121 72  -114 76  -106 78  -97 77  -103 73  -113 72
-121 72

-92 81  -82 83  -68 82  -64 79  -74 76  -84 77

-83 73  -75 74  -65 70  -65 65  -73 67  -79 69

-73 78  -61 81  -45 83  -28 82  -17 80  -23 73  -24 69
-33 66  -43 60  -52 65  -54 71  -65 76

-82 23  -77 22  -74 20  -79 20  -84 22

-74 20  -70 20  -68 18  -73 18

-80 9  -75 11  -71 12  -67 10  -60 9  -54 6  -51 3
-49 0  -44 -2  -38 -4  -35 -6  -37 -13  -39 -18  -42 -23
-46 -25  -49 -29  -53 -33  -58 -36  -58 -40  -63 -43
-65 -48  -68 -55  -73 -53  -75 -49  -74 -43  -73 -38
-72 -33  -71 -28  -70 -19  -75 -15  -79 -8  -81 -4  -79 1

-17 15  -16 21  -12 26  -10 31  -5 36  1 36  9 37  11 33
16 31  21 32  27 31  33 31  35 26  39 20  43 12  51 12
50 8  45 2  42 -3  40 -10  40 -15  36 -19  35 -24  32 -29
27 -34  20 -35  16 -30  14 -24  12 -17  13 -12  12 -7
9 -3  9 3  5 5  0 5  -7 4  -12 8

50 -13  50 -17  48 -22  45 -26  43 -23  44 -18  47 -15

-9 36  -9 43  -2 44  -5 48  1 50  5 52  9 54  10 57
8 58  6 62  13 66  20 70  30 71  34 67  43 67  46 69
55 69  62 71  70 73  81 73  92 76  104 77  112 73
126 72  143 73  154 71  166 70  180 68  180 64  171 62
161 60  163 57  157 51  155 53  156 58  150 59  142 56
137 50  136 46  131 43  129 40  129 36  126 35  125 39
121 40  119 38  122 36  121 31  119 27  116 23  109 21
107 18  109 13  107 9  104 10  100 13  99 9  103 2
100 4  98 9  96 15  93 17  91 21  87 22  83 19  80 15
78 8  75 12  73 19  69 22  67 25  61 25  57 26  52 27
48 30  49 27  53 25  57 24  59 22  56 18  52 16  44 13
42 17  40 21  37 26  35 29  35 33  36 36  31 36  27 37
26 40  31 42  37 42  40 44  37 47  33 45  29 46  27 42
24 40  24 37  21 37  20 40  16 44  13 45  15 42  18 40
16 38  13 41  10 44  7 44  3 43  0 40  -1 37

-180 64  -172 66  -169 67  -175 69  -180 69

-24 64  -22 66  -17 67  -14 65  -17 63

-7 50  1 51  1 54  -3 56  -3 59  -6 58  -5 55  -4 53

-10 52  -10 55  -6 55  -6 52  -8 51

130 32  135 34  138 35  140 39  142 43  145 44  146 42
143 41  142 36  139 34  134 33

120 25  122 25  121 22  120 22

120 19  123 17  124 13  126 8  123 7  121 11

95 6  100 3  106 -5  104 -6  100 -3  97 1

105 -6  111 -7  115 -8  114 -9  109 -8

109 2  114 4  118 7  119 3  116 -4  112 -3  109 -1

119 1  124 2  125 0  122 -1  123 -4  120 -5

131 -1  138 -2  144 -4  150 -7  151 -10  147 -9  142 -4  135 -4

80 9  82 7  81 6  80 6

113 -23  116 -20  122 -19  125 -16  129 -15  132 -12  136 -12
138 -17  141 -17  143 -11  146 -16  149 -21  153 -27  151 -32
150 -36  146 -39  141 -38  138 -35  134 -34  130 -32  125 -32
121 -34  115 -35  114 -30

144 -41  148 -41  147 -44  145 -43

172 -34  176 -36  179 -38  175 -41  174 -39

166 -46  168 -44  173 -41  174 -42  171 -45  168 -47
"""

SIZE = 1024
SCALE = 2
LEFT, RIGHT = 30, 994
PAPER = "#faf6e9"
INK = "#122932"
BODY = "#283f47"
NAVY = "#142d38"
GRID = "#264652"
DOTS = "#6d8e92"
GOLD = "#ffd383"
RUST = "#963b2b"
RULE = "#bdbbac"
FONT_ROOT = Path("/usr/share/fonts/truetype")
FONT_FILES = {
    "serif": "liberation/LiberationSerif-Bold.ttf",
    "heavy": "lato/Lato-Heavy.ttf",
    "bold": "lato/Lato-Bold.ttf",
    "copy": "lato/Lato-Regular.ttf",
}


@lru_cache(maxsize=None)
def face(style, size):
    return ImageFont.truetype(FONT_ROOT / FONT_FILES[style], round(size * SCALE))


def advance(text, font):
    return font.getlength(text) / SCALE


def fit_words(text, font, width, balance=False):
    words = text.split()
    if balance and advance(text, font) > width:
        options = []
        for split in range(1, len(words)):
            first = " ".join(words[:split])
            second = " ".join(words[split:])
            a, b = advance(first, font), advance(second, font)
            if max(a, b) <= width:
                options.append((abs(a - b), first, second))
        if not options:
            raise ValueError(f"Headline cannot fit: {text}")
        _, first, second = min(options)
        return [first, second]

    lines = [words[0]]
    for word in words[1:]:
        combined = f"{lines[-1]} {word}"
        if advance(combined, font) > width:
            lines.append(word)
        else:
            lines[-1] = combined
    return lines


def scaled(*numbers):
    return tuple(round(n * SCALE) for n in numbers)


class Page:
    def __init__(self):
        self.image = Image.new("RGB", (SIZE * SCALE, SIZE * SCALE), PAPER)
        self.draw = ImageDraw.Draw(self.image)

    def box(self, left, top, right, bottom, color):
        self.draw.rectangle(scaled(left, top, right, bottom), fill=color)

    def line(self, x1, y1, x2, y2, color, weight=1):
        self.draw.line(scaled(x1, y1, x2, y2), fill=color, width=round(weight * SCALE))

    def circle(self, x, y, radius, color):
        self.draw.ellipse(scaled(x - radius, y - radius, x + radius, y + radius), fill=color)

    def label(self, x, y, words, font, color=INK, anchor="ls"):
        self.draw.text(scaled(x, y), words, fill=color, font=font, anchor=anchor)


def masthead(page):
    page.line(LEFT, 22, RIGHT, 22, INK, 4)
    page.label(LEFT, 46, DATE, face("heavy", 17), RUST)
    page.label(RIGHT, 46, DEK, face("copy", 16), BODY, "rs")
    page.label(SIZE / 2, 115, TITLE, face("serif", 77), anchor="ms")


def project(lon, lat):
    # Equirectangular map with fixed horizontal and vertical scales in degrees.
    return (51 + (lon + 180) * 922 / 360, 139 + (84 - lat) * 192 / 142)


def locator_map(page):
    page.box(LEFT, 128, RIGHT, 340, NAVY)
    page.line(LEFT, 128, RIGHT, 128, GOLD, 2)
    for lon in range(-180, 181, 30):
        x, _ = project(lon, 0)
        page.line(x, 139, x, 331, GRID, 0.5)
    for lat in range(-45, 76, 15):
        _, y = project(0, lat)
        page.line(51, y, 973, y, GRID, 0.5)

    mask = Image.new("1", (SIZE, 341))
    sketch = ImageDraw.Draw(mask)
    for ring in LAND.strip().split("\n\n"):
        values = iter(map(int, ring.split()))
        vertices = [tuple(round(v) for v in project(lon, lat)) for lon, lat in zip(values, values)]
        sketch.polygon(vertices, fill=1)
    land = mask.load()
    for y in range(141, 332, 4):
        for x in range(52, 974, 4):
            if land[x, y]:
                page.circle(x, y, 0.85, DOTS)

    for _, lon, lat, (badge_x, badge_y), _ in PINS:
        x, y = project(lon, lat)
        page.line(x, y, badge_x, badge_y, NAVY, 3)
        page.line(x, y, badge_x, badge_y, GOLD, 1)
        page.circle(x, y, 4.1, NAVY)
        page.circle(x, y, 2.35, GOLD)

    city_font = face("bold", 13)
    for number, (city, _, _, (x, y), side) in enumerate(PINS, start=1):
        width = advance(city, city_font)
        if side == "left":
            page.box(x - 15 - width - 3, y - 8, x - 12, y + 8, NAVY)
            page.label(x - 15, y + 4, city, city_font, PAPER, "rs")
        else:
            page.box(x + 12, y - 8, x + 15 + width + 3, y + 8, NAVY)
            page.label(x + 15, y + 4, city, city_font, PAPER)
        page.circle(x, y, 11, NAVY)
        page.circle(x, y, 9, GOLD)
        page.label(x, y, str(number), face("heavy", 12), NAVY, "mm")


def story_grid(page):
    row_edges = [350, 473, 587, 699, 822]
    headline = face("heavy", 21.5)
    body = face("copy", 14.5)
    tag = face("heavy", 13)
    page.line(512, row_edges[0], 512, row_edges[-1] - 3, RULE, 0.5)
    page.box(523, row_edges[-2], RIGHT, row_edges[-1] - 3, "#e7edeb")
    for i, (place, title, copy) in enumerate(STORIES):
        row, col = divmod(i, 2)
        top, bottom = row_edges[row:row + 2]
        left, right = (LEFT, 500) if col == 0 else (524, RIGHT)
        accent = NAVY if place == "SPACE" else RUST
        inset = 8 if place == "SPACE" else 0
        x = left + inset
        width = right - x - inset - 2
        page.line(left, top, right, top, accent if row == 0 or inset else RULE)
        page.circle(x + 7, top + 11, 6.5, accent)
        page.label(x + 7, top + 11, str(i + 1), face("heavy", 9), PAPER, "mm")
        page.label(x + 19, top + 15, place, tag, accent)

        baseline = top + 35
        for line in fit_words(title, headline, width, balance=True):
            page.label(x, baseline, line, headline)
            baseline += 21
        baseline -= 6
        for line in fit_words(copy, body, width):
            if baseline + body.getbbox(line, anchor="ls")[3] / SCALE > bottom - 4:
                raise ValueError(f"Story {i + 1} exceeds its allotted height.")
            page.label(x, baseline, line, body, BODY)
            baseline += 15


def figures_bar(page):
    top, bottom = 828, 908
    cell = (RIGHT - LEFT) / len(FIGURES)
    page.box(LEFT, top, RIGHT, bottom, "#eee6d4")
    page.line(LEFT, top, RIGHT, top, RUST, 2)
    captions = face("heavy", 11.5)
    for i, (label, value) in enumerate(FIGURES):
        edge = LEFT + i * cell
        middle = edge + cell / 2
        if i:
            page.line(edge, top + 12, edge, bottom - 12, RULE, 0.5)
        page.label(middle, top + 39, value, face("serif", 40), RUST, "ms")
        lines = fit_words(label, captions, cell - 24)
        y = top + 63 - 6 * (len(lines) - 1)
        for line in lines:
            page.label(middle, y, line, captions, INK, "ms")
            y += 12


def ticker_panel(page):
    top, bottom = 916, 1006
    page.box(LEFT, top, RIGHT, bottom, NAVY)
    page.label(43, 932, "ALSO TODAY", face("heavy", 11), GOLD)
    page.line(118, 928, 981, 928, DOTS, 0.5)
    page.line(512, 939, 512, 995, GRID)
    font = face("bold", 10.5)
    for i, item in enumerate(TICKER):
        col, row = divmod(i, 5)
        x = 47 + 482 * col
        y = 946 + 12.5 * row
        if advance(item, font) > 454:
            raise ValueError(f"Ticker item {i + 1} exceeds its column width.")
        page.circle(x - 7, y - 3.5, 1.25, GOLD)
        page.label(x, y, item, font, PAPER)


def description():
    sections = ["\n".join((TITLE, DATE, DEK))]
    for index, (place, title, copy) in enumerate(STORIES):
        number = index + 1
        detail = "(no pin; SPACE callout)"
        if index < len(PINS):
            city, lon, lat, _, _ = PINS[index]
            detail = f"{place} (pin {number}: {city}, {lat:.2f}, {lon:.2f})"
        sections.append(f"{number}. {title} — {detail}\n{copy}")
    sections.append("\n".join(["Data bar", *(f"{key}: {value}" for key, value in FIGURES)]))
    sections.append("\n".join(["Ticker", *TICKER]))
    return "\n\n".join(sections)


def render():
    if any(not (FONT_ROOT / file).is_file() for file in FONT_FILES.values()):
        sys.exit(69)
    page = Page()
    masthead(page)
    locator_map(page)
    story_grid(page)
    figures_bar(page)
    ticker_panel(page)

    info = PngImagePlugin.PngInfo()
    info.add_text("Title", TITLE)
    info.add_itxt("Description", description(), lang="en", zip=True)
    final = page.image.resize((SIZE, SIZE), resample=Image.Resampling.LANCZOS)
    final.save(sys.stdout.buffer, format="PNG", pnginfo=info, compress_level=9)


if __name__ == "__main__":
    render()
