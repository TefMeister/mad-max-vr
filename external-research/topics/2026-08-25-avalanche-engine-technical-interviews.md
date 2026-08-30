# Developer interviews confirm the render pipeline shape: deferred shading, 3 G-buffers, shipped-D3D11/experimental-D3D12

**Status:** 🆕 new · **Priority:** medium — background/context for `ENGINE-DOSSIER.md` §2 (engine
lineage), §3 (renderer confirmation), and §8 (pass inventory); not a shortcut, but saves guessing.

## What was found

Two DSOGaming interviews with Avalanche Studios developers (around the Mad Max/Just Cause 3 era)
give concrete, developer-sourced technical detail about the Avalanche Engine as it existed for Mad
Max specifically — useful because it's primary-source (the actual engine team), not a fan guess:

- **Renderer confirmed shipped as Direct3D 11** (matches this project's Steam-build assumption and
  the independent ReShade/ReShade-mod confirmation in the companion injection topic). A DirectX 12
  pipeline is described as "in the works" / experimental at the time — **not** something that
  shipped in the released PC build, so §3 should record D3D11 as the confirmed, sole renderer for
  the shipping game, not entertain a DX12 path.
- **Classic deferred shading, 3 G-buffers**, explicitly *without* physically-based lighting (PBR
  support). This differs from Just Cause 3's later clustered-deferred, 4-G-buffer, PBR-capable
  architecture — the two engines are confirmed by the developers themselves to meaningfully diverge,
  not just be reskins of each other. This corroborates the previous sweep's finding that Just Cause
  -focused community tooling doesn't cover Mad Max: it's not just an oversight, the underlying engine
  genuinely differs.
- **A deferred lighting system supporting "hundreds of active light sources,"** with dynamic-shadow
  render prioritization that scales with hardware. Secondary/bounce-style illumination is
  approximated via a custom "filter and back-project the ground color" technique (described as
  creating a sun-halo effect) rather than true global illumination — useful context if this project
  ever needs to understand the lighting pass inventory (§8).
- **Transparency was deliberately de-prioritized** in Mad Max's deferred pipeline ("very little need
  for transparency anyway beyond particle effects") — worth remembering if a VR conversion needs to
  reason about which render passes use forward vs. deferred paths; particle effects are the
  documented exception.
- **Multi-level LOD** spanning "tens of kilometers down to centimeters," with geo-morphing terrain
  transitions — relevant context for the open-world driving game's likely streaming/LOD behavior,
  though not directly camera/projection-relevant.

## Why this matters for this project

None of this is camera/projection-delivery detail (§6/§7 remain fully open, as before) — but it
gives the modding session a credible, developer-confirmed mental model of the renderer's overall
shape before diving into live shader reflection, which should make interpreting what's found (e.g.
which G-buffer holds what, why a given pass looks the way it does) faster and less guesswork-driven.

## Concrete next step

Record D3D11-only (no DX12 in the shipped build) and the 3-G-buffer deferred shading shape directly
in `ENGINE-DOSSIER.md` §2/§3/§8 as developer-confirmed background, distinct from anything yet
verified by this project's own live inspection.

## Sources

- https://www.dsogaming.com/news/avalanche-details-differences-between-mad-max-just-cause-3-engines/
- https://www.dsogaming.com/interviews/avalanche-on-avalanche-engines-future-tech-features-dx12-dynamic-tessellation-plans/
