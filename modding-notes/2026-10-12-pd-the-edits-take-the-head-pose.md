# 2026-10-12 (dev PC, `/pd`, no game launch): the four edits take the head pose

**The game was not launched; nothing here has been run in it.** Design: `2026-10-12-pd-the-road-to-the-headset.md` §3;
the maths: `2026-10-12-pd-the-head-pose-matrix.md`.

## What changed

- Each frame, at the main-pass latch, `headk_prepare` builds this frame's `K` from the matrix as the game wrote it,
  and the eye's world offset. **Only while a head pose is set**; otherwise every edit takes its old one-float path.
- Per-object and shared: `M·K` instead of `M[3][0] += d·w`.
- Previous frame (`prev_edit_k`): last frame's matrix takes the same `K`; its "same object?" test now uses the
  game's own copy of the current matrix (K mixes the columns that test reads; the one-float edit never did).
- Ground motion (`mvo_edit_k`): `V·K` and `Vprev·K` in the reprojection.
- Sun / shadow (`sun_eye_offset`): the eye's world offset from `K`'s transform (same sign switch as before).
- AO box: untouched (ruled out as the shadow, off).
- **A head pose for testing on the monitor:** `madmax_vr_look.txt` next to the exe, `yaw pitch roll x y z`
  (degrees, metres; OpenXR: + yaw = turned left, + pitch = up), read about once a second. The headset bridge will
  set the pose the same way later.

## Verified

- Self-test section 16 (11 checks; 149 in the suite every build runs) `[verified-numerically 2026-10-12]`: no pose =
  no K, and K lasts one frame; no head movement gives the old eye world offset, a head step 10 cm right moves the eye
  10 cm along the camera's right; with a turned, tilted head the previous-frame matrix becomes `W2·V2·E·P` and the
  ground reprojection `S⁻¹(V·K)⁻¹(Vprev·K)S`, both built directly; with no K or a pure-shift K both are the old edits.
- Planted mistakes (eye offset sign, K multiplied on the wrong side) fail four checks.
- All earlier sections still pass, so the old path is unchanged `[compile-verified 2026-10-12]`.
- Installed `dxgi.dll` `fcc053b4355e` (was `cb1439f5545e`, kept on E:); a rebuild gives the same hash.

## Next live test (`/lm`, still camera, then a short drive)

3D on (NUMPAD6), wiggle off (NUMPAD7 to one eye), then write `15 0 0 0 0 0` into `madmax_vr_look.txt`:
- the view turns LEFT 15° and holds; the car stays sharp, its shadow stays under it, the ground does not smear;
- turns right: the mirror is wrong for this game after all;
- the shadow slides or the ground smears: the sun or ground edit is off; the log counters say which;
- nothing turns, the log shows `head pose ON`: the edits are not taking `K` (check the `cbfp stereo frame=` lines).
Then `0 10 0 0 0 0` (look up) and `0 0 0 0.3 0 0` (step right). Delete the file after.

## Not established

That every pass `K` reaches has the assumed `P`; the reversed-Z reading of `n`; how the game's own culling copes
with a turned view (objects at the edge may pop).
