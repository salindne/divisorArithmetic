"""
curve.py -- random genus-3 ramified-model curves and random reduced divisors.

Model:  C: y^2 + h(x) y = f(x),  f monic of degree 7, deg h <= 3,
        exactly one point at infinity.  There is no balancing weight.

Curve classes (matching the repository's own vocabulary):
    "arb"  : f monic deg 7, h random of degree <= 3, any characteristic
    "odd"  : characteristic != 2, h = 0
    "even" : characteristic 2, h != 0 of degree <= 3

Divisor generation is *direct* (no use of reference.py), by
    * building prime divisors  [p, w]  with p irreducible, and
    * Hensel-lifting them to prime powers  [p^e, w_e], and
    * CRT-combining pairwise-coprime prime powers.
Since  p^e | f - w_e(w_e + h)  for each part and the parts are coprime,
the CRT result satisfies  u | f - v(v+h)  by construction; reducing v mod u
gives deg v < deg u.  This yields every factorisation shape of u for
0 <= deg u <= 3, including irreducible quadratic/cubic u, which a
"sum of rational points" generator can never produce.

Curve acceptance is *empirical*, as required: a candidate curve is kept only if
reference.py forms a group on random divisor classes over it (closure, identity,
inverses, commutativity and associativity).  No nonsingularity criterion is
assumed.  `singularity_diagnostic()` is provided for *reporting only*, so the
empirical filter can be cross-checked against textbook theory.
"""

from __future__ import annotations

import random

import reference as cantor  # renamed module; alias keeps the ported body intact
from ff import GF, FiniteField
from poly import ExactQuotientError, Poly

__all__ = [
    "Curve", "random_curve", "random_valid_curve", "validate_curve",
    "random_divisor", "random_divisor_pair", "random_divisor_of_degree",
    "affine_points", "singularity_diagnostic", "CurveRejected",
    "DEGREE_PATTERNS", "PAIR_MODES", "pair_gcd_signature",
    "prime_divisor_pool", "find_prime_divisor", "hensel_lift", "crt_divisor",
    "prime_power_divisors_deg1", "build_test_set", "all_reduced_divisors",
    "LEVELS",
]

# Curve-class names. The repo spells these {arb, nch2, ch2} in every filename;
# the harness this came from spelled them {arb, odd, even}. The repo's names are
# canonical here and the old ones are accepted as aliases, so the audit's stored
# repro scripts still run unedited.
KIND_ALIASES = {"odd": "nch2", "even": "ch2", "arb": "arb",
                "nch2": "nch2", "ch2": "ch2"}
KINDS = ("arb", "nch2", "ch2")
MODELS = ("ramified", "split")


def canonical_kind(kind):
    """Map a curve-class name to its canonical spelling, rejecting unknowns."""
    try:
        return KIND_ALIASES[kind]
    except KeyError:
        raise ValueError("unknown curve kind %r; expected one of %s or the "
                         "aliases odd/even" % (kind, ", ".join(KINDS)))


def deg_f(genus, model):
    """Degree of f: 2g+1 for the ramified model, 2g+2 for the split model."""
    return 2 * genus + 1 if model == "ramified" else 2 * genus + 2


def deg_h_max(genus, model):
    """Maximum degree of h: g for ramified, g+1 for split."""
    return genus if model == "ramified" else genus + 1


class CurveRejected(Exception):
    pass


# ---------------------------------------------------------------------------
# curve object
# ---------------------------------------------------------------------------

class Curve:
    """A hyperelliptic curve y^2 + h(x) y = f(x) over a finite field.

    Parameterised by genus and model rather than fixed at genus-3 ramified:

      ramified (imaginary)  deg f = 2g+1, deg h <= g,   one place at infinity
      split (real)          deg f = 2g+2, deg h <= g+1, two places at infinity
    """

    def __init__(self, F, f, h, kind="arb", genus=3, model="ramified"):
        if model not in MODELS:
            raise ValueError("unknown model %r; expected one of %s"
                             % (model, ", ".join(MODELS)))
        want_f = deg_f(genus, model)
        want_h = deg_h_max(genus, model)
        # Monic is required for the ramified model and NOT for the split one. A
        # split curve needs `x^2 + h_{g+1} x - f_{2g+2}` to have a root in F, and
        # forcing f_{2g+2} = 1 makes that quadratic `x^2 + x + 1` for every
        # characteristic-2 curve -- irreducible over GF(8) and GF(32), so every
        # candidate was rejected and the ch2 split families looked untestable. The
        # formulas themselves treat it as a live parameter: the arb and ch2
        # Precompute functions both read Coeff(f, 2g+2), which would be pointless if
        # it were always 1. reference.compute_vp reads it generally too.
        if model == "ramified":
            assert f.deg == want_f and f.is_monic(), (
                "f must be monic of degree %d for genus %d %s, got degree %d"
                % (want_f, genus, model, f.deg))
        else:
            assert f.deg == want_f, (
                "f must have degree exactly %d for genus %d %s, got degree %d"
                % (want_f, genus, model, f.deg))
        assert h.deg <= want_h, (
            "deg h must be <= %d for genus %d %s, got %d"
            % (want_h, genus, model, h.deg))
        self.F = F
        self.f = f
        self.h = h
        self.kind = canonical_kind(kind)
        self.genus = genus
        self.model = model
        # caches
        self._points = None
        self._pool = {}     # prime degree -> list of (p, w)
        self._vp = None     # split model only, computed on demand

    # -- derived shape -----------------------------------------------------
    @property
    def deg_f(self):
        return deg_f(self.genus, self.model)

    @property
    def deg_h_max(self):
        return deg_h_max(self.genus, self.model)

    # -- coefficient views used by the explicit formulas -------------------
    @property
    def f_coeffs(self):
        """[f0, f1, ..., f_{deg f}] as field elements; the top one is 1."""
        return self.f.coeffs_up_to(self.deg_f)

    @property
    def h_coeffs(self):
        """[h0, ..., h_{deg_h_max}]."""
        return self.h.coeffs_up_to(self.deg_h_max)

    def fc(self, i):
        return self.f.coeff(i)

    def hc(self, i):
        return self.h.coeff(i)

    def __repr__(self):
        return ("Curve(%r, genus=%d, model=%s, kind=%s, f=%s, h=%s)"
                % (self.F, self.genus, self.model, self.kind, self.f, self.h))


# ---------------------------------------------------------------------------
# random curves
# ---------------------------------------------------------------------------

def _random_poly(F, max_deg, rng, monic_deg=None):
    if monic_deg is not None:
        c = [F.random(rng) for _ in range(monic_deg)] + [F.one]
        return Poly(F, c)
    return Poly(F, [F.random(rng) for _ in range(max_deg + 1)])


def random_curve(F, kind, rng=random, genus=3, model="ramified",
                 normal_form=False, infinity_y=None, force_hlead=None):
    """A candidate curve of the requested class (no validation performed).

    `normal_form=True` restricts to the characteristic-2 ramified normal form
    that the ch2 genus-3 formulas are derived for and valid only on:

        h = x^g + h_{g-1} x^{g-1} + ... + h_0        (monic, deg h == g exactly)
        f = x^{2g+1} + f_2 x^2 + f_1 x + f_0         (f_{2g} ... f_3 all zero)

    Those formulas cannot be tested on anything else: outside this shape they
    are not claimed correct, so a mismatch there would be an artefact rather
    than a bug. See divisor-audits/g3ram/CHAR2_NORMAL_FORM.md.

    For the split model, `infinity_y` fixes the root of
    `x^2 + h_{g+1} x - f_{2g+2}` and `force_hlead` fixes h's leading coefficient.
    Both exist because the split formula families differ in what they assume about
    the places at infinity, and each family's own Precompute states which: the nch2
    files hardcode the root as 1, the ch2 files hardcode h_{g+1} as 1 inside the
    polynomial they factor, and the arb files read both from the curve. See
    `_split_leading` and driver.py's `split_infinity_spec`.
    """
    kind = canonical_kind(kind)
    df = deg_f(genus, model)
    dh = deg_h_max(genus, model)

    if normal_form:
        if kind != "ch2" or F.p != 2:
            raise ValueError("normal_form applies to the ch2 class in "
                             "characteristic 2 only")
        if model != "ramified":
            raise ValueError("the derived normal form is for the ramified "
                             "model only")
        # h monic of degree exactly g; f monic with f_{2g}..f_3 zero.
        h = Poly(F, [F.random(rng) for _ in range(genus)] + [F.one])
        fc = [F.random(rng) for _ in range(3)] + [F.zero] * (df - 3) + [F.one]
        return Curve(F, Poly(F, fc), h, kind, genus=genus, model=model)

    if kind == "nch2":
        if F.p == 2:
            raise ValueError("kind 'nch2' requires characteristic != 2")
        f = _random_poly(F, None, rng, monic_deg=df)
        h = Poly.zero(F)
    elif kind == "ch2":
        if F.p != 2:
            raise ValueError("kind 'ch2' requires characteristic 2")
        f = _random_poly(F, None, rng, monic_deg=df)
        while True:
            h = _random_poly(F, dh, rng)
            if not h.is_zero():
                break
    else:  # arb
        f = _random_poly(F, None, rng, monic_deg=df)
        h = _random_poly(F, dh, rng)

    if model == "split":
        # Vp must exist over F, else the curve has no usable split model here.
        # In characteristic 2 that additionally forces deg h == g+1, since the
        # denominator 2*Vl + hl degenerates to hl. Force it rather than
        # rejecting most candidates downstream.
        if F.p == 2 and h.coeff(dh).is_zero():
            cs = h.coeffs_up_to(dh)
            cs[dh] = F.one
            h = Poly(F, cs)
        if force_hlead is not None:
            cs = h.coeffs_up_to(dh)
            cs[dh] = force_hlead
            h = Poly(F, cs)
        f = _split_leading(F, f, h, df, dh, rng, infinity_y)

    return Curve(F, f, h, kind, genus=genus, model=model)


def _split_leading(F, f, h, df, dh, rng, y=None):
    """Set f's leading coefficient so the places at infinity are rational.

    The split model needs `x^2 + h_{g+1} x - f_{2g+2}` to have a root in F: that
    root is the value attached to a place at infinity, and without it the two
    places are conjugate over a quadratic extension and the curve is not a split
    one over F at all.

    Rather than draw f_{2g+2} and reject, pick the root `y` and solve for the
    coefficient: `f_{2g+2} = y^2 + h_{g+1} * y`, which splits by construction.

    This matters most in characteristic 2. Drawing f monic makes the quadratic
    `x^2 + x + 1` for every single curve, whose roots lie in GF(4); over GF(8) or
    GF(32) it is irreducible, so *every* candidate was rejected and the ch2 split
    families looked untestable. Choosing y instead gives valid curves over every
    characteristic-2 field.

    Two families of y are excluded:

      y = 0 and y = -h_{g+1}, because both give f_{2g+2} = y*(y + h_{g+1}) = 0 and
      drop the degree below 2g+2.

      y with 2y + h_{g+1} = 0, because that is the double root: the quadratic then
      has one root rather than two, so the curve has a single place at infinity and
      is ramified there, not split. Precompute divides by exactly that quantity and
      raises ZeroDivisionError, and reference.compute_vp refuses for the same reason
      ("2*Vl + hl = 0, so Vp cannot be built"). Such curves are not split curves, so
      excluding them is correct rather than convenient.

    Over GF(2) with h_{g+1} = 1 nothing survives, since y must avoid both 0 and 1.
    That is a real fact about the field, not a gap: there is no characteristic-2
    split curve over GF(2) with deg h = g+1, and callers are told rather than left
    with a silent zero.
    """
    hl = h.coeff(dh)
    choices = [e for e in F.elements()
               if not e.is_zero() and not (e + hl).is_zero()
               and not (e + e + hl).is_zero()]
    if not choices:
        return f                      # GF(2) with h_{g+1} = 1: nothing to pick
    if y is None:
        y = choices[rng.randrange(len(choices))]
    cs = f.coeffs_up_to(df)
    cs[df] = y * y + hl * y
    if cs[df].is_zero():
        return f
    return Poly(F, cs)


def singularity_diagnostic(curve):
    """Textbook singularity test, for REPORTING ONLY (never used to accept).

    char != 2 :  y^2 + hy = f  <->  (2y+h)^2 = h^2 + 4f, smooth iff h^2+4f squarefree.
    char == 2 :  singular at (x0,y0) iff h(x0) = 0 and f'(x0)^2 = h'(x0)^2 f(x0),
                 i.e. iff gcd(h, f'^2 - h'^2 f) is non-constant (h == 0 counts).
    Returns True when the curve is SINGULAR by this criterion.
    """
    f, h = curve.f, curve.h
    if curve.F.p != 2:
        return not (h * h + 4 * f).is_squarefree()
    fp, hp = f.derivative(), h.derivative()
    w = fp * fp - hp * hp * f
    if h.is_zero():
        return True
    if w.is_zero():
        return True
    return h.gcd(w).deg > 0


# ---------------------------------------------------------------------------
# prime divisors
# ---------------------------------------------------------------------------

def affine_points(curve):
    """All affine F-rational points (a, b) with b^2 + h(a) b = f(a)."""
    if curve._points is None:
        F = curve.F
        pts = []
        for a in F.elements():
            ha, fa = curve.h.eval(a), curve.f.eval(a)
            for b in F.elements():
                if b * b + ha * b == fa:
                    pts.append((a, b))
        curve._points = pts
    return curve._points


def prime_divisors_deg1(curve):
    """Degree-1 prime divisors [x - a, b] for every affine point."""
    if 1 not in curve._pool:
        F = curve.F
        out = []
        for (a, b) in affine_points(curve):
            p = Poly(F, [-a, F.one])
            w = Poly.const(F, b)
            out.append((p, w))
        curve._pool[1] = out
    return curve._pool[1]


def _distinct_degree_gcd(Fv, q, d):
    """gcd(Fv, x^(q^d) - x): product of the distinct irreducible factors of Fv
    whose degree divides d."""
    F = Fv.F
    x = Poly.x(F)
    if Fv.deg <= 0:
        return Poly.one(F)
    xq = x.powmod(q ** d, Fv)
    g = Fv.gcd(xq - x)
    return g


def find_prime_divisor(curve, d, rng=random, attempts=400):
    """Find a prime divisor [p, w] with p irreducible of degree d (d in 1,2,3).

    Method (no factorisation code needed): pick a random v of degree <= 2, set
    Fv = f - v(v+h) (degree 7 since deg v <= 2), and look at
        Q_d = gcd(Fv, x^(q^d) - x) / gcd(Fv, x^q - x)      for d in {2, 3},
    which is the product of the distinct irreducible degree-d factors of Fv
    (degree-1 factors removed; no other degrees divide 2 or 3 nontrivially).
    If deg Q_d == d then Q_d is itself irreducible; take p = Q_d, w = v mod p.
    Then p | Fv and v = w mod p, so p | f - w(w+h).
    """
    F, q = curve.F, curve.F.q
    if d == 1:
        pool = prime_divisors_deg1(curve)
        return rng.choice(pool) if pool else None
    if d < 1:
        raise ValueError("prime divisor degree must be >= 1")
    x = Poly.x(F)
    for _ in range(attempts):
        v = Poly(F, [F.random(rng) for _ in range(curve.genus)])
        Fv = curve.f - v * (v + curve.h)
        if Fv.deg < d:
            continue
        G1 = _distinct_degree_gcd(Fv, q, 1)
        Gd = _distinct_degree_gcd(Fv, q, d)
        try:
            Qd = Gd.exact_quotient(Gd.gcd(G1))
        except ExactQuotientError:            # cannot happen, but stay safe
            continue
        if Qd.deg == d:
            p = Qd.monic()
            w = v.mod(p)
            assert (curve.f - w * (w + curve.h)).mod(p).is_zero()
            return (p, w)
    return None


def prime_divisor_pool(curve, d, rng=random, want=6):
    """A small cached pool of degree-d prime divisors."""
    if d == 1:
        return prime_divisors_deg1(curve)
    have = curve._pool.get(d)
    if have is None:
        have = []
        seen = set()
        for _ in range(8):
            got = find_prime_divisor(curve, d, rng)
            if got is None:
                break
            key = (got[0].c, got[1].c)
            if key not in seen:
                seen.add(key)
                have.append(got)
            if len(have) >= want:
                break
        curve._pool[d] = have
    return have


# ---------------------------------------------------------------------------
# Hensel lifting and CRT
# ---------------------------------------------------------------------------

def hensel_lift(curve, p, w, e):
    """Lift [p, w] to [p^e, w_e] with p^e | f - w_e(w_e + h).

    v_{j+1} = v_j + p^j t  with  t = ((f - v_j(v_j+h))/p^j) / (2 v_j + h)  mod p.
    Returns None if 2w + h is not invertible mod p (ramified prime: the
    prime-power divisor does not exist).
    """
    f, h = curve.f, curve.h
    v = w.mod(p)
    pk = p
    for _ in range(1, e):
        num = f - v * (v + h)
        A = num.exact_quotient(pk).mod(p)
        D = (2 * v + h).mod(p)
        if D.is_zero():
            return None
        try:
            t = (A * D.inverse_mod(p)).mod(p)
        except ZeroDivisionError:
            return None
        v = v + pk * t
        pk = pk * p
        v = v.mod(pk)
    return (pk, v.mod(pk))


def crt_divisor(curve, parts):
    """CRT pairwise-coprime parts [(m_i, r_i)] into a single (u, v)."""
    F = curve.F
    if not parts:
        return cantor.identity(curve)
    M, V = parts[0]
    for (m, r) in parts[1:]:
        g, a, _ = M.xgcd(m)
        if not g.is_one():
            raise CurveRejected("crt_divisor got non-coprime moduli")
        t = ((r - V) * a).mod(m)
        V = (V + M * t)
        M = M * m
        V = V.mod(M)
    M = M.monic()
    return (M, V.mod(M))


# ---------------------------------------------------------------------------
# random reduced divisors
# ---------------------------------------------------------------------------
# A "pattern" is a multiset of (prime_degree, exponent) with
# sum(prime_degree * exponent) == deg u.
def _degree_patterns(max_deg):
    """Every way to build deg u = d from prime places, for d = 0..max_deg.

    A pattern is a tuple of (prime degree, exponent) pairs summing to d. Several
    pairs may share a prime degree, meaning that many *distinct* primes of that
    degree, so ((1,1),(1,1)) is two different degree-1 places while ((1,2),) is
    one place squared. Both are wanted: they exercise different gcd structure.

    Generated rather than hand-written because the split model needs
    deg u <= g+1, so genus 3 split reaches degree 4, past the original table.
    _PATTERNS_REFERENCE below pins the generator against the hand-written table
    it replaces.
    """
    out = {0: [()]}
    for d in range(1, max_deg + 1):
        pats = []

        def build(remaining, max_exp_first, acc):
            if remaining == 0:
                pats.append(tuple(acc))
                return
            for pdeg in range(1, remaining + 1):
                for e in range(1, remaining // pdeg + 1):
                    # Non-increasing (pdeg, e) keeps one representative per
                    # multiset instead of every permutation.
                    if acc and (pdeg, e) > acc[-1]:
                        continue
                    build(remaining - pdeg * e, e, acc + [(pdeg, e)])

        build(d, d, [])
        pats.sort()
        out[d] = pats
    return out


# The hand-written table this replaces, kept as an assertion rather than a
# comment: the generator must reproduce it exactly for degrees 0 to 3.
_PATTERNS_REFERENCE = {
    0: [()],
    1: [((1, 1),)],
    2: [((1, 1), (1, 1)), ((1, 2),), ((2, 1),)],
    3: [((1, 1), (1, 1), (1, 1)), ((1, 2), (1, 1)), ((1, 3),),
        ((2, 1), (1, 1)), ((3, 1),)],
}

_generated = _degree_patterns(3)
for _d, _want in _PATTERNS_REFERENCE.items():
    assert sorted(_generated[_d]) == sorted(_want), (
        "degree-pattern generator disagrees with the validated table at "
        "d=%d: generated %r, expected %r" % (_d, _generated[_d], _want))
del _generated, _d, _want

# Degrees 0..4 covers every model and genus in this repository: ramified needs
# deg u <= g, split needs deg u <= g+1, and g is at most 3.
DEGREE_PATTERNS = _degree_patterns(4)


def _build_from_pattern(curve, pattern, rng, shared=None):
    """Realise a pattern as a reduced divisor.  `shared` is an optional
    (prime_degree, (p, w)) forced part.  Returns None on failure."""
    parts = []
    used = []
    forced = []
    if shared is not None:
        sd, (sp, sw) = shared
        # consume one pattern slot with prime degree sd
        for i, (pd, pe) in enumerate(pattern):
            if pd == sd:
                forced.append((i, pe))
                break
        if not forced:
            return None
        idx, exp = forced[0]
        lift = hensel_lift(curve, sp, sw, exp)
        if lift is None:
            return None
        parts.append(lift)
        used.append(sp)
        pattern = pattern[:idx] + pattern[idx + 1:]

    for (pd, pe) in pattern:
        pool = prime_divisor_pool(curve, pd, rng)
        if not pool:
            return None
        cands = [pw for pw in pool if all(pw[0] != q for q in used)]
        if not cands:
            return None
        p, w = rng.choice(cands)
        lift = hensel_lift(curve, p, w, pe)
        if lift is None:
            return None
        parts.append(lift)
        used.append(p)
    try:
        return crt_divisor(curve, parts)
    except (CurveRejected, ExactQuotientError, ZeroDivisionError):
        return None


def random_divisor_of_degree(curve, d, rng=random, pattern=None, tries=30,
                             shared=None):
    """A random reduced divisor with deg u == d (or None if none could be built)."""
    if d == 0:
        return cantor.identity(curve)
    pats = [pattern] if pattern is not None else list(DEGREE_PATTERNS[d])
    for _ in range(tries):
        pat = rng.choice(pats)
        D = _build_from_pattern(curve, pat, rng, shared=shared)
        if D is None:
            continue
        if D[0].deg != d:
            continue
        if cantor.check_divisor(curve, D) is None:
            return D
    return None


def max_divisor_degree(curve):
    """Largest deg u a reduced divisor can have: g for ramified, g+1 for split."""
    return curve.genus if curve.model == "ramified" else curve.genus + 1


def random_divisor(curve, rng=random, degs=None, weights=None):
    """A random reduced divisor of a random degree drawn from `degs`.

    `degs=None` means every degree the curve admits, 0 through
    max_divisor_degree(curve), rather than the fixed (0,1,2,3) this had when it
    was genus-3-ramified-only.
    """
    if degs is None:
        degs = tuple(range(max_divisor_degree(curve) + 1))
    order = list(degs)
    if weights:
        order = rng.choices(order, weights=weights, k=len(order))
    else:
        rng.shuffle(order)
    for d in order:
        D = random_divisor_of_degree(curve, d, rng)
        if D is not None:
            return D
    for d in (1, 2, 3, 0):
        D = random_divisor_of_degree(curve, d, rng)
        if D is not None:
            return D
    raise CurveRejected("no reduced divisor could be generated")


# ---------------------------------------------------------------------------
# divisor pairs, including the non-generic gcd cases
# ---------------------------------------------------------------------------

PAIR_MODES = ("generic", "equal", "opposite", "shared_u", "shared_opposite",
              "shared_ramified", "identity_left", "identity_right")


def _ramified_deg1_primes(curve):
    """Degree-1 primes with 2w + h == 0 mod p (i.e. P = -P)."""
    out = []
    for (p, w) in prime_divisors_deg1(curve):
        if (2 * w + curve.h).mod(p).is_zero():
            out.append((p, w))
    return out


def random_divisor_pair(curve, rng=random, mode="generic", degs=None):
    """Return (D1, D2) for the requested mode, or None if unavailable.

    `degs=None` means 1 through max_divisor_degree(curve); degree 0 is the
    identity and is covered by the identity_left / identity_right modes.

    modes
    -----
    generic         : two independent random divisors
    equal           : D1 == D2 (the doubling input)
    opposite        : D2 == -D1
    shared_u        : gcd(u1,u2) != 1 via a common non-ramified prime divisor P
                      (so generically gcd(u1,u2,v1+v2+h) == 1: the S != 1,
                      S' == 1 branch)
    shared_opposite : D1 contains P and D2 contains -P for a non-ramified P,
                      so v1+v2+h == 0 mod p: the S' != 1 branch
    shared_ramified : D1 and D2 both contain the same ramified prime P = -P,
                      which also forces v1+v2+h == 0 mod p
    identity_left/right : one operand is the zero class
    """
    if degs is None:
        degs = tuple(range(1, max_divisor_degree(curve) + 1))
    if mode == "generic":
        D1 = random_divisor(curve, rng, degs=degs)
        D2 = random_divisor(curve, rng, degs=degs)
        return (D1, D2)
    if mode == "equal":
        D = random_divisor(curve, rng, degs=degs)
        return (D, D)
    if mode == "opposite":
        D = random_divisor(curve, rng, degs=degs)
        return (D, cantor.negate(curve, D))
    if mode == "identity_left":
        return (cantor.identity(curve), random_divisor(curve, rng, degs=degs))
    if mode == "identity_right":
        return (random_divisor(curve, rng, degs=degs), cantor.identity(curve))

    if mode in ("shared_u", "shared_opposite"):
        # pick a non-ramified prime of degree 1 or 2 to share
        cands = []
        for pd in (1, 2):
            for (p, w) in prime_divisor_pool(curve, pd, rng):
                if not (2 * w + curve.h).mod(p).is_zero():
                    cands.append((pd, (p, w)))
        if not cands:
            return None
        for _ in range(40):
            pd, (p, w) = rng.choice(cands)
            w2 = w if mode == "shared_u" else (-curve.h - w).mod(p)
            d1 = rng.choice([d for d in degs if d >= pd] or [pd])
            d2 = rng.choice([d for d in degs if d >= pd] or [pd])
            D1 = random_divisor_of_degree(curve, d1, rng, shared=(pd, (p, w)))
            D2 = random_divisor_of_degree(curve, d2, rng, shared=(pd, (p, w2)))
            if D1 is not None and D2 is not None:
                return (D1, D2)
        return None

    if mode == "shared_ramified":
        ram = _ramified_deg1_primes(curve)
        if not ram:
            return None
        for _ in range(40):
            p, w = rng.choice(ram)
            d1, d2 = rng.choice(degs), rng.choice(degs)
            D1 = random_divisor_of_degree(curve, max(d1, 1), rng, shared=(1, (p, w)))
            D2 = random_divisor_of_degree(curve, max(d2, 1), rng, shared=(1, (p, w)))
            if D1 is not None and D2 is not None:
                return (D1, D2)
        return None

    raise ValueError("unknown pair mode %r" % (mode,))


def all_reduced_divisors(curve, max_checks=1500000):
    """EVERY reduced divisor on the curve, by brute force over (u, v).

    Enumerates all monic u with deg u <= 3 and all v with deg v < deg u and
    keeps the pairs with u | f - v(v+h).  Deliberately dumb and exhaustive: it
    shares no code path with the divisor generator, so comparing it against
    Cantor addition gives a complete, non-sampled check of the group structure
    (order, closure, inverses, associativity) on small fields.

    Cost is 1 + q^2 + q^4 + q^6 divisibility tests, so keep q small (<= 5, or
    <= 8 if you are patient).
    """
    F = curve.F
    q = F.q
    need = 1 + q ** 2 + q ** 4 + q ** 6
    if need > max_checks:
        raise CurveRejected("exhaustive enumeration too large for %r (%d checks)"
                            % (F, need))
    els = F.elements()
    f, h = curve.f, curve.h
    out = [cantor.identity(curve)]
    for d in (1, 2, 3):
        for ucoef in _tuples(els, d):
            u = Poly(F, list(ucoef) + [F.one])
            if u.deg != d:
                continue
            for vcoef in _tuples(els, d):
                v = Poly(F, list(vcoef))
                if (f - v * (v + h)).mod(u).is_zero():
                    out.append((u, v))
    return out


def _tuples(els, k):
    if k == 0:
        yield ()
        return
    for rest in _tuples(els, k - 1):
        for e in els:
            yield rest + (e,)


def pair_gcd_signature(curve, D1, D2):
    """(deg gcd(u1,u2), deg gcd(gcd(u1,u2), v1+v2+h)) -- the branch selector of
    both the thesis algorithm and Nucomp_g3_RAM."""
    u1, v1 = D1
    u2, v2 = D2
    g = u1.gcd(u2)
    g2 = g.gcd(v1 + v2 + curve.h)
    return (g.deg, g2.deg)


# ---------------------------------------------------------------------------
# empirical curve validation
# ---------------------------------------------------------------------------
# Why the test set is *targeted* and not purely random:
#
# On a curve that is singular at an F-rational point (a, b), the pairs
# [(x-a)^2, b + c(x-a)] are valid reduced divisors for EVERY c in F, instead of
# at most two.  Those surplus divisors are exactly the ones on which Cantor's
# group law breaks, so the test set deliberately contains *all* prime-power
# divisors supported at degree-1 primes.  Measured on hand-built singular
# curves, random triples break associativity only ~0.2-2% of the time, whereas
# the cancellation law (D1 + D2) - D2 == D1 over the targeted set breaks
# 1.3-10% of the time -- which is what makes the filter reliable.

def prime_power_divisors_deg1(curve, max_exp=None):
    """Every valid reduced divisor [p^e, w] with p linear and e <= max_exp.

    max_exp defaults to the largest deg u the curve admits, so g for the
    ramified model and g+1 for split. It was fixed at 3, which on a genus-2
    curve produced degree-3 divisors that then failed validation, rejecting
    every genus-2 curve outright.

    Complete (not sampled): w mod p is one of the <= 2 points above x = a, and
    each further level adds one unknown coefficient which is enumerated over F.
    """
    if max_exp is None:
        max_exp = max_divisor_degree(curve)
    F = curve.F
    f, h = curve.f, curve.h
    out = []
    for a in F.elements():
        p = Poly(F, [-a, F.one])
        level = []
        for (aa, b) in affine_points(curve):
            if aa == a:
                level.append(Poly.const(F, b))
        m = p
        for e in range(1, max_exp + 1):
            keep = []
            for w in level:
                if (f - w * (w + h)).mod(m).is_zero():
                    keep.append(w)
                    out.append((m, w))
            if e == max_exp:
                break
            level = [w + c * m for w in keep for c in F.elements()]
            m = m * p
    return out


def build_test_set(curve, rng=random, n_random=14):
    """Targeted + random divisors used to test the group axioms."""
    tset = list(prime_power_divisors_deg1(curve))
    n_targeted = len(tset)
    for _ in range(n_random):
        try:
            tset.append(random_divisor(curve, rng))
        except CurveRejected:
            break
    if not tset:
        tset = [cantor.identity(curve)]
    return tset, n_targeted


LEVELS = {
    # level      : (pair strategy, n_pairs cap, n_triples, n_random)
    "fast":       ("random", 150, 100, 12),
    "standard":   ("deg1cross", 1600, 220, 14),
    "exhaustive": ("all", 9000, 400, 18),
}


def _cancellation_pairs(tset, n_targeted, strategy, cap, rng):
    """Pairs (D1, D2) for the cancellation / commutativity sweep.

    "deg1cross" is the high-power choice: on a curve singular at an F-rational
    point, the observed cancellation failures always have D1 a surplus divisor
    (deg u >= 2, supported at the singular point) and D2 a degree-1 divisor, so
    sweeping every targeted D1 against every degree-1 D2 makes detection
    deterministic instead of probabilistic.
    """
    targeted = tset[:n_targeted]
    if strategy == "all" and targeted:
        pairs = [(a, b) for a in targeted for b in targeted]
    elif strategy == "deg1cross" and targeted:
        deg1 = [D for D in targeted if D[0].deg == 1]
        pairs = [(a, b) for a in tset for b in deg1]
        pairs += [(b, a) for a in tset for b in deg1]
        # plus unrestricted pairs so closure/commutativity are exercised on
        # operands that are not degree-1
        pairs += [(rng.choice(tset), rng.choice(tset)) for _ in range(80)]
    else:
        pairs = []
    if not pairs:
        return [(rng.choice(tset), rng.choice(tset)) for _ in range(min(cap, 150))]
    if len(pairs) > cap:
        pairs = rng.sample(pairs, cap)
    return pairs


def validate_curve(curve, rng=random, level="standard", n_pairs=None,
                   n_triples=None, n_random=None, require_smooth=True):
    """Empirically test that reference.py forms a group on this curve.

    Checks: validity of every test divisor, left/right identity, inverses,
    closure (with per-reduction-step verification), commutativity,
    cancellation and ASSOCIATIVITY.  Returns (ok, reason).

    level: "fast" (cheap screen used while resampling curves), "standard"
    (default) or "exhaustive".

    Also rejects on the textbook criterion, for the same reason validate_split_curve
    does. Neither check subsumes the other and both are individually incomplete:

      * The criterion detects geometric singularity, over the algebraic closure. Most
        of the curves it flags here have their singular point only in an extension
        field, where F-rational divisor arithmetic can never reach it.
      * The empirical filter samples finitely, so it can miss a singular point even
        when that point IS F-rational. Measured over 500 candidates per field: at
        genus 3 over GF(8), four accepted curves had an F-rational singular point,
        and they passed even standard-level validation.

    So the conservative combination is the right one -- reject if either objects, and
    `require_smooth=True` is the default for that reason. It is a parameter rather
    than a hardcoded test so `random_valid_curve(require_smooth=False)` still means
    what it says; that path exists to study the curves the criterion rejects, and
    silently overriding it would have made the flag a lie.

    This uses the criterion to REJECT, never to accept, so the module's refusal to
    assume a nonsingularity criterion still holds; the cost is a narrower tested
    domain, which is the safe direction.
    """
    if require_smooth and singularity_diagnostic(curve):
        return False, "singular by the textbook criterion"
    strategy, cap, triples, n_rand = LEVELS[level]
    if n_pairs is not None:
        cap = n_pairs
    if n_triples is not None:
        triples = n_triples
    if n_random is not None:
        n_rand = n_random
    try:
        zero = cantor.identity(curve)
        tset, n_targeted = build_test_set(curve, rng, n_random=n_rand)
        for D in tset:
            why = cantor.check_divisor(curve, D)
            if why is not None:
                return False, "generated divisor invalid: %s" % why

        # identity and inverses on every test divisor
        for D in tset:
            if not cantor.eq(cantor.add(curve, D, zero), D):
                return False, "identity law failed (right)"
            if not cantor.eq(cantor.add(curve, zero, D), D):
                return False, "identity law failed (left)"
            if not cantor.eq(cantor.add(curve, D, cantor.negate(curve, D)), zero):
                return False, "inverse law failed"

        for (D1, D2) in _cancellation_pairs(tset, n_targeted, strategy, cap, rng):
            S = cantor.add(curve, D1, D2, verify=True)
            why = cantor.check_divisor(curve, S)
            if why is not None:
                return False, "closure failed: %s" % why
            if not cantor.eq(S, cantor.add(curve, D2, D1)):
                return False, "commutativity failed"
            if not cantor.eq(cantor.add(curve, S, cantor.negate(curve, D2)), D1):
                return False, "cancellation failed"

        # associativity on random triples
        for _ in range(triples):
            D1, D2, D3 = (rng.choice(tset) for _ in range(3))
            L = cantor.add(curve, cantor.add(curve, D1, D2), D3)
            R = cantor.add(curve, D1, cantor.add(curve, D2, D3))
            if not cantor.eq(L, R):
                return False, "associativity failed"
        return True, "ok"
    except (ExactQuotientError, ArithmeticError, ZeroDivisionError,
            CurveRejected, AssertionError) as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)


def random_valid_curve(F, kind, rng=random, max_attempts=400, stats=None,
                       require_smooth=True, always_validate=False,
                       level=None, genus=3, model="ramified", normal_form=False,
                       infinity_y=None, force_hlead=None, basis="neg", **kw):
    """Sample candidate curves until one passes `validate_curve`.

    Acceptance is empirical: a curve is kept only when reference.py demonstrably
    forms a group on it.  `require_smooth` additionally *rejects* curves that
    `singularity_diagnostic` calls singular.  That can only ever discard extra
    curves -- it is never used to accept one -- so it cannot make the harness
    unsound, and it matters because the empirical test provably cannot detect a
    singularity supported at a place of degree >= 2 (see selftest output).

    `stats` (optional dict) accumulates attempts / rejections split by whether
    the diagnostic called the curve singular, so the two filters can be
    cross-tabulated.

    Curve-shape arguments -- genus, model and the split-model infinity controls --
    are named explicitly and forwarded to `random_curve`. They used to fall into
    `**kw`, which is forwarded to `validate_curve` instead, so `genus=3` raised
    TypeError and the generator call was a bare `random_curve(F, kind, rng)`: this
    function could only ever produce genus-3 ramified curves whatever it was asked
    for. Remaining `**kw` still goes to the validator, which is where n_pairs and
    friends belong.

    For `model="split"` the split validator is used, with `basis` selecting the
    reduced basis. Routing a split curve through `validate_curve` would reject every
    one of them: it draws divisors up to degree g+1, which the split model allows,
    and then judges them with the ramified check that caps deg u at g.
    """
    if level is None:
        # without the diagnostic filter the group test is the only guard, so
        # use the high-power sweep; with it, a cheap screen suffices.
        level = "fast" if require_smooth else "standard"
    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        c = random_curve(F, kind, rng, genus=genus, model=model,
                         normal_form=normal_form, infinity_y=infinity_y,
                         force_hlead=force_hlead)
        sing = singularity_diagnostic(c)
        if sing and require_smooth and not always_validate:
            ok, why = False, "diagnostic: singular"
        else:
            # require_smooth=False here on purpose: the diagnostic is applied by
            # this function, both above and below, and `always_validate` exists so
            # the group test can still run on a curve the diagnostic rejected. If
            # validate_curve applied it too, that cross-tabulation would be
            # impossible and `always_validate` would silently do nothing.
            if model == "split":
                try:
                    V = split_basis(c, basis)
                except ArithmeticError as exc:
                    ok, why = False, "no split basis: %s" % exc
                else:
                    ok, why = validate_split_curve(
                        c, V, rng, positive=(basis == "pos"),
                        require_smooth=False, **kw)
            else:
                ok, why = validate_curve(c, rng, level=level,
                                         require_smooth=False, **kw)
            if ok and sing and require_smooth:
                ok, why = False, "diagnostic: singular"
        if stats is not None:
            stats["attempts"] = stats.get("attempts", 0) + 1
            stats.setdefault("reasons", {})
            stats["singular_diag"] = stats.get("singular_diag", 0) + int(sing)
            if not ok:
                stats["rejected"] = stats.get("rejected", 0) + 1
                key = why.split(":")[0]
                stats["reasons"][key] = stats["reasons"].get(key, 0) + 1
                if key != "diagnostic":
                    stats["rejected_by_group_test"] = \
                        stats.get("rejected_by_group_test", 0) + 1
                    stats["group_reject_sing" if sing else "group_reject_smooth"] = \
                        stats.get("group_reject_sing" if sing else
                                  "group_reject_smooth", 0) + 1
            else:
                stats["accepted"] = stats.get("accepted", 0) + 1
        if ok:
            return c
    raise CurveRejected("no valid %s curve over %r after %d attempts"
                        % (kind, F, max_attempts))


# ---------------------------------------------------------------------------
# split-model divisors
# ---------------------------------------------------------------------------

def split_basis(curve, basis):
    """Vp for the positive reduced basis, Vn for the negative one.

    `basis` is "pos" or "neg", which is how the repository splits the directories.
    Raises ArithmeticError, via compute_vp, for a curve whose places at infinity
    are conjugate or coincide -- neither is a split curve over its own field.
    """
    vp = cantor.compute_vp(curve)
    return vp if basis == "pos" else cantor.compute_vn(curve, vp)


def to_split_divisor(curve, D, V, rng=random, n=None):
    """Lift a (u, v) pair to a balanced divisor (u, v, w, n) in the basis V.

    The prime-divisor and CRT machinery above is model-independent -- it only ever
    uses f and h -- so the same generators, and in particular the same careful
    PAIR_MODES gcd structures, serve the split model. What has to be added is the
    balancing weight and the change of basis.

    The weight is drawn from [0, g - deg u], which is what
    reference.split_check_divisor enforces. Note this is why deg u is capped at g
    rather than the g+1 that max_divisor_degree allows: at deg u = g+1 the range is
    empty and no valid weight exists.
    """
    u, v = D[0], D[1]
    w = (curve.f - v * (v + curve.h)).exact_quotient(u)
    room = curve.genus - u.deg
    if room < 0:
        return None
    if n is None:
        n = rng.randint(0, room)
    elif not 0 <= n <= room:
        return None
    return cantor.reduced_basis(curve, (u, v, w, n), V)


def random_split_divisor(curve, V, rng=random, degs=None):
    """A random reduced balanced divisor in the basis V."""
    if degs is None:
        degs = tuple(range(curve.genus + 1))
    D = random_divisor(curve, rng, degs=degs)
    return to_split_divisor(curve, D, V, rng)


# Cycled by the driver across repetitions. "random" appears every other slot on
# purpose: cycling the five modes equally left only one draw in five uniform, and
# that lost a genus-3 split DBL branch that needs a mid-range weight (55/55 down to
# 54/55) while gaining ADD branches. Half uniform, half endpoints keeps both.
WEIGHT_MODES = ("random", "min", "random", "max", "random", "mixed",
                "random", "mixed_rev")


def _weight_for(curve, D, which, rng):
    """A balancing weight for D, drawn as `which` prescribes.

    The legal range is [0, g - deg u]. Drawing it uniformly leaves the endpoints
    thinly sampled, and the endpoints are what the reduce and adjust branches key
    on -- the genus-3 split ADD files carry 350 labelled branches and a uniform
    weight reached only about four fifths of them. `min` and `max` pin the weight to
    each end of the range on purpose.
    """
    room = curve.genus - D[0].deg
    if room < 0:
        return None
    if which == "min":
        return 0
    if which == "max":
        return room
    return rng.randint(0, room)


def random_split_divisor_pair(curve, V, rng=random, mode="generic",
                              weights="random"):
    """A balanced-divisor pair, reusing the ramified pair modes verbatim.

    `weights` additionally controls the two balancing weights: "random" each,
    "min"/"max" both pinned to an end of their legal range, and "mixed"/"mixed_rev"
    one of each. The gcd structure comes from the ramified pair modes, which the
    split model shares because they depend only on f and h.

    Returns None when the underlying pair cannot be built or when either divisor has
    deg u > g, so a caller counts the skip rather than seeing a silent retry.
    """
    degs = tuple(range(curve.genus + 1))
    pair = random_divisor_pair(curve, rng, mode=mode, degs=degs)
    if not pair:
        return None
    D1, D2 = pair
    if weights == "mixed":
        w1, w2 = "min", "max"
    elif weights == "mixed_rev":
        w1, w2 = "max", "min"
    else:
        w1 = w2 = weights
    n1 = _weight_for(curve, D1, w1, rng)
    n2 = _weight_for(curve, D2, w2, rng)
    if n1 is None or n2 is None:
        return None
    S1 = to_split_divisor(curve, D1, V, rng, n=n1)
    S2 = to_split_divisor(curve, D2, V, rng, n=n2)
    if S1 is None or S2 is None:
        return None
    return S1, S2


def validate_split_curve(curve, V, rng=random, n_divisors=8, n_pairs=10,
                         n_triples=4, positive=False, require_smooth=True):
    """Empirically test that reference.py forms a group on this split curve.

    The split analogue of validate_curve, and a separate function rather than a
    branch inside it because almost everything differs: divisors carry a balancing
    weight, validity is judged by split_check_divisor, the identity has weight
    ceil(g/2) rather than 0, and the group law needs the basis V.

    validate_curve cannot be reused as-is -- it draws divisors up to
    max_divisor_degree, which is g+1 for the split model, and then judges them with
    the ramified check_divisor, which caps deg u at g. Every split curve was
    rejected with "deg u = 3 > 2".

    Unlike validate_curve this ALSO rejects on the textbook criterion, because the
    empirical part is weaker here: there is no split negation implemented, so the
    inverse and cancellation laws are not among the checks, and singular curves
    survived. Measured before this: the ramified filter and the diagnostic agreed
    exactly, 176 accepted-and-smooth against 24 rejected-and-singular with no
    disagreement, while the split filter accepted 22 of 240 curves the diagnostic
    calls singular, spread evenly over every family at roughly the 1/q rate at which
    h^2 + 4f is genuinely not squarefree.

    Using the criterion to REJECT is safe in a way that using it to accept would not
    be: it can only shrink the tested domain, never admit a curve the group law
    fails on. And it is valid for both models, since `(2y+h)^2 = h^2 + 4f` makes the
    affine smoothness test independent of whether deg f is 2g+1 or 2g+2.

    Returns (ok, reason).
    """
    if require_smooth and singularity_diagnostic(curve):
        return False, "singular by the textbook criterion"
    try:
        zero = cantor.split_identity(curve, V)
        tset = []
        for _ in range(n_divisors * 6):
            if len(tset) >= n_divisors:
                break
            D = random_split_divisor(curve, V, rng)
            if D is not None:
                tset.append(D)
        if len(tset) < 3:
            return False, "could not build enough split divisors"
        for D in tset:
            why = cantor.split_check_divisor(curve, D, V)
            if why is not None:
                return False, "generated divisor invalid: %s" % why

        for D in tset:
            if not cantor.eq(cantor.split_add(curve, D, zero, V, positive), D):
                return False, "identity law failed (right)"
            if not cantor.eq(cantor.split_add(curve, zero, D, V, positive), D):
                return False, "identity law failed (left)"

        for _ in range(n_pairs):
            D1, D2 = rng.choice(tset), rng.choice(tset)
            S = cantor.split_add(curve, D1, D2, V, positive)
            why = cantor.split_check_divisor(curve, S, V)
            if why is not None:
                return False, "closure failed: %s" % why
            if not cantor.eq(S, cantor.split_add(curve, D2, D1, V, positive)):
                return False, "commutativity failed"

        for _ in range(n_triples):
            D1, D2, D3 = (rng.choice(tset) for _ in range(3))
            L = cantor.split_add(
                curve, cantor.split_add(curve, D1, D2, V, positive), D3, V, positive)
            R = cantor.split_add(
                curve, D1, cantor.split_add(curve, D2, D3, V, positive), V, positive)
            if not cantor.eq(L, R):
                return False, "associativity failed"
        return True, "ok"
    except (ExactQuotientError, ArithmeticError, ZeroDivisionError,
            CurveRejected, AssertionError) as exc:
        return False, "%s: %s" % (type(exc).__name__, exc)
