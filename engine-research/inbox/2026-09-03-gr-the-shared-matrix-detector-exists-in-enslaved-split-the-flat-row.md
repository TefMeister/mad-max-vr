# §6's "must be found by value" probe already exists in `enslaved-vr` — and most of the row is `[PD]`

**From:** `/gr` (2026-09-03, estate sweep)
**Topic:** [`external-research/topics/2026-09-03-the-detector-this-project-needs-is-already-built-in-enslaved.md`](../../external-research/topics/2026-09-03-the-detector-this-project-needs-is-already-built-in-enslaved.md)

## The dossier line

> if one exists it must be found by value (a probe watching `GlobalConstants` for a slot that changes
> with the camera but is constant across draws in a frame)

**That probe is built, validated and running in `enslaved-vr`** — its D3D9 proxy fingerprints each
matrix register per frame, flags any whose value is identical across all draws, and auto-dumps it as
a shared view-projection candidate. It was validated off-game before ever being pointed at the title.
Same question, same discriminator; only the API differs (D3D9 constant registers there, 20 `float4`
slots in one named D3D11 buffer here).

## Suggested board change — split the row, and most of it moves to `[PD]`

The row is currently `[FLAT]` because *"only a running game supplies values to compare"*. That is
true of the **comparison**, not of the **probe**:

- **`[PD]` — write the fingerprint pass now.** The `dxgi.dll` proxy is already built and
  live-verified (§4, 2026-08-25), so there is a proven place to put it. Hook the writes into
  `GlobalConstants` (`Map`/`Unmap` on a dynamic buffer, or `UpdateSubresource`), record all 20 slots
  per draw, and at frame end report which were byte-identical across every draw that bound it.
  Writable and compile-checkable with nothing running.
- **`[FLAT]` — one launch, which answers the question outright**, because the pass names its own
  candidates rather than producing data to analyse later.

## Three things worth copying, one worth avoiding

1. **Pre-commit both readings before the launch.** Enslaved's board says what each outcome means in
   advance — flagged ⇒ very likely the shared view-projection; nothing flagged ⇒ the camera is baked
   into per-object WVP and the plan shifts. That is what makes *one* launch sufficient. This project
   already knows its fallback: `InstanceConsts +0 WorldViewProjMatrix`, named by reflection in 112
   shaders.
2. **Fingerprint all 20 slots, not just matrix-shaped reads.** With no member names a 4×4 could begin
   at any of slots 0–16, and the shared value may not be a full view-projection at all. Per-slot
   constancy for the whole buffer costs nothing and avoids assuming the answer's shape.
3. **Print raw floats in buffer order; do not let the probe interpret layout.** ⚠️ This is the one
   Enslaved got wrong: its 2026-09-01 register layout was transposed and had to be `[disproved]` the
   next day against the game's own matrix in its log. A C++-filled D3D11 constant buffer carries no
   layout guarantee either, so the dump should stay uninterpreted and the reading should decide.

## Nothing public covers this

The public Mad Max prior art (geo-11/DX11 3D fixes, the 3Dmigoto archive) operates per shader — it
patches individual shaders' stereo behaviour and so never needed to name the engine's shared camera
constant. Apex/Avalanche community tooling is asset-side. §6's own reflection pass, which narrowed
this to ~20 slots in one named buffer, is already further than any public source reaches. What was
missing was a probe, not information — and the probe exists on this account.
