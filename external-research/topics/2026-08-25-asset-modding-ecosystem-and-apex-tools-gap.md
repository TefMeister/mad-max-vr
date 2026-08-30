# A Mad Max-specific asset-modding toolkit exists (Gibbed.MadMax, Mad Manager) — but the generic Apex Engine tooling ecosystem does not cover this game

**Status:** 🆕 new · **Priority:** low-medium — asset-format tooling isn't urgent for the camera/VR
work, but this closes off a plausible-looking shortcut before anyone wastes time chasing it, and
documents what does exist for later.

## The negative finding first (important — avoids wasted effort)

Mad Max shares its engine lineage with the Just Cause series and other Avalanche Studios titles
(the "Apex Engine" / Avalanche Engine family), and there is a substantial, actively-maintained
community toolkit ecosystem for that engine family — **[apex-tools-launcher](https://github.com/EonZeNx/apex-tools-launcher)**,
**[apex-tools](https://github.com/EonZeNx/apex-tools)**, **[deca](https://github.com/kk49/deca)**,
**[jc-model-renderer](https://github.com/aaronkirkham/jc-model-renderer)**, the
**[apex_engine_info wiki](https://github.com/kk49/apex_engine_info/wiki)**, and the
**[Apex Resource Index](https://eonzenx.github.io/apex-resource-index/)**. Checked directly: **none
of these currently document or claim support for Mad Max (2015)** — their coverage is explicitly
Just Cause 1–4, Generation Zero, and theHunter: Call of the Wild. Don't assume "same engine family"
means these tools work on Mad Max's files without verification; treat this as unconfirmed/likely-not
until someone actually tries one against a Mad Max archive.

## What actually exists for Mad Max specifically

- **[Gibbed.MadMax](https://github.com/gibbed/Gibbed.MadMax)** — a dedicated modding toolkit by
  "Gibbed" (Rick Hodgin), a long-established reverse-engineer/tool author across many game engines
  (Just Cause, Saints Row, Sonic, and others — a name worth recognizing elsewhere in this
  portfolio's research too). Includes at minimum a property-conversion utility and file-list
  rebuilding tooling, per its GitHub source tree — suggests it understands Mad Max's structured
  data/property format(s) at some level, though this research pass didn't get deep technical
  documentation of the exact archive/format specifics (Nexus Mods blocked automated access to the
  toolkit's own Nexus page, 403).
- **[Mad Manager](https://github.com/y0xOFF/Mad-Manager)** — a community mod manager for Mad Max.
  Mods are organized as `Mod_Main_folder/dropzone/<files>`; Mad Manager copies a mod's `dropzone`
  contents into the game's own equivalent folder when enabled, and removes them when disabled — a
  simple file-overlay approach, not a scripting/injection framework.
- **RESOREP** — referenced alongside Mad Max texture mods as a separate Java-based tool
  ("RESOREP.jar") for applying texture replacements, pointed at the game's `MadMax.exe`.
- Community mod taxonomy: **"RESOREP mods"** (texture swaps) vs. **"dropzone mods"** (gameplay
  mechanic tweaks) — the vocabulary itself confirms the community has a settled, if informal,
  understanding of at least two distinct mod-file mechanisms for this game.

## Why this matters for this project

Not urgent for the VR conversion's core work (camera/projection/stereo rendering doesn't need asset
formats), but useful to have on record for later:
- If the mod ever needs to read or reference level/vehicle data, Gibbed.MadMax is the starting point
  — not the generic Apex tools, which don't apply here.
- The "dropzone" file-overlay convention suggests Mad Max's own data loading already tolerates
  external file overrides in some capacity — worth keeping in mind as a possible lightweight
  alternative to full memory-patching for certain kinds of changes, though this is speculative and
  unconfirmed for anything camera/rendering-related specifically (the existing dropzone mods
  documented so far are gameplay/texture tweaks, not renderer changes).

## Concrete next step

No immediate action needed. Revisit Gibbed.MadMax and Mad Manager only if/when this project needs to
read or modify packaged game data directly; don't spend time evaluating the generic Just
Cause-focused Apex tools against Mad Max without first confirming (quickly, empirically) whether
they even open a Mad Max archive.

## Sources

- https://github.com/EonZeNx/apex-tools-launcher
- https://github.com/kk49/apex_engine_info/wiki
- https://eonzenx.github.io/apex-resource-index/
- https://github.com/gibbed/Gibbed.MadMax
- https://github.com/y0xOFF/Mad-Manager
