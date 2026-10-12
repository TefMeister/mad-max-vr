"""Horizontal shift of named regions (784x561 capture) between a reference and test frames; best normalised
correlation over +-40 px. usage: shift.py ref.png test1.png [test2.png ...]"""
import sys
import numpy as np
from PIL import Image

REGIONS = {
    "car": (310, 320, 450, 470),
    "car shadow": (180, 400, 300, 540),
    "near sand right": (470, 420, 640, 520),
    "crate wall": (10, 220, 260, 280),
    "hills": (520, 120, 780, 230),
    "minimap (HUD)": (60, 380, 160, 470),
}


def g(f):
    return np.asarray(Image.open(f).convert("L")).astype(float)


def shift(a, b, box, rng=40):
    x0, y0, x1, y1 = box
    ref = a[y0:y1, x0:x1]; ref = (ref - ref.mean()) / (ref.std() + 1e-6)
    best = (-9, 0)
    for dx in range(-rng, rng + 1):
        if x0 + dx < 0 or x1 + dx > b.shape[1]: continue
        t = b[y0:y1, x0 + dx:x1 + dx]; t = (t - t.mean()) / (t.std() + 1e-6)
        c = (ref * t).mean()
        if c > best[0]: best = (c, dx)
    return best


if __name__ == '__main__':
  a = g(sys.argv[1])
  for f in sys.argv[2:]:
    b = g(f)
    print(f, " | ".join(f"{k} {shift(a, b, v)[1]:+d} ({shift(a, b, v)[0]:.2f})" for k, v in REGIONS.items()))
