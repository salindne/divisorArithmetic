# divisorArithmetic

Magma explicit formulas for divisor class arithmetic on hyperelliptic curves, with the testing, timing
and table-generation machinery behind them.

Sebastian Lindner. Companion code to *Explicit Formulas for Hyperelliptic Curve Arithmetic* (University
of Calgary, 2020), built as `ucalgary_2020_lindner_sebastian.pdf` in this directory.

**Last updated:** 2026-08-07.

| model | genus 2 | genus 3 |
|---|---|---|
| ramified (imaginary), `deg f = 2g+1` | ✅ `arb`, `nch2`, `ch2` | ⚠️ `arb`, `nch2` only, see [Status](#status) |
| balanced split (real), `deg f = 2g+2` | ✅ `arb`, `nch2`, `ch2` | ✅ `arb`, `nch2`, `ch2` |

Also here: generic-genus Cantor and NUCOMP reference implementations, timing experiments against prior
art, a LaTeX operation-count table generator, a whitebox test-case generator, and a Rust port in a
submodule.

Throughout, "balanced split" without qualification means the basis each genus actually uses: positive
reduced at genus 2, negative reduced at genus 3. See [Reduced basis](#reduced-basis).

---

## Status

**Formulas.** All shipped formula files are covered by the suite in [Testing](#testing).

**Whitebox coverage**, one constructed case per computation path:

| family | cases |
|---|---|
| genus 2 ramified, each of `arb`/`nch2`/`ch2` | 22 |
| genus 2 balanced split, each basis, each of `arb`/`nch2`/`ch2` | 77 |
| genus 3 balanced split, `arb` and `nch2` | 405 |
| genus 3 balanced split, `ch2` | **0, none exists** |
| genus 3 ramified, `arb` and `nch2` | **0, none exists yet** |

The `ch2` genus-3 split family has 405 labelled branches and no whitebox tester. It is covered only by
random testing, and its `test_all.sh` invocation is commented out because the file was never produced.

Genus-3 ramified has no whitebox testers either. Its two random testers were imported from upstream
along with the formulas and are transitional: both guard addition with `if D1 ne D2`, so neither can
exercise `ADD(D, D)`, and `Random(Jac)` almost always yields degree 3, so low-degree branches are barely
covered. Purpose-built testers replace them later.

Whitebox testers instrument ADD and DBL branches only. UTL branches are not instrumented: all eight
split testers set `UTL_DEBUG := false`.

**The full suite passes:** 26 testers, 0 failures, 2 deliberate skips, about 40 minutes, via
[tools/magma-docker/](tools/magma-docker/). With a stock emulator only the six genus-2 ramified testers
load, for reasons
that are not obvious. See [Running Magma](#running-magma).

**Not currently runnable:**

- `latexTables/latexConverter.py` crashes on startup, its input paths being stale, so the committed
  `.tex` tables cannot be regenerated. See [ERRATA.md](ERRATA.md).

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

That runs 26 testers in about 40 minutes and exits 0. The two genus-3 ramified whitebox gaps are reported as skips; see
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
| [Thesis/](Thesis/) | thesis LaTeX sources, see [Thesis](#thesis) |
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
| `nch2` | characteristic not 2, so `h = 0` |
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

runs 26 testers across genus 2 and genus 3.

**Whitebox testers** compute one computer-generated divisor operation per computation path and assert
the result against the reference implementation. Case counts are in [Status](#status).

**Random testers** compute random divisor additions and doublings over a fixed, enumerated list of small
fields. The field list is not random; the curves and divisors drawn on each are. Volumes differ by
family:

| tester | divisors | curves per trial |
|---|---|---|
| genus 2, all families | 2500 or 5000 | 1 |
| genus 3 split `arb` | 100 | 10 |
| genus 3 split `nch2` | 500 | 3 |
| genus 3 split `ch2` | 1000 | 5 |
| genus 3 ramified `arb` | 100 | 10 trials |
| genus 3 ramified `nch2` | 500 | 5 trials |

**Not run by `test_all.sh`:** the `ch2` genus-3 whitebox tester, which does not exist and whose
invocation is commented out; [generic/reduced_basis_tester.mag](generic/reduced_basis_tester.mag);
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

[latexTables/latexConverter.py](latexTables/latexConverter.py) parses the formula files, counts
multiplications, squarings, additions and constant-multiplications per computation path, and emits the
LaTeX tables used in the thesis. It reads two annotation directives from each formula file: `//Constant:`
naming the curve constants, so products with them count as C rather than M, and
`//startIGNORE` / `//endIGNORE` marking blocks excluded from counting, used for the polynomial-level
reference code kept beside each formula.

The script does not currently run: its input paths are stale and its output calls are commented out, so
the committed `.tex` files cannot be reproduced. Several counting faults are also known. Both are in
[ERRATA.md](ERRATA.md).

How the genus-3 ramified counts compare to the published literature — with every prior source's curve
assumptions and the normalisation arithmetic stated — is in [RELATED_WORK.md](RELATED_WORK.md).

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

`ucalgary_2020_lindner_sebastian.pdf` at the repository root is the built document.

[Thesis/](Thesis/) holds the LaTeX sources, `frontmatter.tex`, `chapter1.tex` through `chapter7.tex` and
`appendix.tex`, but not the master document that includes them. No `.tex` file here has a
`\documentclass`, so the thesis cannot be rebuilt from this directory as it stands.

---

## Known gaps and roadmap

- **Genus 3 ramified is `arb` and `nch2` only.** The `ch2` specialisation, and an `nch2` doubling, are
  still to be derived; `nch2` currently borrows the `arb` doubling and so pays for h-terms on every
  double.
- **No whitebox tester for `ch2` genus 3 split**, 405 branches covered by random testing only. The
  generator that would produce it is broken.
- **No whitebox testers for genus 3 ramified.** Its two random testers are transitional imports.
- **No positive-reduced basis at genus 3.**
- **A Python verification framework is planned**, so the formulas can be checked without Magma and
  therefore in CI, which a licensed tool can never do. Until then, defects found are recorded in
  [ERRATA.md](ERRATA.md) rather than fixed until an oracle can see the fix. The verification
  framework is that oracle now -- the `ADD(D, D)` dispatch and E1's closure went through it --
  and the remaining entries wait on the tooling their own text names.

---

## Licence and citation

Code here is MIT licensed, see [LICENSE](LICENSE). The licence covers the code only.
`ucalgary_2020_lindner_sebastian.pdf` and the university thesis class and templates under
[Thesis/](Thesis/) are not covered and retain their own terms.

To cite:

> S. Lindner. *Explicit Formulas for Hyperelliptic Curve Arithmetic.* PhD thesis, University of
> Calgary, 2020.
