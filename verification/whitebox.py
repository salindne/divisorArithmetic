"""whitebox.py -- replay the repository's frozen whitebox cases in Python.

The whitebox testers are generated files holding one case per computation path: a
curve, a basis, both divisors, both balancing weights. They already pass under Magma,
so the inputs are vetted. This reads them, runs the real `.mag` formulas on those
inputs through the interpreter, and compares against `reference.py`.

**Where those cases came from, precisely.** They were *found by random search*, not
built by hand. `whitebox/genFiles/*_WB_gen.mag` loops over random curves and divisor
pairs, prints a block for each operation that agrees with Magma's own Cantor
arithmetic, and lets the formula's own ADD_DEBUG/DBL_DEBUG label name the branch;
`whitebox/whitebox_auto_NEG.py` keeps the first block seen for each label until every
label has one. So "constructed case" below means **frozen and committed**, as opposed
to sampled afresh each run -- it does not mean anyone chose the inputs. That is worth
being exact about, because the value of these cases rests on two properties that
survive the correction and one claim that does not:

  * they are **complete** -- every labelled branch has a case, which random sampling
    in CI time does not achieve;
  * they are **deterministic** -- the same inputs every run, so coverage is a fact
    about the corpus rather than about this run's luck;
  * they are *not* independently designed probes of each branch. A branch is covered
    by whatever input the search happened to land on first.

Coverage under sampling is coupon-collector -- measured across all fourteen families,
35% at 2 curves, 54% at 4, 77% at 16, 84% at 30, then it stalls -- so 100% is not
reachable in CI time and possibly not at all. A frozen corpus with one case per branch
reaches every branch in seconds, every time.

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
  100% coverage. A tester was built by searching until every branch had a case, so a
  file that now covers fewer branches than its tester holds is a regression.

  **harvested** by `--harvest`, for every branch no extracted case reaches: because
  the family has no tester at all (genus-3 ramified), or because the tester's own
  search missed it (genus-3 split ch2, whose regenerated tester reaches 347 of 413).
  Search for an input reaching the branch, then freeze it. Held to the coverage
  recorded when it was harvested, since search cannot be assumed to reach a branch
  needing an algebraic coincidence.

**These two are the same kind of artefact.** Both are the frozen output of a
coverage-guided random search; the difference is only which language ran the search
and whether the result was committed as a Magma tester. That symmetry is the reason
harvesting is an acceptable substitute where no tester exists, and it is why the
report labels each case's provenance rather than implying one is sounder.

Either way, this replays frozen inputs and never samples. Randomness builds the
corpus once, offline; it is not part of the gate.

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

# Frozen cases for branches no Magma tester reaches. Committed, because there is
# nothing to read them out of -- either no tester exists for the family, or its
# search never landed on the branch. Written by `--harvest`, replayed exactly like an
# extracted case.
HARVEST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "harvested_cases.json")

# Every formula file whose coverage is expected to be below its label count, with the
# reason. One artefact for all such cases, because there are two unrelated causes and
# collapsing them into "whatever the last harvest happened to find" made the number
# self-certifying: `--harvest` wrote both the cases and the figure they were graded
# against, so a worse harvest silently lowered the bar.
#
# Written by `--record-baseline`, which REFUSES to lower an existing entry without
# --allow-lower, so a regression cannot be absorbed by re-recording.
BASELINE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "coverage_baseline.json")


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

def tname(path):
    """A tester label that is unambiguous in reports.

    Basenames collide: nch2_splitG2_whiteBox_tester.mag exists under both
    g2/splitModel/posReduced/ and negReduced/, and those are different algorithms
    (which leading coefficient the reduce loop tests first). A failure reported as
    the basename alone left the reader to guess which basis it came from. The parent
    directory is enough to separate every collision in the tree.
    """
    return os.path.join(os.path.basename(os.path.dirname(path)),
                        os.path.basename(path))


class Case(object):
    """One constructed case, with where it came from."""

    def __init__(self, tester, index, q, f, h, V, D1, D2, op):
        self.tester, self.index, self.q = tester, index, q
        self.f, self.h, self.V = f, h, V
        self.D1, self.D2, self.op = D1, D2, op

    def __repr__(self):
        return "<Case %s #%d %s over GF(%d)>" % (
            tname(self.tester), self.index, self.op, self.q)


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
    # Basename, not tname(): the pattern below is anchored, and a parent directory
    # in front of it would never match.
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
                       % (tname(tester), (i + 1) // 2, q,
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
        self.precondition = []
        # Coverage here is 100% by construction -- one constructed case per branch --
        # so any gap is a regression, not a sampling artefact, and fails the run.
        self.coverage_gaps = []
        # Unguarded fall-through markers reached. Never a coverage win: reaching one
        # means the formulas fell through to a case their author believed impossible.
        self.sentinels = []
        # Returns whose value count is not what the model calls for -- errata E2. The
        # extra value used to be truncated and the case counted as a match.
        self.arity = []            # unexpected: fatal
        self.arity_known = []      # errata E2, pinned by identity: reported only
        self.arity_seen = set()
        self.drifted = []          # a harvested case no longer reaches what it recorded
        # Files that MUST be accounted for, derived from the testers found and the
        # harvest baseline rather than from what happened to be covered. Without this
        # the coverage loop iterated over its own results, so a tester that yielded no
        # cases left its formula file out of the loop entirely and the run passed
        # having tested nothing. Verified: 11 testers, 0 cases, exit 0.
        self.expected_files = set()
        self.cases_per_tester = {}

    def failed(self):
        # `precondition` is fatal here, unlike in driver.py. driver.py generates inputs
        # and legitimately lands in the D1 == D2 region; a CONSTRUCTED case never should,
        # and measurably none does, so a case arriving there means this harness
        # misclassified it.
        return bool(self.mismatches or self.unparsed or self.errors
                    or self.no_branch or self.coverage_gaps or self.precondition
                    or self.sentinels or self.arity or self.drifted
                    or self.replayed != self.matched)


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


def expected_formula_files():
    """Every formula file that must be accounted for, from the authoritative source.

    Derived from `driver.discover_families`, which walks the tree, rather than from the
    whitebox testers found on disk. Deriving it from the testers made the expectation a
    function of the evidence: delete a tester and its formula file stopped being
    expected, so it vanished from the report instead of failing. A newly added formula
    file was equally invisible.
    """
    out = set()
    fams, _excluded = D.discover_families()
    for fam in fams:
        for p in (fam.add_path, fam.dbl_path, fam.utl_path):
            if p and os.path.isfile(p):
                out.add(p)
    return out


def replay_tester(tester, res, show_all):
    model, genus, kind, basis = family_of(tester)
    add_path, dbl_path, utl_path = _formula_paths(model, genus, kind, basis)
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
                    add_path, dbl_path, res, utl_path)
    return len(cases)


def _replay_one(case, model, genus, basis, subs, params, add_path, dbl_path, res,
                utl_path=None):
    F = GF(case.q)
    fn = subs.get(case.op)
    if fn is None or case.op not in params:
        res.errors["%s: no %s dispatcher" % (tname(case.tester),
                                             case.op)] += 1
        return
    src = add_path if case.op == "ADD" else dbl_path
    path = []
    try:
        cur = C.Curve(F, case.f, case.h, kind_for(case, model), genus, model)
    except AssertionError as exc:
        res.errors["%s #%d: curve rejected: %s"
                   % (tname(case.tester), case.index,
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
            raw = subs["Precompute"](case.f, case.h, case.q, path=path,
                                     funcs=subs, F=F)
            ccs = raw[0] if len(raw) == 1 else list(raw)
        except Exception as exc:                                # noqa: BLE001
            res.errors["%s #%d: Precompute: %s: %s"
                       % (tname(case.tester), case.index,
                          type(exc).__name__, str(exc)[:50])] += 1
            return
        finally:
            M.ROOT_PIN[0] = None
        d1 = _split_divisor(cur, case.D1, basis_poly)
        d2 = _split_divisor(cur, case.D2, basis_poly) if case.D2 else None
        if d1 is None or (case.op == "ADD" and d2 is None):
            res.errors["%s #%d: could not form a balanced divisor"
                       % (tname(case.tester), case.index)] += 1
            return
        args = D.build_args_split(params[case.op], cur, ccs, d1, d2)
    else:
        d1 = (case.D1[0], case.D1[1])
        d2 = (case.D2[0], case.D2[1]) if case.D2 else None
        args = D.build_args(params[case.op], cur, d1, d2)

    # The whole divisor, not just (u, v). In the split model a divisor is (u, v, w, n)
    # and the balancing weight is part of its identity, so two operands agreeing on u
    # and v but differing in n are DISTINCT divisors and a perfectly legal addition.
    #
    # Comparing only u and v classified 41 such cases as the documented `D1 != D2`
    # precondition and discarded their verdicts. Measured across the extracted corpus:
    # 41 ADD cases have equal (u, v) and ZERO have equal (u, v, n) -- so the test never
    # once fired on a genuinely identical pair, only on 41 legal additions. Those 41 are
    # also the sole coverage of 41 branches, 13 of them in arb_splitG3_ADD.mag. A defect
    # confined to them produced "1682 replayed, 1641 matched, 0 mismatched, PASS", exit 0.
    same = (case.op == "ADD" and case.D2 is not None
            and tuple(case.D1) == tuple(case.D2))
    try:
        vals = fn(*args, path=path, funcs=subs, F=F)
    except Exception as exc:                                    # noqa: BLE001
        if same:
            res.precondition.append(
                "%s #%d %s raised %s where D1 == D2"
                % (tname(case.tester), case.index, case.op,
                   type(exc).__name__))
            return
        res.errors["%s #%d %s: %s: %s"
                   % (tname(case.tester), case.index, case.op,
                      type(exc).__name__, str(exc)[:50])] += 1
        return

    # Precompute's labels belong to the UTL file, not to the ADD/DBL file, so they are
    # split out by name. Without this they were discarded entirely: the nine split UTL
    # files carry 42 labels between them and all 42 read as unexercised.
    utl_labels = set()
    if utl_path and os.path.isfile(utl_path):
        utl_labels = D.labels_in(utl_path)
        res.covered[utl_path].update(
            x[6:] for x in path if x.startswith("PRINT:") and x[6:] in utl_labels)
    labels = [x[6:] for x in path
              if x.startswith("PRINT:") and x[6:] not in utl_labels]
    _note_sentinels(res, src, labels,
                    "%s #%d %s" % (tname(case.tester), case.index,
                                   case.op))
    if not labels:
        res.no_branch.append("%s #%d %s reached no branch label"
                             % (tname(case.tester), case.index,
                                case.op))

    if model == "split":
        gu, gv, gn, note = D.decode_split(F, genus, vals, basis_poly)
        if gu is None:
            res.errors["%s #%d: %s" % (tname(case.tester),
                                       case.index, note)] += 1
            return
        try:
            want = (R.split_add(cur, d1, d2, basis_poly, basis == "pos")
                    if case.op == "ADD"
                    else R.split_double(cur, d1, basis_poly, basis == "pos"))
        except Exception as exc:                                # noqa: BLE001
            res.errors["reference %s: %s: %s"
                       % (_case_id(case), type(exc).__name__, str(exc)[:50])] += 1
            return
        got, exp = (gu, gv, gn), (want[0], want[1], want[3])
    else:
        gu, gv, note = D.decode_divisor(F, genus, vals)
        if note:
            res.arity_seen.add(_case_id(case))
            # errata E2: a return with one value too many. driver.py already records
            # this; whitebox truncated it and counted the case as a match.
            line = "%s over GF(%d): %s" % (_case_id(case), case.q, note)
            if _case_id(case) in KNOWN_ARITY[0]:
                res.arity_known.append(line)
            else:
                res.arity.append(line)
        if gu is None:
            res.errors["%s #%d: bad return arity"
                       % (tname(case.tester), case.index)] += 1
            return
        try:
            want = (R.add(cur, d1, d2) if case.op == "ADD" else R.double(cur, d1))
        except Exception as exc:                                # noqa: BLE001
            res.errors["reference %s: %s: %s"
                       % (_case_id(case), type(exc).__name__, str(exc)[:50])] += 1
            return
        got, exp = (gu, gv), (want[0], want[1])

    res.replayed += 1
    if all(a == b for a, b in zip(got, exp)):
        res.matched += 1
        # Coverage is banked only for a verdict that was actually CHECKED. Banking it
        # before the comparison meant a discarded verdict still counted its branch as
        # covered, so 41 branches read as verified while nothing verified them.
        res.covered[src].update(labels)
        return
    if same:
        # A constructed case must never be in the D1 == D2 region -- none of the 1,338
        # extracted cases is -- so landing here means the harness is wrong about the
        # case, not that the case is excused. Recorded and fatal.
        res.precondition.append(
            "%s #%d %s disagreed where D1 == D2"
            % (tname(case.tester), case.index, case.op))
        return
    res.mismatches.append(dict(
        tester=tname(case.tester), index=case.index, op=case.op,
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


def _case_id(case):
    """A case identity that survives duplicate basenames: family + index + op."""
    model, genus, kind, basis = family_of(case.tester)
    return "%s%s/g%d/%s #%d %s" % (model, basis or "", genus, kind, case.index,
                                   case.op)


# Loaded once by main(); a list so helpers can read it without threading it through.
KNOWN_ARITY = [set()]


def _note_sentinels(res, src, labels, where):
    """Record any unguarded fall-through marker this case reached."""
    for name in sorted(set(labels) & D.sentinel_labels(src)):
        res.sentinels.append("%s reached %r, an unguarded fall-through marker"
                             % (where, name))


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


def harvest(families, seed=1, curves=40, pairs=12, already=None):
    """Find one input per branch for families that have no whitebox tester.

    Genus-3 ramified is the reason this exists. It has no whitebox tester -- PR6
    builds them -- and it is the family this merge series is for, so it cannot go
    untested. Its three developed files (arb ADD, arb DBL, nch2 ADD) get constructed
    cases the only way available: search for an input reaching each labelled branch,
    then freeze it. The three undeveloped cells (nch2 DBL, ch2 ADD, ch2 DBL) have no
    files, so there is nothing to cover until PR6 through PR8 derive them.

    The search uses the random generators, but **the result is a frozen case like any
    other**: CI replays frozen inputs and never samples. Randomness builds the corpus
    once, offline; it is not part of the gate. That is the same procedure the Magma
    whitebox generators use, so an extracted case and a harvested one are the same kind
    of artefact -- see the module docstring.

    `already` maps a formula file to the labels an extracted tester case already
    reaches, and those are skipped. This used to run only for families with no tester
    at all, which left no way to fill a branch a tester's own search had missed: the
    genus-3 split ch2 tester covers 347 of its 413 labels, and the remainder are
    reachable but rare. Harvesting the difference makes the corpus the union of both
    searches, and keeps working unchanged when PR6 adds the genus-3 ramified testers.

    For the split model the infinite-place root is pinned to the reference's own Vp, so
    Precompute's constants and the reference agree by construction rather than by
    convention -- the same trick the extracted cases use with their supplied V.
    """
    out, baseline = [], {}
    for fam in families:
        for op, src in (("ADD", fam.add_path), ("DBL", fam.dbl_path)):
            if not src or not os.path.isfile(src):
                continue
            want = D.labels_in(src) - (already or {}).get(src, set())
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


def _harvest_context(fam, cur, subs, F, utl_path_labels=None):
    """(basis polynomial, ccs) for a generated curve, or None if unusable.

    `utl_path_labels` collects Precompute's own branch labels, which are otherwise
    discarded: the nine split UTL files carry 42 of them and all 42 read as unexercised
    because the call was made without a path to record into.
    """
    if utl_path_labels is None:
        utl_path_labels = []
    if not fam.is_split:
        return (None, None)
    try:
        Vp = R.compute_vp(cur)
    except ArithmeticError:
        return None
    basis_poly = Vp if fam.basis == "pos" else (-Vp - cur.h)
    M.ROOT_PIN[0] = Vp.coeff(fam.genus + 1)
    try:
        raw = subs["Precompute"](cur.f, cur.h, F.q, path=utl_path_labels,
                                 funcs=subs, F=F)
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
    # The whole divisor, for the same reason the replay path compares the whole divisor:
    # in the split model (u, v) equal with different weights is a legal addition, not the
    # documented precondition. Comparing only u and v here discarded exactly the class of
    # input that turned out to be the sole coverage of 41 branches.
    if tuple(d1) == tuple(d2):
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
               source="harvested: no extracted whitebox case reaches this branch")
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
    """The committed harvested cases, or []."""
    if not os.path.isfile(HARVEST_FILE):
        return []
    data = json.loads(open(HARVEST_FILE).read())
    if isinstance(data, list):
        return data
    return data.get("cases", [])


def load_baseline():
    """{repo-relative file: set of branches EXEMPT from coverage} -- `unreached`.

    The exempt set is stored explicitly, as labels, and everything else in the file
    must be covered. Storing what IS covered was tried first and left a hole: a newly
    added branch was neither in the recorded set nor missing from it, so it was exempt
    by accident. Storing what is NOT covered makes a new branch fail by default, which
    is the right default. A count was worse still -- it let branches be traded
    one-for-one while the number held, kept a stale entry downgrading a file that had
    since acquired a tester, and made a baseline of 0 unfailable.
    """
    if not os.path.isfile(BASELINE_FILE):
        return {}
    data = json.loads(open(BASELINE_FILE).read())
    out = {}
    for k, v in data.get("files", {}).items():
        if isinstance(v, dict) and isinstance(v.get("unreached"), list):
            out[k] = set(v["unreached"])
    return out


def known_arity_anomalies():
    """Case identities allowed to return the wrong number of values.

    Pinned by IDENTITY rather than by count, so a NEW anomaly fails even when known
    ones exist. The set is EMPTY since PR5 fixed errata E2 -- one branch of every
    genus-2 ramified ADD returned 6 values where 5 are expected, and the three
    tester cases reaching it were pinned here until the fix landed. The machinery
    stays: it is what let the gate run green over a recorded defect without hiding
    it, and the next such defect uses it the same way.
    """
    if not os.path.isfile(BASELINE_FILE):
        return set()
    data = json.loads(open(BASELINE_FILE).read())
    return set(data.get("arity_anomalies", []))


def baseline_reasons():
    if not os.path.isfile(BASELINE_FILE):
        return {}
    data = json.loads(open(BASELINE_FILE).read())
    return {k: v.get("why", "") for k, v in data.get("files", {}).items()}


def replay_harvested(res, show_all, only=None):
    """Replay the committed harvested cases, for both models.

    Model-aware for the same reason `harvest` is: genus-3 split ch2 has formulas but
    no whitebox tester, so its cases are harvested too, and a split case needs its
    basis polynomial and ccs rebuilt rather than just a curve and two divisors.
    """
    records = load_harvested()
    baseline = load_baseline()
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
        try:
            params = D._dispatcher_body(src, rec["op"])[0]
        except Exception as exc:                                # noqa: BLE001
            res.errors["harvested %d: cannot read the %s signature: %s"
                       % (i, rec["op"], type(exc).__name__)] += 1
            continue
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
            utl_sink = []
            ctx = _harvest_context(fam, cur, subs, F, utl_sink)
            if ctx is None:
                res.errors["harvested %d: could not rebuild the split context" % i] += 1
                continue
            basis_poly, ccs = ctx
            if fam.utl_path and os.path.isfile(fam.utl_path):
                names = D.labels_in(fam.utl_path)
                res.covered[fam.utl_path].update(
                    x[6:] for x in utl_sink
                    if x.startswith("PRINT:") and x[6:] in names)
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
        _note_sentinels(res, src, labels, "harvested case %d" % i)
        # The corpus is only meaningful if a case still reaches what it recorded.
        # Coverage is compared in aggregate, so a case could drift to a different
        # branch and the totals would hide it. Zero drift measured today; this is the
        # guard that keeps it so.
        if rec.get("labels") is not None and labels != rec["labels"]:
            res.drifted.append(
                "harvested case %d (%s %s) recorded %s but reached %s"
                % (i, rec["family"], rec["op"], rec["labels"], labels))
        if not labels:
            res.no_branch.append("harvested case %d reached no branch label" % i)
        res.covered[src].update(labels)

        if model == "split":
            gu, gv, gn, note = D.decode_split(F, fam.genus, vals, basis_poly)
            if gu is None:
                res.errors["harvested %d: %s" % (i, note)] += 1
                continue
            try:
                want = (R.split_add(cur, d1, d2, basis_poly, fam.basis == "pos")
                        if rec["op"] == "ADD"
                        else R.split_double(cur, d1, basis_poly, fam.basis == "pos"))
            except Exception as exc:                            # noqa: BLE001
                res.errors["reference harvested %d: %s: %s"
                           % (i, type(exc).__name__, str(exc)[:50])] += 1
                continue
            got, exp = (gu, gv, gn), (want[0], want[1], want[3])
        else:
            gu, gv, note = D.decode_divisor(F, fam.genus, vals)
            if note:
                ident = "harvested %s #%d %s" % (rec["family"], i, rec["op"])
                res.arity_seen.add(ident)
                (res.arity_known if ident in KNOWN_ARITY[0]
                 else res.arity).append("%s: %s" % (ident, note))
            if gu is None:
                res.errors["harvested %d: bad return arity" % i] += 1
                continue
            try:
                want = (R.add(cur, d1, d2) if rec["op"] == "ADD"
                        else R.double(cur, d1))
            except Exception as exc:                            # noqa: BLE001
                res.errors["reference harvested %d: %s: %s"
                           % (i, type(exc).__name__, str(exc)[:50])] += 1
                continue
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
        # Compared as SETS, with the baseline storing what is EXEMPT (`unreached`).
        # Everything not exempt must be covered, so a newly added branch fails by
        # default rather than inheriting the exemption -- the hole the covered-set
        # form left open. Three further rules keep an entry honest: an exempt label
        # that IS now reached is stale and must be re-recorded; an exempt label the
        # file no longer contains is stale the other way; and no entry may exempt a
        # whole file.
        exempt = baseline.get(rel)
        missing = labels - hit
        extra_note = ""
        if exempt is None:
            if missing:
                mark = "LOST"
                res.coverage_gaps.append(
                    "%s misses %d branch(es) and has no baseline entry: %s"
                    % (rel, len(missing), ", ".join(sorted(missing)[:4])))
            else:
                mark = "ok  "
        else:
            extra_note = "   (%d exempt by baseline)" % len(exempt)
            unexpected = missing - exempt
            stale_hit = exempt & hit
            stale_gone = exempt - labels
            if not hit and labels:
                mark = "LOST"
                res.coverage_gaps.append(
                    "%s covers nothing at all; no baseline may exempt a whole file"
                    % rel)
            elif unexpected:
                mark = "LOST"
                res.coverage_gaps.append(
                    "%s misses %d branch(es) its baseline does not exempt: %s"
                    % (rel, len(unexpected), ", ".join(sorted(unexpected)[:4])))
            elif stale_gone:
                mark = "LOST"
                res.coverage_gaps.append(
                    "%s's baseline exempts %d label(s) the file no longer contains: "
                    "%s -- re-record" % (rel, len(stale_gone),
                                         ", ".join(sorted(stale_gone)[:4])))
            elif stale_hit:
                mark = "UP  "
                res.coverage_gaps.append(
                    "%s now reaches %d branch(es) its baseline exempts: %s -- good "
                    "news, but the entry is stale; rerun --record-baseline to accept"
                    % (rel, len(stale_hit), ", ".join(sorted(stale_hit)[:4])))
            else:
                mark = "base"
        w("    %s %-56s %3d/%3d  %5.1f%%%s\n"
          % (mark, rel, len(hit), len(labels),
             100.0 * len(hit) / len(labels) if labels else 100.0, extra_note))
        # Unexercised branches are listed for EVERY file, baselined or not. They used
        # to be listed only for non-baselined files, so ~131 uncovered branches could
        # not be named by any invocation.
        if labels - hit:
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
        w("  MISCLASSIFIED AS D1 == D2 (%d). A constructed case must never be in that\n"
          "  region -- none of the extracted corpus is -- so landing here means this\n"
          "  harness is wrong about the case, not that the case is excused.\n"
          % len(res.precondition))
        for line in (res.precondition if show_all else res.precondition[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.arity_known:
        w("  WRONG RETURN ARITY, known and pinned (%d).\n"
          "  Not fatal while pinned by case identity in coverage_baseline.json; a\n"
          "  NEW one still fails. (The E2 pins were removed when PR5 fixed it.)\n"
          % len(res.arity_known))
        for line in (res.arity_known if show_all else res.arity_known[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.arity:
        w("  WRONG RETURN ARITY, NOT pinned (%d). The extra value is truncated and the\n"
          "  case would otherwise be counted as a match.\n" % len(res.arity))
        for line in (res.arity if show_all else res.arity[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.sentinels:
        w("  UNGUARDED FALL-THROUGH MARKER REACHED (%d). These are not branches to\n"
          "  cover: reaching one means the formulas fell through to a case their\n"
          "  author believed impossible.\n" % len(res.sentinels))
        for line in (res.sentinels if show_all else res.sentinels[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.unparsed:
        w("  COULD NOT PARSE (%d)\n" % len(res.unparsed))
        for line in (res.unparsed if show_all else res.unparsed[:10]):
            w("    %s\n" % line)
        w("\n")

    if res.drifted:
        w("  HARVESTED CASES DRIFTED (%d) -- the case no longer reaches the branch it\n"
          "  was frozen for, so the corpus no longer covers what its baseline claims.\n"
          % len(res.drifted))
        for line in (res.drifted if show_all else res.drifted[:6]):
            w("    %s\n" % line)
        w("\n")

    if res.drifted:
        w("  HARVESTED CASES DRIFTED (%d) -- the case no longer reaches the branch it\n"
          "  was frozen for, so the corpus no longer covers what its baseline claims.\n"
          % len(res.drifted))
        for line in (res.drifted if show_all else res.drifted[:6]):
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
    empty = [tname(t) for t, n in sorted(res.cases_per_tester.items())
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
        if res.arity:
            reasons.append("%d case(s) with a wrong return arity" % len(res.arity))
        if res.sentinels:
            reasons.append("%d fall-through marker(s) reached" % len(res.sentinels))
        if res.drifted:
            reasons.append("%d harvested case(s) drifted from their recorded branches"
                           % len(res.drifted))
        if res.precondition:
            reasons.append("%d case(s) misclassified as D1 == D2"
                           % len(res.precondition))
        if res.replayed != res.matched:
            reasons.append("%d replayed but only %d matched -- a verdict was discarded"
                           % (res.replayed, res.matched))
        w("  FAILED: %s\n\n" % ", ".join(reasons))
        return 1
    w("  PASS: every constructed case replayed, reached a branch, and matched\n\n")
    return 0


def _families_without_testers(testers):
    """Families whose cases can only be harvested, because no tester exists.

    The genus-3 split ch2 entry has been removed: its generator was repaired and its
    tester regenerated, so it is extracted like every other split family. Harvest still
    supplements it for the branches that tester's own search did not reach, which is a
    different thing and is reported by file coverage rather than here.
    """
    have = {family_of(t)[:3] + (family_of(t)[3],) for t in testers}
    known = [
        (("ramified", 3, "arb", None), "harvested at 100%; PR6 writes the tester"),
        (("ramified", 3, "nch2", None), "harvested at 100%; PR6 writes the tester"),
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
    ap.add_argument("--record-baseline", action="store_true",
                    help="write coverage_baseline.json from this run's coverage. "
                         "Refuses to LOWER an existing entry unless --allow-lower is "
                         "given, so a regression cannot be absorbed by re-recording")
    ap.add_argument("--allow-lower", action="store_true",
                    help="with --record-baseline, permit lowering an entry. Say why in "
                         "the commit message")
    ap.add_argument("--harvest-curves", type=int, default=40,
                    help="curves per field when harvesting (default 40)")
    ap.add_argument("--harvest-pairs", type=int, default=12,
                    help="divisor pairs per curve when harvesting (default 12)")
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
                  % (tname(t), len(cases), model, genus, kind,
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
        records = load_harvested()
        if a.family and not any(a.family in os.path.join(ROOT, _family_dir(r))
                                for r in records):
            print("no whitebox tester and no harvested case matched %r" % a.family)
            return 2
        if not records:
            print("no whitebox tester and no harvested case found")
            return 2

    if a.harvest and a.family:
        # A filtered harvest would write cases for some families and leave the rest of
        # the corpus stale, while the baseline it is graded against covers all of them.
        print("--harvest cannot be combined with --family: a partial harvest would\n"
              "leave the rest of the corpus stale. Harvest everything, or not at all.")
        return 2

    if a.harvest:
        fams, _excl = D.discover_families()

        # What the Magma testers already reach, so the harvest fills the difference
        # instead of duplicating them. Every family is a candidate now, not just the
        # ones with no tester: a tester is itself the product of a random search, so it
        # can leave branches uncovered -- genus-3 split ch2 leaves 66 of 413 -- and
        # there was previously no way to reach those without hand-writing cases.
        extracted = Result()
        for t_path in testers:
            replay_tester(t_path, extracted, False)
        print("\n  extracted cases already cover %d branch(es) across %d file(s)"
              % (sum(len(v) for v in extracted.covered.values()),
                 len(extracted.covered)))

        targets = fams
        print("  harvesting the remainder for %d family(ies)\n" % len(targets))
        records, found = harvest(targets, already=extracted.covered,
                                curves=a.harvest_curves,
                                pairs=a.harvest_pairs)
        payload = {
            "note": ("Frozen cases filling the branches no Magma whitebox tester "
                     "reaches -- either because the family has no tester, or because "
                     "the tester's own random search missed them. Regenerate with "
                     "`python3 whitebox.py --harvest`. CI replays these and never "
                     "samples. Expected coverage lives in coverage_baseline.json, NOT "
                     "here, so a worse harvest cannot lower its own bar."),
            "cases": records,
        }
        with open(HARVEST_FILE, "w") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
        print("\n  wrote %d cases to %s" % (len(records),
                                            os.path.basename(HARVEST_FILE)))
        print("  coverage reached: %s"
              % ", ".join("%s=%d" % (tname(k), v)
                          for k, v in sorted(found.items())))
        print("  run --record-baseline to accept these figures\n")
        return 0

    if a.record_baseline and a.family:
        # A filtered run replays a subset, so recording from it would write
        # zero-coverage entries for every family the filter excluded -- a live path to
        # an unfailable baseline. Same rule as --harvest, for the same reason.
        print("--record-baseline cannot be combined with --family: a filtered run\n"
              "would record zero coverage for everything the filter excluded.")
        return 2

    KNOWN_ARITY[0] = known_arity_anomalies()
    res = Result()
    # Expectations scope to the filter: a filtered run must account for the filtered
    # families' files and no others, or --family marks the other 33 files LOST and
    # exits 1, making the flag useless for the focused runs it exists for. The
    # anti-vacuity guarantee is unchanged for the full run, which is what CI executes.
    expected = expected_formula_files()
    if a.family:
        expected = {p for p in expected if a.family in p}
    res.expected_files |= expected
    for t in testers:
        n = replay_tester(t, res, a.show_all)
        print("  %-52s %4d cases" % (tname(t), n))
    n = replay_harvested(res, a.show_all, a.family)
    if n:
        print("  %-46s %4d cases" % ("harvested_cases.json", n))
    if a.record_baseline:
        return _record_baseline(res, a.allow_lower)
    return report(res, testers, a.show_all, load_baseline())


def _record_baseline(res, allow_lower):
    """Write coverage_baseline.json from this run, refusing silent regressions."""
    old = load_baseline()
    reasons = baseline_reasons()
    new, lowered = {}, []
    for src in sorted(res.expected_files | set(res.covered)):
        labels = D.labels_in(src)
        if not labels:
            continue
        covered = res.covered.get(src, set()) & labels
        hit = len(covered)
        if hit >= len(labels):
            continue                      # at 100%; needs no entry
        rel = os.path.relpath(src, ROOT)
        newly_exempt = (labels - covered) - old.get(rel, set())
        if rel in old and newly_exempt:
            lowered.append((rel, len(newly_exempt),
                            ", ".join(sorted(newly_exempt)[:4])))
        why = reasons.get(rel) or _default_reason(rel)
        new[rel] = {"unreached": sorted(labels - covered),
                    "of": len(labels), "why": why}
    if lowered and not allow_lower:
        print("refusing to lower %d baseline entr%s:\n"
              % (len(lowered), "y" if len(lowered) == 1 else "ies"))
        for rel, n, names in lowered:
            print("  %s: would newly exempt %d branch(es): %s" % (rel, n, names))
        print("\nThat is a coverage regression, not a new baseline. Investigate, or\n"
              "pass --allow-lower and say why in the commit message.")
        return 1
    payload = {
        "note": ("Formula files whose coverage is expected below their label count. "
                 "`unreached` is the exact set of branches EXEMPT from coverage; "
                 "everything else in the file must be covered, so a newly added "
                 "branch fails by default and branches cannot be traded one-for-one. "
                 "Files absent from here must be at 100%. Written by "
                 "`whitebox.py --record-baseline`, which refuses to grow an entry's "
                 "exempt set without --allow-lower."),
        "arity_anomalies": sorted(res.arity_seen),
        "arity_note": ("Cases returning the wrong number of values, pinned by "
                       "identity so a NEW anomaly still fails. Empty since PR5 "
                       "fixed errata E2."),
        "files": new,
    }
    with open(BASELINE_FILE, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    print("\n  recorded %d baseline entr%s and %d pinned arity anomal%s to %s\n"
          % (len(new), "y" if len(new) == 1 else "ies",
             len(res.arity_seen), "y" if len(res.arity_seen) == 1 else "ies",
             os.path.basename(BASELINE_FILE)))
    for rel, v in sorted(new.items()):
        print("    %-58s %3d/%3d covered (%d exempt)  %s"
              % (rel, v["of"] - len(v["unreached"]), v["of"],
                 len(v["unreached"]), v["why"]))
    print()
    return 0


def _default_reason(rel):
    if rel.endswith("_UTL.mag"):
        return ("Precompute's own exits; the whitebox testers were built to cover "
                "ADD/DBL branches, not these")
    return ("coverage here comes from search -- a Magma tester's own generator and the "
            "Python harvester are both coverage-guided random searches -- and these "
            "branches were NOT reached by the recorded budget, which is not the same "
            "as being unreachable. Do not assume a nested IsZero guard means a "
            "coincidence to wait for: several of these are selected by the CURVE, not "
            "the divisors. z3 = W4*dn3 and dn3 collapses to exactly f3 in "
            "characteristic 2, so z3 = 0 iff f3 = 0, and deg(f - Vp*h - Vp^2) "
            "partitions the curves into four mutually exclusive classes that no single "
            "curve can span. See verification/README.md")


if __name__ == "__main__":
    sys.exit(main())
