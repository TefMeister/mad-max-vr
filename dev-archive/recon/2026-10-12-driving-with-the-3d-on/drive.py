"""drive.py LABEL KEYS SECONDS : hold keys (e.g. w or w+a), screenshot every second, release."""
import sys, time, mm
label, keys, secs = sys.argv[1], sys.argv[2].split('+'), float(sys.argv[3])
mm.fg(mm.find())
for k in keys: mm.send(*mm.SC[k], False)
t0 = time.time(); i = 0
try:
    while time.time() - t0 < secs:
        time.sleep(1.0); i += 1; mm.shot(f"{label}_{i}.png")
finally:
    for k in keys: mm.send(*mm.SC[k], True)
