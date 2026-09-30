# 2026-09-30 — the HUD stays put, and the smear was motion blur

`/lm`, dev PC, six launches, unattended (Resume Game → the desert with the car, single-eye mode, separation
0.6054). Screenshots and log summaries: `dev-archive/recon/2026-09-30-hud-skip-and-motion-blur/`.

## The two board questions, answered

**1. "Narrow the edit to one width — the HUD moves with the world."** Editing width **192 alone** still
moves both the world and the HUD (minimap off the left edge, objective text and weapon cluster shifted)
`[verified-live 2026-09-30, n=1]`. So a width cannot separate HUD from world. What does separate them is the
matrix itself: a flat (HUD/UI) draw has no perspective, so its w column is zero. Skipping those draws keeps
the minimap, objective text and weapon cluster exactly in place while the world still moves
`[verified-live 2026-09-30, n=2 launches]`. About 300 k flat draws skipped against 1.43 M edited in one window.

**2. "The smear is not motion blur."** It is. With `MotionBlur=0` in `settings.ini` the car and the crate
wall are sharp in single-eye mode, with the same build and separation that smeared them before
`[verified-live 2026-09-30, n=1]`. The mechanism is `[hypothesis]`: the edit moves each object's current
position but not the previous-frame matrix the blur compares against, so every shifted object looks as if it
is moving sideways. The 2026-09-10 argument ("it survives with the separation held still") did not rule this
out, because the mismatch is there every frame even when the shift is constant.

## What else was tried

| Build | HUD | Car / crates |
| --- | --- | --- |
| width 192 only | moves | smeared |
| all widths, flat skip | **stays** | smeared |
| all widths, only "world-scale clip-like" matrices | stays | car sharp but **not shifted** (the shape test is too strict for nearby objects) |
| widths 192/128/96, flat skip | stays | smeared (so width 64 is not the smear) |
| all widths, flat skip, **motion blur off** | stays | **sharp** |

## The reader's work

- `cbfp.c` (1,568 lines) split move-only into six files under 800 lines; self-test 71/71, exports identical.
  Adopted and pushed (staging `af1794e`), then the HUD skip on top (`46ae37b`).
- The 384-byte buffer is most likely `InstanceConsts` (368 bytes declared, allocated rounded up), read by 112
  shaders whose object placement comes from a separate 64-byte buffer, so its matrix is plain viewProj
  `[inferred-static 2026-09-30]`. Those draws never get the eye shift today.
- It also noticed the edit had no shape gate at all, which led to the flat-skip test above.

## Installed now

`dxgi.dll` `0fed1e4c2d4e` (split + HUD skip). `settings.ini`: `Music=0` (standing rule) and `MotionBlur=0`
(needed for the edit; VR wants it off anyway). Backups: `Mad Max/_backup-2026-09-30-lm/`,
`settings.ini.bak-2026-09-30-pre-music-off`.

## What is NOT established

- A faint dark double edge is left on the car with blur off: some pass of it is still unedited.
- Whether the shift is geometrically right for a given separation (unchanged since 2026-09-10).
- Whether the 384 family (probably debris, grass, foliage) should be edited too.
