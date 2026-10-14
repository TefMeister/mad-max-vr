# 2026-10-14: the sun pass's view rays follow the head pose (`/pd`, dev PC, no launch)

Follows `2026-10-14-lm-the-head-pose-turns-the-world.md`: with a head turn or look-up the geometry moved right, but
the ground went dark or hazy, the car's shadow became a misplaced blob and a dark band crossed the ground.

## 1. Where the lighting gets its positions `[inferred-static]`

From the shipped shader bundle (`Shaders_F.shader_bundle`, read with
`dev-archive/recon/2026-10-11-pd-the-ao-box-under-the-car/bundle-named-disasm.py`):

- `deferred_sunlight`, VS #28, reads an 80-byte cbuffer at VS b1. For the full-screen triangle at clip `(x, y)` it
  builds a view ray `r = ((x·c1 + y·c2 + c4).xyz / (x·c1 + y·c2 + c4).w) · c0.x`. Row `c3` is never read.
- Its pixel shader takes `P = r / (depth·c0.x + c0.y)` and the world position as `P + GlobalConstants[4]`.
- That buffer is never edited by us, so every lit pixel is placed where the UNTURNED camera would have seen it.
  This matches what was seen: the geometry turns, the light and shadow lookups do not.
- Not seen yet: the real width of that buffer at run time. The bind census shows VS b1 widths of 16, 32, 64, 96,
  128, 192, 256 and 384 but no 80, and this engine allocates bigger than it declares.

## 2. The edit (`staging/mad-max-vr/proxy-dxgi/src/cbfp_ray.c`) `[verified-numerically 2026-10-14, n=1 synthetic camera]`

- **Shape test:** c4's ray and the vector `g` that gives the divide (`w = xyz·g`, solved from rows c1, c2, c4) must
  both point within 0.995 of the camera's forward (column 3 of the shared V·P). Anything else is left alone.
- **Turn:** rows become `K⁻¹ · rows`, so a pixel of the turned camera reads the matching unturned ray. The eye's
  sideways shift drops out (it lives in K's row 2, the unread row), and the sun-origin edit already moves the
  camera position for it.
- **Divide:** rebuilt along the TURNED forward, with the same length, so depth is measured the turned way.
- Offered to VS/PS b1-style buffers 80..384 bytes wide, only while a head pose is set. Counters
  `SUN RAYS ... turned / without the shape` in the 5-second report; the first edited buffer is logged once,
  before and after (`cbfp ray: first sun-ray buffer`).
- Self-test section 17: a turned and tilted head gives the turned camera's rays at 9 screen points (to 2e-4);
  no turn leaves them unchanged; colour data and a clip matrix are refused untouched. 157/157.
- Built and installed `a3d31f3aa06b` (old `bd84d87cf463` kept in the build-backups folder), staging `4319fcc`,
  stamped. Not run.

## 3. What the next launch should show

- The log line `cbfp ray: first sun-ray buffer` appears once a pose is set. If it never appears, the counter says
  how many candidates lacked the shape: then the buffer is laid out differently from the shader's declaration.
- With `15 0 0 0 0 0`: ground lit like no pose, shadow under the car. With `0 10 ...`: no dark haze.

## Not established

- Whether fog (`fogvolumeapplyfs`, `foggradient`), the sky (`skybox`, 64 bytes, only x/y/w columns, so it likely
  fails the camera test and may not turn) and SSAO need the same treatment.
- The true `n` is about 0.1013 (column-2 fit), not `vp[14]`; still to be used.
- `headk_is_camera` still has no self-test; the `madmax_vr_kmode.txt` diagnostic is still in.
