# The detector §6 asks for is already built and validated — in `enslaved-vr`

**Date:** 2026-09-03 · **Status:** 🆕 new · **Source:** a sibling project in this estate, not the open
web · **Answers:** the `[FLAT]` board row *"the shared view matrix, if one exists, has to be found BY
VALUE"*

## The gap this closes

§6's negative result is precise about what is needed and why reflection cannot supply it:

> `GlobalConstants` (651 shaders, 2352 bytes) has **no member names to recover**. Its RDEF type record
> shows `Globals` is `float4 Globals[20]` — a raw array the engine fills from C++ […] if one exists it
> must be found by value **(a probe watching `GlobalConstants` for a slot that changes with the camera
> but is constant across draws in a frame)**.

The board turns that into a `[FLAT]` row on the grounds that *"only a running game supplies values to
compare"*.

**That probe already exists, in working form, one repo over.** `enslaved-vr`'s D3D9 proxy was
upgraded to do exactly this: it *"fingerprints each matrix register per frame and flags any whose
value is identical across all draws, auto-dumping it as a SHARED view-projection candidate"* — and it
was **validated off-game** before ever being run against the title. `[compile-verified, per that
project's board]`

Same question, same discriminator, different API. Enslaved asks it of D3D9 vertex-shader constant
registers; Mad Max needs it asked of 20 `float4` slots in one named D3D11 constant buffer. The
*logic* — bucket by value across a frame, flag what does not vary per draw, dump the candidate — is
identical and does not care which API delivers the bytes.

## Why this changes the gate, not just the effort

The board reads the row as `[FLAT]` because comparing values needs a running game. True of the
*comparison*. **Not true of the probe.** Split the row and most of it moves:

- **`[PD]` — write the fingerprint pass.** Mad Max's `dxgi.dll` proxy is already built and
  **live-verified working** (§4, 2026-08-25), so there is a proven place to put it. The pass hooks
  the writes into `GlobalConstants` — `Map`/`Unmap` on a `D3D11_USAGE_DYNAMIC` buffer, or
  `UpdateSubresource` — records the 20 slots per draw, and at frame end reports which slots were
  byte-identical across every draw that bound the buffer. All of that is writable and
  compile-checkable with nothing running.
- **`[FLAT]` — one launch, and it answers the question outright.** Not "gather data and think about
  it later": the pass names its own candidates, exactly as Enslaved's does.

That is the same shape Enslaved used to go from "the camera is somewhere in the renderer" to a
named register, and it is why that project could act the moment a launch happened rather than
scheduling a second one to analyse the first.

## Two things to carry across, and one to be careful about

**Carry across:**

1. **Report the negative as loudly as the positive.** Enslaved's board pre-commits both readings —
   *"if flagged → very likely the pure view-projection […] if nothing is flagged → the camera is
   baked into per-object WVP and the plan shifts"*. Deciding what each outcome means **before** the
   launch is what makes one launch sufficient. Mad Max already knows its fallback: `InstanceConsts
   +0 WorldViewProjMatrix`, named by reflection in 112 shaders, is the per-object route if no shared
   slot exists.
2. **Fingerprint the whole buffer, not just matrix-shaped reads.** With no member names, a 4×4 could
   start at any of slots 0–16 — and it may not be a full view-projection at all. Recording all 20
   slots and reporting per-slot constancy costs nothing extra and avoids assuming the answer's shape.

**Be careful about:** Enslaved's version had to be corrected once, and the correction is instructive.
Its 2026-09-01 register layout *"turned out transposed and was disproved by the game's own `c231`
matrix in the log"* — the registers are **columns** (D3D9 HLSL's default `column_major` with
`mul(M,v)`), translation in the fourth. A D3D11 constant buffer filled from C++ carries no such
guarantee either way, so **the dump must print raw floats in buffer order** and let the reading
decide the layout. Do not have the probe pre-interpret rows and columns; that is precisely the step
that cost Enslaved a day.

## Why the value here is the estate, not the web

Nothing public answers this. The public Mad Max prior art (the geo-11/DX11 3D fixes, the 3Dmigoto
archive) works at the *shader* level — it patches individual shaders' stereo behaviour rather than
identifying the engine's shared camera constant, so it never had to name this buffer. The
Apex/Avalanche tooling ecosystem is asset-side. This project's own reflection pass already narrowed
the search to "one of ~20 slots in one named buffer", which is further than any public source gets.

**What was missing was not information but a probe** — and one exists, written for the same question,
already validated, in a repo on the same account. That is the finding.

## Sources

- `enslaved-vr` — `claude-memory/status/enslaved-vr.md` (the shared-matrix fingerprint upgrade, its
  off-game validation, the pre-committed if-flagged/if-not reading, and the transposed-layout
  correction of 2026-09-02) and that project's `engine-research/ENGINE-DOSSIER.md` §4.
- This project's own `engine-research/ENGINE-DOSSIER.md` §4 (the live-verified `dxgi.dll` proxy) and
  §6 (the `GlobalConstants` reflection negative that defines the search space).

## ✅ Outcome — acted on the same day (folded from `inbox/`, modding verdict 2026-09-03)

The split this topic argued for was made: **the `[PD]` half is done, the `[FLAT]` half is one launch.**
The `dxgi.dll` proxy now carries a constant-buffer fingerprint pass
(`staging/mad-max-vr/proxy-dxgi/src/cbfp.c`) — builds clean, exports unchanged
`[compile-verified 2026-09-03]`; its logic is tested offline against constructed ground truth by a
harness that includes the shipped source, 17 assertions passing
`[verified-numerically 2026-09-03, n=17]`; deployed to the game folder with a dated backup; **never
run against the game**. All three carried-over lessons were taken: both readings pre-committed in the
code, every slot fingerprinted, raw floats logged in buffer order with no layout interpretation.

**One correction this topic could not have known.** Re-running `dxbc-reflect.py` for the runtime
discriminator showed **`GlobalConstants` is two distinct layouts, not one**
`[inferred-static 2026-09-03]`:

| size | shaders | `Globals` extent | slots | trailing members |
| --- | --- | --- | --- | --- |
| 2,352 B | 465 | `[+0, 272]` | 17 float4 | `LightPositions`, `LightColors` |
| 512 B | 186 | `[+0, 320]` | 20 float4 | `ShadowTransform` (three 4×4s) |

465 + 186 = 651, the dossier's own shader count — same population, read more carefully. So
"fingerprint all 20 slots" is **17 in one buffer and 20 in the other**, and the probe watches both.
`ShadowTransform` makes the 512-byte layout very likely the shadow-pass variant, which matters when
reading a result off it. Dossier §6 is corrected; full write-up on the modding side:
`modding-notes/2026-09-03-constant-buffer-fingerprint-pass.md`.

## ✅ The `[FLAT]` half is closed too (folded from `inbox/`, modding verdict 2026-09-04)

The single launch this topic scoped has run. The shared per-pass clip transform is **verified live
at vertex-side `GlobalConstants` slots 0..3** — six byte-identical uploads per frame, each with
slot 4 == slot 9 — decomposing to hfov 80.5° / vfov 50.9° with the eye recovered from row 3
`[measured 2026-09-04, n=4]`. **All three of the lessons this topic carried over from `enslaved-vr`
paid off in the way it argued they would:** pre-committing both readings in the code made it a
single launch rather than a series; fingerprinting every slot is what caught the per-pass
structure; and dumping raw floats in buffer order with no layout interpretation is what made the
decomposition possible afterwards. Status stays ✅ incorporated — this closes its open half.
