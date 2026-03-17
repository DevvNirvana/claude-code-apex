#!/usr/bin/env python3
"""
Token Tracker — Tracks token usage across sessions and reports savings.
Runs as a session companion to show real-time cost intelligence.

Usage:
  python3 .claude/intelligence/token_tracker.py log <command> <input_tokens> <output_tokens>
  python3 .claude/intelligence/token_tracker.py report
  python3 .claude/intelligence/token_tracker.py report --today
  python3 .claude/intelligence/token_tracker.py reset
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict

ROOT        = Path.cwd()
LOG_FILE    = ROOT / ".claude" / "cache" / "token_log.json"
STATS_FILE  = ROOT / ".claude" / "cache" / "token_stats.json"
CONFIG_FILE = ROOT / ".claude" / "config" / "cache-config.json"

def _load_budget() -> dict:
    """Load session budget from cache-config.json."""
    try:
        cfg = json.loads(CONFIG_FILE.read_text())
        b   = cfg.get("session_budget", {})
        return {
            "soft_usd":    float(b.get("soft_warn_usd",    2.00)),
            "hard_usd":    float(b.get("hard_halt_usd",    5.00)),
            "soft_tokens": int(b.get("soft_warn_tokens", 100_000)),
            "hard_tokens": int(b.get("hard_halt_tokens", 250_000)),
        }
    except Exception:
        return {"soft_usd": 2.00, "hard_usd": 5.00,
                "soft_tokens": 100_000, "hard_tokens": 250_000}

def check_budget() -> dict:
    """Return ok/warn/halt for today's session spend."""
    log   = load_log()
    today = datetime.now(timezone.utc).date()
    tlog  = [e for e in log
             if datetime.fromisoformat(e["timestamp"]).date() == today]
    cost   = sum(e.get("cost_usd",     0) for e in tlog)
    tokens = sum(e.get("total_tokens", 0) for e in tlog)
    budget = _load_budget()
    if cost >= budget["hard_usd"] or tokens >= budget["hard_tokens"]:
        status = "halt"
    elif cost >= budget["soft_usd"] or tokens >= budget["soft_tokens"]:
        status = "warn"
    else:
        status = "ok"
    return {"status": status, "session_cost": cost,
            "session_tokens": tokens, "budget": budget}

CYAN   = "\033[0;36m"
GREEN  = "\033[0;32m"
YELLOW = "\033[1;33m"
RED    = "\033[0;31m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# Pricing per 1K tokens (as of 2025, blended estimates)
PRICING = {
    "claude-opus":    {"input": 0.015,  "output": 0.075},
    "claude-sonnet":  {"input": 0.003,  "output": 0.015},
    "claude-haiku":   {"input": 0.00025,"output": 0.00125},
    "gemini-pro":     {"input": 0.00125,"output": 0.005},
    "gemini-flash":   {"input": 0.000075,"output": 0.0003},
    "default":        {"input": 0.003,  "output": 0.015},
}

# Time saved heuristics (minutes per cached / optimized command)
# Based on: avg Claude streaming time + human reading time per command type
TIME_SAVED_MINUTES = {
    "plan":     5,    # planning session: 5 min saved on cache hit
    "design":   8,    # design gen is long: 8 min
    "review":   4,    # review output: 4 min
    "refactor": 6,    # refactor analysis: 6 min
    "docs":     5,    # doc generation: 5 min
    "test":     4,    # test generation: 4 min
    "debug":    3,    # debug analysis: 3 min
    "optimize": 4,    # optimization scan: 4 min
    "ship":     3,    # preflight check: 3 min
    "compact":  2,    # compact: 2 min
    "default":  4,    # unknown command: 4 min
}

# Baseline: what a naive (no optimization) session uses
BASELINE_TOKENS = {
    "plan":     {"input": 2800, "output": 1200},
    "review":   {"input": 3200, "output": 1400},
    "design":   {"input": 3500, "output": 2200},
    "ship":     {"input": 4000, "output": 1800},
    "spawn":    {"input": 2200, "output": 600},
    "debug":    {"input": 2400, "output": 1000},
    "optimize": {"input": 2600, "output": 1200},
    "test":     {"input": 2800, "output": 1800},
    "docs":     {"input": 2000, "output": 1000},
    "refactor": {"input": 3200, "output": 2000},
    "default":  {"input": 2500, "output": 1200},
}

def ensure_files():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.write_text(json.dumps([], indent=2))
    if not STATS_FILE.exists():
        STATS_FILE.write_text(json.dumps({
            "total_sessions": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "baseline_cost_usd": 0.0,
            "commands": {}
        }, indent=2))

def load_log() -> list:
    ensure_files()
    try:
        return json.loads(LOG_FILE.read_text())
    except Exception:
        return []

def atomic_write_json(path: Path, data) -> None:
    """Write JSON atomically — Windows-safe.
    Uses os.replace() which handles existing-target on Windows correctly.
    """
    import os, tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(data, indent=2))
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

def save_log(log: list):
    atomic_write_json(LOG_FILE, log)

def load_stats() -> dict:
    ensure_files()
    try:
        return json.loads(STATS_FILE.read_text())
    except Exception:
        return {}

def save_stats(stats: dict):
    atomic_write_json(STATS_FILE, stats)

def calc_cost(model: str, input_tok: int, output_tok: int) -> float:
    pricing = PRICING.get(model, PRICING["default"])
    return (input_tok / 1000 * pricing["input"]) + (output_tok / 1000 * pricing["output"])

def log_usage(command: str, input_tokens: int, output_tokens: int,
              model: str = "claude-sonnet", cached: bool = False) -> dict:
    """Log command usage. Enforces session budget."""
    import os
    bs = check_budget()
    if bs["status"] == "halt":
        b = bs["budget"]
        print(f"\n{RED}\u26d4 SESSION BUDGET HALTED{RESET}")
        print(f"  Today: ${bs['session_cost']:.4f} >= hard limit ${b['hard_usd']:.2f}")
        print(f"  Set APEX_OVERRIDE_BUDGET=1 to force-continue.")
        if not os.environ.get("APEX_OVERRIDE_BUDGET"):
            return {"halted": True, "reason": "budget_exceeded", **bs}
    elif bs["status"] == "warn":
        b = bs["budget"]
        print(f"\n{YELLOW}\u26a0 Budget: ${bs['session_cost']:.4f} of ${b['hard_usd']:.2f} today{RESET}")
    log = load_log()
    stats = load_stats()
    
    cost = calc_cost(model, input_tokens, output_tokens)
    
    # Baseline cost (what it would cost without optimization)
    baseline = BASELINE_TOKENS.get(command, BASELINE_TOKENS["default"])
    baseline_cost = calc_cost(model, baseline["input"], baseline["output"])
    
    # Time saved: on cache hit = full command time; otherwise = optimization delta
    time_per_cmd = TIME_SAVED_MINUTES.get(command, TIME_SAVED_MINUTES["default"])
    time_saved = time_per_cmd if cached else round(time_per_cmd * (1 - (input_tokens + output_tokens) / max(baseline["input"] + baseline["output"], 1)) * 0.6, 1)
    time_saved = max(0, time_saved)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "command": command,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": round(cost, 6),
        "baseline_cost_usd": round(baseline_cost, 6),
        "savings_usd": round(baseline_cost - cost, 6),
        "time_saved_minutes": round(time_saved, 1),
        "cached": cached
    }
    log.append(entry)
    save_log(log)
    
    # Update stats
    stats["total_sessions"] = stats.get("total_sessions", 0) + 1
    stats["total_input_tokens"] = stats.get("total_input_tokens", 0) + input_tokens
    stats["total_output_tokens"] = stats.get("total_output_tokens", 0) + output_tokens
    stats["total_cost_usd"] = round(stats.get("total_cost_usd", 0) + cost, 6)
    stats["baseline_cost_usd"] = round(stats.get("baseline_cost_usd", 0) + baseline_cost, 6)
    stats["total_time_saved_minutes"] = round(stats.get("total_time_saved_minutes", 0) + time_saved, 1)
    
    cmd_stats = stats.get("commands", {})
    if command not in cmd_stats:
        cmd_stats[command] = {"calls": 0, "input": 0, "output": 0, "cost": 0.0}
    cmd_stats[command]["calls"] += 1
    cmd_stats[command]["input"] += input_tokens
    cmd_stats[command]["output"] += output_tokens
    cmd_stats[command]["cost"] = round(cmd_stats[command]["cost"] + cost, 6)
    stats["commands"] = cmd_stats
    save_stats(stats)
    
    return entry

def show_report(today_only: bool = False):
    log = load_log()
    stats = load_stats()
    
    if today_only:
        today = datetime.now(timezone.utc).date()
        log = [e for e in log if datetime.fromisoformat(e["timestamp"]).date() == today]
    
    if not log:
        print(f"{DIM}No usage logged yet.{RESET}")
        return
    
    total_input  = sum(e["input_tokens"] for e in log)
    total_output = sum(e["output_tokens"] for e in log)
    total_cost   = sum(e["cost_usd"] for e in log)
    baseline     = sum(e["baseline_cost_usd"] for e in log)
    savings      = baseline - total_cost
    savings_pct  = (savings / baseline * 100) if baseline > 0 else 0
    
    period = "Today" if today_only else "All Time"
    
    print(f"\n{BOLD}{CYAN}━━━ TOKEN INTELLIGENCE REPORT ({period}) ━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Total calls:       {len(log)}")
    print(f"  Input tokens:      {total_input:,}")
    print(f"  Output tokens:     {total_output:,}")
    total_time_saved = sum(e.get("time_saved_minutes", 0) for e in log)
    total_time_hrs = total_time_saved / 60

    print(f"  Total tokens:      {total_input + total_output:,}")
    print(f"  Actual cost:       {YELLOW}${total_cost:.4f}{RESET}")
    print(f"  Baseline cost:     {DIM}${baseline:.4f} (without optimization){RESET}")
    print(f"  {GREEN}Saved:             ${savings:.4f} ({savings_pct:.0f}% reduction){RESET}")
    if total_time_saved > 0:
        time_display = f"{total_time_hrs:.1f} hours" if total_time_hrs >= 1 else f"{total_time_saved:.0f} minutes"
        print(f"  {GREEN}Time saved:        ~{time_display}{RESET}")
    
    # Per-command breakdown
    print(f"\n  {BOLD}Command Breakdown:{RESET}")
    cmd_groups = defaultdict(list)
    for entry in log:
        cmd_groups[entry["command"]].append(entry)
    
    for cmd, entries in sorted(cmd_groups.items(), key=lambda x: -len(x[1])):
        calls = len(entries)
        cost  = sum(e["cost_usd"] for e in entries)
        tokens = sum(e["total_tokens"] for e in entries)
        print(f"    /{cmd:<12} {calls:>3}x  {tokens:>7,} tokens  ${cost:.4f}")
    
    # Cache hits
    cached = [e for e in log if e.get("cached")]
    if cached:
        cache_savings = sum(e["baseline_cost_usd"] for e in cached)
        print(f"\n  {GREEN}Cache hits: {len(cached)} calls (saved ~${cache_savings:.4f}){RESET}")
    
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

def reset_log():
    atomic_write_json(LOG_FILE, [])
    atomic_write_json(STATS_FILE, {
        "total_sessions": 0, "total_input_tokens": 0, "total_output_tokens": 0,
        "total_cost_usd": 0.0, "baseline_cost_usd": 0.0, "commands": {}
    })
    print(f"{GREEN}✓ Token log reset{RESET}")

def main():
    args = sys.argv[1:]
    if not args:
        show_report()
        return
    
    cmd = args[0]
    
    if cmd == "log":
        if len(args) < 4:
            print("Usage: token_tracker.py log <command> <input_tokens> <output_tokens> [model] [--cached]")
            sys.exit(1)
        command = args[1]
        input_t = int(args[2])
        output_t = int(args[3])
        model   = args[4] if len(args) > 4 and not args[4].startswith("--") else "claude-sonnet"
        cached  = "--cached" in args
        entry = log_usage(command, input_t, output_t, model, cached)
        print(json.dumps(entry, indent=2))
    
    elif cmd == "report":
        today_only = "--today" in args
        show_report(today_only)
    
    elif cmd == "reset":
        reset_log()
    
    elif cmd == "budget":
        s = check_budget()
        b = s["budget"]
        c = GREEN if s["status"] == "ok" else (YELLOW if s["status"] == "warn" else RED)
        print(f"\n{BOLD}{CYAN}\u2501\u2501\u2501 SESSION BUDGET \u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501{RESET}")
        print(f"  Status:       {c}{s['status'].upper()}{RESET}")
        print(f"  Today cost:   ${s['session_cost']:.4f} / hard ${b['hard_usd']:.2f}")
        print(f"  Today tokens: {s['session_tokens']:,} / {b['hard_tokens']:,}")
        print(f"  Warn at:      ${b['soft_usd']:.2f} / {b['soft_tokens']:,} tokens")
        print(f"{CYAN}\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501{RESET}\n")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
