# /gr drop — two pre-launch controls: the AA toggle has no reported temporal pass; the 2024 fix strips an inside-car blur

**Speaks to:** `ENGINE-DOSSIER.md` §7d *"Not established: … whether the smear is the latch or the
game's own temporal AA reacting to a moved world"*; §8 *"Post / AA chain … not yet inspected
live"*; §6c / the board's cockpit-under-motion row; §11's Depth-of-Field gotcha.

**Topic:** `external-research/topics/2026-09-11-the-aa-toggle-has-no-reported-temporal-pass-and-the-2024-fix-strips-an-inside-car-blur.md`

## What was found `[reported]`

1. The game's anti-aliasing is a two-state toggle that every public description calls a
   single-frame FXAA-style post-process; no source reports ghosting or smearing in the flat game,
   and neither stereoscopic fix (2015, 2024) had to handle a temporal pass. Player opinion, no
   developer statement; PCGamingWiki refused the fetch (unread, not negative).
2. The 2024 geo-11 fix lists a "clean inside car view" change — the game applies some screen
   effect in the in-car view — and still requires DOF at "normal" against GOG v1.03.
3. The fixes treat HUD icons as a depth-layer problem (ordinary quads through the normal path),
   which fits §7d's "HUD comes through a per-object width".

## Suggested change (one or two sentences each)

- §7d *Not established*: add that the cheap discriminator is a launch with **Anti-Aliasing OFF
  and Motion Blur OFF** in Video settings — smear gone ⇒ post chain, smear survives ⇒ the latch
  hypothesis stands. No code needed.
- §6c / cockpit row: note that a game-applied in-car screen effect is reported and should be
  looked for during the under-motion run, with DOF held at "normal".
- §7d HUD problem: before rebuilding per width, try the library's orthographic-matrix test
  (`m32 == 0`, `m33 == 1`) on the edited per-object matrices; if the HUD widths are orthographic,
  refuse on that instead of on width.
