#!/usr/bin/env python3
"""
Sync subscribers from Appwrite to local subscribers.json.

This script reads all active subscribers from the Appwrite database
and writes them to data/subscribers.json, which is read by the daily
report cron to determine who receives the daily report.

Usage:
    uv run --with requests scripts/sync_subscribers.py
    uv run --with requests scripts/sync_subscribers.py --dry-run
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Appwrite config
PROJECT_ID = "aidailyinsight"
DATABASE_ID = "subscribers"
TABLE_ID = "daily_subscribers"
# Use the internal endpoint since this runs inside the corporate network
ENDPOINT = "https://frontend-cloud.corp.kuaishou.com/v1"

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"


def get_appwrite_session():
    """Read session cookies from the appwrite-cf config."""
    import subprocess
    result = subprocess.run(
        ["appwrite-cf", "whoami", "--json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("ERROR: appwrite-cf whoami failed. Make sure you're logged in.")
        print(result.stderr)
        sys.exit(1)
    return True


def fetch_all_subscribers() -> list:
    """Fetch all active subscribers from Appwrite using the SDK client."""
    import requests

    # Use server-side API key approach via appwrite-cf session
    # The CLI has a valid session, we use its cookies
    import subprocess
    import os

    # Read session cookie from appwrite-cf
    config_dir = Path.home() / ".appwrite-cf"
    session_file = config_dir / "session.json"

    if not session_file.exists():
        print("ERROR: No appwrite-cf session found. Run 'appwrite-cf login-ks' first.")
        sys.exit(1)

    with open(session_file) as f:
        session_data = json.load(f)

    # Try to extract session token
    session_token = session_data.get("token") or session_data.get("session")
    if not session_token:
        # Try cookie-based approach
        cookies = session_data.get("cookies", {})
        session_token = cookies.get("a_session_" + PROJECT_ID, "")

    headers = {
        "Content-Type": "application/json",
        "X-Appwrite-Project": PROJECT_ID,
    }

    if session_token:
        headers["X-Appwrite-Key"] = session_token

    all_docs = []
    offset = 0
    limit = 100

    while True:
        url = f"{ENDPOINT}/databases/{DATABASE_ID}/tables/{TABLE_ID}/documents"
        params = {
            "queries[]": json.dumps([
                {"method": "equal", "attribute": "is_active", "values": [True]}
            ]),
            "offset": offset,
            "limit": limit,
        }

        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"ERROR: Failed to fetch subscribers (status {resp.status_code})")
            print(resp.text[:500])
            sys.exit(1)

        data = resp.json()
        docs = data.get("documents", [])
        all_docs.extend(docs)

        if len(docs) < limit:
            break
        offset += limit

    return all_docs


def sync_to_file(docs: list, dry_run: bool = False):
    """Convert Appwrite documents to subscribers.json format and write."""
    subscribers = []
    for doc in docs:
        subscribers.append({
            "username": doc.get("username", ""),
            "kwaiUserId": doc.get("kwai_user_id", ""),
            "subscribed_at": doc.get("subscribed_at", ""),
            "is_active": doc.get("is_active", True),
            "source": doc.get("source", "web_subscribe"),
        })

    # Always include the owner
    owner_exists = any(s["username"] == "shenlang03" for s in subscribers)
    if not owner_exists:
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
        status = "✓" if s["is_active"] else "✗"
        print(f"  {status} {s['username']} (since {s['subscribed_at'][:10]}, source={s['source']})")


def main():
    parser = argparse.ArgumentParser(description="Sync Appwrite subscribers to local JSON")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    args = parser.parse_args()

    print("🔄 Fetching subscribers from Appwrite...")
    docs = fetch_all_subscribers()
    sync_to_file(docs, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
