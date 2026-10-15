# Head passes, live run 2: what the refused candidates are, and the SSAO false positives

From: /lm reader, 2026-10-15 evening. Build read: fb4917c774f5 (diagnostics). Fix build: 13a39611011e,
staging d8dac0d. Switch: `[xr] head_passes=1` (default 0).

## What the run showed

Yaw +25 standing, driving about 8 s, yaw -25. Last counter line: fog 2229, ssao 8, sky 0, decal rays 2323;
candidates with a K 2,743,050 (64 B 1,263,588 · 80 B 0 · 96 B 354,867 · 128 B 712,981 · 256+ B 411,614);
filled before this frame's K 547,423; stale camera 0. [measured 2026-10-15, n=1 run]

## What the refused candidates are

- **Sky near misses are not sky matrices.** Example row set
  `[0 0 0 2.8965 | 0.9955 0.9917 0 0 | 174.921 0.020374 0 1.6 | 0.00113624 1 0 0]`: an empty column 2 by
  coincidence, but per-object instance/material data, not a projection. The sky test was right to refuse them.
  The real sky matrices most likely have an ordinary column 2 and are already turned by the per-object K edit.
  [inferred-static]
- **SSAO near misses are 128-byte per-object InstanceConsts**: WVP in rows 0..3, the object's own world
  rotation in rows 4..6 (B^T·R3 about 50 degrees off), c2 a matrix row, never lens-shaped
  (e.g. `[-0.000897 -0.2359 2.5e-06 -0.987]`). [inferred-static]
- **The 8 "SSAO" edits were false positives, and harmful.** The first, while driving, had rows 4..5
  `[0.9826 0.0263 0.1839 | 0.0068 0.984 -0.177]`: most likely the car's own buffer, whose rotation lines up with
  the chase camera seen from straight behind. The head-pass code claimed the slot, so the per-object K edit was
  skipped for that buffer that frame (a possible one-frame flicker of the car). [inferred-static]
- **The real SSAO cbConstants** probably arrive before this frame's K (about 250 buffers per frame are filled
  before the main-pass latch). [hypothesis] A draw-time edit would be needed if so.
- Decal rays exceeding fog by about 94 while driving: probably more decal types per frame. [hypothesis]

## The fix in 13a39611011e [compile-verified 2026-10-15]

1. Any candidate whose rows 0..3 are a camera matrix (`headk_is_camera`) is left to the per-object path,
   counted as "camera matrices left to the per-object edit".
2. The SSAO test now REQUIRES a lens-shaped c2 (|c2.x|·w ≈ 2, |c2.y|·h ≈ 2, c2.z ≈ -c2.x/2, c2.w ≈ -c2.y/2)
   before turning anything; the lens rescale for eye_hfov runs only when the eye lens differs.
3. New count "SSAO-shaped" inside "filled before this frame's K": 128-byte buffers with a lens-shaped c2 that
   arrive before the latch. Non-zero means the real SSAO is filled early and needs a draw-time edit.
4. Near-miss lines narrowed: SSAO only with a lens-shaped c2; sky only when the row scale is near the shared lens.
5. Self-test 269/269: the old "c2 without the lens shape is rescaled anyway" check now expects refusal, and a
   planted per-object buffer (camera WVP plus camera-aligned rotation) must be left untouched.

## What to look at live (next session)

With `head_passes=1`, drive straight with the chase camera: the SSAO count should stay 0 (or only rise with
real SSAO), "camera matrices left" should climb, and the car must not flicker. Read the new "SSAO-shaped"
number: non-zero means the SSAO pass is filled before K and needs a draw-time edit.

## Still open

- Decal box (144 B, about 176 fills per frame): needs a draw-time edit keyed on the `ssdecal*` pixel shaders.
- Real SSAO if filled before K: draw-time.
- Cloud shadow may not draw at all.
- SSAO c0.x (radius focal) is not scaled for eye_hfov.
- The eye_hfov live test needs the game's field of view widened (about 120 degrees or more for a 20-degree turn).
