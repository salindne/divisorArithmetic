#!/usr/bin/env python3
"""Check that every path the READMEs name actually exists.

The previous README claimed test_all.sh ran a tester that had never existed, gave
three genus-3 filenames wrong, and named two directories wrongly: all the same
failure, prose drifting from the tree with nothing to notice.

Checked: every markdown link target, and every backticked token that looks like a
path (contains a slash, or ends in a known extension).

Usage:
    tools/check_readme_paths.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def _discover_readmes():
    """Every README in the repository, found rather than listed.

    A hardcoded list left `verification/README.md`, `tools/magma-docker/README.md`
    and `Thesis/README.md` unchecked.  Discovery is the point of the tool.

    `rust/` is a submodule and owns its own documentation.
    """
    found = []
    for path in sorted(ROOT.rglob("README.md")):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in (".git", "rust"):
            continue
        found.append(str(rel))
    return found


READMES = _discover_readmes()

EXTENSIONS = (".mag", ".py", ".sh", ".tex", ".pdf", ".md", ".yml", ".yaml",
              ".txt", ".xz", ".gnuplot", ".raw")

# Paths named in the READMEs that are deliberately absent from the repository.
# Each needs a reason; this is not a place to silence real breakage.
EXPECTED_ABSENT = {
    # The Magma toolchain is licensed and gitignored on purpose, and README.md's
    # Requirements section must be able to name it.  See .gitignore.
    "Dockerfile": "gitignored: licensed Magma toolchain, recreated by the user",
    "docker-compose.yml": "gitignored: licensed Magma toolchain",
    "run-magma.sh": "gitignored: licensed Magma toolchain",
    "magma.tar.xz": "gitignored: licensed Magma tarball, never committed",
    # Named generically in prose as an example of a family, not as a path.
    "timings_[xx]bit.mag": "placeholder for the ten per-field-size drivers",
    # Created at runtime by test_all.sh and gitignored.
    ".test-logs/": "gitignored: per-tester logs, created on first run",
    # The generator's staging area, gitignored since v1.0.1. A tester is of record
    # once copied next to its formulas, so a committed staging copy could only be a
    # second, diverging source of truth.
    "whitebox/testerFiles/": "gitignored: generator staging, written on first run",
    # A Docker platform identifier, not a filesystem path.
    "linux/arm64": "docker platform string, not a path",
    "linux/amd64": "docker platform string, not a path",
    # Inside the QEMU source tree, which tools/magma-docker/ patches at build time.
    # Named so a reader can find what the mremap patch touches.
    "linux-user/mmap.c": "path inside the QEMU source tree, not this repository",
    # Thesis/README.md documents the university thesis class, which is excluded from
    # this repository's licence; the example it names ships upstream with the class.
    "sample-thesis.tex": "example shipped with the upstream thesis class, not copied here",
    # The stale path all three genus-3 split whitebox generators used to load from.
    # Those loads are repaired; the entry stays so a reference reintroduced from an
    # old draft is explained rather than failing mysteriously.
    "../g3/splitModel/g3Formulas/":
        "the load path the genus-3 split generators used before it was repaired",
}

# Bare filenames mentioned in prose rather than as locations. Checking these as
# repo-root paths would be wrong; they are resolved by the surrounding text.
PROSE_BASENAMES = {
    "frontmatter.tex", "appendix.tex", "thesis.tex",
    "reduced_basis_arithmetic.mag", "poly_balanced_arithmetic.mag",
    "parse_timings.py", "plot_timings.gnuplot",
    # Directory names discussed generically, present under several parents.
    "g2Formulas/", "g3Formulas/", "genFiles/",
}
PROSE_PATTERNS = [
    re.compile(r"^chapter\d+\.tex$"),
    re.compile(r"^timings_\d+bit\.mag$"),
]


def is_prose(token: str) -> bool:
    if token in PROSE_BASENAMES:
        return True
    return any(p.match(token) for p in PROSE_PATTERNS)


def looks_like_path(token: str) -> bool:
    """Whether a backticked token is a location, as opposed to prose or syntax."""
    # Glob patterns name a family, not a file.
    if "*" in token or "?" in token:
        return False
    # Magma annotation directives: //Constant:, //startIGNORE, //endIGNORE.
    if token.startswith("//"):
        return False
    # Absolute paths refer to the inside of the Docker image, not this repo.
    if token.startswith("/"):
        return False
    # A bare extension, e.g. ".tex" used as "the .tex files".
    if token.startswith(".") and "/" not in token:
        return False
    return "/" in token or token.endswith(EXTENSIONS)


def resolves(base: Path, token: str) -> bool:
    """Whether a token names something that exists.

    Tried against the README's own directory first, then the repository root, so
    a subdirectory README can refer to a top-level file such as test_all.sh.

    Case-sensitive only on a case-sensitive filesystem: on macOS
    `arb_splitG3_whiteBox_tester.mag` resolves to the on-disk
    `..._whitebox_tester.mag`, so a casing error passes locally and fails in CI.
    CI is the authority here.
    """
    return (base / token).exists() or (ROOT / token).exists()


def tokens_from(text: str) -> set[str]:
    found = set()
    # markdown link targets
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        found.add(target.split("#", 1)[0])
    # backticked path-shaped tokens
    for token in re.findall(r"`([^`\n]+)`", text):
        token = token.strip()
        if looks_like_path(token) and " " not in token:
            found.add(token)
    return found


def main() -> int:
    problems = []
    checked = 0

    for name in READMES:
        readme = ROOT / name
        if not readme.exists():
            problems.append((name, name, "README itself is missing"))
            continue
        base = readme.parent
        for token in sorted(tokens_from(readme.read_text())):
            if token in EXPECTED_ABSENT or is_prose(token):
                continue
            checked += 1
            if not resolves(base, token):
                problems.append((name, token, "does not exist"))

    if problems:
        print(f"{len(problems)} path(s) named in a README do not exist:\n")
        for readme, token, why in problems:
            print(f"  {readme}: {token}   ({why})")
        print("\nEither fix the path or, if it is deliberately absent, add it to")
        print("EXPECTED_ABSENT in tools/check_readme_paths.py with a reason.")
        return 1

    print(f"all {checked} path(s) named in {len(READMES)} README(s) exist "
          f"({len(EXPECTED_ABSENT)} deliberately absent, declared)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
