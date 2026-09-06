"""_parser.py -- expression and condition parsing for the .mag interpreter.

Recursive descent with precedence, calls, chained indexing and boolean structure.
Measured over this repository's formula files, all of which is needed:

  IsZero(...) and friends            1347 uses
  ccs[1][2][3] indexing              531 uses in one split file
  bare booleans, `if ADD_DEBUG then` 1791 uses
  lt / le / ge / ne as well as eq    101 uses between them
  negative literals, `eq -1`         53 uses

Negative literals are kept as written, not normalised: in characteristic 2,
-1 == 1, and that coincidence is a real defect in the testers.

Grammar, loosest binding first:

    cond    := or
    or      := and ( 'or' and )*
    and     := not ( 'and' not )*
    not     := 'not' not | rel
    rel     := add ( ('eq'|'ne'|'lt'|'le'|'gt'|'ge') add )?
    add     := mul ( ('+'|'-') mul )*
    mul     := unary ( ('*'|'/') unary )*
    unary   := '-' unary | power
    power   := postfix ( '^' ['-'] INT )*
    postfix := atom ( '(' [args] ')' | '[' cond ']' )*
    atom    := INT | IDENT | '(' cond ')'
"""

from __future__ import annotations

import re

__all__ = ["tokens", "parse_expr", "parse_cond", "ParseError"]


class ParseError(Exception):
    pass


KEYWORDS = {"eq", "ne", "lt", "le", "gt", "ge", "and", "or", "not"}
RELATIONS = {"eq", "ne", "lt", "le", "gt", "ge"}

_TOKEN = re.compile(r"""
      \s*(?:
        (?P<int>\d+)
      | (?P<ident>[A-Za-z_][A-Za-z_0-9]*)
      | (?P<op><=|>=|[-+*/^(),;\[\]<>])
      | (?P<bad>\S)
      )
""", re.X)


def tokens(s):
    """Token list. Raises rather than silently truncating on a bad character."""
    out, i = [], 0
    while i < len(s):
        m = _TOKEN.match(s, i)
        if not m:
            break
        if m.group("bad"):
            raise ParseError("unexpected character %r in %r" % (m.group("bad"), s))
        out.append(m.group("int") or m.group("ident") or m.group("op"))
        i = m.end()
    return out


class _P:
    def __init__(self, toks, src):
        self.t, self.i, self.src = toks, 0, src

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else None

    def take(self):
        if self.i >= len(self.t):
            raise ParseError("unexpected end of %r" % self.src)
        v = self.t[self.i]
        self.i += 1
        return v

    def expect(self, v):
        got = self.take()
        if got != v:
            raise ParseError("expected %r, got %r, in %r" % (v, got, self.src))

    # -- grammar ----------------------------------------------------------
    def cond(self):
        return self.or_()

    def or_(self):
        n = self.and_()
        while self.peek() == "or":
            self.take()
            n = ("or", n, self.and_())
        return n

    def and_(self):
        n = self.not_()
        while self.peek() == "and":
            self.take()
            n = ("and", n, self.not_())
        return n

    def not_(self):
        if self.peek() == "not":
            self.take()
            return ("not", self.not_())
        return self.rel()

    def rel(self):
        n = self.add()
        if self.peek() in RELATIONS:
            op = self.take()
            return ("cmp", op, n, self.add())
        return n

    def add(self):
        n = self.mul()
        while self.peek() in ("+", "-"):
            op = self.take()
            n = (op, n, self.mul())
        return n

    def mul(self):
        n = self.unary()
        while self.peek() in ("*", "/"):
            op = self.take()
            n = (op, n, self.unary())
        return n

    def unary(self):
        if self.peek() == "-":
            self.take()
            return ("neg", self.unary())
        if self.peek() == "+":
            # Magma accepts a leading '+'; same tree as its absence.
            self.take()
            return self.unary()
        return self.power()

    def power(self):
        n = self.postfix()
        while self.peek() == "^":
            self.take()
            neg = False
            if self.peek() == "-":
                self.take()
                neg = True
            e = self.take()
            if not e.isdigit():
                raise ParseError("exponent must be an integer literal, got %r, "
                                 "in %r" % (e, self.src))
            n = ("pow", n, -int(e) if neg else int(e))
        return n

    def postfix(self):
        n = self.atom()
        while True:
            if self.peek() == "(":
                if n[0] != "var":
                    raise ParseError("cannot call a non-name in %r" % self.src)
                self.take()
                args = []
                if self.peek() != ")":
                    args.append(self.cond())
                    while self.peek() == ",":
                        self.take()
                        args.append(self.cond())
                self.expect(")")
                n = ("call", n[1], args)
            elif self.peek() == "[":
                self.take()
                idx = self.cond()
                self.expect("]")
                n = ("index", n, idx)
            else:
                return n

    def atom(self):
        tk = self.take()
        if tk == "(":
            n = self.cond()
            self.expect(")")
            return n
        if tk in ("[", "<"):
            # Sequence `[..]` and tuple `<..>` literals, both nestable, both
            # mapped to one list type: both are 1-based indexable and nothing in
            # these files depends on Magma's homogeneous/heterogeneous
            # distinction. The tuple form is needed for the genus-2 negReduced
            # nch2 Precompute, which returns `<<<f0,...>>>`.
            #
            # `<` is unambiguous here: the formulas spell comparison
            # `lt`/`le`/`gt`, never `<`, and the one other use of angle brackets,
            # `R<x> := PolynomialRing(...)`, is matched as a whole statement
            # before any expression parsing happens.
            close = "]" if tk == "[" else ">"
            items = []
            if self.peek() != close:
                items.append(self.cond())
                while self.peek() == ",":
                    self.take()
                    items.append(self.cond())
            self.expect(close)
            return ("list", items)
        if tk.isdigit():
            return ("int", int(tk))
        if tk in KEYWORDS:
            raise ParseError("unexpected keyword %r in %r" % (tk, self.src))
        return ("var", tk)


def _parse(s, want_cond):
    p = _P(tokens(s), s)
    n = p.cond() if want_cond else p.cond()
    if p.i != len(p.t):
        raise ParseError("trailing tokens %r in %r" % (p.t[p.i:], s))
    return n


def parse_expr(s):
    """Parse an expression. Conditions are a superset, so this shares the entry."""
    return _parse(s, False)


def parse_cond(s):
    """Parse a condition, same AST shape as parse_expr.

    A bare expression is a truth test to the evaluator, which is what
    `if ADD_DEBUG then` needs.
    """
    return _parse(s, True)
