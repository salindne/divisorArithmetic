#!/bin/bash
#
# Runs Magma inside the patched container, mounting the current directory so
# relative `load` statements in a tester resolve as they would locally.
#
# Build the image first, from the repository root with magma.tar.xz present:
#     docker build -f tools/magma-docker/Dockerfile -t magma-qemufix .
#
# Usage:
#     tools/magma-docker/magma.sh some_tester.mag
#     MAGMA=tools/magma-docker/magma.sh ./test_all.sh
#
# See README.md in this directory for why the image needs a patched emulator.

set -uo pipefail

IMAGE="${MAGMA_IMAGE:-magma-qemufix}"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    cat >&2 <<EOF
error: docker image '$IMAGE' not found.

Build it from the repository root, with magma.tar.xz present there:

    docker build -f tools/magma-docker/Dockerfile -t $IMAGE .

magma.tar.xz is licensed commercial software and is not part of this repository.
EOF
    exit 127
fi

exec docker run --rm \
    -v "$(pwd)":/workspace \
    -w /workspace \
    --entrypoint /usr/local/bin/magma-patched \
    "$IMAGE" "$@"
