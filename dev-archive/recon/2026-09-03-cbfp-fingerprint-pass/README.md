# 2026-09-03 — evidence behind the constant-buffer fingerprint pass

`/pd` session, dev PC. **The game was not launched.**

| File | What it is |
|---|---|
| `2026-09-03-globalconstants-reflection.txt` | `dxbc-reflect.py find GlobalConstants` + `summary` against the shipped `Shaders_F.shader_bundle`. This is the dump the §6 correction (two `GlobalConstants` layouts, not one) and the probe's runtime size discriminator are both derived from. Interface metadata only — buffer names, sizes and byte offsets — no game content. |
| `2026-09-03-cbuffer-register-bindings.txt` | `dxbc-reflect.py bind` over the same bundle: which register (`b#`) each constant buffer binds to. `GlobalConstants` is `b0` in all 651 shaders. The header line is the tool's own self-check — every binding name matched a cbuffer in the same shader across all 1363 shaders, which is what says the record layout is being read correctly. |
| `2026-08-25-fovscan-log-skeleton.txt` | The 2026-08-25 proxy log with its 52,986 `CHANGED addr=` rows elided (26 lines survive). Kept because those 26 lines are the only record that the DXGI proxy loaded, that `CreateDXGIFactory1` was called and returned a factory, and how large the FOV memory scan actually was. The 6.8 MB original stays on the dev PC as `Mad Max\madmax_vr_proxy_log.2026-08-25-fovscan.txt` and is deliberately not committed. |

Reproduce the reflection dump with:

```
python flat-to-vr-RE-toolkit/tools/dxbc-reflect.py "<game>/Shaders_F.shader_bundle" find GlobalConstants
python flat-to-vr-RE-toolkit/tools/dxbc-reflect.py "<game>/Shaders_F.shader_bundle" bind
```

Write-up: `modding-notes/2026-09-03-constant-buffer-fingerprint-pass.md`.
