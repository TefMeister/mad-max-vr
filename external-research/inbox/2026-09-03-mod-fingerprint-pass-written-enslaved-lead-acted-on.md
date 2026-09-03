# Modding verdict: the `enslaved-vr` detector lead was acted on the same day — probe written, one launch left

**From:** `/pd` (modding lane), 2026-09-03, dev PC
**About:** `topics/2026-09-03-the-detector-this-project-needs-is-already-built-in-enslaved.md` (currently 🆕 new)
**Suggested INDEX status:** ✅ **incorporated**

## What happened

The drop's central claim — that §6's "must be found by value" row splits, and that **writing** the
probe is `[PD]` work — was correct and has been carried out. The `dxgi.dll` proxy now carries a
constant-buffer fingerprint pass (`staging/mad-max-vr/proxy-dxgi/src/cbfp.c`):

- builds clean, 64-bit, exports unchanged `[compile-verified 2026-09-03]`;
- its logic is tested offline against constructed ground truth by a harness that `#include`s the
  shipped source, 17 assertions passing `[verified-numerically 2026-09-03, n=17]`;
- deployed to the game folder with a dated backup;
- **never run against the game.** Nothing about Mad Max's runtime behaviour is established.

All three carried-over lessons were taken: both readings pre-committed in the code so one launch
suffices, every slot fingerprinted rather than only matrix-shaped reads, and raw floats logged in
buffer order with no layout interpretation (the line the probe prints for a contiguous run says
"4×4-SHAPED — shape only; layout NOT interpreted").

## One correction the drop could not have known

Re-running `dxbc-reflect.py` to pick the runtime discriminator showed **`GlobalConstants` is two
distinct layouts, not one** `[inferred-static 2026-09-03]`:

```
2352 bytes (465 shaders)   Globals[+0,272]  = 17 float4 slots   + LightPositions + LightColors
 512 bytes (186 shaders)   Globals[+0,320]  = 20 float4 slots   + ShadowTransform
```

465 + 186 = 651, matching the dossier's own shader count, so it is the same population read more
carefully. The drop's "fingerprint all 20 slots" is therefore **17 in one buffer and 20 in another**;
the probe watches both. `ShadowTransform` (three 4×4s) makes the 512-byte layout very likely the
shadow-pass variant, which matters when reading a result off it. `ENGINE-DOSSIER.md` §6 is corrected.

## What the board now says

The `[FLAT]` row was split as suggested. The `[PD]` half is done; the `[FLAT]` half is one launch,
and both of its outcomes are already written down in the log the probe emits.

Full write-up: `modding-notes/2026-09-03-constant-buffer-fingerprint-pass.md`.
