#!/usr/bin/env python3
"""Reads that no assignment reaches, checked in statement order.

`undef.py` asks whether a name is assigned anywhere in the function body, which
an assignment BELOW the read satisfies.  That is exactly the shape a mid-edit
rename leaves behind, and four such breakages reached real Magma during the
2026-08-20 genus-3 addition work (`ta` twice, `k3` twice) with `undef.py`
reporting every one of those files clean.

This walks the body top to bottom and asks whether each read has an assignment
ABOVE it.  A name assigned only later, or never, is reported.

    python3 dominance.py g3/ramifiedModel/g3Formulas/arb_ramifiedG3_ADD.mag
    python3 dominance.py                    # every formula file in the tree

WHAT THIS DOES NOT CATCH: statement order is not dominance.  An assignment inside
an `if` block above the read counts as reaching it, so a value defined only on a
sibling path still passes.  Closing that needs the branch structure, and the
guards here nest six deep with `end if;//name` closers a line scanner cannot
match reliably.  This weaker check catches every failure this project has
actually had and is cheap enough for CI; real Magma sees the rest.

Exit status is 1 if any read is reported, so this can gate.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Flags set by the caller before `load`, so they are live on entry everywhere.
GLOBALS = {"ADD_DEBUG", "DBL_DEBUG", "UTL_DEBUG", "DEBUG"}

# Magma keywords and the builtins these files call; a name here is never a read
# of a local.  A missing entry shows up as a false report rather than a silent
# pass, which is the safe direction for a gate.
RESERVED = {
    "if", "then", "else", "elif", "end", "return", "function", "procedure",
    "for", "while", "do", "repeat", "until", "case", "when", "true", "false",
    "and", "or", "not", "xor", "in", "notin", "where", "is", "assert", "error",
    "print", "printf", "local", "eq", "ne", "lt", "le", "gt", "ge", "div",
    "mod", "cat", "join", "meet", "diff", "sdiff", "select", "IsZero",
    "Degree", "Coefficient", "Coeff", "LeadingCoefficient", "ExactQuotient",
    "Quotrem", "Random", "Parent", "PolynomialRing", "GF", "quo", "R", "FF",
    "Q", "Integers", "Rationals", "Sqrt", "Root", "Trace", "Norm", "Numerator",
    "Denominator", "Reverse", "Eltseq", "Append", "Remove", "SetToSequence",
    "Keys", "IsDefined", "AssociativeArray", "Interpolation", "Resultant",
    "XGCD", "GCD", "Gcd", "Xgcd", "Nrows", "Ncols", "Matrix", "Vector",
    "Solution", "Transpose", "Determinant", "Adjoint", "Basis", "Dimension",
}

_HEAD = re.compile(r"^(\w+)\s*:=\s*function\s*\((.*)\)\s*$")
_ASSIGN = re.compile(r"^\s*([A-Za-z]\w*)\s*:=")
# `R<x> := PolynomialRing(GF(q));` binds R *and* the generator x
_GENS = re.compile(r"^\s*([A-Za-z]\w*)\s*<([^>]*)>\s*:=")
_NAME = re.compile(r"(?<![\w.])([A-Za-z]\w*)(?![\w(])")


def _strip(line):
    """The executable part of a line: comments and string literals removed."""
    return re.sub(r'"[^"]*"', '', line.split("//")[0])


def check_function(lines, start, params):
    """[(lineno, name)] for reads with no assignment above them."""
    live = set(params) | GLOBALS
    bad = []
    i = start
    while i < len(lines):
        raw = lines[i]
        if raw.rstrip() == "end function;":
            break
        # a `/* //startIGNORE ... */ //endIGNORE` reference block never executes,
        # and its `u`/`v`/`x` are polynomials, not the coefficient locals here
        if "startIGNORE" in raw:
            while i < len(lines) and "endIGNORE" not in lines[i]:
                i += 1
            i += 1
            continue
        code = _strip(raw)
        g = _GENS.match(code)
        if g:
            live.add(g.group(1))
            live.update(re.findall(r"[A-Za-z]\w*", g.group(2)))
        lhs, sep, rhs = code.partition(":=")
        for name in _NAME.findall(rhs if sep else code):
            if name in RESERVED or name in live:
                continue
            if name[0].isupper() and name not in live:
                continue                      # a called function or a type
            bad.append((i + 1, name))
        m = _ASSIGN.match(code)
        if m:
            live.add(m.group(1))
        i += 1
    return bad


def analyse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    out = []
    for i, line in enumerate(lines):
        m = _HEAD.match(line)
        if not m:
            continue
        name, sig = m.group(1), m.group(2)
        params = re.findall(r"[A-Za-z]\w*", sig)
        for lineno, nm in check_function(lines, i + 1, params):
            out.append((name, lineno, nm))
    return out


def formula_files():
    pats = ["g2/**/*ADD.mag", "g2/**/*DBL.mag", "g2/**/*UTL.mag",
            "g3/**/*ADD.mag", "g3/**/*DBL.mag", "g3/**/*UTL.mag"]
    found = []
    for p in pats:
        found += glob.glob(os.path.join(ROOT, p), recursive=True)
    # the `timings/` tree is a divergent generation and is not of record;
    # `whitebox/` holds generated testers, not formulas
    return sorted(f for f in found
                  if "timings" not in f and "whitebox" not in f)


def main(argv):
    paths = argv[1:] or formula_files()
    total = 0
    for path in paths:
        found = analyse(path)
        rel = os.path.relpath(path, ROOT)
        if found:
            total += len(found)
            print("  FAIL  %s" % rel)
            for fn, lineno, nm in found:
                print("          %s:%d  %r has no assignment above it" % (fn, lineno, nm))
        else:
            print("  OK    %s" % rel)
    print()
    print("  %d read(s) with no assignment above them, across %d file(s)"
          % (total, len(paths)))
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
