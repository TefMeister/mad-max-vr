# Modding verdict (2026-09-04b, dev PC `/lm`): the Capture Mode FOV slider edits only the projection's focal columns; the "carry into gameplay" claim is untested and the `Esc` route resets it

**Lead:** `topics/2026-08-25-native-capture-mode-camera-tool.md` (INDEX row "Native Capture Mode camera tool").
**Verdict:** the black-box part of the lead is now DONE and it paid off; one of its claims is contradicted for the obvious route.

- **The slider is real and it edits the shared main-pass matrix's two focal-scale columns and nothing else**
  — hfov 58.28° … 116.91° (default 80.48°), vfov in lock-step at the window aspect; eye and forward column
  untouched `[measured 2026-09-04, n=6 dumps, 5 slider positions]`. That is exactly the pair a per-eye
  projection rewrite scales, so the lead's "design signal" reading (one central FOV wired to a UI) is
  consistent with what the buffer shows.
- **Reaching it:** the CAMERA SETTINGS tab is mouse-only — click the tab label, click the row label, click
  the `<`/`>` arrows. (Two sessions of keypresses found nothing; the picture settled it in one click.)
- **"Carry the FOV into live gameplay": not by `Esc`.** The first gameplay dump after leaving Capture Mode
  reads the default again `[verified-live 2026-09-04, n=1]`. The route the topic describes (Video Mode `R`,
  then a "show HUD" tab, then resume) was not tried — there is no tab named that among CAMERA / FILTERS /
  CAMERA SETTINGS / VIGNETTE, and this save has no drivable car. Row kept open on the status board as a
  cheap optional test; if you find a source that spells out the exact tab/button, that is worth a drop.
- **The V first-person driving key** (user-reported, config-backed by `settings.ini`) could not be pressed in
  a car: the early-story garage car is a prop. Not a disproof.

Evidence: `dev-archive/recon/2026-09-04b-devpc-capture-mode-fov-slider/`; write-up
`modding-notes/2026-09-04b-capture-mode-fov-slider-moves-the-projection-columns.md`.
