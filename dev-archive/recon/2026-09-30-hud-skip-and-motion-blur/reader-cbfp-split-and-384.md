# /lm reader, 2026-09-30: cbfp.c split (move-only) + what the 384-byte buffer is

From: the static reader helper beside the 2026-09-30 `/lm` session on Mad Max. Files only; the game
was never launched or attached. Nothing here is committed.

## 1. cbfp.c split, move-only

Work copy: `staging/mad-max-vr/cbfp-split-2026-09-30/proxy-dxgi/` (the live
`staging/mad-max-vr/proxy-dxgi/` was not touched; its `cbfp.c` is still 1,568 lines).

| file | lines | holds |
| --- | ---: | --- |
| `cbfp_internal.h` | 190 | includes, constants, types, the extern/prototype block |
| `cbfp.c` | 83 | the design comment + shared state |
| `cbfp_census.c` | 382 | candidate census + fingerprint/record/log helpers |
| `cbfp_stereo.c` | 227 | one-float eye edit, pass latch, counters, read-back |
| `cbfp_report.c` | 204 | `end_frame()` + mark A/B state |
| `cbfp_hooks.c` | 501 | D3D11/DXGI hooks, vtable capture, route B, `cbfp_start` |
| `cbfp_hotkeys.c` | 103 | the NUMPAD entry points from `cbfp.h` |

- Made by a script that slices the original by line range (`split_cbfp.py`, kept beside the copy).
  Text changes: 52 `static` keywords removed (only symbols another file now uses), three anonymous
  struct arrays (`g_cache`, `g_census`, `g_bind`) given named typedefs with the same layout so they
  can be declared `extern`, and new comments/includes/externs. `g_tracked_sizes` and
  `g_perobj_sizes` moved into the header as `static const` (each file gets a read-only copy).
- `verify_moveonly.py` (also kept there) checks it independently: 1,461 original non-blank lines,
  **0 missing** from the split; every added line is a comment, include guard, include, typedef,
  extern or prototype. `[verified-numerically 2026-09-30]`
- Other edits: `build.sh` lists the six `.c` files; `test/fp_selftest.c` includes all six in one
  translation unit, where it used to include `cbfp.c` alone. `README.md` still says "src/cbfp.c"
  and needs a line when this is adopted.
- Build before/after with `-Wall -Wextra`: **0 warnings both**. The self-test build (`-Wall`): 0 both.
  `[compile-verified 2026-09-30]`
- Self-test: **71/71 PASSED before and after, logs byte-identical**.
  `[verified-numerically 2026-09-30, n=71 checks]`
- The export table is identical, down to the RVAs (CreateDXGIFactory / 1 / 2 at 0x1410 / 0x1510 / 0x1610), and
  so are the imported DLLs.
- **The DLL is NOT byte-identical, and that is expected.** Before: 249,856 bytes, md5
  `a35cd0c6...` (same as the live staging build, so the baseline is reproducible). After: 250,880,
  md5 `657254d7...`. `.text` shrank 0x6296 to 0x5e66 and `.pdata` grew 0x234 to 0x2ac. The reason:
  the compiler used to inline across what is now a file boundary, and without LTO it cannot inline
  across files. Functions that were folded into their callers are now separate out-of-line
  functions. That changes the code layout, not the behaviour. The test runs the same source in a
  single unit, which is why it passes identically.
- Adopting it is a copy of `src/`, `build.sh` and `test/fp_selftest.c` over the live folder, plus
  deleting nothing. It was deliberately not done while `/lm` builds from that folder.

## 2. The 384-byte buffer

- **No shipped shader declares a 384-byte cbuffer** (84 layouts, 1,363 shaders; the two
  `*FragmentBundle_F.dll` files next to the bundle hold no DXBC at all). `[inferred-static 2026-09-30]`
- The only layout that can explain it is **`InstanceConsts`, 368 bytes, bound at VS `b1` in all
  112 vertex shaders that declare it.** Its highest slot actually read is 22 (+352..367), and 384 is
  368 rounded up to the next 64 bytes. This is the same "the runtime allocation is bigger than the
  declaration" pattern as 512 and 3136. No other VS-`b1` layout comes within 16 bytes of 384. That
  makes the 2026-09-10 finding "368 never existed" read differently: **the 368 layout most likely
  exists at runtime as a 384-byte buffer.** `[inferred-static 2026-09-30]`
- Its variables (reflection): `WorldViewProjMatrix` +0, `PointLights` +64 (192 bytes),
  `FaceNormal` +256, `DynamicLightMultiplier`, `LightSaturation`, `AmbientLightMultiplier`,
  `ColourMultiplier` +272, `SkyMaskProjMatrix` +288 (a second 4x4 read by 16 of the shaders),
  `ScaledUVs` +352, `AngleFade` +360.
- **Why it holds a copy of the camera's viewProj:** all 112 shaders build the position as
  `world = v0 + cbLightingConsts[3].xyz` (the 64-byte buffer at VS `b2`) and **then** multiply by
  `InstanceConsts[0..3]`. There is no rotation and no per-object matrix before that multiply. So
  `WorldViewProjMatrix` is only the world-to-clip viewProj, and the object's placement lives in
  `cbLightingConsts` slot 3. Seen in the disassembly of shader 0075, and in the SV_Position
  chain for all 112. `[inferred-static 2026-09-30, n=112 shaders]` The draw family is most likely
  translation-only, world-placed instances. Per-vertex alpha fade that culls to (-1,-1,-1,1),
  AngleFade and a FaceNormal sign point at foliage, grass or debris cards. `[hypothesis]`
- **Consequence for stereo:** for these 112 shaders the one-float edit on the 384 buffer is the
  *correct* eye shift (M = VP, and w = |col 0| of the same VP), and leaving 384 out means this
  whole draw family is never shifted. In per-object mode the shared edit is off, so including 384
  does not double-apply. That only happens in "both" mode. That unshifted geometry is one
  candidate for the persistent smear. `[hypothesis]`
- ⚠️ **An anomaly in the one live sample** (launch 4, 2026-09-10): rows 1..3 match the shared
  matrix, but row 0 is `(1.05936, 1.48046, -0.00000, 0.43881)`, where the shared row 0 is
  `(-0.94932, 0.09817, -0.000001, 0.43881)`. The first two numbers equal the lengths of the shared
  viewProj's column 0 and column 1 (1.059361 and 1.480463), which are the horizontal and vertical
  focal terms, to 5 decimals. `[verified-numerically 2026-09-30, n=1 sample]` Possible readings: (a) that write is not an
  InstanceConsts matrix at all, and slot 0 is a packed float4 carrying the projection scales; (b) a
  draw whose x axis is a non-unit billboard basis; (c) a second struct type sharing the width.
  Settle it with a live per-write dump of several 384 writes, all 24 slots. If slots 16, 17 and 22
  hold FaceNormal / ColourMultiplier / AngleFade-like values, and row 0 differs per draw while
  rows 1..3 do not, then it is InstanceConsts.

## 3. Found while reading, not asked: the per-object edit has no shape gate

In `hk_Map`/`hk_Unmap` every buffer whose width is 192/128/96/64 is edited (`m[12] += d*w`) whenever
the latch allows. The census's own clip-shape test (`probe_clip_like`) is never applied to the
edit. From the census, the share of those widths that are NOT clip-shaped: 192 ~34%, 128 ~52%,
96 ~83%, 64 ~92%. Byte +48 of those buffers is being changed. One of them is `cbLightingConsts`
(64 bytes, VS `b2`), whose slot 3.x is the **world x offset** of every object in the 112-shader
family above. That moves those objects along world x, not view x. Material and GUI buffers of the
same widths would also be hit. That is a plausible static cause for **both** open problems, the
HUD moving and the smear. `[inferred-static 2026-09-30]` for the code path; `[hypothesis]` for it
being the cause. A cheap test: gate the per-object edit on `probe_clip_like(m)`, which is a
behaviour change and the modding session's call. Then watch whether the HUD and the smear go away.

Kept locally, not committed (derived from game shaders): the disassembly cache and usage tables
live in the reader's session scratch folder only.
