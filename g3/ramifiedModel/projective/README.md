# Weighted projective coordinates, genus 3 ramified, odd characteristic

**Scope, and it is narrower than the rest of this repository in three ways at once.**

| | |
|---|---|
| genus and model | **genus 3, ramified** only |
| characteristic class | **odd characteristic (`nch2`)** only — `h = 0`, `f₆ = 0`, `char ≠ 7`.  There is no `arb` and no `ch2` here |
| cases covered | **the frequent path only** — `deg u = deg u' = 3` for the additions, `deg u = 3` for the doubling |

That third line is the one to read twice.  Every affine family in this repository is **complete**:
each degenerate case is explicit, there is exactly one inversion, and nothing falls back to Cantor.
**These formulas are not.**  Off the frequent path they return `Z = 0`, which is a refusal, not an
answer.  Completeness needs the 37 degenerate branches per family, and those are not
quasi-homogeneous statement by statement — each is a Karatsuba cross-term fold over coefficients two
weights apart — so it is separate work rather than a finishing touch.

The point of the representation is that it is **inversion-free**: `0I` in every row below, where the
affine formulas each pay `1I`.

## Counts against the previous best

Odd characteristic, frequent case, genus 3 ramified — the same scope as the rest of this file.

Prior work here reports **combined M+S and no additions**, so the columns differ from the main
[README](../../../README.md)'s affine tables.  Both sides are compared on multiplicative work:
`C` is `0` in every Fan–Wollinger–Gong cell because their normal form leaves no curve coefficient to
multiply by, so our `M+S+C` is set against their `M+S`.

<table>
<thead>
<tr><th rowspan="2">operation</th><th colspan="3">FWG 2006, Table V</th><th colspan="6">this work</th><th rowspan="2">margin</th></tr>
<tr><th>M</th><th>S</th><th>M+S</th><th>M</th><th>S</th><th>A</th><th>C</th><th>I</th><th>M+S+C</th></tr>
</thead>
<tbody>
<tr><td><b>addition</b>, independent <code>Z₁, Z₂</code></td><td>123</td><td>7</td><td>130</td><td>86</td><td>13</td><td>61</td><td>1</td><td>0</td><td><b>100</b></td><td>−30</td></tr>
<tr><td><b>mixed addition</b>, one operand affine</td><td>104</td><td>6</td><td>110</td><td>75</td><td>10</td><td>61</td><td>1</td><td>0</td><td><b>86</b></td><td>−24</td></tr>
<tr><td><b>doubling</b></td><td>107</td><td>10</td><td>117</td><td>69</td><td>11</td><td>61</td><td>3</td><td>0</td><td><b>83</b></td><td>−34</td></tr>
</tbody>
</table>

Three rows, because three is what this repository's record transcribes from their Table V
([RELATED_WORK.md](../../../RELATED_WORK.md), lane 2).  A fourth variant is not quoted here, on the
standing rule that a figure we cannot open is not compared against.

**Consequence for a verifier.**  Wesolowski verification is two exponentiations over `λ`-bit
exponents and is **independent of the delay parameter `T`**, so these three rows are the whole cost
model for the half of a VDF that has to be fast.  Windowed at `w = 4`, the ladder is `2λ` doublings
plus `0.5λ` mixed additions, which is stated per bit of `λ` so that it needs no security parameter
chosen for it:

| | per bit of `λ` | at `λ = 128` |
|---|---|---|
| FWG 2006 | `2(117) + ½(110)` = **289** | 36,992 |
| this work | `2(83) + ½(86)` = **209** | 26,752 |
| saving | **80**, or **27.7%** | 10,240 |

An earlier draft of this figure said "roughly 18,000 against 24,300, about 26% cheaper" with no `λ`
given.  Those two numbers imply `λ = 86.1` and `λ = 84.1` respectively — **different security
parameters**, so they were never a consistent pair.  The per-bit form above is exact and derivable
from the table.

**Why the mixed row matters as much as the general one.**  Mixed is the verifier's inner loop: a
windowed exponentiation adds a precomputed **normalised** table entry to a projective accumulator,
and the table can be batch-inverted up front, so Montgomery's trick applies there.  It does not apply
in the delay chain, by construction — that chain is sequential, which is the point of a VDF.

**The general row is the one that cannot be avoided.**  Wesolowski's `π^ℓ · x^r = y` is the one
multiplication in the scheme whose operands both arrive with their own denominator.

### Source

X. Fan, T. Wollinger, G. Gong, *Efficient Explicit Formulae for Genus 3 Hyperelliptic Curve
Cryptosystems*, CACR tech report **2006-38**, University of Waterloo, 41 pp.
<https://cacr.uwaterloo.ca/techreports/2006/cacr2006-38.pdf> — free, and the source of the figures
above.  The journal version, *"… over binary fields"*, IET Information Security **1**(2), 65–81
(2007), doi:10.1049/iet-ifs:20070003, is paywalled and narrower; the tech report supersedes it in
coverage, which is why the odd-characteristic rows are cited from the report.

Their projective formulas assume the same curve shape as ours in this class — `F_p`, `h = 0`,
`f₆ = 0` — so the comparison is like for like on the curve, and differs only in that theirs covers
the frequent case by punting the rest to Cantor while ours refuses it explicitly.

## The grading

`wt(x) = 2`, `wt(y) = 2g+1 = 7`, with `u_i = U_i / Z^{2(e−i)}` and `v_j = V_j / Z^{(2g+1)−2j}`:

```
//Weights: u2=2,u1=4,u0=6,v2=3,v1=5,v0=7,f5=4,f4=6,f3=8
```

Declared in each file's banner and read from there by the gates rather than derived from the genus,
so a file that changes its grading changes its checks with it.  It is the **unique primitive grading**
for this representation, and a uniform single `Z` is not a grading at all — see
[NEW_WORK.md](../../../NEW_WORK.md) N38.

**Curve coefficients arrive raw.**  They are graded, but the formula carries the scaling itself, so a
caller that pre-scales applies it twice: correct at `Z = 1` and wrong at `Z = 2, 3, 7, 50`, measured.

**`Z = 0` is the refusal signal**, not the affine files' all-`(−1)` return, because `−1` is nonzero
and a normalising caller would build a garbage divisor out of it and score it as a disagreement
rather than a skip.

## Files

| | |
|---|---|
| [g3Formulas/nch2_ramifiedG3_ADD.mag](g3Formulas/nch2_ramifiedG3_ADD.mag) | `Deg3ADD` on independent denominators, `Deg3ADDmix`, and the `ADD` dispatcher |
| [g3Formulas/nch2_ramifiedG3_DBL.mag](g3Formulas/nch2_ramifiedG3_DBL.mag) | `Deg3DBL` and the `DBL` dispatcher |
| [nch2_projectiveG3_random.mag](nch2_projectiveG3_random.mag) | the Magma tester, checked against Magma's own Jacobian arithmetic |

**Parameter names are the derivation's, not this repository's house style**, and knowingly so:
every house target name already occurs in both bodies as an internal value, so a whole-token rename
would merge an input with an unrelated intermediate.  A two-phase rename is the follow-up.
`Deg3ADDmix`'s signature carries **three coefficient orders** — read the banner before calling it,
because the order was reconstructed wrongly the first time anyone rebuilt it.

## Reproducing the figures

Operation counts, from the counter of record:

```
python3 verification/opcount.py --family ramified/g3/nch2/projective
```

```
  ramified/g3/nch2/projective GF(31)
     33ADD  75M 10S  61A  1C  0I    share 1.00 of 2229 calls
     33ADD general-Z  86M 13S  61A  1C  0I    share 1.00 of 75 calls
     3DBL  69M 11S  61A  3C  0I    share 1.00 of 2446 calls
```

**`33ADD` is the MIXED addition, and `33ADD general-Z` is the general one.**  `driver.build_args`
constructs affine divisors and binds both denominators to 1, so the dispatcher's mixed branch always
wins on the ordinary path; the general row is measured separately by binding two distinct
denominators.  The two differ by 11M 3S, so quoting the wrong one against a published addition row
compares the wrong operation.

Correctness:

```
python3 verification/projcheck.py --curves 6 --chain 8
```

Four checks per operation.  Two have no analogue in the affine gates: **scaling invariance**, because
a wrong power of `Z` is invisible at `Z = 1` and every frozen case in this repository feeds `Z = 1`;
and **independent scaling**, where each operand carries its own `λ`, because a formula quietly
assuming `Z₁ = Z₂` passes every same-`λ` test and fails first on exactly the VDF multiplication named
above.

Under real Magma, against Magma's own Jacobian arithmetic — an oracle sharing no code with
`verification/reference.py`, with `Z ≠ 1` throughout:

```
cd g3/ramifiedModel/projective
RND_SEED=1805123479 ../../../tools/magma-docker/magma.sh nch2_projectiveG3_random.mag

// Comparisons: 89   // Off-path: 3   // Wrong: 0
```

Magma does not seed deterministically, so the comparison count moves between runs without the seed;
55, 62, 69, 82 and 89 were all observed, every one at 0 wrong.

## What is not here

- **No whitebox tester, and no per-branch corpus.**  There are no degenerate branches to construct
  cases for yet, the frequent path being all that exists.
- **Not in [test_all.sh](../../../test_all.sh).**  It follows [whitebox/probes/](../../../whitebox/probes/),
  which holds hand-run verification artifacts the suite does not count, and the main README's tallies
  describe the twelve shipped complete families.  Run it with the command above.
- **No `arb` and no `ch2`.**  Only the odd-characteristic class is derived.
- **No measurement at cryptographic size.**  The chain check runs 8 steps at `GF(101)`; a real VDF is
  `2⁴⁰` steps at `q ≈ 2⁶⁴⁰`.  The `I ≈ 25M` break-even that makes the inversion-free trade worth
  taking rests on an inversion-to-multiplication ratio this repository has not measured.
