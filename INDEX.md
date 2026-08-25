# Research index

Every research topic gathered for this project, newest first. Each row links to a self-contained
write-up in `topics/`. Status tags:

- 🆕 **new** — found, not yet acted on by the modding side.
- 👀 **reviewed** — a modding session has read it and factored it into a decision, but nothing shipped from it yet.
- ✅ **incorporated** — directly led to a real change (code, a test, a note) in one of the other five repos; linked below.
- ❌ **dead end** — checked out, didn't pan out; kept for the record so it isn't re-investigated from scratch.

| Date | Topic | Status | Summary |
| --- | --- | --- | --- |
| 2026-08-25 | [Denuvo (Steam) + vorpX precedent](topics/2026-08-25-denuvo-and-vorpx-precedent.md) | 🆕 new | Steam build has Denuvo (Origin build doesn't), but vorpX already achieves real Geometry-3D stereo + head tracking against it — strong feasibility signal, contrasts favorably with Burnout Paradise's vorpX failure. |
| 2026-08-25 | [Native Capture Mode camera tool](topics/2026-08-25-native-capture-mode-camera-tool.md) | 🆕 new | The game ships a built-in Video/Capture Mode with an adjustable FOV slider that can carry into live first-person driving — a zero-RE entry point for camera exploration. |
| 2026-08-25 | [Community camera/FOV mods](topics/2026-08-25-community-camera-fov-mods.md) | 🆕 new | Nexus/Steam Workshop mods already manipulate camera/FOV at runtime (mechanism undocumented); consistent "binocs/sniper/cinematics break it" pattern across sources hints at the camera system's structure. |
| 2026-08-25 | [Asset-modding ecosystem & Apex-tools gap](topics/2026-08-25-asset-modding-ecosystem-and-apex-tools-gap.md) | 🆕 new | Gibbed.MadMax + Mad Manager exist as Mad Max-specific asset tools; the generic Just Cause-focused Apex Engine tooling ecosystem does NOT cover Mad Max — don't assume it transfers. |

## How to add a topic

1. New file in `topics/`, named `YYYY-MM-DD-short-slug.md`.
2. One row added to the table above, newest at the top.
3. Update the status tag here as it moves through review → incorporated/dead-end (the modding side should update this when it acts on a lead, so the index reflects reality without the research side needing to poll).
