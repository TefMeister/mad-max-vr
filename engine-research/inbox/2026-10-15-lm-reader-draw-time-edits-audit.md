# 2026-10-15 /lm reader: which edits only run at draw time, and the record to correct; the jitter log names its runtime

From the static reader beside the evening `/lm`. Static reading of the proxy source and of the run-4 log in
`dev-archive/recon/2026-10-15-bridge-direct-launch/`. Nothing here was run in the game.

## 1. Draw-time edits versus Map-time edits

Draw-time means keyed on the pixel shader bound by `PSSetShader`, acted on in a draw hook. Those hooks never received a
call before build `2a5ce5e5eda5` `[verified-live 2026-10-15, n=1]` (dossier, 2026-10-15 evening).

**Draw-time (did not run before `2a5ce5e5eda5`):** `[inferred-static 2026-10-15]`, from `cbfp_draws.c`, `cbfp_dof.c`, `cbfp_pass.c`

| edit | what it does | first in | credited with |
| --- | --- | --- | --- |
| `dof_*` composite, near and far blur (c0.z, c0.w, c2.y zeroed) | the cockpit near blur off | staging `2afa599` (2026-10-15) | Run 2 "neither family is drawn, wheel still blurred": already withdrawn in the notes (section 3 and section 6). Run 4 "wheel, hands and roof sharp, edited 10,700": genuine, since the hooks ran. Nothing to correct. |
| same pass: colour fringe c0.x, lens dirt c12.w, heat-haze gate c14.w zeroed | three screen effects off | `2afa599` | No result credited. It has run only since `2a5ce5e5eda5`, together with the blur edit. Lens dirt has never been seen with or without it ("needs combat: not tried"). |
| `comp_*` composite gets the same six zeroes | lens dirt and fringe off when the final pass is `comp_*` | staging `864d0dc` | **Correction:** that commit's premise ("with HQDof=0 and PostEffects=0 the final picture is drawn by comp_*") is wrong. Run 4, with the hooks working, reads `comp_*=0` draws on every dof line, while `dof_*` draws about one per frame (11,900 by frame 14,100) `[measured 2026-10-15, n=1 run]`. With these settings the final picture is the `dof_*` composite (`dof_u2_ef`). The `comp_*` edit has never run. |
| pass census (draws per named pass) | diagnostic | `864d0dc` | Run 3 "every line read none, `comp_*` 0": already withdrawn as blind. Run 4 lists are real. |
| `madmax_vr_skip.txt` (leave a named pass out) | diagnostic | `864d0dc` | Run 3 "leaving out 27 passes (`comp*`, `tmonly*`) changed nothing": proves nothing, since the skip never fired. `comp*` would change nothing anyway, because it does not draw. **`tmonly*` has not been tested.** |

No draw hook existed in this mod before `2afa599`: the history shows no `PSSetShader`, `VSSetShader` or draw-method
hook earlier, in staging or in `dev-archive` `[measured 2026-10-15]`. So every result dated before 2026-10-15 is
unaffected by the blind hooks.

**Map / UpdateSubresource / bind-time (ran all along):** `[inferred-static 2026-10-15]`

- the shared V*P edit and the head-pose K (`unmap_shared_512`);
- the per-object edits on the 128- and 192-byte matrices, with the previous-frame edit (`cbfp_prev.c`);
- the ground-motion edit (`mvo_try`, at Unmap and on UpdateSubresource copies);
- SSAO (`ao_edit`);
- the sun shadow-origin edit and the PS `$Globals` camera-position edit (`sun_*`, at Unmap and on UpdateSubresource
  copies);
- the sun-ray edit (`ray_try`);
- the fill census;
- the bind census (`VS/PSSetConstantBuffers` and the `...1` variants).

They are keyed on buffer width and content shape, never on the bound shader. Their live results stand as recorded.
The dossier's "no 240-byte PS b1 is bound live; 256 is" comes from the bind census, so it stands too.

## 2. The jitter log names the runtime

`jl_init` now starts as `flat`. Once the OpenXR instance exists, `xrGetInstanceProperties` relabels the log
`openxr-<runtimeName>`: lowercased, any run of characters other than letters, digits and dots becomes one dash, 40
characters at most. The runtime's name and version also go to the proxy log. This keeps simulator runs and headset
runs apart in the BeG0nE logs. The label is checked offline on sample names:

- `OpenXR Simulator` gives `openxr-openxr-simulator`
- `SteamVR/OpenXR` gives `openxr-steamvr-openxr`
- `Oculus` gives `openxr-oculus`

The simulator's real `runtimeName` has not been seen yet. Build `dxgi.dll` `eb6f5ccee224`, staging `41e9415`,
self-test 236/236 `[compile-verified 2026-10-15]`.

## 3. Driving with the head turned (live note from the session, for the eye-lens plan)

Live note from the session: driving at a head yaw of plus or minus 20 degrees, the side the head turns toward loses
large parts of the ground (blue), and dark, hard-edged shadow slabs appear. At yaw 0 the picture is clean.

Most likely the game culls the terrain to its own frustum, and it also fits its shadow cascades to that same unturned
frustum. Ground on the turned side then lies outside every cascade. A wider game view widens both, so the eye-lens
build (`eye_hfov`, previous inbox file) should help both faults `[hypothesis]`.

With an 80-degree eye, a 20-degree turn needs a game hfov of at least 120. The 2026-09-04 slider range was measured
at 58 to 117, which is not enough. The Video Mode route reached about 157 and kept it into gameplay (dossier section
9b and 9c).
