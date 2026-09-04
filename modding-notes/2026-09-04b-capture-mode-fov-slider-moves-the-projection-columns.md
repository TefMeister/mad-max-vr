# 2026-09-04b (`/lm`, dev PC, FULLY AUTONOMOUS) — Capture Mode's FOV slider moves the main-pass projection columns, 58°–117° horizontal; the V driving camera could not be tested because this save has no drivable car

**One launch, one row answered outright, one row blocked by the save, two small extras.** The user
launched the game from Steam and went back to work; Claude drove title → menu → resume → garage,
walked to the car, tried to enter it, went pause → CAPTURE MODE, found the tab switch, swept the
FIELD OF VIEW slider end to end with the probe dumping, exited, pressed the two candidate keys, and
closed the game through its own menus. Windowed 784×561.

Build under test: `staging 4533ec9` rebuilt on this machine (`Mad Max\dxgi.dll` 237,056 B,
`[compile-verified 2026-09-04]`; the previous 02e7d20 build, which had no per-write dump, is kept as
`dxgi.dll.bak-2026-09-04-pre-4533ec9`). Evidence:
`dev-archive/recon/2026-09-04b-devpc-capture-mode-fov-slider/` — filtered proxy log (census lines
stripped, every dump kept), 11 screenshots, the two scripts that drove the slider and decomposed
the dumps, and `fov-decomposition.txt`.

---

## 1. In plain words

Yesterday's home-PC run showed Capture Mode is a free camera that writes the very matrix a VR
patch has to rewrite, but its CAMERA SETTINGS tab could not be reached. Today it was reached — the
tabs are mouse-driven, a click on the label does it — and its FIELD OF VIEW slider turns out to
change **only the two focal-scale columns** of that matrix. The eye position and the forward
vector stay put; the field of view goes from 58° to 117° horizontal. So the engine already has a
live path that widens the projection to headset-like angles, and the decomposition we derived by
hand yesterday predicts the numbers it produces to the degree.

Two things did not happen. The V key (reported first-person driving camera) needs a car, and the
car in this save's garage is a prop you cannot enter — the user confirmed that mid-session — so V
stays *untested*, not disproved. And the FOV does not survive leaving Capture Mode by `Esc`: the
first gameplay dump after exit reads the default again.

## 2. The slider moves the projection, and nothing else `[measured 2026-09-04, n=6 dumps, 5 slider positions]`

Main-pass matrix (the write where slot 4 == slot 9), decomposed as in yesterday's §3a:

| dump | where | \|col 0\| | hfov | \|col 1\| | vfov | eye (slot 9) | \|fwd\| |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | gameplay, garage, first position | 1.1816 | 80.48° | 1.6513 | 62.40° | (−3276.54, 316.02, 6426.46) | 1.0000 |
| 2–5 | Capture Mode, slider untouched, then after bar-click / drag attempts | 1.1816 | 80.48° | 1.6513 | 62.40° | (−3216.80, 314.30, 6416.54) | 1.0000 |
| 6 | after 6 clicks on the slider's `>` arrow | 0.8668 | 98.16° | 1.2113 | 79.08° | same | 1.0000 |
| 7 | slider at its right end | **0.6138** | **116.91°** | 0.8578 | 98.75° | same | 1.0000 |
| 8 | slider at its left end | **1.7936** | **58.28°** | 2.5065 | 43.50° | same | 1.0000 |
| 9 | 12 `>` clicks from the left end | 0.8835 | 97.08° | 1.2347 | 78.01° | same | 1.0000 |
| 10 | first gameplay dump after `Esc` | 1.1816 | 80.48° | 1.6513 | 62.40° | (−3216.85, 314.38, 6416.56) | 1.0000 |

- The ratio |col 1| / |col 0| is **1.3975 in every row** = 784/561, this window's aspect. On the
  home PC at 16:9 it was 1.7778. **The horizontal FOV is the anchored quantity (80.48° here, 80.5°
  there); the vertical one is derived from the aspect.** `[measured 2026-09-04, n=2 machines/aspects]`
- Each `>` click is worth about 3° of hfov near the default (6 clicks: +17.7°; 12 clicks from the
  minimum: +38.8°) — not exactly linear in degrees, so the slider is probably linear in something
  else (focal scale or a 0..1 fraction). Not pursued.
- The forward column stayed unit length and the eye did not move through the sweep: the slider
  edits `P`, not `V`. The reversed-Z constant in row 3 (`r3z`) stayed at 0.1140 throughout.
- **Exiting with `Esc` restores 80.48° at once** (dump 10, 15 writes, the eye nudged by the
  resumed simulation). The slider is a Capture-Mode-only value by this route.
  `[verified-live 2026-09-04, n=1]` The community route for carrying it into driving ("Video Mode,
  then the show-HUD tab, then resume") was not tried — no drivable car, and no tab is called that.

### What this buys the `[PD]` rewrite

Nothing in the buffer changes when the FOV changes except the two focal columns, which is exactly
the pair the rewrite scales. A future live check of the rewrite has a built-in reference: set the
slider to a known angle, read the columns, compare with what the rewrite would have produced.

## 3. Driving the CAMERA SETTINGS tab — mouse only `[verified-live 2026-09-04, n=1 session]`

- **Tab switch = click the tab label.** `CAMERA SETTINGS` is at client (452, 106) at 784×561; the
  chevrons at (65, 108) / (718, 108) were not needed. Yesterday's E / Tab / arrows negative stands.
- On this tab the bottom hint row drops MOVE / ROTATE and shows a mouse glyph for NAVIGATE. Keyboard
  `Down` and `Right` did nothing here (EXPOSURE stayed highlighted, no slider moved).
- **Select a row by clicking its label** (FIELD OF VIEW at (85, 174)); **change the value by
  clicking the `<` / `>` arrows** at the ends of its bar ((55, 189) / (272, 189)). Clicking on the
  bar itself and dragging the knob both did nothing (dumps 3–4 unchanged, screenshots identical).
- Screenshot pairs settled each of these in one step; the dump only confirmed what the picture
  already showed.

## 4. The two keys

- **V on foot: nothing** (expected — `settings.ini` maps `vehicle_fp_cam` to it, vehicle only).
  **V in the car: NOT TESTED.** The garage car is a non-enterable prop: no prompt at two positions,
  `R` (the keymap's `enter_vehicle`) did nothing, and the user confirmed "cannot enter this car". The
  save is at objective *Collect the jag tip*, before a drivable car. The row stays open and moves to
  "needs a save with a car".
- **X in gameplay: nothing** (0.3 s hold, n=1). The pause menu's Capture Mode page says "enter
  capture mode by pressing" two controller glyphs; the keymap's `overview_camera` = X was the
  keyboard guess. Disproved as a keyboard shortcut at n=1.

## 5. The keymap decodes alphabetically `[inferred-static 2026-09-04]`

`Mad Max\settings.ini` `[KeyMapping]` stores an index per action. With A = 0 … Z = 25:
`move_forward=22` W, `move_left=0` A, `move_backward=18` S, `move_right=3` D (these four are
live-verified by walking), `cancel_action=16` Q, `action=4` E, `vehicle_cam=2` C,
`vehicle_fp_cam=21` **V**, `enter_vehicle`/`exit_vehicle=17` **R**, `overview_camera=23` X,
`refuel=5` F. The user's V report is therefore backed by the game's own config before any press.
Indices 26–30 (`binocular`, `call_for_car`, `flashlight`, `canteen`, `sideburner`) look like the
digit row and 111–115 (`fire`, `aim`, `ram`, weapon-select) like mouse buttons/wheel — `[hypothesis]`.

## 6. The clip-z constant varies with position, not time `[measured 2026-09-04, n=2 positions, 13 dumps]`

Yesterday's note called row 3's z "drifting frame to frame" (0.089–0.117 across four dumps).
Today: **0.0889** at the first garage position (dump 1) and **0.1140** at the second — and then
0.1140 unchanged across twelve dumps at that second position over ten minutes, through Capture
Mode, the whole FOV sweep, and three consecutive gameplay dumps three seconds apart. Whatever it
is, it follows where the camera is (or what it looks at), not the clock. Still `[hypothesis]` as to
meaning; the "per-frame drift" wording should be read as "per-position".

## 7. Automation on this game, scored (§5a of `/lm`)

1. **Menu → gameplay: proven** — second dev-PC session, 0.25–0.3 s holds throughout, resume load
   under 55 s.
2. **Commands: N/A** — the proxy's numpad probes are the channel; every dump fired.
3. **Character + camera: proven, and extended** — walking and mouse look on foot; Capture Mode's
   free camera by keyboard (yesterday); **its settings tabs and sliders by mouse click (today)**.
   New harness primitive: `game-harness.py "Mad Max" click <x> <y>` (client coordinates).
4. **Self-close: proven, exercised today** — pause → EXIT TO MAIN MENU (verified highlight) →
   confirm → main menu → 7× Down → EXIT GAME (verified highlight) → Enter; the process was gone
   before the second confirm keypress found a window. The profile's "Enter, then Enter to confirm"
   is at most one Enter too many; harmless.

Not built: a marker-seeking walker was tried to reach the objective and failed on its colour
threshold — the on-screen objective marker is a desaturated green (~(94, 120, 83)), not the bright
green assumed. Left in the recon folder as a lead only; the car question made it moot.

## 8. What is NOT established

- Whether V does anything in a car (needs a save with one).
- Whether any Capture Mode route carries the FOV into gameplay (Video Mode `R` not tried).
- What the slider is linear in; what the 26–30 and 111–115 keymap indices are.
- What the clip-z constant is, beyond "position-dependent".

## 9. Next

Static (`[PD]`, unchanged): the shared-path per-eye rewrite, and the `InstanceConsts` world-matrix
question. Live (`[FLAT]`): V in a car once a save has one; optionally the Video Mode carry-over
test. Nothing here needs the headset.
