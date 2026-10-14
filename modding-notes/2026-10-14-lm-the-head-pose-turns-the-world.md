# 2026-10-14: the head pose turns the world (`/lm`, dev PC)

`/lm`, dev PC, three launches, unattended, one reader. Still camera, standing by the car, 3D on, left eye only,
separation 0.065. Evidence: `dev-archive/recon/2026-10-14-head-pose-live/`. Video of the game window only:
`E:\OBS gameplay videos\mad-max-vr\headpose_2026-10-14_17-05-35.mp4`.

## 1. First try: every head pose broke the picture `[verified-live 2026-10-14, n=1 per pose]`

Installed `06a59ced1fe8`. With `madmax_vr_look.txt` present, every pose broke the picture: 15° left, a 0.3 m step,
10° up, 2° left, and even `0 0 0 0 0 0`. The ground went black or dark blue, the crates and car got teal outlines,
the HUD turned teal, and the car's shadow became black streaks. Removing the file brought back a clean picture.
With the sun, previous-frame and ground switch files removed, it broke the same way, so the per-object edit on its
own was enough. Only in the 15° frame did the geometry visibly turn left, and it went the right way.

## 2. Why (the reader's analysis, confirmed live)

- The maths is right. For a pure step, `M·K` equals the old `m[12] += d·w` to 6e-6 on a real game matrix. It never
  touches clip z, and it touches clip w only for a turn `[verified-numerically 2026-10-14, n=1 matrix]`.
- The per-object edit is picked by buffer **width** only, so pixel-shader buffers of those widths reach it too
  (`PS-b2:128`, `PS-b2:96`, `PS-b1:96` in the bind census). These hold material and colour values, not matrices.
  The old edit added about 0.03 to one float there, which nobody could see. `M·K` adds `K[8]` times column 2 to
  column 0 on every row, which for a colour means red += -0.31 × blue. That is already true at zero pose, because
  the eye shift alone sets `K[8]`.
- Predicted, then seen live: `0 0 0 0 0 0` still broke the picture (teal crates, washed shadow, bright streaks).
  The logged sample matrices of real objects looked as expected: column 2 rows 0-2 about 1e-6, `m[14]` 0.099-0.100.
- A side finding, not the cause: the true `n` is about 0.1013, not the 0.1112 read from `vp[14]`, so the
  head-pose eye shift is about 9% too small `[verified-numerically 2026-10-14, n=1]`.

## 3. The fix, and what it gives `[verified-live 2026-10-14, n=1 per pose, judged by eye]`

`headk_is_camera()` lets only matrices whose column 2 is about `[0, 0, 0, n]` take `K` (rows 0-2 under 1e-3, `m[14]`
within 25% of `n`). Everything else keeps the old one-float edit, and the previous-frame edit gets `K` only on the
same test. A new log line counts the "not a camera" matrices (about 300,000 every 5 s). Self-test 149/149.
Installed `bd84d87cf463`, staging `63bdc22`, stamped.

| pose | per-object edit only | all four edits on |
| --- | --- | --- |
| none / `0 0 0 0 0 0` | clean | clean |
| 0.3 m step right | clean | not tried |
| 15° left | turns left, car sharp; shadow left behind (sun edit off) | turns left, car sharp, ground fine; the shadow is a wrong-shaped blob beside the car |
| 15° right | not tried | turns right; a wide dark band across the ground |
| 10° up | view goes up; the ground darkens and hazes | the same: ground dark and hazy, shadow gone |

So **the geometry now follows the head**. Lighting, shadow and fog do not follow a turn or a look-up yet. They are
most likely full-screen passes that rebuild positions with the camera matrices the game wrote (the shared
512/3136-byte GlobalConstants), which are not edited on the per-object path `[hypothesis]`.

## 4. Also in this build

`madmax_vr_kmode.txt` (0 = M·K, 1 = K·M, 2 = M·Kᵀ, 3 = Kᵀ·M), a diagnostic switch. The reader showed 0 is the only
right product, so it was never tried live. Take it out at the next `/pd`. On each pose change the build logs `K`,
three edited matrices before and after, the lens (`w h n`) and the shared V·P.

## Not established

- Which full-screen pass rebuilds positions, and from which constants.
- Whether the 25% `n` slack lets through anything that is not a camera (the counter cannot tell).
- Driving with a head pose: not tried.

## Automation

Self-launch ✅, menu to gameplay ✅ (RESUME verified by screenshot each time), commands ✅ (numpad, look file, switch
files live), character and camera ✅ (still camera only today), self-close ✅ (WM_CLOSE, clean "unloading" line,
three times).
