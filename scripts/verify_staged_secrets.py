#!/usr/bin/env python3
"""Scan staged Git blobs before creating a commit without printing credentials."""

import re
import subprocess
import sys

from verify_public_secrets import FORBIDDEN_PATTERNS


def main():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT", "-z"],
        capture_output=True, check=True,
    )
    failed = False
    for filename in result.stdout.decode().split("\0"):
        if not filename:
            continue
        if any(
            part in {".git", ".git_disabled", ".env"}
            or (part.startswith(".env.") and part not in {".env.example", ".env.sample"})
            for part in filename.split("/")
        ):
            print(f"Blocked sensitive path: {filename}")
            failed = True
            continue
        content = subprocess.run(
            ["git", "show", f":{filename}"], capture_output=True, check=True,
        ).stdout.decode("latin-1")
        if any(pattern.search(content) for pattern in FORBIDDEN_PATTERNS):
            print(f"Blocked credential pattern: {filename}")
            failed = True
        if re.search(r"(?i)(?:secret|api)[_-]?key.{0,8}[0-9a-f]{28,}", content):
            print(f"Blocked hexadecimal credential: {filename}")
            failed = True
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
