"""selftest.py -- checks the verification framework itself.

`driver.py` compares the .mag formulas against `reference.py`. Nothing it reports
tells you whether that comparison is trustworthy: a reference that is wrong in the
same way as a formula agrees with it, and a curve generator that only ever produces
degenerate curves agrees with everything. This is the file that checks the checker.

Usage:

    python3 selftest.py                 # every section
    python3 selftest.py --section parse group_axioms
    python3 selftest.py --list          # what the sections are
    python3 selftest.py --quick         # smaller samples, for a pre-commit run

Exit status is 0 only if every section that ran passed. A section that cannot run
because an external artefact is missing is reported as SKIP and does not fail the
run -- but it is never silently omitted, because a selftest that quietly shrinks is
worse than one that fails.

Sections, and what each would catch:

  fields          Arithmetic in ff.py and poly.py. Everything rests on these.
  parse           Every function in every formula file still parses. A parser
                  regression shows up here as a number rather than as a driver
                  that quietly tests less.
  acceptance      The empirical curve filter against the textbook singularity
                  criterion, both models. Catches a filter that accepts curves the
                  group law fails on -- which it was doing for the split model.
  group_axioms    Identity, closure, commutativity, associativity, and inverses
                  where available, over every model, genus, class and basis.
  reference       Three-way agreement between reference.py, the repository's own
                  Nucomp_g3_RAM and the thesis algorithm as printed. The strongest
                  soundness check on reference.py that does not need Magma.
  errata          The recorded defects E1 and E2, as required test vectors. If the
                  framework cannot surface these, its D1 = D2 coverage is not real
                  and PR5 cannot be shown to fix anything.
  repros          The audit's stored failures, replayed through the post-rename
                  files. A repro that stops reproducing means either the rename map
                  is wrong or the bug moved; both need investigating, and neither
                  should pass quietly.
  swap            That a deliberately swapped operand pair is detected. PR10
                  reorders parameters in the genus-3 models and a mistake there is
                  wrong only on mixed-degree inputs, so this capability has to be
                  demonstrated before that work starts, not assumed.

The `reference` and `repros` sections need the audit artefacts, which live outside
this repository. Point AUDIT_HARNESS at them, or let those two sections skip.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import random
import re
import shutil
import sys
import tempfile

import curves as C
import driver as D
import maginterp as M
import reference as R
from ff import GF
from poly import Poly

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# The audit's harness and stored repros. Outside this repository on purpose: they are
# evidence from a prior review, not part of the deliverable.
#
# Resolved relative to the repository, not to anyone's home directory. A committed
# absolute path would be wrong on every machine but one, and would have made the two
# sections that use it look permanently skipped to everybody else.
AUDIT_HARNESS = os.environ.get(
    "AUDIT_HARNESS",
    os.path.join(os.path.dirname(ROOT), "divisor-audits", "g3ram", "harness"))

CH2_FIELDS = (2, 4, 8, 16)
ODD_FIELDS = (3, 5, 7, 9, 11, 13)


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

class Report(object):
    """Accumulates per-section verdicts and prints one table at the end."""

    def __init__(self):
        self.rows = []          # (section, verdict, detail)
        self.lines = []         # free-text detail printed under the table

    def ok(self, section, detail=""):
        self.rows.append((section, "PASS", detail))

    def fail(self, section, detail=""):
        self.rows.append((section, "FAIL", detail))

    def skip(self, section, detail=""):
        self.rows.append((section, "SKIP", detail))

    def note(self, text):
        self.lines.append(text)

    def failed(self):
        return any(v == "FAIL" for _s, v, _d in self.rows)

    def render(self):
        w = sys.stdout.write
        if self.lines:
            w("\n")
            for line in self.lines:
                w("  %s\n" % line)
        w("\n" + "=" * 72 + "\n")
        for section, verdict, detail in self.rows:
            w("  %-5s %-14s %s\n" % (verdict, section, detail))
        w("=" * 72 + "\n")
        n_fail = sum(1 for _s, v, _d in self.rows if v == "FAIL")
        n_skip = sum(1 for _s, v, _d in self.rows if v == "SKIP")
        n_pass = sum(1 for _s, v, _d in self.rows if v == "PASS")
        w("  %d passed, %d failed, %d skipped\n\n" % (n_pass, n_fail, n_skip))
        return 1 if n_fail else 0


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def section_fields(rep, quick):
    """Field and polynomial arithmetic, including the char-2 cases."""
    bad = []
    for q in (2, 3, 4, 5, 8, 9, 11, 16, 25, 27, 32):
        F = GF(q)
        els = list(F.elements())
        if len(els) != q:
            bad.append("GF(%d) enumerated %d elements" % (q, len(els)))
            continue
        for a in els:
            if not a.is_zero() and not (a * a.inverse()).is_one():
                bad.append("GF(%d): a * a^-1 != 1 for %s" % (q, a))
            if not (a - a).is_zero():
                bad.append("GF(%d): a - a != 0 for %s" % (q, a))
        # the characteristic really is the characteristic
        acc = F.zero
        for _ in range(F.char):
            acc = acc + F.one
        if not acc.is_zero():
            bad.append("GF(%d): char*1 != 0" % q)
        # polynomial division agrees with multiplication
        rng = random.Random(q)
        for _ in range(20 if quick else 80):
            a = Poly(F, [F.random(rng) for _ in range(5)])
            b = Poly(F, [F.random(rng) for _ in range(3)])
            if b.is_zero():
                continue
            qq, r = a.divmod(b)
            if qq * b + r != a:
                bad.append("GF(%d): divmod identity failed" % q)
                break
            if r.deg >= b.deg:
                bad.append("GF(%d): remainder degree not reduced" % q)
                break
    if bad:
        rep.fail("fields", "%d problems, first: %s" % (len(bad), bad[0]))
    else:
        rep.ok("fields", "11 fields, arithmetic and divmod identities hold")


def section_parse(rep, quick):
    """Every function in every formula file parses."""
    ok, bad = 0, []
    for dirpath, _dirs, files in os.walk(ROOT):
        if os.sep + "timings" + os.sep in dirpath + os.sep:
            continue
        if not re.search(r"g[23]Formulas$", dirpath):
            continue
        for fn in sorted(files):
            if not fn.endswith(".mag"):
                continue
            path = os.path.join(dirpath, fn)
            for name in M.function_names(path):
                try:
                    M.MagmaFn(path, name)
                    ok += 1
                except Exception as exc:                    # noqa: BLE001
                    bad.append("%s::%s: %s" % (fn, name, str(exc)[:60]))
    # The Random*Curve generators are not formulas and are not interpreted:
    # curves.py generates curves instead. Anything else failing is a regression.
    unexpected = [b for b in bad if "Curve" not in b.split("::")[1]]
    detail = "%d functions parse, %d not interpreted (curve generators)" % (ok,
                                                                           len(bad))
    if unexpected:
        rep.fail("parse", "%s; UNEXPECTED: %s" % (detail, unexpected[0]))
    else:
        rep.ok("parse", detail)


def section_acceptance(rep, quick):
    """The empirical curve filter against the textbook singularity criterion.

    Accepting a curve the criterion calls singular is a real failure: a formula
    tested only on singular curves can agree with the reference for the wrong
    reason. Rejecting a smooth curve is merely conservative and is allowed.
    """
    n = 12 if quick else 30
    bad = []
    counts = {"accepted": 0, "rejected": 0}
    for model in ("ramified", "split"):
        for genus in (2, 3):
            for kind, q in (("arb", 9), ("nch2", 11), ("ch2", 4)):
                F = GF(q)
                rng = random.Random("%s%d%s" % (model, genus, kind))
                made = 0
                for _ in range(n * 40):
                    if made >= n:
                        break
                    try:
                        cur = C.random_curve(
                            F, kind, rng, genus=genus, model=model,
                            infinity_y=(F.one if model == "split"
                                        and kind == "nch2" else None),
                            force_hlead=(F.one if model == "split"
                                         and kind == "ch2" else None))
                    except ValueError:
                        break
                    if model == "split":
                        try:
                            V = C.split_basis(cur, "neg")
                        except ArithmeticError:
                            continue
                        ok, _why = C.validate_split_curve(cur, V, rng)
                    else:
                        ok, _why = C.validate_curve(cur, rng, level="fast")
                    made += 1
                    singular = C.singularity_diagnostic(cur)
                    counts["accepted" if ok else "rejected"] += 1
                    if ok and singular:
                        bad.append("%s g%d %s GF(%d): accepted a singular curve"
                                   % (model, genus, kind, q))
    if bad:
        rep.fail("acceptance", "%d accepted-and-singular, first: %s"
                 % (len(bad), bad[0]))
    else:
        rep.ok("acceptance", "%d accepted, %d rejected, none accepted-and-singular"
               % (counts["accepted"], counts["rejected"]))


def section_group_axioms(rep, quick):
    """The group laws, over every model, genus, class and basis."""
    n = 4 if quick else 10
    rows, bad = [], []
    for model in ("ramified", "split"):
        bases = (None,) if model == "ramified" else ("neg", "pos")
        for genus in (2, 3):
            for kind, q in (("arb", 9), ("nch2", 11), ("ch2", 4)):
                for basis in bases:
                    F = GF(q)
                    rng = random.Random("ax%s%d%s%s" % (model, genus, kind, basis))
                    ok_n = rej = 0
                    reason = ""
                    for _ in range(n * 40):
                        if ok_n >= n:
                            break
                        try:
                            cur = C.random_curve(
                                F, kind, rng, genus=genus, model=model,
                                infinity_y=(F.one if model == "split"
                                            and kind == "nch2" else None),
                                force_hlead=(F.one if model == "split"
                                             and kind == "ch2" else None))
                        except ValueError:
                            break
                        if model == "split":
                            try:
                                V = C.split_basis(cur, basis)
                            except ArithmeticError:
                                continue
                            good, why = C.validate_split_curve(
                                cur, V, rng, positive=(basis == "pos"))
                        else:
                            good, why = C.validate_curve(cur, rng, level="fast")
                        if good:
                            ok_n += 1
                        else:
                            rej += 1
                            # A rejected curve is the filter working. Only an
                            # axiom failure on an otherwise-accepted shape is a
                            # problem, and those are what `acceptance` covers.
                            reason = why
                    label = "%s g%d %s%s" % (model, genus, kind,
                                             "" if basis is None else "/" + basis)
                    if ok_n == 0:
                        bad.append("%s: no curve satisfied the axioms (%s)"
                                   % (label, reason))
                    rows.append("%-24s %2d curves satisfy the axioms, %3d rejected"
                                % (label, ok_n, rej))
    for r in rows:
        rep.note(r)
    if bad:
        rep.fail("group_axioms", bad[0])
    else:
        rep.ok("group_axioms", "%d model/genus/class/basis combinations" % len(rows))


def section_reference(rep, quick):
    """Three-way agreement: reference.py, the repo's NUCOMP, the printed thesis.

    Expected outcome is NOT unanimity. reference.py and the repository must agree
    everywhere; the thesis as printed must disagree at a measurable rate, because
    its middle-branch guard reads `deg(s) <= 2` where the repository has
    `deg(s) < 2`. That disagreement is a recorded erratum, so seeing it is the pass
    condition and *not* seeing it would mean this check had stopped working.
    """
    if not os.path.isdir(AUDIT_HARNESS):
        rep.skip("reference", "AUDIT_HARNESS not present at %s" % AUDIT_HARNESS)
        return
    sys.path.append(AUDIT_HARNESS)
    try:
        import repo_nucomp                                  # noqa: PLC0415
    except Exception as exc:                                # noqa: BLE001
        rep.skip("reference", "cannot import repo_nucomp: %s" % exc)
        return
    n = 40 if quick else 120
    bad, thesis_diff, total = [], 0, 0
    for kind, q in (("nch2", 11), ("arb", 9), ("arb", 8)):
        F = GF(q)
        rng = random.Random("ref%s%d" % (kind, q))
        seen = 0
        for _ in range(n * 40):
            if seen >= n:
                break
            cur = C.random_curve(F, kind, rng, genus=3, model="ramified")
            ok, _why = C.validate_curve(cur, rng, level="fast")
            if not ok:
                continue
            pair = C.random_divisor_pair(cur, rng, mode="generic")
            if not pair:
                continue
            D1, D2 = pair
            if D1[0] == D2[0] and D1[1] == D2[1]:
                continue        # the repo's NUCOMP has the same D1 != D2 precondition
            try:
                a = R.add(cur, D1, D2)
                b = repo_nucomp.nucomp_g3_ram(cur, D1, D2, s_guard="lt")
                c = repo_nucomp.nucomp_g3_ram(cur, D1, D2, s_guard="le")
            except Exception:                               # noqa: BLE001
                continue
            seen += 1
            total += 1
            if not (a[0] == b[0] and a[1] == b[1]):
                bad.append("%s GF(%d): reference disagrees with the repository's "
                           "own NUCOMP" % (kind, q))
            if not (a[0] == c[0] and a[1] == c[1]):
                thesis_diff += 1
    if bad:
        rep.fail("reference", bad[0])
    elif total == 0:
        rep.fail("reference", "no comparable inputs were generated")
    elif thesis_diff == 0:
        rep.fail("reference",
                 "the printed thesis guard `deg(s) <= 2` agreed everywhere over "
                 "%d inputs; it should differ, so this check has stopped working"
                 % total)
    else:
        rep.ok("reference",
               "%d/%d agree with the repo's NUCOMP; the printed thesis guard "
               "differs on %d, the recorded erratum" % (total, total, thesis_diff))


def section_errata(rep, quick):
    """E1 and E2 as required test vectors."""
    problems, notes = [], []

    # E2: exactly one 6-valued return among 5-valued ones, in each genus-2
    # ramified ADD file. Static, so it is checked by reading the source.
    for fn in ("arb", "ch2", "nch2"):
        path = os.path.join(ROOT, "g2", "ramifiedModel", "g2Formulas",
                            "%s_ramifiedG2_ADD.mag" % fn)
        src = re.sub(r"//[^\n]*", "",
                     re.sub(r"/\*.*?\*/", "", open(path).read(), flags=re.S))
        arities = {}
        for m in re.finditer(r"return\s+([^;]+);", src):
            k = len(M._split_top(m.group(1)))
            arities[k] = arities.get(k, 0) + 1
        if arities.get(6, 0) != 1:
            problems.append("%s: expected exactly one 6-valued return, found %d"
                            % (os.path.basename(path), arities.get(6, 0)))
        else:
            notes.append("E2 %-4s one 6-valued return among %d 5-valued"
                         % (fn, arities.get(5, 0)))

    # E1: the exact vector from the errata. GF(11), y^2 = x^5 + x^3 + 1,
    # u = x^2 + 1, v = 1, D1 = D2. The guard `IsZero(dw20) and IsZero(dw21)` is
    # too narrow, so dw21 = 0 with dw20 nonzero reaches `dw21^-1`.
    #
    # Two assertions since PR5, and both must hold:
    #   1. ADD on this vector now returns the correct double -- the dispatcher
    #      routes D1 = D2 to DBL before any Deg* case runs, which closes every
    #      known firing of E1 (they all have D1 = D2, the unit-mod-u argument).
    #   2. Deg2ADD called DIRECTLY with the same coefficients still divides by
    #      zero. The narrow guard is retained and recorded, not repaired; this
    #      is what keeps E1 an erratum rather than silently declaring it fixed.
    F = GF(11)
    f = Poly.from_coeffs_desc(F, [F.one, F.zero, F.one, F.zero, F.zero, F.one])
    h = Poly.zero(F)
    u = Poly.from_coeffs_desc(F, [F.one, F.zero, F.one])
    v = Poly.const(F, F.one)
    if not ((v * v + v * h - f) % u).is_zero():
        problems.append("E1 vector is not a valid divisor; the vector is wrong")
    fams, _excluded = D.discover_families()
    dispatched, fired = [], []
    want = None
    for name in ("ramified/g2/arb", "ramified/g2/nch2"):
        fam = [x for x in fams if x.name == name][0]
        subs = dict(M.discover(fam.dbl_path))
        subs.update(M.discover(fam.add_path))
        params, _body = D._dispatcher_body(fam.add_path, "ADD")
        cur = C.Curve(F, f, h, fam.kind, 2, "ramified")
        if want is None:
            want = R.add(cur, (u, v), (u, v))

        # 1. through the dispatcher: correct, and equal to the reference double.
        try:
            got = subs["ADD"](*D.build_args(params, cur, (u, v), (u, v)),
                              funcs=subs, F=F)
            gu, gv, note = D.decode_divisor(F, 2, list(got))
            if note:
                problems.append("E1 dispatch in %s: %s" % (name, note))
            elif (gu, gv) != want:
                problems.append("E1 dispatch in %s returned the wrong double"
                                % name)
            else:
                dispatched.append(name.split("/")[-1])
        except Exception as exc:                            # noqa: BLE001
            problems.append("E1 dispatch in %s raised %s, expected a clean "
                            "double" % (name, type(exc).__name__))

        # 2. the narrow guard itself, reached directly: still errata E1.
        vals = {}
        for base, poly in (("u", u), ("up", u), ("v", v), ("vp", v),
                           ("f", f), ("h", h)):
            for i2 in range(6):
                vals["%s%d" % (base, i2)] = poly.coeff(i2)
        deg2 = subs["Deg2ADD"]
        try:
            deg2(*[vals[k] for k in deg2.params], funcs=subs, F=F)
            problems.append("E1 did not reproduce in %s: Deg2ADD returned "
                            "cleanly -- the recorded erratum has silently "
                            "disappeared" % name)
        except ZeroDivisionError:
            fired.append(name.split("/")[-1])
        except Exception as exc:                            # noqa: BLE001
            problems.append("E1 in %s raised %s, expected ZeroDivisionError"
                            % (name, type(exc).__name__))
    # ch2 is deliberately not on that list: the vector is over GF(11) and the ch2
    # formulas require characteristic 2, so it is outside their domain. Their own
    # instance of E1 shows up in driver.py runs over GF(2) and GF(8).
    notes.append("E1: ADD(D,D) dispatches to the correct double in %s; Deg2ADD "
                 "directly still divides by zero in %s (ch2 needs a char-2 "
                 "vector, out of domain for this one)"
                 % (", ".join(dispatched), ", ".join(fired)))
    for line in notes:
        rep.note(line)
    if problems:
        rep.fail("errata", problems[0])
    else:
        rep.ok("errata", "E1 dispatched around and still recorded; E2 arity "
                         "confirmed")


def _parse_prime_poly(F, text):
    """A Magma-printed polynomial over a prime field."""
    text = text.strip()
    if text in ("0", ""):
        return Poly.zero(F)
    coeffs = {}
    for m in re.finditer(r"([+-]?)\s*(?:(\d+)\s*\*\s*)?(x(?:\^(\d+))?|\d+)", text):
        sign, mul, body, exp = m.groups()
        if not body:
            continue
        if body.startswith("x"):
            e = int(exp) if exp else 1
            c = int(mul) if mul else 1
        else:
            e, c = 0, int(body)
        if sign == "-":
            c = -c
        coeffs[e] = coeffs.get(e, 0) + c
    top = max(coeffs) if coeffs else 0
    return Poly.from_coeffs(F, [F(coeffs.get(i, 0)) for i in range(top + 1)])


def _norm_value(v):
    if isinstance(v, (list, tuple)):
        v = ", ".join(str(x) for x in v)
    return re.sub(r"[\s'\"\[\]()]", "", str(v))


def section_repros(rep, quick):
    """Replay the audit's stored failures through the post-rename files.

    Two things at once: the recorded defects are still present, and PR2's rename
    was neutral, since a rename that changed behaviour would change these outputs.
    """
    files = ("vfy-odd-repros.json", "even_minimal_repros.json",
             "lowdeg-failures.json")
    present = [f for f in files
               if os.path.isfile(os.path.join(AUDIT_HARNESS, f))]
    if not present:
        rep.skip("repros", "no stored repros under %s" % AUDIT_HARNESS)
        return
    fams, _excluded = D.discover_families()
    same = diff = 0
    problems = []
    for fname in present:
        data = json.loads(open(os.path.join(AUDIT_HARNESS, fname)).read())
        records = (list(data.values()) if isinstance(data, dict)
                   else [r.get("rec", r) for r in data])
        for r in records:
            F = GF(r["q"])
            f = _parse_prime_poly(F, r["f"])
            h = _parse_prime_poly(F, r["h"])
            kind = "nch2" if str(r.get("h", "0")).strip() == "0" else "arb"
            fam = [x for x in fams if x.model == "ramified" and x.genus == 3
                   and x.kind == kind]
            if not fam:
                problems.append("no genus-3 ramified %s family" % kind)
                continue
            fam = fam[0]

            def divisor(primary, fallback):
                if primary in r:
                    val = r[primary]
                    if isinstance(val, str):
                        val = [x.strip() for x in val.strip("[]").split(",")]
                    return (_parse_prime_poly(F, val[0]),
                            _parse_prime_poly(F, val[1]))
                return (_parse_prime_poly(F, r[fallback[0]]),
                        _parse_prime_poly(F, r[fallback[1]]))

            try:
                cur = C.Curve(F, f, h, fam.kind, 3, "ramified")
            except AssertionError as exc:
                problems.append("%s: curve rejected: %s" % (fname, str(exc)[:50]))
                continue
            subs = M.discover(fam.add_path)
            params, _body = D._dispatcher_body(fam.add_path, "ADD")
            try:
                out = subs["ADD"](*D.build_args(params, cur,
                                                divisor("D1", ("u1", "v1")),
                                                divisor("D2", ("u2", "v2"))),
                                  funcs=subs, F=F)
                gu, gv, _note = D.decode_divisor(F, 3, out)
                got = "%s, %s" % (gu, gv)
            except Exception as exc:                        # noqa: BLE001
                got = type(exc).__name__
            if _norm_value(r.get("got")) == _norm_value(got):
                same += 1
            else:
                diff += 1
                if len(problems) < 3:
                    problems.append("%s branch %r: recorded %r, now %r"
                                    % (fname, r.get("branch", "?"),
                                       r.get("got"), got))
    if problems:
        rep.fail("repros", "%d of %d changed; first: %s"
                 % (diff, same + diff, problems[0]))
    else:
        rep.ok("repros", "%d stored repros reproduce byte-for-byte across %d files"
               % (same, len(present)))


def section_swap(rep, quick):
    """A deliberately swapped operand pair must be detected.

    PR10 reorders parameters so the smaller-degree divisor arrives first in both
    genus-3 models. A mistake there is wrong ONLY on mixed-degree inputs, which is
    the region the repository's own testers sample thinly, so this has to be shown
    to work before that PR starts.

    Mutates a copy. Nothing under the repository is written.
    """
    src = os.path.join(ROOT, "g3", "ramifiedModel", "g3Formulas",
                       "nch2_ramifiedG3_ADD.mag")
    if not os.path.isfile(src):
        rep.skip("swap", "genus-3 ramified ADD not present")
        return
    text = open(src).read()
    m = re.search(r"return Deg23ADD\(([^)]*)\);", text)
    if not m:
        rep.skip("swap", "no Deg23ADD call site to mutate")
        return
    args = [a.strip() for a in m.group(1).split(",")]
    # Deg23ADD takes the degree-3 divisor's six coefficients then the degree-2
    # divisor's four. Exchange the two blocks: same values, wrong operand order.
    swapped = args[6:10] + args[0:6] + args[10:]
    mutated = (text[:m.start()] + "return Deg23ADD(%s);" % ", ".join(swapped)
               + text[m.end():])
    tmp = tempfile.mkdtemp(prefix="selftest-swap-")
    try:
        dst = os.path.join(tmp, "g3", "ramifiedModel", "g3Formulas")
        os.makedirs(dst)
        for fn in os.listdir(os.path.dirname(src)):
            shutil.copy(os.path.join(os.path.dirname(src), fn), dst)
        open(os.path.join(dst, os.path.basename(src)), "w").write(mutated)
        fams, _excluded = D.discover_families(tmp)
        fam = [f for f in fams if f.kind == "nch2" and f.genus == 3]
        if not fam:
            rep.skip("swap", "the mutated copy was not discovered")
            return
        res = D.Result()
        D.run_family(fam[0], fams, res, (11, 13), 3 if quick else 5, 4,
                     7, False)
        if res.mismatches:
            rep.ok("swap", "%d of %d comparisons caught the swap"
                   % (len(res.mismatches), res.compared))
        else:
            rep.fail("swap", "a swapped operand pair went undetected over %d "
                             "comparisons" % res.compared)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def section_whitebox(rep, quick):
    """The constructed-case gate replays cleanly, and fires when a formula is broken."""
    import whitebox as W                                        # noqa: PLC0415

    res = W.Result()
    testers = W.find_testers()
    if not testers:
        rep.fail("whitebox", "no whitebox tester was found")
        return
    for t in testers:
        W.replay_tester(t, res, False)
    W.replay_harvested(res, False)
    if res.mismatches or res.errors or res.unparsed or res.no_branch:
        rep.fail("whitebox", "%d mismatch(es), %d error kind(s), %d unparsed, "
                             "%d reached no branch"
                 % (len(res.mismatches), len(res.errors), len(res.unparsed),
                    len(res.no_branch)))
        return
    clean = res.replayed

    # Now break a formula on a copy and confirm the cases catch it. A gate that has
    # never been seen to fail is not known to be a gate -- the same
    # demonstrate-rather-than-assume rule the swap section follows.
    src = os.path.join(ROOT, "g2", "ramifiedModel", "g2Formulas",
                       "nch2_ramifiedG2_ADD.mag")
    text = open(src).read()
    m = re.search(r"^(\s*)(upp1\s*:=\s*)([^;]+);", text, re.M)
    if not m:
        rep.skip("whitebox", "%d cases replayed clean; no line found to mutate"
                 % clean)
        return
    mutated = (text[:m.start()]
               + "%s%s%s + 1;" % (m.group(1), m.group(2), m.group(3))
               + text[m.end():])
    tmp = tempfile.mkdtemp(prefix="selftest-whitebox-")
    saved_root = W.ROOT
    try:
        dst = os.path.join(tmp, "g2", "ramifiedModel", "g2Formulas")
        os.makedirs(dst)
        for fn in os.listdir(os.path.dirname(src)):
            shutil.copy(os.path.join(os.path.dirname(src), fn), dst)
        for fn in os.listdir(os.path.join(ROOT, "g2", "ramifiedModel")):
            q = os.path.join(ROOT, "g2", "ramifiedModel", fn)
            if os.path.isfile(q):
                shutil.copy(q, os.path.join(tmp, "g2", "ramifiedModel", fn))
        open(os.path.join(dst, os.path.basename(src)), "w").write(mutated)
        W.ROOT = tmp
        broken = W.Result()
        for t in W.find_testers(tmp):
            if "nch2_ramifiedG2" in t:
                W.replay_tester(t, broken, False)
        caught = bool(broken.mismatches or broken.errors)
    finally:
        W.ROOT = saved_root
        shutil.rmtree(tmp, ignore_errors=True)

    if not caught:
        rep.fail("whitebox", "a perturbed formula went undetected by %d cases"
                 % broken.replayed)
    else:
        rep.ok("whitebox", "%d cases replay clean; a perturbed formula is caught "
                           "by %d of %d" % (clean, len(broken.mismatches),
                                            broken.replayed))


def section_dispatch(rep, quick):
    """A dispatcher can delegate to another dispatcher, three levels deep.

    PR5 puts `if D1 eq D2 then return DBL(...); end if;` at the top of every ADD,
    which makes ADD -> DBL -> Deg*DBL the first depth-three call chain in the
    repository. `_bind` used to re-wrap an already-bound sibling table at each
    level, and the second wrapper passed path=/funcs=/F= keywords into the first
    wrapper's positional-only closure: TypeError. Latent until the dispatch
    existed, which is exactly why this section injects the guard into a COPY and
    exercises the chain now -- the oracle must be shown to see the change before
    the change lands.
    """
    import maginterp as M                                       # noqa: PLC0415
    from poly import Poly                                       # noqa: PLC0415

    add_src = os.path.join(ROOT, "g2", "ramifiedModel", "g2Formulas",
                           "arb_ramifiedG2_ADD.mag")
    dbl_src = os.path.join(ROOT, "g2", "ramifiedModel", "g2Formulas",
                           "arb_ramifiedG2_DBL.mag")

    # The bound table must be recognised as its own output.
    F = GF(11)
    subs = dict(M.discover(dbl_src))
    subs.update(M.discover(add_src))
    b1 = M._bind(subs, [], F)
    if M._bind(b1, [], F) is not b1:
        rep.fail("dispatch", "_bind is not idempotent: re-binding a bound table "
                             "produced a new table")
        return

    # Inject the PR5 guard into a copy of the ADD file, then run the full chain.
    text = open(add_src).read()
    sig = "ADD:= function(u,v,up,vp,f,h)//startIGNORE\n"
    if sig not in text:
        rep.skip("dispatch", "ADD dispatcher signature not found to inject after")
        return
    # Multi-line, matching the files' own block style -- the interpreter's
    # statement splitter does not accept the one-line if-then-return form, so the
    # real PR5 edits use this shape too.
    guard = ("    if u eq up and v eq vp then\n"
             "        return DBL(u,v,f,h);\n"
             "    end if;\n")
    mutated = text.replace(sig, sig + guard, 1)

    tmp = tempfile.mkdtemp(prefix="selftest-dispatch-")
    try:
        tmp_add = os.path.join(tmp, "arb_ramifiedG2_ADD.mag")
        open(tmp_add, "w").write(mutated)
        table = dict(M.discover(dbl_src))
        table.update(M.discover(tmp_add))

        # Errata E1's own vector: GF(11), f = x^5 + x^3 + 1, u = x^2 + 1, v = 1,
        # D1 = D2 -- the input on which undispatched ADD divides by zero.
        R = lambda cs: Poly.from_coeffs(F, [F(c) for c in cs])  # noqa: E731
        f = R([1, 0, 0, 1, 0, 1])
        h = R([0])
        u = R([1, 0, 1])
        v = R([1])

        want_path = []
        want = table["DBL"](u, v, f, h, path=want_path, funcs=table, F=F)

        got_path = []
        got = table["ADD"](u, v, u, v, f, h, path=got_path, funcs=table, F=F)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if got != want:
        rep.fail("dispatch", "ADD(D,D) with the injected guard disagrees with "
                             "DBL: %r vs %r" % (got, want))
        return
    dbl_labels = [x for x in got_path if x.startswith("PRINT:DBL")]
    if not dbl_labels:
        rep.fail("dispatch", "ADD(D,D) matched DBL but no DBL branch label was "
                             "recorded -- the call did not route through DBL")
        return
    rep.ok("dispatch", "ADD -> DBL -> %s resolves at depth 3 and matches DBL "
                       "on errata E1's vector" % dbl_labels[0][6:])


def section_gate_guards(rep, quick):
    """Each guard on the whitebox gate is shown to FIRE, not merely to exist.

    A review found the gate reporting PASS while 41 verdicts were discarded. The fixes
    added guards; a guard never observed to fail is not known to be a guard, so each is
    provoked here and must fail the run.
    """
    import io                                                   # noqa: PLC0415
    import contextlib                                           # noqa: PLC0415
    import whitebox as W                                        # noqa: PLC0415

    def verdict():
        """(exit code, FAILED line) for a full replay under current conditions."""
        res = W.Result()
        res.expected_files |= W.expected_formula_files()
        W.KNOWN_ARITY[0] = W.known_arity_anomalies()
        for t in W.find_testers():
            W.replay_tester(t, res, False)
        W.replay_harvested(res, False)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = W.report(res, W.find_testers(), False, W.load_baseline())
        line = next((x.strip() for x in buf.getvalue().splitlines()
                     if x.startswith("  FAILED")), "")
        return code, line

    baseline_src = pathlib.Path(W.BASELINE_FILE).read_text()
    harvest_src = pathlib.Path(W.HARVEST_FILE).read_text()
    problems, shown = [], []

    def expect_fail(name, mutate, undo):
        try:
            mutate()
            code, line = verdict()
            if code == 0:
                problems.append("%s did not fail the run" % name)
            else:
                shown.append("%s -> %s" % (name, line))
        finally:
            undo()

    def restore_baseline():
        pathlib.Path(W.BASELINE_FILE).write_text(baseline_src)

    def restore_harvest():
        pathlib.Path(W.HARVEST_FILE).write_text(harvest_src)

    code, line = verdict()
    if code != 0:
        rep.fail("gate_guards", "the control run already fails: %s" % line)
        return

    key = "g3/splitModel/negReduced/g3Formulas/ch2_splitG3_ADD.mag"

    def shrink_exemption():
        # The baseline exempts a set of unreached labels. Remove one: the run must
        # fail, because that branch is now required and the corpus does not reach it.
        d = json.loads(baseline_src)
        d["files"][key]["unreached"] = d["files"][key]["unreached"][1:]
        pathlib.Path(W.BASELINE_FILE).write_text(json.dumps(d, indent=1))

    def trade_labels():
        # Swap an exempt label for a covered one, keeping the count identical. The
        # covered one becomes exempt-but-reached (stale) and the removed one becomes
        # required-but-missed; both fire. This is the trade a COUNT could not catch.
        d = json.loads(baseline_src)
        u = d["files"][key]["unreached"]
        u[0] = "ADD000"          # a label the corpus does cover
        pathlib.Path(W.BASELINE_FILE).write_text(json.dumps(d, indent=1))

    def unpin_arity():
        d = json.loads(baseline_src)
        d["arity_anomalies"] = d["arity_anomalies"][1:]
        pathlib.Path(W.BASELINE_FILE).write_text(json.dumps(d, indent=1))

    def drift_case():
        d = json.loads(harvest_src)
        d["cases"][0]["labels"] = ["NOT_A_REAL_LABEL"]
        pathlib.Path(W.HARVEST_FILE).write_text(json.dumps(d, indent=1))

    expect_fail("an exemption is removed from the baseline", shrink_exemption,
                restore_baseline)
    # The one a COUNT could not catch: swap a label, keep the total.
    expect_fail("an exempt label traded for a covered one, count unchanged",
                trade_labels, restore_baseline)

    # A newly added branch in a baselined file must NOT inherit the exemption --
    # the hole the covered-set baseline format left open, demonstrated before the
    # switch to storing `unreached`.
    orig_labels = D.labels_in

    def add_branch():
        D.labels_in = (lambda p: orig_labels(p) | {"ADD_NEWLY_ADDED"}
                       if p.endswith("/ch2_splitG3_ADD.mag") else orig_labels(p))

    expect_fail("a new branch appears in a baselined file", add_branch,
                lambda: setattr(D, "labels_in", orig_labels))
    expect_fail("an arity anomaly is not pinned", unpin_arity, restore_baseline)
    expect_fail("a harvested case drifted from its record", drift_case,
                restore_harvest)

    # The sentinel guard: declare a label that IS reached to be an unguarded marker.
    orig = D.sentinel_labels

    def claim_sentinel():
        D.sentinel_labels = lambda p: ({"ADD00"}
                                       if p.endswith("nch2_ramifiedG2_ADD.mag")
                                       else orig(p))

    expect_fail("a reached label declared a fall-through marker", claim_sentinel,
                lambda: setattr(D, "sentinel_labels", orig))

    for line in shown:
        rep.note(line)
    if problems:
        rep.fail("gate_guards", problems[0])
    else:
        rep.ok("gate_guards", "%d guards provoked, all fired" % len(shown))


SECTIONS = [
    ("fields", section_fields),
    ("parse", section_parse),
    ("acceptance", section_acceptance),
    ("group_axioms", section_group_axioms),
    ("reference", section_reference),
    ("errata", section_errata),
    ("repros", section_repros),
    ("swap", section_swap),
    ("whitebox", section_whitebox),
    ("dispatch", section_dispatch),
    ("gate_guards", section_gate_guards),
]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--section", nargs="*", default=None,
                    help="sections to run; default all")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--quick", action="store_true",
                    help="smaller samples, for a pre-commit run")
    a = ap.parse_args(argv)

    if a.list:
        print("\n  sections\n")
        for name, fn in SECTIONS:
            first = (fn.__doc__ or "").strip().splitlines()[0]
            print("    %-14s %s" % (name, first))
        print()
        return 0

    chosen = SECTIONS
    if a.section:
        unknown = [s for s in a.section if s not in dict(SECTIONS)]
        if unknown:
            print("unknown section(s): %s" % ", ".join(unknown))
            return 2
        chosen = [(n, f) for n, f in SECTIONS if n in a.section]

    rep = Report()
    for name, fn in chosen:
        print("  running %s ..." % name)
        try:
            fn(rep, a.quick)
        except Exception as exc:                            # noqa: BLE001
            rep.fail(name, "raised %s: %s" % (type(exc).__name__, str(exc)[:80]))
    return rep.render()


if __name__ == "__main__":
    sys.exit(main())
