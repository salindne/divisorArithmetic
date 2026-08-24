# divisorArithmetic

Magma explicit formulas for divisor class arithmetic on hyperelliptic curves, with the testing, timing
and table-generation machinery behind them.

Sebastian Lindner. Companion code to *Explicit Formulas for Hyperelliptic Curve Arithmetic* (University
of Calgary, 2020), built as `ucalgary_2020_lindner_sebastian.pdf` in this directory.

**Last updated:** 2026-08-23.

| model | genus 2 | genus 3 |
|---|---|---|
| ramified (imaginary), `deg f = 2g+1` | ✅ `arb`, `nch2`, `ch2` | ✅ `arb`, `nch2`, `ch2` |
| balanced split (real), `deg f = 2g+2` | ✅ `arb`, `nch2`, `ch2` | ✅ `arb`, `nch2`, `ch2` |

Also here: generic-genus Cantor and NUCOMP reference implementations, a Python verification framework
that runs in CI, timing experiments against prior art, a whitebox test-case generator, a LaTeX
operation-count table generator, and a Rust port in a submodule.

Throughout, "balanced split" without qualification means the basis each genus actually uses: positive
reduced at genus 2, negative reduced at genus 3. See [Reduced basis](#reduced-basis).

---

## Status

**Two independent gates.** Magma runs the full tester suite locally; a pure-standard-library Python
framework in [verification/](verification/) runs in CI, which a licensed tool never can.

| gate | result |
|---|---|
| Magma suite, `./test_all.sh` | **30 testers, 0 failures, 0 skips**, ~4 min |
| frozen case corpus, [verification/whitebox.py](verification/whitebox.py) | **1,886 cases replayed, 1,886 matched** |
| branch coverage | **1,925 of 1,929 labelled branches, 99.8%** |
| differential tester, [verification/driver.py](verification/driver.py) `--strict` | **13,746 operations compared, 0 wrong** |
| framework selftest | **17 sections** |

The 4 uncovered branches are individually exempted with written reasons in
`verification/coverage_baseline.json`; one of them, `ch2_splitG3_ADD`'s `ADD227`, carries a proof that it
is unreachable in characteristic 2.

**Branch coverage by family**, from `python3 verification/whitebox.py`:

| family | branches | covered |
|---|---|---|
| genus 2 ramified, each of `arb`/`nch2`/`ch2` | 22 | 100% |
| genus 2 balanced split, each basis, each of `arb`/`nch2`/`ch2` | 80 | 100% except two `UTL0` |
| genus 3 balanced split, `arb` and `nch2` | 413 | 100% except one `UTL4` |
| genus 3 balanced split, `ch2` | 413 | 349/350 ADD, rest 100% |
| genus 3 ramified, each of `arb`/`nch2` | 37 ADD + 11 DBL | 100% |

**Every family now has a Magma whitebox tester.** Genus-3 ramified was the exception until its two were
generated — 48 constructed cases each, every one asserted against Magma's own Jacobian arithmetic — so
`verification/harvested_cases.json` is now empty and all 1,886 cases are extracted from testers. Its two
*random* testers remain transitional imports, and `Random(Jac)` almost always yields degree 3, so
low-degree branches are thinly sampled there; that is what the whitebox testers exist to cover, by
enumerating the divisor space rather than sampling it.

**One limit of the whitebox gate, worth knowing before trusting it.** Coverage is keyed on
`ADD_DEBUG`/`DBL_DEBUG` label strings, so a branch with no label is invisible to it. That gap used to
include `Deg3ADD`'s generic path in the genus-3 ramified files — the frequent case — where sabotage left
the corpus gate reporting a clean pass; those labels have since been added, and the four remaining
unlabelled returns are dispatcher leaves, deliberately consistent between the two files. `UTL` branches
are instrumented at genus 3 only; the eight genus-2 split testers set `UTL_DEBUG := false`.

**Operation counts.** Every operation costs exactly one inversion, so `I` is omitted below.
"Typical" means the non-degenerate path: trivial gcd, `deg s = 2`, a full-degree result. The
condition differs per operation — coprime input supports for an addition, no ramification
point in the support for a doubling — but the role is the same, and it is the case published
tables price.

Highest-degree typical case per family, `M / S / A / C`:

| family | addition | doubling | source |
|---|---|---|---|
| **g2 ramified** arb | 21 / 2 / 31 / 0 | 22 / 4 / 42 / 2 | measured |
| **g2 ramified** nch2 | 21 / 2 / 23 / 0 | 21 / 5 / 25 / 0 | measured |
| **g2 ramified** ch2 | 20 / 3 / 26 / 0 | 21 / 4 / 24 / 0 | measured |
| **g2 split** arb | 27 / 1 / 37 / 3 | 30 / 2 / 44 / 8 | published |
| **g2 split** nch2 | 26 / 2 / 36 / 0 | 29 / 3 / 39 / 0 | published |
| **g2 split** ch2 | 27 / 1 / 34 / 0 | 29 / 2 / 31 / 0 | published |
| **g3 ramified** arb | **53 / 3 / 71 / 1** | **54 / 4 / 80 / 4** | measured |
| **g3 ramified** nch2 | **53 / 3 / 59 / 0** | **53 / 5 / 61 / 0** | measured |
| **g3 ramified** ch2 | **53 / 3 / 66 / 0** | **51 / 4 / 55 / 2** | measured |
| **g3 split** arb | 65 / 3 / 87 / 12 | 73 / 3 / 101 / 19 | published |
| **g3 split** nch2 | 65 / 3 / 85 / 0 | 72 / 4 / 97 / 0 | published |
| **g3 split** ch2 | 65 / 3 / 80 / 0 | 71 / 4 / 86 / 1 | published |

**Two sources, because only one is reproducible here.** *Measured* rows come from
`python3 verification/opcount.py --family <name>`, which executes the formulas over a real
field and identifies the frequent case by observing which branch is taken. *Published* rows
are read from the thesis — `tab:splitfcosts` and `tab:g3splitfcosts{ADD,DBL}` — because
**the counter cannot measure split families yet** and refuses rather than guessing. Until it
can, no split figure here is independently checked.

**Where both exist, they agree exactly.** The genus-2 ramified rows are measured, and they match
`tab:ramfcosts` cell for cell across **all three** characteristic columns — arbitrary, char != 2
and char = 2 — including the lower-degree rows not shown here. Execution against static counting,
two methods sharing no code, same answer. That agreement is the evidence for trusting the measured
genus-3 ramified figures, which have no published counterpart at all: the thesis deferred genus-3
ramified entirely (`chapter6.tex:15`, "ramified models are developed by another student").

Both genus-3 ramified rows beat the thesis's own split Degree-3 rows on M+S, C and A. And
`nch2` is now cheaper than the `arb` it specialises on every shared operation — equal M+S,
strictly fewer additions — which `verification/selftest.py` asserts rather than assumes, so
the drift that once let the child overtake its parent cannot recur silently. See
[EFFICIENCY_NCH2_G3.md](EFFICIENCY_NCH2_G3.md).

See [Operation-count tables](#operation-count-tables) for the counter of record and the one
known misclassification in it.

**Not currently runnable:** `latexTables/latexConverter.py`, whose input paths are stale. It has been
demoted to a LaTeX renderer — counting moved to `verification/opcount.py` — so the committed `.tex`
tables cannot be regenerated, and nothing else depends on it. See [ERRATA.md](ERRATA.md).

---

## Reduced basis

The split model represents a divisor class with `v` normalized against one of the two polynomials at
infinity: positive reduced uses `Vp`, negative reduced uses `Vn`. Both represent the same class. The
choice dictates the direction of any adjustment step, so it changes the formulas rather than the
mathematics.

**Which basis is used where, and why it differs by genus:**

| | basis | reason |
|---|---|---|
| genus 2 | **positive** reduced | Addition and doubling have equal net cost in either basis, so there is no efficiency argument. Positive reduced matches the basis used by Erickson, Jacobson and Stein (2011), which makes the operation-count comparisons directly readable. |
| genus 3 | **negative** reduced | Negative reduced is genuinely cheaper here. It absorbs one adjustment into the continued-fraction steps of Balanced NUCOMP, removing the need for any further adjustment in the frequent cases, and it lowers the degree of the `k = f - v(v+h)` polynomial through cancellations. |

So the published operation-count tables are positive reduced at genus 2 and negative reduced at genus 3.
This is stated in the thesis at chapter 5 for genus 2 and chapter 6 for genus 3, which contrast the two
explicitly.

**What ships here:** genus 2 has both bases, under
[g2/splitModel/posReduced/](g2/splitModel/posReduced/) and
[g2/splitModel/negReduced/](g2/splitModel/negReduced/). Genus 3 has negative reduced only. There is no
positive-reduced basis at genus 3.

---

## Running Magma

**Magma is required and is not in this repository.** It is commercial, licensed software. Place your
tarball as `magma.tar.xz` at the repository root. It is gitignored, must never be committed, and an
image built from it must never be pushed to any registry.

```sh
docker build -f tools/magma-docker/Dockerfile -t magma-qemufix .
MAGMA=tools/magma-docker/magma.sh ./test_all.sh
```

That runs 30 testers in about four minutes and exits 0, essentially all of it Magma:
3.3 min across 62,654 divisor comparisons. The script used to spend a further ~100 seconds in
decorative inter-family `sleep` calls; those are gone. Every family now has a whitebox tester, so there is nothing
left to skip; see
[Status](#status).

Use [tools/magma-docker/](tools/magma-docker/) rather than a plain `docker build`. On Apple Silicon a
plain image cannot run most of this repository.

### Why the container needs a patched emulator

`magma.exe` is a statically linked 32-bit i386 binary from 2015. Apple Silicon cannot run it natively
and Rosetta translates x86-64 only, so Docker routes it through `qemu-i386`, QEMU's user-mode emulator.
QEMU relocates a mapping whenever the guest passes `MREMAP_MAYMOVE`, including when the guest is
*shrinking* it, where Linux would have kept the address. Magma checks that its blocks stay put, so it
aborts:

```
memi_reduce_block_mmap: block moved
Magma: Internal error
```

With a stock emulator only the six genus-2 ramified testers load; every other tester aborts here. It
presents as a size limit, because whether Magma needs a shrink correlates with function length. That is
why it was long mistaken for the formulas being too large for an old Magma.

[tools/magma-docker/](tools/magma-docker/) builds a `qemu-i386` with a one-line fix, after which the
whole suite passes. Full diagnosis, and the list of approaches that do not work, are in
[tools/magma-docker/README.md](tools/magma-docker/README.md).

---

## Repository layout

| path | contents |
|---|---|
| [g2/ramifiedModel/](g2/ramifiedModel/) | genus 2 ramified formulas, testers, shared utilities |
| [g3/ramifiedModel/](g3/ramifiedModel/) | genus 3 ramified formulas, testers, shared utilities |
| [g2/splitModel/posReduced/](g2/splitModel/posReduced/) | genus 2 balanced split, positive reduced |
| [g2/splitModel/negReduced/](g2/splitModel/negReduced/) | genus 2 balanced split, negative reduced |
| [g3/splitModel/negReduced/](g3/splitModel/negReduced/) | genus 3 balanced split, negative reduced |
| [g2/timings/](g2/timings/) | genus 2 timing experiments, prior-art formulas, results (47 files) |
| [g3/timings/](g3/timings/) | genus 3 timing experiments and results (18 files) |
| [generic/](generic/) | generic-genus Cantor and NUCOMP reference implementations, and timings |
| [whitebox/](whitebox/) | whitebox test-case generator and its outputs |
| [latexTables/](latexTables/) | operation-count table generator and generated `.tex` |
| [Thesis/](Thesis/) | thesis LaTeX sources, corrections applied, see [Thesis](#thesis) |
| [ThesisPublished/](ThesisPublished/) | the same sources frozen as published, never edited, see [FROZEN.md](ThesisPublished/FROZEN.md) |
| [test_all.sh](test_all.sh) | test entrypoint |
| [1024bit_primes.mag](1024bit_primes.mag) | pre-generated 1024-bit primes for the timing experiments |
| [rust/](rust/) | Rust port, a git submodule, see [Rust implementation](#rust-implementation) |
| `ucalgary_2020_lindner_sebastian.pdf` | the built thesis |

Formula files live in a `g2Formulas/` or `g3Formulas/` subdirectory of each model directory, for example
[g2/ramifiedModel/g2Formulas/](g2/ramifiedModel/g2Formulas/) and
[g3/splitModel/negReduced/g3Formulas/](g3/splitModel/negReduced/g3Formulas/). Testers sit one level up.

---

## Naming convention

```
{arb,nch2,ch2}_{ramified,split}G{2,3}_{ADD,DBL,UTL}.mag
```

| token | meaning |
|---|---|
| `arb` | arbitrary characteristic, no assumption on the field |
| `nch2` | odd characteristic, so `h = 0`, plus the `f` depression its genus allows: genus 2 `f4 = 0` (needs char != 5), genus 3 `f6 = 0` (needs char != 7) |
| `ch2` | characteristic 2 |
| `ADD` / `DBL` | divisor addition / doubling |
| `UTL` | utilities, split model only, for the two places at infinity |

Tester filenames are inconsistently cased, historically: genus 2 uses `*_whiteBox_tester.mag` with a
capital B, genus 3 uses `*_whitebox_tester.mag`.

**`Deg<i><j>ADD` means different things in different families, so check before comparing.** Function
names give the degrees of the two input divisors, but the two families disagree on whether the digits
describe the parameter order:

| | example | order the parameters arrive in |
|---|---|---|
| genus 2 ramified | `Deg12ADD(up0,vp0, u1,u0,v1,v0, …)` | **smaller** degree first, so the digits are positional |
| genus 3, both models | `Deg23ADD(u12,u11,u10,…, u21,u20,…)` | **larger** degree first, so the digits are merely sorted |

Genus 3 ramified follows genus 3 split, which is why it was safe to rename its imported
`Deg32ADD` to `Deg23ADD` without touching parameters.

The intended resolution is to align genus 3 to genus 2, so that the smaller-degree divisor arrives
first everywhere and every name is positional. That is parameter reordering in both genus-3 models
rather than any renaming, since the names are already correct, and it is deferred until there is an
oracle that samples mixed-degree inputs thoroughly enough to catch a swapped pair.

Same-degree cases are spelled with a single digit everywhere except one: `Deg1ADD` for 1+1 and
`Deg3ADD` for 3+3, but `Deg22ADD` for 2+2 in both genus-3 models. It is the lone holdout, and purely
cosmetic, since a same-degree case has no operand order to confuse. Collapsing it to `Deg2ADD` is queued
with the reordering above. Doubling is already uniform: `Deg1DBL`, `Deg2DBL`, `Deg3DBL`.

**The reference implementation is duplicated.** `reduced_basis_arithmetic.mag` exists in 8 copies across
the tree in 5 byte-distinct versions, and genus 3 additionally has a separate 730-line
`poly_balanced_arithmetic.mag`. The copy under
[g2/splitModel/negReduced/](g2/splitModel/negReduced/reduced_basis_arithmetic.mag) is what the genus-2
testers assert against. Which copy is authoritative for a given consumer is currently implicit, so check
before trusting any cross-comparison.

---

## Testing

```sh
./test_all.sh
```

runs 30 testers across genus 2 and genus 3.

**Whitebox testers** compute one search-found divisor operation per computation path and assert the
result against the reference implementation. Coverage is in [Status](#status). The cases are harvested by
coverage-guided search, not hand-designed; what earns them a place in CI is that they are complete and
deterministic.

**The Python framework** in [verification/](verification/) is what runs in CI, since Magma is licensed
and cannot. It interprets the real `.mag` source, so there is no transcription to drift:

```sh
python3 verification/whitebox.py                                  # frozen corpus, the CI gate
python3 verification/driver.py --curves 3 --pairs 3 --strict      # differential vs an independent reference
python3 verification/opcount.py --family ramified/g3/arb          # operation counts by execution
python3 verification/selftest.py                                  # the framework's own tests
```

It is pure standard library — no install step, no lockfile.

**Random testers** compute random divisor additions and doublings over a fixed, enumerated list of small
fields. The field list is not random; the curves and divisors drawn on each are. **Exactly one curve is
drawn per field, in every tester**, so the field list is the characteristic coverage — which is why the
volumes below were reduced and the field lists were not. The two genus-3 ramified testers used to be the
exception, nesting a ten- and five-curve loop inside the field loop; they now match the other twelve,
where `trial` is a print counter and `TRIALS = #FIELDS`.

| tester | divisors per curve | was |
|---|---|---|
| genus 2 ramified, all three | 500 | 2500 |
| genus 2 split, all six | 250 | 2500 or 5000 |
| genus 3 ramified, both | 50 | 100, 500 |
| genus 3 split, all three | 25 | 100, 500, 1000 |

**Why these are enough, and what they are not for.** The rare branches are proved by the *whitebox*
testers, deterministically: one constructed case per branch label, every one asserted against Magma's own
Jacobian arithmetic, at about a second per tester. Leaving a degenerate case to a one-in-q² dice roll here
was never how it was actually covered. What the random testers uniquely add is *within-branch* input
variation against fresh inputs — and for that, volume was already far past the point of diminishing
return: the one defect of that class this project ever found (E1) took **3,240,293 enumerated pairs**, so
2500 per curve was three orders of magnitude short of catching it and 500 is no further away. The
reduction cost wall-clock, not defect-finding power.

**Replaying a failure.** Magma does not seed deterministically — two runs of the same tester draw
different curves — so each of these testers now prints its seed and the command to reuse it:

```
// - Random seed 1804224007, step 0. Replay this run with RND_SEED=1804224007
```

`RND_SEED` is forwarded into the container unconditionally by
[tools/magma-docker/magma.sh](tools/magma-docker/magma.sh), so that line works as printed.

**Not run by `test_all.sh`:**
[generic/reduced_basis_tester.mag](generic/reduced_basis_tester.mag);
[generic/arbitrary/reduced_basis_tester.mag](generic/arbitrary/reduced_basis_tester.mag); and everything
under [g2/timings/](g2/timings/) and [g3/timings/](g3/timings/).

---

## Generic-genus algorithms

Reference implementations for arbitrary genus, used to validate the explicit formulas and to measure
what the explicit formulas buy.

- [generic/](generic/) is Cantor composition and reduction plus NUCOMP and NUDUPL for `h = 0`,
  characteristic not 2. 25 top-level routines.
- [generic/arbitrary/](generic/arbitrary/) is the same for arbitrary characteristic, with 33 top-level
  routines, 8 more than the `h = 0` version.

Each has ten timing drivers, `timings_2bit.mag` through `timings_1024bit.mag`:

```sh
magma timings_32bit.mag
```

[generic/README.md](generic/README.md) has the routine index, and identifies which of the several
results directories corresponds to which run.

---

## Whitebox case generation

[whitebox/whitebox_auto_NEG.py](whitebox/whitebox_auto_NEG.py) drives the case generators in
[whitebox/genFiles/](whitebox/genFiles/) to emit a tester. Run it from the `whitebox/` directory: the
generators' `load` paths are relative to that, not to `genFiles/`.

```
cd whitebox
./whitebox_auto_NEG.py ch2 split 3 --trials 12000 --out ../g3/splitModel/negReduced/x.mag
./whitebox_auto_NEG.py ch2 split 3 --from-log logs/ch2_splitG3_log.txt   # reparse, no Magma
```

**`--from-log` is the reliable second step, not a fallback.** The generator's search loop is
`while true`: it keeps emitting long after every branch is covered, so the run does not end on its own
and the log grows without bound — a genus-2 ramified regeneration reached 42 MB, against 44K–616K for
the committed logs. Killing the container is not a substitute for finishing, because the runner sees the
non-zero exit (`magma exited 137`) and refuses to write a tester. Let it run until the log contains
every label, stop it, then re-parse the log with `--from-log`, which writes the tester without Magma.
Check coverage first, since the log is the only thing that carries it:

```
grep -oE '^(ADD|DBL)[0-9]+$' logs/<family>_log.txt | sort -u | wc -l
```

Regeneration logs for the genus-2 ramified families are gitignored for size.

**How a case is chosen.** A generator loops over random curves and divisor pairs and prints a block for
each operation whose result agrees with Magma's own Cantor arithmetic, letting the formula's own
`ADD_DEBUG`/`DBL_DEBUG` label name the branch. The runner keeps the first block per label. So a whitebox
tester is the frozen output of a **coverage-guided random search** — complete and replayable, but not a
set of hand-designed probes.

Because coverage is a search, a tester can fall short of its own branch count: the genus-3 split `ch2`
family reaches 347 of 413 labels at 12,000 trials, with the remainder guarded by nested `IsZero`
coincidences that are rare rather than impossible. `verification/whitebox.py --harvest` fills the
difference.

Limitations:

- `--trials` bounds the search. An unreached branch is reported, and writing a tester with a gap needs
  `--allow-incomplete`.
- [whitebox/testerFiles/arb_splitG3_whiteBox_tester.mag](whitebox/testerFiles/arb_splitG3_whiteBox_tester.mag)
  is a 2-of-405-case fragment from an aborted run, not a usable tester. The real 405-case genus-3
  testers are in [g3/splitModel/negReduced/](g3/splitModel/negReduced/).
- `whitebox/logs/` holds the residue of a pre-2025 orchestrator run. Two of the three files begin
  mid-polynomial: that generation reset the log with `truncate(0)` while Magma still held it open at its
  own write offset. The runner now writes to a separate file and never truncates.
- [whitebox/logs/](whitebox/logs/) holds output from aborted runs.

---

## Operation-count tables

**[verification/opcount.py](verification/opcount.py) is the counter of record.** It measures by running
the formulas over a real finite field, per branch, and identifies the frequent case by *observing* which
branch is taken rather than inferring it from the source. It reports inversions, which the older static
counter does not count at all. Every contributing execution is cross-checked against an independent
Cantor implementation, so an input outside the formulas' domain shows up as a mismatch rather than as a
plausible wrong count.

Conventions come from each formula file's own directives, never from a table here: `//Constant:` names
the curve coefficients, so products with them count C rather than M; `//Ignore:` names coefficients whose
products are free; `//startIGNORE` / `//endIGNORE` bracket the polynomial-level reference code kept
beside each formula. Division by 2 counts as an addition, per the thesis.

**One known misclassification, `ERRATA.md` E13.** A product whose factor is a *composite* over curve
coefficients — `2*f6*u1_0` — is charged M although `2*f6` is fixed per curve. Six live sites, all in the genus-3
ramified arbitrary doubling, one of them on a frequent path. Totals are right; the M/C split is not.

[latexTables/latexConverter.py](latexTables/latexConverter.py) is the older static counter, which scanned
the source as text and emitted the thesis's LaTeX tables. The two agreed on all 208 published own-work
quadruples — two methods sharing no code — but it is now **demoted to a renderer**: it does not run today
(stale input paths), several counting faults are recorded in [ERRATA.md](ERRATA.md), and nothing depends
on it except regenerating `.tex`.

How the genus-3 ramified counts compare to the published literature — with every prior source's curve
assumptions and the normalisation arithmetic stated — is in [RELATED_WORK.md](RELATED_WORK.md).

Efficiency findings for the arbitrary-characteristic genus-3 ramified formulas, each located,
measured and adversarially verified, are in [EFFICIENCY_ARB_G3.md](EFFICIENCY_ARB_G3.md). That
document changes no formula; it is the input to the implementation work.

What this project contributes beyond the published thesis — every correction, completion and result,
with the argument for why it is right and the measurement that establishes it — is in
[NEW_WORK.md](NEW_WORK.md). It is written to be lifted into the next publication, and it is kept
current as the work proceeds rather than reconstructed afterwards. Its Part I gives one account of the
curve normal forms, uniform in the genus, producing all six ramified forms — and all six now have a
formula banner declaring exactly that form, the genus-3 characteristic-2 file having been the last to
exist.
[verification/normal_form.py](verification/normal_form.py) reproduces every claim in it.

---

## Timing experiments

[g2/timings/](g2/timings/) and [g3/timings/](g3/timings/) hold the drivers, the prior-art formulas
compared against, the raw results and the plots.

| prior art | genus |
|---|---|
| [lange_2005.mag](g2/timings/formulas/previousBest/lange_2005.mag), [inf_2010.mag](g2/timings/formulas/previousBest/inf_2010.mag), [geo_2011.mag](g2/timings/formulas/previousBest/geo_2011.mag), [geo_noTrade_2011.mag](g2/timings/formulas/previousBest/geo_noTrade_2011.mag) | 2 |
| [rad_2019.mag](g3/timings/formulas/previousBest/rad_2019.mag), [sutherland_2019.mag](g3/timings/formulas/previousBest/sutherland_2019.mag) | 3 |

The formula copies under `timings/*/ramFormulas/` and `timings/*/splitFormulas/` are deliberate variants
rather than duplicates: function names carry a `_RAM` or split suffix so both models can coexist in one
Magma session, returns are tuples, and debug output is commented out to keep I/O out of the timed loop.
They are hand-maintained and can drift from the canonical formulas.

`g2/timings/arbitrary_implementation/` is a superseded fork that no longer runs.

A defect affecting the published negative-reduced generic timings is recorded in [ERRATA.md](ERRATA.md).

---

## Rust implementation

[rust/](rust/) is a git submodule pointing at
[github.com/salindne/divisor-arithmetic](https://github.com/salindne/divisor-arithmetic), a Rust port
with its own tests and CI. Nothing in this repository builds or tests it.

```sh
git submodule update --init --recursive
```

The recorded pointer may lag the submodule's `main`.

---

## Thesis

`ucalgary_2020_lindner_sebastian.pdf` at the repository root is the built document, as published and
never modified.

The source exists in two copies, deliberately:

| | |
|---|---|
| [ThesisPublished/](ThesisPublished/) | **frozen.** Byte-exact as submitted; never edited |
| [Thesis/](Thesis/) | **evolving.** Corrections land here, each logged in [Thesis/ERRATA.md](Thesis/ERRATA.md) |

Both hold `frontmatter.tex`, `chapter1.tex` through `chapter7.tex` and `appendix.tex`, but not the
master document that includes them. No `.tex` file has a `\documentclass`, so the thesis cannot be
rebuilt from either directory as it stands.

Corrections are made only where they are justified, and
[Thesis/ERRATA.md](Thesis/ERRATA.md) says for each one whether it was verified by measurement or
rests on a structural argument. `diff -r ThesisPublished Thesis` shows the current divergence.

---

## Known gaps and roadmap

- **Genus 3 ramified is `arb` and `nch2` only.** The `ch2` specialisation is still to be derived, so
  five of the six `{arb, nch2, ch2} x {ADD, DBL}` cells exist. The `nch2` doubling no longer borrows
  the `arb` one: it is derived at `h = 0` and `f6 = 0`, which removed 26 additions and every constant
  multiplication from the degree-2 case.
- ~~**No whitebox testers for genus 3 ramified.**~~ **Closed.** Both families now have
  one, generated by `whitebox/genFiles/*_ramifiedG3_WB_gen.mag`: 48 constructed cases
  each, one per branch label, every case asserted against Magma's own Jacobian
  arithmetic. Coverage of those four formula files is 100% from *extracted* cases, so
  the harvested corpus that stood in for them is now empty -- the machinery stays for
  the next family derived before its tester exists.
- **`verification/opcount.py` cannot measure split families**, so no split-model operation count can be
  quoted from it yet. The split figures in [RELATED_WORK.md](RELATED_WORK.md) come from an external
  harness.
- **No positive-reduced basis at genus 3.**
- **Errata are recorded before they are fixed, deliberately.** A defect goes into
  [ERRATA.md](ERRATA.md) with a reproducer and waits for a gate that can see the fix. Entries whose
  reproducer already runs get fixed; the rest name the tooling they wait on.

---

## Licence and citation

Code here is MIT licensed, see [LICENSE](LICENSE). The licence covers the code only.
`ucalgary_2020_lindner_sebastian.pdf` and the university thesis class and templates under
[Thesis/](Thesis/) are not covered and retain their own terms.

To cite:

> S. Lindner. *Explicit Formulas for Hyperelliptic Curve Arithmetic.* PhD thesis, University of
> Calgary, 2020.
