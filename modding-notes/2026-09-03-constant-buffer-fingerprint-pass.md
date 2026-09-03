# The shared-view-matrix probe is written — and reflection corrected itself on the way

**2026-09-03, dev PC, `/pd` (parallel development).**
**The game was not launched. Nothing in this note has been run against Mad Max.**

## Why this session existed

`ENGINE-DOSSIER.md` §6 ends on a specific admission: shader reflection off disk names the
*per-object* camera transform (`InstanceConsts.WorldViewProjMatrix` at +0, 112 shaders) but cannot
name a *shared* one, because the engine fills `GlobalConstants` from C++ and its RDEF type record is
a nameless `float4` array. The dossier's own wording was:

> if one exists it must be found by value (a probe watching `GlobalConstants` for a slot that changes
> with the camera but is constant across draws in a frame)

A `/gr` drop that landed in `engine-research/inbox/` this morning made the point that this sentence
describes **two** pieces of work, not one, and that only the second needs a running game: writing the
probe is static work, and the sibling `enslaved-vr` project has already validated the same
discriminator in D3D9. That is the whole content of this session — the probe is now written, built
and tested offline.

## What reflection actually says — a correction to §6

Re-running `dxbc-reflect.py` against the shipped `Shaders_F.shader_bundle` to pick a runtime
discriminator turned up that the dossier had flattened two buffers into one.
`[inferred-static 2026-09-03]`

```
cbuffer GlobalConstants   size 2352 bytes  (465 shaders)
    +0     Globals            272 bytes   <- 17 float4 slots
    +272   LightPositions    1040 bytes
    +1312  LightColors       1040 bytes

cbuffer GlobalConstants   size  512 bytes  (186 shaders)
    +0     Globals            320 bytes   <- 20 float4 slots
    +320   ShadowTransform    192 bytes
```

**There are two distinct `GlobalConstants` layouts, not one**, and 465 + 186 = 651 matches the
dossier's own shader count, so this is the same population read more carefully rather than a
different one. The consequences are small but real:

- The dossier's "`float4 Globals[20]`, buffer size 2352" is a **mix of the two**: the 2352-byte buffer
  has `Globals[17]`, and it is the 512-byte buffer that has `Globals[20]`. Corrected in §6.
- "~20 slots in one named buffer" is really **17 slots in one buffer and 20 in another**, so the
  probe has to watch both, and it does.
- `ShadowTransform` at +320 of the small layout is 192 bytes — three 4×4s, i.e. cascade shadow
  matrices. Named, therefore not a camera candidate, but it means the small `GlobalConstants` is
  very likely the shadow-pass variant, which is worth knowing before reading any result.

### And the register, which was never recorded at all

`dxbc-reflect.py` read the RDEF resource-binding table but never reported it, so a new `bind` mode
was added. `[inferred-static 2026-09-03]`

- **`GlobalConstants` binds to `b0` in all 651 shaders** — unanimous, no exceptions.
- `cbInstanceConsts` is `b1` in 823 shaders (`b3` in 63, `b2` in 7); the unwrapped `InstanceConsts`
  is `b1` in all 176.
- ⚠️ **`b0` is not exclusively `GlobalConstants`** — a buffer named `cb0` also binds `b0` in 16
  shaders. A future patch has to key on more than the register.

This is needed whichever way the launch goes: if the shared matrix exists it is patched in `b0`, and
if it does not, the per-object matrix is patched in `b1`. So it was worth doing before the launch
rather than after it.

**Why the numbers should be believed.** The binding record layout is easy to misread and a wrong
`BindPoint` would look perfectly plausible, so the mode cross-checks every binding name against a
cbuffer declared in the same shader: **all 1363 shaders matched, none orphaned.** And because §6 says
to re-run a tool after editing it, `summary` and `find GlobalConstants` were re-run afterwards and
reproduced the pre-edit dump **byte-for-byte**, so nothing above rests on a changed parser.

What has **not** changed: no member of either `Globals` has a recoverable name, so the by-value
search is still the only route. Reflection narrowed it; it cannot finish it.

## The probe

Added to the existing live-verified `dxgi.dll` proxy (`staging/mad-max-vr/proxy-dxgi/`), as
`src/cbfp.c` + `src/cbfp.h`. It is diagnostic only — it reads, logs and forwards, and never alters a
value the game wrote.

**Where it attaches.** Two routes, because one launch has to be enough:

- **Route A** — the proxy already hands back the factory the game asked for, so `CreateSwapChain` is
  patched in that factory's vtable. When the game creates its swapchain we get its `ID3D11Device`,
  hence its immediate context, hence `Map` / `Unmap` / `UpdateSubresource`, and `Present` from the
  swapchain itself. This is the expected path: the 2026-08-25 log shows the game calling
  `CreateDXGIFactory1` and taking the factory back successfully.
- **Route B** — a watchdog that fires only if route A has produced nothing after 90 s. Every
  `ID3D11DeviceContext` the runtime creates shares one vtable, and so does every `IDXGISwapChain`, so
  a throwaway device and a 1×1 hidden-window swapchain of our own expose the same function pointers
  the game's objects dispatch through. On a normal launch it never runs.
- If both fire, the hook logs whether the two vtables **matched**. That is the shared-vtable
  assumption being tested rather than assumed.

**What it measures.** Per frame, per tracked buffer (`ByteWidth` 2352 or 512, bound as a constant
buffer), which 16-byte slots were byte-identical across *every* write in that frame. Then, on the
user's mark, which of those frame-constant slots **changed** between two marked frames.
Constant-within-frame **and** changed-between-marks is the signature of a shared per-frame camera
constant.

**Hotkeys** (NumLock-independent, alongside the existing NUMPAD1/2 memory scanner):

| Key | Effect |
|---|---|
| NUMPAD3 / PgUp | full raw dump of the next frame — all 32 slots, marked `CONST`/`vary` |
| NUMPAD4 / ← | mark **A** (stand still) |
| NUMPAD5 / Clear | mark **B** and compare (after moving the camera) |

It also logs which API path each buffer is filled through (`Map`/`Unmap` vs `UpdateSubresource`) and
a running census of every constant-buffer size it sees. The first is dossier §7, which was entirely
blank and would otherwise have been a separate investigation; the second is insurance against the
size discriminator being wrong.

### Three things carried over from `enslaved-vr`, one of them a warning

1. **Both readings are pre-committed**, in the code, so the log states the conclusion rather than
   leaving data to interpret later. That is what makes one launch sufficient.
2. **All 32 slots are fingerprinted, not just matrix-shaped reads.** With no member names a 4×4 could
   begin at any slot, and the shared value may not be a matrix at all.
3. **⚠️ Raw floats in buffer order, uninterpreted.** No transposition, no matrix reconstruction, no
   "this looks like a view matrix". Enslaved's own 2026-09-01 register layout was transposed and was
   `[disproved]` the next day; a C++-filled D3D11 buffer carries no layout guarantee either. The
   probe reports a run of ≥4 contiguous constant slots as *4×4-shaped* — shape only, and it says so
   on the line.

## What is established, and what is not

- **Builds clean, zero warnings**, 64-bit, exports unchanged
  (`CreateDXGIFactory`/`1`/`2`). `[compile-verified 2026-09-03]`
- **The fingerprint logic is tested offline against ground truth**, by a harness that
  `#include`s `cbfp.c` itself — the shipped code, not a transcription of it (the Far Cry 2 lesson).
  It fabricates frames whose answer is known by construction and asserts the reported answer:
  18 assertions, all passing. `[verified-numerically 2026-09-03, n=18]` Run it with
  `bash test/build-and-run.sh`. It covers the camera-moved case, the camera-did-not-move case, a
  frame-constant-but-unchanging slot being correctly *excluded*, a within-frame-varying slot never
  becoming a candidate, the ≥4 run rule, and the `Globals` region bounds above.
- **Deployed** to `Mad Max\dxgi.dll`, with the previous build kept as
  `dxgi.dll.bak-2026-09-03-pre-cbfp` — one file copy reverts it.
- **NOT established: anything at all about how Mad Max actually behaves at runtime.** No hook has
  ever fired. Route A is inferred from one log line showing `CreateDXGIFactory1` succeeding; that the
  game then calls `CreateSwapChain` *on that factory* is a reasonable expectation, not an observation.
  Whether either `GlobalConstants` is written more than once per frame is unknown, and if it is
  written exactly once then "constant across draws" is trivially true and proves nothing — the probe
  prints the write count next to every verdict for exactly that reason.

### The diagnostic that would show the derivation is wrong

If the A/B run flags slots, the failure mode to fear is not a wrong slot but a *wrong reason*: a slot
can change between two marks because the camera moved **or** because time advanced. Take mark A and
mark B **without moving the camera at all** first. Anything flagged by that run is time-varying, not
camera-varying, and must be subtracted from the real run's candidates. The probe supports this
directly — mark A / mark B is repeatable as often as you like.

If nothing is flagged even when the camera has plainly moved, and the write count is greater than
one, that is the honest negative: there is no shared camera constant in `GlobalConstants`, the camera
is baked into per-object `InstanceConsts.WorldViewProjMatrix`, and §6 shifts to a per-draw patch.
That outcome is worth as much as the positive one, and the log says so in words.

## Files

- `staging/mad-max-vr/proxy-dxgi/src/cbfp.{c,h}` — the pass.
- `staging/mad-max-vr/proxy-dxgi/test/fp_selftest.c`, `test/build-and-run.sh` — the offline test.
- `dev-archive/recon/2026-09-03-cbfp-fingerprint-pass/` — the reflection dump this was derived from,
  and the skeleton of the 2026-08-25 proxy log (its 52,986 `CHANGED` rows from the parked FOV scan
  are elided; the 6.8 MB original stays on the dev PC as
  `madmax_vr_proxy_log.2026-08-25-fovscan.txt` and is not committed).
