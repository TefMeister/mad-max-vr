# 2026-10-14 (dev PC, `/lm` reader helper, static + numbers): why any head pose breaks the picture

Source: `staging/mad-max-vr/proxy-dxgi/src/cbfp_headk.c` (`hk_mul`, `headk_build`, `headk_view_from_head`,
`headk_apply`), `cbfp_hooks.c` (`unmap_perobj`), `cbfp_census.c`, `cbfp_stereo.c`. Real numbers: the main-pass
shared V·P (write 3 of frame 12097) in the game folder's `madmax_vr_proxy_log.prev-20260910-185248.txt`, and the
bind census in `...prev-20261012-run5.txt`. Script: numpy on those numbers (scratch, not kept).

Main-pass V·P (row-vector, row-major memory):
```
-0.949325   0.098165  -0.000001   0.438810
-0.000032   1.463831   0.000000  -0.149469
 0.470136   0.198318  -0.000002   0.886061
-5789.685 -1519.886    0.111179 -4465.620
```
w = 1.05936 (matches the log's shared_w), h = 1.48046, n read = vp[14] = 0.111179.

## 1. Which product is the old edit

With `hk_mul` (r[i*4+j] = Σ a[i*4+k]·b[k*4+j]) and K = P⁻¹·E·P, a pure sideways eye shift gives K = identity plus
K[8] (row 2, column 0) = d·w/n. Then:
- **M·K** adds K[8]·(column 2) to column 0. On a real camera matrix column 2 is ≈ [0,0,0,n], so this is
  `m[12] += d·w`. On the real V·P above it matches the old edit to 6e-7 (no pose) and 6e-6 (0.3 m step)
  `[verified-numerically 2026-10-14, n=1 matrix]`. Clip z (column 2) is never changed, and clip w (column 3) is
  unchanged for a step. For a yaw, w changes, as a real turn has to.
- **K·M** changes row 2 (how the object's own z feeds the screen): off by 0.29 to 3.0, and w moves by up to 1.4.
- **M·Kᵀ** writes x into clip z: the depth is wrecked (errors of 1,800 to 18,000).
- **Kᵀ·M** changes row 0: off by 0.27 to 2.8.
So **mode 0 (M·K, today's code) is the only correct one**. Modes 1 to 3 should break even real geometry.

The old edit in matrix terms is W·V·T(d)·P, for any P whose row 0 is [w,0,0,0]. It needs nothing about depth.
M·K equals it only when column 2 is [0,0,0,n].

Small side finding: the projection is not exactly the assumed reversed-Z infinite far. Column 2 = A·forward +
[0,0,0,B] with A ≈ −2.2e-6 and B ≈ 0.1013, so the true n is 0.1013, not vp[14] = 0.1112. That makes the head-pose
eye shift about 9 % small. It cannot break the picture. `[verified-numerically 2026-10-14, n=1]`

## 2. Does M·K change clip z or w?

z: never (K's column 2 is always [0,0,1,0]). w: not for a step, only for rotation (correct). So on real matrices
M·K cannot wreck depth: the black ground does not come from the camera maths. `[inferred-static]` + numbers above.

## 3. What does break: non-matrix data takes the edit

- The per-object edit is chosen by **buffer width only** (192, 128, 96, 64; 384 with its switch), at Map/Unmap,
  with no check of which shader stage reads it `[inferred-static]`.
- The bind census shows **pixel-shader** buffers of those widths: `PS-b2:128`, `PS-b2:96`, `PS-b1:96`
  `[measured 2026-10-12]`. Those are material and lighting values, not object→clip matrices.
- `is_flat_matrix` only skips data whose m[3], m[7] and m[11] are all exactly 0. A float4 colour row with alpha
  ≠ 0 passes, so it gets edited `[inferred-static]`.
- The old edit added d·w (0.034) to one float, so it was nearly invisible. M·K does `x += K[8]·z` on every float4
  row (red += K[8]·blue). K[8] = −0.31 even with **no** head pose (the eye shift alone, left eye), and −3.17 for the
  0.3 m step. Test row (0.3, 0.5, 0.8, 1) → (−2.24, 0.5, 0.8, 1) for the step, (0.09, 0.5, 0.8, 0.99) for 2° yaw:
  **red driven to zero or negative = teal / dark blue / black**, which is what Tefa saw
  `[verified-numerically 2026-10-14]` (the cause itself is still `[hypothesis]` until a live run confirms it).
- Since a zero pose (`0 0 0 0 0 0`) still gives K[8] = −0.31, it should break the picture too. That is a cheap
  live check of this reading.

## What to expect from the kmode switch, and the fix

- Mode 0 looks as broken as now; modes 1 to 3 look worse (mode 2 the worst, with depth wrecked).
- Fix: apply K only to buffers that look like a real camera matrix, for example
  `max(|m[2]|,|m[6]|,|m[10]|) < 1e-3` and `m[14]` within ±25 % of the shared n (a real object sits at
  ≈ 0.101 to 0.111). Better still, edit only buffers bound to the vertex shader.
- The same leak means the old one-float edit has been nudging pixel-shader constants all along: possibly the
  "shading changed" seen on 2026-09-08 `[hypothesis]`.
