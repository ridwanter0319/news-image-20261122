"""Compose the one-page broadsheet for Sunday 22 November 2026 (v3).

Deterministic PIL rendering: no network, no randomness, no timestamps.
Every card carries a small vector illustration with a red label, the three
leads are tied to the numbers strip, and briefs stay at readable sizes.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14
CW = W - 2 * M

BG = (247, 242, 230)
PAPER = (253, 250, 243)
INK = (26, 23, 18)
RED = (178, 34, 28)
DARK = (34, 31, 28)
GRAY = (96, 89, 79)
LINE = (70, 63, 53)
TAN = (238, 231, 214)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SERIF_BI = "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def F(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def draw_wrap(d, text, font, x, y, width, fill=INK, lh=None, max_lines=None):
    lh = lh or int(font.size * 1.22)
    lines = wrap(d, text, font, width)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        d.text((x, y + i * lh), ln, font=font, fill=fill)
    return y + len(lines) * lh


def rich_wrap(d, segments, width):
    """Word-wrap a list of (text, font, fill) segments into styled lines."""
    words = []
    for text, font, fill in segments:
        for w_ in text.split():
            words.append((w_, font, fill))
    lines, cur, cur_w = [], [], 0.0
    space_w = tw(d, " ", segments[0][1])
    for w_, font, fill in words:
        ww = tw(d, w_, font)
        add = ww if not cur else ww + space_w
        if cur and cur_w + add > width:
            lines.append(cur)
            cur, cur_w = [(w_, font, fill)], ww
        else:
            cur.append((w_, font, fill))
            cur_w += add
    if cur:
        lines.append(cur)
    return lines


def draw_rich(d, segments, x, y, width, lh, max_lines=None):
    lines = rich_wrap(d, segments, width)
    if max_lines:
        lines = lines[:max_lines]
    space_w = tw(d, " ", segments[0][1])
    for i, line in enumerate(lines):
        cx = x
        for w_, font, fill in line:
            d.text((cx, y + i * lh), w_, font=font, fill=fill)
            cx += tw(d, w_, font) + space_w
    return y + len(lines) * lh


def centered(d, text, font, y, fill=INK, cx=W // 2):
    d.text((cx - tw(d, text, font) / 2, y), text, font=font, fill=fill)


# ---------------------------------------------------------------- illustrations

def tag(d, box, text):
    """Certainty tag in the top-right corner of an illustration."""
    f = F(SANS_B, 9)
    w_ = tw(d, text, f) + 10
    x1, y1 = box[2], box[1]
    d.rectangle([x1 - w_, y1, x1, y1 + 14], fill=(253, 250, 243))
    d.text((x1 - w_ + 5, y1 + 2), text, font=f, fill=RED)


def illus_drones(d, box):
    x0, y0, x1, y1 = box
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        d.line([(x0, y0 + i), (x1, y0 + i)],
               fill=(int(26 + 34 * t), int(36 + 40 * t), int(66 + 44 * t)))
    # drone silhouettes: delta wings and quad crosses
    for cx, cy, s in [(x0 + 178, y0 + 16, 13), (x0 + 222, y0 + 30, 10),
                      (x0 + 246, y0 + 12, 8), (x0 + 146, y0 + 34, 9)]:
        d.polygon([(cx - s, cy + s * 0.5), (cx, cy - s * 0.6), (cx + s, cy + s * 0.5),
                   (cx, cy + s * 0.25)], fill=(210, 216, 228))
    for cx, cy, s in [(x0 + 214, y0 + 48, 7), (x0 + 292, y0 + 40, 6)]:
        d.line([(cx - s, cy - s), (cx + s, cy + s)], fill=(210, 216, 228), width=2)
        d.line([(cx - s, cy + s), (cx + s, cy - s)], fill=(210, 216, 228), width=2)
    # apartment block, bottom right, lit windows, one corner torn
    bx, by = x0 + 226, y1 - 34
    d.rectangle([bx, by, x1 - 6, y1], fill=(16, 15, 20))
    for r in range(3):
        for c in range(5):
            if (r * 5 + c) % 3 != 1:
                d.rectangle([bx + 6 + c * 13, by + 5 + r * 10,
                             bx + 11 + c * 13, by + 9 + r * 10], fill=(250, 196, 84))
    d.polygon([(x1 - 6, by), (x1 - 26, by), (x1 - 6, by + 16)], fill=(240, 120, 50))
    for sx, sy in [(x1 - 22, by + 8), (x1 - 40, by + 20)]:
        d.line([(sx - 5, sy), (sx + 5, sy)], fill=(255, 170, 60), width=2)
        d.line([(sx, sy - 5), (sx, sy + 5)], fill=(255, 170, 60), width=2)
    d.text((x0 + 8, y0 + 8), "186 DRONES", font=F(SANS_B, 21), fill=(255, 255, 255))
    d.text((x0 + 8, y0 + 31), "OVERNIGHT", font=F(SANS_B, 21), fill=(255, 255, 255))
    d.rectangle([x0 + 8, y0 + 58, x0 + 118, y0 + 76], fill=RED)
    d.text((x0 + 14, y0 + 60), "161 DOWNED", font=F(SANS_B, 13), fill=(255, 255, 255))


def illus_cop(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(23, 96, 86))
    d.ellipse([x0 + 218, y0 + 8, x0 + 246, y0 + 36], fill=(250, 205, 92))
    # final-text document, bottom right, clear of the title and the tag
    dx, dy = x1 - 82, y0 + 34
    d.rectangle([dx, dy, dx + 66, dy + 44], fill=(253, 250, 243))
    for i in range(3):
        d.line([(dx + 7, dy + 9 + i * 9), (dx + 59, dy + 9 + i * 9)],
               fill=(150, 143, 130), width=2)
    d.ellipse([dx + 40, dy + 26, dx + 62, dy + 42], outline=RED, width=3)
    d.line([(dx + 43, dy + 40), (dx + 59, dy + 28)], fill=RED, width=3)
    d.text((x0 + 10, y0 + 8), "COP31: FINAL TEXT", font=F(SANS_B, 19), fill=(255, 255, 255))
    d.rectangle([x0 + 10, y0 + 36, x0 + 142, y0 + 56], fill=RED)
    d.text((x0 + 16, y0 + 39), "NO FOSSIL FUELS", font=F(SANS_B, 14), fill=(255, 255, 255))
    d.text((x0 + 10, y0 + 62), "Antalya, Türkiye", font=F(SANS_I, 10), fill=(214, 235, 228))


def illus_radar(d, box):
    x0, y0, x1, y1 = box
    for i in range(y1 - y0):
        t = i / max(1, (y1 - y0))
        d.line([(x0, y0 + i), (x1, y0 + i)],
               fill=(int(66 - 20 * t), int(70 - 16 * t), int(92 - 10 * t)))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(38, 52, 74))
    for i in range(9):
        d.line([(x0 + 12 + i * 36, y1 - 14), (x0 + 20 + i * 36, y1 - 9)],
               fill=(120, 160, 200), width=2)
    # radar dish on a mast
    cx, cy = x0 + 236, y1 - 16
    d.line([(cx, cy), (cx, cy - 34)], fill=(225, 228, 232), width=3)
    d.arc([cx - 26, cy - 58, cx + 26, cy - 6], start=300, end=120, fill=(225, 228, 232), width=4)
    d.line([(cx, cy - 32), (cx + 16, cy - 44)], fill=(225, 228, 232), width=3)
    for r in (14, 24, 34):
        d.arc([cx + 16 - r, cy - 44 - r, cx + 16 + r, cy - 44 + r],
              start=290, end=70, fill=(250, 196, 84), width=2)
    # two small radar squares, questioned
    for sx in (x0 + 178, x0 + 290):
        d.rectangle([sx, y1 - 30, sx + 16, y1 - 14], fill=(200, 204, 210))
        d.text((sx + 3, y1 - 46), "?", font=F(SANS_B, 13), fill=(250, 196, 84))
    d.text((x0 + 8, y0 + 8), "CLAIM VS DENIAL", font=F(SANS_B, 20), fill=(255, 255, 255))
    d.rectangle([x0 + 8, y0 + 36, x0 + 108, y0 + 56], fill=RED)
    d.text((x0 + 14, y0 + 39), "2 RADARS?", font=F(SANS_B, 14), fill=(255, 255, 255))
    d.text((x0 + 8, y0 + 60), "Manama · Patriot radars", font=F(SANS_I, 10), fill=(206, 216, 228))


CARD_COLORS = [
    (44, 62, 92), (96, 74, 40), (52, 84, 60), (74, 52, 92),
    (40, 84, 96), (96, 52, 44), (60, 60, 60), (84, 44, 62),
    (44, 74, 84), (92, 84, 40), (52, 62, 84), (70, 84, 52),
]


def illus_card(d, box, idx, label, place):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=CARD_COLORS[idx % len(CARD_COLORS)])
    f = F(SANS_B, 10)
    w_ = tw(d, label, f) + 10
    d.rectangle([x0, y0, x0 + w_, y1], fill=RED)
    d.text((x0 + 5, y0 + 5), label, font=f, fill=(255, 255, 255))
    # one small vector mark just right of the red label, drawn only when
    # the strip has a clear gap between the label and the place name
    fp = F(SANS_B, 8)
    ix = x0 + w_ + 8
    kind = idx % 4
    if ix + 26 < x1 - tw(d, place, fp) - 12:
        if kind == 0:
            d.ellipse([ix, y0 + 3, ix + 14, y0 + 17], outline=(255, 255, 255), width=2)
            d.line([(ix + 7, y0 + 17), (ix + 7, y0 + 20)], fill=(255, 255, 255), width=2)
        elif kind == 1:
            d.polygon([(ix, y0 + 16), (ix + 8, y0 + 4), (ix + 16, y0 + 16)],
                      outline=(255, 255, 255), width=2)
        elif kind == 2:
            for i in range(3):
                d.line([(ix + i * 8, y0 + 16), (ix + 4 + i * 8, y0 + 5)],
                       fill=(255, 255, 255), width=2)
        else:
            d.arc([ix, y0 + 3, ix + 24, y0 + 19], start=20, end=320,
                  fill=(255, 255, 255), width=2)
    d.text((x1 - tw(d, place, fp) - 5, y0 + 6), place, font=fp, fill=(235, 235, 230))


# ---------------------------------------------------------------- data

NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or suppressed by air defence"),
    ("35%", "electricity goal for 2035, kept"),
    ("$120bn", "adaptation target dropped"),
    ("720/9", "India's record Test total in NZ"),
    ("50", "Wembanyama points, 19 rebounds"),
]

LEADS = [
    {
        "illus": illus_drones, "cert": "REPORTED",
        "kicker": "1 · KYIV REGION, UKRAINE · WAR",
        "headline": "Russia fires 186 drones overnight; a Kyiv-region block is destroyed",
        "body": ("Air defences downed or suppressed 161 of 186 strike drones "
                 "(72 of them jet-powered) fired from eight directions. A "
                 "five-storey block in Dymer destroyed: up to seven people "
                 "feared trapped, two injured, nine evacuated."),
        "source": "(Ukrainian Air Force via wires)",
    },
    {
        "illus": illus_cop, "cert": "REPORTED",
        "kicker": "2 · ANTALYA, TÜRKIYE · CLIMATE",
        "headline": "Climate deal lands with no mention of fossil fuels",
        "body": ("The final text \u201crecalls\u201d the Dubai pact whole, keeps the "
                 "2035 electricity goal, drops the $120bn adaptation target "
                 "and is the first to admit 1.5\u00b0C will be overshot. "
                 "Hoekstra: \u201ca good deal or no deal.\u201d"),
        "source": "(Reuters, BBC, The Guardian)",
    },
    {
        "illus": illus_radar, "cert": "CLAIM",
        "kicker": "3 · MANAMA, BAHRAIN · IRAN",
        "headline": "Iran claims two US radars hit; Bahrain denies it",
        "body": ("The IRGC says it destroyed two Patriot radars on Saturday "
                 "night. Bahrain's foreign ministry answered on Sunday: the "
                 "target was a civilian industrial site \u2014 a fire, no "
                 "injuries \u2014 and a violation of its sovereignty."),
        "source": "(Khaleej Times, Al Jazeera)",
    },
]

CARDS = [
    ("JENSEN IS BACK", "SANTA CLARA · TECH",
     "Nvidia's board votes Jensen Huang back as CEO.",
     "Sunday-night vote was unanimous: reinstated as president, CEO and "
     "director, 11 days after he resigned, after input from senior US "
     "officials; Trump urged the board on Truth Social. SEC 8-K dates the "
     "vote to Sun 22 Nov; announced Mon. (SEC 8-K, Reuters)"),
    ("856 CANDIDATES", "HONG KONG · ELECTION",
     "Hong Kong elects its Election Committee.",
     "856 candidates, 723 seats, 5,700 voters; polls 09:00\u201318:00. (SCMP)"),
    ("720/9 DECLARED", "WELLINGTON · CRICKET",
     "India declare on 720/9, a record in New Zealand.",
     "Rahul 156, Pant 128, Gill 98; hosts 119/2, trailing by 233. (ESPN)"),
    ("VERSTAPPEN WINS", "LAS VEGAS · FORMULA 1",
     "Verstappen takes the Las Vegas Grand Prix.",
     "From pole in 1:27:39.624; Norris +0.639, Piastri +1.529. (FIA)"),
    ("50 POINTS", "SAN ANTONIO · NBA",
     "Wembanyama scores 50 as the Spurs roll on.",
     "50 pts, 19 rebounds, 5 blocks; 114\u201391 over New Orleans. (Reuters)"),
    ("SHIP ABLAZE", "GULF OF FINLAND · SEA",
     "Russian cargo ship Sparta II still burning.",
     "Hit by drones Saturday; Finland leads Loviisa rescue. (Reuters)"),
    ("POWER CUTS", "TEHRAN, IRAN · ENERGY",
     "Iran begins rationing electricity.",
     "Rolling cuts up to two hours a day as war damage bites. (Wires)"),
    ("IN INTENSIVE CARE", "BRASÍLIA, BRAZIL · HEALTH",
     "Bolsonaro in intensive care in Brasília.",
     "Acute bowel obstruction, stable; surgery possible. (Reuters)"),
    ("FBI PROBE", "WASHINGTON · CYBER",
     "FBI probes apparent hack of its crime database.",
     "Washington State pauses gun-dealer checks; breach assessed. (AP)"),
    ("TOLL AT 19", "MANIPUR, INDIA · POISONING",
     "Toxic-liquor toll in Manipur climbs to 19.",
     "600 in hospital, six held; toll up from 16 on Saturday. (Xinhua)"),
    ("5 DEAD, 36 MISSING", "CIKANDE, INDONESIA · FIRE",
     "Candy-factory fire in Cikande: 5 dead, 36 missing.",
     "Blaze tore through the Banten plant; search goes on. (Detiknews)"),
    ("1 DEAD, 16 HURT", "JUNÍN, PERU · QUAKE TOLL",
     "Peru quake toll updated: 1 dead, 16 hurt.",
     "170 homes damaged in Junín; the count is completed. (Reuters)"),
]

BRIEFS = [
    ("16", "Europe", "Estonia to shut five Russia border crossings 1 Dec, after a sabotage bid (Reuters)"),
    ("17", "Europe", "Denmark expels a Russian attaché over an alleged plot against a Ukrainian rapper (Wires)"),
    ("18", "Asia-Pacific", "Nepal PM Shah lands in Delhi on first visit; meets Modi Monday (IANS)"),
    ("19", "Asia-Pacific", "Chinese bomber turns back 170 km from Manila (AP)"),
    ("20", "Asia-Pacific", "Philippines M5.9 quake, 898 km deep, off Palawan (EMSC)"),
    ("21", "Asia-Pacific", "Japan poll: record 82% feel friendly to South Korea (JKN)"),
    ("22", "Asia-Pacific", "Taiwan live-fire drill on Kinmen (CNA)"),
    ("23", "Asia-Pacific", "Indonesia counts the China haul: 35 deals worth Rp274 trillion (Antara)"),
    ("24", "Asia-Pacific", "M7.2 quake strikes Southwest Maluku, deep tremor recorded by BMKG (BMKG, Antara)"),
    ("25", "Africa", "Somalia expels UAE ambassador, recalls its envoy (Wires)"),
    ("26", "Africa", "Sudan: RSF accused of killing civilians, incl. 3 children, in W. Kordofan (Claim)"),
    ("27", "Africa", "Kenya discharges its last Ebola patient (Wires)"),
    ("28", "Oceania", "Melbourne: 70 years since the 1956 Olympics opened (ABC)"),
    ("29", "Americas", "Trump seeks 'permanent' Iran deal; Doha talks to mediators (Al Jazeera)"),
    ("30", "Americas", "Eisenkot invites Likud to coalition talks (Straits Times)"),
    ("31", "Americas", "Mexico counts 11 killed in the north as cartel gunmen answer Friday's capture of \u201cEl Chapo Isidro\u201d with a wave of violence (Reuters, EuroNews)"),
    ("32", "Middle East", "Hamas seeks urgent mediator talks (Al Jazeera)"),
    ("33", "World", "Bitcoin back above $60,000 after Saturday's $55.1k flush (Market data)"),
    ("34", "World", "Gold holds near $5,055 (Reuters)"),
    ("35", "Europe", "FORECAST: ATP Finals final, Turin: Zverev v Alcaraz, 17:00 GMT (Forecast)"),
    ("36", "Europe", "FORECAST: Liverpool host Manchester United, 16:30 GMT \u2014 Pochettino's United debut (Forecast)"),
]

DATE_CHECK = (
    "Left out as other days' news: the 400-drone, 110-missile barrage "
    "(Thu 19\u2013Fri 20 Nov) \u00b7 the 148-drone night and the Kryvyi Rih "
    "double-tap (Fri 20\u2013Sat 21) \u00b7 'El Chapo Isidro' captured (Fri) "
    "\u00b7 Bayelsa boat, 24 dead (Fri) \u00b7 Gaza aid-van strike (Sat) "
    "\u00b7 BepiColombo's Mercury burn (Sat). Tonight's real count: 186 "
    "drones, at the top of this page. Dated where it appears: Nvidia's "
    "board vote (Sunday night, per its SEC 8-K; announced Monday)."
)

# continent shapes as (lon, lat, rx, ry) ellipses for the dotted map
LAND = [
    (-100, 49, 40, 15), (-152, 64, 15, 7), (-85, 38, 24, 10), (-42, 72, 11, 6),
    (-88, 16, 9, 5), (-62, -6, 12, 10), (-64, -23, 8, 12),
    (15, 53, 19, 9), (16, 64, 12, 6), (-3, 40, 7, 5), (-2, 54, 3, 4),
    (20, 8, 21, 14), (25, -13, 15, 13), (47, -19, 3, 5),
    (82, 52, 50, 13), (45, 25, 11, 7), (51, 35, 9, 6), (78, 22, 12, 10),
    (102, 15, 8, 8), (108, 34, 17, 11), (122, 30, 8, 7), (138, 37, 5, 6),
    (113, -1, 13, 3), (134, -25, 14, 8), (147, -42, 4, 4), (172, -42, 3, 5),
    (28, 41, 6, 4),
]

PINS = [
    (1, 30.5, 50.4), (2, 30.4, 36.9), (3, 50.6, 26.2), (4, -122.0, 37.4),
    (5, 114.2, 22.3), (6, 174.8, -41.3), (7, -115.1, 36.2), (8, -98.5, 29.4),
    (9, 25.0, 60.0), (10, 51.4, 35.7), (11, -47.9, -15.8), (12, -77.0, 38.9),
    (13, 93.9, 24.8), (14, 106.3, -6.3), (15, -75.2, -11.5),
]


def draw_map(d, x0, y0, x1, y1):
    d.text((x0, y0), "WHERE IT HAPPENED \u2014 pins match story numbers",
           font=F(SANS_B, 9), fill=INK)
    top = y0 + 14
    cols, rows = 68, 15
    sx = (x1 - x0) / cols
    sy = (y1 - top) / rows
    for r in range(rows):
        lat = 78 - (r + 0.5) * (136 / rows)
        for c in range(cols):
            lon = -180 + (c + 0.5) * (360 / cols)
            inside = any(((lon - lo) / rx) ** 2 + ((lat - la) / ry) ** 2 <= 1.0
                         for lo, la, rx, ry in LAND)
            if inside:
                cx, cy = x0 + (c + 0.5) * sx, top + (r + 0.5) * sy
                d.ellipse([cx - 1.3, cy - 1.3, cx + 1.3, cy + 1.3], fill=(120, 112, 98))
    f = F(SANS_B, 8)
    for num, lon, lat in PINS:
        cx = x0 + (lon + 180) / 360 * (x1 - x0)
        cy = top + (78 - lat) / 136 * (y1 - top)
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED, outline=(255, 255, 255), width=1)
        s = str(num)
        d.text((cx - tw(d, s, f) / 2, cy - 5), s, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- page

def render(dest):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # top strip
    d.text((M, 10), "THE WORLD IN ONE DAY", font=F(SANS_B, 12), fill=INK)
    right = "36 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    fr = F(SANS_B, 9)
    d.text((W - M - tw(d, right, fr), 12), right, font=fr, fill=RED)
    d.line([(M, 27), (W - M, 27)], fill=LINE, width=2)

    # masthead
    centered(d, "Sunday 22 November 2026", F(SERIF_B, 47), 33)
    d.line([(M, 86), (W - M, 86)], fill=LINE, width=1)

    # standfirst
    stand = ("186 drones over Ukraine in the night \u00b7 COP31's deal names no "
             "fossil fuels \u00b7 Iran's radar claim meets Bahrain's denial")
    centered(d, stand, F(SERIF_BI, 16), 91, fill=RED)

    # numbers strip, tied to the leads
    ny = 114
    d.rectangle([M, ny, W - M, ny + 46], fill=TAN)
    cell = CW / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = M + cell * i + cell / 2
        fn = F(SERIF_B, 21)
        d.text((cx - tw(d, num, fn) / 2, ny + 3), num, font=fn, fill=RED)
        fl = F(SANS, 8)
        for j, ln in enumerate(wrap(d, label, fl, cell - 10)):
            d.text((cx - tw(d, ln, fl) / 2, ny + 27 + j * 9), ln, font=fl, fill=INK)
        if i:
            d.line([(M + cell * i, ny + 5), (M + cell * i, ny + 41)], fill=(200, 192, 172))

    # region bar
    ry = ny + 50
    d.rectangle([M, ry, W - M, ry + 20], fill=DARK)
    centered(d, "EUROPE 8 \u00b7 MIDDLE EAST 4 \u00b7 AMERICAS 7 \u00b7 ASIA-PACIFIC 9 "
                "\u00b7 AFRICA 3 \u00b7 OCEANIA 3 \u00b7 WORLD 2",
             F(SANS_B, 12), ry + 4, fill=(255, 255, 255))

    # the day in UTC
    uy = ry + 24
    d.rectangle([M, uy, W - M, uy + 19], fill=(240, 234, 218))
    utc = ("  01:00 HK polls open \u00b7 03:00 COP31 objections close \u00b7 05:11 Hamas "
           "seeks talks \u00b7 05:30 Verstappen wins Vegas \u00b7 06:00 COP31 approval "
           "due \u00b7 07:30 Approval slips again")
    d.text((M + 6, uy + 4), "THE DAY IN UTC", font=F(SANS_B, 9), fill=RED)
    d.text((M + 6 + tw(d, "THE DAY IN UTC", F(SANS_B, 9)), uy + 4), utc,
           font=F(SANS, 9), fill=INK)

    # leads
    ly = uy + 27
    lead_h = 204
    lw = (CW - 16) / 3
    for i, lead in enumerate(LEADS):
        x = M + i * (lw + 8)
        box = (x, ly, x + lw, ly + 84)
        lead["illus"](d, box)
        tag(d, box, lead["cert"])
        ky = ly + 88
        d.text((x, ky), lead["kicker"], font=F(SANS_B, 9), fill=RED)
        hy = draw_wrap(d, lead["headline"], F(SERIF_B, 16), x, ky + 13, lw, lh=18)
        by = draw_wrap(d, lead["body"], F(SANS, 10), x, hy + 2, lw, lh=12)
        d.text((x, by + 1), lead["source"], font=F(SANS_I, 8), fill=GRAY)
    d.line([(M, ly + lead_h), (W - M, ly + lead_h)], fill=LINE, width=1)

    # cards 4-15, every one illustrated
    cy0 = ly + lead_h + 6
    cols, rows = 4, 3
    gap = 6
    cw_ = (CW - (cols - 1) * gap) / cols
    ch = 78
    fb, fr_ = F(SANS_B, 9), F(SANS, 9)
    for idx, (label, place, head, body) in enumerate(CARDS):
        cx = M + (idx % cols) * (cw_ + gap)
        cy = cy0 + (idx // cols) * (ch + gap)
        d.rectangle([cx, cy, cx + cw_, cy + ch], fill=PAPER, outline=(198, 190, 172))
        illus_card(d, (cx + 1, cy + 1, cx + cw_ - 1, cy + 20), idx, label, place)
        num = str(idx + 4)
        if idx == 0:
            # the Nvidia card carries the longest text: one size down so
            # the SEC 8-K dating is never cut off
            segs = [(num + "  ", F(SANS_B, 8), RED),
                    (head + " ", F(SANS_B, 8), INK), (body, F(SANS, 8), INK)]
            draw_rich(d, segs, cx + 5, cy + 24, cw_ - 10, 10, max_lines=5)
        else:
            segs = [(num + "  ", F(SANS_B, 9), RED), (head + " ", fb, INK), (body, fr_, INK)]
            draw_rich(d, segs, cx + 5, cy + 24, cw_ - 10, 11, max_lines=5)

    # briefs 16-36 in two flowing columns
    by0 = cy0 + rows * (ch + gap) + 4
    d.text((M, by0), "ALSO ON SUNDAY \u2014 21 MORE STORIES", font=F(SANS_B, 11), fill=RED)
    d.line([(M, by0 + 15), (W - M, by0 + 15)], fill=LINE, width=1)
    col_w = (CW - 14) / 2
    fb8, fr8 = F(SANS_B, 8), F(SANS, 8)
    half = (len(BRIEFS) + 1) // 2
    for ci, chunk in enumerate((BRIEFS[:half], BRIEFS[half:])):
        x = M + ci * (col_w + 14)
        y = by0 + 19
        for num, region, text in chunk:
            segs = [(num + " " + region + ": ", fb8, RED), (text, fr8, INK)]
            y = draw_rich(d, segs, x, y, col_w, 10) + 3

    # map + date check
    my = 852
    draw_map(d, M, my, M + 496, 950)
    dx = M + 510
    d.rectangle([dx, my, W - M, 950], outline=RED, width=2, fill=(253, 246, 238))
    d.text((dx + 8, my + 6), "DATE CHECK \u2014 LEFT OUT AS OTHER DAYS' NEWS",
           font=F(SANS_B, 10), fill=RED)
    draw_wrap(d, DATE_CHECK, F(SANS, 9), dx + 8, my + 22, W - M - dx - 16, lh=12)

    # sources, certainty, bottom strip
    centered(d, "Sources: Reuters, BBC, AP, Al Jazeera, The Guardian, Ukrinform, "
                "Kyiv Post, ESPN, SCMP, Detiknews. Pictures and map: original, "
                "drawn in code.", F(SANS_I, 9), 956, fill=GRAY)
    centered(d, "CERTAINTY \u2014 REPORTED = carried by the day's wires \u00b7 CLAIM = "
                "one side's account, labelled as such \u00b7 FORECAST = still to "
                "happen when drawn", F(SANS, 9), 971, fill=INK)
    d.rectangle([M, 988, W - M, 1014], fill=DARK)
    d.text((M + 8, 995), "THE WORLD IN ONE DAY", font=F(SANS_B, 12), fill=(255, 255, 255))
    tail = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    ft = F(SANS_B, 10)
    d.text((W - M - 8 - tw(d, tail, ft), 997), tail, font=ft, fill=(255, 255, 255))

    img.save(dest, format="PNG", optimize=False)


if __name__ == "__main__":
    render("entry.png")
