"""Read hfov out of every full dump in a Mad Max proxy log, after a line mark.

hfov = 2*atan(1/|col 0|), where |col 0| = sqrt(m0^2 + m4^2 + m8^2), i.e. the x
components of slots 0,1,2. The relation is the one fitted to the project's own
two 2026-09-04b calibration points (|col0| 1.7936 -> 58.28 deg, 0.6138 ->
116.91 deg); both reproduce to 0.01 deg.

Only the '[Globals]' frame-constant slots are used - the per-write 'wNN' rows
are per-object matrices whose column 0 carries object scale (a 3x-scaled object
reads 3.54 where the shared frame reads 1.18), so they are NOT comparable.
"""
import math
import re
import sys

LOG = r"D:/Program Files (x86)/Steam/steamapps/common/Mad Max/madmax_vr_proxy_log.txt"
mark = int(sys.argv[1]) if len(sys.argv) > 1 else 0

pat = re.compile(
    r"cbfp\s+(?:vary|CONST)\s+slot\s+([0-2])\s+\(\s*\+?\s*\d+\)\s+\[Globals\]:\s+"
    r"(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)")

lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()[mark - 1:]

dumps, cur = [], {}
for ln in lines:
    m = pat.search(ln)
    if not m:
        continue
    slot = int(m.group(1))
    if slot == 0 and cur:
        cur = {}
    cur[slot] = [float(m.group(i)) for i in range(2, 6)]
    if len(cur) == 3:
        dumps.append(cur)
        cur = {}

print("%-6s %-10s %-10s" % ("dump", "|col 0|", "hfov(deg)"))
prev = None
for i, d in enumerate(dumps):
    w = math.sqrt(d[0][0] ** 2 + d[1][0] ** 2 + d[2][0] ** 2)
    hf = 2 * math.degrees(math.atan(1.0 / w)) if w > 0 else float("nan")
    flag = ""
    if prev is not None and abs(hf - prev) > 0.05:
        flag = "   <-- CHANGED by %+.2f deg" % (hf - prev)
    print("%-6d %-10.5f %-10.2f%s" % (i, w, hf, flag))
    prev = hf
if not dumps:
    print("(no [Globals] dumps found after the mark)")
