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
| files differing | **1** (`chapter4.tex`) |
| lines differing | 5 |
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
