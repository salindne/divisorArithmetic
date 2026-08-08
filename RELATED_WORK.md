# Related work: genus-3 ramified-model explicit formulas

The baseline against which this repository's genus-3 ramified formulas
(`g3/ramifiedModel/`) are to be judged. Compiled 2026-08-07/08, before any
efficiency work on those formulas, so that improvements are measured against
the published state of the art rather than only against this repository's own
history. The split-model figures appear only for scale; the thesis
(`Thesis/chapter6.tex`) already covers that comparison.

Every operation count carries its source. Counts measured by this repository's
tooling say so and name the tool. Counts taken from a publication name the
table. Counts **derived by us** from a publication's printed formulas — which
is how every addition count in this document for prior work was obtained,
because no prior author reports one — are marked as derived, with the method in
the [appendix](#appendix-deriving-addition-counts-from-the-published-formulas).

## Two things that constrain every comparison here

**1. No prior work counts an arbitrary field.** Every published genus-3
ramified count is for one of two specialised settings: Fp with `h = 0` and
`f₆ = 0`, or F2n with a fixed shape of `h`. Nothing in the literature covers
the arbitrary-characteristic case at all. So the comparison runs in three
separate lanes, and this repository's **arb** family has no external baseline
in existence — that absence is itself a finding, not a gap in this survey.

**2. All prior work is frequent-case only.** Every source computes the generic
input and punts everything else to Cantor's algorithm; the tables say so in
their own step lists ("If r = 0 then call the Cantor algorithm"). There are no
published special-case counts to compare against, anywhere. Every row below is
therefore frequent-case-scoped by necessity, and completeness — every case
computed explicitly, exactly one inversion, no Cantor fallback — is an
algorithmic property of this repository's formulas that the published record
does not price at all. The lone partial exception is FWG's Fp low-degree
tables, which do give explicit mixed-degree formulas; they appear in the Fp
lane below.

## Counting conventions

**This repository / the thesis** (`Thesis/chapter6.tex`, Field Operation Costs
section): `M` multiplication, `S` squaring, `C` multiplication by a curve
coefficient, `A` addition/subtraction, `I` inversion. Division by 2 counts as
an A. A multiplication is never traded for more than 3 additions. Additions are
counted at all — explicitly "unlike many previous works".

**The prior literature** (2000–2006) counts `I`, `M`, `S` only; the two
Japanese-school papers report a combined `M/S` figure. **No prior work reports
A or C.** So:

- the only unit directly comparable across every source is **I + combined M+S**;
- **A is recoverable for any source that prints its formulas** — done below for
  all fifteen Fan–Wollinger–Gong appendix tables, including their reprint of
  Nyukai's frequent-case formulas, which is the best published count;
- C cannot be separated in prior work and is folded into M throughout.

**The measured counts for this repository** come from the audit harness
(`/Users/s3b/Dev/divisor-audits/g3ram/harness/`), which executes the actual
Magma source per branch and counts operations as they happen. It has **no C
column** (coefficient products count as M) and reports executed counts; ranges
are data-dependent short-circuits, not uncertainty. The audited snapshot is
byte-identical to the imported formulas modulo the PR2 renames, PR4's
comment-only pass and PR5's dispatch guard, none of which touch a formula
statement.

---

## Lane 1 — Fp, odd characteristic, `h = 0` and `f₆ = 0`

Every published odd-characteristic genus-3 formula set uses the depressed
normal form `y² = x⁷ + f₅x⁵ + f₄x⁴ + f₃x³ + f₂x² + f₁x + f₀` (via
`x → x − f₆/7`, valid for characteristic ≠ 7). Curve assumptions are quoted
from FWG's Table IV, which prices each prior work in a dedicated
curve-properties column.

| Source | Venue | ADD (3+3) | DBL (deg 3) | A derived here |
|---|---|---|---|---|
| Kuroki–Gonda–Matsuo–Chao–Tsujii 2002 | SCIS 2002 | 1I + 81M/S | 1I + 74M/S | formulas not in an open copy |
| Gonda–Matsuo–Aoki–Chao–Tsujii 2004/05 | SCIS 2004; IEICE E88-A(1) | 1I + 70M/S | 1I + 71M/S | formulas not in an open copy |
| Guyot–Kaveh–Patankar 2004 | J. Ramanujan Math. Soc. 19(2) | 1I + 64M + 6S | 1I + 61M + 9S | formulas not in an open copy |
| **Nyukai–Matsuo–Chao–Tsujii 2006** | IEICE ISEC2006-5 (Japanese) | **1I + 67M** | **1I + 68M** | **ADD 105A, DBL 93A** |

**Nyukai holds the best published frequent-case count, and its formulas are
recoverable**: FWG reprint them in full as their Tables XVII (addition) and
XVIII (doubling), attributed to reference [86], with per-step costs summing to
exactly the 1I + 67M and 1I + 68M that Table IV reports. That is what makes the
A derivation possible for the one row that matters most.

Guyot–Kaveh–Patankar is the standard genus-3 ramified reference and is
**absent from `Thesis/mylib.bib`**; anything citing it from this repository
must add the entry. Wollinger–Pelzl–Paar's "Fp-general" row (1I + 70M + 6S /
1I + 62M + 10S) is excluded from this lane: it assumes `hᵢ ∈ F₂`, i.e. h ≠ 0,
which no odd-characteristic implementation would use since h is always
eliminable there. It belongs to lane 2.

### FWG's low-degree Fp formulas — the only published non-typical counts

| Operation | Published | A derived here |
|---|---|---|
| ADD 3+2→3 | 1I + 44M | 63A |
| ADD 3+1→3 | 1I + 21M | 28A |
| ADD 1+2→3 | 1I + 18M | 19A |
| DBL 1→2 | 1I + 11M | 12A |
| DBL 2→3 | 1I + 28M | 44A |

### Where this repository stands in this lane

The comparable family is **nch2** — but only in its post-depression form
(`h = 0` *and* `f₆ = 0`), which is what the merge plan's PR17 produces. Today's
file keeps `f₆` live, so it implements a curve form **no published baseline
uses**; its numbers are given as current state, not as a like-for-like row.

| | M + S combined | A |
|---|---|---|
| Nyukai 2006, ADD 3+3 (best published) | 67 | 105 *(derived)* |
| our `nch2` ADD, Deg3 typical, today (f₆ live) | 74–80 | **79** |
| Nyukai 2006, DBL deg 3 | 68 | 93 *(derived)* |
| our DBL (arb DBL borrowed — see lane 3) | 77 | 114 |

**The headline, which reverses the reading from M+S alone: this repository is
behind on multiplications and well ahead on additions.** Our frequent-case
addition spends 7–13 more combined M+S than Nyukai's and **26 fewer additions**
(79 against 105). Under the thesis's own 1M : 3A trade rule those 26 additions
are worth roughly 8.7M, so the two are within a multiplication or so of each
other *today* — before any of the recorded efficiency work.

That work is already itemised and, on this branch, worth **10M + 1S + 15A**:
the f₆ depression (3M + 4A, measured by `opcount-odd-add.py`), ODDADD-19's two
dead lines (6M + 1S + 11A, probe-validated), and ODDADD-20a's leftover h-term
(1M). If all of it lands as recorded — PR14/PR15 must verify each item, that is
their job — this lane's addition lands near 64–70 combined M+S with ~64A,
against Nyukai's 67 and 105. The doubling comparison cannot be made until
`nch2_ramifiedG3_DBL.mag` exists (merge-plan PR6); the borrowed arb DBL pays
h-terms this lane's curves do not have.

---

## Lane 2 — F2n, characteristic 2

For merge-plan PR7/PR8, which will create this repository's ch2 formulas. **We
have no entry in this lane yet**: `even_ramifiedG3_ADD.m` was the arb file
renamed, and was dropped on import.

| Source | Curve | ADD | DBL | A derived here |
|---|---|---|---|---|
| Wollinger–Pelzl–Paar 2005 | hᵢ ∈ F₂, f₆=0 | 1I + 65M + 6S | 1I + 53M + 10S | formulas not in an open copy |
| Wollinger–Pelzl–Paar 2005 | h=1, f₆=0 | 1I + 65M + 6S | 1I + 14M + 11S | " |
| Guyot–Kaveh–Patankar 2004 | deg h=3, h₂=0 | 1I + 62M + 5S | 1I + 63M + 9S | " |
| Guyot–Kaveh–Patankar 2004 | deg h=3, f₆=0 | 1I + 64M + 4S | 1I + 64M + 5S | " |
| Avanzi–Thériault–Wang 2006 | h=1 | 1I + 57M + 6S | 1I + 11M + 11S | " |
| **FWG 2006/07** | **h = X³**, f₅=f₄=f₃=0 | 1I + 60M + 5S | 1I + 26M + 11S (f₆ small) / 1I + 30M + 11S (f₆ arb) | **ADD 89A, DBL 36A** |
| FWG 2006/07 | h = h₂X², f₅=f₃=f₂=0 | 1I + 58M + 6S (h₂ small) / 1I + 60M + 5S (arb) | 1I + 24M + 12S (h₂=1) / 32M + 10S / 36M + 10S | ADD 85A, DBL 31A |
| FWG 2006/07 | h = h₁X, f₆=f₄=f₁=0 | 1I + 57M + 6S (h₁ small) / 58M + 6S (arb) | 1I + 13M + 13S (h₁=1) / 16M + 12S / 20M + 12S | ADD 79A, DBL 23A |
| FWG 2006/07 | h = h₀, f₆=f₅=f₄=f₂=0 | 1I + 57M + 6S | 1I + 10M + 11S (h₀=1) / 11M + 11S / 15M + 11S | ADD 75A, DBL 20A |

**The row to beat is FWG's `h = X³` family** (1I + 60M + 5S + 89A for addition,
1I + 30M + 11S + 36A for doubling): this repository's derived char-2 normal
form is `deg h = 3` with `f = x⁷ + f₂x² + f₁x + f₀`, and `h = X³` is the
closest published shape. Note the striking asymmetry these derived A counts
expose — char-2 doublings are cheap in M but the addition still costs ~89A,
so the addition is where an A-conscious method has room.

FWG's own contribution also includes inversion-free (projective) formulas for
both field types (Fp, h=0, f₆=0: ADD 123M + 7S, DBL 107M + 10S, mixed ADD
104M + 6S — their Table V), out of scope for this repository's affine work.

---

## Lane 3 — arbitrary characteristic

**There is no published baseline. Nothing in the literature gives genus-3
ramified explicit formulas valid over an arbitrary field**; every source
specialises to Fp-with-h=0 or to a fixed char-2 shape of h. This repository's
`arb_ramifiedG3_{ADD,DBL}.mag` can therefore only be judged:

- **internally**, against its own specialisations (an arb formula should cost
  its specialisation plus the h-terms, and no more);
- **against the thesis's own split-model arb rows** for scale (`chapter6.tex`
  frequent-case tables: Degree-3 ADD 65M + 3S + 87A + 12C, Degree-3 DBL
  73M + 3S + 101A + 19C) — with the standing sanity flag that ramified
  arithmetic ought to be *cheaper* than split at equal genus, having no
  balancing and no adjust steps;
- **by the technique checklist** of `Thesis/chapter4.tex`, which is merge-plan
  PR14's method.

Measured today (audit harness, frequent case):

| Operation | Measured |
|---|---|
| `arb` ADD, Deg3 typical | 64–75M, 12–23S, 1I, ~97A |
| `arb` DBL, Deg3 typical | 72M, 5S, 1I, 114A (no variance over 150 samples) |

Against the thesis's split Degree-3 DBL (73M + 3S + 101A), the ramified arb DBL
at 72M + 5S + 114A is **not** clearly cheaper despite having strictly less work
to do. That is the sanity flag firing, and it is the substance of PR14.

---

## Adjacent, not directly comparable

- **Nagao 2000** (ANTS-IV, LNCS 1838): arbitrary-genus group-law improvements;
  a technique source, not a genus-3 formula set.
- **Sutherland 2019** (ANTS-XIII; arXiv:1607.08602): split model — the thesis's
  comparison target for genus-3 split, and the source of the 1M : 3A trade rule
  used throughout this repository. Its abstract confirms the state of this
  survey from the outside: it addresses the general case precisely because "for
  curves with a rational Weierstrass point, fast explicit formulas are well
  known and widely available".
- **Khuri-Makdisi 2018**: arbitrary-genus typical-divisor arithmetic in the
  linear-algebra model; asymptotic, not competitive with hand-optimised
  genus-3 explicit formulas.
- **MacNeil–Jacobson–Scheidler** (ANTS-XIV): genus-3 **non-hyperelliptic**.
- Post-2006 genus-3 activity found by search (2010–2026) is Kummer-variety and
  height material, not affine group-law formulas. **No published improvement on
  the 2006 odd-characteristic counts exists.**

## The thesis's own deferral, resolved

`Thesis/chapter7.tex` and `chapter1.tex` defer ramified genus-3 formulas to
"ongoing work … by a student supervised by the author", promising them "in a
forthcoming paper". As of 2026-08-08 no such publication exists; searches
return only the thesis itself and the split-model Balanced NUCOMP work. The
work-in-progress materialised as
`github.com/amasgari/genus3-hyperelliptic-curve-explicit-formulas`, which this
repository audited and imported (merge-plan PR2). This document and the
efficiency PRs that follow are the continuation of that deferred thread.

---

## Appendix: deriving addition counts from the published formulas

No prior author publishes an A count. Where a source prints its formulas
step by step, A is recoverable by counting the operations in the printed
right-hand sides. This was done for all fifteen Fan–Wollinger–Gong appendix
tables (script: `fwg_acount.py`, kept with the audit harness).

**Rules**, following the thesis convention (`Thesis/chapter6.tex`;
`latexTables/latexConverter.py:105`, `:112`, `:163`):

1. every binary `+` or `−` in a right-hand side is 1A;
2. a **leading** unary minus is free (`t7 = −(t4t5 + t3t6)` is 1A, not 2);
3. each division by 2 is 1A;
4. multiplication by the literal 2 is tallied **separately**, since the thesis
   has no general rule for it — the tables above use rules 1–3 only. Counting
   each as a doubling would add: Nyukai ADD +3, Nyukai DBL +9, FWG ADD 3+2→3
   +4, ADD 3+1→3 +2, ADD 1+2→3 +3, DBL 1→2 +8, DBL 2→3 +7. The char-2 tables
   have none;
5. Input/Output polynomial declarations are not arithmetic and are excluded;
6. exponents rendered with a different minus glyph (`(rs′₂)⁻¹`) are inversions,
   not subtractions, and are excluded.

**Validation.** Three independent checks, all passing:

- **Per-step multiplication costs sum to the published total** in every table
  (e.g. Nyukai ADD: 15 + 10 + 7 + 4 + 13 + 8 + 7 + 3 = 67M, matching its Sum
  row and Table IV). A dropped assignment would show up here as a shortfall.
- **Every table's Sum row matches its own caption's family** and Table I/IV's
  published values — the check that caught an early boundary error in which two
  of the multi-variant char-2 tables had been silently merged.
- **Hand recount of the two largest steps** of the Nyukai addition against the
  raw text: step 1 gives 12A and step 4 gives 28A + 2 divisions by 2, both
  matching the script.

**Not derivable.** Kuroki 2002, Gonda 2004/05, Guyot–Kaveh–Patankar 2004 and
Wollinger–Pelzl–Paar 2005 print their formulas only in sources with no open
copy. Their A counts are recoverable by anyone with library access, using the
rules above; the table rows are marked so this can be extended rather than
guessed.

### Source access

| Source | Canonical | Open copy |
|---|---|---|
| Fan–Wollinger–Gong 2006 (tech report) | — | <https://cacr.uwaterloo.ca/techreports/2006/cacr2006-38.pdf> — **free; the source of every derived count here** |
| Fan–Wollinger–Gong 2007 (journal) | doi:10.1049/iet-ifs:20070003 | paywalled; the tech report supersedes it in coverage |
| Nyukai et al. 2006 | IEICE Tech. Rep. ISEC2006-5 | not open; in Japanese. **Formulas reprinted in FWG Tables XVII–XVIII**, which is how its A counts were derived |
| Guyot–Kaveh–Patankar 2004 | J. Ramanujan Math. Soc. 19(2), 75–115 | none found. The key gap — the only fully published Fp frequent case |
| Gonda et al. 2005 | IEICE Trans. Fund. E88-A(1) | paywalled |
| Kuroki et al. 2002 | SCIS 2002, IEICE Japan | not online |
| Wollinger–Pelzl–Paar 2005 | doi:10.1109/TC.2005.109 | IEEE paywall; a copy exists on academia.edu behind a login |
| Avanzi–Thériault–Wang 2006 | CACR 2006-07 | <https://cacr.uwaterloo.ca/techreports/2006/cacr2006-07.pdf> |
| Sutherland 2019 | ANTS-XIII, OBS 2 | <https://arxiv.org/abs/1607.08602> |
| Lindner 2020 (this thesis) | UCalgary | `Thesis/` in this repository |

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
  ISEC2006-5, May 2006 (in Japanese).
- M. Katagi, T. Akishita, I. Kitamura, T. Takagi, "Efficient Hyperelliptic
  Curve Cryptosystems Using Theta Divisors," IEICE Trans. Fundamentals
  E89-A(1), 151–160, 2006.
- X. Fan, T. Wollinger, G. Gong, "Efficient Explicit Formulae for Genus 3
  Hyperelliptic Curve Cryptosystems," CACR Tech. Report 2006-38; journal
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
