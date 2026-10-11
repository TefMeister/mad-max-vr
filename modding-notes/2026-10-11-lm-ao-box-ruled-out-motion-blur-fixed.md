# 2026-10-11 evening — the AO box is ruled out; the previous-frame edit keeps motion blur sharp

`/lm`, dev PC, three launches, unattended, one reader. Same scene as the afternoon (Resume Game, the car in the desert,
single-eye, separation 0.6054). Evidence: `dev-archive/recon/2026-10-11-the-shadow-is-not-the-ao-box/`. Videos (game
window only) in `E:\OBS gameplay videos\mad-max-vr\` (`ao-box-fix`, `ao-box-fix-2`, `motion-blur-prev-frame`), copied
to the MEGA transfer folder.

## 1. The car's shadow is not the AO box

- The `/pd` AO-box fix edited nothing at first: the only 80-byte buffer is bound at PS b4, not PS b1.
- Widened to 96/128-byte buffers (a shape test decides, and the rest fall through to the normal edit): about 90,000
  edits per 5 s, the inside of the car slightly darker, **the ground shadow still at -1 px** while the car moves -21.
- So the sun's shadow map is the remaining suspect. Lead for the next no-game session: whether the sun pass fills its
  624-byte constants by `Map` (which the afternoon's sun edit touched) or by `UpdateSubresource` (which it did not).

## 2. Motion blur stays sharp with the previous-frame edit

The reader found the previous frame's matrices (128-byte slots 4..7, 192-byte slots 5..8) and built the same eye shift
for them (`madmax_vr_prev.txt`). Live with `MotionBlur=1`: the car smeared without it and was sharp with it
(sharpness 85 → 307; 246 with the 3D off); the crate wall 46 → 174. The near sand stayed blurred (3; 57 off), so the
ground has its own previous-frame source. Motion blur set back to off afterwards.

## Installed now

`dxgi.dll` `028dd80f3f14`; `settings.ini` `Music=0`, `MotionBlur=0`, `SSAO=1`; no switch files. Stamped.

## Automation

Self-launch ✅, menu → gameplay ✅, character + camera not needed, self-close ✅ (WM_CLOSE), three times.
