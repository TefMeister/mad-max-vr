# 2026-10-15 (`/lm` reader, static only): the headset-bridge crash in the simulator

Inputs: the two crash runs' proxy logs (game folder, `...prev-20261015-run3-crash.txt`, `...run4-crash.txt`), the
Windows APPCRASH record (ucrtbase.dll 10.0.19041.7802, c0000005 at offset 0x38668), the staging source.

## What the logs and the fault address show

- **The game's Present ran wild before the crash** `[measured 2026-10-15, n=2 runs]`. The frame counter, which only the
  game's Present moves, went 0 → 300 in 0.10 s, then to 26,100 by 0.46 s after the first frame, with the cumulative
  bind counts unchanged across all those "frames", so no draws happened in between. At the title screen without the
  bridge the same counter moves about 60 a second with draws (run2 of the same day).
- **The fault is on a `call` instruction:** ucrtbase RVA 0x38668 is `call` inside an unexported helper (0x38648-0x38906)
  of the floating-point control-word family (`_control87` / `_controlfp`, mask 0x308031F), next to `_statusfp`
  `[inferred-static]`. A `call` faults only when pushing its return address, so the stack was exhausted.
- **The headset thread never finished its first frame:** its diag line, printed right after the first `xrEndFrame`
  returns, is missing from both logs. No "headset-runtime Present passed through" line, no `CreateSwapChain` from the
  simulator either.
- Most likely reading `[hypothesis]`: a Present that re-enters `hk_Present` on one thread until the stack runs out.
  Not explained yet: what calls back in. The simulator does not hook Present (no hook strings in its DLL). A flat loop
  of Presents with no draws (the game spinning while its window is covered or loses focus) would explain the counter
  but not the stack fault. Both readings are open.
- "screen placed at head height" is the anchoring done on every first frame whatever the layer type, NOT a quad path
  `[inferred-static]`. The 784x561 game picture vs the 1280x720 test-pattern chains do not meet in test-pattern mode
  (the eyes are only cleared, never copied).

## In staging (`74a47b7`, dxgi.dll `b0a980306560`, not deployed) `[compile-verified 2026-10-15]`

- `cbfp_pguard.c`: `hk_Present` counts its depth per thread. A nested Present skips all our work. Past depth 4 it
  returns S_OK without presenting, so such a loop unwinds instead of crashing. Self-test section 18 drives `hk_Present`
  with a real Present that calls back for ever and shows it returning, with the frame's work done once.
- New log lines: `cbfp present guard: Present RE-ENTERED on thread N at depth D, called from <module+offset>`;
  `game Present returned 0x...`; `game Presents now on thread N`; `Present STORM ...` (more than 1000 game Presents
  inside one second), followed by the vtable slot's current owner and the real Present's first two bytes (e9 or ff 25
  = someone inline-hooked it).
- `mxr.c`: on the first headset frame, a line before the pull, after each eye fill, before `xrEndFrame` and after it
  returns. The headset thread now gets an 8 MB stack reserve (insurance only).

## How to read the next launch

- RE-ENTERED lines appear: the calling module names the loop. The guard should keep the game alive.
- A STORM without re-entry: a flat loop. Its `hr` (for example 0x087A0001, occluded) and thread tell whether the game
  is spinning because its window is covered by the simulator's preview.
- The first-frame lines stop at one step: that call is where the headset thread is stuck or died.
