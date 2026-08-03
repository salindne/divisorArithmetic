# Errata

Known defects in this repository and in material published from it, with reproducers.

Nothing here is fixed yet, and that is deliberate. There is currently no way to check a change to a
formula file: Magma is the only implementation, it cannot be run in CI, and on older builds it cannot
even load the genus-3 formulas. A Python verification framework is planned to provide that oracle;
until it exists, editing a formula to fix one of these would be an unverifiable change to published
work. Each entry records what is wrong, how to reproduce it, and what it affects.

Entries are numbered E1, E2, … and referenced from commit messages and from
[README.md](README.md).

---

## E1 — genus-2 ramified ADD: guard too narrow, evaluates `0⁻¹`

**Severity:** correctness. Aborts with a Magma runtime error on reachable input.

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

- `u` is irreducible over `GF(11)`: `−1 ≡ 10` is not a square mod 11 (squares are 1, 3, 4, 5, 9).
- `(u, v)` is a valid reduced divisor: `f − v(v+h) = x⁵ + x³ = x³(x² + 1)`, which `u` divides.
- With `v1 = vp1 = 0` and `v0 = vp0 = 1`: `dw21 = vp1 + v1 = 0`, `dw20 = vp0 + v0 = 2 ≠ 0`.

So the guard is skipped and `b2 := 0^-1` raises.

**Note the input has `D1 = D2`.** This is the genus-2 counterpart of a defect already known in the
genus-3 ramified formulas, where `ADD(D, D)` is silently wrong rather than loud. The testers never
reached it because they only ever compared distinct divisors. The eventual fix is expected to be the
same in both places: dispatch `D1 = D2` to the doubling formula.

**Affects:** the genus-2 ramified formulas as shipped, and the corresponding algorithm as printed in
the thesis, which carries the same guard.

---

## E2 — genus-2 ramified ADD: one 6-valued return among 5-valued returns

**Severity:** latent. No current caller reaches it.

**Where:** the same branch as E1 in all three files — `return 0,0,1,0,0,1;` returns **six** values,
while every other return in those files returns five. The trailing `1` is a balancing weight belonging
to the split model, which the ramified model has no use for.

Harmless today only because nothing reaches that branch. Any caller that unpacks a fixed five values
will break on it, including the planned Python interpreter, which reads these files as its source of
truth.

---

## E3 — generic timing scripts build the second divisor from the wrong source

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

## E4 — `latexConverter.py` produces an empty second operand under Python 3

**Severity:** correctness of generated tables. Latent, because the script does not currently run.

**Where:** [latexTables/latexConverter.py](latexTables/latexConverter.py), lines 383–384 and the loop
at 397:

```python
d2Input = filter(lambda x: SECOND_INPUT in x, noConstInput)
d1Input = [x for x in noConstInput if x not in set(d2Input)]
```

Under Python 2, `filter` returned a list, so `set(d2Input)` was a snapshot and both operand lists came
out right. Under Python 3 `filter` is a lazy iterator: `set(d2Input)` consumes it, so

- nothing is excluded from `d1Input` — every variable, primed and unprimed, lands in `D`;
- the loop at 397 iterates an already-exhausted iterator, so `D'` renders as `[]`.

Reproduced with the file's own variable naming:

```
py3:  D = [u1,u0,v1,v0,up1,up0,vp1,vp0]   D' = []
py2:  D = [u1,u0,v1,v0]                   D' = [up1,up0,vp1,vp0]
```

**Affects:** every ADD table, if regenerated. The committed `.tex` files are correct because they were
generated under Python 2 — so the risk is regeneration, not the current content.

---

## E5 — malformed `//Constant` directives understate three additions

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
2. `d9` and `d10` are missing, replaced by repeats of `d1` and `d0`; `dn5`–`dn10` are absent entirely.
3. A trailing `f3,d6,d7,d8,d1,d0` repeats entries already declared.

[g3/splitModel/negReduced/g3Formulas/nch2_splitG3_DBL.mag](g3/splitModel/negReduced/g3Formulas/nch2_splitG3_DBL.mag)
line 12 has a milder version: `d4` and `d1` each appear twice.

**Measured effect:** three additions understated — `23ADD` by 1, `3ADD` by 2. Corrected totals
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

## E6 — three further `latexConverter.py` counting faults

**Severity:** correctness of generated tables. Recorded together; all three are in the counter itself.

1. **`MUL_TO_ADD` tests the wrong operand,** so the same multiplication is charged 1A or 1C depending
   on the order its operands happen to be written in.
2. **`//startIGNORE` is silently ineffective when the marker is on its own line,** so the
   polynomial-level reference code those blocks are meant to exclude is counted as if it were part of
   the formula.
3. **A missing `//Constant` directive miscounts silently** rather than raising, so a formula file that
   forgets the annotation yields plausible but wrong numbers.

**Affects:** the genus-2 and genus-3 operation-count tables. Repairing these belongs with repairing the
script, which also cannot currently run at all — its six live input paths are missing the `negReduced/`
component and every output call is commented out.

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
  genus-3 generators are genuinely broken, but for a different reason: they point at
  `g3/splitModel/g3Formulas/`, which does not exist.
