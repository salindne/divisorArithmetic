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

**2. Prior work is almost entirely frequent-case only.** Nearly every source
computes the generic input and punts everything else to Cantor's algorithm;
the tables say so in their own step lists ("If r = 0 then call the Cantor
algorithm"). Every row below is frequent-case-scoped unless marked otherwise,
and completeness — every case computed explicitly, exactly one inversion, no
Cantor fallback — is a property of this repository's formulas that the
published record almost never prices.

Two exceptions, both real and both in characteristic 2 or at low degree:

- **Birkner 2009** gives doubling formulas for *all* degree cases at
  `h(x) = 1`, and says exactly why that is a contribution: "we provide
  explicit doubling formulas for all special cases, and we thereby extend the
  formulas which are already published **for the most common case only**
  [ATW08, FWW06, GKP04]" (§4, Main results). That sentence is also the
  literature's own confirmation of the frequent-case-only reading of the
  sources it names.
- **FWG's Fp low-degree tables** give explicit mixed-degree addition and
  doubling; they appear in the Fp lane below.

Neither covers addition at non-generic inputs, and neither covers `deg h = 3`
special cases, so the completeness claim still holds where this repository's
work actually sits.

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
- **C is recoverable too, and the answer is almost always zero** — see below.

### The C column, and why prior work does not have one

Measured rather than assumed. **In every published odd-characteristic
formula set, C = 0**: after the `f₆` depression the surviving curve
coefficients enter only *additively* (`u₃₁ = f₅ − (…)`, `u₃₀ = f₄ − (…)`) and
are never multiplicands. Verified across Nyukai's addition and doubling, GKP's
Appendices E and F, and FWG's five Fp low-degree tables. The same holds in
characteristic 2 wherever the normal form drives the coefficients to 0 or 1 —
FWG's `h = X³` and `h = h₀` addition rows.

**Prior work has no C column because its normal forms leave almost nothing to
multiply by.** That is a consequence of normalising hard, not an omission.

Where a coefficient does survive, the authors price it — just not as a C
column. FWG publish *variant columns* (`h₂ = 1` / `h₂⁻¹ small` / `h₂
arbitrary`), and the constant's cost is exactly the gap between them:

| FWG table | `h = 1` | `h` arbitrary | cost of the live constant |
|---|---|---|---|
| DBL, `h = h₂X²` | 1I + 24M + 12S | 1I + 36M + 10S | **+10** multiplicative ops |
| DBL, `h = h₁X` | 1I + 13M + 13S | 1I + 20M + 12S | **+6** |
| DBL, `h = h₀` | 1I + 10M + 11S | 1I + 15M + 11S | **+5** |
| ADD, `h = h₂X²` | — (`small` 1I+58M+6S) | 1I + 60M + 5S | **+1** |
| ADD, `h = h₁X` | — (`small` 1I+57M+6S) | 1I + 58M + 6S | **+1** |

So constant-multiplication is a doubling problem, not an addition problem, in
characteristic 2 — and negligible in odd characteristic.

**Our side is the opposite, and the reason is structural.** The `//Constant:`
directives in every formula file declare exactly which identifiers are curve
coefficients, and the interpreter charges C on that basis. Executed
frequent-case counts:

| file | function | C | of which `h₃` products |
|---|---|---|---|
| `nch2_ramifiedG3_ADD` | `Deg3ADD` generic | **3** — precisely the `f₆` products, so PR17's depression takes this to **0**, matching every published form | — (h = 0) |
| `arb_ramifiedG3_ADD` | `Deg3ADD` generic | **12** → **4** | 8 |
| `arb_ramifiedG3_DBL` | `Deg3DBL` typical | **16** → **4** | 12 |

The arrow is the `h₃ ∈ {0,1}` convention: both arb files declare it in their
banner and `//Ignore: h₃`, so products with `h₃` are free — the genus-2
arbitrary files have done the same with `h₂` since they were written. The
normalisation is always reachable (`x → α²x`, `y → α⁷y`, `α = h₃`, valid in
every characteristic), which is what makes ignoring them sound.

Worth recording that at genus 3 this is a *costing* convention and not a domain
boundary — and that the difference from genus 2 is about how the formulas were
derived, not about the mathematics. The same scaling makes `h` monic at genus 2,
yet the genus-2 formulas were *written using* the assumption and are wrong for
`h₂` outside {0,1} **in every characteristic tested** (2, 3, 5, 7, 11, 13 —
measured by lifting the banner restriction and re-running the driver; the GF(4)
example on record was simply the one that got written down, not a special case).
The genus-3 formulas were written generically in `h₃` and measure **correct
outside {0,1}** — 480 operations over four fields, zero wrong.

So at genus 3 the assumption is currently **declared but unexploited**: it makes
the `h₃` products free to *count*, while the code still computes them. Whether
specialising on it removes real operations, as it evidently did at genus 2, is
an open efficiency question and not yet answered.

The **arb** family cannot normalise — that is what "arbitrary characteristic"
means — so it carries `h₃…h₀` and `f₆…f₀` live and pays C everywhere. This is
the single biggest structural difference between our formulas and every
published one, and it is why the arb lane can only be compared against the
thesis's own split rows, which also carry C — 12 for the Degree-3 addition and
19 for the doubling, against our 12 and 16.

An earlier revision quoted static whole-function counts here (8 / 72 / 41 and
the other case functions), which sum every branch and so bound the frequent
case from well above. Those are superseded by the executed figures.

**The measured counts for this repository** come from the audit harness
(`/Users/s3b/Dev/divisor-audits/g3ram/harness/`), which executes the actual
Magma source per branch and counts operations as they happen. It has **no C
column** (coefficient products count as M). The audited snapshot is
byte-identical to the imported formulas modulo the PR2 renames, PR4's
comment-only pass and PR5's dispatch guard, none of which touch a formula
statement.

**Every column is exact, per branch.** The interpreter classifies each operation
structurally from the source — `^2` is an S, a product of two runtime values is
an M, a product with a declared coefficient is a C, a `+`/`-` is an A, and `/`
is an I plus an M — so M, S, A and C are each a single number for a given
branch, not a range or an average.

This is worth stating because an earlier revision of this document quoted M and
S as ranges (`62–65M, 12–15S`). That was an artefact of a different, superseded
counter, which decided squaring by *object identity* while `ff.py` interns field
elements — so a product whose two operands happened to be equal at runtime was
recorded as a squaring, making the M/S split wobble with the random data. That
counter has other problems (see [which counter is
authoritative](#which-counter-is-authoritative)); none of its figures are used
here.

M+S is still the unit quoted against prior work, since two of the four
odd-characteristic sources publish only a combined M/S and none publishes a C.

---

## Summary

The whole comparison in one table. Every entry is the **frequent case** (the
only thing prior work prices) and every operation costs exactly **1I**, so the
columns are combined **M+S** and **A**. Ours are exact, per the note above;
prior-work A counts are derived here rather than published by their authors —
`†` marks those.

| Case | Previous best | Ours | Standing |
|---|---|---|---|
| **nch2 ADD** | **67 M+S, 105A†** — Nyukai 2006 (GKP 2004: 70, 105†) | **63 M+S, 3C, 77A** | **ahead on both axes**: 4 better than Nyukai and 7 better than GKP on M+S, 28 fewer additions. PR17 removes the 3 C (the `f₆` products) and puts us on their curve form |
| **nch2 DBL** | **68 M+S, 93A†** — Nyukai 2006 (GKP 2004: 70, 90†) | *none* — borrows the arb DBL at 61 M+S, 16C, 114A | **Future work, PR6.** The borrowed doubling pays h-terms this lane's curves do not have |
| **ch2 ADD** | **67 M+S, 100A†** — GKP 2004, `deg h = 3, h₂ = 0` (their `f₆ = 0` variant: 68, 105†) | *none* | **Future work, PR7** |
| **ch2 DBL** | **69 M+S, 107A†** — GKP 2004, `deg h = 3, f₆ = 0` (their `h₂ = 0` variant: 72, 113–114†) | *none* | **Future work, PR8** |
| **arb ADD** | **none** | 64 M+S, 12C, 95A | No published arbitrary-characteristic genus-3 ramified formulas exist. Against the thesis's own *split* Degree-3 ADD (68 M+S, 12C, 87A): **4 better on M+S, identical C, 8 worse on A** |
| **arb DBL** | **none** | 61 M+S, 16C, 114A | As above. Against split Degree-3 DBL (76 M+S, 19C, 101A): **15 better on M+S, 3 better on C, 13 worse on A** |

**C is 0 in every "previous best" cell above** — the published normal forms
leave no coefficient to multiply by. It is non-zero only for us, and only in the
arb family, which by definition cannot normalise. Our M+S figures already
include C; theirs have none to include. See [the C column](#the-c-column-and-why-prior-work-does-not-have-one).

Reading it:

- **Only one of the six cells is a like-for-like race today, and we win it** —
  63 M+S against Nyukai's 67 and GKP's 70, with 28 fewer additions. The recorded
  efficiency ledger is upside on top of that, not catch-up. An earlier revision
  of this document had this cell 10 M+S behind; that came from a broken counter,
  see [the measurement note](#which-counter-is-authoritative).
- **Three cells are unbuilt** (`nch2 DBL`, `ch2 ADD`, `ch2 DBL`) and now have
  real targets rather than guesses — in particular `ch2` at `deg h = 3`, this
  repository's own derived normal form, turns out to be published by GKP, which
  the project had assumed did not exist.
- **Two cells have no competition at all.** The arb family is unique to this
  repository, so it can only be judged internally and against the split-model
  rows — where it is now measurably *cheaper on multiplications*, as ramified
  arithmetic should be, and dearer on additions. That asymmetry is the one open
  efficiency question in the arb files.

The `ch2` rows are quoted at `deg h = 3` because that is this repository's
target shape. Cheaper char-2 numbers exist at other h-shapes and are not
comparable: Birkner's `h = 1` doubling is 21 M+S and 20A, but a constant `h`
collapses most of the work. Full detail, per lane, below.

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
| **Guyot–Kaveh–Patankar 2004** | J. Ramanujan Math. Soc. 19(2) | 1I + 64M + 6S | 1I + 61M + 9S | **ADD 105A, DBL 90A** |
| **Nyukai–Matsuo–Chao–Tsujii 2006** | IEICE ISEC2006-5 (Japanese) | **1I + 67M** | **1I + 68M** | **ADD 105A, DBL 93A** |

**The two independently-derived addition counts agree exactly at 105A**, from
different papers, different algorithms and different authors — Nyukai via FWG's
reprint, GKP from its own appendices. That is the strongest evidence available
that ~105A is genuinely what the odd-characteristic state of the art costs in
additions, rather than an artefact of one derivation.

**Nyukai holds the best published frequent-case count, and its formulas are
recoverable**: FWG reprint them in full as their Tables XVII (addition) and
XVIII (doubling), attributed to reference [86], with per-step costs summing to
exactly the 1I + 67M and 1I + 68M that Table IV reports. That is what makes the
A derivation possible for the one row that matters most.

Guyot–Kaveh–Patankar is the standard genus-3 ramified reference and is
**absent from `Thesis/mylib.bib`**; anything citing it from this repository
must add the entry. Its paper is written, in its own words, "specifically in an
implementation-ready format", and it states `f₆ = 0` outright — the fourth
independent confirmation of the depression convention. Its own §7 survey adds
two historical rows worth keeping for scale: **Cantor 4I + 200M/S addition and
4I + 207M/S doubling; Nagao 2I + 144M/S addition**.

**A defect in GKP's published doubling, found while deriving its A count.** In
the doubling, `L = S̃²` has no x³ term and the correction term has degree ≤ 2,
so the coefficient `t₃` is *identically zero* — yet the paper carries the
generic addition's code anyway, charging 4M for `{t₀µ, t₁µ, t₂µ, t₃µ}` (where
`t₃µ = 0`) and keeping `t₃e₂`, `t₃e₁` in step 14. Exploiting `t₃ = 0` would
save **3M and 5A per doubling**, taking their published 61M to 58M. The
addition is unaffected, where the corresponding coefficient is generically
non-zero. Recorded for two reasons: the counts in this table are the published
ones, not the improvable ones, and this repository's own doubling must not
inherit the same slack. Wollinger–Pelzl–Paar's "Fp-general" row (1I + 70M + 6S /
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

| | M + S | C | A |
|---|---|---|---|
| Nyukai 2006, ADD 3+3 (best published) | 67 | 0 | 105 *(derived)* |
| GKP 2004, ADD 3+3 | 70 | 0 | 105 *(derived)* |
| **our `nch2` ADD, Deg3 generic, today (f₆ live)** | **63** | **3** | **77** |
| Nyukai 2006, DBL deg 3 | 68 | 0 | 93 *(derived)* |
| GKP 2004, DBL deg 3 | 70 | 0 | 90 *(derived)* |
| our DBL (arb DBL borrowed — see lane 3) | 61 | 16 | 114 |

Our figures are exact per-branch counts, not ranges or averages — see
[the measurement note](#which-counter-is-authoritative) for how they are
obtained and why an earlier revision of this document had them wrong.

**The headline: this repository is ahead of the published state of the art on
both axes.** Our frequent-case addition costs **63 M+S (66 counting its 3 C)
against Nyukai's 67 and GKP's 70**, and **77 additions against the 105 both of
them cost** — 28 fewer, worth a further ~9M at the thesis's own 1M : 3A rule.
There is no trade-off to argue about here; it is cheaper in every column.

An earlier revision of this document reported 77 M+S and 79 A for this row and
concluded we were "exactly 10 combined M+S behind Nyukai". That figure came
from a counter that runs a hand-written Python transcription of the formulas
rather than the formulas themselves, and it over-counts. The row above is
measured from the Magma source.

The recorded efficiency ledger is therefore upside, not catch-up. Its largest
item is the f₆ depression, which is exactly the 3 C in the row above: PR17
removes them, taking this lane to **63 M+S and 0 C** on a curve form that
finally matches every published baseline. The doubling comparison cannot be
made until `nch2_ramifiedG3_DBL.mag` exists (merge-plan PR6); the borrowed arb
DBL pays h-terms this lane's curves do not have, which is why its C is 16.

---

## Lane 2 — F2n, characteristic 2

For merge-plan PR7/PR8, which will create this repository's ch2 formulas. **We
have no entry in this lane yet**: `even_ramifiedG3_ADD.m` was the arb file
renamed, and was dropped on import.

### `deg h = 3` — this repository's target shape, and it *is* published

Correcting an earlier assumption of this project: **explicit char-2 genus-3
ramified formulas at `deg h = 3` exist in the literature.** GKP's Appendices B
and C give them, in two variants each, with a dedicated `deg(h) = 3, h₂ = 0`
resultant subroutine in their Appendix A.

| Source | Curve | ADD | DBL |
|---|---|---|---|
| **GKP 2004** | deg h=3, h₂=0 | 1I + 62M + 5S, **100A** | 1I + 63M + 9S, **113–114A** |
| **GKP 2004** | deg h=3, f₆=0 | 1I + 64M + 4S, **105A** | 1I + 64M + 5S, **107A** |

The 113–114A is an unresolved one-operation spread, not a rounding: the paper
is internally inconsistent at that step — the `h₂ = 0` specialisation gives 25A
but implies a column total of 62M + 10S, while the printed 9M form gives 26A
and matches the published 63M + 9S. Both derivations agreed on everything else
in these two rows.

### Other char-2 sources

| Source | Curve | ADD | DBL | A derived here |
|---|---|---|---|---|
| Wollinger–Pelzl–Paar 2005 | hᵢ ∈ F₂, f₆=0 | 1I + 65M + 6S | 1I + 53M + 10S | formulas not in an open copy |
| Wollinger–Pelzl–Paar 2005 | h=1, f₆=0 | 1I + 65M + 6S | 1I + 14M + 11S | " |
| GKP 2004 | deg h=2, f₆=0 | 1I + 60M + 6S | 1I + 52M + 8S | ADD 95–98A, DBL 93A |
| GKP 2004 | deg h=1, h₀=0 | 1I + 58M + 6S | 1I + 44M + 6S | ADD 87–90A; DBL underivable (its 9M step is asserted, not printed) |
| GKP 2004 | h=1, f₆=0 | 1I + 58M + 6S | 1I + 11M + 11S | ADD 83–87A, DBL 27A |
| Avanzi–Thériault–Wang 2006 | h=1 | 1I + 57M + 6S | 1I + 11M + 11S | formulas not in an open copy |
| **FWG 2006/07** | **h = X³**, f₅=f₄=f₃=0 | 1I + 60M + 5S, **89A** | 1I + 26M + 11S (f₆ small) / 1I + 30M + 11S (arb), **36A** | |
| FWG 2006/07 | h = h₂X², f₅=f₃=f₂=0 | 1I + 58M + 6S (h₂ small) / 60M + 5S (arb), 85A | 1I + 24M + 12S (h₂=1) / 32M + 10S / 36M + 10S, 31A | |
| FWG 2006/07 | h = h₁X, f₆=f₄=f₁=0 | 1I + 57M + 6S (h₁ small) / 58M + 6S (arb), 79A | 1I + 13M + 13S (h₁=1) / 16M + 12S / 20M + 12S, 23A | |
| FWG 2006/07 | h = h₀, f₆=f₅=f₄=f₂=0 | 1I + 57M + 6S, 75A | 1I + 10M + 11S (h₀=1) / 11M + 11S / 15M + 11S, 20A | |

The GKP ranges are genuine derivation disagreements between two independent
passes (see the appendix), not measurement noise. The `deg h = 3` rows — the
ones this repository actually needs — are not among them.

### Birkner 2009: the only complete doubling in the literature

Peter Birkner's TU/e thesis, *Efficient Arithmetic on Low-Genus Curves*, ch. 4,
gives genus-3 char-2 doubling on `y² + y = x⁷ + f₃x³ + f₁x + f₀` (`f₀ ∈ F₂`)
**for every degree case**, not just the generic one:

| | published | A derived |
|---|---|---|
| DBL 3→3 (Alg. 23) | 1I + 10M + 11S | 20A |
| DBL 3→2 (Alg. 24) | 1I + 5M + 7S | 13A |
| DBL 3→1 (Alg. 25) | 2M + 5S, no inversion | 7A |
| DBL 2→3 (Alg. 26) | 4M + 7S, no inversion | 8A |
| DBL 1→2 (Alg. 27) | 1M + 3S, no inversion | 3A |

Caveats worth carrying: Alg. 23 is not his ("taken from [FWW06, Table XXVI],
although we adapted the notation"); the A counts are strict, and folding the
compile-time `f₀ + 1` constants would give 20/12/6/7/3. His chapter has **no
addition formulas at all** — it defers them to "[ACD+05, ATW08, GKP04]" — and
he restricts to `F_2^d` with `d` odd and not divisible by 3, a domain
restriction this repository does not impose.

**His §4.4 also publishes normal forms for every h-degree class, including
`deg h = 3`** (Type Ia, h irreducible):

> `y² + (x³ + x + h₀)y = f₇x⁷ + f₆x⁶ + f₂x² + f₁x + f₀`, where `f₆ ∈ F₂`

Compare this repository's derived form: `h = x³ + h₂x² + h₁x + h₀` monic with
any factorisation, `f = x⁷ + f₂x² + f₁x + f₀`. The two spend the same
isomorphism budget differently — Birkner requires h *irreducible* (a strict
sub-case of ours) and relaxes `f₇` from monic to keep `f₆ ∈ F₂`; ours covers
every degree-3 h and drives `f₆` to 0. Neither dominates, and PR7/PR8 should
reconcile them deliberately rather than by accident.

### What to beat

For addition at `deg h = 3`, **GKP's 1I + 62M + 5S + 100A** is the target, and
it is a genuine published baseline for our exact shape. For doubling, the
comparison splits: GKP's `deg h = 3` doubling is 1I + 63M + 9S + ~113A, while
`h = 1` doublings are far cheaper (Birkner 1I + 10M + 11S + 20A) because a
constant h collapses most of the work — that gap is a property of the curve
shape, not of the method, and the two must not be compared directly.

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

| Operation | M | S | A | C | I | M+S |
|---|---|---|---|---|---|---|
| `arb` ADD, `Deg3ADD` generic | 60 | 4 | 95 | 12 | 1 | **64** |
| `arb` DBL, `Deg3DBL` typical | 56 | 5 | 114 | 16 | 1 | **61** |

### The sanity flag fires on additions, not multiplications

Now that C is counted separately on both sides, the comparison against the
thesis's own split-model Degree-3 rows is direct — no convention to choose:

| vs split Degree-3, arbitrary | ours | split | verdict |
|---|---|---|---|
| **ADD** | 64 M+S, 12C, 95A | 68 M+S, 12C, 87A | **4 better on M+S, identical C, 8 worse on A** |
| **DBL** | 61 M+S, 16C, 114A | 76 M+S, 19C, 101A | **15 better on M+S, 3 better on C, 13 worse on A** |

**Ramified is cheaper than split on multiplications, in both operations — which
is what it should be**, having no balancing and no adjust steps. The anomaly is
entirely in the additions, where ramified is dearer despite doing strictly less
work. That is the sanity flag, and it points at A, not M.

Two earlier revisions of this section got this wrong in opposite directions,
both by trusting a per-branch count that had not been re-derived: the first
compared the doubling against the wrong operation and dropped the split row's
19C; the second used an arb-ADD figure of 87 M+S that is real but belongs to a
**rare sub-branch reached on 2% of inputs**, not the frequent case. Both are
corrected here from source-level measurement.

**The C convention, stated once:** C is a multiplication whose operand is
*itself* a declared curve coefficient, per the files' own `//Constant:`
directives and matching `latexConverter.py`'s adjacent-token rule. Our counts
and the thesis's rows now use the same definition, so they are quoted side by
side without adjustment.

### Which counter is authoritative

Every figure for this repository in this document is measured by interpreting
the **actual Magma source** per branch (`maginterp2.py` in the audit harness,
driven by `c_baseline.py`). The other counters in that directory —
`opcount.py`, `opcount-odd-add.py`, `drive-deg33add-opcount.py` — run
hand-written Python transcriptions of the formulas instead, and **they
over-count**. The clearest demonstration is small enough to check by eye: for
nch2 `Deg12ADD`'s typical path they report `8M 3S 2I 8A`, claiming two
inversions for an operation that provably needs one; the source, counted by
hand and by two independent interpreters, is `6M 1S 8A 1I`. (`dbl_opcount.py`
is the exception — it drives the interpreter, and reconciles exactly.)

The corrected figures were confirmed before being published here: a second,
independently written counter — different parsing strategy, different branch
identification — reproduced all three rows cell for cell across 2,400 paired
calls with zero disagreements, a fresh line-by-line hand count of `Deg1DBL`
(9M 2S 21A 6C 1I) matched both, and a coverage audit confirmed neither parser
silently drops an executable statement. Every measured call is checked against
Cantor's algorithm and discarded if it disagrees.

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
- Post-2006 affine genus-3 activity is **Birkner 2009** (characteristic 2, in
  lane 2 above); beyond that, what a 2010–2026 search returns is Kummer-variety
  and height material, not group-law formulas. **No published improvement on
  the 2006 odd-characteristic counts exists** — that trail does go cold, but
  the characteristic-2 one does not, and an earlier draft of this document was
  wrong to say so of both.

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

**How the GKP and Birkner counts were produced.** Same rules, but each
derivation was run twice by independent passes that did not see each other's
working, and only agreeing results are reported as single numbers. GKP's
algorithms differ from FWG's in one structural way that matters: they delegate
to shared "recurring computations" in their Appendix A, so a correct count must
include those subroutine bodies once per call. For the odd-characteristic
addition, Appendix A contributes **35A of the 105** (13A from the resultant/
inverse routine, 22A from the `P·Q mod U` reduction); Appendix E's own body is
the other 70A. Two Appendix A routines were deliberately *excluded* as
unreachable from the odd-characteristic path, and two steps that look like
Appendix A calls are written out explicitly in Appendix E at 0M and 3M rather
than the subroutine's 11M, so they were counted from their own text.

**Where the two passes disagreed**, reported as ranges above rather than
averaged: GKP char-2 addition at `deg h = 2` (95 vs 98), `deg h = 1` (87 vs
90) and `h = 1` (83 vs 87), each a common-subexpression judgement; and the
`deg h = 3, h₂ = 0` doubling (113 vs 114), where the disagreement traces to an
inconsistency in the paper itself. Every `deg h = 3` addition row — the ones
this repository needs — was agreed by both passes. One column, the `deg h = 1`
doubling, is **underivable**: its 9M step is asserted in prose with no printed
formula.

**How C was derived.** Three routes, per source. Where formulas are printed, a
curve coefficient is a C only when it is a *multiplicand*; standing alone
between signs it is an additive term. Scanning the printed right-hand sides that
way gives **0** for every odd-characteristic table and for the char-2 rows whose
normal form fixes the coefficients at 0 or 1. Where a coefficient stays live,
FWG write it in a vector notation (`(e₀, e₁) = h₂ · (v₁₂, v₁₀)`) that a naive
scan misses, so C there is taken from **the authors' own variant columns** —
the gap between `h = 1` and `h arbitrary` is precisely the constant's cost, and
needs no re-derivation. For our files, C is counted statically per function from
the committed `//Constant:` declarations.

**Conventions that shift the GKP/Birkner numbers slightly**, disclosed so a
reader can adopt their own: additions against an F₂ constant (`τ₃ + 1`,
`f₀ + 1`) are counted as full A here though they are a single-word XOR;
folding the compile-time constants would take Birkner's five to 20/12/6/7/3.
Applying common-subexpression elimination to GKP's odd-characteristic addition,
which its own M count already assumes in places, gives 103A rather than 105A.

**Still not derivable.** Kuroki 2002, Gonda 2004/05 and Wollinger–Pelzl–Paar
2005 print their formulas only in sources with no open copy. Their A counts are
recoverable by anyone with library access, using the rules above; the table
rows are marked so this can be extended rather than guessed.

### Source access

| Source | Canonical | Open copy |
|---|---|---|
| Fan–Wollinger–Gong 2006 (tech report) | — | <https://cacr.uwaterloo.ca/techreports/2006/cacr2006-38.pdf> — **free; the source of every derived count here** |
| Fan–Wollinger–Gong 2007 (journal) | doi:10.1049/iet-ifs:20070003 | paywalled; the tech report supersedes it in coverage |
| Nyukai et al. 2006 | IEICE Tech. Rep. ISEC2006-5 | not open; in Japanese. **Formulas reprinted in FWG Tables XVII–XVIII**, which is how its A counts were derived |
| Guyot–Kaveh–Patankar 2004 | J. Ramanujan Math. Soc. 19(2), 75–115 | no publisher copy, but a readable scan circulates (academia.edu, `jrms_final`); **obtained and fully derived here** |
| Birkner 2009 (PhD thesis) | doi:10.6100/IR640148 | <https://pure.tue.nl/ws/files/3150567/200910363.pdf> — free |
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
- P. Birkner, "Efficient Arithmetic on Low-Genus Curves," PhD thesis,
  Technische Universiteit Eindhoven, 2009; doi:10.6100/IR640148.
- S. A. Lindner, "Improvements to Divisor Class Arithmetic on Hyperelliptic
  Curves," PhD thesis, University of Calgary, 2020 (`Thesis/` in this
  repository).
