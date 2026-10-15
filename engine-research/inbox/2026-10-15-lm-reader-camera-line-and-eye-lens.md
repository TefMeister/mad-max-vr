# 2026-10-15 /lm reader: the jitter recorder's camera line, and the eye lens inside a wider game view

From the static reader beside the evening `/lm`. Nothing here has been run in the game.

## 1. The camera write is now logged (board row "[PD] log the camera write to the jitter recorder")

- Why the rider saw 0 camera writes: the build called `jl_init`, `jl_vr_on/off`, `jl_pose_q` (mxr.c, headset thread)
  and `jl_present` (mmxr_glue.c), but nothing ever called `jl_camera_*` `[inferred-static 2026-10-15]`.
- Where the head-adjusted camera is decided for a frame: `headk_prepare` (cbfp_headk.c), called from
  `unmap_shared_512` (cbfp_hooks.c) on the main-pass latch of the shared 512-byte V*P buffer, with the 3D on. The K it
  builds is multiplied into that same mapped buffer a few lines later, and every other K edit that frame reads it
  through `headk_this_frame()` `[inferred-static 2026-10-15]`.
- The fix: `headk_prepare` calls a listener (`g_headk_on_camera`) whenever a HEADSET pose becomes the frame's camera;
  the glue points it at `jl_camera_q` with the raw pose, the same convention as the recorder's pose lines, so the
  checker's lag and pose-age tests compare like with like. A second latch in the same frame with the same pose is not
  logged again; one with a newer pose is (that would be a real second camera write, and worth seeing).
  `madmax_vr.ini [xr] jitter_camera=0` turns it off; default 1. Build `dxgi.dll` `f0ab11f06dfc`, staging `e1855af`,
  self-test 230/230 `[compile-verified 2026-10-15]`.
- Camera lines appear ONLY with the 3D on (NUMPAD6) and `head_tracking=1`: without those the camera does not follow
  the head at all, so "0 camera writes" in such a run is the true answer, not a recorder fault `[inferred-static]`.
- Not yet known: how many main-pass latches a frame has. If the rider shows about 2 camera writes per picture, there
  are two latches with different poses in one frame, which would itself be a jitter source `[hypothesis]`.

## 2. The revealed edge on a turn: an eye lens narrower than the game's view (board row "[PD] the revealed edge")

- Reading: the empty strip at the bottom left on a 30 degree simulator yaw is terrain the game culled on the CPU to
  its own unturned frustum (hfov 80.5); the sky dome is never culled, which is why the strip is below the horizon
  `[hypothesis]`. The alternatives: GPU occlusion culling from the unturned depth, or a terrain draw that does not
  take K. The observation that separates them is the test below.
- The narrowing folds into K as `K = Pg^-1 * E * Pe` (the game's lens undone, the eye's lens put on). The GPU then
  draws only the eye's view, at full resolution; the game's wide frustum is used only for its culling. K's column 2
  stays (0, 0, 1, 0) and column 3 of Pe is (0, 0, 1, 0) for any lens, so the sun-ray edit's conditions hold
  unchanged `[compile-verified 2026-10-15]`.
- Built behind `madmax_vr.ini [xr] eye_hfov=N` (whole degrees, 20..170; default 0 = byte-for-byte the old K, checked
  by the self-test). It only ever narrows. The headset is told the eye's lens. The log line `cbfp headk: eye lens hfov
  ... head turns up to about X deg` says how far a turn can go. Build `dxgi.dll` `1eff407592d4`, staging `7306c5c`,
  self-test 236/236 `[compile-verified 2026-10-15]`.
- Where the game's view is widened: today only by hand, the dossier section 9c route (Capture Mode -> Video Mode ->
  FIELD OF VIEW up -> Enter), which persists into gameplay. A 30 degree turn with an 80 degree eye needs a game hfov
  of at least 140; the slider's maximum (about 157) covers about 38 degrees. Later, a proxy write of the game's FOV
  value: an exact-value scan is now practical, since each frame's hfov is known from the shared matrix
  (`2*atan(1/|col 0|)`), so the scan can look for that exact number in degrees, radians, half-angle or focal form and
  intersect over two slider positions (much tighter than the 2026-08-25 "any changed float" scan) `[hypothesis]`.
- Expected costs: more objects drawn (CPU and GPU time), and level-of-detail may drop because the game thinks
  objects look smaller. The speed-based FOV change no longer reaches the eye (fixed eye lens), which may be a comfort
  gain. Full-screen passes that rebuild positions from the game's own projection (fog, SSAO, other lights; board row
  13) will be off by the lens ratio even with the head still, as they are today off by the head turn; the same
  `Q = VP*K^-1*VP^-1` fix covers both. Per-object matrices that fail `headk_is_camera` keep the old one-float edit and
  would now look mis-scaled, so watch `g_headk_not_camera` `[inferred-static 2026-10-15]`.
- The alternative long-term route: turn the game's own camera by the head's yaw so its culling follows, leaving K
  only the remainder. Needs the game's camera object found live (the exe is packed); not attempted.
