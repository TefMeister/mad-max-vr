"""Independent check that the split is move-only: every original line is present
in the split files (after undoing ONLY a leading `static ` or the three named
struct typedefs), and every split line that is NOT an original line is printed
for a human to confirm it is a comment, include, typedef, extern or prototype."""
import sys, os, re
from collections import Counter

orig = open(sys.argv[1], encoding="utf-8").read().replace("\r\n", "\n").split("\n")
src = sys.argv[2]
names = ["cbfp_internal.h", "cbfp.c", "cbfp_census.c", "cbfp_stereo.c", "cbfp_report.c",
         "cbfp_hooks.c", "cbfp_hotkeys.c"]
split = []
for n in names:
    split += open(os.path.join(src, n), encoding="utf-8").read().replace("\r\n", "\n").split("\n")

UNDO = {
    "CbfpCacheEntry g_cache[DESC_CACHE];": "static struct { void *p; UINT bw; } g_cache[DESC_CACHE];",
    "CbfpCensusEntry g_census[64];": "static struct { UINT size; unsigned long count; } g_census[64];",
    "CbfpBindEntry g_bind[64];": "static struct { char stage; UINT slot; UINT size; unsigned long count; } g_bind[64];",
}
orig_c = Counter(l for l in orig if l.strip())
split_c = Counter()
destatic = 0
for l in split:
    if not l.strip():
        continue
    if l in UNDO:
        split_c[UNDO[l]] += 1
        continue
    if l not in orig_c and ("static " + l) in orig_c:
        split_c["static " + l] += 1
        destatic += 1
        continue
    split_c[l] += 1

missing = orig_c - split_c
extra = split_c - orig_c
print("original non-blank lines:", sum(orig_c.values()))
print("lines de-staticed:", destatic, "+ 3 anon-struct renames")
print("ORIGINAL LINES MISSING FROM SPLIT:", sum(missing.values()))
for l, c in missing.items():
    print("   MISSING x%d: %s" % (c, l))
print("ADDED lines (not in original):", sum(extra.values()))
for l, c in extra.items():
    print("   +x%d: %s" % (c, l))
