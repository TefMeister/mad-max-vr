import sys, re, math
L = r"D:/Program Files (x86)/Steam/steamapps/common/Mad Max/madmax_vr_proxy_log.txt"
lines = open(L, encoding="utf-8", errors="replace").read().splitlines()
i = 0; dumpno = 0
while i < len(lines):
    if "full raw dump" in lines[i]:
        hdr = next((lines[j] for j in range(i, max(0, i-8), -1) if "cbfp frame=" in lines[j]), "")
        wid = re.search(r"width=(\d+)", hdr); dumpno += 1
        rows = {}; j = i + 1
        while j < len(lines):
            m = re.search(r"cbfp\s+(w\d+) slot\s*(\d+)\s*\(\+\s*\d+\):\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)", lines[j])
            if m: rows.setdefault(m.group(1), {})[int(m.group(2))] = tuple(float(x) for x in m.group(3,4,5,6))
            elif "cbfp" not in lines[j] or "census" in lines[j]: break
            j += 1
        if wid and wid.group(1) == "512":
            print("=== dump", dumpno, hdr[1:13], "frame", re.search(r"frame=(\d+)", hdr).group(1), "writes:", len(rows))
            for wname, sl in rows.items():
                if 9 in sl and 4 in sl and sl[4] == sl[9]:
                    c0 = math.sqrt(sum(sl[r][0]**2 for r in range(3))); c1 = math.sqrt(sum(sl[r][1]**2 for r in range(3))); c3 = math.sqrt(sum(sl[r][3]**2 for r in range(3)))
                    print("  %s cam=(%.2f, %.2f, %.2f)  |c0|=%.4f hfov=%.2f  |c1|=%.4f vfov=%.2f  |fwd|=%.4f  r3z=%.4f" % (wname, *sl[9][:3], c0, 2*math.degrees(math.atan(1/c0)), c1, 2*math.degrees(math.atan(1/c1)), c3, sl[3][2]))
                    break
            else:
                print("  no write with slot4==slot9; writes:", sorted(rows))
        i = j
    else: i += 1
