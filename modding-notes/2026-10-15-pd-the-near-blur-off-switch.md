# 2026-10-15 (`/pd`, dev PC, no launch): the cockpit near blur gets an off switch

The game was not launched, and nothing here has been run in the game.

## What was wrong

In the cockpit view the steering wheel and hands stay heavily blurred. `HQDof=0` did not help
`[verified-live 2026-10-15, n=1]`: it only picks which depth-of-field family runs.

## What the shipped shaders say `[inferred-static 2026-10-15]`

The 24 `dof_*` pixel shaders are the game's final picture pass (scene, blur, bloom, lens dirt, heat haze,
colour grade). Read with `fxc -dumpbin`, every variant blends the same way:

```
far  = sat(z * c4.x - c4.y) / (1 + sat(ny)^2 * c12.z)
near = sat(z * c4.z + c4.w) * c2.y
b    = sat(far * c0.w + near + c0.z)
out  = lerp(scene, blurred, min(3b, 1))
```

`c` is PS b1 `cbConsts` (240 bytes). With c0.z = c0.w = c2.y = 0 the weight is exactly 0 and the pass outputs the
sharp scene. The same buffer holds three more screen effects: c0.x (colour fringing, `_ca` variants), c12.w (lens
dirt) and c14.w (heat haze, on while above 0). Edge fade (`_ef`, a vignette texture) and film grain (`_fg`) have no
number to zero; which variant runs is not known yet.

`dofbokeh_*` (`HQDof=1`) takes its near blur from a separate compute pass's alpha, so this edit cannot remove it:
keep `HQDof=0`.

No 240-byte buffer is ever bound at PS b1 live; 256 is. The engine rounds allocations up (368 → 384, 80 → 96), so
the buffer is most likely 256 bytes `[hypothesis]`. Both widths are covered.

## What was built `[compile-verified 2026-10-15]`, `[verified-numerically 2026-10-15]` for the maths

`cbfp_dof.c`, switch file `madmax_vr_dof.txt` (installed, on):

1. `CreatePixelShader` is hooked; a new shader whose DXBC header checksum matches one of the 48 dof shaders is
   remembered. The checksums are unique to these shaders in the bundle (checked over all 1363 blobs).
2. `PSSetShader` notes when one is bound.
3. Every Map/Unmap or whole UpdateSubresource fill of a 240/256-byte buffer is copied (the game's values).
4. Just before a `Draw` or `DrawIndexed` with a `dof_*` shader bound, the bound PS b1's copy has the six numbers
   zeroed and is written back with a discard map. Earlier draws keep the game's values.

Self-test section 19, 24 checks: a hand transcription of the shader's weight (not the shipped code) is exactly 0
after the edit for 2000 random settings and above 0 before them; checksum matching; the copy ring; the Unmap path;
the draw path with a stub context. A planted mistake (c2.y left alone) fails five checks. 195/195 pass; two builds
are byte-identical.

Installed `dxgi.dll` `3c6d914cf4a9` (331,264 B), previous kept as `dxgi.dll.bak-2026-10-15-pd-pre-dof`
(`b0a980306560`); stamped.

## What is NOT established

- That the shaders are created after our device hook. If `cbfp dof ... dof_*=0` while the cockpit is on screen, they
  were created earlier (or by a different route) and nothing is recognised.
- That the fill is seen. `no copy of its fill` climbing means the buffer is filled in a way we do not copy, or is
  not 240/256 bytes.
- That the near blur in the cockpit is this pass at all. If `edited` climbs and the wheel is still blurred, the blur
  comes from somewhere else (for example the `blurdof` / `extractneardof` passes writing into the scene texture).
- Which `dof_*` variant runs, so whether edge fade and film grain are on screen.

## Next run (one launch, any cockpit scene)

Read the `cbfp dof frame=` line:

| line says | meaning |
| --- | --- |
| `dof_*=24` created, draws climbing, `edited` = draws, wheel sharp | done; switch stays on |
| created 0 | the shaders were made before the hook: move the device hook earlier |
| `no copy` climbing | the cbConsts fill is not seen: widen the width list |
| `edited` climbing, wheel still blurred | the near blur is not this blend: look at `extractneardof` |
| `dofbokeh_*` draws climbing | `HQDof` is back on: set it to 0 |

Delete `madmax_vr_dof.txt` beside the exe to compare with the blur back.
