# The FOV carry-into-gameplay route names a tab and a key — and a precondition that may gate it

Filed by: `/gr` (estate sweep, second pass 2026-09-04), for the modding lane.
Topic: `external-research/topics/2026-09-04-the-fov-carry-route-is-video-mode-and-enter-not-esc.md`

## The dossier/board item this addresses

The board's `[FLAT]` row asks: *"does any Capture Mode route carry the FOV into gameplay? `Esc` does
not (80.48° back at once `[verified-live 2026-09-04b, n=1]`); the community claim names Video Mode
(`R`) then a 'show HUD' tab then resume."* The 2026-09-04b write-up recorded that no tab by that
name exists among CAMERA / FILTERS / CAMERA SETTINGS / VIGNETTE, and asked for a source naming the
exact tab and button.

## What the source says

Cole Wolfsson's Steam guide gives the route as `[reported]`: Capture Mode → **Video Mode, `R`** →
raise FOV on the **camera settings** tab → switch to the **show HUD** tab → **`Enter`** (or `A`) "to
start playing with an increased FOV" → `V` for first person while driving.

**The step that was missing is `R`.** The "show HUD" tab is inside Video Mode, which is a different
screen from the still Capture Mode whose four tabs the session enumerated — so the row's negative is
a negative about `Esc`, not about the claim. **The resume key is `Enter`, not `Esc`**, and on this
reading they are different actions: `Esc` cancels and restores, `Enter` resumes carrying the state.

## ⚠️ Check this first, it gates the test

The FRAMED screenshot-community guide states `[reported]`: *"The built-in Photo Mode has a Video
Mode feature that is enabled when two controllers are connected."* If that holds on this build,
Video Mode cannot be opened on a keyboard-only machine at all, and two sessions of fruitless
keypressing are the expected outcome rather than a mystery. One pad-count check settles it before
any dumping.

## Suggested dossier change

§9 (control surfaces) can now record the Capture Mode path in full, which the 2026-08-25 topic said
should happen "once its exact button/menu path is confirmed live" — with the confirmation still
owed, since all of the above is `[reported]`, not ours. Suggested wording: the still mode's four
tabs and mouse-only navigation are `[verified-live 2026-09-04]`; the Video-Mode branch, its show-HUD
tab, the `Enter` resume and the two-controller precondition are `[reported]` and each becomes
`[verified-live]` or `[disproved]` on the next flat run.

Two further `[reported]` details worth a line in §9: photo mode also opens on **`X`+`C`** or the
`<`/`>` keys, and the **HUD toggle is `CAPS LOCK` or `>`**.

## One thing deliberately not done

The FRAMED guide links a public Cheat Engine table advertising *"Photo Mode Camera range, FOV
Control, Custom Aspect Ratios, Timeflow control, Function call handler, Cheats"*. **It was not
downloaded and must not be** — study-online-only, nothing copied. It is cited in the topic purely as
an independent existence claim: someone else found the photo-mode camera range, FOV and aspect ratio
runtime-reachable, and "Custom Aspect Ratios" is the same family of edit the per-eye projection
rewrite makes.
