from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Token Intelligence
========================
Proactive token analysis BEFORE each command runs.
Shows exactly where tokens are going, flags waste, suggests optimizations.

This is the "loophole finder" — it audits context before spending it.

Usage:
  python3 .claude/intelligence/token_intelligence.py report [command]
  python3 .claude/intelligence/token_intelligence.py audit
  python3 .claude/intelligence/token_intelligence.py pre-flight [command] [query]
"""
import json, sys, os, re
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Smart router integration
try:
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from smart_router import classify_task, get_tier_context_budget, print_routing_report
    SMART_ROUTING = True
except ImportError:
    SMART_ROUTING = False

ROOT     = Path.cwd()
APEX_DIR = ROOT / ".claude"

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"

# Claude Sonnet 4.6 pricing (per 1K tokens)
INPUT_PRICE  = 0.003
OUTPUT_PRICE = 0.015

# Realistic token sizes for each context component
CONTEXT_SIZES = {
    "claude_system_prompt":  3000,  # Claude Code's own system prompt (~50 instructions)
    "claude_md":             None,  # measured from actual file
    "stack_profile":          80,
    "brain_context":         None,  # measured from brain
    "trajectory_context":    400,   # typical 2-3 trajectories
    "taste_context":         150,   # preference profile excerpt
    "command_skill":        2000,   # the command body when invoked
    "reference_doc":        1800,   # typical reference doc
    "user_query":            None,  # measured from actual query
}

# Which components each command loads
COMMAND_CONTEXT_MAP = {
    "setup":      ["claude_md", "stack_profile"],
    "init":       ["claude_md", "stack_profile", "brain_context"],
    "status":     ["claude_md", "stack_profile", "brain_context"],
    "ask":        ["claude_md", "stack_profile", "brain_context"],
    "brainstorm": ["claude_md", "stack_profile", "brain_context", "trajectory_context", "taste_context"],
    "plan":       ["claude_md", "stack_profile", "brain_context", "trajectory_context", "taste_context"],
    "execute":    ["claude_md", "stack_profile", "brain_context"],
    "design":     ["claude_md", "stack_profile", "brain_context", "taste_context", "reference_doc"],
    "review":     ["claude_md", "stack_profile", "brain_context", "reference_doc"],
    "ship":       ["claude_md", "stack_profile", "brain_context"],
    "debug":      ["claude_md", "stack_profile", "brain_context"],
    "test":       ["claude_md", "stack_profile", "reference_doc"],
    "refactor":   ["claude_md", "stack_profile", "brain_context"],
    "optimize":   ["claude_md", "stack_profile", "brain_context"],
    "spawn":      ["claude_md", "stack_profile", "brain_context"],
    "docs":       ["claude_md", "stack_profile"],
    "compact":    ["claude_md"],
    "benchmark":  ["claude_md", "stack_profile"],
    "rollback":       ["claude_md", "stack_profile"],
    "handoff":        ["claude_md", "brain_context"],
    "optimize-context": ["claude_md", "stack_profile", "brain_context"],
}


def _measure_claude_md() -> int:
    f = ROOT / "CLAUDE.md"
    return len(f.read_text(errors="ignore")) // 4 if f.exists() else 679


def _measure_brain() -> int:
    brain_file = APEX_DIR / "brain" / "facts.jsonl"
    if not brain_file.exists():
        return 0
    facts = []
    for line in brain_file.read_text(errors="ignore").splitlines():
        line = line.strip()
        if line:
            try:
                f = json.loads(line)
                if not f.get("invalidated_at"):
                    facts.append(f)
            except Exception:
                continue
    # Simulate formatted output
    formatted = "\n".join(f"- {f.get('content','')}" for f in facts[:15])
    return len(formatted) // 4


def _load_session_stats() -> dict:
    log = APEX_DIR / "cache" / "token_log.json"
    if not log.exists():
        return {}
    try:
        entries = json.loads(log.read_text())
        today = datetime.now(timezone.utc).date()
        today_entries = [
            e for e in entries
            if datetime.fromisoformat(e["timestamp"]).date() == today
        ]
        week_entries = [
            e for e in entries
            if (datetime.now(timezone.utc) -
                datetime.fromisoformat(e["timestamp"])).days < 7
        ]
        return {
            "today_cost":   sum(e.get("cost_usd", 0) for e in today_entries),
            "today_tokens": sum(e.get("total_tokens", 0) for e in today_entries),
            "today_calls":  len(today_entries),
            "week_cost":    sum(e.get("cost_usd", 0) for e in week_entries),
            "week_calls":   len(week_entries),
            "total_saved":  sum(e.get("savings_usd", 0) for e in entries),
        }
    except Exception:
        return {}


def get_command_token_budget(command: str, query: str = "") -> dict:
    """
    Calculate the REAL token budget for a command before it runs.
    Returns breakdown, total, cost estimate, and any waste flags.
    """
    components = COMMAND_CONTEXT_MAP.get(command, ["claude_md", "stack_profile"])

    sizes = {
        "claude_system_prompt": CONTEXT_SIZES["claude_system_prompt"],
        "claude_md":             _measure_claude_md(),
        "stack_profile":         CONTEXT_SIZES["stack_profile"],
        "brain_context":         _measure_brain(),
        "trajectory_context":    CONTEXT_SIZES["trajectory_context"],
        "taste_context":         CONTEXT_SIZES["taste_context"],
        "command_skill":         CONTEXT_SIZES["command_skill"],
        "reference_doc":         CONTEXT_SIZES["reference_doc"],
        "user_query":            len(query) // 4 if query else 50,
    }

    breakdown = {}
    total = sizes["claude_system_prompt"]  # always present
    breakdown["Claude Code system"] = sizes["claude_system_prompt"]

    for comp in components:
        size = sizes.get(comp, 0)
        if size and size > 0:
            breakdown[comp.replace("_", " ").title()] = size
            total += size

    breakdown["Command skill body"] = sizes["command_skill"]
    total += sizes["command_skill"]

    if query:
        breakdown["Your query"] = sizes["user_query"]
        total += sizes["user_query"]

    # Typical output
    output_tokens = 800

    # Waste flags
    flags = []
    claude_md_size = sizes["claude_md"]
    if claude_md_size > 700:
        flags.append(f"CLAUDE.md is {claude_md_size} tokens — target ≤50 lines (~600 tokens)")
    if sizes["brain_context"] > 500:
        flags.append(f"Brain context {sizes['brain_context']} tokens — consider topic-filtered reads")

    return {
        "command":          command,
        "breakdown":        breakdown,
        "input_tokens":     total,
        "output_tokens":    output_tokens,
        "total_tokens":     total + output_tokens,
        "input_cost":       total / 1000 * INPUT_PRICE,
        "output_cost":      output_tokens / 1000 * OUTPUT_PRICE,
        "total_cost":       total / 1000 * INPUT_PRICE + output_tokens / 1000 * OUTPUT_PRICE,
        "waste_flags":      flags,
    }


def print_pre_flight(command: str, query: str = ""):
    """Print a token budget report before running a command."""
    budget = get_command_token_budget(command, query)
    stats  = _load_session_stats()

    print(f"\n{BOLD}{CYAN}━━━ APEX Token Intelligence: /{command} ━━━━━━━━━━━━━━━━{RESET}")

    # Context breakdown
    print(f"\n  {BOLD}Context breakdown:{RESET}")
    for name, tokens in budget["breakdown"].items():
        bar_len = min(30, tokens // 100)
        bar = "█" * bar_len
        pct = tokens / budget["input_tokens"] * 100
        color = RED if pct > 40 else (YELLOW if pct > 20 else DIM)
        print(f"  {color}{name:<28}{RESET} {tokens:>5} tokens ({pct:.0f}%) {DIM}{bar}{RESET}")

    print(f"\n  {BOLD}Budget:{RESET}")
    print(f"    Input:   {budget['input_tokens']:,} tokens  (${budget['input_cost']:.5f})")
    print(f"    Output:  ~{budget['output_tokens']:,} tokens (${budget['output_cost']:.5f})")
    print(f"    {BOLD}Total:   ~{budget['total_tokens']:,} tokens  (${budget['total_cost']:.4f}){RESET}")

    # Session context
    if stats:
        today = stats.get("today_cost", 0)
        calls = stats.get("today_calls", 0)
        saved = stats.get("total_saved", 0)
        budget_cfg = APEX_DIR / "config" / "cache-config.json"
        limit = 5.0
        if budget_cfg.exists():
            try:
                cfg = json.loads(budget_cfg.read_text())
                limit = cfg.get("session_budget", {}).get("hard_halt_usd", 5.0)
            except Exception:
                pass

        color = GREEN if today < limit * 0.4 else (YELLOW if today < limit * 0.8 else RED)
        print(f"\n  {BOLD}Session:{RESET}")
        print(f"    Today:   {color}${today:.4f}{RESET} / ${limit:.2f} limit  ({calls} commands)")
        print(f"    Saved:   {GREEN}${saved:.4f}{RESET} total (cache + optimization)")

    # Waste flags
    if budget["waste_flags"]:
        print(f"\n  {YELLOW}⚠ Optimization opportunities:{RESET}")
        for flag in budget["waste_flags"]:
            print(f"    {DIM}• {flag}{RESET}")
        print(f"    {DIM}Run: python3 .claude/intelligence/claude_md_optimizer.py --audit{RESET}")

    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def print_session_audit():
    """Full session token audit."""
    stats = _load_session_stats()
    log = APEX_DIR / "cache" / "token_log.json"

    print(f"\n{BOLD}{CYAN}━━━ APEX Full Token Audit ━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    if not log.exists():
        print(f"  {DIM}No session data yet. Run some commands first.{RESET}")
    else:
        try:
            entries = json.loads(log.read_text())
            # By command
            by_cmd = {}
            for e in entries:
                cmd = e.get("command", "unknown")
                by_cmd.setdefault(cmd, []).append(e)

            print(f"\n  {BOLD}By command (all time):{RESET}")
            for cmd, cmds in sorted(by_cmd.items(), key=lambda x: -sum(e.get("total_tokens",0) for e in x[1])):
                total_t = sum(e.get("total_tokens", 0) for e in cmds)
                total_c = sum(e.get("cost_usd", 0) for e in cmds)
                cache_hits = sum(1 for e in cmds if e.get("cached"))
                print(f"    /{cmd:<14} {len(cmds):>3}× | {total_t:>8,} tokens | ${total_c:.4f} | {cache_hits} cache hits")

            if stats:
                print(f"\n  {BOLD}Summary:{RESET}")
                print(f"    Today:    ${stats['today_cost']:.4f} ({stats['today_tokens']:,} tokens, {stats['today_calls']} calls)")
                print(f"    This week: ${stats['week_cost']:.4f} ({stats['week_calls']} calls)")
                print(f"    All-time saved: {GREEN}${stats['total_saved']:.4f}{RESET}")
        except Exception as e:
            print(f"  {RED}Could not parse log: {e}{RESET}")

    # CLAUDE.md health
    claude_tokens = _measure_claude_md()
    brain_tokens  = _measure_brain()
    color = GREEN if claude_tokens <= 600 else (YELLOW if claude_tokens <= 900 else RED)
    print(f"\n  {BOLD}Context health:{RESET}")
    print(f"    CLAUDE.md:       {color}{claude_tokens} tokens{RESET} (target ≤600)")
    print(f"    Brain context:   {brain_tokens} tokens (15-25 facts ideal)")

    # Skills check
    skills_dir = APEX_DIR / "skills"
    skill_count = len(list(skills_dir.glob("*/SKILL.md"))) if skills_dir.exists() else 0
    cmd_count   = len(list((APEX_DIR/"commands").glob("*.md"))) if (APEX_DIR/"commands").exists() else 0
    skill_color = GREEN if skill_count >= cmd_count else YELLOW
    print(f"    Skills:          {skill_color}{skill_count}/{cmd_count} lazy-loaded{RESET}")

    # Hooks check
    hooks_dir  = APEX_DIR / "hooks"
    hook_count = len(list(hooks_dir.glob("*.sh"))) if hooks_dir.exists() else 0
    hook_color = GREEN if hook_count >= 4 else YELLOW
    print(f"    Hooks:           {hook_color}{hook_count} active{RESET} (4 minimum)")

    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")



def check_budget_before_command(command: str, query: str = "") -> dict:
    """
    Hard budget check BEFORE running any command.
    Returns: {"allowed": bool, "reason": str, "cost_estimate": float}
    
    This is the token gatekeeper — called by UserPromptSubmit hook.
    If the session is near budget, it blocks BEFORE spending a single token.
    """
    stats  = _load_session_stats()
    budget_cfg = APEX_DIR / "config" / "cache-config.json"
    
    soft_warn  = 3.0   # warn at $3
    hard_halt  = 5.0   # block at $5
    
    if budget_cfg.exists():
        try:
            cfg = json.loads(budget_cfg.read_text())
            sb  = cfg.get("session_budget", {})
            soft_warn = sb.get("soft_warn_usd", 3.0)
            hard_halt = sb.get("hard_halt_usd", 5.0)
        except Exception:
            pass
    
    today_cost = stats.get("today_cost", 0.0)
    
    # Estimate cost of this command using smart router
    if SMART_ROUTING:
        tier   = classify_task(command, query)
        budget = get_tier_context_budget(tier)
        estimate = budget["total_overhead"] / 1000 * INPUT_PRICE + OUTPUT_PRICE * 0.8
    else:
        budget   = get_command_token_budget(command, query)
        estimate = budget["total_cost"]
    
    projected = today_cost + estimate
    
    if projected >= hard_halt:
        return {
            "allowed":      False,
            "reason":       f"Hard limit: today ${today_cost:.3f} + this ~${estimate:.3f} = ${projected:.3f} >= ${hard_halt:.2f}",
            "cost_estimate": estimate,
            "today_cost":   today_cost,
        }
    elif projected >= soft_warn:
        return {
            "allowed":      True,
            "warn":         True,
            "reason":       f"Approaching limit: today ${today_cost:.3f} + this ~${estimate:.3f} = ${projected:.3f}",
            "cost_estimate": estimate,
            "today_cost":   today_cost,
        }
    
    return {"allowed": True, "cost_estimate": estimate, "today_cost": today_cost}


def print_smart_preflight(command: str, query: str = ""):
    """
    Smart pre-flight: shows routing tier + token budget.
    This replaces the old print_pre_flight for all simple commands.
    """
    if SMART_ROUTING:
        from smart_router import classify_task, get_tier_context_budget, TIERS
        tier   = classify_task(command, query)
        budget = get_tier_context_budget(tier)
        total  = budget["total_overhead"]
        saved  = budget.get("savings_vs_full", 0)
        
        c = tier.color
        
        print(f"\n{BOLD}{CYAN}━━━ APEX Token Pre-flight: /{command} ━━━━━━━━━━━━━━{RESET}")
        print(f"  {c}{BOLD}Tier: {tier.name}{RESET}  (~{total:,} tokens)")
        if saved > 0:
            print(f"  {GREEN}Savings vs FULL: ~{saved:,} tokens saved{RESET}")
        
        # Budget check
        check = check_budget_before_command(command, query)
        stats = _load_session_stats()
        today = stats.get("today_cost", 0)
        
        budget_cfg = APEX_DIR / "config" / "cache-config.json"
        limit = 5.0
        if budget_cfg.exists():
            try:
                cfg = json.loads(budget_cfg.read_text())
                limit = cfg.get("session_budget", {}).get("hard_halt_usd", 5.0)
            except Exception:
                pass
        
        color = GREEN if today < limit * 0.4 else (YELLOW if today < limit * 0.8 else RED)
        print(f"  Budget: {color}${today:.4f}{RESET} / ${limit:.2f}  |  This command: ~${check['cost_estimate']:.4f}")
        
        if not check.get("allowed", True):
            print(f"\n  {RED}{BOLD}⛔ BLOCKED: {check['reason']}{RESET}")
            print(f"  {DIM}Adjust budget in .claude/config/cache-config.json{RESET}")
        elif check.get("warn"):
            print(f"  {YELLOW}⚠ {check['reason']}{RESET}")
        
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
    else:
        print_pre_flight(command, query)

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "audit"

    if cmd == "pre-flight":
        command = args[1] if len(args) > 1 else "plan"
        query   = args[2] if len(args) > 2 else ""
        print_pre_flight(command, query)
    elif cmd == "report":
        command = args[1] if len(args) > 1 else "plan"
        budget  = get_command_token_budget(command)
        print(json.dumps(budget, indent=2))
    elif cmd == "audit":
        print_session_audit()
    else:
        print(f"Usage: token_intelligence.py [audit | pre-flight <command> [query] | report <command>]")


if __name__ == "__main__":
    main()
