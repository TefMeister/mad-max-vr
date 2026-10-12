# 2026-10-12 — the car's shadow follows the car, and the sand stays sharp under motion blur

`/lm`, dev PC, three launches, unattended, one reader. Same scene as 2026-10-11 (Resume Game, the car in the desert,
single-eye, separation 0.6054). Evidence: `dev-archive/recon/2026-10-12-the-shadow-follows-and-the-sand-is-sharp/`.
Videos (game window only) in `E:\OBS gameplay videos\mad-max-vr\` (`sun-route`, `sun-768`, `ground-blur`).

## 1. What the new census lines said `[measured 2026-10-12, n=1 launch]`

- **Every constant buffer is filled by `Map(WRITE_DISCARD)`.** No other `Map`, no `UpdateSubresource`, whole or boxed.
- **The D3D11.1 routes are hooked and never used:** no lower-case (offset) binds in the bind census.
- **The 624-byte buffer is bound only at VS b4 and VS b5, never at PS b1.** So the buffer the 2026-10-11 sun edit
  touched is not the sun's constants at all. The reader reads it as a bone palette (624 = 13 x 48; VS b4/b5 declare
  12288-byte `cb4`/`cb5`) `[inferred-static 2026-10-12]`.
- Pixel-stage b1 widths bound about 3 times a frame: 384 (ruled out 2026-10-11) and **768**.

## 2. The sun's constants live in a 768-byte buffer: the shadow now follows `[verified-live 2026-10-12, n=3 toggles + both eyes]`

Same sun-origin edit (register 4 += eye offset through rows 1..3), now also applied to 768-byte buffers:

| frame (against stereo off) | car | car shadow | near sand | crate wall | hills | HUD |
| --- | --- | --- | --- | --- | --- | --- |
| left eye, edit on | -23 | **-23** | -19 | -8 | 0 | 0 |
| left eye, edit off | -19 | **-1** | -19 | -8 | 0 | 0 |
| right eye, edit on | +23 | **+24** | +17 | +9 | 0 | 0 |
| right eye, edit off | +22 | **+1** | +17 | +9 | 0 | 0 |

The difference picture (edit on vs off) shows only shadows changing: the car's, its self-shadow, pebbles, crates.
So the dark double edge was the car standing off its own unshifted sun shadow, and it is fixed.

⚠️ This is the **reflection-size-is-not-runtime-size lesson a third time**: the shaders declare 624 bytes; the game
allocates 768. ⚠️ The edit is width-only: 768 also carries a 672-byte `InstanceConsts` and a 752-byte `$Globals`
layout (reader, static). Nothing visibly broke, but a shape gate is queued. The 624 edit still fires on what is
probably bone data; whether that harms skinning is open.

## 3. The ground's motion blur: fixed by the reader's motion-vector edit `[verified-live 2026-10-12, n=2 toggles]`

The reader found the terrain writes no velocity; a full-screen pass (`motionvectoroutput`, PS b1) reprojects each
pixel with a matrix built from the unshifted camera. Its edit (`madmax_vr_mvo.txt`) rebuilds that matrix for the
shifted eye. With `MotionBlur=1`, still camera, left eye:

| | near-sand sharpness | car | crate wall |
| --- | --- | --- | --- |
| stereo off | 108.8 | 574 | 771 |
| stereo on, edit off | 26.5 / 26.4 | 730 / 743 | 946 / 881 |
| stereo on, edit on | **107.5 / 103.9** | 773 / 729 | 1080 / 1184 |

Not yet tested while driving. Some small orange specks behind the car appeared in edited frames; probably exhaust
particles, unexplained `[hypothesis]`.

## Installed now

`dxgi.dll` `cf9d5be44989` (staging tree with the reader's motion-vector edit + the 768 sun width); switch files
`madmax_vr_sun.txt`, `madmax_vr_prev.txt`, `madmax_vr_mvo.txt` present (they only act with the 3D on, NUMPAD6);
`settings.ini` `MotionBlur=0`, `Music=0`. Stamped. Previous build kept as `dxgi.dll.bak-2026-10-12-lm-pre-sun768`.

## Automation

Self-launch ✅ x3, menu → gameplay ✅ (RESUME GAME verified by screenshot each time), commands ✅ (numpad hotkeys),
character + camera not needed (still scene), self-close ✅ x3 (WM_CLOSE, ~2 s).
