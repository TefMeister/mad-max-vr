# 2026-10-11 `/pd`: the AO box under the car

Static only; the game was not launched. Read from `Shaders_F.shader_bundle` (game file, not committed).

- `bundle-named-disasm.py <bundle> <regex> [outdir]` lists every DXBC blob with the readable name the bundle stores
  before it, and disassembles the matches with the system `d3dcompiler_47.dll` (`D3DDisassemble`). Ours; the `.asm`
  output is game-derived and is not committed.
- Blobs used: #4 `aobox` (vs_5_0), #341 `aosphere` (ps_5_0), #28 `deferred_sunlight` (vs_5_0).
- The key instructions are quoted in `modding-notes/2026-10-11-pd-the-car-shadow-is-an-ao-box.md`.
