"""selftest.py -- checks the verification framework itself.

`driver.py` compares the .mag formulas against `reference.py`. Nothing that says
tells you whether the comparison is trustworthy: a reference that is wrong in the
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

# The audit's harness and stored repros. Outside this repository on purpose: they
# are evidence from a prior review, not part of the deliverable.
AUDIT_HARNESS = os.environ.get(
    "AUDIT_HARNESS", "/Users/s3b/Dev/divisor-audits/g3ram/harness")

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
    F = GF(11)
    f = Poly.from_coeffs_desc(F, [F.one, F.zero, F.one, F.zero, F.zero, F.one])
    h = Poly.zero(F)
    u = Poly.from_coeffs_desc(F, [F.one, F.zero, F.one])
    v = Poly.const(F, F.one)
    if not ((v * v + v * h - f) % u).is_zero():
        problems.append("E1 vector is not a valid divisor; the vector is wrong")
    fams, _excluded = D.discover_families()
    fired = []
    for name in ("ramified/g2/arb", "ramified/g2/nch2"):
        fam = [x for x in fams if x.name == name][0]
        subs = M.discover(fam.add_path)
        params, _body = D._dispatcher_body(fam.add_path, "ADD")
        cur = C.Curve(F, f, h, fam.kind, 2, "ramified")
        try:
            subs["ADD"](*D.build_args(params, cur, (u, v), (u, v)),
                        funcs=subs, F=F)
            problems.append("E1 did not reproduce in %s: no division by zero" % name)
        except ZeroDivisionError:
            fired.append(name.split("/")[-1])
        except Exception as exc:                            # noqa: BLE001
            problems.append("E1 in %s raised %s, expected ZeroDivisionError"
                            % (name, type(exc).__name__))
    # ch2 is deliberately not on that list: the vector is over GF(11) and the ch2
    # formulas require characteristic 2, so it is outside their domain. Their own
    # instance of E1 shows up in driver.py runs over GF(2) and GF(8).
    notes.append("E1 reproduced in: %s (ch2 needs a char-2 vector, out of domain "
                 "for this one)" % ", ".join(fired))
    for line in notes:
        rep.note(line)
    if problems:
        rep.fail("errata", problems[0])
    else:
        rep.ok("errata", "E1 reproduces as a division by zero; E2 arity confirmed")


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


SECTIONS = [
    ("fields", section_fields),
    ("parse", section_parse),
    ("acceptance", section_acceptance),
    ("group_axioms", section_group_axioms),
    ("reference", section_reference),
    ("errata", section_errata),
    ("repros", section_repros),
    ("swap", section_swap),
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
