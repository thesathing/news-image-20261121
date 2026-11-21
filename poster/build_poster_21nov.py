#!/usr/bin/env python3
"""21 Nov poster builder for make.fun news-image-20261121 (Concept A).
Adapted from the v8 builder (same layout, fonts, palette). PIL only,
deterministic. Output: ../entry.png (1024x1024, <= 1 MiB).
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 14  # side margin
CW = W - 2 * M  # 996 content width
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "entry.png")

# ---- palette (cream / navy / red, like the top entries) ----
CREAM = (247, 241, 227)
PAPER = (250, 246, 236)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
NAVY2 = (27, 44, 74)
RED = (176, 30, 36)
RED_DK = (140, 22, 28)
GOLD = (201, 162, 39)
TAN = (216, 201, 163)
TAN_DK = (198, 178, 132)
TEAL = (31, 120, 110)
AMBER = (198, 124, 24)
BROWN = (122, 84, 52)
PURPLE = (104, 78, 140)
SLATE = (90, 100, 112)
WHITE = (255, 255, 255)
SKY = (126, 180, 210)
BLUE = (52, 110, 180)
GREEN = (46, 130, 80)
GREY = (120, 116, 108)
RULE = (26, 26, 26)

FONT_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)
SANS_I = lambda s: font("LiberationSans-Italic.ttf", s)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, color, max_w, leading, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw.text((x, y + i * leading), ln, font=fnt, fill=color)
    return len(lines)


def draw_center(draw, cx, y, text, fnt, color):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=color)


def hline(draw, x0, x1, y, color, width=1):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def vline(draw, x, y0, y1, color, width=1):
    draw.line([(x, y0), (x, y1)], fill=color, width=width)


# ---- simplified coastline point lists (lon, lat) ----
NORTH_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-142, 60), (-135, 57),
                 (-130, 54), (-125, 48), (-124, 40), (-120, 34), (-114, 29),
                 (-109, 24), (-104, 20), (-97, 16), (-91, 14), (-86, 12),
                 (-82, 9), (-79, 8), (-77, 7), (-80, 9), (-83, 10), (-86, 13),
                 (-90, 14), (-93, 15), (-96, 16), (-97, 20), (-97, 25),
                 (-93, 29), (-89, 30), (-84, 30), (-81, 25), (-80, 32),
                 (-76, 35), (-74, 39), (-70, 42), (-67, 45), (-61, 46),
                 (-56, 48), (-60, 52), (-64, 56), (-60, 55), (-65, 58),
                 (-70, 60), (-76, 62), (-82, 64), (-88, 66), (-94, 68),
                 (-100, 69), (-110, 68), (-120, 69), (-130, 70), (-140, 70),
                 (-152, 71), (-162, 70), (-168, 66)]
GREENLAND = [(-44, 60), (-40, 64), (-32, 68), (-24, 70), (-20, 74), (-24, 78),
             (-34, 80), (-48, 79), (-56, 76), (-54, 71), (-52, 65), (-48, 61)]
SOUTH_AMERICA = [(-80, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -11),
                 (-73, -16), (-70, -21), (-70, -28), (-72, -36), (-73, -43),
                 (-74, -49), (-70, -54), (-66, -55), (-67, -51), (-65, -44),
                 (-62, -39), (-58, -34), (-53, -32), (-48, -27), (-41, -23),
                 (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
                 (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11),
                 (-73, 12), (-77, 10), (-80, 9)]
AFRICA = [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
          (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0),
          (12, -4), (13, -8), (13, -12), (12, -17), (14, -22), (16, -28),
          (18, -33), (20, -35), (26, -34), (28, -32), (32, -28), (35, -24),
          (36, -20), (40, -16), (40, -11), (42, -5), (44, -1), (48, 2),
          (51, 5), (51, 11), (46, 11), (43, 12), (40, 15), (38, 18),
          (37, 22), (35, 28), (33, 31), (30, 32), (25, 32), (20, 32),
          (15, 32), (10, 34), (5, 37), (0, 36), (-6, 35)]
EURASIA = [(-10, 36), (-9, 43), (-2, 44), (-2, 48), (0, 50), (3, 52), (7, 54),
           (8, 57), (11, 58), (15, 56), (19, 55), (23, 58), (27, 60),
           (30, 63), (30, 67), (35, 69), (42, 68), (48, 69), (55, 68),
           (62, 69), (69, 71), (76, 72), (83, 73), (90, 75), (97, 76),
           (104, 77), (111, 74), (118, 73), (125, 72), (132, 71), (139, 72),
           (146, 72), (153, 70), (159, 69), (162, 64), (159, 59), (156, 53),
           (152, 47), (147, 43), (142, 44), (140, 39), (136, 35), (132, 33),
           (129, 34), (126, 37), (124, 39), (122, 37), (120, 34), (117, 30),
           (114, 24), (110, 20), (107, 17), (104, 13), (101, 9), (99, 6),
           (102, 2), (104, 1), (101, 5), (98, 9), (95, 13), (92, 17),
           (90, 21), (87, 21), (84, 18), (81, 14), (78, 9), (76, 9),
           (74, 14), (72, 19), (69, 22), (66, 24), (62, 25), (58, 25),
           (54, 26), (50, 28), (46, 29), (42, 29), (38, 27), (36, 23),
           (35, 19), (36, 15), (39, 12), (42, 12), (45, 14), (48, 16),
           (52, 18), (56, 20), (59, 23), (57, 25), (54, 27), (51, 28),
           (48, 29), (45, 30), (42, 30), (39, 30), (36, 31), (33, 32),
           (30, 32), (27, 32), (24, 33), (21, 34), (18, 35), (15, 36),
           (12, 37), (9, 37), (6, 37), (3, 36), (0, 36), (-3, 36),
           (-6, 35), (-10, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
             (135, -12), (132, -12), (130, -13), (126, -14), (122, -17),
             (118, -20), (114, -21), (113, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
      (-2, 50), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
         (141, 40), (142, 42), (143, 44), (141, 45), (140, 42), (139, 39),
         (137, 37), (135, 35), (133, 34), (131, 32), (130, 31)]
NEW_ZEALAND = [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
               (175, -40), (172, -43), (168, -46), (167, -45)]
MADAGASCAR = [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
              (44, -25), (43, -21), (44, -16)]
SUMATRA = [(95, 5), (98, 2), (101, -2), (104, -4), (106, -6), (103, -5),
           (100, -1), (97, 3), (95, 5)]
BORNEO = [(109, 1), (111, 3), (114, 4), (117, 2), (118, -1), (116, -3),
          (113, -3), (110, 0), (109, 1)]
JAVA = [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
        (106, -7), (105, -6)]
NEW_GUINEA = [(131, -1), (135, -2), (138, -4), (141, -5), (141, -8),
              (138, -8), (134, -7), (131, -4), (131, -1)]
ICELAND = [(-22, 64), (-18, 63), (-14, 64), (-16, 66), (-20, 66), (-22, 64)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              AUSTRALIA, UK, JAPAN, NEW_ZEALAND, MADAGASCAR, SUMATRA,
              BORNEO, JAVA, NEW_GUINEA, ICELAND]

# pins: (number, lon, lat, is_lead) — Mercury (5) is the top-right SPACE badge
# Pins nudged apart where the 336px map crowds them (Europe, US East,
# Middle East); the poster already says "Positions approximate."
PINS = [(1, 30.5, 50.4, True), (2, 139.7, 35.7, True), (3, 33.0, 34.5, True),
        (4, -75.2, -11.0, False), (5, -77.0, 38.9, False), (6, 43.0, 22.5, False),
        (7, 12.0, 54.0, False), (8, -2.5, 51.5, False), (9, 60.5, 27.5, False),
        (10, 106.8, -6.2, False), (11, -95.0, 38.0, False),
        (12, 49.0, 34.0, False), (13, -118.5, 34.0, False)]


# ---- art panels ----
def art_kyiv(draw, x, y, w, h):
    """Lead 1: night missile barrage over Kyiv skyline."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # stars
    rnd = random.Random(7)
    for _ in range(26):
        sx = x + rnd.randint(4, w - 4)
        sy = y + rnd.randint(4, int(h * 0.5))
        r = rnd.choice([1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(200, 205, 220))
    # skyline silhouette
    base = y + h - 26
    bx = x + 6
    rnd2 = random.Random(11)
    while bx < x + w - 10:
        bw = rnd2.randint(14, 30)
        bh = rnd2.randint(14, 52)
        draw.rectangle([bx, base - bh, bx + bw, base + 26], fill=(10, 16, 32))
        # lit windows
        for wy in range(base - bh + 5, base - 2, 9):
            for wx in range(bx + 4, bx + bw - 3, 8):
                if rnd2.random() < 0.4:
                    draw.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 200, 90))
        bx += bw + 3
    draw.rectangle([x, base, x + w, y + h], fill=(12, 18, 36))
    # missile trails (diagonal, glowing)
    for (tx, ty, ln) in [(0.18, 0.30, 46), (0.42, 0.18, 58), (0.66, 0.26, 50),
                         (0.86, 0.14, 44)]:
        px, py = x + int(w * tx), y + int(h * ty)
        draw.line([(px, py), (px + ln, py + int(ln * 0.55))], fill=(255, 120, 60),
                  width=3)
        draw.line([(px, py), (px + ln, py + int(ln * 0.55))], fill=(255, 220, 150),
                  width=1)
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 230, 170))
        draw.ellipse([px + ln - 3, py + int(ln * 0.55) - 3,
                      px + ln + 3, py + int(ln * 0.55) + 3], fill=(255, 90, 40))
    # flames at impact
    for fx, fr in [(0.30, 9), (0.62, 7), (0.84, 8)]:
        cx, cy = x + int(w * fx), base - 2
        draw.polygon([(cx - fr, cy), (cx, cy - fr * 2), (cx + fr, cy)],
                     fill=(255, 150, 40))
        draw.polygon([(cx - fr // 2, cy), (cx, cy - fr), (cx + fr // 2, cy)],
                     fill=(255, 220, 110))
    # labels
    draw.text((x + 8, y + 8), "KYIV", font=SANS_B(30), fill=WHITE)
    draw.text((x + 8, y + 42), "MISSILE BARRAGE", font=SANS_B(15), fill=(255, 220, 150))
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=RED)
    draw.text((x + 8, y + h - 19), "400+ DRONES  ·  110+ MISSILES",
              font=SANS_B(12), fill=WHITE)


def art_akvan(draw, x, y, w, h):
    """Lead 2: cyclone spiral over the Bay of Bengal."""
    draw.rectangle([x, y, x + w, y + h], fill=(24, 90, 110))
    # sea bands
    for i, col in enumerate([(24, 90, 110), (28, 100, 120), (22, 82, 102)]):
        draw.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=col)
    # coastline hint (Odisha, left) — a broader coastal wedge
    draw.polygon([(x, y + h), (x, y + int(h * 0.30)), (x + 52, y + int(h * 0.22)),
                  (x + 88, y + int(h * 0.38)), (x + 78, y + int(h * 0.62)),
                  (x + 60, y + h)], fill=(214, 190, 140))
    draw.text((x + 6, y + int(h * 0.58)), "GOPALPUR", font=SANS_B(10), fill=INK)
    draw.text((x + 6, y + int(h * 0.72)), "ODISHA, INDIA", font=SANS(9), fill=INK)
    # spiral (Archimedean, white) — sized to fit between header and red bar
    cx, cy = x + int(w * 0.64), y + int(h * 0.52)
    for turn in range(3):
        pts = []
        for t in range(0, 361, 6):
            a = math.radians(t + turn * 55)
            r = 6 + (t / 360.0) * 20 + turn * 2
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * 0.92))
        draw.line(pts, fill=(235, 244, 248), width=3)
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 240, 200))
    # Gopalpur landfall dot
    gx, gy = x + 62, y + int(h * 0.40)
    draw.ellipse([gx - 5, gy - 5, gx + 5, gy + 5], fill=RED)
    draw.ellipse([gx - 8, gy - 8, gx + 8, gy + 8], outline=WHITE, width=2)
    draw.line([(gx, gy), (cx - 18, cy + 8)], fill=WHITE, width=1)
    # labels
    draw.rectangle([x, y, x + w, y + 26], fill=NAVY)
    draw.text((x + 8, y + 5), "CYCLONE AKVAN", font=SANS_B(14), fill=WHITE)
    draw.text((x + w - 108, y + 6), "BAY OF BENGAL", font=SANS_B(9), fill=SKY)
    draw.rectangle([x, y + h - 24, x + w, y + h], fill=RED)
    draw.text((x + 8, y + h - 20), "LANDFALL 08:30 IST", font=SANS_B(13), fill=WHITE)
    draw.text((x + w - 132, y + h - 19), "70–80 KM/H AT COAST",
              font=SANS_B(10), fill=(255, 220, 150))


def art_markets(draw, x, y, w, h):
    """Lead 3: dark index table + falling line chart."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    # falling line chart (left)
    chart_x0, chart_y0 = x + 10, y + 34
    chart_w, chart_h = 118, h - 62
    pts = []
    for i in range(9):
        px = chart_x0 + i * chart_w // 8
        py = chart_y0 + [4, 10, 8, 22, 30, 26, 44, 56, chart_h - 6][i]
        pts.append((px, py))
    draw.line(pts, fill=(255, 70, 60), width=3)
    for (px, py) in pts:
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 120, 100))
    # header
    draw.text((x + 8, y + 6), "AI SELL-OFF", font=SANS_B(20), fill=WHITE)
    draw.text((x + 8, y + 28), "US & ASIA · FRIDAY CLOSES", font=SANS_B(10),
              fill=(255, 150, 130))
    # index table (right)
    rows = [("NIKKEI", "−5.1%"), ("NASDAQ", "−5.3%"), ("S&P 500", "−3.7%"),
            ("HANG SENG", "−1.9%")]
    tx = x + 138
    ty = y + 34
    for i, (name, val) in enumerate(rows):
        ry = ty + i * 20
        draw.text((tx, ry), name, font=SANS_B(12), fill=(200, 205, 220))
        vw = draw.textlength(val, font=SANS_B(13))
        draw.text((x + w - 10 - vw, ry), val, font=SANS_B(13), fill=(255, 90, 80))
        if i < 3:
            draw.line([(tx, ry + 16), (x + w - 10, ry + 16)],
                      fill=(60, 70, 95), width=1)


def art_cop31(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(16, 84, 96))
    # globe
    draw.ellipse([x + 10, y + 5, x + 42, y + 37], fill=BLUE)
    draw.ellipse([x + 15, y + 10, x + 26, y + 21], fill=GREEN)
    draw.ellipse([x + 27, y + 22, x + 38, y + 32], fill=GREEN)
    # thermometer
    draw.rectangle([x + 56, y + 8, x + 64, y + 30], fill=WHITE)
    draw.ellipse([x + 52, y + 26, x + 68, y + 38], fill=RED)
    draw.rectangle([x + 58, y + 16, x + 62, y + 30], fill=RED)
    # overtime box
    draw.rectangle([x + w - 78, y + 4, x + w - 8, y + 36], fill=RED)
    draw.text((x + w - 73, y + 7), "NO DEAL", font=SANS_B(11), fill=WHITE)
    draw.text((x + w - 73, y + 21), "OVERTIME", font=SANS_B(11), fill=WHITE)


def art_mercury(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(12, 14, 26))
    rnd = random.Random(3)
    for _ in range(18):
        sx = x + rnd.randint(3, w - 3)
        sy = y + rnd.randint(3, h - 3)
        draw.ellipse([sx, sy, sx + 1, sy + 1], fill=(200, 200, 210))
    draw.ellipse([x + w - 44, y + 4, x + w - 8, y + 36], fill=(180, 178, 170))
    draw.ellipse([x + w - 36, y + 10, x + w - 28, y + 18], fill=(150, 148, 140))
    draw.ellipse([x + w - 24, y + 22, x + w - 16, y + 30], fill=(150, 148, 140))
    draw.text((x + 8, y + 10), "6BN MILES", font=SANS_B(14), fill=WHITE)


def art_flags(draw, x, y, w, h):
    """EU + UK flags, side by side."""
    draw.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # EU flag
    ex, ey, ew, eh = x + 8, y + 4, 78, 30
    draw.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    for k in range(12):
        a = math.radians(k * 30 - 90)
        px = ex + ew / 2 + 12 * math.cos(a)
        py = ey + eh / 2 + 8 * math.sin(a)
        draw.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(255, 204, 0))
    # UK flag (simplified)
    ux, uy, uw, uh = x + w - 86, y + 4, 78, 30
    draw.rectangle([ux, uy, ux + uw, uy + uh], fill=(1, 33, 105))
    draw.line([(ux, uy), (ux + uw, uy + uh)], fill=WHITE, width=5)
    draw.line([(ux + uw, uy), (ux, uy + uh)], fill=WHITE, width=5)
    draw.line([(ux, uy), (ux + uw, uy + uh)], fill=(200, 16, 46), width=2)
    draw.line([(ux + uw, uy), (ux, uy + uh)], fill=(200, 16, 46), width=2)
    draw.rectangle([ux + uw // 2 - 4, uy, ux + uw // 2 + 4, uy + uh], fill=WHITE)
    draw.rectangle([ux, uy + uh // 2 - 4, ux + uw, uy + uh // 2 + 4], fill=WHITE)
    draw.rectangle([ux + uw // 2 - 2, uy, ux + uw // 2 + 2, uy + uh],
                   fill=(200, 16, 46))
    draw.rectangle([ux, uy + uh // 2 - 2, ux + uw, uy + uh // 2 + 2],
                   fill=(200, 16, 46))


def art_cpi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 216))
    # two bars, values written to the right of each bar
    draw.rectangle([x + 12, y + 8, x + 30, y + 20], fill=GREY)
    draw.text((x + 36, y + 8), "2.1%", font=SANS_B(11), fill=INK)
    draw.rectangle([x + 12, y + 24, x + 34, y + 36], fill=RED)
    draw.text((x + 40, y + 24), "2.2%", font=SANS_B(11), fill=RED_DK)
    draw.text((x + 96, y + 8), "CPI CORE", font=SANS_B(11), fill=INK)
    draw.text((x + 96, y + 24), "OCT · Y/Y", font=SANS(9), fill=GREY)


def art_rates(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    draw.text((x + 10, y + 4), "3.50%  5Y", font=SANS_B(13), fill=WHITE)
    draw.line([(x + 10, y + 22), (x + w - 10, y + 22)], fill=(255, 90, 80), width=2)
    draw.text((x + 10, y + 25), "3.00%  1Y", font=SANS_B(13), fill=(255, 150, 130))


def art_cricket(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 110, 70))
    draw.rectangle([x + 16, y + 6, x + 44, y + h - 6], fill=(222, 196, 140),
                   outline=(160, 130, 80), width=1)
    draw.ellipse([x + w - 44, y + 8, x + w - 20, y + 32], fill=RED)
    draw.text((x + 56, y + 8), "118", font=SANS_B(24), fill=WHITE)


def art_bukele(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 60, 120))
    draw.rectangle([x + 12, y + 12, x + 52, y + h - 12], fill=(240, 240, 235))
    draw.rectangle([x + 20, y + 6, x + 44, y + 14], fill=RED)
    draw.line([(x + 18, y + 22), (x + 46, y + 22)], fill=GREY, width=1)
    draw.line([(x + 18, y + 28), (x + 46, y + 28)], fill=GREY, width=1)
    draw.text((x + 62, y + 10), "FEB 2027", font=SANS_B(16), fill=WHITE)


def art_boat(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 80, 120))
    for i in range(2):
        wy = y + 22 + i * 7
        draw.arc([x + 6, wy, x + w - 6, wy + 9], 0, 180, fill=(140, 200, 230),
                 width=2)
    draw.polygon([(x + 60, y + 8), (x + 96, y + 8), (x + 88, y + 20),
                  (x + 68, y + 20)], fill=(120, 70, 40))
    draw.text((x + 8, y + 8), "YENNE", font=SANS_B(12), fill=WHITE)


def art_strike(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    for i, col in enumerate([(0, 146, 70), (255, 255, 255), (205, 33, 42)]):
        draw.rectangle([x + 10 + i * 14, y + 8, x + 22 + i * 14, y + 30], fill=col,
                       outline=(180, 175, 160))
    draw.text((x + 62, y + 10), "100 SQUARES", font=SANS_B(14), fill=RED_DK)


def art_pill(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 240, 228))
    draw.ellipse([x + 10, y + 10, x + 66, y + 34], fill=(200, 60, 90))
    draw.ellipse([x + 38, y + 10, x + 66, y + 34], fill=(250, 250, 245))
    draw.ellipse([x + 10, y + 10, x + 66, y + 34], outline=(150, 40, 70), width=2)
    draw.text((x + 76, y + 12), "1 IN 12", font=SANS_B(14), fill=RED_DK)



def art_quake(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(245, 238, 220))
    draw.polygon([(x + 8, y + h), (x + 40, y + 6), (x + 72, y + h)], fill=(122, 84, 52))
    draw.polygon([(x + 52, y + h), (x + 92, y + 12), (x + 130, y + h)], fill=(90, 100, 112))
    draw.line([(x + 40, y + 6), (x + 34, y + 14), (x + 46, y + 14)], fill=WHITE, width=2)
    draw.text((x + 140, y + 10), "6.9", font=SANS_B(18), fill=RED_DK)


def art_cyber(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    draw.rectangle([x + 12, y + 16, x + 40, y + 36], fill=(200, 60, 60))
    draw.arc([x + 17, y + 6, x + 35, y + 22], 180, 360, fill=(200, 205, 220), width=3)
    draw.ellipse([x + 23, y + 22, x + 29, y + 28], fill=WHITE)
    draw.text((x + 52, y + 10), "HACKED", font=SANS_B(15), fill=WHITE)
    draw.text((x + 52, y + 26), "FBI · USDA", font=SANS_B(9), fill=(255, 150, 130))


def art_riyadh(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(30, 60, 90))
    for bx, bw, bh in [(10, 18, 20), (32, 14, 28), (50, 22, 16), (76, 16, 24)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(12, 18, 36))
    draw.arc([x + 100, y + 2, x + 170, y + 30], 200, 340, fill=(255, 220, 150), width=2)
    draw.arc([x + 110, y + 8, x + 160, y + 30], 200, 340, fill=WHITE, width=2)
    draw.text((x + 120, y + 8), "3 DOWN", font=SANS_B(12), fill=(255, 220, 150))


def art_protest(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(240, 236, 224))
    for i in range(7):
        cx = x + 16 + i * 22
        draw.ellipse([cx - 6, y + 22, cx + 6, y + 34], fill=(60, 60, 60))
        draw.rectangle([cx - 8, y + 34, cx + 8, y + h - 2], fill=NAVY)
    draw.rectangle([x + 130, y + 4, x + 182, y + 20], fill=RED)
    draw.text((x + 138, y + 7), "25", font=SANS_B(12), fill=WHITE)
    draw.line([(x + 156, y + 20), (x + 156, y + 30)], fill=INK, width=2)


def art_hormuz(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 80, 120))
    for i in range(2):
        wy = y + 24 + i * 7
        draw.arc([x + 6, wy, x + w - 6, wy + 9], 0, 180, fill=(140, 200, 230), width=2)
    draw.line([(x + 30, y + 8), (x + 70, y + 8)], fill=(200, 205, 220), width=2)
    draw.line([(x + 50, y + 4), (x + 50, y + 14)], fill=(200, 205, 220), width=2)
    draw.ellipse([x + 46, y + 6, x + 54, y + 12], fill=(200, 205, 220))
    draw.text((x + 84, y + 8), "58TH", font=SANS_B(15), fill=WHITE)
    draw.text((x + 84, y + 25), "MQ-9 DOWN", font=SANS_B(9), fill=(140, 200, 230))


def art_fires(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(60, 30, 20))
    for tx in (20, 60, 100):
        draw.polygon([(x + tx, y + h), (x + tx + 10, y + 14), (x + tx + 20, y + h)],
                     fill=(46, 110, 60))
    for fx, fr in [(40, 8), (90, 10), (140, 8)]:
        cx, cy = x + fx, y + h - 4
        draw.polygon([(cx - fr, cy), (cx, cy - fr * 2), (cx + fr, cy)], fill=(255, 150, 40))
        draw.polygon([(cx - fr // 2, cy), (cx, cy - fr), (cx + fr // 2, cy)],
                     fill=(255, 220, 110))
    draw.text((x + 130, y + 6), "FIRES", font=SANS_B(12), fill=(255, 220, 150))


def art_bayer(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 216))
    draw.line([(x + 30, y + 6), (x + 30, y + 34)], fill=INK, width=2)
    draw.line([(x + 12, y + 10), (x + 48, y + 10)], fill=INK, width=2)
    draw.arc([x + 8, y + 10, x + 20, y + 22], 0, 180, fill=INK, width=2)
    draw.arc([x + 40, y + 10, x + 52, y + 22], 0, 180, fill=INK, width=2)
    draw.text((x + 66, y + 8), "$7.25BN", font=SANS_B(14), fill=RED_DK)
    draw.text((x + 66, y + 24), "SETTLED", font=SANS_B(9), fill=GREY)


def art_basra(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(40, 40, 44))
    for bx, bw, bh in [(12, 16, 26), (34, 14, 30), (54, 18, 22)]:
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(120, 116, 108))
    draw.polygon([(x + 40, y + 8), (x + 46, y + 20), (x + 34, y + 20)], fill=(255, 150, 40))
    draw.text((x + 84, y + 8), "4 DEAD", font=SANS_B(14), fill=WHITE)
    draw.text((x + 84, y + 24), "HARTHA PLANT", font=SANS_B(9), fill=(200, 205, 220))


def art_palisades(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(120, 60, 30))
    draw.polygon([(x, y + h), (x + 70, y + 16), (x + 140, y + h)], fill=(60, 40, 26))
    draw.polygon([(x + 60, y + 20), (x + 66, y + 34), (x + 54, y + 34)], fill=(255, 150, 40))
    draw.polygon([(x + 62, y + 26), (x + 66, y + 34), (x + 58, y + 34)], fill=(255, 220, 110))
    draw.text((x + 110, y + 8), "GUILTY", font=SANS_B(14), fill=WHITE)
    draw.text((x + 110, y + 24), "ARSON", font=SANS_B(9), fill=(255, 220, 150))


# ---- map ----
def project(lon, lat, mx, my, mw, mh):
    """Equirectangular projection from the recipe."""
    px = mx + (lon + 180.0) * mw / 360.0
    py = my + (85.0 - lat) * mh / 145.0
    return px, py


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle([mx, my, mx + mw, my + mh], fill=NAVY)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=TAN)
    # graticule hints
    for lon in range(-150, 181, 30):
        gx, _ = project(lon, 85, mx, my, mw, mh)
        draw.line([(gx, my), (gx, my + mh)], fill=(38, 52, 84), width=1)
    # pins 4-13 first, lead pins 1-3 last (on top)
    ordered = sorted(PINS, key=lambda p: (0 if not p[3] else 1, p[0]))
    for num, lon, lat, is_lead in ordered:
        px, py = project(lon, lat, mx, my, mw, mh)
        r = 9 if is_lead else 7
        if is_lead:
            draw.ellipse([px - r - 2, py - r - 2, px + r + 2, py + r + 2],
                         outline=GOLD, width=2)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                     outline=WHITE, width=1)
        tw = draw.textlength(str(num), font=SANS_B(9))
        draw.text((px - tw / 2, py - 6), str(num), font=SANS_B(9), fill=WHITE)
    # Mercury / SPACE badge, top-right corner
    bx, by = mx + mw - 88, my + 6
    draw.rounded_rectangle([bx, by, bx + 82, by + 20], radius=4, fill=NAVY2,
                           outline=GOLD, width=1)
    draw.ellipse([bx + 5, by + 5, bx + 15, by + 15], fill=RED, outline=WHITE)
    draw.text((bx + 20, by + 4), "36 STORIES", font=SANS_B(9), fill=GOLD)


# ---- content (Saturday 21 November 2026 only) ----
STRAP = ("Missiles land in Poland · An AI sell-off sinks markets · "
         "COP31 runs overtime")
STRIP = [
    ("400+", "drones fired at Ukraine overnight"),
    ("110+", "missiles in the same barrage"),
    ("−3.7%", "S&P 500 falls into correction"),
    ("6.9", "magnitude quake shakes Peru's Andes"),
    ("25", "European countries hit by Gen Z protests"),
    ("$7.25bn", "Bayer Roundup settlement approved"),
]
REGIONS = [("EUROPE", "10", NAVY), ("AMERICAS", "11", RED),
           ("ASIA-PACIFIC", "5", TEAL), ("MIDEAST", "7", AMBER),
           ("WORLD", "3", SLATE)]
LEADS = [
    dict(kicker="01 · KYIV & POLAND · WAR",
         headline="Missiles land in Poland as Kyiv is hit again",
         body=("Overnight barrage of 400+ drones and 110+ missiles struck "
               "Kyiv's bridges, power and rail; two Russian missiles and a "
               "suspected drone came down in Poland. PM Tusk calls it a "
               "deliberate provocation. (Reuters, AP)"),
         art=art_kyiv),
    dict(kicker="02 · NEW YORK & TOKYO · MARKETS",
         headline="AI sell-off sinks markets into correction",
         body=("S&P 500 falls 3.7% into correction as AI and chip stocks "
               "rout Wall Street; Nasdaq drops 5.3%, Nikkei 5.1% to "
               "56,436.65, Hang Seng 1.9%. (Reuters, AP)"),
         art=art_markets),
    dict(kicker="03 · ANTALYA, TÜRKIYE · CLIMATE",
         headline="COP31 runs overtime with no fossil-fuel deal",
         body=("UN climate talks pass their deadline with ~200 nations "
               "deadlocked over fossil fuels; no agreement yet as "
               "negotiators work into the weekend. (UN News, Reuters)"),
         art=art_cop31),
]
FEATURES = [
    dict(kicker="04 · JUNÍN, PERU · QUAKE",
         headline="6.9 quake shakes Peru's Andes",
         body=("Strong tremor felt in Lima; no immediate reports of major "
               "damage. (Reuters)"),
         art=art_quake),
    dict(kicker="05 · WASHINGTON · CYBER",
         headline="FBI database reportedly hacked",
         body=("Criminal database and USDA systems hit as US outages "
               "continue. (Reuters)"),
         art=art_cyber),
    dict(kicker="06 · RIYADH · MISSILES",
         headline="Houthis fire on Riyadh; three intercepted",
         body=("Coalition says three missiles were stopped over the "
               "capital. (Reuters)"),
         art=art_riyadh),
    dict(kicker="07 · BERLIN · PROTESTS",
         headline="Gen Z protests spread to 25 countries",
         body=("Youth-led protests spread across 25 European countries. "
               "(AP)"),
         art=art_protest),
    dict(kicker="08 · LONDON · HEALTH",
         headline="Cancer pill undetectable in 1 in 12",
         body=("Daraxonrasib trial: tumours undetectable on scans in one "
               "in 12 patients. (Reuters)"),
         art=art_pill),
    dict(kicker="09 · STRAIT OF HORMUZ · DRONE",
         headline="Iran says it downed a US MQ-9",
         body=("Tehran says the drone is the 58th American MQ-9 it has "
               "brought down. (Reuters)"),
         art=art_hormuz),
    dict(kicker="10 · INDONESIA · FIRES",
         headline="Massive forest fires hit Indonesia",
         body=("Forest fires burn across Indonesia; crews battle the "
               "blazes. (AP)"),
         art=art_fires),
    dict(kicker="11 · UNITED STATES · COURTS",
         headline="Judge approves $7.25bn Bayer deal",
         body=("Roundup settlement validated, ending thousands of "
               "complaints. (Reuters)"),
         art=art_bayer),
    dict(kicker="12 · BASRA, IRAQ · FIRE",
         headline="Power-plant fire kills at least four",
         body=("Blaze at the Hartha plant injures 35 in the preliminary "
               "toll. (Reuters)"),
         art=art_basra),
    dict(kicker="13 · LOS ANGELES · FIRE",
         headline="Man convicted over Palisades fire",
         body=("Jury convicts him of starting the deadly Palisades fire. "
               "(AP)"),
         art=art_palisades),
]
BRIEFS = [
    ("14", "HORMUZ", "Lewis Pugh swims the Strait of Hormuz to spotlight the war's wildlife toll", "Reuters"),
    ("15", "GAZA", "Israeli strikes kill Palestinians in Gaza; West Bank violence continues", "AP"),
    ("16", "MADRID", "Spain heads to a 29 November election as conservatives gain", "Reuters"),
    ("17", "PORT-AU-PRINCE", "Salvadoran troops in Haiti lose soldiers to explosives", "AP"),
    ("18", "INDIA", "Eleven dead and 180+ hospitalised after drinking toxic alcohol", "Straits Times"),
    ("19", "WASHINGTON", "Trump defends his closeness to Putin and Xi on his return from Asia", "Reuters"),
    ("20", "WASHINGTON", "Trump tells Europe to defund Ukraine after his summit with Putin", "Telegraph"),
    ("21", "COPENHAGEN", "Denmark ratifies the US Greenland security deal, 109–0", "Reuters"),
    ("22", "PYONGYANG", "North Korea is expanding its Yongbyon uranium enrichment plant", "IAEA"),
    ("23", "DHAKA", "Violence flares in Bangladesh ahead of Hasina's planned return", "Reuters"),
    ("24", "CARACAS", "US signs a new military deal with Venezuela", "Reuters"),
    ("25", "KERCH", "Ukraine strikes the bridge to Crimea for a third time in four days", "Reuters"),
    ("26", "WASHINGTON", "Anthropic mathematician says he proved the Riemann hypothesis using AI", ""),
    ("27", "BRUSSELS", "UK and EU sign three post-Brexit agreements, their biggest since Brexit", "Reuters"),
    ("28", "LAS VEGAS", "Antonelli fastest in GP qualifying, but a penalty puts Verstappen on pole", "Reuters"),
    ("29", "CLEVELAND", "Harden scores 51 as the Cavaliers beat the Pacers, passing Kobe Bryant", "ESPN"),
    ("30", "TURIN", "Medvedev beats Tiafoe 6–3, 6–4 to reach the ATP Finals semi-finals", "ATP"),
    ("31", "KRYVYI RIH", "Russian strike kills two and injures 42, four of them children", ""),
    ("32", "DAMASCUS", "Syria arrests a former general accused of orchestrating a 2014 massacre", ""),
    ("33", "NEW YORK", "UN cuts its food-aid target despite the looming starvation threat", "UN News"),
    ("34", "BEIJING", "China calls the ICJ Rohingya ruling biased as Myanmar protests it", ""),
    ("35", "BAGHDAD", "Iraq arrests its oil-transport chief on oil-smuggling charges", ""),
    ("36", "KYIV", "Ukrainian drones hit a Russian fertiliser plant that also makes explosives", ""),
]
DATE_CHECK = ("First reported Thursday 19 Nov, so NOT shown as 21 Nov news: "
              "Trump-Xi-Putin Shenzhen summit · Anthropic Nasdaq debut "
              "($2tn) · ICJ Rohingya genocide verdict · GTA VI launch · "
              "Senate Iran war-powers vote 51-48.")
FOOTER = ("Every story here happened, or was first reported, on Saturday 21 "
          "November 2026 in at least one time zone. Sources: Reuters, AP, "
          "AFP, BBC, UN News, Al Jazeera. Original vector drawings.")


# ---- layout ----
def build():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # subtle deterministic paper grain (seeded) under all content
    rnd = random.Random(42)
    for _ in range(5200):
        gx = rnd.randint(0, W - 1)
        gy = rnd.randint(0, H - 1)
        d = rnd.choice([-5, -4, -3, 3, 4, 5])
        draw.point((gx, gy), fill=(CREAM[0] + d, CREAM[1] + d, CREAM[2] + d))

    # ---------- masthead ----------
    draw.text((M, 8), "THE WORLD IN ONE DAY", font=SANS_B(11), fill=RED)
    corner = "SATURDAY'S NEWS · ONE PAGE · 36 STORIES · 5 REGIONS"
    cw = draw.textlength(corner, font=SANS(10))
    draw.text((W - M - cw, 9), corner, font=SANS(10), fill=INK)
    draw_center(draw, W // 2, 20, "Saturday 21 November 2026", SERIF_B(52), INK)
    draw_center(draw, W // 2, 78, STRAP, SERIF_I(15), RED)
    hline(draw, M, W - M, 96, RULE, 2)

    # ---------- strip of 6 ----------
    cell_w = CW / 6.0
    for i, (num, cap) in enumerate(STRIP):
        cx = M + i * cell_w
        draw.text((cx + 8, 102), num, font=SERIF_B(26), fill=RED)
        draw_wrapped(draw, cx + 8, 132, cap, SANS(9), INK, cell_w - 16, 11,
                     max_lines=2)
        if i:
            vline(draw, cx, 102, 144, (200, 192, 172), 1)
    hline(draw, M, W - M, 148, (200, 192, 172), 1)

    # ---------- region bar ----------
    rx, ry = M, 154
    for name, n, col in REGIONS:
        label = f"{name} {n}"
        tw = draw.textlength(label, font=SANS_B(10))
        draw.rectangle([rx, ry, rx + tw + 14, ry + 16], fill=col)
        draw.text((rx + 7, ry + 2), label, font=SANS_B(10), fill=WHITE)
        rx += tw + 14 + 4
    tail = "ALL STORIES: SAT 21 NOV 2026"
    tw = draw.textlength(tail, font=SANS(9))
    draw.text((W - M - tw, ry + 3), tail, font=SANS(9), fill=GREY)

    # ---------- 3 lead cards ----------
    lead_w, lead_gap = 324, 12
    for i, lead in enumerate(LEADS):
        lx = M + i * (lead_w + lead_gap)
        ly = 172
        draw.rectangle([lx, ly, lx + lead_w, 406], outline=(205, 196, 176),
                       width=1)
        lead["art"](draw, lx + 1, ly + 1, lead_w - 2, 112)
        ky = ly + 118
        draw.text((lx + 8, ky), lead["kicker"], font=SANS_B(10), fill=RED)
        hy = ky + 15
        hl = wrap(draw, lead["headline"], SERIF_B(19), lead_w - 16)
        for j, ln in enumerate(hl[:3]):
            draw.text((lx + 8, hy + j * 21), ln, font=SERIF_B(19), fill=INK)
        by = hy + len(hl[:3]) * 21 + 4
        draw_wrapped(draw, lx + 8, by, lead["body"], SANS(10), INK,
                     lead_w - 16, 12.5, max_lines=3)

    # ---------- 10 feature cards (2 rows x 5) ----------
    feat_w, feat_gap = 192, 9
    for row in range(2):
        fy = 412 + row * 110
        for col in range(5):
            f = FEATURES[row * 5 + col]
            fx = M + col * (feat_w + feat_gap)
            draw.rectangle([fx, fy, fx + feat_w, fy + 108],
                           outline=(205, 196, 176), width=1)
            f["art"](draw, fx + 1, fy + 1, feat_w - 2, 40)
            ky = fy + 44
            draw.text((fx + 6, ky), f["kicker"], font=SANS_B(9), fill=RED)
            hy = ky + 13
            hl = wrap(draw, f["headline"], SERIF_B(13), feat_w - 12)
            for j, ln in enumerate(hl[:2]):
                draw.text((fx + 6, hy + j * 14), ln, font=SERIF_B(13), fill=INK)
            by = hy + len(hl[:2]) * 14 + 2
            draw_wrapped(draw, fx + 6, by, f["body"], SANS(9), INK,
                         feat_w - 12, 10.5, max_lines=2)

    # ---------- map + briefs ----------
    band_y = 644
    # map panel
    draw.text((M, band_y + 4), "WHERE IT HAPPENED", font=SANS_B(11), fill=RED)
    draw.text((M, band_y + 18), "Pins 1–13 mark the drawn stories",
              font=SANS(8), fill=GREY)
    map_x, map_y, map_w, map_h = M, band_y + 36, 336, 168
    draw_map(draw, map_x, map_y, map_w, map_h)
    draw.text((M, band_y + 36 + 168 + 8), "1–3 Lead (gold ring) · 4–13 Features",
              font=SANS(8), fill=GREY)
    draw.text((M, band_y + 36 + 168 + 20), "Positions approximate.",
              font=SANS(8), fill=GREY)
    # briefs
    bx0, bx1 = 362, W - M
    draw.text((bx0, band_y + 4), "ALSO ON SATURDAY 21 NOVEMBER — 23 MORE STORIES",
              font=SANS_B(11), fill=RED)
    tail = "World Briefs (14–36)"
    tw = draw.textlength(tail, font=SANS(9))
    draw.text((bx1 - tw, band_y + 5), tail, font=SANS(9), fill=GREY)
    col_w = 317
    cols = [(bx0, BRIEFS[:11]), (bx0 + col_w + 14, BRIEFS[11:])]
    for cx, items in cols:
        cy = band_y + 24
        for num, place, text, src in items:
            prefix = f"{num} {place} — "
            full = prefix + text + (f" ({src})" if src else "")
            lines = wrap(draw, full, SANS(9), col_w)
            for j, ln in enumerate(lines[:2]):
                if j == 0:
                    # bold prefix, regular remainder
                    pw = draw.textlength(prefix, font=SANS_B(9))
                    draw.text((cx, cy), prefix, font=SANS_B(9), fill=RED_DK)
                    draw.text((cx + pw, cy), ln[len(prefix):], font=SANS(9),
                              fill=INK)
                else:
                    draw.text((cx, cy), ln, font=SANS(9), fill=INK)
                cy += 11
            cy += 1
            if cy > 928:
                print(f"WARNING: briefs overflow at {num} {place}")
    hline(draw, M, W - M, 930, (200, 192, 172), 1)

    # ---------- DATE CHECK ----------
    draw.rectangle([M, 936, W - M, 984], outline=RED, width=2, fill=PAPER)
    draw.text((M + 8, 940), "DATE CHECK", font=SANS_B(11), fill=RED)
    draw_wrapped(draw, M + 8, 954, DATE_CHECK, SANS(10), INK, CW - 16, 12,
                 max_lines=2)

    # ---------- footer ----------
    draw_wrapped(draw, M, 990, FOOTER, SANS(8), GREY, CW, 10, max_lines=2)

    return img


def main():
    img = build()
    img.save(OUT, format="PNG", optimize=True)
    print("saved", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
