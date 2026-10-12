"""Sharpness (variance of a 4-neighbour Laplacian) per region. usage: sharp.py a.png b.png ..."""
import sys
import numpy as np
from PIL import Image
from shift import REGIONS

for f in sys.argv[1:]:
    a = np.asarray(Image.open(f).convert("L")).astype(float)
    out = []
    for k in ("car", "near sand right", "crate wall", "car shadow"):
        x0, y0, x1, y1 = REGIONS[k]
        r = a[y0:y1, x0:x1]
        lap = -4 * r[1:-1, 1:-1] + r[:-2, 1:-1] + r[2:, 1:-1] + r[1:-1, :-2] + r[1:-1, 2:]
        out.append(f"{k} {lap.var():.1f}")
    print(f, " | ".join(out))
