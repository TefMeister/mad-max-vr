"""Pull the camera-relevant slots out of every full dump after a line mark.

Reports, per dump of the 512-byte [Globals] buffer:
  hfov   from |col 0| = sqrt(m0^2+m4^2+m8^2), hfov = 2*atan(1/|col0|)
  slot 3 row 3 of the matrix (the translation row)
  slot 4 the per-pass view origin
  slot 9 the frame-constant main camera position

Slot 9 is the one the board named: if V moves the camera from the chase position
to the driver's seat, slot 9 should jump by roughly a car length.
"""
import math
import re
import sys

LOG = r"D:/Program Files (x86)/Steam/steamapps/common/Mad Max/madmax_vr_proxy_log.txt"
mark = int(sys.argv[1]) if len(sys.argv) > 1 else 0

pat = re.compile(
    r"cbfp\s+(?:vary|CONST)\s+slot\s+(\d+)\s+\(\s*\+?\s*\d+\)\s+\[Globals\]:\s+"
    r"(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)")

lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()[mark - 1:]

dumps, cur = [], {}
for ln in lines:
    m = pat.search(ln)
    if not m:
        continue
    slot = int(m.group(1))
    if slot == 0 and cur:
        dumps.append(cur)
        cur = {}
    cur[slot] = [float(m.group(i)) for i in range(2, 6)]
if cur:
    dumps.append(cur)

# keep only dumps that actually carry the camera slots
dumps = [d for d in dumps if {0, 1, 2, 3, 4, 9} <= set(d)]

print("%-5s %-9s %-49s %-49s" % ("dump", "hfov", "slot 9 (frame-constant camera)", "slot 4 (per-pass view origin)"))
prev9 = None
for i, d in enumerate(dumps):
    w = math.sqrt(d[0][0] ** 2 + d[1][0] ** 2 + d[2][0] ** 2)
    hf = 2 * math.degrees(math.atan(1.0 / w)) if w > 0 else float("nan")
    s9, s4 = d[9], d[4]
    flag = ""
    if prev9 is not None:
        dist = math.dist(s9[:3], prev9[:3])
        flag = "   moved %.2f units" % dist if dist > 0.01 else "   (still)"
    print("%-5d %-9.2f %-49s %-49s%s"
          % (i, hf,
             "%10.2f %9.2f %10.2f" % tuple(s9[:3]),
             "%10.2f %9.2f %10.2f" % tuple(s4[:3]),
             flag))
    prev9 = s9
if not dumps:
    print("(no complete [Globals] dumps found after the mark)")
