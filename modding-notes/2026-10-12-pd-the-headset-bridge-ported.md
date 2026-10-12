# 2026-10-12 (dev PC, `/pd`, no game launch): Metro's headset bridge ported into the Mad Max proxy

**The game was not launched; nothing here has run in it.** Design: `2026-10-12-pd-the-road-to-the-headset.md` §4.

## What it is

`staging/mad-max-vr/proxy-dxgi/src/xr/`: Metro's bridge (`mxr*.c`, `mhead.c`, from
`metro-exodus-vr/headset-bridge-2026-10-07`), almost unchanged, plus `mmxr_glue.c`:
- **Off unless `madmax_vr.ini [xr] openxr=1`** (installed with `openxr=0`). Then a headset thread with its own D3D11
  device and session; the game never waits for it.
- **Only the game's Present runs a frame.** This proxy already patches Present, and every swapchain shares that
  vtable, so the simulator's preview presents through the same hook; Metro's filter (headset thread / its window /
  the game's window) keeps those out of `end_frame()`. Bridge off: the hook behaves exactly as before.
- **Which eye a picture is:** where the camera sat this frame (from the eye shift, or this frame's head-pose
  transform); `swap_eyes=1` crosses them if a run shows them crossed.
- **Head tracking** (`head_tracking=1`, needs `layers=projection`): the headset's newest pose feeds `cbfp_headk.c`
  (recentred on its first pose); each picture carries the raw head pose plus the eye offset and the game's lens
  (`tan = 1/w, 1/h`), so the compositor only corrects latency.
- The C++ runtime check (Heavy Rain's lesson) and the BeG0nE jitter recorder (pose at each headset read, present at
  each game Present, session on/off) are in.

## Verified

- Builds; a rebuild gives the same file (`06a59ced1fe8`) `[compile-verified 2026-10-12]`.
- The offline suite still passes (149 checks) and the bridge's own tests ported with it pass (ring: 0 torn reads;
  format pick; head-pose maths 20,014 checks) `[verified-numerically 2026-10-12]`.
- Installed: `dxgi.dll` `06a59ced1fe8` (was `fcc053b4355e`, kept on E:), `openxr_loader.dll` `97a8e5f74fc2`
  (Metro's, x64), `madmax_vr.ini` with `openxr=0`.

## Not established (no game, no runtime has seen it)

- That the game's device accepts the hand-over (Metro's refused keyed-mutex textures made on the game's device; LOCK
  makes them on the headset's device and RING needs no mutex at all; the log names which worked).
- That the eye assignment is the right way round (`swap_eyes`), and the alternate-frame rate in a headset.
- The jitter recorder's camera stream (`jl_camera_*`) is not wired yet: only pose and present.

## Next live test (`/lm`, simulator, still camera)

1. `madmax_vr.ini`: `openxr=1`, `runtime_json=` the simulator, `test_pattern=1`. Launch: the log wants `mxr: ON`,
   `mxr: session running`, red and blue eyes in the simulator window; the game itself unchanged.
2. `test_pattern=0`, 3D on (NUMPAD6, wiggle): each eye shows the game; `mxr lock: WORKS` or `mxr ring: WORKS`.
3. `head_tracking=1`, `set_head_pose yaw 30`: the view turns left and holds; car sharp, shadow under it.
- Game window freezes or the game exits: capture the log tail; first suspect is the Present filter.
- Eyes crossed (near objects separate the wrong way): `swap_eyes=1`.
