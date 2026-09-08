# 2026-09-08b — 157° of FOV persists into ordinary gameplay, the two-controller gate is disproved, and virtual pads do NOT drive the capture camera

`/lm`, dev PC, fully autonomous, second session of the day. The user pressed nothing.

Evidence: `dev-archive/recon/2026-09-08b-video-mode-fov-persists-into-gameplay/`.

This session's whole job was to exhaust Mad Max's `[FLAT]` rows. Three are now answered and one
remains blocked by the save.

---

## 1. ⭐⭐ THE HEADLINE: the wide FOV survives a full exit and persists in normal, HUD-on gameplay

`[verified-live 2026-09-08, n=1, numerically measured at three separate points]`

The board's row asked: *"does any Capture Mode route carry the FOV into gameplay?"* **Yes, and by a
lot.**

```
gameplay → Esc → Down×7 → CAPTURE MODE → Enter
         → R                          (Video Mode)
         → CAMERA SETTINGS → FIELD OF VIEW to maximum
         → Enter (BEGIN SESSION) → Enter (CONTINUE)     ← HUD-free session, 157.38°
         → Esc → Down×7 → CAPTURE MODE → Enter → Esc    ← full exit
         → ORDINARY GAMEPLAY, HUD BACK, STILL 157.38°
```

Measured from `|col 0|` in the proxy's own matrix dump at each step
(`hfov = 2·atan(1/|col0|)`, the relation fitted to §6's two calibration points):

| state | `|col 0|` | hfov |
| --- | --- | --- |
| ordinary gameplay, default | 1.1809 | **80.48°** |
| Photo-Mode Capture Mode, slider at max | 0.6138 | 116.91° |
| Video Mode capture session | 0.2000 | 157.38° |
| **ordinary gameplay AFTER a full exit** | **0.2000** | **157.38°** |

**It is not a stale frame.** After exiting, Max was walked forward 2 s and strafed 1 s; the HUD
(objective text, minimap, weapon widget) is drawn, the scene changes, and a fresh dump still reads
`0.20000`. Side-by-side evidence in the recon folder: `ordinary-gameplay-before-at-80deg-default.png`
against `ordinary-gameplay-HUD-on-at-157deg.png`, same save, same room.

**Why this matters more than a comfort setting.** It is an **engine-native, code-free route to
roughly double the default field of view, in ordinary playable gameplay**, on a game whose shared
matrix we have just shown we cannot move (§7b, this morning). It does not solve stereo, but it is
the first camera/projection lever on this project that works *and* survives.

⚠️ **Not established:** whether it survives a **reload or a relaunch** — no save/config write was
observed, and nothing was tested past this session. That is one launch away and is now a board row.

### The 2026-09-04b negative is explained, not contradicted

That session measured `Esc` out of Photo-Mode Capture Mode restoring 80.48° at once, and it was
right. The difference is **which mode you leave from**: `Esc` out of the *still* Photo Mode reverts;
leaving via **Video Mode → BEGIN SESSION** carries the value. Exactly the distinction `/gr` drew.

---

## 2. ❌ The two-controller gate is DISPROVED for entering Video Mode

`[disproved 2026-09-08, n=1]` — and this **corrects this morning's own write-up.**

The 2026-09-08a session opened Video Mode with two virtual pads held, and recorded honestly that no
pads-removed control had been run. That control has now been run.

**With XInput reporting zero connected controllers** (`slots: NONE`, verified immediately before):

- `R` in Capture Mode **opened Video Mode** — tabs changed to FILTERS / CAMERA SETTINGS / VIGNETTE /
  FRAME, bar changed to `Enter BEGIN SESSION   R PHOTO MODE`;
- `Enter` → the CAPTURE VIDEO panel appeared;
- `Enter` → the **capture session ran**, HUD-free, playable, at 157.38°.

So the FRAMED community claim — *"Video Mode is enabled when two controllers are connected"* — is
**wrong as stated for entering the mode**, on this build. This morning's two virtual pads were
**present but not necessary**, and the caveat written at the time turned out to be the whole story.

⚠️ **The game's own narrower claim is untouched by this.** Its UI says a second controller is needed
*"to control the camera during game play"* — a claim about the camera bindings, not about entry. §3
is about that, and it is a different answer.

---

## 3. ⛔️ Two virtual X360 pads do NOT drive the second-controller camera

`[measured 2026-09-08, 18 numeric hfov dumps + pixel deltas against a no-input control]`

The prize row was to drive the documented second-controller camera: **Increase / Decrease Field Of
View**, **Attach/Detach Camera To Max**, **Toggle Game Camera**, **Toggle Camera Tracking**. Two
ViGEm pads were created (XInput slots [0, 1]) and **every** input on pad 1 was exercised, each
followed by a matrix dump.

**Not one input changed the field of view.** Across 18 dumps spanning `LEFT_SHOULDER`,
`RIGHT_SHOULDER`, both triggers, all four D-pad directions, both thumb clicks, `A`, `B`, `X`, `Y`,
`hfov` read **157.38° every single time**.

Pixel deltas against a no-input control floor of 290 px told the same story: `A` 991 px, `B` 585 px,
and the D-pad/thumb entries at or below the floor.

**What the pads DID do is move the player.** The large deltas from the sticks and shoulders
(200k–330k px) were Max walking — confirmed by resuming afterwards and finding him in a different
part of the garage. The one frame that looked like "the camera flew into the geometry" was the
follow-camera clipping as he walked into a corner, not a free camera.

`START` opened the pause menu — the ordinary player-1 binding — which is itself evidence the game is
treating these pads as **player one**, not as a second player.

### ⚠️ What this negative does and does not mean

It means **two virtual ViGEm X360 pads did not activate the feature.** It does **not** mean two real
controllers would not. A game can distinguish a genuine second device in ways a virtual pad does not
reproduce, and the pads were also hot-plugged *after* the session began. Both are untested. Write it
as a negative about the method, never as "the feature does not work".

### Two traps this probe walked into, both caught

1. **The first probe run was worthless and looked like a triumph.** Its two biggest "hits" —
   `LEFT_SHOULDER` at 62× control and `LEFT_STICK` at 85× — were the two **"Controller Connected —
   Xbox 360 controller" toasts** drawing and clearing. Caught only by looking at the frame. The
   re-run added an 18 s lead-in and switched the measurement from pixels to `hfov` read out of the
   matrix, which nothing drawn on top of the frame can perturb.
2. **`START` produced a real, large FOV change — 157.38° → 116.91° — that means nothing.** 116.91°
   is exactly the Photo-Mode slider maximum set earlier, and the frame showed the pause menu. A
   number moving in the right direction is not a result.

---

## 4. ✅ Keyboard `C` works; keyboard `X` does not

The CAPTURE VIDEO panel's glyph column is a **mix**: white letters `X` (Toggle Depth Of Field) and
`C` (Toggle Game Camera) are keyboard keys, the coloured circles are Xbox face buttons. That matches
Capture Mode's own *"Enter capture mode by pressing C + X"*.

- **`C` — a large, reproducible view change** with **no controller connected**: 197,887 px in one
  session and 221,173 px in another, against control floors of 11,610 and 1,277 respectively.
  `[verified-live 2026-09-08, n=2]` It repositions the camera and **does not change hfov**
  (157.38° before and after), consistent with *Toggle Game Camera*. ⚠️ It is not a clean symmetric
  toggle: the second press gives ~11k, the third ~6k, both at or near the noise floor. Reading it as
  "switches to the game camera and stays there" is `[hypothesis]`.
- **`X` — nothing.** 905 px against a 1,277 px control floor, i.e. **below** the floor, and no hfov
  change. `[disproved 2026-09-08]` as a visible effect on this build/scene. It may still toggle
  depth of field somewhere the eye and this metric cannot see it in a dark interior.

---

## 5. What is left, and what is NOT established

- **`V` in a car is still blocked by the save** — unchanged. This save sits at *Collect the jag tip*
  and the garage car is a non-enterable prop `[verified-live 2026-09-04b, user-confirmed]`. It needs
  play through to the first driving mission.
- Whether the 157° **survives a reload or relaunch**.
- Whether **real** controllers activate the second-controller camera (§3).
- Whether the FOV can be pushed past the slider maximum, or set numerically rather than by 18 clicks.
- What `C` actually toggles between, and why it does not cleanly toggle back.
