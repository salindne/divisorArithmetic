# Errata

Known defects in this repository and in material published from it, with reproducers.

Most entries are still open, and that is deliberate: a fix waits until an oracle can see it.

That bar has now been met once. The two gaps that used to keep every entry frozen -- no tester
exercised these inputs, and nothing gated a regression -- were closed by the Python verification
framework (`verification/`, in CI since PR #3): its differential driver enumerates the `D1 = D2` region
no Magma tester reaches, and its frozen-case gate fails a pull request that regresses a formula. PR5
used that oracle to route `ADD(D, D)` to `DBL` in every dispatcher and to complete three short guards;
E1's status below reflects it. Everything else here remains recorded-not-fixed, each waiting on the
tooling its own entry names.

Historical note, kept because the reasoning shaped the series: the genus-2 ramified random testers
guard their addition with `if D1 ne D2 then`, so no Magma tester can ever demonstrate an `ADD(D, D)`
fix -- which is why the framework, not a tester rebuild, was the prerequisite. And Magma exits 0 on
`Runtime error in assert`, so it could never have gated this on exit status.

Each entry records what is wrong, how to reproduce it, and what it affects.

Entries are numbered E1, E2, … and referenced from commit messages and from
[README.md](README.md). **A number is never reused.** E7 is deliberately absent here: it is a divergent
generation of the formulas under `g2/timings/` and `g3/timings/`, and deciding what it means for the
published timing figures needs the operation counter run over both trees, so it is tracked with that work
rather than asserted early.

---

## E1: genus-2 ramified ADD: guard too narrow, evaluates `0⁻¹`

**Status: closed at the dispatcher (PR5), guard retained.** Every known firing of E1 has `D1 = D2` --
validity of both divisors gives `(vp − v)(v + vp + h) ≡ 0 (mod u)`, and when `dw2` is a nonzero constant
it is a unit mod `u`, forcing `vp = v` -- and the ADD dispatchers now route that case to `DBL` before any
`Deg*` branch runs. The narrow guard inside `Deg2ADD` is unchanged and still divides by zero if called
directly with these coefficients; `verification/selftest.py`'s errata section asserts both halves on
every run (the dispatcher returns the reference double, the direct call still raises). Whether any
`D1 ≠ D2` input can reach the guard is not proven impossible, only never observed -- 13,008 differential
operations found none -- so the entry stays, demoted from live to latent.

**Severity:** was correctness -- aborted with a Magma runtime error on reachable input. Now latent.

**Where:** all three genus-2 ramified addition formulas, in the `IsZero(m3)` branch of `Deg2ADD`:

| file | guard | inverse |
|---|---|---|
| [g2/ramifiedModel/g2Formulas/nch2_ramifiedG2_ADD.mag](g2/ramifiedModel/g2Formulas/nch2_ramifiedG2_ADD.mag) | 280 | 287 |
| [g2/ramifiedModel/g2Formulas/arb_ramifiedG2_ADD.mag](g2/ramifiedModel/g2Formulas/arb_ramifiedG2_ADD.mag) | 290 | 297 |
| [g2/ramifiedModel/g2Formulas/ch2_ramifiedG2_ADD.mag](g2/ramifiedModel/g2Formulas/ch2_ramifiedG2_ADD.mag) | 282 | 289 |

The guard is a conjunction:

```
if IsZero(dw20) and IsZero(dw21) then
    return 0,0,1,0,0,1;
end if;

b2 := dw21^-1;
```

When `dw21 = 0` but `dw20 ≠ 0` the guard does not fire and `dw21^-1` is evaluated as `0⁻¹`.

**Reproducer.** Over `GF(11)`, on `y² = x⁵ + x³ + 1` (so `h = 0`, the `nch2` case), take

```
u = x² + 1        v = 1        D1 = D2 = (u, v)
```

- `u` is irreducible over `GF(11)`: `-1 ≡ 10` is not a square mod 11 (squares are 1, 3, 4, 5, 9).
- `(u, v)` is a valid reduced divisor: `f - v(v+h) = x⁵ + x³ = x³(x² + 1)`, which `u` divides.
- With `v1 = vp1 = 0` and `v0 = vp0 = 1`: `dw21 = vp1 + v1 = 0`, `dw20 = vp0 + v0 = 2 ≠ 0`.

So the guard is skipped and `b2 := 0^-1` raises.

**Note the input has `D1 = D2`.** This is the genus-2 counterpart of a defect already known in the
genus-3 ramified formulas, where `ADD(D, D)` is silently wrong rather than loud. The testers never
reached it because they only ever compared distinct divisors. The eventual fix is expected to be the
same in both places: dispatch `D1 = D2` to the doubling formula.

**Affects:** the genus-2 ramified formulas as shipped, and the corresponding algorithm as printed in
the thesis, which carries the same guard.

---

## E2: genus-2 ramified ADD: one 6-valued return among 5-valued returns

**Status: FIXED (PR5).** The stray sixth value -- a balancing weight left over from the split-model
version of the branch -- is deleted from the `ADD05` return in all three files; the branch now returns
the 5-valued identity like every sibling. The three whitebox cases that were pinned for this in
`coverage_baseline.json` are unpinned, so ANY arity anomaly now fails the gate, and `selftest.py`'s
errata section asserts statically that no 6-valued return remains.

**Severity:** latent. Three constructed whitebox cases now reach it (case 16 of each genus-2 ramified whitebox tester, branch ADD05, that branch's only coverage); the Python gate pins them by identity and reports them on every run.

**Where:** the same branch as E1 in all three files. `return 0,0,1,0,0,1;` returns **six** values,
while every other return in those files returns five. The trailing `1` is a balancing weight belonging
to the split model, which the ramified model has no use for.

Harmless today only because nothing reaches that branch. Any caller that unpacks a fixed five values
will break on it, including the planned Python interpreter, which reads these files as its source of
truth.

---

## E3: generic timing scripts build the second divisor from the wrong source

**Severity:** correctness of published measurements.

**Where:** **all 20** generic timing drivers, at line 65 except
`generic/timings_{2,4,8}bit.mag` where it is line 64:

```
snD1 := Reduced_Basis(spD1,sf,snV);
snD2 := Reduced_Basis(spD1,sf,snV);    <-- spD1; should be spD2
```

(`generic/arbitrary/` carries an `sh` argument too, and the same defect.) The positive-reduced path a
few lines below is correct:

```
prDA := Fibonacci_Add_SPLIT_POS(spD1,spD2,sf,sh,spV,g,length);
```

**Consequence.** `snD1` and `snD2` are the same divisor. Every `Fibonacci_*_SPLIT_NEG` timing loop
therefore measured a chain seeded with `D + D` rather than with two independent random divisors, and
`spD2` is silently discarded on the negative-reduced side only. The positive-reduced numbers are
unaffected.

**Affects:** the published negative-reduced generic-genus timing figures. The positive-reduced figures
and all explicit-formula timings are unaffected.

---

## E4: `latexConverter.py` produces an empty second operand under Python 3

**Severity:** correctness of generated tables. Latent, because the script does not currently run.

**Where:** [latexTables/latexConverter.py](latexTables/latexConverter.py), lines 383-384 and the loop
at 397:

```python
d2Input = filter(lambda x: SECOND_INPUT in x, noConstInput)
d1Input = [x for x in noConstInput if x not in set(d2Input)]
```

Under Python 2, `filter` returned a list, so `set(d2Input)` was a snapshot and both operand lists came
out right. Under Python 3 `filter` is a lazy iterator: `set(d2Input)` consumes it, so

- nothing is excluded from `d1Input`, so every variable, primed and unprimed, lands in `D`;
- the loop at 397 iterates an already-exhausted iterator, so `D'` renders as `[]`.

Reproduced with the file's own variable naming:

```
py3:  D = [u1,u0,v1,v0,up1,up0,vp1,vp0]   D' = []
py2:  D = [u1,u0,v1,v0]                   D' = [up1,up0,vp1,vp0]
```

**Affects: 18 of the 26 committed ADD tables, if regenerated** — corrected 2026-08-10 from "every ADD
table". Measured: 26 ADD tables carry a `D'` row and 8 already show `D' = []` correctly, their sources
taking a single divisor (four each in `split_ADD.tex` and `test.tex`). Those 8 are still wrong for an
unrelated reason — they render `D` with undeclared `yn` names — so "already reproducing" is the wrong
conclusion about them.

**And the fault has a second effect, not previously recorded.** `set(d2Input)` is re-evaluated per
element, so element 0 *is* tested against the fully populated set and every later element against an
empty one. `D'` renders as `[]`, and `D` additionally keeps the primed names it should have excluded. No
committed signature begins with a primed name, so in practice `d1Input` came out as the whole input list.

The committed `.tex` are correct because they were generated under Python 2, where `filter` returned a
list, so the risk is regeneration rather than the current content.

---

## E5: malformed `//Constant` directives understate three additions

**Severity: downgraded 2026-08-10.** It was recorded as affecting published operation counts, and it did
— but only through `latexConverter.py`, which is no longer the counter of record. The operation counts are
now measured by [`verification/opcount.py`](verification/opcount.py), which **cannot have this defect**:
it parses each expression rather than string-matching declared names against source text, so a declared
name containing an operator has no way to swallow arithmetic.

Measured: of the nine names the corrected directive adds (`y2`, `d9`, `d10`, `dn5`–`dn10`), **zero appear
as a multiplicand anywhere in the file**, so the repair reclassifies no product and changes no count the
interpreter produces. The directive is repaired as hygiene; nothing of record moves.

**Where:** [g3/splitModel/negReduced/g3Formulas/nch2_splitG3_ADD.mag](g3/splitModel/negReduced/g3Formulas/nch2_splitG3_ADD.mag)
line **19** — corrected 2026-08-10 from "line 13", which is the line number in the
`timings/` copy, not in the file of record — duplicated verbatim in
[g3/timings/formulas/splitFormulas/nch2_splitG3_ADD.mag](g3/timings/formulas/splitFormulas/nch2_splitG3_ADD.mag)
at line 13. **Both directives were corrected on 2026-08-10**; what follows describes the defect and its
now-limited reach. Compared against the `arb` sibling's directive, which is well formed:

```
arb :  ...,y0,y1,y2,y3,y4,yn0,...,d8,d9,d10,d11,...,dn0,...,dn10
nch2:  ...,y0,y1,-yn2,y3,y4,yn0,...,d8,d1,d0,d11,...,dn0,...,dn4,f3,d6,d7,d8,d1,d0
```

Three separate problems in that one line:

1. `y2` is missing and a spurious `-yn2` sits in its place. The leading minus is not a valid identifier
   character, and the tokeniser lets it swallow subtraction signs in the expressions it then scans.
2. `d9` and `d10` are missing, replaced by repeats of `d1` and `d0`; `dn5` to `dn10` are absent entirely.
3. A trailing `f3,d6,d7,d8,d1,d0` repeats entries already declared.

[g3/splitModel/negReduced/g3Formulas/nch2_splitG3_DBL.mag](g3/splitModel/negReduced/g3Formulas/nch2_splitG3_DBL.mag)
line 12 has a milder version: `d4` and `d1` each appear twice.

**Measured effect:** three additions understated: `23ADD` by 1, `3ADD` by 2. Corrected totals
(M, S, A, C):

| formula | published | corrected |
|---|---|---|
| 23ADD | 224, 11, 329, 0 | 224, 11, **330**, 0 |
| 3ADD | 632, 47, 808, 0 | 632, 47, **810**, 0 |

No multiplication, squaring or constant-multiplication count changes.

**Affects:** the published genus-3 operation-count tables.

Note this is a distinct class of fault from the counting bugs in E6: here the *input annotation* is
malformed, not the counter.

---

## E6: three further `latexConverter.py` counting faults

**Severity:** correctness of generated tables. Recorded together; all three are in the counter itself.

1. **`MUL_TO_ADD` tests the wrong operand,** so the same multiplication is charged 1A or 1C depending
   on the order its operands happen to be written in.
2. **`//startIGNORE` is silently ineffective when the marker is on its own line,** so the
   polynomial-level reference code those blocks are meant to exclude is counted as if it were part of
   the formula.
3. **A missing `//Constant` directive miscounts silently** rather than raising, so a formula file that
   forgets the annotation yields plausible but wrong numbers.

**Affects:** the genus-2 and genus-3 operation-count tables. Repairing these belongs with repairing the
script, which also cannot currently run at all, its six live input paths are missing the `negReduced/`
component and every output call is commented out.

---

## E8: `Negate` returns a non-inverse at odd genus

**Severity:** latent, and total where it fires. `poly_balanced_arithmetic.mag`'s `Negate(D,f,h,Vpl)`
never returns a group inverse at genus 3.

The function branches on parity:

```magma
if g mod 2 eq 0 then
    return <u1,-v1 - (h mod u1),g-Degree(u1)-n1>;
end if;
if n1 gt -1 then
    return <u1,-v1-(h mod u1),g-Degree(u1)-n1-1>;      // odd genus
end if;
```

The even branch is right. The odd branch produces weight `g - deg(u) - n - 1`, which at genus 3 is two
less than the inverse's weight. The correct expression, and the one that agrees with the even branch, is
`2*Ceiling(g/2) - deg(u) - n`.

**Measured**, GF(4), a random genus-3 char-2 split curve, `Neutral(f,h) = <1,0,2>`:

| weight expression | `Add(D, Negate(D)) eq Neutral` |
|---|---|
| shipped, `g-deg(u)-n-1` | **0 of 30** — 21 wrong, 9 raised |
| `2*Ceiling(g/2)-deg(u)-n` | **30 of 30** |

The nine that raise do so because the result is not even a reduced divisor, so `Adjust` cannot repair it;
`Adjust` preserves the divisor class, and the class is already wrong.

**Affects:** nothing today. Grep finds no call site in the repository — only the comment at
`poly_balanced_arithmetic.mag:671`. It is a trap for the first caller, which is why it is recorded rather
than left to be rediscovered. Found while writing a class-targeted pair mode for the genus-3 split
whitebox generator, which needs an inverse and therefore carries its own local one.

**Not fixed here.** `poly_balanced_arithmetic.mag` is loaded by both deployed genus-3 testers and by
every genus-3 entry in `test_all.sh`; editing it to repair dead code is not worth putting those at risk
in a PR about the generators. A fix belongs with a test that exercises `Negate` at both parities.

---

## E9: `RandomDivisorRB` cannot be called

**Severity:** latent. `poly_balanced_arithmetic.mag`:

```magma
RandomDivisorRB:= function(f,h,d)
    adapted:= RandomDivisorAB(f,h,d);
    return ReducedBasis(adapted,f,h);
end function;
```

`RandomDivisorAB` takes **two** arguments. Calling `RandomDivisorRB` therefore raises
`Number of arguments (3) does not equal expected number of arguments (2)` — it has never worked. The
docstring above `RandomDivisorRB` advertises a degree parameter `d` that `RandomDivisorAB` does not
accept and never has.

A second, quieter problem: it returns `ReducedBasis`, the **positive** reduced basis, while living in
`negReduced/` where every formula file expects the negative one. So even repaired by dropping `d`, it
would hand back divisors in the wrong basis for its own directory.

**Affects:** nothing today; no call site, only the comment at `poly_balanced_arithmetic.mag:414`.
Recorded because a caller would hit two bugs, not one.

---

## E10: an empty token in a `//Constant:` list corrupts every count, silently

**Severity:** correctness of generated tables; same family as E5/E6 but a distinct mechanism.

`latexConverter.py` parses the directive list as `line.split()[1].split(',')`, so a space after a
comma or a trailing comma yields an empty-string token. An empty string enters the classified
variable set, `startswith('')` is true at every position, and — measured on synthetic input — **every
multiplication in the file is then charged 1C** regardless of its operands:

```
//Constant: f1,f2     ('z','=','a','*','a')        (1,0,0,0)   correct, 1M
//Constant: f1, f2    ('z','=','a','*','','a','')  (0,0,0,1)   1C — silently wrong
```

**The "no committed directive contains an empty token" claim was wrong, and is corrected here
(2026-08-10). Eleven lines across six files parse as a directive with an empty token**, because
`__setupCode` calls `line.strip()` *before* testing the trigger, so an indented comment matches:

```
    //Ignore w, just need to work in my polynomial algorithms
                 -> split()[1] = 'w,'  ->  ['w', '']
```

In `g2/splitModel/{neg,pos}Reduced/reduced_basis_arithmetic.mag` (:1843, :1920), the
`g3/splitModel/negReduced/` and `generic/arbitrary/` copies (:1793, :1870),
`whitebox/genFiles/reduced_basis_arithmetic.mag` (:1921, :1998), and
`g3/ramifiedModel/ramifiedUtilities.mag:309`.

These reach the **`//Ignore`** path rather than `//Constant`, so the corruption is the opposite of the one
above: an ignored name costs nothing, so every multiplication becomes **free** instead of 1C. They are
latent only because the converter's driver never opens those files.

**A separate fault with the same symptom, recorded 2026-08-10.** The token-consumption loop makes no
progress when *no* term matches the head of the string, not only on an empty term — so a character
outside `OPERANDS` hangs it just as surely. `g3/timings/formulas/previousBest/rad_2019.mag` hangs the
converter today, using Magma sequences, tuples and coercion (`[ ] < > ! ,` and bare `/`) that the tool
never supported. So the hang is reachable by two doors and one is already open.

**Affects:** any future operation-count row generated from a malformed directive. Belongs to PR9's
repair list with E4–E6: the parser should reject empty tokens loudly.

---

## E11: genus-2 arbitrary doubling squares `h2` where it should not

**Severity:** correctness, but **only outside the declared domain**. The formulas declare
`h2 in {0,1}`, and on that domain `h2^2 = h2`, so nothing they claim is wrong. What is wrong is that the
restriction is doing work nobody intended it to do.

**Where:** [g2/ramifiedModel/g2Formulas/arb_ramifiedG2_DBL.mag:189](g2/ramifiedModel/g2Formulas/arb_ramifiedG2_DBL.mag),
in the `IsZero(sp1)` branch that returns a degree-1 divisor (labelled `DBL4`):

```magma
t1   := s0*(u1 - upp0) - h2^2*upp0 + vh1;
vpp0 := upp0*t1 - vh0 - s0*u0;
```

The outer `upp0*t1` supplies a second factor of `upp0`, so the `h2` term contributes `h2^2 * upp0^2`.

**What it should be.** Reducing modulo the monic linear `upp = x + upp0` is evaluation at
`x = -upp0`, and `v'' = -(h + v')` there. With `v' = v + s0*u`:

```
h + v' = (h2 + s0)x^2 + (h1 + v1 + s0*u1)x + (h0 + v0 + s0*u0)
v''    = -(h2 + s0)*upp0^2 + (vh1 + s0*u1)*upp0 - vh0 - s0*u0
```

so the coefficient of `upp0^2` is `h2 + s0`, giving `h2 * upp0^2` and not `h2^2 * upp0^2`. The single
symbol `h2^2` should read `h2`.

**Reproducer, and it separates three candidates.** 3,600 degree-2 doublings per variant over
GF(9), GF(25), GF(27) and GF(49), compared against `verification/reference.py`, with the domain
restriction lifted by setting `driver.banner_members` to `{}`:

| `t1` reads | on-domain | off-domain |
|---|---|---|
| `- h2^2*upp0` — as shipped | 0 wrong | **166 wrong** |
| `- h2*upp0` — **the derivation** | **0 wrong** | **0 wrong** |
| `- h2*upp0^2` | **136 wrong** | 150 wrong |

The third row matters: it is the substitution an earlier investigation tried and recorded as refuted. It
breaks the formulas **on** their declared domain, so it could never have been a candidate — the outer
multiply already supplies the second `upp0`. That refutation was sound about the substitution and
misleading about the conclusion, and it is what made this look like a mystery rather than a transcription
slip.

**Affects:** nothing published. It costs nothing either — `h2` is declared `//Ignore:` in this file, and
`h2^2` is a product of two curve constants, precomputable once per curve, so `h2` versus `h2^2` changes no
operation count. The one-symbol correction restores full generality in `h2` for free.

**Not fixed here** — recorded with its reproducer, per the standing rule that a formula edit waits for
the PR that can gate it.

**And the wider conclusion, which is why this was worth chasing.** The `h2 in {0,1}` declaration was
suspected of being *exploited* — of buying something that a genus-3 analogue could copy. It is not: it is
masking a transcription artifact. There is no template. Genus 3 needs no such assumption at all, being
already correct with `h3` unrestricted: 0 wrong in 1,333 operations off-domain, and no `h3` power occurs
anywhere in either arb genus-3 file.

---

## E12: the random testers print a green summary when they executed nothing

**Found 2026-08-11**, while verifying a formula change under real Magma. The run was launched from the
repository root instead of `g3/ramifiedModel/`, so every `load` failed, and the tester printed:

```
User error: Identifier 'RandomG3Curve' has not been declared or assigned
///////////////////////////////////////////////////////////////////////
TEST_ADD:  true
TEST_DBL:  true
// No errors.
Total time: 0.469 seconds
```

**That is an affirmative pass report from a run that compared nothing.** Two independent causes:

1. **`TEST_ADD` and `TEST_DBL` are configuration switches, not results.** They are set `true` at
   `arb_ramifiedG3_random.mag:35-36` to select which operations to exercise, and echoed verbatim at
   `:199-200`. Nothing ever assigns them again. So `TEST_ADD: true` reads as a verdict and is in fact a
   restatement of the input. The actual verdict is `errorFlag`, declared at `:49`.
2. **`No errors` is true by vacuity.** `errorFlag` starts `false` and is only ever set `true` by a
   mismatch inside the trial loop, so a run whose loop body never executes reports no errors correctly
   and uselessly.

**Scope, measured across all 16 `*_random.mag` testers:** the misleading echo is confined to the two
genus-3 ramified files (the imported ones) — the other fourteen print only the `errorFlag` verdict. But
**not one of the sixteen reports how many comparisons it performed**, so in every family a run that did
nothing is indistinguishable from a run that verified everything, except by reading the per-trial
progress lines *above* the summary.

**Affects:** any verification claim resting on a tester's summary rather than on its trial output. In
this instance the tells were the runtime — 0.469s against the 107–227s a real run takes — and the error
text, both of which the summary actively contradicted. A correct run of the same tester reports
`Trial # 10 over FF(16)` lines and takes about two minutes.

**Relation to the existing gate findings.** `test_all.sh` cannot gate on exit status because Magma exits
0 on `Assertion failed`, which is why it parses stdout instead. E12 is the next layer down: the stdout it
parses is itself green in the vacuous case. Both are the same class — a signal that reports success
because nothing contradicted it.

**Not fixed here.** The fix wants a comparison counter printed by every tester and asserted non-zero,
which touches all sixteen files plus `test_all.sh`'s parser, and belongs with the tester rework (PR6)
rather than inside a formula PR. Recorded with its reproducer: run any tester from the repository root
instead of its own directory.

---

**FIXED 2026-08-23 (PR6).** Each of the fourteen canonical random testers now counts
its comparisons and asserts the count is non-zero:

    printf "\n// Comparisons: %o", nCmp;
    assert nCmp gt 0;

The counter increments at every `:= ADD(...)` / `:= DBL(...)` call site, so it measures
work actually done rather than trials attempted. `assert` was chosen over a printed
warning because `test_all.sh` already greps `Runtime error|Assertion failed`, so an
empty run becomes fatal with no change to the parser.

**Demonstrated by reproducing the original discovery.** Run from the wrong directory,
so every `load` fails, a tester used to print `TEST_ADD: true` / `TEST_DBL: true` /
`// No errors.` in 0.469s. It now prints `// Comparisons: 0` followed by
`Runtime error in assert: Assertion failed`. A healthy run reports a real figure --
57,719 for the genus-2 arbitrary ramified tester.

**Also removed:** the two genus-3 ramified testers echoed `TEST_ADD: ` and
`TEST_DBL: ` with their values. Those are *configuration switches*, and printing them
beside a verdict is what made a vacuous run look verified. The remaining twelve never
printed them.

**The two testers under `g2/timings/` are deliberately untouched**, consistent with
every other gate in the repository: that tree is the E7 divergent generation and is
excluded from `driver.py`, `dominance.py` and the operation counters. Sixteen files
carry the defect; fourteen are of record.

## E13: the interpreter charges C as M when the coefficient is inside a subexpression

**Found 2026-08-11** while implementing the genus-3 arbitrary efficiency findings, by two
independent measurements disagreeing with a hand count. Affects
`verification/maginterp.py`, which is **the counter of record** since PR35 — so this is the
same class as E4–E6 and E10, but in the tool that replaced the one those describe.

**The mechanism.** `maginterp._leafname` (`:75-85`) resolves a factor to a name only when
the node is a bare `var`, seeing through unary minus and nothing else:

```python
while node[0] == "neg":
    node = node[1]
return node[1] if node[0] == "var" else None
```

A product whose factor is any **composite expression over curve constants** therefore
matches neither `CONSTS` nor `IGNORED` and is charged a full `M`, even though it is a
multiplication by a quantity fixed once per curve — a `C` under the thesis's own
definition (`chapter6.tex`, Field Operation Costs). Two shapes occur:

| shape | example | charged | honest |
|---|---|---|---|
| integer multiple of a coefficient | `2*f6*u1_0`, `5*f5*t01` | M | C |
| parenthesised sum of coefficients | `(h3 + h2)*(v1_2 + v1_1)` | M | C |

**Scope, measured across every formula file** (excluding the `timings/` and `whitebox/`
trees): **six live sites, all in `g3/ramifiedModel/g3Formulas/arb_ramifiedG3_DBL.mag`.**
The parenthesised-sum shape has **zero** live sites — PR16 removed the last one. So the
genus-2 families, both split models and the genus-3 split families are unaffected, and no
*published* operation count is wrong: the genus-3 ramified counts were deferred in the
thesis and appear only in this repository's own documents.

| site | function / branch | products |
|---|---|---|
| `:116` | `Deg1DBL`, typical | `4*f4*u1_0`, `5*f5*t01`, `6*f6*t02` |
| `:656` | `Deg3DBL`, **typical** | `2*f6*u1_0` |
| `:536` | `Deg3DBL`, `dw1 = 0` branch | `2*f6*u1_0` |
| `:587` | `Deg3DBL`, CASE #2.1 | `2*f6*u1_0` |

**Consequence for the figures this repository quotes.** The M/C split is wrong on two
frequent cases; the total multiplicative work is right in both:

| | as counted | honest split | total |
|---|---|---|---|
| `Deg3DBL` typical | 57M 4S 92A 3C | **56M 4S 92A 4C** | 64, unchanged |
| `Deg1DBL` typical | 9M 2S 21A 4C | **6M 2S 21A 7C** | 21, unchanged |

`Deg3ADD` is unaffected. `RELATED_WORK.md` and `EFFICIENCY_ARB_G3.md` state the counted
figures with this entry cited, rather than silently substituting the honest ones, because
every other figure in those documents comes from the same tool and mixing conventions
inside one table is worse than a documented offset.

**Why it mattered beyond the split.** It produced a change that had to be abandoned.
Horner-nesting `Deg1DBL`'s `k0` (ledger item ARBDBL-09) *measured* a clean −1S, because
the counter charged the old form's three constant products and the new form's three
general products identically. Honestly the rewrite is **+3M −3C −1S** — it buys three
general multiplications with one squaring and three constant multiplies, the wrong
direction under the 1M:3A rule. The finding was implemented, measured, verified for
correctness, and then dropped once the classification was done by hand. **A verified
measurement is not a verified improvement.**

**Not fixed.** Teaching `_leafname` to fold constant subexpressions reclassifies M as C in
counts this project has already published elsewhere, so it falls under the standing
adjudication rule — presume the published figure correct, hand-count each moved cell, and
decide per cell. That is its own change with its own gate, not a one-line patch. Recorded
here so the register carries it rather than only a findings report.

---

## Not defects

**The reverse is exploitable, found 2026-08-23.** Because the blind spot is about the operand being a
bare NAME, restructuring to keep it bare recovers the honest column. `Deg1DBL` wanted
`t1*(2*f4)`: written `t10 := f4 + f4; t1*t10` the multiplicand is a temporary and the product is
charged **1M**, while `t10 := t1*f4; t10 + t10` computes the same value with `f4` bare and is charged
**1C** -- identical additions, one multiplication moved to the cheaper column by multiplying first and
doubling second. First instance in this repository of working around this erratum in the formulas
rather than waiting for the counter to be fixed, and worth knowing wherever an `i*f_i` derivative
coefficient meets a runtime value.

## E14: the inline `// Nm Ns Na` ledger comments are gate input, and nothing says so

**Found 2026-08-21** by deleting one during a comment-tidying pass and watching `selftest`
turn red two edits later.

`verification/adjugate.py` prices three of its twelve candidate adjugate programs against
**the operation-count comments in the formula files themselves** — `// top: 16m 0s 9a`,
`// 11m 0s 8a`, `// total: 27m 0s 17a (equivalent 98a)` — parsed by `_ANNOT` and keyed by
label. `selftest`'s `adjugate` section then requires that all four such comments across the
`.mag` files be reproduced. Remove one and the section fails with

    arb_ramifiedG3_ADD.mag no longer carries its `top` op-count comment,
    so shipped_7 is measured against nothing

which is the correct behaviour, but only because someone wrote that check. The comments carry
no marker distinguishing them from ordinary annotation, and they sit in the middle of a
straight-line block that invites tidying.

**Two other comment classes in these files are already documented as load-bearing** — the
`if (ADD_DEBUG) then "..."` branch labels, which `whitebox` uses as its coverage denominator
and `harvested_cases.json` stores verbatim, and the `//Constant:` / `//Ignore:` directives,
which decide the C column (E10). This is the third class and the only undocumented one.

**Not fixed, because the fix is a convention rather than a patch.** Options considered: mark
them (`//gate: top: 16m 0s 9a`), which invalidates `_ANNOT` and every existing comment; or move
the expected figures into `adjugate.py`, which loses the property that the measurement lives
beside the code it measures. Recorded here so the next tidying pass knows. Note the standing
rule that if an annotated block moves, the number is **re-measured** rather than carried across
— which is what was done when this one was restored: 16m 0s 9a and 11m 0s 8a, unchanged.

**The failure mode was worse than "the check goes red", and that half IS fixed (2026-08-22).**
On the third deletion the section did not report a missing comment at all — it reported a
*difference*:

    the .mag fragment for shipped_7_dbl: measured [16, 0, 9] against the file's own [4, 0, 4]

`all_annotations` keyed the unlabelled comment as "the first unlabelled ledger anywhere after the
file's cofactor block". With the genuine one deleted, the next unlabelled ledger **217 lines
downstream** — `// 4m 0s 4a`, which prices the `r = u mod s` block of a different branch — was
silently promoted into its place. So the gate compared a correct 16m 0s 9a fragment against an
unrelated annotation and reported the *code* as wrong. A deletion has to read as a deletion.

Two instruments were tried and rejected before the right one was found, and both rejections are
informative. A **fixed line window** fails because the genuine ledger sits 28 lines below
`block_end_line` in the doubling and **575** lines below it in the addition, so no window admits
both. "Must precede the first guard" fails for the same reason. What separates them is that the
*addition labels its ledgers* — its cofactor fragment is `top:`, so its first unlabelled ledger is
unambiguously the lower half, wherever it sits — while the *doubling labels none*, so its single
unlabelled ledger must be pinned to the code. `all_annotations` is now conditioned on exactly
that: a file that labels has already said which is which; a file that does not must put its ledger
within three lines of the determinant. Both deletions now leave the key **absent**, verified by
deleting each in turn and confirming neither borrows a neighbour.

**What is still not fixed is the original complaint:** nothing in the `.mag` files marks these
comments as gate input, so the next tidying pass has no warning. Three deletions in three days.

## E17: a scratch assignment onto a live matrix slot, which no static check can see

**Found 2026-08-22**, twice in two days, in `arb_ramifiedG3_DBL.mag`'s `Deg3DBL`.

Per PR21's convention `t1`–`t9` are reserved for the 3×3 matrix `T`'s entries and `m1`–`m9` for
its adjugate, with `t01`–`t09` as generic scratch. The degenerate leaves of `Deg3DBL` violate it:
they reuse `t2`, `t3`, `t5`, `t6`, `t8`, `t9` as scratch for a local `k` computation. Six of those
are harmless, because each is assigned and then read within the leaf. The seventh was not:

    t7 := vh2 + v2 - h3*u2;    // T's (3,1) entry, the deg-2 coefficient of (2v+h) mod u
    ...
    t7 := f6*u1;               // scratch, inside the IsZero(m7) leaf
    ...
    b1 := t7^-1;               // wants the T entry, gets f6*u1

so `b1` was `1/(f6*u1)`, and the branch died outright with `Illegal negative power of zero
element` whenever `f6` or `u1` was zero. The second instance was the same shape one level up: a
saved copy `ty := u1` was removed as redundant, leaving `u0 := u1 - u1*dm0` reading the `u1`
assigned on the line immediately above, where the exact division needs the value from before it —
**105 of 116 wrong** in the one-ramified-point class.

**No static check in this repository can see either.** `dominance.py` asks whether the name is
assigned above the read: it is — twice. The name is
live, in scope, and holds the wrong value, which is a class strictly harder than E15's
sibling-path reads. `verification/blockcheck.py` caught both, because it executes the polynomial
reference block against the explicit code and compares; real Magma caught the first as a runtime
error. Neither `driver --strict` nor `whitebox` caught the first, the syntax being valid and the
interpreter never reaching that leaf on the sampled inputs.

**Not fixed as a checker**, because the check needed is value-level, not name-level, and that is
what `blockcheck` already is. Recorded as a rule instead: **before reusing a `t`/`m` slot as
scratch, enumerate its reads below the insertion point on every path.** The cheap structural fix
is to honour PR21's convention and take a `t0x` slot, which is what was done here.

**Fourth instance, 2026-08-23, and it arrived from the opposite direction -- collapsing a copy rather
than adding a scratch.** Specialising the doubling to `f6 = 0` turned `t3 := t2 - f6*u2` into the pure
rename `t3 := t2`. Removing it and reading `t2` directly is obviously free, and obviously wrong: `t2`
is reassigned (`t2 := s1*q0`) between that point and the later read in `M20`, so the frequent path
read `s1*q0` where it wanted `u2^2` -- **106 wrong of 120** in the generic class, clean in every
other. The rule therefore generalises: **a copy is safe to collapse only if its SOURCE is intact at
every read of the copy.** That is a liveness question about the source, not the copy, and it is
exactly the direction the eye does not check. Two fixes remove the clobber rather than working around
it -- rename the intervening scratch, or inline `s1*q0` so nothing is overwritten at all; the second
is better, one name fewer at the same cost.

## E18: `opcount.py` answers a parse failure by omitting the row, not by failing

**Found 2026-08-22**, when a missing comma (`return 0, 1, upp1, upp0, 0 vpp1, vpp0;`) reached the
tree during an edit.

`python3 verification/opcount.py --family ramified/g3/arb` printed its `1DBL` and `2DBL` rows and
simply **did not print `3DBL`**. No error, no warning, exit status unchanged. A reader checking
"did my edit move the count" sees the rows that did not move and can easily miss the row that
vanished — the same shape as `test_all.sh` being unable to fail and as E12's green summary over an
empty run, and the reason this project's standing rule is that silence is not success.

`blockcheck` reported the real problem immediately and by name (`User error: bad syntax`), and
`dominance.py` passed, being a line scanner. **Not fixed:** the honest repair is for `opcount` to
know which functions it *expected* to price and fail on any it could not, which means giving it a
per-family manifest. Recorded so that a disappearing row is read as the error it is.

**Fired again 2026-08-23, and the second time is more instructive.** During PR6's cleanup
`arb_ramifiedG3_DBL.mag`'s `Deg3DBL` lost a semicolon --
`vpp0:= vh0 - s1*(s0*u0) - upp0*t3` -- and `opcount --family ramified/g3/arb` printed

    1DBL   7M  1S  24A  4C  1I
    2DBL  28M  4S  70A  9C  1I

and stopped. Two plausible rows, no third, exit 0. The danger is not that the tool is silent; it is
that **the output looks like a successful measurement of a smaller file.** A reader checking "did my
edit move the counts" sees two rows that did not move and can reasonably conclude nothing did. Magma,
handed the file directly, gave the line and column in under a second.

So the rule is better stated positively than as a caveat: **the number of rows is part of the
measurement.** Nine shapes are expected of a genus-3 ramified family; eight means the run failed.
Until `opcount` asserts that itself, it is the reader's job.

## E15: no static check sees a read whose only assignment is on another path

**Found 2026-08-21**, by four separate mid-edit breakages in one day, three of which the static
checks passed and real Magma caught.

The first checker written for this asked, per function, whether a name is assigned **anywhere**
in the body. That question is satisfied by an assignment *below* the read, which is exactly what a
half-finished rename leaves: a variable inlined at one site, its definition deleted, and a
surviving read further up now resolving to a definition that has not run. Two of the day's
breakages had that shape and it reported both files clean. **It is deliberately not committed**,
because `dominance.py` below answers a strictly stronger question and reporting both would be two
tools for one job.

`verification/dominance.py` is added here and asks the ordered question instead: walking each body
top to bottom, does every read have an assignment **above** it? That subsumes the weaker check --
a name never assigned at all is reported too, verified directly -- so it is the only one shipped.
Clean across all 36 formula files (0 reports) and shown to fire — deleting one live `k3:= f6 - u2;` from `arb_ramifiedG3_ADD.mag`
produces 23 reports and exit 1.

**What remains uncovered, stated because the gap is the point.** Statement order is not
dominance. An assignment inside an `if` block above the read counts as reaching it, so a value
defined only on a **sibling path** still passes. That was the fourth breakage: a dropped
`w3:= d*w2;` in `arb_ramifiedG3_ADD.mag`'s typical case, where `w3` is assigned five times
earlier in the function on paths that cannot reach the read. `dominance.py`
passes, `driver --strict` passed **7,248 of 7,248** because its interpreter never reached the
line, and only Magma refused the file. Closing it needs the branch structure, and the guards
nest six deep with `end if;//name` closers a line scanner cannot match reliably.

**So the honest statement of gate coverage for this defect class is:** `dominance.py` catches
assigned-nowhere *and* assigned-below, and **only real Magma catches assigned-on-another-path.** A formula edit that cannot be run under Magma is not verified
against this class.

## E19: a sentence in a banner could redefine the tested domain

**Found 2026-08-23** while writing the genus-3 characteristic-2 banners, by the harness reporting a
domain nobody had declared.

`driver.banner_members` reads a file's own banner to learn which curve coefficients are pinned, and
PR29 taught it the singleton form the char-2 normal form needs -- `h2 = 1`, not `h2 in {0,1}`. The
pattern it used, `\b([fh])(\d+)\s*=\s*(\d+)\b`, was applied to **every comment line in the banner
region**, so it could not distinguish a declaration from a sentence that happened to mention a
coefficient and a value.

**The reproducer is the banner this was found in.** A genus-3 ch2 header declaring the domain
correctly:

    //   h(x) = x^3 + h2*x^2 + h1*x + h0 (deg h = 3, h3 = 1)

and then *explaining* it two lines later:

    //   the y-shift that clears f5 does so through a2*h3, so at h3 = 0 the f
    //   reduction fails as well

yields `members[('h',3)] = {0,1}` -- the union of the declaration and the prose. `curve_in_domain`
then treats `h3 = 0` as permitted and generates `deg h < 3` curves, which is **exactly the family
those formulas do not cover** and which the declaration exists to exclude.

**The genus-3 odd-characteristic files have the same shape and were harmless by luck.** Both
`nch2_ramifiedG3_ADD.mag` and `nch2_ramifiedG3_DBL.mag` explain the depression as "the translation
`x -> x - f6/7` gives `f6 = 0`", which parsed as `members[('f',6)] = {0}`. That is a *pin*, so
`family_domain` **discarded 6 from the contrast-derived constraint** and then re-imposed it through
the members channel. The two effects cancelled and `f6` came out zero either way -- but only because
the sentence happened to state the truth. Measured before the fix: the contrast said
`{'f': {6}}`, the banner reduced it to `{'f': set()}`, and 240 generated curves still had `f6 = 0`
because the members pin replaced the constraint it had removed.

**Class.** Same family as E14 (an inline ledger comment read as gate input) and the load-bearing
label strings: text that looks like documentation and is machine input. Here it is worse than E14,
because the effect is not a wrong report but a **silently different tested domain** -- the PR29
failure mode that section exists to prevent, reintroduced through the prose channel rather than the
parsing one.

**FIXED 2026-08-23.** Declarations are parenthesised in every file that has one -- `(h2 in {0,1})`,
`(deg h = 2, h2 = 1)` -- so the singleton pattern is now read only inside parentheses. Prose cannot
reach it. Verified by reverting the one-line change and watching `selftest.py`'s `domain` section
report `banner prose moved the domain: h3 read as [0, 1], want {1}`; that section is now **8
mechanisms** and the new one is provoked on a synthetic banner rather than on a shipped file, so it
keeps testing the parser after every real banner is corrected.

**Side effect, in the right direction:** with the accidental pin gone, `ramified/g3/nch2` derives
`f6 = 0` from the dispatcher contrast as designed, rather than from a sentence.

## E16: the genus-3 odd-characteristic `dw31`/`dw30` comment has `m7` and `m8` swapped

**Found 2026-08-20** while reading the two genus-3 ramified additions against each other.

`nch2_ramifiedG3_ADD.mag:1407` annotates the degree-1-gcd remainder as

    //dw31:= -m8; dw30:= m7;   //t7^2

against `arb_ramifiedG3_ADD.mag:1420`, which has the same line as

    //dw31:= m7; dw30:= -m8;   //t7^2

**arb is correct.** Verified independently of both files by constructing 300 one-common-point
divisor pairs over GF(10007) and evaluating `t7^2*(up mod dw1)` directly: it equals `m7*x - m8`
in 300 of 300, so `dw31 = m7` and `dw30 = -m8`.

**Comment only, no arithmetic consequence.** Both lines are commented out — they document the
weighted remainder the following code computes, and the live code in both files is right. Left
unfixed only because it is in a file under active editing; it is a one-line correction.

Two things that look wrong and are not, recorded so they are not "fixed" by mistake:

- **The formula copies under `g2/timings/*/ramFormulas/` and `*/splitFormulas/`** are deliberate
  variants, not stale duplicates. Function names carry a `_RAM` or split suffix so both models can be
  loaded into one Magma session, returns are tuples rather than bare value lists, and debug output is
  commented out to keep I/O out of the timed loop. They are hand-maintained and can drift, but they are
  meant to differ. One genuine divergence in a branch predicate is a separate matter and is covered by
  E1's family.
- **The `load` paths in `whitebox/genFiles/`** are relative to `whitebox/`, not to `genFiles/`, because
  that is the directory the generator is driven from. They resolve correctly when run as intended. The
  genus-3 generators pointed at `g3/splitModel/g3Formulas/`, which does not exist; that was genuinely
  broken and is repaired.
