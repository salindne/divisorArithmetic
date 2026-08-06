"""whitebox.py -- replay the repository's constructed whitebox cases in Python.

The whitebox testers are generated files holding one deliberately constructed case
per computation path: a curve, a basis, both divisors, both balancing weights. They
already pass under Magma, so the inputs are vetted. This reads them, runs the real
`.mag` formulas on those inputs through the interpreter, and compares against
`reference.py`.

That gives what random sampling cannot: **deterministic** branch coverage. Coverage
under sampling is coupon-collector -- measured across all fourteen families, 35% at 2
curves, 54% at 4, 77% at 16, 84% at 30, then it stalls -- so 100% is not reachable in
CI time and possibly not at all. One constructed case per branch reaches every branch
by construction, in seconds.

Usage:

    python3 whitebox.py                 # replay everything, report coverage
    python3 whitebox.py --list          # which testers exist, and what is missing
    python3 whitebox.py --family g3/splitModel/negReduced/nch2
    python3 whitebox.py --show-all      # do not truncate any list

Exit status is 0 only if every case replayed, every case reached a branch, and every
result matched the reference.

Cases are extracted at run time rather than from a committed corpus. A corpus would be
one more artefact able to drift away from the testers it came from; reading the testers
directly cannot go stale, and parsing eleven files costs a fraction of a second.

Cases come from two places, and which one is always visible in the report:

  **extracted** from a whitebox tester -- 11 families, 1,338 cases -- and held to
  100% coverage, because a tester holds one case per branch by construction, so
  anything less is a regression.

  **harvested** by `--harvest` for a family that has no tester -- genus-3 ramified,
  and genus-3 split ch2, whose generator cannot run (nor can its two siblings; see
  README). Search for an input reaching each labelled branch, then freeze it. Held to the coverage recorded when it was harvested,
  since search cannot reach a branch needing an algebraic coincidence.

Harvesting uses the random generators, but **the result is a constructed case like any
other**: this replays frozen inputs and never samples. Randomness builds the corpus
once, offline; it is not part of the gate.

Genus-3 ramified has only three developed files -- arb ADD, arb DBL and nch2 ADD --
and all three are harvested at 100%. Its other three cells (nch2 DBL, ch2 ADD, ch2
DBL) do not exist yet, so there is nothing to cover until PR6 through PR8 derive them.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import random
import re
import sys

import curves as C
import driver as D
import maginterp as M
import reference as R
from ff import GF
from poly import Poly

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Constructed cases for families that have no whitebox tester. Committed, because
# there is nothing to read them out of: the Magma generator does not exist yet.
# Written by `--harvest`, replayed exactly like an extracted case.
HARVEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "harvested_cases.json")


# ---------------------------------------------------------------------------
# parsing Magma's printed values
# ---------------------------------------------------------------------------

def _element(F, text):
    """One field element, as the testers write them.

    Prime fields carry plain integers. Extension fields use `FF.1^k`, powers of the
    field generator, which is why this needs the field rather than just the text.
    """
    text = text.strip()
    m = re.fullmatch(r"FF\.1\s*\^\s*(\d+)", text)
    if m:
        return F.gen() ** int(m.group(1))
    if re.fullmatch(r"FF\.1", text):
        return F.gen()
    m = re.fullmatch(r"FF\s*!\s*(-?\d+)", text)
    if m:
        return F(int(m.group(1)))
    if re.fullmatch(r"-?\d+", text):
        return F(int(text))
    raise ValueError("unrecognised field element %r" % text)


def _poly(F, text):
    """A univariate polynomial as the testers write them.

    Handles `R! x^5 + FF.1*x^2 + FF.1^2*x + FF.1`, an `R!`/`R !` prefix, implicit
    coefficient 1, bare constants and a leading minus.
    """
    text = re.sub(r"^\s*R\s*!\s*", "", text.strip())
    text = text.replace(" ", "")
    if text in ("0", ""):
        return Poly.zero(F)
    # split into signed terms at top level; no parentheses occur in these files
    terms = re.findall(r"[+-]?[^+-]+", text)
    coeffs = {}
    for term in terms:
        sign = -1
        if term.startswith("-"):
            term = term[1:]
        elif term.startswith("+"):
            term = term[1:]
            sign = 1
        else:
            sign = 1
        m = re.fullmatch(r"(?:(.+?)\*)?x(?:\^(\d+))?", term)
        if m:
            exp = int(m.group(2)) if m.group(2) else 1
            coeff = _element(F, m.group(1)) if m.group(1) else F.one
        else:
            exp = 0
            coeff = _element(F, term)
        if sign < 0:
            coeff = -coeff
        coeffs[exp] = coeffs.get(exp, F.zero) + coeff
    top = max(coeffs)
    return Poly.from_coeffs(F, [coeffs.get(i, F.zero) for i in range(top + 1)])


# ---------------------------------------------------------------------------
# extraction
# ---------------------------------------------------------------------------

class Case(object):
    """One constructed case, with where it came from."""

    def __init__(self, tester, index, q, f, h, V, D1, D2, op):
        self.tester, self.index, self.q = tester, index, q
        self.f, self.h, self.V = f, h, V
        self.D1, self.D2, self.op = D1, D2, op

    def __repr__(self):
        return "<Case %s #%d %s over GF(%d)>" % (
            os.path.basename(self.tester), self.index, self.op, self.q)


def find_testers(root=ROOT):
    """Every whitebox tester in the repository."""
    out = []
    for dirpath, _dirs, files in os.walk(root):
        if os.sep + "timings" + os.sep in dirpath + os.sep:
            continue
        # `whitebox/testerFiles/` is the generator's staging area, not the testers
        # of record, and it is stale: its genus-3 split arb copy holds 2 cases where
        # the deployed tester holds 405. Including it would silently halve the
        # coverage denominator for that family. Excluded and named, not skipped.
        if os.sep + "whitebox" + os.sep in dirpath + os.sep:
            continue
        for fn in sorted(files):
            if re.search(r"hite[bB]ox_tester\.mag$", fn):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def family_of(tester):
    """(model, genus, kind, basis) for a tester path, matching driver.py's naming."""
    name = os.path.basename(tester)
    m = re.match(r"(arb|nch2|ch2)_(ramified|split)G([23])_", name)
    kind, model, genus = m.group(1), m.group(2), int(m.group(3))
    basis = None
    if "posReduced" in tester:
        basis = "pos"
    elif "negReduced" in tester:
        basis = "neg"
    return model, genus, kind, basis


def extract(tester):
    """Every constructed case in one tester, plus any block that could not be read.

    Blocks are delimited by `FF := GF(q);`, which the generators emit once per case.
    Measured: 1,338 blocks across the eleven testers and 1,338 asserts, so the
    delimiter is exact rather than approximate.
    """
    src = open(tester).read()
    parts = re.split(r"^FF\s*:=\s*GF\((\d+)\);", src, flags=re.M)
    cases, bad = [], []
    for i in range(1, len(parts) - 1, 2):
        q, body = int(parts[i]), parts[i + 1]
        try:
            cases.append(_one_case(tester, len(cases) + 1, q, body))
        except Exception as exc:                                # noqa: BLE001
            bad.append("%s block %d over GF(%d): %s: %s"
                       % (os.path.basename(tester), (i + 1) // 2, q,
                          type(exc).__name__, str(exc)[:70]))
    return cases, bad


def _grab(body, name):
    m = re.search(r"^\s*%s\s*:=\s*(.+?);" % re.escape(name), body, re.M)
    return m.group(1) if m else None


def _one_case(tester, index, q, body):
    F = GF(q)
    ftxt, htxt = _grab(body, "f"), _grab(body, "h")
    if ftxt is None:
        raise ValueError("no f")
    f = _poly(F, ftxt)
    h = _poly(F, htxt) if htxt is not None else Poly.zero(F)

    vtxt = _grab(body, "V")
    V = _poly(F, vtxt) if vtxt is not None else None

    call = re.search(r":=\s*(ADD|DBL)\(", body)
    if not call:
        raise ValueError("no ADD or DBL call")
    op = call.group(1)

    def divisor(tag):
        u, v = _grab(body, "U" + tag), _grab(body, "V" + tag)
        if u is None or v is None:
            return None
        n = _grab(body, "N" + tag)
        return (_poly(F, u), _poly(F, v),
                None if n is None else int(n.strip()))

    d1 = divisor("1")
    d2 = divisor("2") if op == "ADD" else None
    if d1 is None or (op == "ADD" and d2 is None):
        raise ValueError("missing divisor coordinates")
    return Case(tester, index, q, f, h, V, d1, d2, op)


# ---------------------------------------------------------------------------
# replay
# ---------------------------------------------------------------------------

class Result(object):
    def __init__(self):
        self.replayed = self.matched = 0
        self.mismatches = []
        self.unparsed = []
        self.errors = collections.Counter()
        self.no_branch = []
        self.covered = collections.defaultdict(set)
        self.precondition = 0
        # Coverage here is 100% by construction -- one constructed case per branch --
        # so any gap is a regression, not a sampling artefact, and fails the run.
        self.coverage_gaps = []
        # Files that MUST be accounted for, derived from the testers found and the
        # harvest baseline rather than from what happened to be covered. Without this
        # the coverage loop iterated over its own results, so a tester that yielded no
        # cases left its formula file out of the loop entirely and the run passed
        # having tested nothing. Verified: 11 testers, 0 cases, exit 0.
        self.expected_files = set()
        self.cases_per_tester = {}

    def failed(self):
        return bool(self.mismatches or self.unparsed or self.errors
                    or self.no_branch or self.coverage_gaps)


def _formula_paths(model, genus, kind, basis):
    """The ADD/DBL files a family's cases must be run against."""
    if model == "ramified":
        d = os.path.join(ROOT, "g%d" % genus, "ramifiedModel",
                         "g%dFormulas" % genus)
    else:
        d = os.path.join(ROOT, "g%d" % genus, "splitModel",
                         "%sReduced" % basis, "g%dFormulas" % genus)
    stem = "%s_%sG%d_" % (kind, model, genus)
    return (os.path.join(d, stem + "ADD.mag"), os.path.join(d, stem + "DBL.mag"),
            os.path.join(d, stem + "UTL.mag"))


def replay_tester(tester, res, show_all):
    model, genus, kind, basis = family_of(tester)
    add_path, dbl_path, utl_path = _formula_paths(model, genus, kind, basis)
    for p in (add_path, dbl_path):
        if os.path.isfile(p):
            res.expected_files.add(p)
    cases, bad = extract(tester)
    res.cases_per_tester[tester] = len(cases)
    res.unparsed.extend(bad)

    subs = {}
    if os.path.isfile(utl_path):
        subs.update(M.discover(utl_path))
    for p in (dbl_path, add_path):
        if os.path.isfile(p):
            subs.update(M.discover(p))
    params = {}
    for op, p in (("ADD", add_path), ("DBL", dbl_path)):
        if os.path.isfile(p):
            params[op] = D._dispatcher_body(p, op)[0]

    for case in cases:
        _replay_one(case, model, genus, basis, subs, params,
                    add_path, dbl_path, res)
    return len(cases)


def _replay_one(case, model, genus, basis, subs, params, add_path, dbl_path, res):
    F = GF(case.q)
    fn = subs.get(case.op)
    if fn is None or case.op not in params:
        res.errors["%s: no %s dispatcher" % (os.path.basename(case.tester),
                                             case.op)] += 1
        return
    src = add_path if case.op == "ADD" else dbl_path
    path = []
    try:
        cur = C.Curve(F, case.f, case.h, kind_for(case, model), genus, model)
    except AssertionError as exc:
        res.errors["%s #%d: curve rejected: %s"
                   % (os.path.basename(case.tester), case.index,
                      str(exc)[:50])] += 1
        return

    if model == "split":
        # The case supplies V explicitly, so the reference needs no root choice of
        # its own -- which is what makes these cases stronger than generated ones.
        # The tester's `V` is the positive basis; negReduced then uses -V - h.
        Vp = case.V if case.V is not None else R.compute_vp(cur)
        basis_poly = Vp if basis == "pos" else (-Vp - case.h)
        # Pin the infinite-place root to the one this case's own V names, so
        # Precompute's constants describe the same basis the case was built in.
        # Nothing is chosen by convention here: y_{g+1} is V's leading coefficient.
        # Neither global ordering suits every case -- one fails 247 constructed
        # cases, all in characteristic 2, the other fails 332, all over odd primes.
        M.ROOT_PIN[0] = Vp.coeff(genus + 1)
        try:
            raw = subs["Precompute"](case.f, case.h, case.q, funcs=subs, F=F)
            ccs = raw[0] if len(raw) == 1 else list(raw)
        except Exception as exc:                                # noqa: BLE001
            res.errors["%s #%d: Precompute: %s: %s"
                       % (os.path.basename(case.tester), case.index,
                          type(exc).__name__, str(exc)[:50])] += 1
            return
        finally:
            M.ROOT_PIN[0] = None
        d1 = _split_divisor(cur, case.D1, basis_poly)
        d2 = _split_divisor(cur, case.D2, basis_poly) if case.D2 else None
        if d1 is None or (case.op == "ADD" and d2 is None):
            res.errors["%s #%d: could not form a balanced divisor"
                       % (os.path.basename(case.tester), case.index)] += 1
            return
        args = D.build_args_split(params[case.op], cur, ccs, d1, d2)
    else:
        d1 = (case.D1[0], case.D1[1])
        d2 = (case.D2[0], case.D2[1]) if case.D2 else None
        args = D.build_args(params[case.op], cur, d1, d2)

    same = (case.op == "ADD" and case.D2 is not None
            and case.D1[0] == case.D2[0] and case.D1[1] == case.D2[1])
    try:
        vals = fn(*args, path=path, funcs=subs, F=F)
    except Exception as exc:                                    # noqa: BLE001
        if same:
            # The documented D1 != D2 precondition; errata E1. Not this harness's
            # subject, and the constructed cases are not supposed to contain them.
            res.precondition += 1
            return
        res.errors["%s #%d %s: %s: %s"
                   % (os.path.basename(case.tester), case.index, case.op,
                      type(exc).__name__, str(exc)[:50])] += 1
        return

    labels = [s[6:] for s in path if s.startswith("PRINT:")]
    if not labels:
        res.no_branch.append("%s #%d %s reached no branch label"
                             % (os.path.basename(case.tester), case.index,
                                case.op))
    res.covered[src].update(labels)

    if model == "split":
        gu, gv, gn, note = D.decode_split(F, genus, vals, basis_poly)
        if gu is None:
            res.errors["%s #%d: %s" % (os.path.basename(case.tester),
                                       case.index, note)] += 1
            return
        want = (R.split_add(cur, d1, d2, basis_poly, basis == "pos")
                if case.op == "ADD"
                else R.split_double(cur, d1, basis_poly, basis == "pos"))
        got, exp = (gu, gv, gn), (want[0], want[1], want[3])
    else:
        gu, gv, _note = D.decode_divisor(F, genus, vals)
        if gu is None:
            res.errors["%s #%d: bad return arity"
                       % (os.path.basename(case.tester), case.index)] += 1
            return
        want = (R.add(cur, d1, d2) if case.op == "ADD" else R.double(cur, d1))
        got, exp = (gu, gv), (want[0], want[1])

    res.replayed += 1
    if all(a == b for a, b in zip(got, exp)):
        res.matched += 1
        return
    if same:
        res.precondition += 1
        return
    res.mismatches.append(dict(
        tester=os.path.basename(case.tester), index=case.index, op=case.op,
        field=case.q, f=str(case.f), h=str(case.h),
        got=", ".join(str(x) for x in got),
        want=", ".join(str(x) for x in exp),
        labels=labels))


def kind_for(case, model):
    """The Curve `kind` a case's field forces, which is not always the file's kind.

    An `arb` tester runs cases over both odd and characteristic-2 fields, and Curve
    validates `nch2` as requiring odd characteristic and `ch2` as requiring
    characteristic 2. `arb` accepts either, so it is the honest label for a case
    whose file is arb regardless of the field it uses.
    """
    _model, _genus, kind, _basis = family_of(case.tester)
    if kind == "nch2" and case.q % 2 == 0:
        return "arb"
    if kind == "ch2" and case.q % 2 != 0:
        return "arb"
    return kind


def _split_divisor(cur, coords, V):
    u, v, n = coords
    if n is None:
        return None
    try:
        w = (cur.f - v * (v + cur.h)).exact_quotient(u)
    except Exception:                                           # noqa: BLE001
        return None
    return R.reduced_basis(cur, (u, v, w, n), V)


# ---------------------------------------------------------------------------
# harvesting cases for families with no tester
# ---------------------------------------------------------------------------

def _ser_poly(p):
    """A polynomial as a list of coefficient tuples, field-representation agnostic."""
    return [list(p.coeff(i).c) for i in range(p.deg + 1)] if p.deg >= 0 else []


def _de_poly(F, data):
    return Poly.from_coeffs(F, [F.make(tuple(c)) for c in data]) if data \
        else Poly.zero(F)


def harvest(families, seed=1, curves=40, pairs=12):
    """Find one input per branch for families that have no whitebox tester.

    Genus-3 ramified is the reason this exists. It has no whitebox tester -- PR6
    builds them -- and it is the family this merge series is for, so it cannot go
    untested. Its three developed files (arb ADD, arb DBL, nch2 ADD) get constructed
    cases the only way available: search for an input reaching each labelled branch,
    then freeze it. The three undeveloped cells (nch2 DBL, ch2 ADD, ch2 DBL) have no
    files, so there is nothing to cover until PR6 through PR8 derive them.

    The search uses the random generators, but **the result is a constructed case like
    any other**: CI replays frozen inputs and never samples. Randomness builds the
    corpus once, offline; it is not part of the gate.

    For the split model the infinite-place root is pinned to the reference's own Vp, so
    Precompute's constants and the reference agree by construction rather than by
    convention -- the same trick the extracted cases use with their supplied V.
    """
    out, baseline = [], {}
    for fam in families:
        for op, src in (("ADD", fam.add_path), ("DBL", fam.dbl_path)):
            if not src or not os.path.isfile(src):
                continue
            want = D.labels_in(src)
            if not want:
                continue
            subs = {}
            if fam.is_split and fam.utl_path:
                subs.update(M.discover(fam.utl_path))
            subs.update(M.discover(src))
            if op not in subs:
                continue
            params = D._dispatcher_body(src, op)[0]
            spec = D.split_spec(fam, families) if fam.is_split else None
            cons = None
            if not fam.is_split:
                cons, _why = D.domain_constraints(fam, families, op)
                if cons is None:
                    cons = {"f": set(), "h": set()}
            members = D.banner_members(src)
            found, made = {}, 0
            fields = (D.CH2_FIELDS + D.ODD_FIELDS if fam.kind == "arb"
                      else D.ODD_FIELDS if fam.kind == "nch2" else D.CH2_FIELDS)
            for q in fields:
                if len(found) == len(want):
                    break
                F = GF(q)
                if fam.kind == "ch2" and F.char != 2:
                    continue
                if fam.kind == "nch2" and F.char == 2:
                    continue
                rng = random.Random("harvest|%s|%s|%d|%d" % (fam.name, op, q, seed))
                for _ in range(curves):
                    if len(found) == len(want):
                        break
                    if fam.is_split:
                        cur = D.split_curve_in_domain(F, fam, spec, rng)
                    else:
                        cur = D.curve_in_domain(F, fam, cons, rng, members=members)
                    if cur is None:
                        continue
                    ctx = _harvest_context(fam, cur, subs, F)
                    if ctx is None:
                        continue
                    basis_poly, ccs = ctx
                    for mode in C.PAIR_MODES:
                        if len(found) == len(want):
                            break
                        for _ in range(pairs):
                            rec = _try_pair(fam, cur, subs, params, op, mode, rng,
                                            basis_poly, ccs, want, found, out, F)
                            if rec:
                                made += 1
                            if len(found) == len(want):
                                break
            baseline[os.path.relpath(src, ROOT)] = len(found)
            missing = sorted(want - set(found))
            print("  %-24s %-3s  %3d/%3d branches, %2d cases%s"
                  % (fam.name, op, len(found), len(want), made,
                     "" if not missing
                     else "   UNREACHED %d: %s" % (len(missing),
                                                   ", ".join(missing[:2]))))
    return out, baseline


def _harvest_context(fam, cur, subs, F):
    """(basis polynomial, ccs) for a generated curve, or None if unusable."""
    if not fam.is_split:
        return (None, None)
    try:
        Vp = R.compute_vp(cur)
    except ArithmeticError:
        return None
    basis_poly = Vp if fam.basis == "pos" else (-Vp - cur.h)
    M.ROOT_PIN[0] = Vp.coeff(fam.genus + 1)
    try:
        raw = subs["Precompute"](cur.f, cur.h, F.q, funcs=subs, F=F)
        ccs = raw[0] if len(raw) == 1 else list(raw)
    except Exception:                                           # noqa: BLE001
        return None
    finally:
        M.ROOT_PIN[0] = None
    return (basis_poly, ccs)


def _try_pair(fam, cur, subs, params, op, mode, rng, basis_poly, ccs,
              want, found, out, F):
    """One candidate input; records a case if it reaches a not-yet-covered branch."""
    if fam.is_split:
        pair = C.random_split_divisor_pair(cur, basis_poly, rng, mode=mode)
    else:
        pair = C.random_divisor_pair(cur, rng, mode=mode)
    if not pair:
        return None
    d1, d2 = pair
    if d1[0] == d2[0] and d1[1] == d2[1]:
        return None                 # the documented D1 == D2 precondition; PR5's
    arg_d2 = d2 if op == "ADD" else None
    path = []
    try:
        if fam.is_split:
            args = D.build_args_split(params, cur, ccs, d1, arg_d2)
        else:
            args = D.build_args(params, cur, d1, arg_d2)
        subs[op](*args, path=path, funcs=subs, F=F)
    except Exception:                                           # noqa: BLE001
        return None
    labels = [x[6:] for x in path if x.startswith("PRINT:")]
    fresh = [x for x in labels if x in want and x not in found]
    if not fresh:
        return None
    rec = dict(family=fam.name, op=op, q=F.q, model=cur.model,
               basis=fam.basis or "", labels=labels,
               f=_ser_poly(cur.f), h=_ser_poly(cur.h),
               u1=_ser_poly(d1[0]), v1=_ser_poly(d1[1]),
               source="harvested: no whitebox tester exists for this family")
    if fam.is_split:
        rec["n1"] = d1[3]
    if op == "ADD":
        rec["u2"] = _ser_poly(d2[0])
        rec["v2"] = _ser_poly(d2[1])
        if fam.is_split:
            rec["n2"] = d2[3]
    for x in fresh:
        found[x] = len(out)
    out.append(rec)
    return rec


def load_harvested():
    """(cases, per-file coverage baseline) from the committed harvest, or ([], {})."""
    if not os.path.isfile(HARVEST_FILE):
        return [], {}
    data = json.loads(open(HARVEST_FILE).read())
    if isinstance(data, list):
        return data, {}
    return data.get("cases", []), data.get("baseline", {})


def replay_harvested(res, show_all, only=None):
    """Replay the committed harvested cases, for both models.

    Model-aware for the same reason `harvest` is: genus-3 split ch2 has formulas but
    no whitebox tester, so its cases are harvested too, and a split case needs its
    basis polynomial and ccs rebuilt rather than just a curve and two divisors.
    """
    records, baseline = load_harvested()
    if only:
        # --family filters the harvested cases too, so a filtered run reports on the
        # families asked for and nothing else.
        records = [r for r in records
                   if only in os.path.join(ROOT, _family_dir(r))]
        baseline = {k: v for k, v in baseline.items() if only in k}
    for rel in baseline:
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            res.expected_files.add(p)
    if not records:
        return 0
    fams, _excl = D.discover_families()
    by_name = {f.name: f for f in fams}
    for i, rec in enumerate(records, start=1):
        fam = by_name.get(rec["family"])
        if fam is None:
            res.errors["harvested case %d: unknown family %s"
                       % (i, rec["family"])] += 1
            continue
        F = GF(rec["q"])
        src = fam.add_path if rec["op"] == "ADD" else fam.dbl_path
        subs = {}
        if fam.is_split and fam.utl_path:
            subs.update(M.discover(fam.utl_path))
        subs.update(M.discover(src))
        params = D._dispatcher_body(src, rec["op"])[0]
        model = rec.get("model", "ramified")
        try:
            cur = C.Curve(F, _de_poly(F, rec["f"]), _de_poly(F, rec["h"]),
                          fam.kind, fam.genus, model)
        except AssertionError as exc:
            res.errors["harvested %d: curve rejected: %s"
                       % (i, str(exc)[:50])] += 1
            continue

        basis_poly = ccs = None
        if model == "split":
            ctx = _harvest_context(fam, cur, subs, F)
            if ctx is None:
                res.errors["harvested %d: could not rebuild the split context" % i] += 1
                continue
            basis_poly, ccs = ctx
            d1 = _split_divisor_at(cur, _de_poly(F, rec["u1"]),
                                   _de_poly(F, rec["v1"]), rec["n1"], basis_poly)
            d2 = (_split_divisor_at(cur, _de_poly(F, rec["u2"]),
                                    _de_poly(F, rec["v2"]), rec["n2"], basis_poly)
                  if rec["op"] == "ADD" else None)
            if d1 is None or (rec["op"] == "ADD" and d2 is None):
                res.errors["harvested %d: could not form a balanced divisor" % i] += 1
                continue
            args = D.build_args_split(params, cur, ccs, d1, d2)
        else:
            d1 = (_de_poly(F, rec["u1"]), _de_poly(F, rec["v1"]))
            d2 = ((_de_poly(F, rec["u2"]), _de_poly(F, rec["v2"]))
                  if rec["op"] == "ADD" else None)
            args = D.build_args(params, cur, d1, d2)

        path = []
        try:
            vals = subs[rec["op"]](*args, path=path, funcs=subs, F=F)
        except Exception as exc:                                # noqa: BLE001
            res.errors["harvested %d %s %s: %s: %s"
                       % (i, rec["family"], rec["op"], type(exc).__name__,
                          str(exc)[:50])] += 1
            continue
        labels = [x[6:] for x in path if x.startswith("PRINT:")]
        if not labels:
            res.no_branch.append("harvested case %d reached no branch label" % i)
        res.covered[src].update(labels)

        if model == "split":
            gu, gv, gn, note = D.decode_split(F, fam.genus, vals, basis_poly)
            if gu is None:
                res.errors["harvested %d: %s" % (i, note)] += 1
                continue
            want = (R.split_add(cur, d1, d2, basis_poly, fam.basis == "pos")
                    if rec["op"] == "ADD"
                    else R.split_double(cur, d1, basis_poly, fam.basis == "pos"))
            got, exp = (gu, gv, gn), (want[0], want[1], want[3])
        else:
            gu, gv, _note = D.decode_divisor(F, fam.genus, vals)
            if gu is None:
                res.errors["harvested %d: bad return arity" % i] += 1
                continue
            want = (R.add(cur, d1, d2) if rec["op"] == "ADD"
                    else R.double(cur, d1))
            got, exp = (gu, gv), (want[0], want[1])

        res.replayed += 1
        if all(x == y for x, y in zip(got, exp)):
            res.matched += 1
            continue
        res.mismatches.append(dict(
            tester="harvested_cases.json", index=i, op=rec["op"], field=rec["q"],
            f=str(cur.f), h=str(cur.h),
            got=", ".join(str(x) for x in got),
            want=", ".join(str(x) for x in exp),
            labels=labels))
    return len(records)


def _family_dir(rec):
    """A repo-relative path fragment for a harvested record, for --family matching."""
    model, genus, kind = rec["family"].split("/")
    basis = rec.get("basis") or ""
    if model.startswith("split"):
        return os.path.join("g%s" % genus[1:], "splitModel",
                            "%sReduced" % basis, kind)
    return os.path.join("g%s" % genus[1:], "ramifiedModel", kind)


def _split_divisor_at(cur, u, v, n, V):
    """A balanced divisor from stored coordinates and a weight."""
    try:
        w = (cur.f - v * (v + cur.h)).exact_quotient(u)
    except Exception:                                           # noqa: BLE001
        return None
    return R.reduced_basis(cur, (u, v, w, n), V)


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def report(res, testers, show_all, baseline=None):
    w = sys.stdout.write
    w("\n" + "=" * 72 + "\n")
    w("  replayed %d constructed cases, %d matched, %d mismatched\n"
      % (res.replayed, res.matched, len(res.mismatches)))
    w("=" * 72 + "\n\n")

    baseline = baseline or {}
    w("  branch coverage from constructed cases\n")
    total_l = total_c = 0
    gaps = []
    # Iterate the EXPECTED files, not the covered ones. A file that received no cases
    # must appear here as 0/N and fail, rather than vanishing from the report.
    for src in sorted(res.expected_files | set(res.covered)):
        labels = D.labels_in(src)
        if not labels:
            continue
        hit = res.covered.get(src, set()) & labels
        rel = os.path.relpath(src, ROOT)
        total_l += len(labels)
        total_c += len(hit)
        # Two kinds of expectation, because the cases have two sources. A file with a
        # whitebox tester must be at 100%: the tester holds one case per branch by
        # construction, so anything less is a regression. A file whose cases were
        # harvested is held to the baseline recorded when they were harvested, since
        # search cannot reach branches that need an algebraic coincidence -- and that
        # shortfall is written down as a number rather than hidden under a threshold.
        expect = baseline.get(rel, len(labels))
        harvested = rel in baseline
        if len(hit) < expect:
            mark = "LOST"
            res.coverage_gaps.append(
                "%s covers %d branches, below its recorded %d" % (rel, len(hit),
                                                                  expect))
        elif len(hit) == len(labels):
            mark = "ok  "
        else:
            mark = "base"
        w("    %s %-56s %3d/%3d  %5.1f%%%s\n"
          % (mark, rel, len(hit), len(labels),
             100.0 * len(hit) / len(labels) if labels else 100.0,
             "   (harvested, baseline %d)" % expect
             if harvested and len(hit) != len(labels) else ""))
        if len(hit) != len(labels) and not harvested:
            gaps.append((src, sorted(labels - hit)))
    if total_l:
        w("    %-60s %3d/%3d  %5.1f%%\n"
          % ("TOTAL", total_c, total_l, 100.0 * total_c / total_l))
    w("\n")

    for src, missing in gaps:
        shown = missing if show_all else missing[:6]
        w("    %s unexercised: %s%s\n"
          % (os.path.relpath(src, ROOT), ", ".join(shown),
             "" if len(shown) == len(missing)
             else "  (+%d more, --show-all)" % (len(missing) - len(shown))))
    if gaps:
        w("\n")

    if res.precondition:
        w("  %d case(s) landed in the D1 == D2 region and were not counted; that is\n"
          "  the documented precondition, errata E1, and belongs to PR5 rather than\n"
          "  to this harness.\n\n" % res.precondition)

    if res.unparsed:
        w("  COULD NOT PARSE (%d)\n" % len(res.unparsed))
        for line in (res.unparsed if show_all else res.unparsed[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.no_branch:
        w("  REACHED NO BRANCH (%d) -- a constructed case that exercises nothing is\n"
          "  not doing the job it was built for\n" % len(res.no_branch))
        for line in (res.no_branch if show_all else res.no_branch[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.errors:
        w("  ERRORS (%d distinct)\n" % len(res.errors))
        for k, n in res.errors.most_common(None if show_all else 10):
            w("    %4d x %s\n" % (n, k))
        w("\n")

    if res.mismatches:
        w("  MISMATCHES (%d), first %d\n"
          % (len(res.mismatches), min(5, len(res.mismatches))))
        for m in res.mismatches[:5]:
            w("    %s #%d %s over GF(%d)\n"
              % (m["tester"], m["index"], m["op"], m["field"]))
            w("      f = %s\n      h = %s\n" % (m["f"], m["h"]))
            w("      got  %s\n      want %s\n" % (m["got"], m["want"]))
            w("      branch: %s\n\n" % (" -> ".join(m["labels"]) or "(none)"))

    missing_fams = _families_without_testers(testers)
    if missing_fams:
        w("  no Magma whitebox tester exists for these, so their cases are harvested\n"
          "  into harvested_cases.json instead (%d)\n" % len(missing_fams))
        for fam, why in missing_fams:
            w("    %-40s %s\n" % (fam, why))
        w("\n")

    # Nothing may pass by testing nothing.
    if res.replayed == 0:
        res.coverage_gaps.append("no case was replayed at all")
    empty = [os.path.basename(t) for t, n in sorted(res.cases_per_tester.items())
             if n == 0]
    if empty:
        res.coverage_gaps.append(
            "%d tester(s) yielded no cases: %s" % (len(empty), ", ".join(empty)))

    if res.failed():
        reasons = []
        if res.mismatches:
            reasons.append("%d mismatch(es)" % len(res.mismatches))
        if res.unparsed:
            reasons.append("%d unparsed case(s)" % len(res.unparsed))
        if res.no_branch:
            reasons.append("%d case(s) reached no branch" % len(res.no_branch))
        if res.errors:
            reasons.append("%d error kind(s)" % len(res.errors))
        if res.coverage_gaps:
            reasons.append("%d file(s) lost branch coverage" % len(res.coverage_gaps))
        w("  FAILED: %s\n\n" % ", ".join(reasons))
        return 1
    w("  PASS: every constructed case replayed, reached a branch, and matched\n\n")
    return 0


def _families_without_testers(testers):
    have = {family_of(t)[:3] + (family_of(t)[3],) for t in testers}
    known = [
        (("ramified", 3, "arb", None), "harvested at 100%; PR6 writes the tester"),
        (("ramified", 3, "nch2", None), "harvested at 100%; PR6 writes the tester"),
        (("split", 3, "ch2", "neg"),
         "harvested to a baseline; all three genus-3 split generators cannot run"),
    ]
    out = []
    for key, why in known:
        if key in have:
            continue
        model, genus, kind, basis = key
        label = "g%d/%sModel%s %s" % (genus, model,
                                      "/%sReduced" % basis if basis else "", kind)
        out.append((label, why))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--family", default=None,
                    help="substring of a tester path to restrict to")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--show-all", action="store_true")
    ap.add_argument("--harvest", action="store_true",
                    help="regenerate harvested_cases.json for the families that have "
                         "no whitebox tester. Offline and deliberately separate from "
                         "the replay: CI never samples, it replays what this froze")
    a = ap.parse_args(argv)

    testers = find_testers()
    if a.family:
        testers = [t for t in testers if a.family in t]

    if a.list:
        print("\n  whitebox testers found (%d)\n" % len(testers))
        for t in testers:
            cases, bad = extract(t)
            model, genus, kind, basis = family_of(t)
            print("    %-46s %4d cases  %s/g%d/%s%s"
                  % (os.path.basename(t), len(cases), model, genus, kind,
                     "/" + basis if basis else ""))
            if bad:
                print("        %d block(s) unparsed" % len(bad))
        missing = _families_without_testers(testers)
        if missing:
            print("\n  no tester exists for (%d)\n" % len(missing))
            for fam, why in missing:
                print("    %-40s %s" % (fam, why))
        print()
        return 0

    # Do not bail on an empty tester list: the three families without a tester have
    # harvested cases and nothing else, so `--family g3/ramifiedModel` must still run.
    if not testers:
        records, _b = load_harvested()
        if a.family and not any(a.family in os.path.join(ROOT, _family_dir(r))
                                for r in records):
            print("no whitebox tester and no harvested case matched %r" % a.family)
            return 2
        if not records:
            print("no whitebox tester and no harvested case found")
            return 2

    if a.harvest:
        fams, _excl = D.discover_families()
        targets = [f for f in fams if not _has_tester(f, testers)]
        if not targets:
            print("every family has a whitebox tester; nothing to harvest")
            return 0
        print("\n  harvesting for %d family(ies) with no whitebox tester\n"
              % len(targets))
        records, baseline = harvest(targets)
        payload = {
            "note": ("Constructed cases for families with no whitebox tester. "
                     "Regenerate with `python3 whitebox.py --harvest`. CI replays "
                     "these and never samples."),
            "baseline": baseline,
            "cases": records,
        }
        with open(HARVEST_FILE, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
        print("\n  wrote %d cases and %d baselines to %s\n"
              % (len(records), len(baseline), os.path.basename(HARVEST_FILE)))
        return 0

    res = Result()
    for t in testers:
        n = replay_tester(t, res, a.show_all)
        print("  %-46s %4d cases" % (os.path.basename(t), n))
    n = replay_harvested(res, a.show_all, a.family)
    if n:
        print("  %-46s %4d cases" % ("harvested_cases.json", n))
    _cases, baseline = load_harvested()
    return report(res, testers, a.show_all, baseline)


def _has_tester(fam, testers):
    """Whether a driver family is covered by one of the whitebox testers."""
    for t in testers:
        model, genus, kind, basis = family_of(t)
        name = "%s%s/g%d/%s" % (model, basis or "", genus, kind)
        if name == fam.name:
            return True
    return False


if __name__ == "__main__":
    sys.exit(main())
