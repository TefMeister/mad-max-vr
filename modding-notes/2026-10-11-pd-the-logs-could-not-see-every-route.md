# 2026-10-11 (late) — `/pd` (dev PC): the logs could not see every route; now they can, and the sun edit covers both

**The game was not launched, and nothing here has been run in it.**

## The question on the board

The sun-origin edit moved nothing (afternoon). Does the sun pass fill its 624-byte constants by `Map` (which that edit
touched) or by `UpdateSubresource` (which it did not)? This cannot be read off disk: the exe is packed, and the shader
bundle says nothing about how buffers are filled.

## Found while looking: our own bind census was cut short `[verified-numerically 2026-10-11]`

The `cbfp bind census` line was built in a 512-byte buffer and stopped at about 31 entries without saying so. The
afternoon logs' line is 480 characters with exactly 31 entries. So a (stage, slot, size) missing from those lines —
for example any 624-byte bind, or the AO pixel shader's b1 — is **not** evidence that it was never bound. The
"only 80-byte buffer is PS b4" reading still stands on the separate size census (`80:1`, one 80-byte buffer ever
created), but "the sun's 624-byte buffer is never bound" would not have.

## Also never watched: the D3D11.1 routes

The proxy hooked `VS/PSSetConstantBuffers`, `Map/Unmap` and `UpdateSubresource`, but not the D3D11.1
`VS/PSSetConstantBuffers1` (binds with offsets into a larger buffer) or `UpdateSubresource1`. If the game uses them,
every census so far missed those binds and fills. Whether it does is not known; the exe is packed, so its imports
cannot say.

## What was built `[compile-verified 2026-10-11]`

- **Fill census** (`cbfp_fill.c`): per width, how many `Map(WRITE_DISCARD)`, other `Map`s, whole `UpdateSubresource`
  and boxed `UpdateSubresource` calls. Read-only. One launch says which route 624 and 3136 take.
- **Bind census split over lines** (16 per line), so nothing is cut off.
- **D3D11.1 hooks**: `VS/PSSetConstantBuffers1` (lower-case `v`/`p` in the bind census) and `UpdateSubresource1`
  (counted in the fill census); a log line says whether the context offers them at all.
- **The sun-origin edit now also covers whole `UpdateSubresource`/`UpdateSubresource1` fills** of 624 and 3136 bytes,
  editing a private copy (the game's own memory is never written), with its own counter
  (`SUN ORIGIN via UpdateSubresource`). Same switch file as before: `madmax_vr_sun.txt`.
- Self-test 105/105 (9 new); build byte-identical twice; deployed `f79be82c5b20`, previous kept as
  `dxgi.dll.bak-2026-10-11-pd-pre-fill`; stamped.

## The next run (`[FLAT]`, one launch)

Same scene (Resume Game, the car in the desert, single-eye, separation 0.6054). Read the log first, then try the sun
switch:

| log / picture | means |
| --- | --- |
| fill census shows 624 by Update, and with `madmax_vr_sun.txt` the shadow now shifts like the sand | ✅ the afternoon edit was on the wrong route |
| 624 only by Map, D3D11.1 line says no context1, shadow still -1 px | the sun pass's origin is not where we think: next, find which buffer the sun pixel shader reads (bind census parts, PS b1 entries) |
| lower-case `p` entries appear (binds with offsets) | the game packs constants into big buffers; edits keyed on a buffer's width miss them, and a new key (buffer + offset) is needed |
