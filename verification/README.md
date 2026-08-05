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
python3 driver.py                   # do the formulas agree with the reference?

python3 driver.py --list            # every family, and the domain derived for it
python3 driver.py --model ramified --genus 3 --class nch2
python3 driver.py --curves 30 --pairs 16 --seed 23 --show-all   # the long run
python3 selftest.py --list          # what each section checks
```

Both exit 0 only on success.

**`driver.py` with no arguments will exit 1**, and that is correct rather than a
problem: the default coverage floor is 100%, and the three genus-3 split ADD files
have branches that random sampling does not reach at any volume (see Known limits).
It prints exactly which branches, and the comparison result is on the line above:
`0 mismatched` is the number that says the formulas agree. Pass `--min-coverage 50`,
as CI does, to gate on comparisons and coverage collapse rather than on that gap.

Two flags worth knowing:

- `--strict` additionally fails on wrong answers where `D1 == D2`. Today's formulas
  are wrong there, so this fails until PR5 lands. It is how PR5 will be shown to
  have worked.
- `--min-coverage PCT` lowers the coverage floor. CI uses 50 because its volume is
  deliberately small. It never hides anything: every unexercised branch is listed on
  every run either way.

## What is here

| file | |
|---|---|
| `ff.py`, `poly.py` | finite fields and univariate polynomials |
| `reference.py` | the oracle: Cantor composition and reduction for both models, plus balanced arithmetic in both reduced bases |
| `curves.py` | curve and divisor generation, and the empirical filter that decides which curves are usable |
| `_parser.py` | expression parsing for the `.mag` subset: calls, indexing, sequence and tuple literals, full precedence |
| `maginterp.py` | executes `.mag` function bodies. `python3 maginterp.py` reports parse coverage |
| `driver.py` | the differential test, with per-branch coverage |
| `selftest.py` | checks the framework itself, eight sections |

## Current state

Measured with `driver.py --curves 30 --pairs 16`:

| | |
|---|---|
| families covered | **14** — ramified and split, genus 2 and 3, both reduced bases |
| operations compared | **674,528** |
| wrong on the formulas' documented domains | **0** |
| branch coverage | **86.9%** overall; **100% on all nine ramified files** |
| `selftest.py` | 8 sections, 8 passing |
| parse coverage | 240 of 246 functions |

The 6 functions not interpreted are `Random*Curve` generators, which are not formulas
— `curves.py` generates curves instead.

## Two things it finds that no Magma tester in this repository can

Every Magma tester here either guards `if D1 ne D2` or runs one constructed case per
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

- **The three genus-3 split ADD files plateau near 83%.** They carry 350 labelled
  branches each. Volume helps up to a point — 5 curves to 30 moved one file from 40%
  to 81% — and then stops. The rest need *constructed* cases, one per branch, which
  is what this repository's own whitebox generators do. Closing it means adding that
  mechanism, not turning up a dial.
- **The infinite-place root choice is verified self-consistent, not verified against
  Magma.** The split `Precompute` functions take the value at infinity from
  `Factorization(x² + h·x − f)[2][1]`, "the second solution from the factorization
  given by magma". Magma's factor ordering cannot be recovered by reading the source,
  so both orderings were run against the reference and the agreeing one adopted — 31
  of 32 against 2 of 32, and the two are not interchangeable because swapping them
  exchanges the reduced bases. That establishes internal consistency. Confirming it
  matches Magma needs a Magma run.
- **`g2/timings/` and `g3/timings/` are excluded**, and named as excluded on every
  `--list`. They hold an earlier generation of the formulas: the same function names,
  but every body differs, with a different `ccs` layout, tuple returns and opposite
  signs on some terms. They are not the formulas of record.
- **Two `selftest.py` sections need artefacts from outside this repository** — the
  prior audit's harness and stored repros. They report as SKIP when absent, never as
  passing.

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
