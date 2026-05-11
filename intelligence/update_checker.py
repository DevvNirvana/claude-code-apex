from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Auto-Update Checker
========================
Runs silently at session start. If the installed version is behind the
latest release on GitHub, prompts the user once per day.

Behavior:
  - Checks GitHub releases API (with 24h cache — never hammers network)
  - Silent if version is current or network unavailable
  - Non-blocking: never stalls the session if network is slow (3s timeout)
  - Never auto-installs: always asks permission first
  - Works offline: gracefully skips if no internet

APEX version file: .claude/config/apex-version.json
Update cache: .claude/cache/update-check.json

Usage (called by session-start hook):
  python3 .claude/intelligence/update_checker.py check
  python3 .claude/intelligence/update_checker.py version  # show current version
  python3 .claude/intelligence/update_checker.py set 6.0  # set installed version
"""
import json, sys, os, tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT     = Path.cwd()
APEX_DIR = ROOT / ".claude"
VER_FILE = APEX_DIR / "config" / "apex-version.json"
CACHE    = APEX_DIR / "cache" / "update-check.json"

GITHUB_REPO     = "DevvNirvana/claude-code-apex"
GITHUB_API      = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE   = f"https://github.com/{GITHUB_REPO}/releases/latest"
CURRENT_VERSION = "6.0.0"   # Updated on each release

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"


def _version_tuple(v: str) -> tuple:
    """Parse '6.0.1' → (6, 0, 1) for comparison."""
    try:
        parts = v.lstrip("v").split(".")
        return tuple(int(p) for p in parts[:3])
    except Exception:
        return (0, 0, 0)


def get_installed_version() -> str:
    """Read installed version from config. Falls back to CURRENT_VERSION."""
    if VER_FILE.exists():
        try:
            data = json.loads(VER_FILE.read_text())
            return data.get("version", CURRENT_VERSION)
        except Exception:
            pass
    return CURRENT_VERSION


def set_installed_version(version: str):
    """Write installed version after upgrade."""
    VER_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version":        version,
        "installed_at":   datetime.now(timezone.utc).isoformat(),
        "github_repo":    GITHUB_REPO,
    }
    fd, tmp = tempfile.mkstemp(dir=VER_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, VER_FILE)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass


def _load_check_cache() -> dict:
    if CACHE.exists():
        try:
            return json.loads(CACHE.read_text())
        except Exception:
            pass
    return {}


def _save_check_cache(data: dict):
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=CACHE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, CACHE)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass


def fetch_latest_version() -> str | None:
    """
    Fetch latest version from GitHub. Returns None on any failure.
    Hard timeout: 3 seconds — never stalls the session.
    """
    try:
        import urllib.request
        req = urllib.request.Request(
            GITHUB_API,
            headers={"User-Agent": f"APEX/{CURRENT_VERSION}"},
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            tag = data.get("tag_name", "").lstrip("v")
            return tag if tag else None
    except Exception:
        return None


def check_for_update(force: bool = False) -> dict | None:
    """
    Check if an update is available.
    Returns update info dict if update available, None if current or error.
    
    Uses 24h cache to avoid hitting GitHub on every session start.
    """
    cache = _load_check_cache()
    installed = get_installed_version()

    # Check cache freshness (24h)
    if not force and cache.get("checked_at"):
        try:
            checked = datetime.fromisoformat(cache["checked_at"])
            if datetime.now(timezone.utc) - checked < timedelta(hours=24):
                # Use cached result
                latest = cache.get("latest_version")
                if latest and _version_tuple(latest) > _version_tuple(installed):
                    return {
                        "installed":  installed,
                        "latest":     latest,
                        "from_cache": True,
                        "changelog":  cache.get("changelog", ""),
                    }
                return None
        except Exception:
            pass

    # Fetch from GitHub
    latest = fetch_latest_version()

    # Save to cache regardless of result
    _save_check_cache({
        "checked_at":     datetime.now(timezone.utc).isoformat(),
        "latest_version": latest or installed,
        "changelog":      cache.get("changelog", ""),
    })

    if not latest:
        return None

    if _version_tuple(latest) > _version_tuple(installed):
        return {
            "installed": installed,
            "latest":    latest,
            "from_cache": False,
        }

    return None


def prompt_update(update_info: dict):
    """
    Show a non-intrusive update prompt and ask permission.
    If user says yes, prints the upgrade commands.
    If user says no, suppresses for today.
    """
    installed = update_info["installed"]
    latest    = update_info["latest"]

    print(f"\n{CYAN}{BOLD}━━━ APEX Update Available ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Installed:  v{installed}")
    print(f"  Available:  {GREEN}{BOLD}v{latest}{RESET}")
    print(f"  Releases:   {DIM}{RELEASES_PAGE}{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"\n  {BOLD}Update now?{RESET} [{BOLD}y{RESET}/n/skip24h] ", end="", flush=True)

    try:
        response = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        response = "n"

    if response in ("y", "yes", ""):
        print(f"\n{GREEN}Upgrade steps:{RESET}")
        print(f"  1. Download: {RELEASES_PAGE}")
        print(f"  2. Unzip to ~/Downloads/")
        print(f"  3. cd your-project")
        print(f"  4. bash ~/Downloads/claude-orchestrator-apex-v{latest}/install.sh --update")
        print(f"  5. python3 .claude/intelligence/update_checker.py set {latest}")
        print(f"\n{DIM}This preserves your brain, trajectories, and identity.{RESET}\n")
    elif response in ("skip24h", "s"):
        # Already cached — won't prompt again for 24h
        print(f"{DIM}Skipping. Will remind again in 24 hours.{RESET}\n")
    else:
        print(f"{DIM}Skipping for this session.{RESET}\n")


def run_check(silent_if_current: bool = True):
    """Main entry: check and prompt if needed. Called by session-start hook."""
    update = check_for_update()
    if update:
        prompt_update(update)
    elif not silent_if_current:
        v = get_installed_version()
        print(f"{GREEN}✓ APEX v{v} is up to date.{RESET}")


def main():
    args = sys.argv[1:]
    cmd  = args[0] if args else "check"

    if cmd == "check":
        force = "--force" in args
        update = check_for_update(force=force)
        if update:
            prompt_update(update)
        else:
            print(f"{GREEN}✓ APEX v{get_installed_version()} is current.{RESET}")

    elif cmd == "version":
        v = get_installed_version()
        print(f"APEX v{v} (latest check: {_load_check_cache().get('checked_at','never')[:10]})")

    elif cmd == "set":
        version = args[1] if len(args) > 1 else CURRENT_VERSION
        set_installed_version(version)
        print(f"✓ Version set to {version}")

    else:
        print("Usage: update_checker.py [check [--force] | version | set <version>]")


if __name__ == "__main__":
    main()
