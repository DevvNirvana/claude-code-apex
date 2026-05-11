from __future__ import annotations
#!/usr/bin/env python3
"""
APEX CLAUDE.md Optimizer
========================
Trims CLAUDE.md based on ETH Zurich research findings.

Key findings implemented here:
1. Architecture/folder trees are pure noise — agents discover structure themselves
2. Rules enforced by hooks are redundant in CLAUDE.md — remove them to save tokens
3. Generic advice ("write clean code") wastes instruction budget — prune it
4. Target: 40-60 lines. Sweet spot confirmed by Boris Cherny (Claude Code creator),
   HumanLayer production analysis, and ETH Zurich paper recommendations.

Usage:
  python3 .claude/intelligence/claude_md_optimizer.py --audit   # show analysis
  python3 .claude/intelligence/claude_md_optimizer.py --optimize # apply recommendations
"""
import re, sys, os, tempfile
from pathlib import Path

ROOT     = Path.cwd()
CLAUDE   = ROOT / "CLAUDE.md"
HOOKS    = ROOT / ".claude" / "hooks" / "session-start.sh"

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"

# Patterns that waste instruction budget (generic, non-specific)
GENERIC_PATTERNS = [
    r"write clean code",
    r"follow best practices",
    r"be a senior engineer",
    r"think step by step",
    r"ensure code quality",
    r"write readable code",
    r"maintain code quality",
]

# Sections where directory trees live — remove them
ARCH_TREE_PATTERN = re.compile(
    r"```[^\n]*\n"           # opening fence (with optional language)
    r"(?:[^\n]*\n)?"         # optional root dir line (e.g. "src/")
    r"(?:[├└│─\s]+\S+[^\n]*\n){2,}"  # 2+ tree lines with box-drawing chars
    r"```",
    re.MULTILINE
)

def load_hooks_enforced_rules() -> list[str]:
    """Read session-start.sh to know which rules are already hook-enforced."""
    if not HOOKS.exists():
        return []
    content = HOOKS.read_text(errors="ignore")
    rules = []
    for line in content.splitlines():
        if line.startswith("echo '  - "):
            rule = line[10:].rstrip("'").strip()
            if rule:
                rules.append(rule.lower()[:60])
    return rules


def audit_claude_md() -> dict:
    if not CLAUDE.exists():
        return {"exists": False}

    content = CLAUDE.read_text(errors="ignore")
    lines = content.splitlines()
    line_count = len(lines)

    # Check for arch tree
    has_arch_tree = bool(ARCH_TREE_PATTERN.search(content))
    arch_tree_lines = 0
    if has_arch_tree:
        arch_tree_lines = sum(1 for l in lines
                              if re.match(r"^\s*[├└│─\s]+\S", l))

    # Check for generic patterns
    generic_found = []
    for pat in GENERIC_PATTERNS:
        if re.search(pat, content, re.IGNORECASE):
            generic_found.append(pat)

    # Check hooks overlap
    hooks_rules = load_hooks_enforced_rules()
    overlapping_rules = []
    for rule in hooks_rules:
        for line in lines:
            if rule in line.lower():
                overlapping_rules.append(line.strip()[:80])
                break

    # Token estimate
    token_estimate = len(content) // 4
    annual_cost = (token_estimate / 1000) * 0.003 * 20 * 5 * 52  # 20 cmds/day, 5 days, 52 weeks

    return {
        "exists":            True,
        "line_count":        line_count,
        "token_estimate":    token_estimate,
        "arch_tree_present": has_arch_tree,
        "arch_tree_lines":   arch_tree_lines,
        "generic_found":     generic_found,
        "hook_overlaps":     overlapping_rules,
        "target_lines":      50,
        "can_save_lines":    arch_tree_lines + len(generic_found) * 2 + len(overlapping_rules),
        "annual_cost_usd":   annual_cost,
    }


def print_audit(audit: dict):
    if not audit.get("exists"):
        print(f"{YELLOW}No CLAUDE.md found. Run /setup to generate one.{RESET}")
        return

    lc = audit["line_count"]
    target = audit["target_lines"]
    color = GREEN if lc <= target else (YELLOW if lc <= 80 else RED)

    print(f"\n{BOLD}{CYAN}━━━ CLAUDE.md Optimizer Audit ━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Current lines:    {color}{lc}{RESET} (target: ≤{target})")
    print(f"  Token estimate:   ~{audit['token_estimate']} tokens per session load")
    print(f"  Annual cost est:  ~${audit['annual_cost_usd']:.2f} (20 commands/day)")

    if audit["arch_tree_present"]:
        print(f"\n  {RED}✗ Architecture folder tree found ({audit['arch_tree_lines']} lines){RESET}")
        print(f"    {DIM}ETH Zurich: agents discover structure themselves.")
        print(f"    This adds cost without improving outcomes. Remove it.{RESET}")

    if audit["generic_found"]:
        print(f"\n  {YELLOW}⚠ Generic advice found ({len(audit['generic_found'])} patterns):{RESET}")
        for p in audit["generic_found"]:
            print(f"    {DIM}'{p}' — wastes instruction budget{RESET}")

    if audit["hook_overlaps"]:
        print(f"\n  {YELLOW}⚠ Hook-redundant rules found ({len(audit['hook_overlaps'])}):{RESET}")
        for r in audit["hook_overlaps"][:4]:
            print(f"    {DIM}{r[:70]}{RESET}")
        print(f"    {DIM}These are enforced by hooks — remove from CLAUDE.md to save tokens{RESET}")

    saveable = audit["can_save_lines"]
    if saveable > 0:
        print(f"\n  {GREEN}Potential savings: ~{saveable} lines ({saveable * 5} tokens/session){RESET}")
        print(f"  Run: python3 .claude/intelligence/claude_md_optimizer.py --optimize")
    else:
        print(f"\n  {GREEN}✓ CLAUDE.md looks well-optimized{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def optimize_claude_md():
    """Remove noise sections, print a before/after report."""
    if not CLAUDE.exists():
        print(f"{RED}No CLAUDE.md found.{RESET}")
        return

    original = CLAUDE.read_text(errors="ignore")
    content  = original

    # 1. Remove architecture folder trees (confirmed useless by ETH Zurich)
    content = ARCH_TREE_PATTERN.sub("```\n# (folder structure auto-discovered by Claude)\n```", content)

    # 2. Strip generic lines
    new_lines = []
    for line in content.splitlines():
        skip = False
        for pat in GENERIC_PATTERNS:
            if re.search(pat, line, re.IGNORECASE):
                skip = True
                break
        if not skip:
            new_lines.append(line)
    content = "\n".join(new_lines)

    # 3. Remove redundant blank lines (3+ consecutive → 1)
    content = re.sub(r"\n{3,}", "\n\n", content)

    before_lines = len(original.splitlines())
    after_lines  = len(content.splitlines())
    saved = before_lines - after_lines

    # Backup original
    backup = CLAUDE.with_suffix(".md.bak")
    backup.write_text(original, encoding="utf-8")

    # Write optimized
    fd, tmp = tempfile.mkstemp(dir=ROOT, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(content)
        os.replace(tmp, CLAUDE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise

    print(f"\n{GREEN}✓ CLAUDE.md optimized{RESET}")
    print(f"  Before: {before_lines} lines")
    print(f"  After:  {after_lines} lines")
    print(f"  Saved:  ~{saved * 5} tokens per session load")
    print(f"  Backup: {backup.name}")
    print(f"\n  {DIM}Next: manually review for any remaining generic advice{RESET}")
    print(f"  {DIM}Run --audit to see remaining opportunities{RESET}\n")


def main():
    if "--optimize" in sys.argv:
        optimize_claude_md()
    elif "--audit" in sys.argv or not sys.argv[1:]:
        audit = audit_claude_md()
        print_audit(audit)
    else:
        print("Usage: claude_md_optimizer.py [--audit | --optimize]")


if __name__ == "__main__":
    main()
