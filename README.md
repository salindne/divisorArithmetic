# divisorArithmetic

Explicit formulas for divisor class arithmetic on hyperelliptic curves, written in Magma, together
with the testing, timing and table-generation machinery behind them.

Sebastian Lindner. Companion code to *Explicit Formulas for Hyperelliptic Curve Arithmetic*
(University of Calgary, 2020) — `ucalgary_2020_lindner_sebastian.pdf` in this directory.

**Last updated:** 2026-08-03.

Coverage:

| model | genus 2 | genus 3 |
|---|---|---|
| ramified (imaginary), `deg f = 2g+1` | ✅ `arb`, `nch2`, `ch2` | ⛔ not present — see [Status](#status) |
| balanced split (real), `deg f = 2g+2`, negReduced basis | ✅ `arb`, `nch2`, `ch2` | ✅ `arb`, `nch2`, `ch2` |
| balanced split, posReduced basis | ✅ `arb`, `nch2`, `ch2` | ⛔ not present |

Plus generic-genus Cantor/NUCOMP reference implementations, timing experiments against prior art, a
LaTeX operation-count table generator, a whitebox test-case generator, and a Rust port in a submodule.

---

## Status

An honest account of what works, as of the date above.

**Formulas.** All shipped formula files are believed correct on their stated domains and are covered by
the test suite described in [Testing](#testing).

**Test coverage.** Whitebox coverage — one deliberately constructed case per computation path — exists
for:

| family | cases |
|---|---|
| genus 2 ramified, each of `arb`/`nch2`/`ch2` | 22 |
| genus 2 split, each basis × each of `arb`/`nch2`/`ch2` | 77 |
| genus 3 split negReduced, `arb` and `nch2` | 405 |
| genus 3 split negReduced, `ch2` | **0 — none exists** |

The `ch2` genus-3 split family has 405 labelled branches and **no whitebox tester at all**; it is
covered only by random testing. Its invocation in `test_all.sh` is commented out because the file was
never produced. See [Known gaps](#known-gaps-and-roadmap).

Whitebox testers instrument the ADD and DBL branches only. **UTL branches are not instrumented** —
all eight split testers set `UTL_DEBUG := false`.

**Tooling that does not currently run:**

- `latexTables/latexConverter.py` — crashes on startup; its input paths are stale. The committed
  `.tex` tables cannot be regenerated. See [ERRATA.md](ERRATA.md).
- On the local Docker Magma setup, only 6 of the 23 testers load at all — the genus-2 ramified family.
  The other 17 abort inside Magma's allocator before running anything. Cause not isolated; see
  [Most of the suite does not load](#most-of-the-suite-does-not-load-on-the-setup-described-above).
- `whitebox/whitebox_auto_NEG.py` — only the `nch2` genus-2 split configuration is reachable; the
  ramified and posReduced paths are structurally unreachable, and the three genus-3 case generators
  have stale load paths.

---

## Requirements and how to run

**Magma is required and is not in this repository.** It is commercial, licensed software. The local
Docker setup used to develop this code — `Dockerfile`, `docker-compose.yml`, `run-magma.sh` and the
Magma tarball itself — is deliberately gitignored, so a fresh clone has none of it. The licensed
tarball must never be committed, and the resulting image must never be pushed to any registry.

To recreate the environment, place a Magma tarball named `magma.tar.xz` at the repository root and
build an image that extracts it to `/opt/magma`, puts that on `PATH`, and uses `/workspace` as the
working directory:

```sh
docker build -t magma-env .
```

with a one-line wrapper `run-magma.sh`:

```sh
#!/bin/bash
docker run --rm -v "$(pwd)":/workspace magma-env magma "$@"
```

Then run the suite either with `magma` on `PATH`:

```sh
./test_all.sh
```

or through the wrapper:

```sh
MAGMA=./run-magma.sh ./test_all.sh
```

### Most of the suite does not load on the setup described above

Worth knowing before you conclude a formula is broken.

**Symptom.** Loading a formula file aborts with `memi_reduce_block_mmap: block moved` followed by
`Magma: Internal error`, at around 9.8 MB of reported memory usage — so not a memory cap being hit, but
Magma's allocator failing to relocate an mmap'd block. The abort happens during `load`, before any
arithmetic runs.

**Measured, running the suite end to end:** 6 of the 23 testers complete; 17 abort this way. The six are
exactly the genus-2 ramified family. Sorted by the longest single *function* in the formula files each
tester loads:

| family | longest function | result |
|---|---|---|
| genus 2 ramified | 265–267 lines | completes |
| genus 2 split, both bases | 351–386 lines | aborts |
| genus 3 split | 547–2288 lines | aborts |

So the threshold on this setup lies between 267 and 351 lines, and it is **per function, not per file** —
splitting a file into smaller files does not help. Note it is not "genus 2 works, genus 3 does not":
genus-2 *split* also aborts.

**The cause has not been isolated,** and it is worth being explicit that there are two candidates:

1. **The Magma build.** `magma.tar.xz` unpacks Magma **V2.21-4 (STUDENT)** from 2015, and the executable
   is a **32-bit i386** binary (`ELF32`, `Machine type: x86-athlon`). A 32-bit address space is a real
   constraint independent of anything else.
2. **The container and CPU emulation.** The image is `linux/arm64` on Apple Silicon, so that i386 binary
   runs emulated, with an address-space layout quite unlike the one it was built for.

Do not assume it is the Magma version. It may equally be the emulation, or the interaction of the two.

**Already tried, and did not help:** rebuilding with `--platform linux/amd64`; Ubuntu 22.04, 18.04 and
native-i386 base images; disabling ASLR (`--privileged` with `setarch -R`); an unlimited stack; a legacy
VA layout; and Magma's own `-m` and `-S` memory-arena flags.

**Not yet tried, and the two things most likely to settle it:** a native x86-64 Linux host with no
emulation in the picture, and any Magma newer than 2.21. Either would distinguish candidate 1 from
candidate 2.

**Practical consequences.**

- Expect `./test_all.sh` to report 6 passed, 17 failed, 1 skipped, and to exit 1 on this setup. The 17
  failures are environmental, not formula defects — check the logs under `.test-logs/` for
  `memi_reduce_block_mmap` before drawing any conclusion about a formula.
- A full run takes about 5 minutes here, nearly all of it the six that work.
- Individual testers can be run directly, which is often more useful:
  `cd g2/ramifiedModel && ../../run-magma.sh nch2_ramifiedG2_whiteBox_tester.mag`
- `MAGMA` may be given as a relative path; `test_all.sh` resolves it to an absolute one, because it
  changes directory into each formula tree as it goes.
- This is the reason a Python verification framework is planned: the genus-2 split and all genus-3
  formulas currently have no runnable oracle on this machine at all.

---

## Repository layout

| path | contents |
|---|---|
| [g2/ramifiedModel/](g2/ramifiedModel/) | genus 2 ramified formulas, testers, shared utilities |
| [g2/splitModel/posReduced/](g2/splitModel/posReduced/) | genus 2 balanced split, positive-reduced basis |
| [g2/splitModel/negReduced/](g2/splitModel/negReduced/) | genus 2 balanced split, negative-reduced basis |
| [g3/splitModel/negReduced/](g3/splitModel/negReduced/) | genus 3 balanced split, negative-reduced basis |
| [g2/timings/](g2/timings/) | genus 2 timing experiments, prior-art formulas, results (47 files) |
| [g3/timings/](g3/timings/) | genus 3 timing experiments and results (18 files) |
| [generic/](generic/) | generic-genus Cantor/NUCOMP reference implementations and timings |
| [whitebox/](whitebox/) | whitebox test-case generator and its outputs |
| [latexTables/](latexTables/) | operation-count table generator and generated `.tex` |
| [Thesis/](Thesis/) | thesis LaTeX sources (see [Thesis](#thesis)) |
| [test_all.sh](test_all.sh) | test entrypoint |
| [1024bit_primes.mag](1024bit_primes.mag) | pre-generated 1024-bit primes used by the timing experiments |
| [rust/](rust/) | Rust port, a git submodule (see [Rust implementation](#rust-implementation)) |
| `ucalgary_2020_lindner_sebastian.pdf` | the built thesis |

Formula files live in a `g2Formulas/` or `g3Formulas/` subdirectory of each model directory — for
example [g2/ramifiedModel/g2Formulas/](g2/ramifiedModel/g2Formulas/) and
[g3/splitModel/negReduced/g3Formulas/](g3/splitModel/negReduced/g3Formulas/). Testers sit one level up,
beside the model directory.

---

## Naming convention

```
{arb,nch2,ch2}_{ramified,split}G{2,3}_{ADD,DBL,UTL}.mag
```

| token | meaning |
|---|---|
| `arb` | arbitrary characteristic — no assumption on the field |
| `nch2` | characteristic ≠ 2, so `h = 0` |
| `ch2` | characteristic 2 |
| `ADD` / `DBL` | divisor addition / doubling |
| `UTL` | utilities, split model only (infrastructure for the two infinite places) |
| `posReduced` / `negReduced` | which reduced basis the split model uses |

Note the casing inconsistency in tester filenames, which is historical: genus 2 uses
`*_whiteBox_tester.mag` (capital B) and genus 3 uses `*_whitebox_tester.mag` (lowercase).

**The reference implementation is duplicated.** `reduced_basis_arithmetic.mag` exists in 8 copies
across the tree in **5 byte-distinct versions**, and the genus-3 split model additionally has a
separate 730-line `poly_balanced_arithmetic.mag`. The copy under
[g2/splitModel/negReduced/](g2/splitModel/negReduced/reduced_basis_arithmetic.mag) is the one the
genus-2 testers assert against. Which copy is authoritative for a given consumer is currently
implicit — worth knowing before trusting any cross-comparison.

---

## Testing

```sh
./test_all.sh
```

runs 23 testers covering **both** genus 2 and genus 3.

**Whitebox testers** (`*_whiteBox_tester.mag`, `*_whitebox_tester.mag`) compute one
computer-generated divisor operation per computation path through the explicit formulas, and assert the
result against the reference implementation. Case counts are in [Status](#status). ADD and DBL branches
are instrumented; UTL branches are not.

**Random testers** (`*_random.mag`) compute random divisor additions and doublings over a **fixed,
enumerated list of small fields** — the field list is not random, though the curves and divisors drawn
on each are. Per-trial volumes differ by family:

| tester | divisors | curves per trial |
|---|---|---|
| genus 2, all families | 2500 or 5000 | 1 |
| genus 3 split `arb` | 100 | 10 |
| genus 3 split `nch2` | 500 | 3 |
| genus 3 split `ch2` | 1000 | 5 |

**Not run by `test_all.sh`:** the `ch2` genus-3 split whitebox tester (does not exist; invocation
commented out), [generic/reduced_basis_tester.mag](generic/reduced_basis_tester.mag),
[generic/arbitrary/reduced_basis_tester.mag](generic/arbitrary/reduced_basis_tester.mag), and
everything under [g2/timings/](g2/timings/) and [g3/timings/](g3/timings/).

---

## Generic-genus algorithms

Reference implementations of divisor arithmetic for **arbitrary genus**, used to validate the explicit
formulas and to measure how much the explicit formulas actually buy.

- [generic/](generic/) — Cantor composition/reduction plus NUCOMP and NUDUPL, for `h = 0`
  (characteristic ≠ 2). 25 top-level routines.
- [generic/arbitrary/](generic/arbitrary/) — the same for arbitrary characteristic. 33 top-level
  routines, i.e. 8 more than the `h = 0` version.

Each has ten timing drivers, `timings_2bit.mag` through `timings_1024bit.mag`, run directly:

```sh
magma timings_32bit.mag
```

See [generic/README.md](generic/README.md) for the routine-by-routine index and for which of the
several results directories corresponds to which run.

---

## Whitebox case generation

[whitebox/whitebox_auto_NEG.py](whitebox/whitebox_auto_NEG.py) drives the case generators in
[whitebox/genFiles/](whitebox/genFiles/) to emit testers into
[whitebox/testerFiles/](whitebox/testerFiles/). It must be run from the `whitebox/` directory — the
generators' `load` paths are relative to that, not to `genFiles/`.

Current limitations, all real:

- Only the `nch2` genus-2 split configuration is reachable. The output path has `negReduced`
  hardcoded, so every ramified and posReduced configuration is unreachable.
- The three genus-3 generators have stale `load` paths and cannot run.
- [whitebox/testerFiles/arb_splitG3_whiteBox_tester.mag](whitebox/testerFiles/arb_splitG3_whiteBox_tester.mag)
  is a 2-of-405-case fragment from an aborted run, **not** a usable tester. The real 405-case genus-3
  testers are the ones in [g3/splitModel/negReduced/](g3/splitModel/negReduced/).
- [whitebox/logs/](whitebox/logs/) holds output from aborted generation runs.

---

## Operation-count tables

[latexTables/latexConverter.py](latexTables/latexConverter.py) parses the formula files and counts
multiplications, squarings, additions and constant-multiplications per computation path, emitting the
LaTeX tables used in the thesis. It reads two annotation directives from each formula file:
`//Constant:` (which symbols are curve constants, so products with them count as C rather than M) and
`//startIGNORE` / `//endIGNORE` (blocks excluded from counting, used for the polynomial-level reference
code kept alongside each formula).

**This script does not currently run** — its input paths are stale and its output calls are commented
out, so the committed `.tex` files cannot be reproduced. Several counting faults are also known. Both
are documented in [ERRATA.md](ERRATA.md).

---

## Timing experiments

[g2/timings/](g2/timings/) and [g3/timings/](g3/timings/) hold the drivers, the prior-art formulas
compared against, the raw results and the plots.

| prior art | genus |
|---|---|
| [lange_2005.mag](g2/timings/formulas/previousBest/lange_2005.mag), [inf_2010.mag](g2/timings/formulas/previousBest/inf_2010.mag), [geo_2011.mag](g2/timings/formulas/previousBest/geo_2011.mag), [geo_noTrade_2011.mag](g2/timings/formulas/previousBest/geo_noTrade_2011.mag) | 2 |
| [rad_2019.mag](g3/timings/formulas/previousBest/rad_2019.mag), [sutherland_2019.mag](g3/timings/formulas/previousBest/sutherland_2019.mag) | 3 |

The formula copies under `timings/*/ramFormulas/` and `timings/*/splitFormulas/` are **deliberate
variants**, not duplicates: function names carry a `_RAM` / split suffix so both models can coexist in
one Magma session, returns are tuples, and debug output is commented out to keep I/O out of the timed
loop. They are maintained by hand and can drift from the canonical formulas.

`g2/timings/arbitrary_implementation/` is a superseded fork that no longer runs.

A defect affecting the published negative-reduced generic timings is recorded in [ERRATA.md](ERRATA.md).

---

## Rust implementation

[rust/](rust/) is a git submodule pointing at
[github.com/salindne/divisor-arithmetic](https://github.com/salindne/divisor-arithmetic), a Rust port
with its own test suite and CI. It is not built or tested by anything in this repository.

```sh
git submodule update --init --recursive
```

The recorded pointer may lag the submodule's `main`.

---

## Thesis

`ucalgary_2020_lindner_sebastian.pdf` at the repository root is the built document.

[Thesis/](Thesis/) holds the LaTeX sources — `frontmatter.tex`, `chapter1.tex` through `chapter7.tex`,
`appendix.tex` — but **not** the master document that includes them. There is no `\documentclass` in
any `.tex` file here, so the thesis cannot be rebuilt from this directory as it stands.

---

## Known gaps and roadmap

- **Genus 3 ramified formulas are not in this repository.** They were deferred in the thesis
  (chapter 7, "ongoing work elsewhere") and are being merged in separately.
- **No whitebox tester for `ch2` genus 3 split** — 405 branches covered by random testing only. The
  generator that would produce it is currently broken.
- **No posReduced basis at genus 3.**
- **A Python verification framework is planned**, to make the formulas checkable without Magma. Until
  it exists the formula files are frozen: defects found are recorded in [ERRATA.md](ERRATA.md) rather
  than fixed, because there is no oracle to prove a formula edit behaviour-preserving.

See [ERRATA.md](ERRATA.md) for known defects in published material.

---

## Licence and citation

Code in this repository is released under the MIT Licence — see [LICENSE](LICENSE).

The licence covers the code only. `ucalgary_2020_lindner_sebastian.pdf` and the university thesis
class and templates under [Thesis/](Thesis/) are **not** covered by it and retain their own terms.

If this work is useful in yours, please cite the thesis:

> S. Lindner. *Explicit Formulas for Hyperelliptic Curve Arithmetic.* PhD thesis, University of
> Calgary, 2020.
