#!/usr/bin/env python3
"""
APEX Context Guard — Context Pressure Measurement + Active Forgetting Triggers
===============================================================================
Measures context window pressure from three orthogonal signals and returns
structured pressure data. Called by session-pollution.sh on every UserPromptSubmit.

Three pressure signals:
  Turn pressure   — conversations degrade after ~20 meaningful turns
  Token pressure  — estimated from token_tracker session totals
  Base pressure   — CLAUDE.md size (larger = less room for turns)

Thresholds:
  < 50%  — CLEAN    (no action)
  50-69% — WARNING  (hint about /compact)
  70-84% — HIGH     (recitation injection — arXiv:2601.11564 technique)
  85%+   — CRITICAL (compaction trigger — active forgetting substitute)

Recitation technique (arXiv:2601.11564):
  At HIGH pressure, prepend a reminder for Claude to re-anchor to project
  constraints before answering. Proven +4% accuracy on long-context tasks.

Usage:
  python3 .claude/intelligence/context_guard.py check
  python3 .claude/intelligence/context_guard.py status
  echo "prompt text" | python3 .claude/intelligence/context_guard.py inject
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path.cwd()
APEX_DIR  = ROOT / ".claude"
LOGS_DIR  = APEX_DIR / "logs"
TURNS_FILE = LOGS_DIR / "session_turns.txt"
CLAUDE_MD  = ROOT / "CLAUDE.md"

# ── Thresholds ─────────────────────────────────────────────────────────────────
# 50-69%: silent (let basic turn counter handle it)
# 70-84%: recitation injection (arXiv:2601.11564 technique)
# 85-94%: compaction warning
# 95%+:   hard block — compaction required
HIGH_THRESHOLD     = 70   # %  → recitation injection
CRITICAL_THRESHOLD = 85   # %  → compaction warning
BLOCK_THRESHOLD    = 95   # %  → hard block

# Turn caps (past these the model quality measurably degrades)
TURN_HIGH     = 20
TURN_CRITICAL = 28
TURN_BLOCK    = 35

# Token caps (heuristic — Claude Code 200K context, ~15% session overhead)
TOKEN_WARN_K     = 60    # ~60K tokens
TOKEN_HIGH_K     = 100   # ~100K tokens
TOKEN_CRITICAL_K = 140   # ~140K tokens

# CLAUDE.md size thresholds (tokens) — larger = more base context pressure
CLAUDE_LARGE_T = 200   # tokens (~800 chars)
CLAUDE_HUGE_T  = 600   # tokens (~2400 chars) — 600 is the cap from plan

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"


# ── Signal readers ─────────────────────────────────────────────────────────────

def _read_turns() -> int:
    try:
        return int(TURNS_FILE.read_text().strip())
    except Exception:
        return 0


def _read_tokens_k() -> float:
    """Return today's session token total in thousands via token_intelligence."""
    try:
        _intel = Path(__file__).parent
        if str(_intel) not in sys.path:
            sys.path.insert(0, str(_intel))
        from token_intelligence import _load_session_stats
        stats = _load_session_stats()
        return stats.get("today_tokens", 0) / 1000.0
    except Exception:
        return 0.0


def _read_claude_md_tokens() -> int:
    """Return estimated CLAUDE.md token count. Returns 0 if file absent."""
    if not CLAUDE_MD.exists():
        return 0
    try:
        _intel = Path(__file__).parent
        if str(_intel) not in sys.path:
            sys.path.insert(0, str(_intel))
        from token_intelligence import _measure_claude_md
        return _measure_claude_md()
    except Exception:
        try:
            return len(CLAUDE_MD.read_text(encoding="utf-8", errors="ignore")) // 4
        except Exception:
            return 0


# ── Pressure computation ───────────────────────────────────────────────────────

def compute_pressure() -> dict:
    """
    Compute context pressure (0–100) from three signals.
    Returns a dict with pressure, level, signals, and recommendation.

    Pressure formula (plan spec):
      pressure = max(turns/30, session_tokens/100_000, claude_md_tokens/600)
    All three normalized to 0.0–1.0, worst signal wins.
    """
    turns    = _read_turns()
    tok_k    = _read_tokens_k()
    md_tokens = _read_claude_md_tokens()

    # Normalize each signal to 0–100 (plan formula, linear)
    turn_score  = min(100, int(turns / 30 * 100))
    tok_score   = min(100, int(tok_k * 1000 / 100_000 * 100))   # tok_k*1000 = raw tokens
    md_score    = min(100, int(md_tokens / 600 * 100))

    # Worst signal wins (plan: "take the worst")
    pressure = max(turn_score, tok_score, md_score)

    if pressure >= BLOCK_THRESHOLD:
        level = "BLOCK"
        recommendation = "block"
    elif pressure >= CRITICAL_THRESHOLD:
        level = "CRITICAL"
        recommendation = "compact"
    elif pressure >= HIGH_THRESHOLD:
        level = "HIGH"
        recommendation = "recite"
    else:
        # 0–69%: silent — let basic turn counter handle low-level hints
        level = "CLEAN"
        recommendation = "none"

    return {
        "pressure": pressure,
        "level": level,
        "recommendation": recommendation,
        "signals": {
            "turns": turns,
            "turn_score": turn_score,
            "tokens_k": round(tok_k, 1),
            "token_score": tok_score,
            "claude_md_tokens": md_tokens,
            "md_score": md_score,
        },
    }


# ── Output generators ──────────────────────────────────────────────────────────

def get_warning_message(data: dict) -> str:
    """Return a warning string to print to stdout (hooks call this)."""
    level = data["level"]
    pressure = data["pressure"]
    turns = data["signals"]["turns"]

    if level == "CLEAN":
        return ""   # 0–69%: silent, basic turn counter handles low-level hints

    if level == "HIGH":
        return (
            f"\n{YELLOW}⚠ APEX Context: {pressure}% pressure (turn {turns}).{RESET}\n"
            f"{DIM}Re-anchoring to project constraints before responding...{RESET}\n"
        )

    if level == "CRITICAL":
        return (
            f"\n{YELLOW}⚠ APEX Context: {pressure}% — quality may degrade soon.{RESET}\n"
            f"Consider /compact before starting the next task.\n"
            f"{DIM}APEX will re-inject your project context after compaction.{RESET}\n"
        )

    if level == "BLOCK":
        return (
            f"\n{RED}⛔ APEX Context: {pressure}%+ — compaction required before proceeding.{RESET}\n"
            f"{BOLD}Run /compact now.{RESET} Your brain context will be automatically\n"
            f"re-injected when the new session starts.\n"
        )

    return ""


def get_recitation_prompt(data: dict) -> str:
    """
    At HIGH pressure: return a recitation anchor to prepend to context.
    Technique from arXiv:2601.11564 — forcing recitation of key facts
    before answering improves long-context accuracy by ~4%.
    """
    if data["level"] not in ("HIGH", "CRITICAL", "BLOCK"):
        return ""

    pct = data["pressure"]
    base = (
        f"\nAPEX [Context {pct}%]: Before answering, state in one sentence: "
        f"what you're currently working on and the top constraint for this project. "
        f"Then proceed normally.\n"
    )

    # Augment with CLAUDE.md Hard Rules when available (more specific re-anchor)
    try:
        md = CLAUDE_MD.read_text(encoding="utf-8", errors="ignore")
        sections = []
        for heading in ("Hard Rules", "Critical Conventions"):
            start = md.find(f"## {heading}")
            if start == -1:
                continue
            end = md.find("\n## ", start + 1)
            chunk = md[start:end].strip() if end != -1 else md[start:].strip()
            if chunk:
                sections.append(chunk[:400])
        if sections:
            anchor = "\n".join(sections)
            return (
                f"\nAPEX [Context {pct}%]: Before answering, re-confirm these "
                f"constraints are still active, then proceed:\n{anchor}\n"
            )
    except Exception:
        pass

    return base


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"

    if cmd == "check":
        # Used by session-pollution.sh: print warning if needed, exit
        data = compute_pressure()
        msg = get_warning_message(data)
        if msg:
            print(msg)
        # Recitation anchor for HIGH/CRITICAL/BLOCK
        if data["level"] in ("HIGH", "CRITICAL", "BLOCK"):
            anchor = get_recitation_prompt(data)
            if anchor:
                print(anchor)

    elif cmd == "status":
        # Human-readable status report
        data = compute_pressure()
        s = data["signals"]
        level = data["level"]
        pressure = data["pressure"]
        color = {
            "CLEAN": GREEN, "HIGH": YELLOW,
            "CRITICAL": YELLOW, "BLOCK": RED,
        }.get(level, DIM)
        print(f"\n{BOLD}Context Pressure: {color}{pressure}% [{level}]{RESET}")
        print(f"  Turns:     {s['turns']} (score {s['turn_score']})")
        print(f"  Tokens:    {s['tokens_k']:.1f}K (score {s['token_score']})")
        print(f"  CLAUDE.md: {s['claude_md_tokens']} tokens (score {s['md_score']})")
        print(f"  Action:    {data['recommendation']}")

    elif cmd == "inject":
        # Returns recitation prompt when pressure warrants it
        data = compute_pressure()
        if data["level"] in ("HIGH", "CRITICAL", "BLOCK"):
            anchor = get_recitation_prompt(data)
            if anchor:
                print(anchor)

    elif cmd == "json":
        data = compute_pressure()
        print(json.dumps(data, indent=2))

    else:
        print(f"Usage: context_guard.py [check|status|inject|json]")
        sys.exit(1)


if __name__ == "__main__":
    main()
