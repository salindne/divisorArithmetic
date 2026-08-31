"""The correctness gate for projective families. Four checks, none of which any
other gate in this repository performs.

WHY A NEW GATE. Every equality in the harness is exact on the raw return:
`driver._compare` at its `gu == want[0]`, `whitebox._replay_one` at its
`all(a == b for a, b in zip(got, exp))`, `blockcheck`'s `if E ne B then`. A
projective representative is one point of an orbit, so all of them are wrong in
principle for a projective family -- `(U:V:Z)` and `(lambda^a U : lambda^b V :
lambda Z)` are the same divisor and compare unequal. `blockcheck` cannot see such
a file at all: its parameter patterns reject a `Z`, so the function lands in
`unrunnable`.

THE FOUR CHECKS

  1. NORMALISE THEN COMPARE. Require `Z != 0`, form `u = x^g + sum U_i/Z^{a_i} x^i`
     and `v = sum V_j/Z^{b_j} x^j` from the DECLARED weights, and compare that
     against `reference.double` / `reference.add`.

  2. SCALING INVARIANCE, and this is the check with no analogue anywhere in the
     harness. For random `lambda != 0`, running on `(lambda^{a_i} U_i,
     lambda^{b_j} V_j, lambda Z)` must give a result that normalises to the same
     class. A wrong power of `Z` on one term is INVISIBLE at `Z = 1` -- and every
     frozen case and every Magma generator in this repository feeds `Z = 1`,
     because neither the extracted-case parser nor the harvested record has a `Z`
     slot. So without this check a projective formula is only ever tested on the
     one input where it degenerates to the affine one.

     This is also what makes the declared weight vector worth declaring: it turns
     the banner into a falsifiable claim rather than a table. A derived vector
     would be assumed and nothing would test it.

  3. CHAIN CONSISTENCY, which is the actual use. Run the doubling `k` times
     WITHOUT normalising between steps, normalise once, and compare against
     `reference.scalar_mul(curve, 2^k, D)`. This is the only check that can see a
     closure defect: a representation whose exponent pattern shifts per step
     passes checks 1 and 2 and diverges here.

  4. `Z = 0` CLASSIFICATION. What the identity is in this representation, and that
     `Z = 0` arises only where it should.

THE CALLING CONVENTION, established by measurement rather than assumed. Divisor
coordinates arrive PROJECTIVE, scaled by `Z` to their declared weights. Curve
coefficients arrive RAW: the formula carries them itself -- `f5 := f5*Z4` in its own
prologue, which is the `3C` the counter charges it -- so a caller that pre-scales
them applies the carriage twice. Correct at `Z = 1` either way, wrong at every
other `Z` if pre-scaled. See `scale_args`.

SCOPE. Ramified families only. The split model carries a balancing weight `n`
alongside `(u, v)` and its own `ccs` layer; nothing here is written for it, and it
refuses rather than guessing.

Run:  python3 projcheck.py [--curves N] [--pairs N] [--chain K] [--seed S]
"""
import argparse
import random
import re
import sys

import curves as C
import driver as D
import maginterp as M
import reference as R
from ff import GF
from poly import Poly


class Report(object):
    def __init__(self):
        self.checks = 0
        self.failures = []
        self.skips = []

    def ok(self, what, detail=""):
        self.checks += 1
        print("  PASS  %-22s %s" % (what, detail))

    def fail(self, what, detail):
        self.checks += 1
        self.failures.append((what, detail))
        print("  FAIL  %-22s %s" % (what, detail))

    def skip(self, what, why):
        self.skips.append((what, why))
        print("  SKIP  %-22s %s" % (what, why))


# ---------------------------------------------------------------------------
# the representation
# ---------------------------------------------------------------------------

def slot_names(genus):
    """The `u` and `v` coordinate names, descending, as a dispatcher returns them.

    `u_g` is excluded: a monic `u` returns it as the literal 1 at weight 0. A
    family carrying `u` non-monic would need this widened, and would have to
    declare a weight for it -- which is why the weights are read rather than
    assumed.
    """
    us = ["u%d" % i for i in range(genus - 1, -1, -1)]
    vs = ["v%d" % i for i in range(genus - 1, -1, -1)]
    return us, vs


def normalise(F, genus, vals, weights):
    """(u, v) affine from a projective return `(U_g..U_0, V_{g-1}..V_0, Z)`.

    ARITY IS 2g+2, not 2g+1. The shipped return shape INCLUDES the monic leading
    coefficient -- `return 1, upp2, upp1, upp0, vpp2, vpp1, vpp0` is 2g+1 at genus
    3 -- so a projective return carrying Z as well is 2g+2, eight values.

    That matters because it says WHICH branch of `decode_divisor` a projective
    return would have been misread by. An earlier note in this file assumed the
    leading 1 was dropped, making it 2g+1 and colliding with the exact-arity path
    (silent garbage). Under the shipped shape it is 2g+2 and collides with the
    errata-E2 path instead, which truncates Z away, returns a CORRECT affine
    divisor, and reports a note -- and that note was the one `opcount` discarded.
    The quieter failure, and the one that actually applies here.

    Returns (None, None, reason) when it cannot, rather than raising, so a run
    surfaces every bad case instead of stopping at the first.
    """
    us, vs = slot_names(genus)
    want = len(us) + 1 + len(vs) + 1
    if len(vals) != want:
        return None, None, "returned %d values, expected %d" % (len(vals), want)
    Z = vals[-1]
    if Z == F(0):
        return None, None, "Z = 0"
    missing = [n for n in us + vs if n not in weights]
    if missing:
        return None, None, "no declared weight for %s" % ",".join(missing)

    # THE RETURN SHAPE IS THE SHIPPED ONE (author's decision 2026-08-31): slot i
    # holds the coefficient of x^i and the monic 1 sits at slot deg(u), so a
    # lower-degree output arrives bottom-aligned with leading zeros --
    # `return 0, 0, 1, upp0, 0, 0, vpp0` at deg u = 1. All fifteen affine families
    # return that shape and `decode_divisor` reads it; making the one projective
    # family differ would trade a known hazard for a new one.
    #
    # THE CONSEQUENCE, and an earlier version of this function had it wrong: the
    # weight of a slot DEPENDS ON THE OUTPUT DEGREE. The coefficient of x^i in a
    # monic u of degree e sits at weight 2(e - i), so a degree drop of d lowers
    # every u weight by 2d -- a uniform shift off the declared full-degree vector,
    # which is why the banner still declares one thing.
    #
    # `v` does NOT shift. v == y on the support and y has weight 2g+1 whatever the
    # divisor's degree, so v_j is at (2g+1) - 2j on every branch. Measured across
    # all 37 branches of both families, not assumed here.
    zinv = F(1) / Z
    uvals = list(vals[:len(us) + 1])            # includes the leading slot
    lead = next((k for k, x in enumerate(uvals) if x != F(0)), None)
    if lead is None:
        return None, None, "u is identically zero"
    drop = lead                                 # slots skipped = g - deg(u)
    if uvals[lead] != F(1):
        return None, None, ("leading u coefficient is %s, not 1; this decode "
                            "assumes a monic u, and a non-monic family must "
                            "declare a weight for it" % uvals[lead])
    uc, vc = [F(1)], []
    for name, raw in zip(us[drop:], uvals[lead + 1:]):
        uc.append(raw * zinv ** (weights[name] - 2 * drop))
    for name, raw in zip(vs, vals[len(us) + 1:]):
        vc.append(raw * zinv ** weights[name])
    return (Poly.from_coeffs_desc(F, uc),
            Poly.from_coeffs_desc(F, vc), None)


# The curve coefficients are named here so `scale_args` leaves them alone.
_CURVE_COEF = re.compile(r"^[fh]\d+$")


def scale_args(F, args, params, weights, lam):
    """`args` with the DIVISOR coordinates scaled by `lam^weight` and `Z` by `lam`.

    THE CURVE COEFFICIENTS ARE PASSED RAW, and getting this wrong is what the
    first run of this gate caught. Measured 2026-08-31 against
    `row_B_dbl_weighted.mag`: feeding `f5*Z^4, f4*Z^6, f3*Z^8` is correct at Z = 1
    and WRONG at Z = 2, 3, 7, 50, while feeding raw `f5, f4, f3` is correct at all
    five.

    The grading really does give `wt(f_i) = 14 - 2i` -- that is what makes the map
    quasi-homogeneous. But the FORMULA carries them itself: the file's own prologue
    reads `Z2 := Z^2; Z4 := Z2^2; Z6 := Z4*Z2; Z8 := Z4^2; f5 := f5*Z4; ...`, which
    is exactly the 3C this project counts for it. A caller that pre-scales applies
    the carriage twice.

    So the earlier statement in this project's notes -- that a caller must refresh
    `f5*Z^4` as Z changes -- had the cost right and the interface backwards.
    """
    out = []
    for name, val in zip(params, args):
        if name in ("Z", "z"):
            out.append(val * lam)
        elif _CURVE_COEF.match(name):
            out.append(val)                     # raw; the formula carries them
        elif name in weights and not hasattr(val, "coeffs_up_to"):
            out.append(val * lam ** weights[name])
        else:
            out.append(val)
    return out


# ---------------------------------------------------------------------------
# the checks
# ---------------------------------------------------------------------------

def _params(path, fn_name):
    """The parameter names of `fn_name`, in order, read from the source."""
    with open(path) as fh:
        text = fh.read()
    m = re.search(re.escape(fn_name) + r"\s*:=\s*function\s*\(([^)]*)\)", text)
    if not m:
        return None
    return [p.strip() for p in m.group(1).split(",") if p.strip()]


def _bind(params, env):
    """Args for `params` from `env`, or the first name that is missing."""
    out = []
    for p in params:
        if p not in env:
            return None, p
        out.append(env[p])
    return out, None


def _env(F, cur, u, v, Z, weights, genus):
    """Projective inputs plus RAW curve coefficients.

    Raw is not an oversight -- the formula carries them itself. Measured: feeding
    `f5*Z^4` is correct at Z = 1 and wrong at Z = 2, 3, 7, 50.
    """
    uc, vc = u.coeffs_up_to(genus), v.coeffs_up_to(genus - 1)
    env = {"Z": Z, "z": Z}
    for i in range(genus):
        env["u%d" % i] = uc[i] * Z ** weights["u%d" % i]
        env["v%d" % i] = vc[i] * Z ** weights["v%d" % i]
    fc = cur.f.coeffs_up_to(2 * genus + 1)
    for i, c in enumerate(fc):
        env["f%d" % i] = c
    hc = cur.h.coeffs_up_to(genus) if cur.h is not None else []
    for i, c in enumerate(hc):
        env["h%d" % i] = c
    return env


def check_family(rep, fam, ncurves, pairs, chain, seed):
    if fam.is_split:
        rep.skip(fam.name, "split model: balancing weight and ccs layer unhandled")
        return
    if fam.coords != "projective":
        rep.skip(fam.name, "affine family: driver.py already gates it")
        return

    fams, _ = D.discover_families()
    cons, members, why = D.family_domain(fam, fams, "DBL")
    if cons is None:
        rep.fail(fam.name, "no domain: %s" % why)
        return

    g = fam.genus
    for op, path in (("DBL", fam.dbl_path),):
        if not path:
            rep.skip("%s %s" % (fam.name, op), "no file")
            continue
        weights = D.weights_declared(path)
        if not weights:
            rep.fail("%s %s" % (fam.name, op),
                     "declares '//Coordinates: projective' and no '//Weights:'. "
                     "The grading cannot be guessed; see driver.weights_declared")
            continue
        fns = M.discover(path)
        name = "Deg%dDBL" % g
        if name not in fns:
            rep.fail("%s %s" % (fam.name, op), "no %s in %s" % (name, path))
            continue
        params = _params(path, name)
        rng = random.Random(seed)
        F = GF(101)

        n1 = n2 = n3 = n4 = offpath = 0
        depths = []
        bad = []
        for _ in range(ncurves):
            cur = D.curve_in_domain(F, fam, cons, rng, members=members)
            if cur is None:
                continue
            Dv = C.random_divisor_of_degree(cur, g, rng)
            if Dv is None:
                continue
            want = R.double(cur, Dv)

            # 1. NORMALISE THEN COMPARE, at Z = 1 and at Z != 1
            for Z in (F(1), F(rng.randrange(2, 101))):
                env = _env(F, cur, Dv[0], Dv[1], Z, weights, g)
                args, miss = _bind(params, env)
                if args is None:
                    bad.append("no value for parameter %r" % miss)
                    break
                try:
                    out = list(fns[name](*args, funcs=fns, F=F))
                except Exception as exc:
                    bad.append("raised: %s" % str(exc)[:50])
                    break
                nu, nv, whyn = normalise(F, g, out, weights)
                if nu is None:
                    if whyn == "Z = 0":
                        offpath += 1        # not the frequent path; not this file's
                        break
                    bad.append("normalise: %s" % whyn)
                    break
                if nu == want[0] and nv == want[1]:
                    n1 += 1
                else:
                    bad.append("wrong result at Z=%s" % Z)

            # 2. SCALING INVARIANCE: a different representative, same class
            env = _env(F, cur, Dv[0], Dv[1], F(1), weights, g)
            lam = F(rng.randrange(2, 101))
            sc = scale_args(F, _bind(params, env)[0], params, weights, lam)
            try:
                a = list(fns[name](*_bind(params, env)[0], funcs=fns, F=F))
                b = list(fns[name](*sc, funcs=fns, F=F))
            except Exception as exc:
                bad.append("scaling raised: %s" % str(exc)[:40])
                continue
            na = normalise(F, g, a, weights)
            nb = normalise(F, g, b, weights)
            if na[2] == "Z = 0" or nb[2] == "Z = 0":
                continue                    # off-path, as above
            if na[0] is not None and nb[0] is not None and na[:2] == nb[:2]:
                n2 += 1
            else:
                bad.append("scaling by lam=%s changed the class" % lam)

            # 3. CHAIN: feed the output back in, never resetting Z
            # A chain that STOPS EARLY and a chain that DIVERGES are different
            # outcomes, and an earlier version of this conflated them. The ladder
            # legitimately leaves the frequent path -- Znew = d*sp2*Z vanishes
            # exactly when d = 0 or sp2 = 0, at rate O(1/q) per step -- so at
            # GF(101) an exit within a few steps is expected, not a defect. Only a
            # WRONG answer is a failure; depth is reported so a shallow run is
            # visible rather than hidden behind a pass.
            st = _bind(params, _env(F, cur, Dv[0], Dv[1], F(1), weights, g))[0]
            depth, diverged = 0, False
            for k in range(1, chain + 1):
                try:
                    out = list(fns[name](*st, funcs=fns, F=F))
                except Exception:
                    break
                nu, nv, _w = normalise(F, g, out, weights)
                if nu is None:
                    break                   # off-path: this file does not claim it
                wantk = R.scalar_mul(cur, 2 ** k, Dv)
                if not (nu == wantk[0] and nv == wantk[1]):
                    bad.append("chain DIVERGED at step %d" % k)
                    diverged = True
                    break
                depth = k
                env2 = dict(zip(params, st))
                for i in range(g):
                    env2["u%d" % i] = out[g - i]
                    env2["v%d" % i] = out[2 * g - i]
                env2["Z"] = env2["z"] = out[-1]
                st = _bind(params, env2)[0]
            if not diverged:
                n3 += 1
                depths.append(depth)

            # 4. Z = 0 must be refused by the decode, not silently divided by
            zero = list(a[:-1]) + [F(0)]
            if normalise(F, g, zero, weights)[2] is not None:
                n4 += 1
            else:
                bad.append("Z = 0 was not refused")

        tag = "%s %s" % (fam.name, op)
        if bad:
            rep.fail(tag, "; ".join(bad[:4]))
        elif n1 == 0:
            rep.fail(tag, "no curve in the family's domain produced a comparison; "
                          "a gate with nothing to check is not a pass")
        else:
            # Depths are REPORTED, not just counted. "5 chains of 8" would be true
            # of five chains that each died at step 1, and the chain check is the
            # only one that can see a closure defect -- so it must not be able to
            # degrade to nothing behind a PASS.
            rep.ok(tag, "%d normalise-and-compare (Z=1 and Z!=1), %d scaling-"
                        "invariant, %d chains none diverging at depths %s "
                        "(cap %d), %d Z=0 refusals, %d off-path skipped"
                        % (n1, n2, n3, ",".join(map(str, depths)) or "-",
                           chain, n4, offpath))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--curves", type=int, default=3)
    ap.add_argument("--pairs", type=int, default=3)
    ap.add_argument("--chain", type=int, default=8)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args(argv)

    fams, excluded = D.discover_families()
    proj = [f for f in fams if getattr(f, "coords", "affine") == "projective"]

    print("projcheck: %d families discovered, %d projective\n"
          % (len(fams), len(proj)))
    rep = Report()

    if not proj:
        # NOT a pass. This repository's own rule is that a gate producing no
        # comparisons fails rather than reporting green -- `driver.py` fails a
        # selected family that yields nothing, for exactly this reason. A gate
        # that passes because it had nothing to do is the failure mode of
        # `test_all.sh` before PR1 and of `opcount.count_family`'s silent empty.
        print("  NOTHING TO CHECK: no family declares '//Coordinates: projective'.")
        print("  Reported as a FAILURE, not a pass. A gate that goes green because")
        print("  it had nothing to do is the test_all.sh failure mode from before")
        print("  PR1 and opcount.count_family's silent empty. If this fires on a")
        print("  tree that is supposed to have a projective family, discovery is")
        print("  the thing to look at -- start with driver.coords_declared and the")
        print("  directory/banner cross-check in discover_families.")
        return 1

    for fam in proj:
        check_family(rep, fam, args.curves, args.pairs, args.chain, args.seed)

    print()
    if rep.failures:
        print("  FAILED: %d of %d checks" % (len(rep.failures), rep.checks))
        return 1
    print("  PASS: %d checks, %d skipped" % (rep.checks, len(rep.skips)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
