# 2026-10-14 (dev PC, `/lm` reader helper, static only): test sheet for "the headset bridge in the simulator"

Source read: `staging/mad-max-vr/proxy-dxgi/src/xr/{mxr.c, mxr_eyes.c, mmxr_glue.c, mhead.c}`, `cbfp_headk.c`,
`cbfp_hooks.c`, `cbfp_report.c`, `proxy.c` (staging HEAD 661aafe). Nothing was run.

## Runtime and settings

- Simulator runtime JSON on this PC: `D:\claude video game stuff\tools\OpenXR-Simulator\openxr_simulator.json`
  (64-bit; the `-32` one is for 32-bit games) `[measured 2026-10-14]`. Registry ActiveRuntime is SteamVR, so the
  per-game `runtime_json` is needed.
- `madmax_vr.ini` `[xr]`, read ONCE at start (a change needs a relaunch) `[inferred-static]`:
  `openxr` (0), `runtime_json` (empty = system runtime), `layers` (anything but `projection` = floating screen;
  installed ini says `projection`), `test_pattern` (0), `swap_eyes` (0), `head_tracking` (0, forced off unless
  `layers=projection`), `head_position` (1 = turning + moving), `eye_source` (0 = fifo, else latest),
  `share` (`ring` = RING, anything else = LOCK first, RING fallback).
- Installed `dxgi.dll` 06a59ced1fe8 and `openxr_loader.dll` 97a8e5f74fc2 match the 2026-10-12 note; today's log
  already prints `mxr: off ([xr] openxr is not 1)` `[measured 2026-10-14]`.

## Log lines, in order (verbatim format strings)

Bridge on: `mxr share: LOCK first (keyed mutex made on the headset device), RING if that fails`;
`mxr: ON - headset thread started (own device); eyes as per-eye projection views, TEST PATTERN; swap_eyes 0, eye_source fifo; head tracking off`;
`mmxr: headset bridge ON, head tracking off`; `mxr: runtime for this game only: <path>`;
`mxr: waiting for the game's first frame before starting the session`;
`mmxr: game swapchain %p, %ux%u format %d, window %p; only it runs per-frame work`.
Session: `mxr: session created on the headset thread's own device; waiting for the runtime to start it` then
`mxr: session running`.
Test pattern: `mxr: two 1280x720 eye swapchains, format %d`, `mxr diag: ... ; TEST PATTERN`,
`mxr: 1 headset frames submitted` (then every 900). Colours: left 0.8/0.1/0.1 red, right 0.1/0.2/0.9 blue.
Game picture: `mxr lock: WORKS - the game device opened both keyed-mutex textures` or
`mxr ring: WORKS on the headset side - opened %d eye textures (%ux%u)`; in `mxr diag:` both `have L1 R1` and the
serials L/R climbing. Head tracking: `mxr: ON ... head tracking ON (turning + moving)`,
`mmxr: headset bridge ON, head tracking from the headset`, `mxr head: first head pose published (heading %.1f deg)`,
and in `mxr diag:` `head poses N` climbing and `eye views with the drawn pose M` climbing (M>0 = frames drawn with K
reached the headset).
Failure lines: `mxr: STOPPED: that copy is older than 14.40 ...`, `mxr: xrCreateInstance failed`, `mxr: the runtime
ended the session`, `mxr: a Present from a swapchain that is not the game's (%p) - passed straight through` (once per
foreign swapchain), `mxr: xrEndFrame failed`, `mxr share: LOCK failed at ...`.

## Traps found

1. Both eyes must be fed or the headset shows nothing: `submit_frame` needs `have[0] && have[1]`. A single-eye
   mode (NUMPAD7 to `left`/`right`) feeds one eye only. Use wiggle (mode 0). `[inferred-static]`
2. Head tracking only acts with the 3D on: `headk_prepare` runs only under `g_stereo_on`. 3D off = no K, and
   `eye views with the drawn pose` stays 0. `[inferred-static]`
3. No log counter says whether an edit took K or the one-float path: the `cbfp stereo` counters rise the same
   either way, and a K that fails `headk_read_proj` falls back silently. The only signs are the picture and (bridge
   on) `eye views with the drawn pose`. Worth a `/pd` counter (K built / K refused per report). `[inferred-static]`
4. `madmax_vr_look.txt` vs `head_tracking=1`: the headset wins on every frame it has a pose (`mh_latest` never goes
   stale once a pose exists); the look file is used only before the first headset pose, or on the rare frame the
   lock-free read gives up (8 tries). The look file still logs `cbfp: head pose ON ...`, which would then be a
   misleading line. Delete the look file before a head-tracking run. `[inferred-static]`
5. Eye naming: the cbfp mode labelled "left eye only" (e = -1) is read by the glue as the RIGHT eye (camera at -d).
   One of the two labels is wrong; `swap_eyes` absorbs it, but the first headset run should check. `[inferred-static]`
6. AO box edit still takes only the one-float shift (by design, it is off). `[inferred-static]`
