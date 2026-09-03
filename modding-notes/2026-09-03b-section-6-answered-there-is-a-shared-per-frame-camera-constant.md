# 2026-09-03b (`/lm`, dev PC, live, fully autonomous) — §6 ANSWERED: there IS a shared per-frame camera constant, and §7 with it

The one launch §6 was waiting for. User launched, said "all yours", left. Claude drove title screen
→ main menu → gameplay, ran the probe's A/B protocol including its control pair, read the log and
closed the game through its own menus.

**The probe attached on route A** (factory `CreateSwapChain`), hooked the context vtable
(`Map`/`Unmap`/`UpdateSubresource`) and `Present`, and armed the fingerprint pass — all before the
first mark.

---

## 1. ⭐ §6 ANSWERED — a shared per-frame camera constant EXISTS in `GlobalConstants` b0

The probe's decision rule, pre-committed in the code, was: *slots flagged (especially a 4×4-shaped
run) ⇒ a shared per-frame camera constant; nothing flagged above a per-frame write count of 1 ⇒
there is none and the camera is baked into per-object `InstanceConsts.WorldViewProjMatrix`*.

**Slots flagged. The first branch is the answer.**

### The control pair came first, and it earned its place

`[verified-live 2026-09-03]` The row insisted on an A/B pair taken **without moving the camera**,
because anything flagged there is time-varying rather than camera-varying. Run exactly that way:

| pair | flagged slots |
|---|---|
| **control** — camera deliberately untouched | `16, 17, 23, 27, 31` |
| **real** — large camera sweep between marks | `9, 12, 13, 16, 17, 18, 19, 23, 27, 31` |

**Camera-varying set = real − control = slots 9, 12, 13, 18, 19.** Five slots that move only when
the camera does. Without the control, `23/27/31` would have looked like camera data and they are
not.

⚠️ **`16` and `17` appear in both lists and must not simply be subtracted.** They drift a little on
their own but change *enormously* with the camera — slot 16 went `0.372, 0.136, 0.036` → `0.206,
0.573, −0.030` under the sweep, against a third-decimal wobble in the control. They are
camera-driven **and** time-drifting; the set-difference is a starting point, not a verdict.

### What the values look like

| slot | offset | A → B under a camera sweep | reading |
|---|---|---|---|
| **9** | +144 | `−3276.54, 316.02, 6426.46, 1.000` → `−3272.40, 314.62, 6426.35, 1.000` | **a world position, `w=1`.** Moved ~4 units on a pure camera orbit, which is what a third-person *camera* position does while the character stands still |
| 12 | +192 | `0.001669, 3000.0, 0.000334, 316.017` → `…, 314.617` | its `w` tracks slot 9's `y` exactly — a packed value, `3000.0` smells like a far plane |
| 13 | +208 | `0.833333, 0.220058, …` → `…, 0.215389, …` | `0.833333 = 1/1.2`, `0.003333 = 1/300` — reciprocals/scales |
| **16–19** | +256 | large changes at 16/17, small at 18/19 | **the candidate matrix** |

### ⭐ The probe's own verdict, verbatim

```
candidate run: slots 16..19 (+256, 64 bytes) are contiguous -- 4x4-SHAPED (shape only; layout NOT interpreted)
READING: these slots behave like a SHARED per-frame camera constant. Cross-check a 4x4-shaped run
         against InstanceConsts.WorldViewProjMatrix before believing it.
```

That caution is right and is repeated here: **a contiguous 64-byte run is the *shape* of a 4×4, not
proof of one.** The `w` components are `0.25, 0.05, 0.0, 0.0`, which is not the `0,0,0,1` a plain
view matrix row set would show, so it may be a packed camera block rather than a matrix. The
cross-check against `InstanceConsts.WorldViewProjMatrix` is still owed.

## 2. ✅ §7 ANSWERED by the same launch — the fill path is `Map`/`Unmap`

`cbfp frame=… buf=… width=512 writes=10(recorded 10) path=Map/Unmap`

`[verified-live 2026-09-03]` The buffer is filled by **`Map`/`Unmap`, not `UpdateSubresource`**, at
about **10–11 writes per frame**. §7 was previously blank.

That matters for design: a `Map`/`Unmap` buffer is written by the CPU each frame through a pointer,
so an interception has to sit on the unmap (or on the mapped range) rather than on a copy call.

## 3. ⚠️ THE STATIC LAYOUT PREDICTION DOES NOT MATCH THE RUNTIME

This is the finding a static session could not have made, and it needs stating plainly.

`/pd`'s census (2026-09-03) corrected §6 to *two* `GlobalConstants` layouts: **2352 bytes** (17
`Globals` slots, 465 shaders) and **512 bytes** (20 slots + `ShadowTransform`, 186 shaders). The
probe was armed to track both.

`[measured 2026-09-03, n=95 censuses across ~28,500 frames]`

- **The 2352-byte buffer was NEVER bound. Not once, in any census.**
- The buffer that carries the camera constant is the **512-byte** one — the variant the static work
  called *"very likely the shadow-pass variant"* because of its `ShadowTransform` tail.
- **A 3136-byte buffer appears in every census with a count identical to the 512-byte one** — 1:1,
  2:2, … 48:48, in all 95 samples without exception.

**So the layout we have characterised is the one static analysis expected to be the shadow variant,
and the buffer static analysis expected to be the main one never appeared at all.** The 1:1 pairing
with 3136 is a strong hint that 3136 is the real counterpart in this build, and that the 2352 figure
came from shaders that this scene never exercised — or from a layout the shipped binary does not
actually bind.

⚠️ **Do not over-read the census counts.** They increment about once per 600 frames, far too slowly
to be raw writes (the per-frame line reports 10–11 writes/frame for the same buffer), so they are
probably distinct buffer instances rather than writes. **The pairing is solid; the unit is not.**

**⇒ Next `[PD]`:** re-run the static layout census against **3136** bytes, and find which shaders
bind the 2352-byte variant and whether anything in the shipped game ever does.

## 4. Incidental: the game ships a **CAPTURE MODE**

The pause menu lists `CAPTURE MODE` alongside `STORY MISSIONS`, `STATISTICS` and so on. In most
games that is a photo mode, and photo modes usually carry **a free camera** — which is the thing this
project ultimately needs. Not opened this session. `[inferred-static 2026-09-03]` from a menu label
only, which after today's Enslaved lesson is a lead and not evidence.

## 5. What is NOT established

- **That slots 16–19 are a view or view-projection matrix.** Only that they are contiguous, 4×4
  *shaped*, and camera-driven. The `w` column argues against a plain matrix. The cross-check against
  `InstanceConsts.WorldViewProjMatrix` (b1, +0) has not been done.
- **What slots 9/12/13 are individually.** Slot 9 looks like a camera world position; the rest are
  inferred from value shape, not decoded.
- **Whether the 2352-byte layout is ever bound anywhere.** One interior garage and a short walk
  outside is not the whole game.
- **What the census counter actually counts.** §3.
- **Anything about VR.** Flat-screen measurement only; no headset, no stereo attempted.
