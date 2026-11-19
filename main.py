#!/usr/bin/env python3
"""The World In One Day - a bold poster summing up Wednesday 18 November 2026.

Pure Python 3.13 standard library. Deterministic: the same code always
produces the same PNG bytes. Writes entry.png to MAKEFUN_OUTPUT_DIR
when that variable is set, otherwise to /output.
"""

import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- canvas

class Canvas:
    """A plain RGB framebuffer with blocky, high-contrast drawing helpers."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(colour) * (width * height)

    def rect(self, x, y, rw, rh, colour):
        x0 = max(0, int(x)); y0 = max(0, int(y))
        x1 = min(self.w, int(x + rw)); y1 = min(self.h, int(y + rh))
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            off = (yy * self.w + x0) * 3
            self.px[off:off + len(row)] = row

    def dot(self, cx, cy, r, colour):
        """A filled circle, stamped as horizontal runs."""
        cx = int(cx); cy = int(cy); r = int(r)
        for yy in range(cy - r, cy + r + 1):
            if yy < 0 or yy >= self.h:
                continue
            dx = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
            self.rect(cx - dx, yy, dx * 2 + 1, 1, colour)

    def line(self, x0, y0, x1, y1, thick, colour):
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        r = max(1, thick // 2)
        for i in range(steps + 1):
            t = i / steps
            self.dot(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, colour)

    def tri(self, ax, ay, bx, by, cx, cy, colour):
        """Filled triangle via scanline barycentric test on a coarse grid."""
        x0 = int(max(0, min(ax, bx, cx))); x1 = int(min(self.w - 1, max(ax, bx, cx)))
        y0 = int(max(0, min(ay, by, cy))); y1 = int(min(self.h - 1, max(ay, by, cy)))
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if den == 0:
            return
        for yy in range(y0, y1 + 1, 2):
            for xx in range(x0, x1 + 1, 2):
                w0 = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / den
                w1 = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / den
                w2 = 1.0 - w0 - w1
                if w0 >= -0.02 and w1 >= -0.02 and w2 >= -0.02:
                    self.rect(xx, yy, 2, 2, colour)

# ---------------------------------------------------------------- png out

def save_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)

# ---------------------------------------------------------------- font
# A chunky 5x7 pixel font, drawn as solid blocks: bold at any size.

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
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
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
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    ":": (".....", "..#..", "..#..", ".....", "..#..", "..#..", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
}

def text_width(text, scale):
    if not text:
        return 0
    return len(text) * (5 * scale + scale - 1) - (scale - 1)

def draw_text(cv, x, y, text, scale, colour):
    pitch = 5 * scale + scale - 1
    for i, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT[" "])
        gx = x + i * pitch
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.rect(gx + col * scale, y + row * scale, scale, scale, colour)

def draw_centered(cv, cx, y, text, scale, colour):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, colour)

# ---------------------------------------------------------------- palette

INK    = (10, 14, 26)
PAPER  = (246, 244, 238)
WHITE  = (255, 255, 255)
YELLOW = (255, 205, 40)
RED    = (214, 40, 44)
BLUE   = (36, 96, 200)
SKY    = (120, 190, 240)
SEA    = (18, 84, 148)
ORANGE = (255, 130, 30)
GREEN  = (30, 160, 90)
TEAL   = (14, 130, 140)
PURPLE = (86, 52, 160)
GREY   = (96, 104, 118)
BROWN  = (140, 96, 52)

# ---------------------------------------------------------------- scenes
# Each scene fills a box (x, y, w, h = 494 x 138) with one bold picture.

def scene_gulf(cv, x, y, w, h):
    """Missile arc over the Strait of Hormuz, ship below, burst at impact."""
    cv.rect(x, y, w, h - 26, SEA)
    cv.rect(x, y + h - 26, w, 26, (10, 52, 96))
    # missile body, nose up-right, flame behind
    cv.line(x + 92, y + 92, x + 196, y + 34, 13, WHITE)
    cv.line(x + 92, y + 92, x + 66, y + 106, 15, ORANGE)
    cv.line(x + 78, y + 99, x + 58, y + 112, 9, RED)
    # dashed arc of the strike path
    for t in range(9):
        cv.dot(x + 210 + t * 22, y + 30 + int(26 * ((t / 8) ** 2)), 4, YELLOW)
    # explosion burst where it lands
    bx, by = x + 392, y + 62
    for ang in range(0, 360, 30):
        import math
        ex = bx + int(38 * math.cos(math.radians(ang)))
        ey = by + int(38 * math.sin(math.radians(ang)))
        cv.line(bx, by, ex, ey, 7, ORANGE)
    cv.dot(bx, by, 15, YELLOW)
    cv.dot(bx, by, 8, WHITE)
    # warship silhouette on the water line
    cv.rect(x + 60, y + h - 40, 150, 14, INK)
    cv.rect(x + 96, y + h - 54, 52, 14, INK)
    cv.rect(x + 116, y + h - 66, 10, 12, INK)

def scene_apec(cv, x, y, w, h):
    """Two leaders shaking hands under a gold APEC sun."""
    cv.rect(x, y, w, h, RED)
    cv.dot(x + w // 2, y + 34, 22, YELLOW)
    for dx in (-120, -80, 80, 120):
        cv.dot(x + w // 2 + dx, y + 26, 5, YELLOW)
    # left figure
    cv.dot(x + 148, y + 62, 17, PAPER)
    cv.rect(x + 128, y + 78, 40, 52, INK)
    # right figure
    cv.dot(x + w - 148, y + 62, 17, PAPER)
    cv.rect(x + w - 168, y + 78, 40, 52, BLUE)
    # arms meeting in the middle, clasped hands
    cv.line(x + 168, y + 92, x + w // 2 - 8, y + 106, 11, INK)
    cv.line(x + w - 168, y + 92, x + w // 2 + 8, y + 106, 11, BLUE)
    cv.dot(x + w // 2, y + 106, 10, PAPER)
    # banner strip
    cv.rect(x + 60, y + h - 20, w - 120, 8, YELLOW)

def scene_bridge(cv, x, y, w, h):
    """The Kerch Bridge: two towers, the middle span fallen into the sea."""
    cv.rect(x, y, w, h - 30, SKY)
    cv.rect(x, y + h - 30, w, 30, SEA)
    # towers
    cv.rect(x + 84, y + 26, 16, 82, GREY)
    cv.rect(x + w - 100, y + 26, 16, 82, GREY)
    # cables
    cv.line(x + 92, y + 26, x + 40, y + 76, 4, INK)
    cv.line(x + w - 92, y + 26, x + w - 40, y + 76, 4, INK)
    cv.line(x + 92, y + 26, x + w // 2 - 40, y + 70, 4, INK)
    cv.line(x + w - 92, y + 26, x + w // 2 + 40, y + 70, 4, INK)
    # standing deck left and right
    cv.rect(x + 20, y + 72, w // 2 - 62, 12, INK)
    cv.rect(x + w // 2 + 42, y + 72, w // 2 - 62, 12, INK)
    # the fallen span, tilted down into the water
    cv.line(x + w // 2 - 42, y + 78, x + w // 2 + 42, y + 106, 13, RED)
    # splash marks
    for dx in (-26, 0, 26):
        cv.line(x + w // 2 + dx, y + h - 30, x + w // 2 + dx - 6, y + h - 48, 5, WHITE)
    # drone overhead
    cv.dot(x + w - 70, y + 22, 7, INK)
    cv.line(x + w - 88, y + 22, x + w - 52, y + 22, 5, INK)
    cv.line(x + w - 70, y + 12, x + w - 70, y + 32, 5, INK)

def scene_senate(cv, x, y, w, h):
    """Bar chart of the new Senate: blue 56, red 44."""
    cv.rect(x, y, w, h, PAPER)
    base = y + h - 36
    # blue bar, 56 seats, its number inside the bar in white
    cv.rect(x + 110, base - 92, 84, 92, BLUE)
    draw_centered(cv, x + 152, base - 62, "56", 5, WHITE)
    # red bar, 44 seats
    cv.rect(x + 300, base - 72, 84, 72, RED)
    draw_centered(cv, x + 342, base - 42, "44", 5, WHITE)
    # baseline and party ticks
    cv.rect(x + 60, base, w - 120, 6, INK)
    draw_centered(cv, x + 152, base + 10, "DEM", 3, INK)
    draw_centered(cv, x + 342, base + 10, "REP", 3, INK)
    # a gold star for the flipped Alaska seat
    sx, sy = x + 42, y + 30
    cv.line(sx, sy - 14, sx, sy + 14, 6, YELLOW)
    cv.line(sx - 13, sy - 5, sx + 13, sy + 9, 6, YELLOW)
    cv.line(sx + 13, sy - 5, sx - 13, sy + 9, 6, YELLOW)

def scene_health(cv, x, y, w, h):
    """A medical cross beside a spiked virus ball: two outbreaks, one panel."""
    cv.rect(x, y, w, h, (240, 246, 244))
    # red cross in a white badge, left
    cv.dot(x + 92, y + h // 2, 44, WHITE)
    cv.rect(x + 80, y + h // 2 - 30, 24, 60, RED)
    cv.rect(x + 62, y + h // 2 - 12, 60, 24, RED)
    # virus ball, right
    vx, vy = x + w - 130, y + h // 2
    import math
    for ang in range(0, 360, 36):
        ex = vx + int(52 * math.cos(math.radians(ang)))
        ey = vy + int(52 * math.sin(math.radians(ang)))
        cv.line(vx, vy, ex, ey, 7, TEAL)
        cv.dot(ex, ey, 8, TEAL)
    cv.dot(vx, vy, 36, TEAL)
    cv.dot(vx - 12, vy - 8, 7, WHITE)
    cv.dot(vx + 10, vy + 10, 6, WHITE)
    cv.dot(vx + 14, vy - 14, 5, WHITE)
    # rising case dots between them
    for i, dy in enumerate((34, 22, 8, -10)):
        cv.dot(x + 218 + i * 26, y + h // 2 + dy, 6, ORANGE)

def scene_voyager(cv, x, y, w, h):
    """Voyager 1 in deep black space: big dish, long boom, tiny Earth."""
    cv.rect(x, y, w, h, (4, 6, 18))
    # stars
    seed = 7
    for _ in range(46):
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sx = x + seed % (w - 16) + 8
        seed = (seed * 1103515245 + 12345) % (2 ** 31)
        sy = y + seed % (h - 16) + 8
        cv.rect(sx, sy, 3, 3, WHITE)
    # probe: dish, bus, boom
    cv.dot(x + 150, y + 62, 34, PAPER)
    cv.dot(x + 150, y + 62, 34 - 7, (196, 200, 208))
    cv.dot(x + 150, y + 62, 6, INK)
    cv.rect(x + 182, y + 56, 44, 12, GREY)
    cv.line(x + 226, y + 62, x + 356, y + 30, 6, GREY)
    cv.dot(x + 362, y + 28, 8, YELLOW)
    cv.line(x + 190, y + 70, x + 268, y + 108, 6, GREY)
    # signal waves travelling home
    for i in range(3):
        cv.line(x + 118 - i * 22, y + 48 + i * 4, x + 118 - i * 22, y + 76 - i * 4, 5, SKY)
    # Earth: one small blue dot, very far away
    cv.dot(x + 52, y + 108, 9, BLUE)
    cv.dot(x + 49, y + 105, 3, GREEN)

# ---------------------------------------------------------------- layout

PANELS = [
    # scene,       title line 1,       title line 2,      subline,                 accent
    (scene_gulf,   "US STRIKES IRAN",  "AT HORMUZ",       "MISSILE SITE HIT",      RED),
    (scene_apec,   "XI + PUTIN MEET",  "IN SHENZHEN",     "APEC SUMMIT OPENS",     YELLOW),
    (scene_bridge, "KERCH BRIDGE",     "SPAN COLLAPSES",  "UKRAINE STRIKE DAY 2",  ORANGE),
    (scene_senate, "ALASKA FLIPS",     "SENATE 56-44",    "DEMOCRATS TAKE SEAT",   BLUE),
    (scene_health, "US LOSES MEASLES", "EBOLA IN CONGO",  "LOST AFTER 26 YEARS",   TEAL),
    (scene_voyager, "VOYAGER 1",       "ONE LIGHT-DAY",   "FARTHEST OBJECT EVER",  PURPLE),
]

def masthead(cv):
    # red kicker strip
    cv.rect(0, 0, W, 40, RED)
    draw_centered(cv, W // 2, 8, "THE WORLD IN ONE DAY", 3, WHITE)
    # the day, named as large as the canvas allows
    cv.rect(0, 40, W, 172, INK)
    draw_centered(cv, W // 2, 50, "WEDNESDAY", 15, WHITE)
    draw_centered(cv, W // 2, 162, "18 NOVEMBER 2026", 6, YELLOW)

def panel(cv, x, y, w, h, scene, line1, line2, sub, accent):
    scene(cv, x, y, w, 138)
    # black title strip: white titles, coloured subline, accent rule
    cv.rect(x, y + 138, w, h - 138, INK)
    cv.rect(x, y + 138, w, 6, accent)
    draw_text(cv, x + 14, y + 150, line1, 5, WHITE)
    draw_text(cv, x + 14, y + 188, line2, 5, WHITE)
    # sublines get a brightened tint so they stay readable at 300 px wide
    sub_colour = {BLUE: SKY, TEAL: (64, 224, 208), PURPLE: (200, 160, 255)}.get(accent, accent)
    draw_text(cv, x + 14, y + 226, sub, 4, sub_colour)

def build():
    cv = Canvas(W, H, INK)
    masthead(cv)
    top = 224
    pw, ph, gap, mx = 494, 258, 12, 12
    for i, (scene, l1, l2, sub, acc) in enumerate(PANELS):
        col, row = i % 2, i // 2
        panel(cv, mx + col * (pw + gap), top + row * (ph + gap),
              pw, ph, scene, l1, l2, sub, acc)
    return cv

def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    size = save_png(build(), os.path.join(out_dir, "entry.png"))
    print(f"entry.png written: {size} bytes, {W}x{H}")

if __name__ == "__main__":
    main()
