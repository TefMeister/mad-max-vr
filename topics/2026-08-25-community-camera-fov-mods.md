# A small but real community camera/FOV modding scene already exists for Mad Max

**Status:** 🆕 new · **Priority:** medium — supplementary prior art for `ENGINE-DOSSIER.md` §6.

## What exists

Beyond the built-in Capture Mode (see companion topic), independent community mods on Nexus Mods
and Steam Workshop already manipulate the camera and FOV at runtime, beyond what Capture Mode
exposes:

- **["FOV And Camera Tweaks"](https://www.nexusmods.com/madmax/mods/140)** (Nexus) — changes FOV and
  "tweaks various camera properties, multiple options," disables camera auto-centering for vehicle/
  harpoon/enemies, offers a static car-cam option, and includes an **experimental first-person mode**
  (with an optional "hardcore" first-person-combat variant). The author's own notes flag it as
  unfinished/buggy ("many issues with this mode, I don't intend to put any more work into this"),
  and cinematics/some animations are unaffected by it — useful as a signal of *what's hard* here
  (an incomplete first-person conversion attempt is itself informative: it suggests the camera
  system has friction points around cinematics/animation-driven camera state that a from-scratch
  VR conversion will also need to handle).
- **["Field of View (FOV) Changer"](https://www.nexusmods.com/madmax/mods/21)** — simpler, dedicated
  FOV-only mod: `F1` to toggle, numpad +/- to adjust, overrides binocular/sniper zoom (i.e. the same
  FOV-doesn't-apply-during-scoped-views friction Capture Mode also has — corroborating evidence this
  is a real, consistent engine behavior rather than mod-specific).
- **Steam Workshop** also hosts camera mods directly, e.g. "Adjusted 3rd person camera (far)" (changes
  third-person camera distance, first/third-person switching unaffected) and a "Camera Options" mod
  described as integrating with a **"Mod Manager"/in-game "Mod Options" tab** (see the companion
  asset-modding-tooling topic for what that mod-manager ecosystem is).

## What's *not* documented

None of the above sources publish their technical mechanism (config value vs. runtime memory patch
vs. DLL injection) in any page this research pass could access — Nexus Mods blocks automated
fetching (403), and Steam discussion threads that reference these mods don't explain the "how,"
only the "what." This should be treated as genuinely unknown, not assumed to be either simple config
edits or complex hooking, until someone (with authorization to actually run the game) opens one of
these mod packages and looks.

## Why this matters

Confirms, independently of Capture Mode, that camera/FOV state is externally reachable at runtime by
third parties without the developer's cooperation — consistent with the vorpX precedent (companion
topic) that this engine doesn't present unusual resistance to camera manipulation. The recurring
"binoculars/sniper break it" and "cinematics unaffected" pattern across three independent sources
(Capture Mode, the FOV Changer mod, the FOV And Camera Tweaks mod) is worth treating as a reliable
signal about how the camera system is actually structured (context-specific camera modes that don't
all share one code path), not coincidence.

## Concrete next step

If/when this project needs an early proof-of-concept before fully solving §6/§7 from scratch,
downloading and inspecting one of these mods' actual package (once the modding session — not this
research session — is authorized to do so, per this project's own tooling/injection plan, not by
reusing the mod's files in this project) could shortcut discovering the FOV/camera memory location.
Until then, treat this as a corroborating signal, not a solved problem.

## Sources

- https://www.nexusmods.com/madmax/mods/140
- https://www.nexusmods.com/madmax/mods/21
- https://steamcommunity.com/sharedfiles/filedetails/?id=818553969
- https://steamcommunity.com/sharedfiles/filedetails/?id=2996466468
