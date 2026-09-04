# 2026-09-04c (`/pd`, dev PC, static only) — the per-eye edit is ONE FLOAT, there is no separable world matrix, and the census tool was over-reporting

**The game was not launched, and nothing here has been run.** Both `[PD]` rows on the board are
answered; the stereo edit is built, self-tested and deployed. What is not established is that any of
it renders — the algebra and the write path are proven, the picture is not.

---

## 1. The per-object row: no separable world matrix

One command, as the row specified:

```
dxbc-usage.py Shaders_F.shader_bundle InstanceConsts --slots 0-23 --stage vs
```

`[inferred-static 2026-09-04, n=113 shaders]` Of the 113 vertex shaders declaring `InstanceConsts`,
112 use the 368-byte layout, and their slots divide cleanly:

- **0..3** — the full object→clip 4×4, row-vector, straight into `SV_Position` in all 112.
- **4..15** — **four repeated groups of three**, each `add(-pos, A)` / a `w`-difference blend /
  `add_sat(dp3(-delta, dir), bias)`. That is a falloff shape, not a transform. 56 shaders.
- **16, 17** — sign tests and scalar multiplies; 17 is an instance scale on the position path in 75.
- **18..21** — a 3×4 affine, and the one that looks like the answer. It is not: see §3.
- **22** — a fade threshold.

The second per-object buffer, **`cbInstanceConsts`** (188 vertex shaders, nine sizes from 16 to 160
bytes, at `b1` or `b3`), puts its clip transform at **slots 0..3** in every size too.

Tracing what actually reaches `SV_Position` leaves a complete and very short path:

```
clip = (v0 + cbLightingConsts[3].xyz) · InstanceConsts[0..3]
```

`cbLightingConsts` is a nameless 64-byte block — reflection gives one member, `LightingConsts`,
64 bytes, no names inside, the same "engine fills it from C++" shape as `GlobalConstants`. Its
slots 0..2 do colour work (a two-colour lerp and a multiplier); **slot 3 alone is a pre-translation**
of the object-space vertex position, read by all 112.

**⇒ The row's second branch is the live one:** nothing separable means the per-object path has to be
reached by hooking its CPU-side fill, not by recomputing `W · VP_eye`. §2 makes that much cheaper
than it sounded.

## 2. The per-eye edit is one element — of the matrix, on both paths

`[verified-numerically 2026-09-04, n=33 Python cases + 26 C assertions]`

Row-vector storage (`clip = pos · M`) was established 2026-09-03c. A per-eye camera shift is
`V_eye = V · T`, `T` a translation of `d` along the **view** x axis:

```
M_eye = W · V · T · P = M + W · (V·T − V) · P
```

`(V·T − V)` has exactly one non-zero entry, `[3][0] = d`. For any **affine** `W` — fourth column
`[0,0,0,1]ᵀ`, true of every object transform — the product keeps that shape, and post-multiplying by
`P` turns it into "row 3 += d × (row 0 of P)". Row 0 of a perspective projection is `[w,0,0,0]` for
symmetric **and** off-centre frusta, because an off-centre frustum puts its shift in row 2. So:

```
M[3][0] += d * w          w = |column 0| = the horizontal focal term (1.1809 measured live)
```

**This supersedes the board row's own plan.** That row said to replace slots 0..3 with `V_eye · P`
rebuilt from the live decomposition, "leaving column 2 / row 3.z alone" because the reversed-Z shape
is a `[hypothesis]` and the clip-z constant is unexplained. The one-element edit **never reads or
writes either of them**, so neither question can affect it and no error in either can corrupt the
picture — and it is one float instead of sixteen. It also applies unchanged to the per-object path.

⚠️ **`w` must come from the SHARED matrix.** `|column 0|` of a per-object matrix includes the
object's scale — a 3×-scaled object reads 3.54 where `w` is 1.18. Asserted in both harnesses, and
the constraint the per-object path will have to respect when it is built.

**How it was checked.** First in Python (`one_element.py`): build `W`, `V`, `P` independently,
multiply out `W·V·T·P`, compare against `M` with the single element edited — 33 cases over an
ordinary projection, a reversed-Z-infinite one and an off-centre one, with rotation, scale and
5,000-unit translations. Then in C, against the **shipped** `apply_eye_offset()`, inside the proxy's
own harness with its own independent matrix helpers: 12 more cases plus the `w`-source and
fail-safe assertions. **The self-test went 30 → 63 assertions, all passing.**

**The build.** `cbfp.c`'s `hk_Unmap` applies the edit in place on the still-valid mapping, before
`real_Unmap`, only on the 512-byte vertex-side buffer, and only where `slot 4 == slot 9` — the same
main-pass discriminator the diagnostic dump has used since 2026-09-03c, so the shadow cascades and
the five local perspective cameras are deliberately untouched. It refuses a non-finite element, a
NULL pointer or a non-positive `w` and leaves the bytes alone. OFF until **NUMPAD6**; NUMPAD7 cycles
wiggle/left/right, NUMPAD8/9 scale the separation by 1.25. `[compile-verified 2026-09-04]`, clean at
`-Wall`, all three exports intact. **Deployed** to `Mad Max\dxgi.dll` (241,152 B); the previous build
is `dxgi.dll.bak-2026-09-04c-pre-stereo` (237,056 B) and one copy reverts.

## 3. ⚠️ A tool of ours was over-reporting, and it is fixed

`dxbc-usage.py`'s section D walks back from `SV_Position` to say which cbuffer slots feed the
position. **It indexed writes by register name with no regard to program order**, so reaching a
register pulled in every write to it anywhere in the shader — including writes *after* the `o0`
write, which cannot possibly feed it. Shader registers are reused aggressively, so this was not a
corner case. Mad Max shader 0282 writes `r0`, feeds `o0` from it, then reloads `r0` with the
slot-18..21 transform destined for `o3`; the old walk reported slots 18..21 as feeding `SV_Position`
in 16 shaders. **They do not.** That is exactly the false lead that would have sent this project
hunting a per-object world matrix that does not exist.

Fixed to take only the last write **before** each consumer. Section D drops from 40+ rows to 6.
`[verified-numerically 2026-09-04, n=6 cases]` — a new regression test,
`flat-to-vr-RE-toolkit/tools/test/test-dxbc-usage-poschain.py`, covers the reuse case, a genuine
three-hop chain (the walk must not over-correct), `o0` written in pieces, two writes before one
consumer, a direct read into `o0`, and a passthrough.

**Re-audit, per the standing rule.** The tool was used on 2026-09-03c. Its sections A/B/C — the
size/stage census, the slot histogram and the sample instructions — **reproduce byte-for-byte**
after the fix, and they are what those conclusions rested on ("all 186 shaders declaring 512 B are
vertex shaders", "slots 18/19 are read by no shader", "16/17 are xyz offset + w scale", "slots 0..3
are the clip transform"). Those stand. Only "feeds `SV_Position`" claims from section D were
affected, and the only one recorded was for slots 0..3, which survives.

## 4. What the next launch answers

The game is not running on this PC. One launch, get into gameplay, then:

| step | what it means |
| --- | --- |
| press **NUMPAD6** | the log prints `STEREO ON`. From here the main-pass matrix is edited every frame. |
| watch the world | **wiggle mode rocks the whole world left/right each frame** and the amount scales with NUMPAD8/9. That is the edit reaching the screen. |
| watch the HUD | it must **not** move — it does not come through this buffer. If it rocks too, the discriminator is catching more than the main pass. |
| read `cbfp stereo frame=…` | `edited=0` means no write passed `slot 4 == slot 9`, so the picture *cannot* have changed — a different bug from "edited and nothing moved". |
| nothing moves but `edited` is large | the edit is landing on a matrix that is not the one on screen: the 512-byte buffer is the wrong target, or the game re-uploads after our `Unmap`. |
| **NUMPAD3's dump looks unedited** | **expected, not a fault.** `record_write()` runs before the edit, deliberately, so the dump always shows the matrix the *game* wrote. A dump with stereo on is indistinguishable from one with it off; the `cbfp stereo frame=` counters are the only place our edits show. |
| the world shears or tears | the row-vector assumption or the `[3][0]` index is wrong — dump with NUMPAD3 and compare a written matrix against a captured one. |

Capture Mode is the best place for the first try: its camera holds still, so a per-frame wiggle is
unmistakable, and it writes the same slots `[verified-live 2026-09-04]`.
