# Generic-genus divisor arithmetic

Magma implementations of divisor class arithmetic for **arbitrary genus**, used to validate the explicit
formulas elsewhere in this repository and to measure what the explicit formulas actually buy. Written
for the CASC 2020 paper submission.

These scripts run under most versions of Magma, since only polynomial arithmetic over finite fields
is used, so none of the per-function size limits that affect the genus-3 explicit formulas apply here.

## Two variants

| directory | curve model | routines |
|---|---|---|
| `.` (this directory) | `h = 0`, i.e. characteristic ≠ 2 | 25 |
| [arbitrary/](arbitrary/) | arbitrary characteristic | 33 |

The `arbitrary/` variant is the same set of algorithms generalised to carry `h`, and adds 8 routines
beyond the `h = 0` version. The two are independent copies, not a shared library.

## Algorithms

Defined in [reduced_basis_arithmetic.mag](reduced_basis_arithmetic.mag):

| algorithm | ramified | split, negative-reduced | split, positive-reduced |
|---|---|---|---|
| Cantor add | `Add_RAM` | `Add_SPLIT_NEG` | `Add_SPLIT_POS` |
| Cantor double | `Double_RAM` | `Double_SPLIT_NEG` | `Double_SPLIT_POS` |
| NUCOMP | `Nucomp_RAM` | `Nucomp_SPLIT_NEG` | `Nucomp_SPLIT_POS` |
| NUDUPL | `Nuduple_RAM` | `Nuduple_SPLIT_NEG` | `Nuduple_SPLIT_POS` |

Supporting files:

- [reduced_basis_utilities.mag](reduced_basis_utilities.mag): Fibonacci-chain and double-chain drivers
  used by the timing scripts.
- [reduced_basis_tester.mag](reduced_basis_tester.mag): cross-checks the Fibonacci- and double-chain
  results of Cantor against NUCOMP. **Not** invoked by the repository's `test_all.sh`; run it directly.

## Timing experiments

Ten drivers, one per field size:

```sh
magma timings_32bit.mag
```

for `timings_[xx]bit.mag` with `[xx]` in 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024. The `arbitrary/`
directory carries its own set of ten.

### Results directories, read this before trusting a plot

There are **three distinct generations** of results here, and which one is canonical cannot be
recovered: the repository's git history is squashed into a single initial commit, and every file carries
the same checkout mtime. What can be established by comparison:

| directory | contents | relationship |
|---|---|---|
| `graphs/` | 62 PDFs | plots only, no raw data alongside. All 62 differ from both other PDF sets. |
| `processing/` | 62 PDFs, 20 `.raw`, gnuplot script, `parse_timings.py` | self-contained generation |
| `newProcessing/` | 62 PDFs, 20 `.raw`, gnuplot script, `parse_timings.py` | self-contained generation; all 62 PDFs differ from `processing/`, and its 20 `.raw` match nothing in `newRaw/` |
| `newRaw/` | 10 `.raw` | **orphaned**, and matches nothing in either processing directory |

`newRaw/` is a partial re-run whose outputs are not present here.  `processing/` and
`newProcessing/` are two complete but different generations of the same 62 plots.

A raw data directory was removed at v1.0.1: all 21 of its files were byte-identical to their
counterparts under `processing/`.

A defect affecting the negative-reduced timings produced by these scripts is recorded in
[../ERRATA.md](../ERRATA.md).
