"""blockcheck.py -- executes a reference block and compares it against the
explicit code that is supposed to implement it.

    python3 blockcheck.py                        # every family it can reach
    python3 blockcheck.py arb --curves=10 --pairs=10
    python3 blockcheck.py nch2 --function Deg3ADD
    python3 blockcheck.py arb --block-from cand.mag   # a candidate block
    python3 blockcheck.py --list                  # families, fields, blocks

NEEDS REAL MAGMA, SO IT CANNOT RUN IN HOSTED CI

Every other module here is Magma-free by construction: `maginterp.py` executes
the `.mag` source in Python. This one is not, and cannot be, because a reference
block is written in the *full* language -- `Resultant`, `XGCD`, `quo<R | up>`,
polynomial `div` -- which is precisely the part `maginterp.py` does not
implement, since the explicit formulas never use it. So this needs
`tools/magma-docker/magma.sh`, Magma is licensed commercial software, and this is
not a gate a hosted runner can execute. Same standing as the `*_random.mag`
testers: run locally, and before a release.

Magma exits 0 even when a script dies, so exit status is never trusted here.
Python requires the machine-readable `BLOCKCHECK` lines to come back and decides
the verdict itself; a runtime error anywhere in the run suppresses them and is
reported as a failure rather than as silence.

WHAT IT IS FOR

Each formula function opens with a `//Formulation` block inside
`/* //startIGNORE ... */ //endIGNORE`: the readable polynomial-level algorithm
that the explicit coefficient code below it implements. **Nothing else in this
repository ever runs one.** `maginterp.py` interprets the explicit code and reads
*values*, so `whitebox.py`, `driver.py`, `opcount.py` and every one of the Magma
random testers step over the blocks entirely, and every Magma tester loads the
file with the block still commented out. "Uncomment it and it produces the right
answers" was therefore an unverified claim for the whole life of these files --
and it was false: the arbitrary-characteristic genus-3 `Deg3ADD` block agreed on
every input whose `gcd(u, up)` had degree 0, 1 or 2 and disagreed in the `u = up`
class, one cause being a missing `upp := upp/LeadingCoefficient(upp);`.

This module splices the block into a scratch file as its own function and drives
it against the file's own explicit code on the same inputs.

That particular line is now dead code -- in the rewritten CASE #4.1 `upp` is a
monic exact quotient already -- so `selftest.py`'s `blocks` section gates this
module with a different single-line deletion in the same branch, and measures the
original one to keep that statement evidence rather than assertion.

CASE CONTROL IS BY CONSTRUCTION, NOT SAMPLING

That defect survived earlier three-way Magma checking because `Random(Jac)`
essentially never returns two divisors that share a `u`. So divisors are built
here from *affine points of the curve*, which makes the number of shared
x-coordinates -- and hence `deg gcd(u, up)`, the quantity every branch keys on --
a parameter rather than a coincidence:

    shared = 0   ->  gcd(u, up) = 1, the typical path
    shared = 1   ->  gcd of degree 1
    shared = 2   ->  gcd of degree 2
    shared = 3   ->  u = up  (the y at a shared x is changed, so D1 != D2)

Every class in range is required to be non-empty. "Nothing failed" must not be
reachable by comparing nothing -- the same rule `driver.py` applies to a selected
family that produces no comparisons.

EVERY ADD BLOCK IN THESE FILES, NOT ONLY Deg3ADD

The two divisor degrees are read out of the function's signature, so `--function`
reaches all six blocks in each file, and `add_functions` discovers which six they
are rather than naming them. `selftest.py`'s `blocks` section drives every one of
them in both families, so all twelve are gated, not only the one the provocation
is injected into. At that section's settings, `--curves=4 --pairs=6 --seed 11`,
all twelve agree over 9,061 comparisons: `arb` 752/744/973/618/906/1158 and `nch2`
529/528/764/486/738/865 for Deg1ADD, Deg12ADD, Deg22ADD, Deg13ADD, Deg23ADD,
Deg3ADD. The seed is named because it has to be: at the CLI default `--seed 1` the
same twelve agree over 8,904 instead. A comparison count is a property of the run,
not of the formulas -- it moves with the seed, with the field set the tester
declares, and with the curves the generator happens to produce -- so quote one
only with the settings that produced it. The `blocks` section reproduces the 9,061
on every run, which is what keeps that figure honest.

`Deg3ADD` is the default because it is the only one with a `u = up` class -- the
two degree-3 divisors can be equal -- and that is where the defect was.

WHAT IT DOES NOT COVER, PLAINLY

  * It compares the block against the *explicit code*, not against the group
    law. A defect present in both is invisible here. That is not a gap in
    practice -- the explicit code is what `whitebox.py` and `driver.py` check
    against `reference.py`'s independent Cantor arithmetic, and what the Magma
    testers check against Magma's own Jacobian -- but the claim this module
    licenses is exactly "the block agrees with the verified code", and no more.

  * Only the genus-3 ramified families are discovered, by globbing
    `g3/ramifiedModel/*_ramifiedG3_random.mag`. The split model is not covered:
    its divisors carry a weight alongside `(u, v)` and its blocks read it, so the
    point-based construction below cannot express its inputs. Genus 2 is not
    covered either, for no reason beyond nobody having needed it: the machinery
    below is degree-driven and would likely extend.

  * ADD only. A `DBL` block takes one divisor and has no shared-x axis at all, so
    it needs a different driver, not a different argument list.

  * Divisor construction gives `u` distinct roots in the base field. A `u` with a
    repeated root or an irreducible factor is not reachable this way, so a branch
    that only such a `u` can reach is not exercised. The branch structure of
    these functions keys on `gcd(u, up)`, which is why that is the axis chosen,
    but the limit is real.

NOTHING FAMILY-SPECIFIC IS TABULATED HERE

On the same principle as `driver.read_support` and `opcount.directives`: a table
in this file would keep agreeing with itself after the source changed. Which
files to load, which curve generator to draw from and which fields to sweep are
all read out of the family's own `*_random.mag` tester; the degrees of the two
divisors, the argument order and the number of return values are read out of the
function's own signature and first `return`. The `nch2` sweep therefore includes
GF(7), which its banner excludes as a *derivation* characteristic -- deliberately,
because `ramifiedUtilities.mag` records that GF(7) curves already in the depressed
form are legitimate inputs.

The only file this module writes is a scratch `.mag` in this directory, removed
in a `finally`. It never writes under `g3/`, whose files it opens read-only.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

MAGMA = os.path.join(ROOT, "tools", "magma-docker", "magma.sh")

# The testers to read families out of. A glob, not a list of families: a family
# added under here is discovered, and one renamed stops being silently checked.
TESTER_GLOB = os.path.join(ROOT, "g3", "ramifiedModel", "*_ramifiedG3_random.mag")

DEFAULT_FUNCTION = "Deg3ADD"


# ---------------------------------------------------------------------------
# reading the family out of its own tester
# ---------------------------------------------------------------------------

class Target(object):
    """One family: where its formulas are, what curves it is tested over.

    Every field is read from the tester or from the formula file. Nothing here
    is declared by this module.
    """

    def __init__(self, name, tester):
        self.name = name
        self.tester = tester
        src = _read(tester)

        m = re.search(r"_ramifiedG(\d)_random\.mag$", tester)
        self.genus = int(m.group(1))
        self.fdeg = 2 * self.genus + 1

        self.loads = re.findall(r'^\s*load\s+"([^"]+)";', src, re.M)
        if not self.loads:
            raise ValueError("%s has no load statements" % tester)

        add = [p for p in self.loads
               if os.path.basename(p).startswith(name + "_") and "_ADD" in p]
        if len(add) != 1:
            raise ValueError("%s: expected exactly one %s_*_ADD load, found %s"
                             % (tester, name, add or "none"))
        self.add_rel = add[0]
        self.add_path = os.path.join(os.path.dirname(tester), self.add_rel)

        # The DBL the tester loads. Read rather than assumed, which is what made
        # the borrow visible while it lasted: nch2 genus-3 ramified had no doubling
        # of its own and said so by loading arb's. PR6 gave it one, so every tester
        # now names its own family's DBL -- and a future ADD-first specialisation
        # will show up here as a borrow again without this needing to change.
        dbl = [p for p in self.loads if "_DBL" in p]
        self.dbl_rel = dbl[0] if len(dbl) == 1 else None
        self.dbl_path = (os.path.join(os.path.dirname(tester), self.dbl_rel)
                         if self.dbl_rel else None)
        self.dbl_borrowed = bool(
            self.dbl_rel
            and not os.path.basename(self.dbl_rel).startswith(name + "_"))

        m = re.search(r"^\s*FIELDS\s*:=\s*\{([^}]*)\}", src, re.M)
        if not m:
            raise ValueError("%s declares no FIELDS set" % tester)
        self.fields = sorted({int(t) for t in m.group(1).split(",") if t.strip()})

        # Two shapes in the repository: `f,h := RandomG3Curve(F)` and
        # `f := RandomG3NotChar2Curve(F)`, the second meaning h = 0.
        m = re.search(r"^\s*f\s*,\s*h\s*:=\s*(\w+)\(", src, re.M)
        if m:
            self.curve_fn, self.returns_h = m.group(1), True
        else:
            m = re.search(r"^\s*f\s*:=\s*(\w+)\(", src, re.M)
            if not m:
                raise ValueError("%s: cannot see which curve generator it draws from"
                                 % tester)
            self.curve_fn, self.returns_h = m.group(1), False

    @property
    def curve_call(self):
        if self.returns_h:
            return "f, h := %s(q);" % self.curve_fn
        return "f := %s(q);\n        h := R!0;" % self.curve_fn

    def load_lines(self):
        """`load` statements rewritten relative to this directory.

        The scratch file runs from `verification/`, not from the tester's
        directory, so `load "ramifiedUtilities.mag"` has to become
        `load "../g3/ramifiedModel/ramifiedUtilities.mag"`. magma.sh mounts the
        repository root, so a `..` here stays inside the mount.
        """
        base = os.path.dirname(self.tester)
        out = []
        for rel in self.loads:
            p = os.path.relpath(os.path.join(base, rel), HERE)
            out.append('load "%s";' % p)
        return out


def discover_targets():
    """{name: Target} for every genus-3 ramified tester, plus what was unreadable."""
    found, broken = {}, []
    for tester in sorted(glob.glob(TESTER_GLOB)):
        name = os.path.basename(tester).split("_")[0]
        try:
            found[name] = Target(name, tester)
        except Exception as exc:                                # noqa: BLE001
            broken.append((os.path.relpath(tester, ROOT), str(exc)))
    return found, broken


# ---------------------------------------------------------------------------
# reading the function and its block out of the formula file
# ---------------------------------------------------------------------------

def _read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def extract(path, fn=DEFAULT_FUNCTION, span=800):
    """(signature, block body lines, return arity) for one function.

    The body is what lies strictly between the `startIGNORE` and `endIGNORE`
    marker lines -- the markers themselves are part of the commenting, not of
    the algorithm.
    """
    lines = _read(path).split("\n")
    head = re.compile(r"^%s\s*:=\s*function\((.*)\)\s*$" % re.escape(fn))
    at = None
    for i, line in enumerate(lines):
        m = head.match(line)
        if m:
            at, sig = i, m.group(1)
            break
    if at is None:
        raise ValueError("%s defines no %s (on a single line)"
                         % (os.path.basename(path), fn))

    start = end = None
    for i in range(at, min(at + span, len(lines))):
        if start is None and "startIGNORE" in lines[i]:
            start = i
        elif start is not None and "endIGNORE" in lines[i]:
            end = i
            break
    if start is None or end is None:
        raise ValueError("%s: %s has no /* //startIGNORE ... */ //endIGNORE block"
                         % (os.path.basename(path), fn))
    body = lines[start + 1:end]

    arity = None
    for i in range(end + 1, len(lines)):
        m = re.match(r"^\s*return\s+(.*);\s*$", lines[i])
        if m:
            arity = _count_top_level(m.group(1))
            break
    if not arity:
        raise ValueError("%s: cannot read %s's return arity" % (path, fn))
    return sig, body, arity


_ADD_HEAD = re.compile(r"^(Deg\d+ADD)\s*:=\s*function\(", re.M)


def add_functions(path):
    """(runnable, [(name, why)]) -- the ADD blocks in one formula file.

    Discovered, not tabulated, on the same principle as everything else here: a
    function added to the file gets checked, and one renamed stops being silently
    skipped by a list that would keep agreeing with itself. `ADD` itself is
    excluded by the pattern -- it is the dispatcher, taking whole divisors rather
    than coefficients, so the machinery below cannot call it -- and so is every
    `DBL`, which has no shared-x axis. Anything named `Deg<n>ADD` whose block or
    signature cannot be read is returned in the second list rather than dropped.
    """
    runnable, unrunnable = [], []
    for m in _ADD_HEAD.finditer(_read(path)):
        name = m.group(1)
        try:
            sig, body, _arity = extract(path, name)
            degrees_and_args(sig)
            if not [x for x in body if x.strip()]:
                raise ValueError("the block is empty")
            runnable.append(name)
        except Exception as exc:                                # noqa: BLE001
            unrunnable.append((name, str(exc)))
    return runnable, unrunnable


def _count_top_level(text):
    """Number of comma-separated values at bracket depth 0."""
    depth, n = 0, 1
    for ch in text:
        if ch in "([<":
            depth += 1
        elif ch in ")]>":
            depth -= 1
        elif ch == "," and depth == 0:
            n += 1
    return n


def degrees_and_args(sig):
    """((deg D1, deg D2), Magma expressions for the call, in signature order).

    Read from the signature, so a reordered parameter list moves the arguments
    with it -- which is the point: PR10 reorders these, and a table here would
    keep passing.
    """
    params = [p.strip() for p in sig.split(",") if p.strip()]
    pat = re.compile(r"^(up|vp|u|v|f|h)(\d+)$")
    args, du, dup = [], -1, -1
    for p in params:
        m = pat.match(p)
        if not m:
            raise ValueError("unrecognised parameter %r" % p)
        var, idx = m.group(1), int(m.group(2))
        if var == "u":
            du = max(du, idx)
        elif var == "up":
            dup = max(dup, idx)
        args.append("Coeff(%s,%d)" % (var, idx))
    if du < 0 or dup < 0:
        raise ValueError("signature names no u/up coefficients: %r" % sig)
    return (du + 1, dup + 1), args


def strip_markers(lines):
    """A candidate block, with any ignore markers removed."""
    return [x for x in lines
            if "startIGNORE" not in x and "endIGNORE" not in x]


def drop_in_case(body, needle, case):
    """Delete `needle` lines that sit inside `case`, up to its next `return`.

    Used to inject a known defect: the caller asserts on how many were dropped,
    so a mutation that silently matched nothing cannot pass for a provocation.
    """
    out, dropped, armed = [], 0, False
    for line in body:
        if case in line:
            armed = True
        elif armed and re.match(r"^\s*return\b", line):
            armed = False
        if armed and line.strip() == needle:
            dropped += 1
            continue
        out.append(line)
    return out, dropped


# ---------------------------------------------------------------------------
# the generated Magma driver
# ---------------------------------------------------------------------------

DRIVER = r"""
// ---------------------------------------------------------------- the driver
// Divisors are built from affine points, so the number of shared
// x-coordinates -- and hence deg gcd(u,up) -- is chosen, not sampled.
Shuffled := function(L)
    M := L;
    for i := #M to 2 by -1 do
        j := Random(1, i);
        t := M[i]; M[i] := M[j]; M[j] := t;
    end for;
    return M;
end function;

MakeDiv := function(R, xl, yl)
    xx := R.1;
    u := &*[xx - xl[i] : i in [1..#xl]];
    v := Interpolation(xl, yl);
    return u, v;
end function;

D1DEG    := %(d1)d;
D2DEG    := %(d2)d;
MAXSHARE := Min(D1DEG, D2DEG);
CURVES   := %(curves)d;
PAIRS    := %(pairs)d;
SHOWMAX  := 3;
FQ       := %(fields)s;

tally := [0 : i in [0..MAXSHARE]];
bad   := [0 : i in [0..MAXSHARE]];
fcurves := [0 : q in FQ];
fcomp   := [0 : q in FQ];
shown := 0;
curvesused := 0;

for fi in [1..#FQ] do
    q := FQ[fi];
    FF := GF(q);
    R<x> := PolynomialRing(FF);
    for trial in [1..CURVES] do
        %(curve_call)s
        if Degree(f) ne %(fdeg)d then continue; end if;
        C := HyperellipticCurve(f, h);
        if Genus(C) ne %(genus)d then continue; end if;

        // affine points, grouped by x-coordinate
        byx := AssociativeArray();
        for P in Points(C) do
            if P[3] ne 0 then
                if IsDefined(byx, P[1]) then
                    byx[P[1]] := Append(byx[P[1]], P[2]);
                else
                    byx[P[1]] := [P[2]];
                end if;
            end if;
        end for;
        xs := SetToSequence(Keys(byx));
        // A pair sharing `shared` x-coordinates needs D1DEG + D2DEG - shared
        // distinct ones, so the requirement is per class, not per curve: a field
        // with five usable x-coordinates cannot present two disjoint degree-3
        // divisors but can present u = up. Testing D1DEG + D2DEG once, up front,
        // would drop GF(4) -- and with it every char-2 check of the u = up
        // branch below GF(8). Fields that supply nothing at all are reported.
        if #xs lt Max(D1DEG, D2DEG) then continue; end if;
        curvesused +:= 1;
        fcurves[fi] +:= 1;

        for shared in [0..MAXSHARE] do
            if #xs lt D1DEG + D2DEG - shared then continue; end if;
            for rep in [1..PAIRS] do
                perm := Shuffled(xs);
                x1 := [perm[k] : k in [1..D1DEG]];
                x2 := [perm[k] : k in [1..shared]] cat
                      [perm[D1DEG + k] : k in [1..D2DEG - shared]];
                y1 := [Random(byx[t]) : t in x1];
                y2 := [Random(byx[t]) : t in x2];
                u,  v  := MakeDiv(R, x1, y1);
                up, vp := MakeDiv(R, x2, y2);
                if Degree(u) ne D1DEG or Degree(up) ne D2DEG then continue; end if;

                // D1 = D2 is outside the documented domain -- the dispatcher
                // routes it to DBL -- so take the other point over one shared x.
                // A ramified point has a single y and cannot be moved.
                if u eq up and v eq vp then
                    alt := [t : t in byx[x2[1]] | t ne y2[1]];
                    if #alt eq 0 then continue; end if;
                    y2[1] := alt[1];
                    up, vp := MakeDiv(R, x2, y2);
                    if u eq up and v eq vp then continue; end if;
                end if;
                // both sides must be genuine reduced divisors
                if not IsZero((f - v*(v + h)) mod u) then continue; end if;
                if not IsZero((f - vp*(vp + h)) mod up) then continue; end if;

                %(call_explicit)s
                %(call_block)s
                tally[shared + 1] +:= 1;
                fcomp[fi] +:= 1;
                if E ne B then
                    bad[shared + 1] +:= 1;
                    if shown lt SHOWMAX then
                        shown +:= 1;
                        printf "\nMISMATCH shared=%%o q=%%o\n  f  = %%o\n  h  = %%o\n  u  = %%o\n  v  = %%o\n  up = %%o\n  vp = %%o\n  explicit %%o\n  block    %%o\n",
                               shared, q, f, h, u, v, up, vp, E, B;
                    end if;
                end if;
            end for;
        end for;
    end for;
end for;

printf "\n";
for i in [1..#tally] do
    printf "BLOCKCHECK class shared=%%o compared=%%o wrong=%%o\n", i-1, tally[i], bad[i];
end for;
for fi in [1..#FQ] do
    printf "BLOCKCHECK field q=%%o curves=%%o compared=%%o\n", FQ[fi], fcurves[fi], fcomp[fi];
end for;
printf "BLOCKCHECK curves used=%%o\n", curvesused;
printf "BLOCKCHECK total compared=%%o wrong=%%o\n", &+tally, &+bad;
quit;
"""

PROBE = 'printf "BLOCKCHECK probe ok\\n";\nquit;\n'


def build_script(target, function=DEFAULT_FUNCTION, curves=3, pairs=4, seed=1,
                 fields=None, block_lines=None):
    """The whole scratch Magma file, as text.

    The block is spliced in as `BLOCK`, taking the explicit function's own
    signature, so both callees are handed identical arguments by construction
    rather than by two argument lists that could drift apart.
    """
    sig, body, arity = extract(target.add_path, function)
    if block_lines is not None:
        body = strip_markers(block_lines)
    (d1, d2), args = degrees_and_args(sig)
    argexpr = ", ".join(args)

    ev = ",".join("ee%d" % i for i in range(1, arity + 1))
    bv = ",".join("bb%d" % i for i in range(1, arity + 1))
    call_explicit = ("%s := %s(%s);\n                E := [%s];"
                     % (ev, function, argexpr, ev))
    call_block = ("%s := BLOCK(%s);\n                B := [%s];"
                  % (bv, argexpr, bv))

    head = [
        "// Generated by verification/blockcheck.py -- transient, do not edit.",
        "// %s %s: the //Formulation block is spliced in as BLOCK and driven"
        % (target.name, function),
        "// against the file's own explicit %s on the same arguments." % function,
        "SetSeed(%d);" % seed,
        "ADD_DEBUG := false;",
        "DBL_DEBUG := false;",
        "UTL_DEBUG := false;",
    ]
    head += target.load_lines()
    head += ["", "BLOCK := function(%s)" % sig] + body + ["end function;", ""]
    head.append(DRIVER % dict(
        d1=d1, d2=d2, curves=curves, pairs=pairs,
        fields="[" + ",".join(str(q) for q in (fields or target.fields)) + "]",
        curve_call=target.curve_call, fdeg=target.fdeg, genus=target.genus,
        call_explicit=call_explicit, call_block=call_block))
    return "\n".join(head), len(body), arity



# ---------------------------------------------------------------------------
# the doubling half
# ---------------------------------------------------------------------------

_DBL_HEAD = re.compile(r"^(Deg\d+DBL)\s*:=\s*function\(", re.M)


def dbl_functions(path):
    """(runnable, [(name, why)]) -- the DBL blocks in one formula file.

    Same discovery rule as `add_functions`, and the same reason for it. `DBL`
    itself is excluded by the pattern: it is the dispatcher.
    """
    runnable, unrunnable = [], []
    for m in _DBL_HEAD.finditer(_read(path)):
        name = m.group(1)
        try:
            sig, body, _arity = extract(path, name)
            degree_and_args_dbl(name, sig)
            if not [x for x in body if x.strip()]:
                raise ValueError("the block is empty")
            runnable.append(name)
        except Exception as exc:                                # noqa: BLE001
            unrunnable.append((name, str(exc)))
    return runnable, unrunnable


def degree_and_args_dbl(name, sig):
    """(deg D, Magma call expressions, signature width) for one DBL block.

    The degree comes from the NAME, not the signature, and that is not laziness.
    `Deg2DBL` still takes the shared full-degree-3 parameter list -- `u2, u1,
    u0, v2, v1, v0` -- while operating on a degree-2 divisor, so reading the
    highest `u` index gives 3 and builds the wrong divisor. That is the
    signature bloat this plan tracks for PR10; `Deg1DBL` carried it until
    2026-08-21. The addition half reads its degrees off the signature because
    there the two operands' degrees are the only thing distinguishing the
    mixed-degree callees, and PR10 will reorder them; here the name is
    authoritative and the signature is what needs trimming.

    The third return is the width the signature implies, so a caller can report
    the gap rather than silently accommodate it.
    """
    m = re.match(r"Deg(\d+)DBL$", name)
    if not m:
        raise ValueError("not a Deg<n>DBL name: %r" % name)
    ddeg = int(m.group(1))
    params = [p.strip() for p in sig.split(",") if p.strip()]
    pat = re.compile(r"^(u|v|f|h)(\d+)$")
    args, du = [], -1
    for p in params:
        mm = pat.match(p)
        if not mm:
            raise ValueError("unrecognised parameter %r" % p)
        var, idx = mm.group(1), int(mm.group(2))
        if var == "u":
            du = max(du, idx)
        args.append("Coeff(%s,%d)" % (var, idx))
    if du < 0:
        raise ValueError("signature names no u coefficient: %r" % sig)
    return ddeg, args, du + 1


DBL_DRIVER = r"""
// ---------------------------------------------------------------- the driver
// A doubling has no shared-x axis. What its branches key on is
// gcd(u, 2v + h): the ramification points of the divisor, which doubling
// kills. So the class here is the NUMBER OF RAMIFIED POINTS in u, chosen by
// construction rather than sampled -- at 2P = 0 a point contributes nothing to
// the double, and every degenerate branch of every DBL is reached that way.
Shuffled := function(L)
    M := L;
    for i := #M to 2 by -1 do
        j := Random(1, i);
        t := M[i]; M[i] := M[j]; M[j] := t;
    end for;
    return M;
end function;

MakeDiv := function(R, xl, yl)
    xx := R.1;
    u := &*[xx - xl[i] : i in [1..#xl]];
    v := Interpolation(xl, yl);
    return u, v;
end function;

DDEG    := %(ddeg)d;
CURVES  := %(curves)d;
REPS    := %(pairs)d;
SHOWMAX := 3;
FQ      := %(fields)s;

tally := [0 : i in [0..DDEG]];
bad   := [0 : i in [0..DDEG]];
fcurves := [0 : q in FQ];
fcomp   := [0 : q in FQ];
shown := 0;
curvesused := 0;

for fi in [1..#FQ] do
    q := FQ[fi];
    FF := GF(q);
    R<x> := PolynomialRing(FF);
    for trial in [1..CURVES] do
        %(curve_call)s
        if Degree(f) ne %(fdeg)d then continue; end if;
        C := HyperellipticCurve(f, h);
        if Genus(C) ne %(genus)d then continue; end if;

        // affine points split by whether 2y + h(x) vanishes there. Those are the
        // ramification points: the ones doubling annihilates.
        ram := []; ord := []; ramy := AssociativeArray(); ordy := AssociativeArray();
        for P in Points(C) do
            if P[3] eq 0 then continue; end if;
            if IsZero(2*P[2] + Evaluate(h, P[1])) then
                if not IsDefined(ramy, P[1]) then
                    Append(~ram, P[1]); ramy[P[1]] := P[2];
                end if;
            else
                if not IsDefined(ordy, P[1]) then
                    Append(~ord, P[1]); ordy[P[1]] := P[2];
                end if;
            end if;
        end for;
        if #ram + #ord lt DDEG then continue; end if;
        curvesused +:= 1;
        fcurves[fi] +:= 1;

        for nram in [0..DDEG] do
            if #ram lt nram or #ord lt DDEG - nram then continue; end if;
            for rep in [1..REPS] do
                rr := Shuffled(ram); oo := Shuffled(ord);
                xl := [rr[k] : k in [1..nram]] cat [oo[k] : k in [1..DDEG - nram]];
                yl := [];
                for t in xl do
                    if IsDefined(ramy, t) then Append(~yl, ramy[t]);
                    else Append(~yl, ordy[t]); end if;
                end for;
                u, v := MakeDiv(R, xl, yl);
                if Degree(u) ne DDEG then continue; end if;
                // a genuine reduced divisor, and the class we asked for
                if not IsZero((f - v*(v + h)) mod u) then continue; end if;
                if Degree(GCD(u, 2*v + h)) ne nram then continue; end if;

                %(call_explicit)s
                %(call_block)s
                tally[nram + 1] +:= 1;
                fcomp[fi] +:= 1;
                if E ne B then
                    bad[nram + 1] +:= 1;
                    if shown lt SHOWMAX then
                        shown +:= 1;
                        printf "\nMISMATCH ramified=%%o q=%%o\n  f = %%o\n  h = %%o\n  u = %%o\n  v = %%o\n  explicit %%o\n  block    %%o\n",
                               nram, q, f, h, u, v, E, B;
                    end if;
                end if;
            end for;
        end for;
    end for;
end for;

printf "\n";
for i in [1..#tally] do
    printf "BLOCKCHECK class ramified=%%o compared=%%o wrong=%%o\n", i-1, tally[i], bad[i];
end for;
for fi in [1..#FQ] do
    printf "BLOCKCHECK field q=%%o curves=%%o compared=%%o\n", FQ[fi], fcurves[fi], fcomp[fi];
end for;
printf "BLOCKCHECK curves used=%%o\n", curvesused;
printf "BLOCKCHECK total compared=%%o wrong=%%o\n", &+tally, &+bad;
quit;
"""


def build_script_dbl(target, function, curves=3, pairs=4, seed=1,
                     fields=None, block_lines=None):
    """The scratch Magma file for one DBL block, spliced in as `BLOCK`."""
    sig, body, arity = extract(target.dbl_path, function)
    if block_lines is not None:
        body = strip_markers(block_lines)
    ddeg, args, sigwidth = degree_and_args_dbl(function, sig)
    argexpr = ", ".join(args)
    ev = ",".join("ee%d" % i for i in range(1, arity + 1))
    bv = ",".join("bb%d" % i for i in range(1, arity + 1))
    call_explicit = ("%s := %s(%s);\n                E := [%s];"
                     % (ev, function, argexpr, ev))
    call_block = ("%s := BLOCK(%s);\n                B := [%s];"
                  % (bv, argexpr, bv))
    head = [
        "// Generated by verification/blockcheck.py -- transient, do not edit.",
        "// %s %s: the reference block is spliced in as BLOCK and driven against"
        % (target.name, function),
        "// the file's own explicit %s on the same arguments." % function,
        "SetSeed(%d);" % seed,
        "ADD_DEBUG := false;",
        "DBL_DEBUG := false;",
        "UTL_DEBUG := false;",
    ]
    head += target.load_lines()
    head += ["", "BLOCK := function(%s)" % sig] + body + ["end function;", ""]
    head.append(DBL_DRIVER % dict(
        ddeg=ddeg, curves=curves, pairs=pairs,
        fields="[" + ",".join(str(q) for q in (fields or target.fields)) + "]",
        curve_call=target.curve_call, fdeg=target.fdeg, genus=target.genus,
        call_explicit=call_explicit, call_block=call_block))
    return "\n".join(head), len(body), arity

# ---------------------------------------------------------------------------
# running it
# ---------------------------------------------------------------------------

class Outcome(object):
    """What one run measured. `verdict` is decided in Python, never by exit code."""

    def __init__(self, name, function):
        self.name = name
        self.function = function
        self.classes = []          # [(class, compared, wrong)]
        self.axis = "shared"       # what `class` counts: "shared" (ADD) or "ramified" (DBL)
        self.per_field = []        # [(q, curves used, compared)]
        self.curves_used = 0
        self.block_lines = 0
        self.arity = 0
        self.fields = []
        self.error = None          # a Magma runtime error, or a harness problem
        self.retried = False       # the container returned nothing the first time
        self.stdout = ""
        self.scratch = None

    @property
    def compared(self):
        return sum(c for _s, c, _w in self.classes)

    @property
    def wrong(self):
        return sum(w for _s, _c, w in self.classes)

    @property
    def empty_classes(self):
        return [s for s, c, _w in self.classes if c == 0]

    @property
    def empty_fields(self):
        return [q for q, cur, _c in self.per_field if cur == 0]

    @property
    def verdict(self):
        if self.error:
            return "ERROR"
        if not self.classes or self.empty_classes:
            return "UNTESTED"
        return "DISAGREE" if self.wrong else "AGREE"

    def as_dict(self):
        return {
            "family": self.name, "function": self.function,
            "verdict": self.verdict, "compared": self.compared,
            "wrong": self.wrong, "fields": self.fields,
            "block_lines": self.block_lines, "return_arity": self.arity,
            "curves_used": self.curves_used, "error": self.error,
            "retried": self.retried,
            "classes": [{"shared": s, "compared": c, "wrong": w}
                        for s, c, w in self.classes],
            "per_field": [{"q": q, "curves": cur, "compared": c}
                          for q, cur, c in self.per_field],
        }


# Magma's own diagnostics. Deliberately narrow: matching the word "error"
# anywhere would also match a mismatch dump or a comment echoed back.
_ERROR_LINE = re.compile(r"^\s*>>|User error:|Runtime error|^Aborting|"
                         r"has not been declared or assigned")


def _magma(script, tag, timeout=3600, keep=False):
    """Run one scratch script. Returns (stdout+stderr, path or None, error).

    The scratch file has to live inside the mount magma.sh sets up, and that
    mount is the repository root. It goes here, in `verification/`, and not
    under `g3/`: the formula files are opened read-only by this module, and a
    tool that writes beside a file a human is editing is a tool that can lose
    their work.
    """
    if not os.access(MAGMA, os.X_OK):
        return "", None, "no runnable magma.sh at %s" % os.path.relpath(MAGMA, ROOT)
    # The pid is part of the name because the name is not otherwise unique: two
    # runs of the same family and function -- a `selftest.py` in one shell and a
    # `blockcheck.py` in another -- would otherwise share this path, and each
    # one's `finally` would delete the other's script out from under Magma.
    path = os.path.join(HERE, "_blockcheck_%s_%d.mag" % (tag, os.getpid()))
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(script)
        try:
            proc = subprocess.run([MAGMA, os.path.basename(path)], cwd=HERE,
                                  capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return "", (path if keep else None), "Magma did not finish in %ds" % timeout
        except OSError as exc:
            return "", (path if keep else None), "cannot run magma.sh: %s" % exc
        out = proc.stdout + proc.stderr
        return out, (path if keep else None), None
    finally:
        if not keep and os.path.exists(path):
            os.remove(path)


def magma_status(timeout=60):
    """(ok, why) -- whether real Magma can be reached at all.

    Probed by running a two-line script through the same path a real run uses,
    rather than by re-deriving magma.sh's docker knowledge here, which would be
    a second copy to go stale. A hosted runner has `docker` and no image, so the
    probe has to be short: `selftest.py`'s `blocks` section calls this to decide
    whether to skip, and CI must not sit waiting to be told what it knows.
    """
    # Twice, because the container has been seen once in ~35 runs to print its
    # banner and then return nothing -- the emulator this image patches is the
    # likely culprit. One retry turns a rare flake into a rarer one; a genuinely
    # missing image fails both times, in under a second each.
    for _attempt in (1, 2):
        out, _p, err = _magma(PROBE, "probe", timeout=timeout)
        if "BLOCKCHECK probe ok" in out:
            return True, "magma.sh answers"
    if err:
        return False, err
    first = next((x.strip() for x in out.splitlines() if x.strip()), "")
    return False, ("magma.sh did not run Magma: %s" % first if first
                   else "magma.sh produced no output")


def run(target, function=DEFAULT_FUNCTION, curves=3, pairs=4, seed=1, fields=None,
        block_lines=None, keep=False, timeout=3600):
    """Drive one block against its explicit function. Never raises for a Magma
    problem: the problem lands in `Outcome.error` so a caller can report it."""
    res = Outcome(target.name, function)
    res.fields = list(fields or target.fields)
    builder = build_script_dbl if function.endswith("DBL") else build_script
    try:
        script, nlines, arity = builder(target, function, curves, pairs, seed,
                                        fields, block_lines)
    except Exception as exc:                                    # noqa: BLE001
        res.error = "%s: %s" % (type(exc).__name__, exc)
        return res
    res.block_lines, res.arity = nlines, arity

    tag = "%s_%s" % (target.name, function)
    out, path, err = _magma(script, tag, timeout=timeout, keep=keep)
    # The one retry, and only for the shape the container's rare flake takes:
    # no tally and no diagnostic either, meaning nothing came back at all. A run
    # that reported a Magma error is never repeated -- that is the answer.
    if not err and "BLOCKCHECK" not in out and not _ERROR_LINE.search(out):
        res.retried = True
        out, path, err = _magma(script, tag, timeout=timeout, keep=keep)
    res.stdout, res.scratch, res.error = out, path, err
    if err:
        return res

    for line in out.splitlines():
        # `shared` for an addition, `ramified` for a doubling: the same axis role,
        # named for what it counts.
        m = re.match(r"BLOCKCHECK class (shared|ramified)=(\d+) compared=(\d+) wrong=(\d+)", line)
        if m:
            res.axis = m.group(1)
            res.classes.append(tuple(int(g) for g in m.groups()[1:]))
        m = re.match(r"BLOCKCHECK field q=(\d+) curves=(\d+) compared=(\d+)", line)
        if m:
            res.per_field.append(tuple(int(g) for g in m.groups()))
        m = re.match(r"BLOCKCHECK curves used=(\d+)", line)
        if m:
            res.curves_used = int(m.group(1))

    # Two independent failure signals, because Magma has both shapes. A dead
    # ExactQuotient kills the script and the tally lines never appear; an
    # undeclared identifier -- the shape a half-finished rename leaves, and the
    # shape that hid in this repository until a shared-u pair reached it -- only
    # aborts the enclosing loop, so the tally lines DO appear, all zeros. Neither
    # moves the exit status, which Magma leaves at 0 either way.
    why = [x.strip() for x in out.splitlines() if _ERROR_LINE.search(x)]
    if not re.search(r"^BLOCKCHECK total compared=\d+ wrong=\d+", out, re.M):
        res.error = ("the run did not finish: %s"
                     % ("; ".join(why[:3]) if why else "no BLOCKCHECK output"))
    elif why:
        res.error = "Magma reported: %s" % "; ".join(why[:3])
    return res


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_outcome(res, verbose=False):
    w = sys.stdout.write
    w("  %-6s %-9s block %d lines, %d return values, fields %s\n"
      % (res.name, res.function, res.block_lines, res.arity,
         ",".join(str(q) for q in res.fields)))
    if res.retried:
        w("     the first attempt returned nothing at all; run repeated\n")
    if res.error:
        w("     ERROR %s\n" % res.error)
        if verbose and res.stdout:
            for line in res.stdout.splitlines()[-40:]:
                w("       | %s\n" % line)
        return
    # An addition classifies on shared x-coordinates, a doubling on ramified
    # points; the driver says which, so the label is never the wrong one.
    axis = "ramified points     " if res.axis == "ramified" else "shared x-coordinates"
    for cls, compared, wrong in res.classes:
        w("     %s = %d : %7d compared, %d wrong%s\n"
          % (axis, cls, compared, wrong, "" if compared else "   <- NOTHING COMPARED"))
    w("     %d curves used, TOTAL %d compared, %d wrong\n"
      % (res.curves_used, res.compared, res.wrong))
    if res.empty_fields:
        # Not a failure: a field with fewer than deg(u) + deg(up) affine
        # x-coordinates cannot supply these divisors at all. Printed because a
        # sweep that quietly tested twelve of seventeen fields reads as
        # seventeen.
        w("     no usable curve over GF(%s) -- too few affine x-coordinates\n"
          % "), GF(".join(str(q) for q in res.empty_fields))
    if res.verdict == "AGREE":
        w("     the block agrees with the explicit code\n")
    elif res.verdict == "UNTESTED":
        w("     UNTESTED: gcd class(es) %s produced no comparisons\n"
          % ", ".join(str(s) for s in res.empty_classes))
    else:
        w("     the block DISAGREES with the explicit code\n")
    if verbose or res.wrong:
        for line in res.stdout.splitlines():
            if line.startswith("MISMATCH") or line.startswith("  "):
                w("       | %s\n" % line.rstrip())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("family", nargs="*", default=None,
                    help="families to check; default every one discovered")
    ap.add_argument("--function", default=DEFAULT_FUNCTION,
                    help="function whose block to run (default %s)" % DEFAULT_FUNCTION)
    ap.add_argument("--curves", type=int, default=3, help="curves per field")
    ap.add_argument("--pairs", type=int, default=4,
                    help="divisor pairs per curve per gcd class")
    ap.add_argument("--seed", type=int, default=1, help="Magma SetSeed value")
    ap.add_argument("--fields", default=None,
                    help="comma-separated field sizes, overriding the tester's set")
    ap.add_argument("--block-from", dest="block_from", default=None,
                    help="read the block from this file instead of the formula "
                         "file, for checking a candidate rewrite")
    ap.add_argument("--timeout", type=int, default=3600, help="seconds per family")
    ap.add_argument("--keep", action="store_true",
                    help="leave the generated scratch .mag in place")
    ap.add_argument("--list", action="store_true",
                    help="families discovered, and what is read out of each")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)

    targets, broken = discover_targets()
    for rel, why in broken:
        print("  unreadable tester %s: %s" % (rel, why))

    if a.list:
        print("\n  families discovered by %s\n"
              % os.path.relpath(TESTER_GLOB, ROOT))
        for name in sorted(targets):
            t = targets[name]
            try:
                sig, body, arity = extract(t.add_path, a.function)
                (d1, d2), _args = degrees_and_args(sig)
                blk = "%s block %d lines, degrees (%d,%d), %d return values" % (
                    a.function, len(body), d1, d2, arity)
            except Exception as exc:                            # noqa: BLE001
                blk = "%s unavailable: %s" % (a.function, exc)
            print("    %-6s %s" % (name, os.path.relpath(t.add_path, ROOT)))
            print("           curves %s, fields %s" %
                  (t.curve_fn, ",".join(str(q) for q in t.fields)))
            print("           %s" % blk)
        # DBL blocks ARE covered -- pass --function Deg1DBL/Deg2DBL/Deg3DBL. They
        # classify on ramified points rather than shared x-coordinates, and the
        # report says which axis it used. This line claimed otherwise for the whole
        # life of the file, which is worse than a missing feature: it tells a
        # reader an oracle does not exist when it does. The default is Deg3ADD
        # only because that is the block most worth checking, not the only one.
        print("\n  --function selects the block: Deg3ADD (default), Deg1DBL,"
              "\n  Deg2DBL, Deg3DBL. Not covered: the split model and genus 2."
              "\n  Families are discovered from the random testers above, so a"
              "\n  family without one cannot be named here yet."
              "\n  needs real Magma via %s\n" % os.path.relpath(MAGMA, ROOT))
        return 0

    chosen = sorted(targets) if not a.family else a.family
    unknown = [n for n in chosen if n not in targets]
    if unknown:
        print("unknown family/families: %s; known: %s"
              % (", ".join(unknown), ", ".join(sorted(targets)) or "none"))
        return 2
    if not chosen:
        print("no family discovered under %s" % os.path.relpath(TESTER_GLOB, ROOT))
        return 2

    fields = None
    if a.fields:
        fields = [int(t) for t in a.fields.split(",") if t.strip()]

    block_lines = None
    if a.block_from:
        block_lines = _read(a.block_from).split("\n")
        if len(chosen) != 1:
            print("--block-from names one block, so name one family")
            return 2

    ok, why = magma_status()
    if not ok:
        print("cannot run: %s" % why)
        print("this module needs real Magma (%s) and cannot run in hosted CI"
              % os.path.relpath(MAGMA, ROOT))
        return 2

    results = []
    for name in chosen:
        if a.block_from:
            print("  %s: block read from %s" % (name, a.block_from))
        res = run(targets[name], a.function, a.curves, a.pairs, a.seed, fields,
                  block_lines, a.keep, a.timeout)
        results.append(res)
        if not a.json:
            _print_outcome(res, a.verbose)
        if res.scratch:
            print("     scratch kept at %s" % os.path.relpath(res.scratch, ROOT))

    if a.json:
        json.dump([r.as_dict() for r in results], sys.stdout, indent=1)
        sys.stdout.write("\n")
    return 0 if all(r.verdict == "AGREE" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
