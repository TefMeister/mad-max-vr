# 2026-11-27 (/lm, Build PC, OpenXR Simulator): first person on foot and our own controller hands, built; Max found

Tefa: "getting first person to work on mad max with actual 6dof motion controller following hands". Stopped on
Tefa's word ("please stop work on mad max when you can") before the build was seen working in the game.

## Found live

- **Max's world position (his feet)** `[verified-live 2026-11-27, n=3 launches]`: with Max on foot, every float triple
  within 8 m of the main camera (slot 9) was read, Max walked forward, and the triples that moved split into the
  camera's copies and one point 3 m ahead at ground level, held in 67 places. A pointer search from MadMax.exe's image
  found two families of two-step chains `[[exe+s]+o1]+o2`:
  - A: `19cee48 1b8 210`, `19e26b8 1d8 210`, `19e50d0 1c8 210`, `19cee48 1c0 50`, `19e26b8 1e0 50`,
    `19e50d0 1d0 50`, `190d298 7e8 150`, `190d2d0 68 150`;
  - B: `17feb10 c0 550`, `19e54a0 90 7b0`, `1a0b2b0 150 7b0`, `190d290 c8 690`.
  Launch 1 both gave Max; launch 2 B gave Max (also his seated place in the buggy) and A an object ~4.7 km away;
  launch 3 A gave Max and B zeros. So they are two slots of some list of characters, and the mod takes whichever
  point is nearest the camera (within 12 m). Max's body box is about 2.4 m tall with margin: the eye ~1.68 m up.
- Driving the game: direct start with `/windowed /widthW=1280 /heightW=720 /motionblur=0`, Enter at the title, RESUME
  GAME, R out of the buggy (control profile KNOWN.md). One launch landed on the LOAD GAME autosave list by itself
  (F deletes a save there); Esc backed out.

## Built (staging `16b844e` + the candidate fix), all tests pass, NOT seen working in the game

- **First person** (`cbfp_fp.c`, the reader's; `mm_fp_provider.c`): the head-pose term becomes `E = E_fp * E_head`,
  so everything already driven by K (camera, previous-frame, ground motion, sun rays) follows the moved eye.
  `madmax_vr_fp.txt`: `up 1.68`, `level 1`, `hide 0` (`ahead 3` = test without memory). Self-test 286/286.
- **Controller hands** (`xr/mxr_ctl.c`, `xr/mxr_hands.c`, `hands/mmh_*`, the reader's): controllers in the headset
  bridge (grip and aim poses, buttons), Hard Reset's cyborg hand drawn on the bridge's own device into each eye's
  headset picture, fingers by trigger and grip. `madmax_vr.ini [hands] on=1`. Tests: mmh 2395/2395, a D3D11 render
  test 7/7. Live: the hands loaded ("fingers MOVE: 53 named parts, 15 pivots" each), not yet looked at.

## What happened live

- First person switched on, but every frame was refused: on that launch the chosen chains read zeros and the mod
  saw a point ~7 km away. That led to the two-family finding above and the nearest-to-camera fix (built, 286/286),
  which was not run before the stop.
- Log lines kept: `dev-archive/recon/2026-11-27-first-person-and-hands/log-first-person-lines.txt`.

## Left as it was

The game folder is back on the proven build `13a39611011e` with its own `madmax_vr.ini`; today's extra files sit in
the game folder's `_backup-2026-11-27`.

## Next, in order

1. Install the newest staging build, `madmax_vr_fp.txt` with `up 1.68`, `madmax_vr_sun.txt` on, 3D on, one eye: does
   the eye sit at Max's head on foot? (the log line "eye at the head from mm_fp_head_world: N m").
2. Read the "object origins near the head" counts, try `hide 0.4` to hide Max's own head and body.
3. `[hands] on=1` with the simulator's controllers: hands in both eyes at the controllers.
4. Tefa in the headset.
`MODEL: OPUS`; hiding the body is the step that may need FABLE if it fights back.
