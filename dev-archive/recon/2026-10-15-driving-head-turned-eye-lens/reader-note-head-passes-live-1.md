# 2026-10-15 /lm reader: the first live run of `head_passes` (build `b738e5972428`), read statically

Supersedes: nothing. This adds to `2026-10-15-lm-reader-head-passes.md`.

The run: one launch, 3D on, simulator yaw 25, standing at the start spot. Counters at the last line: fog 1903, decal
rays 1903, cloud shadows 0, SSAO 0, sky 0, and the 768-byte sun origin also 1903. All of them rise by 300 per
300-frame line, which is one a frame `[measured 2026-10-15, n=1 run]`.

## 1. Fog, decal rays and the sun origin are three different buffers, not one buffer counted three times

- **The sun-origin edit has the 768-byte PS b1 to itself.** `unmap_sun` claims every 768-byte Map, and the
  head-pass candidate widths stop at 512, so the head passes never see that buffer `[inferred-static]`.
- **The fog edit's first log line names a 384-byte buffer.** Its rows 12-15 start `[-1.69 ... 0.838 ...]`, which is
  the uv-scaled ray row: twice the sun ray's `c1` `[measured, n=1 log line]`.
- **The decal-ray edit's first log line names a 96-byte buffer.** Its rows 0 and 1 hold the same numbers as the
  sun-ray buffer's `c1` and `c2`, so it is a different buffer in the decal layout. Two facts point to an `ssdecal`
  being drawn once a frame:
  - `ssdecal` is the only vertex shader in the bundle with that layout (rows 0, 1, 3, scale in row 4), checked over
    all 335 VS.
  - Its declared 80 bytes arrive as 96 at run time.
  `[inferred-static 2026-10-15]`
- **The point, spot and area light VS use the sun layout (rows 1, 2, 4, scale in row 0) in cb2. So does the
  `depthoffield` VS, in cb1.** `ray_try` already turns those, and it claims a buffer once it edits it. That means no
  buffer is edited by two paths in one Map/Unmap, because each pending Map goes down exactly one path
  `[inferred-static]`.
- **The equal counts are the one-a-frame cadence.** All three passes draw once a frame, and all three start counting
  when the K first exists. The double application asked about does not happen.

## 2. Why cloud shadows, SSAO and the sky read 0: not settled; the next build says which

- **The counter that should have answered was blind.** In `b738e5972428`, a candidate filled before this frame's K
  existed returned without being counted. So "before this frame's camera = 0" proves nothing. Fixed in build
  `fb4917c774f5`, staging `953d1fe`. The `HEAD PASSES` line now gives:
  - candidates with a K, broken down by width (64 / 80 / 96 / 128 / 256+);
  - candidates filled before this frame's K;
  - candidates with a K but a stale shared camera.
  It also prints up to three near-miss lines per kind, each with the number that refused it.
- **Run-time widths fit a bucketed allocator** `[hypothesis]`. The seen widths are 16, 32, 64, 96, 128, 192, 256,
  384, 512 and 768, and every known declared size rounds up into that list: 80 to 96, 240 to 256, 352 to 384. On that
  reading:
  - SSAO (declared 128) arrives at 128;
  - `cloudshadow` (96) at 96;
  - `skybox` (64) at 64;
  - `skygradientshader` (80) at 96;
  - `foggradientshader` (96) at 96.
  All of these are tried. The width is therefore probably not the cause.
- **The G-buffer normals are world-space** `[inferred-static]`. The sun pass takes `dot(normal, -GlobalConstants[3])`
  (the sun direction, which is world-space and is also used by fog) with no transform. So SSAO's rows 4-6 should be a
  world-to-camera rotation, as the edit assumes.
- **Candidate reasons, separated by the next log:**

  | Kind | Possible reasons | What separates them |
  | --- | --- | --- |
  | SSAO | the SSAO buffer is filled before this frame's K; or its rows 4-6 are not this frame's camera axes | an SSAO near-miss line; the filled-before-K count |
  | Sky | its matrices' column 2 is not empty, so it is an ordinary camera and the per-object path already turns it with the full K | no sky near-miss line while 64/96 candidates arrive (then the sky was never broken); a near-miss line gives the lens ratios |
  | Cloud shadows | `cloudshadow` does not draw here (it is not in the pass census table, so nothing shows it), and the sun pass's own cloud-shadow sampling, already turned by the sun-ray edit, does the ground; or it is filled before the K | the cloud near-miss line or its absence |

## 3. Not fixed: the decal box

The `ssdecal` box (VS b1 InstanceConsts, 144 bytes) has only about 176 fills in a whole run. It needs a draw-time
edit:

1. Keep a copy of each 144-byte fill at Unmap.
2. Recognise the seven `ssdecal*` pixel shaders by checksum, as the pass census does.
3. Before each such draw, write `rows 0-3 x K` from the kept copy with a discard Map.
4. Write the original back once the K is gone.

Until then, on a turned head a decal shows only inside the screen footprint where the unturned camera would have
drawn it `[inferred-static]`.
