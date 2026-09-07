"""RepoLens: a lightweight engineering-readiness checker for Git repositories."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str
    points: int = 1


CHECKS = (
    ("README", ("README.md", "README.rst", "README.txt"), "Documented project"),
    ("License", ("LICENSE", "LICENSE.md", "LICENSE.txt"), "License present"),
    ("Git ignore", (".gitignore",), "Ignore rules present"),
    ("Environment example", (".env.example", ".env.sample"), "Safe environment template"),
    ("Tests", ("tests", "test"), "Test directory present"),
    ("CI", (".github/workflows",), "Continuous integration configured"),
)


def run_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    for name, candidates, detail in CHECKS:
        found = any((root / candidate).exists() for candidate in candidates)
        checks.append(Check(name, found, detail))
    return checks


def score(checks: list[Check]) -> int:
    total = sum(c.points for c in checks)
    earned = sum(c.points for c in checks if c.passed)
    return round(earned / total * 100) if total else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Score basic engineering hygiene in a repository.")
    parser.add_argument("path", nargs="?", default=".", help="Repository path (default: current directory)")
    args = parser.parse_args()

    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Not a directory: {root}")

    checks = run_checks(root)
    print(f"RepoLens — {root.name}")
    print("=" * 40)
    for check in checks:
        mark = "PASS" if check.passed else "MISS"
        print(f"[{mark:4}] {check.name:<20} {check.detail}")
    print("-" * 40)
    print(f"Engineering readiness: {score(checks)}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
