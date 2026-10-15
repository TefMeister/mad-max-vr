# 2026-10-15 (evening, dev PC, `/lm`, unattended, one reader): Mad Max's own picture reaches the headset simulator

Installed `dxgi.dll` `3c6d914cf4a9` (Present guard + near-blur switch), `madmax_vr.ini` `openxr=1`, the simulator's
`runtime_json`. Evidence: `dev-archive/recon/2026-10-15-bridge-direct-launch/`.

## 1. Started directly, the overlay loop does not happen

- Mad Max was started as `MadMax.exe` from its own folder, with a new `steam_appid.txt` (`234140`) beside it, Steam
  running, instead of through Steam's launcher.
- The Steam overlay is still loaded in the process (`gameoverlayrenderer64.dll`; the game's Steam library pulls it
  in), yet **0 `Present RE-ENTERED` lines** over two runs, and the game window draws normally
  `[verified-live 2026-10-15, n=2 runs]`.
- So the loop of the afternoon needs the overlay as injected by Steam's launcher (`steam://run`), not merely the
  overlay being loaded `[verified-live 2026-10-15, n=2]`. Why exactly is the reader's question (hook order is the
  likely difference `[hypothesis]`).

## 2. The headset link works on Mad Max

- Run 1, `test_pattern=1`: red/blue in the simulator, the game window drawing (logos, title) `[verified-live 2026-10-15, n=1]`.
- Run 2, `test_pattern=0`, `head_tracking=1`, 3D on (NUMPAD6): **Mad Max's own picture in both eyes of the simulator**,
  in the world, by the car `[verified-live 2026-10-15, n=1]`.
- **LOCK works on Mad Max's device** (unlike Metro's): `mxr lock: game device opens eye 0 ... -> hr 0x00000000`,
  copies and pulls climbing, `slow 0`, `open fails 0`. Device: not DX11-on-12, `ID3D11Device1` yes, feature level
  11_0 `[verified-live 2026-10-15, n=2]`.
- **Head tracking:** simulator yaw 30 deg left turns the view the right way (the car slides right, a cliff comes in on
  the left), the ground stays lit and the car's shadow stays under it; back to 0 returns the same picture
  `[verified-live 2026-10-15, n=1]`. A blue patch at the bottom left on the turn is the known revealed edge (board
  row: draw a wider view than the eye).

## 3. The cockpit near blur is NOT the `dof_*` pass

- With the switch on, in the cockpit (V): `cbfp dof frame=8700: ... dof_*=24 dofbokeh_*=24; draws with dof_*=0,
  edited=0 ...; draws with dofbokeh_*=0`. The steering wheel and hands are still blurred `[verified-live 2026-10-15,
  n=1]`. Read at first as "neither family is drawn"; section 5 shows the draw counting itself is blind, so this
  proves nothing about which pass blurs.

## 4. The reader's overlay fix works with a normal Steam start (run 3)

- The reader traced the loop `[inferred-static 2026-10-15]`: our hook calls the real Present, whose first 5 bytes are
  the overlay's jump; the overlay calls the vtable slot (ours) as "the original", and round it goes, so no level ever
  reached the real Present's body. Fix: a nested call goes to a **pre-overlay Present**, a small trampoline built
  from System32 `dxgi.dll`'s own bytes, so the outer call is drawn by the overlay once and presented once.
  `madmax_vr.ini [present] overlay_fix=0` turns it off. Build `dxgi.dll` `909a4e0a18cb` (staging `864d0dc`,
  self-test 219/219), filed as builds `Headset output/v0.1.0-b001` (the first Mad Max build in the archive).
- Live, started through Steam (`steam://run/234140`): the re-entry came (`gameoverlayrenderer64.dll+0x9b81f`) at the
  moment the headset session started, `pre-overlay Present BUILT - 5 byte(s) patched, 5 copied from the file`, 6,000+
  nested Presents sent to it, **0 storm, the game window draws, the simulator shows the game in both eyes**
  `[verified-live 2026-10-15, n=1]`.

## 5. The pass census and the skip list cannot see the game's draws

- The same build lists 121 full-screen passes by name at each census line and can leave named passes out
  (`madmax_vr_skip.txt`). In the open world every line read `none`, `comp_*` drew 0 times too, and leaving out 27
  passes (`comp*`, `tmonly*`) changed nothing on screen `[verified-live 2026-10-15, n=1]`. So shaders are recognised
  when created but never seen at draw time: the near-blur switch (section 3) was blind for the same reason, and its
  "0 draws" says nothing about the blur. Sent to the reader; the skip file is removed again.

## 6. Draws hooked inside d3d11: the census sees the passes, and the cockpit is sharp (run 4)

- Why the census was blind: shader creation, Map and constant-buffer binds reached our vtable hooks, but no
  PSSetShader or draw call ever did, so the game calls them another way (a pointer copied before we patched, most
  likely; `MadMax.exe` is packed, so it cannot be read) `[inferred-static 2026-10-15]`. The reader's build
  `dxgi.dll` `2a5ce5e5eda5` (staging `d4b46f5`, self-test 226/226, builds `Headset output/v0.1.0-b002`) puts the
  hooks for PSSetShader and all eight draw methods inside d3d11's own functions (one atomic 8-byte jump, a trampoline
  for the copied start), with the old vtable hook as fallback and `[hooks] draw_detours=0` to switch it off.
- Live through Steam: all eight `hooked inside d3d11`; about 1,600 PSSetShader and 2,500 draws per census line on the
  logo screen; no deferred contexts made; 0 storm `[verified-live 2026-10-15, n=1]`.
- In the world the pass list is real: `blurscale`, `blursep`, `dof_u2_ef`, `fogvolumeapplynoise`,
  `fogvolumecompositenear`, `highpass*`, `luminancetodepth*`, `motionblurpassthrough`, `separableblurmed`, `ssao_*`
  `[verified-live 2026-10-15, n=1]`. The same set shows in the chase and cockpit cameras.
- **The near-blur switch works**: `draws with dof_*=10700 ... edited=10700`, and in the cockpit the wheel, hands and
  roof are sharp, in the game window and in both simulator eyes, where the same spot was blurred in run 2
  `[verified-live 2026-10-15, n=1]`. So the near blur WAS the `dof_*` composite (`dof_u2_ef` here); section 3's
  reading is withdrawn.
- Every older draw-time edit keyed on these shaders had never run before this build. Worth re-checking, by eye, any
  past result that depended on one.

## Recorded

- `bridge-direct-launch_2026-10-15_17-10-19.mp4` and `overlay-fix-steam-launch_2026-10-15_17-35-30.mp4` and
  `draw-hooks-pass-census_2026-10-15_17-51-40.mp4` (the game window only), MEGA `Videos\mad-max-vr`.

## Not established

- Comfort, real eye spacing in the headset, driving with head tracking.

## Automation

Self-launch ✅ (directly, `steam_appid.txt`), menu to gameplay ✅ (RESUME GAME verified by a zoomed picture), commands ✅
(numpad), character and camera ✅ (V, simulator head pose), self-close ✅ (window close).
