# cbfp first live run — §6 and §7 answered (2026-09-03)

`madmax_vr_proxy_log-2026-09-03-cbfp-run.txt` — the whole log from the first launch of the
constant-buffer fingerprint probe. Written to the game folder, which is outside every repository,
hence this copy.

## What it establishes

**§6: a shared per-frame camera constant EXISTS in `GlobalConstants` b0.** Run with the control
pair the design demanded:

| pair | flagged slots |
|---|---|
| control (camera NOT moved) | `16, 17, 23, 27, 31` |
| real (large camera sweep) | `9, 12, 13, 16, 17, 18, 19, 23, 27, 31` |

Camera-varying = `9, 12, 13, 18, 19`, plus `16/17` which drift slightly on their own but change
enormously with the camera. The probe flagged **slots 16..19 (+256, 64 bytes) as a contiguous
4×4-SHAPED run** and said, correctly, to cross-check it against `InstanceConsts.WorldViewProjMatrix`
before believing it.

**§7: the fill path is `Map`/`Unmap`**, 10–11 writes per frame, not `UpdateSubresource`.

## ⚠️ The static prediction did not match the runtime

The probe was armed for the two layouts the static census predicted, **2352** and **512** bytes.
Across **95 censuses / ~28,500 frames**:

- **2352 was never bound. Not once.**
- The camera constant is in the **512-byte** buffer — the one static analysis called *"very likely
  the shadow-pass variant"*.
- **3136 bytes appears in every census with a count identical to 512's**, 1:1 through 48:48.

Do not over-read those counts: they rise about once per 600 frames, far too slowly to be writes, so
they are probably distinct buffer instances. The pairing is solid; the unit is not.

Full analysis and what is *not* established:
[`modding-notes/2026-09-03b-section-6-answered-there-is-a-shared-per-frame-camera-constant.md`](../../../modding-notes/2026-09-03b-section-6-answered-there-is-a-shared-per-frame-camera-constant.md)
