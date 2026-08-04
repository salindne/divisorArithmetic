#!/usr/bin/env python3
"""Patch QEMU's linux-user target_mremap so that shrinking never relocates.

QEMU takes an unconditional relocate path whenever MREMAP_MAYMOVE is set: it
picks a fresh VMA with mmap_find_vma() and forces MREMAP_FIXED. Native Linux
only moves a mapping when it has to grow it and cannot do so in place; a shrink
always keeps its address, with the kernel simply unmapping the tail.

Guests that check mremap's return address against the address they passed in
therefore fail under emulation. Magma is one: its memory manager aborts with
"memi_reduce_block_mmap: block moved" when it shrinks a block, which makes any
sufficiently large Magma function impossible to load.

This routes new_size <= old_size through an in-place shrink.
"""

import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "linux-user/mmap.c"

OLD = """    } else if (flags & MREMAP_MAYMOVE) {
        abi_ulong mmap_start;

        mmap_start = mmap_find_vma(0, new_size, TARGET_PAGE_SIZE);

        if (mmap_start == -1) {
            errno = ENOMEM;
            host_addr = MAP_FAILED;
        } else {
            host_addr = mremap(g2h_untagged(old_addr), old_size, new_size,
                               flags | MREMAP_FIXED,
                               g2h_untagged(mmap_start));
            if (reserved_va) {
                mmap_reserve_or_unmap(old_addr, old_size);
            }
        }
    } else {"""

NEW = """    } else if (flags & MREMAP_MAYMOVE && new_size <= old_size) {
        /*
         * A shrink never needs to move.  Linux unmaps the tail and returns the
         * original address; relocating it unconditionally breaks guests that
         * compare mremap's result against the address they passed in.
         */
        host_addr = mremap(g2h_untagged(old_addr), old_size, new_size,
                           flags & ~MREMAP_MAYMOVE);
        if (host_addr != MAP_FAILED && reserved_va && old_size > new_size) {
            mmap_reserve_or_unmap(old_addr + new_size, old_size - new_size);
        }
    } else if (flags & MREMAP_MAYMOVE) {
        abi_ulong mmap_start;

        mmap_start = mmap_find_vma(0, new_size, TARGET_PAGE_SIZE);

        if (mmap_start == -1) {
            errno = ENOMEM;
            host_addr = MAP_FAILED;
        } else {
            host_addr = mremap(g2h_untagged(old_addr), old_size, new_size,
                               flags | MREMAP_FIXED,
                               g2h_untagged(mmap_start));
            if (reserved_va) {
                mmap_reserve_or_unmap(old_addr, old_size);
            }
        }
    } else {"""

src = open(PATH).read()
if OLD not in src:
    sys.exit(f"error: expected MREMAP_MAYMOVE block not found in {PATH}")
if src.count(OLD) != 1:
    sys.exit(f"error: expected exactly one match, found {src.count(OLD)}")
open(PATH, "w").write(src.replace(OLD, NEW))
print(f"patched {PATH}: shrink now stays in place")
