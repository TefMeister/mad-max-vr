# 2026-10-15 (`/pd`, dev PC, no launch): the depth-of-field composite

Scripts used to find the cockpit near blur's controls in the shipped `Shaders_F.shader_bundle`. They read the game
file and write nothing back; no game content is stored here.

- `extract.py <bundle> <outdir> <regex>`: lists every DXBC blob (offset, size, the readable name stored before it,
  shader stage, header checksum) and copies those whose name matches into `<outdir>` for `fxc -dumpbin`.
- `table.py <bundle>`: prints the checksum table for `dof_*` (kind 1) and `dofbokeh_*` (kind 2), the source of
  `staging/mad-max-vr/proxy-dxgi/src/cbfp_dof_sums.inc`.
- `coll.py <bundle>`: shows any checksum that a `dof*` shader shares with a differently named blob. Result: none
  (1363 blobs, 1054 distinct checksums; the 173 shared ones are all outside the dof family).

Findings (from `fxc -dumpbin` of all 24 `dof_*` and one `dofbokeh_*`, `[inferred-static 2026-10-15]`):

- All 24 `dof_*` variants (`pg`/`rh`/`u2` tone curves, with `_ca` colour fringe, `_ef` edge fade, `_fg` film grain,
  `_cf` colour-grade fade) build the blur weight identically from PS b1 `cbConsts` (240 bytes, 15 float4):
  `b = sat(far * c0.w + near * c2.y + c0.z)`, `out = lerp(scene, blurred, min(3b, 1))`.
- Same buffer: c0.x colour fringe offset (`_ca`), c12.w lens dirt, c14.w heat haze gate.
- `_ef` (edge fade texture, a vignette) and `_fg` (film grain, fixed 0.018 amplitude) have no strength number in the
  buffer; only the choice of variant can drop them.
- `dofbokeh_*` takes its near blur from the blurred texture's alpha (a separate compute pass), so its blur cannot be
  removed through this buffer. Keep `HQDof=0`.
