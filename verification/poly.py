"""
poly.py -- dense univariate polynomials over a finite field from ff.py.

Conventions chosen to match Magma, because the whole point of the harness is to
mirror Magma code faithfully:

*   `deg` of the zero polynomial is -1 (Magma's `Degree(0)`).
*   `gcd` and `xgcd` return a **monic** gcd (Magma's `GCD` / `XGCD` normalise).
*   `xgcd(a, b)` returns `(g, s, t)` with `g == s*a + t*b`, matching Magma's
    `S, a1, b1 := XGCD(ub, ua)` argument order.
*   `divmod(a, b)` matches Magma's `Quotrem(a, b)`: `a == q*b + r`, `deg r < deg b`.
*   `exact_quotient` is Magma's `ExactQuotient`: it *asserts* a zero remainder.
"""

from __future__ import annotations

from ff import FFElement, FiniteField

__all__ = ["Poly"]


class Poly:
    """A polynomial with coefficients in a FiniteField, little-endian."""

    __slots__ = ("F", "c")

    # -- construction ------------------------------------------------------
    def __init__(self, F, coeffs=()):
        self.F = F
        c = [F(x) for x in coeffs]
        while c and c[-1].is_zero():
            c.pop()
        self.c = tuple(c)

    @classmethod
    def _raw(cls, F, c):
        """Build from an already-normalised tuple of FFElements (no copying)."""
        obj = cls.__new__(cls)
        obj.F = F
        obj.c = c
        return obj

    @staticmethod
    def _norm(F, c):
        while c and c[-1].is_zero():
            c.pop()
        return Poly._raw(F, tuple(c))

    @classmethod
    def zero(cls, F):
        return cls._raw(F, ())

    @classmethod
    def one(cls, F):
        return cls._raw(F, (F.one,))

    @classmethod
    def x(cls, F):
        return cls._raw(F, (F.zero, F.one))

    @classmethod
    def const(cls, F, a):
        a = F(a)
        return cls._raw(F, () if a.is_zero() else (a,))

    @classmethod
    def from_coeffs(cls, F, coeffs):
        """coeffs little-endian (ints or FFElements)."""
        return cls(F, coeffs)

    @classmethod
    def from_coeffs_desc(cls, F, coeffs):
        """coeffs big-endian, e.g. from_coeffs_desc(F, [1,0,0,3]) == x^3 + 3."""
        return cls(F, list(reversed(list(coeffs))))

    # -- basics ------------------------------------------------------------
    @property
    def deg(self):
        return len(self.c) - 1

    def degree(self):
        return len(self.c) - 1

    def is_zero(self):
        return not self.c

    def is_one(self):
        return len(self.c) == 1 and self.c[0].is_one()

    def __bool__(self):
        return bool(self.c)

    def lc(self):
        """Leading coefficient; zero for the zero polynomial."""
        return self.c[-1] if self.c else self.F.zero

    def coeff(self, i):
        """Magma's Coeff(f, i)."""
        return self.c[i] if 0 <= i < len(self.c) else self.F.zero

    def coeffs_up_to(self, n):
        """[c0, c1, ..., cn] as FFElements, zero-padded."""
        return [self.coeff(i) for i in range(n + 1)]

    def is_monic(self):
        return bool(self.c) and self.c[-1].is_one()

    def monic(self):
        if not self.c:
            raise ZeroDivisionError("cannot normalise the zero polynomial")
        if self.c[-1].is_one():
            return self
        inv = self.c[-1].inverse()
        return Poly._raw(self.F, tuple(a * inv for a in self.c))

    # -- coercion ----------------------------------------------------------
    def _coerce(self, other):
        if isinstance(other, Poly):
            if other.F is not self.F:
                raise TypeError("mixing polynomials over %r and %r" % (self.F, other.F))
            return other
        if isinstance(other, (int, FFElement)):
            return Poly.const(self.F, other)
        return None

    # -- arithmetic --------------------------------------------------------
    def __add__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        a, b = self.c, o.c
        if len(a) < len(b):
            a, b = b, a
        out = list(a)
        for i, bi in enumerate(b):
            out[i] = out[i] + bi
        return Poly._norm(self.F, out)

    __radd__ = __add__

    def __neg__(self):
        return Poly._raw(self.F, tuple(-a for a in self.c))

    def __sub__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        n = max(len(self.c), len(o.c))
        Z = self.F.zero
        out = [(self.c[i] if i < len(self.c) else Z) - (o.c[i] if i < len(o.c) else Z)
               for i in range(n)]
        return Poly._norm(self.F, out)

    def __rsub__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        return o - self

    def __mul__(self, other):
        o = self._coerce(other)
        if o is None:
            return NotImplemented
        a, b = self.c, o.c
        if not a or not b:
            return Poly.zero(self.F)
        Z = self.F.zero
        out = [Z] * (len(a) + len(b) - 1)
        for i, ai in enumerate(a):
            if ai:
                for j, bj in enumerate(b):
                    if bj:
                        out[i + j] = out[i + j] + ai * bj
        return Poly._norm(self.F, out)

    __rmul__ = __mul__

    def __pow__(self, e):
        if e < 0:
            raise ValueError("negative polynomial power")
        r, b = Poly.one(self.F), self
        while e:
            if e & 1:
                r = r * b
            b = b * b
            e >>= 1
        return r

    def divmod(self, other):
        """(q, r) with self == q*other + r and deg(r) < deg(other)."""
        o = self._coerce(other)
        if o is None:
            raise TypeError("cannot divide by %r" % (other,))
        if not o.c:
            raise ZeroDivisionError("polynomial division by zero")
        db = o.deg
        if self.deg < db:
            return Poly.zero(self.F), self
        rem = list(self.c)
        inv = o.c[-1].inverse()
        Z = self.F.zero
        quo = [Z] * (self.deg - db + 1)
        for i in range(self.deg, db - 1, -1):
            ci = rem[i]
            if ci:
                t = ci * inv
                quo[i - db] = t
                for j in range(db + 1):
                    rem[i - db + j] = rem[i - db + j] - t * o.c[j]
        return Poly._norm(self.F, quo), Poly._norm(self.F, rem)

    def __divmod__(self, other):
        return self.divmod(other)

    def __floordiv__(self, other):
        return self.divmod(other)[0]

    def __mod__(self, other):
        return self.divmod(other)[1]

    def __truediv__(self, other):
        """Division by a nonzero *scalar* only (Magma's `u/LeadingCoefficient(u)`)."""
        if isinstance(other, Poly):
            if other.deg == 0:
                other = other.c[0]
            else:
                raise TypeError("Poly/Poly is ambiguous; use exact_quotient or //")
        if isinstance(other, int):
            other = self.F(other)
        inv = other.inverse()
        return Poly._raw(self.F, tuple(a * inv for a in self.c))

    def exact_quotient(self, other):
        """Magma's ExactQuotient: quotient, asserting the remainder is zero."""
        q, r = self.divmod(other)
        if r.c:
            raise ExactQuotientError(
                "inexact division: (%s) / (%s) leaves remainder %s" % (self, other, r))
        return q

    def mod(self, other):
        return self.divmod(other)[1]

    # -- gcd ---------------------------------------------------------------
    def gcd(self, other):
        o = self._coerce(other)
        a, b = self, o
        while b.c:
            a, b = b, a.divmod(b)[1]
        return a.monic() if a.c else a

    def xgcd(self, other):
        """(g, s, t) with g == s*self + t*other, g monic (Magma XGCD order)."""
        o = self._coerce(other)
        F = self.F
        r0, r1 = self, o
        s0, s1 = Poly.one(F), Poly.zero(F)
        t0, t1 = Poly.zero(F), Poly.one(F)
        while r1.c:
            q, r = r0.divmod(r1)
            r0, r1 = r1, r
            s0, s1 = s1, s0 - q * s1
            t0, t1 = t1, t0 - q * t1
        if r0.c:
            inv = r0.c[-1].inverse()
            r0 = Poly._raw(F, tuple(a * inv for a in r0.c))
            s0 = Poly._raw(F, tuple(a * inv for a in s0.c))
            t0 = Poly._raw(F, tuple(a * inv for a in t0.c))
        return r0, s0, t0

    def inverse_mod(self, m):
        g, s, _ = self.xgcd(m)
        if not g.is_one():
            raise ZeroDivisionError("not invertible: gcd = %s" % (g,))
        return s.divmod(m)[1]

    # -- evaluation / misc -------------------------------------------------
    def eval(self, a):
        F = self.F
        a = F(a) if not isinstance(a, FFElement) else a
        acc = F.zero
        for ci in reversed(self.c):
            acc = acc * a + ci
        return acc

    def __call__(self, a):
        return self.eval(a)

    def derivative(self):
        F = self.F
        out = [F(i) * self.c[i] for i in range(1, len(self.c))]
        return Poly._norm(F, out)

    def powmod(self, e, m):
        """self**e mod m, by square-and-multiply (e a non-negative int)."""
        r = Poly.one(self.F).divmod(m)[1]
        b = self.divmod(m)[1]
        while e:
            if e & 1:
                r = (r * b).divmod(m)[1]
            b = (b * b).divmod(m)[1]
            e >>= 1
        return r

    def is_squarefree(self):
        if self.deg <= 0:
            return True
        d = self.derivative()
        if d.is_zero():
            return False
        return self.gcd(d).deg == 0

    # -- comparison / display ---------------------------------------------
    def __eq__(self, other):
        o = self._coerce(other) if not isinstance(other, Poly) else other
        if o is None:
            return NotImplemented
        return self.c == o.c

    def __hash__(self):
        return hash((self.F.q, self.c))

    def __repr__(self):
        if not self.c:
            return "0"
        parts = []
        for i in range(len(self.c) - 1, -1, -1):
            ci = self.c[i]
            if not ci:
                continue
            xs = "" if i == 0 else ("x" if i == 1 else "x^%d" % i)
            if i == 0:
                parts.append(repr(ci))
            elif ci.is_one():
                parts.append(xs)
            else:
                parts.append("%s*%s" % (repr(ci), xs))
        return " + ".join(parts)


class ExactQuotientError(ArithmeticError):
    """Raised where Magma's ExactQuotient would abort."""
