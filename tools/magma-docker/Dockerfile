# Magma in a container, with a patched CPU emulator.
#
# Build from the REPOSITORY ROOT, which must contain magma.tar.xz:
#     docker build -f tools/magma-docker/Dockerfile -t magma-qemufix .
#
# magma.tar.xz is licensed commercial software. It is never committed, and an
# image built from it must never be pushed to any registry.
#
# Without the patch applied below, 17 of this repository's 23 testers abort with
# "memi_reduce_block_mmap: block moved" while loading a formula file. See
# README.md in this directory.

# ---------------------------------------------------------------------------
# 1. Build qemu-i386 with the mremap fix.
#    Only the i386-linux-user target, which keeps this to a few minutes.
# ---------------------------------------------------------------------------
FROM ubuntu:24.04 AS qemu

ARG QEMU_VERSION=8.2.2

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        build-essential meson ninja-build python3 python3-venv pkg-config \
        libglib2.0-dev flex bison curl xz-utils ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN curl -sSL --max-time 600 \
        "https://download.qemu.org/qemu-${QEMU_VERSION}.tar.xz" -o qemu.tar.xz \
    && tar -xJf qemu.tar.xz \
    && rm qemu.tar.xz

COPY tools/magma-docker/patch-qemu-mremap.py /src/patch-qemu-mremap.py
RUN python3 /src/patch-qemu-mremap.py "/src/qemu-${QEMU_VERSION}/linux-user/mmap.c"

RUN cd "qemu-${QEMU_VERSION}" \
    && ./configure \
        --target-list=i386-linux-user \
        --disable-system --disable-tools --disable-docs \
        --disable-guest-agent --disable-gtk --disable-sdl --disable-vnc \
        --disable-curses --disable-libssh --disable-vte \
    && ninja -C build qemu-i386 \
    && install -m 0755 build/qemu-i386 /usr/local/bin/qemu-i386-patched \
    && /usr/local/bin/qemu-i386-patched --version

# ---------------------------------------------------------------------------
# 2. Unpack Magma. Self-contained: needs only magma.tar.xz in the build context.
# ---------------------------------------------------------------------------
FROM ubuntu:24.04 AS magma

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        xz-utils \
    && rm -rf /var/lib/apt/lists/*

COPY magma.tar.xz /tmp/magma.tar.xz
RUN mkdir -p /opt/magma \
    && tar -xJf /tmp/magma.tar.xz -C /opt/magma \
    && rm /tmp/magma.tar.xz \
    && sed -i 's|ROOT=~/Applications/magma|ROOT=/opt/magma|' /opt/magma/magma

# ---------------------------------------------------------------------------
# 3. Runtime. Ubuntu 24.04 to match the glibc the emulator was linked against;
#    magma.exe is a static i386 binary and is indifferent to the host glibc.
# ---------------------------------------------------------------------------
FROM ubuntu:24.04

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        libglib2.0-0t64 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=qemu  /usr/local/bin/qemu-i386-patched /usr/local/bin/qemu-i386-patched
COPY --from=magma /opt/magma /opt/magma

# Equivalent of Magma's own launcher, but routed through the patched emulator
# rather than the host's binfmt_misc handler.
RUN printf '%s\n' \
    '#!/bin/sh' \
    'ROOT=/opt/magma' \
    'export MAGMAPASSFILE="$ROOT/magmapassfile"' \
    'export MAGMA_HELP_DIR="$ROOT/InternalHelp"' \
    'export MAGMA_HTML_DIR="$ROOT/doc/html"' \
    'export MAGMA_SYSTEM_SPEC="$ROOT/package/spec"' \
    'export MAGMA_LIBRARY_ROOT="$ROOT/libs"' \
    'export MAGMA_LIBRARIES="examples:galpols:intro:isolgps:matgps:pergps:simgps:solgps"' \
    'exec /usr/local/bin/qemu-i386-patched "$ROOT/magma.exe" "$@"' \
    > /usr/local/bin/magma-patched \
    && chmod +x /usr/local/bin/magma-patched

WORKDIR /workspace
CMD ["/usr/local/bin/magma-patched"]
