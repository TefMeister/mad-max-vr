# 2026-10-15 /lm reader: fog, cloud shadows, SSAO, the sky and decal rays follow the head (`[xr] head_passes`)

Static work beside the evening `/lm`. The game was not run. The shader readings come from `fxc -dumpbin` of the
shipped `Shaders_F.shader_bundle`, extracted locally with
`dev-archive/recon/2026-10-15-pd-dof-composite/extract.py`. Nothing extracted is committed.

Build `dxgi.dll` `b738e5972428`, staging `15bc2b9`, self-test 267/267, new section 21 `[compile-verified 2026-10-15]`.

## What each pass reads `[inferred-static 2026-10-15]`

- **Fog, all `fogvolumeapply*` variants (12 checked).** PS b1 `cbConstants`, declared 352 bytes. Each pixel's world
  point is `(u*c12 + v*c13 + depth*c14 + c15).xyz / .w`. Here `(u, v)` is the screen uv from `fogvolumeapplyfs`
  (`ndc * (0.5, -0.5) + 0.5`, the same as `CLIP_TO_SCREEN_S`) and depth is the raw depth buffer. The game then
  subtracts GlobalConstants[4], the camera position. So rows 12-15 are `lambda * (V*P*S)^-1` in absolute world
  coordinates. Rows 4-11 are world-space shadow cascades and need no edit.
- **Cloud shadows (`cloudshadow`).** PS b1 `cbConsts`, 96 bytes. Rows 1-4 have the same form as the fog rows, also
  absolute world.
- **SSAO (`ssao_nvidia`).** PS b1, 128 bytes.
  - The camera-space position is `(uv*c2.xy + c2.zw) * z`, where z is the linear depth of the drawn picture, which is
    already the eye's view.
  - G-buffer normals are world-space and are taken into the camera's axes by rows 4-6:
    `n.x*c4 + n.y*c5 + n.z*c6`. After that the shader flips them with (-1, 1, -1).
- **Sky dome.**
  - Shaders: `skybox` (VS b1, 64 bytes), `skygradientshader` (VS b1 `$Globals`, 80 bytes) and `foggradientshader`
    (VS b1, 96 bytes).
  - All three read only columns x, y and w of their 4x4 and force clip z to 0.
- **Screen-space decals (`ssdecal`).**
  - VS b2 `TypeConsts` (80 bytes) has the sun-ray layout with the rows moved: ray rows 0, 1 and 3, row 2 unread, and
    the scale in row 4.
  - The decal box is drawn through VS b1 `InstanceConsts` (144 bytes).
  - Run 4 filled only 176 buffers of 144 bytes in the whole run, and the bind census never shows VS b2 at 80 bytes.
    So screen-space decals did not draw in that open-world scene `[measured 2026-10-15, n=1 run]`.

## The edits

All the edits ride on `hk_Map` / `hk_Unmap`, inside the mapped memory before the game unmaps it. Every fill at these
widths is a Map-discard (fill census, run 4), so no draw hook is needed. Each edit first proves the buffer belongs to
THIS frame's shared camera; anything else is left byte for byte as it was.

- **Fog (rows 12-15, widths 256 to 512) and cloud shadows (rows 1-4, width 96 or 128).**
  - Test: `R * VP * S = lambda * I` within 2%.
  - Edit: `R' = S^-1 * K^-1 * S * R`. This is the dossier's `R*Q`, with `Q = VP * K^-1 * VP^-1`.
  - It is exact for any K, so it also holds with `eye_hfov` on.
- **SSAO (width 128).**
  - Test: rows 4-6 are orthonormal, and `B^T * R3` is a signed permutation, where B is this frame's camera axes taken
    from V*P.
  - Edit: `R3' = (B * E3 * B^T) * R3`, which applies the head's turn in world space.
  - With `eye_hfov` on, `c2` is rescaled to the eye's lens. This only happens when `c2` has the centred shape
    `(2/w, -2/h, -1/w, 1/h)`. Those buffers are counted separately as "lens rescaled".
  - Not done: `c0.x`, which is most likely the AO radius focal factor `[hypothesis]`. With `eye_hfov` on, the AO
    radius may be off by the lens ratio.
- **Sky (widths 64, 80 and 96).**
  - Test: column 2 is empty; columns 0, 1 and 3 are orthogonal, with the shared lens ratios and the shared
    handedness.
  - Edit: `M' = M * Krot`, where Krot is built from the head's ROTATION only. The sky turns but never shifts with the
    eye.
  - Krot's row 2 is (0, 0, 1, 0), so column 2 cannot leak into the columns the shader reads.
  - Before this build the sky matrices failed `headk_is_camera` (their column 2 is empty) and took the one-float edit,
    so the sky did not turn with the head `[inferred-static]`.
- **Decal rays (widths 80 and 96).** The `ray_edit_k` edit, run on a reordered copy.
- **Not built: the decal box.** It is filled about once per decal, so a Map-time edit cannot keep it turned. It needs
  the draw hook: write a K-edited copy before each `ssdecal` draw. Until then, screen-space decals on a turned head
  can only appear inside their unturned screen footprint `[inferred-static]`.

## What to look at live

Settings: `head_passes=1`, the 3D on, `head_tracking=1`. Compare against `head_passes=0`. The proxy log's
`HEAD PASSES` line counts each kind; the first edit of each kind logs its rows before and after.

- **Fog:** turn the head at yaw ±20. With the switch on, the fog's density and distance banding should stay fixed to
  the landscape. With it off, the fog slides with the screen. In run 4, `fogvolumeapplynoise` drew once per frame.
- **Cloud shadows:** look at the moving cloud-shadow patches on the ground while the head turns; they should stay on
  the ground. `cloudshadow` is not in the pass census table, so only the counter shows whether it ran.
- **SSAO:** look at contact darkening under the car, at crate edges and in rock creases. With the switch off, a head
  turn shifts or smears it, or it appears on the wrong faces. With it on, it should stay in the creases. With
  `eye_hfov` on, check that the AO size looks the same as at rest.
- **Sky:** at yaw ±30, the sun disc, the horizon gradient and the clouds should turn with the view. If the sky stays
  glued to the car's heading while the ground turns, the sky test refused: its counter is 0.
- **Decals:** tyre tracks, blood or scorch marks on the ground. They may still clip or vanish on a turn because the
  decal box is not done. The ray counter only shows whether their rays were turned.
- **Counters:** a large `before this frame's camera` count means the game fills these buffers before the main-pass
  camera. Those buffers are then never edited, and the fix would have to move to the draw hook.
