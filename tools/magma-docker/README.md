# Running Magma in Docker on Apple Silicon

A reproducible container for the Magma build this project uses, including a patch
to the CPU emulator without which most of this repository's test suite cannot run
at all.

You supply `magma.tar.xz`. It is licensed commercial software, is never committed,
and the resulting image must never be pushed to a registry.

## Quick start

```sh
# from the repository root, with magma.tar.xz present there
docker build -f tools/magma-docker/Dockerfile -t magma-qemufix .
tools/magma-docker/magma.sh -v                       # smoke test
MAGMA=tools/magma-docker/magma.sh ./test_all.sh      # the whole suite
```

## The problem this solves

Before the patch, 17 of the repository's 23 testers could not be loaded. Every one
died the same way, part-way through reading a formula file:

```
memi_reduce_block_mmap: block moved

Magma: Internal error
```

It was tempting to read that as "this old Magma cannot handle our larger formulas",
because the failures correlated with size: files whose longest single function was
265-267 lines loaded, and 351 lines and up did not. Genus-2 ramified worked;
genus-2 split and all of genus 3 did not. That reading was wrong.

## What is actually happening

`magma.exe` is a **statically linked 32-bit i386** binary from 2015. On Apple
Silicon there is no way to run it natively:

- Rosetta translates x86-64 only and cannot run i386 at all.
- So the Docker VM's `binfmt_misc` routes i386 through **`qemu-i386`**, QEMU's
  user-mode emulator, which translates guest syscalls to host ones.

Running the failing load under `QEMU_STRACE=1` shows the exact moment:

```
mmap2(NULL, 98304, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, ...) = 0x411c6000
mremap(0x411c6000, 98304, 32768, MREMAP_MAYMOVE)                        = 0x40a40000
memi_reduce_block_mmap: block moved
```

Magma **shrinks** a block from 96 KB to 32 KB and checks that the mapping stayed
put. On Linux it always does: shrinking `mremap` unmaps the tail and returns the
original address. The kernel only ever relocates a mapping it has to *grow* and
cannot grow in place.

QEMU returned a different address, so Magma concluded its heap had been corrupted
and aborted. From `linux-user/mmap.c`:

```c
} else if (flags & MREMAP_MAYMOVE) {
    abi_ulong mmap_start;

    mmap_start = mmap_find_vma(0, new_size, TARGET_PAGE_SIZE);   /* always a NEW address */

    if (mmap_start == -1) {
        errno = ENOMEM;
        host_addr = MAP_FAILED;
    } else {
        host_addr = mremap(g2h_untagged(old_addr), old_size, new_size,
                           flags | MREMAP_FIXED,                 /* forces the move */
                           g2h_untagged(mmap_start));
```

Whenever the guest passes `MREMAP_MAYMOVE`, QEMU picks a fresh region and forces
the move with `MREMAP_FIXED`, including for shrinks, where the kernel would not
have moved anything. `MREMAP_MAYMOVE` is permission to move, not a request to.

Note the third branch of that same function, for calls with neither flag, already
shrinks in place correctly. The patch in
[patch-qemu-mremap.py](patch-qemu-mremap.py) routes `new_size <= old_size` to that
behaviour: shrink with plain `mremap`, and account for the released tail rather
than the whole mapping.

## What it fixes

| | before | after |
|---|---|---|
| genus-2 ramified (longest fn 265-267 lines) | loads | loads |
| genus-2 split, both bases (351-386) | **aborts** | loads |
| genus-3 split (547-2288) | **aborts** | loads |

The 2288-line `arb_splitG3_ADD` function loads in well under a second. Function
length was never the cause; it only determined whether Magma's allocator happened
to need a shrink.

## Things that do not work, so nobody retries them

- `QEMU_RESERVED_VA` at any value, `QEMU_GUEST_BASE`, `QEMU_STACK_SIZE`. The
  relocation is unconditional and no tunable reaches it.
- A newer emulator. QEMU 8.2.2 behaves identically to the one Docker Desktop
  ships; the code above is long-standing, not a regression.
- `MAGMA_MEMORY_EXTENSION_SIZE`, across four orders of magnitude. It does not
  affect this allocation path.
- `LD_PRELOAD` to intercept `mremap` in the guest. `magma.exe` is statically
  linked, so there is no dynamic linker to hook.
- Rebuilding for `linux/amd64`, or Ubuntu 22.04 / 18.04 / i386 base images.
  Disabling ASLR, unlimited stack, legacy VA layout, Magma's own `-m` and `-S`.

The remaining alternative, if the patch is ever unavailable, is full-system x86
emulation, where a real guest kernel does `mremap` correctly. It also emulates the
whole CPU, so expect a large slowdown that this patch avoids.

## Upstream

The patch is a behavioural fix to QEMU, not something specific to this project:
any guest that compares `mremap`'s result against the address it passed in will
misbehave the same way. It is worth reporting to qemu-devel.
