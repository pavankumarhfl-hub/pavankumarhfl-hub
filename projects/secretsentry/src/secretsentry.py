"""SecretSentry: defensive scanner for common accidental secrets."""
from __future__ import annotations
import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

PATTERNS = (
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("Generic secret assignment", re.compile(r'''(?i)\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*["'][^"']{8,}["']''')),
)
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
MAX_FILE_BYTES = 1_000_000

@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    snippet: str

def scan(root: Path) -> list[Finding]:
    findings = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, 1):
            for rule, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(str(path.relative_to(root)), number, rule, "[REDACTED]"))
    return findings

def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a source tree for common accidental secret patterns.")
    parser.add_argument("path", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.path).expanduser().resolve()
    if not root.is_dir():
        parser.error(f"Not a directory: {root}")
    findings = scan(root)
    report = {"repository": root.name, "count": len(findings), "findings": [asdict(f) for f in findings]}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"SecretSentry — {root.name}\n{'=' * 42}")
        for f in findings:
            print(f"[FOUND] {f.path}:{f.line} — {f.rule} — {f.snippet}")
        print("-" * 42, f"\nFindings: {len(findings)}")
    return 1 if findings else 0

if __name__ == "__main__":
    raise SystemExit(main())
