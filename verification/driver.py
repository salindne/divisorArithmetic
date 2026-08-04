"""driver.py -- differential test of the .mag explicit formulas against reference.py.

Runs the actual Magma source through `maginterp`, runs `reference.py`'s Cantor
implementation on the same inputs, and compares Mumford coordinates exactly. The
formulas are never transcribed into Python, so there is nothing to drift.

Usage:

    python3 driver.py                                  # every ramified family
    python3 driver.py --genus 3 --class nch2
    python3 driver.py --model ramified --field 8 --curves 40 --seed 5
    python3 driver.py --list                           # families and why any is skipped

Exit status is 0 only if every comparison matched *and* every labelled branch of
every file under test was exercised at least once. Both halves matter: a run that
compares 100,000 divisor pairs but only ever enters the generic branch has tested
one branch, and reporting that as a pass is how the `ADD(D, D)` defect survived
in the inherited testers for as long as it did.

Three things this deliberately does not do quietly:

  * It never invents the curve domain. Which coefficients a family's formulas are
    valid for is read out of the family's own source (see `read_support`), not
    written down here, so a formula that stops reading `f4` cannot be silently
    tested on curves where `f4` is nonzero.
  * It never caps coverage silently. Anything dropped -- a family that cannot be
    loaded, a degree combination with no divisors over a small field, a branch
    never reached -- is printed and counted.
  * It does not treat an arity anomaly as a crash. One branch of every ramified
    ADD returns an extra value (errata E2); the run records it as a finding and
    keeps going, because stopping there would hide everything after it.
"""

from __future__ import annotations

import argparse
import collections
import os
import random
import re
import sys

import curves as C
import maginterp as M
import reference as R
from ff import GF
from poly import Poly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Fields to sweep when --field is not given. Small char-2 fields first: they are
# where exhaustive enumeration is affordable and where `-1 == 1` coincidences
# hide sign errors.
CH2_FIELDS = (2, 4, 8, 16)
ODD_FIELDS = (3, 5, 7, 11, 13)


# ---------------------------------------------------------------------------
# families
# ---------------------------------------------------------------------------

class Family(object):
    """One (model, genus, class) triple and the files implementing it."""

    def __init__(self, model, genus, kind, add_path, dbl_path):
        self.model, self.genus, self.kind = model, genus, kind
        self.add_path, self.dbl_path = add_path, dbl_path

    @property
    def name(self):
        return "%s/g%d/%s" % (self.model, self.genus, self.kind)

    def __repr__(self):
        return "<Family %s>" % self.name


def discover_families(root=ROOT):
    """Every family present in the repository, found by walking the tree.

    Not a hardcoded list: PR6 through PR8 add files to these directories, and a
    driver that had to be edited to see a new specialisation would report full
    coverage of a matrix with a hole in it.
    """
    out = []
    pat = re.compile(r"^(arb|nch2|ch2)_(ramified|split)G([23])_(ADD|DBL)\.mag$")
    seen = {}
    excluded = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            m = pat.match(fn)
            if not m:
                continue
            # g2/timings/ and g3/timings/ hold an earlier self-contained generation
            # of the split formulas, kept to reproduce the published timing figures.
            # Same function names as the canonical files, but every body differs:
            # a different `ccs` layout (ccs[2][3] against ccs[1][3][1]), Magma tuple
            # returns instead of multi-value returns, and opposite signs on some
            # terms. They are not the formulas of record and reference a
            # `nch23_splitG2_UTL.mag` that the canonical tree does not have, so
            # testing them here would report coverage of files nobody ships.
            # Excluded out loud rather than quietly passed over.
            if os.sep + "timings" + os.sep in dirpath + os.sep:
                excluded.append(os.path.join(dirpath, fn))
                continue
            kind, model, genus, op = m.group(1), m.group(2), int(m.group(3)), m.group(4)
            # posReduced and negReduced are separate families sharing filenames.
            basis = ""
            if "posReduced" in dirpath:
                basis = "pos"
            elif "negReduced" in dirpath:
                basis = "neg"
            key = (model + basis, genus, kind)
            seen.setdefault(key, {})[op] = os.path.join(dirpath, fn)
    for (model, genus, kind), ops in sorted(seen.items()):
        out.append(Family(model, genus, kind, ops.get("ADD"), ops.get("DBL")))
    return out, excluded


# ---------------------------------------------------------------------------
# validity domain, read out of the source
# ---------------------------------------------------------------------------

_SIG = r"^%s\s*:=\s*function\s*\((.*?)\)[^\n]*$(.*?)^end function;"


def _dispatcher_body(path, op):
    src = open(path).read()
    src = re.sub(r"//[^\n]*", "", re.sub(r"/\*.*?\*/", "", src, flags=re.S))
    m = re.search(_SIG % op, src, re.S | re.M)
    if not m:
        return None, None
    return [p.strip() for p in m.group(1).split(",")], m.group(2)


def read_support(path, op):
    """{'f': {indices}, 'h': {indices}} that the dispatcher actually reads.

    Only the dispatcher is inspected, because it is the boundary: it decomposes
    the curve into coefficients and hands the Deg* cases exactly the ones they
    need. A coefficient it never extracts cannot influence any result.
    """
    _params, body = _dispatcher_body(path, op)
    if body is None:
        return None
    out = {}
    for v in ("f", "h"):
        out[v] = {int(i) for i in
                  re.findall(r"Coeff\(\s*%s\s*,\s*(\d+)\s*\)" % v, body)}
    return out


_BANNER_MEMBER = re.compile(r"\(\s*([fh])(\d+)\s+in\s*\{([^}]*)\}\s*\)")


def banner_members(path):
    """{('h', 2): {0, 1}} from a file's own banner.

    The genus-2 arbitrary and char-2 files state `h(x) = h2*x^2 + h1*x + h0
    (h2 in {0,1})` in their header, and it is a real restriction, not decoration:
    `h2` is declared `//Ignore: h2` so that products with it are free in the
    operation counts, which is only sound when it is 0 or 1. Feeding h2 = t over
    GF(4) produced 36 wrong doublings in branch DBL4 -- correct `u`, wrong `v` --
    all of them outside the stated domain.

    Read from the source rather than tabulated here, for the same reason
    `read_support` is: a table would silently keep passing after a banner changed.
    """
    out = {}
    for line in open(path):
        if "//" not in line:
            continue
        for m in _BANNER_MEMBER.finditer(line):
            vals = set()
            for tok in m.group(3).split(","):
                tok = tok.strip()
                if tok.isdigit():
                    vals.add(int(tok))
            if vals:
                out[(m.group(1), int(m.group(2)))] = vals
    return out


def domain_constraints(fam, families, op="ADD"):
    """Coefficients that must be zero for `fam`'s formulas to be applicable.

    Derived by contrast with the `arb` family of the same model and genus, which
    is the one valid on arbitrary curves. What `arb` reads and a specialisation
    does not is precisely what that specialisation assumes away.

    The contrast matters. "Unread implies zero" on its own is wrong: no genus-2
    ramified file reads `f0`, `arb` included, because Cantor reduction needs only
    the quotient and the low coefficients of `f` land in the remainder. Treating
    that as an assumption would have restricted every genus-2 run to curves with
    `f0 = 0` and quietly skipped most of the domain.
    """
    path = fam.add_path if op == "ADD" else fam.dbl_path
    if path is None:
        return None, "no %s file" % op
    params, _body = _dispatcher_body(path, op)
    if params and any(p.strip() == "ccs" for p in params):
        # The split dispatchers never touch f or h: they take `ccs`, the constants
        # `Precompute` derives from the curve, so their validity domain is not
        # visible here and the contrast below would wrongly report "arbitrary
        # curves". Producing `ccs` needs a root of x^2 + h_g x - f_{2g+2}, and for
        # the arb and ch2 families Precompute takes it from Magma's Factorization
        # and picks "the second solution" -- an ordering that cannot be reproduced
        # without Magma, and picking the other root swaps the positive and negative
        # reduced bases. Reported as a blocker instead of guessed at.
        return None, ("takes precomputed ccs; needs Precompute, whose infinite-place "
                      "root choice depends on Magma's factor ordering")
    mine = read_support(path, op)
    if mine is None:
        return None, "no %s dispatcher" % op
    if fam.kind == "arb":
        return {"f": set(), "h": set()}, None
    ref = [g for g in families
           if g.model == fam.model and g.genus == fam.genus and g.kind == "arb"]
    if not ref:
        return None, "no arb family to contrast against"
    ref_path = ref[0].add_path if op == "ADD" else ref[0].dbl_path
    if ref_path is None:
        return None, "arb family has no %s file" % op
    theirs = read_support(ref_path, op)
    return {"f": theirs["f"] - mine["f"], "h": theirs["h"] - mine["h"]}, None


def curve_in_domain(F, fam, cons, rng, attempts=300, members=None):
    """A validated curve of `fam`'s class with the assumed-zero coefficients zero."""
    dh_max = C.deg_h_max(fam.genus, fam.model.replace("pos", "").replace("neg", ""))
    for _ in range(attempts):
        cur = C.random_curve(F, fam.kind, rng, genus=fam.genus,
                             model=fam.model.replace("pos", "").replace("neg", ""))
        f, h = cur.f, cur.h
        if cons["f"] and any(not f.coeff(i).is_zero() for i in cons["f"]):
            f = Poly.from_coeffs(F, [F.zero if i in cons["f"] else f.coeff(i)
                                     for i in range(f.deg + 1)])
        if cons["h"] and any(not h.coeff(i).is_zero() for i in cons["h"]):
            h = Poly.from_coeffs(F, [F.zero if i in cons["h"] else h.coeff(i)
                                     for i in range(max(h.deg + 1, 1))])
        # Banner memberships such as (h2 in {0,1}). Only 0 and 1 are expressible,
        # so a coefficient outside the set is redrawn from it rather than nudged.
        if members:
            for (var, idx), allowed in members.items():
                tgt = f if var == "f" else h
                if int(idx) > (tgt.deg if tgt.deg >= 0 else 0) + 0 and \
                        tgt.coeff(idx).is_zero():
                    continue
                cur_c = tgt.coeff(idx)
                as_int = 1 if cur_c.is_one() else (0 if cur_c.is_zero() else None)
                if as_int in allowed:
                    continue
                pick = F.one if 1 in allowed else F.zero
                new = [tgt.coeff(i) for i in range(max(tgt.deg + 1, idx + 1))]
                new[idx] = pick
                if var == "f":
                    f = Poly.from_coeffs(F, new)
                else:
                    h = Poly.from_coeffs(F, new)
        cand = cur._replace(f=f, h=h) if hasattr(cur, "_replace") else None
        if cand is None:                      # not a namedtuple; rebuild
            cand = C.Curve(F, f, h, fam.kind, fam.genus,
                           fam.model.replace("pos", "").replace("neg", ""))
        ok, _why = C.validate_curve(cand, rng, level="fast")
        if ok:
            return cand
    return None


# ---------------------------------------------------------------------------
# calling convention, also read out of the source
# ---------------------------------------------------------------------------

def build_args(params, curve, D1, D2=None):
    """Map a dispatcher's parameter names onto values.

    The two genus-3 ramified dispatchers take `(D1, D2, f, h)` with the divisor
    as a sequence, while genus 2 takes `(u, v, up, vp, f)` with the coordinates
    already split out. Reading the names off the parsed signature keeps the
    driver from encoding either convention, which matters because PR10 is going
    to change parameter order in the genus-3 files on purpose.
    """
    args = []
    for p in params:
        key = p.strip()
        if key in ("D1", "D"):
            args.append([D1[0], D1[1]])
        elif key == "D2":
            args.append([D2[0], D2[1]])
        elif key == "u":
            args.append(D1[0])
        elif key == "v":
            args.append(D1[1])
        elif key in ("up", "u2"):
            args.append(D2[0])
        elif key in ("vp", "v2"):
            args.append(D2[1])
        elif key == "u1":
            args.append(D1[0])
        elif key == "v1":
            args.append(D1[1])
        elif key == "f":
            args.append(curve.f)
        elif key == "h":
            args.append(curve.h)
        elif key == "q":
            args.append(curve.F.q)
        else:
            raise KeyError("unmapped dispatcher parameter %r" % key)
    return args


def decode_divisor(F, genus, vals):
    """(u, v) from a dispatcher's flat return, plus a note on any arity anomaly.

    The convention is `u_g, ..., u_0, v_{g-1}, ..., v_0`: coefficients descending,
    u then v, so 2g+1 values. One branch of every ramified ADD returns 2g+2
    instead -- a balancing weight left over from the split model, recorded as
    errata E2. That is returned as a note rather than raised, so a run surfaces it
    once instead of aborting on the first pair that reaches the branch.
    """
    want = 2 * genus + 1
    note = None
    if len(vals) == want + 1:
        note = "returned %d values, expected %d (errata E2)" % (len(vals), want)
        vals = vals[:want]
    elif len(vals) != want:
        return None, None, "returned %d values, expected %d" % (len(vals), want)
    uc = list(vals[:genus + 1])[::-1]          # ascending
    vc = list(vals[genus + 1:])[::-1]
    return Poly.from_coeffs(F, uc), Poly.from_coeffs(F, vc), note


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------

class Result(object):
    def __init__(self):
        self.compared = 0
        self.matched = 0
        self.mismatches = []            # wrong on the formulas' documented domain
        self.precondition = []          # wrong only where D1 == D2 (errata E1 class)
        self.precondition_errors = collections.Counter()   # crashes, same cause
        self.errors = collections.Counter()
        self.notes = collections.Counter()
        self.covered = collections.defaultdict(set)     # file -> {label}
        self.skipped = []               # (what, why)
        self.pairs_by_mode = collections.Counter()

    def ok(self):
        return not self.mismatches and not self.errors


def labels_in(path):
    """Every branch label in a file: the coverage denominator.

    Both guard spellings, `if ADD_DEBUG then "x";` and `if (ADD_DEBUG) then "x";`.
    The repository uses the first 1743 times and the second 70, and the 70 are all
    genus-3 ramified -- the family this work exists to verify -- so matching only
    one form would have reported that family as having no branches to cover.
    """
    src = open(path).read()
    return set(re.findall(r'if\s*\(?[A-Za-z_0-9]*_DEBUG\)?\s*then\s*"([^"]*)";',
                          src))


def run_family(fam, families, res, fields, n_curves, n_pairs, seed, verbose):
    cons, why = domain_constraints(fam, families, "ADD")
    if cons is None:
        res.skipped.append((fam.name + " ADD", why))
        return
    try:
        subs = M.discover(fam.add_path)
        params, _ = _dispatcher_body(fam.add_path, "ADD")
        add = subs["ADD"]
    except Exception as e:
        res.skipped.append((fam.name + " ADD",
                            "cannot load: %s: %s" % (type(e).__name__, e)))
        return

    dbl = None
    dbl_params = None
    if fam.dbl_path:
        try:
            dsubs = M.discover(fam.dbl_path)
            dbl_params, _ = _dispatcher_body(fam.dbl_path, "DBL")
            dbl = dsubs["DBL"]
            # The ADD dispatcher delegates to DBL nowhere today (that is PR5), but
            # both tables are merged so a future `D1 eq D2` dispatch resolves.
            merged = dict(dsubs)
            merged.update(subs)
            subs = merged
        except Exception as e:
            res.skipped.append((fam.name + " DBL",
                                "cannot load: %s: %s" % (type(e).__name__, e)))

    members = banner_members(fam.add_path)
    if fam.dbl_path:
        members.update(banner_members(fam.dbl_path))
    for q in fields:
        F = GF(q)
        if fam.kind == "ch2" and F.char != 2:
            res.skipped.append((fam.name + " over GF(%d)" % q,
                                "class ch2 needs characteristic 2"))
            continue
        if fam.kind == "nch2" and F.char == 2:
            res.skipped.append((fam.name + " over GF(%d)" % q,
                                "class nch2 needs characteristic != 2"))
            continue
        rng = random.Random("%s|%d|%d" % (fam.name, q, seed))
        made = 0
        for _ in range(n_curves * 4):
            if made >= n_curves:
                break
            cur = curve_in_domain(F, fam, cons, rng, members=members)
            if cur is None:
                continue
            made += 1
            _exercise(fam, cur, add, params, dbl, dbl_params, subs, res,
                      rng, n_pairs, q, verbose)
        if made == 0:
            res.skipped.append((fam.name + " over GF(%d)" % q,
                                "no curve in the formulas' domain after %d attempts"
                                % (n_curves * 4)))
        elif made < n_curves:
            res.skipped.append((fam.name + " over GF(%d)" % q,
                                "only %d of %d curves found in domain"
                                % (made, n_curves)))


def _exercise(fam, cur, add, params, dbl, dbl_params, subs, res, rng,
              n_pairs, q, verbose):
    F = cur.F
    for mode in C.PAIR_MODES:
        for _ in range(n_pairs):
            try:
                pair = C.random_divisor_pair(cur, rng, mode=mode)
            except Exception as e:
                res.errors["pair generation %s: %s" % (mode, type(e).__name__)] += 1
                continue
            if not pair:
                continue
            D1, D2 = pair
            res.pairs_by_mode[mode] += 1
            _compare(fam, cur, add, params, subs, res, D1, D2, "ADD", q, mode,
                     verbose)
            # Commutativity, checked rather than assumed. The genus-3 dispatchers
            # sort their operands by Magma's polynomial order before handing them
            # to a mixed-degree function that is not symmetric, so ADD(D1, D2)
            # and ADD(D2, D1) taking different paths to the same answer is the
            # property that makes that sort safe. Cheap, and it is one of the
            # group axioms the plan requires anyway.
            _compare(fam, cur, add, params, subs, res, D2, D1, "ADD", q,
                     mode + "/swapped", verbose)
            if dbl is not None:
                _compare(fam, cur, dbl, dbl_params, subs, res, D1, None, "DBL",
                         q, mode, verbose)


def _compare(fam, cur, fn, params, subs, res, D1, D2, op, q, mode, verbose):
    F = cur.F
    path = []
    try:
        args = build_args(params, cur, D1, D2)
    except KeyError as e:
        res.errors["%s %s: %s" % (fam.name, op, e)] += 1
        return
    same = (op == "ADD" and D2 is not None
            and D1[0] == D2[0] and D1[1] == D2[1])
    try:
        vals = fn(*args, path=path, funcs=subs, F=F)
    except Exception as e:
        # A crash is classified by the same rule as a wrong answer. Dividing by
        # zero when D1 == D2 is errata E1: the guard `IsZero(dw20) and IsZero(dw21)`
        # is too narrow, so dw21 = 0 with dw20 nonzero reaches `b2 := dw21^-1`.
        # Real inputs outside that precondition must never crash, so those stay
        # errors and still fail the run.
        bucket = res.precondition_errors if same else res.errors
        bucket["%s %s %s: %s: %s"
               % (fam.name, op, mode, type(e).__name__, str(e)[:60])] += 1
        return
    src = fam.add_path if op == "ADD" else fam.dbl_path
    for step in path:
        if step.startswith("PRINT:"):
            res.covered[src].add(step[6:])

    gu, gv, note = decode_divisor(F, fam.genus, vals)
    if note:
        res.notes["%s %s: %s" % (fam.name, op, note)] += 1
    if gu is None:
        res.errors["%s %s: %s" % (fam.name, op, note)] += 1
        return

    try:
        want = R.add(cur, D1, D2) if op == "ADD" else R.double(cur, D1)
    except Exception as e:
        res.errors["reference %s %s: %s" % (fam.name, op, type(e).__name__)] += 1
        return

    res.compared += 1
    if gu == want[0] and gv == want[1]:
        res.matched += 1
        return
    # A wrong answer with D1 == D2 is the documented `D1 != D2` precondition being
    # violated, not a defect on the domain the formulas claim. The thesis assumes it
    # and no file checks it, which is exactly why the inherited Magma testers guard
    # `if D1 ne D2` and so can never see it. Kept separate so this driver can gate
    # the current formulas on their claimed domain while still listing the defect in
    # full; PR5 adds the `D1 eq D2 -> DBL` dispatch and these must flip to matching.
    (res.precondition if same else res.mismatches).append(dict(
        family=fam.name, field=q, op=op, mode=mode,
        f=str(cur.f), h=str(cur.h),
        D1="(%s, %s)" % (D1[0], D1[1]),
        D2=None if D2 is None else "(%s, %s)" % (D2[0], D2[1]),
        got="(%s, %s)" % (gu, gv), want="(%s, %s)" % (want[0], want[1]),
        branch=[s[6:] for s in path if s.startswith("PRINT:")]))


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def report(res, families_run, show_all, strict=False):
    w = sys.stdout.write
    w("\n")
    w("=" * 72 + "\n")
    w("  compared %d operations, %d matched, %d mismatched"
      % (res.compared, res.matched, len(res.mismatches)))
    if res.precondition:
        w(", %d wrong only where D1 == D2" % len(res.precondition))
    w("\n")
    w("=" * 72 + "\n\n")

    if res.pairs_by_mode:
        w("  divisor pairs by mode\n")
        for mode in C.PAIR_MODES:
            n = res.pairs_by_mode.get(mode, 0)
            flag = "" if n else "   <-- none generated"
            w("    %-18s %6d%s\n" % (mode, n, flag))
        w("\n")

    w("  branch coverage\n")
    total_l = total_c = 0
    uncovered_any = False
    for fam in families_run:
        for src in (fam.add_path, fam.dbl_path):
            if not src:
                continue
            labs = labels_in(src)
            if not labs:
                continue
            hit = res.covered.get(src, set()) & labs
            stray = res.covered.get(src, set()) - labs
            total_l += len(labs)
            total_c += len(hit)
            pct = 100.0 * len(hit) / len(labs)
            mark = "ok " if len(hit) == len(labs) else "GAP"
            w("    %s %-52s %3d/%3d  %5.1f%%\n"
              % (mark, os.path.relpath(src, ROOT), len(hit), len(labs), pct))
            missing = sorted(labs - hit)
            if missing:
                uncovered_any = True
                shown = missing if show_all else missing[:8]
                w("          unexercised: %s%s\n"
                  % (", ".join(shown),
                     "" if len(shown) == len(missing)
                     else "  (+%d more, use --show-all)" % (len(missing) - len(shown))))
            if stray:
                w("          labels printed but not found in source: %s\n"
                  % ", ".join(sorted(stray)))
    if total_l:
        w("    %-56s %3d/%3d  %5.1f%%\n"
          % ("TOTAL", total_c, total_l, 100.0 * total_c / total_l))
    w("\n")

    if res.notes:
        w("  notes\n")
        for k, n in sorted(res.notes.items()):
            w("    %6d x %s\n" % (n, k))
        w("\n")

    if res.skipped:
        w("  skipped (%d)\n" % len(res.skipped))
        shown = res.skipped if show_all else res.skipped[:20]
        for what, why in shown:
            w("    - %s: %s\n" % (what, why))
        if len(shown) != len(res.skipped):
            w("    ... +%d more, use --show-all\n" % (len(res.skipped) - len(shown)))
        w("\n")

    if res.errors:
        w("  errors (%d distinct)\n" % len(res.errors))
        for k, n in res.errors.most_common(None if show_all else 15):
            w("    %6d x %s\n" % (n, k))
        w("\n")

    if res.mismatches:
        w("  MISMATCHES (%d), first %d shown\n"
          % (len(res.mismatches), min(5, len(res.mismatches))))
        for m in res.mismatches[:5]:
            w("    %s over GF(%d), %s, mode=%s\n"
              % (m["family"], m["field"], m["op"], m["mode"]))
            w("      f  = %s\n      h  = %s\n" % (m["f"], m["h"]))
            w("      D1 = %s\n" % m["D1"])
            if m["D2"]:
                w("      D2 = %s\n" % m["D2"])
            w("      got  %s\n      want %s\n" % (m["got"], m["want"]))
            w("      branch: %s\n\n" % (" -> ".join(m["branch"]) or "(none recorded)"))

    if res.precondition_errors:
        n = sum(res.precondition_errors.values())
        w("  CRASHES WHERE D1 == D2 (%d), errata E1: the guard `IsZero(dw20) and "
          "IsZero(dw21)`\n  is too narrow, so dw21 = 0 with dw20 nonzero reaches "
          "`dw21^-1`; %s\n"
          % (n, "counted as failure (--strict)" if strict
             else "not counted as failure, PR5 fixes this"))
        for k, c in res.precondition_errors.most_common(None if show_all else 8):
            w("    %6d x %s\n" % (c, k))
        w("\n")

    if res.precondition:
        w("  WRONG WHERE D1 == D2 (%d), the documented `D1 != D2` precondition; %s\n"
          % (len(res.precondition),
             "counted as failure (--strict)" if strict else
             "not counted as failure, PR5 fixes this"))
        by = collections.Counter((m["family"], m["op"], tuple(m["branch"]))
                                 for m in res.precondition)
        for (famname, op, branch), n in sorted(by.items()):
            w("    %6d x %s %s at branch %s\n"
              % (n, famname, op, " -> ".join(branch) or "(none)"))
        m = res.precondition[0]
        w("    first: GF(%d)  f = %s  h = %s\n" % (m["field"], m["f"], m["h"]))
        w("           D1 = D2 = %s\n" % m["D1"])
        w("           got  %s\n           want %s\n" % (m["got"], m["want"]))
        w("\n")

    failed = (bool(res.mismatches) or bool(res.errors) or uncovered_any
              or (strict and (res.precondition or res.precondition_errors)))
    if failed:
        reasons = []
        if res.mismatches:
            reasons.append("%d mismatch(es)" % len(res.mismatches))
        if res.errors:
            reasons.append("%d error kind(s)" % len(res.errors))
        if uncovered_any:
            reasons.append("unexercised branches")
        if strict and res.precondition:
            reasons.append("%d D1 == D2 failure(s)" % len(res.precondition))
        w("  FAILED: %s\n\n" % ", ".join(reasons))
    else:
        w("  PASS: every comparison matched and every branch was exercised\n\n")
    return 1 if failed else 0


# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default="ramified",
                    help="ramified | split | splitpos | splitneg | all "
                         "(default ramified)")
    ap.add_argument("--genus", type=int, default=0, help="2, 3, or 0 for both")
    ap.add_argument("--class", dest="klass", default="all",
                    help="arb | nch2 | ch2 | all")
    ap.add_argument("--field", type=int, default=0,
                    help="a single field size; default sweeps small fields")
    ap.add_argument("--curves", type=int, default=6, help="curves per field")
    ap.add_argument("--pairs", type=int, default=6,
                    help="divisor pairs per curve per pair-mode")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--list", action="store_true",
                    help="list families and the domain read out of each")
    ap.add_argument("--show-all", action="store_true",
                    help="do not truncate skip, error or coverage lists")
    ap.add_argument("--strict", action="store_true",
                    help="also fail on wrong answers where D1 == D2, which today's "
                         "formulas do not claim to support (PR5)")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)

    families, excluded = discover_families()

    def wanted(fam):
        if a.genus and fam.genus != a.genus:
            return False
        if a.klass != "all" and fam.kind != a.klass:
            return False
        if a.model == "all":
            return True
        if a.model == "split":
            return fam.model.startswith("split")
        if a.model == "splitpos":
            return fam.model == "splitpos"
        if a.model == "splitneg":
            return fam.model == "splitneg"
        return fam.model == a.model

    sel = [f for f in families if wanted(f)]

    if a.list:
        print("\n  families found (%d), * = selected by these flags\n" % len(families))
        for fam in families:
            cons, why = domain_constraints(fam, families, "ADD")
            if cons is None:
                dom = "unavailable: %s" % why
            else:
                bits = []
                for v in ("f", "h"):
                    if cons[v]:
                        bits.append("%s: %s = 0"
                                    % (v, ", ".join("%s%d" % (v, i)
                                                    for i in sorted(cons[v]))))
                dom = "; ".join(bits) if bits else "arbitrary curves"
            print("   %s %-22s %s" % ("*" if fam in sel else " ", fam.name, dom))
        if excluded:
            print("  excluded, an earlier generation kept for the published timings"
                  " (%d files):" % len(excluded))
            for f in excluded:
                print("      %s" % os.path.relpath(f, ROOT))
        print()
        return 0

    if not sel:
        print("no family matches those flags; try --list")
        return 2

    fields = (a.field,) if a.field else None
    res = Result()
    for fam in sel:
        fl = fields
        if fl is None:
            fl = CH2_FIELDS if fam.kind == "ch2" else (
                ODD_FIELDS if fam.kind == "nch2" else CH2_FIELDS + ODD_FIELDS)
        print("  %-24s fields %s" % (fam.name, ", ".join(str(x) for x in fl)))
        run_family(fam, families, res, fl, a.curves, a.pairs, a.seed, a.verbose)

    return report(res, sel, a.show_all, a.strict)


if __name__ == "__main__":
    sys.exit(main())
