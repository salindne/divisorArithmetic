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

## E-T11 — twenty cross-reference lines were numbered as algorithm steps

**`chapter5.tex` and `chapter6.tex`, 15 algorithm and subroutine blocks.** **Measured.**

**Reported by the author**: the description of *Genus 3 Split Model Degree 3 Addition*
"ends up being 3 lines off". It does, and the prose was never wrong -- the algorithm
over-numbers.

`\State Go to ... Subroutine~\ref{...}` and `\State See description below.` are
cross-references, not computational steps, but `\State` numbers them. Each one shifts
every later step by one. `alg:g3explSPLIT3ADD` and `alg:g3explSPLIT3DBL` carry three
each, which is exactly the reported drift.

**The prose numbering is the correct one.** Counting every line except those three
reproduces the text's claims for `alg:g3explSPLIT3ADD` exactly:

| line | prose says |
|---|---|
| `\vt = v_2 - v_1` | Step 6 |
| `s' = \vt t \pmod{u_2}` | Step 7 |
| `k = (f - v_1(v_1 + h)/u_1)` | Step 15 |
| `M_2' = (r(v_2 + v_1 + h) + qk)/u_2` | Step 16 |
| `u_n = r(q(v_2 - v_1) + u_1r)/(u_2c_4r_1q_1) - qM_2'/q_1` | Step 17 |

**Fixed by making the cross-references unnumbered**, `\State` -> `\Statex` at 20 sites,
7 in `chapter5.tex` and 13 in `chapter6.tex`. That is the cheap direction: the
alternative was renumbering prose references across two chapters, which would also have
enshrined "Go to Subroutine X" as a step of the computation.

**Verified after the fix**: `alg:g3explSPLIT3ADD` numbers 20 steps and every claim in the
table above lands on the right line. Across both chapters, all 51 explicitly-labelled
`Step~N of Algorithm~\ref{...}` references now resolve to a step that exists, up from 49.

**The two `Step~0` passages are now 1-based too**, the author having decided that the
thesis numbers from 1 as `algorithmicx` prints. `algorithmicx` never emits a step 0, and
in both cited algorithms the "Step 0" content -- a negative reduced normalisation of `v_1`
-- is genuinely step 1.

Each boundary was verified against content rather than shifted blindly, which mattered:
the offset is not uniform. For `alg:explSPLIT12ADDUP`,

| prose was | now | why |
|---|---|---|
| Step 0 | 1 | `v_1 = -\Vp - h - (…)`, the normalisation |
| Steps 1-3 | 2--4 | `d = u_1 \pmod{u_2}` and its zero test |
| Steps 4--12 | 5--13 | begins at `z = (f - v_1(v_1 + h)/(c_3u_1)`, the `z = k/c_3` the prose names |
| Steps 13--15 | **15--17** | `w`, `\vt`, `u_n`. Not 14--16: step 14 is a bare `\EndIf`, no part of the described computation |

A uniform shift would have put the `u_n` computation outside the cited range.


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
