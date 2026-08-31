"""
Operation counts for the explicit formulas, measured by running them.

    python3 verification/opcount.py                     # all fifteen families
    python3 verification/opcount.py --family ramified/g2/ch2
    python3 verification/opcount.py --family splitneg/g3/arb --json

WHY THIS AND NOT THE CONVERTER

`latexTables/latexConverter.py` produced the published tables by scanning the
source as text. This measures the same thing by executing the formulas over a
real finite field, and the two agree on all 208 published own-work quadruples --
two methods sharing no code, which is stronger evidence than either alone.

Two things this can do that a text scan cannot:

  * It counts inversions. The converter has no inversion accounting at all, so
    every `1I` in the thesis is hand-supplied. Measured here, and it comes out at
    exactly one for every published operation -- which is what chapter 5 claims
    in prose and nothing had ever checked.

  * It knows which branch is the frequent case, because it observes how often
    each is taken. Every published row quotes the frequent case; the converter
    infers it from the shape of the source. The two agree, so that inference is
    now validated rather than assumed -- but only one of them can be checked.

THE CONVENTIONS, AND WHERE THEY COME FROM

`chapter6.tex:2323-2336` sets them out: M multiplication, S squaring, C
multiplication by a curve coefficient, A addition, and "the assumption that
division by two ... is [an] addition is applied to the analysis". Additions are
counted, unlike most prior work. This module sets the interpreter's flags to
match, per file, from the file's own `//Constant:` and `//Ignore:` directives --
read from the source, never tabulated here, because a table would keep agreeing
after a banner changed.

HOW THE FREQUENT CASE IS DECIDED

Run many random valid divisor pairs through a function and histogram the
resulting (M,S,A,C,I) tuples; the modal tuple is the frequent case. Its share is
reported, and a share near 1 is the signal that the answer is not an artifact of
sampling. Every execution that contributes is also compared against
`reference.py`'s independent Cantor arithmetic, so an input outside the formulas'
domain is dropped rather than histogrammed as a plausible wrong count.

BOTH MODELS

All fifteen families are measured. The split half needs three things the
ramified half does not, which is why it was refused for so long: its domain
cannot be derived by the arb-contrast (the dispatchers read `ccs`, not curve
coefficients), its dispatcher signature needs `Precompute` run once per curve to
build that `ccs`, and its shapes are indexed by the balancing weight as well as
the degree. `driver.split_spec` and `driver.build_args_split` supply the first
two; the third is `_count_split`'s own, and it matters -- genus 3 prices
"Degree 1", "Degree 1 with Down Adjust" and "Degree 1 with two Up Adjusts"
separately, at 7M, 14M and 42M, and the input weight is exactly what selects
between them.

Two counting conventions are split-specific and both are the interpreter's
(`maginterp.INT_ARITH_FREE`, `DIV_LITERAL_AS_ADD`) rather than tabulated here.
The first is the one worth knowing: a split divisor's balancing weight is a small
integer, so `n := n1 + n2 - 2` is bookkeeping and not two field additions. Charged
as field additions it put a flat +2A on every split row.
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
import projcheck as PJ
import maginterp as M
import reference as R
from ff import GF

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

KEYS = ("M", "S", "A", "C", "I")
_DIRECTIVE = re.compile(r"^[ \t]*//[ \t]*(Constant|Ignore)[ \t]*:(.*)$", re.M)


# ---------------------------------------------------------------------------
# the conventions, read from each file
# ---------------------------------------------------------------------------

def directives(path):
    """({constants}, {ignored}) as the file declares them.

    Read from the source for the same reason `driver.read_support` is: a table
    here would go on agreeing with itself after someone edited a banner.
    """
    consts, ignored = set(), set()
    with open(path) as fh:
        for kind, body in _DIRECTIVE.findall(fh.read()):
            names = {t.strip() for t in body.split(",") if t.strip()}
            (consts if kind == "Constant" else ignored).update(names)
    return consts, ignored


class conventions(object):
    """Apply a file's counting conventions for the duration of a block.

    A context manager because the flags are module state on the interpreter: if
    an exception escapes mid-measurement the next family must not inherit the
    previous one's constant set, which would silently reclassify its products.
    """

    def __init__(self, *paths):
        self.consts, self.ignored = set(), set()
        for p in paths:
            if not p:
                continue
            c, i = directives(p)
            self.consts |= c
            self.ignored |= i

    def __enter__(self):
        self._saved = (M.CONSTS, M.IGNORED, M.DIV_LITERAL_AS_ADD,
                       M.INT_ARITH_FREE)
        M.CONSTS, M.IGNORED = self.consts, self.ignored
        M.DIV_LITERAL_AS_ADD = M.INT_ARITH_FREE = True
        return self

    def __exit__(self, *exc):
        (M.CONSTS, M.IGNORED, M.DIV_LITERAL_AS_ADD,
         M.INT_ARITH_FREE) = self._saved
        return False


# ---------------------------------------------------------------------------
# measuring
# ---------------------------------------------------------------------------

def _tuple_of(counts):
    return tuple(counts.get(k, 0) for k in KEYS)


def measure_call(fn, args, subs, F, path=None):
    """((M,S,A,C,I), result) for one call, or None if it raised.

    The dispatchers call their own Deg* siblings, so the sibling table has to be
    handed in at call time -- `fn(*args, funcs=subs, F=F)`. Discovering a file's
    functions is not enough on its own; without `funcs` the first sibling call
    raises "unknown function".
    """
    M.COUNT.clear()
    try:
        out = fn(*args, path=path if path is not None else [], funcs=subs, F=F)
    except Exception:
        return None
    return _tuple_of(M.COUNT), out


def _agrees(fam, cur, V, D1, D2, op, vals):
    """Does a measured call's RESULT match `reference.py`'s Cantor arithmetic?

    The module header has always claimed this check; until now nothing performed
    it. `measure_call` returned the value and the histogram discarded it, so a
    call that left the formulas' domain and came back with a wrong answer was
    histogrammed as a legitimate operation count -- the one failure mode that
    produces a plausible wrong number rather than an obvious one.

    Returns True (agrees, count it), False (disagrees, do not) or None (the
    reference could not be evaluated, so nothing is known and the sample is
    neither counted nor blamed).
    """
    F = cur.F
    try:
        if fam.is_split:
            gu, gv, gn, note = D.decode_split(F, fam.genus, vals, V)
            if gu is None:
                return False
            pos = (fam.basis == "pos")
            want = (R.split_add(cur, D1, D2, V, pos) if op == "ADD"
                    else R.split_double(cur, D1, V, pos))
            return gu == want[0] and gv == want[1] and gn == want[3]
        coords = getattr(fam, "coords", "affine")
        if coords == "projective":
            # A projective return has to be NORMALISED before it means anything,
            # and `decode_divisor` refuses it by design (PR46) rather than
            # guessing. Normalising here is what makes the counter of record able
            # to measure such a family at all: before this, `count_family` skipped
            # it with 'no ADD file' and the headline figure rested only on the two
            # counters in the untracked research tree.
            #
            # The weight vector is READ from the file's banner, exactly as
            # `projcheck` reads it -- not derived from the genus. A derived vector
            # would be a table by another name and nothing would test it.
            weights = D.weights_declared(fam.dbl_path if op == "DBL"
                                         else fam.add_path)
            if not weights:
                return None                 # nothing declared: not blamed, not counted
            gu, gv, why = PJ.normalise(F, fam.genus, list(vals), weights)
            if gu is None:
                # Off the frequent path (Znew = 0) is not a disagreement -- the file
                # does not claim that branch. Neither counted nor blamed.
                return None if why == "Z = 0" else False
            want = R.add(cur, D1, D2) if op == "ADD" else R.double(cur, D1)
            return gu == want[0] and gv == want[1]
        gu, gv, note = D.decode_divisor(F, fam.genus, vals, coords)
        if gu is None:
            return False
        if note is not None:
            # The note was BOUND AND NEVER READ here. An arity anomaly means the
            # return was truncated to make it decode, so the sample says nothing
            # about the values that were dropped -- histogramming it reports a
            # count as validated when it was not. Dropped instead of laundered.
            # No shipped file produces a note (E2 was fixed in PR5 and
            # `arity_anomalies` is empty at HEAD), so this must change no figure;
            # that invariance is the test. Surfacing it in the report is C3's job.
            return False
        want = R.add(cur, D1, D2) if op == "ADD" else R.double(cur, D1)
        return gu == want[0] and gv == want[1]
    except Exception:
        return None


def count_family(fam, families, field, target=400, seed=7, verbose=False):
    """{label: {"modal":…, "share":…, "n":…, "dist":…}} keyed by operation shape.

    Keyed by degree pattern -- "2DBL", "12ADD", "2ADD" -- because that is how the
    published tables are indexed, and because a lump "ADD" figure would average
    over operations the thesis prices separately.

    Only the family's declared domain is sampled, and divisor degrees are asked
    for rather than taken as they come: `random_divisor` returns the identity
    often enough that an unfiltered sample is mostly `D + 0`, which costs nothing
    and would swamp the histogram.
    """
    if fam.is_split:
        return _count_split(fam, families, field, target, seed, verbose)

    # A DBL-ONLY FAMILY IS A LEGITIMATE SHAPE, and this function could not express
    # one: it derived the domain with op="ADD" and then loaded `fam.add_path`
    # unconditionally, so the first such family -- the projective doubling of PR46
    # -- came back as `skipped: no ADD file` and the counter of record measured
    # nothing for it. PR7+8 recorded the ADD-only case as leaving a family
    # mixed-domain; this is its mirror, and `driver.family_domain` needed the same
    # fix at :347.
    #
    # The domain is derived from whichever operation the family HAS. Ordering
    # matters: with no ADD there is nothing to contrast, so asking for "ADD" is
    # asking about a file that does not exist.
    have_add = bool(fam.add_path)
    cons, members, why = D.family_domain(fam, families, "ADD" if have_add else "DBL")
    if cons is None:
        return None, why
    unpinned = D.require_leading_pin(fam, members)
    if unpinned:
        return None, unpinned

    subs, add_params = {}, None
    if have_add:
        try:
            subs = M.discover(fam.add_path)
            add_params, _ = D._dispatcher_body(fam.add_path, "ADD")
        except Exception as e:
            return None, "cannot load ADD: %s: %s" % (type(e).__name__, e)
    dbl_params = None
    if fam.dbl_path:
        try:
            dsubs = M.discover(fam.dbl_path)
            dbl_params, _ = D._dispatcher_body(fam.dbl_path, "DBL")
            merged = dict(dsubs)
            merged.update(subs)
            subs = merged
        except Exception:
            pass
    if not subs:
        return None, "neither an ADD nor a DBL file could be loaded"

    g = fam.genus
    F = GF(field)
    rng = random.Random("%s|%d|%d" % (fam.name, field, seed))
    hist = collections.defaultdict(collections.Counter)

    # The shapes the published tables price: each degree on its own for doubling,
    # and each unordered pair for addition.
    dbl_shapes = [(d,) for d in range(1, g + 1)]
    add_shapes = [(i, j) for i in range(1, g + 1) for j in range(i, g + 1)]
    per_shape = max(8, target // max(1, len(dbl_shapes) + len(add_shapes)))

    with conventions(fam.add_path, fam.dbl_path):
        curves_tried = 0
        while curves_tried < 60 and min(
                [sum(hist[_label("DBL", s)].values()) for s in dbl_shapes] +
                [sum(hist[_label("ADD", s)].values()) for s in add_shapes]
        ) < per_shape:
            cur = D.curve_in_domain(F, fam, cons, rng, members=members)
            curves_tried += 1
            if cur is None:
                break

            if dbl_params is not None and "DBL" in subs:
                for (d,) in dbl_shapes:
                    for _ in range(per_shape):
                        D1 = C.random_divisor(cur, rng, degs=(d,))
                        if not D1:
                            continue
                        try:
                            args = D.build_args(dbl_params, cur, D1, None)
                        except Exception:
                            continue
                        got = measure_call(subs["DBL"], args, subs, F)
                        if got and _agrees(fam, cur, None, D1, None,
                                           "DBL", got[1]):
                            hist[_label("DBL", (d,))][got[0]] += 1

            if "ADD" in subs:
                for (i, j) in add_shapes:
                    for _ in range(per_shape):
                        D1 = C.random_divisor(cur, rng, degs=(i,))
                        D2 = C.random_divisor(cur, rng, degs=(j,))
                        if not D1 or not D2 or D1 == D2:
                            continue
                        try:
                            args = D.build_args(add_params, cur, D1, D2)
                        except Exception:
                            continue
                        got = measure_call(subs["ADD"], args, subs, F)
                        if got and _agrees(fam, cur, None, D1, D2,
                                           "ADD", got[1]):
                            hist[_label("ADD", (i, j))][got[0]] += 1

    if not any(hist.values()):
        # `not any(hist.values())`, NOT `not hist`. PR46 added this guard with the
        # latter and it never fired: `hist` is a defaultdict(Counter) and the share
        # computation below READS hist[label] for every shape, which CREATES an
        # empty Counter for each. So `hist` is never empty -- it is full of empty
        # Counters -- and an all-samples-dropped family sailed through to `out = {}`
        # with why=None, which is exactly the silent empty the guard was written to
        # stop. Found by the first DBL-only projective family; the fix was ineffective
        # for the whole of PR46.
        #
        # The guard `_count_split` has at :441 and this path did not. Without it an
        # all-samples-dropped family returns `{}`, which is NOT None, so `main`
        # writes `{'field': ..., 'ops': {}}`, keeps the family OUT of `skipped`,
        # prints its header with no rows under it, and exits 0 -- reported as
        # measured with nothing. Every route here is silent: a `build_args`
        # KeyError swallowed by a bare `except: continue` above, or `_agrees`
        # returning False on every sample. A projective family hits both.
        # The reason names CAUSES THAT HAVE ACTUALLY BEEN OBSERVED. An earlier
        # version of this message blamed the field size -- "the off-path rate is
        # O(1/q), try a larger --field" -- which was plausible and wrong on both
        # counts. Measured: the two real causes were `build_args` raising on an
        # unmapped `Z` and a dispatcher calling `Resultant`, which maginterp does
        # not implement; both are swallowed by the bare `except: continue` above.
        # And the field is irrelevant -- once fixed, 454/471/472 samples agreed at
        # GF(31), GF(101) and GF(211) alike.
        return None, ("no sample agreed with the reference over GF(%d); nothing was "
                      "measured. Every sample is dropped silently by the bare "
                      "excepts above, so check in this order: does the dispatcher "
                      "use a primitive maginterp lacks (try calling it directly), "
                      "can build_args bind every parameter name, and does the "
                      "family's domain admit any curve at all." % field)

    out = {}
    for label, h in sorted(hist.items()):
        if not h:
            continue
        modal, n = h.most_common(1)[0]
        total = sum(h.values())
        out[label] = {
            "modal": list(modal),
            "share": round(n / float(total), 4),
            "n": total,
            "dist": [[list(k), v] for k, v in h.most_common(5)],
        }
    return out, None


def _count_split(fam, families, field, target=400, seed=7, verbose=False):
    """The split-model half of `count_family`; same contract, same return.

    Three things differ from the ramified path, and each is why the counter used
    to refuse rather than guess:

    DOMAIN.  `family_domain`'s arb-contrast sees nothing here, because the split
    dispatchers read neither f nor h -- they take `ccs`, the constants
    `Precompute` derives. `driver.split_spec` already derives the domain from
    Precompute's own source instead, and `split_curve_in_domain` already
    validates that the places at infinity are rational. Both are used verbatim;
    nothing about the domain is re-derived here.

    ARGUMENTS.  A split divisor carries a balancing weight alongside (u, v), and
    the dispatcher takes `ccs` rather than curve coefficients, so `build_args`
    cannot map the signature. `build_args_split` can, and `Precompute` is run
    once per curve OUTSIDE the measured call -- it is per-curve setup, not part
    of an operation's cost.

    SHAPE.  The published split tables are not indexed by degree alone: genus 3
    prices "Degree 1", "Degree 1 with Down Adjust" and "Degree 1 with two Up
    Adjusts" separately, at 7M, 14M and 42M. Measured, the input balancing weight
    is exactly what selects between them -- the six (degree, weight) pairs a
    genus-3 divisor admits reproduce the six published doubling rows one for one
    -- so the weight is part of the shape here, not a nuisance parameter. Keying
    on degree alone pooled rows the thesis prices apart and reported whichever
    the sampler happened to favour, which is how a degree-1 doubling would have
    been reported as 42M.

    Weights are therefore driven rather than drawn: every legal weight for a
    shape is asked for, so no published row can go unsampled because the sampler
    never happened to pick its weight.
    """
    spec = D.split_spec(fam, families)
    try:
        subs = dict(M.discover(fam.utl_path)) if fam.utl_path else {}
        add_subs = M.discover(fam.add_path)
        add_params, _ = D._dispatcher_body(fam.add_path, "ADD")
        subs.update(add_subs)
    except Exception as e:
        return None, "cannot load ADD: %s: %s" % (type(e).__name__, e)
    if "Precompute" not in subs:
        return None, "no Precompute available, so ccs cannot be built"

    dbl_params = None
    if fam.dbl_path:
        try:
            dsubs = M.discover(fam.dbl_path)
            dbl_params, _ = D._dispatcher_body(fam.dbl_path, "DBL")
            merged = dict(dsubs)
            merged.update(subs)
            subs = merged
        except Exception:
            pass

    g = fam.genus
    F = GF(field)
    rng = random.Random("%s|%d|%d" % (fam.name, field, seed))
    hist = collections.defaultdict(collections.Counter)

    # A weight is legal in [0, g - deg u], which is what
    # reference.split_check_divisor enforces. Degree 0 is the identity and is a
    # real addition shape here -- the tables carry "Degree 0 and 1" rows -- but
    # not a doubling one, and 0 + 0 is priced nowhere, so it is excluded.
    dbl_shapes = [(d, n) for d in range(1, g + 1) for n in range(0, g - d + 1)]
    add_shapes = [((i, ni), (j, nj))
                  for i in range(0, g + 1) for j in range(i, g + 1)
                  if (i, j) != (0, 0)
                  for ni in range(0, g - i + 1) for nj in range(0, g - j + 1)]
    per_shape = max(4, target // max(1, len(dbl_shapes) + len(add_shapes)))

    def _draw(cur, V, d, n):
        D0 = C.random_divisor(cur, rng, degs=(d,))
        if not D0:
            return None
        try:
            return C.to_split_divisor(cur, D0, V, rng, n=n)
        except Exception:
            return None

    with conventions(fam.add_path, fam.dbl_path):
        curves_used = curves_tried = 0
        while curves_tried < 60 and curves_used < max(3, 60 // max(1, per_shape)):
            curves_tried += 1
            cur = D.split_curve_in_domain(F, fam, spec, rng)
            if cur is None:
                continue
            try:
                V = C.split_basis(cur, fam.basis)
            except ArithmeticError:
                continue
            try:
                # Precompute returns ONE value, the nested constants sequence, so
                # the interpreter's return tuple is unwrapped. Passing the tuple
                # through adds a nesting level and every ccs[2][...] raises.
                raw = subs["Precompute"](cur.f, cur.h, F.q, funcs=subs, F=F)
                ccs = raw[0] if len(raw) == 1 else list(raw)
            except Exception:
                continue
            curves_used += 1

            if dbl_params is not None and "DBL" in subs:
                for (d, n) in dbl_shapes:
                    for _ in range(per_shape):
                        D1 = _draw(cur, V, d, n)
                        if not D1:
                            continue
                        try:
                            args = D.build_args_split(dbl_params, cur, ccs, D1)
                        except Exception:
                            continue
                        got = measure_call(subs["DBL"], args, subs, F)
                        if got and _agrees(fam, cur, V, D1, None, "DBL", got[1]):
                            hist[_split_label("DBL", ((d, n),))][got[0]] += 1

            if "ADD" in subs:
                for ((i, ni), (j, nj)) in add_shapes:
                    for _ in range(per_shape):
                        D1 = _draw(cur, V, i, ni)
                        D2 = _draw(cur, V, j, nj)
                        if not D1 or not D2 or D1 == D2:
                            continue
                        try:
                            args = D.build_args_split(add_params, cur, ccs,
                                                      D1, D2)
                        except Exception:
                            continue
                        got = measure_call(subs["ADD"], args, subs, F)
                        if got and _agrees(fam, cur, V, D1, D2, "ADD", got[1]):
                            hist[_split_label("ADD",
                                              ((i, ni), (j, nj)))][got[0]] += 1

    if not hist:
        return None, ("no curve in the family's domain with rational places at "
                      "infinity over GF(%d)" % field)
    out = {}
    for label, h in sorted(hist.items()):
        modal, n = h.most_common(1)[0]
        total = sum(h.values())
        out[label] = {
            "modal": list(modal),
            "share": round(n / float(total), 4),
            "n": total,
            "dist": [[list(k), v] for k, v in h.most_common(5)],
        }
    return out, None


def _label(op, degs):
    """"2DBL", "12ADD", "2ADD" -- the thesis's own row naming."""
    return "".join(str(d) for d in degs) + op


def _split_label(op, shape):
    """"3DBL n=0", "13ADD n=2,0" -- degree shape plus the balancing weights.

    The weight suffix is not decoration: it is what distinguishes the published
    rows from one another within a degree. See `_count_split`.
    """
    degs = "".join(str(d) for d, _ in shape)
    ns = ",".join(str(n) for _, n in shape)
    return "%s%s n=%s" % (degs, op, ns)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--family", action="append", default=None,
                    help="restrict to a family, e.g. ramified/g2/ch2 (repeatable)")
    ap.add_argument("--field", type=int, default=None,
                    help="field size; default is per-family and characteristic-safe")
    ap.add_argument("--target", type=int, default=400,
                    help="calls per family (default 400)")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    families, _excluded = D.discover_families()
    if a.family:
        want = set(a.family)
        families_sel = [f for f in families if f.name in want]
        if not families_sel:
            print("no family matched %s; known:" % sorted(want))
            for f in families:
                print("   ", f.name)
            return 2
    else:
        # EVERY family. All fifteen are measurable now, so this no longer decides
        # what gets counted -- but it still decides what a skip would be allowed to
        # do silently, which is why it does not filter. Selecting by model here
        # once put the nine split families outside the skip machinery entirely:
        # the run reported six results and an empty `skipped` list, so a reader --
        # or a --json consumer -- saw a complete-looking answer covering 6 of 15
        # families with nothing to say the other nine were never attempted. A
        # family that stops being measurable for any reason must show up in the
        # skip list and in the tally, not vanish from the denominator.
        families_sel = list(families)

    results, skipped = {}, []
    for fam in families_sel:
        field = a.field or (32 if fam.kind == "ch2" else 31)
        got, why = count_family(fam, families, field, a.target, a.seed)
        if got is None:
            skipped.append((fam.name, why))
            continue
        results[fam.name] = {"field": field, "ops": got}

    if a.json:
        json.dump({"results": results, "skipped": skipped}, sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 0

    print("counting by execution; C from each file's //Constant:, x/2 as one addition\n")
    for name in sorted(results):
        blob = results[name]
        print("  %-24s GF(%d)" % (name, blob["field"]))
        free = 0
        for op in sorted(blob["ops"]):
            r = blob["ops"][op]
            m, s, add, c, i = r["modal"]
            if not any(r["modal"]):
                # A shape the dispatcher answers with no arithmetic at all -- an
                # identity or already-balanced input it can return directly. Real,
                # verified against reference.py like every other sample, and priced
                # by no published row, so it is counted rather than listed. --json
                # carries it either way; this only shortens the human report.
                free += 1
                continue
            # Width stays %-4s so the ramified rows print exactly as they always
            # have; the longer split labels simply run past it, and they are all
            # the same length within a group so those columns still line up.
            print("     %-4s %3dM %2dS %3dA %2dC %2dI    share %.2f of %d calls"
                  % (op, m, s, add, c, i, r["share"], r["n"]))
        if free:
            print("     (%d further shapes cost nothing: answered without "
                  "arithmetic)" % free)
    for name, why in sorted(skipped):
        print("  %-24s skipped: %s" % (name, (why or "")[:60]))
    if skipped:
        print("\n  %d of %d families measured, %d skipped."
              % (len(results), len(results) + len(skipped), len(skipped)))
    if not results:
        print("  nothing measured")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
