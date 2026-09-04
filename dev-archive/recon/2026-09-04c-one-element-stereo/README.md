# 2026-09-04c — the per-object census, a tool defect, and the one-element stereo edit

`/pd`, dev PC, static only. **The game was not launched and nothing here has been run.**

| file | what it is |
| --- | --- |
| `instanceconsts-slot-census-2026-09-04.txt` | `dxbc-usage.py Shaders_F.shader_bundle InstanceConsts --slots 0-23 --stage vs`, **after** the tool fix below. The answer to the board's per-object row. |
| `instanceconsts-slot-census-BEFORE-the-tool-fix.txt` | the same command **before** it. Section D lists 40+ rows including `InstanceConsts` slots 4..15 and 18..21 as feeding `SV_Position`. They do not. Kept so the correction is checkable rather than asserted. |
| `cblightingconsts-slot-census.txt` | why slot 3 of that buffer is on the position path and slots 0..2 are not. |
| `cbinstanceconsts-slot-census.txt` | the *other* per-object buffer name, 188 vertex shaders across 9 sizes. |
| `k_eye.py` | the first derivation: a per-eye offset as one shared post-multiply `K = P⁻¹·T·P`. 10 randomised cases, two projection shapes. |
| `one_element.py` | the derivation that supersedes it: the edit is a **single element**. 33 cases across three projection shapes including an off-centre frustum. |
| `fp_selftest-63-assertions.txt` | the shipped proxy's own harness, now 63 assertions (was 30), including the stereo edit against independently built matrices. |

## The three findings

**1. There is no separable world matrix in `InstanceConsts`** `[inferred-static 2026-09-04, n=113 shaders]`.
Slots 0..3 are the full object→clip 4×4 (row-vector `mul/mad/mad/add`). Slots 4..15 are **four
repeated 3-slot groups** — `(position, position, direction+bias)` read with a saturating `dp3`, a
falloff shape, not a transform. Slots 18..21 *are* a 3×4 affine but its result goes to **`o3`**, a
texcoord, after being applied to a camera-relative position. So `WVP_eye = W · VP_eye` is **not**
computable per draw, which is the branch the board row named: the per-object path needs its
CPU-side fill hooked.

**2. `dxbc-usage.py`'s section D over-reported, and is fixed** `[verified-numerically 2026-09-04, n=6 cases]`.
Its walk back from `SV_Position` indexed writes by register *name* with no regard to program order,
so reaching a register pulled in **every** write to it anywhere in the shader — including writes
*after* the `o0` write, which cannot feed it. Registers are reused aggressively, so this was not a
corner case: Mad Max shader 0282 writes `r0`, feeds `o0`, then reloads `r0` with the slot-18..21
transform bound for `o3`. The fix takes only the last write *before* each consumer.
Section D drops from 40+ rows to 6; **sections A/B/C reproduce byte-for-byte**, so the
2026-09-03c conclusions drawn from them (which slots are read, and what the instructions do) stand
unchanged. Test: `flat-to-vr-RE-toolkit/tools/test/test-dxbc-usage-poschain.py`.

**3. The per-eye edit is one float, on both paths** `[verified-numerically 2026-09-04, n=33 Python + 26 C]`.
With row-vector storage, `M_eye = W·V·T·P = M + W·(V·T − V)·P`, and `(V·T − V)` has exactly one
non-zero entry. For any affine `W` and any projection whose row 0 is `[w,0,0,0]` — true of
symmetric *and* off-centre frusta, since off-centre lives in row 2 — the whole edit is:

```
M[3][0] += d * w          w = |column 0| = the horizontal focal term (1.1809 measured live)
```

It reads and writes nothing else. In particular it never touches column 2 or row 3's z, so the
reversed-Z/infinite-far question and the unexplained per-position clip-z constant **cannot affect
it, and cannot be corrupted by it**. This supersedes the board row's original plan of rebuilding
`V_eye · P` from the live decomposition.

⚠️ **`w` must come from the SHARED matrix.** `|column 0|` of a *per-object* matrix includes the
object's scale — a 3× scaled object reads 3.54 where `w` is 1.18 — so the per-object path, when it
is built, has to be handed the shared frame's `w` rather than measuring its own. Asserted in both
harnesses.

**NOT established:** that any of this renders correctly. The algebra is proven and the write path
is proven; only a run shows the picture.
