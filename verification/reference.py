"""reference.py -- an INDEPENDENT reference for divisor class arithmetic.

The gold standard the explicit formulas are differentially tested against. Two
curve models, both written straight from composition-plus-reduction:

  ramified (imaginary)   y^2 + h y = f,  f monic of degree 2g+1, deg h <= g,
                         one point at infinity. Divisor class is a Mumford pair
                         (u, v).

  split (real)           deg f = 2g+2, two points at infinity. Divisor class is
                         (u, v, w, n): Mumford u and v, the redundant polynomial
                         w = (f - v(v+h))/u, and a balancing weight n counting
                         the infinite places.

It shares nothing with the explicit formulas: no continued-fraction step, no
NUCOMP, no case analysis on degrees, no reuse of any intermediate they name.
That independence is why it can be trusted as an oracle, so keep it.

The ramified half derives from the audited harness (3,240,293 exhaustively
enumerated pairs, zero wrong results).  The split half is ported from
generic/arbitrary/reduced_basis_arithmetic.mag, this repository's own
generic-genus Magma reference, itself independent of the explicit formulas.
"""

from __future__ import annotations

from poly import Poly

__all__ = [
    "identity", "negate", "eq", "is_valid_divisor", "check_divisor",
    "compose", "reduce_divisor", "add", "double", "scalar_mul",
    "compute_vp", "reduced_basis", "adapted_basis",
    "split_identity", "split_add", "split_double", "split_adjust",
    "split_check_divisor",
]


# ===========================================================================
# ramified (imaginary) model:  divisor class is (u, v)
# ===========================================================================
#
# Composition
#     d1 = gcd(u1, u2)                = e1*u1 + e2*u2
#     d  = gcd(d1, v1 + v2 + h)       = c1*d1 + c2*(v1 + v2 + h)
#     u  = u1*u2 / d^2
#     v  = (c1*e1*u1*v2 + c1*e2*u2*v1 + c2*(v1*v2 + f)) / d   mod u
#
# Reduction, while deg u > g
#     u <- monic((f - v(v+h)) / u)
#     v <- (-h - v) mod u

def identity(curve):
    """The zero divisor class [1, 0]."""
    return (Poly.one(curve.F), Poly.zero(curve.F))


def negate(curve, D):
    """-[u, v] = [u, (-h - v) mod u]."""
    u, v = D
    return (u, (-curve.h - v).mod(u))


def eq(D1, D2):
    return D1[0] == D2[0] and D1[1] == D2[1]


def is_valid_divisor(curve, D, genus=None):
    return check_divisor(curve, D, genus) is None


def check_divisor(curve, D, genus=None):
    """None if D is a valid reduced divisor on `curve`, else a reason string.

    `genus` defaults to the curve's own, not to a module constant: a hardcoded
    GENUS = 3 silently under-reduced at genus 2.  See add().
    """
    if genus is None:
        genus = curve.genus
    u, v = D
    if u.is_zero():
        return "u is zero"
    if not u.is_monic():
        return "u not monic (lc = %s)" % (u.lc(),)
    if u.deg > genus:
        return "deg u = %d > %d" % (u.deg, genus)
    if v.deg >= u.deg:
        return "deg v = %d >= deg u = %d" % (v.deg, u.deg)
    if not (curve.f - v * (v + curve.h)).mod(u).is_zero():
        return "u does not divide f - v*(v+h)"
    return None


def compose(curve, D1, D2):
    """Cantor composition. Returns a semi-reduced (u, v), deg u <= 2*genus."""
    f, h = curve.f, curve.h
    u1, v1 = D1
    u2, v2 = D2

    d1, e1, e2 = u1.xgcd(u2)                  # d1 = e1*u1 + e2*u2
    d, c1, c2 = d1.xgcd(v1 + v2 + h)          # d  = c1*d1 + c2*(v1+v2+h)

    s1 = c1 * e1
    s2 = c1 * e2
    s3 = c2

    u = (u1 * u2).exact_quotient(d * d)
    num = s1 * u1 * v2 + s2 * u2 * v1 + s3 * (v1 * v2 + f)
    v = num.exact_quotient(d).mod(u)
    return (u, v)


def reduce_divisor(curve, D, genus=None, verify=False):
    """Repeatedly apply the reduction step until deg u <= genus."""
    if genus is None:
        genus = curve.genus
    f, h = curve.f, curve.h
    u, v = D
    steps = 0
    while u.deg > genus:
        un = (f - v * (v + h)).exact_quotient(u).monic()
        vn = (-h - v).mod(un)
        u, v = un, vn
        steps += 1
        if steps > 64:
            raise ArithmeticError("reduction failed to terminate")
        if verify and not (f - v * (v + h)).mod(u).is_zero():
            raise ArithmeticError("reduction produced an invalid semi-reduced pair")
    return (u.monic(), v.mod(u.monic()))


def add(curve, D1, D2, verify=False):
    """The reduced representative of [D1] + [D2].

    `genus=curve.genus` must be threaded explicitly: omitting it leaves reduction
    running to a genus-3 default and returning unreduced garbage at genus 2.
    """
    return reduce_divisor(curve, compose(curve, D1, D2),
                          genus=curve.genus, verify=verify)


def double(curve, D, verify=False):
    """2*[D]. Plain composition already handles u1 == u2."""
    return add(curve, D, D, verify=verify)


def scalar_mul(curve, n, D):
    if n < 0:
        return scalar_mul(curve, -n, negate(curve, D))
    R = identity(curve)
    B = D
    while n:
        if n & 1:
            R = add(curve, R, B)
        B = double(curve, B)
        n >>= 1
    return R


# ===========================================================================
# split (real) model:  divisor class is (u, v, w, n)
# ===========================================================================

def compute_vp(curve):
    """Vp, one of the two square roots of f at infinity, truncated to degree g+1.

    Vp solves Vp*(Vp + h) == f in the top g+2 coefficients, built leading term
    downwards, exactly as ComputeVpl in
    generic/arbitrary/reduced_basis_arithmetic.mag.

    Raises if 2*Vl + hl is not invertible: it is the derivative of fl - hl*y - y^2
    and the denominator of every step.  In characteristic 2 it is hl alone, so a
    char-2 split curve needs deg h == g+1 for Vp to exist this way.
    """
    F, f, h, g = curve.F, curve.f, curve.h, curve.genus
    hl = h.coeff(g + 1)
    fl = f.coeff(2 * g + 2)

    # Vl is a root of y^2 + hl*y - fl.
    vl = _solve_quadratic(F, hl, -fl)
    if vl is None:
        raise ArithmeticError(
            "y^2 + %s*y - %s has no root in %r: this curve has no split model "
            "over its own field of definition" % (hl, fl, F))

    denom = vl + vl + hl
    if denom.is_zero():
        raise ArithmeticError(
            "2*Vl + hl = 0, so Vp cannot be built by this construction. In "
            "characteristic 2 this means deg h < g+1.")
    dinv = denom ** -1

    vp = _monomial(F, g + 1, vl)
    for i in range(g, -1, -1):
        corr = (f - vp * (vp + h)).coeff(g + 1 + i)
        vp = vp + _monomial(F, i, dinv * corr)
    return vp


def _solve_quadratic(F, b, c):
    """A root of y^2 + b*y + c over F, or None. Brute force: F is small here."""
    for y in F.elements():
        if (y * y + b * y + c).is_zero():
            return y
    return None


def compute_vn(curve, vp=None):
    """Vn = -Vp - h, the other root."""
    if vp is None:
        vp = compute_vp(curve)
    return -vp - curve.h


def reduced_basis(curve, D, V):
    """Put v into reduced basis against V, and recompute w.

    vhat = V - ((V - v) mod u). Pass Vp for positive reduced, Vn for negative.
    Generic in V, exactly as Reduced_Basis in the Magma reference.
    """
    u, v, _, n = _split4(curve, D)
    v = v.mod(u)
    vhat = V - (V - v).mod(u)
    what = (curve.f - vhat * (vhat + curve.h)).exact_quotient(u)
    return (u, vhat, what, n)


def adapted_basis(curve, D):
    """Standard Mumford form, v taken mod u."""
    u, v, _, n = _split4(curve, D)
    v = v.mod(u)
    w = (curve.f - v * (v + curve.h)).exact_quotient(u)
    return (u, v, w, n)


def split_identity(curve, V=None):
    """The zero class in the split model, in whichever basis V names.

    Its balancing weight is ceil(g/2), not 0: composition sets
    n = n1 + n2 + deg(S) - ceil(g/2), so adding a u = 1 class shifts n by
    n_E - ceil(g/2), and only n_E = ceil(g/2) leaves the other operand's weight
    alone.

    No `positive` flag, unlike split_add and split_adjust: `reduced_basis` is
    already generic in V, so passing Vp gives the positive-basis identity.
    V=None means the negative basis.
    """
    if V is None:
        V = compute_vn(curve)
    u = Poly.one(curve.F)
    v0 = Poly.zero(curve.F)
    w0 = (curve.f - v0 * (v0 + curve.h)).exact_quotient(u)
    return reduced_basis(curve, (u, v0, w0, _ceil_div(curve.genus, 2)), V)


def split_check_divisor(curve, D, V):
    """None if D is a valid negative-reduced balanced divisor, else a reason.

    Recomputes the closure identity on w rather than trusting the carried value,
    which is what makes w safe to carry at all.
    """
    u, v, w, n = _split4(curve, D)
    g = curve.genus
    if u.is_zero():
        return "u is zero"
    if not u.is_monic():
        return "u not monic (lc = %s)" % (u.lc(),)
    if u.deg > g + 1:
        return "deg u = %d > g+1 = %d" % (u.deg, g + 1)
    if u * w != curve.f - v * (v + curve.h):
        return "u*w != f - v*(v+h): carried w is inconsistent"
    if v != V - (V - v).mod(u):
        return "v is not in the reduced basis for the given V"
    if not (0 <= n <= g - u.deg):
        return "balancing weight n = %d outside [0, g - deg u] = [0, %d]" % (
            n, g - u.deg)
    return None


def split_add(curve, D1, D2, V, positive=False):
    """[D1] + [D2] in the split model.

    Ported from Add_SPLIT_NEG, with `positive=True` selecting Add_SPLIT_POS.
    Compose, normalise, reduce, adjust.
    """
    f, h, g = curve.f, curve.h, curve.genus
    u1, v1, w1, n1 = _split4(curve, D1)
    u2, v2, w2, n2 = _split4(curve, D2)

    # --- compose
    t1 = v1 + h
    S, a1, _b1 = u1.xgcd(u2)
    K = (a1 * (v2 - v1)).mod(u2)
    if not S.is_one():
        S2, a2, b2 = S.xgcd(v2 + t1)
        if not S2.is_one():
            u1 = u1.exact_quotient(S2)
            u2 = u2.exact_quotient(S2)
            K = (a2 * K + b2 * w1).mod(u2)
            w1 = w1 * S2
        else:
            K = (a2 * K + b2 * w1).mod(u2)
        S = S2
    T = u1 * K
    u = u1 * u2
    v = v1 + T
    w = (w1 - K * (t1 + v)).exact_quotient(u2)
    n = n1 + n2 + S.deg - _ceil_div(g, 2)

    u, v, w, n = _split_normalise_reduce(curve, u, v, w, n, V, positive)
    return split_adjust(curve, (u, v, w, n), V, positive)


def split_double(curve, D, V, positive=False):
    """2*[D] in the split model. Ported from Double_SPLIT_{NEG,POS}."""
    f, h, g = curve.f, curve.h, curve.genus
    u1, v1, w1, _n1 = _split4(curve, D)
    n1 = _split4(curve, D)[3]

    # --- compose
    t1 = v1 + v1 + h
    S, _a1, b1 = u1.xgcd(t1)
    if not S.is_one():
        u1 = u1.exact_quotient(S)
        K = (b1 * w1).mod(u1)
        w1 = w1 * S
    else:
        K = (b1 * w1).mod(u1)

    T = u1 * K
    u = u1 * u1
    v = v1 + T
    w = (w1 - K * (t1 + T)).exact_quotient(u1)
    n = 2 * n1 + S.deg - _ceil_div(g, 2)

    u, v, w, n = _split_normalise_reduce(curve, u, v, w, n, V, positive)
    return split_adjust(curve, (u, v, w, n), V, positive)


def _split_normalise_reduce(curve, u, v, w, n, V, positive=False):
    """The normalise-then-reduce tail shared by split_add and split_double.

    `positive=True` selects the positive reduced basis.  Compose and normalise are
    identical in both; the reduce loop differs only in which of the two leading
    coefficients is tested first, exactly as Add_SPLIT_POS differs from
    Add_SPLIT_NEG.  Getting it backwards yields a valid divisor in the right basis
    that is the wrong class: 37 of 63 operations agreeing rather than all.
    """
    f, h, g = curve.f, curve.h, curve.genus

    # --- normalise: bring v back into reduced basis if it outgrew u
    if v.deg >= u.deg:
        q, r = (V - v).divmod(u)
        tv = V - r
        w = w - q * (v + h + tv)
        v = tv

    # --- reduce
    steps = 0
    # first/second are the two leading coefficients, in the order the chosen
    # basis's Magma source tests them.
    first_lc = V.lc() if positive else (-V - h).lc()
    second_lc = (-V - h).lc() if positive else V.lc()
    while u.deg > g + 1:
        if v.deg == g + 1 and v.lc() == first_lc:
            n = n + u.deg - (g + 1)
        elif v.deg == g + 1 and v.lc() == second_lc:
            n = n + g + 1 - w.deg
        else:
            delta = u.deg - w.deg
            if delta % 2:
                raise ArithmeticError(
                    "deg u - deg w = %d is odd; the balancing weight would not "
                    "be an integer" % delta)
            n = n + delta // 2

        ou = u
        u = w
        q, r = (V + v + h).divmod(u)
        tv = V - r
        w = ou - q * (tv - v)
        v = tv

        steps += 1
        if steps > 64:
            raise ArithmeticError("split reduction failed to terminate")

    lc = u.lc()
    return (u.monic(), v, w * lc, n)


def split_adjust(curve, D, V, positive=False):
    """Bring the balancing weight into range.

    Ported from Adjust_SPLIT_NEG, with `positive=True` selecting Adjust_SPLIT_POS.
    Mirror images: each adjusts directly in its own basis one way, and the other
    way converts to the opposite basis, loops there, and converts back.

    Up while n < 0, down while n > g - deg u, and an already-balanced divisor is
    left alone.
    """
    if positive:
        return _split_adjust_pos(curve, D, V)
    f, h, g = curve.f, curve.h, curve.genus
    u, v, w, n = _split4(curve, D)
    steps = 0

    if n < 0:
        while n < 0:
            ou = u
            u = w
            q, r = (V + v + h).divmod(u)
            tv = V - r
            w = ou - q * (tv - v)
            v = tv
            n = n + g + 1 - u.deg
            steps += 1
            if steps > 64:
                raise ArithmeticError("up-adjustment failed to terminate")
        lc = u.lc()
        u, w = u.monic(), w * lc

    elif n > g - u.deg:
        # basis conversion into positive reduced
        Vp = -V - h
        t = Vp - V
        q, r = t.divmod(u)
        tv = v + t - r
        w = w - q * (v + h + tv)
        v = tv

        while n > g - u.deg + 1:
            n = n + u.deg - (g + 1)
            ou = u
            u = w
            q, r = (Vp + v + h).divmod(u)
            tv = Vp - r
            w = ou - q * (tv - v)
            v = tv
            steps += 1
            if steps > 64:
                raise ArithmeticError("down-adjustment failed to terminate")

        # final step back into negative reduced
        n = n + u.deg - (g + 1)
        ou = u
        u = w
        q, r = (V + v + h).divmod(u)
        tv = V - r
        w = ou - q * (tv - v)
        v = tv

        lc = u.lc()
        u, w = u.monic(), w * lc

    return (u, v, w, n)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _split_adjust_pos(curve, D, V):
    """Adjust_SPLIT_POS: the same algorithm in the positive reduced basis."""
    h, g = curve.h, curve.genus
    u, v, w, n = _split4(curve, D)
    steps = 0

    if n > g - u.deg:
        while n > g - u.deg:
            n = n + u.deg - (g + 1)
            ou = u
            u = w
            q, r = (V + v + h).divmod(u)
            tv = V - r
            w = ou - q * (tv - v)
            v = tv
            steps += 1
            if steps > 64:
                raise ArithmeticError("down-adjustment failed to terminate")
        lc = u.lc()
        u, w = u.monic(), w * lc

    elif n < 0:
        # convert into the negative reduced basis, loop there, convert back
        Vn = -V - h
        t = Vn - V
        q, r = t.divmod(u)
        tv = v + t - r
        w = w - q * (v + h + tv)
        v = tv
        while n < -1:
            ou = u
            u = w
            q, r = (Vn + v + h).divmod(u)
            tv = Vn - r
            w = ou - q * (tv - v)
            v = tv
            n = n + g + 1 - u.deg
            steps += 1
            if steps > 64:
                raise ArithmeticError("up-adjustment failed to terminate")
        ou = u
        u = w
        q, r = (V + v + h).divmod(u)
        tv = V - r
        w = ou - q * (tv - v)
        v = tv
        n = n + g + 1 - u.deg
        lc = u.lc()
        u, w = u.monic(), w * lc

    return (u, v, w, n)


def _split4(curve, D):
    """Accept (u, v, w, n) or (u, v, n) or (u, v), filling in what is missing.

    w is derivable as (f - v(v+h))/u, so callers may omit it; supplied, it is used
    as given and split_check_divisor verifies it.
    """
    if len(D) == 4:
        return D
    if len(D) == 3:
        u, v, n = D
        return (u, v, (curve.f - v * (v + curve.h)).exact_quotient(u), n)
    u, v = D
    return (u, v, (curve.f - v * (v + curve.h)).exact_quotient(u), 0)


def _monomial(F, degree, coeff):
    """coeff * x^degree; Poly offers only little-endian from_coeffs."""
    return Poly.from_coeffs(F, [F.zero] * degree + [coeff])


def _ceil_div(a, b):
    """Ceiling(a/b) for non-negative ints, matching Magma's Ceiling(g/2)."""
    return -((-a) // b)
