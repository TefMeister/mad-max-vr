# 2026-10-11 — `/pd` (dev PC): the car's ground shadow is probably an AO box, and the fix is built

**The game was not launched, and nothing here has been run in it.**

## The question

The `/lm` run earlier today measured the car moving -22 px with the eye and the car's shadow on the sand only -1 px.
Moving the sun pass's camera origin (both signs) changed nothing. What draws that shadow?

## What the shader bundle says `[inferred-static 2026-10-11]`

The game draws **ambient-occlusion boxes**: vertex shader `aobox` (#4), pixel shader `aosphere` (#341). The pairing is
read from the names and the matching interface (the VS's `TEXCOORD0.xyz` is the PS's only input); that one sits under
the car is the hypothesis this note tests.

- **`aobox` VS** scales a unit box (`cbInstanceConsts` b1 slot 4), places it in the world (b1 slots 0..3), then projects
  it with the **shared** viewProj (`GlobalConstants` b0 slots 0..3) — not with a per-object object→clip matrix. It hands
  the pixel shader `(0.5x + 0.5w, -0.5y + 0.5w) * b1[5].xy` and `w`.
- **`aosphere` PS** divides by `w` to get the screen position `(u, v)`, samples the depth buffer, and rebuilds the
  pixel's position in the box's own space with one 4×4 held in its own 80-byte `cbInstanceConsts` (PS b1):
  `local = (u*c1 + v*c2 + depth*c3 + c4).xyz / .w`, then `ao = c0.y * pow(min(|local|, 1), c0.x) + c0.z`, written to
  the third G-buffer target.
- That 4×4 is built by the game from the **unshifted** camera. The per-object edit moves the car and the sand on screen,
  but this matrix still reads each pixel as the unshifted camera saw it, so the darkening lands where the car WAS.
  That matches the measured -1 px exactly, and it explains why the sun-origin edit did nothing.
- For contrast, the sun pass's 80-byte buffer (`deferred_sunlight` VS b1) builds view rays and never reads its third
  row. Under a pure sideways eye shift the rays need no change, which is why only the sun's origin was edited.

## The fix `[compile-verified 2026-10-11]`, `[verified-numerically 2026-10-11]` in a model

The per-object edit is a pure sideways eye move: `V' = V` with `V[3][0] += d*w`. The game wrote `P = S⁻¹ V⁻¹ L` (S: clip
row → `(u, v, depth, 1)`, from the VS above; L: world → box). The right matrix for the shifted eye is
`P' = S⁻¹ V'⁻¹ L = S⁻¹ V'⁻¹ V S P`, so it needs only this frame's shared viewProj and the same `d*w`.

- New file `staging/mad-max-vr/proxy-dxgi/src/cbfp_ao.c`; switch file **`madmax_vr_ao.txt`**; off without it.
- It refuses any 80-byte buffer whose `L = V S P` is not rank 4 and affine (a box transform has a constant w), so the
  sun's ray builder and buffers from other cameras are left untouched. Any other screen-space decal built the same way
  passes, and the same correction is right for it.
- The proxy now keeps the main pass's shared viewProj (before the shared edit) for this.
- Self-test 79/79 (8 new): in an independent model camera + box, the unedited matrix puts the shadow 0.26 box
  half-sizes off; the edited one 0.000012. Refusals proven for a no-depth-row buffer and for another camera.
- Build reproducible (`e6d84ac9ccd6`, 262,144 B, built twice). Deployed; previous build kept as
  `dxgi.dll.bak-2026-10-11-pd-pre-ao` beside the exe; stamped.

## What is NOT established

- That the dark shape by the car is this AO box rather than the sun's shadow map `[hypothesis]`; the sun edit's failure
  points here, nothing proves it.
- That the box's raster (still drawn with the unshifted shared viewProj in PER-OBJECT mode) covers the shifted pixels;
  BOTH mode moves the raster too.
- That the aobox VS's viewport scale (VS b1 slot 5) is 1. The shape test assumes it; if it is not, every buffer is
  refused and the log's "last shape ratio" says so.

## The next run (`[FLAT]`, one launch)

Same scene as 2026-10-11 (Resume Game, the car in the desert, single-eye, separation 0.6054). Measure the shadow's
shift with and without `madmax_vr_ao.txt`, and read the log's `AO BOX` line.

| result | means |
| --- | --- |
| `edited` > 0 and the shadow now shifts like the sand (about -24 px) | ✅ fixed: it was the AO box |
| `edited` > 0, the shadow follows but its edge is cut off | the raster: repeat in BOTH mode |
| `edited` > 0, shadow still -1 px | the dark shape is not the AO box: back to the sun's shadow map |
| `edited` = 0, `refused` high | the shape test rejects it: read "last shape ratio" (viewport scale ≠ 1?) |
| `edited` = 0, `no camera` high | the AO buffers are filled before the main pass's shared write in the frame |
