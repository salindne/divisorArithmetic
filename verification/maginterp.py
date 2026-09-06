"""maginterp.py -- executes the .mag formula source directly.

No formula is transcribed into Python, so no transcription can introduce a bug or
hide one.  Every family in the repository is in scope, both models and both
genuses.

Statements supported, which is everything the formula files and their dispatchers
use:

    <name> := <expr>;                        (may span several source lines)
    R<x> := PolynomialRing(...);             (binds x; see _polynomial_ring)
    if <cond> then ... elif ... else ... end if;
    return <expr>, ...;
    assert <cond>;
    "literal";  and  if ADD_DEBUG then "literal"; end if;

Debug prints are kept, not skipped: they name the computation path taken and are
the branch-coverage instrumentation `driver.py` reports against.  Expressions are
parsed by `_parser`.

Two conventions that are silent when wrong:

  * Integer literals stay Python ints, never field elements; see `ev`, where the
    reason is spelled out.  Arithmetic still coerces where an int meets a field
    element or polynomial, so `2*v` is zero in characteristic 2 and `-1 == 1`,
    exactly as Magma.
  * `/` is field division and a zero divisor raises ZeroDivisionError rather than
    being smoothed over.  Errata E1 is exactly such a division and has to surface.
"""
import re

from _parser import parse_cond, parse_expr, tokens, ParseError  # noqa: F401
from poly import Poly

# Operation counter. The conventions are load-bearing: the audit's op-count
# scripts read these, and they mirror the "4m 2s 32a" comments in the formula
# files themselves. Multiplication by an integer literal counts as an addition;
# field division is one inversion plus one multiplication; squaring is S.
COUNT = {}

# Counting conventions, opted into by a caller and all defaulting to OFF, so the
# interpreter counts as it always has unless something sets them.
# verification/opcount.py is what does, and it owns the thesis's conventions.
# Set here rather than there because the multiplication and division sites are
# inside `ev`, and monkeypatching an evaluator from outside works until someone
# reorders a branch.
#
# CONSTS  names declared `//Constant:` in the file being counted. A product with
#         one is a multiplication by a curve coefficient: C, not M.
# IGNORED names declared `//Ignore:`. A product with one costs nothing, which is
#         only sound on the domain the file's banner declares.
# DIV_LITERAL_AS_ADD
#         `x/2` is a halving, which this thesis counts as one addition
#         (chapter6.tex:2333), and `1/x` is an inversion with no product. Without
#         it every `/` is charged I+M, right for `sp0/dw0` and wrong for both.
# INT_ARITH_FREE
#         `+`/`-` between two plain integers is bookkeeping, not a field
#         operation, so it is not an A. The split model's divisors carry a
#         balancing weight: every addition runs `n := n1 + n2 - 2` and every
#         doubling `np := n + n - 2` on small integers in [0, g], and the
#         `Degree(...)` arithmetic in the balancing branches is the same thing.
#         Charged as field additions they put a flat +2A on every split row,
#         which is precisely the disagreement against all four published
#         arbitrary cells that this flag explains. Testing by operand TYPE is
#         sound because a field element is an `FFElement` in every field this
#         repository builds and never a Python `int`. Testing by syntax, the
#         `node[1][0] == "int"` form used for products just above, would not
#         work: `n1 + n2` has no integer literal in it.
CONSTS = set()
IGNORED = set()
DIV_LITERAL_AS_ADD = False
INT_ARITH_FREE = False


def _plain_int(x):
    """A Python integer, not a field element and not a bool.

    `bool` subclasses `int`, so without excluding it a comparison result reaching
    an arithmetic node would be silently free.
    """
    return isinstance(x, int) and not isinstance(x, bool)


def _bump(k, n=1):
    COUNT[k] = COUNT.get(k, 0) + n


def _leafname(node):
    """The variable name a factor reduces to, seeing through unary minus.

    `-yn2*W2` parses as ("*", ("neg", ("var","yn2")), ("var","W2")), so a bare
    node[1][0] == "var" test misses a declared constant behind a minus sign and
    charges M where the cost is C.
    """
    while node[0] == "neg":
        node = node[1]
    return node[1] if node[0] == "var" else None


# Magma builtins the cleaned formula bodies use. Measured: IsZero 1347, Coeff 460,
# ExactQuotient 126, LeadingCoefficient 57, Degree 42, IsOne 18. One table serves
# both levels: 114 of the 126 Deg* functions are pure field arithmetic and 12
# (genus-3 split ADD) work on polynomials, and poly.Poly supplies every one of
# these operations under the same names.
def _is_zero(x):
    # Plain ints reach here: `IsZero(0)`, and constants arithmetic left as ints.
    if isinstance(x, int):
        return x == 0
    return x.is_zero()


def _is_one(x):
    if isinstance(x, int):
        return x == 1
    return x.is_one()


def _degree(p):
    if isinstance(p, int):
        return 0 if p else -1
    return p.deg


def _coeff(p, i):
    return p.coeff(int(i) if isinstance(i, int) else _as_int(i))


def _leading(p):
    return p.lc()


def _exact_quotient(a, b):
    return a.exact_quotient(b)


def _gf(F, q):
    """Magma's `GF(q)`: check the size against the one field threaded as F.

    Constructing a second field would give elements the surrounding arithmetic
    could not mix with, and a mismatch means the file is asking for a field the
    caller did not supply.
    """
    q = _as_int(q)
    if q != F.q:
        raise ParseError("GF(%d) requested but the run is over GF(%d)" % (q, F.q))
    return F


def _polynomial_ring(F, base=None):
    """Magma's `PolynomialRing(...)`, as the ring's own indeterminate.

    Returning `x` rather than a ring object is what makes
    `R<x> := PolynomialRing(GF(q));` usable: the interpreter binds the
    angle-bracket name to this value, which is what the source then uses.
    """
    return Poly.x(F)


def _factorization(F, p):
    """Magma's `Factorization` for the one shape the split files need.

    The split-model Precompute functions factor a monic quadratic for the values
    attached to the places at infinity: y_g solves x^2 + h_g*x - f_{2g+2}.  Only
    that case is supported; anything else raises rather than returning a plausible
    wrong answer.  The result mimics Magma's shape, a 1-based sequence of
    <factor, multiplicity> pairs, so `Factorization(...)[2][1]` works unchanged.

    Ordering is NOT guessed.  `ROOT_PIN`, when set, names the root `[2][1]` must
    yield, which is exact; `whitebox.py` sets it from the case's own basis
    polynomial V, whose leading coefficient is y_{g+1}.  Neither global ordering
    works for every case: measured over 1,258 constructed cases, "second" fails
    247, all in characteristic 2, and "first" fails 332, all over odd primes.
    `ROOT_CHOICE` is the fallback for generated inputs, where no V is given, and
    `driver.py` establishes it by running both settings against the independent
    reference rather than assuming Magma's internal factor order.
    """
    if ROOT_PIN[0] is not None:
        want = ROOT_PIN[0]
        other = -want - p.coeff(1)          # the two roots sum to -b
        one = F.one
        return [[Poly.from_coeffs(F, [-other, one]), 1],
                [Poly.from_coeffs(F, [-want, one]), 1]]
    if not hasattr(p, "deg") or p.deg != 2 or not p.is_monic():
        raise ParseError("Factorization is supported only for a monic quadratic, "
                         "got %r" % (p,))
    b, c = p.coeff(1), p.coeff(0)
    roots = _quadratic_roots(F, b, c)
    if roots is None:
        raise _Irreducible("x^2 + %s*x + %s has no root in GF(%d)" % (b, c, F.q))
    r1, r2 = roots
    if ROOT_CHOICE[0] == "second":
        r1, r2 = r2, r1
    one = F.one
    return [[Poly.from_coeffs(F, [-r1, one]), 1],
            [Poly.from_coeffs(F, [-r2, one]), 1]]


class _Irreducible(Exception):
    """The quadratic defining the infinite places has no root in this field.

    Not a defect: the two places are conjugate over a quadratic extension, so the
    curve is not a split-model curve at all and the caller should skip it.  Its own
    type so a driver counts it as a skip rather than a failure.
    """


def _quadratic_roots(F, b, c):
    """Roots of x^2 + b*x + c in F, or None if it has none.

    Brute force over the field.  The fields in play are GF(2) to GF(32) and small
    primes, so enumeration is cheaper and more obviously correct than a
    characteristic-split formula, and it needs no char-2 branch, where the
    quadratic formula does not apply at all.
    """
    out = []
    for e in F.elements():
        if (e * e + b * e + c).is_zero():
            out.append(e)
    if not out:
        return None
    if len(out) == 1:
        return out[0], out[0]
    return out[0], out[1]


# Which root of the infinite-place quadratic `Factorization` returns first.
#
# "second" is not a guess. The source says "We pick the second solution from the
# factorization given by magma" and takes `Factorization(...)[2][1]`, and both
# orderings measured against the independent reference confirm it: over the
# negative reduced basis the arb genus-2 family agrees on 31 of 32 operations with
# "second" and 2 of 32 with "first", and ch2 agrees 28 of 32 against 2 of 32.
# Swapping them exchanges y and yn, hence the positive and negative reduced bases.
#
# A list so `driver.py` can flip it to re-derive this rather than trust it.
ROOT_CHOICE = ["second"]

# When set to a field element, `Factorization(...)[2][1]` yields exactly that root,
# making the choice exact instead of conventional. `whitebox.py` sets it per case
# from the case's own basis polynomial. None means fall back to ROOT_CHOICE.
ROOT_PIN = [None]

FIELD_BUILTINS = {
    "GF": _gf,
    "PolynomialRing": _polynomial_ring,
    "Factorization": _factorization,
}

BUILTINS = {
    "IsZero": _is_zero,
    "IsOne": _is_one,
    "Degree": _degree,
    "Coeff": _coeff,
    "Coefficient": _coeff,
    "LeadingCoefficient": _leading,
    "ExactQuotient": _exact_quotient,
}


def _as_int(v):
    """Coerce an evaluated index/exponent back to a Python int."""
    if isinstance(v, int):
        return v
    for attr in ("to_int", "lift", "value"):
        if hasattr(v, attr):
            got = getattr(v, attr)
            return int(got() if callable(got) else got)
    return int(str(v))


def _truthy(v):
    """Coerce a value to a bool for `if <expr> then`."""
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return v != 0
    if hasattr(v, "is_zero"):
        return not v.is_zero()
    return bool(v)


def _order_key(v):
    """Sort key for Magma's `lt/le/gt/ge` when the operands are polynomials.

    The genus-3 ramified ADD dispatchers open with `if D2[1] le D1[1] then`,
    commented "ensure u1 is always the larger polynomial", so this ordering decides
    which divisor reaches a mixed-degree function first, and those functions are
    not symmetric in their arguments.

    Degree dominates, which is the part Magma agrees with.  Equal degrees are broken
    deterministically by coefficient text; Magma's own tiebreak is not reproduced
    and need not be, since equal degrees send both divisors to the same same-degree
    function and addition is commutative.  `driver.py` checks that rather than
    assuming it: an operand order the formulas were sensitive to would show up as a
    mismatch.
    """
    if hasattr(v, "deg"):
        return (1, v.deg, tuple(str(v.coeff(i)) for i in range(v.deg, -1, -1)))
    return (0, 0, (str(v),))


def _cmp_ord(a, b, op):
    if hasattr(a, "deg") or hasattr(b, "deg"):
        ka, kb = _order_key(a), _order_key(b)
    else:
        ka, kb = a, b
    if op == "lt":
        return ka < kb
    if op == "le":
        return ka <= kb
    if op == "gt":
        return ka > kb
    return ka >= kb


_CMP = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "lt": lambda a, b: _cmp_ord(a, b, "lt"),
    "le": lambda a, b: _cmp_ord(a, b, "le"),
    "gt": lambda a, b: _cmp_ord(a, b, "gt"),
    "ge": lambda a, b: _cmp_ord(a, b, "ge"),
}


def ev(node, env, F, funcs=None):
    """Evaluate an expression or condition node.

    `funcs` lets a dispatcher call its sibling formula functions; without it such
    a call raises rather than silently returning nothing.
    """
    k = node[0]

    if k == "var":
        try:
            return env[node[1]]
        except KeyError:
            raise ParseError("undefined name %r" % node[1])
    if k == "int":
        # A Python int, NOT F(n). Coercing literals into the field makes every
        # index and exponent reduce modulo the characteristic: `Coeff(u,2)` becomes
        # `Coeff(u, F(2))`, and F(2) == 0 in characteristic 2, so it returns the
        # constant term; at genus 3 `Coeff(f,7)` reads coefficient 1. Odd fields
        # give the right answer by coincidence, which is how it stays hidden.
        # Arithmetic against field elements and polynomials still works, since both
        # coerce int operands (including via __radd__/__rsub__/__rmul__).
        return node[1]
    if k == "neg":
        return -ev(node[1], env, F, funcs)

    if k == "pow":
        b = ev(node[1], env, F, funcs)
        e = node[2]
        if e < 0:
            _bump("I")
            _bump("M", -e - 1)
            return b.inverse() ** (-e) if hasattr(b, "inverse") else b ** e
        if e == 2:
            _bump("S")
        else:
            _bump("M", e - 1)
        return b ** e

    if k == "call":
        name, argnodes = node[1], node[2]
        args = [ev(a, env, F, funcs) for a in argnodes]
        if name in BUILTINS:
            return BUILTINS[name](*args)
        if name in FIELD_BUILTINS:
            return FIELD_BUILTINS[name](F, *args)
        if funcs and name in funcs:
            return funcs[name](*args)
        raise ParseError("unknown function %r" % name)

    if k == "list":
        return [ev(e, env, F, funcs) for e in node[1]]

    if k == "index":
        base = ev(node[1], env, F, funcs)
        idx = _as_int(ev(node[2], env, F, funcs))
        # Magma sequences are 1-based.
        return base[idx - 1]

    if k == "cmp":
        op, a, b = node[1], ev(node[2], env, F, funcs), ev(node[3], env, F, funcs)
        return _CMP[op](a, b)
    if k == "and":
        return (_truthy(ev(node[1], env, F, funcs))
                and _truthy(ev(node[2], env, F, funcs)))
    if k == "or":
        return (_truthy(ev(node[1], env, F, funcs))
                or _truthy(ev(node[2], env, F, funcs)))
    if k == "not":
        return not _truthy(ev(node[1], env, F, funcs))

    a = ev(node[1], env, F, funcs)
    b = ev(node[2], env, F, funcs)
    if k == "*":
        if node[1][0] == "int" or node[2][0] == "int":
            _bump("A")
            return a * b
        if CONSTS or IGNORED:
            ln, rn = _leafname(node[1]), _leafname(node[2])
            if (ln in IGNORED) or (rn in IGNORED):
                return a * b                      # //Ignore: costs nothing
            if (ln in CONSTS) or (rn in CONSTS):
                _bump("C")
                return a * b
        _bump("M")
        return a * b
    if k == "/":
        if DIV_LITERAL_AS_ADD:
            if node[2][0] == "int":
                _bump("A")                        # x/2 is a halving
                return a / b
            if node[1][0] == "int":
                _bump("I")                        # 1/x, no product
                return a / b
        _bump("I")
        _bump("M")
        return a / b
    if k in ("+", "-"):
        if not (INT_ARITH_FREE and _plain_int(a) and _plain_int(b)):
            _bump("A")
        return a + b if k == "+" else a - b
    raise ParseError("unhandled node %r" % (k,))


def clean_body(path, fn):
    src = open(path).read()
    # Tolerate a space before ":=" and any trailing text after the closing paren:
    # the dispatchers are declared "ADD:= function(D1, D2, f, h)//startIGNORE", and
    # requiring ")" at end of line makes every one of them unfindable.
    m = re.search(r"^%s\s*:=\s*function\s*\((.*?)\)[^\n]*$(.*?)^end function;" % fn,
                  src, re.S | re.M)
    assert m, "%s not found in %s" % (fn, path)
    params = [p.strip() for p in m.group(1).split(",")]
    body = m.group(2)
    # Debug prints are NOT stripped: each names the computation path the formulas
    # just took, and `run` records it as the branch-coverage instrumentation. The
    # repository writes the guard two ways, `if ADD_DEBUG then` (1743 occurrences)
    # and `if (ADD_DEBUG) then` (70), so a strip of only the parenthesised form
    # removes exactly the genus-3 ramified family and coverage reads 0 branches out
    # of 0, looking like success. Both forms are matched in `_statement`.
    # Block comments FIRST. The genus-3 split files close theirs as "*///endIGNORE"
    # with no space, so a line-comment pass run first matches the "//" one character
    # early, eats the "*/" with it and orphans the "/*", silently breaking all 18
    # genus-3 split functions that carry such a block.
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    body = re.sub(r"//[^\n]*", "", body)          # line comments
    return params, body


def statements(body):
    """Join physical lines into logical statements ending in ';', 'then' or
    'end if;'."""
    out, buf = [], ""
    for raw in body.split("\n"):
        ln = raw.strip()
        if not ln:
            continue
        buf = (buf + " " + ln).strip() if buf else ln
        if buf.endswith(";") or buf.endswith("then"):
            # One physical line may carry several statements: the dispatchers open
            # with "u1 :=D1[1]; v1:= D1[2]; ...".
            for piece in _split_semis(buf):
                # "else <stmt>" and "elif ..." appear inline in the dispatchers,
                # e.g. `else u2:= D1[1];`. Peel the keyword off so the block
                # builder sees it on its own.
                m_else = re.match(r"^else\s+(?!if\b)(.+)$", piece)
                if m_else:
                    out.append("else")
                    out.append(m_else.group(1).strip())
                    continue
                m_ei = re.match(r"^else\s+(if\b.*)$", piece)
                if m_ei:
                    out.append("else")
                    out.append(m_ei.group(1).strip())
                    continue
                out.append(piece)
            buf = ""
    assert not buf, "dangling text %r" % buf[:120]
    return out


def _depth_delta(s, i):
    """Bracket-nesting change at position i, treating Magma tuples as brackets.

    `<` and `>` delimit tuples, and `Precompute` in the genus-2 negReduced nch2
    file returns `<<<f0,f1,...>,...>>`.  Uncounted, the commas inside read as depth
    zero and the return is torn into fragments starting with the unparsable
    `<<<f0`.  Safe because these files spell comparison `lt`/`le`/`gt`/`ge` as
    words; `<=` and `>=` are skipped explicitly so a stray one cannot unbalance the
    count.
    """
    ch = s[i]
    if ch in "([":
        return 1
    if ch in ")]":
        return -1
    if ch in "<>" and not (i + 1 < len(s) and s[i + 1] == "="):
        return 1 if ch == "<" else -1
    return 0


def _split_semis(s):
    """Split a joined line at top-level ';', keeping each terminator.

    Leaves `end if;` and one-line guarded prints intact, since those are matched
    as whole statements later.
    """
    if s.endswith("then") or s == "end if;" or "_DEBUG" in s:
        return [s]
    out, depth, cur = [], 0, ""
    for i, ch in enumerate(s):
        depth += _depth_delta(s, i)
        cur += ch
        if ch == ";" and depth == 0:
            out.append(cur.strip())
            cur = ""
    if cur.strip():
        out.append(cur.strip())
    return [x for x in out if x]


def _split_top(s):
    """Split on commas at bracket depth zero.

    `return Deg12ADDUP(u20,v20,u10,u11,v10,v11,ccs);` is one value, not seven; a
    naive split on "," tears the call apart into fragments that fail to parse.
    """
    out, depth, cur = [], 0, ""
    for i, ch in enumerate(s):
        depth += _depth_delta(s, i)
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [x.strip() for x in out if x.strip()]


class Block(list):
    pass


def _branch(lines, i):
    """Build statements from `i` until an else / elif / end if.

    Returns (block, index_of_terminator, terminator_text).  The caller seeing the
    terminator is what makes else a *sibling* of its if: recursing blindly on `if`
    buries the else inside the then-branch, so it runs only when the condition is
    true, exactly backwards.
    """
    blk = Block()
    while i < len(lines):
        ln = lines[i]

        if ln == "end if;":
            return blk, i, "end"
        if ln == "else":
            return blk, i, "else"
        m = re.match(r"^elif\s+(.*?)\s+then$", ln) or re.match(r"^elif\s*\((.*)\)\s*then$", ln)
        if m:
            return blk, i, ("elif", m.group(1).strip())

        m = re.match(r"^if\s+(.*?)\s+then$", ln) or re.match(r"^if\s*\((.*)\)\s*then$", ln)
        if m:
            # Collect the whole if / elif* / else? chain as sibling arms.
            arms = []
            cond_now = parse_cond(m.group(1).strip())
            i2 = i + 1
            while True:
                sub, j, term = _branch(lines, i2)
                arms.append((cond_now, sub))
                if isinstance(term, tuple) and term[0] == "elif":
                    cond_now = parse_cond(term[1])
                    i2 = j + 1
                    continue
                if term == "else":
                    sub2, j2, term2 = _branch(lines, j + 1)
                    arms.append((None, sub2))
                    assert term2 == "end", "unterminated else near %r" % lines[j2:j2 + 1]
                    j = j2
                break
            blk.append(("ifchain", arms))
            i = j + 1
            continue

        if ln == ";":
            i += 1
            continue

        # `R<x> := PolynomialRing(GF(q));` in every split-model Precompute. Only the
        # ring's generator is ever used, so that is what the angle-bracket name is
        # bound to: the arb and ch2 files build `x^2 + h3*x - f6` and factor it for
        # the values attached to the two places at infinity. In the nch2 files it is
        # dead code, the Factorization call being commented out and the root
        # hardcoded, and binding it costs nothing.
        m = re.match(r"^[A-Za-z_]\w*\s*<\s*(\w+)\s*>\s*:=\s*(PolynomialRing\(.*\));$",
                     ln)
        if m:
            blk.append(("set", m.group(1), parse_expr(m.group(2))))
            i += 1
            continue

        m = re.match(r"^assert\s+(.*);$", ln)
        if m:
            blk.append(("assert", parse_cond(m.group(1)), m.group(1)))
            i += 1
            continue

        m = re.match(r"^([A-Za-z_][A-Za-z_0-9]*)\s*:=\s*(.*);$", ln)
        if m:
            blk.append(("set", m.group(1), parse_expr(m.group(2))))
            i += 1
            continue

        m = re.match(r'^"([^"]*)";$', ln)
        if m:
            blk.append(("print", m.group(1)))
            i += 1
            continue

        m = re.match(r'^if\s*\(?[A-Za-z_0-9]*_DEBUG\)?\s*then\s*"([^"]*)";\s*end if;$', ln)
        if m:
            blk.append(("print", m.group(1)))
            i += 1
            continue

        m = re.match(r"^return\s+(.*);$", ln)
        if m:
            blk.append(("ret", [parse_expr(e) for e in _split_top(m.group(1))]))
            i += 1
            continue

        raise AssertionError("unparsed statement: %r" % ln)
    return blk, i, None


def build(lines, i=0):
    blk, j, term = _branch(lines, i)
    assert term in (None,), "unexpected %r at end of function" % (term,)
    return blk, len(lines)


class Ret(Exception):
    def __init__(self, vals):
        self.vals = vals


def run(blk, env, F, path, funcs=None):
    for st in blk:
        if st[0] == "set":
            env[st[1]] = ev(st[2], env, F, funcs)
            path.append(st[1])
        elif st[0] == "assert":
            if not _truthy(ev(st[1], env, F, funcs)):
                raise AssertionError("assertion failed: %s" % st[2])
        elif st[0] == "print":
            path.append("PRINT:" + st[1])
        elif st[0] == "ifchain":
            # arms are [(cond, block), ..., (None, block)] with None marking else.
            for cond, sub in st[1]:
                if cond is None or _truthy(ev(cond, env, F, funcs)):
                    run(sub, env, F, path, funcs)
                    break
        else:
            # A dispatcher's `return Deg12ADD(...)` evaluates to the callee's
            # whole tuple, so splice one level rather than returning a 1-tuple
            # wrapping it.
            vals = []
            for e in st[1]:
                v = ev(e, env, F, funcs)
                if isinstance(v, tuple):
                    vals.extend(v)
                else:
                    vals.append(v)
            raise Ret(vals)


class MagmaFn:
    def __init__(self, path, fn):
        self.path, self.name = path, fn
        self.params, body = clean_body(path, fn)
        self.stmts = statements(body)
        self.blk, n = build(self.stmts)
        assert n == len(self.stmts), (fn, n, len(self.stmts))

    def __call__(self, *args, path=None, funcs=None, F=None):
        """Invoke the function.

        `funcs` supplies sibling functions so a dispatcher can delegate to its Deg*
        cases.  `F` names the field explicitly; without it the field comes from
        whichever argument carries one, since the first parameter is not always a
        field element (dispatchers take polynomials, some functions lead with a bare
        weight).
        """
        if len(args) != len(self.params):
            raise AssertionError("%s expects %d args %r, got %d"
                                 % (self.name, len(self.params), self.params, len(args)))
        if F is None:
            for a in args:
                if hasattr(a, "F"):
                    F = a.F
                    break
            if F is None:
                raise AssertionError(
                    "%s: cannot infer the field from any argument; pass F="
                    % self.name)
        env = dict(zip(self.params, args))
        pth = [] if path is None else path
        # Bind the sibling table once. A raw `funcs[name](*args)` inside `ev` drops
        # funcs/F/path, which fails as soon as a Deg* case delegates further
        # (Deg12ADD -> Deg12ADDUP). Binding keeps one shared `path`, which is what
        # makes branch coverage account for branches inside nested calls.
        bound = _bind(funcs, pth, F) if funcs else None
        try:
            run(self.blk, env, F, pth, bound)
        except Ret as r:
            return tuple(r.vals)
        raise AssertionError("%s fell off the end" % self.name)


class _BoundTable(dict):
    """A sibling table whose entries already carry path/funcs/F.

    Its own type so `_bind` recognises its own output.  Without that, a call chain
    of depth three (ADD -> DBL -> Deg2DBL, which the PR5 equal-divisor dispatch
    creates) re-binds the already-bound table inside DBL's __call__, and the second
    wrapper passes path=/funcs=/F= keywords to the first wrapper's positional-only
    closure: TypeError.
    """


def _bind(funcs, path, F):
    """Sibling table whose entries already carry `path`, the table itself and F.

    Self-referential on purpose: a bound callee is given the same bound table, so
    delegation nests to any depth and every branch label lands in one `path`.

    Idempotent: an already-bound table is returned unchanged, which keeps the one
    shared `path` list and the one F it was bound with, and that shared path is
    what makes branch coverage account for branches inside nested calls.
    """
    if isinstance(funcs, _BoundTable):
        return funcs

    bound = _BoundTable()

    def wrap(fn):
        def call(*args):
            return fn(*args, path=path, funcs=bound, F=F)
        return call

    for name, fn in funcs.items():
        bound[name] = wrap(fn)
    return bound


def function_names(path):
    """Every `Name := function(...)` defined in a .mag file, in source order.

    Tolerates both spacings the repo uses, `Deg1ADD:= function` and
    `ADD := function`.
    """
    src = open(path).read()
    return [m.group(1) for m in
            re.finditer(r"^([A-Za-z_][A-Za-z_0-9]*)\s*:=\s*function\s*\(", src, re.M)]


_DISCOVER_CACHE = {}


def discover(path, only=None, skip_unparsable=True):
    """{name: MagmaFn} for a .mag file, discovering the names itself.

    `skip_unparsable=True` returns what it can and records the rest in
    `.unparsable`, so a driver reports partial coverage rather than dying on the
    first dispatcher it cannot read.

    Memoised on (path, only, skip_unparsable): callers replay hundreds of cases
    against the same few files, and re-parsing every function of a 9,000-line
    dispatcher per case measured 20.7s of whitebox.py's 21.4s.  A fresh dict comes
    back each time because callers mutate what they get (driver.py updates it), and
    MagmaFn is safe to share, storing only path, name and parsed statements.
    """
    key = (path, None if only is None else tuple(sorted(only)), skip_unparsable)
    hit = _DISCOVER_CACHE.get(key)
    if hit is None:
        out, bad = {}, {}
        for name in function_names(path):
            if only and name not in only:
                continue
            try:
                out[name] = MagmaFn(path, name)
            except Exception as e:
                if not skip_unparsable:
                    raise
                bad[name] = "%s: %s" % (type(e).__name__, e)
        hit = (out, bad)
        _DISCOVER_CACHE[key] = hit

    fns, bad = hit
    discover.unparsable = dict(bad)
    return dict(fns)


if __name__ == "__main__":
    # Parse coverage across every formula file, so a regression in the parser shows
    # up as a number rather than as a driver that quietly tests less.
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    ok, bad = 0, []
    for path in sorted(root.glob("g*/*[lM]odel/**/g*Formulas/*.mag")):
        for name in function_names(str(path)):
            try:
                MagmaFn(str(path), name)
                ok += 1
            except Exception as exc:                       # noqa: BLE001
                bad.append("%s::%s: %s" % (path.name, name, exc))
    print("%d functions parsed, %d failed" % (ok, len(bad)))
    for line in bad:
        print("   ", line)
