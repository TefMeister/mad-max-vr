# The AA toggle has no reported temporal pass, and the 2024 fix strips an inside-car blur — two cheap controls for the smear row and the cockpit row

**Status:** 🆕 new · **Priority:** medium — it does not answer either row, but it hands each a
pre-launch control that costs nothing and separates "the game's own post chain" from "our latch"
before anyone chases a better pass discriminator.

## The question this speaks to

Dossier §7d (2026-09-10) lists, under *Not established*: "whether the smear is the latch or the
game's own temporal AA reacting to a moved world", and the board's second ⭐⭐ row carries the same
warning — *rule it out against the game's own temporal AA first*. That rule-out needs one fact
the dossier does not yet hold (§8: "Post / AA chain … not yet inspected live"): **does this game
have a temporal pass at all?**

## What the public record says about the anti-aliasing `[reported]`

- The in-game anti-aliasing option is a **two-state toggle** (Off / On). Every player description
  found calls the On state an FXAA-style single-frame post-process — "FXAA with no advanced
  options", blur on edges, flicker on thin geometry when moving — and the standard community
  workarounds are driver-side (DSR, control-panel AA, downsampling), which is what people reach for
  when the built-in AA is a cheap post filter rather than a temporal one.
- **No source found describes ghosting, trailing or smearing in the flat game.** For a title with a
  temporal history buffer that complaint is normally the first thing players report.
- The two stereoscopic fixes for this exact renderer (Helix/3Dmigoto 2015, geo-11 2024) list what
  they had to fix — shadows, bloom, decals, reflections, sparks and broken glass, maps, menus, HUD
  icons — and **nothing about a temporal-reprojection pass**, which a 3D Vision fix would have had
  to fight if one existed.

⚠️ **Provenance:** all of the above is player opinion and fix-author notes; no developer statement
naming the AA technique was found. The PCGamingWiki page for the game refused the automated fetch
(HTTP 403), so it is *unread*, not negative. And "no reported temporal AA" does **not** rule out a
temporal component elsewhere in a deferred renderer (SSAO or reflections with history). That is
exactly why the recommendation is a toggle test, not this note.

## What it buys the smear row

The cheap control, on the next launch that looks at the smear: in the game's own Video settings
set **Anti-Aliasing OFF** and **Motion Blur OFF** (both are ordinary menu toggles), then look
again in single-eye mode with the separation held still, as before.

- **Smear gone** ⇒ it was the game's post chain reacting to a moved world; the latch is off the hook
  for this symptom, and the fix is to leave the post chain unedited (or to key the edit off it).
- **Smear survives** ⇒ the game's two post toggles are cleared as causes, and the board's own
  `[hypothesis]` — inherited pass membership from the last shared write — is the remaining
  suspect. Chase the discriminator.

Either way the answer arrives before any code is written, which is the point.

## Second lead — the 2024 fix strips an "inside car" blur `[reported]`

The 2024 geo-11 fix's change list includes a **"clean inside car view"** item — i.e. the game
applies some screen effect in the in-car view that the fix author found worth removing for stereo.
The post does not say which effect (a blur or DOF layer is the natural reading; it is not stated).
For this project that matters twice over:

- §6c found that `V` is a shipped first-person cockpit camera and the board's cockpit row is
  waiting to measure it *under motion*. Whatever the "inside car" effect is, it will be in the
  picture during that run — **look for it deliberately**, because a full-screen blur in a
  headset is a comfort problem in its own right, separate from bob and FOV.
- The same fix repeats the 2015 requirement that the game's **Depth of Field be left at "normal"**
  (§11's not-yet-understood gotcha). It was still required against the last GOG build (v1.03), so
  the gotcha did not go away with a patch. Worth carrying into any cockpit run as a fixed setting.

## Third lead — the HUD is a depth-layer problem in the stereo fixes, not a separate path `[reported]`

The 2024 fix handles the HUD by pushing icons to a chosen depth (a key cycles the depth of
target icons and crosshair; another toggles the HUD off). That is how a fix treats HUD elements
that are **drawn as ordinary quads through the normal draw path**, not through a path the fix
could simply leave alone — consistent with §7d's finding that the minimap and health cluster
come through one of the four per-object widths. The cross-engine library already carries the
discriminator worth trying before the one-width-at-a-time elimination: *identify an orthographic
projection from the matrix, not from the draw* (`m32 == 0`, `m33 == 1`, so `w` stays 1) —
`flat-to-vr-cross-engine-research/docs/techniques/README.md`, "Two detection rules". If the HUD
draws' per-object matrices are orthographic, that test separates them at any width without a
rebuild per width. If they are projective (a 3D-placed HUD), the width elimination stands.

## Next step for the modding lane

1. Next smear-row launch: Anti-Aliasing OFF + Motion Blur OFF in Video settings first; read the
   smear; record which branch above it landed on.
2. Next cockpit launch: DOF at "normal"; note whether the in-car view carries a screen effect of
   its own.
3. Before rebuilding per width for the HUD: have the census print whether each edited matrix is
   orthographic; if the HUD widths are, key the refusal on that.

## Sources

- Helix Mod: *Mad Max [Geo11] [DX11]* (2024 fix post, Rubini building on DHR's 2015 fix) —
  https://helixmod.blogspot.com/2024/02/mad-max-geo11-dx11.html
- Helix Mod: *Mad Max (DX11)* (2015 fix post) — https://helixmod.blogspot.com/2015/10/mad-max-dx11.html
- Steam community discussions on the game's anti-aliasing (player reports, two threads) —
  https://steamcommunity.com/app/234140/discussions/0/527274088392961906/ and
  https://steamcommunity.com/app/234140/discussions/0/527274088391963459/
- Cross-engine library, orthographic-matrix detection rule —
  https://github.com/TefMeister/flat-to-vr-cross-engine-research/blob/main/docs/techniques/README.md

Nothing was downloaded and no fix text was copied; the mechanisms above are described from the
posts' own wording.
