# 2026-10-15 (`/lm` reader, static only): the other full-screen passes, the true n, the cockpit near blur

Source: `Shaders_F.shader_bundle`, every blob disassembled with
`dev-archive/recon/2026-10-11-pd-the-ao-box-under-the-car/bundle-named-disasm.py` (bundle index numbers below);
live log lines quoted are from the driver's runs of 2026-10-15. Nothing launched or attached by the reader.

## 1. The true n is 0.1000, and why vp[14] drifts `[verified-numerically 2026-10-15, n=1 matrix]`

The projection is reversed-Z with a finite far plane: P's column 2 is `[0, 0, A, n]`, so V·P's column 2 =
A·(column 3) + `[0, 0, 0, n]`, and `vp[14] = A·vp[15] + n` moves with the camera's position. On the live matrix of
2026-10-14 the fit (column 2 projected on the forward) gives A = -2.503e-6 (far plane about 40 km) and n = 0.10000,
a 0.1 near plane. The 0.1013 in the 2026-10-14 note took A from one row only.
Supersedes: the "true n about 0.1013" figure in `modding-notes/2026-10-14-lm-the-head-pose-turns-the-world.md` §2.

In staging (`3ceaa3e`): `headk_read_proj` uses the fitted n; `headk_is_camera` takes A out too (column 2 - A·column 3,
`m[14] - A·m[15]`), so objects past about 10 km (whose `m[14]` fell outside the 25% slack) now take K instead of the
one-float edit. K itself still uses `P` with A = 0 (keeps `K⁻¹` free of z mixing for `cbfp_ray.c`); the cost is a
depth error for far objects under a turn, about 25% of the (tiny) depth value at 20 km `[inferred-static]`.
`madmax_vr_kmode.txt` removed. Self-test section 15b, 165/165, dxgi.dll `32a0e6c852fb` `[compile-verified 2026-10-15]`.
Not deployed.

## 2. Full-screen passes that rebuild positions, ranked by picture coverage `[inferred-static]`

Notation: rows are float4 rows of the named buffer; "world = s·R" means `(u, v, depth, 1)` times four rows, then
divide by w, gives a world position; "caught" = the `cbfp_ray.c` shape test (c4 ray and divide vector both within
0.995 of forward, floats 4..19, 80..384-byte buffers chosen by width).

| rank | pass (bundle #) | what it reads | caught? |
| --- | --- | --- | --- |
| 1 | volumetric fog / sun shafts `fogvolumeapply*` PS (#402-413, VS #35 passes only uv) | PS b1 `cbConstants` (272-352 declared; runtime likely 384): rows 12-15 = world = s·R; rows 4-7, 8-11 = world→shadow cascades (no camera); row 16 params; then `- GlobalConstants[4]` (camera position) | no (floats 4..19 are rows 1-4: params and a shadow row) |
| 2 | cloud shadows `cloudshadow` PS (#362) | PS b1 `cbConsts` 96 bytes: rows 1-4 = world = s·R; row 0, row 5 params; `- GlobalConstants[4]` | no (row 4 is the depth-0, i.e. infinitely far, corner point, not a forward ray) |
| 3 | sky and fog dome `skybox` VS (#115, 64 B), `skygradientshader` VS (#117, 80 B `$Globals`), `foggradientshader` VS (#113, 96 B) | geometry with an object→clip 4x4, columns x, y, w only; clip z forced to 0 | per-object path only; column 2 is unread, so whether `headk_is_camera` passes depends on what the game leaves there. 80 is not a per-object width: the sky gradient may get no edit at all |
| 4 | HBAO+ `ssao_nvidia` PS (#481) | PS b1 128 B: rows 4-6 (xyz) = world→view rotation for the G-buffer normals; rows 0-3 depth/projection numbers (rotation-free) | no |
| 5 | deferred point / spot / area lights VS (#26, #27, #25) + PS (#1273-1289) | VS b2 `cbTypeConsts` (80 B declared): the SAME rows as the sun (ray = (x·c1 + y·c2 + w·c4).xyz/.w · c0.x); PS divides by `depth·c2[0].x + c2[0].y` | yes: selection is by width, not slot, so these take the sun-ray edit if they have the shape |
| 6 | screen-space decals `ssdecal` VS (#91) | VS b2 `cbTypeConsts`: ray rows 0, 1, 3 and scale at row 4.x (a different order) | no |
| - | `depthoffield` VS (#30) | the sun-ray layout | yes if shaped, but DoF should be off |

Edits each needs:
- **Fog (rows 12-15) and cloud shadows (rows 1-4), one shared edit:** `R' = R·Q`, `Q = VP·K⁻¹·VP⁻¹` (a world→world
  move, independent of how the screen is parameterised). Shape test: `R·VP` is, up to scale, a pure screen mapping
  (u feeds only clip x, v only clip y, depth only clip z; w only from the constant row). Head position offsets also
  need `GlobalConstants[4]` moved by the eye's world offset (as the sun origin edit does).
- **Sky / fog dome:** let `headk_is_camera` accept a matrix whose column 2 is all zero when columns 0, 1, 3 match the
  shared camera's axes; `M·K` is then right for a turn (K's row 2 is `[0,0,1,0]` for a rotation) and leaves clip z at 0.
  Add 80 to the widths offered if the sky gradient's runtime width is 80.
- **HBAO+:** rows 4-6 ← rows 4-6 · (head rotation in view axes). Shape test: rows 4-6 orthonormal and equal to the
  shared camera's axes (columns 0, 1 of V·P over w, h, column 3).
- **Decals:** `ray_edit_k` with the row order (0, 1, 3) and scale row 4.
- Side risk `[hypothesis]`: 96 and 128 are per-object widths, so the old one-float edit may already add d·w to
  row 3.x of the cloud-shadow buffer (its depth row) and of the HBAO buffer (row 3.x unread there, harmless).

## 3. The cockpit near blur that survives HQDof=0 `[inferred-static]`

- HQDof picks between two families of the final post-process shader (240-byte PS b1 `cbConsts`, 24 variants
  each): `dofbokeh_*` (#554-577) and `dof_*` (#578-601). Only `dof_*` carries the cheap depth blur, so HQDof=0 most
  likely SWITCHES the near blur to it rather than removing it.
- In `dof_*` the picture is blended toward `BlurredSceneTexture` by `min(3·b, 1)`, where
  `b = sat(c0.w·(1 + r²·c12.z) + c2.y·sat(linear_depth·c4.z + c4.w) + c0.z)`, `linear_depth = depth·c2.z + c2.w`.
  Near objects (cockpit roof, wheel, hands) get `b` near 1 from the `c2.y` term.
- To neutralise: zero **c2.y** (row 2, .y: the depth-blur weight) and, for VR, **c0.z, c0.w** (constant and radial
  edge blur) in that buffer. Do NOT touch c2.x (scene brightness) or c2.z/w. The buffer is hard to tell by content,
  so the safer route is by shader: recognise the `dof_*` pixel shaders at CreatePixelShader by their DXBC checksum
  (bytes 4-19 of the blob) and either swap in a patched copy (the literal 1.0 in `min r0.x, r0.x, l(1.0)` → 0.0, then
  recompute the DXBC checksum) or, while one is bound, zero those three floats in a private copy of the buffer.
- `extractneardof` (#399, 32-byte `cbConsts`, c0.x = strength) and `blurdof` (#345) build a near mask that the
  `dof_*` composite does not sample; they likely belong to the bokeh path.

## 4. Culling (low priority) `[hypothesis]`

Missing terrain at the edge a turn reveals, and a shadow with no caster, fit CPU culling against the unturned camera.
The proxy only sees GPU constants. Cheapest lever: make the game render a WIDER field of view than the eye needs
(its own FOV value, read off `shared_w`) and fold the narrowing back into K (`P_eye⁻¹`·E·`P_game`), so culling has a
margin for the head turn. Finding the frustum planes in memory (six planes = sums/differences of V·P's columns,
normalised) is an `/lm` memory-scan job.
