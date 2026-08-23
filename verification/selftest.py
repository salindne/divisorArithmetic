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
  repros          The audit's stored failures, replayed through the current
                  files. Since PR5, the equal-divisor records must give the
                  reference sum (they are the wrong ADD(D, D) outputs the audit
                  froze, and the dispatch corrects them); any unequal-divisor
                  record must still reproduce byte-for-byte.
  swap            That a deliberately swapped operand pair is detected. PR10
                  reorders parameters in the genus-3 models and a mistake there is
                  wrong only on mixed-degree inputs, so this capability has to be
                  demonstrated before that work starts, not assumed.
  adjugate        That `adjugate.py`'s verdict on the genus-3 adjugate block can
                  come out negative. Two wrong programs are required to be
                  caught, and one of them only outside characteristic 2, which is
                  what shows the sixteen fields are load-bearing. Needs no
                  Magma, so it runs in CI.
  blocks          That `blockcheck.py` -- the only thing here that executes a
                  reference block -- catches a block that disagrees with the
                  explicit code in the `u = up` class, which is where the real
                  defect hid. Needs Magma, so it SKIPs without it.

More sections exist than this list names; `python3 selftest.py --list` prints them
all, from each section's own docstring.

The `reference` and `repros` sections need the audit artefacts, which live outside
this repository. Point AUDIT_HARNESS at them, or let those two sections skip.
The `blocks` section needs real Magma, which no hosted runner has.
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

    # E2, fixed in PR5: no 6-valued return may remain in any genus-2 ramified
    # ADD file. Static, so it is checked by reading the source; a reappearance
    # is a regression of the fix, not a new pin.
    for fn in ("arb", "ch2", "nch2"):
        path = os.path.join(ROOT, "g2", "ramifiedModel", "g2Formulas",
                            "%s_ramifiedG2_ADD.mag" % fn)
        src = re.sub(r"//[^\n]*", "",
                     re.sub(r"/\*.*?\*/", "", open(path).read(), flags=re.S))
        arities = {}
        for m in re.finditer(r"return\s+([^;]+);", src):
            k = len(M._split_top(m.group(1)))
            arities[k] = arities.get(k, 0) + 1
        if arities.get(6, 0) != 0:
            problems.append("%s: errata E2 was fixed in PR5, but %d 6-valued "
                            "return(s) are back"
                            % (os.path.basename(path), arities.get(6, 0)))
        else:
            notes.append("E2 %-4s fixed: 0 6-valued returns among %d 5-valued"
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
        rep.ok("errata", "E1 dispatched around and still recorded; E2 fixed, "
                         "no 6-valued return remains")


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
    """Replay the audit's stored failures through the current files.

    Originally this asserted byte-identity: the recorded defects still present,
    and PR2's rename neutral. PR5's equal-divisor dispatch deliberately changes
    the answer on every record whose two divisors are EQUAL -- those were the
    wrong ADD(D, D) outputs the audit stored -- so the assertion is now split:

      * records with D1 = D2 must now equal the REFERENCE sum. Differing from
        the recorded value is the fix working; matching the reference is the
        stronger replacement for byte-identity.
      * records with D1 != D2 must still reproduce byte-for-byte, which is the
        rename-neutrality evidence, unchanged.
    """
    files = ("vfy-odd-repros.json", "even_minimal_repros.json",
             "lowdeg-failures.json")
    present = [f for f in files
               if os.path.isfile(os.path.join(AUDIT_HARNESS, f))]
    if not present:
        rep.skip("repros", "no stored repros under %s" % AUDIT_HARNESS)
        return
    fams, _excluded = D.discover_families()
    same = diff = dispatched = 0
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
            # DBL merged for the same reason the testers load both files: the
            # dispatcher's equal-divisor route resolves against it. nch2 borrows
            # the arb DBL exactly as its tester and driver.py do.
            subs = dict(M.discover(fam.dbl_path)) if fam.dbl_path else {}
            subs.update(M.discover(fam.add_path))
            params, _body = D._dispatcher_body(fam.add_path, "ADD")
            D1 = divisor("D1", ("u1", "v1"))
            D2 = divisor("D2", ("u2", "v2"))
            try:
                out = subs["ADD"](*D.build_args(params, cur, D1, D2),
                                  funcs=subs, F=F)
                gu, gv, _note = D.decode_divisor(F, 3, out)
                got = "%s, %s" % (gu, gv)
            except Exception as exc:                        # noqa: BLE001
                got = type(exc).__name__
            if D1 == D2:
                want = R.add(cur, D1, D2)
                want_s = "%s, %s" % want
                if _norm_value(want_s) == _norm_value(got):
                    dispatched += 1
                else:
                    problems.append("%s branch %r with D1 = D2: expected the "
                                    "reference sum %r, got %r"
                                    % (fname, r.get("branch", "?"), want_s, got))
            elif _norm_value(r.get("got")) == _norm_value(got):
                same += 1
            else:
                diff += 1
                if len(problems) < 3:
                    problems.append("%s branch %r: recorded %r, now %r"
                                    % (fname, r.get("branch", "?"),
                                       r.get("got"), got))
    if problems:
        rep.fail("repros", "%d unequal-divisor record(s) changed, %d equal-"
                           "divisor record(s) wrong; first: %s"
                 % (diff, len(problems) - min(diff, len(problems)), problems[0]))
    else:
        rep.ok("repros", "%d equal-divisor repros now give the reference sum; "
                         "%d unequal ones reproduce byte-for-byte across %d "
                         "files" % (dispatched, same, len(present)))


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


def section_equal_dispatch(rep, quick):
    """ADD(D, D) returns the correct double, in every family, deterministically.

    The random driver proves this at volume but is deliberately not in CI, so
    without this section nothing in CI would exercise the equal-divisor route at
    all. One curve and one pair per field through the driver's own machinery --
    its pair modes include `equal` and `equal/swapped` -- with the two buckets
    that hold equal-divisor failures required to be empty. Reverting any of the
    dispatch commits fails this section; it is the lock on PR5.
    """
    fams, _excluded = D.discover_families()
    res = D.Result()
    fields = (2, 3, 4, 5) if quick else (2, 3, 4, 5, 7, 8, 9)
    for fam in fams:
        if fam.model.startswith("split"):
            D.run_split_family(fam, fams, res, fields, 1, 1, 1105, False)
        else:
            D.run_family(fam, fams, res, fields, 1, 1, 1105, False)
    equal_wrong = len(res.precondition)
    equal_crash = sum(res.precondition_errors.values())
    if equal_wrong or equal_crash:
        first = (res.precondition[0]["family"] + " " + res.precondition[0]["op"]
                 if res.precondition else
                 next(iter(res.precondition_errors)))
        rep.fail("equal_dispatch",
                 "%d wrong and %d crashed where D1 = D2; first: %s"
                 % (equal_wrong, equal_crash, first))
        return
    if res.mismatches:
        rep.fail("equal_dispatch", "%d mismatch(es) on the documented domain"
                 % len(res.mismatches))
        return
    if not res.compared:
        rep.fail("equal_dispatch", "no comparison ran; the lock is vacuous")
        return
    rep.ok("equal_dispatch",
           "%d comparisons across %d families, 0 wrong where D1 = D2"
           % (res.compared, len(res.per_family)))


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

    # The pin set is empty since PR5 fixed E2, so "remove a pin and watch the
    # shipped anomaly fail" no longer provokes anything. Inject the anomaly
    # instead: every ramified decode reports a wrong arity, none of it pinned.
    orig_decode = D.decode_divisor

    def fake_arity():
        def dec(F, genus, vals):
            gu, gv, note = orig_decode(F, genus, vals)
            return gu, gv, note or "returned 6 values, expected 5 (injected)"
        D.decode_divisor = dec

    def restore_decode():
        D.decode_divisor = orig_decode

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
    expect_fail("an arity anomaly is not pinned", fake_arity, restore_decode)
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


def section_domain(rep, quick):
    """The harness can express `h_g = 1`, and every way it could not is provoked.

    The char-2 decision of 2026-08-09 makes `h_g = 1` true of the implementation
    rather than merely declared -- ch2 stops extracting Coeff(h,g) altogether.
    Four independent mechanisms in driver.py could not represent that, and every
    one of them failed SILENTLY: the gate stayed green while testing curves the
    formulas do not claim. So each is provoked here, in the post-change shape,
    and each check fails without its fix.

    The shapes are simulated rather than waited for, on the PR3 principle that
    an oracle must be shown to see a change before the change lands.
    """
    import collections                                          # noqa: PLC0415
    import driver as D                                          # noqa: PLC0415

    fams, _excluded = D.discover_families()
    def fam(name):
        return [f for f in fams if f.name == name][0]
    ch2g2, arbg3, nch2g3 = fam("ramified/g2/ch2"), fam("ramified/g3/arb"), fam("ramified/g3/nch2")
    real_rs, real_bm = D.read_support, D.banner_members
    problems = []

    try:
        # (a) The banner must parse a singleton pin, not only a set.
        for txt, want_eq in (
                ("//   h(x) = h2*x^2 + h1*x + h0 (h2 in {0,1}) and", []),
                ("//   h(x) = x^2 + h1*x + h0 (deg h = 2, h2 = 1) and", [("h", "2", "1")]),
        ):
            if D._BANNER_EQ.findall(txt) != want_eq:
                problems.append("banner equality form: %r gave %r"
                                % (txt.strip(), D._BANNER_EQ.findall(txt)))
        if D._BANNER_DEG.findall("// (deg h = 2, h2 = 1)") != [("h", "2")]:
            problems.append("banner `deg h = 2` did not parse")

        # ...and banner_members must actually USE it. Testing the regex alone
        # passed with the parse removed from the function -- the very flaw this
        # section exists to catch, found by reverting the fix and watching this
        # check stay green. So round-trip a real banner through the real reader.
        tmpd = tempfile.mkdtemp(prefix="selftest-banner-")
        try:
            probe = os.path.join(tmpd, "ch2_ramifiedG2_ADD.mag")
            with open(probe, "w") as fh:
                fh.write("///////////////////////////////////\n"
                         "// Description: y^2 + h*y = f where\n"
                         "//   h(x) = x^2 + h1*x + h0 (deg h = 2, h2 = 1) and\n"
                         "//   f(x) = x^5 + f1x + f0\n"
                         "//Constant: f1,f0,h1,h0\n"
                         "\n"
                         "Deg1ADD:= function(u0,v0)\n"
                         "    // a body comment that must NOT be read: h2 = 0\n"
                         "    return 0;\n"
                         "end function;\n")
            got = D.banner_members(probe)
            if got.get(("h", 2)) != {1}:
                problems.append("banner_members did not read `h2 = 1` from a "
                                "banner: got %r" % (got,))
            if D.banner_degrees(probe).get("h") != 2:
                problems.append("banner_degrees did not read `deg h = 2`")
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)

        # (b) Equality parsing must stay inside the banner. A formula body is
        # full of derivation comments -- nch2_ramifiedG3_ADD.mag has `-h3 = 0;`
        # -- and a whole-file scan would read one as a domain statement.
        body_pins = D.banner_members(nch2g3.add_path)
        if ("h", 3) in body_pins:
            problems.append("banner_members read h3 out of a formula body comment")

        # (c) A borrowed DBL's banner is not the borrower's domain. nch2/g3 has
        # h = 0 and borrows the arb DBL, whose banner says (h3 in {0,1}).
        cons, mem, _why = D.family_domain(nch2g3, fams, "ADD")
        if ("h", 3) in (mem or {}) or 3 not in cons["h"]:
            problems.append("nch2/g3 inherited h3 from the borrowed arb DBL banner "
                            "(cons[h]=%s, members=%s)" % (sorted(cons["h"]), sorted(mem or {})))

        # (d) A singleton pin must actually bite. Before the skip was gated on
        # `0 in allowed`, narrowing {0,1} to {1} changed nothing at all.
        cons, _mem, _why = D.family_domain(ch2g2, fams, "ADD")
        seen = collections.Counter()
        rng = random.Random(11)
        for _ in range(30 if quick else 60):
            cur = D.curve_in_domain(GF(8), ch2g2, cons, rng, members={("h", 2): {1}})
            if cur is not None:
                seen[cur.h.deg] += 1
        if set(seen) != {2}:
            problems.append("h2 = 1 did not force deg h = 2: %s" % dict(seen))

        # (e) The leading coefficient of a ramified f is the MODEL, not a domain
        # assumption. A ch2 genus-3 dispatcher reads only Coeff(f,2..0), so the
        # zero-contrast used to put index 2g+1 in cons["f"], and curve_in_domain
        # zeroed it -- an uncaught AssertionError out of C.Curve.
        def rs_ch2g3(path, op="ADD"):
            out = real_rs(path, op)
            if out and "nch2_ramifiedG3" in path:
                out = {"f": {0, 1, 2}, "h": {0, 1, 2, 3}}
            return out
        D.read_support = rs_ch2g3
        cons, _mem, _why = D.family_domain(nch2g3, fams, "ADD")
        if 7 in cons["f"]:
            problems.append("cons[f] kept f7, the monic leading coefficient")
        rng = random.Random(4)
        for _ in range(10):
            try:
                D.curve_in_domain(GF(11), nch2g3, cons, rng, members={("h", 3): {1}})
            except AssertionError as e:
                problems.append("uncaught AssertionError from a zeroed leading "
                                "coefficient: %s" % str(e)[:60])
                break
            except ValueError as e:
                # the defensive guard in curve_in_domain, which means the
                # domain_constraints filter above is gone
                problems.append("leading coefficient reached curve_in_domain: "
                                "%s" % str(e)[:60])
                break
        D.read_support = real_rs

        # and the defensive guard, in case that filter is ever removed
        try:
            D.curve_in_domain(GF(11), nch2g3, {"f": {7}, "h": set()}, random.Random(1))
            problems.append("no guard against zeroing a leading coefficient")
        except ValueError:
            pass

        # (f) Post-PR27 end to end: no Coeff(h,2), banner pins h2 = 1.
        def rs_no_h2(path, op="ADD"):
            out = real_rs(path, op)
            if out and "ch2_ramifiedG2" in path:
                out = {"f": out["f"] - {2}, "h": out["h"] - {2}}
            return out
        D.read_support = rs_no_h2
        D.banner_members = (lambda path: {("h", 2): {1}}
                            if "ch2_ramifiedG2" in path else real_bm(path))
        cons, mem, _why = D.family_domain(ch2g2, fams, "ADD")
        seen, f2live = collections.Counter(), 0
        rng = random.Random(3)
        for _ in range(30 if quick else 60):
            cur = D.curve_in_domain(GF(8), ch2g2, cons, rng, members=mem)
            if cur is not None:
                seen[cur.h.deg] += 1
                if not cur.f.coeff(2).is_zero():
                    f2live += 1
        if set(seen) != {2} or f2live:
            problems.append("post-restriction ch2/g2 inverted onto deg h < 2: "
                            "%s, f2 live in %d" % (dict(seen), f2live))
        D.read_support, D.banner_members = real_rs, real_bm

        # (g) An unreadable domain must be loud, not silent.
        D.banner_members = lambda path: {}
        for f in (ch2g2, arbg3):
            _c, mem, _w = D.family_domain(f, fams, "ADD")
            if not D.require_leading_pin(f, mem):
                problems.append("%s: no complaint when the banner pins nothing" % f.name)
        _c, mem, _w = D.family_domain(nch2g3, fams, "ADD")
        if D.require_leading_pin(nch2g3, mem):
            problems.append("nch2/g3 wrongly required an h_g pin (its h is 0)")
        D.banner_members = real_bm
    finally:
        D.read_support, D.banner_members = real_rs, real_bm

    rep.note("    domain: 7 mechanisms provoked (banner set + singleton + scope, "
             "borrowed banner, singleton bite, leading coefficient, loud failure)")
    if problems:
        rep.fail("domain", problems[0])
    else:
        rep.ok("domain", "7 mechanisms provoked, all correct")


def section_specialisation(rep, quick):
    """A specialisation may never cost more than the family it specialises.

    PR15 found that the odd-characteristic genus-3 addition had become MORE
    expensive than the arbitrary-characteristic addition it is a specialisation
    of -- 62 M+S against 56, and 77 additions against 71. That cannot be right:
    nch2 is arb with `h = 0` substituted, so it does strictly less work.

    Nothing caught it, and no existing gate could have. Every check in this
    repository verifies a file against a reference implementation; none compares
    a specialisation against its PARENT. The drift happened because ten
    efficiency findings landed in the parent and none in the child, and each was
    verified against the file it was found in.

    So the relationship is asserted here directly. For every operation shape the
    two families share, the child's cost must not exceed the parent's in M+S, in
    A, or in C. M and S individually are allowed to trade -- several of the
    child's savings turn a multiplication into a squaring -- which is why the
    multiplicative comparison is on the sum.
    """
    import opcount as O                                         # noqa: PLC0415
    import driver as D                                          # noqa: PLC0415

    PAIRS = [("ramified/g3/nch2", "ramified/g3/arb")]

    fams, _excluded = D.discover_families()
    by_name = {f.name: f for f in fams}
    target = 400 if quick else 1500

    for child_name, parent_name in PAIRS:
        child, parent = by_name.get(child_name), by_name.get(parent_name)
        if child is None or parent is None:
            rep.skip("specialisation", "%s or %s not discovered" % (child_name, parent_name))
            continue
        field = 31
        kid, why_kid = O.count_family(child, fams, field, target=target)
        par, why_par = O.count_family(parent, fams, field, target=target)
        if kid is None or par is None:
            rep.skip("specialisation", "not measurable: %s / %s" % (why_kid, why_par))
            continue

        shared = sorted(set(kid) & set(par))
        if not shared:
            rep.fail("specialisation",
                     "%s and %s share no operation shape" % (child_name, parent_name))
            continue
        bad = []
        for shape in shared:
            # The child borrows the parent's doubling outright, so those rows are
            # the same code and carry no information about drift.
            if shape.endswith("DBL") and child.dbl_path == parent.dbl_path:
                continue
            cm, cs, ca, cc, _ci = kid[shape]["modal"]
            pm, ps, pa, pc, _pi = par[shape]["modal"]
            for col, cv, pv in (("M+S", cm + cs, pm + ps), ("A", ca, pa), ("C", cc, pc)):
                if cv > pv:
                    bad.append("%s %s: child %s %d > parent %d" % (child_name, shape, col, cv, pv))
        if bad:
            rep.fail("specialisation", "; ".join(bad[:4]))
            for b in bad:
                rep.note("    " + b)
        else:
            rep.ok("specialisation",
                   "%s never exceeds %s on %d shared shape(s)"
                   % (child_name, parent_name, len(shared)))



def section_blocks(rep, quick):
    """`blockcheck.py` executes a reference block, and is shown to catch a wrong one.

    A reference block -- the `//Formulation` algorithm inside
    `/* //startIGNORE ... */` -- is executed by nothing else in this repository,
    and the claim that uncommenting one reproduces the explicit code was
    unverified for the whole life of these files. It was also false: the genus-3
    ramified `arb` Deg3ADD block agreed on every input whose `gcd(u, up)` had
    degree 0, 1 or 2 and disagreed where `u = up`.

    So this section does two things. It runs every shipped ADD block in every
    family blockcheck can reach -- twelve of them, discovered by
    `blockcheck.add_functions` rather than named here -- and requires agreement in
    every gcd class of every one. Then it injects a defect confined to the
    `u = up` branch of one of them and requires blockcheck to report a
    disagreement whose wrong comparisons all land in that class -- "a guard never
    seen to fire is not known to be a guard", and the class that matters is
    precisely the one the earlier three-way Magma checking missed.

    The provocation is injected into one block, not twelve, because one
    demonstration that the oracle detects a wrong block is what is needed; the
    breadth is in the control, which is the part that would go stale. `--quick`
    keeps one function per family, so a pre-commit run stays at two Magma checks
    plus the provocation.

    Which side of a disagreement is wrong is a question this section cannot
    answer, and it says so rather than guessing: blockcheck compares two
    implementations of the same algorithm. `whitebox.py` and `driver.py` are what
    check the explicit side against `reference.py`.

    THE ORIGINAL DEFECT IS NO LONGER A PROVOCATION, AND THAT IS MEASURED

    The natural injection is the defect itself: delete the missing
    `upp := upp/LeadingCoefficient(upp);` from CASE #4.1. It no longer provokes
    anything, because the rewritten CASE #4.1 obtains `upp` as an exact quotient
    of a monic degree-5 numerator by a monic divisor -- the subtracted term
    `s*(s*u + 2*v + h)` has degree at most 4 against `k*S1`'s 5, in every
    characteristic -- so it is monic already and the normalisation is dead code.
    Measured before choosing a different injection: 170 firings in `arb` and 125
    in `nch2`, leading coefficient 1 at every one. The run is repeated here (not
    in `--quick`) and reported as a note, so that stays evidence rather than a
    remark. A live defect in the same branch is used to gate instead.

    NO FORMULA FILE IS WRITTEN

    `gate_guards` mutates files on disk because `whitebox.py` reads its inputs
    from disk. Here the block is a parameter -- `blockcheck.run(block_lines=...)`
    -- so the mutation happens in memory and the formula file is only ever read.
    Nothing to restore, so no crash and no concurrent edit can lose anyone's
    work. The on-disk path is exercised anyway: the control run below is the one
    that reads the block out of the file.
    """
    import blockcheck as B                                      # noqa: PLC0415

    FAMILY, FUNCTION = "arb", "Deg3ADD"
    # Live defects in the u = up branch: CASE #4.2 divides both u and up by the
    # degree-2 S1, and dropping either division leaves upp = u*up a degree too
    # high. Confined to u = up by construction, which is the property being
    # demonstrated. Two candidates rather than one because the wording of a block
    # is not a stable interface -- if the first idiom is rewritten away the gate
    # should try the next and report which it used, not collapse.
    CANDIDATES = [("up := ExactQuotient(up,S1);", "CASE #4.2"),
                  ("u := ExactQuotient(u,S1);", "CASE #4.2")]
    # The original F2 defect, kept for the note above.
    DEAD, DEAD_CASE = "upp := upp/LeadingCoefficient(upp);", "CASE #4.1"

    targets, broken = B.discover_targets()
    for rel, why in broken:
        rep.note("blocks: unreadable tester %s: %s" % (rel, why))
    if FAMILY not in targets:
        rep.fail("blocks", "blockcheck discovers no %r family; known: %s"
                 % (FAMILY, ", ".join(sorted(targets)) or "none"))
        return

    ok, why = B.magma_status()
    if not ok:
        rep.skip("blocks", "needs real Magma via tools/magma-docker/magma.sh: %s"
                 % why)
        return

    target = targets[FAMILY]
    curves, pairs, seed = (3, 4, 11) if quick else (4, 6, 11)

    # What to check: every ADD block of every discovered family, or one per family
    # in --quick. Discovered from the files, so a block added to one of them is
    # checked without an edit here, and a block renamed out of existence fails the
    # coverage test below instead of quietly leaving the gate.
    plan = []
    for name in sorted(targets):
        fns, unrunnable = B.add_functions(targets[name].add_path)
        for fn, whynot in unrunnable:
            rep.note("    blocks: %s %s has no runnable block: %s"
                     % (name, fn, whynot))
        if FUNCTION not in fns:
            rep.fail("blocks", "%s has no runnable %s block, so the provocation "
                               "has nowhere to go; runnable: %s"
                     % (name, FUNCTION, ", ".join(fns) or "none"))
            return
        plan += [(name, FUNCTION)] if quick else [(name, f) for f in fns]

    control, checked, compared, disagreed = None, [], 0, []
    for name, fn in plan:
        res = B.run(targets[name], fn, curves=curves, pairs=pairs, seed=seed)
        compared += res.compared
        if res.verdict == "AGREE":
            checked.append("%s %s %d" % (name, fn, res.compared))
        else:
            detail = res.error or ", ".join(
                "shared %d: %d wrong of %d" % (s, w, c)
                for s, c, w in res.classes if w) or res.verdict
            disagreed.append("%s %s (%s)" % (name, fn, detail))
            for line in res.stdout.splitlines():
                if line.startswith("MISMATCH"):
                    rep.note("    %s %s %s" % (name, fn, line.strip()))
        if (name, fn) == (FAMILY, FUNCTION):
            control = res
    if disagreed:
        rep.fail("blocks", "shipped block(s) do not agree with their explicit "
                           "code: %s; which side is wrong is for whitebox.py and "
                           "driver.py to say" % "; ".join(disagreed[:3]))
        return
    # "Nothing failed" must not be reachable by checking less than was discovered.
    # Compared against the discovered set rather than against a count, so a family
    # or a block that disappears from the files fails here instead of shrinking
    # the gate silently.
    if control is None or {n for n, _f in plan} != set(targets):
        rep.fail("blocks", "the gate narrowed: %d block(s) checked (%s) over "
                           "families %s, out of %s discovered"
                 % (len(plan), ", ".join("%s %s" % p for p in plan) or "none",
                    ", ".join(sorted({n for n, _f in plan})) or "none",
                    ", ".join(sorted(targets))))
        return
    rep.note("blocks: %d shipped block(s) = their explicit code on %d comparisons "
             "(%s)" % (len(plan), compared, ", ".join(checked)))
    rep.note("blocks: %s %s gcd classes %s"
             % (FAMILY, FUNCTION,
                "/".join(str(c) for _s, c, _w in control.classes)))

    _sig, body, _arity = B.extract(target.add_path, FUNCTION)
    tried, hurt, used = [], None, None
    for needle, case in CANDIDATES:
        mutated, dropped = B.drop_in_case(body, needle, case)
        if dropped == 0:
            tried.append("%r is not inside %s" % (needle, case))
            continue
        hurt = B.run(target, FUNCTION, curves=curves, pairs=pairs, seed=seed,
                     block_lines=mutated)
        used = "dropping %d x %r from %s" % (dropped, needle, case)
        if hurt.verdict == "DISAGREE" and not hurt.error:
            break
        tried.append("%s gave %s" % (used, hurt.error or hurt.verdict))
    problems = []
    if hurt is None:
        problems.append("cannot inject any provocation: %s" % "; ".join(tried))
    elif hurt.error:
        problems.append("the provoked run errored instead of disagreeing: %s"
                        % hurt.error)
    elif hurt.verdict != "DISAGREE":
        problems.append("a wrong block was not detected -- %s gave %s, %d wrong "
                        "of %d" % (used, hurt.verdict, hurt.wrong, hurt.compared))
    else:
        equal_u = max(s for s, _c, _w in hurt.classes)
        stray = [(s, w) for s, _c, w in hurt.classes if w and s != equal_u]
        if stray:
            problems.append("the injected defect is confined to u = up but wrong "
                            "answers appeared in gcd class(es) %s"
                            % ", ".join("%d (%d wrong)" % sw for sw in stray))
        if not [w for s, _c, w in hurt.classes if s == equal_u and w]:
            problems.append("no wrong answer in the u = up class, where the "
                            "injected defect lives")
    for line in tried:
        rep.note("    blocks: " + line)

    if not quick:
        dead, n = B.drop_in_case(body, DEAD, DEAD_CASE)
        if n == 0:
            rep.note("blocks: %r no longer appears inside %s" % (DEAD, DEAD_CASE))
        else:
            r = B.run(target, FUNCTION, curves=curves, pairs=pairs, seed=seed,
                      block_lines=dead)
            rep.note("blocks: dropping the %d %s normalisation(s) -- the original "
                     "defect -- gives %s, %d wrong of %d: dead code there, as "
                     "computed" % (n, DEAD_CASE, r.verdict, r.wrong, r.compared))

    if problems:
        rep.fail("blocks", problems[0])
        for p in problems:
            rep.note("    " + p)
    else:
        rep.ok("blocks", "%d block(s), %d compared clean; %s from %s %s gave %d "
                         "wrong of %d, all in the u = up class"
               % (len(plan), compared, used, FAMILY, FUNCTION,
                  hurt.wrong, hurt.compared))


def section_adjugate(rep, quick):
    """`adjugate.py`'s verification of the genus-3 adjugate block, shown to fire.

    That module recomputes the NEW_WORK N26 measurements -- the candidate table,
    the span of the nine cofactors as quadratic forms, the lower bound on t-by-t
    products, and the bilinear floor for the bottom row -- from scratch, with no
    third-party dependency. Everything it prints is either measured on the spot
    or read out of a formula file, so this section's job is to make sure its
    verdict is capable of coming out negative.

    THE CONTROL

    Its `source` section is run first, because everything else in the module
    stands on it: the cofactor definitions are parsed out of the `//| m1= ... |`
    comment block that nine formula files carry, and required to agree with an
    adjugate this module builds itself from `multiply by w, reduce mod up`. If a
    file's block is edited into disagreement, that is where it shows.

    Then the candidate table and the whole-region pair, at reduced trials.

    THE PROVOCATIONS -- TWO, BECAUSE ONE WOULD NOT SHOW THE FIELDS ARE REAL

    "A guard never seen to fire is not known to be a guard", so a wrong program
    is handed to `adjugate.check` and a negative verdict is *required*:

      * an operand swap (`m9 = t1*t5 - t2*t1` for `- t2*t4`) has to be reported
        wrong in every field, all sixteen, seven of which have characteristic 2.

      * a sign flip (`t5 = t1 + up1*t7` for `-`) has to be reported wrong in
        every odd-characteristic field and in *none* of the characteristic-2
        ones. That asymmetry is the check that the sixteen fields are not
        decoration: a suite that only ever ran GF(2) would pass the first
        provocation and miss this one entirely, and a suite that never ran GF(2)
        would report the second as simply wrong everywhere.

    Neither perturbation changes the op count, so a count-only comparison would
    accept both -- which is why the values are compared against an independent
    schoolbook reference rather than the counts being compared against a table.

    THE COUNTS ARE REQUIRED AGAINST THE FILES, NOT AGAINST A TABLE HERE

    `arb_ramifiedG3_DBL.mag` annotates its adjugate block `// 16m 0s 9a` and
    `arb_ramifiedG3_ADD.mag` annotates `// top: 16m 0s 9a`,
    `// total: 27m 0s 17a` and `// 11m 0s 8a`. All four comments are parsed and
    the measured counts are required to equal them exactly. A count that moves
    because someone improved the block fails here until the comment moves with
    it, which is the intended behaviour.

    NO FORMULA FILE IS WRITTEN

    On the same principle as `blocks`: the candidate programs are Python
    functions passed to `adjugate.check` as parameters, so a provocation is a
    function defined in this docstring's own scope and nothing on disk is
    touched. The formula files are opened read-only, for parsing.

    THE THREE SHIPPED FRAGMENTS ARE MEASURED ON THE SOURCE, NOT ON A RETYPING

    `adjugate.section_mag` extracts each shipped fragment's real statement text
    from the .mag between two anchors and executes it through `maginterp.py` --
    the same interpreter and cost model `opcount.py` uses -- then requires the
    count AND the values to equal the transcription's. So for `shipped_7`,
    `shipped_7_dbl` and `split_q` a transcription that drifted from the file is
    caught. A moved anchor fails rather than skipping, since the anchors are the
    only handle on the source.

    WHAT THIS SECTION DOES NOT CHECK

    The rest are still transcriptions: `shipped_9` and both `region` rows straddle
    the `d eq 0` guard, so no anchor pair isolates them as a program, and the
    `row3` pair and every rank-5 variant exist nowhere in the repository as .mag.
    For those, the *values* are checked against the parsed cofactor definitions
    and the region *count* against the file's own `// total:` comment, but a
    transcription error preserving both would survive.
    """
    import adjugate as ADJ                                      # noqa: PLC0415

    trials = 25 if quick else 60
    problems = []

    src = ADJ.section_source()
    if not src["ok"]:
        rep.fail("adjugate", "the cofactor definitions do not check out: %s"
                 % "; ".join(src["problems"][:2]))
        return
    rep.note("adjugate: %d formula file(s) carry the cofactor block, all nine "
             "entries agreeing with an independently built adj(T); det(T) = the "
             "5x5 Sylvester Res(w,up)" % src["files_with_block"])

    # The three shipped fragments' REAL statement text, extracted between two
    # anchors and priced through `maginterp.py` -- the same interpreter and cost
    # model `opcount.py` uses. This is the only thing here that measures the
    # source rather than a retyping of it, so a transcription that drifted from
    # the .mag is caught here and nowhere else. A moved anchor is a failure and
    # not a skip: the anchors are the module's only handle on the source.
    mag = ADJ.section_mag()
    for row in mag["rows"]:
        if not row["ok"]:
            problems.append("the .mag fragment for %s: %s"
                            % (row["candidate"], row["why"] or "not ok"))

    table = ADJ.section_table("entries", None, trials)
    region = ADJ.section_table("region", None, trials)
    for blob, what in ((table, "candidate"), (region, "region")):
        for row in blob["rows"]:
            if not row["ok"]:
                problems.append("%s %s does not reproduce the reference: %s"
                                % (what, row["name"],
                                   (row["fails"] or [["?"]])[0]))
            if row["expect_agrees"] is False:
                problems.append("%s %s measured %dM %dS %dA against the claimed "
                                "%s" % (what, row["name"], row["M"], row["S"],
                                        row["A"], row["expect"]))

    # the four op-count comments in the two ramified files, parsed, required
    annots = ADJ.all_annotations()
    required = [("shipped_7", ("arb_ramifiedG3_ADD.mag", "top")),
                ("shipped_7_dbl", ("arb_ramifiedG3_DBL.mag", "block")),
                ("region_shipped", ("arb_ramifiedG3_ADD.mag", "total"))]
    rows = {r["name"]: r for r in table["rows"] + region["rows"]}
    for name, key in required:
        want, row = annots.get(key), rows.get(name)
        if row is None:
            problems.append("candidate %s has gone from adjugate.py, so the "
                            "%s comment is no longer checked" % (name, key[0]))
        elif want is None:
            problems.append("%s no longer carries its `%s` op-count comment, so "
                            "%s is measured against nothing"
                            % (key[0], key[1], name))
        elif (row["M"], row["S"], row["A"]) != want:
            problems.append("%s measured %dM %dS %dA against %s's own %dm %ds "
                            "%da" % (name, row["M"], row["S"], row["A"], key[0],
                                     want[0], want[1], want[2]))
    lh = region.get("lower_half") or {}
    if lh.get("agrees") is False:
        problems.append("the lower half measured %s against the file's %s"
                        % (lh.get("measured"), lh.get("annotation")))
    elif lh.get("annotation") is None:
        problems.append("arb_ramifiedG3_ADD.mag's unlabelled op-count comment "
                        "has gone, so the lower half is measured against nothing")

    # ---- the provocations -------------------------------------------------
    def swapped_operand(t1, t4, t7, up0, up1, up2):
        """shipped_7 with `- t2*t4` written `- t2*t1`. Wrong in every field."""
        t2 = -(up0 * t7)
        t5 = t1 - up1 * t7
        t8 = t4 - up2 * t7
        m7 = t4 * t8 - t5 * t7
        m8 = t2 * t7 - t1 * t8
        m9 = t1 * t5 - t2 * t1
        m5 = m9 + up2 * m8
        m3 = -(up0 * m8)
        m2 = -(up0 * m7)
        m1 = m5 + up1 * m7
        return dict(m1=m1, m2=m2, m3=m3, m5=m5, m7=m7, m8=m8, m9=m9,
                    d=t1 * m1 + t4 * m2 + t7 * m3)

    def flipped_sign(t1, t4, t7, up0, up1, up2):
        """shipped_7 with `t5 = t1 + up1*t7`. Invisible in characteristic 2."""
        t2 = -(up0 * t7)
        t5 = t1 + up1 * t7
        t8 = t4 - up2 * t7
        m7 = t4 * t8 - t5 * t7
        m8 = t2 * t7 - t1 * t8
        m9 = t1 * t5 - t2 * t4
        m5 = m9 + up2 * m8
        m3 = -(up0 * m8)
        m2 = -(up0 * m7)
        m1 = m5 + up1 * m7
        return dict(m1=m1, m2=m2, m3=m3, m5=m5, m7=m7, m8=m8, m9=m9,
                    d=t1 * m1 + t4 * m2 + t7 * m3)

    good = ADJ.check(ADJ.shipped_7, 6, trials=trials)
    nfields = len(good["fields"])
    nch2 = sum(1 for n in good["fields"] if n in ADJ.CH2_NAMES)

    swap = ADJ.check(swapped_operand, 6, trials=trials)
    if swap["ok"]:
        problems.append("an operand swap in shipped_7 was NOT detected")
    elif len(swap["fields_wrong"]) != nfields:
        problems.append("the operand swap was detected in %d of %d fields, not "
                        "all: missing %s"
                        % (len(swap["fields_wrong"]), nfields,
                           sorted(set(good["fields"]) - set(swap["fields_wrong"]))))
    if (swap["M"], swap["S"], swap["A"]) != (good["M"], good["S"], good["A"]):
        problems.append("the operand swap changed the op count, so it does not "
                        "demonstrate that values are what is being compared")

    flip = ADJ.check(flipped_sign, 6, trials=trials)
    if flip["ok"]:
        problems.append("a sign flip in shipped_7 was NOT detected")
    elif flip["fields_wrong_char2"]:
        problems.append("a sign flip was reported wrong in characteristic 2 "
                        "(%s), where it cannot be"
                        % ", ".join(flip["fields_wrong_char2"]))
    elif len(flip["fields_wrong"]) != nfields - nch2:
        problems.append("the sign flip was detected in %d of the %d odd-"
                        "characteristic fields"
                        % (len(flip["fields_wrong"]), nfields - nch2))

    # ---- the bound and the floor, at cheap settings ------------------------
    span = ADJ.section_span((2, 3))
    if not span["ok"]:
        problems.append("the span of the nine entries is not 3-dimensional as "
                        "computed: generic %s, at up=0 %s"
                        % (span["generic_rank_over_Q_of_up"],
                           span["rank_at_up0_over_Q"]))
    bound = ADJ.section_bound((2, 3) if quick else (2, 3, 5, 7))
    if bound["bound"] != 4:
        problems.append("the lower bound came out %s, not 4"
                        % bound["bound"])
    rank = ADJ.section_rank((2, 3) if quick else (2, 3, 5))
    if not rank["ok"]:
        problems.append("the bottom row's bilinear floor is not as computed: "
                        "floor %s, attained %s"
                        % (rank["floor"], rank["attained"]))

    located = [r for r in mag["rows"] if r.get("found")]
    rep.note("adjugate: %d shipped fragment(s) executed from their real .mag text "
             "through maginterp.py: %s -- each equal to its transcription's count "
             "and values"
             % (len(located),
                ", ".join("%s %dM %dS %dA" % (r["candidate"], r["count"][0],
                                              r["count"][1], r["count"][2])
                          for r in located)))
    rep.note("adjugate: %d candidates + %d region variants verified over %d "
             "fields (%d of characteristic 2) x %d trials, and once as an "
             "identity in Z[t,up]"
             % (len(table["rows"]), len(region["rows"]), nfields, nch2, trials))
    rep.note("adjugate: the operand swap is wrong in all %d fields at the same "
             "%dM %dS %dA; the sign flip is wrong in the %d odd fields and in "
             "none of the %d characteristic-2 ones"
             % (len(swap["fields_wrong"]), swap["M"], swap["S"], swap["A"],
                len(flip["fields_wrong"]), nch2))
    rep.note("adjugate: span 3 at generic up and at up -> 0; bound %s t-by-t "
             "products, shipped spends %d of which %d survive up -> 0; bottom "
             "row floor %s bilinear products, shipped spends %d"
             % (bound["bound"], bound["census"]["shipped_7"]["t_by_t"],
                bound["census"]["shipped_7"]["t_by_t_up0"], rank["floor"],
                next(d["bilinear"] for d in rank["decompositions"]
                     if d["program"] == "row3_shipped")))

    if problems:
        rep.fail("adjugate", problems[0])
        for p in problems:
            rep.note("    " + p)
    else:
        rep.ok("adjugate", "%d programs verified and counted, %d of them priced "
                           "from their real .mag text; two provocations detected, "
                           "one only outside characteristic 2; 4 op-count "
                           "comments in the .mag files reproduced"
               % (len(table["rows"]) + len(region["rows"]), len(located)))


def section_dominance(rep, quick):
    """A read whose only assignment sits below it, checked in statement order.

    `undef.py` asks, per function, whether a name is assigned ANYWHERE in the
    body. An assignment below the read satisfies that, which is exactly the
    residue of a half-finished rename: a variable inlined at one site, its
    definition deleted, and a surviving read further up now resolving to a
    definition that has not run. Two such breakages reached real Magma during
    the 2026-08-20 genus-3 addition work and `undef.py` called both files clean.

    `dominance.py` walks each body in order and reports reads with no
    assignment above them. Both halves are exercised here: every formula file
    must be clean, and deleting one live assignment must be caught -- a gate
    never seen to fire is not known to be a gate.

    What this does NOT cover is recorded in `ERRATA.md` E15 and matters: an
    assignment inside an `if` above the read counts as reaching it, so a value
    defined only on a sibling path still passes. Only Magma sees that.
    """
    import dominance as DM                                      # noqa: PLC0415

    files = DM.formula_files()
    if not files:
        rep.fail("dominance", "no formula files discovered")
        return
    dirty = [(os.path.relpath(p, ROOT), DM.analyse(p)) for p in files]
    bad = [(rel, found) for rel, found in dirty if found]
    if bad:
        rel, found = bad[0]
        fn, lineno, nm = found[0]
        rep.fail("dominance", "%s %s:%d reads %r with no assignment above it (%d total)"
                 % (rel, fn, lineno, nm, sum(len(f) for _, f in bad)))
        return

    # the provocation: remove one live assignment that many reads depend on
    target = os.path.join(ROOT, "g3", "ramifiedModel", "g3Formulas",
                          "arb_ramifiedG3_ADD.mag")
    if not os.path.exists(target):
        rep.ok("dominance", "%d file(s) clean; provocation skipped, %s absent"
               % (len(files), os.path.basename(target)))
        return
    original = open(target, encoding="utf-8").read()
    lines = original.split("\n")
    hit = None
    for i, line in enumerate(lines):
        if line.strip().startswith("k3:=") and "//" not in line.split("k3")[0]:
            hit = i
            break
    if hit is None:
        rep.ok("dominance", "%d file(s) clean; provocation skipped, no k3 assignment"
               % len(files))
        return
    lines[hit] = "        //" + lines[hit].strip()
    try:
        open(target, "w", encoding="utf-8").write("\n".join(lines))
        provoked = DM.analyse(target)
    finally:
        open(target, "w", encoding="utf-8").write(original)
    if not provoked:
        rep.fail("dominance", "deleting a live k3 assignment was NOT detected, "
                              "so the check cannot be relied on")
        return
    rep.ok("dominance", "%d formula file(s) clean; deleting one live k3 assignment "
                        "gave %d report(s), so the check fires"
           % (len(files), len(provoked)))


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
    ("equal_dispatch", section_equal_dispatch),
    ("gate_guards", section_gate_guards),
    ("domain", section_domain),
    ("specialisation", section_specialisation),
    ("dominance", section_dominance),
    ("adjugate", section_adjugate),
    ("blocks", section_blocks),
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
