# 2026-10-12 (dev PC, `/pd`, no game launch): the road to the headset

**The game was not launched. This is a design, made from the dossier, the proxy's source and the game's
`settings.ini`.** Settles the board row "plan the road to the headset".

## 1. Two eyes: alternate frames, not two renders a frame

**Decision: alternate frames (AFR)** — frame N is the left eye, N+1 the right — exactly the proxy's existing
"wiggle" mode (`g_stereo_mode` 0), handed to OpenXR one eye per frame, as Metro's bridge does.

Why not render twice a frame: this proxy changes constants as the game writes them (Map/Unmap). Drawing a frame a
second time would mean recording every draw call of the immediate context and replaying it with other constants;
DX11 has no way to capture an immediate-context frame for replay, so that is a renderer rewrite, not an edit. AFR
needs nothing new from the game. Cost: each eye updates at half the game's frame rate, so the game must run at
about twice the headset rate (Mad Max is a 2015 game; the home PC should manage) `[hypothesis]`; the jitter recorder
(`jitterlog.h`, estate rule) is wired in from the first headset build so stepping is measured, not guessed.

## 2. The head pose: one 4x4 per frame, not one float

Today each eye is ONE float, `M[3][0] += d·w` (dossier §7b), which can move the eye sideways and nothing else.
A head turns and moves. The general edit is still one small step, because only `V·P` is uploaded and `P` has a known
shape (dossier §6, measured 2026-09-04): row-vector, `|col 0| = w`, `|col 1| = h`, column 3 = unit forward,
column 2 ≈ 0 with row 3's z a small positive constant `n` (reversed-Z, infinite far `[hypothesis]`). So

    P = [ w 0 0 0 ; 0 h 0 0 ; 0 0 0 1 ; 0 0 n 0 ]          (rows, row-vector convention)

and any rigid change of the eye in VIEW space, `E` (head rotation, then head and eye offset), becomes

    M' = M · K,    K = P⁻¹ · E · P

for the shared matrix AND every per-object `W·V·P` matrix alike: `W·V·P·P⁻¹·E·P = W·(V·E)·P`. `K` is built once per
frame from `w, h, n` read off the shared matrix. **The current one-float edit is the special case E = a pure x
shift**, so the first self-test checks that `K` reproduces it exactly, then checks `M·K` against independently built
`W·V·E·P` (the same check The Evil Within's clip-space head pose passed, 83,957 cases, `b9c20fb`). `n` cancels for
everything but depth; reading it from the same frame's matrix keeps depth exact `[inferred-static 2026-10-12]`.

**Only `V·P` is known, not `V`:** `E` is in view space, which is exactly what the headset gives (head relative to
the recentred start, as in Prototype and Metro: OpenXR z back → mirror to this view's z forward). No world-space
camera is needed for the main picture.

## 3. What each existing edit needs when the head moves

All four already take "this frame's eye" as an input; they generalise from `d` to `E`:

| edit | today | with a head pose |
| --- | --- | --- |
| per-object (`InstanceConsts`) | `M[3][0] += d·w` | `M · K` |
| sun / shadow (`sun_eye_offset`, camera position + shadow origin in world) | world offset of the eye from `d` along the camera's right | world offset of the head+eye: `E`'s translation taken to world with the camera's rotation, read off the shared matrix (columns 0,1,3 normalised = right, up, forward; §6) |
| previous frame (`prev_edit`, keeps motion blur from seeing the eye jump) | same `d` on last frame's matrix | same `K` on last frame's matrix, so neither the eye swap nor head motion reads as motion (motion blur is going off in VR anyway, but the vectors also feed other passes) |
| ground motion (`mvo_edit`, `motionvectoroutput`) | `d·w` into the reprojection | `K` into the reprojection |
| AO box (`ao_edit`) | eye offset | ruled out as the shadow (2026-10-11); keep it off |

## 4. Getting the pictures to the headset

Port **Metro's bridge** (`staging/metro-exodus-vr/headset-bridge-2026-10-07/src/mxr*.c`, DX11 like this game): own
D3D11 device and session on a headset thread, the game never waits; each Present copies the back buffer to the eye
it was drawn for (LOCK, falling back to RING); each picture carries the head pose and the game's own lens (`w, h`)
to a projection layer, so the compositor only corrects latency (Metro's 2026-10-12 head-tracking design, same
shape). The eye of a Present = the eye this frame's edits used (one frame counter; pairing queue as Metro if Present
runs on another thread). Plus the C++ runtime check from Heavy Rain; Mad Max's folder carries no own
`msvcp140.dll`, so the system's newer copy is used `[measured 2026-10-12]`.

## 5. Screen effects (standing rule, 2026-10-12): what to switch off for VR

From `settings.ini` `[Graphics]` (game closed, backed up first) `[inferred-static 2026-10-12]`, unless noted:

| effect | switch | now | VR |
| --- | --- | --- | --- |
| motion blur | `MotionBlur` | 0 | off — proven: the smear went with it `[verified-live 2026-09-30]` |
| depth of field (the cockpit's strong near blur) | `HQDof` | 1 | 0; if the blur stays, it is the low-quality DoF and needs the menu or a shader skip |
| heat haze (a screen distortion) | `Heathaze` | 1 | 0 to try |
| post effects (grain / vignette / colour grade, by its name) | `PostEffects` | 1 | 0 to try; if it also removes needed tone mapping, keep 1 and find the pieces |
| sand / blood / rain on the screen, low-health tint, camera shake | none in `settings.ini` | — | find live (menu, then shader skip), one board row |
| bloom, fog, soft particles, FXAA | `Bloom`, `VolumeFogQuality`, `SoftParticles`, `FXAA` | on | keep: world effects, not painted on the camera |

## What is NOT established

- That `P` has exactly that shape in every pass `K` would touch (the per-object path shares the shared frame's `w`,
  §7b; shadow cascades are orthographic and must be skipped, as the current edit already does).
- The reversed-Z reading (`n`) — only a live depth check shows a mismatch; the self-test can only prove the algebra.
- AFR comfort at the frame rate the home PC reaches.

## The rows this leaves

1. `[PD]` `K` = `P⁻¹·E·P` in C, with a self-test (reproduces the one-float edit exactly; matches `W·V·E·P`).
2. `[PD]` move the four edits from `d` to `E` (and the sun's world offset), each with its test; off by default.
3. `[PD]` port Metro's headset bridge + head pose + jitter recorder; off unless switched on.
4. `[FLAT]` the screen-effect switches in `settings.ini` (game closed), then look; find the rest live.
5. `[FLAT]` the simulator: AFR pictures arrive, the head turn turns the view the right way, the car stays sharp.
