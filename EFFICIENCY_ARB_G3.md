# Efficiency vetting: the arbitrary-characteristic genus-3 ramified formulas

A findings report on `g3/ramifiedModel/g3Formulas/arb_ramifiedG3_ADD.mag` and
`arb_ramifiedG3_DBL.mag`. **No formula is changed by this document.** Each
finding is located, measured, argued for correctness, and left for
implementation one commit at a time so that every change is separately
bisectable.

Companion to [RELATED_WORK.md](RELATED_WORK.md), which establishes what the
published state of the art costs and what these files cost today.

## Re-vetted and partly implemented, 2026-08-10

**The findings hold. Two things in this document do not.**

*Every line number is stale by roughly nineteen* — A1 cites `:2262, :2267-2268`,
where the code now sits at `:2276, :2281-2282`; B1 cites `:411-413, :750-752`,
now `:427-429, :766-768`. PR20's justification block and earlier insertions moved
them. **Locate these findings by content, not by line.**

*The baseline moved, and one delta with it.* PR35 corrected inversions written
`1/x` (one M per operation) and PR20's `//Ignore: h3` made those products free to
count. So the true starting point is `59M 4S 95A 4C` for the addition and
`55M 5S 114A 4C` for the doubling, not the figures below. A1's `−4C` is really
**−3C**: one of the products it deletes is `h3*v1_0`, which is already free.

**A1, A2 and B1 are implemented.** Measured with `verification/opcount.py`:

| | before | after |
|---|---|---|
| `Deg3ADD` generic | 59M 4S 95A 4C | **54M 3S 74A 1C** |
| `Deg3DBL` typical | 55M 5S 114A 4C | **55M 5S 111A 4C** |

A and S land exactly as this document predicted. The remaining findings — B2–B6
and C2 — are not yet applied, and should be re-located by content and re-measured
against the corrected baseline in the same way.

## Baseline

Frequent case, measured from the Magma source per branch (see
[Method](#method)). Every operation costs exactly one inversion.

| function | M | S | A | C | M+S |
|---|---|---|---|---|---|
| `Deg3ADD`, generic (`gcd(u₁,u₂) = 1`, `det ≠ 0`, `deg s = 2`) | 60 | 4 | 95 | 12 | 64 |
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

| | ADD | DBL |
|---|---|---|
| today | 60M 4S 95A 12C | 56M 5S 114A 16C |
| after the confirmed findings | **55M 3S 74A 8C** | **≈58M 4S 92A 14C** |
| thesis split, same degree | 65M 3S 87A 12C | 73M 3S 101A 19C |

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
