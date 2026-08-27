# Thesis errata — divergences from the published version

`Thesis/` is the **evolving** copy of the dissertation source. Corrections land
here as they are found and justified.

[`ThesisPublished/`](../ThesisPublished/) is the **published** source, frozen:
byte-exact as submitted, and never edited. The published PDF,
[`ucalgary_2020_lindner_sebastian.pdf`](../ucalgary_2020_lindner_sebastian.pdf),
is likewise untouched and remains the authoritative artefact of record.

This file lists every way `Thesis/` differs from `ThesisPublished/`, so the two
can always be reconciled without reading git history. To see the raw difference:

    diff -r ThesisPublished Thesis

**A correction is listed here only if it is justified in the entry.** Where a
change was verified by measurement, the measurement is named. Where it was not,
that is stated plainly rather than left to the reader to assume.

## Status

| | |
|---|---|
| files differing | **3** (`chapter4.tex`, `chapter5.tex`, `chapter6.tex`) |
| entries | **9** (E-T1 … E-T9) |
| published state | commit `399c817` |

---

## E-T1 — `alg:g3nucomp` was missing its addition precondition

**`chapter4.tex:542`.** Commit `1d0bb37`. **Not separately measured; structural.**

The genus-3 ramified addition algorithm required only `deg(u₂) ≤ deg(u₁)`,
where its genus-2 counterpart at `:344` also requires the divisors to differ.
Restored:

```diff
-\Require $[u_1,v_1],$ $[u_2,v_2]$ where $\deg(u_2) \leq \deg(u_1)$.
+\Require $[u_1,v_1],$ $[u_2,v_2]$ where $[u_1,v_1] \neq [u_2,v_2]$ and $\deg(u_2) \leq \deg(u_1)$.
```

This is the precondition whose absence let `ADD(D, D)` go unchecked throughout
the implementation. The code half of the same correction is the equal-divisor
dispatch added to all fourteen ADD dispatchers.

## E-T2 — `alg:g3balnucomp` was missing the same precondition

**`chapter4.tex:646`.** Commit `1d0bb37`. **Not separately measured; structural.**

As E-T1, in the split-model algorithm, in the triple form
`[u₁,v₁,n₁] ≠ [u₂,v₂,n₂]` matching `:427`.

## E-T3 — genus-2 balanced Require had a typesetting fault

**`chapter4.tex:427`.** Commit `1d0bb37`. **Typographical.**

The clause was present but two `$…$` groups ran together with no conjunction,
so the rendered line read as one malformed condition. `" and "` inserted.

## E-T4 — `alg:g3nucomp` middle-branch guard was wrong

**`chapter4.tex:559`.** Commit `1d0bb37`. **Measured.**

```diff
-    \ElsIf{$\deg(s) \leq 2$}
+    \ElsIf{$\deg(s) < 2$}
```

The strongest-evidenced entry here. `verification/reference.py` agrees with this
repository's own `Nucomp_g3_RAM` on 120 of 120 inputs per field, while the
algorithm **as printed** disagrees on 7–13% of generic additions, and the cause
isolates to this single character. After the first branch fails, `deg(s) ≤ 2`
always holds for an addition, which makes the final `Else` unreachable.

`selftest.py`'s `reference` section asserts that the *printed* variant
disagrees, so this correction cannot silently rot: if someone "fixes" the
reference to match the published text, that test fails.

## E-T5 — the same guard in `alg:g3balnucomp`

**`chapter4.tex:668`.** Commit `1d0bb37`. **NOT measured — stated plainly.**

The split-model algorithm has the same guard in the same shape and was corrected
the same way. Unlike E-T4 there is **no split variant of the cross-check**, so
this rests on the structural argument alone. Two supporting observations: its
doubling counterpart at `:610` already uses `<`, as does the ramified one at
`:520`.

## E-T6 — the char-2 normalisation had a misplaced term, and unstated scope

**`chapter5.tex`, subsection "char(k) = 2".** **Measured, three independent ways.**

Three corrections in one passage, all of them in the *thesis*; the implementation was right
throughout and needed no change.

**(a) The transformation's constant term.** As printed, `f₃` was distributed over one term too many:

```
    printed:   f3*(f3 + h1*h2 + f4*h2^2 + f2*h2^2) / h2^3
    corrected: (f3*(f3 + h1*h2 + f4*h2^2) + f2*h2^2) / h2^3
```

The `f₂h₂²` term must stand alone. The printed map is still a *valid isomorphism* — it lands on a
genuine curve — but it leaves `f₂ ↦ f₂(f₃+1)/h₂⁶` rather than `0`, so it does not produce the normal
form claimed beside it. This matches **Lange (2005)**, the source the passage cites, whose numerator
is `f3(f3 + h1h2 + f4h2²) + f2h2²`; the error is a transcription slip.

Evidence: symbolic substitution in characteristic 2 followed by division by `h₂¹⁰`; Magma over 269
genus-2 curves on GF(4)/GF(8)/GF(16)/GF(32) where the printed map left `f₂ ≠ 0` on **229** of them
and the corrected map on **none**, with zero point failures either way; and an independent
homogeneity argument — under `x → α²x, y → α⁵y` every legitimate term of the constant must scale as
`α⁻⁵`, and the stray `f₃f₂/h₂` scales as `α⁻⁹`, so it cannot belong.

**(b) The scope.** `f₄ = f₃ = f₂ = 0` holds **only when `deg h = 2`**. The coefficient `a₀` of the
`y`-substitution enters the degree-2 coefficient solely through `a₀h₂`, so when `h₂ = 0` it drops out
and `f₂` is not clearable. Exhaustive search over the full automorphism group: `deg h = 2` reaches the
form 25/25 of the time, `deg h = 1` 10/25, `deg h = 0` 3–4/25. Lange states the same restriction, and
says plainly that for `h₂ = 0` "f2 cannot [be] assumed to be 0".

**(c) The justification.** "h non-constant is guaranteed because otherwise the curve model is
singular" is false. `y² + y = x⁵` over GF(2) is accepted by Magma as a genus-2 curve with one point
at infinity, and a constant non-zero `h` gives a smooth affine model. Lange's actual reason is
different and correct: such curves are **supersingular**, so the discrete logarithm problem on them
is weaker. Corrected to say that.

**Why the code was not wrong.** `ch2_ramifiedG2_{ADD,DBL}.mag` declare `h2 ∈ {0,1}`, spanning
`deg h < 2` as well, and on that family `f₂` is provably not removable — so keeping `f₂` live was
correct for the domain those files claim, not an oversight. An earlier reading of this repository had
it backwards, treating the thesis sentence as evidence of a code defect.

**Now done, in E-T7.** The formulas are restricted to
`deg h = 2` with `h₂ = 1`, so `f₄ = f₃ = f₂ = 0` is true of the implementation rather than
merely available to assume — the same normal form genus 3 uses, giving both genera one exposition.
That narrows the declared domain rather than fixing an error: curves with `deg h < 2`, including the
Koblitz/subfield family at `deg h = 1`, move to the arbitrary-characteristic formulas, which serve
them correctly at higher cost. Once that lands, this entry's `f₂` discussion describes history.

## E-T7 — the char-2 Degree-2 doubling loses one addition

**`chapter5.tex:900`, `tab:ramfcosts`, char$(k) = 2$ column.** **Measured.**

`21&4&25&0` becomes `21&4&24&0`, in **both** tables that quote this operation:
`tab:ramfcosts` at `chapter5.tex:901` and the `char(k) = 2` "A4 -- This work"
row of `tab:ramfcomparisons` at `:985`. One addition, in two cells; every other
cell in both tables is unchanged.

The comparison table was missed on the first pass, which left the working thesis
quoting 24A and 25A for the same operation eighty lines apart. Found by running
the operation counter over all seven op-count tables: it reproduces 207 of the
208 published own-work quadruples, and the single exception was this cell. Worth
recording as a method — a table that is *not* generated has no other guard
against this, and searching one table for the changed value is not enough when a
second table quotes the same row.

The implementation's char-2 genus-2 formulas were restricted to the full normal
form — `h` monic of degree exactly 2 and `f = x^5 + f_1x + f_0` — which is the
form this chapter derives. `f_2` was previously a live parameter, entering as a
bare additive term, so dropping it removes one addition from every branch that
computed `k_0 = f_2 + \dots`.

**Why only one cell.** `f_2` appeared at five arithmetic sites, and only one of
them is on a frequent path: `Deg2DBL`'s main branch. The other four sit in
special cases — `Deg2DBL`'s `d = 0` branch, and branches of `Deg12ADD` and
`Deg2ADD` that the table does not price. Measured over 2,514 operations against
the pre-restriction formulas on identical curves, with the frequent case
identified by frequency:

| | frequent A, before | after |
|---|---|---|
| Degree 1 doubling | 5 | 5 |
| **Degree 2 doubling** | **25** | **24** |
| Degree 1 and 2 addition | 19 | 19 |
| Degree 2 addition | 26 | 26 |

The rarer branches do move — `Deg12ADD` 27 → 26, `Deg2ADD` 32 → 31 and 41 → 40,
`Deg2DBL` 18 → 17 and 19 → 18 — but no published row quotes them.

**M, S, C and I are unchanged, and the `h_2` half changes no count at all.**
Setting `h_2 = 1` removes 43 real multiplications from the two files, but those
products were declared `//Ignore: h2` and so were already priced at zero: sound
only because the banner declared `h_2 \in \{0,1\}`. The published counts had
therefore always described an implementation that exploits the assumption, while
the shipped code computed the products anyway. That gap is now closed in the
code's favour rather than the table's.

**Evidence.** 2,514 comparisons of the restricted formulas against the
pre-restriction ones on curves in the narrowed domain, **zero disagreements** —
which is the correctness argument, since every curve the restricted formulas
accept is one the old formulas accepted. Independently: `driver.py --strict`
1,428 comparisons against Cantor's algorithm, all matching; the regenerated
whitebox corpus at 22 of 22 branches; and both Magma testers green.

**Not corrected here:** the appendix tables in `latexTables/` are generated by
`latexConverter.py`, which does not currently run, so they still describe the
pre-restriction formulas. They are `\input` nowhere — `appendix.tex` holds empty
stubs — so nothing in the document is inconsistent today.

## E-T8 — eighteen split-model operation counts, from two counting faults

**`chapter5.tex:2333, 2336, 2402`; `chapter6.tex:2380, 2422, 2431, 2440, 2452,
2464, 2473, 2476, 2479, 2482, 2485, 2488`.** **Measured, by two independent
counters that now agree on all 208 published cells.**

Eighteen cells across four tables — `tab:splitfcosts`, `tab:splitfcomparisons`,
`tab:g3splitfcostsADD`, `tab:g3splitfcostsDBL`. Aggregate correction
**M +13, C −13, A −14**. Sixteen are distinct; two are the same operation
restated in a comparison table.

**Entirely split-model.** No ramified count moves, at either genus, so
`tab:ramfcosts` and `tab:ramfcomparisons` are untouched by this entry.

**Two faults in `latexTables/latexConverter.py`, which generated these numbers.**

*A curve constant between two multiplications was charged twice.* The counter
inspects only the tokens immediately flanking each `*`, so a constant at
position *j* satisfies the left test of the `*` after it and the right test of
the `*` before it. `w2*d5*(d2 - v1*t1)` was scored 2C where the cost is 1C + 1M:
once a runtime value enters a multiplicative chain the accumulated left operand
is runtime, and a product of two runtime values is a full multiplication. The
diagnosis is confirmed by the cases that were already right — `f1*a*b` and
`a*b*f1` both scored 1C + 1M before and after, and only the flanked arrangement
changes.

*A unary sign was charged as an addition.* Every `+` and `-` token cost 1A, with
a single hard-coded exemption for one leading `-`. So a leading `+` was charged
(`ch2_splitG3_ADD.mag:4173`, `vpp0 := +v0 + h0 + ...`), and so was every sign
appearing inside an expression — `Deg23ADD` carries three internal negations and
was over-counted by 3A. A sign is unary exactly when the token before it is an
operator, an open parenthesis, or the assignment.

**How the corrected values were established, and why they are trustworthy.**
Two counters that share no code now agree on **every one of the 208** published
own-work quadruples:

| | |
|---|---|
| the static token scan, with both faults fixed | 208 / 208 |
| an interpreter executing the formulas over a finite field | 208 / 208 |
| the corrected tables here, read back from the `.tex` | 208 / 208 |

The interpreter identifies the frequent case by *measurement* — histogramming
many random valid divisor pairs and taking the modal operation tuple — where the
static counter infers it from the source structure. On the eighteen corrected
cells the modal share is 0.80 to 0.99, and every execution contributing to a
count was cross-checked against an independent Cantor implementation.

Two corrections were needed on the measuring side before the counts could be
trusted, and both are recorded because they show what the agreement is worth:
the interpreter charged an inversion and a multiplication for division by two,
where this thesis states plainly that halving is counted as an addition
(`chapter6.tex:2333`); and its constant-detection missed a constant reached
through a unary minus, since `-yn2*W2` parses with the negation bound tighter
than the product. Six of the twenty-four cells first flagged were that second
fault, not a defect in the tables.

**Not corrected here, and worth being exact about.** Both counting faults are
still present in `latexTables/latexConverter.py` as committed — they were fixed
in a working copy to establish these numbers, and repairing the tool itself is
separate work. So the corrected values in the tables above cannot yet be
reproduced by running anything in this repository; they are reproduced by the
interpreter, which can. The generated tables under `latexTables/` likewise still
carry the old numbers, and are `\input` nowhere — the appendix holds empty
section stubs — so no document is inconsistent. The converter additionally does
not run at all in its committed state, for reasons unrelated to counting.

---

## Known defects not yet corrected

Found while reading; recorded here so they are not rediscovered. None is
corrected in `Thesis/` yet.

| where | defect |
|---|---|
| `chapter6.tex:1091` | `u_2 = x^3 + u_{12}x^2 + u_{21}x + u_{20}` — the leading coefficient should be `u_{22}`; `u_{12}` belongs to `u_1`, declared the line above |
| `chapter5.tex:397-401` | bare `u_1`/`u_0` used where `u_{n_1}`/`u_{n_0}` are meant, colliding with `u_1` = input divisor 1; carries into `:410-411` |
| `chapter6.tex:1260-1261` | malformed subscripts, `r_{\vt_2 + r_{q_{11}}t_7 + r_{q_01}}` — an expression inside a subscript and a missing brace pair. The parallel block at `:530-532` is clean |
| `chapter5.tex:1831` | unbalanced parenthesis: `-w_4(` is never closed |
| `chapter5.tex:643` | dangling text: "where only the degree 2 coefficient `k_2 = ` of `k` is used" |
| `chapter4.tex:545` vs `:547` | `alg:g3nucomp` assigns `(S,a_2,b_2)` then tests `S' \neq 1`; `S'` is never defined. `alg:g3balnucomp:651` gets this right |
| `chapter5.tex`, char-2 subsection | the `f₄ = f₃ = f₂ = 0` assumption stated beside `tab:ramfcosts` is **not exploited by the counts**. Those counts are generated from the implementation, which computes `k0 := f2 + …` rather than dropping the term — verified by matching the code's additions, squarings and inversions against the published Degree-2 doubling row exactly (25A, 4S, 1I). So the assumption is real but unused, and a genuinely `f₂`-free derivation would count fewer additions. Being resolved in the implementation's favour: the formulas are being restricted to the full normal form so the assumption becomes true of the code, after which these rows need regenerating |
| `g2/ramifiedModel/g2Formulas/ch2_*` (code, not thesis) | the assumed shape `f = x⁵ + f₂x² + f₁x + f₀` fixes `f₃ = 0`. For `deg h = 2` and `deg h = 1` that is reachable, but when `h` is **constant** `f₃` is an isomorphism invariant, so such curves cannot be brought into the shape at all. `RandomG2Char2Curve` hard-zeroes `f₃`, so the family is never generated and never flagged — a coverage gap, not a formula error |

## A notation inconsistency to resolve before the appendix is filled

The thesis body indexes divisors numerically — `u_1`, `u_2` in, `u_n` out, with
coefficients written by digit concatenation (`u_{11}` = divisor 1, degree 1) and
the output nested (`u_{n_1}`). The **generated tables** in
[`latexTables/`](../latexTables/) use the opposite convention: `D`, `D'`, `D''`
with primes for divisor identity and subscripts meaning degree only
(`u^{\prime\prime}_1`), which is what the Magma implementation uses.

Those tables are not `\input` anywhere yet — `appendix.tex` holds three empty
section stubs — but their totals match `tab:ramfcosts` exactly, so they are
plainly intended to fill them. **Dropping them in as-is would place two
contradictory notations in one document.** Two smaller faults inside the
generated tables themselves: `split_ADD.tex:26` labels the result `D''` but
writes single-primed coefficients, and `split_*.tex` orders coordinates
low-to-high where `ram_*.tex` orders them high-to-low.

## E-T9 — the odd-characteristic counts DO assume `f4 = 0`

**`chapter5.tex:86-87`.** Found 2026-08-12 while vetting the genus-3 odd-characteristic
addition, and provable from the shipped code rather than argued.

**As published:**

> Operation counts in Section~\ref{sec:ramFieldCosts} assume $h = 0$ whenever
> char($k) \neq 2$, but make no assumption about $f_4$.

**The second clause is false.** The genus-2 odd-characteristic addition assumes `f4 = 0`
throughout, three ways over:

| evidence | value |
|---|---|
| occurrences of `f4` in `g2/ramifiedModel/g2Formulas/nch2_ramifiedG2_ADD.mag` | **zero** |
| its banner | `f(x) = x^5 + f3x^3 + f2x^2 + f1x + f0` |
| its `//Constant:` directive | `f3,f2,f1` |

So the file implements the depressed form the *preceding two sentences* of the same
paragraph derive — `x -> x - f4/5`, valid when the characteristic is also not five — and
the counts in `tab:ramfcosts` are counts of that code. The sentence contradicts its own
table.

**Corrected to:** "...assume $h = 0$ whenever char($k) \neq 2$, and additionally assume
$f_4 = 0$ whenever the characteristic is also not five."

**`chapter5.tex:1167` says the same thing about `f_5` and is TRUE — do not touch it.**
That sentence is about the genus-2 *split* model, whose odd-characteristic formulas really
do keep `f5` live: `g2/splitModel/negReduced/g2Formulas/nch2_splitG2_UTL.mag:32` reads
`f5:= Coeff(f,5);`. The two sentences look identical and only one is wrong, which is
presumably how this survived.

**Why it matters beyond the sentence.** It is the same omission at genus 3, where the
odd-characteristic file has kept `f6` live and so implements a curve form **no published
source uses** — every odd-characteristic genus-3 count in the literature assumes
`f6 = 0`. Correcting the genus-2 sentence and depressing the genus-3 file are the same
fix at two genera; see [`../EFFICIENCY_NCH2_G3.md`](../EFFICIENCY_NCH2_G3.md).

**Affects:** the prose only. No table cell moves — `tab:ramfcosts` was always generated
from the `f4`-free code, which is why the contradiction is with the sentence and not with
the numbers.

---

## E-T10 — the genus-3 split Degree-3 rows trade one multiplication for twelve additions

**`chapter6.tex:2389` in `tab:g3splitfcostsDBL` and `:2491` in `tab:g3splitfcostsADD`.**
**Measured, and hand-counted independently.**

**This is not an error in the thesis.** The published counts were correct for the
formulas as published; the formulas have since changed under them. The entry
exists because `Thesis/` must not quote a cost the code no longer has.

    :2389  &73&3&101&19 &72&4&97&0 &71&4&86&1   becomes
           &74&3& 89&19 &73&4&85&0 &72&4&74&1

    :2491  &65&3& 87&12 &65&3&85&0 &65&3&80&0   becomes
           &66&3& 75&12 &66&3&73&0 &66&3&68&0

Six cells, `+1M -12A` in each, across the `arb`, `nch2` and `ch2` columns of both
tables. S and C are unchanged everywhere, and no other row in either table moves.

**What changed.** The addition and doubling now carry the full adjugate of the
`3x3` matrix `T` and apply it as a matrix-vector product, where they previously
built only its first column and reduced `vt*q mod up` by Karatsuba twice. The
trade is `+1M` for `-12A`, which the thesis's own `1M : 3A` rule accepts
comfortably.

**Where the cost actually moves, which the derivation should state.** Not at the
`T` block: that costs `15M 0S 9A` either way, yielding three adjugate entries in
the old arrangement and seven in the new, because column 3 of `T` is `x` times
column 2 reduced modulo the modulus, so six of the nine entries are one
multiplication each rather than a `2x2` minor. The whole `+1M` and the whole
`-12A` are downstream, where applying the matrix costs `12M 8A` against
Karatsuba's `11M 20A`.

**Adjudicated per the standing rule.** `verification/opcount.py` measures the new
figures by execution and a hand count of the changed region reproduces the same
`+1M -12A`, two methods sharing no code. `verification/selftest.py`'s published
pins for `33ADD n=0,0` and `3DBL n=0` are updated with the reason recorded
inline, and every other pinned cell still matches its published value.

## E-T11 — `\EndIf` lines were numbered, so every prose step reference drifted

**`Thesis/thesis.tex` preamble; symptom visible throughout `chapter5.tex` and
`chapter6.tex`.** **Fixed by one preamble line.**

**Reported by the author**: the description of *Genus 3 Split Model Degree 3 Addition*
"ends up being 3 lines off", and separately that a formula attributed to Steps 14--16
looked like Step 18.

**Cause.** `algorithmic[1]` numbers `\EndIf` lines. The prose never counted them as steps.
Each `\EndIf` therefore shifts every later reference by one, and the drift grows down each
algorithm. `alg:g3explSPLIT3ADD` has three, which is exactly the reported figure.

**Fix:** `\algtext*{EndIf}` in the preamble, which removes those lines from the output
entirely. The prose numbering was correct as written; nothing in either chapter needed
renumbering for this cause.

**Verified by hand on two algorithms chosen because they discriminate:**

| algorithm | prose claim | lands on |
|---|---|---|
| `alg:explRAM2ADD` | weights at Steps 12--13 | 12--13 |
| | `u_n = (s''(\vt - v_1/s_1) + k/s_1^2)/u_2` at Steps 14--16 | 14--16 |
| | `v_n = \vt \pmod{u_n}` at Step 17 | 17 |
| `alg:g3explSPLIT3ADD` | `\vt` 6, `s'` 7, `k` 15, `M_2'` 16, `u_n` 17 | all five exact |

**Checked again on the author's prompt, and the discriminating comparison is now explicit.**
`alg:explRAM2ADD` carries two `\EndIf` and **zero** `\State` escape lines, so the escape
hypothesis predicts no shift at all there:

| prose Step | expects | counting `\EndIf` | suppressing it |
|---|---|---|---|
| 13 | monic `s''` / weights | `\EndIf` | `Compute monic $s''$` |
| 16 | `u_n = (s''(\vt - v_1/s_1) + k/s_1^2)/u_2` | `k = (f - v_1(v_1+h))/u_1` | the `u_n` line |
| 17 | `v_n = \vt \pmod{u_n}` | `\vt = -su_1 - v_1 - h` | the `v_n` line |

Three of three suppressing, none of three counting.

Broadened as well: pairing each prose `In Step~N, <description>` with the algorithm block it
immediately follows gives **14 matches across 8 algorithms** in both chapters, among them
`alg:explRAM1DBL`, `alg:explRAM12ADD`, `alg:explRAM1ADD`, `sub:explRAM2ADDd`,
`alg:g3explSPLIT3DBL` and `alg:g3explSPLITpre` -- a range of sizes and structures. Pairing
by "the block above" is what the document actually does, and it avoids the mis-pairing that
broke three earlier automated attempts.

*One harness bug found while doing this, worth recording as a method note.* A comparison of
the two hypotheses came back identical for every algorithm, which looked like evidence they
were indistinguishable. The regex listed `State|If|ElsIf|Else|...` without `EndIf`, and
`\EndIf` never matches `\If` because of the leading `\\` anchor -- so both branches had
already dropped `\EndIf` and were equal by construction. Alternation order matters: `EndIf`
must precede `If`.

**A WRONG DIAGNOSIS WAS COMMITTED FIRST AND IS REVERTED HERE.** The initial reading blamed
`\State Go to ... Subroutine` and `\State See description below.` lines, and changed 20 of
them to `\Statex`. That reading fit `alg:g3explSPLIT3ADD` perfectly **by coincidence**: it
has three such lines *and* three `\EndIf`s, so both hypotheses shift by exactly three
there. `alg:explRAM2ADD` discriminates -- two `\EndIf`s, zero `\State` escapes -- and only
the `\EndIf` explanation survives it. The 20 `\Statex` edits are reverted.

*A hypothesis that fits one instance exactly can still be wrong, and the instance that
looks most convincing is the one least able to discriminate.*

**A second correction to the earlier commit.** With `\EndIf` counted, the offset in the
degree 1 and 2 addition passage looked non-uniform, and its last range was rewritten as
Steps 15--17. Under the correct numbering the offset is a uniform +1 and that range is
**14--16**. Fixed.

**Also fixed here:** `chapter5.tex:643` read `\vh_1 = h_1 + v_1` inside a block that
otherwise writes `v_{11}`, `u_{11}`, `u_{21}`.  It is **`v_{11}`**, the first divisor.

**This entry first said `v_{21}` and that was wrong.** The reasoning was that the enclosing
`alg:explRAM2ADD` is an addition whose XGCD takes `h + v_1 + v_2`, so the second divisor must
appear; and the code idiom `vh1 := h1 + vp1` was cited in support.  Both halves fail.  That
idiom is from `Deg12ADD` (`arb_ramifiedG2_ADD.mag:134,181`), a *different* function, where the
primed group is the degree-2 divisor.  The function this passage describes is `Deg2ADD`, whose
signature is `Deg2ADD(u1,u0,v1,v0,up1,up0,vp1,vp0,...)` with the unprimed group first, and
whose corresponding lines read

    t4   := h1 + v1;
    upp0 := spp0*(t3 - m3) + m1 + w3*(h2*(spp0 - up1) + t4 + v1) + w4*(u1 + up1 - f4);

at `:449` and `:451`, repeated verbatim at `:410` and `:412` in branch `ADD09`.  So `\vh_1`
is `h_1 + v_1` **unprimed**, and the thesis block's `\vh_1 + v_{11}` is `t4 + v1`, that is
`h_1 + 2v_{11}`.

**And the passage says so two lines above the block.** It states the polynomial being computed
as `u_n' = (s(-su_1 - 2v_1 - h) + k)/u_2`, whose `2v_1 + h` has degree-1 coefficient
`h_1 + 2v_{11}`.  `v_2` enters this step only through `s` and `k`, never as a bare
coefficient, so no `v_{2i}` belongs in the block at all.  The XGCD's `h + v_1 + v_2` is a
different step.

**The lesson is the one this project keeps relearning: a code idiom is evidence only from the
function under discussion.** The generalisation from `Deg12ADD` to `Deg2ADD` was never
checked, and the reading it overrode -- the one a reader would naturally guess -- was correct.

**What is NOT claimed.** No global "every reference resolves" statement. Three successive
attempts to verify that automatically were each wrong -- counting only `\State` lines (13
steps where there are 19), missing plural `Steps~N--M` forms (51 references where there are
87), and mis-pairing a step number with a nearby unrelated `\ref`. A trustworthy
reference-checker is its own piece of work and is not attempted here. What is verified is
the two algorithms above, by hand, and the cause they share.

**Seven anchors across the two genus-3 split algorithms settle it, and they reproduce the
author's own report.** Each algorithm carries `\EndIf` lines before its arithmetic begins,
and the chapter 6 prose names steps of each by number.  Numbering both ways:

| algorithm | step named in prose | prose says | `\EndIf` numbered | `\EndIf` suppressed |
|---|---|---|---|---|
| `3DBL` | monic quotient `q'`, remainder `r'` | 10--11 | 12--13 | **10--11** |
| `3DBL` | compute the six ratios | 14 | 17 | **14** |
| `3DBL` | `M_2' = (r(2v_1 + h) + qk)/u_1` | 15 | 18 | **15** |
| `3DBL` | `z`, then `v_n` | 17--18 | 20--21 | **17--18** |
| `3ADD` | compute the six ratios | 14 | 17 | **14** |
| `3ADD` | `M_2' = (r(v_2 + v_1 + h) + qk)/u_2` | 16 | 19 | **16** |
| `3ADD` | `u_n = r(q(v_2 - v_1) + u_1r)/(u_2c_4r_1q_1) - qM_2'/q_1` | 17 | 20 | **17** |

Every one lands exactly with suppression.  Without it each is off by precisely the number of
`\EndIf` lines above it, which is 2 for the first row and 3 for the rest.  The author
reported the Degree 3 Addition description as "3 lines off" before any diagnosis was
attempted, and three is that algorithm's `\EndIf` count.  Seven anchors do not land on their
stated numbers by coincidence, and the first row is the useful one for a different reason:
it is off by **two**, not three, so it rules out a constant offset from any other cause.

**One typo found by the same numbering, and corrected.** `chapter6.tex:1257` introduced the
`3ADD` `u_n` block as "The explicit formula for Step~15 is", where step 15 of that algorithm
is `k`.  The sentence immediately above says "In Step~17, the output polynomial
$u_n = rM_1 - qM_2$ ... is directly computed monic", and the parallel block above that reads
"In Step~16 ... The explicit formula for Step~16 is", so the label is Step~17.  Present at
`ThesisPublished/chapter6.tex:1257` as well, so it is not an artifact of this branch.

**The identical string 736 lines earlier is CORRECT and was deliberately not touched.**
`chapter6.tex:521` also reads "The explicit formula for Step~15 is", but that passage belongs
to `3DBL`, whose step 15 really is `M_2'`.  Two occurrences of one string, one right and one
wrong, is exactly the case a blind substitution ruins, so the edit was anchored on the
surrounding sentence rather than on the string.

**One further step reference in the same passage is left alone.** After the `u_n` block,
"the computation of $z = (ru_1 - u_n)/q$ in Step~17 must be adjusted" names Step~17, but `z`
is step 18 of `alg:g3explSPLIT3ADD` and step 34 of `alg:g3balnucomp`, and the sentence cites
neither algorithm explicitly.  It is not clear which numbering is intended, so it is recorded
rather than guessed.  Wants the author.

**The page count is no longer evidence against this.** Suppressing `\EndIf` shortens the
build by seven pages, which read as moving away from the published 267 while two other
reconstruction defects were still in place.  Both are now fixed and the build totals 266
against a published 267 whose first page is a repository cover sheet, so it agrees exactly.
See `Thesis/README.md`.

## E-T12 — a spurious `r_{` swallowed two terms of the genus-3 split Degree 3 Addition u_n

**`chapter6.tex:1260-1261`, the explicit formula for Step~17 of
`alg:g3explSPLIT3ADD`.** **Corrected against the code.**

    u_{n_1} = c_6(r_{\vt_2 + r_{q_{11}}t_7 + r_{q_{01}}} + r_{q_{01}}) + …
    u_{n_0} = c_6(r_{\vt_2r_{r_{01}} + r_{q_{01}}}(t_7 + r_{r_{01}})) + …

An `r_{` was inserted before `\vt_2` and its closing brace landed after
`r_{q_{01}}`, subscripting `r` by a two- or three-term expression. Both lines now read as
`arb_splitG3_ADD.mag` computes them:

| corrected | code |
|---|---|
| `c_6(\vt_2 + r_{q_{11}}t_7 + r_{q_{01}} + r_{q_{01}}) + M'_{20} + q_{q_{01}}M'_{21}` | `c6*(vt2 + rq11*t7 + rq01 + rq01) + M20p + qq01*M21p` |
| `c_6(r_{r_{01}}\vt_2 + r_{q_{01}}(t_7 + r_{r_{01}})) + q_{q_{01}}M'_{20}` | `c6*(rr01*vt2 + rq01*(t7 + rr01)) + qq01*M20p` |

**The reading that looked obvious was wrong, and this is the point of the entry.** The
natural repair is to close the subscript after `\vt_2`, giving `r_{\vt_2} + …`. The code
shows there is no `r_{\vt_2}` object: the term is plain `\vt_2` and the whole `r_{` was
spurious. That repair would have compiled cleanly and been wrong, with nothing to catch
it -- LaTeX cannot tell a well-formed subscript from an intended one.

The tell that confirms the correction is the doubled `r_{q_{01}} + r_{q_{01}}`: the broken
text kept one copy inside the bogus subscript and one outside, and the code has both.

Two smaller faults in the same block were fixed alongside: `r_{q_01}` for `r_{q_{01}}`
twice, and a missing `+` before `q_{q_{01}}M'_{20}` that the parallel Step~16 block has.

## E-T13 — eight generated OUT rows primed the result as an input

**`latexTables/split_ADD.tex`, eight `\bf{OUT:}` rows.** **Fixed.**

Each row declares `$D + D' = D'' = [\ldots]$` and then wrote its coefficients
single-primed, `u^{\prime}_1`. Single primes belong to `D'`, the second *input*, so those
rows named the result with the notation of an operand. Now `u^{\prime\prime}`, matching
every other generated table -- `split_DBL`, `ram_ADD`, `ram_DBL` and `ram_arb_ADD` are all
double-primed throughout, so `split_ADD.tex` was the sole outlier.

Lines 26, 45, 79, 94, 134, 153, 191 and 206. Scoped to `OUT` rows so no body formula was
touched.

**Two things in the same file are deliberately left.**

`:191` and `:206` now read `[u^{\prime\prime}_1,u^{\prime\prime}_0,v_1,v_0,0]` and
`[1,u^{\prime\prime}_0,y_1,v_0,1]` -- the `v` coefficients are *unprimed*, so they name the
first input. That may be correct: in a degenerate case the output `v` can be the input `v`
unchanged. Deciding needs the case, not the notation.

`:253` has `[0,1,y_1,y_0,_1nn^{\prime}_1]` in the balancing-weight slot, which is a
generation artifact. **It compiles** -- `,_1` subscripts the comma, legal and meaningless --
so no build catches it, and the file has never been compiled anyway, being `\input`
nowhere. What the weight should be needs the author.

**A retraction belongs here.** Four `IN` rows in this file read `D' = []`, which is exactly
the signature `ERRATA.md` **E4** describes for `latexConverter.py`'s drained `filter()`. It
is not that bug: all four are `01ADDDWN`, `01ADDUP`, `02ADDDWN` and `02ADDUP`, degree-zero
additions whose second divisor genuinely is the identity. E4's claim that the committed
`.tex` is unaffected stands.

**Also corrected: the recorded description of the coordinate-ordering problem.** The
project's plan said `split_*.tex` orders coordinates low-to-high while `ram_*.tex` orders
high-to-low. Measured, both files *mix* orderings internally -- `split_ADD` 28 ascending
against 18 descending, `ram_ADD` 9 against 5, `ram_arb_ADD` 6 against 8. So it is not a
disagreement between two files with a consistent convention each; no file is internally
consistent. That is a larger problem than recorded and is folded into PR31, where these
tables first get used and a reader would see it.

## E-T14 — the three front-matter list references are one page low

**`Thesis/frontmatter.tex`, and the published PDF carries it too.** **Recorded, not fixed.**

The table of contents lists its own three front-matter entries one page below where they
print, in the published thesis and in the rebuild alike:

| entry | table of contents says | actually prints on |
|---|---|---|
| Table of Contents | iv | v |
| List of Tables | viii | ix |
| List of Algorithms | ix | x |

**The cause is that each contents line is written before the page break that starts the
list**, so it records the preceding page.  For the list of algorithms it is visible in the
source: `frontmatter.tex:65` issues `\addcontentsline{toc}{chapter}{List of Algorithms}` on
the line above `\listofalgorithms`, and the class comment immediately below says memoir does
not clear the page for content lists and that `ucalgmthesis` fixes this for its own table of
contents and lists of tables and figures but not for anything else.  `listofalgorithms` comes
from the `algorithm` package, so it is not covered.

**Not a convergence artifact, and not an artifact of the reconstruction.** Six `pdflatex`
passes leave it unchanged with zero rerun requests, and the rebuild reproduces the defect
exactly one page further along, claiming ix and x where it prints x and xi.  Reproducing the
original's quirk is evidence the reconstruction is faithful.

**Why it is left alone.** A `\clearpage` before the `\addcontentsline` corrects the list of
algorithms entry only.  The other two are written by the class rather than by these sources,
so a one-line fix would leave two of three wrong while changing the front matter.  Wants the
author's call.
