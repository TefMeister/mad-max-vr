# 2026-10-12 (dev PC, `/pd`, no game launch): the head-pose matrix is built and tested

**The game was not launched; nothing new is wired into the game yet.** Design:
`2026-10-12-pd-the-road-to-the-headset.md` §2.

- `staging/mad-max-vr/proxy-dxgi/src/cbfp_headk.c`: reads `w, h, n` off the shared `V·P`, builds `K = P⁻¹·E·P`,
  applies `M·K`, and turns an OpenXR head pose (recentred heading, optional position, plus the eye shift `d`) into
  the view-space `E` (OpenXR z back, mirrored to this view's z forward).
- Self-test section 15 (13 checks, in the suite every build runs; 138 in all) `[verified-numerically 2026-10-12]`:
  `w, h, n` come back from `V·P`; `K` for a pure eye shift equals the shipped one-float edit on 8 objects; `M·K`
  equals `W·V·E·P` built directly for 400 random turns and offsets; a head turned left 30° centres a point 30° left,
  likewise up, a step right, a step back, position off; recentring leaves only the look-up; without the z mirror the
  turn goes the wrong way.
- The checks can fail: a copy with `P⁻¹` planted wrong fails b and c.
- The installed `dxgi.dll` is unchanged (nothing calls the new code yet).

Not established: that every pass `K` will touch has this `P` (callers skip orthographic shadow cascades, as today);
the reversed-Z reading of `n`. Next: move the four edits from `d` to `E` (board row).
