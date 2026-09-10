# 2026-09-10 — The per-object path DOES move the world, and the buffer we were editing never existed

Dev PC `DESKTOP-V8GTSIR`, `/lm`, five launches, all mine, every one closed through the game's own
menus with no `taskkill`.

Evidence: `dev-archive/recon/2026-09-10-the-per-object-path-moves-the-world/` (three proxy logs,
six screenshots). Distilled into the dossier.

---

## The headline

**⭐⭐ The per-object write site IS the on-screen transform.** Editing it moves the world, visibly
and unmistakably. That is the result this project's whole camera line has been waiting for since
the shared path was closed on 2026-09-08.

It took four launches to get there, because the row's premise was wrong in a way nobody had
checked.

## Why the queued launch could not have worked

The board said "the per-object edit is built and deployed — one launch says whether the world
moves". The launch said something better: **`PER-OBJECT edited=0`, and every refusal counter also
0.** Not refused. Never attempted.

The reason is in the proxy's own census, and it is embarrassing in a useful way:

**`PEROBJ_SIZE` was 368 bytes, and this game never allocates a 368-byte constant buffer. Not once,
in over 22,000 frames of real gameplay** `[verified-live 2026-09-10, n=1 session]`.

368 came from **shader reflection** — S6b named `InstanceConsts` at 368 bytes across 112 shaders.
But this file already records the same mismatch once, in `g_tracked_sizes`: the 512-byte
reflection layout has a **3136-byte runtime twin**. So on this engine a reflection size is not a
runtime size, and matching a buffer by a reflection-derived byte width was never sound. We had
written the counter-example down and then walked into it again.

⚠️ **The counters are what made this readable at all.** "Everything zero, including the refusals"
is a different statement from "the edit was refused", and only the second would have sent us
hunting for a latch bug. Whoever added a separate counter per refusal reason saved this session.

## The control that made it decisive

Before changing anything: switch the path to SHARED with `NUMPAD0` and watch.

```
PER-OBJECT edited=0      (unchanged)
SHARED     edited=2217   (climbing)
```

`[verified-live 2026-09-10, n=1 launch]`. So the hotkeys land, the hook is alive, the edit
machinery works — and the per-object path specifically sees nothing. That separated "my harness is
broken" from "the target does not exist" in about ninety seconds, and it is worth doing first
every time.

## Measuring the right buffer instead of guessing another size

Rather than try 384 and then 336 and then 480, the proxy got a **candidate census**: score every
mapped constant buffer against the shape of a real object→clip matrix, and let the numbers name
the buffer.

Two things had to be right about it, and the first cut got one of them wrong:

1. **Sample at `Unmap`, never at `Map`.** These buffers are mapped `D3D11_MAP_WRITE_DISCARD`, so
   at `Map` time the contents are undefined by specification — and undefined in the most dangerous
   way, because it still looks like data.
2. **Sample in GAMEPLAY, not on first sight.** The first cut dumped one buffer per width the first
   time it saw it, and first sight is the menu and the loading screen. The same widths read
   *affine* there and *projective* in the world. Fixed by re-arming the census on the dump hotkey,
   so pressing it in gameplay re-samples everything against what is actually on screen.

The predicate is three properties of the shared main-pass matrix we already have live: the last
column is not `(0,0,0,1)` (which is what rules out an affine object→world matrix, the commonest
false positive); rows 0..2 are a bounded non-degenerate basis; and row 3 is a **world-scale**
translation, because the camera sits thousands of units from the world origin. It is a filter for
a human, not a decision — it counts candidates per width and prints one example each.

## What it found

Over 300 frames of gameplay `[verified-live 2026-09-10, n=1 session]`:

| width | buffers unmapped | object→clip-shaped | bind census |
| ---: | ---: | ---: | --- |
| **192** | 197,128 | **130,200** | `VS-b1` 75,728 + `VS-b3` 68,937 |
| **128** | 182,700 | **87,000** | `VS-b1`, `VS-b3` |
| **384** | 25,023 | 21,723 | `VS-b1` 38,410 |
| **64** | 248,475 | **20,100** | `VS-b1`, `VS-b2` |
| **96** | 104,665 | **18,000** | `VS-b1` 94,845 |
| 256, 768, 480, 624, 1392, 3792, 7632, 8112, 8208, 9024 | — | **0** | — |

The four kept show **different translations per buffer** — `(-92.4, 73.5)`, `(-108.4, 84.1)`,
`(-134.2, 71.0)` — while sharing `m[14] = 0.0992` to four decimals. Different objects, one camera.
That is exactly what a per-object object→clip matrix looks like.

**⭐ And 384 is the most interesting of the five, which is why it is EXCLUDED.** Its rows 1..3 are
byte-identical to the shared 512-byte main-pass matrix — `-5789.70361, -1519.87537, 0.11118,
-4465.60254`. It is the camera's own viewProj, copied into a second buffer. Editing it would
double-apply against the shared path and make any result uninterpretable.

## The result

Retargeted onto 192/128/96/64, with a separate counter per width so a bad result stays readable:

```
PER-OBJECT edited=21,999,140 | refused: off-main-pass=2,828,972  no-shared-w=0  bad-matrix=0
  width 192 edited=6,511,536
  width 128 edited=5,853,045
  width  96 edited=1,741,557
  width  64 edited=7,893,002
```

From exactly 0. And **the world moves** — at an exaggerated separation the whole scene swings
across the frame, and in single-eye mode it shifts steadily sideways `[verified-live 2026-09-10,
n=1 session]`. Judged by eye against a still scene, as the board asked. Screenshots
`shot-20-baseline`, `shot-22-exaggerated`, `shot-24-left-eye-moderate`.

## Two problems the result immediately hands us

Both were predicted by the board's own reading table, which is a good sign for the table.

- **⚠️ The HUD moves with the world.** The board said it must not — the HUD "does not come through
  this buffer". It does come through at least one of the four widths: the minimap and the
  health/weapon cluster slide left with the scene. So widening to four bought the world and a UI
  regression together. **The per-width counters are exactly how to narrow it**: rebuild with one
  width at a time and look. `192` alone is the obvious first try, being both the top scorer and
  the most heavily VS-bound.
- **⚠️ A persistent smear that is not motion blur.** It survives in single-eye mode with the
  separation held still, so it is not the wiggle. The likely cause is the one the code already
  flags as an untested `[hypothesis]`: pass membership is **inherited** from the most recent
  shared-buffer write (`slot 4 == slot 9`), because per-object buffers carry no main-pass
  discriminator of their own. 2,828,972 `off-main-pass` refusals say the latch is doing real work;
  the smear says it is not doing it accurately enough, and some passes are getting an edit that
  disagrees with their neighbours. That is a better pass discriminator, not a different write site
  — which is precisely the branch the board wrote down in advance.

## What is NOT established

- Which of the four widths carries the HUD. Nobody has tried one width at a time yet.
- Whether the smear is the pass latch or the game's own temporal AA reacting to a moved world.
  Single-eye mode narrows it but does not settle it.
- Whether the shift is geometrically *correct* for a given separation — nothing has been measured,
  only seen. A real IPD in real world units still has to be calibrated.
- Whether 384 (the copied viewProj) is read by anything that matters. It was excluded on the
  reasonable grounds of avoiding a double-apply, not because it was shown to be inert.

## Automation scorecard

| Capability | State |
| --- | --- |
| 1. Self-launch | ✅ Steam appid 234140, five times |
| 2. Menu → gameplay | ✅ title → RESUME GAME (highlight verified every time) → world |
| 3. Commands | ✅ the proxy's own numpad hotkeys, driven with non-extended scancodes |
| 4. Character + camera | not exercised — this row needed a still scene, not movement |
| 5. Self-close | ✅ five times, through the game's own pause → EXIT TO MAIN MENU → EXIT GAME, every committing step verified by screenshot first. No `taskkill`. |

⚠️ Hold duration matters on this game: 250–300 ms holds, not taps. And NumLock was forced ON at
session start so numpad scancodes arrive as numpad VKs.

## Builds

All reproducible byte-for-byte across back-to-back links.

| sha256 | bytes | what |
| --- | --- | --- |
| `395cc037…` | 247,808 | first-cut census (one sample per width) |
| `9bfb29fe…` | 247,808 | census re-arms on the dump hotkey |
| `97969c28…` | 249,344 | scoring census over a 300-frame window |
| `8eb6649e…` | 249,856 | **per-object edit retargeted onto 192/128/96/64** — deployed and stamped |

Previous install kept as `dxgi.dll.bak-2026-09-10-was-245760-pre-probe`. Self-test 71/71 after
every edit.
