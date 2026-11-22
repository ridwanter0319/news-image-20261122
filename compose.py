"""Compose the one-page broadsheet for Sunday 22 November 2026.

Draws the whole newspaper page with PIL: masthead, numbers strip, region
bar, three illustrated lead cards, ten numbered cards, a briefs column
block, a dotted world map with numbered pins, and the date-check footer.
Deterministic: no randomness, no network, fixed fonts where available.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 241, 227)
PAPER = (255, 253, 246)
NAVY = (20, 38, 76)
RED = (179, 49, 42)
INK = (28, 26, 23)
GRAY = (90, 84, 74)
LINE = (201, 191, 168)
GOLD = (201, 150, 46)
SKY = (214, 226, 238)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def serif_b(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def serif_i(size):
    return font("DejaVuSerif-Italic.ttf", size)


def sans_b(size):
    return font("DejaVuSans-Bold.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def wrap(draw, text, fnt, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def block(draw, x, y, text, fnt, maxw, lh, color=INK, max_lines=None):
    lines = wrap(draw, text, fnt, maxw)
    if max_lines:
        lines = lines[:max_lines]
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += lh
    return y


def fit_block(draw, x, y, text, maxw, max_h, sizes, bold=False, color=INK):
    """Draw text shrinking the font until it fits max_h; return end y."""
    for size in sizes:
        fnt = sans_b(size) if bold else sans(size)
        lh = size + 3
        lines = wrap(draw, text, fnt, maxw)
        if len(lines) * lh <= max_h:
            for ln in lines:
                draw.text((x, y), ln, font=fnt, fill=color)
                y += lh
            return y
    fnt = sans(sizes[-1])
    lh = sizes[-1] + 3
    lines = wrap(draw, text, fnt, maxw)
    max_lines = max(1, int(max_h // lh))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and draw.textlength(last + " …", font=fnt) > maxw:
            last = last.rsplit(" ", 1)[0]
        lines[-1] = last + " …"
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += lh
    return y


def header(draw):
    # Kicker row
    draw.text((16, 10), "THE WORLD IN ONE DAY", font=sans_b(13), fill=NAVY)
    right = "SUNDAY'S NEWS · ONE PAGE · 40 STORIES · 6 REGIONS"
    fnt = sans_b(12)
    draw.text((1008 - draw.textlength(right, font=fnt), 11), right, font=fnt, fill=RED)
    draw.line((16, 32, 1008, 32), fill=NAVY, width=2)
    # Masthead: navy band + red date block
    draw.rectangle((16, 38, 1008, 96), fill=NAVY)
    draw.rectangle((716, 38, 1008, 96), fill=RED)
    draw.text((34, 52), "THE WORLD IN ONE DAY", font=serif_b(34), fill=(255, 255, 255))
    draw.text((730, 46), "Sunday", font=serif_b(19), fill=(255, 255, 255))
    draw.text((730, 68), "22 November 2026", font=serif_b(19), fill=(255, 255, 255))
    # Standfirst + date line
    sf = "Cartel kingpin captured in Sinaloa · Kyiv's bridges burn · Peru's Andes shake"
    fnt = serif_i(17)
    draw.text(((1024 - draw.textlength(sf, font=fnt)) / 2, 104), sf, font=fnt, fill=INK)
    dl = ("Every story on this page happened, or was first reported, on Sunday "
          "22 November 2026 in at least one time zone.")
    fnt = sans(11)
    draw.text(((1024 - draw.textlength(dl, font=fnt)) / 2, 130), dl, font=fnt, fill=GRAY)
    draw.line((16, 148, 1008, 148), fill=LINE, width=1)


NUMBERS = [
    ("M7.2", "earthquake in Southwest Maluku, Indonesia"),
    ("11", "killed in Mexico's post-arrest cartel violence"),
    ("70+", "Saudi airstrikes the Houthis say hit eight areas of Yemen"),
    ("Rp274tn", "in 35 Indonesia–China business deals"),
    ("-3.71%", "the IHSG's fall across the week to 5,146"),
    ("4,000 yrs", "age of the bronze neck ring the melting Alps gave back"),
]


def numbers_strip(draw):
    y0, y1 = 154, 206
    draw.rectangle((16, y0, 1008, y1), fill=(238, 231, 211))
    draw.text((24, y0 + 3), "THE DAY IN NUMBERS", font=sans_b(9), fill=RED)
    colw = 992 / 6
    for i, (big, label) in enumerate(NUMBERS):
        x = 16 + i * colw + 8
        if i:
            draw.line((16 + i * colw, y0 + 6, 16 + i * colw, y1 - 6), fill=LINE, width=1)
        draw.text((x, y0 + 13), big, font=serif_b(18), fill=RED)
        block(draw, x, y0 + 34, label, sans(8), colw - 16, 9.5, color=GRAY, max_lines=2)


def region_bar(draw):
    draw.rectangle((16, 210, 1008, 232), fill=NAVY)
    txt = "EUROPE 9   ·   ASIA-PACIFIC 11   ·   AMERICAS 9   ·   MIDDLE EAST 5   ·   AFRICA 2   ·   WORLD / SCIENCE 4"
    fnt = sans_b(13)
    draw.text(((1024 - draw.textlength(txt, font=fnt)) / 2, 215), txt, font=fnt, fill=(255, 255, 255))


LEADS = [
    ("1", "SINALOA, MEXICO · CARTEL", 'Mexico captures "El Chapo Isidro"',
     "Fausto Isidro Meza Flores, on the FBI's top-10 fugitives list, is seized in a "
     "military raid in Sinaloa; cartel gunmen answer with a wave of violence — 11 "
     "killed in the north, helicopters reported showering fire.",
     "Reuters, EuroNews"),
    ("2", "KYIV, UKRAINE · WAR", "Russia strikes Kyiv's bridges after the Crimean Bridge attack",
     "Three crossings hit as Zelenskyy calls Ukraine's Kerch strike an \"appropriate "
     "reaction\"; ballistic missiles also hit Kryvyi Rih, and a Russian cargo ship "
     "burns after a drone strike in the Gulf of Finland.",
     "Reuters, Ukrinform"),
    ("3", "ANDES, PERU · EARTHQUAKE", "M6.8 quake shakes Peru",
     "The tremor rattles the Andes and sends Lima residents fleeing into the "
     "streets; no casualties immediately reported.",
     "USGS, The Hindu"),
]


def draw_lead_art(draw, idx, x, y, w, h):
    draw.rectangle((x, y, x + w, y + h), fill=SKY)
    if idx == 0:  # Sinaloa: sun, sierra, helicopter
        draw.ellipse((x + w - 70, y + 10, x + w - 26, y + 54), fill=(240, 180, 60))
        draw.polygon([(x, y + h), (x + 90, y + 38), (x + 170, y + h)], fill=(150, 120, 84))
        draw.polygon([(x + 110, y + h), (x + 210, y + 30), (x + w, y + h)], fill=(120, 94, 64))
        hx, hy = x + 52, y + 26  # helicopter silhouette
        draw.ellipse((hx, hy, hx + 44, hy + 16), fill=INK)
        draw.line((hx + 40, hy + 6, hx + 66, hy + 2), fill=INK, width=3)
        draw.line((hx - 8, hy - 4, hx + 54, hy - 4), fill=INK, width=3)
        draw.line((hx + 10, hy + 16, hx + 8, hy + 24), fill=INK, width=2)
        draw.line((hx + 34, hy + 16, hx + 36, hy + 24), fill=INK, width=2)
    elif idx == 1:  # Kyiv: bridges over the Dnipro, one span broken, smoke
        draw.rectangle((x, y + h - 26, x + w, y + h), fill=(86, 130, 168))
        for sx in (x + 150, x + 205, x + 250):
            for k in range(5):
                draw.ellipse((sx + k * 3, y + 8 + k * 2, sx + 26 + k * 4, y + 30 + k * 3),
                             outline=(90, 90, 90))
        draw.line((x, y + h - 30, x + 120, y + h - 30), fill=INK, width=5)
        draw.line((x + 120, y + h - 30, x + 168, y + h - 12), fill=INK, width=5)
        draw.line((x + 196, y + h - 18, x + w, y + h - 30), fill=INK, width=5)
        for px in (x + 40, x + 120, x + 270):
            draw.line((px, y + h - 30, px, y + h - 58), fill=INK, width=3)
        draw.polygon([(x + 168, y + 30), (x + 178, y + 44), (x + 190, y + 30),
                      (x + 184, y + 48), (x + 176, y + 38)], fill=(232, 120, 40))
    else:  # Andes: peaks, snow, quake cracks, houses
        draw.polygon([(x, y + h), (x + 90, y + 18), (x + 180, y + h)], fill=(110, 104, 120))
        draw.polygon([(x + 110, y + h), (x + 215, y + 8), (x + w, y + h)], fill=(88, 82, 100))
        draw.polygon([(x + 78, y + 34), (x + 90, y + 18), (x + 104, y + 36),
                      (x + 94, y + 30), (x + 86, y + 40)], fill=(255, 255, 255))
        draw.polygon([(x + 202, y + 26), (x + 215, y + 8), (x + 230, y + 28),
                      (x + 220, y + 20), (x + 210, y + 32)], fill=(255, 255, 255))
        draw.line((x + 30, y + h - 6, x + 52, y + h - 22, x + 44, y + h - 30,
                   x + 66, y + h - 44), fill=RED, width=3)
        for hx in (x + 236, x + 268):
            draw.rectangle((hx, y + h - 24, hx + 24, y + h - 6), fill=(196, 164, 110))
            draw.polygon([(hx - 3, y + h - 24), (hx + 12, y + h - 34), (hx + 27, y + h - 24)],
                         fill=RED)


def leads(draw):
    y0, hh = 238, 224
    colw, gap = 322, 13
    for i, (num, tag, head, body, src) in enumerate(LEADS):
        x = 16 + i * (colw + gap)
        draw.rectangle((x, y0, x + colw, y0 + hh), fill=PAPER, outline=LINE, width=1)
        draw_lead_art(draw, i, x + 8, y0 + 8, colw - 16, 92)
        draw.ellipse((x + 14, y0 + 14, x + 40, y0 + 40), fill=RED)
        nf = sans_b(15)
        draw.text((x + 27 - draw.textlength(num, font=nf) / 2, y0 + 18), num, font=nf,
                  fill=(255, 255, 255))
        ty = y0 + 108
        draw.text((x + 10, ty), tag, font=sans_b(10), fill=RED)
        ty = block(draw, x + 10, ty + 15, head, serif_b(15), colw - 20, 18)
        ty = fit_block(draw, x + 10, ty + 3, body, colw - 20, y0 + hh - ty - 22,
                       (11, 10, 9))
        draw.text((x + 10, y0 + hh - 16), "(" + src + ")", font=serif_i(9), fill=GRAY)


CARDS = [
    ("4", "ANTALYA, TÜRKIYE · CLIMATE", 'COP31\'s draft "ignores fossil fuels"',
     "Activists condemn the closing text as the summit nears its end; \"worst COP "
     "ever\" charges fly while the phase-out fight goes to the wire.",
     "Reuters, UN News", ""),
    ("5", "MALUKU, INDONESIA · EARTHQUAKE", "M7.2 quake strikes Southwest Maluku",
     "BMKG records the deep tremor as it also warns of very heavy rain across "
     "eight provinces, Java and Sumatra included, for 22–23 November.",
     "BMKG, Antara", ""),
    ("6", "JAKARTA · TRADE", "Indonesia counts the China haul",
     "Prabowo is home from Manila's ASEAN summit and Shenzhen's APEC meetings "
     "with 35 business deals worth Rp274 trillion and 30,000+ projected jobs.",
     "Antara", ""),
    ("7", "STRAIT OF HORMUZ · ENERGY", "Iran readies a tanker convoy to break the blockade",
     "Tehran organises the sailing and threatens Gulf facilities; Trump accuses "
     "Iran of breaching the MoU and vows a permanent deal to bar its nuclear path.",
     "Reports", "CLAIM"),
    ("8", "TEL AVIV · POLITICS", 'Eisenkot invites Likud to "marathon" coalition talks',
     "The opposition leader opens the door to Netanyahu's party as the split grows "
     "between the Peace Council and the premier's camp over Trump's Gaza plan.",
     "Yedioth Ahronoth", ""),
    ("9", "WASHINGTON · CYBER", "FBI probes a hack of its criminal database",
     "The NCIC system — fugitives, missing persons, stolen property — is "
     "investigated as the USDA is also hit in reported cyberattacks.",
     "Reports", ""),
    ("10", "YEMEN / RIYADH · WAR", "Houthis count 70+ Saudi airstrikes across eight areas",
     "Riyadh says it downed three missiles and a drone; explosions are heard in "
     "the Saudi capital after an air-threat warning.",
     "Reports", "CLAIM"),
    ("11", "RUGBY · SPORT", "England thrash the All Blacks",
     "A famous win after Moody fronts the haka with his team.",
     "Reports", ""),
    ("12", "PARIS · FOOTBALL", "PSG win 3-2 at Nice, but Doué is badly hurt",
     "The France forward suffers a serious injury in the victory.",
     "France 24", ""),
    ("13", "SWISS ALPS · SCIENCE", "The melting ice gives back a 4,000-year-old bronze neck ring",
     "Archaeologists recover it where a high pass's ice has receded.",
     "France 24", ""),
]


def cards(draw):
    colw, gap = 192, 8
    ys = (468, 586)
    for i, (num, tag, head, body, src, claim) in enumerate(CARDS):
        x = 16 + (i % 5) * (colw + gap)
        y0 = ys[i // 5]
        hh = 112
        draw.rectangle((x, y0, x + colw, y0 + hh), fill=PAPER, outline=LINE, width=1)
        draw.rectangle((x, y0, x + colw, y0 + 15), fill=NAVY)
        draw.text((x + 6, y0 + 3), num, font=sans_b(10), fill=GOLD)
        draw.text((x + 26, y0 + 3), tag, font=sans_b(7), fill=(255, 255, 255))
        ty = block(draw, x + 7, y0 + 19, head, serif_b(11), colw - 14, 12, max_lines=3)
        # Body at a fixed readable size; as many full lines as the card
        # holds, so no story is cut mid-sentence where it can be helped.
        bfnt = sans(8.5)
        lines = wrap(draw, body, bfnt, colw - 14)
        max_lines = max(1, int((y0 + hh - 14 - (ty + 2)) // 10.5))
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            last = lines[-1]
            while last and draw.textlength(last + " …", font=bfnt) > colw - 14:
                last = last.rsplit(" ", 1)[0]
            lines[-1] = last + " …"
        by = ty + 2
        for ln in lines:
            draw.text((x + 7, by), ln, font=bfnt, fill=INK)
            by += 10.5
        tail = "(" + src + ")" + (" · " + claim if claim else "")
        draw.text((x + 7, y0 + hh - 13), tail, font=serif_i(8), fill=GRAY)


BRIEFS = [
    ("14", "JAKARTA", "Jakarta's 2027 minimum wage is set at Rp6,136,941, the nation's highest, up 7.1% — unions protest and demand Rp6.21 million (AFU)"),
    ("15", "JAKARTA", "Prosecutors weigh a death-penalty demand for Riza Chalid in the Pertamina oil-corruption case (Kabar18)"),
    ("16", "KLUNGKUNG, BALI", "A landslide flattens buildings and vehicles; losses near Rp1 billion (Kabar18)"),
    ("17", "JAKARTA", "Guns N' Roses play GBK stadium as police warn of gridlock (Sat night show, reported Sunday) (Kabar18)"),
    ("18", "BRUSSELS", "Indonesia and the EU sign IEU-CEPA, freeing 90.4% of export tariff lines (signed Sat, Brussels) (AFU)"),
    ("19", "TALLINN", "Estonia moves to close its border with Russia; Moscow cries \"a new Iron Curtain\" (Jagran)"),
    ("20", "COPENHAGEN", "Denmark urges the EU to cap Russian visas after an alleged plot to kill a US-Ukrainian rapper is foiled (Reports)"),
    ("21", "PARIS", "France's sixth straight Saturday of protests draws a lower turnout (France 24)"),
    ("22", "PARIS", "French police officers are jailed for racist violence in a landmark ruling (France 24)"),
    ("23", "WASHINGTON", "The Pentagon curbs US–Canada military cooperation under new Hegseth guidelines (Washington Post)"),
    ("24", "WASHINGTON", "1,000+ FEMA staff are told to work from home after bed bugs infest the DC office (France 24)"),
    ("25", "WASHINGTON", "A US judge halts Trump's bid to reshape a $4 billion homeless-assistance programme (Reports)"),
    ("26", "PRETORIA", "Phumzile Mlambo-Ngcuka, South Africa's first female deputy president, dies at 71 (Reports)"),
    ("27", "BLUE NILE, SUDAN", "The Tasis alliance seizes the Bau district (Reports)"),
    ("28", "NEW YORK", "UN talks agree to create a worldwide pact on lethal autonomous weapons (Reports)"),
    ("29", "THE HAGUE", "The ICJ holds preventing genocide a collective duty of all nations (Reports)"),
    ("30", "HORMUZ", "A British marathon swimmer crosses the strait to spotlight the war's toll on marine life (Reports)"),
    ("31", "BRASÍLIA", "Bolsonaro is hospitalised with abdominal pain while in confinement (Reports)"),
    ("32", "PATNA, INDIA", "Modi inaugurates the Nitish Setu, a bridge linking Patna and Vaishali named for Nitish Kumar (PTI)"),
    ("33", "RANCHI, INDIA", "Cyclone Akvan cancels 14 flights at Ranchi airport (Jagran)"),
    ("34", "TOKYO / DELHI", "Japanese forces will use Indian facilities for live-fire training, a first (Jagran)"),
    ("35", "CANBERRA", "Pat Cummins wins Cricket Australia's unanimous backing to remain Test captain (Jagran)"),
    ("36", "CANADA", "Scientists sequence whole humpback genomes from drones flown through the whales' breath (France 24)"),
    ("37", "SAN FRANCISCO", "An Anthropic mathematician claims an AI-assisted advance on a 167-year-old maths problem (Reports)"),
    ("38", "FLORIDA", "Trump says all top-20 leaders are expected at the Florida G20 summit (Reports)"),
    ("39", "ISLAMABAD", "Pakistan hopes for an early US–Iran deal: \"the world cannot afford a prolonged conflict\" (ARY)"),
    ("40", "JAKARTA", "The IHSG ends a bruising week down 3.71% at 5,146 as BI's 6% rate anchors policy (Kabar18)"),
]


def brief_item(draw, x, y, w, num, place, text):
    fnt_b, fnt = sans_b(8), sans(8)
    prefix = num + " " + place + " — "
    pw = draw.textlength(prefix, font=fnt_b)
    draw.text((x, y), prefix, font=fnt_b, fill=NAVY)
    words = text.split()
    lines, cur, avail = [], "", w - pw
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=fnt) <= avail or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
            avail = w
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines[:3]):
        draw.text((x + (pw if i == 0 else 0), y + i * 8.5), ln, font=fnt, fill=INK)
    return y + max(1, len(lines[:3])) * 8.5 + 1.5


def briefs(draw):
    draw.rectangle((16, 704, 1008, 722), fill=RED)
    draw.text((24, 708), "ALSO ON SUNDAY 22 NOVEMBER — BRIEFS 14–40", font=sans_b(11),
              fill=(255, 255, 255))
    colw, gap = 322, 13
    ys = [728] * 3
    for i, (num, place, text) in enumerate(BRIEFS):
        c = i % 3
        x = 16 + c * (colw + gap)
        ys[c] = brief_item(draw, x, ys[c], colw, num, place, text)


CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66), (-80, 62),
     (-76, 58), (-70, 45), (-75, 38), (-80, 32), (-81, 26), (-84, 30), (-90, 21),
     (-97, 16), (-92, 15), (-83, 9), (-90, 14), (-97, 16), (-105, 20), (-110, 23),
     (-114, 29), (-117, 33), (-122, 37), (-124, 46), (-130, 55), (-150, 60), (-165, 60)],
    [(-79, 9), (-72, 12), (-64, 10), (-55, 6), (-50, 0), (-44, -3), (-35, -8),
     (-39, -13), (-40, -22), (-48, -27), (-52, -33), (-58, -39), (-62, -41),
     (-65, -45), (-67, -50), (-69, -54), (-71, -54), (-73, -46), (-73, -37),
     (-71, -30), (-70, -20), (-75, -15), (-77, -12), (-80, -5), (-81, -1), (-80, 4)],
    [(-17, 15), (-10, 29), (-6, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 12), (48, 5), (42, -2), (40, -10), (36, -20), (33, -27),
     (25, -34), (18, -33), (15, -27), (12, -18), (13, -12), (9, -1), (9, 4),
     (-8, 5), (-13, 8)],
    [(-9, 43), (-2, 44), (-1, 46), (-5, 48), (0, 50), (3, 53), (8, 55), (10, 57),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 65), (18, 69), (12, 65), (5, 60),
     (5, 58), (0, 52), (-3, 53), (-6, 54), (-10, 52), (-5, 50), (-2, 44), (-9, 37)],
    [(28, 41), (36, 36), (44, 29), (48, 30), (57, 26), (66, 25), (72, 20), (77, 8),
     (80, 13), (86, 20), (89, 22), (92, 16), (98, 10), (100, 6), (105, 9), (108, 15),
     (110, 20), (120, 25), (122, 31), (129, 33), (135, 35), (140, 40), (142, 50),
     (155, 55), (162, 60), (178, 65), (178, 69), (150, 70), (135, 72), (120, 73),
     (105, 77), (90, 75), (75, 72), (60, 69), (45, 68), (32, 65), (28, 55), (30, 46)],
    [(113, -22), (114, -28), (115, -34), (118, -35), (124, -33), (129, -32),
     (135, -35), (138, -36), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (151, -24), (146, -19), (142, -11), (142, -15), (137, -12),
     (136, -15), (132, -11), (130, -13), (126, -14), (122, -17), (117, -20)],
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44), (140, 45),
     (138, 38), (135, 34), (131, 32)],
]

ISLANDS = [(102, -2, 7, 3), (114, -1, 6, 4), (108, -7, 8, 2), (120, -2, 4, 3),
           (128, -3, 4, 2), (136, -4, 7, 3), (147, -42, 5, 4), (-3, 54, 3, 4)]

PINS = [(-107, 25), (30.5, 50.4), (-72, -13), (30.7, 36.9), (127, -3), (106.8, -6.2),
        (56.5, 26.5), (34.8, 32.1), (-77, 38.9), (48, 15.5), (-1.5, 52), (2.35, 48.85),
        (8, 46.8)]


def in_poly(lon, lat, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


PIN_OFF = {2: (0, -2), 4: (5, 3), 8: (-6, 3), 10: (6, 6), 11: (-4, -3),
           12: (-5, 3), 13: (5, -4)}


def world_map(draw):
    x0, y0, x1, y1 = 16, 894, 436, 1014
    draw.rectangle((x0, y0, x1, y1), fill=(238, 231, 211), outline=LINE, width=1)
    draw.text((x0 + 8, y0 + 5), "WHERE IT HAPPENED", font=sans_b(10), fill=NAVY)
    mx, my, mw, mh = x0 + 10, y0 + 24, x1 - x0 - 20, 90

    def proj(lon, lat):
        return (mx + (lon + 180) / 360 * mw, my + (80 - lat) / 145 * mh)

    lat = -58.0
    while lat < 80:
        lon = -178.0
        while lon < 180:
            hit = any(in_poly(lon, lat, p) for p in CONTINENTS)
            if not hit:
                for (clon, clat, rw, rh) in ISLANDS:
                    if abs(lon - clon) < rw and abs(lat - clat) < rh:
                        hit = True
                        break
            if hit:
                px, py = proj(lon, lat)
                draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill=(110, 100, 84))
            lon += 2.4
        lat += 2.4
    for i, (lon, lat) in enumerate(PINS):
        px, py = proj(lon, lat)
        dx, dy = PIN_OFF.get(i + 1, (0, 0))
        cx, cy = px + dx, py + dy
        if dx or dy:
            draw.ellipse((px - 1.5, py - 1.5, px + 1.5, py + 1.5), fill=RED)
            draw.line((px, py, cx, cy), fill=RED, width=1)
        draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=RED, outline=(255, 255, 255), width=1)
        label = str(i + 1)
        fnt = sans_b(7)
        draw.text((cx - draw.textlength(label, font=fnt) / 2, cy - 4), label,
                  font=fnt, fill=(255, 255, 255))


DATE_CHECK = (
    "DATE CHECK — Dated items are marked where they appear: the IEU-CEPA signing "
    "(Brussels, Sat) and the Guns N' Roses GBK show (Sat night). First reported "
    "Friday 20 Nov or earlier, so NOT on this page: the Shenzhen deal signings "
    "themselves · Bank Indonesia's rate decision · Cyclone Akvan's landfall · the "
    "Shenzhen trilateral declaration. Not yet: COP31's final text · any US–Iran "
    "deal · Mexico's updated official toll."
)

SOURCES = (
    "Every story here happened, or was first reported, on Sunday 22 November 2026 "
    "in at least one time zone. Claims are attributed, not stated as fact. Sources: "
    "Reuters, AP, AFP, France 24, Antara, BMKG, PTI, The Hindu, UN News. "
    "Original vector drawings."
)


def footer(draw):
    world_map(draw)
    x = 448
    draw.rectangle((x, 894, 1008, 1014), fill=PAPER, outline=LINE, width=1)
    ty = block(draw, x + 10, 900, DATE_CHECK, sans(9), 540, 11.5)
    draw.line((x + 10, ty + 3, 998, ty + 3), fill=LINE, width=1)
    block(draw, x + 10, ty + 7, SOURCES, serif_i(9), 540, 11.5, color=GRAY)


def build(path):
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    header(draw)
    numbers_strip(draw)
    region_bar(draw)
    leads(draw)
    cards(draw)
    briefs(draw)
    footer(draw)
    img.save(path, format="PNG")
    return path


if __name__ == "__main__":
    build(os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png"))

