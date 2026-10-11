# 2026-10-11 — the car's shadow stays behind

`/lm`, dev PC, three launches, unattended, one reader. Resume Game → the desert with the car, single-eye (left) mode,
separation 0.6054, per-object edit. Evidence: `dev-archive/recon/2026-10-11-the-shadow-stays-behind/`. Videos (game
window only): `E:\OBS gameplay videos\mad-max-vr\` (`car-double-edge`, `ssao-off`, `sun-shadow-fix`), copied to the
MEGA transfer folder.

## What moves and what does not

Best-correlation sideways shift of each region against the "off" frame `[measured 2026-10-11, n=4 frame pairs]`:

| region | shift |
| --- | --- |
| car body | -22 px |
| near sand | -24 px |
| crate wall (~40 m) | -8 px |
| far hills | -1 px |
| HUD | 0 px |
| **the car's shadow on the sand** | **-1 px** |

So the world shifts in a sensible depth order, but the car's shadow stays where it was, and the car stands off its
own shadow. That is most likely the "faint dark double edge" `[hypothesis]`.

## What was tried (all live, this session)

1. **The 384 family** (switch file `madmax_vr_384.txt`): it is bound to the PIXEL stage (PS b1). Adding it changes
   lighting broadly (sky, hills, crate shading) but the shadow stays at -1 px.
2. **SSAO off** (`settings.ini`, restored to 1 afterwards): no change to the shadow; no measurable dark band beside the
   car in any case.
3. **BOTH mode** (shared + per-object): shadow 0 px.
4. **The sun pass's camera origin** (reader's recipe, `madmax_vr_sun.txt`, sign flip `madmax_vr_sun_neg.txt`): both
   edits fired about 30 times a second; the shadow stayed at -1 px with either sign `[verified-live 2026-10-11, n=1 each]`.

## The reader

Job 1: which car passes the edit reaches (paint, wheels, pre-pass and velocity: yes; `aobox`, outlines, skidmarks,
trails: no). Job 2: the sun pass's reconstruction maths and the origin edit tried in item 4. Both folded into the
dossier.

## Installed now

`dxgi.dll` `09075895af00` (the new switches stay off without their files; otherwise the 2026-09-30 behaviour).
`settings.ini`: `Music=0`, `MotionBlur=0`, `SSAO=1`. Switch files taken back out. Previous build kept in
`E:\Mod backups (2026-10-11)\mad-max\`.

## Automation (five capabilities)

Self-launch ✅ (`steam://rungameid/234140`); menu → gameplay ✅ (Enter at the title, Enter on Resume Game, ~65 s);
commands N/A; character + camera not needed (still view); self-close ✅ (WM_CLOSE) three times.

## NOT established

Where the car's ground shadow is actually drawn from (a separate car shadow, a screen-space pass, or a cached shadow
map), and whether the sun pass reads its origin from a third place.
