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
| files differing | **2** (`chapter4.tex`, `chapter5.tex`) |
| entries | **7** (E-T1 … E-T7) |
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

`21&4&25&0` becomes `21&4&24&0`. One addition, in one cell; every other cell in
the table is unchanged.

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
