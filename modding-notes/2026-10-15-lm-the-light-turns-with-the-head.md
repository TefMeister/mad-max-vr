# 2026-10-15: the light turns with the head; the headset bridge crashes in the simulator (`/lm`, dev PC)

`/lm`, dev PC, seven launches, unattended, one reader. Still camera by the car, 3D on, one eye, separation 0.065.
Evidence: `dev-archive/recon/2026-10-15-sun-rays-live/`. Videos of the game window only, in
`E:\OBS gameplay videos\mad-max-vr\` (`sunrays_`, `screenfx_`, `simbridge_`, `newn_`, `simguard_`, `flatcheck_` 2026-10-15).

## 1. The sun-ray edit works `[verified-live 2026-10-15, n=2 per pose, judged by eye]`

Installed `a3d31f3aa06b`. The log shows `cbfp ray: first sun-ray buffer (96 bytes) edited` and about 970 buffers
turned per 5 s (`SUN RAYS`), so the buffer is 96 bytes at run time, not the 80 the shader declares.

| pose | 2026-10-14 (before) | today |
| --- | --- | --- |
| 15° left | shadow a wrong-shaped blob beside the car | ground lit normally, shadow under the car, right shape |
| 15° right | wide dark band across the ground | ground lit, shadow under the car |
| 10° up | ground dark and hazy, shadow gone | ground lit, shadow under the car, sky normal |
| 0.3 m step | not tried with all edits | clean |
| 30° right | not tried | ground lit, shadow under the car |

**What is still wrong on a turn:** at the edge the turn reveals, terrain is missing (sky shows through) and a
long shadow lies on the ground with nothing casting it. Most likely the game culls objects against its own
unturned view on the CPU, while the shadow map has its own culling `[hypothesis]`. The reader's cheapest lever:
make the game draw a wider view than the eye needs and fold the narrowing back into `K`.

## 2. The reader's tidied build `[verified-live 2026-10-15, n=1 per pose]`

Staging `3ceaa3e`, installed `32a0e6c852fb` (old `a3d31f3aa06b` kept in the build-backups folder):
- The true `n` is **0.1000**, from a fit of the depth column (reversed-Z with a far plane about 40 km); the 0.1013
  of 2026-10-14 used one row only, and `vp[14]` moves with the camera `[verified-numerically 2026-10-15, n=1 matrix]`.
  The log now says `cbfp headk lens from the shared matrix: w 1.05936 h 1.48046 n 0.1`.
- `headk_is_camera` takes the far-plane part out first, so objects past ~10 km also take `K`; tested (165/165).
- `madmax_vr_kmode.txt` removed.
- Live: the same five poses give the same good pictures as above.

## 3. Screen effects for VR `[verified-live 2026-10-15, n=1]`

`settings.ini` backed up (`settings.ini.bak-2026-10-15-pre-screen-effects`), then `HQDof=0`, `Heathaze=0`,
`PostEffects=0` (`MotionBlur=0` already). Chase camera: colours and tone fine. **Cockpit camera: the roof, wheel
and hands are still heavily blurred**, so `HQDof` does not switch the near blur off. The reader: `HQDof` only picks
which DoF shader family runs (`dofbokeh_*` or `dof_*`); `dof_*` blends toward a blurred copy by a weight built
from PS b1 `cbConsts` (240 bytes) row 2 `.y` (depth blur) and row 0 `.z/.w` (constant and edge blur); recognise
the `dof_*` shaders by checksum at creation and neutralise that weight `[inferred-static 2026-10-15]`.
Lens dirt, damage tint and shake need combat: not tried.

## 4. The headset bridge crashes in the simulator `[verified-live 2026-10-15, n=2]`

`madmax_vr.ini`: `openxr=1`, the simulator's `runtime_json`, `test_pattern=1`, `layers=projection`, 3D off.
Both launches: `session running`, `two 1280x720 eye swapchains`, `screen placed at head height 1.70 m`,
`mxr share: game device ...`, then the game dies 0.15-0.36 s later, still on the legal screen. Windows: access
violation in `ucrtbase.dll` at offset 0x38668. No dump (LocalDumps needs admin). The simulator's own log stops
before the session.

The reader read the two crash logs: the frame counter ran 0 → 26,100 in 0.46 s with no draws, and the fault offset
is a `call` inside a CRT float-control helper, so the stack ran out `[inferred-static 2026-10-15]`. It built a
Present guard (depth count per thread; a nested Present goes straight to the real one, past depth 4 it returns S_OK
unpresented) and first-frame logging. Staging `74a47b7`, installed `b0a980306560`, self-test 171/171.

## 5. Guarded launch: the Steam overlay is what loops `[verified-live 2026-10-15, n=1]`

- `Present RE-ENTERED on thread ... at depth 2..5, called from gameoverlayrenderer64.dll+0x93f6f` right after the
  session starts. The real Present starts with `e9` (a jump: the Steam overlay patched it), and the overlay calls back
  through the swapchain's Present slot, which is ours. Without the bridge: 0 re-entries (flat check, same build).
- **The game survived** and the **red/blue test pattern reached the simulator** (screenshot), `xrEndFrame` returned 0,
  `mxr lock: WORKS`, 9,000 headset frames in 2.5 min.
- **But the game's own window went black** (never reached the title) with a `Present STORM` (1000+/s, re-entries
  climbing to 38,000): the loop is cut, not cured, so the game's picture is never really presented.
- Why only with the bridge on is not known `[hypothesis: the headset thread's device or the simulator's preview
  window makes the overlay re-hook]`. Next: one launch with the Steam overlay off for Mad Max separates "the overlay
  causes it" from anything of ours; then the guard should call the pre-overlay Present, or skip our work but let the
  outermost call present.

Bridge switched back off (`openxr=0`, ini restored from `madmax_vr.ini.bak-2026-10-15-pre-sim`); flat check on
`b0a980306560`: title screen normal, no re-entry.

## Not established

- Whether fog, cloud shadows, SSAO and decals need edits: the reader lists the edits (fog/cloud: PS b1 screen-to-world
  matrix rows; SSAO: rows 4-6 normal rotation; decals: reordered ray rows) `[inferred-static 2026-10-15]`; on today's
  still scene no fog fault was visible after the sun-ray edit.
- Driving with a head pose: not tried.

## Automation

Self-launch ✅ ×7, menu to gameplay ✅ (RESUME GAME verified by screenshot each time; one Enter was swallowed by a
slow legal screen, so screenshot before pressing), commands ✅ (numpad, look file), character and camera ✅ (still
camera; V for the cockpit), self-close ✅ (WM_CLOSE).
