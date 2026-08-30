# Mad Max ships a built-in "Capture Mode" with adjustable FOV — a native camera-exploration tool

**Status:** 🆕 new · **Priority:** medium-high — a concrete, zero-reverse-engineering entry point
for `ENGINE-DOSSIER.md` §6 (camera & projection) and §9 (cvar/console cheat sheet).

## What it is

Mad Max ships a developer-exposed, in-game **"Capture Mode"** (accessible from the main menu, or by
clicking both thumbsticks on a controller), which includes a **"Video Mode"** (opened with `R` on
keyboard / `Y` on controller) offering direct, first-class control over the camera — including an
adjustable **FOV slider** — plus the ability to toggle HUD visibility and, per community guides,
even carry a custom FOV setting *into actual first-person driving gameplay* (not just static
screenshots) by adjusting it in Video Mode, then switching to the "show HUD" tab and resuming play.

Community-documented limits: the custom FOV value resets when the camera changes, doesn't apply
while using binoculars/sniper rifle, and (in the screenshot-only path) the HUD is hidden.

## Why this matters for this project specifically

This is unusually good news for a project whose entire premise depends on understanding and
overriding the camera/projection system: **the developers already built and shipped a live,
player-facing camera/FOV control surface**, rather than this project needing to find one from
nothing. Concretely useful:

1. **A known-safe way to explore FOV/camera parameter ranges without touching game memory at all.**
   Before any hooking work starts, Capture Mode can be used (by the modding session, live, per this
   project's normal test protocol) to observe how far FOV can go, what breaks (HUD, binocs/sniper,
   cinematics per the community mod notes), and get a first empirical sense of the camera model —
   pure black-box observation, no injection risk.
2. **A strong hint that FOV/camera parameters are stored somewhere reasonably central and
   already wired to a UI**, rather than hardcoded per-context — the existence of a working slider
   that affects live first-person driving gameplay suggests one authoritative FOV value (or a small
   handful) rather than dozens of hardcoded per-camera-mode constants. Worth confirming, not
   assuming, once live investigation starts — but it's the kind of design signal worth testing for.
3. **Directly relevant to `ENGINE-DOSSIER.md` §9** (cvar/console cheat sheet) even if Capture Mode
   isn't a console/cvar system per se — it's the same category of "built-in dev-exposed control
   surface," worth recording there once its exact button/menu path is confirmed live.

## Concrete next step

During first-look reverse engineering, try Capture Mode → Video Mode first, before any hooking:
note the FOV range, what the mode does/doesn't affect, and whether toggling it while a debugger or
memory scanner is attached shows an obvious, single point of change (a promising lead for finding
the live camera/projection struct without needing shader reflection first).

## Sources

- https://steamcommunity.com/sharedfiles/filedetails/?id=917610216
- https://www.nexusmods.com/madmax/mods/21
