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
| — | [In flight](#part-vii--in-flight) | decided, not yet established |

---

# Part I — Normal forms

**The single most reusable result here, and the one a paper should lead with.**
Every formula file in this repository declares a curve shape in its banner, and
each declaration is a claim that an arbitrary curve can be brought to that shape
by an isomorphism — so restricting to it costs no generality. Six such
forms exist across two genera and three characteristic classes. **Five are
declared by a shipped ramified banner today, and only three of those
declarations are already the form derived here** — the genus-2 characteristic-2
banner still declares `h₂ ∈ {0,1}` with `f₂` live (PR27), the genus-3 `nch2`
banner still carries `f₆` (PR15/PR17), and the genus-3 characteristic-2 banner
does not exist yet (PR7/PR8). They were inherited piecemeal from different
sources, justified differently in each place, and one of them is wrong in the
published thesis (N3).

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
Reconciling the two forms explicitly, along with GKP's two variants, is
PR7/PR8's stated obligation and should appear in the paper as a comparison
rather than as a claim of priority.

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
`Deg1ADD` case 2, `Deg22ADD` 3.1/3.2; genus-2 split `ADD15/19/38/58` in both
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

**Two places the analogy is deliberately inexact**, recorded in the code rather
than smoothed over. `RandomG3NotChar2Curve` still draws `f₆`, because the
genus-3 formulas do not yet apply the depression — dropping it belongs with the
formula change, or the generator would again be testing a domain the formulas do
not claim. And `RandomG3Char2Curve` constructs both `f` *and* `h`
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
frequent case is **62 combined M+S, 3C, 77A** — 5 better than Nyukai and 8 better
than GKP on M+S, with 28 fewer additions. And against the thesis's own
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

---

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
| arb `Deg3ADD` generic | 60 | 4 | 95 | 12 | 1 | 64 |
| arb `Deg3DBL` typical | 56 | 5 | 114 | 16 | 1 | 61 |
| nch2 `Deg3ADD` generic | 59 | 4 | 77 | 3 | 1 | 63 |

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

---

# Part VII — In flight

Decided and reasoned, not yet established. Listed so the paper does not claim
them early, and so each arrives here with its evidence when it lands.

| what | why it is not yet a result | owner |
|---|---|---|
| Apply the depression `x → x − f₆/7` to the genus-3 `nch2` formulas | Mathematics verified (Part I, and 310 transported additions); the formulas still take `f₆`. Until then our odd-characteristic counts sit on a curve form no published baseline uses | PR15/PR17 |
| Characteristic-2 genus-3 formulas at `deg h = 3` | Normal form established (Part I). Formulas not derived. Must reconcile explicitly against Birkner's Type Ia and GKP's two variants, and beat GKP's 1I+62M+5S/100A | PR7/PR8 |
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
