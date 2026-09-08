# 2026-09-08 — the shared-matrix edit reaches the GPU but does NOT move the world, and Video Mode hands us 157° of live, playable FOV

`/lm`, dev PC, fully autonomous. The user launched nothing and pressed nothing.

Evidence: `dev-archive/recon/2026-09-08-shared-matrix-edit-does-not-translate-and-video-mode-fov/`
(full proxy log, the second-controller binding panel, the 157° gameplay frame, the amplified
left-vs-right difference image).

---

## 1. ⛔️ The starred row is answered, and the answer is NO: `M[3][0] += d*w` does not translate the world

`[verified-live 2026-09-08, n=2 render states]`

**The edit fires.** Final counter: `STEREO OFF … Applied 116364, skipped 0`. And `skipped` is not
the interesting number — reading `cbfp.c`, a buffer that fails the `slots_xyz_equal(…, 4, 9, 0.01f)`
main-pass test is counted **neither applied nor skipped**, so `skipped=0` does not mean "everything
matched". `applied=116,364` means **116,364 writes genuinely passed the main-pass discriminator and
were edited.** The board's `edited=0` outcome is firmly ruled out.

**The picture changes.** Against a control that is as clean as a control ever gets: in Capture Mode
the scene is completely frozen, and **three consecutive captures differed by exactly zero** —
`mean|d|=0.0000, max=0.0, 0 pixels >8`. So every difference measured there is ours.

**But the world does not move.**

| separation (world units) | ×human IPD | pixels differing >8 | best horizontal shift L→R |
| --- | --- | --- | --- |
| 0.052 | 0.8× | **0** | 0 px |
| 1.478 | 23× | 3,181 | **0 px** |
| 13.764 | 212× | 8,735 | **0 px** |

At 13.76 world units the two eyes are **13.8 metres apart** and the frame still does not translate
by a single pixel. What *does* change is **shading**: the amplified difference image shows faint
intensity changes in the light shaft on the floor and around lit surfaces, not a displaced scene.

**Repeated in a second render state.** The above is Capture Mode. Re-run in live gameplay (inside a
Video Mode capture session, scene animating), with a two-shot no-input control:

```
CONTROL (stereo off, 2 s apart) : 4,061 px >8
SIGNAL  (left vs right, 13.76)  : 7,934 px >8      best horizontal shift: 0 px
```

Signal is about 2× the control — a real effect — and **still 0 px of translation**. Same verdict,
different state, so this is not an artefact of Capture Mode.

### What this means, and the possibilities it does NOT collapse

This is the board's third outcome: *"`edited` large but nothing moves ⇒ the 512-byte buffer is not
the matrix on screen, or the game re-uploads after our `Unmap`."* Both halves stay open, but they
are **not** equally likely any more:

- **(b) the game re-uploads after our `Unmap`** is *weakened by our own evidence*. If our write were
  simply overwritten before the draw, the picture would be **identical**, and it is measurably not.
  Something consumes our edited bytes. (It survives only in a partial form: some passes re-upload,
  others do not.)
- **(a) the buffer is not the matrix that positions on-screen geometry** is the leading reading, and
  it fits the shading-only signature: the buffer we edit feeds lighting/shadow/screen-space work,
  while world position comes from elsewhere.
- **(c) `M[3][0]` is the wrong element for this matrix's on-screen convention** is not excluded by
  anything measured here, though §7a's algebra was proven numerically over 33 Python + 26 C cases.

**The observation that would separate them** is a read-back: re-read the buffer at the next `Map`
and see whether our value is still there. That is a small proxy change and it is `[PD]`.

### ⭐ This resolves the 2026-09-04c contingency, in the direction that matters

That entry deliberately left the per-object branch off the board: *"the per-object build is
contingent on whether the shared edit renders."* **It does not render.** So the contingency is
discharged and **the per-object `InstanceConsts` path is now the route**, not a fallback — which
§6b already characterised (slots 0..3 are the full object→clip 4×4; it needs its CPU-side fill
hooked). The one-float algebra of §7a carries over to it unchanged; only the write site moves.

---

## 2. ⭐⭐ Video Mode is real, it is reachable on a keyboard-only machine, and it gives 157° of *playable* FOV

`[verified-live 2026-09-08, n=1]`

This closes the "cheap, optional" third row far more decisively than it was framed.

**The route, confirmed end to end:**

```
gameplay → Esc → Down×7 (skipping the two greyed rows) → CAPTURE MODE → Enter
         → R                      (the HUD bar literally reads "R  VIDEO MODE")
         → CAMERA SETTINGS tab    (mouse-only: click the label, then the ‹ › arrows)
         → FIELD OF VIEW, 18 × ›  (slider to maximum)
         → Enter                  ("BEGIN SESSION")
         → Enter                  ("CONTINUE")
         → live, playable, HUD-free gameplay
```

**Measured there: `|col 0| = 0.2000` → hfov ≈ 157.4°**, using the relation fitted to 2026-09-04b's
own two calibration points (`|col0| 1.7936 → 58.28°`, `0.6138 → 116.91°`, i.e.
`hfov = 2·atan(1/|col0|)`; both reproduce to 0.01°). For scale:

| state | hfov |
| --- | --- |
| ordinary gameplay default | 80.48° |
| Photo-Mode Capture Mode, slider at maximum | 116.91° |
| **Video Mode capture session** | **≈157.4°** |

So Video Mode reaches **beyond the Photo Mode slider's own maximum**, and unlike Photo Mode it is
not a still: `hold w 1.5` walked Max forward and the camera followed (264,354 pixels changed), and
the state **survives the pause menu and RESUME GAME**.

**`/gr`'s corrected recipe was right on every point it corrected.** `R` was the missing step; the
resume key is `Enter`, not `Esc`; and our two previous negatives were about the exit key rather than
about the claim.

### The two-controller precondition is REAL — and virtual pads satisfy it

The game says so itself, twice, in its own UI `[verified-live 2026-09-08]`:

- Capture Mode's description panel: *"Connect a second controller and have a friend control the
  camera during game play and capture footage with a cinematic flair."*
- The CAPTURE VIDEO panel: *"You need to connect a second controller and have a friend control the
  camera during game play in order to capture footage that uses the capture camera."*

**This machine has zero physical controllers** (`slots before: []`). Two ViGEm virtual pads were
held for the session and XInput reported **slots [0, 1]** throughout, and Video Mode opened. New
tool: `flat-to-vr-RE-toolkit/tools/hold-pads.py`.

⚠️ **What that does and does not show.** Video Mode opened *with* two pads present; **no control was
run with the pads removed**, so this session cannot say whether the two pads were necessary. Read it
as "the documented precondition can be satisfied here", not "the pads caused it". The control is one
`R` press with no pads and it is owed.

### ⭐ The prize is the binding list, not the FOV

The CAPTURE VIDEO panel documents what the **second controller** drives, live, during gameplay:

- **Increase Field Of View / Decrease Field Of View**
- **Attach/Detach Camera To Max**
- **Toggle Game Camera**, **Toggle Camera Tracking**
- Toggle Alternate Camera 1 / Alternate Camera 2
- Rotate Camera Axis (two axes), Pan Up, Pan Down
- Toggle Depth Of Field, Normal Game Speed, Slow Motion, Start/Stop Recording

That is a **shipped, engine-native, runtime-controllable detached camera with FOV control and an
attach/detach-to-player toggle** — reachable with no code at all. For a project whose whole problem
is "decouple the camera and control its projection", this is the most useful surface found on this
game so far. ⚠️ **None of these buttons was actually pressed this session** — the bindings are
`[verified-live]` *as documentation*, and every one of them is `[reported]` as behaviour until a
virtual pad drives it.

---

## 3. Two automation traps, both of which produced a wrong reading before they were caught

**⚠️ NumLock changes what the proxy's hotkeys do, and it fails silently.** With NumLock **off**, a
numpad scancode produces the *navigation* VK (`0x51` → `VK_NEXT`), and the proxy accepts navigation
keys as aliases — but its alias table pairs them differently than its numpad table. The first
`numpad3` ("dump the next frame") was logged as **`cbfp: stereo separation -> 0.0520`**, i.e. it ran
NUMPAD9. Worse, the aliases for the stereo keys are `RIGHT` and `UP`, which in Capture Mode **move
the camera** — so the whole experiment would have run with a drifting viewpoint and no error
anywhere. **Set NumLock ON before using numpad hotkeys on this game**, and check the log line
matches the key you meant.

**⚠️ The pause-menu row count in the profile is right and mine was wrong.** Six downs from RESUME
GAME lands on **CREDITS**, not EXIT GAME; the seventh is EXIT GAME. Verified by capture before
pressing Enter — which is exactly why the "navigate → capture → verify → commit" rule exists.

---

## 4. Automation scored by the four capabilities

| # | capability | verdict |
| --- | --- | --- |
| 1 | menu → gameplay | ✅ title → RESUME GAME → world, then pause → CAPTURE MODE → Video Mode → capture session. Every hazard screen captured and the highlight verified before committing (`NEW GAME` under `RESUME GAME`; `EXIT TO MAIN MENU` passed en route to `CAPTURE MODE`; `CREDITS` immediately above `EXIT GAME`) |
| 2 | commands | ✅ the proxy's numpad hotkeys, **once NumLock was on** (see §3). No in-game console on this title |
| 3 | character + camera | ✅ `hold w` moved Max inside the capture session; mouse-clicks drove the mouse-only Capture Mode tabs and sliders (18 slider clicks) |
| 4 | self-close | ✅ **clean, no taskkill** — pause → EXIT TO MAIN MENU → confirm → main menu → Down×7 → EXIT GAME → confirm. Process gone |

**All four proven on this game in one session.** The install stays a DEV BUILD: `dxgi.dll` deployed
and stamped, nothing reverted.

---

## 5. What this session did NOT establish

- **Why** the shared-matrix edit does not translate — three possibilities remain live (§1), and the
  read-back test that separates them was not run.
- Whether the two virtual pads were **necessary** for Video Mode, or merely present (§2).
- Whether **any** second-controller binding actually responds to a virtual pad.
- Whether the 157° FOV survives a **full** exit from capture mode. `Esc` reached the pause menu and
  `RESUME GAME` returned *into* the session, so the session is stickier than expected — how it ends
  cleanly is unknown.
- `V` in a car — still untestable on this save (the garage car is a prop, `[verified-live 2026-09-04b]`).
