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
#   LOGDIR=/somewhere ./test_all.sh      # where per-tester logs are written
#
# Exits 0 only if every tester ran to completion and reported no errors;
# otherwise prints a summary and exits 1.
#
# Magma is commercial software and is not part of this repository; see README.md
# "Requirements and how to run".
#
# Runnable from any working directory: all paths are resolved against the
# location of this script, not the caller's cwd.
#
# Kept compatible with bash 3.2, which is what /bin/bash is on macOS.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAGMA="${MAGMA:-magma}"
SLEEP="${SLEEP:-1}"
LOGDIR="${LOGDIR:-$ROOT/.test-logs}"

# ---------------------------------------------------------------------------
# preflight
# ---------------------------------------------------------------------------

# If MAGMA is given as a path rather than a bare command name, make it absolute.
# This script cds into each formula directory, so a relative wrapper path such as
# MAGMA=./run-magma.sh would resolve during preflight and then fail with exit 127
# on every single tester.
case "$MAGMA" in
    */*) MAGMA="$(cd "$(dirname "$MAGMA")" && pwd)/$(basename "$MAGMA")" ;;
esac

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

mkdir -p "$LOGDIR" || exit 1
FAILLOG="$LOGDIR/failures.txt"
SKIPLOG="$LOGDIR/skipped.txt"
: > "$FAILLOG"
: > "$SKIPLOG"
PASSED=0

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

# run_test <whitebox|random> <file>
#
# Magma cannot be gated on its exit status: it returns 0 even when an assertion
# fails ("Runtime error in assert: Assertion failed") and simply stops reading
# the file. A truncated run is therefore indistinguishable from a clean one by
# exit code alone, which is why classification is done by parsing the output and
# why the terminal-marker check matters as much as the error grep.
run_test() {
    local kind=$1 file=$2
    local rel="${PWD#"$ROOT"/}"
    local tag="${rel//\//_}__${file%.mag}"
    local log="$LOGDIR/$tag.log"
    local status why=''

    "$MAGMA" "$file" 2>&1 | tee "$log"
    status=${PIPESTATUS[0]}

    if [ "$status" -ne 0 ]; then
        why="magma exited $status"
    elif grep -qE 'Runtime error|Assertion failed' "$log"; then
        why="runtime error or failed assertion"
    elif [ "$kind" = whitebox ] && ! grep -q 'Total Cases:' "$log"; then
        why="stopped before the end (no 'Total Cases:' line)"
    elif [ "$kind" = random ] && grep -q '// Errors occured\.' "$log"; then
        why="tester reported errors"
    elif [ "$kind" = random ] && ! grep -q '// No errors\.' "$log"; then
        why="stopped before the end (no '// No errors.' line)"
    fi

    if [ -n "$why" ]; then
        printf '%s/%s: %s\n' "$rel" "$file" "$why" >> "$FAILLOG"
        printf '\n*** FAIL: %s -- %s\n    log: %s\n\n' "$file" "$why" "$log"
    else
        PASSED=$((PASSED + 1))
        printf '\n    pass: %s\n\n' "$file"
    fi
}

# skip_test <what> <reason>
skip_test() {
    printf '%s: %s\n' "$1" "$2" >> "$SKIPLOG"
    printf 'SKIP: %s -- %s\n\n' "$1" "$2"
}

# run_family <field label> <whitebox file|-> <random file>
run_family() {
    local label=$1 whitebox=$2 random=$3

    if [ "$whitebox" = "-" ]; then
        skip_test "${PWD#"$ROOT"/} whitebox over $label" \
                  "no such tester exists in this repository"
    else
        boxed "White Box Testing Over $label"
        pause 1
        run_test whitebox "$whitebox"
    fi

    boxed "Random Testing Over $label"
    pause 1
    run_test random "$random"

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
# summary
# ---------------------------------------------------------------------------

t=$SECONDS
h=$(( t / 3600 )); m=$(( (t % 3600) / 60 )); s=$(( t % 60 ))
if   (( h > 0 )); then elapsed="${h} hour(s), ${m} minute(s) and ${s} second(s)"
elif (( m > 0 )); then elapsed="${m} minute(s) and ${s} second(s)"
else                   elapsed="${s} second(s)"
fi

# wc -l, not `grep -c . || echo 0`: grep exits 1 on no match, so the fallback
# fired in addition to grep's own "0" and produced a two-line count.
nfail=$(wc -l < "$FAILLOG" | tr -d '[:space:]')
nskip=$(wc -l < "$SKIPLOG" | tr -d '[:space:]')

heading 'SUMMARY'
printf '  passed:  %s\n  failed:  %s\n  skipped: %s\n  elapsed: %s\n  logs:    %s\n\n' \
       "$PASSED" "$nfail" "$nskip" "$elapsed" "$LOGDIR"

if [ "$nskip" -gt 0 ]; then
    echo '  Skipped:'
    sed 's/^/    - /' "$SKIPLOG"
    echo
fi

if [ "$nfail" -gt 0 ]; then
    echo '  Failed:'
    sed 's/^/    - /' "$FAILLOG"
    echo
    echo 'TESTING FAILED'
    echo
    exit 1
fi

echo 'All testing completed successfully'
echo
