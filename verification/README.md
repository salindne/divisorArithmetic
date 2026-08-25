# verification

A Magma-free semantic gate for the explicit formulas in this repository — with
one deliberate exception, `blockcheck.py`, which runs the reference blocks and
therefore needs real Magma. It is a local gate, never a CI one; see
[The reference blocks](#the-reference-blocks-and-the-only-thing-that-runs-them).

Magma is commercial software distributed as a licensed tarball. It cannot run on a
hosted CI runner, and it exits 0 even when an assertion fails, so it could not gate
on exit status even on a self-hosted one. Everything else in `.github/workflows/`
is a static check by construction. This directory is the only thing that can verify
a *formula* automatically.

It works by running the real `.mag` source through an interpreter and comparing it
against an independent implementation of the group law. **No formula is transcribed
into Python**, so there is nothing for a transcription to get wrong and nothing to
drift when a formula changes.

One module is an exception and says so in its own docstring: `adjugate.py` compares
*candidate rewrites* of one fragment, which do not exist in the `.mag` source at all,
so it has no choice but to transcribe. What it can and does check is that the
transcriptions produce the values the formula files' own comment block defines and,
where the file annotates an operation count, that they cost what the file says. For
the three candidates that *are* in the source, it goes further: its `mag` section
executes their real statement text through `maginterp.py` and requires the
transcription to match it, count and values, so those three are not transcriptions
in the load-bearing sense at all.

Pure standard library. No install step, no lockfile, no dependency to break.

## Running it

```sh
cd verification

python3 selftest.py                 # is the framework trustworthy?
python3 whitebox.py                 # do the formulas agree, on every path?

python3 whitebox.py --list          # which testers exist, and what is harvested
python3 whitebox.py --harvest       # rebuild cases for families with no tester
python3 driver.py                   # random differential testing, not in CI
python3 driver.py --curves 30 --pairs 16 --seed 23 --show-all   # the long run
python3 selftest.py --list          # what each section checks

python3 blockcheck.py               # do the reference BLOCKS agree? needs Magma
python3 blockcheck.py arb --curves=10 --pairs=10
python3 blockcheck.py --list        # families, fields and blocks it can reach

python3 adjugate.py                 # the genus-3 adjugate block: candidates,
                                    # counts, span, lower bounds. ~32s, no Magma
python3 adjugate.py --list          # candidates, fields, sections
python3 adjugate.py --section mag    # the shipped fragments priced from their .mag
python3 adjugate.py --section bound --primes 2,3,5,7,11

python3 dominance.py                # names read with no assignment ABOVE them
                                    # (which includes never assigned at all)
python3 dominance.py g3/ramifiedModel/g3Formulas/arb_ramifiedG3_ADD.mag
```

**`whitebox.py` is the gate.** It replays 2,233 frozen cases, two per computation path
per characteristic class for the ramified families and one elsewhere,
and is deterministic: same inputs, same branches, every run. `driver.py` generates
random inputs instead, which is a different and complementary job -- see below.

### Where the cases came from: found by search, then frozen

Worth stating plainly, because "constructed" invites the wrong reading. Nobody designed
these inputs. `whitebox/genFiles/*_WB_gen.mag` loops over random curves and divisor
pairs, prints a block for each operation whose result agrees with Magma's own Cantor
arithmetic, and lets the formula's own `ADD_DEBUG`/`DBL_DEBUG` label name the branch;
`whitebox/whitebox_auto_NEG.py` keeps the first block for each label until every label
has one. The harvested cases for the families with no tester are the same procedure in
Python.

So a "constructed case" here means **frozen and committed**, in contrast to sampled
afresh each run. Two properties earn it a place in CI -- it is *complete* (every
labelled branch has a case) and *deterministic* (coverage is a fact about the corpus,
not about this run's luck). What it is **not** is an independently designed probe of
each branch: a branch is covered by whatever input the search first landed on.

### Why frozen cases gate CI and random sampling does not

Sampling coverage is coupon-collector. Measured across all fourteen families:

| volume | time | operations | coverage |
|---|---|---|---|
| `--curves 4 --pairs 4` | 37s | 22,384 | 54.1% |
| `--curves 16 --pairs 10` | 3.4 min | 224,498 | 76.8% |
| `--curves 30 --pairs 16` | ~14 min | 674,528 | 86.9% |

It stalls near 87%, so a coverage floor over sampled runs would either be met
trivially or fail honest runs for a reason unrelated to correctness. The frozen corpus
reaches every branch in two seconds, every time, so coverage becomes a gate worth
having.

**Both still matter, for different things.** A frozen corpus gives one input per
branch, which cannot catch a guard too narrow for a sub-case *within* the branch —
errata E1 exactly. The evidence is in this repository: the whitebox testers cover
405/405 branches, pass, and found neither E1 nor `ADD(D, D)`; exhaustive enumeration
found both. So `driver.py` keeps that job, at volume, locally and before a release —
just not in per-PR CI, where 37 seconds of sampling proves neither thing.

`driver.py` flags worth knowing:

- `--strict` additionally fails on wrong answers where `D1 == D2`. The formulas used
  to be wrong there; PR5's equal-divisor dispatch fixed it, and this flag is how that
  was shown (695,888 compared, 695,888 matched, exit 0). It stays on in any run that
  gates anything.
- `--min-coverage PCT` turns coverage into a gate, default 0 (report only).
- A selected family producing **no comparisons** always fails, deterministically:
  "nothing failed" must not be reachable by testing nothing.

## The reference blocks, and the only thing that runs them

Every formula function opens with a `//Formulation` block inside
`/* //startIGNORE ... */ //endIGNORE`: the readable polynomial-level algorithm that
the explicit coefficient code below it implements. **`blockcheck.py` is the only
thing in this project that executes one.** `maginterp.py` interprets the explicit
code and reads *values*, not polynomials, so `whitebox.py`, `driver.py`,
`opcount.py` and every one of the Magma random testers step straight over the
blocks, and every Magma tester loads the file with the block still commented out.

"Uncomment it and it produces the right answers" was therefore an unverified claim
for the whole life of these files. It was also false: the genus-3 ramified `arb`
`Deg3ADD` block agreed on every input whose `gcd(u, up)` had degree 0, 1 or 2 and
disagreed where `u = up`. One cause was a missing
`upp := upp/LeadingCoefficient(upp);` that the split model has.

**What it gates.** The block is spliced into a scratch file as its own function
and driven against the file's own explicit `Deg3ADD` on identical arguments. Case
control is by *construction*: divisors are built from affine points of the curve,
so the number of shared x-coordinates — and hence `deg gcd(u, up)`, which every
branch keys on — is chosen rather than sampled. That is the whole point.
`Random(Jac)` essentially never returns two divisors sharing a `u`, which is why
the 2,539 three-way Magma checks recorded for these blocks in PR4 did not catch
it — a volume of checking that never reached the class the defect lived in.

| shared x-coordinates | what the formulas see |
|---|---|
| 0 | `gcd(u, up) = 1`, the typical path |
| 1 | `gcd` of degree 1 |
| 2 | `gcd` of degree 2 |
| 3 | `u = up` (a `y` at a shared `x` is moved, so `D1 ≠ D2`) |

Every class in range must be non-empty, on the same rule `driver.py` applies to a
family that produces no comparisons.

**Not only `Deg3ADD`.** The two divisor degrees come out of the function's own
signature, so `--function` reaches all six blocks in each file, and which six they
are is discovered rather than listed. The `blocks` section drives every one of them
in both families, so all twelve are gated: at its settings
(`--curves=4 --pairs=6 --seed 11`) all twelve agree over 9,061 comparisons, and it
re-measures that on every run. The seed is quoted because it has to be — the same
twelve agree over 8,904 at the CLI default `--seed 1`. A comparison count is a
property of the run, not of the formulas.

`Deg3ADD` is the CLI default because it is the only one whose two divisors can be
equal, so it is the only one with a `u = up` class — and that is where the defect
was. It is also the only one the provocation is injected into: one demonstration
that the oracle catches a wrong block is what is needed, and the breadth belongs in
the control, which is the part that would otherwise go stale.

**Why it is not in CI.** It needs real Magma, through
`tools/magma-docker/magma.sh`. A reference block is written in the *full*
language — `Resultant`, `XGCD`, `quo<R | up>`, polynomial `div` — which is exactly
the part `maginterp.py` does not implement, because the explicit formulas never
use it. So this cannot be made Magma-free the way the rest of this directory is,
and it has the same standing as the `*_random.mag` testers: run it locally, and
before a release. Magma exits 0 even when a script dies, so exit status is never
trusted: Python requires the machine-readable `BLOCKCHECK` lines and decides the
verdict itself. Both Magma failure shapes are handled — a dead `ExactQuotient`
kills the script and the tally never prints, while an undeclared identifier
aborts only the enclosing loop and the tally prints all zeros.

`selftest.py`'s `blocks` section gates it, by provocation: it runs all twelve
shipped blocks and requires agreement, then injects a defect confined to the
`u = up` branch of one and requires a disagreement whose wrong answers all land in
that class. It fails rather than shrinks if a family or a block stops being
discovered — "nothing failed" must not be reachable by checking less than was
found. It SKIPs, with the reason, when Magma is absent, in about a tenth of a
second, in both shapes a runner presents (no `docker` on `PATH`, and `docker`
present with the image absent). It costs about 22 seconds locally, 15 Magma
invocations, and 3 in `--quick`, which keeps one function per family. The
injection is **not** the original missing normalisation, and the reason is
measured: the rewritten CASE #4.1 obtains `upp` as an exact quotient of a monic
degree-5 numerator by a monic divisor, so it is monic already and that line is
dead code — leading coefficient 1 at all 170 firings in `arb` and 125 in `nch2`.
The section re-runs that deletion and reports the result, so the claim stays
evidence rather than a remark.

**What it does not cover, plainly.**

- It compares the block against the **explicit code**, not against the group law,
  so a defect present in both is invisible to it. Not a gap in practice — the
  explicit code is what `whitebox.py` and `driver.py` check against
  `reference.py`, and what the Magma testers check against Magma's own Jacobian —
  but the claim it licenses is exactly "the block agrees with the verified code".
- Genus-3 **ramified** families only, discovered by globbing
  `g3/ramifiedModel/*_ramifiedG3_random.mag`. The split model cannot be driven
  this way: its divisors carry a weight alongside `(u, v)` and its blocks read it.
  Genus 2 is simply not wired up; the machinery is degree-driven and would likely
  extend.
- **ADD only.** A `DBL` block takes one divisor and has no shared-x axis, so it
  needs a different driver, not a different argument list.
- `u` gets **distinct roots in the base field**. A `u` with a repeated root or an
  irreducible factor is unreachable this way, so a branch only such a `u` can
  reach is not exercised.
- **One guard has not been seen to fire.** If a tester stops being readable — no
  `load` statements, no `FIELDS` set, no recognisable curve generator — the family
  is dropped from discovery and reported, and the `blocks` section fails if the one
  it injects into is the family that vanished. Provoking that needs a mutated
  `*_random.mag`, which was not done, so unlike the other four failure paths of
  that section it is reasoned about rather than measured. The four that were
  measured: a shipped block that disagrees, a provocation that matches nothing, a
  provocation that turns out to be a no-op, and a gate that covers fewer families
  than were discovered.
- A field with fewer affine x-coordinates than `deg u + deg up` cannot present
  these divisors at all. Measured for `Deg3ADD`: GF(2) supplies nothing, and
  GF(3), GF(4), GF(5) and GF(7) reach only the shared classes that need fewer
  distinct x-coordinates. Reported per field on every run rather than passed over
  in silence — characteristic 2 is covered mostly by GF(8), GF(16) and GF(32).

Nothing family-specific is tabulated in it, on the same principle as
`driver.read_support` and `opcount.directives`: which files to load, which curve
generator to draw from and which fields to sweep are read out of the family's own
`*_random.mag` tester, and the divisor degrees, argument order and return arity
out of the function's own signature and first `return`. The one file it writes is
a scratch `.mag` in this directory, removed in a `finally`; it never writes under
`g3/`.

## The adjugate block, and the one place candidates are compared

`adjugate.py` is about a single fragment: the 3×3 matrix `T` of multiplication by
`w = u − up` modulo `up`, its adjugate `M`, and `d = det(T) = Res(w, up)`. Every
genus-3 addition and doubling in this repository opens with it, and the six runtime
inputs are `t1, t4, t7, up0, up1, up2` — the three subtractions `t1 = u0 − up0` and
its siblings are paid before the fragment starts and are not counted, which is why
`16M 0S 9A` is the right count for a fragment that visibly performs twelve
additions.

It exists because the measurements behind [`NEW_WORK.md`](../NEW_WORK.md) N26 were
made in about 140 one-off scratch scripts outside the repository, several of them
importing sympy, so none of them could be reproduced from a checkout. Everything
here is recomputed: standard library only, exact where exactness is needed
(`fractions.Fraction`, and a hand-rolled sparse multivariate polynomial), and no
Magma.

**The definitions are read out of the source, not written down here.** Nine formula
files carry the cofactor comment block

```
//| m1= t5*t9-t8*t6,  m2= t3*t8-t2*t9, m3= t2*t6-t3*t5 |
//| m4= t6*t7-t4*t9,  m5= t1*t9-t3*t7, m6= t3*t4-t1*t6 |
//| m7= t4*t8-t5*t7,  m8= t2*t7-t1*t8, m9= t1*t5-t2*t4 |
```

and all nine are parsed from each of the nine and required to agree with an
adjugate this module builds itself, from `multiply by w, reduce mod up, take 2×2
minors`. Each file's determinant line is checked too, and `det(T)` against the 5×5
Sylvester resultant of `w` and `up`, so the comment's claim that the determinant
*is* the resultant is measured rather than repeated. One interesting outcome:
`g3/splitModel/negReduced/g3Formulas/ch2_splitG3_ADD.mag` writes
`d := t1*m1 + t2*m4 + up0*t8*m7`, which differs from
the general form by a factor of −1 on the last term and is therefore reported as
*agreeing in characteristic 2 only* — correct for a `ch2_` file, and it would be
reported as a disagreement from any other.

**What the table says.** Twelve programs, each verified over sixteen fields —
GF(2), GF(4), GF(8), GF(16), GF(32), GF(256), GF(2¹⁶) and the primes 3 … 1000003 —
and once symbolically in `Z[t,up]`, which is the stronger statement: the
coefficients are integers, so an identity there holds in every characteristic. The
counts follow `chapter6.tex:2323-2336` and `maginterp.py` (a unary minus is free, a
literal-integer product is 1A, halving is refused in characteristic 2) and are
scored in the thesis's 1M : 3A equivalent additions (`chapter4.tex:817`). One
deliberate divergence, stated in the docstring: a same-object product `x * x` is
charged S here, where `maginterp.py` charges M for `x*x` and S only for `x^2`. It
moves no figure below — every candidate has S = 0 — and S is priced as M in the
`equiv` column for the same reason.

`gives` is how many of the thirteen values (`m1..m9`, `d`, `sp0..sp2`) the program
returns. **Rows with different `gives` are not comparable** — `rank5_7` is the
cheapest number in the table and does not form `d`, so it is not competing with
`shipped_7`, which does. The tool prints the column and prints the like-for-like
groups, cheapest first, underneath the table, for exactly this reason.

| program | gives | M | S | A | equiv | note |
|---|---|---|---|---|---|---|
| `shipped_7` | 8 | 16 | 0 | 9 | **57** | the shipped block; `// top: 16m 0s 9a` |
| `shipped_7_dbl` | 8 | 16 | 0 | 9 | **57** | the doubling's transcription of the same; `// 16m 0s 9a` |
| `rank5_7_d` | 8 | 15 | 0 | 14 | **59** | the same eight values: 1M cheaper, 5A dearer |
| `shipped_9` | 10 | 18 | 0 | 11 | **65** | plus the `m4`/`m6` close |
| `rank5_9_d` | 10 | 17 | 0 | 16 | **67** | the same ten values |
| `rank5_7` | 7 | 12 | 0 | 12 | 48 | no `d`; not a rival to any row above |
| `rank5_9` | 9 | 14 | 0 | 14 | 56 | no `d`; likewise |
| `split_q` | 4 | 15 | 0 | 9 | 54 | the split model's first column only, and all nine `T` entries to get it |
| `row3_shipped` | 3 | 9 | 0 | 5 | **32** | bottom row + column 2 of `T` |
| `row3_rank5` | 3 | 8 | 0 | 10 | **34** | the same three values |
| `region_shipped` | 4 | 27 | 0 | 17 | **98** | the whole region; `// total: 27m 0s 17a (equivalent 98a)` |
| `region_rank5` | 4 | 26 | 0 | 22 | **100** | the same four values |

The bolded pairs are the comparisons that mean anything, and the rank-5 route loses
every one of them: 57 → 59, 65 → 67, 32 → 34, and 98 → 100 for the whole region. It
buys one multiplication for five additions, over the 1M : 3A threshold, so on the
thesis's own scale the trade is refused. Nothing in the table changes a published
row.

Four operation-count comments in the two ramified files are parsed and required to
equal the measurement exactly — `// 16m 0s 9a` in the doubling, and `// top:`,
`// total:` and the unlabelled `// 11m 0s 8a` in the addition, the last checked as
the difference between the whole region and the top block, since the lower half
reads `m1..m9` and is not a program on its own.

**The lower bound, which is the part that was in dispute.** Two claims had been
made and they disagreed: that the nine entries span a 3-dimensional space of
quadratic forms in `(t1,t4,t7)` so at least 3 `t`-by-`t` products are needed, and
that the answer is at least 4. The second is right, and the argument is:

- the span really is 3-dimensional — exactly, over `Q(up0,up1,up2)`, by
  fraction-free elimination, and equally at `up → 0` and over GF(2) … GF(11), where
  it is `U = span{t1², t1·t4, t4² − t1·t7}`;
- a product of two `t`-linear forms is a *reducible* quadratic. Exhaustively, over
  GF(2), GF(3), GF(5), GF(7) and GF(11), the products that **lie in** `U` span only
  2 dimensions (5, 28, 176, 540 and 2300 of them respectively, out of all ordered
  pairs);
- so three products whose span contained the 3-dimensional `U` would span exactly
  `U`, hence all three would lie in `U`, hence span at most 2. Contradiction.
  Outside characteristic 2 the same conclusion comes from an exact computation
  instead of an enumeration: writing the generic element of `U` as
  `a·t1² + b·t1·t4 + c·(t1·t7 − t4²)` in the basis the tool *derives* from the nine
  entries, the Hessian determinant is `2c³`, so the reducible locus is the
  2-dimensional `c = 0` — the multiples of `t1`. The `2` is why characteristic 2
  needs the enumeration, and there the enumeration over GF(2) is exhaustive.
  `U`, that basis, and the cross product's slice space in the section below are all
  computed rather than written down, so `--section bound` on its own cannot report
  a bound from a stale basis.

The specialisation is a choice, and the tool shows it matters: the same
enumeration at five values of `up` over GF(7) yields 4 at four of them —
`(0,0,0)`, `(1,2,3)`, `(3,5,6)`, `(1,1,1)` — and **nothing at all** at `(1,0,0)`,
where the products lying in the span already span it (1,512 of them). Taking a
bound at the best specialisation is legitimate, since a program that computes the
entries for every `up` computes them at any single one, but the bound is not
available everywhere and that is worth seeing.

Four products attain it, so the bound is tight where it applies — and that is
exactly the limit worth stating. **It bounds only the products of two `t`-linear
forms in the `up → 0` specialisation.** Measured, every program in the table has
exactly 4 such products, so the bound separates none of them; the shipped block
spends 16M in total and 6 `t`-by-`t` products, of which 4 survive the
specialisation. The gap between this bound and the shipped count is 12
multiplications wide and this module does not close it.

**The bottom row is a cross product.** `(m7,m8,m9)` is, as a polynomial identity,
column 1 × column 2 of `T`. The 3×3×3 tensor of that bilinear map admits **no
rank-4 decomposition** over GF(2), GF(3) or GF(5) — exhaustively, by enumerating
every 4-dimensional space containing its slice space and asking whether the
rank-1 matrices inside it span it — and a rank-5 one is exhibited: five of
`row3_rank5`'s eight products are bilinear in the two columns, `m7`, `m8` and `m9`
lie in their span, and the other three build column 2, which the shipped route
pays for as well. So five is the floor for that row, it is attained, and the
shipped row spends six. This is a statement about programs that treat the two
columns as independent inputs; in the real block column 2 is a function of column 1
and of `up`, so a program may exploit that and the floor does not transfer. It is
not proved over Q either — a rational rank-4 decomposition would need a common
denominator divisible by 2, 3 and 5 to survive all three refutations.

**Gated by provocation**, in `selftest.py`'s `adjugate` section, with nothing on
disk touched: the candidate programs are Python functions handed to
`adjugate.check`, so a wrong one is a function defined inside the section. Two are
required to be caught — an operand swap, which must be reported wrong in all
sixteen fields, and a sign flip, which must be reported wrong in all nine
odd-characteristic fields and in **none** of the seven characteristic-2 ones.
Neither changes the operation count, so a count-only comparison would accept both.
The asymmetry is the check that the sixteen fields are not decoration.

**What it does not cover.**

- **Nine of the twelve programs are transcriptions.** The `mag` section closes the
  gap for the other three and only for those: it extracts the fragment's real
  statement text from the `.mag` between two anchors, executes it through
  `maginterp.py` — the same interpreter and cost model `opcount.py` uses — and
  requires the count *and* the values to equal the transcription's. Measured that
  way, `shipped_7` is 16M 0S 9A over 11 statements, `shipped_7_dbl` 16M 0S 9A over
  17, and `split_q` 15M 0S 9A over 10, all three with the reference values. A moved
  anchor is reported as `located NO` and fails, rather than being skipped.
  `shipped_9` and both `region` rows straddle the `d eq 0` guard so no anchor pair
  isolates them as a program, and the `row3` pair and every rank-5 variant exist
  nowhere in the repository as `.mag`; those stay transcriptions, tied to the
  source only by their values and by the `// total:` comment, and a transcription
  error preserving both would survive there.
- It is a static count of a straight-line fragment: not a published table row, no
  inversion, no branch structure.
- The alternative route the doubling's comment prices at `11m 20a`
  (`g3/ramifiedModel/g3Formulas/arb_ramifiedG3_DBL.mag`, at
  `// 11m 20a where the matrix-vector product costs 11m 8a`) — first column only, then Karatsuba twice —
  is **not** implemented here. It exists nowhere in the repository as code, so
  building it would mean inventing it, and neither its `11m 20a` nor the
  `11m 8a` it is compared against is verified by this module. The tool prints
  that under `NOT ESTABLISHED HERE`, along with the consequence: taking the
  file's figure on trust and adding the split first column, which *is* measured
  at `15M 0S 9A`, that route comes to `26M 0S 29A`, equivalent 107. So **two
  different 26M rows** are in play, and the `26M 0S 22A` in the table is the
  rank-5 adjugate one, not this one — which is the likeliest reason the row was
  hard to reproduce.
- No file under `g3/` or `g2/` is written. They are opened read-only.

## What is here

| file | |
|---|---|
| `ff.py`, `poly.py` | finite fields and univariate polynomials |
| `reference.py` | the oracle: Cantor composition and reduction for both models, plus balanced arithmetic in both reduced bases |
| `curves.py` | curve and divisor generation, and the empirical filter that decides which curves are usable |
| `_parser.py` | expression parsing for the `.mag` subset: calls, indexing, sequence and tuple literals, full precedence |
| `maginterp.py` | executes `.mag` function bodies. `python3 maginterp.py` reports parse coverage |
| `whitebox.py` | replays the frozen cases; **this is what CI gates on** |
| `harvested_cases.json` | frozen cases for every branch no Magma WHITEBOX tester reaches -- currently 96 cases, all for the two genus-3 ramified families, which have random testers but no whitebox generator. Re-harvested when the odd-characteristic genus-3 doubling was derived, since its branches had until then been the arb file's. The genus-3 split `ch2` entries left when PR12's regenerated tester made them redundant |
| `coverage_baseline.json` | the branches exempt from coverage, **as a named label set with a reason each** — everything else must be covered, so a newly added branch fails by default and branches cannot be traded one-for-one. Also pins any known arity anomalies by case identity, so a new one fails while known ones stay reported-not-fatal; the pin set is empty since PR5 fixed errata E2 |
| `driver.py` | random differential testing, with per-branch coverage; not in CI |
| `normal_form.py` | verifies the curve normal forms the formula banners declare, at both genera, including the negative controls. Standalone, no arguments, ~1 min; not in CI. Backs Part I of [`NEW_WORK.md`](../NEW_WORK.md) |
| `blockcheck.py` | executes a reference block and compares it against the explicit code it documents. The only thing here that runs a block, and the only thing here that needs Magma; not in CI |
| `adjugate.py` | the genus-3 addition/doubling adjugate-and-determinant block: candidate programs verified and operation-counted over sixteen fields and once symbolically, the span of the nine cofactors as quadratic forms, and two lower bounds. Backs `NEW_WORK.md` N23. Standard library only, no Magma, ~32s |
| `dominance.py` | reads with no assignment above them, in statement order -- which also covers a name never assigned at all, so it is the only checker of this class shipped. Asking merely "is it assigned *somewhere*" is satisfied by an assignment *below* the read, which is exactly what a half-finished rename leaves behind. Standard library only, no Magma, instant. What it cannot see -- an assignment on a sibling path, or a name assigned above with the WRONG value -- is `ERRATA.md` E15 and E17 |
| `selftest.py` | checks the framework itself, seventeen sections |

## Current state

Measured with `driver.py --curves 30 --pairs 16`:

| | |
|---|---|
| families covered | **14** — ramified and split, genus 2 and 3, both reduced bases |
| operations compared | **674,528** |
| wrong on the formulas' documented domains | **0** |
| branch coverage | **86.9%** overall; **100% on all nine ramified files** |
| `selftest.py` | 16 sections, 16 passing (`blocks` needs Magma and skips without it) |
| parse coverage | 240 of 246 functions |

The 6 functions not interpreted are `Random*Curve` generators, which are not formulas
— `curves.py` generates curves instead.

## Two things it finds that no Magma tester in this repository can

Every Magma tester here either guards `if D1 ne D2` or holds one frozen case per
branch, so neither can see the `D1 = D2` region at all. The driver reports it
separately from failures on the documented domain:

- **64,883 wrong sums where `D1 == D2`**, in the run above. The thesis assumes `D1 ≠ D2` and no file
  checked it. A double-and-add ladder hits this. **Fixed by PR5**: every ADD dispatcher now routes
  `D1 = D2` to the doubling, and the same run under `--strict` is 695,888/695,888.
- **Divisions by zero in the same region** — errata E1, where the guard
  `IsZero(dw20) and IsZero(dw21)` is too narrow, so `dw21 = 0` with `dw20` nonzero
  reaches `dw21^-1`. Every known firing has `D1 = D2`, so PR5's dispatch closes them
  at the dispatcher; the narrow guard itself is still as published, by decision.

Both figures describe the pre-PR5 state and are kept as the record of what the
dispatch fixed.

## Design decisions worth knowing before changing anything

**Nothing family-specific is tabulated. It is read out of the source.** Which curves
a family's formulas are valid for, how its dispatcher is called, and what its
`ccs` constants mean are all derived from the family's own `.mag` files. A table
would keep passing after the source changed.

**"A coefficient no formula reads must be zero" is false**, and assuming it produced
a wrong answer twice. No genus-2 ramified file reads `f0`, `arb` included, because
Cantor reduction needs only the quotient and the low coefficients land in the
remainder. Domains are derived by *contrast* against the `arb` family of the same
model and genus, which is the one valid on arbitrary curves: what the general family
reads and a specialisation does not is what that specialisation assumed away.

**But the contrast can only ever say ZERO, and two coefficients are not about
that.** Ask for a domain through `family_domain`, never `domain_constraints`
alone. Two things the contrast cannot express:

- *`f_{2g+1}` is the model.* A ramified `f` is monic, so a characteristic-2
  genus-3 dispatcher in the normal form reads only `Coeff(f,2..0)` — and the
  contrast read the absent leading index as an assumption, zeroed it, and
  `curves.Curve` raised an uncaught `AssertionError`. Filtered out for ramified
  families, and deliberately **not** for split, where `f_{2g+2}` is a live
  non-monic parameter.
- *`h_g`'s value IS the domain*, 0-or-1 for `arb` and exactly 1 for `ch2`. Once a
  `ch2` file stops extracting `Coeff(h,g)` — the point of exploiting the
  assumption — the contrast reads that as "`h_g` is zero" and the tested domain
  **inverts** onto `deg h < g`, exactly the family `ch2` excludes. Measured
  before the fix: 40 draws, `deg h = 2` came up zero times.

So **the banner wins over the contrast**: any coefficient a banner pins is
removed from the zero-contrast and left to the members pass. `banner_members`
reads both `(h2 in {0,1})` and the singleton `h2 = 1`, from the banner only — a
formula body is full of derivation comments like `-h3 = 0;` that a whole-file
scan would misread — and a **borrowed** file's banner is excluded, since the
genus-3 `nch2` family borrows the `arb` DBL, whose banner would otherwise hand it
`h₃ ∈ {0,1}` for formulas derived at `h = 0`.

**An unreadable domain fails the run.** Every failure in this class was silent,
so `require_leading_pin` refuses to run a ramified `arb` or `ch2` family whose
banner pins no `h_g`, reporting through `res.errors` rather than `res.skipped`.
`selftest.py`'s `domain` section provokes all seven mechanisms and each check has
been shown to fail with its fix reverted.

**Branch coverage is not optional output.** Several defects in this repository
survived because a tester never reached the branch. An unexercised branch is
reported every run and, by default, fails it.

**Nothing is capped silently.** A family that cannot be loaded, a field with no
suitable curve, a directory excluded from discovery: all are printed with the
reason. A truncated run that prints "all passed" is worse than one that fails.

**Curve acceptance is empirical, and the textbook criterion is used only to reject.**
A candidate curve is kept only if `reference.py` forms a group on it. The
singularity criterion additionally rejects, never accepts, because the two are
individually incomplete: the criterion detects singularity over the algebraic
closure, while the empirical filter samples finitely and can miss even an F-rational
singular point. Rejecting on both is the safe direction — it narrows the tested
domain rather than admitting a curve the group law fails on.

## Known limits

- **Why coverage of `ch2_splitG3_ADD` was hard, and what it took.** This is worth
  recording because the obvious diagnosis was wrong twice.

  The generator's own divisor sampler, `RandomDivisorAB`, cannot produce most of the
  divisors that exist. It demands `GCD(u, Derivative(u)) eq 1` and every factor of `u`
  linear, and it requires each root to be the x-coordinate of an F_q-rational affine
  point. Measured on one genus-3 split curve over GF(4): **39 of the 154 reduced
  divisors, 25%**, and the sampled set is exactly the structurally reachable one, so no
  number of draws widens it. It also takes the weight as `Random(g - Degree(u))`, so a
  degree-3 divisor always gets weight 0, and two independent draws essentially never
  share a `u` — which is what a guard like `ADD172`'s `IsZero(m3) //u = up` needs.
  Enumerating every `v` for every monic `u` and testing divisibility admits all of it
  and costs 0.2s per GF(4) curve.

  That was still not enough, and the reason is the **curve**, not the divisors. Two of
  the guarded intermediates are curve constants in disguise: `z3 = W4*dn3` where `dn3`
  collapses to exactly `f3` in characteristic 2, so `z3 = 0` iff `f3 = 0`. The unifying
  quantity is `W0 := f - Vp*h - Vp^2`, of degree at most `g`, and its degree partitions
  the curves into **four mutually exclusive classes**:

  | `deg W0` | condition | branches only this class can reach |
  |---|---|---|
  | 3 | `f3 ≠ 0` | `ADD190`, `ADD255`, `ADD296` |
  | 2 | `f3 = 0`, `k2 ≠ 0` | `ADD251`, `ADD267` |
  | 1 | `f3 = 0`, `k2 = 0`, `k1 ≠ 0` | `ADD227`, `ADD247`, `ADD263` |
  | ≤ 0 | `f3 = k2 = k1 = 0` | `Precompute`'s `UTL0` leaf |

  No single curve spans them, and `RandomChar2G3SplitCurve` lands in the last two only
  1/q² and 1/q³ of the time. That is why those branches never appeared, and why the
  generator now sweeps curves by `deg W0` class instead of only drawing them.

  The third piece: every one of the eleven hardest branches **returns the same divisor
  class**, `T3 = [inf₊ - inf₋]` (one returns `-2·T3`). So their inputs are not rare
  divisors, they are pairs whose class *sum* is forced — a solvable equation rather than
  a coincidence to wait for. For each `D1` the only possible partner is `D2 := T - D1`,
  one `Add` per divisor per target, which turns a coupon-collector search into an
  enumeration of every pair that could ever reach them.

  Cost, measured, for the same family:

  | search | operations | branches of 405 |
  |---|---|---|
  | original sampler, 12,000 trials | 47,098 | 347 |
  | original sampler, ~15,700 trials | 61,848 | 353 |
  | enumerated divisors, 80 curves | 426,745 | 398 |
  | + degree-stratified pairs, 4 curves | 17,368 | 305 |
  | + curve sweep by `deg W0`, GF(4) only, 12 curves | 32,847 | **381** |
  | full: sweep + random phase, both fields | 903,043 | **402** |

  Read the last two rows together: steering curves reached 381 branches in 32,847
  operations, where undirected search needed 426,745 to reach 398. Roughly 13× per
  operation.

  Every one of those operations is also a differential test — the generator emits a
  case only when the formula agrees with Magma's own Cantor arithmetic — so the run
  above is a **903,043-operation, zero-failure** check of these formulas over a domain
  the previous sampler could not express.

- **Random sampling alone plateaus near 87%**, which is why it is not the gate. The
  three genus-3 split ADD files carry 350 labelled branches each; raising volume moved
  one from 40% to 81% and then stopped. The frozen corpus closes it instead.

- **The infinite-place root is exact wherever a basis polynomial is available, and
  conventional otherwise.** The split `Precompute` functions take the value at infinity
  from `Factorization(x² + h·x − f)[2][1]`, "the second solution from the factorization
  given by magma", and Magma's factor ordering cannot be recovered by reading source.
  Constructed cases supply `V` explicitly, so `y_{g+1}` is its leading coefficient and
  `maginterp.ROOT_PIN` makes the choice exact — no convention involved. Measured, no
  global ordering would have worked: one fails 247 cases, all in characteristic 2, the
  other 332, all over odd primes. `driver.py`'s generated inputs have no supplied `V`,
  so they fall back to `ROOT_CHOICE`, established by running both against the reference.

- **`ff.py`'s extension-field moduli match Magma's**, queried from Magma directly rather
  than assumed. They already agreed for GF(4), GF(8), GF(16), GF(27) and GF(32); GF(9)
  and GF(25) did not, and that reproduced as wrong constructed cases. Anything outside
  `MAGMA_MODULI` still uses the search order, so a new extension field wants checking
  before its cases are trusted.

- **`g2/timings/` and `g3/timings/` are excluded**, and named as excluded on every
  `--list`. They hold an earlier generation of the formulas: the same function names, but
  every body differs, with a different `ccs` layout, tuple returns and opposite signs on
  some terms. They are not the formulas of record; see `ERRATA.md` E7.

- **Two `selftest.py` sections need artefacts from outside this repository** — the prior
  audit's harness and stored repros. They report as SKIP when absent, never as passing.

## Relationship to the Magma testers

They are independent oracles and both are worth having. The Magma testers assert
against Magma's own Jacobian arithmetic; this framework asserts against a
from-scratch Cantor implementation, cross-checked three ways.

They have been run against each other: the full Magma suite passes 28 testers with 0
failures (2 deliberate skips), and the driver reports 0 mismatches on the same families. Agreement is
expected only where both can look, and the one asymmetry is the point — the driver
sees the `D1 = D2` region and no Magma tester can.

`blockcheck.py` sits between the two: it uses Magma, because a reference block
needs the full language, but it is driven from here and its inputs are constructed
rather than drawn from `Random(Jac)`. That is the second thing no Magma tester in
this repository can do — reach two divisors that share a `u` — and it is where the
block defect was.

See `../README.md` for the repository as a whole and `../ERRATA.md` for the recorded
defects, several of which are reproduced here as required test vectors.
