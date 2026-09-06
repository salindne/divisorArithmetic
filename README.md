# divisorArithmetic

Magma explicit formulas for divisor class arithmetic on hyperelliptic curves of genus 2 and 3.

Sebastian Lindner. Companion code to *Explicit Formulas for Hyperelliptic Curve Arithmetic* (University of Calgary, 2020), built as `ucalgary_2020_lindner_sebastian.pdf` in this directory.

Twelve families: addition and doubling for each characteristic class `{arb, nch2, ch2}`, in the ramified (imaginary, `deg f = 2g+1`) and balanced split (real, `deg f = 2g+2`) models, at genus 2 and genus 3.  Every case is explicit with no Cantor fallback and costs exactly one inversion.  The split model requires a choice of reduced basis: positive reduced at genus 2, negative reduced at genus 3.  Genus 2 ships both.  See [Reduced basis](#reduced-basis).

Also included: generic-genus Cantor and NUCOMP reference implementations, a Python verification framework that runs in CI, Magma whitebox and random testers for every family, timing experiments, a LaTeX table generator, and a Rust port.  See [Repository layout](#repository-layout).

**Last updated:** 2026-08-26.

---

## Typical Case Operation Counts

The frequent case of the highest-degree operation in each family.  "Frequent" means the non-degenerate path, trivial gcd and full-degree result.  There is exactly one inversion per operation.

<table>
<thead>
<tr><th rowspan="2">family</th><th colspan="4">addition</th><th colspan="4">doubling</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>g2 ramified</b> arb</td><td>21</td><td>2</td><td>31</td><td>0</td><td>22</td><td>4</td><td>42</td><td>2</td></tr>
<tr><td><b>g2 ramified</b> nch2</td><td>21</td><td>2</td><td>23</td><td>0</td><td>21</td><td>5</td><td>25</td><td>0</td></tr>
<tr><td><b>g2 ramified</b> ch2</td><td>20</td><td>3</td><td>26</td><td>0</td><td>21</td><td>4</td><td>24</td><td>0</td></tr>
<tr><td><b>g2 split</b> arb</td><td>27</td><td>1</td><td>37</td><td>3</td><td>30</td><td>2</td><td>44</td><td>8</td></tr>
<tr><td><b>g2 split</b> nch2</td><td>26</td><td>2</td><td>36</td><td>0</td><td>29</td><td>3</td><td>39</td><td>0</td></tr>
<tr><td><b>g2 split</b> ch2</td><td>27</td><td>1</td><td>34</td><td>0</td><td>29</td><td>2</td><td>31</td><td>0</td></tr>
<tr><td><b>g3 ramified</b> arb</td><td>53</td><td>3</td><td>71</td><td>1</td><td>54</td><td>4</td><td>80</td><td>4</td></tr>
<tr><td><b>g3 ramified</b> nch2</td><td>53</td><td>3</td><td>59</td><td>0</td><td>53</td><td>5</td><td>61</td><td>0</td></tr>
<tr><td><b>g3 ramified</b> ch2</td><td>51</td><td>3</td><td>62</td><td>0</td><td>51</td><td>4</td><td>55</td><td>2</td></tr>
<tr><td><b>g3 split</b> arb</td><td>66</td><td>3</td><td>75</td><td>12</td><td>74</td><td>3</td><td>89</td><td>19</td></tr>
<tr><td><b>g3 split</b> nch2</td><td>66</td><td>3</td><td>73</td><td>0</td><td>73</td><td>4</td><td>85</td><td>0</td></tr>
<tr><td><b>g3 split</b> ch2</td><td>66</td><td>3</td><td>68</td><td>0</td><td>72</td><td>4</td><td>74</td><td>1</td></tr>
</tbody>
</table>

Every figure is measured.  `python3 verification/opcount.py --family <name>` executes the formulas over a real field, identifies the frequent case by observing which branch is taken, and cross-checks each contributing call against the Cantor reference implementation.  All sixteen families measure: the twelve above, genus-2 split negative reduced, and the genus-3 ramified family in weighted projective coordinates, which is frequent path only and carries no row in the table above.

Where the thesis publishes a cell, measurement reproduces it exactly: the genus-2 ramified rows against `tab:ramfcosts`, and 168 split shapes against `tab:splitfcosts` and `tab:g3splitfcosts{ADD,DBL}`, every one at exactly one inversion.  Two of those cells have since moved by design: the genus-3 split `33ADD n=0,0` and `3DBL n=0` each trade one multiplication for twelve additions, so measurement and the published table differ there deliberately, recorded in [Thesis/ERRATA.md](Thesis/ERRATA.md).  One systematic divergence turned up during the original check and was the tool's rather than the thesis's, a flat `+2A` on every split row, because a divisor's balancing weight is a small integer and `n := n1 + n2 - 2` is bookkeeping rather than field arithmetic.  See [NEW_WORK.md](NEW_WORK.md) N31.

The genus-2 split figures are positive reduced, the basis of record.  Negative reduced is a different algorithm and differs by an operation or two on several rows.

Each specialisation is cheaper than the `arb` it specialises on every shared shape, which `verification/selftest.py` asserts rather than assumes.  See [Operation-count tables](#operation-count-tables) for the counter of record and the one known misclassification in it, and [Related work](#related-work) for how these compare against prior art.

---

## Related Work

Two kinds of comparison.  For genus-2 ramified and both split families the previous best is the thesis itself, since genus-2 ramified and the split model are its own contribution, and the rows are reproduced here so the repository tells the whole story in one place.  Genus-3 ramified is the exception: the thesis defers it (`chapter6.tex:15`, *"ramified models are developed by another student"*), so the published state of the art there is other people's.  That family now lives here and is complete.  Randall Apperley wrote an initial version of the arbitrary characteristic addition and doubling and Amir Abbas Asgari wrote an initial specialisation of the odd characteristic addition; this work reworked those three and derived the other three to the current state of the art.

Every "this work" figure below is re-derived from `verification/opcount.py` and matches the published table exactly.  [RELATED_WORK.md](RELATED_WORK.md) carries the full survey, the per-lane detail and an access table for each source.

### Genus 2, ramified

Against Lange 2005, the standard reference, in the 4 coordinate affine setting.

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">Lange 2005</th><th colspan="4">this work</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>2DBL</b></td><td>22</td><td>6</td><td>56</td><td>3</td><td>22</td><td>4</td><td>42</td><td>2</td></tr>
<tr><td><b>12ADD</b></td><td>10</td><td>1</td><td>25</td><td>0</td><td>9</td><td>1</td><td>22</td><td>0</td></tr>
<tr><td><b>2ADD</b></td><td>22</td><td>3</td><td>40</td><td>0</td><td>21</td><td>2</td><td>31</td><td>0</td></tr>
</tbody>
</table>

### Genus 2, split

Against Erickson, Jacobson and Stein 2011.

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">EJS 2011</th><th colspan="4">this work</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>2DBL</b></td><td>30</td><td>2</td><td>50</td><td>10</td><td>30</td><td>2</td><td>44</td><td>8</td></tr>
<tr><td><b>2ADD</b></td><td>27</td><td>1</td><td>37</td><td>3</td><td>27</td><td>1</td><td>37</td><td>3</td></tr>
<tr><td><b>12ADD</b></td><td>17</td><td>2</td><td>30</td><td>6</td><td>14</td><td>2</td><td>26</td><td>3</td></tr>
<tr><td><b>1ADD</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td></tr>
</tbody>
</table>

Two cells tie exactly and the rest are ahead on additions and constant products.  The larger gains are in the adjustment operations, which this summary omits and the thesis table carries in full: EJS need two inversions for several of them where this work needs one.

### Genus 3, ramified

Prior work reports combined M+S and no additions, so the columns differ from the families above, and both sides cost exactly 1I.  † marks A counts we derived rather than figures the authors published: where a paper prints its formulas step by step the count is recoverable and is marked, and where the paper is closed it is not quoted.  The derivation rules are in [RELATED_WORK.md](RELATED_WORK.md).

<table>
<thead>
<tr><th rowspan="2">cell</th><th colspan="3">Nyukai 2006</th><th colspan="3">GKP 2004</th><th colspan="3">this work</th></tr>
<tr><th>M+S</th><th>C</th><th>A</th><th>M+S</th><th>C</th><th>A</th><th>M+S</th><th>C</th><th>A</th></tr>
</thead>
<tbody>
<tr><td><b>odd char, addition</b></td><td>67</td><td>0</td><td>105†</td><td>70</td><td>0</td><td>105†</td><td>56</td><td>0</td><td>59</td></tr>
<tr><td><b>odd char, doubling</b></td><td>68</td><td>0</td><td>93†</td><td>70</td><td>0</td><td>90†</td><td>58</td><td>0</td><td>61</td></tr>
<tr><td><b>char 2, addition</b></td><td colspan="3">n/a</td><td>67</td><td>0</td><td>100†</td><td>54</td><td>0</td><td>62</td></tr>
<tr><td><b>char 2, doubling</b></td><td colspan="3">n/a</td><td>69</td><td>0</td><td>107†</td><td>55</td><td>2</td><td>55</td></tr>
<tr><td><b>arbitrary, addition</b></td><td colspan="3">n/a</td><td colspan="3">n/a</td><td>56</td><td>1</td><td>71</td></tr>
<tr><td><b>arbitrary, doubling</b></td><td colspan="3">n/a</td><td colspan="3">n/a</td><td>58</td><td>4</td><td>80</td></tr>
</tbody>
</table>

The characteristic 2 rows quote whichever GKP variant is cheaper for that operation, their `h₂ = 0` form for the addition and their `f₆ = 0` form for the doubling.  Against the variant not shown the margin is wider: 68 M+S and 105A for the addition, 72 M+S and 113 to 114A for the doubling.

### Genus 3, split

Against Rezai Rad et al. 2019 and Sutherland 2019.

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">Rezai Rad et al. 2019</th><th colspan="4">Sutherland 2019</th><th colspan="4">this work</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>3DBL odd</b></td><td>85</td><td>2</td><td>163</td><td>0</td><td>74</td><td>8</td><td>127</td><td>0</td><td>73</td><td>4</td><td>85</td><td>0</td></tr>
<tr><td><b>3ADD odd</b></td><td>75</td><td>2</td><td>138</td><td>0</td><td>73</td><td>6</td><td>127</td><td>0</td><td>66</td><td>3</td><td>73</td><td>0</td></tr>
<tr><td><b>3DBL char 2</b></td><td>89</td><td>1</td><td>116</td><td>0</td><td colspan="4">n/a</td><td>72</td><td>4</td><td>74</td><td>1</td></tr>
<tr><td><b>3ADD char 2</b></td><td>81</td><td>0</td><td>118</td><td>0</td><td colspan="4">n/a</td><td>66</td><td>3</td><td>68</td><td>0</td></tr>
</tbody>
</table>

### Reading these tables

- `C` is zero in every previous best cell because those normal forms leave no curve coefficient to multiply by.  It is non-zero only here and only in the `arb` families, which by definition cannot normalise, so those cells are the cost of generality rather than an oversight.
- The genus-3 ramified characteristic 2 rows are quoted at `deg h = 3`, this repository's target shape.  Cheaper char 2 numbers exist at other `h` shapes and are not comparable, Birkner's `h = 1` doubling being 21 M+S and 20A because a constant `h` collapses most of the work.
- The genus-2 ramified and both split comparisons are as the thesis published them in 2020. The genus-3 ramified survey was compiled in 2026 and is current.

---

## Current and planned work

What is missing, in progress, or knowingly deferred.  Verification figures are under [Testing](#testing); this section is about what is not done.

- **The characteristic 2 genus-3 formulas have no published comparison, and one is not planned here.**  Three normal forms differ: ours (any degree-3 `h`, `f₆ = 0`), Birkner's Type Ia (`h` irreducible, `f₆ ∈ F₂`, `f₇` non-monic) and GKP's two variants. [RELATED_WORK.md](RELATED_WORK.md) carries the forms and the counts with citations.
- **One known saving in the split model is unapplied**, its identity already proved: a redundant 2×2 system in the genus-3 split degree-3 addition, `11M 6A` deletable.  What blocks it is the code rather than the counter, since the file's normalisation of `b2` does not match the closed form the proof gives, and `verification/opcount.py` cannot carry the edit in any case because the leaf carries no operation count.  [ERRATA.md](ERRATA.md) E24 holds the proof, the 400 of 400 constructed trials behind it, the nine unexamined sibling sites and the experiment that would settle it.  The adjugate trade in the same family is applied, six published cells moved by `+1M −12A` each and recorded in `Thesis/ERRATA.md` E-T10.
- **Detectability is 85.4%, not 100%.**  The whitebox corpus holds two cases per computation path per characteristic class from different fields, and 14.6% of the assignments in the formula bodies can still be perturbed without changing the returned divisor.  Some of that is structural, a branch guarded on `d = 0` needing `d = 0` to be reached at all, so 100% is not the target.  `verification/detect.py` reports it per family.
- **One branch is exempt from coverage**, `ADD227` of `ch2_splitG3_ADD`, and it carries a proof of unreachability in characteristic 2 rather than a search budget excuse.  Everything else is covered, 1,928 of 1,929.
- **`latexTables/latexConverter.py` is not runnable and will not be repaired**; its input paths are stale.  It was demoted to a LaTeX renderer once counting moved to `verification/opcount.py`, and repairing it was declined in August 2026 because the tables it renders are not needed.  So the committed `.tex` tables cannot be regenerated, nothing else depends on it, and the counting faults recorded against it in [ERRATA.md](ERRATA.md) as E4, E6 and E10 describe a tool that is not the counter of record and is not maintained.
- **The thesis's three appendix stubs stay empty**, for the same reason.  `Thesis/thesis.tex` leaves `\appendix` commented out with the reason inline.
- **Errata are recorded before they are fixed, deliberately.**  A defect goes into [ERRATA.md](ERRATA.md) with a reproducer and waits for a gate that can see the fix.  Entries whose reproducer already runs get fixed; the rest name the tooling they wait on.

---

## Reduced basis

The split model represents a divisor class with `v` normalised against one of the two polynomials at infinity: positive reduced uses `Vp`, negative reduced uses `Vn`.  Both represent the same class.  The choice dictates the direction of any adjustment step, so it changes the formulas rather than the mathematics.

| | basis | reason |
|---|---|---|
| genus 2 | **positive** reduced | Addition and doubling have equal net cost in either basis, so there is no efficiency argument.  Positive reduced matches the basis used by Erickson, Jacobson and Stein (2011), which makes the operation cost comparisons directly readable. |
| genus 3 | **negative** reduced | Negative reduced is genuinely cheaper here.  It absorbs one adjustment into the continued-fraction steps of Balanced NUCOMP, removing the need for any further adjustment in the frequent cases, and it lowers the degree of the `k = f - v(v+h)` polynomial through cancellations. |

The published operation cost tables follow that choice, and the thesis contrasts the two bases explicitly in chapter 5 for genus 2 and chapter 6 for genus 3.

Genus 2 ships both, under [g2/splitModel/posReduced/](g2/splitModel/posReduced/) and [g2/splitModel/negReduced/](g2/splitModel/negReduced/).  Genus 3 ships negative reduced only; there is no positive reduced basis at genus 3.

---

## Running Magma

**Magma is required and is not in this repository.**  It is commercial, licensed software.  Place your tarball as `magma.tar.xz` at the repository root.  It is gitignored, must never be committed, and an image built from it must never be pushed to any registry.

```sh
docker build -f tools/magma-docker/Dockerfile -t magma-qemufix .
MAGMA=tools/magma-docker/magma.sh ./test_all.sh
```

That runs 30 testers and exits 0, in a little over five minutes, essentially all of it Magma: 297 s of reported Magma time, across 62,944 divisor comparisons summed over the fifteen random testers.  Every family has a whitebox tester, so nothing is skipped.  See [Testing](#testing).

Use [tools/magma-docker/](tools/magma-docker/) rather than a plain `docker build`.  On Apple Silicon a plain image cannot run most of this repository.

### Why the container needs a patched emulator

`magma.exe` is a statically linked 32-bit i386 binary from 2015.  Apple Silicon cannot run it natively and Rosetta translates x86-64 only, so Docker routes it through `qemu-i386`, QEMU's user-mode emulator.  QEMU relocates a mapping whenever the guest passes `MREMAP_MAYMOVE`, including when the guest is shrinking it, where Linux would have kept the address.  Magma checks that its blocks stay put, so it aborts:

```
memi_reduce_block_mmap: block moved
Magma: Internal error
```

With a stock emulator only the six genus-2 ramified testers load, and every other tester aborts here.  It presents as a size limit, because whether Magma needs a shrink correlates with function length, which is why it was long mistaken for the formulas being too large for an old Magma.

[tools/magma-docker/](tools/magma-docker/) builds a `qemu-i386` with a one-line fix, after which the whole suite passes.  The full diagnosis and the list of approaches that do not work are in [tools/magma-docker/README.md](tools/magma-docker/README.md).

---

## Repository layout

| path | contents |
|---|---|
| [g2/ramifiedModel/](g2/ramifiedModel/) | genus 2 ramified formulas, testers, shared utilities |
| [g3/ramifiedModel/](g3/ramifiedModel/) | genus 3 ramified formulas, testers, shared utilities |
| [g3/ramifiedModel/projective/](g3/ramifiedModel/projective/) | weighted projective, odd characteristic, **frequent path only** — inversion-free, not complete, and outside the suite tallies above.  Its own [README](g3/ramifiedModel/projective/README.md) carries the counts against Fan–Wollinger–Gong |
| [g2/splitModel/posReduced/](g2/splitModel/posReduced/) | genus 2 balanced split, positive reduced |
| [g2/splitModel/negReduced/](g2/splitModel/negReduced/) | genus 2 balanced split, negative reduced |
| [g3/splitModel/negReduced/](g3/splitModel/negReduced/) | genus 3 balanced split, negative reduced |
| [g2/timings/](g2/timings/) | genus 2 timing experiments, prior work formulas, results (47 files) |
| [g3/timings/](g3/timings/) | genus 3 timing experiments and results (18 files) |
| [generic/](generic/) | generic-genus Cantor and NUCOMP reference implementations, and timings |
| [whitebox/](whitebox/) | whitebox test-case generator and its outputs |
| [latexTables/](latexTables/) | operation cost table generator and generated `.tex` |
| [Thesis/](Thesis/) | thesis LaTeX sources, corrections applied, see [Thesis](#thesis) |
| [ThesisPublished/](ThesisPublished/) | the same sources frozen as published, never edited, see [FROZEN.md](ThesisPublished/FROZEN.md) |
| [test_all.sh](test_all.sh) | test entrypoint |
| [FORMULA-MANIFEST.json](FORMULA-MANIFEST.json) | what this repository implements, in a form a script can read.  Generated by [tools/gen_manifest.py](tools/gen_manifest.py) from the same walk the verification harness tests against, so the two cannot disagree.  `--check` runs in CI |
| [1024bit_primes.mag](1024bit_primes.mag) | pre-generated 1024-bit primes for the timing experiments |
| [rust/](rust/) | Rust port, a git submodule, see [Rust implementation](#rust-implementation) |
| `ucalgary_2020_lindner_sebastian.pdf` | the built thesis |

Formula files live in a `g2Formulas/` or `g3Formulas/` subdirectory of each model directory, for example [g2/ramifiedModel/g2Formulas/](g2/ramifiedModel/g2Formulas/) and [g3/splitModel/negReduced/g3Formulas/](g3/splitModel/negReduced/g3Formulas/).  Testers sit one level up.

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

Tester filenames are inconsistently cased, historically: genus 2 uses `*_whiteBox_tester.mag` with a capital B, genus 3 uses `*_whitebox_tester.mag`.

**`Deg<i><j>ADD` names the degrees of the two input divisors, and one family disagrees about the order, so check before comparing.**

**The digits are positional: the smaller-degree divisor arrives first, in every family.**  Coefficients within an operand descend.

| | example |
|---|---|
| genus 2 ramified | `Deg12ADD(u0, v0, up1, up0, vp1, vp0, …)` |
| genus 2 split, both bases | `Deg12ADD(u0, v0, up1, up0, vp1, vp0, ccs)` |
| genus 3 ramified | `Deg23ADD(u1, u0, v1, v0, up2, up1, up0, vp2, vp1, vp0, …)` |
| genus 3 split | `Deg23ADD(u1, u0, v1, v0, up2, up1, up0, vp2, vp1, vp0, ccs)` |

So reading a name tells you what the inputs are, and the two `Deg12ADD` forms above differ only in their curve-constant tail.  Genus-3 split was the last family to bind the larger divisor first, and genus-2 split the last to write coefficients ascending; both were aligned together, the second having contradicted its own `Deg2DBL` in the same file.

Same-degree cases are spelled with a single digit throughout: `Deg1ADD` for 1+1, `Deg2ADD` for 2+2, `Deg3ADD` for 3+3.  The genus-3 models spelled the middle one `Deg22ADD` until it was collapsed with the reorder above.  Doubling matches: `Deg1DBL`, `Deg2DBL`, `Deg3DBL`.

**The reference implementation is duplicated.**  `reduced_basis_arithmetic.mag` exists in 8 copies across the tree in 5 byte-distinct versions, and genus 3 additionally has a separate 730-line `poly_balanced_arithmetic.mag`.  The copy under [g2/splitModel/negReduced/](g2/splitModel/negReduced/reduced_basis_arithmetic.mag) is what the genus-2 testers assert against.  Which copy is authoritative for a given consumer is currently implicit, so check before trusting any cross-comparison.

---

## Testing

```sh
./test_all.sh
```

runs 30 testers across genus 2 and genus 3, fifteen whitebox and fifteen random, in a little over five minutes.

**Where the project stands**, each figure reproduced by the command beside it:

| gate | result | command |
|---|---|---|
| Magma suite | **30 testers, 0 failures, 0 skips** | `./test_all.sh` |
| frozen case corpus | **7,043 cases replayed, 7,043 matched** | `python3 verification/whitebox.py` |
| branch coverage | **1,928 of 1,929 labelled branches, 99.9%** | as above |
| corpus detectability | **85.4%** of formula-body assignments observable | `python3 verification/detect.py` |
| differential tester | **55,236 operations compared, 0 wrong** | `python3 verification/driver.py --strict` |
| framework selftest | **22 sections, 0 failures, 0 skips** | `python3 verification/selftest.py` |
| formula manifest | **16 families, 41 formula files, 0 unclaimed** | `python3 tools/gen_manifest.py --check` |

The one uncovered branch is exempted with a written reason in `verification/coverage_baseline.json`: `ch2_splitG3_ADD`'s `ADD227` carries a proof that it is unreachable in characteristic 2.

**Whitebox testers** replay divisor operations found by coverage-guided search, two per computation path per characteristic class and drawn from different fields, asserting each result against the reference implementation.  The cases are not hand-designed; what earns them a place in CI is that they are complete and deterministic.

**Coverage and detectability answer different questions.**  Coverage asks whether every branch is reached.  Detectability asks whether a change to the arithmetic would be noticed: every executed assignment is perturbed and the result compared, so an assignment whose perturbation changes nothing is invisible to the corpus however well covered its branch is.  `ERRATA.md` **E20** is that distinction costing a correct optimisation, and it is why each path carries two cases from different fields rather than one.  100% is neither reachable nor the target, some assignments being structurally invisible, such as a guard variable a branch requires to be zero.  Per family the figures run from 69% to 96.5%.

**The Python framework** in [verification/](verification/) is what runs in CI, since Magma is licensed and cannot.  It interprets the real `.mag` source, so there is no transcription to drift:

```sh
python3 verification/whitebox.py                                  # frozen corpus, the CI gate
python3 verification/driver.py --curves 3 --pairs 3 --strict      # differential vs an independent reference, smoke volume
python3 verification/opcount.py --family ramified/g3/arb          # operation costs by execution
python3 verification/selftest.py                                  # the framework's own tests
```

It is pure standard library, so there is no install step and no lockfile.

**Random testers** compute random divisor additions and doublings over a fixed, enumerated list of small fields.  The field list is not random; the curves and divisors drawn on each are.  Exactly one curve is drawn per field in every tester, so the field list is the characteristic coverage, which is why the divisor volumes are small where the field lists are not.

| tester | divisors per curve |
|---|---|
| genus 2 ramified, all three | 500 |
| genus 2 split, all six | 250 |
| genus 3 ramified, all three | 50 |
| genus 3 split, all three | 25 |

**Why these are enough, and what they are not for.**  The rare branches are proved by the whitebox testers deterministically, every case asserted against Magma's own Jacobian arithmetic at about a second per tester, so leaving a degenerate case to a one-in-q² dice roll here was never how it was covered.  What the random testers uniquely add is within-branch input variation against fresh inputs, and for that volume was already far past the point of diminishing return: the one defect of that class this project ever found (E1) took **3,240,293 enumerated pairs**, so 2500 per curve was three orders of magnitude short of catching it and 500 is no further away.

**Replaying a failure.**  Magma does not seed deterministically, two runs of the same tester drawing different curves, so each of these testers prints its seed and the command to reuse it:

```
// - Random seed 1804224007, step 0. Replay this run with RND_SEED=1804224007
```

`RND_SEED` is forwarded into the container unconditionally by [tools/magma-docker/magma.sh](tools/magma-docker/magma.sh), so that line works as printed.

**Not run by `test_all.sh`:** [generic/reduced_basis_tester.mag](generic/reduced_basis_tester.mag); [generic/arbitrary/reduced_basis_tester.mag](generic/arbitrary/reduced_basis_tester.mag); and everything under [g2/timings/](g2/timings/) and [g3/timings/](g3/timings/).

---

## Generic-genus algorithms

Reference implementations for arbitrary genus, used to validate the explicit formulas and to measure what the explicit formulas buy.

- [generic/](generic/) is Cantor composition and reduction plus NUCOMP and NUDUPL for `h = 0`, characteristic not 2.  25 top-level routines.
- [generic/arbitrary/](generic/arbitrary/) is the same for arbitrary characteristic, with 33 top-level routines, 8 more than the `h = 0` version.

Each has ten timing drivers, `timings_2bit.mag` through `timings_1024bit.mag`:

```sh
magma timings_32bit.mag
```

[generic/README.md](generic/README.md) has the routine index, and identifies which of the several results directories corresponds to which run.

---

## Whitebox case generation

[whitebox/whitebox_auto_NEG.py](whitebox/whitebox_auto_NEG.py) drives the case generators in [whitebox/genFiles/](whitebox/genFiles/) to emit a tester.  Run it from the `whitebox/` directory: the generators' `load` paths are relative to that, not to `genFiles/`.

```
cd whitebox
./whitebox_auto_NEG.py ch2 split 3 --trials 12000 --out ../g3/splitModel/negReduced/x.mag
./whitebox_auto_NEG.py ch2 split 3 --from-log logs/ch2_splitG3_log.txt   # reparse, no Magma
```

**How a case is chosen.**  A generator loops over random curves and divisor pairs and prints a block for each operation whose result agrees with Magma's own Cantor arithmetic, letting the formula's own `ADD_DEBUG`/`DBL_DEBUG` label name the branch.  The runner banks one block per label per field, then keeps `--per-char` of them per characteristic class, climbing the field ladder from the bottom, so a branch ends up with two cases from two different fields.  Both halves of that are measured rather than preferred: two cases at one field leave more of the arithmetic invisible than one case at a larger field, because same-field failures are correlated, and the ladder is climbed from the bottom because the benefit saturates immediately while the cost does not.  A whitebox tester is therefore the frozen output of a coverage-guided random search, complete and replayable, but not a set of hand-designed probes.  Every case in the committed corpus is extracted from such a tester; `verification/whitebox.py --harvest` can search for cases directly, but nothing in the corpus comes from it today.

**Three of the fifteen generators are unbounded**, the genus-3 split ones.  Their search loop is `while true`, so the run does not end on its own and the log grows without limit; the other twelve iterate a fixed field list and terminate.  For those three, killing the container is not a substitute for finishing, because the runner sees the non-zero exit (`magma exited 137`) and refuses to write a tester.  Let it run until the log holds every label, stop it, then re-parse with `--from-log`, which writes the tester without Magma.  Check coverage first, since the log is the only thing that carries it:

```
grep -oE '^(ADD|DBL)[0-9]+$' logs/<family>_log.txt | sort -u | wc -l
```

**Regeneration cannot always reproduce what is deployed, which is what `--merge-tester` is for.**  A fresh genus-3 split search reaches 403 of that family's 405 labels, and each label it misses is covered by exactly one deployed case, so discarding the existing tester would lose coverage.  `--merge-tester` appends an existing tester's case blocks verbatim, which is regeneration rather than copying, since a tester is a header plus one self-contained block per case.  The useful consequence is that a partial run pays: any second case found is additive and coverage cannot fall.

| flag | effect |
|---|---|
| `--trials` | bounds the search |
| `--per-char` | cases kept per label per characteristic class, default 2 |
| `--basis` | `neg` or `pos`, selecting the genus-2 split basis and the generator that matches it |
| `--inherit-from FIELD:LOG` | take an existing log's blocks as candidates, which is how `arb` carries its specialisations' cases |
| `--merge-tester PATH` | append an existing tester's case blocks verbatim |
| `--from-log` | re-parse a log without running Magma |
| `--allow-incomplete` | write a tester that misses a label, refused by default |

Limitations:

- An unreached branch is reported, and writing a tester with a gap needs `--allow-incomplete`.
- `whitebox/testerFiles/` is the generator's staging directory and is gitignored.  A tester is of record only once it is copied next to the formulas it tests; `verification/whitebox.py` excludes the staging path so a half-finished run cannot be mistaken for a gate.
- [whitebox/logs/](whitebox/logs/) holds the residue of a pre-2025 orchestrator run alongside output from aborted ones.  Two of the three original files begin mid-polynomial: that generation reset the log with `truncate(0)` while Magma still held it open at its own write offset.  The runner now writes to a separate `.new` file and never truncates.  Regeneration logs are gitignored, running to gigabytes where the committed ones are kilobytes.

---

## Operation-count tables

**[verification/opcount.py](verification/opcount.py) is the counter of record.**  It measures by running the formulas over a real finite field, per branch, and identifies the frequent case by observing which branch is taken rather than inferring it from the source.  It reports inversions, which the older static counter does not count at all.  Every contributing execution is cross-checked against an independent Cantor implementation, so an input outside the formulas' domain shows up as a mismatch rather than as a plausible wrong count.  Per-function figures for every family are in the [appendix](#appendix-operation-costs-by-function).

Conventions come from each formula file's own directives, never from a table here: `//Constant:` names the curve coefficients, so products with them count C rather than M; `//Ignore:` names coefficients whose products are free; `//startIGNORE` / `//endIGNORE` bracket the polynomial-level reference code kept beside each formula.  Division by 2 counts as an addition, per the thesis.

**One known misclassification, `ERRATA.md` E13.**  A product whose factor is a composite over curve coefficients, `2*f6*u1_0`, is charged M although `2*f6` is fixed per curve.  Six live sites, all in the genus-3 ramified arbitrary doubling, one of them on a frequent path.  Totals are right; the M and C split is not.

[latexTables/latexConverter.py](latexTables/latexConverter.py) is the older static counter, which scanned the source as text and emitted the thesis's LaTeX tables.  The two agreed on all 208 published own-work quadruples, two methods sharing no code, but it is now demoted to a renderer: it does not run today, its input paths being stale, several counting faults are recorded in [ERRATA.md](ERRATA.md), and nothing depends on it except regenerating `.tex`.

How the genus-3 ramified figures compare to the published literature, with every prior source's curve assumptions and the normalisation arithmetic stated, is in [RELATED_WORK.md](RELATED_WORK.md).

Efficiency findings for the arbitrary-characteristic genus-3 ramified formulas, each located, measured and adversarially verified, are in [EFFICIENCY_ARB_G3.md](EFFICIENCY_ARB_G3.md).  That document changes no formula; it was the input to the implementation work, which is complete.

What this project contributes beyond the published thesis, every correction, completion and result with the argument for why it is right and the measurement that establishes it, is in [NEW_WORK.md](NEW_WORK.md).  It is written to be lifted into the next publication and kept current as the work proceeds rather than reconstructed afterwards.  Its Part I gives one account of the curve normal forms, uniform in the genus, producing all six ramified forms, and all six now have a formula banner declaring exactly that form.  [verification/normal_form.py](verification/normal_form.py) reproduces every claim in it.

---

## Timing experiments

[g2/timings/](g2/timings/) and [g3/timings/](g3/timings/) hold the drivers, the prior work formulas compared against, the raw results and the plots.

| prior work | genus | model | source |
|---|---|---|---|
| [lange_2005.mag](g2/timings/formulas/previousBest/lange_2005.mag) | 2 | ramified | Lange 2005 |
| [inf_2010.mag](g2/timings/formulas/previousBest/inf_2010.mag) | 2 | split | Erickson, Jacobson and Stein 2011 |
| [geo_2011.mag](g2/timings/formulas/previousBest/geo_2011.mag) | 2 | ramified | Costello and Lauter 2011, as published |
| [geo_noTrade_2011.mag](g2/timings/formulas/previousBest/geo_noTrade_2011.mag) | 2 | ramified | Costello and Lauter 2011, with one trade undone here |
| [rad_2019.mag](g3/timings/formulas/previousBest/rad_2019.mag) | 3 | split | Rezai Rad et al. 2019 |
| [sutherland_2019.mag](g3/timings/formulas/previousBest/sutherland_2019.mag) | 3 | split | Sutherland 2019 |

Only [lange_2005.mag](g2/timings/formulas/previousBest/lange_2005.mag) names an author, `// Author: Sebastian Lindner,2019`, which is accurate about who wrote the transcription rather than who derived the mathematics.  The other five carry no author line.  [ERRATA.md](ERRATA.md) records that header.  All six fall back on Cantor's algorithm in the cases their source did not develop, so the timed chains are complete.

- **Lange 2005.**  T. Lange, "Formulae for Arithmetic on Genus 2 Hyperelliptic Curves," Applicable Algebra in Engineering, Communication and Computing 15, 295–328, 2005.  Bib key `Lange_explicit_2005`.  Degree 1 and 2 addition, degree 2 addition, degree 2 doubling and the special output cases of each.
- **Erickson, Jacobson and Stein 2011.**  S. Erickson, M. J. Jacobson and A. Stein, "Explicit formulas for real hyperelliptic curves of genus 2 in affine representation," Advances in Mathematics of Communications 5(4), 623–666, 2011.  Bib key `EricksonJacobsonStein_realg2_2011`.  The file's Baby Step and Inverse Baby Step operations are the Degree 0 and 2 ADD with up and down adjust of this work, which is the comparison the thesis draws in chapter 5.  The filename says 2010 and the journal issue is 2011; the later date is the one every citation here uses.
- **Costello and Lauter 2011.**  C. Costello and K. Lauter, "Group Law Computations on Jacobians of Hyperelliptic Curves," Selected Areas in Cryptography 2011, Lecture Notes in Computer Science 7118, 92–117.  Bib key `CostelloLauter_geo_2011`.  Only the degree 2 addition and doubling frequent cases were developed there, so both files fall back on Cantor for everything else.
- **Rezai Rad et al. 2019.**  M. Rezai Rad, M. J. Jacobson and R. Scheidler, "Jacobian Versus Infrastructure in Split Hyperelliptic Curves," Algebra, Codes and Cryptology, Communications in Computer and Information Science 1133, 183–203, 2019.  Bib key `rad2019jacobian`.  The filename's `rad` is the first author's surname, not an abbreviation of a topic.
- **Sutherland 2019.**  A. V. Sutherland, "Fast Jacobian arithmetic for hyperelliptic curves of genus 3," ANTS-XIII, Open Book Series 2, 2019; arXiv:1607.08602.  This is the entry the reference list in [RELATED_WORK.md](RELATED_WORK.md) already carries, reproduced rather than restated.  Bib key `Sutherland_g3_2019` dates the work 2018, the symposium year, and records the volume as 2(1) and the pages as 425–442; the filename and the reference list date it 2019, the year the proceedings volume appeared, and that is the date used here.

The two Costello-Lauter files differ, function names and line breaks aside, in one computational block, the 2×2 solve, which occurs once in the doubling and once in the addition.  The published form spends 5 multiplications there and the variant spends 6, the difference being a trade of 1 field multiplication for 13 field additions that the published formulas take and this repository's variant declines ([Thesis/chapter5.tex](Thesis/chapter5.tex) line 2581).  The committed genus-2 timings measure the variant as the faster of the two in all twenty comparisons, addition and doubling at each of the ten field sizes ([g2/timings/processing/g2_timings.raw](g2/timings/processing/g2_timings.raw), columns `PNAR` against `PGAR` and `PNDR` against `PGDR`).  The variant is this repository's own construction and not a second set of counts printed by Costello and Lauter.

The formula copies under `timings/*/ramFormulas/` and `timings/*/splitFormulas/` are deliberate variants rather than duplicates: function names carry a `_RAM` or split suffix so both models can coexist in one Magma session, returns are tuples, and debug output is commented out to keep I/O out of the timed loop.  They are hand-maintained and can drift from the canonical formulas.

`g2/timings/arbitrary_implementation/` is a superseded fork that no longer runs.

A defect affecting the published negative reduced generic timings is recorded in [ERRATA.md](ERRATA.md).

---

## Rust implementation

[rust/](rust/) is a git submodule pointing at [github.com/salindne/divisor-arithmetic](https://github.com/salindne/divisor-arithmetic), a Rust port with its own tests and CI.  Nothing in this repository builds or tests it.

```sh
git submodule update --init --recursive
```

The recorded pointer may lag the submodule's `main`.

---

## Thesis

`ucalgary_2020_lindner_sebastian.pdf` at the repository root is the built document, as published and never modified.

The source exists in two copies, deliberately:

| | |
|---|---|
| [ThesisPublished/](ThesisPublished/) | **frozen.**  Byte-exact as submitted; never edited |
| [Thesis/](Thesis/) | **evolving.**  Corrections land here, each logged in [Thesis/ERRATA.md](Thesis/ERRATA.md) |

Both hold `frontmatter.tex`, `chapter1.tex` through `chapter7.tex` and `appendix.tex`.  Neither held the master document that includes them, so for a long time the thesis could not be rebuilt from either directory; [Thesis/thesis.tex](Thesis/thesis.tex) is that master, reconstructed, and [Thesis/thesis.pdf](Thesis/thesis.pdf) is what it builds.

**The two PDFs are different documents and the distinction matters.**  `ucalgary_2020_lindner_sebastian.pdf` is as submitted in 2020.  [Thesis/thesis.pdf](Thesis/thesis.pdf) is the corrected thesis, so it is the only place the errata are visible rendered rather than as source.  Rebuild it with:

```sh
cd Thesis
mkdir -p build && cp mylib.bib build/
pdflatex -output-directory=build thesis && (cd build && bibtex thesis)
pdflatex -output-directory=build thesis && pdflatex -output-directory=build thesis
cp build/thesis.pdf thesis.pdf
```

**Build out of tree, as above.**  A bare `pdflatex thesis` in that directory overwrites
`Thesis/thesis.aux` and `Thesis/thesis.toc`, which are committed artifacts of the original
2020 build and are what the reconstructed master's include order was recovered from.

Corrections are made only where they are justified, and [Thesis/ERRATA.md](Thesis/ERRATA.md) says for each one whether it was verified by measurement or rests on a structural argument.  `diff -r ThesisPublished Thesis` shows the current divergence.

---

## Licence and citation

Code here is MIT licensed, see [LICENSE](LICENSE).  The licence covers the code only.  `ucalgary_2020_lindner_sebastian.pdf` and the university thesis class and templates under [Thesis/](Thesis/) are not covered and retain their own terms.

To cite:

> S. Lindner. *Explicit Formulas for Hyperelliptic Curve Arithmetic.* PhD thesis, University of Calgary, 2020.

---

## Appendix: operation costs by function

Operation costs for every non-degenerate function, measured as in [Typical Case Operation Counts](#typical-case-operation-counts) and reported per characteristic class.  Each figure is the frequent branch of that operation.  Ramified rows are function names; split rows carry the input balancing weights, because at split the weight is what selects which published row an operation belongs to.  Shapes the dispatcher answers without arithmetic are omitted, five at genus 2 split and thirteen at genus 3 split.  Genus-2 split negative reduced is omitted, positive reduced being the basis of record.  Measured over GF(31) for `arb` and `nch2`, GF(32) for `ch2`.

### Genus 2, ramified

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">arb</th><th colspan="4">nch2</th><th colspan="4">ch2</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>11ADD</b></td><td>3</td><td>0</td><td>4</td><td>0</td><td>3</td><td>0</td><td>4</td><td>0</td><td>3</td><td>0</td><td>4</td><td>0</td></tr>
<tr><td><b>12ADD</b></td><td>9</td><td>1</td><td>22</td><td>0</td><td>8</td><td>2</td><td>15</td><td>0</td><td>8</td><td>1</td><td>19</td><td>0</td></tr>
<tr><td><b>22ADD</b></td><td>21</td><td>2</td><td>31</td><td>0</td><td>21</td><td>2</td><td>23</td><td>0</td><td>20</td><td>3</td><td>26</td><td>0</td></tr>
<tr><td><b>1DBL</b></td><td>4</td><td>1</td><td>15</td><td>3</td><td>3</td><td>1</td><td>9</td><td>1</td><td>2</td><td>2</td><td>5</td><td>2</td></tr>
<tr><td><b>2DBL</b></td><td>22</td><td>4</td><td>42</td><td>2</td><td>21</td><td>5</td><td>25</td><td>0</td><td>21</td><td>4</td><td>24</td><td>0</td></tr>
</tbody>
</table>

### Genus 3, ramified

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">arb</th><th colspan="4">nch2</th><th colspan="4">ch2</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>11ADD</b></td><td>3</td><td>0</td><td>4</td><td>0</td><td>3</td><td>0</td><td>4</td><td>0</td><td>3</td><td>0</td><td>3</td><td>0</td></tr>
<tr><td><b>12ADD</b></td><td>6</td><td>1</td><td>8</td><td>0</td><td>6</td><td>1</td><td>8</td><td>0</td><td>6</td><td>1</td><td>7</td><td>0</td></tr>
<tr><td><b>13ADD</b></td><td>18</td><td>1</td><td>39</td><td>0</td><td>16</td><td>3</td><td>28</td><td>0</td><td>15</td><td>2</td><td>33</td><td>0</td></tr>
<tr><td><b>22ADD</b></td><td>25</td><td>1</td><td>41</td><td>0</td><td>24</td><td>2</td><td>33</td><td>0</td><td>23</td><td>2</td><td>35</td><td>0</td></tr>
<tr><td><b>23ADD</b></td><td>36</td><td>3</td><td>55</td><td>0</td><td>35</td><td>4</td><td>45</td><td>0</td><td>34</td><td>4</td><td>46</td><td>1</td></tr>
<tr><td><b>33ADD</b></td><td>53</td><td>3</td><td>71</td><td>1</td><td>53</td><td>3</td><td>59</td><td>0</td><td>51</td><td>3</td><td>62</td><td>0</td></tr>
<tr><td><b>1DBL</b></td><td>7</td><td>1</td><td>24</td><td>4</td><td>5</td><td>1</td><td>15</td><td>1</td><td>4</td><td>2</td><td>7</td><td>2</td></tr>
<tr><td><b>2DBL</b></td><td>28</td><td>4</td><td>70</td><td>9</td><td>25</td><td>4</td><td>44</td><td>0</td><td>21</td><td>4</td><td>38</td><td>5</td></tr>
<tr><td><b>3DBL</b></td><td>54</td><td>4</td><td>80</td><td>4</td><td>53</td><td>5</td><td>61</td><td>0</td><td>51</td><td>4</td><td>55</td><td>2</td></tr>
</tbody>
</table>

### Genus 2, split, positive reduced

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">arb</th><th colspan="4">nch2</th><th colspan="4">ch2</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>01ADD n=0,0</b></td><td>4</td><td>0</td><td>9</td><td>3</td><td>3</td><td>1</td><td>7</td><td>2</td><td>3</td><td>1</td><td>7</td><td>2</td></tr>
<tr><td><b>01ADD n=2,1</b></td><td>4</td><td>0</td><td>13</td><td>3</td><td>3</td><td>1</td><td>9</td><td>2</td><td>3</td><td>1</td><td>8</td><td>2</td></tr>
<tr><td><b>02ADD n=0,0</b></td><td>6</td><td>0</td><td>17</td><td>3</td><td>4</td><td>2</td><td>12</td><td>0</td><td>5</td><td>1</td><td>11</td><td>0</td></tr>
<tr><td><b>02ADD n=2,0</b></td><td>6</td><td>0</td><td>17</td><td>3</td><td>4</td><td>2</td><td>12</td><td>0</td><td>5</td><td>1</td><td>11</td><td>0</td></tr>
<tr><td><b>11ADD n=0,0</b></td><td>11</td><td>2</td><td>19</td><td>4</td><td>9</td><td>4</td><td>17</td><td>1</td><td>9</td><td>4</td><td>15</td><td>1</td></tr>
<tr><td><b>11ADD n=0,1</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>4</td><td>0</td></tr>
<tr><td><b>11ADD n=1,0</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>4</td><td>0</td></tr>
<tr><td><b>11ADD n=1,1</b></td><td>9</td><td>2</td><td>20</td><td>3</td><td>9</td><td>2</td><td>16</td><td>1</td><td>8</td><td>3</td><td>14</td><td>1</td></tr>
<tr><td><b>12ADD n=0,0</b></td><td>15</td><td>2</td><td>30</td><td>5</td><td>15</td><td>2</td><td>26</td><td>0</td><td>14</td><td>3</td><td>22</td><td>0</td></tr>
<tr><td><b>12ADD n=1,0</b></td><td>14</td><td>2</td><td>26</td><td>3</td><td>14</td><td>2</td><td>22</td><td>0</td><td>14</td><td>2</td><td>19</td><td>0</td></tr>
<tr><td><b>22ADD n=0,0</b></td><td>27</td><td>1</td><td>37</td><td>3</td><td>26</td><td>2</td><td>36</td><td>0</td><td>27</td><td>1</td><td>34</td><td>0</td></tr>
<tr><td><b>1DBL n=0</b></td><td>12</td><td>2</td><td>20</td><td>3</td><td>10</td><td>3</td><td>19</td><td>1</td><td>11</td><td>3</td><td>14</td><td>1</td></tr>
<tr><td><b>1DBL n=1</b></td><td>14</td><td>2</td><td>26</td><td>4</td><td>12</td><td>3</td><td>23</td><td>1</td><td>11</td><td>4</td><td>16</td><td>1</td></tr>
<tr><td><b>2DBL n=0</b></td><td>30</td><td>2</td><td>44</td><td>8</td><td>29</td><td>3</td><td>39</td><td>0</td><td>29</td><td>2</td><td>31</td><td>0</td></tr>
</tbody>
</table>

### Genus 3, split, negative reduced

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="4">arb</th><th colspan="4">nch2</th><th colspan="4">ch2</th></tr>
<tr><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th><th>M</th><th>S</th><th>A</th><th>C</th></tr>
</thead>
<tbody>
<tr><td><b>01ADD n=0,0</b></td><td>33</td><td>2</td><td>48</td><td>21</td><td>30</td><td>4</td><td>37</td><td>7</td><td>31</td><td>3</td><td>37</td><td>11</td></tr>
<tr><td><b>01ADD n=0,1</b></td><td>8</td><td>0</td><td>17</td><td>5</td><td>6</td><td>1</td><td>14</td><td>3</td><td>6</td><td>1</td><td>12</td><td>3</td></tr>
<tr><td><b>01ADD n=1,0</b></td><td>8</td><td>0</td><td>17</td><td>5</td><td>6</td><td>1</td><td>14</td><td>3</td><td>6</td><td>1</td><td>12</td><td>3</td></tr>
<tr><td><b>01ADD n=3,2</b></td><td>8</td><td>0</td><td>12</td><td>4</td><td>6</td><td>1</td><td>10</td><td>3</td><td>6</td><td>1</td><td>10</td><td>3</td></tr>
<tr><td><b>02ADD n=0,0</b></td><td>37</td><td>2</td><td>54</td><td>21</td><td>33</td><td>5</td><td>42</td><td>6</td><td>34</td><td>4</td><td>39</td><td>10</td></tr>
<tr><td><b>02ADD n=0,1</b></td><td>10</td><td>0</td><td>23</td><td>6</td><td>8</td><td>2</td><td>19</td><td>2</td><td>9</td><td>1</td><td>17</td><td>2</td></tr>
<tr><td><b>02ADD n=1,0</b></td><td>10</td><td>0</td><td>23</td><td>6</td><td>8</td><td>2</td><td>19</td><td>2</td><td>9</td><td>1</td><td>17</td><td>2</td></tr>
<tr><td><b>02ADD n=3,1</b></td><td>10</td><td>0</td><td>23</td><td>6</td><td>9</td><td>1</td><td>21</td><td>2</td><td>9</td><td>1</td><td>20</td><td>2</td></tr>
<tr><td><b>03ADD n=0,0</b></td><td>40</td><td>2</td><td>60</td><td>22</td><td>36</td><td>5</td><td>44</td><td>3</td><td>37</td><td>3</td><td>46</td><td>9</td></tr>
<tr><td><b>03ADD n=1,0</b></td><td>11</td><td>0</td><td>29</td><td>7</td><td>9</td><td>1</td><td>21</td><td>0</td><td>9</td><td>1</td><td>21</td><td>2</td></tr>
<tr><td><b>03ADD n=3,0</b></td><td>11</td><td>0</td><td>29</td><td>7</td><td>9</td><td>1</td><td>21</td><td>0</td><td>9</td><td>1</td><td>21</td><td>2</td></tr>
<tr><td><b>11ADD n=0,0</b></td><td>41</td><td>4</td><td>57</td><td>23</td><td>38</td><td>6</td><td>46</td><td>8</td><td>38</td><td>6</td><td>45</td><td>10</td></tr>
<tr><td><b>11ADD n=0,1</b></td><td>14</td><td>2</td><td>26</td><td>5</td><td>13</td><td>3</td><td>23</td><td>1</td><td>13</td><td>3</td><td>20</td><td>1</td></tr>
<tr><td><b>11ADD n=0,2</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td></tr>
<tr><td><b>11ADD n=1,0</b></td><td>14</td><td>2</td><td>26</td><td>5</td><td>13</td><td>3</td><td>23</td><td>1</td><td>13</td><td>3</td><td>20</td><td>1</td></tr>
<tr><td><b>11ADD n=1,1</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td></tr>
<tr><td><b>11ADD n=1,2</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td></tr>
<tr><td><b>11ADD n=2,0</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td></tr>
<tr><td><b>11ADD n=2,1</b></td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td><td>3</td><td>0</td><td>5</td><td>0</td></tr>
<tr><td><b>11ADD n=2,2</b></td><td>17</td><td>2</td><td>25</td><td>5</td><td>15</td><td>4</td><td>23</td><td>1</td><td>15</td><td>4</td><td>21</td><td>1</td></tr>
<tr><td><b>12ADD n=0,0</b></td><td>47</td><td>5</td><td>67</td><td>22</td><td>44</td><td>7</td><td>54</td><td>6</td><td>44</td><td>7</td><td>50</td><td>9</td></tr>
<tr><td><b>12ADD n=0,1</b></td><td>18</td><td>3</td><td>36</td><td>6</td><td>17</td><td>4</td><td>30</td><td>1</td><td>17</td><td>4</td><td>28</td><td>1</td></tr>
<tr><td><b>12ADD n=1,0</b></td><td>18</td><td>3</td><td>36</td><td>6</td><td>17</td><td>4</td><td>30</td><td>1</td><td>17</td><td>4</td><td>28</td><td>1</td></tr>
<tr><td><b>12ADD n=1,1</b></td><td>6</td><td>1</td><td>10</td><td>0</td><td>6</td><td>1</td><td>10</td><td>0</td><td>6</td><td>1</td><td>10</td><td>0</td></tr>
<tr><td><b>12ADD n=2,0</b></td><td>6</td><td>1</td><td>10</td><td>0</td><td>6</td><td>1</td><td>10</td><td>0</td><td>6</td><td>1</td><td>10</td><td>0</td></tr>
<tr><td><b>12ADD n=2,1</b></td><td>20</td><td>3</td><td>39</td><td>7</td><td>19</td><td>4</td><td>36</td><td>1</td><td>18</td><td>5</td><td>33</td><td>1</td></tr>
<tr><td><b>13ADD n=0,0</b></td><td>53</td><td>4</td><td>74</td><td>22</td><td>49</td><td>7</td><td>62</td><td>3</td><td>51</td><td>5</td><td>56</td><td>7</td></tr>
<tr><td><b>13ADD n=1,0</b></td><td>22</td><td>2</td><td>43</td><td>7</td><td>21</td><td>3</td><td>36</td><td>0</td><td>22</td><td>2</td><td>33</td><td>0</td></tr>
<tr><td><b>13ADD n=2,0</b></td><td>25</td><td>2</td><td>49</td><td>8</td><td>23</td><td>4</td><td>42</td><td>0</td><td>23</td><td>4</td><td>40</td><td>0</td></tr>
<tr><td><b>22ADD n=0,0</b></td><td>61</td><td>3</td><td>78</td><td>25</td><td>56</td><td>6</td><td>72</td><td>5</td><td>57</td><td>5</td><td>66</td><td>8</td></tr>
<tr><td><b>22ADD n=0,1</b></td><td>30</td><td>1</td><td>47</td><td>8</td><td>29</td><td>2</td><td>47</td><td>0</td><td>29</td><td>2</td><td>41</td><td>0</td></tr>
<tr><td><b>22ADD n=1,0</b></td><td>30</td><td>1</td><td>47</td><td>8</td><td>29</td><td>2</td><td>47</td><td>0</td><td>29</td><td>2</td><td>41</td><td>0</td></tr>
<tr><td><b>22ADD n=1,1</b></td><td>37</td><td>1</td><td>56</td><td>7</td><td>36</td><td>2</td><td>57</td><td>0</td><td>33</td><td>4</td><td>52</td><td>0</td></tr>
<tr><td><b>23ADD n=0,0</b></td><td>75</td><td>3</td><td>89</td><td>18</td><td>72</td><td>5</td><td>78</td><td>3</td><td>72</td><td>4</td><td>76</td><td>7</td></tr>
<tr><td><b>23ADD n=1,0</b></td><td>41</td><td>1</td><td>59</td><td>3</td><td>41</td><td>1</td><td>57</td><td>0</td><td>41</td><td>1</td><td>55</td><td>0</td></tr>
<tr><td><b>33ADD n=0,0</b></td><td>66</td><td>3</td><td>75</td><td>12</td><td>66</td><td>3</td><td>73</td><td>0</td><td>66</td><td>3</td><td>68</td><td>0</td></tr>
<tr><td><b>1DBL n=0</b></td><td>42</td><td>5</td><td>66</td><td>27</td><td>40</td><td>6</td><td>57</td><td>7</td><td>38</td><td>7</td><td>44</td><td>10</td></tr>
<tr><td><b>1DBL n=1</b></td><td>7</td><td>1</td><td>19</td><td>6</td><td>7</td><td>1</td><td>15</td><td>3</td><td>7</td><td>1</td><td>14</td><td>3</td></tr>
<tr><td><b>1DBL n=2</b></td><td>14</td><td>3</td><td>25</td><td>8</td><td>14</td><td>3</td><td>24</td><td>3</td><td>12</td><td>3</td><td>19</td><td>4</td></tr>
<tr><td><b>2DBL n=0</b></td><td>62</td><td>5</td><td>95</td><td>31</td><td>60</td><td>7</td><td>89</td><td>4</td><td>60</td><td>7</td><td>80</td><td>7</td></tr>
<tr><td><b>2DBL n=1</b></td><td>37</td><td>0</td><td>56</td><td>13</td><td>35</td><td>2</td><td>54</td><td>3</td><td>36</td><td>1</td><td>48</td><td>3</td></tr>
<tr><td><b>3DBL n=0</b></td><td>74</td><td>3</td><td>89</td><td>19</td><td>73</td><td>4</td><td>85</td><td>0</td><td>72</td><td>4</td><td>74</td><td>1</td></tr>
</tbody>
</table>
