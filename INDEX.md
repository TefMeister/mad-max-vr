# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-25 | [MMConsole unlocks the dev console](topics/2026-08-25-mmconsole-unlocks-the-dev-console.md) | 🆕 new | A community thread-injection tool already exposes the exact `IConsoleCommand`/`invoke`/`set`/`get`/`variable_list`/`function_list` system our own static recon found — works on Steam; its GOG/Origin-only "dumper" feature is also indirect evidence for the Denuvo question. |
| 2026-08-25 | [Denuvo status update: recent reports](topics/2026-08-25-denuvo-status-update-recent-reports.md) | 🆕 new | Follow-up on our own M0 recon's Denuvo discrepancy — community reports as recent as Jan 2025 (incl. a Steam-vs-GOG performance complaint) still describe Denuvo as present on Steam; doesn't resolve the conflict but shifts the evidence weight. |
| 2026-08-25 | [FearLess AOB Cheat Table camera features](topics/2026-08-25-fearless-aob-cheat-table-camera-features.md) | 👀 reviewed | A mature, AOB-based Cheat Engine table already exposes Photo Mode camera range, FOV, aspect ratio, HUD removal, and a callable "change camera" game function — the strongest camera prior-art found so far. Factored into ENGINE-DOSSIER.md §6. |
| 2026-08-25 | [Avalanche Engine technical interviews](topics/2026-08-25-avalanche-engine-technical-interviews.md) | 👀 reviewed | Developer interviews confirm shipped D3D11 (DX12 was experimental/unshipped), classic deferred shading with 3 G-buffers, and real architectural divergence from Just Cause 3's engine — context for §2/§3/§8. Factored into all three sections. |
| 2026-08-25 | [ReShade/Special K dxgi.dll proxy confirmed](topics/2026-08-25-reshade-specialk-dxgi-proxy-confirmed.md) | 👀 reviewed | ReShade and Special K both hook Mad Max via dxgi.dll-proxy loading — a third independent tool confirming injection works. **Caveat found by our own M0 static recon the same day: our direct evidence (no "Denuvo" string, no dbdata activation file) conflicts with this topic's Denuvo-still-active claim — see ENGINE-DOSSIER.md §4 for the honest, unresolved writeup.** dxgi.dll proxy plan factored into §4 regardless. |
| 2026-08-25 | [Denuvo (Steam) + vorpX precedent](topics/2026-08-25-denuvo-and-vorpx-precedent.md) | 👀 reviewed | Steam build has Denuvo (Origin build doesn't), but vorpX already achieves real Geometry-3D stereo + head tracking against it — strong feasibility signal, contrasts favorably with Burnout Paradise's vorpX failure. Will factor into ENGINE-DOSSIER.md §4 once M0 recon confirms Denuvo presence directly. |
| 2026-08-25 | [Native Capture Mode camera tool](topics/2026-08-25-native-capture-mode-camera-tool.md) | 👀 reviewed | The game ships a built-in Video/Capture Mode with an adjustable FOV slider that can carry into live first-person driving — a zero-RE entry point for camera exploration. Noted for the first live session, not yet actionable (static recon phase). |
| 2026-08-25 | [Community camera/FOV mods](topics/2026-08-25-community-camera-fov-mods.md) | 👀 reviewed | Nexus/Steam Workshop mods already manipulate camera/FOV at runtime (mechanism undocumented); consistent "binocs/sniper/cinematics break it" pattern across sources hints at the camera system's structure. |
| 2026-08-25 | [Asset-modding ecosystem & Apex-tools gap](topics/2026-08-25-asset-modding-ecosystem-and-apex-tools-gap.md) | 👀 reviewed | Gibbed.MadMax + Mad Manager exist as Mad Max-specific asset tools; the generic Just Cause-focused Apex Engine tooling ecosystem does NOT cover Mad Max — don't assume it transfers. Not urgent, filed for later. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
