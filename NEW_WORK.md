# New work

What this project contributes beyond the published thesis, written to be
lifted into the next publication.

[`RELATED_WORK.md`](RELATED_WORK.md) records what other people did. This file
records what **we** did: every correction, completion and result, with the
argument for why it is right and the measurement that establishes it. It is
written for a reader who will turn it into paper prose, so each entry says what
was there before, what changed, why the change is correct, how that was
established, and what a paper would claim from it.

**This file is maintained as the work progresses.** Every PR that corrects the
thesis, changes a formula, or establishes a mathematical result adds its entry
here in the same commit. An entry written months later from git history is
worth a fraction of one written while the reasoning is fresh — the *why* is the
part that does not survive in a diff.

## Relationship to the other documents

Four documents already exist and this one deliberately does not duplicate them:

| document | what it holds | what it does not |
|---|---|---|
| [`ERRATA.md`](ERRATA.md) | defects in published material, E1–E10, with reproducers | why they matter, or what replaces them |
| [`Thesis/ERRATA.md`](Thesis/ERRATA.md) | every divergence of `Thesis/` from `ThesisPublished/`, E-T1–E-T6 | the mathematics behind a correction, at length |
| [`RELATED_WORK.md`](RELATED_WORK.md) | the literature, normalised to our counting conventions | our own contributions |
| [`EFFICIENCY_ARB_G3.md`](EFFICIENCY_ARB_G3.md) | 30 efficiency findings, per-site, with deltas | the framing that makes them a result |

Those are working records. **This one is the narrative**, and it is the only
place where the *reasoning* is written out at publication depth. Where an entry
below has a short counterpart in one of the four, it links to it rather than
restating the detail.

## Status

| # | contribution | status |
|---|---|---|
| **Part I** | Normal forms: one account for both genera and all characteristic classes | **established**, reproducible |
| N1 | The NUCOMP branch guard is wrong as printed | **established**, measured |
| N2 | The addition algorithms are missing their distinctness precondition | **established** |
| N3 | The characteristic-2 normalisation: misplaced term, unstated scope, wrong justification | **established**, three ways |
| N4 | `ADD(D, D)` is silently wrong in all fourteen families | **established**, fixed, gated |
| N5 | One addition branch returns the wrong number of values | **established**, fixed |
| N6 | `h` may be taken monic at genus 3, in every characteristic | **established**, declared |
| N7 | The genus-3 curve generator produced curves outside the declared domain | **established**, fixed |
| N8 | Addition counts for the previous best, derived where the authors never stated them | **established** |
| N9 | Constant multiplications, on both sides of the comparison | **established** |
| N10 | The project's own addition counts were over-stated by a broken counter | **established**, corrected |
| N11 | The arbitrary-characteristic genus-3 formulas carry dead and duplicated work | **established**, not yet implemented |
| N12 | An independent reference implementation and differential oracle | **established**, in CI |
| N13 | Three assumptions in one family were declared but never exploited | **established**, one now closed |
| N14 | Two counting faults put eighteen published operation counts wrong | **established** by two independent counters |
| N15 | Operation counts measured by execution, not by scanning text | **established**, in the repository |
| N16 | A declared domain was masking a transcription slip, not buying anything | **established**; defect recorded, not yet fixed |
| N17 | The genus-3 ramified addition now beats the split-model one on M+S, C and A | **implemented**; superseded by N18 |
| N18 | The doubling trades one multiplication for twenty-two additions; the ledger is closed but for two open items | **implemented**, measured, Magma-verified |
| N19 | The specialised odd-characteristic addition had fallen behind the general one it specialises | **implemented**; the invariant is now asserted in CI |
| N20 | The polynomial reference blocks are executable, so they became a second oracle | **established**; 12 functions checked, 3 defects found |
| N21 | Two weights that were larger than the mathematics requires, and a Bézout cofactor that is a constant | **implemented and measured**; both addition files |
| N22 | A degree-order convention adopted everywhere except one function | **implemented and measured**; pure refactor |
| N23 | When to build the inverse and when the adjugate: the trade runs both ways | **implemented and measured**; both addition files |
| N24 | What the reference block is for, and two facts found by making it say so | **established**; documentation plus two results |
| N25 | Reduce before you divide: the second cofactor collapses to a scalar at `Deg23ADD` | **implemented and measured**; both addition files |
| N26 | The same collapse at `Deg3ADD`, plus the reduce-first rule extended to multiplication and bounded | **implemented and measured**; both addition files |
| N27 | A reference block written leaf-for-leaf against the code becomes a debugger; the defect class surviving every static check is the defined-with-the-wrong-value read; and `l = r*s + M2` needs no division | **implemented and verified**; the doubling at **54M 4S 84A 4C**, 3 defects found, 2 gates repaired, 6-lens sweep |
| N28 | The sixth cell of the matrix: the odd-characteristic doubling, derived rather than borrowed; `M21 = -kp3`, a quotient coefficient recomputed under another name; and branch coverage by enumeration rather than sampling | **implemented and verified**; `25M 4S 44A 0C` and `53M 5S 61A 0C`, 48/48 branches by constructed case, E12 closed, 28 testers 0 skips |
| N29 | The last two cells: characteristic 2 at genus 3, where the doubling's saving is mostly arithmetic that stops existing because half of every integer multiplier is zero; E19, a sentence in a banner that could silently redefine the tested domain; and E20, a green Magma run that carried no information | **implemented and verified**; `51M 3S 62A 0C` and `51M 4S 55A 2C`, 1,777 additions and 2,223 doublings against Magma's Jacobian 0 wrong, six-cell matrix complete, 30 testers 0 skips, one saving refused for want of an oracle |
| N30 | A multiplication that moved rather than vanished: `t7*m3 = t2*m8` by associativity, so the determinant needs `m8` and `m3` belongs with its only other reader | **implemented and verified**; `-1M` on every degenerate `Deg3ADD` leaf across all three families and the arb doubling, frequent case unchanged, and the op-count ledger corrected by the gate rather than by reading |
| — | [In flight](#part-vii--in-flight) | decided, not yet established |

---

# Part I — Normal forms

**The single most reusable result here, and the one a paper should lead with.**
Every formula file in this repository declares a curve shape in its banner, and
each declaration is a claim that an arbitrary curve can be brought to that shape
by an isomorphism — so restricting to it costs no generality. Six such
forms exist across two genera and three characteristic classes. **Five are
declared by a shipped ramified banner today, and only three of those
declarations were already the form derived here.** They had been inherited
piecemeal from different sources, justified differently in each place, and one of
them is wrong in the published thesis (N3). **All six now match**, and each
arrived by its own route: the genus-2 characteristic-2 banner stopped declaring
`h₂ ∈ {0,1}` with `f₂` live, and became `deg h = 2, h₂ = 1` with `f₂` gone; the
genus-3 `nch2` banner dropped `f₆` when the depression was applied; and the
genus-3 characteristic-2 banner was written to the derived form from the start,
being the last of the six to exist at all. That the account produces all six, and
that all six files now declare what it produces, is the claim Part I is making.

What follows is **one account that produces all six**, uniform in the genus, and
it is verified rather than argued: [`verification/normal_form.py`](verification/normal_form.py)
reproduces every claim below in about a minute.

    python3 verification/normal_form.py

## The transformation group, and its budget

For a ramified (imaginary) model `y² + h(x)y = f(x)` with `f` monic of degree
`2g+1`, the isomorphisms preserving that shape are generated by

| | transformation | parameters |
|---|---|---|
| scaling | `x → α²x`, `y → α^(2g+1)y`, divide through by `α^(4g+2)` | `α ≠ 0`, 1 |
| translation | `x → x + β` | `β`, 1 |
| shift | `y → y + a(x)`, `deg a ≤ g` | `a_g … a_0`, `g+1` |

That is `g + 3` parameters. The curve has `g + 1` coefficients in `h` and
`2g + 1` in `f` below the monic leading term, so `3g + 2` in all. The budget is
therefore tight but not trivially so, and **how you spend it is the whole
design question** — the three characteristic classes spend it differently, and
that is why their normal forms differ.

## The degree-g floor rule

The result that explains where every form stops.

> **Rule.** Let `h` be monic of degree exactly `g`. The shift `y → y + a(x)`
> with `deg a ≤ g−1` clears exactly the coefficients `f_{2g−1}, …, f_g` of `f`,
> triangularly and without obstruction — and it cannot reach any lower.

The mechanism, in characteristic 2 where the shift leaves `h` untouched and
sends `f → f + a² + a·h`:

- `a_i` reaches degree `i + g`, through the product `a_i · h_g = a_i`. The
  leading coefficient of `h` is the lever, which is why `h` must be monic of
  degree **exactly** `g` — at `h_g = 0` the lever is gone.
- `a_i²` lands at degree `2i`, and `2i < i + g` precisely when `i < g`. Every
  square therefore falls **strictly below** the coefficient its own `a_i`
  controls, so solving from the top down is triangular and never doubles back.
- The floor is `g` because `deg a` stops at `g−1`. Below `f_g` there is no
  lever at all.

So `g` shift parameters clear `g` coefficients, and `f_{g−1}, …, f_0` survive
in every characteristic-2 normal form. At genus 2 that leaves `f₁, f₀`; at
genus 3, `f₂, f₁, f₀`.

**This is the answer to a question that confused this project twice** — why
`f₃` is removable at genus 3 while `f₂` is not, when `f₂` *is* removable at
genus 2. The floor sits at `f_g`, so it moves with the genus: `f₂` is the floor
at genus 2 (removable, just), and `f₂` is one below the floor at genus 3
(not removable, ever). The two facts were repeatedly read as contradictory and
are not.

**And it is conditional on `deg h = g`,** which is the other half of the
confusion. When `deg h < g` the `a_0` lever `a_0 · h_g` vanishes and the floor
coefficient is no longer clearable. Verified by exhaustive search over the
entire shift space rather than by sampling: of 72 curves with `deg h < g`, **68
cannot reach the floor by any shift whatsoever**. The remaining four are
small-field coincidences, not a route. This is exactly the condition Lange
states for genus 2 and the reason the published `f₄ = f₃ = f₂ = 0` holds only at
`deg h = 2` — see N3.

## Characteristic 2: spend the budget on `f`

Three steps, in this order.

1. **Scale `h` monic.** `α = h_g`. This divides by nothing but `h_g` itself, so
   it is valid in **every** characteristic — no small-prime condition anywhere.
   Costs 1 parameter, buys 1 coefficient.
2. **Translate to kill `f_{2g}`.** `x → x + f_{2g}`. Unconditional in
   characteristic 2, and the reason is worth stating because it is not
   obvious: `deg f` is odd, so the `x^{2g}` coefficient of `(x + β)^{2g+1}` is
   `(2g+1)β = β`, since `2g+1` is odd and hence 1 modulo 2.
3. **Shift to clear the floor**, `f_{2g−1} … f_g`, by the rule above.

Total: `g + 2` parameters spent, `g + 2` coefficients cleared, leaving `h` with
`g` free coefficients and `f` with `g`.

| | normal form reached |
|---|---|
| genus 2 | `y² + (x² + h₁x + h₀)y = x⁵ + f₁x + f₀` |
| genus 3 | `y² + (x³ + h₂x² + h₁x + h₀)y = x⁷ + f₂x² + f₁x + f₀` |

**Why step 2 uses the translation and not the shift, which is the subtle part.**
The shift *could* be given degree `g` rather than `g−1`, and `a_g` would then
reach `f_{2g}` — but it reaches it as `a_g² + a_g`, an Artin–Schreier
expression, solvable only when the absolute trace of `f_{2g}` vanishes. Measured:
**315 of 600 random curves have `Tr(f_{2g}) ≠ 0`**, so that route fails about
half the time. Routing `f_{2g}` through the translation instead is unconditional,
and it is what makes the form above hold for *every* curve with `deg h = g`
rather than for a trace-selected half of them.

This is a real distinction from the literature rather than a presentational one.
Birkner's characteristic-2 genus-3 classification reaches `f₆ ∈ F₂` — a residue
left exactly where the trace obstruction bites — while normalising `h` further
(to `x³ + x + h₀`, and only for irreducible `h`) and giving up monic `f`. Same
budget, different allocation: **Birkner spends it on `h`, we spend it on `f`**,
and our form applies to any degree-3 `h` rather than to irreducible `h` only.
The two forms are worth reconciling explicitly in the paper, along with GKP's two
variants, and as a **comparison rather than a claim of priority** — neither
dominates, and saying which is preferable requires naming what you are optimising.
That is publication work, not repository work: no formula, count or test here
depends on it, and the material it needs is already committed in
[`RELATED_WORK.md`](RELATED_WORK.md), which carries both normal forms and GKP's
`1I + 62M + 5S / 100A` with citations.

## Odd characteristic: spend the budget on `h`, and stop one coefficient in

In characteristic `≠ 2` the shift does something much better: `y → y − h/2`
sends `h → 0` outright, removing all `g+1` of its coefficients at once. That is
one more coefficient than the shift buys in characteristic 2 (`g`), so it is the
right trade — **but it spends the shift entirely.** Any further `y → y + a`
would reintroduce `h = 2a ≠ 0`.

What remains is `x → α²x + β`, `y → α^(2g+1)y`: two parameters. `β` kills
`f_{2g}`; `α` only rescales. So the odd-characteristic normal form stops at
`f_{2g} = 0` and nothing below it is reachable. Verified by exhaustive search
over that entire surviving group — `f_{2g}` cleared on **80 of 80** curves,
`f_{2g−1}` unreachable on **76 of 80**.

| | normal form reached |
|---|---|
| genus 2 | `y² = x⁵ + f₃x³ + f₂x² + f₁x + f₀`, `char ∉ {2, 5}` |
| genus 3 | `y² = x⁷ + f₅x⁵ + f₄x⁴ + f₃x³ + f₂x² + f₁x + f₀`, `char ∉ {2, 7}` |

**The characteristic condition is necessary, not conservative.** `β` must
satisfy `(2g+1)β = −f_{2g}`, so it fails exactly when the characteristic divides
`2g+1`: 5 at genus 2, 7 at genus 3. Measured directly — over `GF(2g+1)`, `f_{2g}`
is invariant under **every** translation, on 155 genus-2 and 163 genus-3 curves.
There is no choice of `β`, not merely no convenient one.

Every published odd-characteristic genus-3 formula set assumes `f₆ = 0`
(Kuroki, Gonda, Guyot–Kaveh–Patankar, Nyukai, Fan–Wollinger–Gong — see
`RELATED_WORK.md` lane 1), so this is the standard form and not our invention.
The contribution here is that **our `nch2` genus-3 file does not yet apply it**,
which is N-in-flight below and makes our counts incomparable in the direction
that flatters nobody.

## Arbitrary characteristic: you cannot spend it at all

The `arb` family must serve every characteristic and every `deg h ≤ g` with one
set of formulas. Completing the square is unavailable (characteristic 2 might
hold); the floor rule is unavailable (`deg h = g` might not hold). **Only step 1
survives** — the scaling is the one transformation with no condition on
characteristic — and even it only gives `h_g ∈ {0, 1}`: monic when `deg h = g`,
zero otherwise.

So the honest `arb` banner is `h_g ∈ {0,1}` with every `f` coefficient live,
which is what the files now declare (N6). That this is the *maximum* obtainable
is not a limitation of anyone's effort; it follows from the account above.

## What is new here, stated carefully

The individual moves are known. The `α`-scaling at genus 2 is Lange's; the
depression is standard; Artin–Schreier obstructions in characteristic 2 are
textbook. Three things are, as far as the literature reviewed in
`RELATED_WORK.md` shows, not written down anywhere in this combined form:

1. **The uniform statement.** One `g`-indexed account producing all six
   declared forms, with the floor at `f_g` and the budget identity
   `g + 2` parameters ⇄ `g + 2` coefficients. The literature treats genus 2 and
   genus 3 separately and characteristic 2 and odd separately, so the
   *pattern* — that odd characteristic buys one more coefficient by spending
   the shift on `h`, and characteristic 2 buys one fewer but keeps `h` — is
   invisible from any single source.
2. **The routing observation**, that sending `f_{2g}` through the translation
   rather than the shift converts a trace-obstructed normalisation into an
   unconditional one. This is what makes our characteristic-2 genus-3 form hold
   for all degree-3 `h`.
3. **That it is machine-checked**, including the negative controls. Normal-form
   claims in this literature are conventionally asserted with a substitution and
   left; one of them turned out to be wrong for twenty years of citation (N3).

**Evidence.** [`verification/normal_form.py`](verification/normal_form.py), five
checks: 120 curves fully normalised at both genera over `GF(2)`…`GF(32)` with
**1,497 affine points transported and none lost** (pointwise, not by point
count — a count alone cannot distinguish an isomorphism from a coincidence of
order); the floor rule's negative control, 68/72 exhaustively stuck; the
Artin–Schreier control, 315/600 blocked; the odd-characteristic group search,
80/80 and 76/80; and the depression's necessity, 318 curves over `GF(5)`/`GF(7)`.

---

# Part II — Corrections to the published thesis

All three are recorded tersely in [`Thesis/ERRATA.md`](Thesis/ERRATA.md). What
follows is the reasoning at the depth a paper needs. `ThesisPublished/` is
frozen byte-exact and none of these touch it.

## N1 — The NUCOMP branch guard is wrong as printed

**Status:** established, measured, corrected in `Thesis/`. E-T4, E-T5.

**Where.** `chapter4.tex:559` (`alg:g3nucomp`) and `:668` (`alg:g3balnucomp`).

**What was there.** The middle branch of the genus-3 NUCOMP dispatch tests
`deg(s) ≤ 2`.

**What it should be.** `deg(s) < 2`.

**Why.** After the first branch fails, `deg(s) ≤ 2` holds for *every* addition,
so the printed guard is a tautology at that point: it swallows the remaining
cases and makes the final `Else` unreachable. The algorithm as printed is not a
slower variant of the right one — it computes wrong answers.

**Evidence.** This is the strongest-evidenced correction in the project because
it is differential rather than structural. `verification/reference.py`,
implementing the *corrected* algorithm, agrees with this repository's own
`Nucomp_g3_RAM` on 120 of 120 inputs per field. The algorithm **as printed**
disagrees on 7–13% of generic additions, and the cause isolates to that single
character: `<` gives 150/150, `≤` gives 140/150. `selftest.py`'s `reference`
section asserts that the *printed* variant disagrees, so the correction cannot
silently rot — anyone "fixing" the reference back to the published text fails
the suite.

**Honest limit.** The split-model twin (E-T5) has the same guard in the same
shape and is corrected the same way, but there is **no split variant of the
cross-check**, so it rests on the structural argument alone. Stated as such
rather than folded in.

**For the paper.** A published algorithm has a wrong branch condition that makes
one in ten generic genus-3 additions incorrect, found by differential testing
against an independent implementation. The implementation in the repository was
always right; only the printed text was wrong, which is precisely the class of
error that survives review.

## N2 — The addition algorithms are missing their distinctness precondition

**Status:** established, corrected in `Thesis/`. E-T1, E-T2, E-T3.

**Where.** `chapter4.tex:542`, `:646`, `:427`.

**What was there.** `alg:g3nucomp` requires only `deg(u₂) ≤ deg(u₁)`. Its
genus-2 counterpart at `:344` additionally requires the two divisors to differ.

**What it should be.** `[u₁,v₁] ≠ [u₂,v₂]` in the ramified algorithm and the
triple form `[u₁,v₁,n₁] ≠ [u₂,v₂,n₂]` in the split one. A third site, `:427`,
had the clause present but two `$…$` groups run together with no conjunction,
so it rendered as one malformed condition.

**Why it matters.** This is not pedantry about a `Require` line. The absent
precondition is exactly what let `ADD(D, D)` go unchecked through the entire
implementation — see N4, where it is wrong in all fourteen families. A
double-and-add ladder hits it on the first repeated addend.

**For the paper.** The precondition and the implementation defect are one
finding, not two; the paper should present them together, since the interest is
that a missing line of pseudocode propagated into fourteen independently written
formula families and survived every existing test because every existing test
guarded against it.

## N3 — The characteristic-2 normalisation: three errors in one passage

**Status:** established three independent ways, corrected in `Thesis/`. E-T6.
Merged 2026-08-09.

**Where.** `chapter5.tex`, the `char(k) = 2` subsection.

**This started as the opposite claim, which is worth recording.** Reading the
thesis sentence *"results in `h₂ = 1` and `f₄ = f₃ = f₂ = 0`"* against the
shipped characteristic-2 formulas — which keep `f₂` live — suggested the *code*
was carrying a coefficient it could eliminate. It is the other way round. The
code is correct for the domain it declares; the thesis passage is wrong in three
separate ways.

**(a) The transformation's constant term.** As printed, `f₃` is distributed over
one term too many:

```
printed:   f3*(f3 + h1*h2 + f4*h2^2 + f2*h2^2) / h2^3
corrected: (f3*(f3 + h1*h2 + f4*h2^2) + f2*h2^2) / h2^3
```

`f₂h₂²` must stand alone. The printed map is a **valid isomorphism** — it lands
on a genuine curve — but it leaves `f₂ ↦ f₂(f₃+1)/h₂⁶` rather than `0`, so it
does not produce the normal form claimed beside it. Lange (2005), the source the
passage cites, has it right; this is a transcription slip.

Established three ways, deliberately independent: symbolic substitution in
characteristic 2 followed by division by `h₂¹⁰`; Magma over **269 genus-2 curves**
on `GF(4)`/`GF(8)`/`GF(16)`/`GF(32)`, where the printed map left `f₂ ≠ 0` on
**229** of them and the corrected map on **none**, with zero point failures
either way — confirming it really is an isomorphism, just to the wrong form; and
a homogeneity argument needing no algebra at all, that under `x → α²x, y → α⁵y`
every legitimate term of the constant scales as `α⁻⁵` while the stray `f₃f₂/h₂`
scales as `α⁻⁹`, so it cannot belong.

**(b) The scope.** `f₄ = f₃ = f₂ = 0` holds only when `deg h = 2`. This is the
degree-`g` floor rule of Part I at `g = 2`: the shift's `a₀` reaches the
degree-2 coefficient solely through `a₀h₂`, so at `h₂ = 0` the lever is gone.
Exhaustive search over the automorphism group: `deg h = 2` reaches the form
25/25, `deg h = 1` 10/25, `deg h = 0` 3–4/25. Lange states the same restriction
and says plainly that for `h₂ = 0`, `f₂` cannot be assumed zero.

**(c) The justification, which ran two reasons together.** The passage justified
its restriction on `h` by claiming a constant `h` makes the curve model
singular. That is false — `y² + y = x⁵` over `GF(2)` is accepted by Magma as a
genus-2 curve with one point at infinity, and constant non-zero `h` gives a
smooth affine model. Lange's actual reason is different and correct: such curves
are **supersingular**, so the discrete logarithm problem on them is weaker.

But supersingularity excludes `deg h = 0` **only**. It does not justify
excluding `deg h = 1`, which is the Koblitz/subfield family and not
supersingular at all. `deg h = 2` is required for a separate reason — the
transformation divides by `h₂`. The corrected passage gives both reasons
separately.

**A correction to carry, because it invalidates an argument used earlier in this
project.** `2-rank 0 ⟹ supersingular` holds at genus `≤ 2` only. Galbraith
(ASIACRYPT 2001, Thm 9) proves every genus-2 `y² + cy = f` over `F_2ⁿ` is
supersingular; at genus 3 it fails, and `y² + y = x⁷` is a counterexample. Any
genus-3 reasoning of the form "constant `h` is cryptographically dead" is
unsound. Both places this repository states it are genus-2-scoped and correct.

**For the paper.** Three independent errors in one normalisation passage, one of
which silently produces the wrong normal form while remaining a valid
isomorphism — the hardest kind to catch by inspection, since the result *is* a
curve and the map *is* invertible. The homogeneity argument is the cheap detector
and is worth presenting as a technique: scaling weights are a one-line check that
would have caught this without any computation.

---

# Part III — Corrections and completions in the implementation

## N4 — `ADD(D, D)` is silently wrong in all fourteen families

**Status:** established, fixed, gated. PR5, merged.

**What was there.** Every addition dispatcher in the repository — genus 2 and 3,
ramified and split, all three characteristic classes — assumed distinct inputs
and none checked. On equal inputs they return wrong results rather than
failing.

**Why it went unseen.** Every existing Magma tester guards with
`if D1 ne D2 then`. The defect is invisible to a test suite that was written
around it, which is why an independent oracle mattered more than more testing of
the same kind.

**Scale, measured.** `driver.py --curves 3 --pairs 3 --seed 11 --strict`:
**1,300 wrong results in 12,587 operations**, spread across all fourteen
families — genus-2 ramified `ADD00`/`ADD06`; genus-3 ramified `DEG33ADD`,
`Deg1ADD` case 2, `Deg2ADD` 3.1/3.2; genus-2 split `ADD15/19/38/58` in both
bases; roughly twenty genus-3 split branches. **Zero wrong on the documented
domain** — the formulas were never wrong at what they claimed, only at what
callers would reasonably do.

**The fix.** An equal-divisor guard at the top of each dispatcher, routing to
the doubling. The test differs per model and getting the split one wrong deletes
coverage: equal `(u,v)` with **different weights** is a legal addition and must
fall through, so the split guard tests `n` as well. A `(u,v)`-only guard was
measured to swallow **56 branches across 9 files**.

**Result.** 13,008 compared / 13,008 matched / exit 0, and a standing long run
at **695,888 / 695,888** with the equal-divisor region now inside the count
rather than excluded from it.

**For the paper.** A precondition stated in pseudocode (N2) but absent from the
paper's algorithm propagated into fourteen independently derived formula
families, and remained invisible for years because the test suite encoded the
same assumption. The methodological point — that a test suite written by the
same understanding that wrote the code cannot find this class of defect — is the
publishable one.

## N5 — One addition branch returns the wrong number of values

**Status:** established, fixed. E2, PR5.

Branch `ADD05` of all three genus-2 ramified additions returned **six** values
where every sibling returns five — a leftover split-model balancing weight in
ramified code. Live, not latent: three frozen whitebox cases reach it, and it is
the *sole* coverage of that branch in each file.

Worth recording for the methodology: the gate initially **laundered** this. The
comparison truncated the extra value and passed. The fix was to make an arity
mismatch fatal, and — because the three known cases were the only coverage of
their branch and the truncated comparison was in fact correct for them — to pin
those three by identity until the formulas were fixed, so a *new* anomaly still
failed. The pin set is now empty and any anomaly is fatal.

**For the paper.** A verification harness that silently normalises away a
discrepancy is worse than no harness, because it converts a real defect into a
green result. This one did, briefly, and the fix pattern — fail on the class,
pin the known instances by identity, empty the pin set when they are fixed — is
reusable.

## N6 — `h` may be taken monic at genus 3, in every characteristic

**Status:** established, declared in the banners. PR20, merged.

The genus-3 arbitrary-characteristic files now declare `h₃ ∈ {0,1}`, matching
the genus-2 precedent. The justification is step 1 of Part I: `α = h₃` makes `h`
monic and leaves `f` monic, dividing by nothing but `h₃`, so it holds in every
characteristic. Verified over `GF(7)`…`GF(101)` including `GF(25)`, `GF(27)`,
`GF(32)`, `GF(64)`.

**The framing matters and was the author's.** `h₃ ∈ {0,1}` is a **precondition
on the caller**, not a restriction on supported curves. Any curve with
`deg h = 3` converts to one with `h` monic; an implementer normalises once at
setup and every subsequent operation is cheaper. This is what the literature
does explicitly — Fan–Wollinger–Gong state that they *"firstly construct the
isomorphic transformations to achieve as many zero coefficients as possible."*

**Two things this exposed, both honest and both recorded rather than hidden.**
First, the assumption is currently **declared but not exploited**: `//Ignore: h3`
makes the `h₃` products free to *count* (8 of the addition's 12 C, 12 of the
doubling's 16) while the code still computes them. Whether real work can be
removed is PR24's question. Second, **no curve-normalisation utility exists at
either genus** — an implementer told to ensure `h` is monic must derive the
transformation themselves. If the formulas depend on a precondition, the
repository should ship the means to satisfy it.

**A genuine asymmetry with genus 2, worth stating.** The genus-2 formulas
*require* `h₂ ∈ {0,1}`: feeding `h₂ ∉ {0,1}` produces wrong doublings in branch
`DBL4`, in every characteristic tested (2, 3, 5, 7, 11, 13 — 19 mismatches over
`GF(9)` in an 8×8 sweep). The genus-3 formulas were written generically in `h₃`
and stay correct off-domain. So the two genera differ *derivationally*, not just
in their banners, and the obvious explanation — a reduction of `h` modulo a
linear `u` giving `h₂·upp₀²` where the code has `h₂²·upp₀` — was **tested and
refuted**; substituting it does not fix the off-domain failures. The mechanism
is still open and should not be re-guessed.

## N7 — The genus-3 curve generator produced curves outside the declared domain

**Status:** established, fixed. PR25, merged.

`RandomG3Curve` drew `h₃` from the whole field while the formulas declared
`h₃ ∈ {0,1}`, so the Magma testers were exercising curves the banner does not
claim. The file carried a comment admitting it: `//h3 will be made Random(0,1)
later`. Genus 2 has always done this correctly, which is exactly why its
formulas can exploit the assumption and why nothing ever caught the gap — no
generator ever produced a violating curve.

Restructured to the genus-2 shape at the same time: `RandomG3Curve`,
`RandomG3NotChar2Curve`, `RandomG3Char2Curve`, replacing a `char_type`
parameter.

**One place the analogy is deliberately inexact**, recorded in the code rather
than smoothed over. (There were two: `RandomG3NotChar2Curve` also drew `f₆`,
because the genus-3 formulas had not yet applied the depression. N19 applied it,
and the generator stopped drawing the term in the same commit — dropping it any
earlier would have had the generator testing a domain the formulas did not claim,
and dropping it any later would have had the formulas claiming a domain the
generator did not produce. That is now the exact genus-2 analogue.)
`RandomG3Char2Curve` constructs both `f` *and* `h`
directly in the characteristic-2 normal form — `h` monic of degree exactly 3 —
rather than normalising an arbitrary curve into it, so it never samples
`deg h < 3`: that region has its own normal form and is served by the arb
formulas. (`RandomG3Curve`, the *arb* generator, is the one that draws
`h₃ ∈ {0,1}` and so puts half its curves at `deg h < 3` — which is exactly the
domain its banner declares.) The genus-2 characteristic-2 generator still draws
`h₂ ∈ {0,1}` and does sample `deg h < 2`; PR27 restricts it.

**For the paper.** A generator that samples outside a formula's declared domain
makes every passing test meaningless in the region that matters, and a generator
that samples *inside* a domain the formulas do not actually require hides the
fact that the assumption is unused. Both happened here, in opposite directions,
at the two genera.

## N13 — Three assumptions in one family were declared but never exploited

**Status:** established; the genus-2 characteristic-2 case is now closed. PR27,
with `Thesis/ERRATA.md` E-T7.

**The pattern, which is the finding.** A formula file's banner declares which
curves it is valid for, and the operation-count tables are priced against that
declaration. Three times in the ramified family, the declaration was real and
the *code did not use it*:

| where | declared | what the code did |
|---|---|---|
| genus-2 ch2, `f₂` | `f₄ = f₃ = f₂ = 0` beside `tab:ramfcosts` | computed `k0 := f2 + …` |
| genus-2 ch2, `h₂` | `h₂ ∈ {0,1}`, with `//Ignore: h2` pricing its products at zero | computed all 43 of them |
| genus-3 arb, `h₃` | `h₃ ∈ {0,1}`, with `//Ignore: h3` | computes all 187 of them |

Each is individually defensible and none is a *correctness* defect — the
formulas are right for the domain they claim. The pattern is what matters: an
`//Ignore:` directive is a promise that a product is free, and a promise made in
a table is not kept by the code that generates the table.

**What closing the genus-2 case actually bought, measured.** Restricting to
`h₂ = 1` and `f₄ = f₃ = f₂ = 0` moves **one cell** of `tab:ramfcosts` — the
char-2 Degree-2 doubling, 25A → 24A. Of `f₂`'s five arithmetic sites only one is
on a frequent path; the other four are special cases the table does not price.
Measured across 2,514 operations against the pre-restriction formulas on
identical curves:

| | frequent A, before | after |
|---|---|---|
| Degree 1 doubling | 5 | 5 |
| **Degree 2 doubling** | **25** | **24** |
| Degree 1 and 2 addition | 19 | 19 |
| Degree 2 addition | 26 | 26 |

An earlier estimate of three changed cells was wrong, and the difference is
instructive: the arithmetic sites were all located by hand and correctly
counted, but *which branch is frequent* cannot be read off the source. Only a
run tells you.

**And the `h₂` half moves no published number at all** — 43 real multiplications
disappear from the implementation, and every one was already priced at zero. So
the change makes the *already-published* counts true of the code rather than
reducing them.

**Why do it, then.** Two reasons, neither of them speed. Both genera now share
one characteristic-2 exposition — `h` monic of degree exactly `g`, `f` maximally
depressed, exactly the Part I normal form — so the thesis derivation and the
implementation describe the same curve. And the gap between what the tables
claim and what the code does is closed in the code's favour.

**What it costs, knowingly.** `deg h = 1` at genus 2 is the Koblitz/subfield
family (Günther–Lange–Stein, SAC 2000; Lange, FFA 11 (2005) 200–229), which uses
divisor addition directly via τ-NAF. Those curves move to the arbitrary-
characteristic formulas, which serve them correctly at higher cost. A real loss
of specialisation for a real user, recorded as a decision rather than an
oversight — and the dispatchers now refuse them outright rather than returning
quietly wrong answers.

**Evidence.** 2,514 comparisons against the pre-restriction formulas on curves
in the narrowed domain, **zero disagreements** — which is the whole correctness
argument, since every curve the restricted formulas accept is one the old
formulas accepted. Plus 1,428 comparisons against Cantor's algorithm, a
regenerated whitebox corpus at 22 of 22 branches, and both Magma testers green.

**For the paper.** Three times in one formula family, an assumption was declared
in the banner, priced into the published operation counts, and then not used by
the code — so the tables described a better implementation than the one that
shipped. The genus-3 instance is still open. The general lesson is that a
costing convention is a claim about the implementation and needs the same
verification as a formula: nothing in the toolchain checked that an `//Ignore:`d
coefficient was actually exploited.

## N14 — Two counting faults put eighteen published operation counts wrong

**Status:** established, tables corrected. `Thesis/ERRATA.md` E-T8.

**What was wrong.** The operation-count tables were generated by a static token
scan of the Magma source, and it carried two faults:

- *A curve constant between two multiplications was charged twice.* Only the
  tokens immediately flanking each `*` are inspected, so a constant at position
  *j* satisfies the left test of the `*` after it and the right test of the `*`
  before it. `w2*d5*(d2 - v1*t1)` scored 2C where the cost is 1C + 1M.
- *A unary sign was charged as an addition.* Every `+`/`-` token cost 1A, with a
  single hard-coded exemption for one leading `-`. A leading `+` was charged, and
  so was every sign inside an expression — one addition carried three internal
  negations and was over-counted by 3A.

Eighteen published cells across four split-model tables, aggregate **M +13,
C −13, A −14**. No ramified count moves at either genus.

**Why the corrected numbers are trustworthy, which is the methodological point.**
Two counters that **share no code** now agree on all 208 published cells: the
static scan with both faults fixed, and an interpreter that *executes* the
formulas over a finite field. Independent agreement is much stronger evidence
than either counter alone ever had — and stronger than the published cells had,
which rested on one implementation with no second opinion.

The interpreter also settles something the static counter cannot express. Every
published row quotes the *frequent case*, and the static counter infers which
branch that is from source structure. The interpreter measures it — histogram
many random valid divisor pairs, take the modal tuple. On the corrected cells the
modal share is 0.80–0.99, and the two methods pick the same branch on 150/150
distinct cells, so the structural inference is now **validated rather than
assumed**. A prior concern that the static counter merely guessed is retired.

**Two errors on the measuring side, recorded because they show what the
agreement is worth.** The interpreter charged an inversion plus a multiplication
for division by two, where the thesis states plainly that halving counts as an
addition (`chapter6.tex:2333`) — so the *published* convention was right and the
measurement wrong. And its constant detection missed a constant reached through
a unary minus, because `-yn2*W2` parses with the negation bound tighter than the
product; six of the twenty-four cells first flagged were that fault, not a defect
in the tables. Had either gone unnoticed, six correct cells would have been
"corrected" into error.

**For the paper.** Published operation counts in this literature rest on one
hand-written counter per author, with no independent check — and two faults in
ours, each a few lines, moved eighteen numbers. The transferable claim is that an
operation count is a *measurement* and deserves the same treatment as any other:
a second method that shares no code. Here the second method also caught two
errors in the first, in both directions.

## N15 — Operation counts measured by execution rather than by scanning text

**Status:** established, in the repository. `verification/opcount.py`.

**What changed.** Published operation counts in this literature are produced by
scanning formula source as text — one hand-written counter per author, with no
second opinion. This project now counts by **executing** the formulas over a
finite field and histogramming the result. The two methods agree on all 208
published cells (N14), so the text scan is vindicated where it can be checked —
but only one of the two can be checked at all, and it is not the text scan.

**Three things follow that a text scan cannot deliver.**

*Inversions are counted.* The converter has no inversion accounting whatsoever,
so every `1I` in the thesis is hand-supplied. Measured, every published operation
comes out at **exactly one inversion** — which is what chapter 5 asserts in prose
and what nothing had ever verified.

*The frequent case is measured, not inferred.* Every published row quotes the
frequent case. A text scan must deduce which branch that is from the shape of the
source; execution observes how often each is actually taken. On the 150 distinct
published cells the two agree, so the inference is now **validated rather than
assumed** — a claim that could not be made before, in either direction.

*Formulas the scanner cannot read at all are now counted.* All three genus-3
ramified files are unparseable to `latexConverter.py`: they write guards as
`if (X eq 0) then`, a form it has no grammar for, so it yields no genus-3
ramified figure whatsoever. Those nine operations are the family this whole
project exists for.

**And it corrected the figures it replaced, in two ways.**

*One multiplication per operation.* The genus-3 ramified formulas write
inversions as `1/dw1` — 97 times in one file alone — and the previous counter
charged each an inversion **plus a multiplication**, counting a multiply by 1
that nobody performs. Isolated by running with the rule disabled, which
reproduces the old figures exactly, so the difference is attributed rather than
asserted.

*The C column.* PR20 declared `h3` `//Ignore:`, making its products free to
count, and the recorded figures had not caught up: the arb addition falls from
12C to 4C and the doubling from 16C to 4C — matching exactly the 8 and 12 `h3`
products PR20 had recorded.

**What that does to the standing comparison.** The `nch2` genus-3 addition's
frequent case was **62 combined M+S, 3C, 77A** at the time of this entry — 5 better
than Nyukai and 8 better than GKP on M+S, with 28 fewer additions. (N19 later took
it to **56 M+S, 0C, 59A**; the figures here are this entry's own.) And against the thesis's own
split-model Degree-3 rows, ramified is now cheaper on **both** multiplications and
constant multiplications, where the earlier reading had the addition's C as
"identical". The sanity flag is unchanged and still points at additions.

**A correction that ran the other way, and it matters.** The interpreter was
initially *wrong* about division: it charged I+M for every `/`, where this thesis
counts a halving as one addition (`chapter6.tex:2333`). There the **published
convention was right and the measurement wrong** — which is why the adjudication
rule for this project is to presume the published counts correct and hand-count
any divergence, rather than to trust whichever tool is newest.

**For the paper.** An operation count is a measurement, and in this literature it
has never been treated as one: it is derived once, by hand, from formulas the
reader cannot execute. Two independent methods agreeing on 208 cells is a
stronger claim than any single count in the field, and the disagreements were
informative in both directions — two faults in the text scanner, and one in the
executor.

## N16 — A declared domain was masking a transcription slip, not buying anything

**Status:** established. Defect recorded as `ERRATA.md` E11, not yet fixed.

**The question.** Both arbitrary-characteristic families declare `h_g ∈ {0,1}`, and at genus 2 that
restriction is *load-bearing*: lift it and the doubling returns wrong answers. The natural reading is that
genus 2 exploits the assumption to save work, in which case the exploitation sites would be a template to
copy to genus 3, where the same assumption is declared and demonstrably not used.

**The answer is that nothing is being bought.** Genus 2's dependence is one squared symbol.

`arb_ramifiedG2_DBL.mag:189` computes `t1 := s0*(u1 - upp0) - h2^2*upp0 + vh1`, and the following line
multiplies `t1` by `upp0`, so the `h₂` term contributes `h₂²·upp0²`. Deriving the branch instead of reading
it: reduction modulo the monic linear `upp = x + upp0` is evaluation at `x = −upp0`, and `v'' = −(h + v')`
there, so the coefficient of `upp0²` is `h₂ + s₀` — giving `h₂·upp0²`. The exponent is a slip.

On `{0,1}` it cannot be detected, because `h₂² = h₂` exactly there. **Measured, 3,600 doublings per
variant over four fields against an independent Cantor implementation:**

| `t1` reads | on-domain | off-domain |
|---|---|---|
| `- h2^2*upp0` as shipped | 0 wrong | **166 wrong** |
| `- h2*upp0` the derivation | **0 wrong** | **0 wrong** |
| `- h2*upp0^2` | **136 wrong** | 150 wrong |

**And the third row is the methodological point.** That substitution had been tried before and recorded as
refuted, which is what made the whole thing look mysterious. It *is* refuted — but because it breaks the
formulas **on** their declared domain, since the outer multiply already supplies the second `upp0`. A
candidate that changes on-domain behaviour was never a candidate at all, and noticing that is what turned
an open puzzle into a one-symbol answer. The prior work was right about the substitution and wrong about
what its failure implied.

**So there is no template, and genus 3 does not need one.** The genus-3 arbitrary formulas are already
correct with `h₃` unrestricted — **0 wrong in 1,333 operations** off-domain — and no `h₃` power occurs
anywhere in either file. Their `h₃ ∈ {0,1}` declaration is a costing convention and nothing else, which is
what PR20 recorded and this confirms from the opposite direction.

**The prize, measured rather than estimated, is zero in every counted column.** The `h₃` products were
already free to count once PR20 declared `h₃` `//Ignore:` — that is what took the arbitrary addition to 4C
and the doubling to 4C (N15). So exploiting the assumption cannot reduce C further, and the only remaining
yield is real runtime, obtainable by branching on `h₃` and doubling the code paths in both files. That is a
maintenance decision, not an optimisation with a number attached.

**For the paper.** A restriction that is load-bearing is usually assumed to be earning its keep. Here one
was masking a transcription slip, at both a cost and a benefit of exactly zero: `h₂` is `//Ignore:`d and
precomputable, so `h₂` versus `h₂²` changes no operation count, and the one-symbol correction restores full
generality for free. The transferable habit is deriving the branch rather than reading it — the slip is
invisible in the source and obvious in the algebra.

## N17 — The arbitrary genus-3 addition now beats the split-model one in every column

**Status:** three findings implemented and measured. **Superseded by N18**, which
closed the rest of the ledger; this entry is kept as the dated record of the first
pass and its figures are that pass's, not the current ones.

**The anomaly this closes.** Ramified arithmetic has strictly less to do than
split — no balancing, no adjust steps — so it should be cheaper in every column.
It was not: the addition was dearer on additions than the thesis's own
split-model Degree-3 row, which is what N11's vetting set out to explain.

**The explanation was dead and duplicated work, and removing it is enough.**

| | before | after |
|---|---|---|
| `Deg3ADD` typical | 59M 4S 95A 4C | **54M 3S 74A 1C** |
| `Deg3DBL` typical | 55M 5S 114A 4C | **55M 5S 111A 4C** |
| split Degree-3 ADD, for comparison | 65M 3S 87A 12C | — |

So the addition goes from **64 M+S, 12C, 95A** as first recorded to **57 M+S, 1C,
74A**, against the split addition's 68 M+S, 12C, 87A. Better on every axis, and
the anomaly is gone rather than explained away.

Three changes, each its own commit, each measured on its own and Magma-verified on
its own. What follows is the correctness argument for each, because in every case
the argument is a **liveness** argument — which reads exist, and where — and that
is precisely what an operation count cannot see.

**A1 — two quotient coefficients nothing reads.** `arb_ramifiedG3_ADD.mag`'s
generic `Deg3ADD` path computes the exact division `w1 = (f − v1h − v1²)/u1` in
full, all four coefficients. Only `w1_3` and `w1_2` are ever read: they feed the
resultant immediately below, and the remaining reads of `w1_2`/`w1_3` — three of
them further down the same path — are what stop the deletion cascading. `w1_1`
and `w1_0` are read nowhere on any path. `tb := h2*v1_1` existed solely to serve
them and dies with them; `ta` survives, because `w1_2` still needs it.

This is the thesis's own technique applied to the thesis's own code: **efficient
exact division** (`sec:exactdiv`) states that only the highest `d1 − d2 + 1`
coefficients of `f − v(v+h)` are required. Here that count is two, and four were
being formed. The deleted definitions are kept verbatim in a comment, because a
reader who wonders what the quotient's low coefficients *were* should not have to
reconstruct them from the division.

**−5M −1S −19A −3C**, the single largest item in the ledger.

**A2 — two temporaries formed before the only branch that consumes them.**
`ht = t1 + v2` is formed coefficient-wise on entry. `ht2` is read on the generic
path; `ht1` and `ht0` are read **only** inside the `det eq 0` branch, which is
where a non-trivial gcd is handled. Establishing that took an if/end-if depth walk
over the whole function rather than a grep: a grep finds the readers, but only a
scope walk establishes there are no *others*, and the claim being made is about
absence. Moved into the branch that reads them. The special cases pay the same two
additions, just later; the generic path stops paying them at all. **−2A.**

**B1 — `h + v1`, formed twice on one path.** In `Deg3DBL`, `d = (2v1 + h) mod u1`
is built as `h_i + 2*v1_i − …`, and then the typical case's `vn_i` subtracts
`h_i + v1_i` again. Forming `hv_i = h_i + v1_i` once serves both — `d_i` becomes
`hv_i + v1_i − …`, and `vn_i` subtracts `hv_i` directly. What makes this a real
saving rather than a reshuffle is that both sites are on the **same** path: `d` is
computed before any branch, and `vn` sits in the unguarded TYPICAL CASE, so every
typical doubling previously formed the sum twice. **−3A.**

**What re-vetting the ledger cost, and why it was worth it.** The report was
written against a baseline that has since moved twice — PR35 corrected inversions
written `1/x`, and PR20's `//Ignore: h3` made those products free — so its
absolute figures no longer applied, and **every line number in it was stale by
about nineteen**.

The predictions that held were the ones expressed as *deltas in A and S*, which
survived both corrections untouched. The ones that broke were absolute counts and
positions. That is a useful thing to know about how to write such a report: record
what a change removes, not what the total will be.

**A correction to this entry, made 2026-08-11 — the C figures were superseded, not
wrong, and the distinction matters.** An earlier revision of this paragraph said
"one documented delta was simply wrong afterwards: A1's `−4C` is `−3C`". That
misattributes a convention change as a mistake in the report. When the report was
measured, `h3` was a declared `//Constant:`, so `h3*v1_0` genuinely cost 1C and
`−4C` was genuinely right; PR20 moved `h3` to `//Ignore:` and made it free. The
same single event accounts for two further apparent errors found later, in B2 and
in the E-Karatsuba finding — **one cause, three symptoms, zero defects.**
Reproduced in both directions by restoring the old directive, which recovers the
report's original figures exactly.

The durable lesson is not about arithmetic. `RELATED_WORK.md` already carried the
correct explanation — *"the C column fell because PR20 moved `h3` from
`//Constant:` to `//Ignore:` … the table above had not caught up"* — while this
entry was calling the same discrepancy an error two files away. So: **before
filing a discrepancy as a defect in someone's work, check whether the repository
already explains it.** Under this project's own adjudication rule the published
figure is presumed correct until a hand count says otherwise, and that rule
protects prior work from exactly this kind of drive-by attribution.

**For the paper.** The interesting claim is not the improvement but its cause. Two
formula families written by different people for the same curve model differed by
21 additions, and the difference was not algorithmic — it was quotient
coefficients computed past the point the thesis's own exact-division technique
says they are needed, and temporaries formed before the branch that uses them.
Neither is visible in a count; both are visible in a liveness analysis.

---

## N18 — The doubling: twenty-two additions for one multiplication

**Status:** implemented and measured, 2026-08-11. **Every finding in the genus-3
ramified efficiency ledger is now applied**, except one that was applied and
reverted, and two that belong to other files by scope — see
[`EFFICIENCY_ARB_G3.md`](EFFICIENCY_ARB_G3.md).

**The result.** Six further findings landed, each its own commit, each measured and
confirmed under real Magma. A seventh was implemented, measured, and then dropped
before it shipped; see the honesty note at the end of this entry, which is the most
transferable thing here.

| | pre-PR16 | now |
|---|---|---|
| `Deg3ADD` typical | 59M 4S 95A 4C | **53M 3S 71A 1C** |
| `Deg3DBL` typical | 55M 5S 114A 4C | **57M 4S 92A 3C** |

The doubling is the interesting one. **Twenty-two additions came off and one
multiplication went on** — 114A → 92A, with M+S rising 60 → 61 and the wider
M+S+C holding at 64. Under the thesis's own 1M:3A rule that is a decisive win, and
it is worth stating as the trade it is rather than as a free saving: an earlier
draft of this entry called it "removed for nothing", which is true only under the
M+S+C aggregate and false on the M+S figure the project usually quotes.

**The rare branches were finished too, not just the frequent case.** Special-case
inputs are `O(1/q)`, so none of this moves a published figure, but leaving them
would have meant shipping known waste: the `det = 0` doubling path alone dropped
**−8M −1S −8A** across three findings (`m6`/`m4` deferred past the test, the `dw`
block read off the adjugate, B5's fusion swept). The `dw` case is the sharpest —
the block recomputed the third row of the adjugate that the code above it had
already built, and the ledger had costed it at "~4M" and then at −2M −1S −2A,
missing both times that its expensive line *is* the cofactor `m7`.

### The findings, one by one

Each is stated as what it removes, with the argument that makes it safe. In every
case that argument is about **liveness or an algebraic identity**, never about the
count — which is why an operation counter can confirm a saving but never find one.

**C2 — solve by matrix-vector product, not Karatsuba twice.** `+1M −12A`, frequent
case. `Deg3DBL` built only the **first column** of the adjugate — `m1`, `m4`, `m7`
plus the determinant, the thesis's own T13 recipe — and then recovered `s = k·q mod u₁`
with two Karatsuba multiplications. Building all nine entries and solving by
matrix-vector product is cheaper. The nine entries are not nine minors: column 3 of
the Sylvester matrix is `x·`(column 2) reduced mod `u₁`, so six of them are *shifts*
of the bottom row at one multiplication each. `m4` and `m6` are the only two the
determinant does not read, so they are formed below the `det = 0` test and the rare
paths pay one multiplication and no additions. The addition in the same directory
already had this shape; both files now land on `27m 0s 17a` for the same job.

**D33-06 — use the cheap `vn` tail in all three gcd families.** `−1M −3A`, frequent
case. `Deg3ADD` repeats its closing formulas once per gcd family. `CASE #3.1`
precomputes `ty = (u₁₂−q₀)·tx + (un₂−q₀)·s₂⁻¹` and reads it twice — whole in `vn₁`,
times `−q₀` in `vn₀`. The other two copies distribute that quantity and then
re-derive `q₀·ty·tx` and `(un₂−q₀)·q₀·s₂⁻¹`. Hand count: 13M 22A distributed against
12M 19A shared. Transplanted into both expensive copies, keeping the names `tx`/`ty`
those lines already used so no identifier is introduced and `tb` — the name A1
deleted from this path — is not resurrected.

**B2, B3 — reuse `d₂` and `t06` in the doubling's `M20`.** `−4A`, frequent case. `M20`
wrote out `h₂ + 2v₁₂ − h₃u₁₂` inline; that is exactly `d₂`, formed at the head of the
function. And `f₅ + h₃(r₀ − v₁₂)` is `t06 + h₃r₀` by distributivity, `t06` being
`f₅ − h₃v₁₂`. **`t06` has three assignments in the function, so proximity proves
nothing**: the other two sit inside blocks that always return before this line, which
is established by an if/end-if depth walk rather than by reading nearby code. B2 also
survived B1 intact — B1 changed how `d₂` is *spelled*, not what it holds.

**B4, B5, B6 — the `k` block.** `+1M −1S −3A −1C`, frequent case, applied to the
typical path and its byte-identical twin. `k2` re-derived `f₅ − t04` which is `t06` on
the line above; `k0` re-derived `h₂ + 2v₁₂` where `hv₂ + v₁₂` costs one addition
instead of two; `k1` computed `h₂v₁₂` and `v₁₂²` separately where they combine into
`v₁₂·hv₂`. That last trades a squaring and a constant-multiply for a general
multiplication — neutral on M+S, one addition off.

**The fusion family — the same combination wherever the sum is in hand.** Off the
frequent path. `−h₂v₁₂ − v₁₂²` is `−v₁₂(h₂ + v₁₂)`, and `h₂ + v₁₂` is already live as
`t1_2` in the addition and `hv₂` in the doubling. Applied at four sites. One of them
also carried a Karatsuba in the losing direction: `−(h₃+h₂)(v₁₂+v₁₁) + ta + tb` is
exactly `−h₃v₁₁ − h₂v₁₂`, since `ta = h₃v₁₂` and `tb = h₂v₁₁` two lines above, so the
`+ta+tb` cancels the diagonal products and leaves the cross terms. Both `ta` and `tb`
remain read elsewhere, so no dead store appears. Case #2.4 already held the unfused
direct form, so the file had been contradicting itself.

**D33-07 — form `m6` and `m4` below the test that makes them useless.** `0` on the
frequent case, `−2M −2A` on each of twelve `det = 0` return sites. Unlike A1 these
values are *live* on the generic path, so deleting them would be a correctness bug;
this is A2's pattern with the direction reversed — the reading side is the generic
path, so the move is downward past `end if;`. The two `// convenient zero` comments
were also false as claims about the values: both entries are ordinary adjugate
entries feeding `sp1`, nonzero in 19,997 of 20,000 random draws. What is true is
nearly the opposite — a term that is *identically zero* has been folded into each so
that `tf`, `m8` and `m7` can stand in for products the plain cofactor needs.

**ARBDBL-06 — read `dw` off the adjugate instead of recomputing it.** `−6M −1S −4A`
on the `det = 0` path. The block recomputed `dw = d mod u₁` from scratch when the
Sylvester block directly above already held it: `dw` is the third row of the adjugate
up to sign, so `dw₂ = −t8`, `dw₁ = m7`, `dw₀ = −m8` as polynomial identities in
`d₂,d₁,d₀,u₁₂,u₁₁,u₁₀` rather than as coincidences of the branch. `dw₂` is not formed
at all, its only two readers having been the other two lines, and `t02 = d₂²` dies
with it. **The ledger had costed this at "~4M" and then at −2M −1S −2A; both missed
that `dw₁` is exactly the cofactor `m7`** — the expensive line at 3M 2A — so both
priced only the cheap half.

**B5's sweep, and C3.** Nine sites where `h_i + 2v₁ᵢ` costs two additions and the live
temporary makes it one; `−4A` on the doubling's `det = 0` path and `−1A` each on three
more branches. And the two questions the original authors left in the files —
`use my determinant calculation??` and `SWAPPING st WITH w1 ALSO WORKS????` — become
statements, the first answered by C2 and the second in the affirmative at no cost.

**The direction is the opposite of what was assumed, and that is the publishable
part.** The project's own merge plan recorded a suspicion that the *addition* was
an unfinished port and should be brought to the T13 shape. Measured, that costs
**−1M for +12A** — the losing side of the thesis's 1M:3A rule — while the reverse,
bringing the *doubling* to the adjugate shape, is **+1M for −12A**. Same rule, same
twelve additions, opposite signs. The full adjugate wins in both files. A structural
suspicion of the form "these two differ, so one is unfinished" gets the asymmetry
right and the direction backwards half the time, and only measurement distinguishes
the halves.

*Three-way duplication is not free.* D33-06 above is usually the kind of thing filed
as a maintenance problem — three copies of one computation. Here it was an
**efficiency** problem: the copies had diverged, so two of them were paying for
something the third had already avoided, and the cheap version was sitting in the
same function all along. Worth diffing duplicated formula code, not merely
deduplicating it.

*One temporary enables a family of savings.* N17's `h + v1` — introduced purely to
avoid forming a sum twice — turned out to unlock the same fusion at four further
sites, because wherever `h₂v₁₂ + v₁₂²` appears it is `v₁₂(h₂ + v₁₂)` and the sum is
now already in hand. Before that temporary existed the fusion bought a multiplication
and saved nothing. **A cheap change can convert an unprofitable technique into a
profitable one, and a findings report written before it cannot see that.**

**A counter blind spot, and the reverted finding it produced.** Two independent
measurements said a Karatsuba removal saved a multiplication. It does not: the
factor is `(h₃ + h₂)`, a **precomputable sum of two curve coefficients**, and under
`h₃ ∈ {0,1}` literally `h₂` or `h₂+1`. The counter charges it a full M because its
constant-detection resolves a name only through a unary minus, never through a
composite expression. So N17's A1 is honestly **−4M −4C** rather than −5M −3C, at
the same total of eight.

**Then the same gap produced a change that had to be abandoned, which is the part
worth writing up.** (Recorded as ERRATA E13, with the scope measured at six live
sites.) Horner-nesting the degree-1 doubling's `k0` measured a clean
−1S. Honestly it is **+3M −3C −1S**: the original multiplies by `4f₄`, `5f₅` and
`6f₆` — all fixed per curve, hence C — and Horner replaces them with three genuine
`u₁₀·(variable)` products. The counter reported no change in M because it charges
both shapes the same. The measurement was reproduced, the algebra was verified, the
formulas were correct, and the change was still the wrong direction under the
thesis's own cost model. It never shipped — there is no revert to find in the
history, because it was removed from the branch before that branch was pushed.

**The lesson is that a verified measurement is not a verified improvement.** Both
the finding and its refutation came from the same instrument, and the instrument
could not distinguish a multiplication by a curve constant from a general one in the
one syntactic shape that mattered. What caught it was reading the expression and
asking which factors are fixed once per curve — an argument no counter makes.
Anyone quoting operation counts from a tool should know which classifications it
cannot make; ours cannot fold constant subexpressions, and that is now recorded
beside the counts rather than in its source only.

**For the paper.** Three things generalise past this curve model. Structural
asymmetry between two implementations of the same operation identifies *where* to
look and not *which way to go*, and the cost of guessing is a rule violation in the
wrong direction. Duplicated code in explicit formulas should be diffed rather than
merely deduplicated, because divergent copies mean one of them is paying for
nothing. And a shared temporary changes the economics of every technique downstream
of it, so an efficiency ledger is not a set of independent line items — it has to be
re-derived as items land, which is why every delta here was re-measured against the
tree as it actually stood rather than trusted from the report.

---

## N19 — The specialised addition had fallen behind the general one

**Status:** implemented and measured, 2026-08-12, and the invariant it proposes is now
enforced in `verification/selftest.py`. Full detail in
[`EFFICIENCY_NCH2_G3.md`](EFFICIENCY_NCH2_G3.md).

**The observation, which is a process result before it is a mathematical one.** The
odd-characteristic genus-3 addition is the arbitrary-characteristic addition
specialised to `h = 0`. Ten efficiency findings landed in the general file; none
landed in the specialised one. So for a while the repository shipped a *general*
addition cheaper than its own *specialisation* — 56 M+S, 1C, 71A against
62 M+S, 3C, 77A — which cannot be right on any correct accounting, since the
specialisation does strictly less work.

**Nobody had looked, because there was no reason to.** Each finding was verified
against the file it was found in. What no per-file gate can see is that a
specialisation and its parent have drifted apart, and this project has no check for
that relationship at all. **A specialisation hierarchy needs an invariant, not just
per-file tests:** the child may never cost more than the parent in any column. That
is mechanically checkable from `opcount.py` and is not checked today.

**What the drift was made of.** Measured composite, four findings:

| step | `Deg3ADD` typical |
|---|---|
| before | 58M 4S 77A 3C |
| after | **53M 3S 59A 0C** |

Three are the direct twins of findings already landed in the parent — dead quotient
coefficients, a `vn` tail written three inequivalent times, and two temporaries
formed before the only branch that reads them. The fourth is the `f6 = 0`
depression, which had never been applied.

**The depression is the interesting one, and its value is not arithmetic.** Every
published odd-characteristic genus-3 source — Kuroki, Gonda, Guyot, Nyukai,
Fan–Wollinger–Gong — assumes `f₆ = 0`. Keeping it live meant this repository was
implementing a curve form **nobody in the literature uses**, so its counts were not
comparable in the direction that flatters nobody. After the depression the
comparison is apples-to-apples for the first time: **56 M+S and 59A against
Nyukai's 67 and 105.**

And the audit's recorded cost for it was wrong in a way worth recording. It said
`8M + 22A`. All eight products are `f₆·u₁ᵢ` — a coefficient the file itself declares
constant times a variable — so they are C, honestly, being multiplications by a
quantity fixed once per curve. **The depression removes zero multiplications.** It is
`22A + 8C` static, `4A + 3C` on the frequent case. A finding whose headline is
"comparability" and not "operations saved" is harder to sell and is what the evidence
supports.

**The blast radius is the work, and it does not live in the formula file.** Three
things must move in the same commit, each established by making the gate fail:

- the curve generator still draws an `x⁶` term — leaving it produced **25,477 Magma
  error lines** over 60 trials;
- the dispatcher still extracts `Coeff(f,6)`, and the test harness derives the tested
  domain *by contrast* with the general file's dispatcher, so while that line is
  there the harness keeps generating `f₆ ≠ 0` curves and reports **110 mismatches**;
- two of the thirty frozen corpus records sit on `f₆ = 1` curves.

**A depression is therefore not a formula edit.** It is a change of domain, and every
artefact that generates or freezes an input to those formulas encodes the old domain
somewhere. The formula file is the smallest part of it.

**Four assumptions were tested and refuted**, so the budget is closed: the leftover
α-scaling buys nothing once `h = 0`, `f₅ = 0` is not reachable, an alternative
allocation of the normalisation budget loses, and there is no halving site to exploit
in `char ≠ 2`. No published source takes a third assumption either. `h = 0` and
`f₆ = 0` is the whole of it — which is itself worth stating, since it closes a
question rather than leaving it open.

**And a thesis erratum falls out with a proof.** `chapter5.tex` claimed the
odd-characteristic counts "make no assumption about `f₄`". The genus-2 file contains
**zero** occurrences of `f₄`, its banner omits the term, and its constant directive
omits it — so the counts do assume it, and the sentence contradicts the table two
paragraphs later. The neighbouring sentence saying the same of `f₅` is **true**,
because the genus-2 *split* formulas really do keep `f₅` live. Two near-identical
sentences, one wrong; see [`Thesis/ERRATA.md`](Thesis/ERRATA.md) E-T9.

**For the paper.** Two transferable points. First, the one above: **a specialisation
must be re-derived when its parent improves, and the invariant that child ≤ parent in
every column is worth enforcing mechanically** — the drift here was invisible to
every per-file gate the project has, and those gates are thorough. That invariant is
now a `selftest.py` section, shown to fire: against the pre-implementation file it
reports all three columns exceeded. **Two findings existed only because the earlier
ones landed** — eleven of the seventeen disguised squarings become available only once
`f₆ = 0` makes the leading quotient coefficient a bare negation — which is the same
non-independence the doubling ledger showed, and the second reason a ledger has to be
re-derived rather than replayed. Second, that a
normal-form assumption is a claim about the *domain*, not about the formulas: the
depression's cost was three artefacts outside the formula file and zero
multiplications inside it, and a report that prices only the arithmetic prices the
easy part.

---

## N20 — The polynomial reference blocks are executable, and that turned them into a test

**Status:** established, 2026-08-13. PR36, in progress.

Every case function in the genus-2 and genus-3 ramified formula files opens with a
commented block holding the *polynomial-level* formulation the explicit coefficient
arithmetic implements — `d := up mod u`, `k := (f - v*(v+h)) div u`, and so on. Their
stated purpose is that deleting the explicit formulas and uncommenting the block leaves
a working function. Until now that was an aspiration: nothing ever ran them.

**They can now be extracted mechanically and checked, and doing so is worth more than
reading them.** A parser lifts each block out of the source verbatim, wraps it in the
host function's own signature, and the result is compared against the explicit formulas
on genuinely on-curve divisor pairs — pairs built from affine points, with deliberate
overlap so the degenerate branches are reached rather than hoped for. Across the two
genus-3 ramified addition files that is **12 functions, 7,235 + 5,365 pairs over six
fields, every one of the seven returned coefficients compared, zero disagreements and
zero runtime errors.** The blocks are now a second oracle rather than a comment.

Three things this found that reading could not:

- **`ExactQuotient` and `div` are not interchangeable here, and the difference is
  invisible until the block is executed.** Each block builds `f` truncated at the lowest
  coefficient its own signature carries, because the omitted low coefficients have degree
  below the divisor's and so cannot reach the quotient — measured, `div` returns the true
  exact quotient on 3,000 of 3,000 degree-2 divisors. But the *numerator* is then not
  divisible: `up | f - vp(vp+h)` holds for the full `f` and fails for the truncated one on
  **0 of 3,000**. So `ExactQuotient` raises on every evaluation of that line, and `div`
  is not a loose spelling of it but the correct operator. Both now carry an
  `//Exact quotient` comment saying which it is.
- **The genus-2 blocks are not runnable at all**, for a different reason: they reference
  `f0`, which is not a parameter of the functions that contain them. Magma resolves free
  identifiers at *definition* time, so uncommenting one does not merely fail at that line
  — it refuses to define the function and aborts the load. The genus-3 blocks were
  written extractable; the genus-2 ones were not, and the asymmetry had gone unnoticed
  because neither had been tried.
- **Two commented lines in the degree-2-plus-degree-3 addition were wrong, in both
  files, and one had a correct twin 135 lines away.** `//t22:= -v2;` and `//t22:= vp2;`
  annotate the same quantity in sibling branches and disagree; the first is right. The
  companion `//vt2:=` line had its operands reversed. The value is load-bearing even
  though the line is commented out: the Karatsuba immediately below expands
  `(at1 + at2)*(vt1 + vt2)` with `vt2` folded in as `-vp2`, and the `mod up` reduction
  two branches later folds the same coefficient in as `up*vp2`. A commented-out
  coefficient can still document a live one.

**For the paper.** The transferable point is that **a reference formulation shipped as a
comment is untested documentation, and the cost of testing it is a parser, not a
rewrite.** This project already treats the interpreter as the counter of record (N12)
because interpreting the real source removes transcription drift; the same argument
applies one level up, to the algorithm statement the formulas claim to implement. Two of
the three findings above are exactly transcription drift between a formulation and its
implementation, which is the class of defect a human reading both is worst at.

**The blocks were then rewritten to say what the explicit code actually does.** They had
been generic: one `XGCD(u,up)` call, a second `XGCD` on the gcd, and a three-way tail on
`Degree(u) + Degree(up)`. That is a correct algorithm but it is not the algorithm below it,
so no statement of it could serve as the comment above any particular explicit group. All
four are now unfolded in the resultant form the house exemplars use — `Deg2ADD`, in both
`arb_splitG3_ADD` and genus-2 ramified — with every gcd case explicit and its own
return. `Deg3ADD` goes from 51 lines to 178 and from 3 returns to 12.

**How many leaves is settled by the parent, not by taste.** Each block's header names
`Nucomp_g3_RAM` as what it specialises, and that function dispatches once on
`Degree(s) lt 2`; thesis `alg:g3nucomp` writes the same single `\ElsIf{\deg(s) < 2}`. The
author's own comment there says why — *"stay within these cases and go forward with the
following output cases within each GCD case"* — the gcd axis and the output axis are
orthogonal, and the explicit code's fifteen leaves are the pruned cross product of four
gcd cases against three output cases. The block mirrors the algorithm's granularity, so
its twelve leaves are right and the explicit code's extra `deg(s) = 0` versus `= 1` splits
are degree bookkeeping. The same source settles a second point: it carries *"k should be
pushed forward depending on case, should only compute k right before needed"*, which the
old block violated by computing `k` unconditionally at the top. The new one computes it
per branch, and never on the two paths that return without it.

**One construct is load-bearing and looks like a hack.** Three lines read
`dx := (Degree(dw2) eq 2) select (up mod dw2) else dw2;`. A linear `dw2` always divides
`up`, so a plain remainder vanishes there and routes a degree-1 second gcd into the
composition-only branch. Measured: the plain-`mod` spelling is **wrong on 15 of 1,890**
degenerate-shape pairs and **never raises** — it silently returns a degree-1 or degree-2
`upp` where the answer has degree 3. The alternative is an extra `if Degree(...) eq 2`
guard level the explicit code does not have.

**A defect the rewrite surfaced.** The `CASES` enumeration says case 4.2 is
`DA = P3-P1-P2 (return 2P3)`, and the `ADD_DEBUG` label inside that case said
`DA = P1-P2-P3`. The arithmetic decides it: `(P1+P2+P3) + (P3-P1-P2) = 2P3` matches the
stated return, where `P1-P2-P3` would give `2P1`. Wrong in both addition files, at the
label and at an in-case comment, with two frozen corpus records carrying the wrong string.
Corrected in all six places.

Landing alongside it, and behaviour-preserving: the genus-3 ramified case functions now
take **the smaller-degree divisor first, unprimed**, matching genus 2, so `u, v` is
always the lower-degree operand, `up, vp` the higher, and `upp, vpp` the result. Genus 3
had `(u, v)` first but bound to the *larger* divisor, so a reader who knew genus 2 read
every mixed-degree signature backwards. Verified as a pure refactor by comparing both
addition dispatchers against their pre-change selves on 2,995 operations spanning all
six degree pairs — zero mismatches — with every operation count identical per branch.

---

## N21 — Two weights larger than the mathematics requires, and a cofactor that is a constant

**Status:** implemented and measured, 2026-08-14. Genus-3 ramified `Deg2ADD`, both
the arbitrary and the odd-characteristic file.

The degree-2-plus-degree-2 addition's degenerate branches carried three separate
pieces of avoidable work. None is visible in the published frequent-case row, and
none was found by reading the arithmetic — each came from asking what a *weight*
was for.

**A cube weight where linear suffices — and it was avoidable in both files, for
different reasons.** The branch test needs `dw3 = (h+v+vp) mod S1` with `S1` linear,
i.e. the cubic `h+v+vp` evaluated at `m4/m3`; clearing denominators for a cubic
costs `m3^3`. But `S1` divides `up`, so reduction is transitive:

    (h+v+vp) mod S1  =  ((h+v+vp) mod up) mod S1

and `(h+v+vp) mod up` is **linear**, so the weight is `m3`. The arbitrary file was
evaluating the cubic directly; its sibling branch one level up already performed
exactly the `mod up` reduction, so the cheaper route was present in the same
function and unused. Hoisting it serves both branches: **−2S −1C +2A** on the two
degree-1-gcd cases. The odd-characteristic file had no cubic at all — at `h = 0`
the quantity is linear from the start — and yet carried a `d1^2` factor copied from
the arbitrary shape, which then forced a `d1^4` correction downstream to undo
itself: **−1M −1S**. The same finding twice, reached from opposite directions.

**The Bézout cofactor `a2` is a constant, not a quadratic.** The reference block
computes it as `ExactQuotient((1 - b2*(h+v+vp)) mod up, S1)` — reduced mod `up`
*first*, so the numerator is linear and the quotient by a linear `S1` has degree 0.
The explicit code instead divided the unreduced cubic by the monic gcd and got a
degree-2 `at`, then paid for a polynomial-by-polynomial product. Both are valid
representatives, because `s` is taken mod `up`; they differ by a multiple of
`up/S1`, which is *not* a multiple of `up`, so the interchange is legitimate here
and would not be if the modulus changed.

**But being a constant is a precondition, not the win.** `a2` never appears alone —
only as `a2*a1`, and with `dw = m3*dw3` and `a1 = -1/m3` that product is `gt1/dw`:
one multiplication of a subexpression the branch test already formed. That kills
`a1`, the monic `dm`, both `at` coefficients and the entire `st` chain, and shrinks
the inversion from `1/(m3*dw)` to `1/dw`, which also drops a squaring. Measured on
constructed inputs over nine fields:

| | before | after |
|---|---|---|
| arb, gcd degree 1, `dw != 0` | 44M 2S 78A 2C 1I | **38M 1S 68A 2C 1I** |
| nch2, same branch | 38M 5S 55A 0C 1I | **34M 3S 51A 0C 1I** |

**A redundant guard, with a one-line proof.** The `u = up` branch tested
`IsZero(dw20) and IsZero(dw21)`. Subtracting the two curve conditions gives
`u | (vp-v)(vp+v+h)`; if `dw21 = 0` then `vp+v+h` is the constant `dw20` mod `u`, so
`u | (vp-v)*dw20`, and since `deg(vp-v) < deg u` with `vp != v` that forces
`dw20 = 0`. No squarefree assumption needed. So `dw21 = 0` alone decides it, which
is what the split model has always tested, and `dw20` moves below the guard:
**−1M −3A** on the branch that returns the neutral element.

**For the paper.** The transferable point is that **a weight is a claim about a
degree, and it should be re-derived whenever the degree changes** — by a
specialisation (`h = 0` collapsing a cubic to a linear form) or by an available
reduction (`S1 | up` making the cubic unnecessary). Copying a parent's weighted
shape into a child carries an assumption the child does not have; that is the same
class of defect as N19's cost drift, seen in the arithmetic rather than the totals.
Second point: the frequent case did not move in either file, so none of this
appears in a published table. Rare-branch savings survive only in the commit
record, which is an argument for measuring per branch rather than reporting the
modal cost alone.

## N22 — A convention adopted everywhere except one function

**Status:** implemented and measured, 2026-08-15. Genus-3 ramified `Deg13ADD`,
both the arbitrary and the odd-characteristic file. The frequent case moves in
both, so this one *does* reach a published row.

Neither finding is a new technique. Both are places where `Deg13ADD` alone fails
to do what the rest of the repository already does — which is worth recording
precisely because that is the class of defect an efficiency review reading a
function in isolation cannot see.

**The closing reduction is a difference of two monic cubics.** `vpp` is
`(-up*s - vp - h) mod upp`, and `up` and `upp` are both monic of degree 3, so
`up ≡ up - upp (mod upp)` — a subtraction, not a multiplication. Written out with
`t = s0 + h3`, the identity is

    t*upp_i - s0*up_i  =  s0*(upp_i - up_i) + h3*upp_i

and `h3*X` is free under the file's `//Ignore: h3`, so each coefficient keeps one
general multiplication where it had two. This is pure distributivity: it holds in
any commutative ring, uses no branch invariant, and is therefore valid on every
path of the function at once.

**Every other `vpp` site in all three genus-3 ramified files already writes the
folded form** — `arb_ramifiedG3_DBL.mag:332-333`, `:612-613`, `:673`, and
`arb_ramifiedG3_ADD.mag` at `Deg2ADD:418`, `Deg23ADD:862`, `Deg3ADD:897-899`,
`:1059-1061`, `:1138-1140`. The only unfolded lines anywhere were the four in the
arb `Deg13ADD` and the four in the nch2 one.

| | before | after |
|---|---|---|
| arb `Deg13ADD` frequent | 20M 1S 37A 1I | **18M 1S 39A 1I** |
| arb `Deg13ADD` `d = 0`, `dw ≠ 0` | 26M 1S 48A 1I | **24M 1S 50A 1I** |
| nch2 `Deg13ADD` frequent | 18M 3S 28A 1I | **16M 3S 28A 1I** |
| nch2 `Deg13ADD` `d = 0`, `dw ≠ 0` | 23M 3S 38A 1I | **21M 3S 38A 1I** |

**The nch2 half is the clean result, and it is free.** With `h = 0` there is no
`h3` term to add back, so the fold is `−2M` at **zero** additions — the file was
literally writing `s0*upp2 - s0*up2`, which is `s0*(upp2 - up2)` spelled as two
multiplications.

**The arb half is `−2M +2A`, and its honest scope must be stated.** The saving is
real on the declared domain `h3 ∈ {0,1}`, where `h3*upp_i` is a zero or a copy;
charged as a general multiplication it would be roughly neutral. That is the
costing convention PR20 adopted and the file already applies at fourteen other
sites, so this is consistency rather than a fresh bet — but it does widen the
declared-versus-computed gap PR24 measured, and a reader is owed that.

**Second finding: a Horner tail evaluated twice.** `d := up0 - u0*(up1 - u0*t1)`
is `up(-u0)` by Horner, and its inner value `up1 - u0*t1` was recomputed verbatim
as `upp0` on the `dw = 0` return. It is not a coincidence that they agree:
`d = 0` means `up = u*(x² + t1*x + t0)`, so `t1` and `t0` **are** the coefficients
of `ExactQuotient(up, u)`, which is exactly what that branch returns. Naming the
intermediate costs nothing on any path — `d` still costs 2M 3A — and the return
then reads it free: **7M 13A → 6M 12A**. The nch2 file already named it
(`temp3`); only arb did not.

**What was checked and found already optimal**, since a review that reports only
what it changed is not evidence of much. Efficient exact division is applied
tightly: only `k3…k0` are formed and `k0` is consumed solely by `s0`'s Horner
evaluation, so no quotient coefficient is dead — the ODDADD-19 pattern does not
recur here. Karatsuba is used at the one place it pays (`k1`, where `ta` and `tb`
are needed anyway) and genuinely does not pay in `k0`: both regroupings of
`vp1*vh2 + vp2*vh1` and of `up0*k3 + up2*k1` need a product that is not otherwise
computed. Also refuted: the `M1`/`M2` route quoted in the reference block (9M+1S
against the current 5M+1S); the l'Hôpital shortcut `k(-u0) = N'(-u0)/up'(-u0)`,
which is a true identity here since `N(-u0) = 0`, but needs a second inversion;
recomputing `dw` as `2*v0 + h(-u0)`, true on this branch but circular, since
`vp(-u0) = v0` is only known after the test it would replace; Takahashi
normalisation reordering, inapplicable because `upp` is monic for free at genus 3;
Karatsuba modular reduction, inapplicable with a single multiplier; folding `vpp1`
the same way, exactly cost-neutral because `s0*up1` is shared with `upp0`; folding
`k0` into the Horner, `−1M +1S` and so neutral on M+S; and fusing `upp2`'s
`h3*s0 + s0^2` into `s0*(s0 + h3)`, neutral and dominated once the `vpp` fold
removes that temporary.

**Evidence.** A rig that constructs inputs forcing each of the three paths —
random pairs for the typical case, a shared point for `d = 0`, its opposite for
`dw = 0` — checked against `reference.py` over GF(11), GF(13), GF(17), GF(25),
GF(27): **1,368–2,044 cases per path per variant, zero mismatches**, with the
operation counts taken from the repository's own counter under the file's
directives. Then the standing gates: `driver --strict` 12,972/12,972,
`whitebox` 1,812/1,812, `selftest` 14 sections including the child-never-dearer
invariant, the reference blocks agreeing with the explicit code on 1,491
`Deg13ADD` pairs under real Magma, and both random testers clean at 111s and
216s — runtimes worth quoting, because E12 records that a sub-second run prints
the same green summary having executed nothing.

**For the paper:** the closing reduction of a divisor addition is a difference of
two monic polynomials of the same degree, so the `s·up` products it appears to
need are additions. Stated once, it applies to every branch of every addition and
doubling in the family — and the one function that did not use it was measurably
dearer for it, in the frequent case, in both characteristic families.

## N23 — When to build the inverse, and when to build the adjugate

**Status:** implemented and measured, 2026-08-16. Genus-3 ramified `Deg23ADD`, arbitrary
characteristic. Degenerate branches only, so no published row moves.

Both models must solve the same sub-problem in the degenerate cases of an addition: given
`dw2 = (h+v+vp) mod u` and the reduced quotient `kp`, find `s` with `dw2·s ≡ kp (mod u)`. There are
two ways, and this repository had been using **both, in different files, without the choice ever
being stated**.

- **Build the inverse.** Form `bt`, a weighted `dw2^{-1} mod u`, then multiply `bt·kp mod u` and
  divide by the weight. This is what the genus-3 ramified addition does.
- **Build the adjugate.** Write multiplication by `dw2` modulo `u` as a matrix in the basis
  `{1,x}`, take its adjugate; the determinant *is* `Resultant(u,dw2)`, and the same entries then
  give `s` by one matrix-vector product. This is what the genus-3 split addition does, everywhere,
  without exception.

**Measured across every shape in both models**, by classifying each function's solve: the split
builds an inverse object **zero** times in the addition and **zero** times in the doubling. The
ramified builds one 5 times in `Deg23ADD` and 11 times in `Deg3ADD`. Both doublings, `Deg2ADD`,
and all three typical paths already agree — they use the adjugate.

**The rule that decides it, which neither file states.** The adjugate always costs
`4M 2A` to build and `4M 2A` to apply. The inverse route's cost depends entirely on whether `bt`'s
coefficients fall out of the `dx` computation for free:

| site | `bt` costs | verdict |
|---|---|---|
| `Deg23ADD` #3.2/#3.1 | `bt0 = dw20 - u1*dw21` — **1M 1A, and it duplicates a subexpression already inside `dx0`** | adjugate wins |
| `Deg3ADD` #4.1 | `bt0 = -temp6`, and `temp6` was already formed for `dx1`/`dx0` — **2A, two negations** | inverse wins; leave it |

So the answer is not "always use the adjugate". It is **use the adjugate exactly when the inverse's
coefficients are not already lying around**, and `Deg23ADD` #3.x is the only site in either ramified
file where they are not.

**What landed.** `dx0`'s standalone weighted resultant and the separate `bt` + Karatsuba solve are
replaced by

    n3:= dw20 - u1*dw21;
    n4:= u0*dw21;
    dx0:= dw20*n3 + dw21*n4;        //Resultant(u,dw2) = the 2x2 determinant
    ...
    sp1:= dw20*kp1 - dw21*kp0;
    sp0:= n3*kp0 + n4*kp1;

`sp` is the same object under both routes — each equals `dx0·s` — so `#3.2`'s `sp0/dx0` and `#3.1`'s
weight bookkeeping needed no change at all, which is the check that the substitution is faithful
rather than merely agreeing numerically.

| branch | before | after |
|---|---|---|
| #3.1, `deg(s) = 1` | 51M 4S 87A 1I | **50M 3S 82A 1I** |
| #3.2, `deg(s) = 0` | 37M 2S 67A 1I | **36M 1S 62A 1I** |
| #3.3 | 29M 1S 47A 1I | 30M 0S 47A 1I — M+S and A both unchanged |
| #3.4, typical | — | unchanged |

`#3.3` returns before the solve, so it pays the determinant's extra multiplication without
collecting the saving; at 30 M+S and identical A it is a wash, not a loss.

**Evidence.** A rig that constructs inputs forcing each of the four `d = 0` sub-paths — `u | up`
with the second divisor carrying both points, one opposite point, or both opposite —
**5,512 cases over GF(11), GF(13), GF(17), GF(25) against `reference.py`, zero mismatches**. Then
the standing gates: `driver --strict` 1,818/1,818 on the family, `whitebox` 1,812/1,812, the
reference blocks agreeing with the explicit code on 1,406 `Deg23ADD` pairs under real Magma, and the
random tester clean at 113s.

**Honest limit:** the `Deg3ADD` #4.1 verdict is derived from operation counting, not measured. No
variant was built, because the direction is unambiguous — the adjugate would first have to reduce
`dw2` modulo the shrunk quadratic `up` before it could start, which is 2M 2A the inverse route never
pays.

**For the paper:** an explicit-formula derivation should state which of the two inverse routes it is
using and why, because the choice is not uniform even within one implementation — and the deciding
question is not the degree of the modulus but whether the resultant computation has already produced
the coefficients the inverse needs.

### N23a — the same change in the specialisation, and a rare-branch cost charged to the frequent path

The odd-characteristic `Deg23ADD` carried the identical `bt` construction and took the identical
port, at `h = 0`: #3.1 `50M 4S 71A → 49M 4S 68A`, #3.2 `36M 2S 52A → 35M 2S 49A`.

**But porting it did not clear the specialisation invariant, and what did is worth recording.** With
arb's `Deg23ADD` improved to 39 M+S, `selftest`'s guard fired —
`ramified/g3/nch2 23ADD: child M+S 40 > parent 39` — and the cause was nowhere near the branch being
ported. It was the **prologue**:

| | forms the x-coefficient of `up mod u` as |
|---|---|
| arb | `u1*t0` with `t0 = up2 - u1` — **1M** |
| nch2 | `temp3 = u1^2 - u0` then `up1 - u1*up2 + temp3` — **1M 1S** |

nch2 split one product into a multiplication *plus* a squaring so it could keep `temp3` for two
degenerate branches that reuse it. Those branches are reached rarely; the squaring was paid on
**every** call. Writing it arb's way as `d1 := up1 + u1*temp2 - u0` and letting the two consumers
form `-u0 + u1*(u1 - k3)` locally — which is what arb already does — removes it:
**35M 5S 46A → 35M 4S 45A**, i.e. 40 M+S → 39, and the invariant passes with the child now equal on
M+S and ten additions cheaper.

**The lesson is the one the invariant exists to catch, in a new form.** PR15 found a specialisation
that had drifted dearer because improvements landed only in the parent. This is subtler: nch2 was
*internally* consistent and correct, and the extra squaring looked like a sensible common
subexpression — it is only visibly wrong when measured against the parent, on the frequent path,
where the cached value is never read. **A temporary hoisted for a rare branch is a cost transfer
from the rare branch to every call**, and nothing but a per-shape comparison against the parent will
surface it.

**Two more, found by the same comparison and specific to `h = 0`.** Where arb writes
`- vp1*vh2 - vp2*vh1` — two genuinely different products — the specialisation collapses both to
`vp1*vp2` and was computing it **twice**, and `vp2*vh2` became `vp2*vp2`, a squaring written as a
product. Both appear in each of the function's two `k` blocks. The file's own `Deg13ADD` already had
them right (`t5:= vp1*vp2` then `- t5 - t5`, and `vp2^2`), so this was an internal inconsistency, not
a missing technique. Forming the product once and spelling the squaring as one gives **−2M +1S** on
each of #3.1, #3.2, #3.3 and the two `#2.x` branches — one off the multiplicative total on five
branches. The frequent path has its own shorter `k` block and is untouched.

**Collapsing a specialisation is where disguised squarings are born.** `vh_i = h_i + vp_i` becomes
`vp_i` at `h = 0`, so two distinct arb products silently become one repeated product and another
becomes a square. Neither is visible in the parent, and neither shows up as an error — only as cost.
Worth checking at every `h = 0` collapse rather than reading for correctness alone.

Same evidence as N23: rig over all four `d = 0` sub-paths (5,690 nch2 cases, 0 mismatches),
`driver --strict` 1,017/1,017, `whitebox` 1,812/1,812, blocks agreeing on 1,161 `Deg23ADD` pairs
under Magma, tester clean at 215s, `selftest` 14/14.

## N24 — What the reference block is for, and two facts found by making it say so

**Status:** documentation change plus two established results, 2026-08-16. Genus-3 ramified
`Deg23ADD`, both files. No formula changed; no operation count moved.

The `//startIGNORE` reference blocks exist so that **each explicit part has the polynomial-level
operation it implements written directly above it**. A block that computes the right answer by a
different route fails that purpose while passing every gate — which is exactly what `Deg23ADD`'s did.

**The mismatch.** The block tested `Resultant(u, h+v+vp)` on the outside with the `dw2 = 0` test
nested inside it; the explicit code tests `dw2 = 0` first and the resultant second. The two are
equivalent — `dw2 = 0` implies the resultant vanishes — but the block sat a nesting level deeper
than the code it documents, computed `k` on both sides of a branch where the code computes it once,
and gave a reader no way to pair a block statement with the case it belongs to. Both blocks now
follow the code's order, with `CASE #3.4 / #3.3 / #3.2-#3.1 / #2.3 / #2.2-#2.1 / #1.2-#1.1` labels
matching the explicit `ADD_DEBUG` strings.

**First result: the continued-fraction arm is unreachable at this degree pair, so one formula
covers two cases.** The explicit code splits `#3.2` from `#3.1` (and `#2.2` from `#2.1`, and the
typical path from its `deg(s) = 0` twin). The block does not, and should not: `s` is reduced modulo
the **quadratic** `u`, so `deg(s) < 2` always, and NUCOMP's `deg(s) >= 2` branch cannot be entered.
Confirmed mechanically — `Quotrem` occurs in `Deg3ADD` and nowhere else in either file. The cases
therefore differ only in the *degree of the output*, which the block's generic
`upp := ExactQuotient(...); upp := upp/LeadingCoefficient(upp)` produces by itself. Splitting the
block would have duplicated a formula to express nothing.

**Second result: at `Deg23ADD` both coefficients of `dw2` must be tested, and at `Deg2ADD` only
one must.** The guard reads `if (dw21 eq 0 and dw20 eq 0)`, and the natural question is whether the
second conjunct is redundant, as it provably is one degree down. It is not.

- At `Deg2ADD` the branch is `u = up`, so `u | (vp - v)(h + v + vp)` with `deg(vp - v) < deg u`
  forces `vp = v` — that is `D1 = D2`, which the dispatcher has already routed to the doubling.
  Hence `dw21 = 0` implies `dw20 = 0`.
- At `Deg23ADD` the branch is `u | up` with `deg u = 2 < 3 = deg up`. The same argument yields only
  `vp = v (mod u)`, which says `D2 = D1 + P3` — an ordinary configuration, not an excluded one. So
  `dw2` can be a nonzero constant.

Measured over GF(11) … GF(29) on 37,760 `u | up` pairs: **460 with `dw21 = 0` and `dw20 != 0`**, and
1,389 the other way round. Witness over GF(11): `u = x^2 + 10x + 2`, `up = x*u`, `vp mod u = 4x + 9`
which equals `v` exactly, giving `dw2 = (h + 2v) mod u = 9`. Both halves of the guard are load-bearing.

**A corollary the guard below it does not need.** The next test reads
`if (dw21 ne 0 and dx0 eq 0)`. Once `#3.4` has returned, `dw21 = 0` implies `dw20 != 0`, and then
`dx0 = dw20*n3 + dw21*n4` collapses to `dw20^2 != 0`. So `dx0 = 0` already forces `dw21 != 0` and
the first conjunct is redundant. **Removed in both files**, which also closed the last place where
the block and the code disagreed — both now read `if IsZero(dx0)`. Cost-neutral, guards not being
counted.

**For the paper:** the two degenerate-case guards look like the same test one degree apart and are
not. Whether a divisor's second coordinate can be tested by its leading coefficient alone depends on
whether the branch's gcd condition makes the two divisors *equal* or merely makes one *contain* the
other — and only the first is excluded by the equal-divisor dispatch.

## N25 — Reduce before you divide: the second-cofactor collapse at `Deg23ADD`

**Status:** implemented and measured, 2026-08-18. Genus-3 ramified `Deg23ADD`, both files. Degenerate
branches only — the frequent case does not move, so no published row changes.

`Deg2ADD` already carried the observation that `a2` collapses to a constant (N21). The same collapse
was available in `Deg23ADD`'s `gcd(u,up) = dw1` family and had not been taken, and the reference block
was already describing the cheaper route while the explicit code did something else:

    t  := (1 - b2*(h + v + vp)) mod u;
    a2 := ExactQuotient(t,S);

**Reducing modulo `u` before dividing by `S` is the whole trick.** `deg u = 2` and `deg S = 1`, so
`t` has degree ≤ 1 and the quotient is a **scalar**; `a1 = 1/m3` is a scalar too, so `a2*a1` is one
field element. Concretely `a2 = -b2*g1` with `g1` the x-coefficient of `(h+v+vp) mod u`, giving
`a2*a1 = -g1*m3^2/dw`, and then

    s = (a2*a1*(v - vp) + b2*k) mod u   ->   sp = a21*vt + M3*kp,   s = sp/dw

with `vt = (v - vp) mod u` and `kp = k mod u`, both degree ≤ 1. **Two products.**

The explicit code had been reducing *late* instead: it built a degree-2 `at`, multiplied by the full
`vt` to get a degree-4 `z` — a 3×3 Karatsuba at 6M — and only then reduced. The split-model addition
has done it the block's way all along, carrying a single `a21` coefficient.

**A squaring in the same tail.** The `deg(s) = 1` setup needs `1/s1`, `s0/s1` and `s1` from one
inversion, and was forming both `dw^2` and `sp1^2`. But `dw*w1` *is* `1/sp1`, and that intermediate
serves two of the three:

    w1:= (dw*sp1)^-1;
    w2:= dw*w1;        // = 1/sp1 -- serves both lines below
    s0:= sp0*w2;       // = sp0/sp1
    w2:= dw*w2;        // = dw/sp1 = 1/s1, so dw^2 need never be formed
    s1:= sp1^2*w1;

| branch | before | after |
|---|---|---|
| arb `#2.1`, `deg(s) = 1` | 59M 5S 97A 1I | **54M 4S 87A 1I** |
| arb `#2.2`, `deg(s) = 0` | 46M 2S 81A 1I | **41M 2S 71A 1I** |
| nch2 `#2.1` | 55M 6S 79A 1I | **50M 5S 72A 1I** |
| nch2 `#2.2` | 42M 3S 64A 1I | **37M 3S 57A 1I** |
| `#2.3`, `#3.x`, typical, both files | — | unchanged |

**These are the most expensive branches in the function** — arb `#2.1` was 59M against the frequent
case's 36M — which is why the collapse is worth more here than the `Deg2ADD` instance was.

### What was checked and found already at its floor

Stated because the negative half is the more reusable half.

- **The `k` and `k mod u` chain is tight.** Liveness confirms `k3` and `k2` are read downstream while
  `k1` and `k0` exist only to produce `kp1`/`kp0`, so that is the right place to attack — but every
  temporary already has two consumers (`up2*k3` serves `k2` and `k1`'s Karatsuba; `up1*k2` serves
  `k1` and `k0`; `u1*kp3` serves `kp2` and `kp1`'s Karatsuba; `u0*kp2` serves `kp0` and the same
  Karatsuba), and both Karatsubas are the paying direction. Regrouping `up0*k3 + up2*k1`, or
  `vp1*vh2 + vp2*vh1`, each needs one fresh product and is 2M either way.
- **`kp` cannot be had more cheaply than by reducing `k`.** The identity `kp = (N mod u)*dw1^{-1}`
  fails precisely here: this branch *is* the one where `gcd(u,up) != 1`, so `dw1` is not invertible
  modulo `u`. And `(N mod (up*u))/up` costs far more than the division it replaces.
- **The `vpp` block's 8M is at the Karatsuba floor.** Reducing `s*(up - upp)` naively costs 9M; with
  the 2×3 Karatsuba it costs 8M, which is what the code already achieves by a different grouping.
- **Expanding `vh` in the `k` block is refused, again.** `vp2*vh2 -> -vp2^2 - h2*vp2` and
  `vp1*vh2 + vp2*vh1 -> -2*vp1*vp2 - h2*vp1 - h1*vp2` buy one M+S for three C. PR16/PR17 took this
  family's C from 12 to 1; three C for one M+S moves against that. Recorded so it is not re-derived
  a third time. At `h = 0` the same rewrites are free rather than trades, and nch2 already has them.
- **One nch2 fold cannot transfer to arb.** nch2 writes `+ up2*(up0 - k1)` for
  `- up0*k3 - up2*k1`, valid only because `k3 = -up2` there. In arb `k3 = f6 - up2` is a general
  value. That single fold is part of why nch2's `#2.1` measures 50M against arb's 54M.

### And the split model's weight scheme cannot come the other way

Asked directly, and the answer is structural rather than a missed technique. The ramified `upp` is
normalised by exactly `-s1^2`, a perfect square in one quantity, so dividing by it distributes as
powers of `1/s1` term by term and rides along on brackets that had to be formed anyway — zero extra
multiplications. Split's normaliser is `-s1*(s1 - c4)` with `c4` a curve constant from the balancing
data: not a power of anything, so it needs one multiplication per coefficient, which is its three
`w2*(...)`. Scaling `s` by `1/s1` there leaves a residual `s1/(s1 - c4)` and still costs three. The
cause is the model — `deg f = 2g+2` with two points at infinity puts a `c4` term at the same degree
as `s1^2`, and they add; the ramified's top degree is clean.

**Evidence.** `rig23` was extended with the `gcd(u,up) = 1` family, which **no oracle in the
repository reached before** — `whitebox` has one frozen case per branch and the random testers never
hit `#2.3` at all. Per file: 8,352 (arb) and 8,641 (nch2) constructed cases over six sub-paths
against `reference.py`, zero mismatches; `driver --strict` 1,818 and 1,017; `whitebox` 1,812/1,812;
reference blocks agreeing with the explicit code on 1,420 and 1,151 `Deg23ADD` pairs under real
Magma; testers clean at 114s and 216s; `selftest` 14 sections including the child-never-dearer
invariant.

**And the coverage gap it closed was not hypothetical.** Two sign errors in `#2.3` — one per file,
the same `+ u0*vp2` where `-[(v - vp) mod u]` requires `- u0*vp2` — were live while
**`whitebox`, `opcount`, the load checks and *both* Magma random testers all passed**. Only the
constructed rig saw them. That branch is reached by one frozen case per file and by no random draw,
so a single-case corpus cannot discriminate a sign there.

**For the paper:** when a cofactor is obtained by dividing one polynomial by another, reduce modulo
the eventual modulus *first*. If the modulus has degree `n` and the divisor degree `n-1`, the
quotient is a constant, and a degree-`(n-1)` object that was going to be multiplied out and reduced
never has to exist. The saving is not in the division but in everything downstream of it.

## N26 — The same collapse at `Deg3ADD`, and the floor measured rather than derived

**Status:** implemented and measured, 2026-08-21. Genus-3 ramified `Deg3ADD`, both files. Degenerate
branches only — the frequent case does not move, so no published row changes.

N21 found the constant cofactor at `Deg2ADD`, N25 took it at `Deg23ADD`. `Deg3ADD` is the last and
largest instance, and it turned into a different kind of result: **the interesting question is not
where the collapse applies but where it has already bottomed out**, and that is measurable rather
than derivable.

### The floor is a measurement

`Deg3ADD` computes `a2 := ExactQuotient(t,S)` at four places, under four different guards. Hand
deriving the achievable degree at each of them was attempted first and got **two of the four wrong,
in both directions** — one site was called reducible when degree 1 is its floor, and the site with
real slack was mis-costed by 2M. What settled it was instrumenting the reference block, which is
executable since N24, and printing `Degree(t)`, `Degree(S)` and `Degree(a2)` at each site over
thirteen fields:

| block site | guard | `deg S` | `deg a2` reached | explicit code carried |
|---|---|---|---|---|
| 1 | `Degree(dw1) eq 1` | 1 | 1 | 1 — at floor |
| 2 | `IsZero(dw)`, `#3.4` | 2 | **0**, in 585 of 585 non-degenerate hits | **1 — slack** |
| 3 | `quo<R\|S>`, `#3.3/2/1` | 2 | 1 | 1 — at floor |
| 4 | `quo<R\|up>`, `#2.x` | 1 | 1 | 1 — at floor |

One site of four, not the four a degree-counting heuristic proposes. `a2 = -b2*(ht2 - h3*up2)`: the
x² coefficient of `(vp + v + h) mod up`, which is `(vp + v + h) - h3*up` because `up` is monic, over
the monic `S = dw1/t7`. **nch2 already had this site constant** — with `h = 0` the reduction is
vacuous — and at `h3 = 0` the arb expression collapses to exactly nch2's shipped `-ht2*wi`, which is
the cross-check that the weight is right.

The load-bearing subtlety, and the reason this is legal only inside `#3.4`: the reduced `a2` is **not
the Bezout cofactor for this `b2`**. It differs by `b2*h3*(up/S)`, and `s` survives only because
`vp - v` vanishes modulo `S/S1` in this branch — the second shared point lies on both divisors. The
double-root case needs its own argument: if `gcd(u,up) = (x-r)²` then `r` must be ramified, since
otherwise the lift of `vp` at `r` is unique and equals `-v-h mod (x-r)²`, which is `#3.5`.

### Reduce before you multiply

The same principle, applied to a product rather than a division, is worth more here than the cofactor
collapse. Three instances, all of the shape *the result is needed modulo `up`, so reduce the operand
first and the product never has the degree you are about to throw away*:

| where | was | now | delta |
|---|---|---|---|
| `s = (a2*a1*(vp-v) + b2*k) mod up`, `#3.3/2/1`, both files | 19M 36A | **18M 23A** | −1M −13A |
| `#3.4`'s `a2` becoming a constant, arb | 14M 23A | **11M 17A** | −3M −6A |
| `s`'s `vp - v` reduced before `a1*(vp-v)`, `dw4` guard, both | 37M 68A / 28M 56A | **36M 64A / 27M 52A** | −1M −4A |

The first is the largest single item in the function. `b2*k` was built as a **degree-5** polynomial —
six coefficients — and then 6M 22A were spent grinding degrees 5, 4 and 3 back off modulo the cubic
`up`. Reducing `k` first costs 3M 6A and makes the product degree 3, matching the other summand, so
the reduction becomes one step at 3M 7A. `Deg3ADD` already did this two hundred lines above, in the
`u = up` family, which is what made the shape credible before it was measured.

### Where reducing first is a loss

Recorded because the rule is not unconditional, and the counter-example is one branch away. In the
`#2.x` `s` section the same rewrite **costs** 2M and saves 5A — a loss at 1M : 3A. The difference is
what else is degree-4: there, `lh = y*z` is degree 4 independently of `k`, so shortening `rh` does
not shorten the reduction, and the `kp` chain is pure addition. In the `#3.3/2/1` case `rh` was the
*only* long summand, so reducing it shortened the reduction itself. **The rule is not "reduce early";
it is "reduce early when the operand you reduce is what makes the reduction long."**

### What the specialisation can do that the parent cannot

Four savings landed in nch2 with no arb counterpart, all traceable to `h = 0` zeroing one coefficient
and leaving a Karatsuba that had paid for itself while the operand was full-degree:

- `z1 = ta - (bt0 + bt1)*y0` is `-bt1*y0` once `y0` is a scalar: −2A, and two copies deleted.
- `lh3`, `lh2` in two separate blocks lose their compensating sums once `y2 = 0`: −2A each.
- **`lh4 = y2*z2 = 0` makes `sp4` the bare scalar `t6`**, so every `up_j*sp4` merges with the
  neighbouring `k_i*t6` into one product `t6*(k_i - up_j)`: **−2M −7A**. In arb `sp4 = lh4 + t6` is
  not a scalar multiple of `t6`, and the same fold has to pay `up_j*lh4` three times — measured
  **+1M**, so arb keeps its Karatsuba form. This is the ordinary direction reversed: usually the
  child inherits the parent's improvement, and here the child admits a restructure the parent cannot.

### A weight the specialisation was carrying for no reason

nch2 carried `at` one factor of `t7` heavier than arb throughout the `#3.3/2/1` family — `ht2*t7` and
`t5*t7` where arb has `ht2` and `t5` — with the `s`-chain below dividing the extra factor back out at
three sites. Six coordinated edits bring it onto arb's weight: **−2M on every call through the
family, and −1M more in whichever of the three `deg(s)` cases is taken.** A first attempt that
changed only the producer and not the consumer gave 248 wrong at `shared = 2`, which is recorded
because the failure is instructive: a weight is a contract between two ends of a computation and
cannot be renegotiated at one end.

This is drift of the kind PR15 found, and **no gate in the repository compares a specialisation's
weights against its parent's** — `selftest`'s invariant compares costs, which were never violated.

### What was checked and found already at its floor

- **The batched inversion** producing `s1`, `1/s1` and `s0/s1` from one inversion is 1I 5M 1S and
  optimal: forming `1/s1` as `d²*w1` trades 1M for 1S+1M, and inverting `sp1` alone needs a second
  inversion for `s1`.
- **`at*vt` at 5M** is the Karatsuba optimum for degree 1 × degree 2; **`y*z` at 6M** is the standard
  3×3; **the degree-4 reduction at 5M** is the 6M two-step with one Karatsuba recovered.
- **Three Karatsubas are exact washes** at the thesis's 1M : 3A — 1M 4A against 2M 1A direct is 7
  against 7. Left alone in both directions.
- **Expanding a nested `w3`** to avoid multiplying by it twice costs 2M+1S against 2M.

**Evidence.** Per file: reference blocks agreeing with the explicit code on 11,892 (arb) and 9,235
(nch2) constructed `Deg3ADD` pairs under real Magma, every gcd class 0–3 hit; `driver --strict`
174,700 comparisons across all fourteen families, zero mismatched; `whitebox` 1,836 frozen cases;
`selftest` 16 sections; the full Magma suite 26 passed, 0 failed. The frequent-case rows are
unchanged by design — `33ADD` 53M 3S 71A 1C and 53M 3S 59A 0C — so **`opcount` cannot see any of
this**, and every figure above is hand-derived from the block text and cross-checked against a
line-by-line M/S/A tally rather than measured by the counter.

**Six live breakages were found and fixed in passing**, five of them mid-edit renames: a variable
read before its only assignment, twice; a cofactor computed against the divided coefficients when
`k := k*S` requires the undivided ones; a reduction lead overwriting the prologue's `t4`, which is
read a hundred lines later; and a dropped `w3 := d*w2`. Only the last was invisible to every static
check — see `ERRATA.md` E15.

**For the paper:** the reduce-first rule extends from division to multiplication, but it is
conditional, and the condition is about the *reduction* rather than the operand: reduce early when
the operand you reduce is what makes the reduction long. And when a formula has many branches, the
achievable degree at each is worth measuring on an executable statement of the algorithm rather than
deriving — four sites, two hand-derived wrong, and the measurement was a dozen lines.

## N27 — Writing the algorithm down four times, and what that surfaced in the doubling

**Status:** implemented and verified, 2026-08-22. `arb_ramifiedG3_DBL.mag`, `Deg3DBL`. The
restructure itself was cost-neutral — `57M 4S 92A 3C` to `56M 4S 93A 4C`, one multiplication
reclassified M→C and one addition added, so total multiplicative work held at 64 — and **three live
defects were found on the way**. A six-lens efficiency sweep afterwards took the frequent case to
**`54M 4S 84A 4C`**, i.e. **−2M −9A** against the restructured form and −3M −8A against where PR16
left it, with a further **−1M −7A** off the degenerate leaves. Both halves are below.

### The reference block had one prelude serving four leaves, and that hid the arithmetic

`Deg3DBL`'s polynomial reference block originally stated the shared work once — `k`, the gcd, the
division of `u` — and then branched. That is the economical way to write it and the wrong way to
*check* it, because the explicit code does not share those steps: each leaf recomputes `k` against
a different modulus, and the whole point of the degenerate leaves is that they differ in which `u`
and which `v` they use. A block that shares the prelude cannot be laid against the code line by
line, so a reader cannot see which leaf is doing what.

Rewriting it as **four self-contained leaves**, each ending in its own `return`, forced a derivation
that the shared form had let us skip. The `deg gcd = 1` leaf had been written as "compose, then
reduce": build `upp := u^2` at degree 4 and reduce. Correct, and not what the explicit computes.
From `vpp = v + u*s`,

    f - vpp*(vpp + h) = u*(dm*k - s*(2v + h) - u*s^2)

so `upp = -s^2 - (s*(2v + h) - dm*k)/u` directly — the two steps at once, at degree 3 throughout.
The `dm*k` in that expression is exactly the explicit code's `kt`, whose `// kt = kp*dm` comment was
the clue that the block was one step behind the code. The leaf's own `M2` line now sits beside the
generic one and the single difference between them is visible: the degenerate leaf carries `dm*k`
where the generic carries plain `k`.

**A naming collision fell out of the same exercise.** Three objects were competing for two names:
`dw = (2v + h) mod u`, the raw gcd whose coefficients the explicit calls `m7` and `-m8`, and that
gcd made monic. At `deg u = 3` the second and third are genuinely different objects — `dw` can be
quadratic while the gcd is linear — which is *not* true at `deg u = 2`, where `Deg2DBL` may take
`dw` directly. The block now says so in as many words, because the analogy from the lower degree is
exactly the trap: an idiom that transfers between `Deg2DBL` and `Deg3DBL` for two of the four leaves
and silently fails for the others.

### Three defects, and none of them was findable by a static check

Recorded in full as `ERRATA.md` **E17** and **E18**; the summary here is the part that generalises.

1. **A scratch assignment onto a live matrix slot.** `t7` holds `T`'s (3,1) entry and was reused as
   scratch (`t7 := f6*u1`) above a read that wanted the entry, so `b1` became `1/(f6*u1)` and the
   branch died whenever `f6` or `u1` was zero.
2. **A "redundant" saved copy that was not.** `tx := u2` genuinely was redundant, `u2` never being
   overwritten; `ty := u1` was not, and removing it left `u0 := u1 - u1*dm0` reading the `u1`
   assigned one line above where the exact division needs the earlier value. **105 of 116 wrong** in
   the one-ramified-point class, and clean in every other class.
3. **A missing comma**, which `opcount` answered by printing the other two rows and omitting the
   third rather than failing.

The generalisable point is about **gate coverage for value-level errors**. `dominance.py`, added the
day before, asks whether every read has an assignment above it — which subsumes asking whether it is
assigned at all. It passes on all three of these, because in every case the name *is* assigned above
— with the wrong value. This is a strictly harder class than E15's sibling-path reads, and the only two instruments
that see it are `blockcheck.py`, which executes the reference block against the explicit code and
compares per ramification class, and real Magma. The class-wise report is what made the second
defect diagnosable in one run rather than bisected: 105 of 116 wrong in exactly one class localises
the error to one leaf before any code is read.

**So the reference block earns its keep twice over.** N24 recorded that making it *runnable* found
two facts. Making it *leaf-for-leaf congruent with the code* is what turned it into a debugger: the
class breakdown is only informative because each class corresponds to exactly one leaf.

### Two gate repairs, one of which had been reporting the wrong thing

`blockcheck` labelled its doubling classes "shared x-coordinates", the addition's axis, where the
driver it runs measures **ramified points** — right numbers, wrong name, for the axis that
distinguishes every doubling branch.

`adjugate.py`'s ledger lookup is the more interesting one, and it is E14's third firing. Deleting an
inline `// Nm Ns Na` comment did not report a missing comment; it silently promoted the next
unlabelled ledger 217 lines downstream and reported the *code* as wrong. Two candidate fixes were
built and both fail, informatively: a fixed line window cannot work because the genuine ledger sits
28 lines below the anchor in the doubling and 575 below it in the addition, and "must precede the
first guard" fails for the same reason. What separates the two files is that the addition **labels**
its ledgers, so its unlabelled one is unambiguous wherever it sits, while the doubling labels none
and must therefore pin its single ledger to the determinant. The rule is now conditioned on that,
and both deletions leave the key absent rather than borrowing a neighbour.

### The frequent path had no name

`Deg3DBL`'s generic branch — 94% of calls — carried no `DBL_DEBUG` label, so `whitebox` could not
see it: exactly the gap PR16 demonstrated for `Deg3ADD` with a tripwire, where sabotaging the
frequent path left the gate at 1812/1812 PASS. Labelled, and the corpus re-harvested to cover it:
**94 → 96 cases, denominator 1,869 → 1,870, coverage 1,866/1,870.** `coverage_baseline.json` needed
no change, the new branch being genuinely covered rather than exempted.

Ten further returns in the file are unlabelled and correctly so — they are inside the
`/* //startIGNORE ... */` reference blocks and never execute. Four more are the dispatcher's leaves,
which are live; those are left alone deliberately, because the addition's dispatcher carries no
labels either and labelling one file's dispatcher and not the other's would create the divergence
this work exists to remove.

### The efficiency sweep, and why independent convergence is the signal worth acting on

Six searches were run over the same function, each given one lens and no knowledge of the others:
reduce-before-multiply, Karatsuba in both directions, disguised squarings and shared subexpressions,
liveness and code motion, weight and inversion scheduling, and cross-file technique comparison
against `Deg3ADD`, the odd-characteristic sibling and split's `Deg3DBL`. They produced **40
candidates over 22 distinct sites, plus 99 notes on ground already at its floor.**

**What decided which to take was agreement between lenses that could not see each other.** Five of
the five items applied were multi-lens; every single-lens candidate on the frequent path turned out
to be either a duplicate or already covered.

| taken | where | measured |
|---|---|---|
| `l = r*s + M2` outright, so the division by `q` is never performed | frequent, the `vpp` tail | **−2M −5A** |
| `t9*f6` for `- t10 - t10`, and `t8*f6` for `- t11 - t11` | frequent, the `k` block | **−2A**, 2 statements gone |
| `ht1`/`ht2` named once, the T setup already forming both | all four leaves | **−1A** frequent, −6A rare |
| `t5 + t3 - t9` for `t5 - u1 - u1 + t3` | frequent, `M20` | **−1A** |
| `b10 := t8*w1` | the `deg gcd = 1` leaf | **−1M −1A** |

The largest, and the only one carrying real mathematics, is the first. `l := ExactQuotient(u*r - upp, q)`
looks like a division and is not one: `u*r − upp = r*(u − r) + q*M2 = q*(r*s + M2)`, so **`l = r*s + M2`
with the quotient never formed.** That deletes an entire temporary and the `q0*t9` product with it.
Three lenses derived it independently and produced *the same replacement text*, and all three
predicted `54M 4S 88A 4C` before it was applied — which is what it measured.

**Two smaller ones are the same shape as PR16's B1** — a value already computed and then recomputed.
`t8` at the T setup holds exactly `t4 - u2*t7`, and the degenerate leaf re-formed it; the T setup
likewise already forms `vh1 + v1` and `vh2 + v2`, and six later sites re-formed them. Naming a
quantity the code has already built is free, and it was worth −1M −7A here. **Six of six lenses found
the `b10` one independently**, which is the strongest convergence in the set and says something about
how visible this class is once you look for it — and how invisible it is otherwise, since it had
survived PR14, PR16 and this session's own restructure.

### The refutations, which are the more durable output

Recorded because a negative result stops the next search, and several of these are proofs rather than
failures to find anything:

- **The three `k`/`kp` sites are at their floor.** The frequent path computes exactly the three
  coefficients its consumers read, and none of `kp3..kp1` or `k2..k0` on the degenerate branch is
  dead. This was the reduce-first lens's main question, answered negatively.
- **Reducing `kp` mod the new `u` instead of the original is a LOSS** on the `d = 0`, `m7 ≠ 0`
  branch, confirming the file's own comment. The same conditionality N26 established.
- **No disguised squaring exists anywhere on the frequent path.** All 56 products were enumerated by
  operand pair. PR17 found eleven in the sibling addition; there are none here.
- **The `s2` weight on `r` is pinned by the mathematics, not chosen**, so the two `*s2` products
  cannot ride along and be removed once — the weight lens's own hypothesis, refuted with a proof.
- **The Karatsuba squaring of `r` loses**, and the `k = kp mod u` reduction is a *degenerate*
  Karatsuba site in every instance because `kp` is monic. Both directions of the technique checked.
- **`m2`, `m3`, `m5` are not deferrable** past `if IsZero(d)`: the determinant genuinely reads all
  three. Refuted with a count, so the `m4`/`m6` deferral does not generalise.
- **Hoisting `t6 := f6 - u2 - u2` above the `sp2` guard is an exact wash** — built, measured,
  reverted.
- **The single-inversion budget holds**, verified by enumerating all five inversion sites rather than
  assumed; and both weight-inversion blocks are at their floor (1I 6M 1S and 1I 5M 2S), every weight
  read.
- **The adjugate and the matrix-vector product are at their floor**, and C2 was re-confirmed from the
  split side — so that item stays closed rather than being reopened.

**One candidate was refuted on location alone**, quoting text that is not in the function. That is
the failure mode PR16 recorded when every line number in `EFFICIENCY_ARB_G3.md` had gone stale, and
it is why a proposal is checked against the file before it is costed.

**One available saving was deliberately NOT taken**, and the reason is this session's own scar
tissue: a further −1A is available by making `M20`'s prefix a single live variable, but the proposal
reuses `t4` — a live matrix slot — to free the name it needs. That is exactly the E17 defect class,
twice over in two days, for one addition in eighty-four. It wants a `t0x` slot and a liveness proof,
not a quick substitution.

**For the paper:** an executable statement of the algorithm is worth writing in the same shape as
the code it documents, not the shortest shape that is mathematically complete. The economical form —
prelude once, then branch — is unusable as an oracle, because the branch-wise agreement report is
only diagnostic when branches correspond one-to-one. The defect class that survives every static
check is not the undefined read but the **defined-with-the-wrong-value** read; the instrument for it
is differential execution against an independent statement of the same algorithm, per branch. And
when several independent searches are run over one function, **agreement between searches that cannot
see each other is a better filter than any single search's confidence** — every item that survived
measurement here was found by two or more lenses, and the one six-lens item was a recomputation of a
value the function already had.

## N28 — The sixth cell, and a coefficient the formula already had under another name

**Status:** implemented and verified, 2026-08-23. New file `nch2_ramifiedG3_DBL.mag`; both genus-3
ramified doublings re-measured. This completes five of the six cells of the
`{arb, nch2, ch2} x {ADD, DBL}` matrix at genus 3; only characteristic 2 remains.

### The family had been doubling with the wrong formulas, correctly

Since the import, odd-characteristic genus-3 doubling had no formulas of its own. It *borrowed* the
arbitrary-characteristic ones — the tester loaded `arb_ramifiedG3_DBL.mag`, `driver.py` carried an
explicit borrow, and the addition's equal-divisor dispatch passed `0*f` for the absent `h`. That was
correct, because `h = 0` curves are a subset of what the arb file accepts, and it is exactly why
nothing ever flagged it: **a specialisation that silently uses its parent produces right answers at
the parent's price.** PR15 recorded the resulting mixed-domain state; this entry closes it.

Deriving the file is mostly mechanical — `h = 0` kills 105 coefficient occurrences and `f6 = 0`
another 29 — but the cost it removes is not evenly spread:

| | parent (arb) | specialised | removed |
|---|---|---|---|
| `Deg1DBL` | 7M 1S 24A 4C | **5M 1S 15A 1C** | 2M, 9A, 3C |
| `Deg2DBL` | 28M 4S 70A 9C | **25M 4S 44A 0C** | 3M, 26A, 9C |
| `Deg3DBL` | 54M 4S 80A 4C | **53M 5S 61A 0C** | 1M, 19A, 4C (+1S) |

**Every constant multiplication disappears.** That is the sharp structural result: at `h = 0` and
`f6 = 0` the only surviving curve coefficients are `f5 … f0`, and each enters *additively* rather
than as a multiplicand — the same property that makes every published odd-characteristic count
C-free, and the reason those counts are now directly comparable with ours.

**The reduction of `2v + h` mod `u` vanishes entirely.** At `h = 0` the first column of the
multiplication matrix `T` is just `2v`, so `t1`, `t4`, `t7` become `2v0`, `2v1`, `2v2` and
`Deg1DBL`'s resultant is `2*v0` outright with no `u`-dependence left to reduce. Two products above
`Deg2DBL`'s `IsZero(d)` guard — `u1^2` and `u0*u1`, needed by arb for `m3` and `m4` — become dead
there and move into the branches that use them.

### `M21 = -kp3`: a coefficient the formula was recomputing under another name

The largest single saving is not a specialisation effect at all; it is an identity the arb file
cannot have. In `Deg2DBL`'s frequent case, `M2`'s x-coefficient is **exactly minus the reduced
quotient's top coefficient**:

    t5  = u0 - t1                     (t1 = u1^2)
    kp3 = k3 - t5 + t1  = k3 - u0 + 2*u1^2
    M21 = u0 - k3 - u1*M22            with M22 = 2*u1
        = u0 - k3 - 2*u1^2  = -kp3

So `M21`'s whole statement is redundant, and `u1*M21 = -t9` where `t9 = u1*kp3` was already formed
four lines earlier. Two further products go the same way: `u1*M22 = 2*u1^2 = t1 + t1` and
`u0*M22 = 2*u0*u1 = t2 + t2`, both already in hand for the resultant. Net **-3M -1A**, free on both
axes — `28M 4S 45A` to `25M 4S 44A`. It holds only at `h = 0`: arb's `M21` carries `h2*s1 + h3*s0`
and the identity fails.

### The exact division that is not one, one branch further

N27 recorded that `l := ExactQuotient(u*r - upp, q)` needs no division. The same shape appears in
`Deg2DBL`'s `gcd = d` leaf and had not been taken: there the new `u` is **linear**, so `k` can be
evaluated at its root by Horner instead of first being reduced modulo the original quadratic `u`.
Both routes cost five multiplications; the Horner one costs six fewer additions (five in arb). The
`kp` block — four statements and a Karatsuba — disappears.

**This one was nearly broken by being "corrected".** Its sign handling looks wrong on inspection, and
the reading that looks right fails every one of 120,000 trials while the code as proposed passes all
of them. The test is only meaningful under the leaf's own precondition — the new linear `u` must
divide the original quadratic one, so `u0 = u1*c - c^2` — and a random test without that constraint
verifies nothing. **Recorded because the instinct to fix it was wrong and the measurement was right.**

### Keeping a coefficient bare recovers the C column

`ERRATA.md` **E13** records that a product by a *composite* over curve coefficients is charged M
where it is honestly C, because the constant is no longer a bare name. `Deg1DBL` shows the reverse is
exploitable: `t1*(f4 + f4)` is charged 1M, while `t10 := t1*f4; t10 + t10` computes the same value
with `f4` bare and is charged **1C**, at identical additions. One multiplication moved to the cheaper
column by multiplying first and doubling second. This is the first instance in the repository of
*restructuring to keep the coefficient bare* rather than waiting for the counter to be fixed.

### Every integer scalar multiple is now an explicit addition chain

Both doubling files previously wrote `7*t1`, `5*f5`, `3*f3`, `6*(f6*t1)`, `4*f4`, `2*(...)`. The
convention prices each at 1A (`chapter6.tex:2333`), which understates them: written out they cost 12A
for the six. They are now addition chains, at a true cost of **+2A per file**, not +9A, because of
three things worth stating:

- **a joint chain beats two separate ones.** `7*t1 + 5*f5` reaches both coefficients at once through
  `(1,1) -> (2,2) -> (3,2) -> (6,4) -> (7,5)`, five additions where `7a` alone is four and `5b` alone
  is three.
- **doubling after the offset beats doubling before.** `(3,2) -> (6,4) -> (7,5)` needs one doubling;
  building `4t1 + 4f5` first and patching both coefficients needs three separate adds.
- **an existing doubling can serve as a multiplier.** `upp1 = u0 + u0` is the `2*u0` the `k0` term
  needs, so the factored form `2*u0*(t1*(3Y + 2f4) + Z)` pays that doubling once and uses it twice.

The multipliers themselves are forced: `k0 = P'(-u0)` for `P = f - v*(v+h)`, so they are the
derivative's `7,6,5,4,3,2` and no rewriting removes them. What is *not* forced is how they are built.

### Two defects, and the second is a gate failing quietly

Both arose in cleanup, not in the derivation.

**A "free copy" that was not safe to collapse.** At `f6 = 0` the statement `t3 := t2` is a pure
rename, so removing it and reading `t2` directly looks free. But `t2` is reused as scratch
(`t2 := s1*q0`) between the assignment and the later read, so `M20` read the wrong value: **106 wrong
of 120** on the generic path, clean in every other class. This is `ERRATA.md` **E17**'s fourth
instance in four days. The rule it earns: **collapsing a copy requires a liveness proof on the
SOURCE, not on the copy.** `dominance.py` passes on all four — the name is assigned above, with the
wrong value.

**A missing semicolon that `opcount` hid.** `vpp0:= vh0 - s1*(s0*u0) - upp0*t3` lost its terminator.
`opcount` printed the `1DBL` and `2DBL` rows, **silently omitted `3DBL`, and exited 0** — the second
firing of **E18**. `dominance.py` passed, being a line scanner. Only `blockcheck` named it, and
loading the file under Magma gave the line and column. A disappearing row is an error, not a zero.

### What the six-lens sweep says about consensus

Forty-three candidates over both files, 111 notes on ground already at its floor. Six savings
survived measurement. The methodological result is about **how** to read agreement between
independent searches:

- **convergence is a good filter for whether a saving exists.** Every item that survived was found by
  at least one lens that located it in the real file; the item six lenses found independently
  (`M22 = un1 + un1`) was real.
- **convergence is a bad filter for how large it is.** On the two biggest items the *majority* was
  correct but incomplete and a single lens had the full result: five lenses proposed `-2M` where one
  found `-3M -1A`, and three proposed `-1A`/`-2A` where one found `-4A` by folding a third consumer.
  A majority vote would have banked two thirds of the available saving and called it done.

### The family got real whitebox testers, and every family in the repository now has one

PR6's other half. Genus-3 ramified had **no Magma whitebox tester**: its branch coverage came from
*harvested* cases -- found by the Python harness's own coverage-guided search and frozen -- which is
weaker than the *extracted* cases every other family uses, because it is the same oracle checking
itself rather than Magma's Jacobian arithmetic checking the formulas.

The blocker was specific and recorded by PR4: `whitebox_auto_NEG.py` synthesises the expected label
set as `ADD000..ADDnnn` from the *count* of DEBUG lines, so it could not consume this family's prose
labels. The choice was to number the labels or teach the generator prose. **Numbering won**, matching
genus-2 ramified and both split models -- 96 labels across four files became `ADD00..ADD36` and
`DBL00..DBL10` -- with each branch's meaning kept in a trailing comment, since the prose was
deliberately built and the plan itself calls the numeric tags opaque.

**Coverage came from enumeration, not sampling, and that is the transferable part.** PR12 measured
`RandomDivisorAB` reaching 25% of the reduced divisors on one split curve: it rejects an inseparable
`u` and any `u` with an irreducible factor of degree > 1. The ramified model makes the fix far
cheaper than it was there, because a ramified divisor is `<u,v>` with **no balancing weight**, so it
maps straight onto a Magma Jacobian element:

- `DivisorsWithU` lists every `v` with `u | v^2 + v*h - f`, so the divisor space is enumerated;
- class targeting is Magma's own arithmetic -- `D2 := T - D1` is Jacobian subtraction, where the
  split generator needed a local `InverseD` because `Negate` returns a non-inverse at odd genus (E8);
- pair modes are built rather than waited for: equal `u`, a shared irreducible factor, forced class
  sums, and a shape matrix over `(deg u1, deg u2)`.

Result: **48 of 48 branch tags in each family**, 48 constructed cases per tester, every case asserted
against `D1 + D2` on the Jacobian. Shown to be a real oracle rather than a label printer by
perturbing `Deg1DBL`'s `upp1` and watching `Assertion failed`.

**The instructive failure was the frequent case.** nch2 first reached 46 of 48, missing `ADD36` --
`Typical, deg(s) = 2`, about 90% of calls. `AllDivisors` lists the identity first and the generic
filler scanned row by row from `i = 1`, so all 200 filler pairs were `<identity, D>`, which route
through an unlabelled dispatcher leaf and can never contribute a case. **A budget spent in list order
is not a budget spent on variety**; the shape matrix fixed it by construction.

Downstream, the harvested corpus that stood in for these testers is now **empty** -- the same 100%
coverage comes from extracted cases -- and `test_all.sh` reports **28 testers, 0 skips**, the two
skips having been exactly these two gaps. The harvest machinery stays for the next family derived
before its tester exists, which is ch2 at genus 3.

### E12 closed: a tester that verified nothing said so

Fourteen canonical random testers now print a comparison count and assert it non-zero. `assert` was
chosen over a warning because `test_all.sh` already greps `Runtime error|Assertion failed`, so the
check is fatal without touching the parser. Demonstrated by reproducing the original discovery: run
from a directory where every `load` fails, a tester used to print `TEST_ADD: true` and
`// No errors.` in 0.469 seconds and now prints `// Comparisons: 0` and `Assertion failed`. The two
genus-3 ramified testers also stopped echoing `TEST_ADD`/`TEST_DBL`, which are *configuration
switches* -- printing them beside a verdict is what made a vacuous run look verified.

**For the paper:** a specialisation that borrows its parent's formulas is correct and therefore
invisible; the cost only becomes measurable once the child exists, and here it was 26 additions and
every constant multiplication in one function. Separately, an integer multiplier priced at one
addition by convention costs more than that in fact, and the honest cost depends on the chain — a
joint chain over two coefficients, and reusing a doubling the result needs anyway, took the true
price of removing six of them from +9A to +2A.


## N29 — Completing the matrix: characteristic 2 at genus 3, and a sentence that moved the tested domain

The last two cells. `ch2_ramifiedG3_{ADD,DBL}.mag` specialise the arbitrary-characteristic
formulas at `h` monic of degree exactly 3 and `f₆ = f₅ = f₄ = f₃ = 0`, in characteristic 2 —
the form Part I derives and `RandomG3Char2Curve` has built since the generator work. With
these, all six cells of `{arb, nch2, ch2} × {ADD, DBL}` exist at genus 3 ramified, and every
one of the repository's fourteen families has a Magma whitebox tester.

| | parent (arb) | ch2 |
|---|---|---|
| `Deg1DBL` | 7M 1S 24A 4C | **4M 2S 7A 2C** |
| `Deg2DBL` | 28M 4S 70A 9C | **21M 4S 38A 5C** |
| `Deg3DBL` | 54M 4S 80A 4C | **51M 4S 55A 2C** |
| `Deg3ADD` | 53M 3S 71A 1C | **53M 3S 66A 0C** |

**The doubling gains far more than the addition, and the reason is worth stating.** Nearly all
of the doubling's saving is arithmetic that stops existing rather than arithmetic done better.
Its integer multipliers had been rewritten as addition chains (N28), and in characteristic 2
half of every chain is zero: the five-rung chain building `7t₁ + 5f₅` collapses to `t₁`
because `7 ≡ 5 ≡ 1` and `f₅ = 0`; `3(f₃ − h₃v₀)` becomes `v₀`; `3(f₆t₁) + 2f₄` dies twice
over, once through `6 ≡ 4 ≡ 0` and again through `f₆ = f₄ = 0`; and `2u₀ = 0` kills both a
product and a returned coordinate. `k₃ = f₆ − 2u₂ = 0` removes an entire reduction step of
`k = kp mod u`. The addition has no comparable structure to lose, which is why its frequent
case saves one constant multiplication and five additions and no multiplications at all. That
is thin, and it is the obvious target for an efficiency pass rather than a result to dress up.

**`k₀` was derived twice and the two agree.** Reducing the parent's chains mod 2 gives
`t₁(t₁² + v₀) + f₁ + h₁v₀`. Deriving it afresh: `k(u₀) = P'(u₀)` for `P = f − v(v+h)` holds in
any characteristic, and in characteristic 2 only odd-degree terms differentiate, so
`P' = x⁶ + v₀x² + f₁ + h₁v₀`. Same expression by two routes.

### The efficiency pass, and the saving that was refused

The specialisation had bought `1C` and `5A` on the frequent addition and **not one
multiplication**, which is why it was swept: six lenses, 18 findings, 104 notes on
ground already at its floor.

    Deg3ADD typical   53M 3S 66A 0C   ->   51M 3S 62A 0C     (parent: 53M 3S 71A 1C)

**`l := ExactQuotient(u*r - upp, q)` is not a division.** With `C := (u*s) div
(up*s2)`, monic of degree 2, `u + w3*M1 = q*C`, so `u*r - upp = q*(r*C + w3*M2)`
and `l = r*C + w3*M2` — the quotient is never formed. `C1` is `u2 + q0`, and `C0`
collapses to `s0 + t8 + t6` because `q0*t7 = up2*t7 + s1*t7` and the prologue's
`t8 = t4 + up2*t7` cancels the `t4` that `u1 + up1` supplies, so `C0` costs two
additions and no new multiplication. Then `vpp = l + v + h + (r1 + 1)*upp` lets
each `r1*C_i` pair with the `r1*upp_i` beside it. The block goes from 9M 19A to
7M 17A.

This is **N27's phenomenon through a different identity**. In the doubling `up = u`,
so the analogue collapses all the way to `l = r*s + M2`; here it stops at `r*C`.
Three lenses reached it independently and one derived it as `A := u*s div up`
rather than as `C` — which is what makes it a confirmation, because the brief had
*told* them the doubling result and agreement on the conclusion alone would have
proved nothing.

**Two duplicate computations.** `k2 + up1 = t4 + v2 + u2²` with `t4 = u1 + up1`
already in the prologue, so `u1 + up1` was being formed twice and `k2` need never
be formed at all — which also stops the other two leaves paying for a value they
never read. And `M10 + r0 = vt2 + r1*t7` is what `upp1` wants, built on the way to
`M10` and then discarded; naming the sum and letting `M10` be the extra addition
saves an addition in three separate leaves.

**One finding escapes the family.** `t7*m3 = t7*(up0*m8) = (up0*t7)*m8 = t2*m8`,
and the prologue already holds `t2 = up0*t7`. Pure associativity — no
characteristic assumption and no domain restriction — so it holds in the
arbitrary-characteristic and odd-characteristic parents verbatim, where the signs
cancel because `t2` and `m3` carry the same `-up0` factor. With `d` reading
`t2*m8`, `m3` is wanted only by the typical family and moves there, so every
degenerate leaf stops paying for it. Recorded in both efficiency reports rather
than applied: those files are merged and one is published.

### The refusal, which is the part worth reading

Two lenses agreed the `l` collapse also applies at `ADD29` and `ADD33`, `-2M -2A`
each. It was applied, and **Magma reported 0 wrong across 2,119 comparisons.**

That pass was worthless. Breaking `ADD33`'s `C0` left Magma at 0 wrong and
whitebox at 48/48 *matched*; breaking its `vpp0` unmistakably left Magma **still**
at 0 wrong, and only whitebox caught it. So the probe never reaches `ADD33`, and
whitebox reaches it through one frozen case whose `t8` happens to be zero — the
very term the change turns on.

The change was reverted. Not because it is thought wrong, but because nothing in
the repository can tell, and landing it would assert a correctness claim no gate
supports. Recorded as `ERRATA.md` **E20**, with the two independent causes: the
probe has no pair-construction mode for `gcd(u, up) = e` or `= ew`, and one case
per branch is complete without being adequate — a case whose coefficients zero a
term cannot see a change to that term.

**For the paper.** This is the sharpest form of the rule E15 states. There the
edit could not be run at all; here it *was* run, under real Magma, and came back
green — and the green carried no information. A pass on an unreached branch is
indistinguishable from a pass on a correct one, which is the entire argument for
running a negative control per landed item rather than once at the end. Every
saving above is reported with the control that fires for it.

### A sentence in a banner could redefine what gets tested

The finding of independent interest, recorded as `ERRATA.md` **E19**. `driver.banner_members`
reads a file's own banner to learn which curve coefficients are pinned, and the singleton form
the characteristic-2 normal form needs — `h₂ = 1`, not `h₂ ∈ {0,1}` — was matched anywhere in
the banner region. It therefore could not distinguish a declaration from a sentence.

Writing the genus-3 characteristic-2 banner produced exactly that collision. It declares the
domain correctly, `(deg h = 3, h₃ = 1)`, and then *explains* it two lines later: the y-shift
clears `f₅` through `a₂h₃`, so at `h₃ = 0` the reduction fails. The parser read the union,
`{0,1}`, and `curve_in_domain` would then have generated `deg h < 3` curves — precisely the
family these formulas do not cover and the declaration exists to exclude.

**The genus-3 odd-characteristic banners have the same shape and were harmless only by luck.**
Both explain the depression as "the translation `x → x − f₆/7` gives `f₆ = 0`", which parsed as
a pin — so `family_domain` *discarded* 6 from the contrast-derived constraint and then
re-imposed it through the members channel. Measured: the contrast said `{'f': {6}}`, the banner
reduced it to `{'f': set()}`, and 240 generated curves still came out with `f₆ = 0` because the
pin replaced the constraint it had removed. The two effects cancelled because that sentence
happens to state the truth.

Declarations are parenthesised in every file that has one, so the singleton form is now read
only inside parentheses. **For the paper:** this is the same class as an inline op-count comment
being read as gate input (E14), and worse in effect — not a wrong report but a silently
different tested domain. A project that puts machine-readable declarations in comments has to
say where the comment stops being prose, and this one had not.

### Two limits of the harness, found by trying to use it

**The specialisation invariant compares only the modal leaf.** It was relaxed here from
per-column M+S, A, C to an aggregate M+S+C, because ch2's `Deg23ADD` trades two multiplications
for one squaring and one constant product: 39 multiplicative operations either way and nine
fewer additions, which the per-column rule rejected as "C 1 > 0". The only way to satisfy the
old rule was to write a constant product as though its operand were general — the dishonest
accounting E13 exists to warn about — and S had already been pooled with M for exactly this
reason. Re-demonstrating that it still catches drift is where the limit surfaced: an injected
+4M *passed*, because it had gone into a 3.7% leaf. Aimed at the 87% leaf it fails correctly.
So this gate cannot see drift in a degenerate branch, which is the same blindness the operation
counter has and for the same reason.

**`blockcheck` withholds a verdict rather than passing vacuously, and that mattered.** Asked to
check the new `Deg3DBL` reference block it reported `UNTESTED: gcd class(es) 3 produced no
comparisons` and declined to say the block agreed — because the fully ramified class needs
`u = h` exactly, which its default budget never reached. Twelve curves over GF(4), GF(8) and
GF(16) reach it in 8 comparisons, and then it agrees. A gate that reports "nothing compared"
instead of "0 wrong" is the difference between this being evidence and being decoration.

### How it was verified

Real Magma against its own Jacobian arithmetic, on curves from `RandomG3Char2Curve` with the
declared domain asserted per curve, enumerating the divisors and **constructing** the pairs —
a shape matrix over `(deg u₁, deg u₂)`, equal `u` with different `v`, shared irreducible
factors, and forced class sums including `D₂ = −D₁`. Construction rather than sampling because
the degenerate branches dispatch on `deg gcd(u, up)`, and independent draws share a factor with
probability `O(1/q)`.

**1,777 additions across all nine degree shapes and all four gcd classes, 0 wrong. 2,223
doublings across all three degrees and all four ramification classes, 0 wrong.** Both oracles
shown to bite, aimed at the leaves that matter: perturbing `Deg3ADD`'s 87% leaf gives 12 wrong
of 1,001, and dropping `h₁v₀` from `Deg1DBL`'s `k₀` gives 12 wrong of 41 — only 12 because
`h₁v₀` vanishes whenever either factor does, which is why the report is split per class rather
than given as a single total.

All four reference blocks agree with their explicit code. `whitebox` replays 1,886 cases with
the new files at 37/37 and 11/11. `driver --strict` rises from 12,972 to 13,746 comparisons,
0 wrong, now that the family is covered. The Magma suite is 30 testers, 0 failures, 0 skips.

**One honest limit on the derivation.** `Deg3ADD` is 956 lines and was derived in five regions
— prologue, and one per gcd family. The glue lines *between* regions belonged to no region, and
one still read `h₃`: the file would not have loaded. It was found by grepping for live
references to the dropped symbols, not by the splice being trusted. Region-wise assembly of a
function needs that check as a standing step, because the regions are what get verified and the
seams are what do not.


## N30 — A multiplication that moved, and the ledger that would not let it be miscounted

`Deg3ADD` computes, above the `d` guard, `m3 := -up0*m8` and then
`d := t1*m1 + t4*m2 + t7*m3`. But `t7*m3 = t7*(-up0*m8) = (-up0*t7)*m8 = t2*m8`,
and the prologue already holds `t2 = -up0*t7` — the signs cancelling because `t2`
and `m3` carry the same `-up0` factor. **Pure associativity: no characteristic
assumption, no domain restriction, true on every curve.**

With `d` reading `t2*m8`, `m3`'s only remaining reader is the typical case's `sp0`,
so it is computed there. Applied to all three genus-3 ramified additions and the
arbitrary doubling, whose determinant block has the same shape.

**What it is worth, stated exactly.** Nothing on the frequent path, and a
multiplication on every leaf that returns before `sp0`:

| file | degenerate leaves | frequent |
|---|---|---|
| `arb_ramifiedG3_ADD` | 50→49M, 77→76M, 82→81M | unchanged, `53M 3S 71A 1C` |
| `nch2_ramifiedG3_ADD` | 73→72M, 49→48M, 29→28M | unchanged, `53M 3S 59A 0C` |
| `ch2_ramifiedG3_ADD` | 76→75M, 50→49M, 79→78M | unchanged, `51M 3S 62A 0C` |

**The gate corrected the accounting, which is the reason this entry exists.** The
file annotates its determinant region `top: 16m` / `11m` / `total: 27m`, and with
`top` falling to 15m it seemed to follow that the total was 26m. `adjugate.py`
refused that: it measures the region, and the region is *all nine entries, `d`, and
`sp = M*vt`* — in which `sp0` reads `m3`, so the path still pays. The
multiplication had moved, not vanished: `top` 16→15, the `sp` block 11→12, total
unchanged at 27m. A saving on the degenerate leaves was very nearly written down
as a saving on the frequent one.

**For the paper:** the inline `// Nm Ns Na` ledgers in these files are gate input,
not decoration (`ERRATA.md` E14), and this is the first time that has *paid*
rather than merely bitten. Four separate places had to agree before the change
would pass — the fragment anchors, both Python transcriptions, the file's own
ledger comments, and the two provocations, which are copies of the shipped
fragment and must match its op count exactly or they stop demonstrating that
values rather than counts are what the check compares. A change that is only
"obviously right" cannot satisfy five independent statements of the same number.

**Provenance.** Found while sweeping the characteristic-2 specialisation (N29),
where it applies identically, and deliberately *not* applied there — those two
parents are merged, so it was recorded in both efficiency reports and carried as
its own PR with its own gate run rather than riding in behind another family's
work.

# Part IV — The comparison with prior work

Full detail in [`RELATED_WORK.md`](RELATED_WORK.md). The three results below are
the ones a paper would claim.

## N8 — Addition counts for the previous best, derived where the authors never stated them

**Status:** established. PR13, merged.

**No prior author reports A.** Every genus-3 ramified paper from 2000–2006
reports multiplications, squarings and inversions only. The thesis counts
additions "unlike many previous works", which makes its comparison table
incomplete in the one column it uniquely provides.

Where the step-by-step formulas are published, A is derivable by us. The key
discovery was that **Fan–Wollinger–Gong Tables XVII/XVIII are a full reprint of
Nyukai's formulas** — the previous best — so the best published counts are
derivable after all: **Nyukai ADD 105A, DBL 93A**, plus all thirteen other FWG
tables, GKP and Birkner.

Validated three ways, because a derived count nobody published is exactly the
kind of number that goes wrong quietly: per-step M sums to the authors' own
published totals; the tables' `Sum` rows match their captions; and hand
recounts on sampled steps.

**This reverses the headline.** Against Nyukai we are 4 combined M+S better and
**28 additions** better; against GKP, 7 and 28. The comparison had previously
been reported the other way round, from a broken counter (N10).

**Two methodological corrections that restructure the comparison itself**, both
the author's:

1. **No prior work counts an arbitrary field.** Every published count is either
   `Fp` (odd, `h = 0`, `f₆ = 0`) or `F2n`. So the comparison runs in three
   lanes, and **our `arb` family has no external baseline at all** — no
   published arbitrary-characteristic genus-3 ramified formulas exist. That is
   itself a finding.
2. **All prior work is frequent-case only.** Special inputs are punted to full
   Cantor — FWG's tables literally read *"If r = 0 then call the Cantor
   algorithm."* So there are no special-case counts to compare anywhere, and
   **completeness — every case explicit, exactly one inversion, no Cantor
   fallback — is a genuine algorithmic differentiator of this repository's
   formulas**, not a fairness footnote.

## N9 — Constant multiplications, on both sides

**Status:** established. PR18, merged.

The thesis counts multiplication by a curve constant separately, as C. Prior
work has no C column, and the reason is structural rather than an omission:
**their normal forms leave almost nothing to multiply by.** Every surviving
coefficient in the depressed odd-characteristic form enters *additively*.
Measured: C = 0 in Nyukai's addition and doubling, in GKP's odd-characteristic
appendices, and in FWG's five `Fp` low-degree tables.

Three consequences, and getting these wrong caused a real error in this project
(the lane-3 comparison, twice):

- **The `Fp` lane needs no C adjustment** — both sides are C ≈ 0, so M+S is the
  complete multiplicative count and the comparison stands as published.
- **Lane 3 is where C decides the answer**, because both sides carry it: the
  thesis's split rows have 12C and 19C, ours 12C and 16C. C must be reported
  separately there and never folded silently.
- **Where a coefficient does survive in characteristic 2, FWG price it as
  variant columns rather than as C**, and the gap between `h = 1` and
  `h arbitrary` *is* the constant's cost: +10 multiplicative operations for the
  `h₂x²` doubling, +6 for `h₁x`, +5 for `h₀`, and only +1 for the additions.
  **Constant multiplication is a doubling problem in characteristic 2 and a
  non-problem in odd characteristic.** A method note that cost us time: FWG
  write these products in vector notation, which a naive scan misses entirely.

## N10 — The project's own addition counts were over-stated

**Status:** established, corrected. PR19, merged.

Every genus-3 ramified **addition** count this project had quoted — in the
audit report, the plan, and the first revision of `RELATED_WORK.md` — came from
counters driving hand-written Python *transcriptions* of the formulas rather
than the formulas themselves. They over-count. Doubling figures always
reconciled because the doubling counter drives the interpreter instead.

Proof by eye: the `nch2 Deg12ADD` typical case was reported as `8M 3S 2I 8A` —
**two inversions for a one-inversion operation** — against a hand-counted and
twice-interpreted `6M 1S 8A 1I`.

Corrected frequent-case baseline, source-level, with C split per the committed
`//Constant:` directives:

| function | M | S | A | C | I | M+S |
|---|---|---|---|---|---|---|
| arb `Deg3ADD` typical | 60 | 4 | 95 | 12 | 1 | 64 |
| arb `Deg3DBL` typical | 56 | 5 | 114 | 16 | 1 | 61 |
| nch2 `Deg3ADD` typical | 59 | 4 | 77 | 3 | 1 | 63 |

**Both comparisons invert.** Against published work we are ahead on both axes.
Against the thesis's own *split* rows, ramified is cheaper on multiplications in
both operations — as it should be, having no balancing to do — and dearer only
on additions. **So the standing sanity flag points at A, not M**, which
redirected the efficiency work (N11).

**For the paper.** Counts derived from a transcription rather than from the
artefact are a systematic hazard in this literature, since every published count
is hand-derived from formulas the reader cannot execute. Our own project
produced a wrong comparison this way and published it internally before catching
it. An interpreter that counts the *shipped source* is the fix, and it is cheap.

---

# Part V — Efficiency

## N11 — The arbitrary-characteristic genus-3 formulas carry dead and duplicated work

**Status:** established (report), not yet implemented. PR14 merged as
[`EFFICIENCY_ARB_G3.md`](EFFICIENCY_ARB_G3.md); implementation is PR16.

Thirty findings, **27 confirmed** by independent adversarial verification, 2
partial, 1 refuted. Each verifier had to reproduce the delta from its own rig
*and* re-test correctness against Cantor across all reachable branches before
the finding counted.

The question it set out to answer was why ramified genus-3 addition is dearer on
additions than the thesis's own split-model addition, when ramified has strictly
less work to do. **The answer is mostly dead and duplicated work, not a wrong
algorithm:**

| | ADD | DBL |
|---|---|---|
| today | 60M 4S 95A 12C | 56M 5S 114A 16C |
| after the confirmed findings | **55M 3S 74A 8C** | **≈58M 4S 92A 14C** |
| thesis split, same degree | 65M 3S 87A 12C | 73M 3S 101A 19C |

The corrected addition beats the split addition in **every** column. The
doubling figure is marked approximate on purpose — it sums seven separately
measured edits and composition was not measured.

Three results worth a paper's space beyond the ledger:

- **The largest single finding is dead code**: `Deg3ADD` computes two quotient
  coefficients no branch ever reads, at −5M −1S −19A −4C.
- **A hypothesis held for months was backwards.** Applying the thesis's T13
  first-column recipe to the addition *costs* 12A to save 1M — a losing trade at
  the thesis's own 1M : 3A threshold. The winning direction is the opposite:
  porting the addition's adjugate shape *into* the doubling, at +1M −12A. The
  same trade is available in the split-model genus-3 addition.
- **A finding inherited from the audit was refuted.** Deleting the line it
  identified would have been a correctness bug. Recorded as refuted rather than
  quietly dropped.

**For the paper.** The efficiency gap between two of the author's own formula
families was explained not by algorithmic difference but by unfinished porting —
and the thesis technique everyone would reach for first makes it worse. Both are
more interesting than the raw improvement.

---

# Part VI — Methodology

## N12 — An independent reference implementation and differential oracle

**Status:** established, in CI. PR3, PR12, merged.

Magma is licensed and cannot run on hosted CI, and — verified directly — **it
exits 0 on `Assertion failed`**, so it can never gate on exit status anyway.
Every formula-level claim in this project therefore rests on a second,
independent substrate: a pure-standard-library Python framework that
**interprets the real Magma source text**, so there is no transcription to
drift (which is exactly the failure N10 records).

| | |
|---|---|
| frozen cases replayed in CI | **1,812**, all matching |
| branch coverage | **1,851 / 1,855 (99.8%)** |
| standing differential run | **695,888 / 695,888**, 0 wrong |
| selftest sections | **12**, each provoking the guard it protects |
| Magma suite | 26 passed, 0 failed, 2 skipped |

Three design points that are the transferable part:

- **The gate must be shown to fail.** `selftest.py` provokes each of six guards
  and requires the run to fail; a guard never seen to fire is not known to be a
  guard. Two of them were found to be broken this way, including one whose
  failure path raised a traceback instead of a report — the worst moment to have
  no output.
- **Coverage baselines store a label set, not a count.** A count lets a new
  branch inherit an exemption, lets branches be traded one-for-one, and a
  baseline of zero is unfailable. Measured: the covered-set form still left one
  hole, so the baseline stores the *exempt* set instead, which closes it by
  construction.
- **The whitebox corpus is search-harvested, not deliberately constructed**, and
  four places in the repository said otherwise. What earns those cases a place
  in CI is that they are complete and deterministic, not that anyone designed
  them. Correcting the claim mattered because it changes what a reader should
  infer from 100% coverage.

Along the way the framework also established a result about *reachability*
that is worth reporting: the divisor sampler reached only 25% of reduced
divisors, and reachability is often a property of the **curve** rather than the
divisor — four mutually exclusive classes entered at rates down to `1/q³`. The
hardest branches take inputs whose class sum is forced, which is an equation,
not a coincidence. Steering curve generation is worth ~13× per operation over
sampling harder, and took one family from 353 to **404 of 405** branches.


## N31 — Measuring the split model, and a convention that was costing two additions a row

**Status** — established, PR41. **Where** — `verification/opcount.py`,
`verification/maginterp.py`; the published tables it is checked against are
`Thesis/chapter5.tex` `tab:splitfcosts` and `chapter6.tex`
`tab:g3splitfcosts{ADD,DBL}`.

**What was there.** The counter of record measured **six of fifteen** families.
The nine split ones were refused, and for a real reason rather than an unfinished
one: the ramified domain is derived by *contrast* — what `arb` extracts from the
curve and a specialisation does not is what the specialisation assumes away — and
that argument has nothing to work with in the split model, whose dispatchers read
neither `f` nor `h`. They take `ccs`, the constants `Precompute` derives. So
`family_domain` returned `split family: see split_spec` and stopped.

**What changed.** Three things, and only the third was new mathematics of any
kind. `driver.split_spec` already derived the split domain from `Precompute`'s
own source, and `split_curve_in_domain` already validated the places at infinity;
`build_args_split` already mapped the `(u1,v1,n1,u2,v2,n2,ccs)` signature.
Both are used verbatim. `Precompute` runs once per curve **outside** the measured
call, being per-curve setup rather than part of an operation's cost.

**The third thing is that a split operation's shape is not its degree.** The
published tables price "Degree 1", "Degree 1 with Down Adjust" and "Degree 1 with
two Up Adjusts" as separate rows, at 7M, 14M and 42M. Measured, **the input
balancing weight is exactly what selects between them**: a genus-3 divisor of
degree `d` admits weights `[0, 3-d]`, which gives six `(degree, weight)` pairs,
and those six reproduce the six published doubling rows one for one. The weight
is therefore part of the shape, not a nuisance parameter. Keying on degree alone
pooled rows the thesis prices apart and reported whichever the sampler happened to
favour — under which a degree-1 doubling reported as **42M**, the two-Up-Adjusts
row, rather than 7M.

### The disagreement, which was the tool's and not the thesis's

First measurement put every split row **+2A** above its published cell — all four
genus-3 arbitrary cells checked by hand, `33ADD` 89 against 87, `3DBL` 103 against
101, and both two-Up-Adjust doublings likewise, with `M`, `S` and `C` exact
everywhere. A *systematic* offset is one cause, not four errata, and the standing
adjudication rule says presume the published count correct and hand-count the
divergence.

The cause is that a split divisor carries a **balancing weight**, and the weight
is a small integer in `[0, g]`, not a field element. Every addition runs
`n := n1 + n2 - 2` and every genus-3 doubling `np := n + n - 2`. Charged as field
additions that is a flat `+2A` on every row. The thesis is right not to count
them: they are bookkeeping, of the same kind as a loop index.

So the interpreter gained `INT_ARITH_FREE`, testing operand **type** — sound
because a field element is an `FFElement` in every field this repository builds
and never a Python `int`, so no field addition can be freed by it. Testing by
syntax, the form already used for integer-literal products, cannot work here:
`n1 + n2` contains no literal.

**The convention is not uniform, and assuming it was is a refutation worth
recording.** The guard was first written to assert `+2A` everywhere and **failed
on three cells**. Measured per shape: every addition at both genera and both bases
moves `+2A`, every genus-3 doubling moves `+2A`, and **the genus-2 doublings move
nothing** — they carry no weight addition on the counted path, deriving the new
weight as `2 - Degree(upp)` instead. Nothing but `A` ever moves, in any family.
The pins now carry the measured delta per cell.

### Evidence

With the convention applied, **168 measured shapes reproduce their published cell
exactly**: 42 shapes in each of the three genus-3 split families against
`tab:g3splitfcosts`, and 14 in each of the three genus-2 `posReduced` families
against `tab:splitfcosts` — zero unmatched, and no published row left
unreproduced. Both tables are parsed out of the `.tex` rather than retyped,
because a table retyped by hand is a third place for a number to be wrong. Every
priced row comes out at exactly **one inversion**, which chapter 6 claims in prose
and nothing had checked for the split model.

**This also settles the genus-2 basis question from the other direction.**
`posReduced` matches the published table 14 of 14 in all three characteristic
classes; `negReduced` differs on three to five rows, each by one or two
operations. That is a different algorithm, not a defect — and it independently
confirms `posReduced` as the genus-2 basis of record, which had been decided on a
39/39-against-11/39 comparison made by other means.

**Honest limits.** The genus-2 `negReduced` families are measured but their
figures are checked against nothing, no published table pricing that basis. Both
genus-3 `posReduced` families do not exist to measure. And thirteen genus-3 shapes
per family cost *nothing at all* — inputs the dispatcher answers without
arithmetic; they are verified against `reference.py` like every other sample and
carried in `--json`, but summarised rather than listed, since no published row
prices them.

**One further defect fixed in passing, of the E12 class.** The module's header
claimed every contributing execution was compared against `reference.py`'s
independent Cantor arithmetic. It never was — `measure_call` returned the value
and the histogram discarded it, so a call that left the domain and returned a
wrong answer was histogrammed as a legitimate count. That is the failure mode
that yields a *plausible* wrong number rather than an obvious one, and it is
exactly the risk the split work adds. The check is now performed; a disagreeing
sample is dropped rather than counted. Turning it on moved **no** ramified figure,
which says the previous numbers were not masking anything — but they were
unguarded.

**For the paper.** The operation counts for all fifteen families are now
reproducible from the sources by execution, and the entire arbitrary,
odd-characteristic and characteristic-2 columns of both published split tables
have been independently confirmed — 168 cells, by a method sharing no code with
the one that produced them. The transferable point is the smaller one: an
operation count must decide what is a *field* operation, and a model with a
balancing weight carries integer bookkeeping that looks like arithmetic and is
not. Two additions a row, on every split row in the thesis, hung on that
distinction.


## N32 — Complete is not adequate: what a test corpus can reach against what it can see

**Status** — established, PR38. **Where** — `whitebox/whitebox_auto_NEG.py`,
`verification/detect.py`, and the four regenerated ramified testers. **Errata** —
`ERRATA.md` **E20**, both causes now closed.

**What was there.** The frozen whitebox corpus reached **every** labelled branch in
the repository — 1,925 of 1,929 — and had done for a long time. That is
*completeness*, and this entry is about the discovery that it is not *adequacy*: a
branch reached by one case whose arithmetic happens to zero a term cannot
distinguish a change to that term. The branch is covered; the change is invisible.

**Why it is worth an entry rather than a changelog line: the gap cost a correct
result.** Two independent derivations agreed that the `l = r*C + w3*M2` collapse
applied at `Deg3ADD`'s `ADD29` and `ADD33` leaves, `−2M −2A` each. It was applied.
Real Magma reported 0 wrong across 2,119 comparisons and `whitebox` matched 48 of
48. Both were vacuous, and only the negative control showed it: breaking `ADD33`'s
`C0` left *both* oracles green, and breaking its `vpp0` unmistakably left Magma
green. The saving was reverted — not believed wrong, but unverifiable. It was later
recovered from **outside** the corpus, by exhausting all 11,342 ordered pairs over
GF(4), so the operations are not owed. The corpus that could not see it was
unchanged, and that is what this closes.

### The instrument, and two ways to get it wrong

`verification/detect.py` perturbs every assignment the corpus executes by one and
compares the operation's returned divisor. If the divisor does not move, that
assignment is **invisible**. Three causes — dead, overwritten before use, or
multiplied by zero — are deliberately not distinguished, because for this purpose
they are the same thing.

Two decisions in the metric matter more than the machinery, and a naive version
gets both wrong.

**Scope it to the formula bodies.** Counting every layer gives **48.2%** invisible
where the `Deg*` bodies are at **18.7%**. The difference is the split dispatchers
unpacking `ccs` into some sixty named constants of which any branch reads a handful;
perturbing one a branch never reads is dead unpacking, not a blind spot. Reporting
48.2% would have been a plausible wrong number of exactly the kind this project
keeps having to undo.

**Score by branch, not by case.** An assignment is invisible only if *every* case
covering that branch misses it. Summed per case instead, the two-case corpus scores
85.9% where its union is **93.3%** — and worse, adding a redundant case could
*lower* the score, which is incoherent for a metric whose whole premise is that
more cases cannot hurt.

### The cause was a selection rule, not bad luck

Generators emit every verified block, looping `for F in FIELDS` with FIELDS
ascending; the selector kept the **first** block per label. So every branch's one
case came from the **smallest field reaching it** — the most degenerate arithmetic
available. `ADD33`'s `t8 = 0` was not a coincidence but the predictable consequence
of taking GF(2) when GF(8) sat in the same log. Measured: **every one of the 1,886
cases had at least one invisible assignment.** Systemic, not a handful.

### Two cases per branch, from different fields — and why not one bigger one

| corpus | invisible |
|---|---|
| one case at GF(3), as shipped | 20.0% |
| one case at GF(5) | 9.7% |
| one case at GF(9) | 9.7% |
| **two cases both at GF(3)** | **11.8%** |
| two cases, GF(3) + GF(5) | 7.1% |
| two cases, GF(5) + GF(9) | 6.5% |

Three results worth keeping, none of them obvious in advance:

**Same-field pairs are correlated, so "different fields" is a constraint and not a
preference.** Two cases at GF(3) do *worse* than one case at GF(5): the second draw
shares the first's coincidence probabilities and is blind to most of what it is
blind to. This is the result that decided the rule.

**Field size saturates immediately.** GF(3) to GF(5) halves blindness; GF(5) to
GF(9) gains nothing at all. And the cost does not saturate — enumeration is
`q² + q⁴ + q⁶` divisibility tests, so GF(9) ran over twenty minutes without
finishing where GF(5) is seconds. Climbing only as far as the quota requires is both
cheaper and no worse, which is a pleasant direction for a trade-off to run.

**The quota belongs to the characteristic class, not the family.** `nch2` admits
only odd fields and `ch2` only even ones, so two each; `arb` admits both and takes
two of each. One parameter, no per-family table — and it repairs something nobody
had looked for: `arb`'s genus-3 corpus was **45 cases in characteristic 2 against 3
in odd characteristic**, so 45 of its 48 branches had never been whiteboxed in odd
characteristic at all, in the one family whose entire purpose is working in every
characteristic. It is now 94 against 96.

### Evidence

| family | cases | detectable |
|---|---|---|
| `arb` g3 ramified | 48 → 382 | 81.8% → **96.2%** |
| `nch2` g3 ramified | 48 → 96 | 80.0% → **93.3%** |
| `ch2` g3 ramified | 48 → 96 | 81.4% → **88.3%** |
| `arb` g2 ramified | 22 → 175 | 86.1% → **96.5%** |
| `nch2` g2 ramified | 22 → 44 | 93.2% → **94.1%** |
| `ch2` g2 ramified | 22 → 43 | 87.9% → **95.7%** |
| `arb` g2 split, neg | 77 → 606 | 77.2% → **83.0%** |
| `nch2` g2 split, neg | 77 → 153 | 84.6% → **85.0%** |
| `ch2` g2 split, neg | 77 → 149 | 82.0% → **84.1%** |
| `arb` g2 split, pos | 77 → 606 | 65.0% → **69.4%** |
| `nch2` g2 split, pos | 77 → 153 | 75.1% → **76.1%** |
| `ch2` g2 split, pos | 77 → 149 | 67.2% → **70.3%** |
| `nch2` g3 split | 405 → 1,203 | 84.7% → **88.2%** |
| `arb` g3 split | 405 → 1,979 | 80.6% → **84.3%** |
| `ch2` g3 split | 404 → 1,209 | 81.9% → **85.8%** |
| **repository** | **1,886 → 7,043** | **81.3% → 85.4%** |

Every one of the twelve improves. The before-figures are comparable under either
keying, because a one-case-per-branch corpus has nothing to intersect and the
grouping flaw could not bite it.

**All fifteen families.** The three genus-3 split ones were extended by MERGING
rather than regenerating: a fresh search reaches 403 of 405 branches and the three it
misses are each covered by exactly one deployed case, so replacing their corpora
would have dropped branches. Merging keeps the deployed cases and adds the second
per branch that a search can find.

**Repository-wide, 81.3% to 85.4%** -- 12,728 invisible assignments of 67,931 down
to 9,884. The denominator is identical before and after, which is the check that the
comparison is like-for-like: it is per-branch, and the branches did not change.

The total moves less than the per-family figures because genus-3 split is 54,431 of
those 67,931 assignments, 80% of the whole, and those three families gain three to
four points where the smaller ones gain ten to fourteen. That is not a disappointment
to explain away -- they were already the best-covered families, at 80-85% where the
ramified ones sat at 80-87% on a twentieth of the code -- but it does mean the
per-family table is the honest presentation and the headline alone is not. Corpus 1,886 → 4,664,
and coverage ROSE, 1,925 → 1,928 of 1,929: three baseline exemptions died of progress,
`Precompute` leaves firing on 0.88% of curves that a corpus drawing hundreds across
four fields now reaches.

**`arb` carries its specialisations' cases as well as its own**, which is sound
because it is valid on every curve they are and the testers RECOMPUTE the expected
result rather than storing it — the ramified ones against Magma's Jacobian, the split
ones against the reference library — so an inherited case re-derives its own answer.
They are additive rather than replacing, and the reason is measured: nch2 only ever
presents `h = 0` and ch2 only `h` monic of degree `g`, so the union of the two
exercises neither non-monic `h` nor `deg h < g`, and **E11** is a defect of exactly
that class. What it buys is honestly small in detectability — `arb` g3 gains 0.4
points and `arb` g2 nothing — and real in curve shape: `arb` g3's own corpus held NO
`h = 0` case at all and now holds 96, on a family that must accept them.

**The acceptance test is E20's own mutation.** Dropping `t8` from `ADD33`'s `C0` is
**missed** by the committed 48-case corpus (48/48 matched) and **caught** by the new
96-case corpus (94 of 96). Branch coverage did not fall, and later rose to 1,928, and
`coverage_baseline.json` needed no edit, coverage being label-keyed. No formula file
is touched, and `opcount` is byte-identical across all fifteen families.

### Four defects the extension turned up, three of them in the tooling

Worth recording because each was invisible until something asked the tool to do a
thing it had never been asked before, and because two of them were caught by the
oracle the other one passed.

**The emitter could not produce a genus-2 split tester at all, and had not been able
to since PR12** (`ERRATA.md` **E21**). The weight was read from a fixed index, and
the two genuses use different reference libraries with different divisor shapes —
`<u, v, w, n>` at genus 2 against `<u, v, n>` at genus 3 — so that index is the
weight at one and the *cofactor* at the other. PR12 fixed this defect's mirror image
for genus 3 and created this one; nobody noticed because no genus-2 split tester was
ever regenerated afterwards. **A tool can lose a capability silently for as long as
nothing exercises it, and "the deployed artefacts are correct" says nothing about
whether the thing that produces them still works.**

**The tool could not target the posReduced basis** (**E22**), so three of fifteen
testers were unmaintainable by the tool maintaining the other twelve. A `--basis`
flag looks sufficient and is not: it routes the output side and leaves the generator
negReduced in four places. Built that way, every Python gate passed all three
posReduced testers and **Magma failed all three on assertions** — the sharpest
demonstration in this series that the two oracles are not redundant. And the
single-file fix is impossible rather than inelegant: Magma cannot `load` inside a
conditional, so a run-time basis switch cannot bring in the right formulas.

**My own instrument was understating the split families by five points.**
`detect.py` keyed each assignment by its position in the execution trace, and
`Precompute` has eight exits taking different numbers of assignments — so two cases
reaching one branch by different curve routes had every later index shifted, and
their blind sets were never intersected. The tell was in the output and nearly went
past me: the denominator ROSE with the case count, where per-branch scoring should
hold it fixed. Keyed by `(function, variable, occurrence)` instead, arb genus-2 split
is 82.2% where it had measured 78.5%.

**And a log collision that would have crossed the two bases.** `FileInfo.LOG` was not
basis-aware, so a posReduced run overwrote the negReduced log — and `--inherit-from`
reads those logs, so a negReduced `arb` could have been handed posReduced cases and
compared a different divisor. Caught by noticing a POS log where a NEG one belonged.

**Honest limits, and the first is a correction to my own record.** PR7+8's outcome
summary said the `ADD29`/`ADD33` saving was reverted and left it there, so the plan
for this work claimed it would be recovered. It had already been recovered, in
PR7+8 itself, once the exhaustive probe gave it an oracle. **This work therefore
recovers no operations**, and its case rests on detectability alone. Two things
follow: a summary that records a refusal must record its resolution, and the errata
entry — which did say so — was the reliable record where the summary was not.

The rest: the three genus-3 split families are still one case per branch, at 405
branches each with `Precompute` in the loop, and are regenerated separately. Their
committed logs are partial — rebuilding `nch2_splitG3` from its log reaches 86 of 405
— so they need real runs rather than re-selection. Everything that blocked the other
twelve is discharged: the six genus-2 generators have a budget, the emitter can emit
genus 2, and posReduced can be targeted.
And detectability will not reach 100%: `f7` is assigned and never read and is not
deletable, a branch guarded on `d = 0` must have `d = 0` to be reached, and the
adjugate entries are dead on the degenerate paths that never consume them. Measured,
those are exactly the names that survive every field.

**For the paper.** A test suite can reach every branch of a program and still be
unable to see a change to it, and the distinction is measurable rather than
rhetorical: perturb each computed value and ask whether the output moves. Applied to
formulas verified against an independent implementation of the group law, it found
that 18.7% of the arithmetic was unobserved — and that the cause was not sampling
luck but a selection rule preferring the smallest field, where degeneracies are
cheapest. The remedy is two cases per branch drawn from *different* fields, and the
non-obvious part is that two from the same field is worse than one from a bigger
one.

---

# Part VII — In flight

Decided and reasoned, not yet established. Listed so the paper does not claim
them early, and so each arrives here with its evidence when it lands.

| what | why it is not yet a result | owner |
|---|---|---|
| Apply the depression `x → x − f₆/7` to the genus-3 `nch2` formulas | Mathematics verified (Part I, and 310 transported additions); the formulas still take `f₆`. Until then our odd-characteristic counts sit on a curve form no published baseline uses | PR15/PR17 |
| ~~Characteristic-2 genus-3 formulas at `deg h = 3`~~ | **DONE.** Derived, Magma-verified against the Jacobian (1,777 additions and 2,223 doublings, 0 wrong), and gated. `33ADD` 51M 3S 62A 0C, `3DBL` 51M 4S 55A 2C. The reconciliation against Birkner's Type Ia and GKP's two variants is **for the paper, and is not tracked here** (decided 2026-08-24): nothing in the code or the tests depends on it, and `RELATED_WORK.md` already carries both normal forms and GKP's counts with citations | — |
| Exploit `h₃ ∈ {0,1}` rather than merely declaring it | The assumption is currently free to *count* but still computed. Whether real work can be removed is unmeasured, and the genus-2 mechanism that would be the template is not yet understood (N6) | PR24 |
| Implement the 27 confirmed efficiency findings | Report only so far; each must land with its own oracle run | PR16 |
| Non-ordinary characteristic-2 curves (`deg h < 3`) | **Researched and declined.** Real uses exist — halving, Koblitz curves — but a curve is ordinary with probability `1 − O(1/q)`, there is no parameterised middle option (one file covering all four strata must keep `f₅…f₃` live — `f₆` stays killable by the translation, unconditionally, per Part I step 2 — at which point it *is* the `arb` file), and the remaining prize is a doubling prize on the most saturated ground. The `arb` formulas serve these curves correctly today | — |

---

## Adding an entry

One entry per contribution, in the Part it belongs to, in the same commit as the
work. Keep the shape:

**Status** — established / established-and-fixed / report-only / in flight, with
the PR. **Where** — file and line, or the thesis location. **What was there.**
**What changed.** **Why it is right** — the argument, at the depth a referee
would want. **Evidence** — the measurement, with its numbers, and its honest
limits. **For the paper** — the one-sentence claim, and what makes it
interesting beyond the fix.

Two standing rules, both learned the hard way here:

- **Record refutations.** N11 contains one, N6 another. A hypothesis that was
  tested and failed is worth as much page space as one that held, because the
  alternative is that the next person re-runs the experiment.
- **State honest limits in the entry, not in a footnote.** E-T5 is not measured
  and says so; the doubling composite is approximate and says so.

## N33 — The adjugate is nearly free, and a discarded quotient is a Bezout cofactor

**Status** — established, C4. **Where** — `g3/splitModel/negReduced/g3Formulas/`,
all six `Deg3ADD` and `Deg3DBL` files; the published tables are
`Thesis/chapter6.tex` `tab:g3splitfcosts{ADD,DBL}`, corrected as `E-T10`.

**What was there.** Composing two degree-3 divisors needs `s = vt*q mod up`,
where `q = d/w mod up` is a quadratic whose coefficient vector is the first
column of the adjugate of the `3x3` matrix `T`. The split formulas built exactly
that column -- three `2x2` minors `m1`, `m4`, `m7` -- took the determinant by
expanding along `T`'s first row, and then reduced the product `vt*q` modulo `up`
using Karatsuba twice.

**The finding, and it is not the one the plan predicted.** Carrying the *whole*
adjugate and applying it as a matrix-vector product is `+1M -12A` on the generic
path of all six operations. The plan expected the extra multiplication to be paid
at the `T` block, on the reasoning that nine entries must cost more than three.
Measured, the block costs **`15M 0S 9A` either way**.

The reason is structural rather than a happy accident, and it is the part worth
publishing. Column 3 of `T` is `x` times column 2, reduced modulo `up`. `adj(T)`
is itself a multiplication matrix -- by `q`, up to `det(T)` -- so it inherits that
shift structure. Concretely, the bottom row `(m7, m8, m9)` is the cross product
of columns 1 and 2 of `T` and needs no third column at all, and the remaining six
entries are then **shifts of that row costing one multiplication each** instead
of a `2x2` minor costing two:

    m5 = m9 + w2*m8      m2 = -w0*m7      m1 = m5 + w1*m7
    m4 = m8 + w2*m7      m6 = m2 - w1*m8  m3 = -w0*m8

with `(w0, w1, w2)` the modulus coefficients. Three minors at `2M` and six shifts
at `1M` is `12M`, exactly what three minors at `2M` plus the three now-unneeded
`T` entries `t3`, `t6`, `t9` at `1M` used to cost. The nine-entry adjugate is
free relative to the three-entry column.

A further multiplication falls out of `t7*m3 = (-w0*t7)*m8 = t2*m8`, the signs
cancelling because `t2` and `m3` carry the same `-w0` factor. So the determinant
can be expanded along `T`'s first *column* reading `m8` in place of `m3`, and
`m3` is left wanted only by the generic path, which computes it there -- no
degenerate leaf pays for an entry it never reads.

**Where the cost actually moves.** Downstream. Applying the matrix is
`9M 6A` plus the three deferred entries at `3M 2A`, so `12M 8A`, against
Karatsuba's `11M 20A`. One multiplication on, twelve additions off, and no
reduction step because applying the multiplication matrix *is* the reduction.

**Measured, six sites, `+1M -12A` at every one:**

| | addition | doubling |
|---|---|---|
| arb | 65/3/87/12 -> **66/3/75/12** | 73/3/101/19 -> **74/3/89/19** |
| nch2 | 65/3/85/0 -> **66/3/73/0** | 72/4/97/0 -> **73/4/85/0** |
| ch2 | 65/3/80/0 -> **66/3/68/0** | 71/4/86/1 -> **72/4/74/1** |

`+6M -72A` in total, accepted comfortably by the thesis's own `1M : 3A` rule. No
other shape moved in any of the twelve families, which is the acceptance test:
the trade is confined to the generic path it targets.

**Scope, and why it is exactly six.** The `3x3` multiplication matrix exists only
when reducing modulo a degree-3 modulus, so the lower-degree additions and
doublings carry a smaller system with nothing to trade, and genus-2 split has no
such matrix at all -- `m7` occurs zero times in all six of its formula files.

**For the paper.** State the shift structure as the result, not the `+1M -12A`.
The operation count is an artefact of one model at one genus; the statement that
*the adjugate of a multiplication matrix inherits the shift structure of the
matrix, so all nine entries cost barely more than one column* is what transfers,
and it is what makes the matrix-vector form cheaper than forming the polynomial
and reducing.

### The refutation this replaced

The plan carried a hand count saying the conversion **loses `2M 1A`** at the
block and that the `+1M` is paid there. That count is wrong, and it was wrong in
a way no amount of re-reading would have caught: it priced the ramified route's
seven entries against split's three without noticing both arrangements spend the
same fifteen multiplications. `verification/adjugate.py` settles it by executing
both from their real `.mag` text -- `split_q_col1` at `15M 0S 9A` for four
entries, `split_q` at `15M 0S 9A` for seven -- and the pre-C4 route is kept as a
candidate rather than deleted so the comparison keeps scoring it.

**The methodological point, which this project keeps relearning:** state what a
change *removes*, and measure the total. A hand count of two arrangements is a
prediction, not a result, and here the prediction had the right bottom line for
the wrong reason. My own independent hand count also said `0M` before the
measurement said `+1M`.

### A related result, proved and deliberately not applied

The same leaf structure exposed that split spends `11M 6A` reconstructing a
Bezout cofactor it has already computed. The mathematics is settled -- `400 of
400` constructed trials against ground truth in the quotient ring -- and the
implementation is blocked on the file's normalisation of `b2`, so it is recorded
in `ERRATA.md` **E24** rather than applied. The general statement belongs here
because it outlives the leaf:

**Wherever an explicit formula computes a remainder `r = a mod b` and later needs
the Bezout cofactor of `b` modulo `a`, equivalently an inverse of `b` in
`F_q[x]/(a)`, the quotient discarded by that division already is that cofactor,
up to the scalar `lc(r)`.** One Euclidean step gives `t_1 = -q` in the extended
algorithm's recurrence `t_{i+1} = t_{i-1} - q_i*t_i`, and reducing
`s_1*a + t_1*b = r` modulo `a` gives `b^{-1} = t_1*r^{-1} (mod a)`. The cost of
the modular inverse collapses to the cost of inverting a leading coefficient.

The ramified model exploits this; the split model does not. The reason is
**inversion scheduling**, and that is the publishable observation: ramified
inverts early, so the monic-making scalar is exact and everything downstream is
unweighted, while split must invert late because its `f` is non-monic of degree
`2g+2` and `upp` needs normalising only after `upp` is known -- batching that
normalisation with weight removal is precisely how the split formulas hold to a
single inversion. Late inversion means every upstream quantity is carried
projectively, and a weighted cofactor is not a drop-in for an exact one. The
omission is a consequence of a deliberate design choice, not an oversight.

## N34 — One calling convention, and why a rename is safer than a reorder

**Status** — established, PR10. **Where** — the three genus-3 split additions, the six genus-2 split
additions, and the `Deg22ADD` name in both genus-3 models.

**What was there.** `Deg<i><j>ADD` names the degrees of its two input divisors, and the repository
disagreed with itself about what that meant. In genus-2 ramified, genus-2 split and (since PR36)
genus-3 ramified the digits were **positional**: the smaller-degree divisor arrived first. In genus-3
split they were merely **sorted**, and the larger arrived first. Separately, genus-2 split wrote each
operand's coefficients **ascending** where the other three families wrote them descending.

**Why the first of those is a correctness problem and not a style one.** A caller who reads the name
and passes operands in the genus-2 order gets a **silently wrong answer**, not an error, because the
arities happen to match. That is the same defect class that got the inherited
`*_use_for_odd_even.m` files dropped at import for carrying a reversed operand convention. The second
is genuinely cosmetic, but genus-2 split contradicted *itself*: `Deg2DBL(u1,u0,v1,v0,ccs)` and
`Deg2ADD(u0,u1,v0,v1,...)` sat in the same file.

**The convention now holds in all twelve families**: digits positional, smaller divisor first,
coefficients descending. Every `Deg12ADD` in the repository reads
`(u0, v0, up1, up0, vp1, vp0, ...)`, differing only in the curve-constant tail.

### Three kinds of edit, and they must not be conflated

This is the transferable part, because the three have different risk and different verification:

1. **A pure rename**, `Deg22ADD` -> `Deg2ADD`. No operand order to confuse, verifiable by
   copy-and-diff. It landed first and alone, so the risky diff stayed small.
2. **A prefix swap inside a function body**, `u <-> up` and `v <-> vp` with subscripts untouched --
   the prefix is the divisor identity, the subscript the coefficient index within it.
3. **An argument reorder at the call site**, with *no* renaming, because the caller's variables keep
   their meaning.

Conflating 2 and 3 corrupts the dispatcher; doing 2 without 3 produces a wrong answer with no compile
error. They are the same conceptual change and opposite textual ones.

### The swap is one pass with a lookup, not three passes through a sentinel

```python
TOK  = re.compile(r'(?<![A-Za-z0-9_])(up|vp|u|v)([0-9])(?![A-Za-z0-9_])')
SWAP = {"u": "up", "up": "u", "v": "vp", "vp": "v"}
new  = TOK.sub(lambda m: SWAP[m.group(1)] + m.group(2), body)
```

A sentinel (`up -> TMP`, `u -> up`, `TMP -> u`) is correct but its correctness rests on the sentinel
never colliding and on nobody reordering the passes later. `re.sub` with a callback replaces each
match independently and never rescans its own output, so `u0 -> up0` and `up0 -> u0` in the same pass
cannot interfere. **The hazard becomes structurally impossible rather than avoided by discipline.**

Two things about it that would each have produced a half-applied swap, which is the wrong-answer case:

- **`up|vp` must precede `u|v` in the alternation.** Python matches leftmost-first, not longest, so the
  other order matches the `u` of `up0`, fails the digit test, and skips the token entirely -- leaving
  every `up` untouched while every `u` swaps.
- **The substitution must be scoped to the target function bodies, not the file.** `up3` is not a
  divisor coefficient: it is a live scratch temporary in `Deg3ADD` holding `up2^2`. A file-wide pass
  would have renamed it to `u3`.

Both were established by measurement before the first edit, not discovered afterwards: the pattern was
run against all three files and shown to rewrite exactly thirteen token forms while leaving the other
fifty-two identifiers beginning `u` or `v` alone, `upp0`-`upp3`, `unp0`, `vpp0`-`vpp2`, `vh0`-`vh2`,
`vt0`-`vt2` and the bare `u`, `up`, `v`, `vp` among them.

### The acceptance test for a reorder is that nothing moves

**`opcount.py` identical per branch, per family, before and after** -- a reorder that changes a count
has changed behaviour. Measured identical across all 42 shapes in each genus-3 split family and every
shape in all six genus-2 split families. That gate did not exist when this work was first scheduled;
PR41 supplied it.

Two mechanical self-checks ran before any gate, and both are cheap enough to be worth habit: within
the swapped bodies the token counts must **exchange exactly** (`u` 543 <-> 597 and `v` 602 <-> 495 in
arb), and `git diff --stat` must show **equal insertions and deletions**, 1,106/1,106 for arb and
2,200/2,200 for the two specialisations. A partial swap fails both.

### The trap that cost two earlier PRs was absent, and that was checked rather than assumed

PR21 drifted 56 frozen cases and PR36 another 20, both because a rename touched debug label strings
that the corpus stores verbatim. Here `Deg22ADD` **never appears inside a label string**: genus-3 split
labels are numeric (`ADD000`..`ADD349`) and the genus-3 ramified labels were numbered in PR6, carrying
the prose name only in a trailing comment. `harvested_cases.json` holds 0 cases and
`coverage_baseline.json` no `Deg`-bearing labels. So no frozen-corpus substitution and no re-harvest.

### An honest limit

The plan named an `_OLD` same-session differential as the per-file acceptance test, the technique PR36
used. It was attempted in Python and abandoned after ten minutes without completing: interpreting nine
functions of a 10,000-line file at that volume is too slow, and the Magma form is its own piece of
tooling. What stands in for it, and I think adequately:

- **The frozen corpus is itself an old-versus-new comparison.** Those cases were extracted from runs of
  the *old* code and record both the returned divisor and the branch label reached; the new code
  reproduces every one exactly.
- **`driver --strict` agrees with `reference.py`** over 55,236 operations across every degree
  combination, so old and new agree with each other through an independent oracle.
- **The specific failure this edit risks -- a missed call site feeding old-order arguments to a
  reordered function -- is exactly what the corpus catches**, because its cases drive the dispatcher
  rather than the leaf functions.

Recorded rather than glossed, because "the plan said do X, we did Y" is the kind of substitution that
is invisible six months later.

## N35 — Five wrong repairs to published text, and what each one shows about evidence

**Status** — established-and-fixed, PR22. **Where** — `Thesis/chapter4.tex`, `chapter5.tex`,
`chapter6.tex`, `thesis.tex`, and `latexTables/split_ADD.tex`.

**What was there.** A set of defects found by reading the thesis: a coefficient named for the wrong
divisor, an unbalanced parenthesis, a dangling `=`, two malformed nested subscripts, an unbound
symbol in an algorithm, and the step-numbering drift the author reported.  Nothing in the repository
had ever checked a `.tex` file, which is how they survived.

**What changed.** The defects are corrected and the reconstructed build now agrees with the published
thesis page for page.  But the durable content of this entry is that **five of the repairs attempted
were wrong**, and each failed in a different and instructive way.  A sixth item, the notation pass the
PR was scoped for, was cancelled on measurement before any edit.

### The five, and what each one is evidence about

**1. A code idiom is evidence only from the function under discussion.** `\vh_1 = h_1 + v_1` was
disambiguated to `v_{21}`, the second divisor, citing `vh1 := h1 + vp1`.  That line is in
`Deg12ADD`, where the primed group is the degree-2 divisor.  The passage describes `Deg2ADD`, whose
unprimed group is first and which reads `t4 := h1 + v1`, so the answer is `v_{11}`.  The generalisation
across functions was never checked, and the reading it overrode was the one a reader would guess.

**2. A notation convention can track arity rather than the file.** Eight generated OUT rows were
double-primed because single primes "name the second input".  Those four blocks have no second input:
their `IN` rows read `D' = []` and the implementing functions take no primed parameter, so `up*` names
the *result* and the source returns it.  The edit made four self-consistent tables inconsistent, since
their bodies define only `u^{\prime}_*`.  Reverted.  The actual fault is a hardcoded
`$D + D' = D'' = $` label applied regardless of arity.

**3. Naming an unbound symbol can be the wrong half of a fix.** `alg:g3nucomp` bound `S` and then
tested and divided by an undefined `S'`.  Renaming the binding to `S'` makes the algorithm
well-formed and **wrong**: `kS` downstream must be the second gcd, because `k` is formed from the
undivided `u_1`.  The implementations settle it with the overwrite convention the published text
already had, and scale `k` by exactly that quantity at nine live sites.  The repair is `S' \to S` at
the test and the division, which is also the only version well defined on every path.

**4. A source-level count cannot see a counter reset.** Four prose citations reading `Step~0` were
shifted to `Step~1` because `algorithmic[1]` numbers from 1.  Three algorithms carry
`\setcounter{ALG@line}{-1}` and genuinely print `0`, in the frozen published source as well as here.
The published text was right.  Counting `\State` lines by hand reproduces the wrong answer perfectly,
which is why **the arbiter for a step reference is the rendered PDF, never the `.tex`**.

**5. A hypothesis can fit one case for the wrong reason.** The step drift was first blamed on
`\State Go to ...` escape lines, and 20 lines were edited.  It fitted `alg:g3explSPLIT3ADD` only
because that algorithm has three `\EndIf` **and** three escape lines.  The real cause is that
`algorithmic` numbers `\EndIf`.

**Why it is right.** The surviving corrections are decided by something stronger than reading in
every case where that was possible.  The `u_{n_1}`/`u_{n_0}` block is **proved**: each `align*` block
states a formula and then its factored form, and the factorisation holds only for the corrected
coefficient names, checked symbolically.  The two malformed subscripts are matched term for term
against `arb_splitG3_ADD.mag:10308-10310`.  The `\EndIf` cause is confirmed on **seven** step
references across two algorithms, every one landing when `\EndIf` is unnumbered and every one off by
exactly the count of `\EndIf` lines above it; one of the seven is off by two rather than three, which
is what rules out a constant offset from another cause.

**Evidence.** The build is the new instrument, and it did not exist before this series.  266 pages
against a published 267 whose first page is a repository cover sheet, so 266 against 266, with front
matter i to xiii, Chapter 1 on 14, Chapter 7 on 260, the bibliography on 263 and an identical 246-page
span from Chapter 1 to Chapter 7.  Extracted words 106,463 against 106,841, a 0.35% spread, and
`NUCOMP` 268 against 268.  Eighteen step citations were re-checked against the rendering across five
algorithms and all eighteen land.

**Honest limits.** No `.mag` file is touched, so no formula gate applies and none of this is backed by
execution; where a correction is "matched against code" that is a reading of the source.  Nothing in
the Magma constrains LaTeX numbering, so the `\EndIf` item has no code cross-check at all.  There is
**no** global claim that every step reference resolves: eighteen were checked and nothing outside them,
and three earlier attempts to automate that check were each wrong, in four distinct ways.  An
unbalanced `(` is legal in math mode, so the build is silent on that defect and it is not
gate-verifiable beyond "still compiles".

**For the paper.** Restoring the ability to build the thesis turned it into a checkable artifact for
the first time, and the immediate yield was not the defects it found but the **five wrong repairs it
caught before they were published** — each traceable to a specific, nameable failure of evidence:
generalising an idiom across functions, mistaking arity for convention, fixing the near half of a
two-ended defect, trusting a source count over a rendering, and accepting a hypothesis that fitted one
case by coincidence.

## N36 — A record that was wrong for years because nothing read it against what it described

**Status** — established, PR34. **Where** — `g2/timings/`, `g3/timings/`,
`verification/driver.py`, `verification/README.md`, `ERRATA.md` E7 and E25,
`Thesis/ERRATA.md` E-T15 and E-T16, `Thesis/chapter5.tex`, `Thesis/chapter6.tex`.

**What was there.** `g2/timings/` and `g3/timings/` hold copies of the genus-2 ramified,
genus-2 split and genus-3 split formulas, and the published timing figures were produced from
them.  A comment in `verification/driver.py`, duplicated in `verification/README.md` and
reserved as erratum E7, described them as a divergent generation in which "every body differs",
citing a different `ccs` layout, opposite signs on some terms, and a dependency the canonical
tree lacked.  On that basis the trees were excluded from every gate, and E7 was held open for
weeks as a live question about whether the published timings measured the formulas of record.

**What changed.** All three specific claims are false, and false the same way: **they compare
the genus-2 timings split files against `negReduced`.** That tree is `posReduced`, where
`ccs[2][3]` and `dw := v0+vp0-u0*f4-upp0*upp1` are byte-identical to it, and where
`nch2_splitG2_UTL.mag` — the "missing" dependency, which is in fact a stale doc comment rather
than a load — is shipped.  `ccs[1][3][1]` and the `+` signs are `negReduced`'s, which is the
*basis*, and a basis is supposed to differ in sign.

Two more: the scope sentence said "the split formulas" while the filter it justifies excludes
ramified files too, and "same function names" holds only at genus-2 split — genus-2 ramified has
zero overlap, every name `_RAM`-suffixed, and genus 3 differs by exactly PR10's `Deg22ADD`
rename, which this tree never received *because it is excluded from every gate*.

**And the polarity was backwards.** The timings trees are the **frozen 2020 original**; the
canonical tree is what moved, by dated post-publication improvements.  E7 called the frozen copy
the divergence.

**Why it is right.** The tell that would have caught it at any point is that the "missing"
filename appears in `posReduced`'s addition file as well as the timings one.  Beyond that: an
arithmetic operator census per shared function is identical in 22 of 24 genus-3 split additions
and 8 of 11 genus-2 split additions against `posReduced`, the survivors differing by single
operations; against `negReduced` **none** match and the up/down adjustment pairs are *swapped*,
which is what opposite adjustment senses look like.  Two other artifacts in the repository
already said `posReduced` was the genus-2 basis of record, so the file contradicted its own
siblings.

**Evidence, with its limits stated.** No differential was run under the gates, so the trees are
*indicated* to compute the same group law, not shown to; doing that needs an opt-in reach and an
adapter for the packed-tuple interface, deliberately left to separate work.  The census leaves
**14 of 82 functions uncovered** — 10 dispatchers, 3 `Precompute`s, 1 curve generator — and the
dispatchers are exactly where operand order and the equal-divisor route live.  A negative finding
on that evidence is tolerable where a positive claim would not be, and E7 says so.

**One difference no instrument could see.** The timings copy of `nch2_ramifiedG2_ADD` tests only
`dw21` where canonical tests `IsZero(dw20) and IsZero(dw21)`, so its return condition is *wider*:
on `dw21 = 0, dw20 ≠ 0` it returns the identity where canonical raises.  A silent wrong value
against a loud crash, neither correct.  **A widened `and` adds no operator, moves no count and
changes no fingerprint**, so every census, count and differential in this work is structurally
blind to it; it was found by reading the two guards side by side.

**A separate published erratum, found by recomputing rather than by reading.**
`chapter5.tex:2669-2671` said split arithmetic is "about 20% slower" than ramified at genus 2.
From the repository's own committed raw, addition runs 22% to 38% and doubling 28% to 53% over 4
to 1024 bits: "about 20%" holds at one cell of eighteen.  Doubling is worse than addition at nine
of ten field sizes, and addition's penalty peaks at 32 bits then falls monotonically — the
signature of a fixed overhead being amortised, which a constant percentage asserts the opposite
of.  Corrected to both ranges.  Also corrected: both chapters described the experiment as "series
of thousands" of operations where the schedule runs from 500,000 steps down to 45,000, five
trials each.

**For the paper.** The interesting result is not that E7 was wrong but *how it stayed wrong*: it
was a comparison against the wrong sibling, written into a code comment, which then justified
excluding the very files that would have exposed it.  The exclusion made the record unfalsifiable
and simultaneously froze the tree it described, which is why a two-year-old rename is the clearest
evidence of what the tree is.  **A record that justifies not looking at its subject cannot decay
gracefully.**  The companion finding is the opposite shape and equally cheap: a published
performance claim contradicted by data committed alongside it, which nobody had recomputed.

## N37 — Closing a "not proven impossible", and three defects that failed by being quiet

**Status** — established, PR44. **Where** — `ERRATA.md` E1 and E7,
`verification/e1_reachability.py`, `verification/driver.py`, `verification/curves.py`,
`verification/selftest.py`.

**What was there.** Two kinds of loose end, left deliberately and recorded rather than fixed.
`ERRATA.md` E1 described a guard too narrow to catch `dw21 = 0, dw20 != 0`, and said every observed
firing had `D1 = D2` but that reaching it with distinct divisors was "not proven impossible, only
never observed -- 13,008 differential operations found none".  And `E7` recorded three ways the
verification harness could test the wrong thing without saying so.

### The proof, and how cheap it turned out to be

The branch needs `d = 0` and `m3 = 0`.  All three genus-2 ramified addition files share the
prologue

```
m3 := up1 - u1;   m4 := u0 - up0;
m1 := m4 + up1*m3;   m2 := -up0*m3;
d  := m1*m4 - m2*m3;
```

so `m3 = 0` collapses it to `m1 = m4`, `m2 = 0`, hence `d = m4^2`, and `d = 0` forces `m4 = 0`.
`m3 = m4 = 0` **is** `u = up`.  Then validity of both divisors gives `u | (vp - v)(vp + v + h)`, and
the defect case is exactly `dw2 = (vp + v + h) mod u` being a nonzero constant -- a unit mod `u` --
so `u | (vp - v)`, and both being reduced of degree below 2 forces `vp = v`.  `u = up` with `v = vp`
is `D1 = D2`, intercepted by every dispatcher since PR5.

**Two lines of algebra and thirty seconds of enumeration closed a question that had stood since
PR3.**  `verification/e1_reachability.py` checks both steps rather than trusting either: every
`(u, up)` quadruple in the branch, and every ordered pair of distinct valid divisors sharing a `u`.
GF(3)/GF(5)/GF(7) gives 17,068 curves and 1,242,140 pairs; `--full` reaches 163,478 and 32,237,830.
Zero hits throughout.

**Worth saying plainly: the evidence was never the hard part.**  The entry already had 13,008 clean
differential operations, and adding three orders of magnitude to that would still have been a
sample.  What changed the status was noticing that `m3 = 0` makes the determinant a perfect square,
which is visible in five lines of the file and had been sitting there since the formulas were
written.

### Three defects that failed by being quiet

All three were **latent**, and the fix in each case is not to compute something different but to
**refuse rather than guess**:

| | it used to | it now |
|---|---|---|
| colliding family keys | keep the last file walked, so which family got tested depended on directory order | raise, naming both paths |
| an unrecognised split model | return `None`, which `curves.split_basis` treats as "neg", testing the family against the wrong reduced basis | raise at both ends, and validate before touching the curve so the error names the real fault |
| the long spelling `Coefficient(f, i)` | contribute nothing to `read_support`, silently widening the inferred domain | read it, with a lookbehind so `LeadingCoefficient(` is not mistaken for one |

**A correction to our own record.** The first was called "a real bug today" in `E7` and in the #43
pull request body.  It is not: the timings exclusion runs *before* the key is built, and no two
canonical files collide, so it cannot fire.  Latent, like the other two.

**And the section written to prove they fire had a silently skipped branch.**  The unknown-basis
check was guarded by `hasattr(f, "_replace")`, which is False because `Family` is a plain class, so
that third of the test never ran -- and the section still passed.  Found by removing the fix and
watching the *wrong* assertion fail.  It is the exact failure mode the section exists to catch,
reproduced inside the catcher.

**Why it is right.** Each guard was removed in turn and the section shown to fail naming its own
defect: the collision raise, the `Family.basis` raise, the `split_basis` raise, and the widened
pattern.  A gate never seen to fire is not known to be a gate, and that applies to the parts of a
gate as much as to the whole.

**Evidence.** `opcount.py --json` byte-identical, md5 `2a93ffaa1e39fcbbe2bb3a1abfc878ce`, so nothing
measured moved; `driver --strict` 13,746/13,746; whitebox PASS; dominance clean on 39 files;
selftest 19 sections to **20**.  No `.mag` file touched anywhere in this work.

**Honest limits.** The E1 enumeration is `nch2` only, where `dw2 = vp + v` needs no reduction; `arb`
and `ch2` carry the `h` terms and are not enumerated, though the argument turns only on `dw2` being
a unit and is unchanged.  E1 itself **stays open as latent**: the narrow guard is still there and
still divides by zero on a direct call to `Deg2ADD`.  What is settled is that nothing reaches it
through a dispatcher.

**For the paper.** Two things.  A reachability question left open as "never observed" is often
closed by an invariant already visible in the code -- here, that a `2x2` resultant with one entry
zero is a perfect square -- and the cost of looking is far below the cost of the sampling that
substitutes for it.  And a defect that makes a gate report the wrong *subject* is worse than one
that makes it fail, because the run stays green; the corresponding fix is never a better guess, it
is a refusal.

---

## N38 — The first projective formula, and the grading that makes a ladder possible

**Status** — established, PR46.  **Where** —
`g3/ramifiedModel/projective/g3Formulas/nch2_ramifiedG3_DBL.mag`,
`verification/projcheck.py`, `verification/driver.py`, `verification/selftest.py`,
`ERRATA.md` E23.

### The result

Weighted projective coordinates for the genus-3 ramified model, at

    wt(x) = 2,  wt(y) = 2g+1 = 7
    u_i = U_i/Z^(2(e-i))   for a monic u of degree e
    v_j = V_j/Z^(7-2j)     on every branch, independent of e
    f_i graded at 14 - 2i

with a single auxiliary coordinate `Z` and **no field inversion**.  The frequent-path
doubling measures **69M 11S 61A 3C 0I**, against **53M 5S 61A 0C 1I** affine, so removing
the inversion costs `16M 6S 3C` and the trade pays when `I > about 25M`.  Against
Fan-Wollinger-Gong's twenty-year-old inversion-free genus-3 doubling at **107M + 10S** on
the same curve family (`Fp`, `h = 0`, `f6 = 0`), that is **83 against 117**.

**Three properties, each measured rather than argued.**

**The grading is unique.**  An exact null-space solve over **Q** from the parsed AST, an
exhaustive structured search of 585,000 candidate weightings of which exactly 6 pass and
all 6 are integer multiples of the same vector, and 400,000 unstructured random vectors of
which 0 pass.

**It closes.**  The output is a valid input at the same exponents, so a ladder iterates in
one coordinate system.  Verified by feeding the output straight back in: 39 chained
doublings across five chains at depths 8,8,7,8,8, each step checked against
`reference.scalar_mul`, `Z` never reset.

**The `u` exponents shift with the output degree and the `v` exponents do not.**  The
coefficient of `x^i` in a monic `u` of degree `e` sits at `2(e-i)`, so a degree drop of `d`
lowers every `u` weight by `2d`; `v == y` on the support and `y`'s weight does not depend on
the divisor's degree, so `v_j` is at `7-2j` on every branch.  That asymmetry is what lets
the file keep the shipped bottom-aligned return shape -- slot `i` holds the coefficient of
`x^i`, monic 1 at slot `deg u` -- instead of inverting the convention every affine family
uses.

### Two things that are NOT what an earlier reading of this work said

**The curve coefficients arrive RAW.**  They are graded, and the carriage costs the 3C the
counter charges -- but the FORMULA carries them, in its own prologue
(`Z4 := Z2^2; f5 := f5*Z4; ...`).  A caller that pre-scales applies the carriage twice:
correct at `Z = 1` and wrong at `Z = 2, 3, 7, 50`, measured.  Notes written during the
derivation said a caller must "refresh `f5*Z^4` as `Z` changes", which has the cost right
and the interface backwards.

**Uniform single-`Z` is not a grading of this map at all.**  Equal weights force
`wt(x) = 0`, hence `wt(y) = 0`.  Under iteration the uniform pattern diverges,
`(1,1,1,1,1,1) -> (4,5,6,6,7,8) -> (10,14,18,15,19,23) -> unbounded`, so it must be
re-imposed after every squaring.  FWG's published system is uniform single-`Z`, and their
own conclusion nominated "generalized weighted projective coordinates" as the next step.
Built as a control and optimised hard -- monomial addition chains at their floor, global
CSE, `Z1,Z2` unified up front -- it still loses by 16 operations on the doubling.

### For the paper

The contribution is not "projective formulas for genus 3" -- those have existed since 2006.
It is that the *weighting* was never derived from the curve's own grading, that doing so
closes under iteration where the uniform scheme does not, and that a NUCOMP-derived affine
base converts without giving back its structure: the addition count is unchanged at 61A.

State the break-even honestly.  `I ~ 25M` is below FWG's own stated floor of "at least 30
additional multiplications", and the figure that matters is not the speed but the
calibration: a delay parameter set against 107M+10S overestimates its delay by about a
quarter.

### Limits, stated

Frequent path only, so the completeness property the affine formulas are known for is **not**
claimed here.  `opcount.py` skips the family for want of an ADD file, so the 69M figure rests
on two independent counters in the local research tree rather than on the counter of record.
And **nothing has run under real Magma** -- `ERRATA.md` E15 says a formula that cannot be run
under Magma is not verified against the sibling-path class, and that stands unmet.
