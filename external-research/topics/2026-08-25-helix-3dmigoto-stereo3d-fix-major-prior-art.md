# A real, working 3Dmigoto stereo-3D shader fix already exists for Mad Max's exact D3D11 renderer — the single best camera/projection prior art found for this project so far

**Status:** 🆕 new · **Priority:** very high — this is a materially bigger find than the previous
stereo-3D topic filed for Burnout Paradise (where no Remastered-specific fix existed at all).
Directly targets `ENGINE-DOSSIER.md` §6/§7 (camera & projection delivery, the dossier's own
"crucial section") and §8 (pass inventory), and adds a second confirmed injection vector to §4.

## What exists

**[Helix Mod: Mad Max (DX11)](https://helixmod.blogspot.com/2015/10/mad-max-dx11.html)** is a
published, working NVIDIA 3D Vision stereoscopic fix built on **3DMigoto** — the same D3D11
shader-hooking/constant-buffer framework already identified as "the right tool class" for this
project in the previous sweep's Burnout Paradise research. Unlike that Burnout Paradise finding
(where no one had done this work for the D3D11 Remastered build), **this fix targets the exact
engine and renderer this project cares about**: Mad Max's shipped D3D11 pipeline. The fix's own
public GitHub mirror (**ThreeDeeJay/3d_fixes**, `Mad Max/` folder — the same collection family
DarkStarSword, credited in the previous sweep as the reference 3Dmigoto maintainer, personally
contributed fixes to) shows its real scope: **86 individual shader-override files (54 pixel
shaders, 32 vertex shaders)**, each named by the shader's own hash — i.e., 86 distinct shaders in
Mad Max's D3D11 pipeline have already been identified, targeted, and patched by a third party.
That is direct, concrete evidence of how large and how tractable this engine's shader surface is
for exactly the kind of "find and hook the shader that reads the view/projection matrix" work
`ENGINE-DOSSIER.md` §6 needs.

## Technical detail from the fix's own writeup

- **Handles per-render-pass depth/stereo issues individually**, not with one global transform:
  documented fixes cover shadows/lighting, lens-flare separation, fire-effect "halo" reduction
  (bright fire elements causing eye strain in stereo), decal depth, and skybox/sun stereo
  separation. This is a real, itemized pass inventory for §8 — someone has already had to reason
  about each of these render targets individually to get stereo right, which is exactly the kind
  of breakdown this project's own §8 will eventually need (through a different technical means —
  true per-eye VR rendering rather than 3D-Vision's projection trick — but the *render-pass
  taxonomy itself transfers directly*).
- **HUD/UI is handled as a separate depth-plane problem**, with runtime hotkeys: target icons/
  crosshair depth cycles via `P`, full HUD toggle via `L`, and a manual convergence/depth-offset
  adjustment via `O`. The author's own comment ("those iniparams x and y, same as the HUD
  MOD...so will take more time to change") confirms this is done via **3DMigoto's `IniParams`
  mechanism** — runtime-adjustable shader constants exposed through the config file rather than
  fixed at compile time — a concrete, reusable pattern worth understanding for this project's own
  camera/UI-depth override work, independent of 3D Vision specifically.
- **A real gotcha, worth remembering early**: the game's own **Depth of Field setting must be left
  at "normal"** — other DOF settings reportedly cause landscape depth *inversion* in stereo. This
  is a concrete, actionable warning: whatever post-processing/DOF pass Mad Max runs interacts with
  depth/stereo in a fragile, non-obvious way, and is worth testing early rather than discovering
  mid-project.
- **The fix proxies via `d3d11.dll`, not `dxgi.dll`** (per the public repo's file listing:
  `d3d11.dll`, `d3dcompiler_46.dll`, `nvapi64.dll`, `d3dx.ini` sit alongside the `ShaderFixes/`
  folder). This is a **second, independently-confirmed injection point** for this exact game,
  complementing the `dxgi.dll` proxy this project's own M0 work already live-verified — useful to
  know both are viable if one ever needs revisiting (e.g. if shader-level hooking specifically
  requires being resident at the `d3d11.dll` boundary rather than `dxgi.dll`'s).
- Compatibility notes (driver/Windows-version fragility, a specific "Compatibility Mode
  (Ctrl+Alt+F11) must be disabled" requirement) are 3D-Vision/NVAPI-specific and **won't transfer**
  to a headset-based VR approach — flagged so no one wastes time chasing those specific quirks.

## Why this is the standout finding of this sweep

Every previous lead (vorpX, ReShade/Special K, the AOB cheat table, native Capture Mode) established
that camera/FOV/injection is *reachable*. This is the first source that shows someone has actually
gone **shader-by-shader through this exact D3D11 binary and made per-eye-relevant modifications
stick**, at real scale (86 shaders), with a documented render-pass breakdown. It doesn't hand this
project the exact camera/projection constant-buffer answer (§6/§7 still need this project's own
live shader-reflection work — 3D Vision's projection-shift technique isn't the same problem as true
per-eye VR rendering, and no cbuffer slot/offset/handedness specifics were published in what this
pass could access), but it substantially de-risks the *scope* of that work: the shader surface is
finite, individually addressable, and a third party already proved it's not defended against this
class of analysis.

## Concrete next step

When shader-reflection work on `MadMax.exe` begins (§6/§7), treat this fix's existence and public
repo (file/shader-hash listing only — never its actual shader code, per this project's "write our
own code" policy) as a scope-and-feasibility reference, and consider evaluating `d3d11.dll`-level
proxying as an alternative/complement to the already-proven `dxgi.dll` proxy if shader-call
interception specifically is needed. Also record the DOF="normal" stereo-depth-inversion gotcha in
`ENGINE-DOSSIER.md` §8 as an early warning, even though its underlying cause (and relevance to a
true-VR approach vs. 3D-Vision's technique) isn't yet understood.

## Sources

- https://helixmod.blogspot.com/2015/10/mad-max-dx11.html
- https://github.com/ThreeDeeJay/3d_fixes (Mad Max folder)
- https://github.com/DarkStarSword/3d-fixes
