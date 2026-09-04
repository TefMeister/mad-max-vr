# The FOV carry-into-gameplay route is Video Mode + `Enter`, not `Esc` — and Video Mode may need two pads

**Status:** 🆕 new · **Priority:** medium — it answers, with a named tab and a named key, the one
question the 2026-09-04b live session left open, and it turns a `[reported]` community claim into a
one-launch test with a pre-committed reading.

## The question this answers

`topics/2026-08-25-native-capture-mode-camera-tool.md` reported, from community guides, that a
custom FOV set in Capture Mode can be carried into live first-person driving. The 2026-09-04b
session tested it and found the first gameplay dump after leaving Capture Mode reads the default
80.48° again `[verified-live 2026-09-04, n=1]`. Its verdict was careful about what that did and did
not prove: **it exited with `Esc`**, and recorded that the route the guides describe — Video Mode,
then a "show HUD" tab, then resume — was never tried, because no tab by that name exists among the
four the still Capture Mode shows (CAMERA / FILTERS / CAMERA SETTINGS / VIGNETTE). It asked for a
source naming the exact tab and button.

## The route, as the guide actually words it

Cole Wolfsson's Steam guide (2017-05-01) gives it as four steps `[reported]`:

1. Enter **Capture Mode** — from the main menu, or click both thumbsticks on a controller.
2. Enter **Video Mode** — **`R`** on keyboard, **`Y`** on controller. *This is the step that was
   missing.*
3. **Increase the FOV in the camera settings tab**, then **switch to the show HUD tab**.
4. Press **`Enter`** (keyboard) or **`A`** (controller) "to start playing with an increased FOV".
   Then **`V`**, or double-tap D-pad down, for first person while driving.

So the "show HUD" tab is **inside Video Mode**, a different mode behind `R`, not among the still
mode's four tabs — which is exactly why the session could not find it, and why its negative result
is a negative about `Esc` rather than about the claim. **And the resume key is `Enter`, not `Esc`.**
On this reading the two are not the same action at all: `Esc` exits and restores, `Enter` resumes
*out of* Video Mode carrying its state.

## ⚠️ The precondition that may explain the whole difficulty

The FRAMED screenshot-community guide for this game states plainly `[reported]`:

> "The built-in Photo Mode has a Video Mode feature that is enabled when two controllers are
> connected."

If that holds on this build, **Video Mode is not reachable at all on a keyboard-only machine**, and
two sessions of keypress hunting failing to open anything is the expected outcome rather than a
puzzle. It is a cheap thing to check and it gates the whole test, so check it first.

## Two other things that guide gives us

- **A second way into photo mode:** `X`+`C`, or the `<`/`>` keys, in addition to the pause-menu
  route this project already uses. **HUD toggle is `CAPS LOCK` or `>`** `[reported]`.
- **A public Cheat Engine table exists for this game** whose advertised features are *"Photo Mode
  Camera range, FOV Control, Custom Aspect Ratios, Timeflow control, Function call handler,
  Cheats"*, with `F1` toggling photo-mode FOV control, `Num +`/`Num -` adjusting it, and `F2`
  unlocking aspect ratio `[reported]`. The guide does not name its author. **We do not download it**
  — the standing rule is study-online-only, and nothing from it may be copied. What it is worth to
  us is the *existence claim*: someone else independently found the photo-mode camera range, the FOV
  and the aspect ratio to be reachable and changeable at runtime, and **"Custom Aspect Ratios"
  is the same family of edit a per-eye projection rewrite makes**. That corroborates our own
  measurement that the slider moves only the projection's two focal-scale columns.

## Why this matters for this project specifically

The board's open row asks whether *any* Capture Mode route carries the FOV into gameplay. It is
marked cheap and optional, and it should stay that way — but the answer is worth having, because the
two outcomes say different things about the engine:

- **It carries** ⇒ the engine has a live FOV-override path that survives the transition back into
  gameplay, writing the same shared main-pass matrix columns the per-eye rewrite targets. That is a
  path worth understanding before the rewrite, and a zero-RE way to hold a non-default FOV while
  the probe dumps.
- **It does not carry, even by this route** ⇒ the community claim is about playing *inside* Video
  Mode rather than about a persistent setting, the row closes for good, and the still-camera testbed
  (already proven) remains the only Capture Mode value to this project.

## Concrete next step — one flat run, readings pre-committed

Cheapest first, and stop at the first failure:

1. **Are two controllers connected?** If not and Video Mode will not open on `R`, that is the
   FRAMED precondition confirmed — record it and stop; the row needs a pad before it needs a test.
2. Capture Mode → **`R`** → **CAMERA SETTINGS** tab → raise FOV toward the 116.91° end (mouse-only:
   click the tab label, click the row label, then the `<`/`>` arrows — established 2026-09-04b).
3. Switch to the **show HUD** tab → press **`Enter`**.
4. Dump, and read the shared main-pass matrix's focal columns. **hfov materially above 80.48°** ⇒
   it carried. **80.48° back** ⇒ it did not, and the row closes.

## Sources

- https://steamcommunity.com/sharedfiles/filedetails/?id=917610216 — "How To: Increase FOV in
  First-Person", Cole Wolfsson, 2017-05-01. Already cited by the 2026-08-25 topic; re-read here for
  its exact step wording, which is what the open question needed.
- https://framedsc.com/GameGuides/MadMax.htm — FRAMED screenshot-community game guide for Mad Max.
  New source for this project.
