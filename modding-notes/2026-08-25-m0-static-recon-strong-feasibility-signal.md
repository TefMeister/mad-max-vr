# 2026-08-25 — First look: this one looks genuinely promising

Session type: static file analysis (no game launch) plus reading a parallel research
session's findings, per our now-standard practice of checking `-external-research` fresh
before writing anything.

## What we know for sure

- **The renderer is Direct3D 11**, and — per developer interviews the research session
  found — it's confirmed to be the *only* renderer that shipped (a DX12 path existed only as
  unfinished R&D at the time).
- **The engine is Avalanche Engine**, using Havok for physics, Bink for video, FMOD for
  audio. Developer interviews also confirm this engine build is meaningfully different from
  Just Cause 3's later engine (classic deferred shading, 3 G-buffers, no PBR) — which is
  exactly why the popular Just Cause modding-tool ecosystem doesn't work on Mad Max.
- **A real developer console exists** in the exe (`invoke`/`set`/`get`/`variable_list`/
  `function_list` commands referenced directly in the binary's own strings) — not yet tested
  live, but a promising, low-risk thing to explore before any hooking work.
- **The exe is 64-bit** — a different build target than Burnout Paradise's 32-bit proxy DLL.

## The genuinely good news: this might be the easiest project in the portfolio so far

The research session found **four independent third-party tools already working against
this exact Steam build**: vorpX (with a real stereo-3D + head-tracking mode), ReShade,
Special K, and — best of all — a mature Cheat Engine table that already has a **directly
callable "change camera" function** plus FOV and camera-range control. On top of that, the
game ships its **own built-in camera tool** ("Capture Mode" → "Video Mode," `R` key) with an
FOV slider that can reportedly be carried into live gameplay. That's five independent signs,
before we've written a line of code, that the camera/projection system here is tractable.

## The one genuinely open question: does this game even have Denuvo?

Community reports (from the research session) say yes, the Steam release has Denuvo. But our
own direct check of the actual installed exe found **nothing** — no "Denuvo" string anywhere
in the binary (unlike Burnout Paradise, where it was completely unambiguous), and the exact
file the community named as Denuvo's local activation token doesn't exist on this install
either. Our best guess: this may be a case of "shipped with Denuvo, removed in a later patch"
— the same pattern documented industry-wide during Burnout Paradise's research. We're not
claiming certainty either way; this gets resolved for real the first time a debugger is
attached.

## Next step

Build a `dxgi.dll` proxy DLL — the community's ReShade/Special K precedent confirms this is
specifically the right DLL to proxy for this game (not `d3d11.dll`, which is what we used for
Burnout Paradise). Same from-scratch, log-and-forward approach as before, just retargeted to
64-bit and to `CreateDXGIFactory1` (the exact entry point this exe calls).

Full technical detail: `mad-max-vr-dev-archive`, `recon/2026-08-25-m0-static-recon/`.
Distilled reference: `mad-max-vr-engine-research`, `ENGINE-DOSSIER.md`.
