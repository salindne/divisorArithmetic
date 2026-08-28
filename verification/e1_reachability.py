"""
E1's guard region is unreachable with two distinct divisors, proved and checked.

`ERRATA.md` E1 records a guard that is too narrow: in the `IsZero(m3)` branch of
`Deg2ADD`, all three genus-2 ramified addition files test
`IsZero(dw20) and IsZero(dw21)` and return the identity, then fall through to
`b2 := dw21^-1`.  On `dw21 = 0` with `dw20 != 0` that divides by zero.

The entry has always said the same thing about reachability: every observed
firing has `D1 = D2`, which the dispatchers have routed to `DBL` since PR5, but
"whether any `D1 != D2` input can reach the guard is not proven impossible, only
never observed -- 13,008 differential operations found none".

It is provable, and this script checks the proof.

THE ARGUMENT, in two steps
--------------------------

All three files share the prologue that computes the resultant by a 2x2 system:

    m3 := up1 - u1;   m4 := u0 - up0;
    m1 := m4 + up1*m3;   m2 := -up0*m3;
    d  := m1*m4 - m2*m3;

Step 1.  The branch needs `d = 0` AND `m3 = 0`.  With `m3 = 0` the prologue
collapses: `m1 = m4`, `m2 = 0`, so `d = m4*m4 - 0*0 = m4^2`.  Then `d = 0`
forces `m4 = 0`, and `m3 = m4 = 0` is exactly `u = up`.

Step 2.  Both divisors are valid, so `u | f - v(v+h)` and `up | f - vp(vp+h)`.
With `u = up`, subtracting gives

    u | (f - v(v+h)) - (f - vp(vp+h)) = (vp - v)(vp + v + h).

The defect case is `dw2 = (vp + v + h) mod u` being a NONZERO CONSTANT -- that
is precisely `dw21 = 0, dw20 != 0`.  A nonzero constant is a unit modulo `u`, so
`u | (vp - v)`.  Both `v` and `vp` are reduced, of degree below `deg u = 2`, so
`vp - v = 0` and `vp = v`.

`u = up` and `v = vp` is `D1 = D2`.  Which the dispatchers intercept.

So the region is dead code on its entry points, and the same argument covers the
frozen timings copy's *wider* return condition (`ERRATA.md` E7), which returns
the identity where the canonical files raise.

WHAT THIS SCRIPT CHECKS

Both steps, by exhaustive enumeration rather than by trusting the algebra:

  Step 1 over all `(u1, u0, up1, up0)` in the field: every quadruple with
  `m3 = 0` and `d = 0` must have `u = up`, and the count of such quadruples must
  be exactly `q^2` (one per monic `u`).

  Step 2 over all squarefree monic quintics: build every valid degree-2 divisor,
  group by `u` (Step 1 having forced `up = u`), and check every ordered pair
  with `D1 != D2`.  None may reach `dw21 = 0, dw20 != 0`.

Scoped to `nch2` (`h = 0`, odd characteristic), where `dw2 = vp + v` needs no
reduction.  The `arb` and `ch2` files compute `dw2 = (vp + v + h) mod u`
including the `h` terms; the argument is identical, since it turns only on `dw2`
being a unit, but the enumeration here does not cover them.

Standalone, no arguments.  About 30 seconds over GF(3), GF(5), GF(7) -- 17,068
curves and 1,242,140 pairs; pass `--full` to add GF(11), which takes about ten
minutes and brings the totals to 163,478 curves and 32,237,830 pairs.  Not in CI: like
`normal_form.py`, it verifies mathematics rather than the formulas, and CI gates
on the frozen corpus.
"""
import argparse
import itertools
import sys


def _polymod(a, m, p):
    """`a` reduced modulo the monic quadratic `m = [m0, m1, 1]`, low-to-high."""
    r = list(a)
    while len(r) > 2:
        c = r.pop()
        d = len(r) - 2
        r[d] = (r[d] - c * m[0]) % p
        r[d + 1] = (r[d + 1] - c * m[1]) % p
    while len(r) < 2:
        r.append(0)
    return r


def _polymulmod(a, b, m, p):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            r[i + j] = (r[i + j] + x * y) % p
    return _polymod(r, m, p)


def _squarefree(f, p):
    """gcd(f, f') == 1 over GF(p), `f` low-to-high."""
    fp = [(i * f[i]) % p for i in range(1, len(f))]
    a, b = list(f), list(fp)
    while any(b):
        while b and b[-1] == 0:
            b.pop()
        if not b:
            break
        inv = pow(b[-1], p - 2, p)
        while len(a) >= len(b) and any(a):
            while a and a[-1] == 0:
                a.pop()
            if not a or len(a) < len(b):
                break
            c = (a[-1] * inv) % p
            sh = len(a) - len(b)
            for i in range(len(b)):
                a[sh + i] = (a[sh + i] - c * b[i]) % p
        a, b = b, a
    while a and a[-1] == 0:
        a.pop()
    return len(a) == 1


def step1(p):
    """Every (u, up) with m3 = 0 and d = 0 has u = up.  Returns (hits, bad)."""
    hits = bad = 0
    for u1, u0, up1, up0 in itertools.product(range(p), repeat=4):
        m3 = (up1 - u1) % p
        m4 = (u0 - up0) % p
        m1 = (m4 + up1 * m3) % p
        m2 = (-up0 * m3) % p
        d = (m1 * m4 - m2 * m3) % p
        if d == 0 and m3 == 0:
            hits += 1
            if (u1, u0) != (up1, up0):
                bad += 1
    return hits, bad


def step2(p):
    """No D1 != D2 sharing u reaches dw21 = 0 with dw20 != 0."""
    curves = pairs = hits = 0
    for coeffs in itertools.product(range(p), repeat=5):
        f = list(coeffs) + [1]
        if not _squarefree(f, p):
            continue
        curves += 1
        byu = {}
        for u1, u0 in itertools.product(range(p), repeat=2):
            m = [u0, u1, 1]
            fm = _polymod(f, m, p)
            for v1, v0 in itertools.product(range(p), repeat=2):
                vv = _polymulmod([v0, v1], [v0, v1], m, p)
                if fm == vv:
                    byu.setdefault((u1, u0), []).append((v1, v0))
        for vs in byu.values():
            for (v1, v0), (vp1, vp0) in itertools.permutations(vs, 2):
                pairs += 1
                if (vp1 + v1) % p == 0 and (vp0 + v0) % p != 0:
                    hits += 1
    return curves, pairs, hits


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--full", action="store_true",
                    help="add GF(11); roughly ten minutes instead of one")
    args = ap.parse_args(argv)
    fields = [3, 5, 7] + ([11] if args.full else [])

    print("Step 1: m3 = 0 and d = 0 force u = up")
    ok = True
    for p in fields:
        hits, bad = step1(p)
        flag = "ok" if (bad == 0 and hits == p * p) else "FAIL"
        ok &= (bad == 0 and hits == p * p)
        print("  GF(%-2d)  %5d quadruples in the branch (expected %d), %d with u != up  %s"
              % (p, hits, p * p, bad, flag))

    print("\nStep 2: no D1 != D2 sharing u reaches dw21 = 0, dw20 != 0")
    tc = tp = th = 0
    for p in fields:
        curves, pairs, hits = step2(p)
        tc += curves
        tp += pairs
        th += hits
        ok &= (hits == 0)
        print("  GF(%-2d)  %6d squarefree curves, %9d pairs, %d reaching the defect  %s"
              % (p, curves, pairs, hits, "ok" if hits == 0 else "FAIL"))

    print("\n  %d curves, %d pairs with D1 != D2 entering the m3 = 0, d = 0 branch, "
          "%d reaching dw21 = 0 with dw20 != 0" % (tc, tp, th))
    if ok:
        print("  PASS: E1's guard region is unreachable with two distinct divisors.")
        return 0
    print("  FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
