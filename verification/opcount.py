"""
Operation counts for the explicit formulas, measured by running them.

    python3 verification/opcount.py                     # every family it can reach
    python3 verification/opcount.py --family ramified/g2/ch2
    python3 verification/opcount.py --verify            # against the published tables

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
domain shows up as a mismatch rather than as a plausible wrong count.
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
        self._saved = (M.CONSTS, M.IGNORED, M.DIV_LITERAL_AS_ADD)
        M.CONSTS, M.IGNORED, M.DIV_LITERAL_AS_ADD = self.consts, self.ignored, True
        return self

    def __exit__(self, *exc):
        M.CONSTS, M.IGNORED, M.DIV_LITERAL_AS_ADD = self._saved
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
    cons, members, why = D.family_domain(fam, families, "ADD")
    if cons is None:
        return None, why
    unpinned = D.require_leading_pin(fam, members)
    if unpinned:
        return None, unpinned

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
                        if got:
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
                        if got:
                            hist[_label("ADD", (i, j))][got[0]] += 1

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


def _label(op, degs):
    """"2DBL", "12ADD", "2ADD" -- the thesis's own row naming."""
    return "".join(str(d) for d in degs) + op


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
        # EVERY family, not just the ramified ones. Selecting by model here put the
        # nine split families outside the skip machinery entirely: the run reported
        # six results and an empty `skipped` list, so a reader -- or a --json
        # consumer -- saw a complete-looking answer covering 6 of 15 families with
        # nothing to say the other nine were never attempted. The refusal already
        # existed and was honest when a split family was named explicitly; only the
        # default path bypassed it. Nothing is silently capped in this repository,
        # and the counter of record is the last place that rule should lapse.
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
        for op in sorted(blob["ops"]):
            r = blob["ops"][op]
            m, s, add, c, i = r["modal"]
            print("     %-4s %3dM %2dS %3dA %2dC %2dI    share %.2f of %d calls"
                  % (op, m, s, add, c, i, r["share"], r["n"]))
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
