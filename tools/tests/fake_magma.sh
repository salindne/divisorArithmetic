#!/bin/bash
#
# Stands in for the `magma` binary so test_all.sh's pass/fail classification can
# be tested without Magma, which is licensed, absent from CI, and on some builds
# unable to load the genus-3 testers at all.
#
# It reproduces the output shapes real Magma produces, selected by FAKE_MAGMA_MODE:
#
#   pass       every tester runs to completion and reports no errors
#   assert     one whitebox tester hits a failed assertion and stops mid-file,
#              exiting 0 -- the case that makes exit-status gating useless
#   errors     one random tester completes but reports "// Errors occured."
#   occurred   same, but with the genus-3 ramified testers' spelling,
#              "// Errors occurred!!!" -- two r's, no full stop. A separate mode
#              because matching only the one-r spelling left that check dead.
#   truncated  one whitebox tester stops early with no error message at all
#
# Usage: FAKE_MAGMA_MODE=assert ./fake_magma.sh <tester.mag>

set -u

mode="${FAKE_MAGMA_MODE:-pass}"
file="${1:?no tester file given}"

case "$file" in
    *whiteBox_tester.mag|*whitebox_tester.mag) kind=whitebox ;;
    *_random.mag)                              kind=random   ;;
    *)                                         kind=other    ;;
esac

# Which tester the failure modes target. Deliberately not the first one run, so
# a test that only checks the first result cannot pass by accident.
TARGET_WHITEBOX='nch2_splitG2_whiteBox_tester.mag'
TARGET_RANDOM='ch2_ramifiedG2_random.mag'
# The genus-3 ramified testers use the other spelling, so they get their own target.
TARGET_RAMIFIED_G3='nch2_ramifiedG3_random.mag'

emit_whitebox_header() {
    echo "// Whitebox testing of explicit formulas."
    echo "Case ADD00: passed"
    echo "Case ADD01: passed"
}

case "$kind:$mode" in
    whitebox:pass|whitebox:errors|whitebox:occurred)
        emit_whitebox_header
        echo '
Total Cases: 22'
        ;;
    whitebox:assert)
        emit_whitebox_header
        if [ "$file" = "$TARGET_WHITEBOX" ]; then
            # Real Magma prints this, stops reading the file, and still exits 0.
            echo 'Case ADD02:'
            echo ''
            echo '>> assert Divisors_Equal(D3, D3check);'
            echo '   ^'
            echo 'Runtime error in assert: Assertion failed'
            exit 0
        fi
        echo '
Total Cases: 22'
        ;;
    whitebox:truncated)
        emit_whitebox_header
        # No error, no terminal marker: the shape of a run killed externally.
        [ "$file" = "$TARGET_WHITEBOX" ] && exit 0
        echo '
Total Cases: 22'
        ;;
    random:occurred)
        echo '// Random testing of explicit formulas.'
        if [ "$file" = "$TARGET_RAMIFIED_G3" ]; then
            echo '
// Errors occurred!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        else
            echo '
// No errors.'
        fi
        ;;
    random:pass|random:assert|random:truncated)
        echo '// Random testing of explicit formulas.'
        echo '// - 2500 divisors per trial.'
        echo '
// No errors.'
        ;;
    random:errors)
        echo '// Random testing of explicit formulas.'
        echo '// - 2500 divisors per trial.'
        if [ "$file" = "$TARGET_RANDOM" ]; then
            echo '
// Errors occured.'
        else
            echo '
// No errors.'
        fi
        ;;
    *)
        echo "fake_magma: unhandled kind=$kind mode=$mode for $file" >&2
        exit 2
        ;;
esac

exit 0
