# A 2024 geo-11 fix exists for this game — and the public fix archive may name the `GlobalConstants` slots we are hunting by value

**Status:** 🆕 new · **Priority:** high — it points at the one open question §6/§7 currently has no
cheap answer to, and it updates prior art the dossier records as nine years old.

## The open question this is aimed at

`status/mad-max-vr.md`, 2026-09-01:

> **⚠️ Negative result that bounds the technique:** the shared per-frame buffer `GlobalConstants`
> (651 shaders) has **no recoverable member names** — its RDEF type record shows `Globals` is a raw
> **`float4[20]`** array the engine fills from C++, not a struct. A shared view matrix, if one exists,
> must be found **by value**, though reflection has narrowed it to ~20 slots in one named buffer.

Finding a matrix by value means a live run, a capture, and a pile of inference. There may be a
shortcut that needs none of it.

## Why a 3D fix is the natural place to look

A stereoscopic-3D fix for a D3D11 game **is, mechanically, a document about where that game keeps its
view and projection matrices.** It cannot be anything else: to shift geometry per eye, the fix has to
know which constant-buffer slot holds the transform, in which shaders, for which passes. Those facts
are written down in the fix's own shader-assembly patches and its `d3d11x.ini`, because that is the
form the fix takes.

The Mad Max fixes are exactly that, for this exact renderer. And they are **published as text in a
public repository** — the Helix/3Dmigoto fix archive — so they can be *read online* without cloning or
downloading anything, which is what this project's rules allow.

**The distinction that matters, and it is a real one:** reading a fix to learn **where this game
stores its view-projection** is learning a fact about the game we own. That is not the same as taking
someone's fix. Nothing may be copied — no shader text, no ini, no assembly — and any implementation
here must be our own. But *"`GlobalConstants` slot N is the view-projection"* is a fact about Mad Max,
and once known it is verified against our own reflection dump in minutes.

## What the prior art actually is, updated

The dossier and `topics/2026-08-25-helix-3dmigoto-stereo3d-fix-major-prior-art.md` record **DHR's
2015 fix** (86 shaders). That is no longer the current state `[reported 2026-09-01]`:

| | 2015 fix | 2024 fix |
| --- | --- | --- |
| Author | DHR | **Rubini**, building on DHR's |
| Target | the 2015 build | **GOG v1.03**, "the last game version" |
| Stack | 3Dmigoto | **geo-11 v0.6.182 + 3Dmigoto 1.3.16** |
| Latest revision | — | **V4, 2024-10-04** |
| Fixes listed | shadows, bloom, decals, reflections (per the earlier topic) | maps and menus, all HUD icons, reduced DOF, clean in-car view (no blur), damage effects (broken glass, sparks) |

Two things follow. First, **this game's stereo prior art is actively maintained into 2024**, not a
2015 artifact — a stronger feasibility signal than the dossier currently reflects. Second, the 2024
fix is built on **geo-11**, which the cross-engine library already documents as the modern
3D-Vision replacement — so the technique used is current, and the fix's per-pass list is a ready-made
inventory of which passes break under stereo in this exact renderer.

**Honest limit:** the fix's *blog post* is user-facing — hotkeys, autoconvergence, depth cycling — and
**names no constant-buffer slots, registers or shader hashes**. Checked directly, 2026-09-01. The
register-level detail, if it exists anywhere public, is in the fix package's own files in the archive,
not in the announcement.

## Concrete next steps

1. **Read the Mad Max fix's files in the public archive, online, in a browser** —
   `DarkStarSword/3d-fixes` is the canonical collection. Look for the `d3d11x.ini` and any shader
   patch that touches the world transform, and note **which constant buffer and which `float4` index**
   the fix reads a view or view-projection matrix from.
2. **Cross-check whatever that says against our own `dxbc-reflect.py` output** for `GlobalConstants`.
   Reflection has already narrowed the target to ~20 `float4` slots in one named buffer; a claimed
   index either matches a plausible matrix layout there or it does not, and either way the check is
   free and needs no launch.
3. If the archive turns out not to carry that detail, this costs an hour and the "find it by value"
   plan is unchanged.
4. Independently: **update §6/§8's prior-art note to the 2024 geo-11 fix**, and use its per-effect
   list (HUD icons, menus, maps, DOF, in-car blur, damage sparks) as the expected break-list for our
   own stereo work. Those are the passes that will need attention here, named by someone who fixed
   them on this renderer.

## Sources

- https://helixmod.blogspot.com/2024/02/mad-max-geo11-dx11.html
- https://helixmod.blogspot.com/2015/10/mad-max-dx11.html
- https://github.com/DarkStarSword/3d-fixes
- https://helixmod.blogspot.com/2017/04/collection-of-bookmarked-posts-related.html
