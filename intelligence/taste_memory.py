#!/usr/bin/env python3
"""
Taste Memory — Explicit Developer Preference Learning
=====================================================
Collects explicit feedback signals after /design, /plan, /brainstorm
commands. Builds a developer preference profile that gets injected
into future commands as context.

Signal flow:
  Command outputs → "Was this on target?" prompt → signal stored
  → After 10 signals of same type → preference summary generated
  → Injected into future command context

Multi-author ready: each signal carries author + project fields
for future team intelligence support.

Usage:
  python3 .claude/intelligence/taste_memory.py log <command> <signal>
  python3 .claude/intelligence/taste_memory.py profile
  python3 .claude/intelligence/taste_memory.py inject <command>
  python3 .claude/intelligence/taste_memory.py review
"""
import json, sys, os, tempfile, hashlib
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT    = Path.cwd()
MEMORY  = ROOT / ".claude" / "memory"
SIGNALS = MEMORY / "taste_signals.jsonl"
PROFILE = MEMORY / "taste_profile.json"

CYAN  = "\033[0;36m"; GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"
DIM   = "\033[2m";    BOLD  = "\033[1m";    RESET  = "\033[0m"
RED   = "\033[0;31m"

# Number of signals before auto-generating preference summary
SUMMARY_THRESHOLD = 10

VALID_SIGNALS = {"accepted", "modified", "rejected"}
LEARNABLE_COMMANDS = {"design", "plan", "brainstorm", "review", "refactor"}


def _atomic_append(path: Path, line: str):
    """Append a JSON line atomically."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _atomic_write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except: pass
        raise


def log_signal(
    command: str,
    signal_type: str,
    context_summary: str = "",
    modification_note: str = "",
    author: str = "developer",
    project: str = "",
    trajectory_id: str = "",
) -> dict:
    """
    Log an explicit taste signal.
    signal_type: "accepted" | "modified" | "rejected"
    """
    if command not in LEARNABLE_COMMANDS:
        print(f"{YELLOW}⚠ Taste signals not tracked for /{command}{RESET}")
        return {}

    if signal_type not in VALID_SIGNALS:
        print(f"{RED}Invalid signal type. Use: {', '.join(VALID_SIGNALS)}{RESET}")
        sys.exit(1)

    signal = {
        "signal_id":        hashlib.sha256(
            (command + signal_type + datetime.now(timezone.utc).isoformat()).encode()
        ).hexdigest()[:12],
        "command":          command,
        "signal_type":      signal_type,
        "context_summary":  context_summary[:200],
        "modification_note": modification_note[:300],
        "author":           author,
        "project":          project or ROOT.name,
        "trajectory_id":    trajectory_id,
        "timestamp":        datetime.now(timezone.utc).isoformat(),
    }

    _atomic_append(SIGNALS, json.dumps(signal))

    color = GREEN if signal_type == "accepted" else (
            YELLOW if signal_type == "modified" else RED)
    print(f"{color}✓ Signal logged: {signal_type} for /{command}{RESET}")

    # Check if we have enough signals to regenerate profile
    all_signals = load_signals()
    cmd_signals = [s for s in all_signals if s.get("command") == command]
    if len(cmd_signals) >= SUMMARY_THRESHOLD and len(cmd_signals) % SUMMARY_THRESHOLD == 0:
        print(f"{CYAN}ℹ {len(cmd_signals)} signals for /{command} — updating preference profile{RESET}")
        _update_profile(all_signals)

    return signal


def load_signals() -> list[dict]:
    if not SIGNALS.exists():
        return []
    signals = []
    for line in SIGNALS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                signals.append(json.loads(line))
            except Exception:
                continue
    return signals


def _update_profile(signals: list[dict]):
    """
    Build a preference profile from accumulated signals.
    Groups by command, computes acceptance rates, extracts
    common modification patterns.
    """
    profile = {
        "generated_at":  datetime.now(timezone.utc).isoformat(),
        "total_signals": len(signals),
        "commands":      {},
        "global_patterns": [],
    }

    by_command = defaultdict(list)
    for s in signals:
        by_command[s["command"]].append(s)

    for cmd, cmd_signals in by_command.items():
        accepted  = [s for s in cmd_signals if s["signal_type"] == "accepted"]
        modified  = [s for s in cmd_signals if s["signal_type"] == "modified"]
        rejected  = [s for s in cmd_signals if s["signal_type"] == "rejected"]
        total     = len(cmd_signals)
        accept_rate = len(accepted) / total if total > 0 else 0

        # Extract modification notes for pattern analysis
        mod_notes = [s["modification_note"] for s in modified if s.get("modification_note")]

        profile["commands"][cmd] = {
            "total_signals":       total,
            "acceptance_rate":     round(accept_rate, 2),
            "accepted":            len(accepted),
            "modified":            len(modified),
            "rejected":            len(rejected),
            "common_modifications": mod_notes[:10],  # last 10 modification notes
            "preference_hint":     _derive_hint(cmd, accept_rate, mod_notes),
        }

    _atomic_write_json(PROFILE, profile)
    print(f"{GREEN}✓ Preference profile updated{RESET}")
    return profile


def _derive_hint(command: str, accept_rate: float, mod_notes: list[str]) -> str:
    """Generate a plain-english preference hint from signals."""
    if accept_rate >= 0.80:
        return f"High acceptance ({accept_rate:.0%}). Current approach well-calibrated."
    elif accept_rate >= 0.50:
        hints = []
        if mod_notes:
            # Most common words in modification notes = what keeps changing
            from collections import Counter
            import re
            words = []
            for note in mod_notes:
                words.extend(re.findall(r'\b[a-z]{4,}\b', note.lower()))
            common = [w for w, _ in Counter(words).most_common(5)
                      if w not in {"that","this","with","from","have","been","were"}]
            if common:
                hints.append(f"Frequent modifications around: {', '.join(common)}")
        return "; ".join(hints) if hints else f"Moderate acceptance ({accept_rate:.0%}). Review modification patterns."
    else:
        return f"Low acceptance ({accept_rate:.0%}). This command needs recalibration."


def load_profile() -> dict:
    if not PROFILE.exists():
        return {}
    try:
        return json.loads(PROFILE.read_text())
    except Exception:
        return {}


def get_injection_context(command: str) -> str:
    """
    Return preference context to inject into a command prompt.
    Called by /plan, /design, /brainstorm before generating output.
    """
    profile = load_profile()
    if not profile or command not in profile.get("commands", {}):
        return ""

    cmd_prof = profile["commands"][command]
    if cmd_prof["total_signals"] < 5:
        return ""  # Not enough data yet

    lines = [f"\n## Developer Preferences for /{command}\n"]
    lines.append(f"_Based on {cmd_prof['total_signals']} past sessions "
                 f"(acceptance rate: {cmd_prof['acceptance_rate']:.0%})_\n")

    hint = cmd_prof.get("preference_hint", "")
    if hint:
        lines.append(f"**Calibration note:** {hint}\n")

    mods = cmd_prof.get("common_modifications", [])
    if mods:
        lines.append("**Typical modifications this developer makes:**")
        for m in mods[:5]:
            lines.append(f"- {m}")
        lines.append("")

    lines.append("_Adjust your output to align with these patterns._\n")
    return "\n".join(lines)


def prompt_feedback(command: str, context_summary: str = "") -> str:
    """
    Interactive one-line feedback prompt. Called after command output.
    Returns signal type string.
    """
    print(f"\n{DIM}Was /{command} on target? "
          f"(y=yes / p=partially: reason / n=no: reason){RESET} ", end="", flush=True)
    try:
        response = input().strip()
    except (EOFError, KeyboardInterrupt):
        return "skipped"

    if response.lower() in ("y", "yes", ""):
        log_signal(command, "accepted",
                   context_summary=context_summary)
        return "accepted"
    elif response.lower().startswith("p"):
        note = response[1:].strip(": ").strip()
        log_signal(command, "modified",
                   context_summary=context_summary,
                   modification_note=note)
        return "modified"
    elif response.lower().startswith("n"):
        note = response[1:].strip(": ").strip()
        log_signal(command, "rejected",
                   context_summary=context_summary,
                   modification_note=note)
        return "rejected"
    return "skipped"


def show_profile():
    profile = load_profile()
    signals = load_signals()
    print(f"\n{BOLD}{CYAN}━━━ DEVELOPER TASTE PROFILE ━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Total signals: {len(signals)}")
    print(f"  Last updated:  {profile.get('generated_at', 'never')[:10]}")

    if not profile.get("commands"):
        print(f"\n  {DIM}No preference data yet. "
              f"Signals are collected after /design, /plan, /brainstorm.{RESET}")
    else:
        for cmd, data in profile["commands"].items():
            color = (GREEN if data["acceptance_rate"] >= 0.8
                     else YELLOW if data["acceptance_rate"] >= 0.5 else RED)
            print(f"\n  /{cmd}  "
                  f"[{data['total_signals']} signals | "
                  f"{color}{data['acceptance_rate']:.0%} accepted{RESET}]")
            hint = data.get("preference_hint", "")
            if hint:
                print(f"    {DIM}{hint}{RESET}")
            mods = data.get("common_modifications", [])
            if mods:
                print(f"    Frequent mods: {mods[0][:80]}")
    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def review_checkpoints():
    """
    Every 10 sessions, generate a human-review report.
    Human must approve/reject the learned patterns.
    """
    signals = load_signals()
    if len(signals) < 10:
        print(f"{DIM}Need at least 10 signals for a review checkpoint. "
              f"Currently: {len(signals)}{RESET}")
        return

    profile = load_profile()
    print(f"\n{BOLD}{CYAN}━━━ APEX LEARNING REVIEW CHECKPOINT ━━━━━━━━━━━━━━━{RESET}")
    print(f"{YELLOW}⚠ Review what APEX thinks it has learned.{RESET}")
    print(f"{YELLOW}  Approve to apply these patterns. Reject to reset.{RESET}\n")

    for cmd, data in profile.get("commands", {}).items():
        print(f"  /{cmd}: APEX believes you prefer...")
        hint = data.get("preference_hint", "No clear pattern yet")
        print(f"    {hint}")
        mods = data.get("common_modifications", [])
        if mods:
            print(f"    Common changes: {'; '.join(mods[:3])}")
        print()

    print("Approve these learnings? (yes / no - reset all): ", end="", flush=True)
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if answer in ("yes", "y"):
        profile["human_approved_at"] = datetime.now(timezone.utc).isoformat()
        _atomic_write_json(PROFILE, profile)
        print(f"{GREEN}✓ Learnings approved and locked in{RESET}")
    else:
        # Reset signals and profile
        # os.replace() handles existing .bak on Windows (Path.rename would fail)
        if SIGNALS.exists():
            import os as _os
            _os.replace(str(SIGNALS), str(SIGNALS.with_suffix(".jsonl.bak")))
        if PROFILE.exists():
            import os as _os
            _os.replace(str(PROFILE), str(PROFILE.with_suffix(".json.bak")))
        print(f"{GREEN}✓ Signals reset. APEX will relearn from scratch.{RESET}")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "profile":
        show_profile()
        return

    cmd = args[0]
    if cmd == "log":
        if len(args) < 3:
            print("Usage: taste_memory.py log <command> <accepted|modified|rejected> "
                  "[context] [note]")
            sys.exit(1)
        log_signal(
            command         = args[1],
            signal_type     = args[2],
            context_summary = args[3] if len(args) > 3 else "",
            modification_note = args[4] if len(args) > 4 else "",
        )
    elif cmd == "inject":
        command = args[1] if len(args) > 1 else "plan"
        ctx = get_injection_context(command)
        print(ctx if ctx else f"{DIM}No preference context available for /{command}{RESET}")
    elif cmd == "review":
        review_checkpoints()
    elif cmd == "rebuild":
        signals = load_signals()
        _update_profile(signals)
    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
