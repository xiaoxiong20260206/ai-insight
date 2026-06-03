#!/usr/bin/env python3
"""
Sync subscribers from Appwrite to local subscribers.json.

Uses appwrite-cf CLI for authentication (calls databases list-documents).

Usage:
    python3 scripts/sync_subscribers.py
    python3 scripts/sync_subscribers.py --dry-run
"""

import json
import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

DATABASE_ID = "subscribers"
TABLE_ID = "daily_subscribers"

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"


def fetch_subscribers_from_appwrite() -> list[dict]:
    """Fetch all documents from Appwrite using the CLI."""
    result = subprocess.run(
        [
            "appwrite-cf", "databases", "list-documents",
            "--database-id", DATABASE_ID,
            "--collection-id", TABLE_ID,
        ],
        capture_output=True, text=True,
    )

    if result.returncode != 0:
        print("ERROR: appwrite-cf databases list-documents failed", file=sys.stderr)
        print(result.stderr[:500], file=sys.stderr)
        sys.exit(1)

    # CLI outputs metadata lines before the JSON; find the JSON block
    lines = result.stdout.strip().split("\n")
    json_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("{"):
            json_start = i
            break

    if json_start is None:
        print("ERROR: No JSON found in CLI output", file=sys.stderr)
        print(result.stdout[:500], file=sys.stderr)
        sys.exit(1)

    json_text = "\n".join(lines[json_start:])
    data = json.loads(json_text)
    return data.get("documents", [])


def sync(docs: list[dict], dry_run: bool = False):
    """Convert documents to subscribers.json format and write."""
    subscribers = []
    for doc in docs:
        if not doc.get("is_active", False):
            continue
        subscribers.append({
            "username": doc.get("username", ""),
            "kwaiUserId": doc.get("kwai_user_id", ""),
            "subscribed_at": (doc.get("subscribed_at") or "")[:10],
            "is_active": True,
            "source": doc.get("source", "web_subscribe"),
        })

    # Always ensure owner is present
    if not any(s["username"] == "shenlang03" for s in subscribers):
        subscribers.insert(0, {
            "username": "shenlang03",
            "kwaiUserId": "560215856862",
            "subscribed_at": "2026-03-10",
            "is_active": True,
            "source": "owner",
        })

    output = {
        "updated_at": datetime.now().strftime("%Y-%m-%d"),
        "subscribers": subscribers,
    }

    if dry_run:
        print("DRY RUN - Would write:")
        print(json.dumps(output, indent=2, ensure_ascii=False))
        print(f"\nTotal active subscribers: {len(subscribers)}")
        return

    DATA_DIR.mkdir(exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Synced {len(subscribers)} subscribers to {SUBSCRIBERS_FILE}")
    for s in subscribers:
        print(f"  ✓ {s['username']} (since {s['subscribed_at']}, source={s['source']})")


def main():
    parser = argparse.ArgumentParser(description="Sync Appwrite subscribers to local JSON")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("🔄 Fetching subscribers from Appwrite...")
    docs = fetch_subscribers_from_appwrite()
    sync(docs, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
