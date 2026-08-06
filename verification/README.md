# verification

A Magma-free semantic gate for the explicit formulas in this repository.

Magma is commercial software distributed as a licensed tarball. It cannot run on a
hosted CI runner, and it exits 0 even when an assertion fails, so it could not gate
on exit status even on a self-hosted one. Everything else in `.github/workflows/`
is a static check by construction. This directory is the only thing that can verify
a *formula* automatically.

It works by running the real `.mag` source through an interpreter and comparing it
against an independent implementation of the group law. **No formula is transcribed
into Python**, so there is nothing for a transcription to get wrong and nothing to
drift when a formula changes.

Pure standard library. No install step, no lockfile, no dependency to break.

## Running it

```sh
cd verification

python3 selftest.py                 # is the framework trustworthy?
python3 whitebox.py                 # do the formulas agree, on every path?

python3 whitebox.py --list          # which testers exist, and what is harvested
python3 whitebox.py --harvest       # rebuild cases for families with no tester
python3 driver.py                   # random differential testing, not in CI
python3 driver.py --curves 30 --pairs 16 --seed 23 --show-all   # the long run
python3 selftest.py --list          # what each section checks
```

**`whitebox.py` is the gate.** It replays 1,802 frozen cases, one per computation path,
and is deterministic: same inputs, same branches, every run. `driver.py` generates
random inputs instead, which is a different and complementary job -- see below.

### Where the cases came from: found by search, then frozen

Worth stating plainly, because "constructed" invites the wrong reading. Nobody designed
these inputs. `whitebox/genFiles/*_WB_gen.mag` loops over random curves and divisor
pairs, prints a block for each operation whose result agrees with Magma's own Cantor
arithmetic, and lets the formula's own `ADD_DEBUG`/`DBL_DEBUG` label name the branch;
`whitebox/whitebox_auto_NEG.py` keeps the first block for each label until every label
has one. The harvested cases for the families with no tester are the same procedure in
Python.

So a "constructed case" here means **frozen and committed**, in contrast to sampled
afresh each run. Two properties earn it a place in CI -- it is *complete* (every
labelled branch has a case) and *deterministic* (coverage is a fact about the corpus,
not about this run's luck). What it is **not** is an independently designed probe of
each branch: a branch is covered by whatever input the search first landed on.

### Why frozen cases gate CI and random sampling does not

Sampling coverage is coupon-collector. Measured across all fourteen families:

| volume | time | operations | coverage |
|---|---|---|---|
| `--curves 4 --pairs 4` | 37s | 22,384 | 54.1% |
| `--curves 16 --pairs 10` | 3.4 min | 224,498 | 76.8% |
| `--curves 30 --pairs 16` | ~14 min | 674,528 | 86.9% |

It stalls near 87%, so a coverage floor over sampled runs would either be met
trivially or fail honest runs for a reason unrelated to correctness. The frozen corpus
reaches every branch in two seconds, every time, so coverage becomes a gate worth
having.

**Both still matter, for different things.** A frozen corpus gives one input per
branch, which cannot catch a guard too narrow for a sub-case *within* the branch —
errata E1 exactly. The evidence is in this repository: the whitebox testers cover
405/405 branches, pass, and found neither E1 nor `ADD(D, D)`; exhaustive enumeration
found both. So `driver.py` keeps that job, at volume, locally and before a release —
just not in per-PR CI, where 37 seconds of sampling proves neither thing.

`driver.py` flags worth knowing:

- `--strict` additionally fails on wrong answers where `D1 == D2`. Today's formulas
  are wrong there, so this fails until PR5 lands. It is how PR5 will be shown to
  have worked.
- `--min-coverage PCT` turns coverage into a gate, default 0 (report only).
- A selected family producing **no comparisons** always fails, deterministically:
  "nothing failed" must not be reachable by testing nothing.

## What is here

| file | |
|---|---|
| `ff.py`, `poly.py` | finite fields and univariate polynomials |
| `reference.py` | the oracle: Cantor composition and reduction for both models, plus balanced arithmetic in both reduced bases |
| `curves.py` | curve and divisor generation, and the empirical filter that decides which curves are usable |
| `_parser.py` | expression parsing for the `.mag` subset: calls, indexing, sequence and tuple literals, full precedence |
| `maginterp.py` | executes `.mag` function bodies. `python3 maginterp.py` reports parse coverage |
| `whitebox.py` | replays the frozen cases; **this is what CI gates on** |
| `harvested_cases.json` | frozen cases for every branch no Magma tester reaches: the two genus-3 ramified families, which have no tester, plus the tail of genus-3 split `ch2`, whose tester's own search missed 58 of 413 |
| `coverage_baseline.json` | the branches exempt from coverage, **as a named label set with a reason each** — everything else must be covered, so a newly added branch fails by default and branches cannot be traded one-for-one. Also pins the three known errata-E2 arity anomalies by case identity, so a new one fails while the known ones stay reported-not-fatal until PR5 |
| `driver.py` | random differential testing, with per-branch coverage; not in CI |
| `selftest.py` | checks the framework itself, ten sections |

## Current state

Measured with `driver.py --curves 30 --pairs 16`:

| | |
|---|---|
| families covered | **14** — ramified and split, genus 2 and 3, both reduced bases |
| operations compared | **674,528** |
| wrong on the formulas' documented domains | **0** |
| branch coverage | **86.9%** overall; **100% on all nine ramified files** |
| `selftest.py` | 10 sections, 10 passing |
| parse coverage | 240 of 246 functions |

The 6 functions not interpreted are `Random*Curve` generators, which are not formulas
— `curves.py` generates curves instead.

## Two things it finds that no Magma tester in this repository can

Every Magma tester here either guards `if D1 ne D2` or holds one frozen case per
branch, so neither can see the `D1 = D2` region at all. The driver reports it
separately from failures on the documented domain:

- **64,883 wrong sums where `D1 == D2`**, in the run above. The thesis assumes `D1 ≠ D2` and no file
  checks it. A double-and-add ladder hits this. PR5 adds the dispatch that fixes it.
- **Divisions by zero in the same region** — errata E1, where the guard
  `IsZero(dw20) and IsZero(dw21)` is too narrow, so `dw21 = 0` with `dw20` nonzero
  reaches `dw21^-1`.

Both are expected and are not counted as failures today. `--strict` makes them fail.

## Design decisions worth knowing before changing anything

**Nothing family-specific is tabulated. It is read out of the source.** Which curves
a family's formulas are valid for, how its dispatcher is called, and what its
`ccs` constants mean are all derived from the family's own `.mag` files. A table
would keep passing after the source changed.

**"A coefficient no formula reads must be zero" is false**, and assuming it produced
a wrong answer twice. No genus-2 ramified file reads `f0`, `arb` included, because
Cantor reduction needs only the quotient and the low coefficients land in the
remainder. Domains are derived by *contrast* against the `arb` family of the same
model and genus, which is the one valid on arbitrary curves: what the general family
reads and a specialisation does not is what that specialisation assumed away.

**Branch coverage is not optional output.** Several defects in this repository
survived because a tester never reached the branch. An unexercised branch is
reported every run and, by default, fails it.

**Nothing is capped silently.** A family that cannot be loaded, a field with no
suitable curve, a directory excluded from discovery: all are printed with the
reason. A truncated run that prints "all passed" is worse than one that fails.

**Curve acceptance is empirical, and the textbook criterion is used only to reject.**
A candidate curve is kept only if `reference.py` forms a group on it. The
singularity criterion additionally rejects, never accepts, because the two are
individually incomplete: the criterion detects singularity over the algebraic
closure, while the empirical filter samples finitely and can miss even an F-rational
singular point. Rejecting on both is the safe direction — it narrows the tested
domain rather than admitting a curve the group law fails on.

## Known limits

- **`ch2_splitG3_ADD` sits at 339 of 350 branches.** The eleven that remain are each
  guarded by a nested `IsZero` on an intermediate value (`z2`, `z3`, `z4`, `w2`, `k3`),
  so reaching one needs an algebraic coincidence rather than a different kind of input.
  They are named individually in `coverage_baseline.json`; the reason says *not reached
  by the recorded budget*, which is not the same as unreachable.

  Getting here needed two searches, and the cost difference is the point:

  | source | budget | branches of 405 |
  |---|---|---|
  | Magma generator | 400 trials | 179 |
  | Magma generator | 12,000 trials (**committed tester**) | 347 |
  | Magma generator | ~15,700 trials | 353 |
  | `--harvest` on top of the 347 | `--harvest-curves 160 --harvest-pairs 40`, ~10 min | **401 of 413** |

  The generator's last 14,750 blocks bought six branches; the harvester bought
  forty-seven in ten minutes, because it varies degree combinations and pair modes
  deliberately while the generator draws two `RandomDivisorAB` divisors. So the tester
  supplies the bulk and the harvester the tail, and `--harvest` fills whatever no
  extracted case reaches rather than only serving families with no tester at all.

- **Random sampling alone plateaus near 87%**, which is why it is not the gate. The
  three genus-3 split ADD files carry 350 labelled branches each; raising volume moved
  one from 40% to 81% and then stopped. The frozen corpus closes it instead.

- **The infinite-place root is exact wherever a basis polynomial is available, and
  conventional otherwise.** The split `Precompute` functions take the value at infinity
  from `Factorization(x² + h·x − f)[2][1]`, "the second solution from the factorization
  given by magma", and Magma's factor ordering cannot be recovered by reading source.
  Constructed cases supply `V` explicitly, so `y_{g+1}` is its leading coefficient and
  `maginterp.ROOT_PIN` makes the choice exact — no convention involved. Measured, no
  global ordering would have worked: one fails 247 cases, all in characteristic 2, the
  other 332, all over odd primes. `driver.py`'s generated inputs have no supplied `V`,
  so they fall back to `ROOT_CHOICE`, established by running both against the reference.

- **`ff.py`'s extension-field moduli match Magma's**, queried from Magma directly rather
  than assumed. They already agreed for GF(4), GF(8), GF(16), GF(27) and GF(32); GF(9)
  and GF(25) did not, and that reproduced as wrong constructed cases. Anything outside
  `MAGMA_MODULI` still uses the search order, so a new extension field wants checking
  before its cases are trusted.

- **`g2/timings/` and `g3/timings/` are excluded**, and named as excluded on every
  `--list`. They hold an earlier generation of the formulas: the same function names, but
  every body differs, with a different `ccs` layout, tuple returns and opposite signs on
  some terms. They are not the formulas of record; see `ERRATA.md` E7.

- **Two `selftest.py` sections need artefacts from outside this repository** — the prior
  audit's harness and stored repros. They report as SKIP when absent, never as passing.

## Relationship to the Magma testers

They are independent oracles and both are worth having. The Magma testers assert
against Magma's own Jacobian arithmetic; this framework asserts against a
from-scratch Cantor implementation, cross-checked three ways.

They have been run against each other: the full Magma suite passes 25 testers with 0
failures, and the driver reports 0 mismatches on the same families. Agreement is
expected only where both can look, and the one asymmetry is the point — the driver
sees the `D1 = D2` region and no Magma tester can.

See `../README.md` for the repository as a whole and `../ERRATA.md` for the recorded
defects, several of which are reproduced here as required test vectors.
