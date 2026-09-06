#!/usr/bin/env python3
"""Generate FORMULA-MANIFEST.json, the inventory of tracked formula files.

Derived from `verification/driver.py`'s `discover_families()`, the same walk the
verification harness tests against, so the manifest and the gates cannot
disagree about what exists.  Hand-counted copies of this answer have gone stale
more than once.

Tracked files only, so the manifest is a function of the git index and is
byte-identical in every clone.  No line counts, sizes or hashes: they would put
this file in the diff of every formula commit, and the figure of record for a
formula is its operation count, which `verification/opcount.py` measures.

Usage:
    tools/gen_manifest.py             # write FORMULA-MANIFEST.json
    tools/gen_manifest.py --check     # fail if the committed manifest is stale
    tools/gen_manifest.py --out PATH  # write elsewhere
"""

from __future__ import annotations

import difflib
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

# So importing `driver` leaves no verification/__pycache__ behind.
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "FORMULA-MANIFEST.json"

sys.path.insert(0, str(ROOT / "verification"))
import driver as D  # noqa: E402  (path must be set first)

# The competitors the timing experiments measure against.  Discovery cannot see
# them: they are named for their authors rather than
# `<class>_<model>G<genus>_<op>.mag`, under a `timings/` path it excludes.
# Matched on the directory name at any depth, so one filed under a new parent
# still lands in the manifest.
COMPETITOR_DIR = "previousBest"

# Every canonical formula file lives in one of these.  Used only to detect a
# file discovery did not claim; see `unclaimed`.
FORMULA_DIRS = ("g2Formulas", "g3Formulas")

# `rust/` is a submodule and owns its own tree, as in the two sibling tools.
SUBMODULE_PREFIXES = ("rust/",)


def in_submodule(relpath: str) -> bool:
    return relpath.startswith(SUBMODULE_PREFIXES)


def tracked() -> set[str]:
    """Every path git tracks, repository-relative, outside the submodule."""
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    return {p for p in out if p and not in_submodule(p)}


def rel(path) -> str:
    """A repository-relative path with forward slashes, unresolved."""
    p = Path(path)
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def unclaimed(files: set[str], claimed: set[str]) -> list[str]:
    """Tracked files under a `g?Formulas/` directory that no family claims.

    A `g?Formulas/` directory holds the ADD, DBL and UTL files of the families
    that live there and nothing else.  Discovery reports what it matched and not
    what it skipped, so a file misnamed by one character produces no family, no
    error and no skip line, and no gate ever loads it.
    """
    return sorted(f for f in files
                  if PurePosixPath(f).parent.name in FORMULA_DIRS
                  and f not in claimed)


def build(files: set[str]) -> tuple[dict, list[str]]:
    """The manifest, plus the discovered paths git does not track."""
    families, excluded = D.discover_families(str(ROOT))

    dropped = set()

    def keep(path) -> str | None:
        r = rel(path)
        if r in files:
            return r
        dropped.add(r)
        return None

    entries, claimed = [], set()
    for fam in sorted(families, key=lambda f: f.name):
        ops = {}
        for op, path in (("ADD", fam.add_path), ("DBL", fam.dbl_path),
                         ("UTL", fam.utl_path)):
            r = keep(path) if path else None
            if r:
                ops[op] = r
                claimed.add(r)
        # A family with no tracked file is in a working tree, not in this
        # repository, and leaves no entry.
        if not ops:
            continue
        entries.append({
            "name": fam.name,
            "model": fam.model,
            "genus": fam.genus,
            "class": fam.kind,
            "coordinates": fam.coords,
            # True when the family has no doubling of its own and uses the arb
            # one.  None does today.
            "doubling_borrowed": bool(fam.dbl_borrowed),
            "files": ops,
        })

    competitors = sorted(f for f in files
                         if COMPETITOR_DIR in PurePosixPath(f).parts
                         and f.endswith(".mag"))
    excluded_rel = sorted(r for r in (keep(p) for p in excluded) if r)
    orphans = unclaimed(files, claimed)
    affine = [e for e in entries if e["coordinates"] == "affine"]

    data = {
        "generated_by": "tools/gen_manifest.py",
        "source_of_truth": "verification/driver.py discover_families()",
        "scope": "files tracked by git, outside the rust submodule",
        "counts": {
            "families": len(entries),
            "families_affine": len(affine),
            "families_projective": len(entries) - len(affine),
            "formula_files": len(claimed),
            "competitor_files": len(competitors),
            "excluded_files": len(excluded_rel),
            # Zero.  Anything else is a formula file no gate can reach.
            "unclaimed_formula_files": len(orphans),
        },
        "families": entries,
        # Published implementations the timing experiments measure against, and
        # the correctness gates never load.
        "competitors": competitors,
        # The frozen 2020 generation under `timings/`, excluded by
        # `discover_families()` itself and quoted here rather than relisted.
        "excluded": excluded_rel,
        "unclaimed": orphans,
    }
    return data, sorted(dropped)


def render(data: dict) -> str:
    """The committed form.  `build` sorts every list, so this stays a function
    of the index."""
    return json.dumps(data, indent=2) + "\n"


def summary(data: dict) -> str:
    c = data["counts"]
    return ("%d families (%d affine, %d projective), %d formula files, "
            "%d competitors, %d excluded"
            % (c["families"], c["families_affine"], c["families_projective"],
               c["formula_files"], c["competitor_files"], c["excluded_files"]))


def report_dropped(dropped: list[str]) -> None:
    if not dropped:
        return
    print("\n%d discovered file(s) git does not track, left out of the "
          "manifest:" % len(dropped))
    for path in dropped:
        print("  " + path)


def report_unclaimed(orphans: list[str]) -> None:
    print("\n%d file(s) under a g?Formulas/ directory that no family claims, "
          "so no gate loads them:" % len(orphans))
    for path in orphans:
        print("  " + path)


def parse_args(argv: list[str]) -> tuple[bool, Path] | None:
    """`(check, out)`, or None after printing why the arguments were rejected.

    Unrecognised arguments are rejected rather than ignored, so a typo cannot
    reach the write path and overwrite the manifest it was asked to check.
    """
    check = False
    out = MANIFEST
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--check":
            check = True
        elif arg == "--out":
            i += 1
            if i >= len(argv) or argv[i].startswith("--"):
                print("--out needs a path")
                return None
            out = Path(argv[i]).resolve()
        else:
            print("unknown argument %r\n"
                  "usage: tools/gen_manifest.py [--check] [--out PATH]" % arg)
            return None
        i += 1
    return check, out


def main(argv: list[str]) -> int:
    parsed = parse_args(argv)
    if parsed is None:
        return 2
    check, out = parsed

    data, dropped = build(tracked())
    text = render(data)
    orphans = data["unclaimed"]

    name = rel(out)

    if check:
        if not out.exists():
            print("%s does not exist; run tools/gen_manifest.py" % name)
            report_dropped(dropped)
            return 1
        committed = out.read_text()
        if committed != text:
            diff = difflib.unified_diff(
                committed.splitlines(True), text.splitlines(True),
                fromfile=name + " (committed)", tofile=name + " (regenerated)")
            print("%s is stale:\n" % name)
            sys.stdout.writelines(diff)
            print("\nRegenerate with tools/gen_manifest.py and commit the "
                  "result.")
            report_dropped(dropped)
            return 1
        print("%s is current: %s" % (name, summary(data)))
        report_dropped(dropped)
        if orphans:
            report_unclaimed(orphans)
            return 1
        return 0

    out.write_text(text)
    print("wrote %s: %s" % (name, summary(data)))
    report_dropped(dropped)
    if orphans:
        report_unclaimed(orphans)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
