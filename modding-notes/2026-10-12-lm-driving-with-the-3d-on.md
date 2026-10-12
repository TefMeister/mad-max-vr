# 2026-10-12 (afternoon) — driving with the 3D on

`/lm`, dev PC, two launches, unattended, one reader. Build `0ab2a6496cb7`, switch files sun/prev/mvo, `MotionBlur=1`
for the run, single eye (left). Evidence: `dev-archive/recon/2026-10-12-driving-with-the-3d-on/`. Video (game window
only): `E:\OBS gameplay videos\mad-max-vr\driving_2026-10-12_13-13-39.mp4`.

## 1. Driving straight and turning `[verified-live 2026-10-12, n=1 per row, judged by eye]`

| run (3 s of W, shots each second) | what it looked like |
| --- | --- |
| 3D off | the game's own motion blur on the ground while moving |
| 3D on, ground fix off | the ground and the car smear far more than with 3D off |
| 3D on, all fixes on | like 3D off: car sharp, ground with normal motion blur |
| turn (W+A), 3D off and on | both blur strongly while the camera swings; no difference seen |

The car's shadow stayed under the car in every 3D-on frame, straight and turning. A sharpness statistic was tried and
rejected: each drive covers different ground, so the numbers jump far more than the effect.

⚠️ One turn ended in a grey, washed-out picture: that was the game's death fade (Max died in the crash, Game Over
screen right after), not our edit. CONTINUE reloaded the checkpoint.

## 2. The cockpit view (`V`) with the 3D on `[verified-live 2026-10-12, n=1]`

- With the test separation (0.6054, ten times real eyes) the eye moves 30 cm sideways, into the car's door frame:
  the roof and the wheel vanish behind a blurred pillar. Not a bug: the wide test spacing.
- With a real spacing (0.065) the cockpit works: left eye, no shift, right eye all show the wheel and the pillar from
  slightly different places, the far hills unmoved.
- The cockpit has a strong built-in depth-of-field blur on near things (roof, wheel, hands). That will need turning
  off for a headset `[hypothesis: it is the game's DoF setting]`.

## 3. The field of view, read from the log `[measured 2026-10-12, n=3 launches]`

The reader found it: `shared_w=` in the `cbfp stereo frame=` line (printed only with the 3D on, every 300 frames);
hfov = 2·atan(1/shared_w).

- Chase camera, standing: **86.70°** on all three launches today (`1.05936`), so the FOV is stable across relaunches.
  The 157-161° wide FOV of September is not present; whether a setting changed since is not known.
- Chase camera while driving: occasional wider samples, 90-97° (`0.9975`, `0.9743`, `0.9025`, `0.8835`): the game
  widens the view with speed `[measured, sparse samples]`.
- Cockpit (`V`): a steady **102.43°** (`0.80366`), standing and driving alike; no speed widening seen there.

## 4. The reader's tidy-up, verified in the game `[verified-live 2026-10-12, n=1]`

Move-only split of `hk_Unmap`, `end_frame` and the self-test, plus one shared copy of the matrix helpers
(`cbfp_clipmat.c`). Self-test output byte-identical (125/125), exports identical; new hash `cb1439f5545e` (smaller:
duplicate code removed). Live: car -22 / shadow -23 (sun off: -19 / -1), all three edits counting. Merged to staging
main `9ac22ce`; backup tag `pre-split-2026-10-12`.

## 5. Not done

- Cockpit while driving at real spacing: only standing still was checked at 0.065.

## Installed now

`dxgi.dll` `cb1439f5545e` (the split, behaviour unchanged), switch files sun/prev/mvo; `settings.ini` back to `MotionBlur=0`, `Music=0`.
Stamped.

## Automation

Self-launch ✅, menu → gameplay ✅ (RESUME verified; a second Enter needed at the title once), commands ✅, character +
camera ✅ (driving straight, reversing, turning, braking, cockpit toggle), recovery from Game Over ✅ (CONTINUE),
self-close ✅ x2 (WM_CLOSE). ⚠️ Once the title screen had already passed when the first Enter arrived; it landed on the main menu's default RESUME GAME. Always screenshot before Enter.
