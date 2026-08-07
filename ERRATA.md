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

**Affects:** every ADD table, if regenerated. The committed `.tex` files are correct because they were
generated under Python 2, so the risk is regeneration, not the current content.

---

## E5: malformed `//Constant` directives understate three additions

**Severity:** correctness of published operation counts.

**Where:** [g3/splitModel/negReduced/g3Formulas/nch2_splitG3_ADD.mag](g3/splitModel/negReduced/g3Formulas/nch2_splitG3_ADD.mag)
line 13, duplicated verbatim in
[g3/timings/formulas/splitFormulas/nch2_splitG3_ADD.mag](g3/timings/formulas/splitFormulas/nch2_splitG3_ADD.mag)
line 13. Compared against the `arb` sibling's line 13, which is well formed:

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

## Not defects

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
