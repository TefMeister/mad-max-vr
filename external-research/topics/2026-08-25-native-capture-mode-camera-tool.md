# Mad Max ships a built-in "Capture Mode" with adjustable FOV — a native camera-exploration tool

**Status:** ✅ incorporated (2026-09-04) · **Priority:** medium-high — a concrete, zero-reverse-engineering entry point
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

---

## ✅ Outcome — tried live over two sessions (folded from `inbox/`, modding verdicts 2026-09-04 and 2026-09-04b)

**The lead paid off, and its black-box half is now finished.** Both readings this topic asked for
came back, and one of its community-sourced claims is contradicted for the obvious route.

### What Capture Mode turned out to be

A **real free camera**, reached from the pause menu → Log → CAPTURE MODE: arrows/WASD move it,
the mouse rotates it, `U`/`I` tilt, `Enter` captures, `R` opens Video Mode, `Esc` exits
`[verified-live 2026-09-04, n=1]`. Better than this topic predicted: **its camera writes the same
shared constant-buffer slot 9 and the same main-pass clip matrix that gameplay writes** — holding
`W` for 1.5 s moved the eye 6.34 units along the matrix's forward column. That makes it a still,
controllable testbed for per-eye rewrites of that constant, which is worth more to this project
than the FOV slider was.

### The FOV slider, measured

It edits **only the projection's two focal-scale columns and nothing else**: hfov 58.28° … 116.91°
(default 80.48°), vfov in lock-step at the window aspect, with the eye and the forward column
untouched `[measured 2026-09-04, n=6 dumps, 5 slider positions]`. That is exactly the pair a per-eye
projection rewrite scales, so **point 2 of "Why this matters" above is corroborated** — one central
FOV wired to a UI, not dozens of per-context constants.

Reaching it is **mouse-only**: click the CAMERA SETTINGS tab label, click the row label, then the
`<`/`>` arrows. Two sessions of keypress hunting found nothing; a screenshot settled it in one click.

### ❌ The "carries into live gameplay" claim — not by the `Esc` route

This topic reported, from community guides, that a custom FOV can be carried into first-person
driving gameplay. **The first gameplay dump after leaving Capture Mode with `Esc` reads the default
again** `[verified-live 2026-09-04, n=1]`. The specific route the guides describe (Video Mode `R`,
then a "show HUD" tab, then resume) **was not tried and is not disproved** — there is no tab by that
name among CAMERA / FILTERS / CAMERA SETTINGS / VIGNETTE. Treat the carry-into-gameplay claim as
`[reported]` and route-specific, not as a property of the slider.

The row stays open on the status board as a cheap optional test. **If a public source spells out the
exact tab and button, that is worth a drop** — it is the one part of this lead still unresolved.

The `V` first-person driving key (user-reported, config-backed in `settings.ini`) could not be
pressed in a car: the early-story garage car is a prop. Not a disproof either.

Modding write-ups: `modding-notes/2026-09-04-main-pass-matrix-verified-live-and-capture-mode-is-a-free-camera.md`
and `modding-notes/2026-09-04b-capture-mode-fov-slider-moves-the-projection-columns.md`; evidence
`dev-archive/recon/2026-09-04b-devpc-capture-mode-fov-slider/`.
