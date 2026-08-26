#!/usr/bin/env python3
"""Extract the substack.sid cookie from a local Firefox profile and save it
to ~/.config/plumbeer/substack/cookies.json.

macOS + Firefox only. The caller (see SKILL.md Phase 1) is responsible for
checking those prerequisites before running this script — it does not
re-check them itself, and it will not install or configure Firefox.

Reads a *copy* of Firefox's cookies.sqlite (plus its -wal file) so it works
even while Firefox is open and holding the original locked. Never prints the
cookie value itself.

Usage:
    python3 extract_firefox_cookie.py [--profile PATH]

If --profile is omitted, the script looks for a "*.default-release" profile
first, falling back to "*.default", under the standard macOS Firefox profile
directory.
"""
import argparse
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path


def find_profiles_dir() -> Path:
    return Path.home() / "Library" / "Application Support" / "Firefox" / "Profiles"


def find_profile(profiles_dir: Path) -> Path:
    if not profiles_dir.is_dir():
        raise SystemExit(f"No Firefox profiles directory found at {profiles_dir}")

    for pattern in ("*.default-release", "*.default"):
        matches = sorted(profiles_dir.glob(pattern))
        if matches:
            return matches[0]

    raise SystemExit(
        f"No '*.default-release' or '*.default' profile found under {profiles_dir}. "
        "Pass --profile explicitly."
    )


def extract_cookie(profile_dir: Path) -> str:
    db_path = profile_dir / "cookies.sqlite"
    if not db_path.exists():
        raise SystemExit(f"No cookies.sqlite found in {profile_dir}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        # Copy the db and its -wal/-shm sidecars so we read committed +
        # in-flight writes without needing Firefox to release its lock.
        for sidecar in ("cookies.sqlite", "cookies.sqlite-wal", "cookies.sqlite-shm"):
            src = profile_dir / sidecar
            if src.exists():
                shutil.copy2(src, tmp_dir / sidecar)

        con = sqlite3.connect(tmp_dir / "cookies.sqlite")
        try:
            row = con.execute(
                "SELECT value FROM moz_cookies WHERE host LIKE '%substack.com' AND name = 'substack.sid'"
            ).fetchone()
        finally:
            con.close()

    if not row:
        raise SystemExit(
            "No substack.sid cookie found. Make sure you're logged into "
            "Substack in this Firefox profile."
        )
    return row[0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        type=Path,
        help="Path to a specific Firefox profile directory (skips auto-detection).",
    )
    args = parser.parse_args()

    profile_dir = args.profile or find_profile(find_profiles_dir())
    print(f"Using Firefox profile: {profile_dir}")

    cookie_value = extract_cookie(profile_dir)

    out_dir = Path.home() / ".config" / "plumbeer" / "substack"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "cookies.json"
    out_path.write_text(json.dumps({"substack.sid": cookie_value}))
    out_path.chmod(0o600)

    print(f"Saved cookie to {out_path} (length: {len(cookie_value)} chars)")


if __name__ == "__main__":
    main()
