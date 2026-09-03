# 2026-09-03c (`/pd`, home PC, NO LAUNCH) — the two `GlobalConstants` layouts are the VERTEX and PIXEL views, slots 16..19 are not a matrix, and the clip transform is at slots 0..3 — per pass

**The game was not launched and nothing here has been run.** Everything below is
`[inferred-static 2026-09-03]` from disassembling the shipped shaders, `[verified-numerically]`
for the probe's new logic, or `[compile-verified]` for the build; the one launch this sets up is
in §6.

Source: `staging` `4533ec9` (`proxy-dxgi/`). Deployed on the home PC: `Mad Max\dxgi.dll`
237,056 B (previous 70,656 B build kept as `dxgi.dll.bak-2026-09-03c-pre-bindcensus`),
hash-verified. Evidence: `dev-archive/recon/2026-09-03c-stage-split-and-slot-usage/`.
New tool: `flat-to-vr-RE-toolkit/tools/dxbc-usage.py`.

---

## 1. In plain words

The board had two static rows from the first live run. One said: "the probe found four
consecutive slots (16..19) that *look* like a 4×4 matrix — check them against the per-object
`WorldViewProjMatrix` before believing it." The other said: "the static shader census predicted
a 2352-byte buffer that the running game never used, and a 3136-byte buffer that no shader
mentions — sort that out."

Both were answerable from the shader bundle on disk, by going one level deeper than reflection:
**disassembling the shaders and reading what they actually do with each slot.** Reflection tells
you a buffer's shape; the disassembly tells you which slots the code touches and how.

- **Slots 16..19 are not a matrix.** Two of the four are read by *no shader at all*, and the
  other two are used as "offset plus scale" for a texture coordinate. The 4×4 shape was a
  coincidence of layout.
- **The two layouts are not "main" and "shadow"; they are the vertex-shader view and the
  pixel-shader view of the same buffer.** Every one of the 186 shaders declaring the 512-byte
  layout is a vertex shader; every one of the 465 declaring 2352 bytes is a pixel shader. So the
  running game never binding a 2352-byte buffer just means the pixel side is allocated bigger
  (3136 bytes) than the shaders declare — which Direct3D allows — and that is why 3136 and 512
  appeared in lockstep: they are the two halves of one thing.
- **The camera matrix is at slots 0..3 of the vertex-side buffer — and the probe's own filter
  hid it.** Fifteen vertex shaders multiply the incoming position by slots 0..3 as a full 4×4;
  in two of them the result goes straight to `SV_Position`, which is the clip-space position.
  Those slots change *within* a frame (one value per rendering pass, ~10 passes) — exactly what
  the probe's "constant within the frame" rule was built to exclude, because it was hunting a
  *per-frame* constant. A per-*pass* camera is the more common design, and it is what this is.

So the crucial-section question — "is there a shared view-projection?" — now has a fuller
answer: **yes, at slots 0..3 of the vertex-side `GlobalConstants` (b0), written per pass** — but
the *majority* of vertex shaders do not use it for their position; they use a per-object
`WorldViewProj` in `InstanceConsts` (b1, slots 0..3). Both paths matter for VR.

## 2. What the disassembly says

Method: `dxbc-usage.py Shaders_F.shader_bundle GlobalConstants --slots 0-5,9,16-19` — every
DXBC blob split by stage from its RDEF header, disassembled with `fxc -dumpbin`, and every
`cb<N>[slot]` reference tallied where `N` is the register `GlobalConstants` binds to in that
shader. 651 shaders, 0 disassembly failures.

### 2a. Stage split `[inferred-static 2026-09-03, n=651]`

| declared size | stage | shaders | companions |
| --- | --- | --- | --- |
| 512 (`Globals` 20 slots + `ShadowTransform`) | **vs, all 186** | 186 | `cbLightingConsts` 110, `InstanceConsts` 109, `cbInstanceConsts` 64 |
| 2352 (`Globals` 17 slots + light arrays) | **ps, all 465** | 465 | `cbInstanceConsts` 335, `booleans` 277 |

**No cbuffer of size 3136 exists anywhere in the bundle** (all 84 layouts, 1363 shaders).
Arithmetic that fits but is not evidence: `3136 = 320 + 2 × 1408` — a 20-slot `Globals` plus
88-entry light arrays — while `2352 = 272 + 2 × 1040` is 17 slots plus 65-entry arrays.
`[hypothesis]` on the meaning; the bind census (§4) is what will say whether 3136 sits at `PS b0`.

The 2026-09-03 `/pd` reading "`ShadowTransform` makes the 512-byte layout very likely the
shadow-pass variant" is **`[disproved 2026-09-03c]`** — `ShadowTransform` (slots 20..31) is the
three cascade matrices the *vertex* shaders read to project into the shadow maps; 57 of them do.

### 2b. Slot usage, vertex side (512) `[inferred-static 2026-09-03]`

| slot | read by | how | reading |
| --- | --- | --- | --- |
| **0..3** | 15 vs | `mul r, v0.y, cb0[1]; mad r, v0.x, cb0[0], r; mad r, v0.z, cb0[2], r; add o0, r, cb0[3]` | **full 4×4 on the position; `o0` = `SV_Position` in shaders 0009 and 0023** — a clip-space transform. Row-vector form (`pos · M`, translation in row 3) |
| 4 | 25 vs | `add r, worldpos, -cb0[4].xyz` | a position subtracted from world positions: a **per-pass view origin** (varies within the frame) |
| 5 | 84 vs | `dp3 …, cb0[5].xyz, -cb0[8].xyz`; scaled adds | a direction; with slot 8 (110 vs) probably light/view directions |
| 8 | 110 vs | direction maths | see 5 |
| **9** | 146 vs | `add r, v0.xyz, -cb0[9].xyz` | **the main camera position** — usage matches the probe's reading (`w = 1`, moved ~4 units on an orbit, frame-constant) |
| 12, 13 | 134 vs | `mad … cb0[12].x/.z`, `mul_sat … cb0[13].w; min … cb0[13].y` | packed fog/fade parameters (`3000.0` far, `1/1.2`, `1/300`) |
| **16, 17** | 13 vs | `mov r1.x, cb0[16].w; mad o3.xyz, r0.xyz, r1.xxz, cb0[16].xyz` | **`xyz` offset + `w` scale for a projected coordinate** — not matrix rows |
| **18, 19** | **0** | — | **read by nothing** |
| 20..23, 24..31 | 15 / 57 vs | matrix chains | `ShadowTransform`: cascade matrices |

Pixel side (2352): slots 1, 3, 5 are read by 300+ shaders (light/ambient terms); its slot 16 is
used with exactly the `mul_sat / mad / min` pattern the vertex side applies to its slot 13, so the
two `Globals` structs are *different* layouts of overlapping content (the PS one has no matrix at
0..3; its slot 0 is read by nothing) — consistent with a different HLSL header per stage.

### 2c. Where the clip-space position comes from, across all 186 vertex shaders

Walking the register chain back from `o0` (tool section D): **`InstanceConsts` b1 slots 0..3 in
109 shaders and `cbInstanceConsts` b1 slots 0..3 in ~35** — the per-object `WorldViewProjMatrix`
that reflection named on 2026-09-01 — versus **`GlobalConstants` slots 0..3 in 15**. The shared
per-pass matrix serves world-space draws (sky, particles, decals, simple quads); the bulk of the
scene carries the camera baked into each object's WVP. **For VR that means both:** patching the
per-pass matrix alone would move 15 shader families and leave the world in place.
`InstanceConsts` slots 4..15 sit on the position path in 56 shaders and 16/17/22 in ~80 — whether
a separable world matrix lives there is the next static question (§7).

## 3. What the first live run's log already corroborates

`[measured 2026-09-03b]`, read back against the disassembly rather than re-measured:

- In gameplay frames the frame-constant list starts at slot 6: **slots 0..5 vary within the
  frame** (written 10–11× per frame with different values). That is what a per-pass clip
  transform (0..3) plus per-pass view origin (4) and direction (5) look like. In the menu, with
  one write per frame, all 32 slots were trivially "constant".
- Slot 9 was frame-constant and camera-varying with `w = 1` — the main camera position, exactly
  as the vertex shaders use it.
- Slots 16/17 changed enormously under the sweep while 18/19 barely moved — consistent with
  16/17 being camera-anchored projection offsets and 18/19 being unused padding or stale data.
- The 3136 and 512 creation counts tracked 1:1 through 48 — one allocation pair per frame
  context, vertex half + pixel half.

## 4. What the probe now does (built, not run)

`staging 4533ec9`, `[compile-verified 2026-09-03]`, self-test **30/30**
`[verified-numerically 2026-09-03, n=30]` (was 17; the harness includes the shipped `cbfp.c`):

1. **Tracks 3136** alongside 512 and 2352, all 32 slots fingerprinted.
2. **Bind census** — hooks `VSSetConstantBuffers` / `PSSetConstantBuffers` and counts
   `(stage, slot, ByteWidth)`; logs each first sighting once (`cbfp bind: first sighting VS b0 <-
   512-byte …`) and a compact table every 300 frames. Unlike the creation census, this unit means
   what it says.
3. **Per-write dump** — `NUMPAD3` now also prints slots 0..4 and 9 of *every* write of the
   512-byte buffer in that frame (capped at 16) and flags the write whose slot-4 view origin
   equals the slot-9 main-camera position: **`<== slot 4 == slot 9: … MAIN PASS candidate`**.
   Its slots 0..3 are the main-pass clip transform.
4. The A/B result now carries a note that a per-pass matrix is excluded by design and points at
   the dump.

Build scripts find `llvm-mingw` on either machine (PATH first, then the per-user WinGet path).

## 5. What is NOT established

- **That slots 0..3 hold the *main camera's* view-projection** rather than only shadow/reflection
  passes'. The disassembly proves the slots carry a clip-space transform for world-space
  positions and the log proves they change per pass; which write is the main pass is what the
  per-write dump decides. Falsifier: no write has slot 4 == slot 9 → slot 4 is not the view
  origin (or the main pass writes it elsewhere), and the 0..3 rows must be read by eye.
- **That the 3136-byte buffer is the pixel-side `GlobalConstants`.** Pairing + no other size
  fitting is strong; the bind census reading `PS b0 <- 3136` is the confirmation. Falsifier: it
  binds somewhere else, or `PS b0` shows 2352 after all.
- **Handedness, row/column convention, and where `P` comes from** — none of that is touched. The
  chain `pos.x·M[0] + pos.y·M[1] + pos.z·M[2] + M[3]` fixes the *storage* as row-vector
  (translation in the fourth slot); nothing more.
- **Whether `InstanceConsts` carries a separable world matrix** (§7). If it does not, the
  per-object path needs its WVP re-derived per draw from something else.

## 6. Next launch — the one dump, and what each outcome means

Launch normally (Steam is fine; the proxy is `dxgi.dll` in the game folder), reach gameplay, stand
still, press **`NUMPAD3`** once, then quit. Read `madmax_vr_proxy_log.txt`:

1. `cbfp bind: first sighting VS b0 <- 512-byte` and `PS b0 <- 3136-byte` → the stage split and
   the pixel-side allocation are confirmed; the `[hypothesis]` in §2a becomes `[verified-live]`.
   `PS b0 <- 2352` instead → the pairing story was wrong and 3136 is something else.
2. In the per-write dump, **exactly one write flagged `MAIN PASS candidate`** → its slots 0..3
   are the main camera's clip transform; note the frame's write index (the pass order). Several
   flagged with identical 0..3 rows → depth pre-pass + main share the eye; still the answer. None
   flagged → §5 first falsifier; read the rows by eye (the main pass is the one whose 0..3 rows
   change smoothly with a small mouse move between two dumps).
3. Optional while there: `NUMPAD4`, orbit, `NUMPAD5` — the A/B still runs and should again name
   9/12/13 and 16/17 (a regression check on the probe, nothing new).

## 7. Queued for a static session

- `InstanceConsts` slots 4..15 / 16 / 17 / 22 on the position path: is there a world matrix
  (or a world-view) separable from the WVP? `dxbc-usage.py … InstanceConsts --slots 0-23
  --stage vs` is the whole command.

## 8. Method note

Reflection got this project to "20 unnamed slots"; **disassembly is what names them**, and it
is on disk, Denuvo or not. The tool is generic (`dxbc-usage.py`) and the lesson is not: a
by-value probe with a "constant across the frame" filter cannot see a per-pass camera, and a
4×4-shaped run of slots is shape, not meaning.
