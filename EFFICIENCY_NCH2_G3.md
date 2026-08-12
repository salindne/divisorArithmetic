# Efficiency vetting: the odd-characteristic genus-3 ramified addition

A findings report on `g3/ramifiedModel/g3Formulas/nch2_ramifiedG3_ADD.mag`.

**Implemented 2026-08-12.** The report is kept as the record of how each finding was
established; every frequent-case figure below was reproduced by the implementation,
and the two places the implementation learned something the report did not know are
marked **[ON LANDING]**.

Companion to [`EFFICIENCY_ARB_G3.md`](EFFICIENCY_ARB_G3.md), which did the same
for the arbitrary-characteristic pair and whose findings are now implemented.
That matters here: **this file is the arb addition specialised to `h = 0`**, so
the arb work is not merely a precedent, it is the source this one should have
been derived from.

> **Identifier note, 2026-08-12.** PR21 renamed the divisor coordinates to house
> style, so the names quoted throughout this document are the pre-rename ones. They
> are left as written, because a findings report is a record of what the code looked
> like when the finding was made. Translate with:
> `u1_i → u<i>`, `u2_i → up<i>`, `un<i> → upp<i>`, `v1_i → v<i>`, `v2_i → vp<i>`,
> `vn<i> → vpp<i>`, and `t1_i`/`hv<i> → vh<i>`. The polynomials `u1`/`u2`/`v1`/`v2`
> became `u`/`up`/`v`/`vp`.

## Outcome

`Deg3ADD` typical went **58M 4S 77A 3C → 53M 3S 59A 0C**, and the addition is now
cheaper than the arb it specialises on every shared operation shape — equal M+S,
strictly fewer additions. `verification/selftest.py` asserts that relationship now,
so the drift described below cannot recur unnoticed.

**[ON LANDING] Two findings existed only because the others landed first.** Eleven of
the seventeen disguised squarings are available only once `f₆ = 0` makes the leading
quotient coefficient a bare negation of a `u1` coefficient — they are not in the list
below, because they could not be seen from the un-depressed file. A ledger has to be
re-derived as items land, not replayed.

## The situation, and why it was backwards

The arbitrary formulas received ten efficiency findings. This one received none.
So the *general* addition is currently cheaper than the *specialised* one, which
cannot be right on a correct accounting — nch2 does strictly less work.

| | M | S | A | C | I | M+S |
|---|---|---|---|---|---|---|
| `arb` `Deg3ADD` typical | 53 | 3 | 71 | 1 | 1 | 56 |
| `nch2` `Deg3ADD` typical, today | 58 | 4 | 77 | 3 | 1 | **62** |

## The result

Four findings move the frequent case. **Measured as a composite, not summed** —
the lesson from the arb work, where composition turned out not to be additive:

| step | `Deg3ADD` typical | gate |
|---|---|---|
| today | 58M 4S 77A 3C | — |
| dead `w1_1`/`w1_0` deleted | 54M 3S 66A 1C | driver clean |
| + the cheap `vn` tail | 53M 3S 63A 1C | driver clean |
| + `ht1`/`ht0` sunk into `det = 0` | **53M 3S 61A 1C** | driver 12,990/12,990 |
| + `f6 = 0` | **53M 3S 59A 0C** | driver 12,972/12,972 |

**Removes 5M 1S 18A 3C.** The result sits at **56 M+S, 0C, 59A** — twelve
additions and one C below the arb parent at identical M and S, so the
specialisation is cheaper than the general case again.

**And for the first time the comparison with the literature is apples-to-apples**,
because `f6 = 0` is the curve form every published odd-characteristic source
already assumes:

| | M+S | C | A | curve |
|---|---|---|---|---|
| **ours, after these findings** | **56** | **0** | **59** | `h = 0`, `f₆ = 0` |
| Nyukai 2006 | 67 | 0 | 105† | `h = 0`, `f₆ = 0` |
| GKP 2004 | 70 | 0 | 105† | `h = 0`, `f₆ = 0` |
| Gonda et al. | 70 | 0 | — | `h = 0`, `f₆ = 0` |
| Kuroki et al. | 81 | 0 | — | `h = 0`, `f₆ = 0` |

† derived by us from the published formulas; no prior author reports A. See
[`RELATED_WORK.md`](RELATED_WORK.md).

---

## The four frequent-case findings

Each was found by **at least two probes independently**, and the first was found
by five. Each was then handed to an adversarial verifier that rebuilt the edit on
its own tree; all four survived.

### 1. Two quotient coefficients nothing reads — `−4M −1S −11A −2C`

The generic path computes all four coefficients of `w1 = (f − v1²)/u1`. Only
`w1_3` and `w1_2` are read: they feed the resultant immediately below. `w1_1` and
`w1_0` are read nowhere on any path.

This is the thesis's own **efficient exact division** (`sec:exactdiv`) applied to
its own code — only the highest `d1 − d2 + 1` coefficients are needed, here two of
four. It is the exact twin of the arb file's A1, which has landed, so the edit has
a working precedent including the convention of keeping the deleted definitions in
a comment.

Recorded in the source-repo audit as **ODDADD-19** at `6M 1S 11A`. The M figure was
measured against a counter that over-charged inversions; re-measured it is **4M**.

### 2. The cheap `vn` tail, at both expensive sites — `−1M −3A`

`Deg3ADD` repeats its closing formulas once per gcd family, and **the three copies
are not equivalent.** `CASE #3.1` precomputes

    ty = (u1_2 − q0)·tx + (un2 − q0)·wi

and reads it twice — whole in `vn1`, times `−q0` in `vn0`. The other two copies
distribute that quantity and then re-derive `q0·ty·tx` and `(un2 − q0)·q0·wi`.
So the duplication had already cost a multiplication and three additions on the
frequent path.

Transplanted into both expensive copies, keeping the names `tx`/`ty` those lines
already use, so no identifier is introduced. Identical to the arb file's D33-06.

### 3. `ht1`/`ht0` formed before the only branch that reads them — `−2A`

`ht2` is read on the generic path; `ht1` and `ht0` are read **only** inside
`if (det eq 0)`. Moved there. The special cases pay the same two additions later;
the generic path stops paying them. Identical to the arb file's A2.

### 4. The `f6 = 0` depression — `−4A −3C` alone, `−2A −1C` after finding 1

The headline finding, and the one with the most to say.

**The mathematics.** `x → x − f6/7` kills the `x⁶` coefficient, and needs exactly
`char ≠ 7`: over GF(7) the `x⁷` term contributes `−7c·x⁶ ≡ 0`, so the coefficient
is invariant under **all seven** translations — verified exhaustively, not
sampled. The isomorphism carries divisors as `u(x) → u(x−c)`, `v(x) → v(x−c)`.

**It removes ZERO multiplications, and the audit's figure was wrong about that.**
The audit recorded `8M + 22A` static. All eight products are `f6*u1_i` — a bare
`var` times a bare `var` with `f6` in this file's own `//Constant:` — so the counter
charges them **C**, and that is the honest classification: a multiplication by a
quantity fixed once per curve. Established by parsing the block directly, twice,
independently:

    before   w1_3{A:1} w1_2{A:3,C:1,S:1} w1_1{A:5,C:1,M:1,S:1} w1_0{A:6,C:1,M:3}
    after    {A:11, M:4, S:2}
    diff     exactly {A:4, C:3}

Note this is *not* an instance of [`ERRATA.md`](ERRATA.md) E13: E13's
misclassifying shapes are composite factors like `2*f6*u1_0`, and all 22 arithmetic
uses of `f6` in this file are `f6 - u1_i` or `f6*u1_i`. Checked.

**So the value of this finding is comparability, not arithmetic.** It removes four
additions and three constant-multiplies from the frequent case, and it puts the
file on the curve form the entire published record uses. State it that way, or the
change reads as underwhelming for the size of its blast radius.

**It is not additive with finding 1, and it collides with it textually.** Measured
on separate trees:

| | `Deg3ADD` typical |
|---|---|
| base | 58M 4S 77A 3C |
| finding 1 alone | 54M 3S 66A 1C |
| `f6 = 0` alone | 58M 4S 73A 0C |
| **both** | **54M 3S 64A 0C** |

`f6`'s frequent-case contribution **halves** from `4A 3C` to `2A 1C` if finding 1
lands first — because finding 1 deletes two of the lines `f6` appears in. A
verifier applying its `f6` script on top of finding 1 hit
`count mismatch 2 != 3` and could not proceed. **Land `f6` first, or re-derive its
occurrence counts.**

---

## The blast radius, and it is the real work

**Three hard gates. The PR fails without each of them**, and this was established
by making it fail, not by reasoning.

### (a) The curve generator must stop drawing `x⁶`

`ramifiedUtilities.mag`'s `RandomG3NotChar2Curve` draws a full monic degree-7 `f`.
Its own banner already pre-announces this change and must be rewritten in the same
commit.

**Proof it is mandatory:** with the formula edit applied and the generator left
alone, real Magma printed **25,477 error lines over 60 trials**. No hang risk from
the narrower draw — a monic degree-7 `f` with `f6 = 0` is squarefree for 486 of 729
candidates over GF(3) exhaustively, and 80–97% by sampling over GF(5) … GF(31).

### (b) The dispatcher must stop extracting `Coeff(f,6)`

`driver.domain_constraints` derives the tested domain **by contrast** with arb's
dispatcher. While nch2 still reads `Coeff(f,6)` the driver infers no constraint and
keeps generating `f6 ≠ 0` curves, which the depressed formulas legitimately get
wrong.

**Reproduced directly:** the formula edit alone gives `'f': set()` and **110 driver
mismatches**; dropping the extraction gives `'f': {6}` and a clean
12,972/12,972. Note the comparison count dips from 12,990 as the domain narrows —
expected, and not a coverage loss to chase.

### (c) Two frozen corpus records sit on `f6 = 1` curves

Exactly **2 of the 30** `ramified/g3/nch2` records in
`verification/harvested_cases.json` are on an `f6 = 1` curve — both `Deg3ADD`, both
over GF(3). Unfixed, `whitebox.py` fails with 2 mismatches, one drifted case and a
lost-coverage report.

**Replace those two records surgically. Do NOT run a bare `--harvest`:** on a
pristine tree it already rewrites 1,307 lines and writes 80 cases where the corpus
has 70, adding ten unrelated nch2 DBL cases. That would fold a pre-existing
divergence into this PR. With a surgical swap, coverage stays 30/30 and
`coverage_baseline.json` needs no edit at all.

### Documentation that moves with it

`README.md`'s `nch2` description needs genus-qualifying (genus 2: `f4 = 0`,
`char ≠ 5`; genus 3: `f6 = 0`, `char ≠ 7`) — the audit noted the genus-2 condition
has **never** been stated in the files. `RELATED_WORK.md`'s `3C → 0C` cell and its
`62 M+S, 3C, 77A` figures. `NEW_WORK.md`'s note that the generator "still draws
`f₆`", which becomes false. And a thesis erratum, below.

### The banner must state `char ≠ 7`

The banner says characteristic not 2 and will now also require not 7. The audit's
standing complaint is that the genus-2 files never state their own `char ≠ 5`;
do not repeat it here.

---

## What was tried and refuted

Recorded with equal weight, so nobody re-runs these.

**No third assumption is available.** Four candidates, all refuted by measurement:

| candidate | verdict |
|---|---|
| the leftover α-scaling pins an `f` coefficient | **refuted** — buys nothing at `h = 0` |
| `f5 = 0` reachable | **refuted** — not clearable; the size of the temptation is on record |
| a different budget allocation | **refuted** — the trade loses |
| a halving to exploit (`char ≠ 2`) | **refuted** — no candidate site exists |

`h = 0` and `f6 = 0` is the whole normalisation budget, and no published source
takes a third assumption either.

**No `C2`-type win.** The arb *doubling* gained `+1M −12A` by replacing a
first-column-plus-Karatsuba shape with the full nine-entry adjugate. **nch2 already
uses the full adjugate** — the same shape as the arb addition — so there is nothing
to convert. Applying the transform in the other direction loses, exactly as C1
measured for the arb addition.

**No branch becomes unreachable at `h = 0`.** There is no dead code to strip.

**nch2 improves on arb nowhere.** A probe hunted specifically for a site where the
specialiser had bettered its source, so it could be back-ported. It found none.

**One proposed common subexpression is the wrong direction:** `+1M −1S −1A −1C` on
the frequent case. Rejected.

**`ODDADD-14(a)`, the `st` aliases, has no operation-count delta at all** — they are
plain variable-to-variable copies, which the counter charges nothing for. The
recorded entry conflated that with the squaring half.

---

## Off the frequent path

Real but invisible to any published row. Worth taking for tidiness, on the arb
precedent, not for the count.

| finding | where | delta |
|---|---|---|
| `m6`/`m4` formed above the `det = 0` test | 12 early-return sites | −2M −2A each |
| `M64` sink, same pattern | every `det = 0` sub-case | −2M −2A |
| leftover h-term `ta := d0*d2` (**ODDADD-20a**) | all five `#3.x` branches | −1M |
| duplicate `ta` (**ODDADD-20b**, restated) | — | −1A |
| dead `dm0 := d0*a1` (**ODDADD-13**) | `Deg22ADD` #2.1 | −1M |
| Karatsuba in the losing direction | 8 sites | −3A each, 24A static |
| disguised squarings, `M → S` | 11 sites | −1M +1S each |
| `Deg3ADD` case #4.2 | — | −1M +1S −1A |
| `Deg22ADD` `st` alias | #3.1 | −1M −1A +1S |

**`ODDADD-13` is confirmed here where its arb twin was REFUTED.** The audit claimed
a dead `dm0` in both files; the arb line is live and deleting it there would be a
correctness bug. In nch2 it really is dead. That asymmetry is what a specialisation
audit is for, and it vindicates the audit's original per-file distinction.

The `M → S` rewrites are a **strict trade**, neutral on the combined M+S figure the
literature comparison uses, and favourable only under `S < M`. Land them on that
basis or not at all; they are free either way and they remove an oddity.

---

## Two process warnings for the implementation

**Anchored replacement only.** `    vn0:=` is a substring of `        vn0:=`, so a
four-space pattern silently matches an eight-space site. This happened during the
measurement of this report: the eight-space site was rewritten with four-space
indentation. Harmless in Magma, invisible to every gate, and exactly how a
"mechanical" edit script goes wrong. Match on the full line or anchor to
line-start.

**`whitebox.py` cannot gate the changes to `Deg3ADD`.** Its corpus and coverage
denominator are keyed on `ADD_DEBUG` label strings, and this function's typical
path carries none — the same gap demonstrated with a tripwire in the arb file.
Run it, because the `f6` work does move two of its records, but **cite
`driver.py --strict` and real Magma** as the evidence for the frequent-case edits.

**And when running Magma, check the runtime.** A run that prints `TEST_ADD: true`
and `No errors` in under a second has loaded nothing and verified nothing
([`ERRATA.md`](ERRATA.md) E12). A real `nch2_ramifiedG3_random.mag` run takes about
220 seconds and prints per-trial lines.

---

## Method

Seven independent probes, one per dimension — the `f6` depression, a transfer audit
of all ten landed arb findings, the recorded ledger, `h = 0` leftovers found by
diffing against arb, a structural comparison, the thesis technique checklist, and
the assumptions question — followed by adversarial verification of the frequent-case
findings, each verifier rebuilding the edit on its own tree and briefed to refute.

Every figure is measured by `verification/opcount.py`, which executes the formulas
over a real finite field and identifies the frequent case by observing which branch
is taken. Off-path figures come from per-branch replay, since the modal figure
cannot show them. The repository was never modified during measurement.

**Convergence is the strongest evidence here.** Finding 1 was found independently by
five probes with different briefs, findings 2 and 3 by three each, and all of them
measured the same delta to the digit.
