"""Generate a Magma whitebox tester from a case generator in genFiles/.

A generator is a Magma script that loops over random curves and divisor pairs,
prints a `@B` .. `@E` block for each operation whose result agrees with Magma's own
Cantor arithmetic, and lets the formula's own ADD_DEBUG/DBL_DEBUG label name the
branch. Collecting one block per distinct label yields a tester holding a frozen
case for every branch. Coverage is therefore a random search, not a construction --
what makes the result valuable is that it is complete and replayable, not that any
case was hand-built.

Rewritten from a version that could not run here, and in fact could not run
anywhere as committed:

  * it drove the generator as `Popen(["magma", ...])`, needing Magma on PATH, then
    SIGSTOPped that pid every ten seconds to scrape the log and SIGCONTed it. Magma
    runs in a container in this repository, where signalling the wrapper does not
    pause Magma inside it;
  * `f.truncate(0)` reset the log while Magma still held it open at its own write
    offset, so the next block landed after a hole. The committed
    logs/{arb,nch2}_splitG3_log.txt both begin mid-polynomial, which is that race;
  * the generators looped `while true`, terminating only by being killed;
  * it was hardcoded to one family, `FileInfo("nch2","split","2")`;
  * and it stopped at `#Create Magma file` -- the emitter below was never called,
    so a successful collection wrote nothing.

Now the generator carries its own trial bound (WB_TRIALS) and writes where it is
told (WB_LOG), so this runs it once, waits, and parses the finished log. Anything
the trials failed to reach is reported rather than looped on forever.

Usage:
    ./whitebox_auto_NEG.py ch2 split 3 --trials 400 --out ../g3/.../x.mag
    ./whitebox_auto_NEG.py ch2 split 3 --from-log logs/ch2_splitG3_log.txt
"""

import argparse
import os
import subprocess
import sys

#fieldType = arb, ch2, nch2
#curveType = ramified, split
#genus     = integer greater than 1
#tagDigit  = (DBL_DEBUG digits, ADD_DEBUG digits)
class FileInfo(object):
    def __init__(self,fieldType, curveType, genus):
        # Only the split model has a reduced-basis subdirectory. This was
        # unconditional, so every ramified path pointed at a
        # ../g2/ramifiedModel/negReduced/ that has never existed -- which is most of
        # why only one family was ever reachable.
        if curveType == "split":
            self.PATH = "../g" + genus + "/" + curveType + "Model/negReduced/"
        else:
            self.PATH = "../g" + genus + "/" + curveType + "Model/"
        self.GEN = "genFiles/" + fieldType + "_" + curveType + "G" + genus + "_WB_gen.mag"
        self.ADD = "g" + genus + "Formulas/" + fieldType + "_" + curveType + "G" + genus + "_ADD.mag"
        self.DBL = "g" + genus + "Formulas/" + fieldType + "_" + curveType + "G" + genus + "_DBL.mag"
        self.UTL = "g" + genus + "Formulas/" + fieldType + "_" + curveType + "G" + genus + "_UTL.mag"
        self.LOG = "logs/" + fieldType + "_" + curveType + "G" + genus + "_log.txt"
        self.OUT = "testerFiles/" + fieldType + "_" + curveType + "G" + str(genus) + "_whiteBox_tester.mag"
        self.GENUS = genus
        self.FIELD = fieldType;

        if curveType == "split":
            self.split = True
        else:
            self.split = False

        # The shared polynomial-arithmetic file the tester must load. Genus 2 split
        # keeps it in reduced_basis_arithmetic.mag; genus 3 split renamed it to
        # poly_balanced_arithmetic.mag, which is what the deployed genus-3 testers
        # load and what the emitter below had hardcoded wrongly.
        if self.split:
            if genus == "2":
                self.ARITH = "reduced_basis_arithmetic.mag"
            else:
                self.ARITH = "poly_balanced_arithmetic.mag"
        else:
            self.ARITH = "ramifiedUtilities.mag"

        self.dblNum = 0
        #Counts DBL cases
        f = open(self.PATH + self.DBL, "r")        
        raw = f.readlines()

        for line in raw:
            if "DBL_DEBUG" in line:
                self.dblNum = self.dblNum + 1
        f.close()
        self.dblTag = "{0:0=" + str(len(str(self.dblNum))) + "d}"


        self.addNum = 0
        #Counts ADD cases
        f = open(self.PATH + self.ADD, "r")        
        raw = f.readlines()

        for line in raw:
            if "ADD_DEBUG" in line:
                self.addNum = self.addNum + 1
        f.close()
        self.addTag = "{0:0=" + str(len(str(self.addNum))) + "d}"    



class CaseGen(object):
    """Runs a generator once, then parses its log into one case per branch."""

    def __init__(self, fileInfo, magmaCmd=None, trials=400, seed=1, divisors=1):
        self.file = fileInfo
        self.magmaCmd = magmaCmd or ["../tools/magma-docker/magma.sh"]
        self.trials = trials
        self.seed = seed
        self.divisors = divisors

    def expectedTags(self):
        """The branch labels a complete tester must hold.

        Derived the way the original did -- from the count of DEBUG lines in each
        formula file, zero-padded -- because that is what the generators' labels
        were numbered against.
        """
        dbl = ["DBL" + self.file.dblTag.format(i) for i in range(self.file.dblNum)]
        add = ["ADD" + self.file.addTag.format(i) for i in range(self.file.addNum)]
        return dbl, add

    def runGenerator(self, logPath):
        """Run the generator to completion, writing its log to logPath."""
        env = dict(os.environ)
        env["WB_TRIALS"] = str(self.trials)
        env["WB_SEED"] = str(self.seed)
        env["WB_DIVISORS"] = str(self.divisors)
        env["WB_LOG"] = logPath
        env["MAGMA_ENV"] = "WB_TRIALS WB_SEED WB_LOG WB_DIVISORS"

        if os.path.exists(logPath):
            os.remove(logPath)

        print("running %s: %d trials, %d divisors/curve, seed %d"
              % (self.file.GEN, self.trials, self.divisors, self.seed))
        proc = subprocess.run(self.magmaCmd + [self.file.GEN], env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out = proc.stdout.decode("utf-8", "replace")
        if proc.returncode != 0:
            sys.stderr.write(out)
            raise SystemExit("magma exited %d" % proc.returncode)
        # Magma exits 0 on a failed assertion, so the output must be read.
        for marker in ("Runtime error", "User error", "Assertion failed"):
            if marker in out:
                sys.stderr.write(out)
                raise SystemExit("magma reported %r" % marker)
        if not os.path.exists(logPath):
            sys.stderr.write(out)
            raise SystemExit("generator produced no log at %s" % logPath)

    def parseLog(self, logPath):
        """Collect the first block for each branch label.

        A `failed` line means the formula disagreed with Cantor. The generator
        prints it instead of a block and carries on; here it is fatal, because a
        tester must not be built from a run that contained a wrong answer.
        """
        dblCases, addCases = self.expectedTags()
        wanted = set(dblCases) | set(addCases)
        cases, failures, blocks = {}, 0, 0

        with open(logPath, "r") as f:
            raw = f.readlines()

        processing, current = False, []
        for line in raw:
            if "failed" in line:
                failures += 1
            if "@B" in line:
                processing, current = True, []
            elif processing and "@E" in line:
                processing = False
                blocks += 1
                self._takeCase(cases, current, wanted)
                current = []
            elif processing:
                current.append(line.strip())

        if failures:
            raise SystemExit("generator reported %d failed comparison(s) in %s; "
                             "refusing to build a tester from it"
                             % (failures, logPath))

        missing = sorted(t for t in (set(dblCases) | set(addCases)) if t not in cases)
        print("%d blocks parsed, %d of %d branches covered"
              % (blocks, len(cases), len(dblCases) + len(addCases)))
        if missing:
            print("%d branch(es) not reached by this search:" % len(missing))
            print("  " + " ".join(missing))
        return cases, missing

    def _takeCase(self, cases, current, wanted):
        """Store one block, keyed by the label the formula printed.

        The label is the first line of the block because ADD_DEBUG/DBL_DEBUG print
        it from inside the formula. It is compared stripped: ADD082 carries a
        trailing space in all three genus-3 split ADD files.
        """
        if not current:
            return
        tag = current[0].strip()
        if tag not in wanted or tag in cases:
            return

        def divisor(s):
            return s.replace(' ', '').replace('<', '').replace('>', '').split(',')

        if self.file.split:
            # label, F, f, h, Vp, Vn, RD1, RD2, result
            if len(current) < 9:
                return
            curve = [current[2], current[3], current[4], current[5]]
            divs = [divisor(current[6]), divisor(current[7])]
            result = current[8]
        else:
            # label, F, f, h, RD1, RD2, result
            if len(current) < 7:
                return
            curve = [current[2], current[3]]
            divs = [divisor(current[4]), divisor(current[5])]
            result = current[6]

        if tag.startswith("DBL"):
            divs = divs[:1]
        cases[tag] = (current[1], curve, divs, result)


class Magma(object):
    def __init__(self, fileInfo, cases):
        self.file = fileInfo
        self.magma = []
        self.cases = cases
        self.generateCode()
        self.makeFile()
        

    def generateCase(self, case):
        g = int(self.file.GENUS)

        self.magma.append('FF := GF(' + case[1][0] + ');\n')
        self.magma.append('R<x>:=PolynomialRing(FF);\n')
        self.magma.append('f:= R! ' + case[1][1][0] + ';\n')
        self.magma.append('h:= R! ' + case[1][1][1] + ';\n')

        if self.file.split:
            self.magma.append('V:= R! ' + case[1][1][2] + ';\n')
            self.magma.append('Vn:= -V - h;\n')
            self.magma.append('ccs:= Precompute(f,h,' + case[1][0] + ');\n')
            self.magma.append('\n')

            
            # Return list and the polynomials rebuilt from it. Every term carries
            # an explicit *x^i, including x^1 and x^0, matching the deployed
            # genus-3 testers so a regenerated file can be diffed against them.
            returned = 'un' + str(g)
            polyU = 'un' + str(g) + '*x^' + str(g)
            polyV = ('Coeff(Vn,' + str(g+1) + ')*x^' + str(g+1)
                     + ' + Coeff(Vn,' + str(g) + ')*x^' + str(g))

            i = g - 1
            while i >= 0:
                returned = returned + ',un' + str(i)
                polyU = polyU + ' + un' + str(i) + '*x^' + str(i)
                i = i - 1

            i = g - 1
            while i >= 0:
                returned = returned + ',vn' + str(i)
                polyV = polyV + ' + vn' + str(i) + '*x^' + str(i)
                i = i - 1

            # A split divisor is the 3-tuple <u, v, n>. The emitter used to write a
            # 4-tuple <u, v, ExactQuotient(f - v*(v+h),u), n> and read n from
            # index 3 of the parsed divisor, which is a stale generation: the
            # generators print NegativeReducedBasis, which returns <D[1],vhat,D[3]>,
            # and every deployed genus-3 tester writes <U1, V1, N1>. Reading index 3
            # of a 3-element list is an IndexError, so this path could not have
            # produced the deployed testers.
            #
            # AdaptedBasis inverts NegativeReducedBasis, recovering the divisor the
            # generator actually handed to Cantor. Comparing in the reduced basis is
            # what the deployed testers do, and it is also the only comparison the
            # formulas' output supports: they return v only up to degree g-1, with
            # the top two coefficients taken from Vn.
            def _divisor(d, k):
                self.magma.append('U' + k + ' := R! ' + d[0] + ';\n')
                self.magma.append('V' + k + ' := R! ' + d[1] + ';\n')
                self.magma.append('N' + k + ' := ' + d[2] + ';\n')

            if 'DBL' in case[0]:
                _divisor(case[1][2][0], '1')
                self.magma.append('D1 := <U1, V1, N1>;\n')
                self.magma.append('AD1 := AdaptedBasis(D1,f,h);\n')
                self.magma.append(returned + ',nN := DBL(U1,V1,N1,ccs);\n')
                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                self.magma.append('Cantor:= NegativeReducedBasis(Double(AD1,f,h,V),f,h);\n')
                self.magma.append('assert <nU,nV,nN> eq Cantor;\n\n')

            else:
                _divisor(case[1][2][0], '1')
                _divisor(case[1][2][1], '2')
                self.magma.append('D1 := <U1, V1, N1>;\n')
                self.magma.append('AD1 := AdaptedBasis(D1,f,h);\n')
                self.magma.append('D2 := <U2, V2, N2>;\n')
                self.magma.append('AD2 := AdaptedBasis(D2,f,h);\n')
                self.magma.append(returned + ', nN := ADD(U1,V1,N1,U2,V2,N2,ccs);\n')
                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                self.magma.append('Cantor:= NegativeReducedBasis(Add(AD1,AD2,f,h,V),f,h);\n')
                self.magma.append('assert <nU,nV,nN> eq Cantor;\n\n')

        else:
            self.magma.append('C:= HyperellipticCurve(f,h);\n')
            self.magma.append('J:= Jacobian(C);\n')
            self.magma.append('\n')
            
            returned = 'un' + str(g)
            polyU = 'un' + str(g) +'*x^' +str(g)

            i = g - 1
            while i >= 0:
                returned = returned + ',un' + str(i)
                polyU = polyU + ' + un' + str(i) +'*x^' + str(i)
                i = i-1
            
            i = g - 1
            polyV = 'vn' + str(i) +'*x^' + str(i)
            returned = returned + ',vn' + str(i)

            i = i-1
            while i >= 0:
                returned = returned + ',vn' + str(i)
                polyV = polyV + ' + vn' + str(i) +'*x^' + str(i)
                i = i-1




            if 'DBL' in case[0]:
                self.magma.append('U1 := R!' + case[1][2][0][0] + ';\n')
                self.magma.append('V1 := R!' + case[1][2][0][1] + ';\n')
                self.magma.append('D1 := J![U1,V1];\n')

                if self.file.FIELD == "nch2":
                    self.magma.append(returned + ' := DBL(U1,V1,f);\n')
                else:
                    self.magma.append(returned + ' := DBL(U1,V1,f,h);\n')

                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                self.magma.append('Cantor:= 2*D1;\n')
                self.magma.append('assert (' + polyU + ') eq Cantor[1] and (' + polyV + ') eq Cantor[2];\n')
                self.magma.append('\n\n')
                

            else:
                self.magma.append('U1 := R!' + case[1][2][0][0] + ';\n')
                self.magma.append('V1 := R!' + case[1][2][0][1] + ';\n')
                self.magma.append('U2 := R!' + case[1][2][1][0] + ';\n')
                self.magma.append('V2 := R!' + case[1][2][1][1] + ';\n')
                self.magma.append('D1 := J![U1,V1];\n')
                self.magma.append('D2 := J![U2,V2];\n')

                if self.file.FIELD == "nch2":
                    self.magma.append(returned + ' := ADD(U1,V1,U2,V2,f);\n')
                else:
                    self.magma.append(returned + ' := ADD(U1,V1,U2,V2,f,h);\n')
                
                self.magma.append('nU:= R! ' + polyU + ';\n')
                self.magma.append('nV:= R! ' + polyV + ';\n')
                self.magma.append('Cantor:= D1 + D2;\n')
                self.magma.append('assert (' + polyU + ') eq Cantor[1] and (' + polyV + ') eq Cantor[2];\n')
                self.magma.append('\n\n')


    def generateCode(self):
        self.magma.append('ADD_DEBUG := true;\n')
        self.magma.append('DBL_DEBUG := true;\n')

        if self.file.split:
            self.magma.append('UTL_DEBUG := false;\n')
            self.magma.append('load "' + self.file.ARITH + '";\n')
            self.magma.append('load "' + self.file.UTL + '";\n')
        else:
            self.magma.append('load "' + self.file.ARITH + '";\n')

        self.magma.append('load "' + self.file.DBL + '";\n')
        self.magma.append('load "' + self.file.ADD + '";\n')
        self.magma.append('"";' + '\n\n')

        # Sorted by branch label rather than by the order the search happened to
        # find them, so two runs that cover the same branches produce the same file
        # and a regenerated tester can be diffed against its predecessor.
        totalCases = 0
        for case in sorted(self.cases.items()):
            totalCases = totalCases + 1
            self.generateCase(case)

        self.magma.append('"\nTotal Cases: ' + str(totalCases) +'";\n')
        self.magma.append("quit;")
        



    def makeFile(self):
        with open(self.file.OUT, 'w+') as out:
            out.writelines(self.magma)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("field", choices=["arb", "nch2", "ch2"])
    ap.add_argument("curve", choices=["split", "ramified"])
    ap.add_argument("genus")
    ap.add_argument("--trials", type=int, default=400,
                    help="random curves to try (default 400)")
    ap.add_argument("--seed", type=int, default=1,
                    help="Magma seed, so the search is reproducible (default 1)")
    ap.add_argument("--divisors", type=int, default=1,
                    help="divisor pairs per curve, minus one (default 1)")
    ap.add_argument("--out", help="where to write the tester (default testerFiles/)")
    ap.add_argument("--log", help="where the generator writes its log "
                                  "(default a scratch file beside logs/)")
    ap.add_argument("--from-log", dest="fromLog",
                    help="parse an existing log instead of running Magma")
    ap.add_argument("--magma", default="../tools/magma-docker/magma.sh",
                    help="Magma command (default the container wrapper)")
    ap.add_argument("--allow-incomplete", action="store_true",
                    help="write the tester even if some branch was never reached")
    args = ap.parse_args(argv)

    fileInfo = FileInfo(args.field, args.curve, args.genus)
    if args.out:
        fileInfo.OUT = args.out

    gen = CaseGen(fileInfo, magmaCmd=[args.magma], trials=args.trials,
                  seed=args.seed, divisors=args.divisors)

    if args.fromLog:
        logPath = args.fromLog
    else:
        # Not fileInfo.LOG by default: whitebox/logs/ holds committed residue of the
        # last orchestrator run, and regenerating should not overwrite it.
        logPath = args.log or (fileInfo.LOG + ".new")
        gen.runGenerator(logPath)

    cases, missing = gen.parseLog(logPath)
    if missing and not args.allow_incomplete:
        raise SystemExit("refusing to write an incomplete tester; raise --trials, "
                         "or pass --allow-incomplete to accept the gap")
    if not cases:
        raise SystemExit("no cases parsed from %s" % logPath)

    Magma(fileInfo, cases)
    print("wrote %s: %d cases" % (fileInfo.OUT, len(cases)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
Magma(fileInfo, cases)