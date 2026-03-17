#!/usr/bin/env python3
"""
Evaluator — Self-Scoring Engine for APEX Commands
==================================================
Tracks command output quality using deterministic rubrics.
No additional Claude API calls — scores are computed from
observable outcomes: developer fixes, plan completion rates,
taste signals.

Scoring rubrics:
  /review  — pct of flagged issues subsequently fixed
  /plan    — pct of planned tasks completed without unplanned additions
  /design  — explicit taste signal acceptance rate
  /ship    — pct of SHIP verdicts that deployed without incident

Human review checkpoint every 10 sessions.

Usage:
  python3 .claude/intelligence/evaluator.py record <command> <outcome_json>
  python3 .claude/intelligence/evaluator.py score <command>
  python3 .claude/intelligence/evaluator.py report
  python3 .claude/intelligence/evaluator.py checkpoint
"""
import json, sys, os, tempfile
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

ROOT   = Path.cwd()
EVAL   = ROOT / ".claude" / "memory" / "evaluations.jsonl"

CYAN  = "\033[0;36m"; GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"
DIM   = "\033[2m";    BOLD  = "\033[1m";    RESET  = "\033[0m"
RED   = "\033[0;31m"

CHECKPOINT_INTERVAL = 10  # sessions between human review prompts


def _atomic_append(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_evals() -> list[dict]:
    if not EVAL.exists():
        return []
    evals = []
    for line in EVAL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                evals.append(json.loads(line))
            except Exception:
                continue
    return evals


def record_outcome(
    command: str,
    outcome_type: str,
    score: float,
    metadata: dict = None,
):
    """
    Record a command outcome for scoring.

    outcome_type examples:
      review.issue_fixed        — a flagged review issue was fixed
      review.false_positive     — a flagged issue was dismissed
      plan.task_completed       — a planned task finished as expected
      plan.unplanned_addition   — a task was added not in original plan
      design.accepted           — design used without changes
      design.modified           — design was changed significantly
      ship.clean_deploy         — shipped without post-deploy issues
      ship.rollback             — had to roll back after deploy
    """
    entry = {
        "command":      command,
        "outcome_type": outcome_type,
        "score":        round(score, 3),
        "metadata":     metadata or {},
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }
    _atomic_append(EVAL, json.dumps(entry))
    return entry


def compute_command_score(command: str) -> dict:
    """Compute aggregate quality score for a command."""
    evals = [e for e in load_evals() if e["command"] == command]
    if not evals:
        return {"command": command, "score": None,
                "message": "No evaluation data yet"}

    # Aggregate by outcome category
    by_type = defaultdict(list)
    for e in evals:
        by_type[e["outcome_type"]].append(e["score"])

    all_scores = [e["score"] for e in evals]
    avg = sum(all_scores) / len(all_scores)
    trend = _compute_trend(evals)

    result = {
        "command":        command,
        "score":          round(avg, 2),
        "total_outcomes": len(evals),
        "trend":          trend,
        "breakdown":      {k: round(sum(v) / len(v), 2) for k, v in by_type.items()},
        "grade":          _grade(avg),
    }
    return result


def _grade(score: float) -> str:
    if score >= 0.85:   return "A"
    elif score >= 0.75: return "B"
    elif score >= 0.60: return "C"
    elif score >= 0.40: return "D"
    else:               return "F"


def _compute_trend(evals: list[dict]) -> str:
    """Simple trend: compare first half vs second half scores."""
    if len(evals) < 6:
        return "insufficient_data"
    mid   = len(evals) // 2
    first = sum(e["score"] for e in evals[:mid]) / mid
    last  = sum(e["score"] for e in evals[mid:]) / (len(evals) - mid)
    if last > first + 0.05:   return "improving"
    elif last < first - 0.05: return "degrading"
    else:                     return "stable"


def show_report():
    evals = load_evals()
    if not evals:
        print(f"{DIM}No evaluation data yet.{RESET}")
        print(f"{DIM}Outcomes are recorded as you use APEX commands.{RESET}")
        return

    commands = list({e["command"] for e in evals})
    print(f"\n{BOLD}{CYAN}━━━ APEX COMMAND QUALITY REPORT ━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Total outcomes recorded: {len(evals)}\n")

    for cmd in sorted(commands):
        result = compute_command_score(cmd)
        score  = result.get("score")
        if score is None:
            continue
        grade  = result["grade"]
        trend  = result["trend"]
        trend_icon = {"improving": "↑", "degrading": "↓",
                      "stable": "→", "insufficient_data": "?"}.get(trend, "?")
        color = (GREEN if score >= 0.75 else
                 YELLOW if score >= 0.55 else RED)
        print(f"  /{cmd:12} {color}Grade {grade} ({score:.0%}){RESET} "
              f"{trend_icon} {trend} "
              f"[{result['total_outcomes']} outcomes]")
        breakdown = result.get("breakdown", {})
        for otype, bscore in sorted(breakdown.items()):
            bc = GREEN if bscore >= 0.75 else (YELLOW if bscore >= 0.5 else RED)
            print(f"    {DIM}{otype:30}{bc}{bscore:.0%}{RESET}")
        print()

    # Check if checkpoint needed
    session_count = _count_sessions(evals)
    if session_count > 0 and session_count % CHECKPOINT_INTERVAL == 0:
        print(f"{YELLOW}⚠ Checkpoint due: {session_count} sessions recorded. "
              f"Run: python3 .claude/intelligence/evaluator.py checkpoint{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def _count_sessions(evals: list[dict]) -> int:
    """Estimate number of distinct sessions from timestamp clustering."""
    if not evals:
        return 0
    days = set()
    for e in evals:
        try:
            d = datetime.fromisoformat(e["timestamp"]).date()
            days.add(d)
        except Exception:
            pass
    return len(days)


def run_checkpoint():
    """Human review checkpoint — show what APEX has learned, get approval."""
    evals = load_evals()
    commands = list({e["command"] for e in evals})

    print(f"\n{BOLD}{CYAN}━━━ APEX LEARNING CHECKPOINT ━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{YELLOW}Review what APEX has observed about command quality.{RESET}")
    print(f"{YELLOW}Approve to continue learning. Reject to reset.\n{RESET}")

    for cmd in sorted(commands):
        result = compute_command_score(cmd)
        if result.get("score") is None:
            continue
        print(f"  /{cmd}: score={result['score']:.0%} "
              f"grade={result['grade']} trend={result['trend']}")
        worst = sorted(result.get("breakdown", {}).items(),
                       key=lambda x: x[1])[:2]
        for otype, bscore in worst:
            if bscore < 0.6:
                print(f"    {RED}Weak area: {otype} ({bscore:.0%}){RESET}")

    print("\nApprove these evaluations? (yes / no - reset): ", end="", flush=True)
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return

    if answer not in ("yes", "y"):
        if EVAL.exists():
            import os as _os
            _os.replace(str(EVAL), str(EVAL.with_suffix(".jsonl.bak")))
        print(f"{GREEN}✓ Evaluations reset.{RESET}")
    else:
        print(f"{GREEN}✓ Evaluations approved — continuing to learn.{RESET}")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "report":
        show_report()
        return

    cmd = args[0]
    if cmd == "record":
        if len(args) < 4:
            print("Usage: evaluator.py record <command> <outcome_type> <score>")
            sys.exit(1)
        record_outcome(
            command      = args[1],
            outcome_type = args[2],
            score        = float(args[3]),
            metadata     = json.loads(args[4]) if len(args) > 4 else {},
        )
        print(f"{GREEN}✓ Outcome recorded{RESET}")

    elif cmd == "score":
        command = args[1] if len(args) > 1 else "review"
        result  = compute_command_score(command)
        print(json.dumps(result, indent=2))

    elif cmd == "checkpoint":
        run_checkpoint()

    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
