#!/usr/bin/env python3
"""Render the v2 front page for 21 November 2026.

A single 1024x1024 newspaper page with 36 dated stories: three large
leads, ten small features, a world map and twenty-three briefs. Everything
is drawn with Pillow from hand-written shapes; there is no network access,
no clock and no unseeded randomness, so every run writes identical bytes.

Run from the repository root with:
    python3 poster/build_poster_v2.py
which writes entry.png beside main.ts.
"""

import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE_W = 1024
PAGE_H = 1024
EDGE = 14
INNER = PAGE_W - 2 * EDGE

CREAM = (247, 241, 227)
CARD = (252, 248, 238)
INK = (24, 24, 30)
NAVY = (13, 32, 54)
NAVY_SOFT = (18, 46, 74)
CRIMSON = (178, 34, 34)
CRIMSON_DK = (139, 22, 22)
GOLD = (201, 162, 39)
TEAL = (14, 92, 96)
OCHRE = (122, 90, 20)
BROWN = (122, 84, 52)
VIOLET = (104, 78, 140)
SLATE = (70, 70, 78)
MUTED = (90, 88, 80)
HAIRLINE = (180, 172, 150)
SAND = (222, 196, 150)
WHITE = (255, 255, 255)

FONT_HOME = Path("/usr/share/fonts/truetype/liberation")


def _load(name, size):
    return ImageFont.truetype(str(FONT_HOME / name), size)


def serif_b(size):
    return _load("LiberationSerif-Bold.ttf", size)


def serif(size):
    return _load("LiberationSerif-Regular.ttf", size)


def serif_i(size):
    return _load("LiberationSerif-Italic.ttf", size)


def sans(size):
    return _load("LiberationSans-Regular.ttf", size)


def sans_b(size):
    return _load("LiberationSans-Bold.ttf", size)


def sans_i(size):
    return _load("LiberationSans-Italic.ttf", size)


def split_lines(draw, text, fnt, width):
    """Greedy wrap of `text` to lines no wider than `width`."""
    out, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def para(draw, x, y, text, fnt, width, fill=INK, gap=None):
    """Draw wrapped text starting at (x, y); return y below the block."""
    if gap is None:
        gap = int(fnt.size * 1.22)
    for line in split_lines(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += gap
    return y


def centred(draw, y, text, fnt, fill=INK):
    """Draw one line centred on the page; return the next y."""
    w = draw.textlength(text, font=fnt)
    draw.text(((PAGE_W - w) / 2, y), text, font=fnt, fill=fill)
    return y + int(fnt.size * 1.2)


def first_line_rest(draw, text, fnt, first_width, rest_width):
    """Wrap where the opening line is narrower than the following ones."""
    out, cur, limit = [], "", first_width
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= limit or not cur:
            cur = trial
        else:
            out.append(cur)
            cur = word
            limit = rest_width
    if cur:
        out.append(cur)
    return out

# ------------------------------------------------------------------ content

NUMBERS = [
    ("400+", "drones fired at Ukraine overnight"),
    ("110+", "missiles in the same barrage"),
    ("-3.7%", "S&P 500 falls into correction"),
    ("6.9", "magnitude quake shakes Peru's Andes"),
    ("25", "European countries hit by Gen Z protests"),
    ("$7.25bn", "Bayer Roundup settlement approved"),
]

# label, colour — counts sum to 36 over seven regions
REGIONS = [
    ("EUROPE 9", NAVY),
    ("AMERICAS 10", CRIMSON),
    ("ASIA-PACIFIC 4", TEAL),
    ("MIDEAST 6", OCHRE),
    ("AFRICA 2", BROWN),
    ("OCEANIA 2", VIOLET),
    ("WORLD 3", SLATE),
]

BIG_STORIES = [
    {
        "kick": "01 · KYIV & POLAND · WAR",
        "head": "Missiles land in Poland as Kyiv is hit again",
        "body": ("Overnight barrage of 400+ drones and 110+ missiles struck "
                 "Kyiv's bridges, power and rail; two Russian missiles and a "
                 "suspected drone came down in Poland. PM Tusk calls it a "
                 "deliberate provocation. (Reuters, AP)"),
        "art": "kyiv",
    },
    {
        "kick": "02 · NEW YORK & TOKYO · MARKETS",
        "head": "AI sell-off sinks markets into correction",
        "body": ("S&P 500 falls 3.7% into correction as AI and chip stocks "
                 "rout Wall Street; Nasdaq drops 5.3%, Nikkei 5.1% to "
                 "56,436.65, Hang Seng 1.9%. (Reuters, AP)"),
        "art": "markets",
    },
    {
        "kick": "03 · ANTALYA, TÜRKIYE · CLIMATE",
        "head": "COP31 runs overtime with no fossil-fuel deal",
        "body": ("UN climate talks pass their deadline with ~200 nations "
                 "deadlocked over fossil fuels; no agreement yet as "
                 "negotiators work into the weekend. (UN News, Reuters)"),
        "art": "cop",
    },
]

SMALL_STORIES = [
    {"kick": "04 · JUNÍN, PERU · QUAKE",
     "head": "6.9 quake shakes Peru's Andes",
     "body": "Strong tremor felt in Lima; no immediate reports of major damage. (Reuters)",
     "art": "quake", "tag": "6.9"},
    {"kick": "05 · WASHINGTON · CYBER",
     "head": "FBI database reportedly hacked",
     "body": "Criminal database and USDA systems hit as US outages continue. (Reuters)",
     "art": "hack", "tag": "HACKED"},
    {"kick": "06 · RIYADH · MISSILES",
     "head": "Houthis fire on Riyadh; three intercepted",
     "body": "Coalition says three missiles were stopped over the capital. (Reuters)",
     "art": "riyadh", "tag": "3 DOWN"},
    {"kick": "07 · BERLIN · PROTESTS",
     "head": "Gen Z protests spread to 25 countries",
     "body": "Youth-led protests spread across 25 European countries. (AP)",
     "art": "protest", "tag": "25"},
    {"kick": "08 · LONDON · HEALTH",
     "head": "Cancer pill undetectable in 1 in 12",
     "body": "Daraxonrasib trial: tumours undetectable on scans in one in 12 patients. (Reuters)",
     "art": "pill", "tag": "1 IN 12"},
    {"kick": "09 · STRAIT OF HORMUZ · DRONE",
     "head": "Iran says it downed a US MQ-9",
     "body": "Tehran says the drone is the 58th American MQ-9 it has brought down. (Reuters)",
     "art": "drone", "tag": "58TH"},
    {"kick": "10 · INDONESIA · FIRES",
     "head": "Massive forest fires hit Indonesia",
     "body": "Forest fires burn across Indonesia; crews battle the blazes. (AP)",
     "art": "fires", "tag": "FIRES"},
    {"kick": "11 · UNITED STATES · COURTS",
     "head": "Judge approves $7.25bn Bayer deal",
     "body": "Roundup settlement validated, ending thousands of complaints. (Reuters)",
     "art": "scales", "tag": "$7.25BN"},
    {"kick": "12 · BASRA, IRAQ · FIRE",
     "head": "Power-plant fire kills at least four",
     "body": "Blaze at the Hartha plant kills at least four. (Reuters)",
     "art": "plant", "tag": "4 DEAD"},
    {"kick": "13 · LOS ANGELES · FIRE",
     "head": "Man convicted over Palisades fire",
     "body": "Jury convicts him of starting the deadly fire. (AP)",
     "art": "flame", "tag": "GUILTY"},
]

# number, place, text — briefs 14-30 and 35-36 are the v1 wording;
# 31-34 are the new Africa + Oceania coverage for v2.
BRIEFS = [
    (14, "HORMUZ", "Lewis Pugh swims the Strait of Hormuz to spotlight the war's wildlife toll. (Reuters)"),
    (15, "GAZA", "Israeli strikes kill Palestinians in Gaza; West Bank violence continues. (AP)"),
    (16, "MADRID", "Spain heads to a 29 November election as conservatives gain. (Reuters)"),
    (17, "PORT-AU-PRINCE", "Salvadoran troops in Haiti lose soldiers to explosives. (AP)"),
    (18, "INDIA", "Eleven dead and 180+ hospitalised after drinking toxic alcohol. (Straits Times)"),
    (19, "WASHINGTON", "Trump defends his closeness to Putin and Xi on his return from Asia. (Reuters)"),
    (20, "WASHINGTON", "Trump tells Europe to defund Ukraine after his summit with Putin. (Telegraph)"),
    (21, "COPENHAGEN", "Denmark ratifies the US Greenland security deal, 109-0. (Reuters)"),
    (22, "PYONGYANG", "North Korea expanding Yongbyon uranium enrichment. (IAEA)"),
    (23, "DHAKA", "Violence flares in Bangladesh ahead of Hasina's planned return. (Reuters)"),
    (24, "CARACAS", "US signs a new military deal with Venezuela. (Reuters)"),
    (25, "KERCH", "Ukraine strikes the bridge to Crimea for a third time in four days. (Reuters)"),
    (26, "WASHINGTON", "Anthropic mathematician says he proved the Riemann hypothesis using AI."),
    (27, "BRUSSELS", "UK and EU sign three post-Brexit agreements, their biggest since Brexit. (Reuters)"),
    (28, "LAS VEGAS", "Antonelli fastest in GP qualifying; Verstappen on pole after a penalty. (Reuters)"),
    (29, "CLEVELAND", "Harden scores 51, passing Kobe Bryant, as the Cavaliers beat the Pacers. (ESPN)"),
    (30, "TURIN", "Sinner beats Tiafoe 6-3, 6-4 to reach the ATP Finals semi-finals. (ATP)"),
    (31, "JOHANNESBURG", "South Africa mourns ex-deputy president Phumzile Mlambo-Ngcuka, 71. (Zambian Observer)"),
    (32, "BLANTYRE", "Malawi fuel crisis drags on; government gives no end date. (Malawi News)"),
    (33, "COOK ISLANDS", "Cyclone Xavier, ex-Category 5, weakens east of Pago Pago. (JTWC)"),
    (34, "MELBOURNE", "North Melbourne reach a fourth straight AFL Women's grand final. (One Turn)"),
    (35, "BAGHDAD", "Iraq arrests its oil-transport chief on oil-smuggling charges."),
    (36, "KYIV", "Ukrainian drones hit a Russian fertiliser plant that also makes explosives."),
]

DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as 21 Nov news: "
              "Trump–Xi–Putin Shenzhen summit · Anthropic Nasdaq debut ($2tn) · "
              "ICJ Rohingya genocide verdict · GTA VI launch · "
              "Senate Iran war-powers vote 51–48.")

CLOSING = ("Every story here happened, or was first reported, on Saturday 21 November 2026 "
           "in at least one time zone. Sources: Reuters, AP, AFP, BBC, UN News, "
           "Al Jazeera. Original vector drawings.")

# Map pins, one per drawn story 1-13: (longitude, latitude)
PIN_SPOTS = [
    (30.5, 50.4),    # Kyiv
    (-74.0, 40.7),   # New York
    (33.0, 34.0),    # Antalya (nudged south of Kyiv)
    (-75.2, -10.0),  # Junin, Peru
    (-77.0, 38.9),   # Washington
    (40.0, 16.0),    # Riyadh (nudged SW of the Hormuz/Basra cluster)
    (14.0, 55.0),    # Berlin (nudged NE of London)
    (-2.0, 50.0),    # London
    (60.0, 20.0),    # Hormuz (nudged SE of the Basra cluster)
    (113.0, -2.0),   # Indonesia
    (-95.0, 38.0),   # United States
    (47.8, 30.5),    # Basra
    (-118.2, 34.0),  # Los Angeles
]

# ------------------------------------------------------------------ pictures

def _seeded(seed):
    return random.Random(seed)


def _night_stars(d, x, y, w, h, seed, count=24):
    rng = _seeded(seed)
    for _ in range(count):
        sx = rng.randint(x + 3, x + w - 3)
        sy = rng.randint(y + 3, y + h // 2)
        r = rng.choice([1, 1, 2])
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=WHITE)


def paint_kyiv(d, x, y, w, h):
    """Night skyline under a missile barrage."""
    rng = _seeded(11)
    d.rectangle([x, y, x + w, y + h], fill=(10, 22, 44))
    _night_stars(d, x, y, w, h, 12, 30)
    floor = y + h - 8
    cx = x + 6
    while cx < x + w - 16:
        bw = rng.randint(16, 30)
        bh = rng.randint(22, 52)
        d.rectangle([cx, floor - bh, cx + bw, floor], fill=(24, 34, 56))
        for wy in range(floor - bh + 5, floor - 6, 9):
            for wx in range(cx + 4, cx + bw - 4, 8):
                if rng.random() < 0.5:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
        cx += bw + 4
    for i in range(3):
        sx = x + 40 + i * 90
        sy = y + 14 + i * 10
        ex, ey = sx + 70, sy + 42
        pts = []
        for t in range(11):
            f = t / 10.0
            pts.append((sx + (ex - sx) * f, sy + (ey - sy) * f * f))
        d.line(pts, fill=(255, 150, 60), width=2)
        d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 120, 40))
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 220, 140))
    for fx in (x + 60, x + 200, x + 280):
        d.polygon([(fx - 9, floor), (fx, floor - 16), (fx + 9, floor)],
                  fill=(255, 140, 40))
        d.polygon([(fx - 5, floor), (fx, floor - 9), (fx + 5, floor)],
                  fill=(255, 220, 90))


def paint_markets(d, x, y, w, h):
    """Dark panel: index table with a falling chart line."""
    rng = _seeded(21)
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 10, y + 5), "US & ASIA · FRIDAY CLOSES",
           font=sans_b(9), fill=(170, 185, 205))
    pts = []
    for i in range(7):
        px = x + w * 0.62 + w * 0.34 * i / 6
        py = y + 6 + i * 2 + rng.randint(-1, 1)
        pts.append((px, py))
    d.line(pts, fill=(255, 70, 60), width=2)
    rows = [("NIKKEI", "-5.1%"), ("NASDAQ", "-5.3%"),
            ("S&P 500", "-3.7%"), ("HANG SENG", "-1.9%")]
    ry = y + 24
    for name, val in rows:
        d.text((x + 10, ry), name, font=sans_b(12), fill=(220, 225, 235))
        vw = d.textlength(val, font=sans_b(13))
        d.text((x + w - 10 - vw, ry), val, font=sans_b(13), fill=(255, 90, 80))
        d.line([x + 8, ry + 15, x + w - 8, ry + 15], fill=(60, 80, 110), width=1)
        ry += 17


def paint_cop(d, x, y, w, h):
    """Teal panel: globe, thermometer and the COP31 label."""
    d.rectangle([x, y, x + w, y + h], fill=TEAL)
    cx, cy, r = x + 52, y + 52, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 130, 140))
    d.ellipse([cx - r + 10, cy - r + 8, cx - 2, cy - 4], fill=(90, 170, 120))
    d.ellipse([cx + 2, cy + 2, cx + r - 8, cy + r - 10], fill=(120, 180, 110))
    d.ellipse([cx - r + 14, cy - 6, cx + r - 16, cy + r - 6],
              fill=(38, 130, 140))
    tx = x + 148
    d.rounded_rectangle([tx, y + 14, tx + 16, y + h - 26], radius=8,
                        fill=(240, 240, 235), outline=(180, 40, 40), width=2)
    d.ellipse([tx - 5, y + h - 34, tx + 21, y + h - 8], fill=(200, 40, 40))
    d.rectangle([tx + 4, y + 34, tx + 12, y + h - 20], fill=(200, 40, 40))
    d.text((x + 8, y + 6), "COP31", font=sans_b(15), fill=WHITE)


def paint_quake(d, x, y, w, h):
    """Two mountain peaks with crack lines."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    d.polygon([(x + 8, y + h - 6), (x + 58, y + 12), (x + 108, y + h - 6)],
              fill=(120, 84, 50))
    d.polygon([(x + 92, y + h - 6), (x + 140, y + 4), (x + 182, y + h - 6)],
              fill=(90, 90, 100))
    d.polygon([(x + 48, y + 20), (x + 58, y + 12), (x + 68, y + 20)],
              fill=WHITE)
    d.polygon([(x + 132, y + 12), (x + 140, y + 4), (x + 148, y + 12)],
              fill=WHITE)
    d.line([(x + 60, y + h - 6), (x + 74, y + h - 22), (x + 66, y + h - 34)],
           fill=(60, 40, 25), width=2)
    d.line([(x + 150, y + h - 6), (x + 142, y + h - 20), (x + 152, y + h - 30)],
           fill=(60, 40, 25), width=2)


def paint_hack(d, x, y, w, h):
    """Padlock on dark blue, binary digits in the corners."""
    rng = _seeded(31)
    d.rectangle([x, y, x + w, y + h], fill=(16, 30, 58))
    lx, ly = x + 46, y + 26
    d.arc([lx - 11, ly - 10, lx + 11, ly + 10], 180, 360,
          fill=(255, 210, 90), width=4)
    d.rounded_rectangle([lx - 16, ly + 8, lx + 16, ly + 26], radius=4,
                        fill=(210, 60, 50))
    d.ellipse([lx - 3, ly + 13, lx + 3, ly + 19], fill=WHITE)
    d.rectangle([lx - 1, ly + 18, lx + 1, ly + 24], fill=WHITE)
    for bx, by in ((x + 6, y + 4), (x + 6, y + 16), (x + w - 44, y + 26),
                   (x + w - 44, y + 38), (x + 96, y + h - 14),
                   (x + 130, y + h - 14)):
        d.text((bx, by), rng.choice(["1010", "0110", "1101", "0011"]),
               font=sans(9), fill=(110, 160, 220))


def paint_riyadh(d, x, y, w, h):
    """City at night with three interception bursts."""
    rng = _seeded(41)
    d.rectangle([x, y, x + w, y + h], fill=(18, 44, 78))
    _night_stars(d, x, y, w, h, 42, 12)
    floor = y + h - 6
    cx = x + 8
    while cx < x + w - 10:
        bw = rng.randint(14, 26)
        bh = rng.randint(16, 38)
        d.rectangle([cx, floor - bh, cx + bw, floor], fill=(30, 60, 100))
        for wy in range(floor - bh + 4, floor - 5, 8):
            for wx in range(cx + 3, cx + bw - 3, 7):
                if rng.random() < 0.4:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 214, 120))
        cx += bw + 3
    for ix, iy in ((x + 32, y + 14), (x + 70, y + 20), (x + 106, y + 14)):
        for dx, dy in ((-9, -4), (9, -4), (-9, 4), (9, 4), (0, -8), (0, 8)):
            d.line([ix, iy, ix + dx, iy + dy], fill=(255, 200, 90), width=2)
        d.ellipse([ix - 3, iy - 3, ix + 3, iy + 3], fill=(255, 230, 150))


def paint_protest(d, x, y, w, h):
    """A row of marchers carrying small placards."""
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    floor = y + h - 6
    for i in range(5):
        px = x + 20 + i * 30
        d.ellipse([px - 4, floor - 20, px + 4, floor - 12], fill=(40, 40, 44))
        d.polygon([(px - 5, floor - 11), (px + 5, floor - 11),
                   (px + 4, floor), (px - 4, floor)], fill=(60, 60, 70))
        d.line([px + 5, floor - 18, px + 12, floor - 30],
               fill=(90, 70, 40), width=2)
        d.rectangle([px + 6, floor - 38, px + 22, floor - 30],
                    fill=(200, 60, 50) if i % 2 == 0 else (30, 90, 140))
    d.line([x + 6, floor, x + w - 6, floor], fill=(120, 110, 95), width=2)


def paint_pill(d, x, y, w, h):
    """A tilted capsule with small pills around it."""
    d.rectangle([x, y, x + w, y + h], fill=(244, 238, 226))
    cx, cy = x + 76, y + 26
    d.rounded_rectangle([cx - 38, cy - 11, cx + 38, cy + 11], radius=11,
                        fill=(214, 60, 70))
    d.rounded_rectangle([cx - 38, cy - 11, cx, cy + 11], radius=11,
                        fill=WHITE)
    d.ellipse([cx - 38, cy - 11, cx - 16, cy + 11], fill=WHITE)
    d.line([cx - 52, cy, cx + 52, cy], fill=(180, 40, 50), width=1)
    for px, py, col in ((x + 22, y + h - 18, (30, 120, 130)),
                        (x + 44, y + h - 14, (214, 120, 40)),
                        (x + w - 30, y + h - 18, (90, 90, 160))):
        d.ellipse([px - 8, py - 5, px + 8, py + 5], fill=col)


def paint_drone(d, x, y, w, h):
    """A jet over the sea, with a dotted flight path."""
    rng = _seeded(51)
    d.rectangle([x, y, x + w, y + h], fill=(16, 52, 84))
    for _ in range(10):
        sx = rng.randint(x + 4, x + w - 4)
        sy = rng.randint(y + 4, y + h - 4)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(200, 220, 255))
    cx, cy = x + 88, y + 30
    d.polygon([(cx - 36, cy), (cx + 20, cy - 6), (cx + 36, cy),
               (cx + 20, cy + 6)], fill=(30, 34, 40))
    d.polygon([(cx - 8, cy - 5), (cx + 4, cy - 20), (cx + 10, cy - 5)],
              fill=(30, 34, 40))
    d.polygon([(cx - 8, cy + 5), (cx + 4, cy + 20), (cx + 10, cy + 5)],
              fill=(30, 34, 40))
    d.ellipse([cx + 22, cy - 2, cx + 30, cy + 2], fill=(140, 200, 230))
    for i in range(5):
        px = x + 12 + i * 14
        py = y + 10 + i * 3
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 200, 100))
    d.line([x, y + h - 10, x + w, y + h - 10], fill=(90, 160, 200), width=2)
    d.line([x + 20, y + h - 5, x + 60, y + h - 5], fill=(60, 130, 170), width=1)


def paint_fires(d, x, y, w, h):
    """Pine trees with flames and a low sun."""
    rng = _seeded(61)
    d.rectangle([x, y, x + w, y + h], fill=(28, 52, 30))
    floor = y + h - 6
    for i in range(5):
        tx = x + 16 + i * 34
        th = rng.randint(20, 34)
        d.polygon([(tx - 12, floor), (tx, floor - th), (tx + 12, floor)],
                  fill=(20, 80, 40))
        d.rectangle([tx - 2, floor - 8, tx + 2, floor], fill=(90, 60, 30))
    for fx in (x + 40, x + 110, x + 160):
        d.polygon([(fx - 9, floor), (fx, floor - 20), (fx + 9, floor)],
                  fill=(255, 140, 30))
        d.polygon([(fx - 5, floor), (fx, floor - 11), (fx + 5, floor)],
                  fill=(255, 220, 90))
    d.ellipse([x + 150, y + 6, x + 168, y + 20], fill=(255, 220, 150))


def paint_scales(d, x, y, w, h):
    """The scales of justice on cream."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 220))
    cx = x + 96
    top = y + 8
    d.line([cx, top, cx, y + h - 12], fill=(60, 50, 35), width=3)
    d.line([cx - 52, top + 8, cx + 52, top + 8], fill=(60, 50, 35), width=3)
    for sx in (cx - 52, cx + 52):
        d.line([sx, top + 8, sx, top + 30], fill=(60, 50, 35), width=2)
        d.arc([sx - 20, top + 26, sx + 20, top + 46], 0, 180,
              fill=(150, 120, 50), width=3)
        d.line([sx - 20, top + 36, sx + 20, top + 36],
               fill=(150, 120, 50), width=2)
    d.ellipse([cx - 5, top - 4, cx + 5, top + 6], fill=(150, 120, 50))
    d.rectangle([cx - 24, y + h - 12, cx + 24, y + h - 6], fill=(60, 50, 35))


def paint_plant(d, x, y, w, h):
    """Cooling tower, chimneys and a small fire."""
    d.rectangle([x, y, x + w, y + h], fill=(36, 36, 44))
    floor = y + h - 6
    d.polygon([(x + 30, floor), (x + 38, y + 16), (x + 62, y + 16),
               (x + 70, floor)], fill=(120, 120, 130))
    d.ellipse([x + 38, y + 12, x + 62, y + 20], fill=(90, 90, 100))
    for sx in (x + 96, x + 118):
        d.rectangle([sx, y + 10, sx + 12, floor], fill=(160, 90, 50))
        d.rectangle([sx - 2, y + 6, sx + 14, y + 12], fill=(120, 60, 35))
    for i in range(3):
        d.ellipse([x + 94 + i * 7, y + 2, x + 106 + i * 7, y + 11],
                  fill=(200, 200, 205))
    d.polygon([(x + 150, floor), (x + 160, floor - 22), (x + 170, floor)],
              fill=(255, 140, 30))
    d.line([x + 8, floor, x + w - 8, floor], fill=(200, 200, 200), width=2)


def paint_flame(d, x, y, w, h):
    """One large flame with embers."""
    rng = _seeded(71)
    d.rectangle([x, y, x + w, y + h], fill=(24, 22, 28))
    cx = x + 96
    floor = y + h - 8
    d.polygon([(cx - 34, floor), (cx - 8, y + 14), (cx + 10, y + 30),
               (cx + 34, floor)], fill=(230, 90, 30))
    d.polygon([(cx - 18, floor), (cx, y + 26), (cx + 18, floor)],
              fill=(255, 190, 60))
    d.polygon([(cx - 8, floor), (cx, y + 38), (cx + 8, floor)],
              fill=(255, 240, 160))
    for _ in range(8):
        ex = rng.randint(x + 20, x + w - 20)
        ey = rng.randint(y + 8, y + 26)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(255, 160, 60))


PAINTERS = {
    "kyiv": paint_kyiv, "markets": paint_markets, "cop": paint_cop,
    "quake": paint_quake, "hack": paint_hack, "riyadh": paint_riyadh,
    "protest": paint_protest, "pill": paint_pill, "drone": paint_drone,
    "fires": paint_fires, "scales": paint_scales, "plant": paint_plant,
    "flame": paint_flame,
}

# ------------------------------------------------------------------ the map

# Hand-drawn continent outlines, (longitude, latitude) pairs.
LAND = [
    # North America
    [(-166, 66), (-150, 70), (-130, 71), (-110, 69), (-95, 68), (-85, 66),
     (-78, 60), (-66, 58), (-56, 50), (-62, 46), (-70, 41), (-75, 35),
     (-80, 27), (-84, 30), (-90, 21), (-97, 25), (-105, 22), (-112, 25),
     (-118, 33), (-124, 41), (-124, 49), (-135, 58), (-155, 58),
     (-164, 60), (-166, 66)],
    # South America
    [(-78, 8), (-77, 3), (-80, -4), (-79, -10), (-74, -16), (-70, -22),
     (-70, -32), (-72, -44), (-73, -50), (-66, -55), (-65, -46),
     (-61, -38), (-56, -34), (-48, -27), (-41, -22), (-36, -8),
     (-38, -4), (-45, -2), (-51, 1), (-56, 4), (-61, 9), (-68, 11),
     (-74, 11), (-78, 8)],
    # Africa
    [(-6, 35), (8, 37), (19, 33), (29, 31), (33, 29), (38, 21),
     (41, 15), (44, 11), (51, 11), (46, 1), (41, -5), (39, -12),
     (35, -19), (32, -27), (27, -33), (18, -35), (15, -28), (12, -18),
     (13, -11), (9, -1), (9, 4), (0, 6), (-8, 4), (-13, 8),
     (-16, 14), (-17, 21), (-15, 27), (-10, 31), (-6, 35)],
    # Europe
    [(-10, 36), (-9, 43), (-3, 44), (-1, 47), (-4, 49), (0, 51),
     (3, 53), (7, 55), (9, 58), (6, 62), (12, 65), (18, 69),
     (26, 71), (31, 70), (38, 68), (45, 68), (49, 64), (50, 58),
     (46, 53), (41, 48), (37, 46), (30, 45), (27, 43), (22, 40),
     (18, 39), (13, 44), (8, 44), (3, 42), (0, 39), (-3, 36),
     (-10, 36)],
    # Asia
    [(-10, 36), (28, 36), (36, 36), (38, 41), (44, 40), (49, 39),
     (53, 37), (57, 26), (62, 25), (68, 24), (73, 19), (78, 8),
     (82, 14), (89, 22), (93, 20), (98, 15), (101, 8), (104, 3),
     (106, 10), (110, 15), (115, 22), (120, 29), (122, 33), (127, 40),
     (131, 43), (136, 44), (141, 47), (142, 54), (155, 51), (162, 56),
     (161, 61), (170, 66), (179, 66), (172, 69), (160, 70), (148, 71),
     (136, 72), (124, 73), (112, 74), (100, 76), (88, 75), (78, 72),
     (68, 69), (58, 68), (50, 68), (44, 68), (38, 68), (31, 70),
     (25, 71), (18, 69), (12, 65), (6, 62), (9, 58), (7, 55),
     (3, 53), (0, 51), (-4, 49), (-1, 47), (-3, 44), (-9, 43),
     (-10, 36)],
    # Australia
    [(114, -22), (114, -31), (117, -35), (124, -33), (130, -32),
     (136, -35), (140, -38), (146, -39), (150, -37), (153, -27),
     (152, -22), (146, -19), (142, -11), (136, -12), (131, -12),
     (126, -14), (121, -18), (114, -22)],
]


def paint_tag(d, x, y, w, text, fill=CRIMSON):
    """Small white-on-colour label pinned to the top-right of an art box."""
    f = sans_b(10)
    tw = d.textlength(text, font=f)
    bw = int(tw) + 12
    bx = x + w - 4 - bw
    d.rectangle([bx, y + 4, bx + bw, y + 22], fill=fill)
    d.text((bx + 6, y + 6), text, font=f, fill=WHITE)


def paint_brief(d, x, y, num, place, text, width):
    """One brief entry; returns the y just below it."""
    head = "%d %s — " % (num, place)
    fb, fr = sans_b(8), sans(8)
    hw = d.textlength(head, font=fb)
    lines = first_line_rest(d, text, fr, width - hw, width)
    d.text((x, y), head, font=fb, fill=INK)
    d.text((x + hw, y), lines[0], font=fr, fill=INK)
    for j, line in enumerate(lines[1:], start=1):
        d.text((x, y + 10 * j), line, font=fr, fill=INK)
    return y + 10 * len(lines) + 1


def render():
    img = Image.new("RGB", (PAGE_W, PAGE_H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((EDGE, 7), "THE WORLD IN ONE DAY", font=sans_b(13), fill=CRIMSON)
    corner = "SATURDAY'S NEWS · ONE PAGE · 36 STORIES · 7 REGIONS"
    d.text((PAGE_W - EDGE - d.textlength(corner, font=sans_b(11)), 8),
           corner, font=sans_b(11), fill=INK)

    # ---- date, strap, rule
    centred(d, 24, "Saturday 21 November 2026", serif_b(54), INK)
    centred(d, 90, "Missiles land in Poland · An AI sell-off sinks markets · "
                   "COP31 runs overtime", serif_i(15), CRIMSON)
    d.line([EDGE, 112, PAGE_W - EDGE, 112], fill=INK, width=2)

    # ---- six-number strip
    cell = INNER // 6
    for i, (num, cap) in enumerate(NUMBERS):
        x = EDGE + i * cell
        if i:
            d.line([x, 120, x, 168], fill=(200, 192, 172), width=1)
        d.text((x + 6, 118), num, font=sans_b(26), fill=CRIMSON)
        para(d, x + 6, 150, cap, sans(10), cell - 12, fill=MUTED, gap=12)

    # ---- region bar: widths proportional to each count
    total = sum(int(label.rsplit(" ", 1)[1]) for label, _ in REGIONS)
    rx = EDGE
    for label, colour in REGIONS:
        count = int(label.rsplit(" ", 1)[1])
        rw = int(INNER * count / total)
        d.rectangle([rx, 176, rx + rw - 1, 196], fill=colour)
        f = sans_b(10)
        tw = d.textlength(label, font=f)
        d.text((rx + (rw - tw) / 2, 179), label, font=f, fill=WHITE)
        rx += rw

    # ---- three lead cards
    lead_w, lead_gap, lead_y, lead_h = 324, 12, 202, 200
    for i, story in enumerate(BIG_STORIES):
        x = EDGE + i * (lead_w + lead_gap)
        d.rectangle([x, lead_y, x + lead_w, lead_y + lead_h],
                    fill=CARD, outline=HAIRLINE, width=1)
        PAINTERS[story["art"]](d, x + 1, lead_y + 1, lead_w - 2, 96)
        if story["art"] == "kyiv":
            d.rectangle([x + 1, lead_y + 78, x + lead_w - 1, lead_y + 97],
                        fill=CRIMSON_DK)
            d.text((x + 10, lead_y + 82), "400+ DRONES · 110+ MISSILES",
                   font=sans_b(11), fill=WHITE)
        if story["art"] == "cop":
            bw = d.textlength("OVERTIME", font=sans_b(10)) + 14
            d.rectangle([x + lead_w - 6 - bw, lead_y + 6,
                         x + lead_w - 6, lead_y + 42], fill=CRIMSON)
            d.text((x + lead_w - 6 - bw + 7, lead_y + 10), "NO DEAL",
                   font=sans_b(10), fill=WHITE)
            d.text((x + lead_w - 6 - bw + 7, lead_y + 24), "OVERTIME",
                   font=sans_b(10), fill=WHITE)
        ty = lead_y + 104
        d.text((x + 8, ty), story["kick"], font=sans_b(10), fill=CRIMSON)
        ty += 14
        ty = para(d, x + 8, ty, story["head"], serif_b(16),
                  lead_w - 16, fill=INK, gap=19)
        para(d, x + 8, ty + 3, story["body"], sans(10),
             lead_w - 16, fill=INK, gap=12)

    # ---- ten feature cards, two rows of five
    feat_w, feat_gap, feat_h = 192, 9, 108
    for row, fy in enumerate((408, 524)):
        for col in range(5):
            story = SMALL_STORIES[row * 5 + col]
            x = EDGE + col * (feat_w + feat_gap)
            d.rectangle([x, fy, x + feat_w, fy + feat_h],
                        fill=CARD, outline=HAIRLINE, width=1)
            PAINTERS[story["art"]](d, x + 1, fy + 1, feat_w - 2, 48)
            paint_tag(d, x + 1, fy + 1, feat_w - 2, story["tag"],
                      fill=CRIMSON if col % 3 else NAVY)
            ty = fy + 53
            d.text((x + 6, ty), story["kick"], font=sans_b(8), fill=CRIMSON)
            ty += 11
            ty = para(d, x + 6, ty, story["head"], serif_b(12),
                      feat_w - 12, fill=INK, gap=14)
            para(d, x + 6, ty + 1, story["body"], sans(8),
                 feat_w - 12, fill=INK, gap=10)

    # ---- lower section headers
    d.text((EDGE, 638), "WHERE IT HAPPENED", font=sans_b(11), fill=CRIMSON)
    d.text((496, 638), "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES",
           font=sans_b(11), fill=CRIMSON)
    tail = "ALL STORIES: SAT 21 NOV 2026"
    d.text((PAGE_W - EDGE - d.textlength(tail, font=sans(9)), 639),
           tail, font=sans(9), fill=MUTED)

    # ---- map (light continents on navy)
    mx, my, mw, mh = EDGE, 658, 470, 212
    d.rectangle([mx, my, mx + mw, my + mh], fill=NAVY)
    d.text((mx + 8, my + 4), "Pins 1–13 mark the drawn stories",
           font=sans(9), fill=(200, 205, 215))

    def project(lon, lat):
        px = mx + 8 + (lon + 180.0) / 360.0 * (mw - 16)
        py = my + 22 + (75.0 - lat) / 132.0 * (mh - 30)
        return (px, py)

    for poly in LAND:
        d.polygon([project(lon, lat) for lon, lat in poly], fill=SAND)
    for lon in range(-150, 181, 30):
        for lat in range(-45, 76, 30):
            px, py = project(lon, lat)
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(60, 80, 110))
    for i, (lon, lat) in enumerate(PIN_SPOTS, start=1):
        px, py = project(lon, lat)
        ring = GOLD if i <= 3 else WHITE
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=CRIMSON,
                  outline=ring, width=2)
        tw = d.textlength(str(i), font=sans_b(9))
        d.text((px - tw / 2, py - 6), str(i), font=sans_b(9), fill=WHITE)
    badge = "36 STORIES"
    bw = d.textlength(badge, font=sans_b(11)) + 16
    d.rounded_rectangle([mx + mw - bw - 8, my + 6, mx + mw - 8, my + 28],
                        radius=11, fill=GOLD)
    d.text((mx + mw - bw, my + 9), badge, font=sans_b(11), fill=NAVY)
    d.text((mx, 876), "1–3 Lead (gold ring) · 4–13 Features",
           font=sans(9), fill=INK)
    d.text((mx, 888), "Positions approximate.", font=sans(9), fill=MUTED)

    # ---- briefs, two columns
    for cx, items in ((496, BRIEFS[:11]), (756, BRIEFS[11:])):
        yy = 658
        for num, place, text in items:
            yy = paint_brief(d, cx, yy, num, place, text, 252)
            yy += 1
            if yy > 944:
                print("WARNING: briefs overflow at %d %s (y=%d)"
                      % (num, place, yy))

    # ---- date check + footer
    d.rectangle([EDGE, 948, PAGE_W - EDGE, 988], outline=CRIMSON, width=2)
    d.text((EDGE + 8, 952), "DATE CHECK", font=sans_b(10), fill=CRIMSON)
    para(d, EDGE + 8, 966, DATE_CHECK, sans(9), INNER - 16,
         fill=INK, gap=11)
    centred(d, 994, CLOSING, sans_i(8), MUTED)

    return img


def main():
    out = Path(__file__).resolve().parent.parent / "entry.png"
    img = render()
    img.save(out, format="PNG")
    data = out.read_bytes()
    print("wrote %s %d bytes sha256=%s"
          % (out, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
