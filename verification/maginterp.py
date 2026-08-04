"""maginterp2.py -- generalisation of magma-interp.py to ANY of the four
ramified-G3 formula files.  Executes the Magma source text directly so that no
hand transcription can introduce or hide a bug.

Grammar supported (all the Deg_ij ADD / Deg_i DOUBLE bodies use):
    <name> := <expr>;              (may span several source lines)
    if (<cond>) then ... end if;
    return <expr>, ... ;
    if (ADD_DEBUG|DBL_DEBUG) then "..."; end if;      (skipped)
    <cond> ::= C {and C},  C ::= <expr> eq 0 | <expr> ne 0
Integer literals are coerced into the field of the incoming arguments, so 2
vanishes in characteristic 2 and -1 == 1, exactly as Magma.
`/` is field division; a zero divisor raises ZeroDivisionError.
"""
import re
import sys

HERE = "/private/tmp/claude-501/-Users-s3b-Dev-divisor-arithmetic/f1be528a-632c-4bff-89ce-61f41f8f0235/scratchpad/g3ramaudit"
REPO = ("/private/tmp/claude-501/-Users-s3b-Dev-divisor-arithmetic/"
        "f1be528a-632c-4bff-89ce-61f41f8f0235/scratchpad/g3ram/")
sys.path.insert(0, HERE)

from _parser import parse_cond, parse_expr, tokens, ParseError  # noqa: F401

# Operation counter. The conventions are load-bearing: the audit's op-count
# scripts read these, and they mirror the "4m 2s 32a" comments in the formula
# files themselves. Multiplication by an integer literal counts as an addition;
# field division is one inversion plus one multiplication; squaring is S.
COUNT = {}


def _bump(k, n=1):
    COUNT[k] = COUNT.get(k, 0) + n


# Magma builtins the cleaned formula bodies actually use. Measured: IsZero 1347,
# Coeff 460, ExactQuotient 126, LeadingCoefficient 57, Degree 42, IsOne 18.
# The same table serves both levels, because 114 of the 126 Deg* functions are
# pure field arithmetic while 12 (genus-3 split ADD) work on polynomials, and
# poly.Poly supplies every one of these operations under the same names.
def _is_zero(x):
    return x.is_zero()


def _is_one(x):
    return x.is_one()


def _degree(p):
    return p.deg


def _coeff(p, i):
    return p.coeff(int(i) if isinstance(i, int) else _as_int(i))


def _leading(p):
    return p.lc()


def _exact_quotient(a, b):
    return a.exact_quotient(b)


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


_CMP = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "lt": lambda a, b: a < b,
    "le": lambda a, b: a <= b,
    "gt": lambda a, b: a > b,
    "ge": lambda a, b: a >= b,
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
        return F(node[1])
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
        if funcs and name in funcs:
            return funcs[name](*args)
        raise ParseError("unknown function %r" % name)

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
        _bump("M")
        return a * b
    if k == "/":
        _bump("I")
        _bump("M")
        return a / b
    if k in ("+", "-"):
        _bump("A")
        return a + b if k == "+" else a - b
    raise ParseError("unhandled node %r" % (k,))


def clean_body(path, fn):
    src = open(path).read()
    m = re.search(r"^%s:=\s*function\s*\((.*?)\)\s*$(.*?)^end function;" % fn,
                  src, re.S | re.M)
    assert m, "%s not found in %s" % (fn, path)
    params = [p.strip() for p in m.group(1).split(",")]
    body = m.group(2)
    # strip debug prints FIRST (they contain ';' inside no string, but the
    # string may contain '=' and ','); the whole one-line construct goes.
    body = re.sub(r'if\s*\((?:ADD_DEBUG|DBL_DEBUG)\)\s*then\s*"[^"]*";\s*end if;',
                  "", body)
    # Block comments FIRST. The genus-3 split files close theirs as
    # "*///endIGNORE" with no space, so a line-comment pass run first matches at
    # the "//" one character early, eats the "*/" with it, and orphans the "/*".
    # That silently broke all 18 genus-3 split functions that carry such a block.
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
            # A physical line may carry several statements: the dispatchers open
            # with "u1 :=D1[1]; v1:= D1[2]; ...". Split at top-level semicolons
            # so each becomes its own statement.
            for piece in _split_semis(buf):
                out.append(piece)
            buf = ""
    assert not buf, "dangling text %r" % buf[:120]
    return out


def _split_semis(s):
    """Split a joined line at top-level ';', keeping each terminator.

    Leaves `end if;` and one-line guarded prints intact, since those are matched
    as whole statements later.
    """
    if s.endswith("then") or s == "end if;" or "_DEBUG" in s:
        return [s]
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        cur += ch
        if ch == ";" and depth == 0:
            out.append(cur.strip())
            cur = ""
    if cur.strip():
        out.append(cur.strip())
    return [x for x in out if x]


def _split_top(s):
    """Split on commas at bracket depth zero.

    `return Deg12ADDUP(u20,v20,u10,u11,v10,v11,ccs);` is one value, not seven.
    A naive split on "," tore the call apart and the fragments then failed to
    parse.
    """
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
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


def build(lines, i=0):
    """Build a block tree.

    Handles `if <cond> then` with or without surrounding parentheses. The repo
    writes both: genus-3 ramified parenthesises, genus-3 split does not, and a
    parser that insisted on one silently rejected half the repository.
    """
    blk = Block()
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^if\s+(.*?)\s+then$", ln) or re.match(r"^if\s*\((.*)\)\s*then$", ln)
        if m:
            sub, i = build(lines, i + 1)
            blk.append(("if", parse_cond(m.group(1).strip()), sub))
            continue
        m = re.match(r"^(elif)\s+(.*?)\s+then$", ln)
        if m:
            sub, i = build(lines, i + 1)
            blk.append(("elif", parse_cond(m.group(2).strip()), sub))
            continue
        if ln == "else":
            sub, i = build(lines, i + 1)
            blk.append(("else", None, sub))
            continue
        if ln == ";":
            i += 1              # empty statement left by a split; harmless
            continue
        if ln == "end if;":
            return blk, i + 1
        m = re.match(r"^([A-Za-z_][A-Za-z_0-9]*)\s*:=\s*(.*);$", ln)
        if m:
            blk.append(("set", m.group(1), parse_expr(m.group(2)))); i += 1
            continue
        m = re.match(r'^"([^"]*)";$', ln)
        if m:                       # bare unguarded print
            blk.append(("print", m.group(1))); i += 1
            continue
        m = re.match(r'^if\s*\(?[A-Za-z_0-9]*_DEBUG\)?\s*then\s*"([^"]*)";\s*end if;$', ln)
        if m:                       # one-line guarded print: a branch label
            blk.append(("print", m.group(1))); i += 1
            continue
        m = re.match(r"^return\s+(.*);$", ln)
        if m:
            blk.append(("ret", [parse_expr(e) for e in _split_top(m.group(1))]))
            i += 1
            continue
        raise AssertionError("unparsed statement: %r" % ln)
    return blk, i


class Ret(Exception):
    def __init__(self, vals):
        self.vals = vals


def run(blk, env, F, path, funcs=None):
    taken = False   # whether an earlier arm of the current if/elif/else fired
    for st in blk:
        if st[0] == "set":
            env[st[1]] = ev(st[2], env, F, funcs)
            path.append(st[1])
        elif st[0] == "print":
            path.append("PRINT:" + st[1])
        elif st[0] in ("if", "elif", "else"):
            # An if/elif/else chain is a run of sibling entries. Only evaluate a
            # later arm if no earlier one in the chain fired.
            if st[0] == "if":
                taken = False
            if st[0] == "else":
                fired = not taken
            else:
                fired = (not taken) if st[0] == "elif" else True
                if fired:
                    fired = _truthy(ev(st[1], env, F, funcs))
            if fired:
                taken = True
                run(st[2], env, F, path, funcs)
        else:
            raise Ret([ev(e, env, F, funcs) for e in st[1]])


class MagmaFn:
    def __init__(self, path, fn):
        self.path, self.name = path, fn
        self.params, body = clean_body(path, fn)
        self.stmts = statements(body)
        self.blk, n = build(self.stmts)
        assert n == len(self.stmts), (fn, n, len(self.stmts))

    def __call__(self, *args, path=None):
        assert len(args) == len(self.params), \
            (self.name, len(args), len(self.params))
        F = args[0].F
        env = dict(zip(self.params, args))
        pth = [] if path is None else path
        try:
            run(self.blk, env, F, pth)
        except Ret as r:
            return tuple(r.vals)
        raise AssertionError("%s fell off the end" % self.name)


def function_names(path):
    """Every `Name := function(...)` defined in a .mag file, in source order.

    Replaces having the caller enumerate names by hand. Tolerates both spacings
    the repo uses, `Deg1ADD:= function` and `ADD := function`.
    """
    src = open(path).read()
    return [m.group(1) for m in
            re.finditer(r"^([A-Za-z_][A-Za-z_0-9]*)\s*:=\s*function\s*\(", src, re.M)]


def discover(path, only=None, skip_unparsable=True):
    """{name: MagmaFn} for a .mag file, discovering the names itself.

    `skip_unparsable=True` returns what it can and records the rest in
    `.unparsable`, so a driver can report partial coverage rather than dying on
    the first dispatcher it cannot read.
    """
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
    out_obj = dict(out)
    discover.unparsable = bad
    return out_obj


def load(fname, names):
    """Back-compatible loader for the audit's stored scripts."""
    return {n: MagmaFn(REPO + fname, n) for n in names}


ADD_MAIN = "arb_ramifiedG3_ADD.m"
ADD_VAR = "arb_ramifiedG3_ADD_use_for_odd_even.m"
DBL_MAIN = "arb_ramifiedG3_DOUBLE.m"
DBL_VAR = "arb_ramifiedG3_DOUBLE_use_for_odd_even.m"

if __name__ == "__main__":
    for fname, names in [
        (ADD_MAIN, ["Deg11ADD", "Deg21ADD", "Deg22ADD", "Deg31ADD",
                    "Deg32ADD", "Deg33ADD"]),
        (ADD_VAR, ["Deg11ADD", "Deg12ADD", "Deg22ADD", "Deg13ADD",
                   "Deg23ADD", "Deg33ADD"]),
        (DBL_MAIN, ["Deg1DOUBLE", "Deg2DOUBLE", "Deg3DOUBLE"]),
        (DBL_VAR, ["Deg1DOUBLE", "Deg2DOUBLE", "Deg3DOUBLE"]),
    ]:
        print("===", fname)
        for n in names:
            f = MagmaFn(REPO + fname, n)
            print("   %-10s %2d params  %3d stmts  %2d top-level"
                  % (n, len(f.params), len(f.stmts), len(f.blk)))
