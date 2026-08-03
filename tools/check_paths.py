#!/usr/bin/env python3
"""Check that every file this repository references actually exists.

Stale paths are the single largest class of defect in this repository: broken
`load` statements in Magma files and broken `open()` calls in Python scripts,
several of which silently disabled whole tools. This catches new ones.

Known-broken paths are listed in tools/known_broken_paths.txt so the check can
pass today while still failing on anything newly broken. That file is debt with
a name attached; it should only ever shrink.

Usage:
    tools/check_paths.py              # fail on any unlisted broken path
    tools/check_paths.py --strict     # also fail if a listed path now resolves
    tools/check_paths.py --list       # print every broken path, allowlist format
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST = ROOT / "tools" / "known_broken_paths.txt"

# Magma: load "target";
MAG_LOAD = re.compile(r'load\s+"([^"]+)"')
# Python: open('target'  /  open("target"
PY_OPEN = re.compile(r"""open\(\s*['"]([^'"]+)['"]""")


def tracked(suffix: str) -> list[Path]:
    """Files git tracks with the given suffix, excluding the rust submodule."""
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", f"*{suffix}"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return [ROOT / p for p in out if not p.startswith("rust/")]


def base_dir(path: Path) -> Path:
    """The directory a file's relative references resolve against.

    Normally the file's own directory. The whitebox case generators are the
    exception: whitebox_auto_NEG.py drives them from whitebox/, so their paths
    are relative to that.
    """
    rel = path.relative_to(ROOT)
    if rel.parts[:2] == ("whitebox", "genFiles"):
        return ROOT / "whitebox"
    return path.parent


def is_relocatable(path: Path) -> bool:
    """True for files whose references are not meant to resolve where they sit.

    whitebox/testerFiles/ holds generator *output*. A generated tester is meant
    to be copied into the formula directory it tests and run from there, so its
    `load "g2Formulas/..."` lines resolve at the destination, not here. Checking
    them in place would report two dozen phantom breakages.
    """
    return path.relative_to(ROOT).parts[:2] == ("whitebox", "testerFiles")


def references() -> list[tuple[str, str, Path]]:
    """Every (source file, referenced target, resolved absolute path)."""
    found = []
    for path in tracked(".mag"):
        if is_relocatable(path):
            continue
        text = path.read_text(errors="replace")
        for target in MAG_LOAD.findall(text):
            found.append((str(path.relative_to(ROOT)), target,
                          base_dir(path) / target))
    for path in tracked(".py"):
        text = path.read_text(errors="replace")
        for target in PY_OPEN.findall(text):
            # Only path-shaped arguments; skip mode strings and format templates.
            if not re.search(r"[/.]", target) or "%" in target or "{" in target:
                continue
            found.append((str(path.relative_to(ROOT)), target,
                          base_dir(path) / target))
    return found


def load_allowlist() -> set[str]:
    if not ALLOWLIST.exists():
        return set()
    entries = set()
    for line in ALLOWLIST.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            entries.add(line)
    return entries


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    listing = "--list" in argv

    allow = load_allowlist()
    broken, unexpected_ok = [], []

    for source, target, resolved in references():
        key = f"{source}::{target}"
        if not resolved.exists():
            if key not in allow:
                broken.append((key, source, target))
        elif key in allow:
            unexpected_ok.append(key)

    if listing:
        for key, _, _ in broken:
            print(key)
        for key in sorted(allow):
            print(key)
        return 0

    rc = 0
    if broken:
        print(f"{len(broken)} broken path reference(s) not in the allowlist:\n")
        for key, source, target in broken:
            print(f"  {source}")
            print(f"      load/open -> {target}   (does not exist)")
        print(f"\nIf a reference is knowingly broken, add it to")
        print(f"{ALLOWLIST.relative_to(ROOT)} with a reason.")
        rc = 1

    if unexpected_ok:
        msg = (f"\n{len(unexpected_ok)} allowlisted path(s) now resolve; "
               f"remove them from {ALLOWLIST.relative_to(ROOT)}:")
        print(msg)
        for key in unexpected_ok:
            print(f"  {key}")
        if strict:
            rc = 1

    if rc == 0 and not unexpected_ok:
        total = len(references())
        print(f"all {total} path references resolve "
              f"({len(allow)} known-broken, allowlisted)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
