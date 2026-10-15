# 2026-10-15 (late evening, dev PC, `/lm`, unattended, one reader): driving with the head turned, and the eye-lens fix

Three launches through Steam, all in the OpenXR simulator, 3D on (NUMPAD6, separation 0.065). Evidence:
`dev-archive/recon/2026-10-15-driving-head-turned-eye-lens/`.

## 1. Driving with the head turned shows the ground missing on the turned side

- Build `2a5ce5e5eda5`. Driven with a ViGEm virtual pad (right trigger, left stick), because W/A/S/D also move the
  simulator's own head and the arrow keys do not drive the car `[verified-live 2026-10-15]`.
- Head yaw +20 (left), driving straight: a blue strip on the left where the ground should be. Head yaw -20 (right),
  driving and turning: large blue areas and dark, hard-edged shadow slabs on the right, in the game window and both
  eyes `[verified-live 2026-10-15, n=1 each]`.
- Head straight while driving: clean `[verified-live 2026-10-15, n=1]`. The car's shadow stays under the car; no fog
  or cloud-shadow fault was visible.
- So the revealed edge is THE fault of head-turned driving, and it is much bigger while moving than standing.

## 2. The cockpit while driving, at real eye spacing

- Wheel, hands and dashboard sharp in both eyes while driving; the near A-pillar shows the parallax expected at
  0.065; a 30 degree head turn looks out of the side window `[verified-live 2026-10-15, n=1]`. Comfort is not
  judged (the simulator has no real head).
- On the way, the car rolled down a cliff and ended upside down: the game's physics, not the mod.

## 3. The eye-lens fix: the gap goes away inside the covered range (build `eb6f5ccee224`)

- The reader's fix (`[xr] eye_hfov=N`, default 0 = off) shows the eye an N-degree lens inside a wider game view, so
  the game decides what to draw for its wide view while the eye sees only the middle.
- Game view widened through Capture Mode -> Video Mode -> CAMERA SETTINGS -> FIELD OF VIEW to maximum -> BEGIN
  SESSION -> CONTINUE (route and click points in `ai-game-control-profiles/routes/mad-max/KNOWN.md`). It reached
  **116.9 degrees, not the 157.4 of 2026-09-08** (`shared_w=0.61383`) `[measured 2026-10-15, n=1]`.
- With `eye_hfov=80` the log said `head turns up to about 18 deg sideways stay inside what the game drew`.
  - Head yaw 15, standing: the ground whole. Head yaw -15, driving and turning: the ground whole.
  - Head yaw 30, beyond the 18 covered: the blue gap back on the turned side.
  `[verified-live 2026-10-15, n=1 each]`
- So the gap is the game culling to its own view, and the fix removes it as far as the game's view reaches
  `[verified-live 2026-10-15, n=1]`. Not run: a yaw-15 control with the fix off in the same launch (the gap showed at
  yaw 20 without the fix earlier the same evening).
- In the capture session the whole picture was very bright and hazy, with and without the fix; most likely the
  capture session's own look `[hypothesis]`.
- Installed now with `eye_hfov` off: ordinary play runs at 80.5 degrees, which leaves an 80-degree eye no room.
- Next: make the game draw wider by itself (write its field of view from the mod), so the fix works in ordinary
  play and covers about 38 degrees at 157.

## 4. The jitter recorder can read Mad Max now

- The reader added the camera line (`[xr] jitter_camera`, default on; needs the 3D and `head_tracking=1`) and
  labels the log with the runtime's own name: `OpenXR Simulator Runtime` -> `openxr-openxr-simulator-runtime`.
- A 40 s slow simulator sweep (yaw +-20 at 0.1 Hz), standing and driving: 36.3 camera writes a second against 57.6
  pictures over a run that included menus; **jitter in 2 of 53 turning seconds**, the rest smooth
  `[measured 2026-10-15, n=1 run]`. Its stated cause for the 2 seconds: the camera written but unchanged on some
  pictures. Simulator only: says nothing yet about a real headset.

## 5. The reader's audit: which edits never ran before the draw hooks

- Only the edits keyed on the bound shader (all added on 2026-10-15) were dead before `2a5ce5e5eda5`. Everything
  keyed on buffer shape ran all along and its results stand.
- Correction: with `HQDof=0` and `PostEffects=0` the final picture is the `dof_*` composite; `comp_*` never draws,
  so its edit has never run `[measured 2026-10-15, n=1 run]`.

## 6. Fog, cloud shadows, SSAO and sky follow the head: first live look (build `b738e5972428`)

- The reader's `[xr] head_passes=1` turns these full-screen passes with the head (and with the eye lens). One launch,
  head yaw 25, standing: fog edited about 60 times a second, decal rays the same; cloud shadows, SSAO and sky 0 (the
  build's own check refused them). The picture looked normal: nothing visibly wrong, nothing visibly fixed
  `[verified-live 2026-10-15, n=1]`.
- Fog, decal rays and the older sun-origin edit all counted exactly 1,903: possibly one buffer counted, or edited,
  three times `[hypothesis]`. Sent back to the reader with the zero counts.
- Installed with `head_passes=1` (the dev build stays on).
- A diagnostic build (`fb4917c774f5`) explained it: the three counts are three different buffers. The skipped sky
  and SSAO candidates were per-object data, and 8 SSAO edits were false (possibly the car's own buffer). The reader's
  fix (`13a39611011e`, builds b005) leaves those to the per-object edit; installed, not yet run.

## Recorded

- `drive-head-turned_2026-10-15_18-14-45.mp4`, `cockpit-driving_2026-10-15_18-21-11.mp4`,
  `jitter-camera-line_2026-10-15_18-34-24.mp4`, `eye-lens-fix_2026-10-15_18-42-33.mp4`, `head-passes_2026-10-15_18-52-34.mp4`, `head-passes-diagnostics_2026-10-15_19-05-46.mp4` (the game window only), MEGA
  `Videos\mad-max-vr`.

## Not established

- Why Video Mode reached 157 on 2026-09-08 and 117 today.
- Whether fog, SSAO and other lights look right with the eye lens on (the reader predicts them off by the lens
  ratio; its next build addresses it).
- Anything about comfort or a real headset.

## Automation

Self-launch ✅ (Steam), menu to gameplay ✅ (RESUME GAME checked by pixel colour first), commands ✅ (numpad 3D,
Capture Mode route by clicks), character and camera ✅ (virtual pad driving, simulator head pose and sweep),
self-close ✅ (window close).
