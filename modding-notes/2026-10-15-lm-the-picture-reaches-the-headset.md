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
  n=1]`. With `HQDof=0` neither family is drawn at all, so the near blur comes from another pass. Sent to the reader.

## Recorded

- `bridge-direct-launch_2026-10-15_17-10-19.mp4` (the game window only), MEGA `Videos\mad-max-vr`.

## Not established

- Whether the bridge works with a normal Steam launch (the reader's fix).
- Comfort, real eye spacing in the headset, driving with head tracking.

## Automation

Self-launch ✅ (directly, `steam_appid.txt`), menu to gameplay ✅ (RESUME GAME verified by a zoomed picture), commands ✅
(numpad), character and camera ✅ (V, simulator head pose), self-close ✅ (window close).
