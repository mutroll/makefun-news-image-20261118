#!/usr/bin/env python3
"""news-image-20261118 entry: draw one image summing up the world news of
Wednesday 18 November 2026 and write it to /output/entry.png.

Python 3.13 standard library only, no network, fully deterministic:
the picture is drawn pixel by pixel with an own bitmap font and an own
PNG encoder (zlib/struct), so two runs write exactly the same bytes.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (246, 241, 229)
PANEL_BG = (255, 253, 247)
INK = (22, 22, 30)
WHITE = (255, 255, 255)
GOLD = (198, 146, 42)
RED = (166, 43, 37)
BLUE = (32, 99, 155)
UKRAINE_BLUE = (38, 84, 158)
NAVY = (36, 54, 94)
GREEN = (46, 125, 79)
PURPLE = (75, 46, 131)
SKY = (173, 205, 230)
SEA = (70, 130, 180)
YELLOW = (244, 197, 49)
GREY = (120, 118, 110)

# ---------------------------------------------------------------- font
# A 5x7 bitmap font, one tuple of 7 rows per glyph, '#' marks a lit cell.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".....", ".##..", ".##.."),
    "'": (".##..", ".##..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": (".##..", "..#..", "...#.", "...#.", "...#.", "..#..", ".##.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}


def text_width(s, scale, bold=False):
    if not s:
        return 0
    w = len(s) * 6 * scale - scale
    if bold:
        w += max(1, scale // 3)
    return w


def wrap_text(s, scale, max_width, bold=False):
    """Greedy word wrap: split s into lines no wider than max_width."""
    lines = []
    current = ""
    for word in s.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale, bold) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- canvas

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg) * (w * h)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def frame(self, x, y, w, h, color, t):
        self.rect(x, y, w, t, color)
        self.rect(x, y + h - t, w, t, color)
        self.rect(x, y, t, h, color)
        self.rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=3):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = max(0, t // 2)
        while True:
            self.rect(x0 - r, y0 - r, 2 * r + 1, 2 * r + 1, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dyy = yy - cy
            span = int((r * r - dyy * dyy) ** 0.5)
            self.rect(cx - span, yy, 2 * span + 1, 1, color)

    def poly(self, pts, color):
        ys = [p[1] for p in pts]
        for yy in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    nodes.append(x0 + (yy - y0) * (x1 - x0) // (y1 - y0))
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                self.rect(nodes[i], yy, nodes[i + 1] - nodes[i] + 1, 1, color)

    def text(self, x, y, s, scale, color, bold=False):
        dx = max(1, scale // 3) if bold else 0
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for r in range(7):
                row = glyph[r]
                for c in range(5):
                    if row[c] == "#":
                        self.rect(cx + c * scale, y + r * scale, scale, scale, color)
                        if dx:
                            self.rect(cx + c * scale + dx, y + r * scale,
                                      scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_centered(self, y, s, scale, color, bold=False):
        w = text_width(s, scale, bold)
        self.text((self.w - w) // 2, y, s, scale, color, bold)

    def text_block(self, x, y, s, scale, color, max_width, line_h,
                   bold=False, max_lines=None):
        lines = wrap_text(s, scale, max_width, bold)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * line_h, ln, scale, color, bold)
        return len(lines)


# ---------------------------------------------------------------- icons
# Each icon is drawn inside a box of about 88 x 60 px at (x, y).

def icon_missile(cv, x, y):
    # a missile flying up-right over sea waves
    cv.poly([(x + 26, y + 38), (x + 58, y + 2), (x + 70, y + 6),
             (x + 46, y + 42), (x + 34, y + 46)], INK)
    cv.poly([(x + 28, y + 36), (x + 16, y + 48), (x + 34, y + 46)], RED)
    cv.poly([(x + 22, y + 42), (x + 8, y + 56), (x + 28, y + 50)], GOLD)
    for i, wx in enumerate(range(x + 2, x + 84, 16)):
        wy = y + 52 + (4 if i % 2 else 0)
        cv.line(wx, wy, wx + 10, wy - 4, SEA, 3)


def icon_flags(cv, x, y):
    # three summit flags on poles
    for i, col in enumerate([RED, GOLD, BLUE]):
        px = x + 12 + i * 30
        cv.rect(px, y + 6, 3, 48, INK)
        cv.rect(px + 3, y + 6, 22, 14, col)
    cv.rect(x + 2, y + 54, 86, 4, INK)


def icon_bridge(cv, x, y):
    # a suspension bridge whose middle span has broken and dropped
    cv.rect(x + 14, y + 4, 6, 38, INK)
    cv.rect(x + 66, y + 4, 6, 38, INK)
    cv.line(x + 17, y + 4, x + 4, y + 32, GREY, 2)
    cv.line(x + 17, y + 4, x + 36, y + 32, GREY, 2)
    cv.line(x + 69, y + 4, x + 52, y + 32, GREY, 2)
    cv.line(x + 69, y + 4, x + 84, y + 32, GREY, 2)
    cv.rect(x + 2, y + 32, 36, 5, INK)
    cv.rect(x + 52, y + 32, 34, 5, INK)
    cv.line(x + 38, y + 34, x + 52, y + 44, RED, 5)
    for i, wx in enumerate(range(x + 2, x + 84, 16)):
        wy = y + 52 + (4 if i % 2 else 0)
        cv.line(wx, wy, wx + 10, wy - 4, SEA, 3)


def icon_dome(cv, x, y):
    # a capitol dome on columns
    cv.disc(x + 44, y + 26, 20, NAVY)
    cv.rect(x + 24, y + 26, 40, 6, PAPER)
    cv.rect(x + 42, y + 0, 4, 8, NAVY)
    cv.disc(x + 44, y + 2, 3, GOLD)
    cv.rect(x + 16, y + 32, 56, 4, INK)
    for i in range(4):
        cv.rect(x + 20 + i * 14, y + 36, 5, 14, INK)
    cv.rect(x + 14, y + 50, 60, 4, INK)


def icon_health(cv, x, y):
    # a medical cross badge with virus dots around it
    cv.disc(x + 44, y + 28, 22, RED)
    cv.rect(x + 39, y + 14, 10, 28, WHITE)
    cv.rect(x + 30, y + 23, 28, 10, WHITE)
    for (dx, dy) in [(6, 6), (78, 4), (82, 44), (4, 46), (70, 54), (14, 56)]:
        cv.disc(x + dx, y + dy, 4, GREEN)
        cv.line(x + dx, y + dy, x + dx + 6, y + dy - 6, GREEN, 2)


def icon_probe(cv, x, y):
    # a deep-space probe: dish, body, boom, stars
    for (sx, sy) in [(8, 6), (76, 2), (84, 30), (64, 52), (6, 34)]:
        cv.rect(x + sx, y + sy, 3, 3, GOLD)
    cv.poly([(x + 10, y + 10), (x + 42, y + 26), (x + 10, y + 42)], BLUE)
    cv.line(x + 32, y + 26, x + 52, y + 26, INK, 3)
    cv.rect(x + 52, y + 20, 14, 12, INK)
    cv.line(x + 66, y + 26, x + 84, y + 10, INK, 2)
    cv.disc(x + 85, y + 9, 3, RED)
    cv.line(x + 59, y + 32, x + 59, y + 48, INK, 3)
    cv.line(x + 48, y + 48, x + 70, y + 48, GOLD, 3)


ICONS = [icon_missile, icon_flags, icon_bridge, icon_dome, icon_health,
         icon_probe]

# ---------------------------------------------------------------- content

PANELS = [
    ("MIDDLE EAST", RED, icon_missile,
     "US BOMBS IRAN, IRAN HITS BACK",
     "US JETS HIT A GUARDS SITE ON QESHM ISLAND; IRAN HIT BASES IN "
     "KUWAIT, BAHRAIN."),
    ("ASIA-PACIFIC", BLUE, icon_flags,
     "XI, PUTIN MEET AT APEC",
     "XI PROMISED TO FIGHT PROTECTIONISM; PUTIN HIT SANCTIONS. "
     "A TRUMP SUMMIT FOLLOWS."),
    ("UKRAINE", UKRAINE_BLUE, icon_bridge,
     "UKRAINE HITS KERCH BRIDGE",
     "ITS ROADWAY PARTLY FELL AFTER SECOND-DAY STRIKES. 141 DRONES; "
     "SIX HURT IN DNIPRO."),
    ("UNITED STATES", NAVY, icon_dome,
     "SENATE GOES 56-44",
     "IN ALASKA, MARY PELTOLA BEAT DAN SULLIVAN: DEMOCRATS' BIGGEST "
     "MAJORITY SINCE 2009."),
    ("HEALTH", GREEN, icon_health,
     "US LOSES MEASLES STATUS",
     "AFTER 26 YEARS, 5,412 CASES ENDED US ELIMINATION. CONGO EBOLA: "
     "11,000 CASES."),
    ("SPACE", PURPLE, icon_probe,
     "VOYAGER 1: A LIGHT-DAY OUT",
     "THE FARTHEST HUMAN-MADE OBJECT EVER: 16 BILLION MILES OUT, "
     "A LIGHT-DAY AWAY."),
]

FOOTER = ("ALSO TODAY: KNESSET ELECTS KAHANA SPEAKER - PEACE BOARD FAULTS "
          "ISRAEL, HAMAS - WHO: 950,000 IN GAZA FACE FLOODS")


def draw_panel(cv, x, y, w, h, panel):
    cat, color, icon, headline, caption = panel
    cv.rect(x, y, w, h, PANEL_BG)
    cv.frame(x, y, w, h, INK, 2)
    cv.rect(x, y, w, 26, color)
    cv.text(x + 12, y + 3, cat, 3, WHITE, bold=True)
    icon(cv, x + 14, y + 38)
    cv.text_block(x + 114, y + 36, headline, 4, INK, w - 114 - 12, 31,
                  bold=True, max_lines=2)
    cv.text_block(x + 12, y + 104, caption, 3, INK, w - 24, 24,
                  max_lines=4)


def build_image():
    cv = Canvas(W, H, PAPER)
    cv.frame(10, 10, W - 20, H - 20, INK, 3)
    cv.frame(18, 18, W - 36, H - 36, INK, 1)

    # masthead
    cv.text_centered(28, "THE DAY'S WORLD NEWS IN ONE PICTURE", 3, RED,
                     bold=True)
    cv.text_centered(58, "THE WORLD IN ONE DAY", 7, INK, bold=True)
    cv.rect(24, 118, W - 48, 5, INK)
    cv.rect(24, 128, W - 48, 2, INK)
    cv.text_centered(142, "WEDNESDAY", 10, INK, bold=True)
    cv.text_centered(220, "18 NOVEMBER 2026", 9, RED, bold=True)
    cv.rect(24, 292, W - 48, 2, INK)

    # six story panels, two columns by three rows
    pw, ph = 482, 198
    for i, panel in enumerate(PANELS):
        col = i % 2
        row = i // 2
        x = 24 + col * (pw + 12)
        y = 302 + row * (ph + 10)
        draw_panel(cv, x, y, pw, ph, panel)

    # footer strip: three caption lines inside the dark band
    fy = 924
    cv.rect(24, fy, W - 48, 76, INK)
    cv.text_block(40, fy + 5, FOOTER, 3, WHITE, W - 80, 23, max_lines=3)
    return cv


# ---------------------------------------------------------------- png out

def encode_png(cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.buf[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build_image())
    with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
