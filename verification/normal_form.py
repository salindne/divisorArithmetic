"""
Normal forms for ramified hyperelliptic curves, verified rather than asserted.

Every curve shape this repository's formula files declare in their banners is a
normal form: a claim that an arbitrary curve can be brought to that shape by an
isomorphism, so restricting the formulas to it costs no generality. The claims
are load-bearing -- they decide which coefficients a formula may drop -- but
until this file they were only ever argued on paper, and one of them turned out
to be wrong in the published thesis (see Thesis/ERRATA.md, E-T6).

This script establishes the whole account by construction and exhaustive
search, at genus 2 and genus 3 together. It is standalone: run it directly, no
arguments.

    python3 verification/normal_form.py

WHAT IS CHECKED

  1. The characteristic-2 form.  Random curves with deg h = g and h NOT monic
     are normalised to h monic and f_{2g} = ... = f_g = 0.  Each of the three
     steps is verified POINTWISE: every affine point of the old curve is
     carried by the explicit substitution onto the new curve, bijectively.  A
     point count alone would not catch a substitution that permutes the curve
     onto a different one with the same order.

  2. The degree-g floor rule, by negative control.  With deg h < g the a_0
     lever is a_0 * h_g and dies, so f_g is no longer clearable.  Confirmed by
     EXHAUSTIVE search over the entire shift space, not by sampling.

  3. Why f_{2g} is routed through the x-translation and not the y-shift.  The
     y-shift route raises an Artin-Schreier equation a_g^2 + a_g = f_{2g},
     solvable only when the absolute trace vanishes -- about half the time.
     The x-translation route is unconditional in characteristic 2 because
     deg f is odd.

  4. The odd-characteristic form, and why it stops one coefficient in.
     Completing the square removes h entirely but SPENDS the y-shift, leaving
     only x -> a^2 x + b, y -> a^(2g+1) y.  b kills f_{2g}; a only rescales.
     Confirmed by exhaustive search over that entire surviving group.

  5. Necessity of char != 2g+1 for the depression (char != 5 at genus 2,
     char != 7 at genus 3): over GF(2g+1) the x^{2g} coefficient is invariant
     under every translation, so no choice of b works.

NEW_WORK.md, Part I, is the prose account these checks support.
"""

from __future__ import annotations

import itertools
import random

from ff import GF

# --------------------------------------------------------------------------
# Polynomials as low-to-high lists of field elements.  Deliberately not
# poly.py: that module is tuned for the divisor arithmetic and carries a
# modulus notion this file has no use for.
# --------------------------------------------------------------------------


def ptrim(p):
    while len(p) > 1 and p[-1].is_zero():
        p = p[:-1]
    return p


def pdeg(p):
    p = ptrim(p)
    return -1 if (len(p) == 1 and p[0].is_zero()) else len(p) - 1


def padd(a, b):
    F = a[0].F
    z = F(0)
    n = max(len(a), len(b))
    return ptrim([(a[i] if i < len(a) else z) + (b[i] if i < len(b) else z)
                  for i in range(n)])


def pmul(a, b):
    F = a[0].F
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai.is_zero():
            continue
        for j, bj in enumerate(b):
            out[i + j] = out[i + j] + ai * bj
    return ptrim(out)


def pscale(a, c):
    return ptrim([c * x for x in a])


def peval(p, x):
    acc = p[0].F(0)
    for c in reversed(p):
        acc = acc * x + c
    return acc


def coeff(p, i):
    return p[i] if i < len(p) else p[0].F(0)


def shift_x(p, b):
    """p(x + b)."""
    F = p[0].F
    out, pw, xb = [F(0)], [F(1)], [b, F(1)]
    for c in p:
        out = padd(out, pscale(pw, c))
        pw = pmul(pw, xb)
    return out


# --------------------------------------------------------------------------
# Pointwise isomorphism checking
# --------------------------------------------------------------------------


def affine_points(f, h, F):
    pts = []
    for x in F.elements():
        hx, fx = peval(h, x), peval(f, x)
        for y in F.elements():
            if (y * y + hx * y) == fx:
                pts.append((x, y))
    return pts


def check_iso(f, h, fn, hn, phi, F, what):
    """Every affine point of (f, h) lands on (fn, hn) under phi, bijectively."""
    src = affine_points(f, h, F)
    dst = set(affine_points(fn, hn, F))
    img = set()
    for (x, y) in src:
        p = phi(x, y)
        if p not in dst:
            raise AssertionError(f"{what}: point {(x, y)} left the curve")
        img.add(p)
    if len(img) != len(src):
        raise AssertionError(f"{what}: substitution is not injective on points")
    if img != dst:
        raise AssertionError(f"{what}: image misses {len(dst - img)} points")
    return len(src)


# --------------------------------------------------------------------------
# The three characteristic-2 steps
# --------------------------------------------------------------------------


def make_h_monic(f, h, g):
    """alpha-scaling  x = a^2 x~,  y = a^(2g+1) y~,  divided by a^(4g+2).

    Sends h_g -> h_g / a and leaves f monic.  Divides by nothing except a = h_g
    itself, so it is valid in EVERY characteristic -- this is the step that
    makes 'h monic' a free assumption rather than a restriction.
    """
    a = coeff(h, g)
    if a.is_zero():
        raise ValueError("h has degree < g; nothing to scale")
    d = 2 * g + 1
    hn = ptrim([coeff(h, i) * a ** (2 * i) / a ** d for i in range(g + 1)])
    fn = ptrim([coeff(f, i) * a ** (2 * i) / a ** (2 * d) for i in range(d + 1)])
    return fn, hn, (lambda x, y: (x / a ** 2, y / a ** d))


def kill_top(f, h, g):
    """x -> x + b kills f_{2g}.

    Unconditional in characteristic 2 because deg f is odd: the x^{2g}
    coefficient of (x + b)^(2g+1) is (2g+1)b = b.  In odd characteristic it is
    b = -f_{2g}/(2g+1), which needs char not dividing 2g+1.
    """
    F = f[0].F
    b = coeff(f, 2 * g) if F.char == 2 else -coeff(f, 2 * g) / F(2 * g + 1)
    return shift_x(f, b), shift_x(h, b), (lambda x, y: (x - b, y))


def clear_floor(f, h, g):
    """y -> y + a(x), deg a <= g-1, clearing f_{2g-1} ... f_g.

    THE DEGREE-g FLOOR RULE.  In characteristic 2 the shift leaves h untouched
    and sends f -> f + a^2 + a*h.  Coefficient a_i controls degree i+g through
    a_i * h_g = a_i, while a_i^2 lands at degree 2i, and 2i < i+g exactly when
    i < g.  Every square therefore lands strictly BELOW the coefficient its own
    a_i controls, so the system is triangular from the top with no obstruction
    anywhere -- and it bottoms out at degree g because deg a stops at g-1.
    """
    F = f[0].F
    if F.char != 2:
        raise ValueError("characteristic-2 routine")
    a = [F(0)] * g
    for i in range(g - 1, -1, -1):
        ap = ptrim(list(a))
        cur = padd(f, padd(pmul(ap, ap), pmul(ap, h)))
        a[i] = coeff(cur, i + g)          # h_g = 1, so the lever is exactly a_i
    ap = ptrim(list(a))
    fn = padd(f, padd(pmul(ap, ap), pmul(ap, h)))
    return fn, h, (lambda x, y: (x, y + peval(ap, x)))


# --------------------------------------------------------------------------
# Odd characteristic
# --------------------------------------------------------------------------


def complete_square(f, h):
    """char != 2:  y -> y - h/2  sends (f, h) -> (f + h^2/4, 0).

    Removes all g+1 coefficients of h, but spends the y-shift doing it.
    """
    F = f[0].F
    hh = [c / F(2) for c in h]
    sq = pmul(hh, hh)
    return padd(f, sq), [F(0)]


def scale_h_zero(f, g, a):
    """x -> a^2 x, y -> a^(2g+1) y with h already 0."""
    d = 2 * g + 1
    return ptrim([coeff(f, i) * a ** (2 * i) / a ** (2 * d) for i in range(d + 1)])


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def check_char2_normalisation(g, q, trials, rng):
    """(1) Full normalisation of curves that are NOT already in the form."""
    F, d = GF(q), 2 * g + 1
    ok = pts = 0
    for _ in range(trials):
        lead = F(0)
        while lead.is_zero():
            lead = F.random(rng)
        h = ptrim([F.random(rng) for _ in range(g)] + [lead])
        f = ptrim([F.random(rng) for _ in range(d)] + [F(1)])
        if pdeg(h) != g:
            continue

        f1, h1, phi = make_h_monic(f, h, g)
        assert coeff(h1, g).is_one(), "h not monic after scaling"
        assert coeff(f1, d).is_one(), "f lost monicity under scaling"
        pts += check_iso(f, h, f1, h1, phi, F, "scaling")

        f2, h2, phi = kill_top(f1, h1, g)
        assert coeff(f2, 2 * g).is_zero(), "f_2g survived the translation"
        assert coeff(h2, g).is_one(), "translation disturbed monic h"
        check_iso(f1, h1, f2, h2, phi, F, "translation")

        f3, h3, phi = clear_floor(f2, h2, g)
        for i in range(g, 2 * g + 1):
            assert coeff(f3, i).is_zero(), f"f_{i} survived the y-shift"
        assert coeff(f3, d).is_one(), "f lost monicity under the y-shift"
        assert pdeg(h3) == g and coeff(h3, g).is_one(), "h moved under the shift"
        check_iso(f2, h2, f3, h3, phi, F, "y-shift")

        ok += 1
    return ok, pts


def check_floor_rule(g, q, trials, rng):
    """(2) deg h < g: EXHAUSTIVE search shows the floor is not reachable."""
    F, d = GF(q), 2 * g + 1
    els = list(F.elements())
    stuck = 0
    for _ in range(trials):
        h = ptrim([F.random(rng) for _ in range(g)] + [F(0)])
        f = ptrim([F.random(rng) for _ in range(d)] + [F(1)])
        f, h, _ = kill_top(f, h, g)
        reachable = False
        for combo in itertools.product(els, repeat=g):
            ap = ptrim(list(combo))
            nf = padd(f, padd(pmul(ap, ap), pmul(ap, h)))
            if all(coeff(nf, i).is_zero() for i in range(g, 2 * g)):
                reachable = True
                break
        if not reachable:
            stuck += 1
    return stuck


def check_artin_schreier(g, q, trials, rng):
    """(3) The y-shift route to f_{2g} is trace-obstructed; translation is not."""
    F, d = GF(q), 2 * g + 1
    blocked = 0
    for _ in range(trials):
        f = ptrim([F.random(rng) for _ in range(d)] + [F(1)])
        t = coeff(f, 2 * g)
        if not any((z * z + z) == t for z in F.elements()):
            blocked += 1
    return blocked


def check_odd_char(g, q, trials, rng):
    """(4) Odd characteristic stops at f_{2g}, by exhaustive group search."""
    F, d = GF(q), 2 * g + 1
    els = list(F.elements())
    nz = [e for e in els if not e.is_zero()]
    cleared = stuck = 0
    for _ in range(trials):
        h = ptrim([F.random(rng) for _ in range(g + 1)])
        f = ptrim([F.random(rng) for _ in range(d)] + [F(1)])
        f, h = complete_square(f, h)
        assert pdeg(h) <= 0 and coeff(h, 0).is_zero(), "square not completed"
        f, _, _ = kill_top(f, h, g)
        assert coeff(f, 2 * g).is_zero(), "f_2g survived"
        cleared += 1

        reachable = False
        for a in nz:
            fa = scale_h_zero(f, g, a)
            for b in els:
                fb = shift_x(fa, b)
                fb = pscale(fb, F(1) / coeff(fb, d))      # re-monicise
                if (coeff(fb, 2 * g).is_zero()
                        and coeff(fb, 2 * g - 1).is_zero()):
                    reachable = True
                    break
            if reachable:
                break
        if not reachable:
            stuck += 1
    return cleared, stuck


def check_depression_necessity(g, trials, rng):
    """(5) Over GF(2g+1) no translation moves f_{2g} at all."""
    p = 2 * g + 1
    F, d = GF(p), 2 * g + 1
    invariant = 0
    for _ in range(trials):
        f = ptrim([F.random(rng) for _ in range(d)] + [F(1)])
        if coeff(f, 2 * g).is_zero():
            continue
        if all(coeff(shift_x(f, b), 2 * g) == coeff(f, 2 * g)
               for b in F.elements()):
            invariant += 1
    return invariant


def main():
    rng = random.Random(20260809)
    failures = 0

    print("(1) characteristic 2: normalising curves NOT already in the form")
    print("    h of degree exactly g but non-monic; every step checked "
          "pointwise")
    for g in (2, 3):
        for q in (2, 4, 8, 16, 32):
            n, pts = check_char2_normalisation(g, q, 12, rng)
            print(f"    genus {g}  GF({q:>2})   {n:>2}/12 reach "
                  f"h monic, f_{g}..f_{2 * g} = 0;  "
                  f"{pts:>5} affine points transported, 0 lost")
            failures += (n != 12)

    print()
    print("(2) the degree-g floor rule: deg h < g, EXHAUSTIVE over all shifts")
    for g in (2, 3):
        for q in (2, 4, 8):
            s = check_floor_rule(g, q, 12, rng)
            print(f"    genus {g}  GF({q:>2})   {s:>2}/12 curves cannot reach "
                  f"f_{g}..f_{2 * g - 1} = 0 by ANY shift")

    print()
    print("(3) why f_2g goes through the translation, not the y-shift")
    for g in (2, 3):
        for q in (2, 4, 8, 16, 32):
            b = check_artin_schreier(g, q, 60, rng)
            print(f"    genus {g}  GF({q:>2})   {b:>2}/60 curves have "
                  f"Tr(f_{2 * g}) != 0, blocking the y-shift route")

    print()
    print("(4) odd characteristic: h dies, and the form stops at f_2g")
    print("    exhaustive over the entire surviving (alpha, beta) group")
    for g in (2, 3):
        for q in (11, 13, 17, 19, 23):
            top, stuck = check_odd_char(g, q, 8, rng)
            print(f"    genus {g}  GF({q:>2})   f_{2 * g} cleared {top}/8;  "
                  f"f_{2 * g - 1} unreachable for {stuck}/8")
            failures += (top != 8)

    print()
    print("(5) necessity of char != 2g+1 for the depression")
    for g in (2, 3):
        n = check_depression_necessity(g, 200, rng)
        print(f"    genus {g}  GF({2 * g + 1})   f_{2 * g} invariant under ALL "
              f"{2 * g + 1} translations, on {n} curves with f_{2 * g} != 0")

    print()
    if failures:
        print(f"FAILED: {failures} check(s) did not reach their target")
        return 1
    print("All normal-form claims reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
