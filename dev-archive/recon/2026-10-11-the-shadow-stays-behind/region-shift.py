"""Horizontal shift of named regions between a reference frame and test frames (best normalised correlation over
+-80 px). Regions are full-resolution x0,y0,x1,y1 on the 1280x720 capture."""
import sys
import numpy as np
from PIL import Image

REGIONS = {
    "road edge (fused: terrain)": (120, 380, 420, 700),
    "near fence/sign (split)": (820, 150, 1100, 300),
    "Alan (split)": (720, 290, 900, 640),
    "street lamp glow": (380, 120, 520, 240),
    "trees top (fused: foliage)": (520, 0, 820, 160),
}


def g(f):
    return np.asarray(Image.open(f).convert("L")).astype(float)


def shift(a, b, box, rng=80):
    x0, y0, x1, y1 = box
    ref = a[y0:y1, x0:x1]
    ref = (ref - ref.mean()) / (ref.std() + 1e-6)
    best = (-9, 0)
    for dx in range(-rng, rng + 1):
        if x0 + dx < 0 or x1 + dx > b.shape[1]:
            continue
        t = b[y0:y1, x0 + dx:x1 + dx]
        t = (t - t.mean()) / (t.std() + 1e-6)
        c = float((ref * t).mean())
        if c > best[0]:
            best = (c, dx)
    return best


ref = g(sys.argv[1])
for f in sys.argv[2:]:
    b = g(f)
    print(f.split("/")[-1].split("\\")[-1])
    for name, box in REGIONS.items():
        c, dx = shift(ref, b, box)
        print("   %-28s dx=%+4d px  corr=%.2f" % (name, dx, c))
