"""Is a per-eye offset expressible as ONE shared post-multiply on any
object-to-clip matrix?

Mad Max's per-object path gives each draw a full object->clip matrix M at
InstanceConsts slots 0..3 (row-vector storage: clip = pos * M). There is no
separable world matrix (census 2026-09-04), so a VR patch cannot rebuild
W * V_eye * P per draw. The question this answers: can we instead post-multiply
every per-object M by a single correction K_eye that depends only on the SHARED
projection P and the eye offset?

Derivation (row vectors, clip = p * W * V * P):
    M       = W * V * P
    M_eye   = W * V_eye * P
    V_eye   = V * T_view(d)          # a shift along the view-space X axis
  =>M_eye   = W * V * T_view(d) * P
            = (W * V * P) * P^-1 * T_view(d) * P
            = M * K_eye ,  K_eye = P^-1 * T_view(d) * P

K_eye is the same matrix for every draw in the frame. If this holds numerically
for arbitrary W and V, the per-object path costs one 4x4 multiply per draw and
needs no knowledge of the object at all.

Run: python k_eye.py      (exit 0 = every check passed)
"""
import math
import random

random.seed(20260904)


def mat_mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mat_id():
    return [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]


def translate(x, y, z):
    m = mat_id()
    m[3][0], m[3][1], m[3][2] = x, y, z          # row-vector: translation in row 3
    return m


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    m = mat_id(); m[1][1], m[1][2], m[2][1], m[2][2] = c, s, -s, c
    return m


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    m = mat_id(); m[0][0], m[0][2], m[2][0], m[2][2] = c, -s, s, c
    return m


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    m = mat_id(); m[0][0], m[0][1], m[1][0], m[1][1] = c, s, -s, c
    return m


def scale(sx, sy, sz):
    m = mat_id(); m[0][0], m[1][1], m[2][2] = sx, sy, sz
    return m


def inverse(m):
    """Gauss-Jordan; these matrices are small and well conditioned."""
    n = 4
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-12:
            raise ZeroDivisionError("singular")
        a[col], a[piv] = a[piv], a[col]
        d = a[col][col]
        a[col] = [v / d for v in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0.0:
                f = a[r][col]
                a[r] = [v - f * w for v, w in zip(a[r], a[col])]
    return [row[n:] for row in a]


def proj_standard(hfov_deg, aspect, znear, zfar):
    """Ordinary D3D perspective, row-vector, z in [0,1]."""
    w = 1.0 / math.tan(math.radians(hfov_deg) / 2.0)
    h = w * aspect
    q = zfar / (zfar - znear)
    return [[w, 0, 0, 0],
            [0, h, 0, 0],
            [0, 0, q, 1],
            [0, 0, -q * znear, 0]]


def proj_reversed_z_infinite(hfov_deg, aspect, znear):
    """Reversed-Z with an infinite far plane - the shape dossier section 6
    hypothesises for this game (column 2 near zero, a small constant in row 3)."""
    w = 1.0 / math.tan(math.radians(hfov_deg) / 2.0)
    h = w * aspect
    return [[w, 0, 0, 0],
            [0, h, 0, 0],
            [0, 0, 0, 1],
            [0, 0, znear, 0]]


def close(a, b, tol=1e-7):
    return all(abs(a[i][j] - b[i][j]) <= tol * max(1.0, abs(b[i][j]))
               for i in range(4) for j in range(4))


PASS = FAIL = 0


def check(name, got, want, tol=1e-7):
    global PASS, FAIL
    ok = close(got, want, tol)
    print("%s %s" % ("PASS" if ok else "FAIL", name))
    if not ok:
        for i in range(4):
            print("     got %s" % ["%9.5f" % v for v in got[i]])
            print("    want %s" % ["%9.5f" % v for v in want[i]])
    if ok:
        PASS += 1
    else:
        FAIL += 1


def random_world():
    return mat_mul(mat_mul(scale(random.uniform(0.2, 5), random.uniform(0.2, 5),
                                 random.uniform(0.2, 5)),
                           mat_mul(rot_x(random.uniform(-3, 3)),
                                   mat_mul(rot_y(random.uniform(-3, 3)),
                                           rot_z(random.uniform(-3, 3))))),
                   translate(random.uniform(-5000, 5000),
                             random.uniform(-5000, 5000),
                             random.uniform(-5000, 5000)))


def random_view():
    return mat_mul(translate(random.uniform(-5000, 5000), random.uniform(-5000, 5000),
                             random.uniform(-5000, 5000)),
                   mat_mul(rot_y(random.uniform(-3, 3)), rot_x(random.uniform(-1, 1))))


def _run_tests():
    global PASS, FAIL
    for label, P in (("ordinary projection", proj_standard(80.5, 16 / 9.0, 0.1, 5000.0)),
                     ("reversed-Z infinite far", proj_reversed_z_infinite(80.5, 16 / 9.0, 0.0889))):
        Pinv = inverse(P)
        for trial in range(3):
            W, V = random_world(), random_view()
            d = random.uniform(-0.05, 0.05) * 100.0          # eye offset, world units
            T = translate(d, 0, 0)                            # along the VIEW x axis
            K = mat_mul(mat_mul(Pinv, T), P)
            M = mat_mul(mat_mul(W, V), P)
            M_true = mat_mul(mat_mul(W, mat_mul(V, T)), P)
            check("%s, trial %d: M * K == W * V_eye * P" % (label, trial + 1),
                  mat_mul(M, K), M_true)

        # K must not depend on the object: the SAME K works for a second object.
        V = random_view()
        d = 3.25
        K = mat_mul(mat_mul(Pinv, translate(d, 0, 0)), P)
        for trial in range(2):
            W = random_world()
            M = mat_mul(mat_mul(W, V), P)
            M_true = mat_mul(mat_mul(W, mat_mul(V, translate(d, 0, 0))), P)
            check("%s: one K, different object %d" % (label, trial + 1),
                  mat_mul(M, K), M_true)

    # K's actual shape, for the record - this is what the proxy would hardcode.
    P = proj_reversed_z_infinite(80.5, 16 / 9.0, 0.0889)
    K = mat_mul(mat_mul(inverse(P), translate(3.25, 0, 0)), P)
    print("\nK_eye for the reversed-Z shape, d = 3.25 view-space units:")
    for row in K:
        print("   [%12.6f %12.6f %12.6f %12.6f]" % tuple(row))

    print("\n%d passed, %d failed" % (PASS, FAIL))
    raise SystemExit(1 if FAIL else 0)


if __name__ == "__main__":
    _run_tests()
