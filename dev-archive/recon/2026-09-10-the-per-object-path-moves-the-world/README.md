# 2026-09-10 — the per-object path moves the world, and 368 never existed

Dev PC `DESKTOP-V8GTSIR`, `/lm`, five launches. Write-up:
`modding-notes/2026-09-10-the-per-object-path-moves-the-world-and-368-never-existed.md`.
Distilled: dossier §7d.

## Logs

| File | What it shows |
| --- | --- |
| `log-launch2-first-cut-census-menu-time.txt` | The first-cut census, sampling one buffer per width on first sight. Its lesson is negative and worth keeping: first sight is the **menu and the loading screen**, and the same widths read *affine* there and *projective* in the world. A census that samples once cannot decide anything. |
| `log-launch4-the-scored-census-names-the-widths.txt` | The scored census over 300 frames of gameplay. Names the per-object widths — 192 (130,200 candidates), 128 (87,000), 64 (20,100), 96 (18,000) — and shows **384 carrying a byte-identical copy of the shared main-pass matrix**. |
| `log-launch5-the-world-moves.txt` | The edit retargeted onto 192/128/96/64. `PER-OBJECT edited` goes from 0 to 21,999,140, with 2,828,972 `off-main-pass` refusals. |

## Screenshots

| File | What it proves |
| --- | --- |
| `shot-04-loaded.png` | The still scene every judgement below is made against — parked car, desert, HUD intact. |
| `shot-20-baseline.png` | Stereo OFF, immediately before the test. |
| `shot-21-stereo-on.png` | Stereo ON at the default 0.065 separation. Deliberately kept: at a human IPD the shift is **not** judgeable by eye, which is why the exaggeration step exists. |
| `shot-22-exaggerated.png` | Separation raised ~87x in wiggle mode. The whole scene swings across the frame. **This is the ⭐⭐ result.** |
| `shot-24-left-eye-moderate.png` | Single-eye mode, moderate separation — a steady sideways shift rather than a per-frame rock. Also the clearest evidence of the **HUD moving with the world**, which it should not: the minimap and health cluster have slid left. |
| `shot-25-settled.png` | The same view left to settle. The smear survives with the separation held still, so it is **not** motion blur — see the dossier on the pass latch. |

## The three things worth carrying to another project

1. **A size taken from shader reflection is a hypothesis about a name, not about an allocation.**
   `PEROBJ_SIZE` was 368 because reflection said so; the game never allocates 368 bytes. This
   project had already recorded the same mismatch once (a 512-byte layout with a 3136-byte runtime
   twin) and walked into it again anyway.
2. **One counter per refusal reason.** "Everything zero, including the refusals" is a different
   claim from "the edit was refused", and only the second sends you hunting for a latch bug.
3. **Run the cheap control first.** Switching the edit to the known-working path and watching its
   counter climb separated "my harness is broken" from "the target does not exist" in ninety
   seconds, before a single line was changed.
