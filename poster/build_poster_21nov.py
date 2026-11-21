#!/usr/bin/env python3
"""Build the 21 November 2026 one-page news poster.

One 1024x1024 front page: 36 stories, 5 regions. PIL only, no network,
no timestamps, seeded randomness only, so repeated runs are byte-identical.
Writes entry.png next to this script's parent directory.
"""

import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 14
CW = W - 2 * MARGIN  # 996

CREAM = (247, 241, 227)
PAPER = (252, 248, 238)
INK = (24, 24, 30)
NAVY = (13, 32, 54)
NAVY2 = (18, 46, 74)
RED = (178, 34, 34)
DARKRED = (139, 22, 22)
GOLD = (201, 162, 39)
TEAL = (14, 92, 96)
ORANGE = (214, 110, 30)
GREY = (90, 88, 80)
LIGHT = (233, 226, 208)
SAND = (222, 196, 150)

FONT_DIR = Path("/usr/share/fonts/truetype/liberation")

SERIF = FONT_DIR / "LiberationSerif-Regular.ttf"
SERIF_B = FONT_DIR / "LiberationSerif-Bold.ttf"
SERIF_I = FONT_DIR / "LiberationSerif-Italic.ttf"
SANS = FONT_DIR / "LiberationSans-Regular.ttf"
SANS_B = FONT_DIR / "LiberationSans-Bold.ttf"
SANS_I = FONT_DIR / "LiberationSans-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(str(path), size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.22)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def text_h(draw, text, fnt, max_w, leading=None):
    if leading is None:
        leading = int(fnt.size * 1.22)
    return len(wrap(draw, text, fnt, max_w)) * leading


def centre(draw, y, text, fnt, fill=INK, cx=W // 2):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return y + int(fnt.size * 1.2)


# ---------------------------------------------------------------- data

STATS = [
    ("400+", "drones fired at Ukraine overnight"),
    ("110+", "missiles in the same barrage"),
    ("-3.7%", "S&P 500 falls into correction"),
    ("6.9", "magnitude quake shakes Peru's Andes"),
    ("25", "European countries hit by Gen Z protests"),
    ("$7.25bn", "Bayer Roundup settlement approved"),
]

REGIONS = [
    ("EUROPE 10", NAVY, (255, 255, 255)),
    ("AMERICAS 11", RED, (255, 255, 255)),
    ("ASIA-PACIFIC 5", TEAL, (255, 255, 255)),
    ("MIDEAST 7", (122, 90, 20), (255, 255, 255)),
    ("WORLD 3", (70, 70, 78), (255, 255, 255)),
]

LEADS = [
    {
        "kicker": "01 · KYIV & POLAND · WAR",
        "head": "Missiles land in Poland as Kyiv is hit again",
        "body": ("Overnight barrage of 400+ drones and 110+ missiles struck "
                 "Kyiv's bridges, power and rail; two Russian missiles and a "
                 "suspected drone came down in Poland. PM Tusk calls it a "
                 "deliberate provocation. (Reuters, AP)"),
        "band": "400+ DRONES · 110+ MISSILES",
        "art": "kyiv",
    },
    {
        "kicker": "02 · NEW YORK & TOKYO · MARKETS",
        "head": "AI sell-off sinks markets into correction",
        "body": ("S&P 500 falls 3.7% into correction as AI and chip stocks "
                 "rout Wall Street; Nasdaq drops 5.3%, Nikkei 5.1% to "
                 "56,436.65, Hang Seng 1.9%. (Reuters, AP)"),
        "band": None,
        "art": "markets",
    },
    {
        "kicker": "03 · ANTALYA, TÜRKIYE · CLIMATE",
        "head": "COP31 runs overtime with no fossil-fuel deal",
        "body": ("UN climate talks pass their deadline with ~200 nations "
                 "deadlocked over fossil fuels; no agreement yet as "
                 "negotiators work into the weekend. (UN News, Reuters)"),
        "band": "NO DEAL OVERTIME",
        "art": "cop",
    },
]

FEATURES = [
    {"kicker": "04 · JUNÍN, PERU · QUAKE",
     "head": "6.9 quake shakes Peru's Andes",
     "body": "Strong tremor felt in Lima; no immediate reports of major damage. (Reuters)",
     "art": "quake", "badge": "6.9"},
    {"kicker": "05 · WASHINGTON · CYBER",
     "head": "FBI database reportedly hacked",
     "body": "Criminal database and USDA systems hit as US outages continue. (Reuters)",
     "art": "hack", "badge": "HACKED"},
    {"kicker": "06 · RIYADH · MISSILES",
     "head": "Houthis fire on Riyadh; three intercepted",
     "body": "Coalition says three missiles were stopped over the capital. (Reuters)",
     "art": "riyadh", "badge": "3 DOWN"},
    {"kicker": "07 · BERLIN · PROTESTS",
     "head": "Gen Z protests spread to 25 countries",
     "body": "Youth-led protests spread across 25 European countries. (AP)",
     "art": "protest", "badge": "25"},
    {"kicker": "08 · LONDON · HEALTH",
     "head": "Cancer pill undetectable in 1 in 12",
     "body": "Daraxonrasib trial: tumours undetectable on scans in one in 12 patients. (Reuters)",
     "art": "pill", "badge": "1 IN 12"},
    {"kicker": "09 · STRAIT OF HORMUZ · DRONE",
     "head": "Iran says it downed a US MQ-9",
     "body": "Tehran says the drone is the 58th American MQ-9 it has brought down. (Reuters)",
     "art": "drone", "badge": "58TH"},
    {"kicker": "10 · INDONESIA · FIRES",
     "head": "Massive forest fires hit Indonesia",
     "body": "Forest fires burn across Indonesia; crews battle the blazes. (AP)",
     "art": "fires", "badge": "FIRES"},
    {"kicker": "11 · UNITED STATES · COURTS",
     "head": "Judge approves $7.25bn Bayer deal",
     "body": "Roundup settlement validated, ending thousands of complaints. (Reuters)",
     "art": "scales", "badge": "$7.25BN"},
    {"kicker": "12 · BASRA, IRAQ · FIRE",
     "head": "Power-plant fire kills at least four",
     "body": "Blaze at the Hartha plant injures 35 in the preliminary toll. (Reuters)",
     "art": "plant", "badge": "4 DEAD"},
    {"kicker": "13 · LOS ANGELES · FIRE",
     "head": "Man convicted over Palisades fire",
     "body": "Jury convicts him of starting the deadly fire. (AP)",
     "art": "flame", "badge": "GUILTY"},
]

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
    (31, "KRYVYI RIH", "Russian strike kills two and injures 42, four of them children."),
    (32, "DAMASCUS", "Syria arrests a former general accused of orchestrating a 2014 massacre."),
    (33, "NEW YORK", "UN cuts its food-aid target despite the looming starvation threat. (UN News)"),
    (34, "BEIJING", "China calls the ICJ Rohingya ruling biased as Myanmar protests it."),
    (35, "BAGHDAD", "Iraq arrests its oil-transport chief on oil-smuggling charges."),
    (36, "KYIV", "Ukrainian drones hit a Russian fertiliser plant that also makes explosives."),
]

DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as 21 Nov news: "
              "Trump–Xi–Putin Shenzhen summit · Anthropic Nasdaq debut ($2tn) · "
              "ICJ Rohingya genocide verdict · GTA VI launch · "
              "Senate Iran war-powers vote 51–48.")

FOOTER = ("Every story here happened, or was first reported, on Saturday 21 November 2026 "
          "in at least one time zone. Sources: Reuters, AP, AFP, BBC, UN News, "
          "Al Jazeera. Original vector drawings.")

# lon/lat pins for the 13 drawn stories (lon, lat)
PINS = [
    (30.5, 50.4),    # 1 Kyiv
    (-74.0, 40.7),   # 2 New York
    (32.0, 36.9),    # 3 Antalya
    (-75.2, -10.0),  # 4 Junin
    (-77.0, 38.9),   # 5 Washington
    (46.7, 24.7),    # 6 Riyadh
    (12.0, 53.0),    # 7 Berlin
    (-0.1, 51.5),    # 8 London
    (56.5, 26.5),    # 9 Hormuz
    (113.0, -2.0),   # 10 Indonesia
    (-95.0, 38.0),   # 11 United States
    (47.8, 30.5),    # 12 Basra
    (-118.2, 34.0),  # 13 Los Angeles
]

# ---------------------------------------------------------------- art

def stars(d, box, rng, n=26):
    x0, y0, x1, y1 = box
    for _ in range(n):
        x = rng.randint(x0 + 2, x1 - 2)
        y = rng.randint(y0 + 2, y1 - 2)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))


def art_kyiv(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(10, 22, 44))
    stars(d, box, rng, 30)
    # skyline blocks
    base = y1 - 8
    bx = x0 + 6
    while bx < x1 - 14:
        bw = rng.randint(16, 30)
        bh = rng.randint(22, 52)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(24, 34, 56))
        for wy in range(base - bh + 5, base - 6, 9):
            for wx in range(bx + 4, bx + bw - 4, 8):
                if rng.random() < 0.5:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 120))
        bx += bw + 4
    # missile trails: orange arcs with dots
    for i in range(3):
        sx = x0 + 40 + i * 90
        sy = y0 + 14 + i * 10
        ex = sx + 70
        ey = sy + 42
        pts = []
        for t in range(0, 11):
            f = t / 10.0
            pts.append((sx + (ex - sx) * f, sy + (ey - sy) * f * f))
        d.line(pts, fill=(255, 150, 60), width=2)
        d.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 120, 40))
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 220, 140))
    # ground fires
    for fx in (x0 + 60, x0 + 200, x0 + 280):
        d.polygon([(fx - 9, base), (fx, base - 16), (fx + 9, base)],
                  fill=(255, 140, 40))
        d.polygon([(fx - 5, base), (fx, base - 9), (fx + 5, base)],
                  fill=(255, 220, 90))


def art_markets(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=NAVY)
    f_lab = font(SANS_B, 9)
    d.text((x0 + 10, y0 + 5), "US & ASIA · FRIDAY CLOSES", font=f_lab,
           fill=(170, 185, 205))
    # small falling red line chart, top-right strip
    pts = []
    n = 7
    for i in range(n):
        px = x0 + (x1 - x0) * 0.62 + (x1 - x0) * 0.34 * i / (n - 1)
        py = y0 + 6 + i * 2 + rng.randint(-1, 1)
        pts.append((px, py))
    d.line(pts, fill=(255, 70, 60), width=2)
    rows = [("NIKKEI", "-5.1%"), ("NASDAQ", "-5.3%"),
            ("S&P 500", "-3.7%"), ("HANG SENG", "-1.9%")]
    f_row = font(SANS_B, 12)
    f_val = font(SANS_B, 13)
    ry = y0 + 24
    for name, val in rows:
        d.text((x0 + 10, ry), name, font=f_row, fill=(220, 225, 235))
        vw = d.textlength(val, font=f_val)
        d.text((x1 - 10 - vw, ry), val, font=f_val, fill=(255, 90, 80))
        d.line([x0 + 8, ry + 15, x1 - 8, ry + 15], fill=(60, 80, 110), width=1)
        ry += 17


def art_cop(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=TEAL)
    cx, cy, r = x0 + 52, y0 + 52, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(38, 130, 140))
    d.ellipse([cx - r + 10, cy - r + 8, cx - 2, cy - 4], fill=(90, 170, 120))
    d.ellipse([cx + 2, cy + 2, cx + r - 8, cy + r - 10], fill=(120, 180, 110))
    d.ellipse([cx - r + 14, cy - 6, cx + r - 16, cy + r - 6], fill=(38, 130, 140))
    # thermometer, left of the red NO DEAL box
    tx = x0 + 148
    d.rounded_rectangle([tx, y0 + 14, tx + 16, y1 - 26], radius=8,
                        fill=(240, 240, 235), outline=(180, 40, 40), width=2)
    d.ellipse([tx - 5, y1 - 34, tx + 21, y1 - 8], fill=(200, 40, 40))
    d.rectangle([tx + 4, y0 + 34, tx + 12, y1 - 20], fill=(200, 40, 40))
    d.text((x0 + 8, y0 + 6), "COP31", font=font(SANS_B, 15),
           fill=(255, 255, 255))


def art_quake(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 222, 196))
    d.polygon([(x0 + 8, y1 - 6), (x0 + 58, y0 + 12), (x0 + 108, y1 - 6)],
              fill=(120, 84, 50))
    d.polygon([(x0 + 92, y1 - 6), (x0 + 140, y0 + 4), (x0 + 182, y1 - 6)],
              fill=(90, 90, 100))
    d.polygon([(x0 + 48, y0 + 20), (x0 + 58, y0 + 12), (x0 + 68, y0 + 20)],
              fill=(255, 255, 255))
    d.polygon([(x0 + 132, y0 + 12), (x0 + 140, y0 + 4), (x0 + 148, y0 + 12)],
              fill=(255, 255, 255))
    # crack lines
    d.line([(x0 + 60, y1 - 6), (x0 + 74, y1 - 22), (x0 + 66, y1 - 34)],
           fill=(60, 40, 25), width=2)
    d.line([(x0 + 150, y1 - 6), (x0 + 142, y1 - 20), (x0 + 152, y1 - 30)],
           fill=(60, 40, 25), width=2)


def art_hack(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 30, 58))
    # padlock, left of centre so the badge stays clear
    lx, ly = x0 + 46, y0 + 26
    d.arc([lx - 11, ly - 10, lx + 11, ly + 10], 180, 360,
          fill=(255, 210, 90), width=4)
    d.rounded_rectangle([lx - 16, ly + 8, lx + 16, ly + 26], radius=4,
                        fill=(210, 60, 50))
    d.ellipse([lx - 3, ly + 13, lx + 3, ly + 19], fill=(255, 255, 255))
    d.rectangle([lx - 1, ly + 18, lx + 1, ly + 24], fill=(255, 255, 255))
    # binary rain, top corners only
    f_bin = font(SANS, 9)
    for bx, by in ((x0 + 6, y0 + 4), (x0 + 6, y0 + 16),
                   (x1 - 44, y0 + 26), (x1 - 44, y0 + 38),
                   (x0 + 96, y1 - 14), (x0 + 130, y1 - 14)):
        d.text((bx, by), rng.choice(["1010", "0110", "1101", "0011"]),
               font=f_bin, fill=(110, 160, 220))


def art_riyadh(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 44, 78))
    stars(d, box, rng, 12)
    base = y1 - 6
    bx = x0 + 8
    while bx < x1 - 10:
        bw = rng.randint(14, 26)
        bh = rng.randint(16, 38)
        d.rectangle([bx, base - bh, bx + bw, base], fill=(30, 60, 100))
        for wy in range(base - bh + 4, base - 5, 8):
            for wx in range(bx + 3, bx + bw - 3, 7):
                if rng.random() < 0.4:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 214, 120))
        bx += bw + 3
    # intercept bursts, kept left of the badge zone
    for ix, iy in ((x0 + 32, y0 + 14), (x0 + 70, y0 + 20), (x0 + 106, y0 + 14)):
        for dx, dy in ((-9, -4), (9, -4), (-9, 4), (9, 4), (0, -8), (0, 8)):
            d.line([ix, iy, ix + dx, iy + dy], fill=(255, 200, 90), width=2)
        d.ellipse([ix - 3, iy - 3, ix + 3, iy + 3], fill=(255, 230, 150))


def art_protest(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 232, 214))
    base = y1 - 6
    for i in range(5):
        px = x0 + 20 + i * 30
        # person: head + body, all inside the 48px art box
        d.ellipse([px - 4, base - 20, px + 4, base - 12], fill=(40, 40, 44))
        d.polygon([(px - 5, base - 11), (px + 5, base - 11),
                   (px + 4, base), (px - 4, base)], fill=(60, 60, 70))
        d.line([px + 5, base - 18, px + 12, base - 30], fill=(90, 70, 40), width=2)
        d.rectangle([px + 6, base - 38, px + 22, base - 30],
                    fill=(200, 60, 50) if i % 2 == 0 else (30, 90, 140))
    d.line([x0 + 6, base, x1 - 6, base], fill=(120, 110, 95), width=2)


def art_pill(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(244, 238, 226))
    cx, cy = x0 + 76, y0 + 26
    # capsule tilted, kept left of the badge zone
    d.rounded_rectangle([cx - 38, cy - 11, cx + 38, cy + 11], radius=11,
                        fill=(214, 60, 70))
    d.rounded_rectangle([cx - 38, cy - 11, cx, cy + 11], radius=11,
                        fill=(255, 255, 255))
    d.ellipse([cx - 38, cy - 11, cx - 16, cy + 11], fill=(255, 255, 255))
    d.line([cx - 52, cy, cx + 52, cy], fill=(180, 40, 50), width=1)
    # small pills
    for px, py, col in ((x0 + 22, y1 - 18, (30, 120, 130)),
                        (x0 + 44, y1 - 14, (214, 120, 40)),
                        (x1 - 30, y1 - 18, (90, 90, 160))):
        d.ellipse([px - 8, py - 5, px + 8, py + 5], fill=col)


def art_drone(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 52, 84))
    for _ in range(10):
        x = rng.randint(x0 + 4, x1 - 4)
        y = rng.randint(y0 + 4, y1 - 4)
        d.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(200, 220, 255))
    # jet silhouette, smaller and clear of the badge
    cx, cy = x0 + 88, y0 + 30
    d.polygon([(cx - 36, cy), (cx + 20, cy - 6), (cx + 36, cy),
               (cx + 20, cy + 6)], fill=(30, 34, 40))
    d.polygon([(cx - 8, cy - 5), (cx + 4, cy - 20), (cx + 10, cy - 5)],
              fill=(30, 34, 40))
    d.polygon([(cx - 8, cy + 5), (cx + 4, cy + 20), (cx + 10, cy + 5)],
              fill=(30, 34, 40))
    d.ellipse([cx + 22, cy - 2, cx + 30, cy + 2], fill=(140, 200, 230))
    # dashed flight path curving up to the jet
    for i in range(5):
        px = x0 + 12 + i * 14
        py = y0 + 10 + i * 3
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 200, 100))
    # sea line
    d.line([x0, y1 - 10, x1, y1 - 10], fill=(90, 160, 200), width=2)
    d.line([x0 + 20, y1 - 5, x0 + 60, y1 - 5], fill=(60, 130, 170), width=1)


def art_fires(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(28, 52, 30))
    base = y1 - 6
    for i in range(5):
        tx = x0 + 16 + i * 34
        th = rng.randint(20, 34)
        d.polygon([(tx - 12, base), (tx, base - th), (tx + 12, base)],
                  fill=(20, 80, 40))
        d.rectangle([tx - 2, base - 8, tx + 2, base], fill=(90, 60, 30))
    # flames
    for fx in (x0 + 40, x0 + 110, x0 + 160):
        d.polygon([(fx - 9, base), (fx, base - 20), (fx + 9, base)],
                  fill=(255, 140, 30))
        d.polygon([(fx - 5, base), (fx, base - 11), (fx + 5, base)],
                  fill=(255, 220, 90))
    d.ellipse([x0 + 150, y0 + 6, x0 + 168, y0 + 20], fill=(255, 220, 150))


def art_scales(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 234, 220))
    cx = x0 + 96
    top = y0 + 8
    d.line([cx, top, cx, y1 - 12], fill=(60, 50, 35), width=3)
    d.line([cx - 52, top + 8, cx + 52, top + 8], fill=(60, 50, 35), width=3)
    for sx in (cx - 52, cx + 52):
        d.line([sx, top + 8, sx, top + 30], fill=(60, 50, 35), width=2)
        d.arc([sx - 20, top + 26, sx + 20, top + 46], 0, 180,
              fill=(150, 120, 50), width=3)
        d.line([sx - 20, top + 36, sx + 20, top + 36], fill=(150, 120, 50), width=2)
    d.ellipse([cx - 5, top - 4, cx + 5, top + 6], fill=(150, 120, 50))
    d.rectangle([cx - 24, y1 - 12, cx + 24, y1 - 6], fill=(60, 50, 35))


def art_plant(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(36, 36, 44))
    base = y1 - 6
    # cooling tower
    d.polygon([(x0 + 30, base), (x0 + 38, y0 + 16), (x0 + 62, y0 + 16),
               (x0 + 70, base)], fill=(120, 120, 130))
    d.ellipse([x0 + 38, y0 + 12, x0 + 62, y0 + 20], fill=(90, 90, 100))
    # chimneys
    for sx in (x0 + 96, x0 + 118):
        d.rectangle([sx, y0 + 10, sx + 12, base], fill=(160, 90, 50))
        d.rectangle([sx - 2, y0 + 6, sx + 14, y0 + 12], fill=(120, 60, 35))
    # smoke above the left chimney only, clear of the badge
    for i in range(3):
        d.ellipse([x0 + 94 + i * 7, y0 + 2, x0 + 106 + i * 7, y0 + 11],
                  fill=(200, 200, 205))
    d.polygon([(x0 + 150, base), (x0 + 160, base - 22), (x0 + 170, base)],
              fill=(255, 140, 30))
    d.line([x0 + 8, base, x1 - 8, base], fill=(200, 200, 200), width=2)


def art_flame(d, box, rng):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(24, 22, 28))
    cx = x0 + 96
    base = y1 - 8
    d.polygon([(cx - 34, base), (cx - 8, y0 + 14), (cx + 10, y0 + 30),
               (cx + 34, base)], fill=(230, 90, 30))
    d.polygon([(cx - 18, base), (cx, y0 + 26), (cx + 18, base)],
              fill=(255, 190, 60))
    d.polygon([(cx - 8, base), (cx, y0 + 38), (cx + 8, base)],
              fill=(255, 240, 160))
    # embers
    for _ in range(8):
        ex = rng.randint(x0 + 20, x1 - 20)
        ey = rng.randint(y0 + 8, y0 + 26)
        d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(255, 160, 60))


ART = {
    "kyiv": art_kyiv, "markets": art_markets, "cop": art_cop,
    "quake": art_quake, "hack": art_hack, "riyadh": art_riyadh,
    "protest": art_protest, "pill": art_pill, "drone": art_drone,
    "fires": art_fires, "scales": art_scales, "plant": art_plant,
    "flame": art_flame,
}

# Simplified continent outlines in (lon, lat) pairs, drawn by hand.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 71), (-100, 69), (-85, 66), (-80, 62),
     (-76, 58), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-81, 26), (-84, 30), (-90, 21), (-97, 26), (-105, 22), (-110, 24),
     (-117, 33), (-125, 40), (-124, 48), (-135, 58), (-155, 58),
     (-165, 60), (-168, 66)],
    # Central America sliver
    [(-90, 21), (-86, 16), (-83, 9), (-79, 9), (-83, 15), (-90, 14),
     (-92, 16), (-97, 16), (-90, 21)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -33), (-72, -44), (-74, -52), (-66, -55),
     (-65, -45), (-62, -39), (-57, -35), (-48, -28), (-41, -23),
     (-35, -9), (-35, -6), (-44, -3), (-50, 0), (-54, 2), (-60, 8),
     (-62, 10), (-70, 11), (-77, 8), (-79, 9)],
    # Africa
    [(-6, 35), (10, 37), (20, 33), (30, 31), (32, 31), (35, 28),
     (38, 22), (40, 15), (43, 11), (51, 11), (46, 1), (41, -4),
     (40, -11), (36, -18), (33, -26), (28, -33), (19, -35), (15, -27),
     (12, -18), (13, -12), (9, -1), (9, 4), (0, 6), (-8, 4),
     (-13, 8), (-17, 15), (-17, 21), (-16, 28), (-10, 31), (-6, 35)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50),
     (2, 51), (4, 53), (8, 57), (10, 59), (6, 62), (12, 65),
     (18, 69), (25, 71), (30, 70), (32, 68), (40, 68), (44, 68),
     (48, 66), (50, 60), (48, 55), (44, 52), (40, 48), (38, 46),
     (30, 46), (28, 44), (23, 40), (20, 40), (16, 38), (12, 44),
     (8, 44), (3, 42), (0, 39), (-2, 37), (-6, 36), (-10, 36)],
    # Asia
    [(-10, 36), (30, 36), (36, 36), (36, 42), (42, 41), (44, 39),
     (48, 39), (50, 37), (54, 37), (57, 26), (61, 25), (66, 25),
     (72, 20), (77, 8), (80, 13), (88, 22), (92, 21), (97, 16),
     (100, 8), (104, 2), (104, 9), (109, 13), (114, 22), (120, 28),
     (122, 32), (120, 35), (127, 40), (130, 42), (135, 44), (140, 46),
     (142, 52), (142, 59), (156, 51), (162, 56), (162, 60), (158, 64),
     (170, 66), (178, 65), (180, 66), (178, 68), (170, 70), (160, 70),
     (150, 71), (140, 72), (130, 72), (120, 73), (110, 74), (100, 76),
     (90, 75), (80, 73), (70, 72), (68, 69), (60, 69), (54, 68),
     (50, 68), (44, 68), (40, 68), (32, 68), (30, 70), (25, 71),
     (18, 69), (12, 65), (6, 62), (10, 59), (8, 57), (4, 53),
     (2, 51), (0, 50), (-4, 48), (-1, 46), (-2, 44), (-9, 43),
     (-10, 36)],
    # Australia
    [(114, -22), (114, -32), (118, -35), (124, -33), (130, -32),
     (136, -35), (140, -38), (146, -39), (150, -37), (153, -27),
     (153, -22), (146, -19), (142, -11), (136, -12), (132, -12),
     (126, -14), (122, -17), (114, -22)],
]

# ---------------------------------------------------------------- layout

def draw_badge(d, box, text, fill=RED):
    x0, y0, x1, y1 = box
    f = font(SANS_B, 10)
    tw = d.textlength(text, font=f)
    bw = int(tw) + 12
    bx = x1 - 4 - bw
    d.rectangle([bx, y0 + 4, bx + bw, y0 + 22], fill=fill)
    d.text((bx + 6, y0 + 6), text, font=f, fill=(255, 255, 255))


def wrap_first(draw, text, fnt, first_w, rest_w):
    """Wrap text where the first line has first_w and the rest rest_w."""
    words = text.split()
    lines = []
    cur = ""
    limit = first_w
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= limit:
            cur = trial
        else:
            lines.append(cur)
            cur = word
            limit = rest_w
    if cur:
        lines.append(cur)
    return lines


def draw_brief(d, x, y, num, place, text, col_w):
    f_b = font(SANS_B, 8)
    f_r = font(SANS, 8)
    prefix = "%d %s — " % (num, place)
    pw = d.textlength(prefix, font=f_b)
    lines = wrap_first(d, text, f_r, col_w - pw, col_w)
    d.text((x, y), prefix, font=f_b, fill=INK)
    d.text((x + pw, y), lines[0], font=f_r, fill=INK)
    for j, line in enumerate(lines[1:], start=1):
        d.text((x, y + 10 * j), line, font=f_r, fill=INK)
    return y + 10 * len(lines) + 1


def build():
    rng = random.Random(20261121)
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)

    # ---- masthead
    f_mast = font(SANS_B, 13)
    d.text((MARGIN, 7), "THE WORLD IN ONE DAY", font=f_mast, fill=RED)
    f_top = font(SANS_B, 11)
    rt = "SATURDAY'S NEWS · ONE PAGE · 36 STORIES · 5 REGIONS"
    d.text((W - MARGIN - d.textlength(rt, font=f_top), 8), rt,
           font=f_top, fill=INK)

    # ---- date + strap
    f_date = font(SERIF_B, 54)
    centre(d, 24, "Saturday 21 November 2026", f_date, INK)
    f_strap = font(SERIF_I, 15)
    centre(d, 90, "Missiles land in Poland · An AI sell-off sinks markets · "
                  "COP31 runs overtime", f_strap, RED)
    d.line([MARGIN, 112, W - MARGIN, 112], fill=INK, width=2)

    # ---- stat strip
    cell_w = CW // 6
    f_num = font(SANS_B, 26)
    f_cap = font(SANS, 10)
    for i, (num, cap) in enumerate(STATS):
        x = MARGIN + i * cell_w
        if i:
            d.line([x, 120, x, 168], fill=(200, 192, 172), width=1)
        d.text((x + 6, 118), num, font=f_num, fill=RED)
        draw_wrapped(d, x + 6, 150, cap, f_cap, cell_w - 12, fill=GREY,
                     leading=12)

    # ---- region bar
    total = sum(int(r[0].rsplit(" ", 1)[1]) for r in REGIONS)
    rx = MARGIN
    f_reg = font(SANS_B, 11)
    for label, colour, fg in REGIONS:
        count = int(label.rsplit(" ", 1)[1])
        rw = int(CW * count / total)
        d.rectangle([rx, 176, rx + rw - 1, 196], fill=colour)
        tw = d.textlength(label, font=f_reg)
        d.text((rx + (rw - tw) / 2, 179), label, font=f_reg, fill=fg)
        rx += rw

    # ---- lead cards
    lead_w = 324
    lead_gap = 12
    lead_y = 202
    lead_h = 200
    f_kick = font(SANS_B, 10)
    f_head = font(SERIF_B, 16)
    f_body = font(SANS, 10)
    for i, lead in enumerate(LEADS):
        x = MARGIN + i * (lead_w + lead_gap)
        d.rectangle([x, lead_y, x + lead_w, lead_y + lead_h],
                    fill=PAPER, outline=(180, 172, 150), width=1)
        art_box = (x + 1, lead_y + 1, x + lead_w - 1, lead_y + 97)
        ART[lead["art"]](d, art_box, rng)
        if lead["art"] == "kyiv":
            f_band = font(SANS_B, 11)
            d.rectangle([x + 1, lead_y + 78, x + lead_w - 1, lead_y + 97],
                        fill=DARKRED)
            d.text((x + 10, lead_y + 82), lead["band"], font=f_band,
                   fill=(255, 255, 255))
        if lead["art"] == "cop":
            f_band = font(SANS_B, 10)
            bw = d.textlength(lead["band"], font=f_band) + 14
            d.rectangle([x + lead_w - 6 - bw, lead_y + 6,
                         x + lead_w - 6, lead_y + 42], fill=RED)
            d.text((x + lead_w - 6 - bw + 7, lead_y + 10),
                   "NO DEAL", font=f_band, fill=(255, 255, 255))
            d.text((x + lead_w - 6 - bw + 7, lead_y + 24),
                   "OVERTIME", font=f_band, fill=(255, 255, 255))
        ty = lead_y + 104
        d.text((x + 8, ty), lead["kicker"], font=f_kick, fill=RED)
        ty += 14
        ty = draw_wrapped(d, x + 8, ty, lead["head"], f_head,
                          lead_w - 16, fill=INK, leading=19)
        draw_wrapped(d, x + 8, ty + 3, lead["body"], f_body,
                     lead_w - 16, fill=INK, leading=12)

    # ---- feature cards, 2 rows x 5
    feat_w = 192
    feat_gap = 9
    feat_h = 108
    feat_rows = [408, 524]
    f_fkick = font(SANS_B, 8)
    f_fhead = font(SERIF_B, 12)
    f_fbody = font(SANS, 8)
    for row_i, fy in enumerate(feat_rows):
        for col_i in range(5):
            feat = FEATURES[row_i * 5 + col_i]
            x = MARGIN + col_i * (feat_w + feat_gap)
            d.rectangle([x, fy, x + feat_w, fy + feat_h],
                        fill=PAPER, outline=(180, 172, 150), width=1)
            art_box = (x + 1, fy + 1, x + feat_w - 1, fy + 49)
            ART[feat["art"]](d, art_box, rng)
            draw_badge(d, art_box, feat["badge"],
                       fill=RED if col_i % 3 else NAVY)
            ty = fy + 53
            d.text((x + 6, ty), feat["kicker"], font=f_fkick, fill=RED)
            ty += 11
            ty = draw_wrapped(d, x + 6, ty, feat["head"], f_fhead,
                              feat_w - 12, fill=INK, leading=14)
            draw_wrapped(d, x + 6, ty + 1, feat["body"], f_fbody,
                         feat_w - 12, fill=INK, leading=10)

    # ---- bottom headers
    f_sec = font(SANS_B, 11)
    d.text((MARGIN, 638), "WHERE IT HAPPENED", font=f_sec, fill=RED)
    d.text((496, 638), "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES",
           font=f_sec, fill=RED)
    f_small = font(SANS, 9)
    rt2 = "ALL STORIES: SAT 21 NOV 2026"
    d.text((W - MARGIN - d.textlength(rt2, font=f_small), 639), rt2,
           font=f_small, fill=GREY)

    # ---- map
    mx, my, mw, mh = MARGIN, 658, 470, 212
    d.rectangle([mx, my, mx + mw, my + mh], fill=NAVY)
    d.text((mx + 8, my + 4), "Pins 1–13 mark the drawn stories",
           font=f_small, fill=(200, 205, 215))

    def project(lon, lat):
        px = mx + 8 + (lon + 180.0) / 360.0 * (mw - 16)
        py = my + 22 + (75.0 - lat) / 132.0 * (mh - 30)
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([project(lon, lat) for lon, lat in poly], fill=SAND)
    # graticule dots
    for lon in range(-150, 181, 30):
        for lat in range(-45, 76, 30):
            px, py = project(lon, lat)
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(60, 80, 110))
    # pins
    f_pin = font(SANS_B, 9)
    for i, (lon, lat) in enumerate(PINS, start=1):
        px, py = project(lon, lat)
        ring = GOLD if i <= 3 else (255, 255, 255)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=ring, width=2)
        tw = d.textlength(str(i), font=f_pin)
        d.text((px - tw / 2, py - 6), str(i), font=f_pin,
               fill=(255, 255, 255))
    # 36 stories badge
    f_badge = font(SANS_B, 11)
    btxt = "36 STORIES"
    bw = d.textlength(btxt, font=f_badge) + 16
    d.rounded_rectangle([mx + mw - bw - 8, my + 6, mx + mw - 8, my + 28],
                        radius=11, fill=GOLD)
    d.text((mx + mw - bw, my + 9), btxt, font=f_badge, fill=NAVY)
    # legend
    f_leg = font(SANS, 9)
    d.text((mx, 876), "1–3 Lead (gold ring) · 4–13 Features",
           font=f_leg, fill=INK)
    d.text((mx, 888), "Positions approximate.", font=f_leg, fill=GREY)

    # ---- briefs, two columns
    col_w = 252
    cols = [(496, BRIEFS[:11]), (756, BRIEFS[11:])]
    for cx, items in cols:
        yy = 658
        for num, place, text in items:
            yy = draw_brief(d, cx, yy, num, place, text, col_w)
            yy += 1

    # ---- date check box
    d.rectangle([MARGIN, 948, W - MARGIN, 988], outline=RED, width=2)
    f_dc = font(SANS_B, 10)
    d.text((MARGIN + 8, 952), "DATE CHECK", font=f_dc, fill=RED)
    draw_wrapped(d, MARGIN + 8, 966, DATE_CHECK, font(SANS, 9),
                 CW - 16, fill=INK, leading=11)

    # ---- footer
    centre(d, 994, FOOTER, font(SANS_I, 8), GREY)

    return img


def main():
    out = Path(__file__).resolve().parent.parent / "entry.png"
    img = build()
    img.save(out, format="PNG")
    data = out.read_bytes()
    print("wrote %s %d bytes sha256=%s" % (out, len(data),
          hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
