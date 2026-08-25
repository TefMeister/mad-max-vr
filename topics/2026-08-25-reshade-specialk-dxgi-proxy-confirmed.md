# ReShade and Special K both confirm dxgi.dll-proxy injection as the working vector — plus GOG joins Origin as Denuvo-free

**Status:** 🆕 new · **Priority:** medium — a concrete, specific confirmation for
`ENGINE-DOSSIER.md` §4's injection-vector question, following up the previous sweep's vorpX finding.

## What was found

- **ReShade works against the Steam (Denuvo) build of Mad Max** via the standard proxy-DLL method:
  renaming `ReShade64.dll` to `dxgi.dll` and dropping it in the game folder — the ordinary
  DXGI-proxy loading trick this whole portfolio already favors as "more Denuvo-resistant than
  debugger-based approaches" (per the equivalent reasoning already recorded in the Burnout Paradise
  dossier). A dedicated "Mad Max Reshade Pro" preset mod exists on Nexus, and **Special K** — a more
  advanced overlay/injection framework that itself supports loading ReShade through its own plugin
  system — also lists Mad Max as supported. That's now **three independent tools** (vorpX, ReShade,
  Special K) confirmed working against this Denuvo-protected Steam build, on top of the AOB Cheat
  Engine table and native Capture Mode found in the same sweep — a strongly consistent picture that
  this game does not meaningfully resist standard D3D11-level hooking.
- **`dxgi.dll` is specifically the correct interception point** (not `d3d11.dll` or another proxy
  name) — useful, concrete detail for `ENGINE-DOSSIER.md` §4's "injection vector that works" field,
  since it confirms exactly which system DLL the game's loader resolves through first.
- **GOG's build of Mad Max also has no Denuvo**, alongside the previously-noted Origin/EA build —
  only the Steam release carries it. (Community discussion as recently as within the last couple of
  years still shows Denuvo present on Steam with no removal patch found in this search pass — treat
  it as still active on the installed Steam build, not something to assume has lapsed.) This refines
  the previous sweep's Denuvo topic rather than replacing it.
- Denuvo's offline-activation token for this game is stored at
  `Steam\userdata\<user-id>\234140\dbdata`, per community troubleshooting notes — background detail
  in case offline/activation-related crashes come up during dev testing, unrelated to the modding
  work itself.

## Why this matters

Confirms, with a specific and reusable technical detail (`dxgi.dll` proxy naming), exactly the kind
of injection foothold `ENGINE-DOSSIER.md` §4 is looking for — and stacks a third independent tool
onto the feasibility case built in the previous sweep (vorpX) and this sweep (the AOB cheat table,
which works via CE's own process-attach method rather than DLL proxying, but demonstrates the same
underlying point: this build doesn't resist third-party memory/DLL access).

## Concrete next step

When injection work starts, `dxgi.dll` proxy loading is the proven, low-risk starting point — try it
before more invasive approaches, consistent with this portfolio's general DXGI-proxy-first pattern.

## Sources

- https://wiki.special-k.info/en/SpecialK/Tools
- https://www.nexusmods.com/madmax/mods/182
- https://steamcommunity.com/app/234140/discussions/0/600766396226376603/
