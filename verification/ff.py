"""
ff.py -- finite fields GF(p^n) for the genus-3 ramified-model audit harness.

Elements of GF(p^n) are represented as polynomials over GF(p) modulo a monic
irreducible polynomial of degree n that is found by exhaustive search (so the
construction is self-contained and needs no tables).

Design notes
------------
*   Elements are *interned*: for a given field there is at most one FFElement
    object per value, so `==` / `hash` are cheap and objects are shared.  Field
    orders in this harness are tiny (<= 32 in the colleague's testers), so the
    pool never gets large.
*   `int` interoperates with FFElement everywhere (0, 1, -1, 2, ... are the
    common cases), which lets poly.py and curve.py write `2*v + h` naturally in
    a characteristic-agnostic way.
*   No dependency on poly.py -- the small amount of GF(p)[x] arithmetic needed
    to build the field is implemented here on plain integer lists.
"""

from __future__ import annotations

import random

__all__ = ["FiniteField", "FFElement", "GF", "factor_prime_power"]


# ---------------------------------------------------------------------------
# helpers: prime-power factorisation and GF(p)[x] on little-endian int lists
# ---------------------------------------------------------------------------

def factor_prime_power(q: int):
    """Return (p, n) with q == p**n, p prime.  Raise if q is not a prime power."""
    if q < 2:
        raise ValueError("field order must be at least 2, got %r" % (q,))
    p = None
    for cand in range(2, q + 1):
        if q % cand == 0:
            p = cand
            break
    m, n = q, 0
    while m % p == 0:
        m //= p
        n += 1
    if m != 1:
        raise ValueError("%d is not a prime power" % q)
    return p, n


def _pnorm(a, p):
    a = [x % p for x in a]
    while a and a[-1] == 0:
        a.pop()
    return a


def _pmul(a, b, p):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    out[i + j] += ai * bj
    return _pnorm(out, p)


def _pdivmod(a, b, p):
    """Divide a by b in GF(p)[x]; a, b normalised little-endian int lists."""
    if not b:
        raise ZeroDivisionError("division by zero polynomial")
    a = list(a)
    db, inv = len(b) - 1, pow(b[-1], -1, p)
    q = [0] * max(0, len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = (a[i] * inv) % p
        if c:
            q[i - db] = c
            for j in range(db + 1):
                a[i - db + j] = (a[i - db + j] - c * b[j]) % p
    return _pnorm(q, p), _pnorm(a, p)


def _pxgcd(a, b, p):
    """Extended gcd in GF(p)[x].  Returns (g, s, t) with g == s*a + t*b, g monic."""
    r0, r1 = _pnorm(list(a), p), _pnorm(list(b), p)
    s0, s1 = [1], []
    t0, t1 = [], [1]
    while r1:
        q, r = _pdivmod(r0, r1, p)
        r0, r1 = r1, r
        s0, s1 = s1, _pnorm([x - y for x, y in _zip_pad(s0, _pmul(q, s1, p))], p)
        t0, t1 = t1, _pnorm([x - y for x, y in _zip_pad(t0, _pmul(q, t1, p))], p)
    if r0:
        inv = pow(r0[-1], -1, p)
        r0 = _pnorm([x * inv for x in r0], p)
        s0 = _pnorm([x * inv for x in s0], p)
        t0 = _pnorm([x * inv for x in t0], p)
    return r0, s0, t0


def _zip_pad(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0, b[i] if i < len(b) else 0) for i in range(n)]


def _monic_polys_of_degree(d, p):
    """Iterate over all monic degree-d polynomials in GF(p)[x] (little-endian)."""
    lows = [0] * d
    while True:
        yield lows + [1]
        i = 0
        while i < d:
            lows[i] += 1
            if lows[i] < p:
                break
            lows[i] = 0
            i += 1
        if i == d:
            return


def _is_irreducible(poly, p):
    """Trial-division irreducibility test for poly monic of degree n over GF(p).

    A degree-n polynomial is reducible iff it has a factor of degree <= n/2,
    hence iff it is divisible by *some* monic polynomial of degree 1..n//2.
    Exhaustive trial division is therefore a complete test.  Cost is ~p^(n/2),
    which is negligible for the field orders used here.
    """
    n = len(poly) - 1
    if n <= 1:
        return n == 1
    budget = sum(p ** d for d in range(1, n // 2 + 1))
    if budget > 500000:
        raise ValueError("irreducibility search too large for GF(%d^%d)" % (p, n))
    for d in range(1, n // 2 + 1):
        for g in _monic_polys_of_degree(d, p):
            _, rem = _pdivmod(poly, g, p)
            if not rem:
                return False
    return True


# Magma's own defining polynomials, ascending coefficients, for the extension fields
# this repository's testers actually use. Queried from Magma directly rather than
# assumed -- `DefiningPolynomial(GF(q))` under tools/magma-docker/.
#
# Matching matters because the whitebox testers write extension-field elements as
# `FF.1^k`, powers of Magma's generator. Any irreducible gives an isomorphic field, so
# a case stays a valid test either way, but the curve it names is only the intended one
# when the generator agrees. The search order below already agrees for GF(4), GF(8),
# GF(16), GF(27) and GF(32); it did not for GF(9) or GF(25), and that mismatch
# reproduced as two wrong constructed cases over GF(9).
MAGMA_MODULI = {
    (2, 2): [1, 1, 1],              # x^2 + x + 1
    (2, 3): [1, 1, 0, 1],           # x^3 + x + 1
    (2, 4): [1, 1, 0, 0, 1],        # x^4 + x + 1
    (2, 5): [1, 0, 1, 0, 0, 1],     # x^5 + x^2 + 1
    (3, 2): [2, 2, 1],              # x^2 + 2x + 2
    (3, 3): [1, 2, 0, 1],           # x^3 + 2x + 1
    (5, 2): [2, 4, 1],              # x^2 + 4x + 2
}


def _find_irreducible(p, n):
    """Magma's monic irreducible of degree n over GF(p) where known, else the
    smallest in the search order."""
    if (p, n) in MAGMA_MODULI:
        return list(MAGMA_MODULI[(p, n)])
    if n == 1:
        return [0, 1]
    for cand in _monic_polys_of_degree(n, p):
        if _is_irreducible(cand, p):
            return cand
    raise AssertionError("no irreducible polynomial found for GF(%d^%d)" % (p, n))


# ---------------------------------------------------------------------------
# field elements
# ---------------------------------------------------------------------------

class FFElement:
    """An element of GF(p^n), stored as an n-tuple of GF(p) coefficients."""

    __slots__ = ("F", "c")

    def __init__(self, F, c):
        self.F = F
        self.c = c

    # -- coercion ----------------------------------------------------------
    def _coerce(self, other):
        if isinstance(other, FFElement):
            if other.F is not self.F:
                raise TypeError("mixing elements of %r and %r" % (self.F, other.F))
            return other
        if isinstance(other, int):
            return self.F(other)
        return None

    # -- arithmetic --------------------------------------------------------
    def __add__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        F, p = self.F, self.F.p
        return F.make(tuple((a + b) % p for a, b in zip(self.c, o.c)))

    __radd__ = __add__

    def __neg__(self):
        F, p = self.F, self.F.p
        return F.make(tuple((-a) % p for a in self.c))

    def __sub__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        F, p = self.F, self.F.p
        return F.make(tuple((a - b) % p for a, b in zip(self.c, o.c)))

    def __rsub__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        return o - self

    def __mul__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        F = self.F
        p, n = F.p, F.n
        a, b = self.c, o.c
        if n == 1:
            return F.make(((a[0] * b[0]) % p,))
        prod = [0] * (2 * n - 1)
        for i, ai in enumerate(a):
            if ai:
                for j, bj in enumerate(b):
                    if bj:
                        prod[i + j] += ai * bj
        res = [prod[i] % p for i in range(n)]
        red = F._red
        for k in range(2 * n - 2, n - 1, -1):
            ck = prod[k] % p
            if ck:
                rk = red[k]
                for i in range(n):
                    res[i] = (res[i] + ck * rk[i]) % p
        return F.make(tuple(res))

    __rmul__ = __mul__

    def inverse(self):
        F = self.F
        if self.is_zero():
            raise ZeroDivisionError("inverse of zero in %r" % (F,))
        if F.n == 1:
            return F.make((pow(self.c[0], -1, F.p),))
        g, s, _ = _pxgcd(list(self.c), list(F.modulus), F.p)
        assert g == [1], "modulus not irreducible?"
        s = list(s) + [0] * (F.n - len(s))
        return F.make(tuple(s[: F.n]))

    def __truediv__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        return self * o.inverse()

    def __rtruediv__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        return o * self.inverse()

    def __pow__(self, e):
        if e < 0:
            return self.inverse() ** (-e)
        r, b = self.F.one, self
        while e:
            if e & 1:
                r = r * b
            b = b * b
            e >>= 1
        return r

    # -- predicates / conversion ------------------------------------------
    def is_zero(self):
        return not any(self.c)

    def is_one(self):
        return self.c == self.F.one.c

    def __bool__(self):
        return any(self.c)

    def __eq__(self, other):
        if isinstance(other, FFElement):
            return self is other or (self.F is other.F and self.c == other.c)
        if isinstance(other, int):
            return self.c == self.F(other).c
        return NotImplemented

    def __hash__(self):
        return hash((self.F.q, self.c))

    def __repr__(self):
        F = self.F
        if F.n == 1:
            return str(self.c[0])
        terms = []
        for i in range(F.n - 1, -1, -1):
            if self.c[i]:
                if i == 0:
                    terms.append(str(self.c[i]))
                elif self.c[i] == 1:
                    terms.append("t" if i == 1 else "t^%d" % i)
                else:
                    terms.append("%d*%s" % (self.c[i], "t" if i == 1 else "t^%d" % i))
        return "+".join(terms) if terms else "0"


# ---------------------------------------------------------------------------
# the field
# ---------------------------------------------------------------------------

class FiniteField:
    """GF(q) with q = p^n, realised as GF(p)[t]/(modulus)."""

    _cache = {}

    def __new__(cls, q):
        if q in cls._cache:
            return cls._cache[q]
        self = super().__new__(cls)
        self.q = q
        self.p, self.n = factor_prime_power(q)
        self.modulus = tuple(_find_irreducible(self.p, self.n))
        self._pool = {}
        self._red = self._reduction_table()
        self.zero = self.make(tuple([0] * self.n))
        self.one = self.make(tuple([1] + [0] * (self.n - 1)))
        self._all = None
        cls._cache[q] = self
        return self

    # -- construction ------------------------------------------------------
    def _reduction_table(self):
        p, n, m = self.p, self.n, self.modulus
        red = {}
        if n == 1:
            return red
        cur = [(-m[i]) % p for i in range(n)]          # t^n mod modulus
        red[n] = tuple(cur)
        for k in range(n + 1, 2 * n - 1):
            new = [0] * (n + 1)
            for i in range(n):
                new[i + 1] = cur[i]
            top, new = new[n], new[:n]
            if top:
                rn = red[n]
                for i in range(n):
                    new[i] = (new[i] + top * rn[i]) % p
            cur = new
            red[k] = tuple(cur)
        return red

    def make(self, c):
        """Intern and return the element with coefficient tuple `c`."""
        e = self._pool.get(c)
        if e is None:
            e = FFElement(self, c)
            self._pool[c] = e
        return e

    def __call__(self, v):
        """Coerce int / tuple / list / FFElement into this field."""
        if isinstance(v, FFElement):
            if v.F is self:
                return v
            raise TypeError("cannot coerce element of %r into %r" % (v.F, self))
        if isinstance(v, int):
            return self.make(tuple([v % self.p] + [0] * (self.n - 1)))
        if isinstance(v, (tuple, list)):
            c = [x % self.p for x in v] + [0] * (self.n - len(v))
            if len(c) > self.n:
                raise ValueError("too many coefficients for %r" % (self,))
            return self.make(tuple(c))
        raise TypeError("cannot coerce %r into %r" % (v, self))

    # -- enumeration / sampling -------------------------------------------
    def elements(self):
        if self._all is None:
            out, n, p = [], self.n, self.p
            idx = [0] * n
            while True:
                out.append(self.make(tuple(idx)))
                i = 0
                while i < n:
                    idx[i] += 1
                    if idx[i] < p:
                        break
                    idx[i] = 0
                    i += 1
                if i == n:
                    break
            self._all = out
        return self._all

    def random(self, rng=random):
        return rng.choice(self.elements())

    def gen(self):
        """A generator of the field as GF(p)-algebra (t), or 1 when n == 1."""
        if self.n == 1:
            return self.one
        return self.make(tuple([0, 1] + [0] * (self.n - 2)))

    @property
    def char(self):
        return self.p

    def __repr__(self):
        return "GF(%d)" % self.q if self.n == 1 else "GF(%d^%d)" % (self.p, self.n)


def GF(q):
    return FiniteField(q)
