#!/usr/bin/env python3
"""
Trajectory Store — Experience Replay for APEX
==============================================
Research basis: NeurIPS 2025 Self-Generated In-Context Examples.
Storing successful session trajectories and injecting them as
in-context examples lifts planning accuracy from ~73% to ~89%
with zero model training required.

A trajectory is a complete record of a successful session:
task → plan → execute → ship. When a similar task recurs,
the most relevant 2-3 trajectories are injected as context.

Usage:
  python3 .claude/intelligence/trajectory_store.py store <json_file>
  python3 .claude/intelligence/trajectory_store.py query "build auth flow"
  python3 .claude/intelligence/trajectory_store.py list
  python3 .claude/intelligence/trajectory_store.py stats
"""
from __future__ import annotations
import json, sys, hashlib, os, tempfile
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

ROOT    = Path.cwd()
STORE   = ROOT / ".claude" / "memory" / "trajectories"
GLOBAL  = Path.home() / ".apex" / "global-trajectories"

CYAN  = "\033[0;36m"; GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"
DIM   = "\033[2m";    BOLD  = "\033[1m";    RESET  = "\033[0m"
RED   = "\033[0;31m"

STOP_WORDS = {
    "a","an","the","and","or","in","on","to","for","of","with","by","is","it"
}

# Synonym map — same as cache_manager for consistency
SYNONYMS = {
    "build": "create", "make": "create", "add": "create",
    "implement": "create", "develop": "create", "write": "create",
    "auth": "login", "authentication": "login", "signin": "login",
    "signup": "register", "logout": "signout",
    "ui": "frontend", "interface": "frontend", "view": "frontend",
    "screen": "page", "route": "page",
    "component": "widget", "element": "widget",
    "db": "database", "data": "database",
    "query": "fetch", "retrieve": "fetch", "load": "fetch", "get": "fetch",
    "api": "endpoint", "handler": "endpoint", "controller": "endpoint",
    "fix": "debug", "bug": "debug", "error": "debug", "issue": "debug",
    "optimize": "performance", "speed": "performance",
    "test": "spec", "testing": "spec",
    "docs": "documentation", "document": "documentation",
    "refactor": "restructure", "cleanup": "restructure",
}

def _tokenize(text: str) -> set:
    import re
    words = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    filtered = [w for w in words if len(w) > 1 and w not in STOP_WORDS]
    normalized = [SYNONYMS.get(w, w) for w in filtered]
    return set(normalized)

def _similarity(a: str, b: str) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    return (0.4 * inter / len(ta | tb)) + (0.6 * inter / min(len(ta), len(tb)))

def _atomic_write(path: Path, data: dict):
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

def ensure_dirs():
    STORE.mkdir(parents=True, exist_ok=True)

def store_trajectory(trajectory: dict) -> str:
    """
    Store a completed session trajectory.

    Required fields:
      task_description: str       — what was built
      task_type:        str       — plan/auth_flow/etc from classifier
      stack:            str       — "nextjs-typescript-supabase"
      session_summary:  str       — what was actually built
      key_decisions:    list[str] — architectural choices made
      what_worked:      str       — patterns that succeeded
      what_to_avoid:    str       — pitfalls encountered
      ship_verdict:     str       — SHIP / HOLD / HOLD_CRITICAL

    Optional:
      author:           str       — defaults to "developer"
      project:          str       — project name
      total_tasks:      int
      tasks_completed:  int
      promote_global:   bool      — copy to ~/.apex/global-trajectories
    """
    ensure_dirs()

    tid = hashlib.sha256(
        (trajectory.get("task_description", "") +
         datetime.now(timezone.utc).isoformat()).encode()
    ).hexdigest()[:16]

    entry = {
        "trajectory_id":    tid,
        "task_description": trajectory.get("task_description", ""),
        "task_type":        trajectory.get("task_type", "general"),
        "stack":            trajectory.get("stack", ""),
        "framework":        trajectory.get("framework", ""),
        "session_summary":  trajectory.get("session_summary", ""),
        "key_decisions":    trajectory.get("key_decisions", []),
        "what_worked":      trajectory.get("what_worked", ""),
        "what_to_avoid":    trajectory.get("what_to_avoid", ""),
        "total_tasks":      trajectory.get("total_tasks", 0),
        "tasks_completed":  trajectory.get("tasks_completed", 0),
        "ship_verdict":     trajectory.get("ship_verdict", "SHIP"),
        "author":           trajectory.get("author", "developer"),
        "project":          trajectory.get("project", ""),
        "timestamp":        datetime.now(timezone.utc).isoformat(),
        "quality_score":    _compute_quality(trajectory),
    }

    path = STORE / f"{tid}.json"
    _atomic_write(path, entry)

    if trajectory.get("promote_global") and entry["quality_score"] >= 0.8:
        GLOBAL.mkdir(parents=True, exist_ok=True)
        _atomic_write(GLOBAL / f"{tid}.json", entry)
        print(f"{GREEN}✓ Trajectory promoted to global store{RESET}")

    print(f"{GREEN}✓ Trajectory stored: {tid}{RESET}")
    print(f"  Task: {entry['task_description'][:60]}")
    print(f"  Quality score: {entry['quality_score']:.2f}")
    return tid

def _compute_quality(t: dict) -> float:
    """Score a trajectory by completeness and success signals."""
    score = 0.0
    if t.get("ship_verdict") == "SHIP":       score += 0.4
    elif t.get("ship_verdict") == "HOLD":     score += 0.2
    total = t.get("total_tasks", 0)
    done  = t.get("tasks_completed", 0)
    if total > 0:
        score += 0.3 * (done / total)
    if t.get("key_decisions"):                score += 0.1
    if t.get("what_to_avoid"):                score += 0.1
    if t.get("session_summary"):              score += 0.1
    return round(min(score, 1.0), 2)

def query_trajectories(
    task_description: str,
    stack: str = "",
    task_type: str = "",
    limit: int = 3,
    min_quality: float = 0.5,
    include_global: bool = True,
) -> list[dict]:
    """
    Return the N most relevant trajectories for a given task.
    Used by /plan and /brainstorm to inject experience-replay context.
    """
    ensure_dirs()
    candidates = []

    search_dirs = [STORE]
    if include_global and GLOBAL.exists():
        search_dirs.append(GLOBAL)

    seen_ids = set()
    for search_dir in search_dirs:
        for f in search_dir.glob("*.json"):
            try:
                t = json.loads(f.read_text())
                tid = t.get("trajectory_id", f.stem)
                if tid in seen_ids:
                    continue
                seen_ids.add(tid)
                if t.get("quality_score", 0) < min_quality:
                    continue
                if t.get("ship_verdict") not in ("SHIP", "HOLD"):
                    continue

                # Compute relevance score
                text_sim   = _similarity(task_description, t.get("task_description", ""))
                type_bonus  = 0.15 if task_type and t.get("task_type") == task_type else 0.0
                stack_bonus = 0.10 if stack and stack in t.get("stack", "") else 0.0
                relevance   = text_sim + type_bonus + stack_bonus

                if relevance > 0.2:
                    candidates.append({**t, "_relevance": round(relevance, 3)})
            except Exception:
                continue

    candidates.sort(key=lambda x: (-x["_relevance"], -x.get("quality_score", 0)))
    return candidates[:limit]

def format_for_context(trajectories: list[dict]) -> str:
    """
    Format retrieved trajectories as in-context examples for injection
    into /plan or /brainstorm prompts.
    """
    if not trajectories:
        return ""
    lines = ["\n## Experience: Similar Tasks Completed Before\n"]
    lines.append("_Inject these as context — they represent what worked in practice._\n")
    for i, t in enumerate(trajectories, 1):
        lines.append(f"### Example {i}: {t['task_description'][:80]}")
        lines.append(f"**Stack:** {t.get('stack', 'unknown')} | "
                     f"**Verdict:** {t.get('ship_verdict', '?')} | "
                     f"**Relevance:** {t.get('_relevance', 0):.0%}\n")
        if t.get("session_summary"):
            lines.append(f"**What was built:** {t['session_summary'][:200]}\n")
        if t.get("key_decisions"):
            lines.append("**Key decisions made:**")
            for d in t["key_decisions"][:4]:
                lines.append(f"- {d}")
            lines.append("")
        if t.get("what_worked"):
            lines.append(f"**What worked:** {t['what_worked'][:150]}\n")
        if t.get("what_to_avoid"):
            lines.append(f"**Avoid:** {t['what_to_avoid'][:150]}\n")
    return "\n".join(lines)

def list_trajectories(limit: int = 20):
    ensure_dirs()
    all_t = []
    for f in STORE.glob("*.json"):
        try:
            t = json.loads(f.read_text())
            all_t.append(t)
        except Exception:
            continue
    all_t.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    print(f"\n{BOLD}{CYAN}━━━ TRAJECTORIES ({len(all_t)} stored) ━━━━━━━━━━━━━━━━━━━━━{RESET}")
    for t in all_t[:limit]:
        verdict_color = GREEN if t.get("ship_verdict") == "SHIP" else YELLOW
        ts = t.get("timestamp", "")[:10]
        print(f"  {DIM}{ts}{RESET}  "
              f"{verdict_color}{t.get('ship_verdict','?'):5}{RESET}  "
              f"q={t.get('quality_score',0):.2f}  "
              f"{t.get('task_description','')[:55]}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

def show_stats():
    ensure_dirs()
    all_t = list(STORE.glob("*.json"))
    global_t = list(GLOBAL.glob("*.json")) if GLOBAL.exists() else []
    shipped = 0
    total_q = 0.0
    for f in all_t:
        try:
            t = json.loads(f.read_text())
            if t.get("ship_verdict") == "SHIP": shipped += 1
            total_q += t.get("quality_score", 0)
        except: pass
    avg_q = total_q / len(all_t) if all_t else 0
    print(f"\n{BOLD}{CYAN}━━━ TRAJECTORY STATS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Project trajectories: {GREEN}{len(all_t)}{RESET}")
    print(f"  Global trajectories:  {GREEN}{len(global_t)}{RESET}")
    print(f"  SHIP verdict rate:    {GREEN}{shipped}/{len(all_t)}{RESET}")
    print(f"  Avg quality score:    {GREEN}{avg_q:.2f}{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

def main():
    args = sys.argv[1:]
    if not args:
        show_stats()
        return
    cmd = args[0]
    if cmd == "store":
        if len(args) < 2:
            print("Usage: trajectory_store.py store <json_file>")
            sys.exit(1)
        data = json.loads(Path(args[1]).read_text())
        store_trajectory(data)
    elif cmd == "query":
        query = args[1] if len(args) > 1 else ""
        stack = args[2] if len(args) > 2 else ""
        results = query_trajectories(query, stack=stack)
        if results:
            print(format_for_context(results))
        else:
            print(f"{DIM}No relevant trajectories found.{RESET}")
    elif cmd == "list":
        list_trajectories()
    elif cmd == "stats":
        show_stats()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
