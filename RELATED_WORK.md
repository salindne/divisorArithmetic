# Related work: genus-3 ramified-model explicit formulas

The baseline against which this repository's genus-3 ramified formulas
(`g3/ramifiedModel/`) are to be judged. Compiled 2026-08-07, before any
efficiency work on those formulas, so that improvements are measured against
the published state of the art rather than only against this repository's own
history. The split-model figures appear only for scale; the thesis
(`Thesis/chapter6.tex`) already covers that comparison.

Every operation count in this document carries its source. Counts measured by
this repository's tooling say so and name the tool; counts taken from a
publication name the table they came from. Where a source could not be opened
directly (one technical report is in Japanese), the count is attributed to the
survey that reports it and marked accordingly.

## Counting conventions, and how sources are normalised

**This repository / the thesis** (`Thesis/chapter6.tex`, Field Operation Costs
section): `M` multiplication, `S` squaring, `C` multiplication by a curve
coefficient, `A` addition/subtraction, `I` inversion. Division by 2 counts as
an A (following Sutherland). A multiplication is never traded for more than 3
additions. Additions are counted at all — unlike most prior work.

**The prior literature** (2000–2006, below) counts `I`, `M`, `S` only, and the
two Japanese-school papers report a combined `M/S` figure. No prior work
reports A or C. Consequently:

- the only unit comparable across every source is **I + combined M+S**;
- A-count comparisons are possible only against the thesis's own split-model
  rows;
- prior works fold coefficient multiplications into M (their curves have at
  most two live coefficients after normalisation, so the distinction barely
  arises).

**The measured counts in this document** come from the audit harness
(`/Users/s3b/Dev/divisor-audits/g3ram/harness/`), which executes the actual
Magma source text per branch and counts field operations as they happen. Its
vocabulary differs from the thesis converter's in two ways it does not hide:
it has **no C column** (coefficient products count as M), and it reports
executed counts — ranges reflect data-dependent short-circuits, not
uncertainty. Its `small` column covers only multiplication by integer
literals. The audited snapshot it measures is byte-identical to the imported
formulas modulo the PR2 renames, PR4's comment-only pass and PR5's dispatch
guard, none of which touch a formula statement.

## The published record, odd characteristic (h = 0)

Every published odd-characteristic genus-3 formula set uses the depressed
normal form: `y² = x⁷ + f₅x⁵ + f₄x⁴ + f₃x³ + f₂x² + f₁x + f₀`, i.e. **f₆ = 0**
(via `x → x − f₆/7`, valid for characteristic ≠ 7). The survey table in
Fan–Wollinger–Gong (Table IV of the CACR 2006-38 technical report) lists the
curve assumptions of each in a dedicated column; the normal form above is
quoted from their own Table VII.

| Source | Venue | Curve | ADD (3+3) | DBL (deg 3) | I + M+S |
|---|---|---|---|---|---|
| Kuroki–Gonda–Matsuo–Chao–Tsujii 2002 | SCIS 2002 | Fp, h=0, f₆=0 | 1I + 81M/S | 1I + 74M/S | 81 / 74 |
| Gonda–Matsuo–Aoki–Chao–Tsujii 2004/05 | SCIS 2004; IEICE Trans. E88-A(1) | Fp, h=0, f₆=0 | 1I + 70M/S | 1I + 71M/S | 70 / 71 |
| Guyot–Kaveh–Patankar 2004 | J. Ramanujan Math. Soc. 19(2), 75–115 | Fp, h=0, f₆=0 | 1I + 64M + 6S | 1I + 61M + 9S | 70 / 70 |
| Nyukai–Matsuo–Chao–Tsujii 2006 | IEICE Tech. Rep. ISEC2006-5 (Japanese; as reported in FWG Table IV) | Fp, h=0, f₆=0 | 1I + 67M/S | 1I + 68M/S | **67 / 68** |

Notes, per source:

- **Kuroki et al. 2002** made the first extension of Harley's algorithm to
  genus 3.
- **Gonda et al. 2004** added Toom-style multiplication and "virtual
  polynomial multiplication" (Karatsuba applied twice across multiply-and-add
  sequences — the shape the thesis's T13 recipe descends from).
- **Guyot–Kaveh–Patankar 2004** compute the resultant and pseudo-inverse
  together via (implicit) Cramer's rule — the lineage of the thesis's
  almost-inverse section — and cover both odd and even characteristic,
  "applicable to almost all hyperelliptic curves of genus 3". **This is the
  standard genus-3 ramified reference and it is absent from
  `Thesis/mylib.bib`**; anything citing it from this repository must add the
  entry.
- **Nyukai et al. 2006** improved the resultant computation in Harley-style
  addition and hold the best published combined count for the frequent-case
  ADD. The report is in Japanese and was not independently opened; both
  figures are as reported by FWG's Table IV.
- **Wollinger–Pelzl–Paar 2005** (IEEE Trans. Computers 54(7), 861–872) also
  publish an "Fp-general" row (1I + 70M + 6S / 1I + 62M + 10S) — but for
  curves with `hᵢ ∈ F₂`, i.e. h ≠ 0. Over odd characteristic h can always be
  eliminated, so that row measures a form no odd-characteristic implementation
  would use; it is **excluded from the odd-char baseline** here and belongs to
  the char-2 comparison below.

After 2006 the odd-characteristic affine trail goes cold: a 2026-08 search
(2010–2026) finds no published improvement on these counts. Sutherland's
ANTS-XIII paper (2019) confirms the situation from the outside — its abstract
addresses the general (split) case precisely because "for curves with a
rational Weierstrass point, fast explicit formulas are well known and widely
available". The frequent-case bar this repository has to clear is therefore
**67 combined M+S for ADD (Nyukai), 68 for DBL (Nyukai), with GKP at 70/70 as
the best fully-published (non-survey-attributed) figures.**

## The published record, characteristic 2

For PR7/PR8 (this repository's ch2 cells, still to be derived). All from FWG
Table IV unless marked:

| Source | Curve | ADD | DBL |
|---|---|---|---|
| Wollinger–Pelzl–Paar 2005 | F2n, hᵢ ∈ F₂, f₆=0 | 1I + 65M + 6S | 1I + 53M + 10S |
| Wollinger–Pelzl–Paar 2005 | F2n, h=1, f₆=0 | 1I + 65M + 6S | 1I + 14M + 11S |
| Guyot–Kaveh–Patankar 2004 | F2n, deg h=3, h₂=0 | 1I + 62M + 5S | 1I + 63M + 9S |
| Guyot–Kaveh–Patankar 2004 | F2n, deg h=3, f₆=0 | 1I + 64M + 4S | 1I + 64M + 5S |
| Avanzi–Thériault–Wang 2006 (CACR 2006-07) | F2n, h=1 | 1I + 57M + 6S | 1I + 11M + 11S |
| Fan–Wollinger–Gong 2006/07 | F2n, h=X³, f₅=f₄=f₃=0 | 1I + 60M + 5S | 1I + 26M + 11S (f₆ small) |
| Fan–Wollinger–Gong 2006/07 | F2n, h=h₂X², f₅=f₃=f₂=0 | 1I + 58M + 6S (h₂ small) | 1I + 20M + 12S (h₂=1, f₆ small) |

FWG's own contribution is char-2 affine formulas for all four `deg h`
families, inversion-free (projective) formulas for both field types (Fp,
h=0, f₆=0: ADD 123M + 7S, DBL 107M + 10S, mixed ADD 104M + 6S — their Table
V), and the only published **low-degree-case** set over Fp (their Table I:
ADD 3+2→3 at 1I + 44M, ADD 3+1→3 at 1I + 21M, ADD 1+2→3 at 1I + 18M, DBL of a
degree-1 divisor at 1I + 11M, degree-2 at 1I + 28M) — the natural external
reference for this repository's non-typical branches, which no other source
covers at all.

**Citation warning, on record in the merge plan:** `Thesis/mylib.bib`'s
`fan_g3_2006` entry carries the IET journal title (*"… over binary fields"*,
IET Information Security 1(2), 65–81, 2007). The odd-characteristic material
and Table IV quoted here are in the fuller CACR 2006-38 technical report
(*Efficient Explicit Formulae for Genus 3 Hyperelliptic Curve Cryptosystems*,
41 pp., <https://cacr.uwaterloo.ca/techreports/2006/cacr2006-38.pdf>). Cite
the tech report for odd-characteristic claims and the IET version for char-2
ones.

## Adjacent, not directly comparable

- **Nagao 2000** (ANTS-IV, LNCS 1838, 439–448): polynomial-arithmetic-level
  improvements to the group law for arbitrary genus; a technique source (the
  thesis cites it), not a complete genus-3 formula set.
- **Sutherland 2019** (*Fast Jacobian arithmetic for hyperelliptic curves of
  genus 3*, ANTS-XIII, Open Book Series 2; arXiv:1607.08602): split model —
  the thesis's own comparison target for genus-3 split, and the source of the
  1M : 3A trade rule used throughout this repository. Cited here for the
  state-of-the-art statement quoted above, not for ramified counts.
- **Khuri-Makdisi 2018** (*On Jacobian group arithmetic for typical divisors
  on curves*, Research in Number Theory 4(1)): arbitrary-genus typical-divisor
  arithmetic in the linear-algebra model; asymptotically interesting, not
  competitive with hand-optimised genus-3 explicit formulas.
- **MacNeil–Jacobson–Scheidler** (`evan_g3`, ANTS-XIV): genus-3
  **non-hyperelliptic** curves; in the bibliography, out of scope here.
- Post-2006 genus-3 activity found by the search is Kummer-variety/height
  material (e.g. Stoll's explicit genus-3 hyperelliptic Kummer theory), not
  affine group-law formulas.

## The thesis's own deferral, resolved

`Thesis/chapter7.tex` and `chapter1.tex` (contributions list) defer ramified
genus-3 formulas to "ongoing work … by a student supervised by the author",
promising them "in a forthcoming paper". As of 2026-08-07 no such publication
exists: searches for it return only the thesis itself and the split-model
Balanced NUCOMP publication. The work-in-progress materialised as
`github.com/amasgari/genus3-hyperelliptic-curve-explicit-formulas`, which this
repository audited and imported (merge-plan PR2). This document and the
efficiency PRs that follow it are the continuation of that deferred thread.

## Where this repository stands (measured 2026-08-07)

Measured by the audit harness on the imported formulas; tool named per row.
Ranges are executed-count ranges across random inputs on the named branch.

| Operation | File | Frequent case, measured | Tool |
|---|---|---|---|
| ADD (3+3, gcd 1) | `arb_ramifiedG3_ADD.mag` | 64–75M, 12–23S, 1I, ~97A | `drive-deg33add-opcount.py` (n=329) |
| ADD (3+3, gcd 1) | `nch2_ramifiedG3_ADD.mag` (h=0, **f₆ still live**) | 62–65M, 12–15S, 1I, 79A | `opcount-odd-add.py` (n=152) |
| DBL (deg 3, typical) | `arb_ramifiedG3_DBL.mag` | 72M, 5S, 1I, 114A (no variance over 150 samples) | `dbl_opcount.py` |
| DBL (deg 3, typical) | nch2 — **file does not exist**; the family borrows arb's DBL | 72M, 5S, 1I, 114A + the h-terms it needn't pay | `dbl_opcount.py` |

The f₆ depression the entire published record assumes (and this repository's
nch2 file does not yet apply — merge-plan PR15/PR17) is worth, measured:
3M + 4A on the generic path, 3M + 4A on the degree-1-gcd path, 2M + 3A in
case #2.4 (`opcount-odd-add.py`, f₆-column; soundness-validated separately by
`vfy-odd-f6-opcount.py`).

### The comparison that matters

Odd characteristic, frequent case, in the only cross-source unit (I + M+S
combined; our measured midpoints):

| | ADD | DBL |
|---|---|---|
| Best published (Nyukai 2006, as reported) | 1I + 67 | 1I + 68 |
| Best fully published (GKP 2004) | 1I + 70 | 1I + 70 |
| This repo, nch2 today (f₆ live) | 1I + 74–80 | 1I + 77 (borrowed arb DBL) |

**This repository's genus-3 ramified formulas are currently behind the
2004–2006 state of the art by roughly 7–13 combined operations on ADD and
7–9 on DBL.** Three caveats keep this honest rather than alarming: the
substrates differ (our figures are executed counts including every
coefficient product; the published figures are static frequent-case counts on
two-coefficient curves); our files are complete over all input cases with
exactly one inversion, which no prior work except FWG's low-degree tables
even attempts; and no prior work counts additions, where the thesis's
methods concentrate their gains.

The sanity flag from the merge plan points the same direction: ramified
arithmetic should be cheaper than split arithmetic at the same genus (no
balancing, no adjust steps), yet the thesis's published **split** nch2 rows —
ADD 65M + 3S + 85A, DBL 72M + 4S + 97A (`chapter6.tex`, frequent-case tables)
— sit at or below today's ramified measurements. A correct, complete, but
unoptimised port is exactly what the audit ledger already suggested
(ODDADD-19 alone wastes 6M + 1S per generic addition; the f₆ depression
another 3M + 4A; ODDADD-20a/13 another 2M).

### Verdict per operation

- **arb ADD**: the one structural gap versus both the literature and this
  repository's own DBL — it builds the full 9-entry adjugate with a 9M
  matrix–vector product where the DBL in the same directory already uses the
  first-column + Karatsuba-twice shape (Gonda's "virtual multiplication", the
  thesis's T13). Closing that is merge-plan PR14/PR16 work.
- **arb DBL**: already T13-shaped; 72M + 5S measured against GKP's 61M + 9S
  static leaves ~7 combined operations to find (ARBDBL-06/09 are the recorded
  candidates).
- **nch2 ADD**: apply the depression (3M + 4A) and the ODDADD ledger
  (≥ 7M + 1S recorded); mid-60s combined is plausible, i.e. at or below the
  Nyukai bar — merge-plan PR15/PR17.
- **nch2 DBL**: does not exist; specialising the improved arb DBL under
  h = 0, f₆ = 0 (merge-plan PR6) competes against Nyukai's 68 / GKP's 70.
- **ch2 ADD/DBL**: to be created (merge-plan PR7/PR8) against the char-2
  table above; this repository's derived normal form (deg h = 3,
  `f = x⁷ + f₂x² + f₁x + f₀`) is closest to FWG's `h = X³` family
  (1I + 60M + 5S / 1I + 26M + 11S), which is the row to beat.

## References

- J. Kuroki, M. Gonda, K. Matsuo, J. Chao, S. Tsujii, "Fast Genus Three
  Hyperelliptic Curve Cryptosystems," SCIS 2002, IEICE Japan, 2002.
- M. Gonda, K. Matsuo, K. Aoki, J. Chao, S. Tsujii, "Improvements of Addition
  Algorithm on Genus 3 Hyperelliptic Curves and Their Implementation," SCIS
  2004; IEICE Trans. Fundamentals E88-A(1), 2005.
- C. Guyot, K. Kaveh, V. M. Patankar, "Explicit Algorithm for the Arithmetic
  on the Hyperelliptic Jacobians of Genus 3," J. Ramanujan Math. Soc. 19(2),
  75–115, 2004. *(Not in `Thesis/mylib.bib`.)*
- T. Wollinger, J. Pelzl, C. Paar, "Cantor versus Harley: Optimization and
  Analysis of Explicit Formulae for Hyperelliptic Curve Cryptosystems," IEEE
  Trans. Computers 54(7), 861–872, 2005.
- R. M. Avanzi, N. Thériault, Z. Wang, "Rethinking Low Genus Hyperelliptic
  Jacobian Arithmetic over Binary Fields," CACR Tech. Report 2006-07, 2006.
- J. Nyukai, K. Matsuo, J. Chao, S. Tsujii, "On the resultant computation in
  the addition Harley algorithms on hyperelliptic curves," IEICE Tech. Report
  ISEC2006-5, May 2006 (in Japanese; counts as reported by FWG Table IV).
- M. Katagi, T. Akishita, I. Kitamura, T. Takagi, "Efficient Hyperelliptic
  Curve Cryptosystems Using Theta Divisors," IEICE Trans. Fundamentals
  E89-A(1), 151–160, 2006.
- X. Fan, T. Wollinger, G. Gong, "Efficient Explicit Formulae for Genus 3
  Hyperelliptic Curve Cryptosystems," CACR Tech. Report 2006-38,
  <https://cacr.uwaterloo.ca/techreports/2006/cacr2006-38.pdf>; journal
  version "… over binary fields," IET Information Security 1(2), 65–81, 2007.
- K. Nagao, "Improving Group Law Algorithms for Jacobians of Hyperelliptic
  Curves," ANTS-IV, LNCS 1838, 439–448, 2000.
- A. V. Sutherland, "Fast Jacobian arithmetic for hyperelliptic curves of
  genus 3," ANTS-XIII, Open Book Series 2, 2019; arXiv:1607.08602.
- K. Khuri-Makdisi, "On Jacobian group arithmetic for typical divisors on
  curves," Research in Number Theory 4(1), 2018.
- S. A. Lindner, "Improvements to Divisor Class Arithmetic on Hyperelliptic
  Curves," PhD thesis, University of Calgary, 2020 (`Thesis/` in this
  repository).
