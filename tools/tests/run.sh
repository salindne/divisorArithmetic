#!/bin/bash
#
# Tests that test_all.sh actually detects failure.
#
# The suite it guards cannot be run here: Magma is licensed and absent from CI,
# and the local build cannot load the 9456-line genus-3 testers. So the gate is
# exercised against tools/tests/fake_magma.sh, which reproduces the output shapes
# real Magma produces -- including the important one, where a failed assertion
# stops the file mid-way and Magma still exits 0.
#
# Usage: tools/tests/run.sh

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FAKE="$ROOT/tools/tests/fake_magma.sh"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fails=0

# expect <expected exit> <mode> <description>
expect() {
    local want=$1 mode=$2 desc=$3
    local out got

    out=$(FAKE_MAGMA_MODE="$mode" MAGMA="$FAKE"  LOGDIR="$WORK/$mode" \
          "$ROOT/test_all.sh" 2>&1)
    got=$?

    if [ "$got" -eq "$want" ]; then
        printf 'ok    %-10s exit=%s  %s\n' "$mode" "$got" "$desc"
    else
        printf 'FAIL  %-10s exit=%s (wanted %s)  %s\n' "$mode" "$got" "$want" "$desc"
        printf '%s\n' "$out" | tail -20 | sed 's/^/        | /'
        fails=$((fails + 1))
    fi
}

echo "testing test_all.sh failure detection"
echo

expect 0 pass      'all testers clean'
expect 1 assert    'failed assertion, magma still exits 0'
expect 1 errors    'random tester reports "// Errors occured." (one r)'
expect 1 occurred  'random tester reports "// Errors occurred!!!" (two r, no stop)'
expect 1 truncated 'whitebox tester stops early with no error message'

echo

# The pass run must also have actually run the testers rather than trivially
# succeeding, and must report the remaining whitebox gaps as skipped.
#
# 30 and 0. The count reached 28 when the two genus-3 ramified whitebox testers
# were written, replacing what had been announced as deliberate skips, and 30 when
# the characteristic-2 genus-3 pair completed the six-cell matrix. Every family in
# the repository has a whitebox tester, which is why there is nothing left to skip.
# These numbers are meant to be updated when a tester is added -- that is the point
# of asserting them, so a tester cannot quietly vanish.
out=$(FAKE_MAGMA_MODE=pass MAGMA="$FAKE"  LOGDIR="$WORK/verify" \
      "$ROOT/test_all.sh" 2>&1)
npass=$(printf '%s\n' "$out" | sed -n 's/^  passed:  *\([0-9]*\)$/\1/p')
nskip=$(printf '%s\n' "$out" | sed -n 's/^  skipped: *\([0-9]*\)$/\1/p')

if [ "$npass" = "30" ]; then
    printf 'ok    %-10s 30 testers passed, not a vacuous success\n' 'coverage'
else
    printf 'FAIL  %-10s expected 30 passing testers, got "%s"\n' 'coverage' "$npass"
    fails=$((fails + 1))
fi

if [ "$nskip" = "0" ]; then
    printf 'ok    %-10s no skips left to hide: every family has a whitebox tester\n' 'skip'
else
    printf 'FAIL  %-10s expected 0 skips, got "%s"\n' 'skip' "$nskip"
    fails=$((fails + 1))
fi

echo
if [ "$fails" -gt 0 ]; then
    echo "$fails check(s) failed"
    exit 1
fi
echo 'all checks passed'
