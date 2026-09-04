# 2026-09-04 (`/lm`, home PC, FULLY AUTONOMOUS) — the main-pass camera matrix is VERIFIED LIVE at vertex-side slots 0..3, the stage split is confirmed, and Capture Mode IS a free camera that drives the same matrix

**One launch, four answers.** The user launched the game and left it in the Graphics settings
screen; Claude backed out to the main menu, resumed the save, fired the `NUMPAD3` dump twice,
re-ran the `NUMPAD4`/`NUMPAD5` A/B, opened the pause menu, entered Capture Mode, moved its
camera, and dumped twice more. The game was left running, parked in Capture Mode (nothing here
needs a relaunch).

Build under test: `staging 4533ec9`, `Mad Max\dxgi.dll` 237,056 B (2026-09-03c). Windowed
1920×1080. Evidence: `dev-archive/recon/2026-09-04-main-pass-matrix-live-and-capture-mode/`
(filtered proxy log — the per-300-frame census lines stripped, every dump and A/B kept — plus
four 960×540 screenshots).

---

## 1. In plain words

Yesterday's static work said: the camera matrix should be at slots 0..3 of the vertex-side shared
buffer, written once per rendering pass, and the two puzzling buffer sizes should turn out to be
the vertex half and the pixel half of the same thing. Both pre-committed readings came back true
on the first dump, and the "bonus" row — is the pause menu's Capture Mode a free camera? — came
back true as well, with a twist that matters: **moving the Capture Mode camera moves exactly the
same matrix and camera-position slot that gameplay uses.** So the game ships a free camera that
feeds the very constant a VR patch has to rewrite, which makes it a ready-made testbed for
head-pose experiments without any of our own camera code.

The matrix also decomposes cleanly by hand: the horizontal field of view is 80.5°, vertical
50.9°, the 16:9 aspect falls out to four decimals, and the camera position is recovered from the
translation row to the centimetre. That is what a real view-projection looks like; a coincidence
does not do that.

## 2. The stage split — outcome (1), confirmed

```
cbfp bind: first sighting VS b0 <- 512-byte constant buffer  (tracked GlobalConstants candidate)
cbfp bind: first sighting PS b0 <- 3136-byte constant buffer (tracked GlobalConstants candidate)
```

`[verified-live 2026-09-04, n=1 launch]` — first sightings within 1 ms of each other, and the
bind census holds `VS-b0:512` and `PS-b0:3136` at identical counts all session (827 = 827 at
every census). `PS b0 <- 2352` never appeared. The 2026-09-03c `[hypothesis]` "3136 is the
pixel-side allocation of the 2352-byte declared layout" is now `[verified-live 2026-09-04]` as to
*where it binds*; the internal layout past slot 17 is still uninterpreted.

## 3. The per-write dump — outcome (2b): several writes, identical rows

Gameplay frame, standing still in the garage, 14 writes of the 512-byte buffer in the frame:

| write | slot 4 == slot 9? | what it looks like |
| --- | --- | --- |
| 0, 1, 2 | no | three orthographic-scale matrices (row magnitudes 0.035 / 0.0088 / 0.0018, identical rotation rows, sun-fixed): the **cascaded shadow maps**. Their rows 0..2 were byte-identical across both gameplay dumps while row 3 tracked the camera. `[measured 2026-09-04, n=2 dumps]` |
| **3, 5, 7, 9, 11, 13** | **yes** | **six byte-identical copies of one perspective matrix whose row 3 encodes the slot-9 camera** — the main camera's clip transform, re-uploaded before each of six passes that share the eye |
| 4, 6, 8, 10, 12 | no | five further perspective matrices with unit forward vectors and view origins within ~50 units of the camera, each looking a different way (one straight down). Local-light shadow cameras is the natural reading. `[hypothesis]` |

So the pre-committed rule's second branch applies: "several flagged with identical 0..3 rows ⇒
depth pre-pass + main share the eye; still the answer." Dump 2, taken after a small mouse move,
showed the same structure with the flagged matrix yawed by 13.0° and the cascades' rotation rows
unchanged. In Capture Mode the count of flagged writes dropped to 5, then 4 (fewer passes in a
paused scene) — still all identical to each other.

### 3a. The matrix itself, and what falls out of it

Row-vector storage (`pos · M`), gameplay dump 1, main pass:

```
row 0:   0.219722   0.181706  -0.000002   0.978718
row 1:   0.000000   2.091212   0.000000  -0.088091
row 2:   1.160276  -0.034410   0.000000  -0.185340
row 3: -6736.5405  155.6439    0.088921  4425.7319
slot 9 (camera): -3276.5466  316.0177  6426.4590  1
```

Reading the columns of the upper 3×3 as vectors `[measured 2026-09-04, n=4 dumps consistent]`:

- **column 3 (→ clip.w) is a unit vector** (|·| = 1.00000): the view **forward**. `w = distance
  along forward`, positive in front of the camera.
- **column 0 (→ clip.x)** has magnitude 1.1809 → `1/tan(hfov/2)` → **hfov = 80.5°**.
- **column 1 (→ clip.y)** has magnitude 2.0994 → **vfov = 50.9°**; ratio 1.7778 = **16:9** exactly.
- The three are mutually orthogonal to 5 decimals (x·fwd = 0.00000, y·fwd = 0.00000, x·y = 0.00000).
- **row 3 = −camera · each column**: −cam·x = −6736.54 (stored −6736.54), −cam·y = 155.64
  (stored 155.64), −cam·fwd = 4425.73 (stored 4425.73). The slot-9 position is the eye of this
  matrix, not merely near it.
- **Y is up** (the up column's dominant component is y; the camera height is slot 9's y).
- **right × up = −forward** in world coordinates. Read carefully: this fixes the *triple*, not
  "D3D vs OpenGL" — the world basis is right-handed-with-forward-along-−z *or* the storage is
  the transpose of a left-handed convention; what the patch needs is only that `w` is positive
  in front and `x`/`y` scale as above, and both are now measured.
- **column 2 (→ clip.z) is ≈ 0 and row 3's z is a small positive constant** (0.0889 in this
  frame, 0.0924 and 0.1169 in later frames): clip.z does not depend on the vertex at all, so
  depth = const / w. That is the shape of **reversed-Z with an infinite far plane**, and the
  constant would be the near distance — but the constant *changing between frames* (three
  values across four dumps) is unexplained. `[hypothesis]` on the reversed-Z reading; the
  per-frame drift is an open question, not a finding. Do not build a depth assumption on it yet.
- Capture Mode's matrix carries the same FOV (80.6° / 51.0°) — the free camera does not change
  the projection, only the view. `[measured 2026-09-04, n=2]`

### 3b. What this means for the patch

`WVP_eye = V_eye · P` for the shared path is now computable from what the buffer holds: the
upper 3×3 gives right/up/forward and the two focal scales, row 3 gives the eye. A per-eye rewrite
on `Unmap` of the 512-byte buffer, applied to every write where slot 4 equals slot 9, moves the
15 world-space shader families. The other ~144 vertex shaders still take their position from
the per-object `InstanceConsts` WVP — unchanged, still the queued `[PD]` question.

## 4. A/B regression — reproduces the dev PC

`NUMPAD4`, 40 × 25 px mouse orbit, `NUMPAD5`: **9, 12, 13, 16, 17, 18, 19, 23, 27, 31** — the
exact 2026-09-03b list `[verified-live 2026-09-04, n=2 machines]`. The probe's frame-constant
logic is stable across machines and build revisions; nothing new was expected and nothing new
appeared. Incidental, pixel side: its slot 4 is the camera position with `w = 0.000977`
(1/1024), and slot 7 is the camera position **rounded to integers** — noted, not pursued.

## 5. Capture Mode IS a free camera — and it drives the main-pass matrix

`[verified-live 2026-09-04, n=1]`. Pause menu → Log column → CAPTURE MODE (7 Down presses from
RESUME GAME; the two greyed rows WASTELAND MISSIONS / ENCOUNTERS are **skipped** by the highlight)
→ Enter. The screen offers **MOVE (arrow keys AND WASD), ROTATE (mouse), U / I tilt, Enter =
capture image, R = video mode, Esc = exit**, with tabs CAMERA / FILTERS / CAMERA SETTINGS /
VIGNETTE.

Holding `W` for 1.5 s moved slot 9 by **6.34 units along the view forward** (cosine 0.999 to
the forward column) and the flagged main-pass matrix's row 3 moved with it. The free camera
writes the same slot the gameplay camera writes. `[measured 2026-09-04, n=1 move]`

Not established: **how to switch tabs.** Arrow keys move the camera (they are MOVE), and `E`
and `Tab` did nothing — probably the mouse on the on-screen chevrons or `Q`/`E`-style
shoulder buttons on a pad. The CAMERA SETTINGS tab (where external research places the FOV
slider) was therefore not reached. Cheap to finish next time, not needed for anything queued.

## 6. Driving the game on this machine — what changed from the profile

- **70 ms taps are IGNORED here; 250–300 ms holds work.** Two `Esc` taps did nothing (screen
  unchanged, game rendering and focused); a 0.3 s hold backed out immediately, and every later
  press used holds. The dev PC's profile recorded taps as working at 784×561 — the difference is
  probably polling cadence against frame time, not the key. `[verified-live 2026-09-04, n=2 taps
  failed, ~20 holds succeeded]`
- Window was **windowed 1920×1080 at (798,137)** with the desktop visible around it; the first
  BitBlt before focusing captured the whole 3424-px-wide desktop, every capture after focusing
  was the clean 1920×1080 client area.
- Resume-game load was under 45 s here (profile says ~60 s).
- The four capabilities on this game, as of today: **(1) menu → gameplay: proven** (2 machines);
  **(2) commands: N/A** (no console used; the proxy's numpad probes are the command channel, and
  they fire reliably from synthetic input); **(3) character + camera: proven** (mouse look, and
  now Capture Mode's free camera by keyboard); **(4) self-close: proven on the dev PC, not
  exercised today** — the game was deliberately left running.

## 7. What is NOT established

- Which of the six main-eye writes is *the* main colour pass versus depth pre-pass / SSAO /
  whatever else shares the eye — they are byte-identical, so for a rewrite it does not matter,
  but a per-pass render-target census would name them.
- The identity of writes 4/6/8/10/12 (local-light shadow cameras is a guess).
- The reversed-Z / infinite-far reading, and why the clip.z constant drifts frame to frame.
- Whether the 3136-byte pixel-side buffer's slots past 17 hold anything a patch needs.
- Capture Mode's tab-switch key, and whether its FOV slider changes the projection columns.

## 8. Next

Static (`[PD]`): design and build the shared-path rewrite on `Unmap` (rows from §3a, applied to
writes where slot 4 == slot 9), and answer the `InstanceConsts` world-matrix question. Live
after that: the first per-eye offset test — Capture Mode is the place to run it, because its
camera is still and the rewrite's effect can be read off a screenshot pair.
