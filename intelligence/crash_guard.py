from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Crash Guard
================
Writes atomic checkpoints before every destructive command.
Detects crash state on /init and surfaces recovery automatically.

The problem this solves:
  Claude Code's --resume fails on crash because sessions-index.json
  and the .jsonl files can fail independently (documented OOM bug #90).
  Even when resume works, APEX has no idea WHERE in a multi-task
  /execute sequence you were.

What APEX stores independently (survives any crash):
  .claude/checkpoints/last.json  — atomic write, always current
  .claude/checkpoints/archive/   — ring buffer of last 10 checkpoints

Checkpoint format:
  {
    "timestamp": "2026-04-20T14:32:11Z",
    "command": "execute",
    "task_summary": "Step 3/5: Add RLS policies to profiles table",
    "git_hash": "a3b4c5d",
    "git_branch": "feat/auth",
    "files_in_flight": ["src/auth/session.ts", "lib/db/policies.sql"],
    "todo_snapshot": "- [>] TASK-003: Add RLS...",
    "session_id": "abc123",    # Claude Code session ID if available
    "safe_to_resume": true     # false if mid-write when crashed
  }

Usage:
  # Before a command (automatic via PreToolUse hook)
  python3 .claude/intelligence/crash_guard.py checkpoint "execute" "Step 3/5..."
  
  # On /init — auto-detect and surface crash
  python3 .claude/intelligence/crash_guard.py detect
  
  # After clean session end — clear checkpoint
  python3 .claude/intelligence/crash_guard.py clear
  
  # List recent checkpoints
  python3 .claude/intelligence/crash_guard.py history
"""
import json, sys, os, subprocess, tempfile
from pathlib import Path
from datetime import datetime, timezone

ROOT      = Path.cwd()
APEX_DIR  = ROOT / ".claude"
CP_DIR    = APEX_DIR / "checkpoints"
LAST_CP   = CP_DIR / "last.json"
ARCHIVE   = CP_DIR / "archive"
RING_SIZE = 10  # keep last 10 checkpoints


def _get_apex_version() -> str:
    ver_file = APEX_DIR / "config" / "apex-version.json"
    try:
        return json.loads(ver_file.read_text()).get("version", "6.0.0")
    except Exception:
        return "6.0.0"

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"


def _git(cmd: str) -> str:
    """Run a git command, return output or empty string on failure."""
    try:
        r = subprocess.run(
            ["git"] + cmd.split(),
            capture_output=True, text=True, timeout=3, cwd=ROOT,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _read_todo_snapshot() -> str:
    """Read the in-progress items from TODO.md or AI_TASKS.md."""
    for fname in ["TODO.md", "docs/AI_TASKS.md", "AI_TASKS.md"]:
        f = ROOT / fname
        if f.exists():
            lines = f.read_text(errors="ignore").splitlines()
            in_progress = [l for l in lines if l.strip().startswith("- [>]")]
            return "\n".join(in_progress[:5]) if in_progress else ""
    return ""


def _get_session_id() -> str:
    """Try to find the current Claude Code session ID from the project dir."""
    try:
        # Claude Code stores sessions in ~/.claude/projects/<encoded-cwd>/
        encoded = ROOT.as_posix().replace("/", "-").lstrip("-")
        sessions_dir = Path.home() / ".claude" / "projects" / encoded
        if sessions_dir.exists():
            jsonl_files = sorted(
                sessions_dir.glob("*.jsonl"),
                key=lambda f: f.stat().st_mtime,
                reverse=True,
            )
            if jsonl_files:
                return jsonl_files[0].stem
    except Exception:
        pass
    return ""


def _atomic_write(path: Path, data: dict) -> None:
    """Write JSON atomically — survives OOM kill mid-write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_checkpoint(command: str, task_summary: str = "", files: list[str] | None = None) -> dict:
    """
    Write a checkpoint before a destructive command.
    Called by the PreToolUse hook before every Write/Edit/Bash.
    """
    CP_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    checkpoint = {
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "command":       command,
        "task_summary":  task_summary or f"Running /{command}",
        "git_hash":      _git("rev-parse --short HEAD"),
        "git_branch":    _git("rev-parse --abbrev-ref HEAD"),
        "git_status":    _git("status --short") or "clean",
        "files_in_flight": files or [],
        "todo_snapshot": _read_todo_snapshot(),
        "session_id":    _get_session_id(),
        "safe_to_resume": True,
        "_apex_version": _get_apex_version(),
    }

    # Archive the previous checkpoint (ring buffer)
    if LAST_CP.exists():
        try:
            prev = json.loads(LAST_CP.read_text())
            ts   = prev.get("timestamp", "unknown").replace(":", "-")[:19]
            arch = ARCHIVE / f"{ts}.json"
            _atomic_write(arch, prev)
            # Prune ring: keep only last RING_SIZE
            archives = sorted(ARCHIVE.glob("*.json"), key=lambda f: f.stat().st_mtime)
            for old in archives[:-RING_SIZE]:
                old.unlink(missing_ok=True)
        except Exception:
            pass

    _atomic_write(LAST_CP, checkpoint)
    return checkpoint


def detect_crash() -> dict | None:
    """
    Called by /init. Returns crash info if a checkpoint exists
    that looks like it wasn't cleanly closed.
    
    A checkpoint is "stale" (indicates crash) if:
    - last.json exists
    - AND the git hash in it differs from current HEAD
    - OR a completed.flag file does NOT exist alongside it
    """
    if not LAST_CP.exists():
        return None

    completed_flag = CP_DIR / "completed.flag"
    if completed_flag.exists():
        return None  # clean session end

    try:
        cp = json.loads(LAST_CP.read_text())
    except Exception:
        return None

    current_hash = _git("rev-parse --short HEAD")

    # Check if something changed since the checkpoint (files were modified)
    cp_hash = cp.get("git_hash", "")
    git_changed = cp_hash and current_hash and cp_hash != current_hash

    # Check age — checkpoints older than 24h are probably not crash-related
    from datetime import timedelta
    try:
        cp_time = datetime.fromisoformat(cp["timestamp"])
        age = datetime.now(timezone.utc) - cp_time
        if age > timedelta(hours=24):
            return None
    except Exception:
        pass

    cp["_git_changed_since"] = git_changed
    cp["_current_hash"] = current_hash
    return cp


def clear_checkpoint():
    """Mark the session as cleanly completed."""
    if LAST_CP.exists():
        CP_DIR.mkdir(parents=True, exist_ok=True)
        (CP_DIR / "completed.flag").write_text(
            datetime.now(timezone.utc).isoformat()
        )


def list_history() -> list[dict]:
    """Return the last N checkpoints."""
    checkpoints = []
    if LAST_CP.exists():
        try:
            checkpoints.append(json.loads(LAST_CP.read_text()))
        except Exception:
            pass
    if ARCHIVE.exists():
        for f in sorted(ARCHIVE.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                checkpoints.append(json.loads(f.read_text()))
            except Exception:
                continue
    return checkpoints


def print_crash_recovery(crash: dict):
    """Print a clear, actionable crash recovery briefing."""
    print(f"\n{BOLD}{YELLOW}━━━ APEX Crash Recovery Detected ━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Previous session ended unexpectedly.")
    print(f"")
    print(f"  {BOLD}Last known state:{RESET}")
    print(f"    Time:     {crash['timestamp'][:19].replace('T',' ')}")
    print(f"    Command:  /{crash.get('command', 'unknown')}")
    print(f"    Task:     {crash.get('task_summary', 'unknown')[:70]}")
    print(f"    Branch:   {crash.get('git_branch', 'unknown')}")
    print(f"    Git hash: {crash.get('git_hash', 'unknown')}")

    files = crash.get("files_in_flight", [])
    if files:
        print(f"\n  {BOLD}Files that were being modified:{RESET}")
        for f in files[:5]:
            print(f"    {DIM}• {f}{RESET}")

    todo = crash.get("todo_snapshot", "")
    if todo:
        print(f"\n  {BOLD}In-progress tasks at crash time:{RESET}")
        for line in todo.splitlines()[:3]:
            print(f"    {DIM}{line}{RESET}")

    if crash.get("_git_changed_since"):
        print(f"\n  {YELLOW}⚠ Git state has changed since checkpoint.{RESET}")
        print(f"  {DIM}Run 'git diff {crash.get('git_hash','')}' to see what changed.{RESET}")

    session_id = crash.get("session_id", "")
    if session_id:
        print(f"\n  {BOLD}To resume the Claude Code session:{RESET}")
        print(f"  {DIM}claude --resume {session_id}{RESET}")
        print(f"  {DIM}(may not work if session was corrupted — see /handoff fallback){RESET}")
    else:
        print(f"\n  {BOLD}No session ID found — start fresh:{RESET}")
        print(f"  {DIM}Run /handoff to read the checkpoint and rebuild context.{RESET}")

    print(f"\n  {BOLD}Recommended next steps:{RESET}")
    print(f"  {DIM}1. git diff HEAD to verify file state{RESET}")
    print(f"  {DIM}2. Review TODO.md for in-progress tasks{RESET}")
    print(f"  {DIM}3. Run /{crash.get('command', 'init')} to continue{RESET}")
    print(f"  {DIM}4. python3 .claude/intelligence/crash_guard.py clear when done{RESET}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def main():
    args = sys.argv[1:]
    cmd  = args[0] if args else "detect"

    if cmd == "checkpoint":
        command      = args[1] if len(args) > 1 else "unknown"
        task_summary = args[2] if len(args) > 2 else ""
        cp = write_checkpoint(command, task_summary)
        print(f"{DIM}Checkpoint saved: /{command} — {cp['git_hash']} on {cp['git_branch']}{RESET}")

    elif cmd == "detect":
        crash = detect_crash()
        if crash:
            print_crash_recovery(crash)
        else:
            print(f"{GREEN}✓ No crash state detected — clean session.{RESET}")

    elif cmd == "clear":
        clear_checkpoint()
        print(f"{GREEN}✓ Session marked complete — checkpoint cleared.{RESET}")

    elif cmd == "history":
        history = list_history()
        print(f"\n{BOLD}Checkpoint history ({len(history)} entries):{RESET}")
        for cp in history[:5]:
            print(f"  {DIM}{cp['timestamp'][:19]} /{cp.get('command','?')} — {cp.get('task_summary','')[:50]}{RESET}")

    else:
        print("Usage: crash_guard.py [checkpoint <cmd> [summary] | detect | clear | history]")


if __name__ == "__main__":
    main()
