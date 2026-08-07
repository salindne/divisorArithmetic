#!/bin/bash
#
# Runs Magma inside the patched container, mounting the repository so relative
# `load` statements in a tester resolve as they would locally.
#
# The mount is the repository root, not the current directory, and the working
# directory inside the container mirrors where you invoked this from. Mounting
# $PWD instead would work only at the root: the whitebox generators live in
# whitebox/ and load "../g3/splitModel/negReduced/...", which escapes a mount
# rooted at whitebox/. That never surfaced because test_all.sh only ever runs
# from the root.
#
# Build the image first, from the repository root with magma.tar.xz present:
#     docker build -f tools/magma-docker/Dockerfile -t magma-qemufix .
#
# Usage:
#     tools/magma-docker/magma.sh some_tester.mag
#     MAGMA=tools/magma-docker/magma.sh ./test_all.sh
#     (from whitebox/)  ../tools/magma-docker/magma.sh genFiles/foo_gen.mag
#
# Override the mount root with MAGMA_MOUNT for a tree outside this repository.
# Forward variables into the container by naming them in MAGMA_ENV, which the
# whitebox generators read via GetEnv:
#     MAGMA_ENV="WB_TRIALS WB_SEED" WB_TRIALS=400 ... magma.sh gen.mag
#
# See README.md in this directory for why the image needs a patched emulator.

set -uo pipefail

IMAGE="${MAGMA_IMAGE:-magma-qemufix}"

# Repository root, so a caller in a subdirectory can still load "../".
#
# Both paths are resolved with `pwd -P`. Without that they can disagree over a
# symlinked prefix -- on macOS /tmp is a symlink to /private/tmp, and git reports
# one while the shell reports the other -- which would make the containment test
# below fail for a directory that is plainly inside the repository.
if [ -n "${MAGMA_MOUNT:-}" ]; then
    MOUNT=$(cd "$MAGMA_MOUNT" && pwd -P)
elif TOP=$(git rev-parse --show-toplevel 2>/dev/null) && [ -n "$TOP" ]; then
    MOUNT=$(cd "$TOP" && pwd -P)
else
    MOUNT=$(pwd -P)
fi

HERE=$(pwd -P)

# Where we are relative to the mount, so `load "genFiles/x.mag"` still works.
case "$HERE" in
    "$MOUNT") SUBDIR="" ;;
    "$MOUNT"/*) SUBDIR="${HERE#"$MOUNT"/}" ;;
    *) echo "error: $HERE is not inside the mount root $MOUNT" >&2; exit 2 ;;
esac

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    cat >&2 <<EOF
error: docker image '$IMAGE' not found.

Build it from the repository root, with magma.tar.xz present there:

    docker build -f tools/magma-docker/Dockerfile -t $IMAGE .

magma.tar.xz is licensed commercial software and is not part of this repository.
EOF
    exit 127
fi

ENV_ARGS=()
for name in ${MAGMA_ENV:-}; do
    ENV_ARGS+=(-e "$name")
done

exec docker run --rm \
    -v "$MOUNT":/workspace \
    -w "/workspace${SUBDIR:+/$SUBDIR}" \
    "${ENV_ARGS[@]+"${ENV_ARGS[@]}"}" \
    --entrypoint /usr/local/bin/magma-patched \
    "$IMAGE" "$@"
