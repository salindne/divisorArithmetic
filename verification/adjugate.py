"""adjugate.py -- the genus-3 adjugate/determinant block: candidates verified,
counted, and bounded from below, with no third-party dependency.

    python3 adjugate.py                      # every section
    python3 adjugate.py --list               # candidates, fields, sections
    python3 adjugate.py --section table
    python3 adjugate.py --section bound --primes 2,3,5,7,11
    python3 adjugate.py --json
    python3 adjugate.py --verbose

WHAT THE BLOCK IS

`T` is the 3x3 matrix of multiplication by `w = u - up` modulo `up` (monic,
degree 3) in the basis {1,x,x^2}; `M = adj(T)`; `d = det(T) = Res(w,up)`. The six
runtime inputs are `t1,t4,t7,up0,up1,up2` with `t1 = u0-up0`, `t4 = u1-up1`,
`t7 = u2-up2` -- those three subtractions are paid before the block starts and
are not counted here, which is why a count of 9A appears against a fragment that
visibly performs twelve.

The naming is the files' own,

    | t1 t2 t3 |            | m1 m2 m3 |
    | t4 t5 t6 |     M =    | m4 m5 m6 |     d = t1*m1 + t4*m2 + t7*m3
    | t7 t8 t9 |            | m7 m8 m9 |

and the cofactor definitions are not written down in this module. They are parsed
out of the `//| m1= t5*t9-t8*t6, ... |` comment block that the genus-3 formula
files carry -- however many that is on the day; the `source` section discovers
them and prints the count, and this line deliberately does not repeat a number
that would go stale. At the time of writing it was nine.
They are required to agree with an independent construction built here from the
mathematics (multiply by `w`, reduce mod `up`, take the adjugate by 2x2 minors).
Same principle as `opcount.directives` and `driver.read_support`: a table in this
file would keep agreeing with itself after the source changed. `d` is checked
against the 5x5 Sylvester resultant of `w` and `up` as well, so the comment's
claim that the determinant *is* the resultant is measured rather than repeated.

WHY IT EXISTS

The measurements behind NEW_WORK N26 were made in about 140 one-off scratch
scripts outside the repository, several of them importing sympy, so none of the
numbers could be reproduced from a checkout and a reviewer marked them
unverifiable. Everything here is recomputed from scratch: no sympy, no numpy,
standard library only, and exact -- `fractions.Fraction` where a rational is
needed, and a hand-rolled sparse multivariate polynomial where an identity is
needed.

WHAT IT ESTABLISHES

  source   Every discovered cofactor comment block, parsed, agrees with the
           others and with the independent adjugate; `d = Res(w,up)`. The number
           of files is counted at run time and printed, not asserted here.
  table    Ten candidate programs, executed over 16 fields (7 of characteristic
           2, primes up to 10^6) and once symbolically over Q, with M/S/A counted
           on the repository's conventions and scored in the thesis's 1M:3A
           equivalent additions. Each row also states how many of the thirteen
           values it delivers, because a program that returns fewer of them is
           not competing with one that returns more.
  region   The two whole-region variants -- the shipped 27M 0S 17A that
           `arb_ramifiedG3_ADD.mag` annotates `// total:`, and the rank-5
           26M 0S 22A -- so the trade that was refused is visible as two numbers.
  span     The nine entries as quadratic forms in (t1,t4,t7): the span's exact
           dimension over Q(up0,up1,up2), at up -> 0, and over small prime
           fields.
  bound    A lower bound of 4 on the number of t-by-t products, at the up -> 0
           specialisation, by exhaustive enumeration in small characteristic and
           by an exact Hessian computation elsewhere.
  mag      The three shipped fragments' real statement text, extracted from the
           .mag between two anchors and executed through `maginterp.py`, priced on
           the same cost model `opcount.py` uses. Its counts and its values are
           required to equal the transcriptions'. This is what makes those three
           rows measurements of the source rather than of a retyping.
  rank     The bottom row (m7,m8,m9) is a cross product; its tensor admits no
           rank-4 decomposition over GF(2), GF(3), GF(5) (exhaustive), and a
           rank-5 one is exhibited. So 5 bilinear products is the floor for that
           row and the shipped code spends 6.

WHAT IT DOES **NOT** COVER, PLAINLY

  * The bound is a bound on **products of two t-linear forms in the up -> 0
    specialisation**. It is not a bound on the whole program. The shipped block
    spends 16 multiplications, of which 6 are t-by-t and 4 survive up -> 0; the
    bound says 4 of those 16 are necessary and says nothing whatever about the
    other 12. Anyone reading "16M is optimal" out of this is reading something
    that is not here.

  * The rank-4 impossibility is a statement about the **bilinear** complexity of
    the cross product, i.e. about programs that treat column 1 and column 2 of T
    as independent inputs. In the real block column 2 is a function of column 1
    and of up, so a program is free to exploit that, and 5 is therefore a floor
    only inside the stated model. It is exhaustive over GF(2), GF(3), GF(5) and
    is not proved over Q -- a rational rank-4 decomposition would have to have a
    common denominator divisible by 2, 3 and 5 to survive all three refutations.

  * Op counts are static counts of a straight-line fragment. They are not the
    published table rows and they do not include the inversion.

    The transcription gap is closed for the three shipped rows and only for those.
    The `mag` section extracts the block's real statement text from the .mag file
    between two anchors, executes it through `maginterp.py` over GF(p) -- the same
    interpreter and the same cost model `opcount.py` uses -- and requires the
    result to equal the transcription's count AND the reference values. So for
    `shipped_7`, `shipped_7_dbl` and `split_q` the count is measured on the source
    rather than on a retyping of it. `shipped_9`, the two `region` rows, the
    `row3` pair and every rank-5 variant are NOT covered that way: `shipped_9` and
    the regions span code either side of the `d eq 0` guard and the rest exist
    nowhere in the repository. Those remain transcriptions, tied to the source
    only by their values agreeing with the parsed cofactor definitions and, for
    the regions, by the file's own `// total: 27m 0s 17a` comment. A transcription
    error preserving both values and count would still survive there.

  * The third route the files discuss -- `arb_ramifiedG3_DBL.mag` prices it at
    `11m 20a`, first column only and then Karatsuba twice -- is
    **not measured here**, and the `region` section says so in its output. It
    exists nowhere in the repository as code, so building it would mean
    inventing it; the `26M 0S 22A` row is the rank-5 adjugate route and is not
    that one.

  * Nothing under `g3/` or `g2/` is written. The formula files are opened
    read-only.

NO .mag LINE NUMBERS ARE QUOTED

Anchor text is, and deliberately: the genus-3 addition files are under active
edit, and every line number this module first quoted had moved by the time it was
finished. Thesis line numbers are quoted, since those files are stable.

The `mag` section does print .mag line numbers, but it *found* them from the
anchors at run time and prints them only to say where it read; nothing is looked
up by line number and nothing goes stale. A moved anchor is reported as
`located NO`, not silently skipped.

CONVENTIONS, AND WHERE THEY COME FROM

`chapter6.tex:2323-2336` and `maginterp.py`: `+` and `-` cost 1A; a product of
two runtime values costs 1M; a unary minus is free, because it folds into the
sibling subtraction, which is exactly what `maginterp.py` does (`neg` bumps
nothing); multiplication or division by a literal small integer costs 1A
(`chapter6.tex:2333`, and halving is refused in characteristic 2). Squaring is
charged S when the two factors are the same object, which is a DELIBERATE
DIVERGENCE from `maginterp.py` and worth stating plainly: measured, `maginterp`
charges M for `x*x` and S only for `x^2`, because it sees source text and `x*x`
there might be two different reads. This module sees Python objects, so
`x * x` is a squaring and is charged S. It makes no difference to any figure
printed here -- every candidate has S = 0, none of them squares anything -- but it
means a candidate written with `x * x` would be priced 1S where the same line in a
.mag would be priced 1M, and the `mag` section, which does run through
`maginterp`, would then disagree and say so. Every candidate here
is a straight line, so its count is input-independent; that is not assumed, it is
checked on every trial and a count that moves is reported as a failure.

The thesis never trades 1M for more than 3A (`chapter4.tex:817`), so each row is
also scored `3*(M+S) + A` equivalent additions. S is priced as M there; every
candidate below has S = 0, so nothing in this file depends on that choice.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Where to look for the cofactor comment block. A glob, not a list of files: a
# file that grows one gets cross-checked, and one that loses it is reported.
FORMULA_DIRS = (
    os.path.join(ROOT, "g3", "ramifiedModel", "g3Formulas"),
    os.path.join(ROOT, "g3", "splitModel", "negReduced", "g3Formulas"),
)

# The nine input names, in the order every candidate takes them.
VARS = ("t1", "t4", "t7", "up0", "up1", "up2", "vt0", "vt1", "vt2")
NV = len(VARS)
TIDX = (0, 1, 2)                       # which of VARS are the t's
UPIDX = (3, 4, 5)


# ===========================================================================
# exact sparse multivariate polynomials over Q
# ===========================================================================

class Poly(object):
    """A polynomial as {exponent tuple: Fraction}, over any fixed variable count.

    Written out rather than imported because `verification/` has no third-party
    dependency and CI must need no install step. Only what is used below: ring
    operations, substitution of a variable to a constant, the homogeneous part in
    a chosen subset of the variables, and one partial derivative.
    """

    __slots__ = ("c", "n")

    def __init__(self, c, n):
        self.c = {m: v for m, v in c.items() if v}
        self.n = n

    # -- constructors -------------------------------------------------------
    @classmethod
    def zero(cls, n):
        return cls({}, n)

    @classmethod
    def const(cls, q, n):
        return cls({(0,) * n: Fraction(q)}, n)

    @classmethod
    def var(cls, i, n):
        e = [0] * n
        e[i] = 1
        return cls({tuple(e): Fraction(1)}, n)

    # -- ring ---------------------------------------------------------------
    def __add__(self, o):
        r = dict(self.c)
        for m, v in o.c.items():
            r[m] = r.get(m, Fraction(0)) + v
        return Poly(r, self.n)

    def __sub__(self, o):
        r = dict(self.c)
        for m, v in o.c.items():
            r[m] = r.get(m, Fraction(0)) - v
        return Poly(r, self.n)

    def __neg__(self):
        return Poly({m: -v for m, v in self.c.items()}, self.n)

    def __mul__(self, o):
        if isinstance(o, (int, Fraction)):
            return Poly({m: v * o for m, v in self.c.items()}, self.n)
        r = {}
        for ma, va in self.c.items():
            for mb, vb in o.c.items():
                k = tuple(x + y for x, y in zip(ma, mb))
                r[k] = r.get(k, Fraction(0)) + va * vb
        return Poly(r, self.n)

    __rmul__ = __mul__

    def __eq__(self, o):
        return isinstance(o, Poly) and self.c == o.c

    def __hash__(self):
        return hash(tuple(sorted(self.c.items())))

    def is_zero(self):
        return not self.c

    # -- the few analytic things needed -------------------------------------
    def at_zero(self, idxs):
        """This polynomial with every variable in `idxs` set to 0."""
        s = set(idxs)
        return Poly({m: v for m, v in self.c.items()
                     if not any(m[i] for i in s)}, self.n)

    def subs(self, values):
        """Substitute {index: Fraction} and return the result."""
        out = Poly.zero(self.n)
        for m, v in self.c.items():
            term = Poly({tuple(0 if i in values else e
                               for i, e in enumerate(m)): v}, self.n)
            for i, q in values.items():
                term = term * (Fraction(q) ** m[i])
            out = out + term
        return out

    def homog(self, idxs, deg):
        """The part of total degree `deg` in the variables `idxs`."""
        return Poly({m: v for m, v in self.c.items()
                     if sum(m[i] for i in idxs) == deg}, self.n)

    def diff(self, i):
        r = {}
        for m, v in self.c.items():
            if m[i]:
                k = list(m)
                k[i] -= 1
                r[tuple(k)] = v * m[i]
        return Poly(r, self.n)

    def is_integral(self):
        return all(v.denominator == 1 for v in self.c.values())

    def text(self, names):
        if not self.c:
            return "0"
        out = []
        for m in sorted(self.c, reverse=True):
            v = self.c[m]
            body = "*".join(("%s^%d" % (names[i], e)) if e > 1 else names[i]
                            for i, e in enumerate(m) if e)
            if not body:
                body = "1"
            elif v == 1:
                out.append(("+ " if out else "") + body)
                continue
            elif v == -1:
                out.append("- " + body if out else "-" + body)
                continue
            sign = "- " if v < 0 else ("+ " if out else "")
            out.append("%s%s*%s" % (sign, abs(v), body))
        return " ".join(out)


# ===========================================================================
# the independent construction: T, adj(T), det, Res(w, up)
# ===========================================================================

def _pv(i):
    return Poly.var(i, NV)


def build_T():
    """The matrix of multiplication by `w = t1 + t4 x + t7 x^2` modulo
    `up = x^3 + up2 x^2 + up1 x + up0`, in the basis {1, x, x^2}.

    Built from polynomial arithmetic, not from the files: this is the thing the
    files' comment block is checked *against*.
    """
    t1, t4, t7 = _pv(0), _pv(1), _pv(2)
    up0, up1, up2 = _pv(3), _pv(4), _pv(5)
    zero = Poly.zero(NV)
    w = [t1, t4, t7]                      # coefficients, low to high
    upc = [up0, up1, up2]                 # up = x^3 + up2 x^2 + up1 x + up0

    def reduce_mod_up(coeffs):
        """Reduce a coefficient list mod up, in place, top down."""
        c = list(coeffs)
        for deg in range(len(c) - 1, 2, -1):
            lead = c[deg]
            if lead.is_zero():
                continue
            c[deg] = zero
            for j in range(3):
                c[deg - 3 + j] = c[deg - 3 + j] - lead * upc[j]
        return c[:3]

    cols = []
    for shift in range(3):                # w * x^shift mod up
        raw = [zero] * (3 + shift)
        for i, a in enumerate(w):
            raw[i + shift] = raw[i + shift] + a
        cols.append(reduce_mod_up(raw + [zero]))
    # T[i][j] = coefficient of x^i in w*x^j mod up
    return [[cols[j][i] for j in range(3)] for i in range(3)]


def t_names_map(T):
    """{'t1': Poly, ..., 't9': Poly} in the files' own numbering."""
    return {"t%d" % (3 * i + j + 1): T[i][j] for i in range(3) for j in range(3)}


def adjugate(T):
    """adj(T) by 2x2 minors: M[i][j] = (-1)^(i+j) * minor(j, i)."""
    out = [[None] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            r = [x for x in range(3) if x != j]
            c = [x for x in range(3) if x != i]
            minor = (T[r[0]][c[0]] * T[r[1]][c[1]]
                     - T[r[0]][c[1]] * T[r[1]][c[0]])
            out[i][j] = minor if (i + j) % 2 == 0 else -minor
    return out


def det3(T):
    return (T[0][0] * (T[1][1] * T[2][2] - T[1][2] * T[2][1])
            - T[0][1] * (T[1][0] * T[2][2] - T[1][2] * T[2][0])
            + T[0][2] * (T[1][0] * T[2][1] - T[1][1] * T[2][0]))


def det_leibniz(A):
    """Determinant of a small square matrix over Poly, by the Leibniz sum.

    Division-free, so it is valid over the polynomial ring itself. Used only for
    the 5x5 Sylvester matrix -- 120 terms, which is cheaper than writing a
    fraction-free elimination that would then need its own test.
    """
    n = len(A)
    total = Poly.zero(A[0][0].n)
    for perm in itertools.permutations(range(n)):
        sign, seen = 1, list(perm)
        # parity by counting inversions
        inv = sum(1 for a in range(n) for b in range(a + 1, n)
                  if seen[a] > seen[b])
        if inv % 2:
            sign = -1
        term = Poly.const(sign, A[0][0].n)
        for i in range(n):
            term = term * A[i][perm[i]]
        total = total + term
    return total


def resultant_w_up():
    """Res(w, up) as the determinant of the 5x5 Sylvester matrix.

    w has degree 2 and up degree 3, so the Sylvester matrix is (2+3)x(2+3): three
    shifted rows of w and two shifted rows of up.
    """
    t1, t4, t7 = _pv(0), _pv(1), _pv(2)
    up0, up1, up2 = _pv(3), _pv(4), _pv(5)
    one, zero = Poly.const(1, NV), Poly.zero(NV)
    w = [t7, t4, t1]                       # high to low
    up = [one, up2, up1, up0]
    rows = []
    for s in range(3):                     # deg(up) = 3 rows of w
        rows.append([zero] * s + w + [zero] * (2 - s))
    for s in range(2):                     # deg(w) = 2 rows of up
        rows.append([zero] * s + up + [zero] * (1 - s))
    return det_leibniz(rows)


# ===========================================================================
# reading the cofactor block out of the formula files
# ===========================================================================

_BLOCK = re.compile(r"^\s*//\s*\|(.+)\|\s*$")
_ENTRY = re.compile(r"\b(m[1-9])\s*=\s*([^,|]+)")
_DETLINE = re.compile(r"^\s*(?:d|det)\s*:?=\s*([^;]+);")
# `// 16m 0s 9a`, `// top: 16m 0s 9a`, `// total: 27m 0s 17a (equivalent 98a)`
_ANNOT = re.compile(r"//\s*(top|total)?:?\s*(\d+)m\s+(\d+)s\s+(\d+)a")
# How far below the determinant an unlabelled ledger may sit, in a file that
# labels none of them. See all_annotations() for why this is conditional.
_ADJACENT = 3
# The doubling writes the first column as d0,d1,d2 and says so in comments.
ALIASES = {"d0": "t1", "d1": "t4", "d2": "t7"}


def _tokens(expr):
    return re.findall(r"[A-Za-z_]\w*|[*+\-()]", expr)


def parse_expr(expr, env):
    """Evaluate a sum of products of names against `env`. No precedence beyond
    `*` binding tighter than `+`/`-`, which is all these lines contain."""
    toks, pos = _tokens(expr), [0]

    def name():
        tok = toks[pos[0]]
        pos[0] += 1
        if tok not in env:
            raise ValueError("unknown name %r in %r" % (tok, expr.strip()))
        return env[tok]

    def factor():
        if toks[pos[0]] == "-":
            pos[0] += 1
            return -factor()
        if toks[pos[0]] == "(":
            pos[0] += 1
            v = summation()
            if pos[0] >= len(toks) or toks[pos[0]] != ")":
                raise ValueError("unbalanced ( in %r" % expr.strip())
            pos[0] += 1
            return v
        return name()

    def product():
        v = factor()
        while pos[0] < len(toks) and toks[pos[0]] == "*":
            pos[0] += 1
            v = v * factor()
        return v

    def summation():
        v = product()
        while pos[0] < len(toks) and toks[pos[0]] in "+-":
            op = toks[pos[0]]
            pos[0] += 1
            rhs = product()
            v = v + rhs if op == "+" else v - rhs
        return v

    v = summation()
    if pos[0] != len(toks):
        raise ValueError("trailing %r in %r" % (toks[pos[0]:], expr.strip()))
    return v


def formula_files():
    """Every .mag under the genus-3 formula directories, discovered."""
    out = []
    for d in FORMULA_DIRS:
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.endswith(".mag"):
                out.append(os.path.join(d, fn))
    return out


def read_cofactor_block(path, tvals):
    """({m1..m9: Poly}, det Poly or None, [annotations]) as one file declares it.

    `tvals` supplies t1..t9 from the independent construction, so what is read
    from the file is the *shape* of each cofactor, evaluated on values this
    module derived itself. Returns None if the file carries no block.
    """
    with open(path, encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    env = dict(tvals)
    for a, b in ALIASES.items():
        env[a] = tvals[b]
    # Two split files expand t3 inline in the determinant line, as `up0*t8`, so
    # the coefficient names have to be in scope as well as t1..t9.
    for i, nm in enumerate(VARS):
        env[nm] = _pv(i)

    got, first, last = {}, None, None
    for i, line in enumerate(lines):
        m = _BLOCK.match(line)
        if not m:
            continue
        found = _ENTRY.findall(m.group(1))
        if not found:
            continue
        if first is None:
            first = i
        last = i
        for name, body in found:
            got[name] = parse_expr(body, env)
    if not got:
        return None

    # the determinant, if the file forms it within reach of the block
    det = None
    denv = dict(env)
    denv.update(got)
    for i in range(last + 1, min(last + 40, len(lines))):
        m = _DETLINE.match(lines[i])
        if m and "m1" in m.group(1):
            det = parse_expr(m.group(1), denv)
            break

    annots = []
    for i in range(last, min(last + 40, len(lines))):
        m = _ANNOT.search(lines[i])
        if m:
            annots.append((m.group(1) or "block",
                           int(m.group(2)), int(m.group(3)), int(m.group(4))))
    return got, det, annots


def block_end_line(path):
    """Line index of the last `//| m1= ... |` line in a file, or None."""
    last = None
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh):
            m = _BLOCK.match(line)
            if m and _ENTRY.findall(m.group(1)):
                last = i
    return last


def all_annotations():
    """{(basename, label): (M,S,A)} -- the repository's own op-count comments.

    A labelled comment (`// top: 16m 0s 9a`, `// total: 27m 0s 17a`) is keyed by
    its label. An unlabelled one is keyed "block" and taken as the first
    unlabelled comment IMMEDIATELY AFTER the file's cofactor block, which is the
    only way to tell the doubling's `// 16m 0s 9a` (its adjugate block) from the
    `// 0m 0s 9a` above it (the `d = (2va+h) mod u` block, which is not this
    fragment at all). Parsed rather than tabulated, so a banner edited without
    re-measuring shows up here as a difference.

    THE UNLABELLED ONE IS BOUNDED TO THE FRAGMENT, and that is not fussiness.
    "First unlabelled comment after the block" used to mean *anywhere* after it,
    so deleting the ledger -- which happened three times during the 2026-08
    genus-3 work, because nothing in the file marks these comments as gate input
    (`ERRATA.md` E14) -- silently promoted the next unlabelled ledger 245 lines
    downstream into its place. The check then compared a 16m 0s 9a fragment
    against a 4m 0s 4a annotation and reported a difference that had nothing to do
    with the code. A missing ledger must read as missing, so `verify_annotations`
    can say so, rather than as a wrong number.

    Neither a fixed window nor "must precede the first guard" is the instrument.
    Both files carry SEVERAL legitimate inline ledgers, and what the unlabelled
    key means differs between them:

      * the doubling labels nothing, so its one unlabelled ledger sits on the
        determinant line and measures the cofactor fragment;
      * the addition labels that same fragment `top:`, so its first UNLABELLED
        ledger is the one below `sp0/sp1/sp2` and measures the lower half --
        575 lines below `block_end_line`, and correctly so.

    So the rule is conditioned on whether the file labels at all. A file that
    labels its ledgers has already said which is which. A file that does not must
    put its single ledger within `_ADJACENT` lines of the determinant, and if it
    is gone the key stays absent -- which is what makes a deletion visible.
    """
    out = {}
    for path in formula_files():
        base, end = os.path.basename(path), block_end_line(path)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")

        labelled = False
        for line in lines:                      # labelled: anywhere in the file
            m = _ANNOT.search(line)
            if m and m.group(1) is not None:
                labelled = True
                key = (base, m.group(1))
                if key not in out:
                    out[key] = tuple(int(g) for g in m.groups()[1:])

        if end is None:
            continue
        lo = end + 1
        if not labelled:
            # No labels to disambiguate, so the ledger must be at the determinant.
            det = next((i for i, l in enumerate(lines)
                        if i > end and _DETLINE.match(l.split("//")[0])), None)
            if det is None:
                continue
            lo, hi = det + 1, det + 1 + _ADJACENT
            lines = lines[:hi]
        for line in lines[lo:]:
            m = _ANNOT.search(line)
            if m and m.group(1) is None:
                key = (base, "block")
                if key not in out:
                    out[key] = tuple(int(g) for g in m.groups()[1:])
                break
    return out


# ===========================================================================
# fields
# ===========================================================================

class Fp(object):
    """A prime field, as ints mod p."""

    def __init__(self, p):
        self.p, self.char, self.name = p, p, "GF(%d)" % p
        self.size = p

    def rnd(self, rng):
        return rng.randrange(self.p)

    def add(self, a, b):
        return (a + b) % self.p

    def sub(self, a, b):
        return (a - b) % self.p

    def mul(self, a, b):
        return (a * b) % self.p

    def neg(self, a):
        return (-a) % self.p

    def scale(self, a, n):
        return (a * n) % self.p

    def inv(self, a):
        return pow(a, self.p - 2, self.p)

    def elements(self):
        return range(self.p)


class GF2k(object):
    """GF(2^k), bit-packed, reduced by a fixed irreducible."""

    MOD = {1: 0b11, 2: 0b111, 3: 0b1011, 4: 0b10011, 5: 0b100101,
           8: 0b100011011, 16: 0b10001000000001011}

    def __init__(self, k):
        self.k, self.m = k, self.MOD[k]
        self.char, self.size = 2, 1 << k
        self.name = "GF(%d)" % (1 << k)

    def rnd(self, rng):
        return rng.randrange(1 << self.k)

    def add(self, a, b):
        return a ^ b

    sub = add

    def neg(self, a):
        return a

    def scale(self, a, n):
        return a if n % 2 else 0

    def mul(self, a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if (a >> self.k) & 1:
                a ^= self.m
        return r

    def elements(self):
        return range(1 << self.k)


CH2 = (1, 2, 3, 4, 5, 8, 16)                      # GF(2) .. GF(2^16)
CH2_NAMES = frozenset("GF(%d)" % (1 << k) for k in CH2)
PRIMES = (3, 5, 7, 11, 13, 101, 1009, 10007, 1000003)


def default_fields():
    return [GF2k(k) for k in CH2] + [Fp(p) for p in PRIMES]


def _is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def validate_fields(fields, rng, samples=40):
    """[(field name, problem)] -- the fields really are fields.

    Cheap, and not optional: a broken GF(2^16) multiplication would make every
    candidate below agree with a reference computed the same broken way, and the
    whole file would report VERIFIED. So each field is required to have
    a^(q-1) = 1 for sampled nonzero elements, distributivity on sampled triples,
    and (for the prime fields) a prime modulus.
    """
    bad = []
    for F in fields:
        if isinstance(F, Fp) and not _is_prime(F.p):
            bad.append((F.name, "modulus is not prime"))
            continue
        for _ in range(samples):
            a, b, c = (F.rnd(rng), F.rnd(rng), F.rnd(rng))
            if F.mul(a, F.add(b, c)) != F.add(F.mul(a, b), F.mul(a, c)):
                bad.append((F.name, "distributivity failed"))
                break
            if a:
                x, e = 1, F.size - 1
                base = a
                while e:
                    if e & 1:
                        x = F.mul(x, base)
                    base = F.mul(base, base)
                    e >>= 1
                if x != 1:
                    bad.append((F.name, "a^(q-1) != 1 for a=%d" % a))
                    break
        acc, one = 0, 1
        for _ in range(F.char):
            acc = F.add(acc, one)
        if acc != 0:
            bad.append((F.name, "char*1 != 0"))
    return bad


# ===========================================================================
# the tracked element
# ===========================================================================

class HalvingInChar2(Exception):
    """Raised by `Elt.half()` where it is undefined."""


class Elt(object):
    """A field element that tallies M / S / A on the repository's conventions.

    A unary minus is free: `maginterp.py`'s `neg` bumps nothing, because in this
    source a negation always folds into the sibling subtraction. Multiplication
    or division by a literal integer is 1A, as `maginterp.py` charges for
    `int * x` and `x / int`. Squaring is charged S when both factors are the *same
    object*; `maginterp.py`, measured, charges S for `x^2` and M for `x*x`, so this
    is a divergence and not an analogue -- see the module docstring. It changes no
    figure here, since every candidate has S = 0.
    """

    __slots__ = ("v", "c", "F")

    def __init__(self, v, c, F):
        self.v, self.c, self.F = v, c, F

    def _w(self, v):
        # `type(self)`, not `Elt`: the recording subclass below has to survive
        # into derived values, or a product whose left operand is a temporary
        # goes unrecorded and the t-by-t census silently undercounts. It did.
        return type(self)(v, self.c, self.F)

    def __mul__(self, o):
        if isinstance(o, int):
            self.c["A"] += 1
            return self._w(self.F.scale(self.v, o))
        self.c["S" if self is o else "M"] += 1
        return self._w(self.F.mul(self.v, o.v))

    __rmul__ = __mul__

    def __add__(self, o):
        self.c["A"] += 1
        return self._w(self.F.add(self.v, o.v))

    def __sub__(self, o):
        self.c["A"] += 1
        return self._w(self.F.sub(self.v, o.v))

    def __neg__(self):
        return self._w(self.F.neg(self.v))

    def sq(self):
        self.c["S"] += 1
        return self._w(self.F.mul(self.v, self.v))

    def half(self):
        if self.F.char == 2:
            raise HalvingInChar2("division by 2 is undefined in %s" % self.F.name)
        self.c["A"] += 1
        return self._w(self.F.mul(self.v, self.F.inv(2)))

    def __repr__(self):
        return "<%s %s>" % (self.v, self.F.name)


class PolyField(object):
    """The polynomial ring, dressed as a field so `Elt` can run over it.

    Running a candidate here proves the identity rather than sampling it: the
    coefficients of every candidate are integers, so an equality that holds in
    Z[t,up] holds in every characteristic. The random field trials are kept as
    the independent check -- two ways of being right, sharing no arithmetic.
    """

    char, size, name = 0, 0, "Z[t,up]"

    def add(self, a, b):
        return a + b

    def sub(self, a, b):
        return a - b

    def mul(self, a, b):
        return a * b

    def neg(self, a):
        return -a

    def scale(self, a, n):
        return a * n

    def inv(self, a):
        raise NotImplementedError("no inverses in the polynomial ring")


# a record of the products a symbolic run performed, for the t-by-t census
class Recorder(dict):
    def __init__(self):
        dict.__init__(self, M=0, S=0, A=0)
        self.products = []


class RecElt(Elt):
    """Like `Elt`, but a symbolic run also keeps each product's two factors."""

    __slots__ = ()

    def __mul__(self, o):
        if isinstance(o, int):
            self.c["A"] += 1
            return self._w(self.F.scale(self.v, o))
        self.c["S" if self is o else "M"] += 1
        self.c.products.append((self.v, o.v))
        return self._w(self.F.mul(self.v, o.v))

    __rmul__ = __mul__


# ===========================================================================
# the reference values
# ===========================================================================

KEYS = ("m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9", "d",
        "sp0", "sp1", "sp2")


def reference_polys():
    """{key: Poly} for m1..m9, d, sp0..sp2, from the independent construction."""
    T = build_T()
    M = adjugate(T)
    out = {"m%d" % (3 * i + j + 1): M[i][j] for i in range(3) for j in range(3)}
    out["d"] = det3(T)
    vt = [_pv(6), _pv(7), _pv(8)]
    for i in range(3):
        out["sp%d" % i] = (M[i][0] * vt[0] + M[i][1] * vt[1] + M[i][2] * vt[2])
    return out


def reference_over(F, args):
    """The same values in a concrete field, computed the plain way.

    Deliberately the schoolbook route -- six T entries, nine 2x2 minors, one
    3x3 determinant -- so that it shares no structure with any candidate. Its
    agreement with `reference_polys()` is checked in the `source` section.
    """
    mul, sub, add, neg = F.mul, F.sub, F.add, F.neg
    t1, t4, t7, up0, up1, up2 = args[:6]
    t2 = neg(mul(up0, t7))
    t5 = sub(t1, mul(up1, t7))
    t8 = sub(t4, mul(up2, t7))
    t3 = neg(mul(up0, t8))
    t6 = sub(t2, mul(up1, t8))
    t9 = sub(t5, mul(up2, t8))
    T = [[t1, t2, t3], [t4, t5, t6], [t7, t8, t9]]
    out = {}
    for i in range(3):
        for j in range(3):
            r = [x for x in range(3) if x != j]
            c = [x for x in range(3) if x != i]
            minor = sub(mul(T[r[0]][c[0]], T[r[1]][c[1]]),
                        mul(T[r[0]][c[1]], T[r[1]][c[0]]))
            out["m%d" % (3 * i + j + 1)] = minor if (i + j) % 2 == 0 else neg(minor)
    out["d"] = add(add(mul(t1, out["m1"]), mul(t4, out["m2"])),
                   mul(t7, out["m3"]))
    if len(args) > 6:
        vt = args[6:9]
        for i in range(3):
            out["sp%d" % i] = add(add(mul(vt[0], out["m%d" % (3 * i + 1)]),
                                      mul(vt[1], out["m%d" % (3 * i + 2)])),
                                  mul(vt[2], out["m%d" % (3 * i + 3)]))
    return out


# ===========================================================================
# the candidates
# ===========================================================================

def shipped_7(t1, t4, t7, up0, up1, up2):
    """arb_ramifiedG3_ADD.mag, `t1:= u0 - up0;` .. `d:= t1*m1 + t4*m2 + t7*m3;`.

    That is the whole block above the `d eq 0` guard. Anchored on its text and
    not on line numbers: these files are under active edit and every number
    quoted here moved once already while this module was being written.
    """
    t2 = -(up0 * t7)
    t5 = t1 - up1 * t7
    t8 = t4 - up2 * t7
    m7 = t4 * t8 - t5 * t7
    m8 = t2 * t7 - t1 * t8
    m9 = t1 * t5 - t2 * t4
    m5 = m9 + up2 * m8
    m3 = -(up0 * m8)
    m2 = -(up0 * m7)
    m1 = m5 + up1 * m7
    d = t1 * m1 + t4 * m2 + t7 * m3
    return dict(m1=m1, m2=m2, m3=m3, m5=m5, m7=m7, m8=m8, m9=m9, d=d)


def shipped_7_dbl(t1, t4, t7, up0, up1, up2):
    """arb_ramifiedG3_DBL.mag, `ta := u2*d2;` .. `det := d0*m1 + d1*m2 + d2*m3;`.

    The same block written differently.

    The doubling names the first column d0,d1,d2 and keeps `tc = up0*t7`
    unnegated. Transcribed separately, and required to produce the same values
    and the same count as `shipped_7`: two transcriptions agreeing is the only
    check available here on whether either was transcribed correctly.
    """
    ta = up2 * t7
    tb = up1 * t7
    tc = up0 * t7
    t5 = t1 - tb
    t8 = t4 - ta
    temp3 = t7 * tc
    temp4 = t4 * t8
    temp5 = t1 * t8
    m9 = t1 * t5 + t4 * tc
    m8 = -temp5 - temp3
    m7 = temp4 - t7 * t5
    tf = -(up0 * m7)
    m5 = m9 + up2 * m8
    m3 = -(up0 * m8)
    m2 = tf
    m1 = m5 + up1 * m7
    d = t1 * m1 + t4 * m2 + t7 * m3
    return dict(m1=m1, m2=m2, m3=m3, m5=m5, m7=m7, m8=m8, m9=m9, d=d)


def shipped_9(t1, t4, t7, up0, up1, up2):
    """shipped_7 plus `m6:= m2 - up1*m8; m4:= m8 + up2*m7;` on the generic path."""
    t2 = -(up0 * t7)
    t5 = t1 - up1 * t7
    t8 = t4 - up2 * t7
    m7 = t4 * t8 - t5 * t7
    m8 = t2 * t7 - t1 * t8
    m9 = t1 * t5 - t2 * t4
    m5 = m9 + up2 * m8
    m3 = -(up0 * m8)
    m2 = -(up0 * m7)
    m1 = m5 + up1 * m7
    d = t1 * m1 + t4 * m2 + t7 * m3
    m6 = m2 - up1 * m8
    m4 = m8 + up2 * m7
    return dict(m1=m1, m2=m2, m3=m3, m4=m4, m5=m5, m6=m6, m7=m7, m8=m8,
                m9=m9, d=d)


def split_q(t1, t4, t7, up0, up1, up2):
    """arb_splitG3_ADD.mag, `t1 := u0 - up0;` .. `d := t1*m1 + t2*m4 + t3*m7;`.

    The whole first column, and d.

    The split model wants only column 1 of the adjugate (it is the coefficient
    vector of q = d/w mod up), and pays for all nine T entries to get it.
    """
    t2 = -(up0 * t7)
    t5 = t1 - up1 * t7
    t8 = t4 - up2 * t7
    t3 = -(up0 * t8)
    t6 = t2 - up1 * t8
    t9 = t5 - up2 * t8
    m1 = t5 * t9 - t6 * t8
    m4 = t6 * t7 - t4 * t9
    m7 = t4 * t8 - t5 * t7
    d = t1 * m1 + t2 * m4 + t3 * m7
    return dict(m1=m1, m4=m4, m7=m7, d=d)


def _rank5_row3(t1, t4, t7, up0, up1, up2):
    """The five-product bottom row, and column 2 of T. Shared by the variants.

    (m7,m8,m9) is the cross product of column 1 and column 2 of T (checked in
    the `rank` section), and the cross product has a five-product bilinear
    scheme. This is that scheme, transcribed from the session's
    scratchpad/final_report.py and scratchpad/adjfloor.py.
    """
    b1 = -(up0 * t7)
    b2 = t1 - up1 * t7
    b3 = t4 - up2 * t7
    b13 = b1 + b3
    a23 = t4 + t7
    sb = b13 + b2
    sa = a23 + t1
    R1 = t7 * sb
    R2 = t4 * b1
    R3 = a23 * b13
    R4 = t1 * b2
    R5 = sa * b3
    u = R3 - R2
    return u - R1, u - R5, R4 - R2


def rank5_7(t1, t4, t7, up0, up1, up2):
    """The seven entries, no d, via the five-product bottom row."""
    m7, m8, m9 = _rank5_row3(t1, t4, t7, up0, up1, up2)
    m5 = m9 + up2 * m8
    m3 = -(up0 * m8)
    m2 = -(up0 * m7)
    m1 = m5 + up1 * m7
    return dict(m1=m1, m2=m2, m3=m3, m5=m5, m7=m7, m8=m8, m9=m9)


def rank5_7_d(t1, t4, t7, up0, up1, up2):
    """The seven entries and d, via the five-product bottom row."""
    out = rank5_7(t1, t4, t7, up0, up1, up2)
    out["d"] = (t1 * out["m1"] + t4 * out["m2"] + t7 * out["m3"])
    return out


def rank5_9_d(t1, t4, t7, up0, up1, up2):
    """All nine entries and d, via the five-product bottom row."""
    out = rank5_7_d(t1, t4, t7, up0, up1, up2)
    out["m6"] = out["m2"] - up1 * out["m8"]
    out["m4"] = out["m8"] + up2 * out["m7"]
    return out


def rank5_9(t1, t4, t7, up0, up1, up2):
    """All nine entries, no d, via the five-product bottom row."""
    out = rank5_7(t1, t4, t7, up0, up1, up2)
    out["m6"] = out["m2"] - up1 * out["m8"]
    out["m4"] = out["m8"] + up2 * out["m7"]
    return out


def row3_shipped(t1, t4, t7, up0, up1, up2):
    """The bottom row alone, shipped route: column 2 of T, then three minors."""
    t2 = -(up0 * t7)
    t5 = t1 - up1 * t7
    t8 = t4 - up2 * t7
    return dict(m7=t4 * t8 - t5 * t7,
                m8=t2 * t7 - t1 * t8,
                m9=t1 * t5 - t2 * t4)


def row3_rank5(t1, t4, t7, up0, up1, up2):
    """The bottom row alone, five-product route."""
    m7, m8, m9 = _rank5_row3(t1, t4, t7, up0, up1, up2)
    return dict(m7=m7, m8=m8, m9=m9)


def region_shipped(t1, t4, t7, up0, up1, up2, vt0, vt1, vt2):
    """The whole region: all nine entries, d, and sp = M*vt.

    The fragment `arb_ramifiedG3_ADD.mag` annotates
    `// top: 16m 0s 9a` / `// 11m 0s 8a` / `// total: 27m 0s 17a (equivalent 98a)`.
    """
    out = shipped_9(t1, t4, t7, up0, up1, up2)
    m = out
    sp0 = vt0 * m["m1"] + vt1 * m["m2"] + vt2 * m["m3"]
    sp1 = vt0 * m["m4"] + vt1 * m["m5"] + vt2 * m["m6"]
    sp2 = vt0 * m["m7"] + vt1 * m["m8"] + vt2 * m["m9"]
    return dict(d=m["d"], sp0=sp0, sp1=sp1, sp2=sp2)


def region_rank5(t1, t4, t7, up0, up1, up2, vt0, vt1, vt2):
    """The same region with the five-product bottom row underneath it."""
    m = rank5_9_d(t1, t4, t7, up0, up1, up2)
    sp0 = vt0 * m["m1"] + vt1 * m["m2"] + vt2 * m["m3"]
    sp1 = vt0 * m["m4"] + vt1 * m["m5"] + vt2 * m["m6"]
    sp2 = vt0 * m["m7"] + vt1 * m["m8"] + vt2 * m["m9"]
    return dict(d=m["d"], sp0=sp0, sp1=sp1, sp2=sp2)


class Candidate(object):
    """One program, what it claims to produce, and what was claimed of it.

    `expect` is the session's claim as recorded in the task that commissioned
    this module -- not ground truth. `annot` names a `(file, label)` op-count
    comment in the repository, which is ground truth about what the repository
    says. Both are printed beside the measurement, and a difference is reported
    rather than reconciled.
    """

    def __init__(self, name, fn, nargs, expect=None, annot=None, group="entries"):
        self.name, self.fn, self.nargs = name, fn, nargs
        self.expect, self.annot, self.group = expect, annot, group
        self.doc = (fn.__doc__ or "").strip().splitlines()[0]


CANDIDATES = [
    Candidate("shipped_7", shipped_7, 6, (16, 0, 9),
              ("arb_ramifiedG3_ADD.mag", "top")),
    Candidate("shipped_7_dbl", shipped_7_dbl, 6, (16, 0, 9),
              ("arb_ramifiedG3_DBL.mag", "block")),
    Candidate("shipped_9", shipped_9, 6, (18, 0, 11)),
    Candidate("split_q", split_q, 6, (15, 0, 9)),
    Candidate("rank5_7_d", rank5_7_d, 6, (15, 0, 14)),
    Candidate("rank5_7", rank5_7, 6, (12, 0, 12)),
    Candidate("rank5_9_d", rank5_9_d, 6, (17, 0, 16)),
    Candidate("rank5_9", rank5_9, 6, None),
    Candidate("row3_shipped", row3_shipped, 6, (9, 0, 5)),
    Candidate("row3_rank5", row3_rank5, 6, (8, 0, 10)),
    Candidate("region_shipped", region_shipped, 9, (27, 0, 17),
              ("arb_ramifiedG3_ADD.mag", "total"), group="region"),
    Candidate("region_rank5", region_rank5, 9, (26, 0, 22), None, group="region"),
]


def equiv_additions(M, S, A):
    """The thesis's 1M : 3A scale (chapter4.tex:817). S is priced as M."""
    return 3 * (M + S) + A


# ===========================================================================
# verifying and counting a candidate
# ===========================================================================

def _lcg(seed):
    """A tiny deterministic generator, so a run reproduces without `random`
    seeding conventions mattering. (`random` is permitted here; this is simply
    shorter to state and stable across versions.)"""
    x = seed & 0xFFFFFFFFFFFF
    while True:
        x = (25214903917 * x + 11) & 0xFFFFFFFFFFFF
        yield x >> 16


class _Rng(object):
    def __init__(self, seed):
        self.g = _lcg(seed)

    def randrange(self, n):
        return next(self.g) % n


def _seed_for(seed, label):
    """A per-field seed that does not move between processes.

    `hash(str)` is salted per interpreter, so using it here would give a
    different input sequence on every run and the tool would not be able to
    reproduce its own output. Spelled out instead.
    """
    h = 2166136261
    for ch in label:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return seed ^ h


def check(fn, nargs=6, fields=None, trials=200, seed=20260819, keys=None):
    """Verify one program against the reference, and count it.

    Returns {ok, claims, M, S, A, MS, equiv, fields, trials, symbolic,
    t_by_t, t_by_t_up0, fails}. `fails` holds at most seven records, each
    (field, inputs, key, got, want) -- or a marker for a count that moved, a
    claim set that moved, or a halving refused in characteristic 2.
    """
    fields = fields if fields is not None else default_fields()
    ref = reference_polys()
    fails, counts, claims = [], None, None

    # --- the symbolic run: an identity in Z[t,up], hence in every characteristic
    PF = PolyField()
    rec = Recorder()
    sym_ok, sym_why = True, ""
    try:
        got = fn(*[RecElt(_pv(i), rec, PF) for i in range(nargs)])
    except Exception as exc:                                    # noqa: BLE001
        sym_ok, sym_why, got = False, "%s: %s" % (type(exc).__name__, exc), {}
    if sym_ok:
        claims = tuple(sorted(got))
        unknown = [k for k in claims if k not in KEYS]
        if unknown:
            sym_ok, sym_why = False, "unknown keys %s" % unknown
        else:
            for k in claims:
                if got[k].v != ref[k]:
                    sym_ok = False
                    sym_why = "%s differs from the reference as a polynomial" % k
                    break
            else:
                nonint = [k for k in claims if not got[k].v.is_integral()]
                if nonint:
                    sym_ok, sym_why = False, "non-integer coefficients in %s" % nonint
    symbolic = {"ok": sym_ok, "why": sym_why,
                "M": rec["M"], "S": rec["S"], "A": rec["A"]}
    if not sym_ok:
        fails.append(("Z[t,up]", (), "*symbolic*", sym_why, ""))

    # --- the t-by-t census, from the recorded products
    tbt = tbt0 = 0
    for a, b in rec.products:
        if not a.homog(TIDX, 1).is_zero() and not b.homog(TIDX, 1).is_zero():
            tbt += 1
        a0, b0 = a.at_zero(UPIDX), b.at_zero(UPIDX)
        if not a0.homog(TIDX, 1).is_zero() and not b0.homog(TIDX, 1).is_zero():
            tbt0 += 1

    # --- the field runs
    #
    # Every field is visited even once the candidate is known to be wrong, and
    # the per-field mismatch tally is kept. A program can be wrong in one
    # characteristic and right in another -- a sign flip is invisible in
    # characteristic 2 -- so "which fields disagreed" is the interesting output
    # and stopping at the first is not good enough. Only the detailed records are
    # capped.
    per_field = {}
    for F in fields:
        rng = _Rng(_seed_for(seed, F.name))
        wrong_here = 0
        for _ in range(trials):
            args = [F.rnd(rng) for _ in range(nargs)]
            c = {"M": 0, "S": 0, "A": 0}
            try:
                out = fn(*[Elt(a, c, F) for a in args])
            except HalvingInChar2 as exc:
                fails.append((F.name, tuple(args), "*refused*", str(exc), ""))
                break
            if claims is None:
                claims = tuple(sorted(out))
            elif tuple(sorted(out)) != claims:
                fails.append((F.name, tuple(args), "*claims changed*",
                              tuple(sorted(out)), claims))
                break
            if counts is None:
                counts = dict(c)
            elif c != counts:
                fails.append((F.name, tuple(args), "*count is input-dependent*",
                              dict(c), counts))
                break
            want = reference_over(F, args)
            for k in claims:
                g = out[k].v if isinstance(out[k], Elt) else out[k]
                if g != want[k]:
                    wrong_here += 1
                    if len(fails) <= 6:
                        fails.append((F.name, tuple(args), k, g, want[k]))
            if wrong_here >= 3:
                break                      # this field has answered
        per_field[F.name] = wrong_here
    counts = counts or {"M": symbolic["M"], "S": symbolic["S"], "A": symbolic["A"]}
    M, S, A = counts["M"], counts["S"], counts["A"]
    if (M, S, A) != (symbolic["M"], symbolic["S"], symbolic["A"]):
        fails.append(("Z[t,up]", (), "*count differs symbolically*",
                      (symbolic["M"], symbolic["S"], symbolic["A"]), (M, S, A)))
    wrongf = sorted(n for n, k in per_field.items() if k)
    return {"ok": not fails and not wrongf, "claims": claims,
            "M": M, "S": S, "A": A,
            "MS": M + S, "equiv": equiv_additions(M, S, A),
            "fields": [F.name for F in fields], "trials": trials,
            "fields_wrong": wrongf,
            "fields_wrong_char2": [n for n in wrongf if n in CH2_NAMES],
            "symbolic": symbolic, "t_by_t": tbt, "t_by_t_up0": tbt0,
            "fails": fails[:7]}


# ===========================================================================
# linear algebra
# ===========================================================================

def rref_q(rows):
    """(rank, reduced rows) over Q, exact."""
    rows = [[Fraction(x) for x in r] for r in rows]
    ncols = len(rows[0]) if rows else 0
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = Fraction(1) / rows[r][c]
        rows[r] = [x * inv for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [rows[i][k] - f * rows[r][k] for k in range(ncols)]
        r += 1
    return r, [row for row in rows[:r]]


def rank_p(rows, p):
    """Rank over GF(p)."""
    rows = [[x % p for x in r] for r in rows]
    ncols = len(rows[0]) if rows else 0
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(rows)) if rows[i][c] % p), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = pow(rows[r][c], p - 2, p)
        rows[r] = [x * inv % p for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] % p:
                f = rows[i][c]
                rows[i] = [(rows[i][k] - f * rows[r][k]) % p for k in range(ncols)]
        r += 1
    return r


def rank_over_polys(rows):
    """Rank of a matrix of Poly entries over the fraction field Q(vars).

    Fraction-free elimination: `row_i <- row_i * pivot - row_p * row_i[c]`. Every
    step is invertible over the fraction field, so the rank is preserved, and no
    division -- hence no polynomial gcd machinery -- is needed. This is what
    makes "the dimension at *generic* up" an exact statement rather than a
    statement about the up values that happened to be sampled.
    """
    rows = [list(r) for r in rows]
    ncols = len(rows[0]) if rows else 0
    r = 0
    for c in range(ncols):
        piv = next((i for i in range(r, len(rows)) if not rows[i][c].is_zero()),
                   None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        pivot = rows[r][c]
        for i in range(r + 1, len(rows)):
            if not rows[i][c].is_zero():
                f = rows[i][c]
                rows[i] = [rows[i][k] * pivot - rows[r][k] * f
                           for k in range(ncols)]
        r += 1
    return r


# ===========================================================================
# section: source
# ===========================================================================

def section_source(verbose=False):
    """The files' own cofactor block, against an independent construction."""
    T = build_T()
    tvals = t_names_map(T)
    ref = reference_polys()
    out = {"files": [], "problems": [], "t_entries": {}}

    for name in sorted(tvals, key=lambda s: int(s[1:])):
        out["t_entries"][name] = tvals[name].text(VARS)

    # d = Res(w, up), independently
    res = resultant_w_up()
    out["det_is_resultant"] = (res == ref["d"])
    if not out["det_is_resultant"]:
        out["problems"].append("det(T) != Res(w,up) (5x5 Sylvester)")

    seen = 0
    for path in formula_files():
        try:
            got = read_cofactor_block(path, tvals)
        except Exception as exc:                                # noqa: BLE001
            out["problems"].append("%s: %s" % (os.path.basename(path), exc))
            continue
        if got is None:
            continue
        entries, det, annots = got
        seen += 1
        base = os.path.basename(path)
        bad = [k for k in sorted(entries) if entries[k] != ref[k]]
        # A characteristic-2 file may legitimately write `+` where the general
        # form has `-`. So a determinant line that differs is asked the further
        # question of whether the difference is divisible by 2, and that is
        # accepted only from a file the repository names `ch2_`.
        if det is None:
            detstate = "absent"
        elif det == ref["d"]:
            detstate = "agrees"
        elif all(v.numerator % 2 == 0 and v.denominator == 1
                 for v in (det - ref["d"]).c.values()):
            detstate = ("agrees in characteristic 2 only"
                        if base.startswith("ch2_")
                        else "DISAGREES (though only by a multiple of 2)")
        else:
            detstate = "DISAGREES"
        out["files"].append({
            "file": os.path.relpath(path, ROOT),
            "entries": len(entries), "disagree": bad,
            "det": detstate,
            "annotations": [list(a) for a in annots],
        })
        if bad:
            out["problems"].append("%s: %s disagree with adj(T)"
                                   % (base, ",".join(bad)))
        if detstate.startswith("DISAGREES"):
            out["problems"].append("%s: its determinant line %s"
                                   % (base, detstate))
    if seen == 0:
        out["problems"].append("no formula file carries a `//| m1= ... |` block")
    out["files_with_block"] = seen

    # the concrete-field reference must agree with the polynomial one
    F = Fp(10007)
    rng = _Rng(5)
    mism = 0
    for _ in range(50):
        args = [F.rnd(rng) for _ in range(9)]
        want = reference_over(F, args)
        subs = {i: Fraction(args[i]) for i in range(9)}
        for k in want:
            v = ref[k].subs(subs)
            val = int(v.c.get((0,) * NV, Fraction(0))) % F.p
            if val != want[k]:
                mism += 1
    out["field_reference_mismatches"] = mism
    if mism:
        out["problems"].append("the field reference and the polynomial "
                               "reference disagree %d times" % mism)
    out["ok"] = not out["problems"]
    return out


# ===========================================================================
# section: table / region
# ===========================================================================

def section_table(group="entries", fields=None, trials=200, seed=20260819):
    """Every candidate, verified over every field and counted."""
    annots = all_annotations()
    rows = []
    for cand in CANDIDATES:
        if cand.group != group:
            continue
        r = check(cand.fn, cand.nargs, fields, trials, seed)
        got = (r["M"], r["S"], r["A"])
        row = {
            "name": cand.name, "doc": cand.doc, "claims": list(r["claims"] or ()),
            "ok": r["ok"], "M": r["M"], "S": r["S"], "A": r["A"],
            "equiv": r["equiv"], "symbolic": r["symbolic"]["ok"],
            "t_by_t": r["t_by_t"], "t_by_t_up0": r["t_by_t_up0"],
            "expect": list(cand.expect) if cand.expect else None,
            "expect_agrees": (None if not cand.expect
                              else got == tuple(cand.expect)),
            "fails": [[str(x) for x in f] for f in r["fails"]],
        }
        if cand.annot:
            a = annots.get(cand.annot)
            row["annotation"] = {
                "where": "%s (%s)" % cand.annot,
                "value": list(a) if a else None,
                "agrees": (None if a is None else got == a),
            }
        rows.append(row)
    out = {"rows": rows,
           "ok": all(r["ok"] for r in rows) and bool(rows),
           "annotations_read": {"%s|%s" % k: list(v)
                                for k, v in sorted(annots.items())}}

    # `arb_ramifiedG3_ADD.mag` annotates three fragments, not two: the adjugate
    # block (`// top:`), the whole thing (`// total:`), and the lower half
    # (unlabelled, `// 11m 0s 8a`). The lower half has no candidate of its own --
    # it is not a self-contained program, it reads m1..m9 -- so it is checked as
    # the difference between the two that are.
    if group == "region":
        top = check(shipped_7, 6, fields, trials, seed)
        whole = next((r for r in rows if r["name"] == "region_shipped"), None)
        ann = annots.get(("arb_ramifiedG3_ADD.mag", "block"))
        if whole:
            diff = (whole["M"] - top["M"], whole["S"] - top["S"],
                    whole["A"] - top["A"])
            out["lower_half"] = {
                "measured": list(diff),
                "annotation": list(ann) if ann else None,
                "agrees": None if ann is None else diff == ann,
            }
            if ann is not None and diff != ann:
                out["ok"] = False
        # Said in the output, not only in the docstring: the third route the
        # files discuss is not measured anywhere here, and a reader comparing
        # 27M against 26M should know which 26M this is.
        sq = check(split_q, 6, fields, trials, seed)
        shipped_equiv = next(r["equiv"] for r in rows
                             if r["name"] == "region_shipped")
        out["not_established"] = [
            "A third route exists and is NOT implemented or measured here. The",
            "doubling's comment -- `// 11m 20a where the matrix-vector product "
            "costs",
            "11m 8a` -- describes taking only the first column of the adjugate "
            "and",
            "reducing s = k*q mod u with Karatsuba twice. No code for it exists "
            "in",
            "the repository, so building it would mean inventing it, and this "
            "module",
            "verifies neither of those two figures.",
            "",
            "Its consequence, though, is worth stating: taking the file's `11m "
            "20a` on",
            "trust and adding the split first column, which IS measured here at "
            "%dM %dS %dA," % (sq["M"], sq["S"], sq["A"]),
            "that route comes to %dM %dS %dA, equivalent %da, against the "
            "shipped %da."
            % (sq["M"] + 11, sq["S"], sq["A"] + 20,
               equiv_additions(sq["M"] + 11, sq["S"], sq["A"] + 20),
               shipped_equiv),
            "So TWO different 26M rows are in play, and the `26M 0S 22A` above "
            "is the",
            "rank-5 adjugate one, not this one.",
        ]
    return out


# ===========================================================================
# section: span
# ===========================================================================

QUAD = ((2, 0, 0), (1, 1, 0), (1, 0, 1), (0, 2, 0), (0, 1, 1), (0, 0, 2))
QUAD_NAMES = ("t1^2", "t1*t4", "t1*t7", "t4^2", "t4*t7", "t7^2")
NINE = ("m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9")


def _quad_vector(poly, up_subs=None):
    """The coefficient vector of a t-quadratic over the six t-monomials.

    `up_subs` may be None (keep up symbolic -- entries are Poly coefficients) or
    {index: value}, in which case the entries come out as Fractions.
    """
    p = poly if up_subs is None else poly.subs(up_subs)
    if up_subs is None:
        cols = []
        for q in QUAD:
            sel = {}
            for m, v in p.c.items():
                if (m[0], m[1], m[2]) == q:
                    sel[tuple([0, 0, 0] + list(m[3:]))] = v
            cols.append(Poly(sel, NV))
        return cols
    return [p.c.get(tuple(list(q) + [0] * (NV - 3)), Fraction(0)) for q in QUAD]


def section_span(primes=(2, 3, 5, 7, 11), verbose=False):
    """The nine entries as quadratic forms in (t1,t4,t7): the span's dimension."""
    ref = reference_polys()
    nine = [ref[k] for k in NINE]

    # exact, at generic up: rank over the fraction field Q(up0,up1,up2)
    generic = rank_over_polys([_quad_vector(p) for p in nine])

    # at up -> 0, over Q, with the reduced basis printed
    rows0 = [_quad_vector(p, {3: 0, 4: 0, 5: 0}) for p in nine]
    rank0, basis0 = rref_q(rows0)
    basis_text = []
    for row in basis0:
        parts = []
        for coef, nm in zip(row, QUAD_NAMES):
            if not coef:
                continue
            sign = ("- " if coef < 0 else "+ ") if parts else ("-" if coef < 0
                                                               else "")
            mag = "" if abs(coef) == 1 else "%s*" % abs(coef)
            parts.append("%s%s%s" % (sign, mag, nm))
        basis_text.append(" ".join(parts) or "0")

    # at particular up over Q, and over small prime fields
    ups = [(0, 0, 0), (1, 0, 0), (1, 2, 3), (3, 5, 6), (7, 11, 13)]
    at_up_q = []
    for up in ups:
        rows = [_quad_vector(p, {3: up[0], 4: up[1], 5: up[2]}) for p in nine]
        at_up_q.append({"up": list(up), "rank": rref_q(rows)[0]})
    at_up_p = []
    for p in primes:
        for up in ups:
            rows = [[int(x) for x in _quad_vector(q, {3: up[0], 4: up[1],
                                                     5: up[2]})]
                    for q in nine]
            at_up_p.append({"p": p, "up": list(up), "rank": rank_p(rows, p)})

    # the six-dimensional ambient space is what a full-rank span would need
    return {
        "ambient": len(QUAD),
        "generic_rank_over_Q_of_up": generic,
        "rank_at_up0_over_Q": rank0,
        "basis_at_up0": basis_text,
        "at_up_over_Q": at_up_q,
        "at_up_over_Fp": at_up_p,
        "ok": (generic == 3 and rank0 == 3
               and all(x["rank"] == 3 for x in at_up_q)
               and all(x["rank"] == 3 for x in at_up_p)),
        "note": ("The span is 3-dimensional, not 6. A rank-6 span would have "
                 "forced 6 t-by-t products and proved the shipped count "
                 "optimal; it does not."),
    }


# ===========================================================================
# section: bound
# ===========================================================================

def U_rows():
    """U, the span at up -> 0, as integer rows -- DERIVED, never typed in.

    The bound and the Hessian both stand on U being exactly
    span{t1^2, t1*t4, t4^2 - t1*t7}. That basis used to be written out as a
    literal in three places, which meant `--section bound` on its own would keep
    reporting a bound of 4 from a stale U if the entries ever changed. It is now
    computed here from `reference_polys()` at up -> 0, cleared of denominators,
    and every consumer takes it from this one function.
    """
    ref = reference_polys()
    rows0 = [_quad_vector(ref[k], {3: 0, 4: 0, 5: 0}) for k in NINE]
    _, red = rref_q(rows0)
    out = []
    for row in red:
        den = 1
        for x in row:
            den = den * x.denominator // _gcd(den, x.denominator)
        out.append([int(x * den) for x in row])
    return out


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def hessian_det_of_U():
    """det of the Hessian of the generic element of U, exactly, over Q.

    U is taken from `U_rows()`, which derives it from the entries -- it is not
    named or typed in here. Its basis is written with coefficients (a,b,c) in the
    order `U_rows()` returns; a quadratic form in three variables is a product of
    two linear forms exactly when the rank of its Hessian is at most 2, i.e. when
    the determinant vanishes.

    Returns (det, varnames, basis_text, pure_cube_index): the last is the index
    of the single coefficient the determinant is a cube in, or None if it is not
    of that shape -- read off the determinant rather than assumed, because which
    basis vector carries it depends on the order `rref_q` happens to produce.
    """
    # variables: t1,t4,t7,a,b,c
    n = 6
    tv = [Poly.var(i, n) for i in range(3)]
    coef = [Poly.var(i, n) for i in range(3, 6)]
    U = U_rows()
    monos = [Poly({tuple(list(q) + [0, 0, 0]): Fraction(1)}, n) for q in QUAD]
    q = Poly.zero(n)
    basis_text = []
    for k, row in enumerate(U):
        term = Poly.zero(n)
        for j, cj in enumerate(row):
            if cj:
                term = term + monos[j] * Poly.const(Fraction(cj), n)
        q = q + coef[k] * term
        basis_text.append(term.text(("t1", "t4", "t7", "a", "b", "c")))
    H = [[q.diff(i).diff(j) for j in range(3)] for i in range(3)]
    det = det_leibniz(H)
    pure = None
    for k in range(3):
        if det.c and all(m[3 + k] == 3 and all(m[3 + j] == 0 for j in range(3)
                                               if j != k) for m in det.c):
            pure = k
            break
    return det, ("t1", "t4", "t7", "a", "b", "c"), basis_text, pure


def _lin_forms(p):
    """Every linear form in (t1,t4,t7) over GF(p), as coefficient triples."""
    return list(itertools.product(range(p), repeat=3))


def products_in_U(p, exhaustive_pairs=True):
    """(#products landing in U, dim of their span, #pairs examined) over GF(p).

    A product of two t-linear forms is a reducible quadratic. U is 3-dimensional.
    If three products spanned a space containing U then that space would *be* U,
    so all three would lie in U -- and this enumeration measures how large a
    space the products that lie in U can span.
    """
    # U as rows over the six t-monomials: t1^2, t1t4, t1t7, t4^2, t4t7, t7^2 --
    # derived from the entries by `U_rows()`, not written out here.
    Urows = [[x % p for x in r] for r in U_rows()]
    dimU = rank_p([r[:] for r in Urows], p)
    forms = _lin_forms(p)
    found, pairs = [], 0
    for l1 in forms:
        a1, b1, c1 = l1
        for l2 in forms:
            a2, b2, c2 = l2
            pairs += 1
            v = [(a1 * a2) % p, (a1 * b2 + b1 * a2) % p, (a1 * c2 + c1 * a2) % p,
                 (b1 * b2) % p, (b1 * c2 + c1 * b2) % p, (c1 * c2) % p]
            if not any(v):
                continue
            if rank_p([r[:] for r in Urows] + [v], p) == dimU:
                found.append(v)
    span = rank_p([r[:] for r in found], p) if found else 0
    return len(found), span, pairs, dimU


def products_in_span_at(up, p):
    """(#products in the entry span at this `up`, dim of their span) over GF(p).

    The same enumeration as `products_in_U`, but against the span at an arbitrary
    `up` rather than at `up -> 0`. Included because the choice of specialisation
    is not free: a program that computes the entries for every `up` also computes
    them at any single `up`, so the bound may be taken at whichever one gives the
    best answer -- and the answers differ. This is what shows `up -> 0` is the
    right choice rather than an arbitrary one.
    """
    ref = reference_polys()
    rows = [[int(x) % p for x in _quad_vector(ref[k], {3: up[0], 4: up[1],
                                                      5: up[2]})]
            for k in NINE]
    dim = rank_p([r[:] for r in rows], p)
    found = []
    for l1 in _lin_forms(p):
        a1, b1, c1 = l1
        for l2 in _lin_forms(p):
            a2, b2, c2 = l2
            v = [(a1 * a2) % p, (a1 * b2 + b1 * a2) % p, (a1 * c2 + c1 * a2) % p,
                 (b1 * b2) % p, (b1 * c2 + c1 * b2) % p, (c1 * c2) % p]
            if not any(v):
                continue
            if rank_p([r[:] for r in rows] + [v], p) == dim:
                found.append(v)
    return len(found), (rank_p([r[:] for r in found], p) if found else 0), dim


def attaining_four():
    """Four products of linear forms whose span contains U, and the solution.

    Attainability, so the bound is reported as tight in the specialisation rather
    than merely as a bound. Solved exactly over Q.
    """
    prods = [((1, 0, 0), (1, 0, 0)),          # t1*t1
             ((1, 0, 0), (0, 1, 0)),          # t1*t4
             ((0, 1, 0), (0, 1, -1)),         # t4*(t4-t7)
             ((0, 0, 1), (-1, 1, 0))]         # t7*(t4-t1)

    def vec(l1, l2):
        a1, b1, c1 = l1
        a2, b2, c2 = l2
        return [a1 * a2, a1 * b2 + b1 * a2, a1 * c2 + c1 * a2,
                b1 * b2, b1 * c2 + c1 * b2, c1 * c2]

    cols = [vec(*pr) for pr in prods]
    # the targets ARE U's derived basis, so a change in the entries changes what
    # has to be hit here rather than leaving a stale triple to be hit instead
    names = ("t1^2", "t1*t4", "t1*t7", "t4^2", "t4*t7", "t7^2")

    def _label(row):
        parts = []
        for cf, nm in zip(row, names):
            if not cf:
                continue
            sign = ("- " if cf < 0 else "+ ") if parts else ("-" if cf < 0 else "")
            parts.append("%s%s%s" % (sign, "" if abs(cf) == 1 else "%d*" % abs(cf),
                                     nm))
        return " ".join(parts) or "0"

    targets = {_label(row): row for row in U_rows()}
    out = {}
    for name, tgt in targets.items():
        # solve cols^T x = tgt by rref on the augmented system
        aug = [[Fraction(cols[j][i]) for j in range(4)] + [Fraction(tgt[i])]
               for i in range(6)]
        rank, red = rref_q(aug)
        sol, ok = [Fraction(0)] * 4, True
        for row in red:
            lead = next((j for j in range(4) if row[j]), None)
            if lead is None:
                if row[4]:
                    ok = False
                continue
            sol[lead] = row[4]
        # verify
        chk = [sum(sol[j] * cols[j][i] for j in range(4)) for i in range(6)]
        if chk != [Fraction(x) for x in tgt]:
            ok = False
        out[name] = {"coeffs": [str(x) for x in sol], "solved": ok}
    return {"products": ["t1*t1", "t1*t4", "t4*(t4-t7)", "t7*(t4-t1)"],
            "solutions": out,
            "all_solved": all(v["solved"] for v in out.values())}


def section_bound(primes=(2, 3, 5, 7, 11), verbose=False):
    """The lower bound on t-by-t products, at the up -> 0 specialisation."""
    det, names, basis_text, pure = hessian_det_of_U()
    # the Hessian determinant is a cubic in (a,b,c): read off WHICH coefficient
    # it is a cube in, rather than declaring that it is `a`
    det_text = det.text(names)
    only_a = pure is not None
    cube_var = names[3 + pure] if pure is not None else None
    coeff_a3 = Fraction(0)
    if pure is not None:
        key = [0, 0, 0, 0, 0, 0]
        key[3 + pure] = 3
        coeff_a3 = det.c.get(tuple(key), Fraction(0))

    per_p = []
    for p in primes:
        n, span, pairs, dimU = products_in_U(p)
        per_p.append({"p": p, "dim_U": dimU, "in_U": n, "span": span,
                      "pairs": pairs})

    four = attaining_four()

    # the same enumeration at other up, to show the specialisation was chosen
    at_other_up = []
    q = max(x for x in primes if x <= 7) if any(x <= 7 for x in primes) else None
    if q:
        for up in ((0, 0, 0), (1, 0, 0), (1, 2, 3), (3, 5, 6), (1, 1, 1)):
            n, span, dim = products_in_span_at(up, q)
            # The argument only closes at k = dim: `dim` products whose span
            # contains a dim-dimensional V span exactly V, so they all lie in V,
            # so they span at most `their_span`. That is a contradiction exactly
            # when their_span < dim, and then the bound is dim + 1. When
            # their_span = dim it yields nothing.
            at_other_up.append({"p": q, "up": list(up), "span_dim": dim,
                                "in_span": n, "their_span": span,
                                "bound": dim + 1 if span < dim else None})

    # the census of t-by-t products in the shipped and rank-5 rows
    census = {}
    for cand in CANDIDATES:
        r = check(cand.fn, cand.nargs, fields=[], trials=0)
        census[cand.name] = {"M": r["M"], "t_by_t": r["t_by_t"],
                             "t_by_t_up0": r["t_by_t_up0"]}

    bound = 4 if all(x["span"] <= 2 for x in per_p) else None
    return {
        "hessian_det": det_text,
        "hessian_det_is_multiple_of_a_cubed": only_a,
        "hessian_cube_variable": cube_var,
        "hessian_a3_coefficient": str(coeff_a3),
        "U_basis_derived": basis_text,
        "reducible_locus_dim": 2 if only_a else None,
        "per_prime": per_p,
        "at_other_up": at_other_up,
        "attaining": four,
        "census": census,
        "bound": bound,
        "ok": (bound == 4 and only_a and four["all_solved"]
               and all(x["dim_U"] == 3 for x in per_p)),
    }


# ===========================================================================
# section: mag -- the real source text, executed and priced
# ===========================================================================

# (candidate, file, first statement, last statement, {mag name: our name})
MAG_BLOCKS = (
    ("shipped_7", "g3/ramifiedModel/g3Formulas/arb_ramifiedG3_ADD.mag",
     "t2:= -up0*t7;", "d:= t1*m1 + t4*m2 + t7*m3;", {}),
    # The DBL's block was brought onto the ADD's notation on 2026-08-22, so the
    # rename map is now nearly empty: `d0/d1/d2` became `t1/t4/t7` and `det`
    # became `d` in the file itself. Only u -> up remains, the DBL naming its
    # single divisor u where the ADD's fragment reads the second operand.
    ("shipped_7_dbl", "g3/ramifiedModel/g3Formulas/arb_ramifiedG3_DBL.mag",
     "t2 := -u0*t7;", "d := t1*m1 + t4*m2 + t7*m3;",
     {"u0": "up0", "u1": "up1", "u2": "up2"}),
    ("split_q", "g3/splitModel/negReduced/g3Formulas/arb_splitG3_ADD.mag",
     "t2 := -up0*t7;", "d := t1*m1 + t2*m4 + t3*m7;", {}),
)

# The three `t1 = u0 - up0` differences are deliberately outside every anchor
# range: they are paid before the fragment and the files' comments do not count
# them, which is the whole reason 9A appears against text performing twelve.
MAG_PRIME = 1000003


def price_mag_block(spec, p=MAG_PRIME, inputs=(3, 5, 7, 11, 13, 17)):
    """Execute one .mag fragment through `maginterp` and price it.

    Returns a dict, never raises for a moved anchor -- the genus-3 addition files
    are under active edit, so a missing anchor is *reported* rather than thrown.

    The interpreter's three module-level flags are set the way `opcount.py` sets
    them (`DIV_LITERAL_AS_ADD` on, no `//Constant:` and no `//Ignore:` in scope --
    this fragment names no curve coefficient, and asserting that here is cheaper
    than trusting it) and restored afterwards, because `selftest.py` imports both
    this module and `opcount.py` into one process.
    """
    name, rel, start, end, rename = spec
    out = {"candidate": name, "file": rel, "anchors": [start, end],
           "found": False, "ok": False, "why": ""}
    path = os.path.join(ROOT, rel)
    try:
        import maginterp as MI                                  # noqa: PLC0415
        from ff import GF                                       # noqa: PLC0415
    except ImportError as exc:                                  # noqa: BLE001
        out["why"] = "maginterp/ff unavailable: %s" % exc
        return out
    if not os.path.isfile(path):
        out["why"] = "no such file"
        return out
    lines = open(path, encoding="utf-8").read().split("\n")
    si = next((i for i, ln in enumerate(lines) if ln.strip().startswith(start)),
              None)
    ei = None
    if si is not None:
        ei = next((i for i in range(si, len(lines))
                   if lines[i].strip().startswith(end)), None)
    if si is None or ei is None:
        out["why"] = ("anchor not found: %r" % (start if si is None else end))
        return out
    out["found"] = True
    out["statements_from_to"] = [si + 1, ei + 1]          # 1-based, for the human
    body = "\n".join(re.sub(r"//.*$", "", ln) for ln in lines[si:ei + 1])
    saved = (MI.CONSTS, MI.IGNORED, MI.DIV_LITERAL_AS_ADD)
    try:
        sts = MI.statements(body)
        blk, _ = MI.build(sts)
        F = GF(p)
        env = {}
        for k, v in zip(VARS[:6], inputs):
            env[k] = F(v)
        for magname, ours in rename.items():
            if ours in dict(zip(VARS[:6], inputs)):
                env[magname] = F(dict(zip(VARS[:6], inputs))[ours])
        MI.CONSTS, MI.IGNORED, MI.DIV_LITERAL_AS_ADD = set(), set(), True
        MI.COUNT.clear()
        MI.run(blk, env, F, [])
        count = dict(MI.COUNT)
    except Exception as exc:                                    # noqa: BLE001
        out["why"] = "%s: %s" % (type(exc).__name__, exc)
        return out
    finally:
        MI.CONSTS, MI.IGNORED, MI.DIV_LITERAL_AS_ADD = saved

    out["statements"] = len(sts)
    out["count"] = [count.get(k, 0) for k in ("M", "S", "A")]
    out["extra_ops"] = {k: v for k, v in count.items()
                        if k not in ("M", "S", "A") and v}

    # values, against the same reference the candidates are checked against
    class _F(object):
        char = size = p
        name = "GF(%d)" % p

        def add(self, a, b):
            return (a + b) % p

        def sub(self, a, b):
            return (a - b) % p

        def mul(self, a, b):
            return (a * b) % p

        def neg(self, a):
            return (-a) % p

    want = reference_over(_F(), list(inputs))
    got, wrong = {}, []
    for magname, val in env.items():
        ours = rename.get(magname, magname)
        if ours in KEYS:
            got[ours] = int(str(val)) % p
            if got[ours] != want[ours] % p:
                wrong.append(ours)
    out["values"] = sorted(got)
    out["values_wrong"] = sorted(wrong)

    # the transcription this is meant to pin
    cand = next((c for c in CANDIDATES if c.name == name), None)
    tr = check(cand.fn, cand.nargs, fields=[], trials=0) if cand else None
    if tr is not None:
        out["transcription_count"] = [tr["M"], tr["S"], tr["A"]]
        out["transcription_values"] = sorted(tr["claims"] or ())
    out["count_agrees"] = tr is not None and out["count"] == out[
        "transcription_count"]
    out["values_agree"] = tr is not None and out["values"] == out[
        "transcription_values"]
    out["ok"] = (not wrong and out["count_agrees"] and out["values_agree"]
                 and not out["extra_ops"])
    if not out["ok"] and not out["why"]:
        out["why"] = "; ".join(filter(None, [
            "values wrong: %s" % out["values_wrong"] if wrong else "",
            "count %s vs the transcription's %s" % (out["count"],
                                                    out.get("transcription_count"))
            if not out["count_agrees"] else "",
            "value set %s vs the transcription's %s"
            % (out["values"], out.get("transcription_values"))
            if not out["values_agree"] else "",
            "unexpected %s" % out["extra_ops"] if out["extra_ops"] else ""]))
    return out


def section_mag(verbose=False):
    """The shipped fragments' real text, executed through `maginterp.py`."""
    rows = [price_mag_block(s) for s in MAG_BLOCKS]
    annots = all_annotations()
    for row in rows:
        base = os.path.basename(row["file"])
        label = {"shipped_7": "top", "shipped_7_dbl": "block"}.get(
            row["candidate"])
        a = annots.get((base, label)) if label else None
        row["annotation"] = list(a) if a else None
        row["annotation_agrees"] = (None if a is None or "count" not in row
                                    else row["count"] == list(a))
        if row["annotation_agrees"] is False:
            row["ok"] = False
            row["why"] = (row["why"] + "; " if row["why"] else "") + (
                "measured %s against the file's own %s" % (row["count"], list(a)))
    return {"rows": rows, "prime": MAG_PRIME,
            "ok": bool(rows) and all(r["ok"] for r in rows)}


# ===========================================================================
# section: rank (the bottom row's tensor)
# ===========================================================================

def cross_product_identity():
    """(ok, detail) -- (m7,m8,m9) is the cross product of columns 1 and 2 of T."""
    T = build_T()
    a = [T[0][0], T[1][0], T[2][0]]
    b = [T[0][1], T[1][1], T[2][1]]
    cross = [a[1] * b[2] - a[2] * b[1],
             a[2] * b[0] - a[0] * b[2],
             a[0] * b[1] - a[1] * b[0]]
    ref = reference_polys()
    want = [ref["m7"], ref["m8"], ref["m9"]]
    return cross == want, [c.text(VARS) for c in cross]


def cross_slice_space():
    """The three matrices E_k with (a x b)_k = a^T E_k b, built from the formula.

    Not typed in as nine numbers each: `no_rank4` decides a question about this
    space, so the space is generated from the same cross-product formula that
    `cross_product_identity()` checks the bottom row against. Row-major 3x3.
    """
    out = []
    for k in range(3):
        E = [0] * 9
        i, j = (k + 1) % 3, (k + 2) % 3
        E[3 * i + j] = 1
        E[3 * j + i] = -1
        out.append(E)
    return out


def _rank1_set(p):
    """{canonical 9-tuple: True} for every rank-1 3x3 matrix over GF(p),
    normalised so the first nonzero entry is 1."""
    out = {}
    for u in itertools.product(range(p), repeat=3):
        if not any(u):
            continue
        for v in itertools.product(range(p), repeat=3):
            if not any(v):
                continue
            m = tuple((u[i] * v[j]) % p for i in range(3) for j in range(3))
            out[_canon(m, p)] = True
    return out


def _canon(m, p):
    lead = next((x for x in m if x % p), None)
    if lead is None:
        return m
    inv = pow(lead, p - 2, p)
    return tuple(x * inv % p for x in m)


def no_rank4(p):
    """(possible, examined) -- is a rank-4 decomposition of the cross product's
    tensor consistent with its slice space over GF(p)?

    A rank-r decomposition `a x b = sum_r c_r (alpha_r . a)(beta_r . b)` makes
    every output slice a combination of the r rank-1 matrices
    `alpha_r beta_r^T`, so the slice space -- here the whole 3-dimensional space
    L of matrices `E_i` of the cross product -- lies inside a space V spanned by
    r rank-1 matrices, with dim V <= r.

    For r = 4: dim V is 3 or 4. If 3 then V = L, and L would have to contain a
    rank-1 matrix. If 4 then V = L + <X> for some X outside L, and V must be
    spanned by its own rank-1 elements. Both are decidable by enumeration, and
    both are enumerated here -- X ranges over the projective points of the
    6-dimensional quotient, exhaustively.
    """
    L = [[x % p for x in r] for r in cross_slice_space()]
    if rank_p([r[:] for r in L], p) != 3:
        raise ValueError("the cross product's slice space is not 3-dimensional "
                         "over GF(%d)" % p)
    rank1 = _rank1_set(p)

    # case dim V = 3: does L itself contain a rank-1 element?
    for co in itertools.product(range(p), repeat=3):
        if not any(co):
            continue
        m = tuple(sum(co[i] * L[i][j] for i in range(3)) % p for j in range(9))
        if _canon(m, p) in rank1:
            return True, "L contains a rank-1 element %s" % (m,)

    # case dim V = 4: enumerate X modulo L, projectively. Enumerating GF(p)^9
    # would be p^9; a complement of L is 6-dimensional, and every 4-dimensional
    # V containing L is L + <X> for exactly one projective point X of it.
    #
    # The complement is the three diagonal units plus one unit from each
    # off-diagonal pair. NOT the symmetric matrices: in characteristic 2 the
    # alternating matrices are themselves symmetric, so that choice is not a
    # complement at all -- it fails the rank test below, which is why the test
    # is here.
    comp, examined = [], 0
    for i, j in ((0, 0), (1, 1), (2, 2), (2, 1), (0, 2), (1, 0)):
        e = [0] * 9
        e[3 * i + j] = 1
        comp.append(e)
    if rank_p([r[:] for r in L] + [r[:] for r in comp], p) != 9:
        raise ValueError("the chosen complement of L is not one over GF(%d)" % p)

    for co in itertools.product(range(p), repeat=6):
        if not any(co):
            continue
        lead = next(x for x in co if x)
        if lead != 1:                              # projective: first nonzero = 1
            continue
        X = [sum(co[i] * comp[i][j] for i in range(6)) % p for j in range(9)]
        examined += 1
        V = [r[:] for r in L] + [X]
        # the rank-1 elements of V, and the dimension they span
        found = []
        for cs in itertools.product(range(p), repeat=4):
            if not any(cs):
                continue
            m = tuple(sum(cs[i] * V[i][j] for i in range(4)) % p
                      for j in range(9))
            if _canon(m, p) in rank1:
                found.append(list(m))
        if found and rank_p(found, p) >= 4:
            return True, "V = L + <%s> is spanned by its rank-1 elements" % (X,)
    return False, "examined %d complements, none spanned by rank-1 elements" % examined


def _in_span(poly, gens):
    """Is `poly` a Q-combination of `gens`? Exact."""
    gens = list(gens)
    mons = sorted({m for g in gens for m in g.c} | set(poly.c))
    rows = [[g.c.get(m, Fraction(0)) for m in mons] for g in gens]
    r0 = rref_q([r[:] for r in rows])[0]
    r1 = rref_q(rows + [[poly.c.get(m, Fraction(0)) for m in mons]])[0]
    return r0 == r1


def bilinear_census(row_fn):
    """One bottom-row program, taken apart: how many products are bilinear?

    Two things are computed for the five-product scheme, and the same two for the
    shipped one, so "the shipped row spends six" is a measurement here rather
    than a remark. First, how many products have one factor in span(column 1) and
    the other in span(column 2) -- the rest are the cost of *forming* column 2,
    which both routes pay. Second, whether each of m7, m8, m9 is a Q-combination
    of those products, since otherwise a count of them decomposes nothing.
    """
    T = build_T()
    col1 = [T[0][0], T[1][0], T[2][0]]
    col2 = [T[0][1], T[1][1], T[2][1]]
    PF = PolyField()
    rec = Recorder()
    row_fn(*[RecElt(_pv(i), rec, PF) for i in range(6)])

    bilinear, other, detail = [], [], []
    for a, b in rec.products:
        ab = _in_span(a, col1) and _in_span(b, col2)
        ba = _in_span(b, col1) and _in_span(a, col2)
        (bilinear if (ab or ba) else other).append(a * b)
        detail.append({"a": a.text(VARS), "b": b.text(VARS),
                       "bilinear_in_the_two_columns": ab or ba})

    ref = reference_polys()
    spanned = {k: _in_span(ref[k], bilinear) for k in ("m7", "m8", "m9")}
    return {
        "program": row_fn.__name__,
        "total_products": rec["M"] + rec["S"],
        "bilinear": len(bilinear),
        "building_column_2": len(other),
        "row_in_span_of_the_bilinear_products": spanned,
        "ok": all(spanned.values()),
        "detail": detail,
    }


def section_rank(primes=(2, 3, 5), verbose=False):
    """The bottom row is a cross product; its bilinear floor is exactly 5."""
    idok, cross = cross_product_identity()
    decs = [bilinear_census(row3_rank5), bilinear_census(row3_shipped)]
    per_p = []
    for p in primes:
        possible, why = no_rank4(p)
        per_p.append({"p": p, "rank4_possible": possible, "detail": why})
    five = next(d for d in decs if d["program"] == "row3_rank5")
    return {
        "cross_identity": idok, "cross": cross,
        "decompositions": decs,
        "per_prime": per_p,
        "floor": 5 if all(not x["rank4_possible"] for x in per_p) else None,
        "attained": five["bilinear"],
        "ok": (idok and all(d["ok"] for d in decs) and five["bilinear"] == 5
               and all(not x["rank4_possible"] for x in per_p)),
    }


# ===========================================================================
# printing
# ===========================================================================

def _w(s):
    sys.stdout.write(s)


def print_source(r):
    _w("\n  THE BLOCK'S OWN DEFINITIONS, READ FROM THE SOURCE\n\n")
    _w("    T, built here from `multiply by w, reduce mod up`:\n")
    for k in sorted(r["t_entries"], key=lambda s: int(s[1:])):
        _w("      %-3s = %s\n" % (k, r["t_entries"][k]))
    _w("\n    d = det(T) equals the 5x5 Sylvester Res(w,up): %s\n"
       % ("yes" if r["det_is_resultant"] else "NO"))
    _w("\n    files carrying a `//| m1= ... |` block: %d\n" % r["files_with_block"])
    for f in r["files"]:
        _w("      %-58s %d entries, %s\n"
           % (f["file"], f["entries"],
              "all agree with adj(T)" if not f["disagree"]
              else "DISAGREE: " + ",".join(f["disagree"])))
        _w("        determinant line %s%s\n"
           % (f["det"],
              (";  op-count comments " +
               ", ".join("%s %dm %ds %da" % tuple(a) for a in f["annotations"]))
              if f["annotations"] else ""))
    _w("\n    the concrete-field reference and the polynomial reference "
       "disagreed %d times in 50x13 comparisons\n"
       % r["field_reference_mismatches"])
    for p in r["problems"]:
        _w("    PROBLEM %s\n" % p)


def _gives_warning(rows):
    """The like-for-like groups, computed from the rows' own claim sets.

    Printed because the table invites exactly one wrong reading: `rank5_7` costs
    12M and `shipped_7` costs 16M, but `rank5_7` does not form `d` and the two are
    not the same job. Grouping by the exact set of values returned, and naming the
    cheapest and dearest in each group, is what makes the honest comparison
    visible instead of leaving it to be noticed.
    """
    groups = {}
    for row in rows:
        groups.setdefault(tuple(row["claims"]), []).append(row)
    parts = []
    for claims, grp in sorted(groups.items(), key=lambda kv: -len(kv[0])):
        if len(grp) < 2:
            continue
        grp = sorted(grp, key=lambda x: x["equiv"])
        parts.append("{%s} " % ",".join(claims) + " < ".join(
            "%s %da" % (x["name"], x["equiv"]) for x in grp))
    if not parts:
        return "no two rows here return the same set"
    return "\n      " + "\n      ".join(parts)


def print_table(r, title, verbose=False):
    _w("\n  %s\n\n" % title)
    _w("    %-16s %-9s %5s %4s %3s %4s %6s   %-18s %s\n"
       % ("candidate", "verified", "gives", "M", "S", "A", "equiv", "claimed",
          "repo comment"))
    for row in r["rows"]:
        exp = ("%dM %dS %dA %s" % (row["expect"][0], row["expect"][1],
                                   row["expect"][2],
                                   "ok" if row["expect_agrees"] else "DIFFERS")
               if row["expect"] else "-- none --")
        ann = "--"
        if "annotation" in row:
            a = row["annotation"]
            ann = ("%s: %s" % (a["where"],
                               "absent" if a["value"] is None
                               else ("%dm %ds %da %s"
                                     % (a["value"][0], a["value"][1],
                                        a["value"][2],
                                        "ok" if a["agrees"] else "DIFFERS"))))
        _w("    %-16s %-9s %5d %4d %3d %4d %6d   %-18s %s\n"
           % (row["name"], "yes" if row["ok"] else "NO", len(row["claims"]),
              row["M"], row["S"], row["A"], row["equiv"], exp, ann))
    _w("\n    equiv = 3*(M+S) + A, the thesis's 1M:3A scale (chapter4.tex:817)\n")
    _w("    gives = how many of the thirteen values (m1..m9, d, sp0..sp2) the\n"
       "      program returns, all of them verified. Rows with different `gives`\n"
       "      are NOT comparable; the like-for-like groups, cheapest first, are%s\n"
       % _gives_warning(r["rows"]))
    _w("    every row also verified as a polynomial identity in Z[t,up], so it "
       "holds in every characteristic\n")
    if r.get("not_established"):
        _w("\n    NOT ESTABLISHED HERE\n")
        for line in r["not_established"]:
            _w("      %s\n" % line)
    if r.get("lower_half"):
        lh = r["lower_half"]
        _w("    lower half (region minus the top block, which is not a program "
           "on its own):\n      measured %dM %dS %dA against the file's own %s"
           " -- %s\n"
           % (lh["measured"][0], lh["measured"][1], lh["measured"][2],
              ("%dm %ds %da" % tuple(lh["annotation"])) if lh["annotation"]
              else "(no comment found)",
              "agrees" if lh["agrees"] else "DIFFERS"))
    for row in r["rows"]:
        if verbose or not row["ok"]:
            _w("      %-16s claims %s; t-by-t products %d (%d survive up -> 0)\n"
               % (row["name"], ",".join(row["claims"]), row["t_by_t"],
                  row["t_by_t_up0"]))
            for f in row["fails"]:
                _w("        FAIL %s\n" % (f,))


def print_span(r):
    _w("\n  THE NINE ENTRIES AS QUADRATIC FORMS IN (t1,t4,t7)\n\n")
    _w("    ambient space of t-quadratics                 %d-dimensional\n"
       % r["ambient"])
    _w("    span at generic up, over Q(up0,up1,up2)       %d   (exact, "
       "fraction-free elimination)\n" % r["generic_rank_over_Q_of_up"])
    _w("    span at up -> 0, over Q                       %d\n"
       % r["rank_at_up0_over_Q"])
    _w("      basis:  %s\n" % "   |   ".join(r["basis_at_up0"]))
    _w("\n    at particular up over Q:  %s\n"
       % ", ".join("up=%s rank %d" % (tuple(x["up"]), x["rank"])
                   for x in r["at_up_over_Q"]))
    by_p = {}
    for x in r["at_up_over_Fp"]:
        by_p.setdefault(x["p"], []).append(x["rank"])
    _w("    over prime fields:        %s\n"
       % ", ".join("GF(%d) ranks %s" % (p, sorted(set(v)))
                   for p, v in sorted(by_p.items())))
    _w("\n    %s\n" % r["note"])


def print_bound(r):
    _w("\n  THE LOWER BOUND ON t-BY-t PRODUCTS, AT up -> 0\n\n")
    _w("    U = the span at up -> 0, 3-dimensional. Its basis is DERIVED from the\n")
    _w("    nine entries here, not written down -- everything below is computed\n")
    _w("    against whatever that derivation returns:\n")
    for nm, row in zip("abc", r["U_basis_derived"]):
        _w("      %s * (%s)\n" % (nm, row))
    _w("\n    A product of two t-linear forms is a reducible quadratic, so its\n")
    _w("    Hessian has rank <= 2. For the generic element of U:\n\n")
    _w("      det Hessian = %s\n" % r["hessian_det"])
    cv = r["hessian_cube_variable"]
    _w("      vanishes exactly on %s = 0 (a 2-dimensional subspace of U): %s\n"
       % (cv or "?",
          ("yes, the determinant is a multiple of %s^3" % cv)
          if r["hessian_det_is_multiple_of_a_cubed"] else "NOT ESTABLISHED"))
    _w("      -- valid in characteristic != 2 only: the coefficient of %s^3 is "
       "%s.\n" % (cv or "?", r["hessian_a3_coefficient"]))
    _w("\n    Exhaustive enumeration over GF(p), all ordered pairs of linear "
       "forms:\n\n")
    _w("      %-8s %6s %10s %8s %11s\n"
       % ("field", "dim U", "pairs", "in U", "their span"))
    for x in r["per_prime"]:
        _w("      %-8s %6d %10d %8d %11d\n"
           % ("GF(%d)" % x["p"], x["dim_U"], x["pairs"], x["in_U"], x["span"]))
    _w("\n    So the products that LIE in U span only %d dimensions. Three "
       "products\n"
       % max([x["span"] for x in r["per_prime"]] or [0]))
    _w("    whose span contained the 3-dimensional U would span exactly U, "
       "hence all\n    three would lie in U, hence span <= 2. Contradiction:\n")
    _w("\n      AT LEAST %s t-BY-t PRODUCTS ARE NEEDED.\n"
       % (r["bound"] if r["bound"] else "-- NOT DETERMINED --"))
    if r.get("at_other_up"):
        _w("\n    The specialisation is a choice, and it matters. A program that "
           "computes\n    the entries for every up computes them at any single "
           "up, so the bound may\n    be taken wherever it is best. The same "
           "enumeration at other up:\n\n")
        _w("      %-12s %9s %10s %12s %8s\n"
           % ("up", "span dim", "in span", "their span", "bound"))
        for x in r["at_other_up"]:
            _w("      %-12s %9d %10d %12d %8s\n"
               % (tuple(x["up"]), x["span_dim"], x["in_span"], x["their_span"],
                  x["bound"] if x["bound"] else "none"))
        _w("      over GF(%d)\n" % r["at_other_up"][0]["p"])
        got4 = [tuple(x["up"]) for x in r["at_other_up"] if x["bound"] == 4]
        none = [tuple(x["up"]) for x in r["at_other_up"] if not x["bound"]]
        _w("\n    %d of these %d specialisations give 4 -- %s --\n"
           "    and %d gives nothing at all: %s, where the products that lie in "
           "the span\n    already span it. So the bound is not an artefact of "
           "choosing up -> 0, but\n    neither is it available at every up.\n"
           % (len(got4), len(r["at_other_up"]),
              ", ".join(str(u) for u in got4), len(none),
              ", ".join(str(u) for u in none) or "none"))
    _w("\n    Four suffice, so the bound is tight in this specialisation: %s\n"
       % ", ".join(r["attaining"]["products"]))
    for name, sol in sorted(r["attaining"]["solutions"].items()):
        _w("      %-14s = %s  %s\n" % (name, sol["coeffs"],
                                       "solved" if sol["solved"] else "FAILED"))
    _w("\n    WHAT THIS DOES NOT PROVE. It bounds the products of two t-linear\n"
       "    forms in the up -> 0 specialisation. It is not a bound on the whole\n"
       "    program. Measured, per candidate:\n\n")
    _w("      %-16s %4s %10s %14s\n"
       % ("candidate", "M", "t-by-t", "survive up->0"))
    for name in sorted(r["census"]):
        c = r["census"][name]
        _w("      %-16s %4d %10d %14d\n"
           % (name, c["M"], c["t_by_t"], c["t_by_t_up0"]))
    sh = r["census"].get("shipped_7", {})
    if sh and r["bound"]:
        _w("\n    Every program in the table has exactly %d products surviving "
           "up -> 0, so\n    the bound of %d is attained by all of them and "
           "separates none of them.\n"
           % (sh["t_by_t_up0"], r["bound"]))
        _w("    The shipped block spends %dM. The bound speaks about %d of "
           "those %d and\n    says nothing whatever about the other %d -- "
           "including the %d further\n    t-by-t products that the "
           "specialisation kills. The gap between this\n    bound and the "
           "shipped count is %d multiplications wide and closing it is\n"
           "    not attempted here.\n"
           % (sh["M"], r["bound"], sh["M"], sh["M"] - r["bound"],
              sh["t_by_t"] - sh["t_by_t_up0"], sh["M"] - r["bound"]))
        _w("\n    Two claims were made about this bound and they disagreed. The "
           "first --\n    the nine entries span a 3-dimensional space, so at "
           "least 3 products are\n    needed -- is the crude dimension count, "
           "and it is true but weaker. The\n    second is the argument above, "
           "and it is the correct one: 4, not 3. The\n    enumeration is what "
           "settles it, and it is exhaustive in every field it\n    reports.\n")


def print_mag(r):
    _w("\n  THE SHIPPED FRAGMENTS' REAL TEXT, EXECUTED THROUGH maginterp.py\n\n")
    _w("    Statements are extracted from the .mag between two anchors and run\n")
    _w("    over GF(%d) by the same interpreter and cost model `opcount.py` uses.\n"
       % r["prime"])
    _w("    This is what makes these three rows measurements of the source.\n\n")
    _w("    %-15s %-9s %5s %4s %3s %4s  %-9s %-9s %s\n"
       % ("candidate", "located", "stmts", "M", "S", "A", "= transcr", "= comment",
          "values"))
    for row in r["rows"]:
        if not row.get("found"):
            _w("    %-15s %-9s  %s\n" % (row["candidate"], "NO", row["why"]))
            continue
        c = row["count"]
        _w("    %-15s %-9s %5d %4d %3d %4d  %-9s %-9s %s\n"
           % (row["candidate"], "yes", row["statements"], c[0], c[1], c[2],
              "yes" if row["count_agrees"] else "NO",
              {True: "yes", False: "NO", None: "--"}[row["annotation_agrees"]],
              "OK" if not row["values_wrong"]
              else "WRONG " + ",".join(row["values_wrong"])))
    for row in r["rows"]:
        if row.get("found"):
            _w("      %-15s %s lines %d-%d, `%s` .. `%s`\n"
               % (row["candidate"], row["file"],
                  row["statements_from_to"][0], row["statements_from_to"][1],
                  row["anchors"][0], row["anchors"][1]))
            _w("        gives %s\n" % ",".join(row["values"]))
        if not row["ok"] and row["why"]:
            _w("      PROBLEM %s: %s\n" % (row["candidate"], row["why"]))
    _w("\n    NOT COVERED BY THIS SECTION: shipped_9, region_shipped,\n")
    _w("    region_rank5, row3_shipped and every rank-5 variant. The first three\n")
    _w("    straddle the `d eq 0` guard so no single anchor pair is a program; the\n")
    _w("    rest exist nowhere in the repository as .mag. Those stay\n")
    _w("    transcriptions, pinned only by their values and by the file's own\n")
    _w("    `// total:` comment.\n")


def print_rank(r):
    _w("\n  THE BOTTOM ROW IS A CROSS PRODUCT, AND ITS BILINEAR FLOOR IS 5\n\n")
    _w("    (m7,m8,m9) = column1 x column2 of T, as polynomials: %s\n"
       % ("yes" if r["cross_identity"] else "NO"))
    for c in r["cross"]:
        _w("      %s\n" % c)
    _w("\n    each bottom-row program taken apart:\n\n")
    _w("      %-14s %8s %10s %14s %s\n"
       % ("program", "products", "bilinear", "build col 2", "row in their span"))
    for d in r["decompositions"]:
        _w("      %-14s %8d %10d %14d %s\n"
           % (d["program"], d["total_products"], d["bilinear"],
              d["building_column_2"],
              ", ".join("%s %s" % (k, "yes" if v else "NO") for k, v
                        in sorted(d["row_in_span_of_the_bilinear_products"]
                                  .items()))))
    _w("\n    rank-4 decomposition, by exhaustive search on the slice space:\n")
    for x in r["per_prime"]:
        _w("      %-9s rank 4 possible: %-5s  %s\n"
           % ("GF(%d)" % x["p"], "YES" if x["rank4_possible"] else "no",
              x["detail"]))
    _w("\n    So %s bilinear products is the floor and %d is what the "
       "five-product\n    scheme spends, so the floor is attained; the shipped "
       "row spends %d.\n"
       % (r["floor"] if r["floor"] else "-- NOT DETERMINED --", r["attained"],
          next(d["bilinear"] for d in r["decompositions"]
               if d["program"] == "row3_shipped")))
    _w("\n    This is a statement about programs that treat the two columns as\n"
       "    independent inputs. In the real block column 2 is a function of\n"
       "    column 1 and up, so a program may exploit that and the floor does\n"
       "    not transfer to it. Not proved over Q either: a rational rank-4\n"
       "    decomposition would need a common denominator divisible by every\n"
       "    prime refuted above.\n")


# ===========================================================================
# CLI
# ===========================================================================

SECTIONS = ("source", "mag", "table", "region", "span", "bound", "rank")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--section", nargs="*", default=None,
                    help="sections to run; default all of %s" % ", ".join(SECTIONS))
    ap.add_argument("--list", action="store_true",
                    help="candidates, fields and sections")
    ap.add_argument("--trials", type=int, default=200,
                    help="random input tuples per field (default 200)")
    ap.add_argument("--seed", type=int, default=20260819)
    ap.add_argument("--fields", default=None,
                    help="comma-separated field sizes, overriding the default set")
    ap.add_argument("--primes", default="2,3,5,7,11",
                    help="primes for the exhaustive span/bound enumeration")
    ap.add_argument("--rank-primes", dest="rank_primes", default="2,3,5",
                    help="primes for the exhaustive rank-4 search (5 takes ~10s, "
                         "7 is far slower and is not run by default)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)

    fields = None
    if a.fields:
        want = [int(t) for t in a.fields.split(",") if t.strip()]
        fields, unknown = [], []
        for q in want:
            k = q.bit_length() - 1
            if q == (1 << k) and k in GF2k.MOD:
                fields.append(GF2k(k))
            elif _is_prime(q):
                fields.append(Fp(q))
            else:
                unknown.append(q)
        if unknown:
            print("cannot build a field of size %s; char-2 sizes available: %s"
                  % (unknown, [1 << k for k in sorted(GF2k.MOD)]))
            return 2
    primes = tuple(int(t) for t in a.primes.split(",") if t.strip())
    rprimes = tuple(int(t) for t in a.rank_primes.split(",") if t.strip())

    if a.list:
        print("\n  candidates\n")
        for c in CANDIDATES:
            print("    %-16s %d inputs, group %-7s claimed %s"
                  % (c.name, c.nargs, c.group,
                     ("%dM %dS %dA" % c.expect) if c.expect else "--"))
            print("        %s" % c.doc)
        print("\n  fields: %s"
              % ", ".join(F.name for F in (fields or default_fields())))
        print("  sections: %s" % ", ".join(SECTIONS))
        print("\n  a claimed count is the commissioning session's figure, not "
              "ground truth;\n  where a formula file annotates the same "
              "fragment, that comment is parsed\n  and compared too.\n")
        return 0

    chosen = list(SECTIONS)
    if a.section:
        unknown = [s for s in a.section if s not in SECTIONS]
        if unknown:
            print("unknown section(s): %s; known: %s"
                  % (", ".join(unknown), ", ".join(SECTIONS)))
            return 2
        chosen = [s for s in SECTIONS if s in a.section]

    # The fields must be fields before anything is verified over them.
    fl = fields if fields is not None else default_fields()
    badf = validate_fields(fl, _Rng(a.seed))
    results = {"field_problems": badf,
               "fields": [F.name for F in fl]}
    if badf:
        print("  the field arithmetic is broken, so nothing below would mean "
              "anything:")
        for name, why in badf:
            print("    %s: %s" % (name, why))
        return 1

    if "source" in chosen:
        results["source"] = section_source(a.verbose)
    if "mag" in chosen:
        results["mag"] = section_mag(a.verbose)
    if "table" in chosen:
        results["table"] = section_table("entries", fields, a.trials, a.seed)
    if "region" in chosen:
        results["region"] = section_table("region", fields, a.trials, a.seed)
    if "span" in chosen:
        results["span"] = section_span(primes, a.verbose)
    if "bound" in chosen:
        results["bound"] = section_bound(primes, a.verbose)
    if "rank" in chosen:
        results["rank"] = section_rank(rprimes, a.verbose)

    if a.json:
        json.dump(results, sys.stdout, indent=1, default=str)
        sys.stdout.write("\n")
    else:
        _w("\n  %d fields validated (a^(q-1) = 1, distributivity, char*1 = 0):"
           " %s\n" % (len(fl), ", ".join(F.name for F in fl)))
        if "source" in results:
            print_source(results["source"])
        if "mag" in results:
            print_mag(results["mag"])
        if "table" in results:
            print_table(results["table"],
                        "CANDIDATES, VERIFIED AND COUNTED", a.verbose)
        if "region" in results:
            print_table(results["region"],
                        "THE WHOLE REGION: adjugate + d + sp = M*vt", a.verbose)
        if "span" in results:
            print_span(results["span"])
        if "bound" in results:
            print_bound(results["bound"])
        if "rank" in results:
            print_rank(results["rank"])
        _w("\n" + "=" * 72 + "\n")
        for s in chosen:
            r = results.get(s, {})
            _w("  %-5s %s\n" % ("ok" if r.get("ok") else "PROBLEM", s))
        _w("=" * 72 + "\n\n")

    return 0 if all(results.get(s, {}).get("ok") for s in chosen) else 1


if __name__ == "__main__":
    sys.exit(main())
