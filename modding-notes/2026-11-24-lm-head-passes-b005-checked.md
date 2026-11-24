# 2026-11-24 (/lm, Build PC, OpenXR Simulator): the head-passes build b005 checked while driving

The board's row: "head passes, check the fixed build: b005 `13a39611011e`, `head_passes=1`, 3D on, drive straight behind
the car, head yaw ±25: the SSAO count stays 0, 'camera matrices left to the per-object edit' climbs, the car never
flickers; read the SSAO-shaped number."

## Result `[verified-live 2026-11-24, n=1]`

- 3D on (NUMPAD6) with the head at yaw 0 first; drove straight ~28 s on a virtual pad (right trigger 0.55), head set
  to +25, -25, +25, 0 in the simulator during the drive.
- `ssao=0 (lens rescaled 0)` the whole run, no `first SSAO edit` line, no `near miss, SSAO` line: **pass** (no false
  SSAO edit came back).
- `camera matrices left to the per-object edit` climbed 64,538 -> 1,074,085: **pass** (the guard fires).
- `fog` and `decal-rays` climbed at ~60 a second; `PER-OBJECT edited` climbed.
- **`SSAO-shaped 0`** throughout (`filled before this frame's K` 1.4 million): the real SSAO constants are NOT filled
  before the head pose exists. So either they arrive later and the edit refuses them, or SSAO is not drawing; SSAO=1
  is set in settings.ini. Next step for the SSAO half is a draw-time look, not an early fill.
- The car was whole in all three head-turned pictures (two of them while driving). Flicker is judged by eye over time;
  three stills are not a video, so "never flickers" is n=3 stills, not proven.
- At ±25 the revealed edge (the game's own view not reaching that far) showed as expected, with no `eye_hfov` set.

## The Build PC's Mad Max setup (it had none)

- The September add-on had been cleared on 2026-11-14; b005 restored by `builds.py` (which first wrote into the dev
  PC's path, a fault now on FAULTS.md; this PC got `builds_app.mad-max-vr` in lanes.conf).
- No settings.ini existed, so the game started fullscreen at the desktop size. The exe's own command-line help (the
  reader found it): `MadMax.exe /windowed /widthW=1280 /heightW=720 /motionblur=0` gave a 1280x720 window. With a
  small settings.ini in place (Music=0, the VR screen-effect zeros, SSAO=1), the game wrote out its full settings.ini
  at a clean close, keeping all of them: from now on a plain start is windowed and the music is off.
