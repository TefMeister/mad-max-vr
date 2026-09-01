# 2026-09-01 — Shader reflection off disk: Denuvo blocks the debugger, not the shaders

**Date:** 2026-09-01, dev machine. **The game was never launched** (a parallel session owns the
machine's one "game may run" slot). Static analysis of a shipped file; nothing modified.

**Result: the dossier's §6/§7 shader-reflection work can start without a debugger, a capture, or a
launch.** Denuvo makes this game impossible to attach to — that finding stands and is not
challenged here — but it protects the *executable*. The shaders are separate data, and they ship
with their reflection metadata intact.

---

## What is actually on disk

`Shaders_F.shader_bundle` (6.1 MB, loose in the game root) contains **1363 DXBC shaders, every one
of them with an `RDEF` chunk** — 1363 `RDEF`, 1363 `ISGN`, 1363 `SHEX`, 0 `SHDR` (so SM5/D3D11
throughout). RDEF is the reflection chunk: constant-buffer names, variable names, byte offsets and
sizes.

**84 distinct constant-buffer layouts.** The ones that matter, by how many shaders use them:

| Buffer | Shaders |
|---|---|
| `cbInstanceConsts` | 893 |
| `GlobalConstants` | 651 |
| `cbMaterialConsts` | 434 |
| `InstanceConsts` | 176 |
| `cbLightingConsts` | 114 |

## The named finding: a per-object World×ViewProjection

`[inferred-static 2026-09-01]` — read from the shipped bundle; not observed live.

```
cbuffer InstanceConsts                   size   368 bytes   (in 112 shaders)
    +0     WorldViewProjMatrix            64 bytes   <- 4x4
    +64    PointLights                   192 bytes
    +256   FaceNormal / DynamicLightMultiplier / LightSaturation / AmbientLightMultiplier
    +272   ColourMultiplier               16 bytes
    +288   SkyMaskProjMatrix              64 bytes   <- 4x4
    +352   ScaledUVs / AngleFade
```

So **Mad Max composes World×ViewProjection per object** and hands it over at **offset 0 of
`InstanceConsts`**, in at least 112 shaders. Other variants carry `SpotProjectionMatrix1..3`,
`SpotShadowMatrix1`, `PointlightProjectionMatrix1` — the shadow/light passes, useful mainly as
things *not* to touch. A handful of small `$Globals` buffers carry a plain `ViewProj` or
`WorldViewProj` at +0 (post/effect shaders).

## ⚠️ The important negative result: the shared per-frame buffer has no names

`GlobalConstants` is the obvious place for a shared view matrix, and it is used by 651 shaders. Its
reflection is:

```
cbuffer GlobalConstants   size 2352 bytes
    +0     Globals          272 bytes
    +272   LightPositions  1040 bytes
    +1312  LightColors     1040 bytes
```

Reading the RDEF **type** record for `Globals` shows it is not a struct at all — it is
`float4 Globals[20]`, class 1 (vector), 4 columns, 20 elements. **The engine builds this buffer as a
raw `float4` array in C++, so there are no member names to recover.** Same for the `InstanceConsts`
member inside `cbInstanceConsts`.

This is worth stating plainly because it bounds what this technique can do here: **reflection names
the per-object matrix but cannot name whatever lives inside `Globals[]`.** If a shared
view/projection exists, its index in that array has to be found by value — writing a probe that
watches `GlobalConstants` across frames and looks for a slot behaving like a view matrix (changes
when the camera moves, constant across draws within a frame). Reflection has narrowed that from
"somewhere in the renderer" to "one of 17–20 float4 slots in one named buffer", which is a very
different search.

## Why this matters beyond Mad Max

The project record says a debugger cannot attach to this game, full stop — three attempts, Denuvo
confirmed live. That closed off the usual route. **It does not close off shader work**, because
protection covers code, not the shader bundle sitting in the game folder.

New reusable tool: **`flat-to-vr-RE-toolkit/tools/dxbc-reflect.py`** (`list` / `find` / `summary`).
It scans for DXBC containers anywhere in a file rather than assuming an archive format, detects the
SM4-vs-SM5 variable-record stride rather than guessing (guessing wrong yields plausible garbage
names, not an error), and walks nested struct members.

```
python dxbc-reflect.py Shaders_F.shader_bundle summary
python dxbc-reflect.py Shaders_F.shader_bundle find "view|proj|camera"
```

**The bundle is not committed** — it is original game content. Only the tool and these findings are;
a constant-buffer layout is interface metadata, the same category as an export-name dump.

## Next, still no launch needed

1. Widen the sweep: enumerate every buffer containing a 64-byte matrix and classify passes by which
   buffers they bind — that builds most of dossier §8 (pass inventory) off disk.
2. Then, when a live session happens, the probe above for `Globals[]`.

🤖 Static analysis of a shipped shader bundle. The game was not launched and nothing was modified.
