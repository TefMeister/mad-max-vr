"""The per-eye offset for Mad Max is ONE ELEMENT of the matrix, on both paths.

Follows from k_eye.py. Row vectors throughout (clip = pos * M), which is how
this game stores its matrices (census 2026-09-03c/2026-09-04).

    M      = W * V * P                  (per-object: W is the object's world
                                         matrix; shared path: W = identity)
    V_eye  = V * T,  T = translate(d,0,0) in VIEW space
    M_eye  = W * V * T * P = M + W * (V*T - V) * P

(V*T - V) has exactly one non-zero entry, [3][0] = d. For any AFFINE W (fourth
column [0,0,0,1]^T - true of every object transform) the product W*(V*T-V) also
has exactly one non-zero entry, [3][0] = d. Post-multiplying by P turns that
into "row 3 += d * (row 0 of P)". For any projection whose row 0 is [w,0,0,0] -
true of symmetric AND off-centre frusta, since off-centre lives in row 2 - that
is a single scalar:

    M_eye = M with element [3][0] += d * w        w = |column 0| = the
                                                  horizontal focal term

So the entire stereo edit is one float per matrix. It needs no decomposition of
the view, no knowledge of the near/far convention, and no assumption about the
reversed-Z shape or the unexplained constant in row 3 - none of those terms are
touched or even read.

Run: python one_element.py      (exit 0 = every check passed)
"""
import math
import random

from k_eye import (mat_mul, mat_id, translate, rot_x, rot_y, rot_z, scale,
                   proj_standard, proj_reversed_z_infinite, random_world,
                   random_view)

random.seed(4092026)

PASS = FAIL = 0


def check(name, got, want, tol=1e-6):
    global PASS, FAIL
    ok = all(abs(got[i][j] - want[i][j]) <= tol * max(1.0, abs(want[i][j]))
             for i in range(4) for j in range(4))
    print("%s %s" % ("PASS" if ok else "FAIL", name))
    if not ok:
        for i in range(4):
            print("     got %s" % ["%11.5f" % v for v in got[i]])
            print("    want %s" % ["%11.5f" % v for v in want[i]])
    if ok:
        PASS += 1
    else:
        FAIL += 1


def one_element_edit(M, d, w):
    """The whole proposed patch."""
    out = [row[:] for row in M]
    out[3][0] += d * w
    return out


def focal_from_matrix(M):
    """|column 0| of the matrix, which is how the live probe measures w
    (1.1809 -> hfov 80.5 deg, measured 2026-09-04). For a per-object matrix
    this is NOT w alone - it is w scaled by the object's transform - so the
    shared path is where w must be read."""
    return math.sqrt(M[0][0] ** 2 + M[1][0] ** 2 + M[2][0] ** 2)


PROJS = (("ordinary", proj_standard(80.5, 16 / 9.0, 0.1, 5000.0)),
         ("reversed-Z infinite far", proj_reversed_z_infinite(80.5, 16 / 9.0, 0.0889)),
         ("off-centre reversed-Z", None))

# an off-centre (asymmetric) frustum - what a real HMD eye actually needs
P_off = proj_reversed_z_infinite(80.5, 16 / 9.0, 0.0889)
P_off[2][0] = 0.137          # horizontal centre shift lives in row 2, not row 0
P_off[2][1] = -0.042
PROJS = (PROJS[0], PROJS[1], ("off-centre reversed-Z", P_off))

for label, P in PROJS:
    w = P[0][0]
    # 1. the SHARED path (W = identity)
    for trial in range(3):
        V = random_view()
        d = random.uniform(-8.0, 8.0)
        M = mat_mul(V, P)
        M_true = mat_mul(mat_mul(V, translate(d, 0, 0)), P)
        check("%s, shared path, trial %d" % (label, trial + 1),
              one_element_edit(M, d, w), M_true)

    # 2. the PER-OBJECT path, arbitrary world matrix (rotation, scale, huge
    #    translation) - the same single-element edit must still be exact
    for trial in range(4):
        W, V = random_world(), random_view()
        d = random.uniform(-8.0, 8.0)
        M = mat_mul(mat_mul(W, V), P)
        M_true = mat_mul(mat_mul(W, mat_mul(V, translate(d, 0, 0))), P)
        check("%s, per-object path, trial %d" % (label, trial + 1),
              one_element_edit(M, d, w), M_true)

    # 3. the same d applied to many objects in one frame - one w, one d
    V = random_view()
    d = 3.25
    for trial in range(3):
        W = random_world()
        M = mat_mul(mat_mul(W, V), P)
        M_true = mat_mul(mat_mul(W, mat_mul(V, translate(d, 0, 0))), P)
        check("%s, shared d across objects, %d" % (label, trial + 1),
              one_element_edit(M, d, w), M_true)

# 4. w really is recoverable as |column 0| of the SHARED matrix, and really is
#    NOT recoverable that way from a per-object one (which is why the proxy must
#    read it from GlobalConstants, not from InstanceConsts).
P = proj_reversed_z_infinite(80.5, 16 / 9.0, 0.0889)
V = random_view()
shared = mat_mul(V, P)
got_w = focal_from_matrix(shared)
print("\n%s |col 0| of the shared matrix = %.6f, P[0][0] = %.6f"
      % ("PASS" if abs(got_w - P[0][0]) < 1e-6 else "FAIL", got_w, P[0][0]))
PASS += 1 if abs(got_w - P[0][0]) < 1e-6 else 0
FAIL += 0 if abs(got_w - P[0][0]) < 1e-6 else 1

scaled = mat_mul(mat_mul(scale(3.0, 3.0, 3.0), V), P)
differs = abs(focal_from_matrix(scaled) - P[0][0]) > 1e-3
print("%s |col 0| of a SCALED per-object matrix = %.6f (differs from w, as it must)"
      % ("PASS" if differs else "FAIL", focal_from_matrix(scaled)))
PASS += 1 if differs else 0
FAIL += 0 if differs else 1

# 5. the measured live value: hfov 80.5 deg <-> |col 0| 1.1809
w_meas = 1.1809
hfov = 2.0 * math.degrees(math.atan(1.0 / w_meas))
ok = abs(hfov - 80.5) < 0.05
print("%s measured |col 0| 1.1809 -> hfov %.3f deg (recorded 80.5)"
      % ("PASS" if ok else "FAIL", hfov))
PASS += 1 if ok else 0
FAIL += 0 if ok else 1

print("\n%d passed, %d failed" % (PASS, FAIL))
raise SystemExit(1 if FAIL else 0)
