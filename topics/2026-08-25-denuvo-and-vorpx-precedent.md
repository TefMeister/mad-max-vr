# Mad Max: Steam build has Denuvo, but vorpX already achieves real geometric stereo 3D + head tracking on it

**Status:** 🆕 new · **Priority:** high — strong, concrete feasibility signal for the whole project,
and directly informs `ENGINE-DOSSIER.md` §4 (DRM/injection foothold).

## What was found

- **DRM split by storefront**: per community reports, the **Origin/EA App release of Mad Max has no
  Denuvo**, while the **Steam release is Denuvo-protected**. Our install (per
  `claude-memory/STATUS.md`) is the Steam build, so Denuvo applies here — worth recording precisely
  rather than assuming, since (unlike Burnout Paradise Remastered, this portfolio's other confirmed
  Denuvo title) Mad Max's Denuvo status isn't uniform across storefronts.
- **vorpX has a working, actively-discussed profile for Mad Max**, and — critically, unlike the
  Burnout Paradise case where vorpX flatly fails to hook the Steam build — vorpX's own forums
  describe real success against this game: a **Geometry 3D (G3D)** profile exists (vorpX's
  highest-fidelity stereo mode, which reconstructs true per-eye geometry rather than faking depth
  from the 2D image/Z-buffer) alongside faster/lower-fidelity Z-Buffer-based profiles, and users
  discuss **head tracking working in third-person**, with community iteration/refinement over time
  (an older, non-3D "Z-Normal" cloud profile was reportedly superseded by a proper 3D one).

## Why this matters

1. **Third-party D3D hooking demonstrably works against this exact Steam/Denuvo build.** This is a
   much stronger and more specific data point than Burnout Paradise's situation, where vorpX
   couldn't even attach. Whatever Denuvo is doing here, it isn't blocking the class of renderer-level
   hooking this project's own DLL-proxy plan depends on.
2. **Geometry 3D mode is proof the engine's camera/projection system is already understood well
   enough, by a third party, to correctly derive true per-eye stereo projections** — not just a
   depth-based illusion. That's essentially the same core problem as `ENGINE-DOSSIER.md` §6 (camera
   & projection delivery). vorpX's actual implementation is closed-source/proprietary, so this
   isn't a source to copy from, but it is strong independent confirmation that the underlying
   problem (find the VP/projection matrices, override them per-eye) is solvable for this engine —
   not a case where the renderer does something exotic that defeats standard approaches.
3. **Head tracking in third-person was reportedly functional** via vorpX — useful context for this
   project's own comfort/design decisions later, even though vorpX's implementation details aren't
   accessible to learn from directly.

## Caveats

- vorpX forum content changes/gets superseded over time (the thread itself notes an older profile
  being replaced by a better one) — treat "it works" as directionally true but re-verify current
  profile quality rather than assuming the exact configuration described is still the best one.
- None of vorpX's technique is public/documented in a reusable way — this is a *feasibility* signal,
  not a technical shortcut. The actual camera/projection reverse-engineering for `ENGINE-DOSSIER.md`
  §6/§7 still has to be done independently, same as every other project in this portfolio.

## Concrete next step

When DRM/injection recon starts (`ENGINE-DOSSIER.md` §4), record the Denuvo-on-Steam /
Denuvo-free-on-Origin split as a known fact rather than something to test blind, and treat the
"vorpX already hooks and stereo-renders this exact build" result as reassurance that a from-scratch
D3D11 proxy-DLL approach is very likely viable here, unlike the extra caution warranted on the
Burnout Paradise front.

## Sources

- https://www.vorpx.com/forums/topic/mad-max/
- https://www.vorpx.com/forums/topic/mad-max-g3d-fix-for-the-lights/
- https://www.vorpx.com/forums/topic/mad-max-works-no-3d/
- https://www.vorpx.com/more-headtracking-z-buffer-vs-geometry-3d/
