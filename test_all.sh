#!/bin/bash
#
# Runs every explicit-formula tester in this repository: whitebox testers, which
# exercise one deliberately constructed case per computation path, and random
# testers, which exercise many random divisor operations over a fixed list of
# small fields.
#
# Usage:
#   ./test_all.sh                        # requires `magma` on PATH
#   MAGMA=./run-magma.sh ./test_all.sh   # run Magma through the Docker wrapper
#   SLEEP=0 ./test_all.sh                # skip the decorative pauses
#
# Magma is commercial software and is not part of this repository; see README.md
# "Requirements and how to run".
#
# Runnable from any working directory: all paths are resolved against the
# location of this script, not the caller's cwd.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAGMA="${MAGMA:-magma}"
SLEEP="${SLEEP:-1}"

# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------

if ! command -v "$MAGMA" >/dev/null 2>&1 && [ ! -x "$MAGMA" ]; then
    cat >&2 <<EOF
error: Magma not found as '$MAGMA'.

Magma is commercial software and is not included in this repository. Either put
it on your PATH, or build the local Docker image and run through the wrapper:

    docker build -t magma-env .
    MAGMA=./run-magma.sh ./test_all.sh

See README.md "Requirements and how to run".
EOF
    exit 127
fi

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

# boxed <text> -- the dashed banner style used throughout this script
boxed() {
    local text="  $1  "
    local rule
    rule=$(printf '%*s' "${#text}" '' | tr ' ' '-')
    printf '%s\n%s\n%s\n\n' "$rule" "$text" "$rule"
}

# heading <text> -- the wider banner used for top-level sections
heading() {
    local text="- $1 -"
    local rule
    rule=$(printf '%*s' "${#text}" '' | tr ' ' '-')
    printf '\n\n\n%s\n%s\n%s\n\n\n' "$rule" "$text" "$rule"
}

# pause <seconds> -- decorative, suppressed entirely by SLEEP=0
pause() {
    [ "$SLEEP" -eq 0 ] 2>/dev/null && return 0
    sleep "$1"
}

# run_test <file> -- run one tester in the current directory
run_test() {
    "$MAGMA" "$1"
}

# skip_test <file> <reason>
skip_test() {
    printf 'SKIP: %s -- %s\n\n' "$1" "$2"
}

# run_family <field label> <whitebox file|-> <random file>
run_family() {
    local label=$1 whitebox=$2 random=$3

    if [ "$whitebox" = "-" ]; then
        skip_test "whitebox tester over $label" \
                  "no such tester exists in this repository"
    else
        boxed "White Box Testing Over $label"
        pause 1
        run_test "$whitebox"
        echo
    fi

    boxed "Random Testing Over $label"
    pause 1
    run_test "$random"
    echo

    boxed "Finished Testing Over $label"
    echo
    pause 3
}

ARB='Arbitrary Fields'
CH2='Characteristic 2 Fields'
NCH2='Characteristic !=2 Fields'

# ---------------------------------------------------------------------------
# genus 2
# ---------------------------------------------------------------------------

heading 'TESTING EXPLICIT GENUS 2 ARITHMETIC'

heading 'TESTING EXPLICIT GENUS 2 BALANCED SPLIT MODEL ARITHMETIC (Positive Reduced)'
pause 5
cd "$ROOT/g2/splitModel/posReduced" || exit 1
run_family "$ARB"  arb_splitG2_whiteBox_tester.mag  arb_splitG2_random.mag
run_family "$CH2"  ch2_splitG2_whiteBox_tester.mag  ch2_splitG2_random.mag
run_family "$NCH2" nch2_splitG2_whiteBox_tester.mag nch2_splitG2_random.mag

heading 'TESTING EXPLICIT GENUS 2 BALANCED SPLIT MODEL ARITHMETIC (Negative Reduced)'
pause 5
cd "$ROOT/g2/splitModel/negReduced" || exit 1
run_family "$ARB"  arb_splitG2_whiteBox_tester.mag  arb_splitG2_random.mag
run_family "$CH2"  ch2_splitG2_whiteBox_tester.mag  ch2_splitG2_random.mag
run_family "$NCH2" nch2_splitG2_whiteBox_tester.mag nch2_splitG2_random.mag

heading 'TESTING EXPLICIT GENUS 2 RAMIFIED MODEL ARITHMETIC'
pause 5
cd "$ROOT/g2/ramifiedModel" || exit 1
run_family "$ARB"  arb_ramifiedG2_whiteBox_tester.mag  arb_ramifiedG2_random.mag
run_family "$CH2"  ch2_ramifiedG2_whiteBox_tester.mag  ch2_ramifiedG2_random.mag
run_family "$NCH2" nch2_ramifiedG2_whiteBox_tester.mag nch2_ramifiedG2_random.mag

# ---------------------------------------------------------------------------
# genus 3
# ---------------------------------------------------------------------------

heading 'TESTING EXPLICIT GENUS 3 ARITHMETIC'

heading 'TESTING EXPLICIT GENUS 3 BALANCED SPLIT MODEL ARITHMETIC (Negative Reduced)'
pause 5
cd "$ROOT/g3/splitModel/negReduced" || exit 1
run_family "$ARB"  arb_splitG3_whitebox_tester.mag  arb_splitG3_random.mag

# No ch2 genus-3 whitebox tester exists: the family has 405 labelled branches
# and none of them is covered by a constructed case. The generator that would
# produce it (whitebox/genFiles/ch2_splitG3_WB_gen.mag) has stale load paths.
# Announced rather than silently omitted.
run_family "$CH2"  -                                ch2_splitG3_random.mag

run_family "$NCH2" nch2_splitG3_whitebox_tester.mag nch2_splitG3_random.mag

# ---------------------------------------------------------------------------
# done
# ---------------------------------------------------------------------------

t=$SECONDS
h=$(( t / 3600 )); m=$(( (t % 3600) / 60 )); s=$(( t % 60 ))
if   (( h > 0 )); then elapsed="${h} hour(s), ${m} minute(s) and ${s} second(s)"
elif (( m > 0 )); then elapsed="${m} minute(s) and ${s} second(s)"
else                   elapsed="${s} second(s)"
fi
printf 'All testing completed in %s\n\n\n' "$elapsed"
