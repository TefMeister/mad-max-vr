# theHunter: Call of the Wild VR: native per-eye stereo on a sibling Avalanche engine, source readable

**Found:** 2026-09-23, `/gr` estate sweep, through phunkaeg's *VR Modding Playbook* (`sources.yml` →
`theHunterCotW-VR`, stereo rung R1 = the engine itself renders each eye).
**Source:** vaas993, *theHunterCotW-VR* — <https://github.com/vaas993/theHunterCotW-VR> (GPL-3.0,
last commit 2026-09-10; Nexus <https://www.nexusmods.com/thehuntercallofthewild/mods/1037>).
Read on GitHub only; nothing copied.

## What it is

A native OpenXR VR mod for theHunter: Call of the Wild, update 9.2. The author states the world is
drawn **from the game's own camera, once per eye**, with 6DoF and a weapon with real depth, not a
screen floating in a void `[reported]`. It loads through an **`XINPUT9_1_0.dll` proxy**, which avoids
fighting other mods over the graphics DLLs `[reported]`.

## Why it matters here

theHunter runs on **Apex**, the later name of the **Avalanche Engine** that Mad Max uses
`[reported]`. Our own interviews topic (2026-08-25) already warns that Mad Max diverged from Just
Cause 3's branch, so **nothing here is an offset to reuse** `[hypothesis]`. What transfers is the
*map*: which parts of an Avalanche-family renderer had to be found and fixed to reach true per-eye
rendering. Their source tree names them, by file: an Apex layout header with its own address table,
a camera probe, a constant-buffer scanner, a frame hook, head tracking, a per-eye TAA plan and a
TAA-replacement plan, recentring, 6DoF, and a separate tier-1 field-of-view plan `[reported]`.

Three points line up with our open rows:

1. **The smear.** Our ⭐⭐ row says the smear survives single-eye mode with the separation held still,
   so it is not motion blur. theHunter's notes name **TAA history as the prime suspect for shimmer**
   in this engine family and carry two separate plans for it (per-eye history, or replacement)
   `[reported]`. Worth reading `docs/TAA_PER_EYE_PLAN.md` before the pass-latch hunt, to see whether
   their symptom matches ours `[hypothesis]`.
2. **The HUD moving with the world.** The playbook's rule from another project (06
   `#the-report-is-an-instrument`, META-018): a per-eye edit **gated on perspective projection never
   reaches an orthographic HUD**, and vice versa. Our edit fires on four widths of matrix; if the
   HUD's matrix is orthographic, testing the projection's shape before editing is a one-condition
   way to leave the HUD alone `[hypothesis]`.
3. **The wide field of view.** Their `docs/TIER1_FOV_PLAN.md` and the playbook's lesson that
   **culling follows the game's FOV, not the headset's** bear on our "does the wide FOV survive a
   relaunch" row: a wide FOV that survives is also what keeps edge geometry from popping.

## Next step

Read, on GitHub, `docs/ARCHITECTURE.md` and `docs/FEATURES_AND_FINDINGS.md` in that repo and compare
their camera and frame-hook description with our dossier §6–7. Treat every match as a lead to test
on Mad Max, never as a fact about it.

## Credits

vaas993 (theHunterCotW-VR); phunkaeg (*VR Modding Playbook*).
