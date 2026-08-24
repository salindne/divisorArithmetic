# Efficiency vetting: the arbitrary-characteristic genus-3 ramified formulas

A findings report on `g3/ramifiedModel/g3Formulas/arb_ramifiedG3_ADD.mag` and
`arb_ramifiedG3_DBL.mag`. **No formula is changed by this document.** Each
finding is located, measured, argued for correctness, and left for
implementation one commit at a time so that every change is separately
bisectable.

Companion to [RELATED_WORK.md](RELATED_WORK.md), which establishes what the
published state of the art costs and what these files cost today.

> **Identifier note, 2026-08-12.** PR21 renamed the divisor coordinates to house
> style, so the names quoted throughout this document are the pre-rename ones. They
> are left as written, because a findings report is a record of what the code looked
> like when the finding was made. Translate with:
> `u1_i → u<i>`, `u2_i → up<i>`, `un<i> → upp<i>`, `v1_i → v<i>`, `v2_i → vp<i>`,
> `vn<i> → vpp<i>`, and `t1_i`/`hv<i> → vh<i>`. The polynomials `u1`/`u2`/`v1`/`v2`
> became `u`/`up`/`v`/`vp`.

## Re-vetted and fully implemented, 2026-08-10 and 2026-08-11

**Every finding in this document held.** Two things about *this document* did not,
and one of the two turns out not to be an error at all.

*Every line number in this document is stale, and no single offset corrects them.*
A1 cited `:2262, :2267-2268`; C2 cited `:428-443, :606-619`, which had drifted +22
before it was applied. PR20's justification block moved them once, and then each
implemented finding moved everything below it again, by a different amount per
file. Worked example of the failure mode: section E's `ADD:1467, :1469` now land on
unrelated live code. **Locate everything by content, never by line** — and do not
try to apply a fixed offset, which is what the earlier "stale by about nineteen"
note invited. This is not a precaution against a future rename: the positions were
already unusable before anyone renamed anything.

*The C figures are SUPERSEDED, not wrong.* When this report was measured, `h3` was
a declared `//Constant:` in both arb files, so every `h3*X` product cost 1C. PR20
(`0d0c70d`) moved it to `//Ignore:`, making them free. Three deltas here were read
as errors on that account and none of them is one:

| | as reported | today | the product that became free |
|---|---|---|---|
| A1 | −4C | −3C | `h3*v1_0` |
| B2 | −1C | −0C | `h3*u1_2` |
| E-Karatsuba | +2C | +1C | `h3*v1_1` |

Reproduced in both directions: restoring `h3` to `//Constant:` in both files
recovers this report's C column exactly, including its `16C` doubling baseline,
and its A and S columns too. Its M comes back one short in each operation --
that difference is PR35's separate inversion fix, so the reproduction is exact
for C and not for M. An independent cross-check needs no measurement at all — PR20 recorded
that the directive freed "8 of the addition's 12 C, 12 of the doubling's 16", and
12−8 = 4 and 16−12 = 4 are exactly the two baselines below. **One convention
change, not three defects.** Read `RELATED_WORK.md`'s measurement note before
filing any future C discrepancy as an error; it already explained this.

*The baseline also moved for M*, because PR35 stopped charging an inversion
written `1/x` an inversion plus a multiplication. True starting point:
`59M 4S 95A 4C` for the addition, `55M 5S 114A 4C` for the doubling.

### What landed

Part 1 (A1, A2, B1) and part 2 (C2, D33-06, B2–B6, D33-07 and the fusion family)
are implemented, one commit each, every one measured with
`verification/opcount.py` and confirmed under real Magma.

| | pre-PR16 | now | removed |
|---|---|---|---|
| `Deg3ADD` typical | 59M 4S 95A 4C | **53M 3S 71A 1C** | 5M 1S 24A 4C |
| `Deg3DBL` typical | 55M 5S 114A 4C | **57M 4S 92A 3C** | 1S 22A 1C, +2M |

The addition's removals are stated on the honest classification, not the counter's:
one of the six M it appears to remove is a multiply by a precomputable constant
sum — see the blind spot below. Total multiplicative work removed is nine either
way.

Against the thesis's own split-model Degree-3 rows, stated per column rather than
in aggregate, because the aggregate hides the one column that got worse:

| | M+S | S alone | C | A |
|---|---|---|---|---|
| `Deg3ADD` ours / split | **56 / 68** | 3 / 3, a tie | **1 / 12** | **71 / 87** |
| `Deg3DBL` ours / split | **61 / 76** | **4 / 3, one worse** | **3 / 19** | **92 / 101** |

So the addition wins on M+S, C and A and ties on S; the doubling wins on M+S, C
and A and loses one squaring. "Better in every column" is true of the addition
only if S is read inside M+S, which is why it is broken out here.

**The doubling's own before/after is a trade, not a free win.** On M+S it went
60 → 61, one worse; on the wider M+S+C it is 64 → 64. Twenty-two additions came
off, and one multiplication went on. Under the thesis's 1M:3A rule that is a
clear win, but it is a *trade* and should be described as one.

The sanity flag this vetting existed to explain is closed.

### Two figures in this document were too SMALL

Both found by re-measurement, and both in our favour:

- **ARBDBL-06 is −6M −1S −4A**, not the re-counted −2M −1S −2A. Measured after
  implementation; see below for why both earlier figures were short.
- **D33-07 touches 12 return sites in each file**, not "7 in arb, 8 in nch2".

### ARBDBL-06: applied, and worth more than the ledger recorded twice over

The `dw` block inside `det eq 0` recomputed what the Sylvester block above already
holds — `dw` is the third row of the adjugate up to sign:

    dw2 = u1_2*d2 - d1   = -t8
    dw1 = m7                                    (the expensive line: 3M 2A)
    dw0 = d0*t8 - t2*d2  = temp5 + temp3 = -m8

`dw2` is not formed at all, its only readers having been the other two lines, and
`t02 = d2²` dies with it. **Measured −6M −1S −4A** on the `det = 0` path
(57M 4S 95A 3C → 51M 3S 91A 3C); the frequent case does not move.

The ledger recorded "~4M" with a flag to re-count, and the re-count gave
−2M −1S −2A. **Both missed that `dw1` is exactly `m7`**, which is the expensive
half. It was also deferred out of the first part-2 pass because C2 had rewritten
the block it borrows from — the re-pointing above is the whole of the extra work
that needed.

### One finding is open: implemented, measured, and dropped before it shipped

**ARBDBL-09.** Note there is no revert commit to look for — it was built on a branch,
measured, found to be a loss, and removed from the history before that branch was
pushed. `Deg1DBL` is byte-identical to what it was before PR16.

Horner-nesting
`k0` in `Deg1DBL` measured −1S and is honestly **+3M −3C −1S**: the old form
multiplies by `4*f4`, `5*f5` and `6*f6`, all precomputable per curve and therefore
C, and Horner replaces them with three genuine `u1_0*(variable)` products. The
counter could not see the difference for the same reason as below — recorded as
**ERRATA E13**. The ledger's original −1M −1S was measured against a counter with the
same gap, so this entry has never had a trustworthy figure.

Its second half — hoisting the scalars for a further −5A — was rejected on a false
ground when the change landed (the claim was that they depend on the divisor; they
do not, the hoistable quantities are the integer multiples `i·f_i`). It is real,
and it needs the caller to supply them, so it is an interface change rather than a
formula rewrite. Open, not refuted.

### A tooling blind spot, narrowed but NOT closed

`maginterp._leafname` returns a name only for a `var` node, seeing through unary
minus and nothing else. So a product whose factor is any *composite* expression
over curve constants matches neither `CONSTS` nor `IGNORED` and is charged a full
M, even when it is precomputable per curve. Two shapes occur here:

- `(h3 + h2)*(v1_2 + v1_1)` — a parenthesised **sum**. This was the last live
  instance of that shape in the whole g2+g3 corpus, and the fusion commit removed
  it (A1 removed the other).
- `2*f6*u1_0`, `4*f4*u1_0`, `5*f5*t01` — an integer **multiple** of a coefficient.
  These are still live, including on the frequent `Deg3DBL` path, so **the gap is
  narrowed, not closed.** It is what made ARBDBL-09 look like a win.

Now recorded as **ERRATA E13**, with the scope measured: **six live sites, all in
`arb_ramifiedG3_DBL.mag`**, and none of the parenthesised-sum shape left anywhere.
Consequences for the figures in this document: A1's honest split is **−4M −4C**
rather than −5M −3C at the same total of eight; and one site sits on the frequent
`Deg3DBL` path, so that row's honest split is **56M 4S 92A 4C** where the counter
says 57M 4S 92A 3C — 64 multiplicative operations either way. The counted figures are
what this document quotes, because every other number here comes from the same tool
and mixing conventions inside one table is worse than a documented offset.
**Recorded, not fixed** — the reclassification falls under the
presume-the-published-correct rule and needs its own gate.

### A naming note, and the defect behind it

This document once called the addition's frequent path "generic" and the doubling's
"typical". They are the same notion — trivial gcd, `deg s = 2`, full-degree result, one
inversion — and the source calls it **`TYPICAL CASE`** in both files, for every function
but one. Unified on the source's word.

The exception is the reason the drift happened: **`Deg3ADD` has no `TYPICAL CASE` banner
and no `Typical` label.** All eight of its labels name degenerate gcd cases, so its
frequent path is the only one with no word in the source to quote. That is the same
missing-label defect that makes `whitebox.py` blind to this function, seen from the
naming side rather than the coverage side — one fix closes both, and it belongs with the
branch-label work.

### Four findings this document did not have, three of them now applied

Turned up by implementing the rest:

- **B5's technique, swept — APPLIED.** `h2 + 2*v1_2` costs two additions where a
  live temporary makes `hv2 + v1_2` (doubling) or `t1_2 + v1_2` (addition) cost
  one; likewise `h1 + 2*v1_1`. Applied at **nine live sites**, measured −4A on the
  DBL `det = 0` path and −1A each on three more buckets. B6's identical-shape
  finding had been swept across every site while B5's was applied only where the
  report named it; that inconsistency is gone. Deg2DBL's `d1` is deliberately left
  — no such temporary is in scope there, so fusing would have to create one.
- **`dw2` is exactly `-t8` — APPLIED**, inside ARBDBL-06 above, which is where it
  belonged.
- **C3's other half — APPLIED.** `// SWAPPING st WITH w1 ALSO WORKS????` is now a
  statement: reducing `w1` instead of `st` costs the same, the two differing by a
  multiple of `u1` that the reduction removes. **No `????` remains in either file.**
- **The counter's integer-multiple blind spot** is a tooling finding and stays
  open, above.

### What whitebox.py can and cannot gate here

**Stated because four commit messages in this branch initially cited it wrongly.**
`whitebox.py`'s corpus and its coverage denominator are keyed on
`ADD_DEBUG`/`DBL_DEBUG` label strings. Every region edited in `Deg3ADD` — the
generic `CASE #1.1` path included — carries **no label**, so the frozen corpus
holds no case that reaches them and its 1,812/1,812 says nothing about them.

Demonstrated rather than assumed: sabotaging the frequent-path `vn1` with a
`+ 12345` leaves `whitebox.py` at **1812/1812 PASS**, while `driver --strict`
reports 2 mismatches and real Magma drops its `No errors` line.

So for these files the gates are **`driver --strict` and Magma**. This is the same
gap the merge plan records as "15 missing branch labels … `Deg3ADD`'s 100% is
really 8 of ~15 live returns"; it is now demonstrated with a tripwire rather than
inferred, and it is the strongest argument for adding those labels.

## Baseline

**Everything below this line is the report as first written**, measured against the
directive set of 2026-08-09 where `h3` was a `//Constant:` and inversions written
`1/x` were over-charged. Its `12C`/`16C` and its M figures are correct *for that
convention* and are left as measured; see the re-vet above for the translation and
for what was actually implemented. Read "today" throughout as 2026-08-09.

Frequent case, measured from the Magma source per branch (see
[Method](#method)). Every operation costs exactly one inversion.

| function | M | S | A | C | M+S |
|---|---|---|---|---|---|
| `Deg3ADD`, typical (`gcd(u₁,u₂) = 1`, `det ≠ 0`, `deg s = 2`) | 60 | 4 | 95 | 12 | 64 |
| `Deg3DBL`, typical (`gcd(u₁, 2v+h) = 1`, `deg s = 2`) | 56 | 5 | 114 | 16 | 61 |

For scale, the thesis's own **split-model** Degree-3 arbitrary rows
(`chapter6.tex`): ADD 65M 3S 87A 12C (M+S 68), DBL 73M 3S 101A 19C (M+S 76).
Ramified has strictly less work to do than split — no balancing, no adjust
steps — so it should be cheaper in every column. It already is on
multiplications. **It is not on additions, and that is what this vetting set out
to explain.**

## What was found

Thirty findings. Twenty-seven survived independent adversarial verification,
two survived in part, one was refuted. The verifier for each finding had to
reproduce the measured delta from its own rig and re-test correctness against
Cantor's algorithm across all reachable branches before the finding counted.

The answer to the additions question is mostly **dead and duplicated work**, not
a wrong algorithm:


| | ADD (2026-08-09) | DBL (2026-08-09) |
|---|---|---|
| then | 60M 4S 95A 12C | 56M 5S 114A 16C |
| after the confirmed findings | **55M 3S 74A 8C** | **≈58M 4S 92A 14C** |
| thesis split, same degree | 65M 3S 87A 12C | 73M 3S 101A 19C |

The predicted DBL additions, 92A, are exactly what the implementation measured —
the A column of this report survived every convention change intact, which is the
lesson recorded in the re-vet.

The ADD figure is a measured composite of two independent, non-overlapping
edits. The DBL figure sums seven separately measured edits and is marked
approximate on purpose: composition is not measured, and PR16 must re-measure
after each commit rather than trust the sum.

---

## A. Dead work — the largest single finding

### A1. `Deg3ADD` computes two quotient coefficients that no branch ever reads

`arb_ramifiedG3_ADD.mag:2262, :2267-2268` — **−5M −1S −19A −4C** on every
generic addition. Frequent case `60M 4S 95A 12C` → `55M 3S 76A 8C`.

`w1_1` and `w1_0` are assigned and never read again — not on the generic path,
not anywhere: a scan of the whole file after their definition finds no reader.
`tb` at `:2262` is their only other consumer and dies with them. The thesis's
`sec:exactdiv` says the quotient `(f − v₁h − v₁²)/u₁` needs only its top
`d₁ − d₂ + 1` coefficients; this site computes two more.

This is the same defect the source-repo audit recorded as **ODDADD-19**, and it
was rediscovered here independently by two probes that did not share results —
one working the thesis technique checklist, one re-verifying the ledger. Both
measured the identical delta.

Cases 1.2 and 1.3 of the same function get the identical saving. All ten
special branches are unchanged. Verified over 20,189 calls with side-by-side
output comparison and zero divergences; the change is pure dead-store
elimination and none of the deleted expressions contains a division, so no path
can differ even in error behaviour.

**The nch2 twin is real too** (`nch2_ramifiedG3_ADD.mag:2234-2235`), at
**−4M −1S −11A −2C**, taking that file's generic case from `59M 4S 77A 3C` to
`55M 3S 66A 1C`. It belongs to PR15/PR17 rather than here, but the ledger's
recorded "6M 1S 11A" was close on A and over on M.

### A2. `ht1`/`ht0` are computed unconditionally, read only when `det = 0`

`arb_ramifiedG3_ADD.mag:1442-1443` — **−2A** on the generic path, zero
elsewhere. Pure code motion into the `if (det eq 0)` branch that consumes them
(readers confirmed at `:1484-1485`, `:1655-1656`, `:1998`/`:2002` by an if-nesting
matcher, not a grep). The special branches pay the same two additions, just
later.

**A1 and A2 compose**, measured: `60M 4S 95A 12C` → **`55M 3S 74A 8C`**, i.e.
**M+S 64 → 58, C 12 → 8, A 95 → 74**.

That single result changes the standing against the thesis's split-model
addition from "4 better on M+S, 8 worse on A" to **better in every column**:
58 vs 68 M+S, 8 vs 12 C, 74 vs 87 A.

---

## B. Redundant recomputation in `Deg3DBL`

Six findings, each small, each confirmed with no variance across thousands of
typical-branch calls, all in the addition column where this file is weakest.

| # | location | change | delta |
|---|---|---|---|
| B1 | `:411-413`, `:750-752` | precompute `h + v₁` once instead of re-forming it in `d₂/d₁/d₀` and `vn₂/vn₁/vn₀` | −3A |
| B2 | `:730` | `M20` recomputes `d₂` inline; reuse the one computed 300 lines earlier | −3A −1C |
| B3 | `:730` | `M20` re-derives `f₅ − h₃v₁₂`, already sitting in `t06` | −1A |
| B4 | `:601` | `k2` re-derives `f₅ − t04`, which is `t06` on the line above | −1A |
| B5 | `:603` | `k0` re-derives `h₂ + 2v₁₂` rather than reusing `d₂ + t01` | −1A |
| B6 | `:602` | `k1` splits `h₂v₁₂` and `v₁₂²`, which combine into one product | +1M −1S −1A −1C |

B2 and B3 touch the same line and compose there. B6 is the only one that moves
a multiplication, and it is neutral on M+S.

---

## C. The adjugate/T13 question — the hypothesis was backwards

The merge plan recorded a structural suspicion: the ADD builds a full 9-entry
adjugate with a 9M matrix–vector product while the DBL in the same directory
already uses the thesis's T13 first-column recipe with Karatsuba twice, so the
ADD looked like an unfinished port. **Measured, it runs the other way.**

### C1. Applying T13 to the ADD is a losing trade — negative result

`arb_ramifiedG3_ADD.mag:1452-1474`, `:2277-2279`. Rewriting the ADD to the T13
shape gives `60M 4S 95A 12C` → `59M 4S 107A 12C`: **−1M for +12A.** The thesis's
own rule (`sec:trades`) never trades one multiplication for more than three
additions, so this is rejected by the project's own standard. Recorded so nobody
re-derives it hopefully.

### C2. Porting the ADD's shape *into* the DBL is a winning trade

`arb_ramifiedG3_DBL.mag:428-443`, `:606-619` — **+1M −12A**, i.e.
`56M 5S 114A 16C` → `57M 5S 102A 16C`. Read the other way: the file as it stands
**buys 1M at a price of 12A**, which is the same `sec:trades` violation, in the
opposite direction. Reproduced on 4,312 exhaustive plus 3,243 random plus 599
char-2/char-3 typical-branch calls with no spread. Rare `det = 0` branches pay
`+3M +2A`.

Found independently by the structural probe and by the technique checklist,
which flagged it as the `sec:trades` violation without knowing the other had
found it.

### C3. Both of the authors' own open questions resolve here

`arb_ramifiedG3_DBL.mag:403-405` carries `// use sebastian's k calculations???`
and `// use my determinant calculation??`; the ADD carries a surviving
`SWAPPING st WITH w1 ALSO WORKS????`. These are the authors' admission that the
comparison was left unfinished. The first is exactly C2's question and the
answer is *use the determinant calculation* (+1M −12A). The second is
answered in the affirmative with zero op-count consequence. Both should become
statements rather than questions.

### C4. The same trade is available in the split-model genus-3 addition

`g3/splitModel/negReduced/g3Formulas/` — the same 1M-for-12A swap appears in the
split ADD routines by the identical mechanism, expected `+1M −12A` per
frequent-case call. **Out of scope here and not measured**; recorded because it
touches published split-model formulas and therefore belongs to a decision about
the thesis tables, not to this PR.

---

## D. Ledger re-verification

The source-repo audit's efficiency ledger, re-checked at current repo line
numbers with the corrected counter. Several entries were "probe-validated"
against the old, over-counting translations, so their claimed deltas needed
re-deriving even where the observation was sound.

| ledger id | verdict | delta |
|---|---|---|
| ODDADD-19 (arb) | **confirmed** | −5M −1S −19A −4C — see [A1](#a1-deg3add-computes-two-quotient-coefficients-that-no-branch-ever-reads) |
| ODDADD-19 (nch2) | **confirmed**, recorded delta slightly off | −4M −1S −11A −2C |
| ODDADD-13 | **REFUTED for arb** | `dm_0` at `:529` is *live* in the arb file; dead only in nch2, and only in `Deg22ADD` case #2.1, worth −1M there |
| D33-07 | **confirmed exactly** | 0 on the frequent case; −2M −2A on every `det = 0` return site (7 in arb, 8 in nch2) |
| ARBDBL-06 | **confirmed, smaller than recorded** | −2M −1S −2A, and **not on the frequent path** — the whole `dw` block sits inside `if (det eq 0)`. Recorded as "~4M"; the flag to "re-count before adopting" was right |
| ARBDBL-09 | **confirmed, different delta** | Horner alone is **−1S**, not −1M −1S. With `f′`/`h′` constants hoisted: −1S −5A |
| D33-06 | **confirmed** | the three-way duplication has already cost real operations: the `vn`-tail port is −1M −3A on the frequent case of *both* files. The collapse itself is op-count-neutral |

The ODDADD-13 refutation is worth stating plainly: the ledger recorded an "arb
twin" that does not exist. Deleting that line in the arb file would be a
correctness bug.

---

## E. Documentation errata found while measuring

None of these change an operation count; all of them mislead a reader.

- **`arb_ramifiedG3_ADD.mag:1467, :1469`** — the two `// convenient zero`
  comments are false. (This is also D33-07's site: those two multiplications are
  computed before the `det eq 0` test that makes them useless.)
- **`arb_ramifiedG3_DBL.mag:604`** — the committed op-count comment for the `k`
  block does not match the block. Measured: 5M 2S 30A 7C.
- **`arb_ramifiedG3_DBL.mag:434`** — the commented-out `t3` in the Sylvester
  setup is described wrongly.
- **`arb_ramifiedG3_DBL.mag:526`, `arb_ramifiedG3_ADD.mag:2091`** — the
  `// no karatsuba` annotations. Karatsuba is applied in the wrong direction at
  `ADD:2091` (−1M −3A +2C available on the case #2.x branches) and correctly
  omitted at `DBL:526`.

## Partial and refuted

- **Karatsuba verdicts (partial).** `ADD:2267` un-Karatsuba is −1M +2C −3A, but
  that line is inside the block A1 deletes, so the finding is subsumed. The
  `DBL:609-618` un-Karatsuba measurement (+4 M+S, −10A) is really C2 seen from a
  different angle. Kept for the record, not as separate work.
- **`2*f6*u1_0` charged as a general multiplication (refuted).** This is an
  artefact of how the counters bind `-2*(...)`, not a property of the formulas.
  Real, but a *measurement* observation; it belongs with the tooling notes in
  RELATED_WORK, not here.

---

## Method

Every number is measured by interpreting the actual Magma source per branch —
`maginterp2.py` in the audit harness with `CONSTS` set from each file's own
`//Constant:` directive and `KEEP_LABELS` on for branch identification, driven
by `c_baseline.py`. The older `opcount*`/`drive-*` counters run hand-written
Python transcriptions and over-count; they are not used here and should not be
used again. See RELATED_WORK.md's
[measurement note](RELATED_WORK.md#which-counter-is-authoritative).

Each finding was produced by one agent and then handed to a different one whose
brief was to **refute** it: reproduce the delta on an independently written rig,
re-test correctness against `cantor.add`/`cantor.double` across all reachable
branches including characteristic 2 and 3, confirm the location in the current
repo file, and check the change against the 1M:3A rule. A finding whose measured
delta differed from its claim was refuted as stated. Scratch copies only — the
repository was never modified during measurement.

Two facts about the counter that matter when reading these deltas: it **charges
dead assignments** (so it over-counts rather than under-counts, the safe
direction for an audit — and it is why A1 shows up as a saving at all), and it
charges `a^3` as 2M where the convention wants 1S+1M. No `^3` occurs on any
frequent path, so no figure here is affected.

## Handoff to PR16

Suggested order, largest and safest first. Each lands as its own commit with
`driver.py --strict`, `whitebox.py` and the Magma suite run after it, and the
frequent-case count re-measured — **the composite figures above are sums of
separate measurements, not measured composites**, except A1+A2 which was.

1. **A1** — the dead `w1` coefficients. Largest single win, pure dead-store
   elimination, zero correctness risk.
2. **A2** — `ht1`/`ht0` code motion. Pure motion into the only consuming branch.
3. **C2** — the DBL adjugate port. Largest addition win, but it is a real
   algorithmic change and deserves its own commit and its own scrutiny.
4. **B1–B6** — the DBL recomputations, individually.
5. **D** — D33-07 and ARBDBL-06/09, all off the frequent path and worth little;
   take them for tidiness, not for the count.
6. **E** — the comment errata, in a single documentation commit.

Not for PR16: **C4**, which touches published split-model formulas, and the
nch2 half of A1, which is PR15/PR17's.

---

## Addendum, 2026-08-24 — `t7*m3` is `t2*m8`, and the family already holds `t2`

Found while sweeping the characteristic-2 genus-3 addition, which is a
specialisation of this file and carries the same statements. It applies **here**,
unchanged, and it is not a characteristic-2 result: the derivation is pure
associativity.

`Deg3ADD` computes, before the `d` guard:

    t7:= u2 - up2;
    t2:= -up0*t7;
    m8:= t2*t7 - t1*t8;
    m3:= -up0*m8;
    d := t1*m1 + t4*m2 + t7*m3;

and `t7*m3 = t7*(-up0*m8) = (-up0*t7)*m8 = t2*m8`. The signs cancel because `t2`
and `m3` carry the same `-up0` factor, so the identity is exact in every
characteristic and on every curve — no domain reasoning at all.

**What it buys.** With `d` reading `t2*m8`, the only remaining reader of `m3` is
the typical family's `sp0`. So `m3:= -up0*m8;` moves from the shared prologue into
that family, and **every leaf reached through `IsZero(d)` stops paying for a
multiplication it never uses.** The typical case is unchanged: the product moves
rather than disappearing.

**Measured in the specialisation**, where it has landed: the three degenerate
`Deg3ADD` cost rows moved `76M → 75M`, `50M → 49M` and `79M → 78M`, with the
modal row untouched. Expect the same shape here, since the statements are the same.

**APPLIED 2026-08-24** in its own commit, with its own gate run, as the plan's
PR37. The adjudication question was settled first: every genus-3 ramified count in
`README.md` is marked *measured*, and the thesis defers these formulas outright
(`chapter6.tex:15`, "ramified models are developed by another student"), so no
published cell could move.

**And the frequent case saves nothing, which is the part worth stating.** The
region annotated `total: 27m 0s 17a` is *all nine entries, `d`, and `sp = M*vt`* --
and `sp0` reads `m3`, so the path that reaches the typical case still pays for it.
The multiplication MOVED, from the top block into the `sp` block: `top` 16m -> 15m,
the `sp` block 11m -> 12m, total unchanged. The saving is exactly and only on the
leaves that return before `sp0`, which never wanted `m3`.

That correction came from the gate, not from reading: `adjugate.py` rejected a
"total: 26m" that seemed to follow from `top: 15m`, because it measures the region
and the region had not changed.

**Verification available.** `verification/opcount.py --family ramified/g3/<class>`
shows the per-leaf distribution, which is where the saving is visible — the modal
figure cannot show it. `dominance.py` will catch the move if `m3` is left read
above its new assignment on any path.
