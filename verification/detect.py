"""
How much of the formulas can the frozen whitebox corpus actually see?

    python3 verification/detect.py                          # every tester
    python3 verification/detect.py --family ramified/g3/ch2
    python3 verification/detect.py --tester <path> --json

WHY THIS EXISTS

`whitebox.py` answers "is every branch reached?" and the answer is yes -- 1,870 of
1,870 labels. That is COMPLETENESS, and it is not the same as ADEQUACY. A branch
reached by one case whose arithmetic happens to zero a term cannot distinguish a
change to that term, so the branch is covered and the change is still invisible.

That is not hypothetical. `ERRATA.md` E20 records a correct `-2M -2A` saving at
`ADD29`/`ADD33` that was applied, measured green under real Magma across 2,119
comparisons, and then reverted -- because deliberately breaking the same line ALSO
measured green. The corpus reached the branch and could not see the term.

WHAT IT MEASURES

Every assignment the corpus executes is perturbed by one, and the operation's
returned divisor compared against the unperturbed run. If the divisor does not
move, that assignment is INVISIBLE: nothing in the corpus would catch a change to
the expression producing it. An assignment can be invisible for three reasons and
this does not distinguish them, because for this purpose they are the same thing --
it is dead, it is overwritten before use, or something multiplies it by zero.

    detectability = 1 - invisible/total, over the Deg* formula bodies

ONLY THE Deg* BODIES ARE SCORED, and that is not a convenience. Counting every
layer gives 48.2% invisible where the formula bodies are at 18.7%, because the
split dispatchers unpack `ccs` into some sixty named constants of which any branch
reads a handful. Perturbing a constant a branch never reads is dead unpacking, not
a blind spot. The other layers are reported separately rather than dropped.

WHAT A GOOD SCORE IS NOT

It is not 100%. Some invisibility is structural: `f7` is assigned and never read
and is deliberately not deletable (`driver.read_support` parses the dispatcher's
`Coeff` reads to infer the tested domain), and a branch guarded on `d = 0` must
have `d = 0` for the case to reach it at all. Measured, the names that survive
every field are the adjugate entries `m1`-`m9` and the determinant, dead on the
degenerate paths that do not consume them. So this is a RELATIVE instrument: use it
to show one corpus strictly better than another, not to chase a target.
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys

import maginterp as M
import whitebox as W
from poly import Poly

HERE = os.path.dirname(os.path.abspath(__file__))

# Interpreter state for one measured replay.
_COUNT = [0]            # assignments executed so far
_TARGET = [-1]          # which one to perturb; -1 perturbs nothing
_RECORD = [False]       # collect (function, name) for the baseline pass
_NAMES = []
_LABELS = []            # branch labels the case reached, identifying its branch
_RETS = []
_STACK = ["?"]

_real_run = M.run
_real_call = M.MagmaFn.__call__
_real_replay = W._replay_one


def _call(self, *args, path=None, funcs=None, F=None):
    """Track which function an assignment happens in, for the layer split."""
    _STACK.append(self.name)
    try:
        return _real_call(self, *args, path=path, funcs=funcs, F=F)
    finally:
        _STACK.pop()


def _plus_one(v):
    """v + 1 in whatever v is, or None if it cannot be perturbed."""
    try:
        if isinstance(v, bool):
            return None
        if isinstance(v, int):
            return v + 1
        if isinstance(v, Poly):
            return v + Poly(v.F, [v.F.one])
        if hasattr(v, "F"):
            return v + v.F.one
    except Exception:                                        # noqa: BLE001
        return None
    return None


def _run(blk, env, F, path, funcs=None):
    """`maginterp.run`, statement for statement, with one assignment perturbed.

    A copy rather than a wrapper because the perturbation has to happen between
    evaluating a statement's right-hand side and binding its name, and `run` loops
    internally. Recursion reaches this rather than the original because `run` in the
    real body resolves through module globals, which is also what makes nested Deg*
    calls measurable rather than only the dispatcher.

    `selftest` asserts this produces the identical path and return as the real
    interpreter when nothing is perturbed, so a divergence cannot go unnoticed.
    """
    for st in blk:
        if st[0] == "set":
            val = M.ev(st[2], env, F, funcs)
            if _COUNT[0] == _TARGET[0]:
                bumped = _plus_one(val)
                if bumped is not None:
                    val = bumped
            env[st[1]] = val
            path.append(st[1])
            if _RECORD[0]:
                _NAMES.append((_STACK[-1], st[1]))
            _COUNT[0] += 1
        elif st[0] == "assert":
            if not M._truthy(M.ev(st[1], env, F, funcs)):
                raise AssertionError("assertion failed: %s" % st[2])
        elif st[0] == "print":
            path.append("PRINT:" + st[1])
            if _RECORD[0]:
                _LABELS.append(st[1])
        elif st[0] == "ifchain":
            for cond, sub in st[1]:
                if cond is None or M._truthy(M.ev(cond, env, F, funcs)):
                    _run(sub, env, F, path, funcs)
                    break
        else:
            vals = []
            for e in st[1]:
                v = M.ev(e, env, F, funcs)
                if isinstance(v, tuple):
                    vals.extend(v)
                else:
                    vals.append(v)
            _RETS.append(tuple(vals))
            raise M.Ret(vals)


def _label_for(path):
    """A tester's shortest unambiguous name: basename, plus the basis when it has one."""
    parts = path.replace(os.sep, "/").split("/")
    base = parts[-1]
    for p in parts:
        if p in ("posReduced", "negReduced"):
            return "%s [%s]" % (base, p[:3])
    return base


def layer_of(fn):
    """Which layer an assignment belongs to. Only Deg* bodies are scored."""
    if fn.startswith("Deg"):
        return "formulas"
    if fn in ("ADD", "DBL"):
        return "dispatcher"
    if fn == "Precompute":
        return "precompute"
    return "utilities"


def measure_tester(tester, per_case=False):
    """Detectability of one tester. Replays it once per executed assignment."""
    captured = []

    def capture(case, model, genus, basis, subs, params, add_path, dbl_path,
                res, utl_path=None):
        captured.append(((case, model, genus, basis, subs, params, add_path,
                          dbl_path, W.Result()), {"utl_path": utl_path}))

    W._replay_one = capture
    try:
        W.replay_tester(tester, W.Result(), False)
    finally:
        W._replay_one = _real_replay

    def one_pass(args, target, record=False):
        _COUNT[0], _TARGET[0], _RECORD[0] = 0, target, record
        del _RETS[:]
        if record:
            del _NAMES[:]
            del _LABELS[:]
        try:
            _real_replay(*args[0], **args[1])
        except Exception:                                    # noqa: BLE001
            return "RAISED"
        return _RETS[-1] if _RETS else None

    layers = collections.defaultdict(lambda: [0, 0])
    blind_names = collections.Counter()
    cases = []
    unusable = 0
    # Scored by BRANCH, not by case. A branch may be covered by more than one case
    # -- that is the point of the two-per-branch corpus -- and an assignment is
    # invisible only if EVERY case reaching it misses it. Summing per case instead
    # would mean adding a redundant case could LOWER the score, which is wrong for
    # a metric whose whole purpose is that more cases cannot hurt.
    #
    # AN ASSIGNMENT IS IDENTIFIED BY (function, variable, nth occurrence), NOT by
    # its position in the trace. Position looks simpler and is wrong as soon as two
    # cases reach the same branch by different routes: `Precompute` has eight exits
    # and takes a different number of assignments on each, so a case whose curve
    # takes a different leaf shifts every later index and nothing lines up. The
    # symptom was measurable -- the genus-2 split families reported 2,462
    # assignments where one case per branch reported 1,559, when per-branch scoring
    # should hold that figure FIXED. Every extra group was one branch counted twice
    # because its cases disagreed about a label or a prefix length, so their blind
    # sets were never intersected and the whole benefit of the second case went
    # unmeasured. Those families looked like they had gained a point where the
    # ramified ones gained ten.
    #
    # The branch key likewise ignores UTL labels: they name Precompute's exits,
    # which are a property of the curve rather than of the operation under test, so
    # two cases exercising the same formula branch belong together even when their
    # curves route through Precompute differently.
    by_branch = {}      # key -> {"seen": {triple: layer}, "blind": {triple}}

    M.run, M.MagmaFn.__call__ = _run, _call
    try:
        for args in captured:
            case = args[0][0]
            base = one_pass(args, -1, record=True)
            names = list(_NAMES)
            key = tuple(x for x in _LABELS if not x.startswith("UTL"))
            if base is None or base == "RAISED":
                unusable += 1
                continue

            # Stable identity per assignment, independent of anything before it.
            seen_count = collections.Counter()
            triples = []
            for fn, var in names:
                seen_count[(fn, var)] += 1
                triples.append((fn, var, seen_count[(fn, var)]))

            blind_here = set()
            for k, t in enumerate(triples):
                if one_pass(args, k) == base:
                    blind_here.add(t)

            slot = by_branch.setdefault(key, {"seen": {}, "blind": {}})
            for t in triples:
                slot["seen"][t] = layer_of(t[0])
            for t in triples:
                # Invisible only if blind in EVERY case that reaches it, so a
                # triple one case cannot see and another can becomes visible.
                if t in blind_here:
                    slot["blind"].setdefault(t, True)
                else:
                    slot["blind"][t] = False

            if per_case:
                fform = [t for t in triples if layer_of(t[0]) == "formulas"]
                cases.append({"index": case.index, "op": case.op, "q": case.q,
                              "assigns": len(fform),
                              "invisible": len([t for t in fform
                                                if t in blind_here])})
    finally:
        M.run, M.MagmaFn.__call__ = _real_run, _real_call

    for slot in by_branch.values():
        for t, lay in slot["seen"].items():
            layers[lay][0] += 1
            if slot["blind"].get(t):
                layers[lay][1] += 1
                if lay == "formulas":
                    blind_names[t[1]] += 1

    f_tot, f_blind = layers["formulas"]
    return {
        # Disambiguated, not basenamed. `arb_splitG2_whiteBox_tester.mag` exists
        # under BOTH posReduced/ and negReduced/, which are different algorithms
        # with different costs -- reporting by basename gives two identically
        # labelled rows and no way to tell which basis each belongs to. PR12 fixed
        # this at 19 call sites elsewhere for the same reason.
        "tester": _label_for(tester),
        "cases": len(captured),
        "unusable": unusable,
        "assigns": f_tot,
        "invisible": f_blind,
        "detectability": round(1.0 - f_blind / float(max(1, f_tot)), 4),
        "layers": {k: {"assigns": v[0], "invisible": v[1]}
                   for k, v in sorted(layers.items())},
        "worst_names": blind_names.most_common(12),
        "per_case": cases,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--tester", action="append", default=None,
                    help="measure this tester file (repeatable)")
    ap.add_argument("--family", action="append", default=None,
                    help="substring of a tester name, e.g. ramified/g3 (repeatable)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--per-case", action="store_true",
                    help="include a row per case")
    a = ap.parse_args(argv)

    if a.tester:
        testers = a.tester
    else:
        testers = W.find_testers()
        if a.family:
            testers = [t for t in testers
                       if any(f in t.replace(os.sep, "/") for f in a.family)]
        if not testers:
            print("no tester matched %s" % a.family)
            return 2

    out = [measure_tester(t, per_case=a.per_case) for t in testers]
    if a.json:
        json.dump(out, sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 0

    print("detectability = 1 - invisible/total over the Deg* formula bodies.")
    print("Higher is better; 100% is not reachable and is not the target -- see "
          "the module docstring.\n")
    print("  %-52s %5s %7s %9s %6s" % ("tester", "cases", "assigns",
                                       "invisible", "detect"))
    tot = blind = 0
    for r in out:
        tot += r["assigns"]
        blind += r["invisible"]
        print("  %-52s %5d %7d %9d %5.1f%%"
              % (r["tester"], r["cases"], r["assigns"], r["invisible"],
                 100.0 * r["detectability"]))
        if r["unusable"]:
            print("      %d case(s) had no usable baseline and were not scored"
                  % r["unusable"])
    if len(out) > 1:
        print("\n  %-52s %5s %7d %9d %5.1f%%"
              % ("TOTAL", "", tot, blind,
                 100.0 * (1.0 - blind / float(max(1, tot)))))
    if len(out) == 1:
        print("\n  by layer (only `formulas` is scored):")
        for k, v in out[0]["layers"].items():
            print("     %-12s %7d assigns %7d invisible  (%.1f%%)"
                  % (k, v["assigns"], v["invisible"],
                     100.0 * v["invisible"] / max(1, v["assigns"])))
        print("\n  most often invisible: %s"
              % ", ".join("%s x%d" % (n, c) for n, c in out[0]["worst_names"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
