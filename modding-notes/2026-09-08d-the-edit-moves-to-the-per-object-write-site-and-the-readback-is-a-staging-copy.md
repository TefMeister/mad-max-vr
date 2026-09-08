# 2026-09-08d — the edit moves to the per-object write site, and the read-back had to be a staging copy

`/pd`, dev PC. **The game was not launched and nothing here has been run.** All three `[PD]` rows
are closed: compile-verified, plus 71 offline checks against the shipped code.

Deployed `d707c4773d7f`, 245,760 B, stamped. Previous build backed up as
`dxgi.dll.bak-2026-09-08-pre-perobject`.

---

## 1. ⭐⭐ The edit now goes to the per-object write site

The shared-matrix branch is empirically closed: on 2026-09-08, 116,364 writes passed the
`slot4==slot9` test, the picture measurably changed against a zero-noise control, and the frame did
not translate by one pixel even at **13.76 world units — 212× a human IPD** `[verified-live
2026-09-08, n=2 render states]`. What changed was shading.

§6b names the remaining route: `InstanceConsts` slots 0..3 **are** the object→clip 4×4 that feeds
`SV_Position` in 112 of 112 shaders. §7a's one-float algebra carries over unchanged — only the write
site moves. It has moved.

### What was built

- `InstanceConsts` (368 bytes) is now intercepted at `Map`/`Unmap`, and the same
  `apply_eye_offset()` runs on its slots 0..3.
- **It is handed the *shared* frame's `w`, never its own.** An object's scale multiplies column 0 —
  a 3× scaled object reads 3.54 where `w` is 1.18 — so a per-object `|col 0|` is wrong by exactly
  the object's scale. Section 7 of the suite has asserted this since 2026-09-04; the new code obeys
  it.
- A `NUMPAD0` path selector: **per-object → shared → both**, defaulting to per-object. The shared
  path stays reachable so the two can be A/B'd without a rebuild, and so a per-object result is not
  confounded by a shared edit still firing underneath it.

### ⚠️ The load-bearing assumption, stated plainly

Per-object buffers carry **no main-pass discriminator of their own** — §6b established that slots
4..15 are falloff data, not a transform. So pass membership is **inherited**: a latch, set from the
most recent 512-byte shared write, records whether that write looked like the main camera
(`slot4==slot9`), and per-object writes are edited only while the latch is set and a `w` from **the
same frame** is cached.

**That is a `[hypothesis]`, and it is the thing most likely to be wrong.** It assumes the game
interleaves shared and per-object fills in the order the latch implies. If it does not, the failure
is specific and recognisable: **shadows and reflections swimming against a shifted eye**, because
those passes got the edit too. That is a different symptom from "nothing moved", and telling them
apart is what the counters are for.

Not fudged anywhere: a stale `w` from an earlier frame is **refused**, not reused, because it would
be wrong by exactly the FOV change between frames — which on screen looks like a mistuned IPD rather
than a bug, the most expensive kind of wrong value.

### Scope, deliberately narrow

Only the 368-byte `InstanceConsts`. The other per-object buffer, `cbInstanceConsts`, exists in nine
sizes from 16 to 160 bytes; §6b says those also carry a clip transform at slots 0..3, but **a
16-byte buffer cannot hold a 4×4 at all**, so that cannot be true of every size and the population
has not been separated. Editing nine unverified sizes to gain draws we have no evidence we need
would make a bad result uninterpretable. If 368 alone moves the world, whether it moves *all* of it
is the next question — answered by looking, not by widening pre-emptively.

Per-object buffers are **not** routed through the fingerprint machinery. They are written once per
draw, which would exhaust `FP_MAX_WRITES` (128) and `FP_MAX_BUFFERS` (8) in a single frame and make
the census meaningless. They take an edit-only path.

---

## 2. The read-back: the board's method could not work, and that is the finding

The row asked to *"read the buffer back at the next `Map`"* to separate (a) wrong buffer, (b) the
game re-uploads after our `Unmap`, (c) wrong element.

**Reading at the next `Map` cannot answer it.** Constant buffers are mapped
`D3D11_MAP_WRITE_DISCARD`, which by specification hands back a **fresh allocation whose previous
contents are undefined**. Whatever came back would be meaningless — and meaningless in the most
dangerous way, because it would look like data and would have been written down.

What does answer it is a **staging copy**, taken after our `Unmap` has returned and the buffer is no
longer mapped: `CopyResource` into a `STAGING` buffer, `Map` it `READ`, and look. That reports what
the buffer actually holds.

| read-back says | meaning |
| --- | --- |
| **our value survived** | the bytes are in the buffer the game draws from. **(b) is excluded**, (a) is weakened, (c) survives |
| **overwritten** | something rewrote it between our `Unmap` and the copy — **(b) is the answer**, and the edit must move later in the frame |

It stalls the pipeline, so it is one-shot on `NUMPAD-DOT` / `DELETE` and takes four samples. It uses
`real_Map`/`real_Unmap`, not the hooks, so our own instrumentation cannot record a write the game
never made.

---

## 3. ⭐ The `FreeLibrary` row, with the caveat it deserves

The proxy loaded the system `dxgi.dll` by full path and never released it. If the game unloaded the
proxy, that system copy stayed resident and the next `LoadLibrary("dxgi.dll")` **by base name** would
find it — the game would then run perfectly without us, with a log that ends mid-session and reads
like a crash.

Now released, with two guards:

- **Only when `reserved == NULL`** (a genuine dynamic unload). On process termination every module
  is being torn down anyway and `FreeLibrary` is at best pointless.
- ⚠️ **Calling `FreeLibrary` from `DllMain` is against the documented loader rules** and can
  deadlock. It is accepted here only because this proxy already calls `LoadLibraryA` from
  `DLL_PROCESS_ATTACH` — the standard proxy-DLL bargain — so the *asymmetry*, not the call, was the
  anomaly. **If this ever deadlocks on unload, the fix is to stop loading in `DllMain` too, not to
  reinstate the leak.** Written into the code beside it.

---

## 4. Three defects in our own tooling, found because the tooling was used

**(a) The self-test printed its verdict before a third of its own checks.** `SELFTEST PASSED` was
printed above sections 6, 7, 7b and 8 — all added after it — so it counted only the first five
sections. A failure in the **stereo maths** would have printed `SELFTEST PASSED` and then the failing
lines. The exit code was always correct; the line a human reads was not, which is the worse half.
Verdict moved to the end and given a check count. Verified by breaking a late check on purpose:
it now prints `SELFTEST FAILED (1 failure, 71 checks)` where it previously printed PASSED
`[verified-numerically 2026-09-08]`.

**(b) The suite was not wired to the build, and when wired, a pipe swallowed its exit status.**
`bash test/build-and-run.sh | tail -1` takes the status of `tail`, so a failing suite would print
`SELFTEST FAILED` and the build would still succeed — `set -e` cannot help there. Now captured and
checked. Verified: a deliberately broken check makes `build.sh` exit 1 with *"this build is not fit
to deploy"* `[verified-numerically 2026-09-08]`.

**(c) The build was not reproducible** — two builds of identical source differed by 2 bytes (the PE
`TimeDateStamp`), so `CONVENTIONS.md`'s *rebuild and compare the hash* check silently could not work.
Fixed with `-Wl,--no-insert-timestamp`; now **0 differing bytes** `[verified-numerically 2026-09-08]`.

⚠️ **That is the THIRD project today with defect (c)** — `doom-2016-vr` and `unreal-gold-vr` were the
other two, across two different toolchains (llvm-mingw and MSVC). This is not a coincidence about
one project; it is a blind spot in the estate. **Assume "rebuild and compare the hash" is broken on
any project until someone has actually built twice and compared.**

`-Wextra` was added at the same time; the proxy is clean under it.

---

## 5. What this session did NOT establish

- **That the per-object edit moves the frame.** The algebra was already proven (sections 6–7, over
  independently constructed W, V and P); the *plumbing* is now proven (section 7b); the picture is
  not. Only a run shows it.
- Whether the main-pass latch correctly classifies per-object writes. `[hypothesis]`, and the most
  likely thing to be wrong.
- Whether our bytes survive to the draw. That is what the read-back is for, and it has not been run.
- Whether `cbInstanceConsts` also needs editing.
- Nothing here has been run. The game was not launched.

---

## 6. What to run next time the game is up

Stereo starts **OFF** and the path defaults to **per-object**.

```
NUMPAD3   dump one frame          (sanity: the hooks are alive)
NUMPAD6   stereo ON               (per-object, wiggle, sep 0.065)
          -- watch the picture --
NUMPAD8   separation x1.25, repeat to exaggerate
NUMPAD.   read our edit back out of the buffer
NUMPAD0   switch path (per-object -> shared -> both) to A/B
```

| what you see / what the log says | meaning |
| --- | --- |
| **the world visibly shifts sideways, wiggling** | ⭐⭐ the per-object path is the on-screen transform. This is the result the whole camera line has been waiting for |
| **shadows or reflections swim against the shift** | the latch is misclassifying passes — the `[hypothesis]` in §1 is wrong, and the fix is a better pass discriminator, not a different element |
| `PER-OBJECT edited=0`, `off-main-pass` high | the latch never saw a main-pass shared write; the two fills are not interleaved as assumed |
| `PER-OBJECT edited=0`, `no-shared-w` high | it did, but `w` was not cached in the same frame |
| `Map slots full` non-zero | edits were dropped before being attempted — raise `FP_MAX_PENDING` |
| **large `edited` count, nothing moves** | the same result the shared path gave. The on-screen transform is in **neither** buffer, and the next move is to find what actually feeds `SV_Position` at runtime |
| read-back says **OUR VALUE SURVIVED** | the game does not re-upload; possibility (b) is dead |
| read-back says **OVERWRITTEN** | possibility (b) is the answer; the edit must move later in the frame |

⚠️ Judge the shift **by eye against a still scene**, not by the counters — the counters only say the
edit fired. And a dump taken with stereo ON still shows the matrix the *game* wrote, by design
(`record_write()` runs before the edit), so an unchanged dump is **not** evidence the edit failed.
