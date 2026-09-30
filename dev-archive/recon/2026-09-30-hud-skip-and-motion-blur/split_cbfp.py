"""Move-only split of cbfp.c. Slices the ORIGINAL by line ranges; the only text
changes are (a) `static ` removed from symbols another file now needs, (b) three
anonymous struct arrays given a named typedef so they can be declared extern,
(c) new #include / comment lines. Everything else is byte-for-byte original."""
import re, sys, os

SRC = sys.argv[1]      # original cbfp.c
OUT = sys.argv[2]      # output src dir
L = open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n").split("\n")
# L[i] is line i+1

def rng(a, b):
    return L[a - 1:b]

DESTATIC = {
    # state now shared
    "g_cs", "g_ready", "g_track", "g_track_count", "g_pending", "g_frame",
    "g_census_count", "g_bind_count", "g_dump_pending", "g_mark_pending",
    "real_Map", "real_Unmap",
    # census / helpers
    "is_perobject_size", "g_probe_n", "g_probe_active", "g_probe_until", "g_probe_dropped",
    "probe_want", "probe_note", "probe_report", "is_tracked_size", "globals_slots",
    "tail_name", "cached_width", "track_for", "record_write", "constant_mask",
    "log_slot", "slots_xyz_equal", "log_per_write", "log_matrix_runs", "mask_to_text",
    # stereo
    "focal_from_matrix", "apply_eye_offset", "g_stereo_eye", "g_stereo_applied",
    "g_stereo_skipped", "g_stereo_path", "g_shared_w", "g_shared_w_frame",
    "g_main_pass_latched", "g_po_applied", "g_po_by_width", "g_po_no_w", "g_po_not_main",
    "g_po_bad", "g_pending_full", "perobj_decide", "g_readback_pending", "readback_check",
    # report
    "end_frame",
}
changed = []

def destatic(lines, first_lineno):
    out = []
    for k, s in enumerate(lines):
        if s.startswith("static "):
            m = re.match(r"static (?:const )?[\w\s\*\(]*?\(?\s*(?:STDMETHODCALLTYPE\s*)?\*?\s*(\w+)\s*[\[\(=;)]", s)
            # simple, robust: find the declared identifier
            ids = [n for n in DESTATIC if re.search(r"[\s\*\(]" + n + r"\b", s)]
            if ids:
                s = s[len("static "):]
                changed.append((first_lineno + k, ids[0]))
        out.append(s)
    return out

def anon(lines, first_lineno):
    rep = {
        "static struct { void *p; UINT bw; } g_cache[DESC_CACHE];": "CbfpCacheEntry g_cache[DESC_CACHE];",
        "static struct { UINT size; unsigned long count; } g_census[64];": "CbfpCensusEntry g_census[64];",
        "static struct { char stage; UINT slot; UINT size; unsigned long count; } g_bind[64];": "CbfpBindEntry g_bind[64];",
    }
    out = []
    for k, s in enumerate(lines):
        if s in rep:
            changed.append((first_lineno + k, "anon-struct -> " + rep[s].split()[0]))
            s = rep[s]
        out.append(s)
    return out

def seg(a, b):
    return anon(destatic(rng(a, b), a), a)

def skip(lines_with_no, drop):
    return lines_with_no

def seg_minus(a, b, drops):
    out = []
    for n in range(a, b + 1):
        if n in drops:
            continue
        out.append(L[n - 1])
    # re-run transforms line by line with correct numbers
    res = []
    for n in range(a, b + 1):
        if n in drops:
            continue
        res.extend(anon(destatic([L[n - 1]], n), n))
    return res

INC = '#include "cbfp_internal.h"'
def banner(name, what):
    return [f"/* {name} -- {what}",
            " * Split out of cbfp.c on 2026-09-30, MOVE-ONLY: see cbfp.c's header for the",
            " * whole design, and cbfp_internal.h for what the pieces share. */",
            INC, ""]

files = {}

# ---- header -----------------------------------------------------------
H = ["/* cbfp_internal.h -- what the cbfp_*.c pieces share. INTERNAL: proxy.c",
     " * includes only cbfp.h. Created 2026-09-30 by a move-only split of the",
     " * 1,568-line cbfp.c; every definition below was moved here verbatim, and the",
     " * extern block names only what more than one piece now needs. */",
     "#ifndef CBFP_INTERNAL_H", "#define CBFP_INTERNAL_H", ""]
H += rng(52, 59) + [""]
H += rng(61, 92) + [""]
H += rng(94, 113) + [""]
H += rng(185, 218) + [""]
H += ["/* From the candidate census block (cbfp_census.c). */", L[260 - 1],
      "/* From the edit read-back block (cbfp_stereo.c). */", L[760 - 1], "",
      "/* From the stereo block (cbfp_stereo.c) -- see the comments there. */",
      L[677 - 1], L[719 - 1], "",
      "/* Named so they can be declared extern; layout unchanged from the original",
      " * anonymous structs. */",
      "typedef struct { void *p; UINT bw; } CbfpCacheEntry;",
      "typedef struct { UINT size; unsigned long count; } CbfpCensusEntry;",
      "typedef struct { char stage; UINT slot; UINT size; unsigned long count; } CbfpBindEntry;",
      "",
      "/* ---- cbfp.c: shared state ---- */",
      "extern CRITICAL_SECTION g_cs;",
      "extern int g_ready;",
      "extern TrackedBuffer g_track[FP_MAX_BUFFERS];",
      "extern int g_track_count;",
      "extern PendingMap g_pending[FP_MAX_PENDING];",
      "extern CbfpCacheEntry g_cache[DESC_CACHE];",
      "extern CbfpCensusEntry g_census[64];",
      "extern int g_census_count;",
      "extern CbfpBindEntry g_bind[64];",
      "extern int g_bind_count;",
      "extern unsigned long g_frame;",
      "extern int g_dump_pending;",
      "extern int g_mark_pending;",
      "",
      "/* ---- cbfp_hooks.c ---- */",
      "extern HRESULT (STDMETHODCALLTYPE *real_Map)(ID3D11DeviceContext *, ID3D11Resource *, UINT,",
      "                                             D3D11_MAP, UINT, D3D11_MAPPED_SUBRESOURCE *);",
      "extern void (STDMETHODCALLTYPE *real_Unmap)(ID3D11DeviceContext *, ID3D11Resource *, UINT);",
      "",
      "/* ---- cbfp_census.c: candidate census, fingerprint helpers ---- */",
      "extern int           g_probe_n;",
      "extern int           g_probe_active;",
      "extern unsigned long g_probe_until;",
      "extern unsigned long g_probe_dropped;",
      "int is_perobject_size(UINT bw);",
      "int probe_want(UINT bw);",
      "void probe_note(UINT bw, const unsigned char *bytes);",
      "void probe_report(void);",
      "int is_tracked_size(UINT bw);",
      "int globals_slots(UINT bw);",
      "const char *tail_name(UINT bw);",
      "UINT cached_width(ID3D11Resource *res);",
      "TrackedBuffer *track_for(ID3D11Buffer *buf, UINT bw);",
      "void record_write(TrackedBuffer *t, const unsigned char *src, UINT src_bytes, int via_update);",
      "unsigned int constant_mask(const TrackedBuffer *t);",
      "void log_slot(const char *prefix, const unsigned char *bytes, int slot);",
      "int slots_xyz_equal(const unsigned char *bytes, int sa, int sb, float eps);",
      "void log_per_write(const TrackedBuffer *t);",
      "void log_matrix_runs(const char *prefix, unsigned int mask);",
      "void mask_to_text(unsigned int mask, char *out, size_t n);",
      "",
      "/* ---- cbfp_stereo.c: the per-eye edit, its latch and counters, read-back ---- */",
      "extern int   g_stereo_on;",
      "extern int   g_stereo_mode;",
      "extern float g_stereo_sep;",
      "extern int  g_stereo_eye;",
      "extern long g_stereo_applied;",
      "extern long g_stereo_skipped;",
      "extern int  g_stereo_path;",
      "extern float         g_shared_w;",
      "extern unsigned long g_shared_w_frame;",
      "extern int  g_main_pass_latched;",
      "extern long g_po_applied;",
      "extern long g_po_by_width[8];",
      "extern long g_po_no_w;",
      "extern long g_po_not_main;",
      "extern long g_po_bad;",
      "extern long g_pending_full;",
      "extern int  g_readback_pending;",
      "float focal_from_matrix(const float *m);",
      "int apply_eye_offset(float *m, float d, float w);",
      "int perobj_decide(void);",
      "void readback_check(ID3D11DeviceContext *ctx, ID3D11Resource *res, UINT bw,",
      "                    float expect, const char *what);",
      "",
      "/* ---- cbfp_report.c ---- */",
      "void end_frame(void);",
      "",
      "#endif /* CBFP_INTERNAL_H */", ""]
files["cbfp_internal.h"] = H

# ---- cbfp.c : top comment + shared state --------------------------------
C = rng(1, 51)
C += ["/* LAYOUT (2026-09-30 move-only split; the file had passed the 1,500-line hard",
      " * limit). This file keeps the design notes above and the shared state.",
      " *   cbfp_internal.h  constants, types, what the pieces share",
      " *   cbfp_census.c    candidate census + fingerprint/record/log helpers",
      " *   cbfp_stereo.c    the one-float per-eye edit, pass latch, counters, read-back",
      " *   cbfp_report.c    end_frame(): the per-frame report, marks, census lines",
      " *   cbfp_hooks.c     the D3D11/DXGI hooks, vtable capture, route B, cbfp_start",
      " *   cbfp_hotkeys.c   the NUMPAD entry points declared in cbfp.h */",
      INC, ""]
C += seg_minus(115, 137, {120})
C += [""]
files["cbfp.c"] = C

# ---- census ----
X = banner("cbfp_census.c", "candidate census and the fingerprint helpers.")
X += [L[183 - 1], "", L[120 - 1], ""]
X += seg(220, 259) + seg(261, 593) + [""]
files["cbfp_census.c"] = X

# ---- stereo ----
S = banner("cbfp_stereo.c", "the per-eye edit, the pass latch, its counters, read-back.")
S += seg_minus(595, 819, {677, 719, 760}) + [""]
files["cbfp_stereo.c"] = S

# ---- report ----
R = banner("cbfp_report.c", "end_frame(), the per-frame report.")
R += ["/* Mark A/B state (moved from cbfp.c's state block; only end_frame uses it). */"]
R += seg(138, 143) + [""]
R += seg(821, 1011) + [""]
files["cbfp_report.c"] = R

# ---- hooks ----
K = banner("cbfp_hooks.c", "the D3D11/DXGI hooks, vtable capture, route B, cbfp_start().")
K += seg(145, 181) + [""] + seg(1013, 1470) + [""]
files["cbfp_hooks.c"] = K

# ---- hotkeys ----
T = banner("cbfp_hotkeys.c", "the hotkey entry points declared in cbfp.h.")
T += seg(1471, 1568) + [""]
files["cbfp_hotkeys.c"] = T

os.makedirs(OUT, exist_ok=True)
for name, lines in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines))
    print(f"{name}: {len(lines)} lines")

# coverage: every original line 1..1568 used exactly once?
used = set()
for a, b in [(1,51),(52,59),(61,92),(94,113),(115,137),(138,143),(145,181),(183,183),(185,218),
             (220,259),(260,260),(261,593),(595,819),(821,1011),(1013,1470),(1471,1568)]:
    for n in range(a, b + 1):
        assert n not in used or n in (), n
        used.add(n)
missing = [n for n in range(1, len(L) + 1) if n not in used and L[n-1].strip()]
print("original non-blank lines not placed:", missing)
print("de-static / renamed lines:", len(changed))
for c in changed:
    print("  ", c)
