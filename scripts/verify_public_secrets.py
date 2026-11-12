#!/usr/bin/env python3
"""Verify that public AI Insight content contains no credentials or Git metadata."""

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = PROJECT_ROOT.parent / "ai-insight-public"

FORBIDDEN_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"openApp[0-9A-Za-z]{16,}",
        r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
        r"\b(?:secret|api)[_-]?key\b\s*[:=]\s*[\"']?[0-9A-Za-z_\-]{16,}",
        r"(?i)\bpassword\b\s*[:=]\s*[\"']?\S{8,}",
        r"\bghp_[0-9A-Za-z]{20,}\b",
        r"\bgithub_pat_[0-9A-Za-z_]{20,}\b",
        r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b",
        r"\bsk-[0-9A-Za-z_\-]{20,}\b",
    ]
]

FORBIDDEN_PATH_PARTS = {".git", ".git_disabled"}
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".txt", ".xml", ".yml", ".yaml"}
MAX_FILE_BYTES = 10 * 1024 * 1024


def find_violations(target: Path):
    violations = []

    for path in sorted(target.rglob("*")):
        relative = path.relative_to(target)
        if any(part in FORBIDDEN_PATH_PARTS for part in relative.parts):
            violations.append((relative, "Git metadata is not allowed in the public repository"))
            continue

        if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
            continue

        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as error:
            violations.append((relative, f"Unable to read file: {error}"))
            continue

        for line_number, line in enumerate(text.splitlines(), 1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    violations.append((relative, f"line {line_number}: forbidden credential pattern"))
                    break

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET, help="Public repository directory to scan")
    args = parser.parse_args()

    target = args.target.resolve()
    if not target.is_dir():
        print(f"❌ Public repository directory does not exist: {target}")
        return 1

    violations = find_violations(target)
    if violations:
        print(f"❌ Found {len(violations)} credential/Git-metadata violation(s):")
        for relative, reason in violations[:20]:
            print(f"  - {relative}: {reason}")
        if len(violations) > 20:
            print(f"  ... and {len(violations) - 20} more")
        return 1

    print("✅ Public credential scan passed: no Git metadata or credential patterns were found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
