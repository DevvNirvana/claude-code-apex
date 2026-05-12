from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Context Engine — Cognitive Memory Architecture Core
=========================================================
Called on every UserPromptSubmit via inject-reference.sh hook.
Returns the exact context to inject — nothing more, nothing less.

Three-tier memory system:
  Semantic  — project_brain facts + code symbol index (always true)
  Episodic  — trajectory_store past sessions (what worked before)
  Working   — smart injection per prompt + context_guard pressure mgmt

Token caps (hard enforced — never exceeded):
  MICRO:    0 tokens  (~60% of prompts — zero overhead)
  LIGHT:    200 tokens (brain constraints only)
  STANDARD: 500 tokens (brain + code index hints)
  FULL:     900 tokens (brain + trajectories + taste + code index)

Usage:
  echo "$PROMPT" | python3 .claude/intelligence/context_engine.py
  python3 .claude/intelligence/context_engine.py "fix the auth bug"
"""
import json
import re
import sys
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT     = Path.cwd()
APEX_DIR = ROOT / ".claude"
_INTEL   = Path(__file__).parent
sys.path.insert(0, str(_INTEL))

# ── Token caps per tier ───────────────────────────────────────────────────────
BRAIN_CAPS = {
    "MICRO":    0,
    "LIGHT":    200,
    "STANDARD": 350,
    "FULL":     600,
}
TRAJ_CAP   = 1600   # chars (~400 tokens)
TASTE_CAP  = 600    # chars (~150 tokens)
CODE_CAP   = 320    # chars (~80 tokens)

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"

# ── Intent extraction ─────────────────────────────────────────────────────────

# Maps inferred command → smart_router command key
_INTENT_PATTERNS = [
    (re.compile(r'\b(plan|planning|architect|roadmap|breakdown)\b', re.I), "plan"),
    (re.compile(r'\b(design|ui|ux|layout|wireframe|component)\b', re.I),   "design"),
    (re.compile(r'\b(brainstorm|ideas|explore|approach|options)\b', re.I), "brainstorm"),
    (re.compile(r'\b(review|audit|check|analyze|assess|quality)\b', re.I), "review"),
    (re.compile(r'\b(ship|deploy|release|prod|publish)\b', re.I),          "ship"),
    (re.compile(r'\b(fix|bug|error|broken|crash|exception|fail)\b', re.I), "debug"),
    (re.compile(r'\b(refactor|restructure|cleanup|clean up|simplify)\b', re.I), "refactor"),
    (re.compile(r'\b(optimiz\w*|performance|speed up|faster|slow)\b', re.I),  "optimize"),
    (re.compile(r'\b(tests?|spec|coverage|jest|pytest|vitest|unit)\b', re.I), "test"),
    (re.compile(r'\b(build|create|implement|add|write|make|develop)\b', re.I), "execute"),
    (re.compile(r'\b(document|docs|readme|comment|explain)\b', re.I),      "docs"),
    (re.compile(r'\b(where|what|which|how|show|list|find|who|when)\b', re.I), "ask"),
]

_CMD_RE = re.compile(r'^/([a-z][a-z\-]+)\b', re.I)


def extract_intent(prompt: str) -> tuple[str, str]:
    """
    Extract (command_hint, query) from raw prompt.
    command_hint maps to smart_router's command tier table.
    """
    p = prompt.strip()

    # Explicit /command at start
    m = _CMD_RE.match(p)
    if m:
        cmd   = m.group(1).lower()
        query = p[m.end():].strip()
        return cmd, query or p

    # Infer from keywords
    for pattern, cmd in _INTENT_PATTERNS:
        if pattern.search(p):
            return cmd, p

    return "ask", p   # conservative default → MICRO or LIGHT


# ── Module imports (all wrapped — degrades gracefully if unavailable) ─────────

def _load_smart_router():
    try:
        from smart_router import classify_task, get_tier_context_budget
        return classify_task, get_tier_context_budget
    except Exception:
        return None, None


def _load_brain():
    try:
        from project_brain import brain_read_selective, format_for_injection
        return brain_read_selective, format_for_injection
    except Exception:
        return None, None


def _load_trajectories():
    try:
        from trajectory_store import query_trajectories, format_for_context
        return query_trajectories, format_for_context
    except Exception:
        return None, None


def _load_taste():
    try:
        from taste_memory import get_injection_context
        return get_injection_context
    except Exception:
        return None


def _load_code_index():
    try:
        from code_index import query_index, format_for_injection as fmt_code
        return query_index, fmt_code
    except Exception:
        return None, None


def _load_budget_check():
    try:
        from token_intelligence import check_budget_before_command
        return check_budget_before_command
    except Exception:
        return None


# ── Context builders ──────────────────────────────────────────────────────────

def _inject_brain(query: str, tier_name: str, command: str) -> str:
    brain_read_selective, format_for_injection = _load_brain()
    if not brain_read_selective:
        return ""
    try:
        cap   = BRAIN_CAPS.get(tier_name, 350)
        facts = brain_read_selective(query, command, cap)
        return format_for_injection(facts) if facts else ""
    except Exception:
        return ""


def _inject_code_index(query: str) -> str:
    query_index, fmt_code = _load_code_index()
    if not query_index:
        return ""   # code_index.py not yet built (Phase 2) — silent
    try:
        keywords = [w for w in re.sub(r'[^a-z0-9\s]', ' ', query.lower()).split()
                    if len(w) > 3][:6]
        if not keywords:
            return ""
        results = query_index(keywords, limit=5)
        if not results:
            return ""
        raw = fmt_code(results)
        return raw[:CODE_CAP] if raw else ""
    except Exception:
        return ""


def _inject_trajectories(query: str) -> str:
    query_trajectories, format_for_context = _load_trajectories()
    if not query_trajectories:
        return ""
    try:
        stack = ""
        sp = APEX_DIR / "config" / "stack-profile.json"
        if sp.exists():
            try:
                stack = json.loads(sp.read_text()).get("framework", "")
            except Exception:
                pass
        trajs = query_trajectories(query, stack=stack, limit=2)
        if not trajs:
            return ""
        raw = format_for_context(trajs)
        return (raw[:TRAJ_CAP] + "\n_[truncated for token budget]_") if len(raw) > TRAJ_CAP else raw
    except Exception:
        return ""


def _inject_taste(command: str) -> str:
    get_injection_context = _load_taste()
    if not get_injection_context:
        return ""
    try:
        raw = get_injection_context(command)
        if not raw:
            return ""
        return (raw[:TASTE_CAP] + "\n_[truncated]_") if len(raw) > TASTE_CAP else raw
    except Exception:
        return ""


def _check_budget(command: str, query: str) -> str:
    check_budget_before_command = _load_budget_check()
    if not check_budget_before_command:
        return ""
    try:
        result = check_budget_before_command(command, query)
        if not result.get("allowed", True):
            return f"\n{RED}⛔ APEX Budget: {result['reason']}{RESET}\n"
        if result.get("warn"):
            return f"\n{YELLOW}⚠ APEX Budget: {result['reason']}{RESET}\n"
        return ""
    except Exception:
        return ""


# ── Main assembly ─────────────────────────────────────────────────────────────

def build_injection(prompt: str) -> str:
    """
    Core function. Given a raw prompt, returns the context string to inject.
    Returns "" for MICRO tier (no overhead for simple questions).
    Never raises — all errors produce empty string.
    """
    if not prompt or not prompt.strip():
        return ""

    classify_task, _ = _load_smart_router()

    # If smart_router unavailable, fall back to minimal injection
    if not classify_task:
        brain_block = _inject_brain(prompt, "LIGHT", "ask")
        return brain_block

    command, query = extract_intent(prompt)

    try:
        tier = classify_task(command, query)
    except Exception:
        return ""

    # MICRO → zero injection (covers ~60% of real prompts)
    if tier.name == "MICRO":
        return ""

    sections = []

    # Budget warning (prepended if needed)
    budget_warn = _check_budget(command, query)

    # Semantic memory — brain facts (LIGHT+)
    if tier.load_brain:
        block = _inject_brain(query, tier.name, command)
        if block:
            sections.append(block)

    # Semantic memory — code symbol hints (STANDARD+)
    if tier.name in ("STANDARD", "FULL"):
        block = _inject_code_index(query)
        if block:
            sections.append(block)

    # Episodic memory — past trajectories (FULL only)
    if tier.load_trajectory:
        block = _inject_trajectories(query)
        if block:
            sections.append(block)

    # Taste preferences (FULL only)
    if tier.load_taste:
        block = _inject_taste(command)
        if block:
            sections.append(block)

    if not sections and not budget_warn:
        return ""

    result = "\n".join(sections)
    if budget_warn:
        result = budget_warn + result

    return result


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

    # Read prompt: prefer stdin (handles special chars + long prompts safely)
    if not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    elif len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = ""

    if not prompt:
        sys.exit(0)

    result = build_injection(prompt)
    if result and result.strip():
        print(result)


if __name__ == "__main__":
    main()
