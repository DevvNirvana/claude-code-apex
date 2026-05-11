from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Skills Manager
===================
Converts APEX commands to Claude Code Skills format for lazy loading.

Research basis:
  - Progressive disclosure: 100 tokens per skill description at startup
    vs 22,276 tokens if all 19 commands loaded eagerly (91% reduction)
  - Skills load full content ONLY when Claude determines they're relevant
  - UserPromptSubmit hooks can trigger specific skills via keyword matching

Skills format per Claude Code official spec (code.claude.com/docs/en/skills):
  .claude/skills/<name>/SKILL.md with YAML frontmatter:
    name: <name>
    description: <when Claude should invoke this — keyword-rich>

Usage:
  python3 .claude/intelligence/skills_manager.py install   # create skills from commands
  python3 .claude/intelligence/skills_manager.py stats     # show token savings
  python3 .claude/intelligence/skills_manager.py validate  # check all skills valid
"""
import json, sys, os
from pathlib import Path

ROOT     = Path.cwd()
APEX_DIR = ROOT / ".claude"
COMMANDS = APEX_DIR / "commands"
SKILLS   = APEX_DIR / "skills"

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"

# Maps command name → trigger keywords for description (keyword-rich = better discovery)
SKILL_DESCRIPTIONS = {
    "setup":    "Zero-friction onboarding for any project. Auto-detects stack, generates CLAUDE.md, seeds brain, warms cache. Use on first install or new project.",
    "init":     "Session initialization. Validates docs, syncs brain, warms cache. Use at the start of every session or after updating CLAUDE.md.",
    "status":   "Full system dashboard. Brain health, cache stats, budget, quality grades, DORA metrics, active agents. Use when you want a system overview.",
    "brainstorm": "Socratic requirements before coding. Generates Decision Record with what we ARE and are NOT building. Use before planning any non-trivial feature.",
    "ask":      "Read-only codebase query with brain context. Use when you have a question about the codebase without wanting to modify anything.",
    "plan":     "DAG-structured planning with trajectory injection and brain constraints. Use to break down a feature or task into ordered steps before executing.",
    "execute":  "Batched plan execution with lint and test checkpoints between every step. Use to run an existing plan from TODO.md or AI_TASKS.md.",
    "design":   "Stack-adaptive UI with aesthetic direction phase before coding. Use when building components, pages, or any visual interface.",
    "spawn":    "Parallel agents in isolated git worktrees with domain conflict detection. Use when tasks can run simultaneously without interfering.",
    "test":     "Framework-specific test generation with TDD enforcement. Use to generate tests for existing or new code.",
    "debug":    "Root cause analysis with brain constraint injection. Use when investigating bugs, errors, or unexpected behavior.",
    "optimize": "Performance profiling and targeted fixes. Use for bundle size, query performance, render time, or load time issues.",
    "refactor": "Safe refactoring with impact analysis and dependency checking. Use when improving code structure without changing behavior.",
    "docs":     "Documentation generation for README, API docs, JSDoc, or inline comments. Use to document existing or new code.",
    "review":   "Multi-perspective deep review against your AI_RULES.md conventions. Use before merging any significant change.",
    "ship":     "40-point pre-flight deployment checklist. Runs your actual build and test commands. Use before every deploy.",
    "rollback": "Emergency rollback using worktree metadata and git revert. Use when a deploy breaks production.",
    "compact":  "Archive completed work and compress stale docs. Use when TODO.md or SESSION_LOG.md exceeds 150 lines.",
    "benchmark":"Statistical consistency measurement for any command. Use after modifying command prompts to verify quality.",
    "optimize-context": "Research-backed audit of CLAUDE.md and hooks. Removes token waste, generates hooks. Use when costs are high or compliance is low.",
    "handoff":  "Session context transfer. Creates a compact briefing file for the next session. Use when ending a complex session to preserve context.",
}


def install_skills(force: bool = False) -> int:
    """Convert command files to Skills format."""
    if not COMMANDS.exists():
        print(f"{RED}No .claude/commands/ found. Run APEX install first.{RESET}")
        return 0

    SKILLS.mkdir(parents=True, exist_ok=True)
    created = 0

    for cmd_file in sorted(COMMANDS.glob("*.md")):
        name = cmd_file.stem
        skill_dir = SKILLS / name

        if skill_dir.exists() and not force:
            continue

        skill_dir.mkdir(exist_ok=True)
        description = SKILL_DESCRIPTIONS.get(name,
            f"APEX {name} command. Use when the user asks to {name} something.")

        # Build SKILL.md with proper frontmatter
        content = cmd_file.read_text(errors="ignore")
        # Strip the first H1 heading (skill name comes from frontmatter now)
        lines = content.split("\n")
        body_start = 0
        for i, line in enumerate(lines):
            if line.startswith("# /") or line.startswith("# "):
                body_start = i + 1
                break
        body = "\n".join(lines[body_start:]).strip()

        skill_md = f"""---
name: {name}
description: {description}
---

{body}
"""
        (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
        created += 1

    return created


def show_stats():
    cmd_tokens = sum(
        len(f.read_text()) // 4
        for f in COMMANDS.glob("*.md")
    ) if COMMANDS.exists() else 0

    skill_count = len(list(SKILLS.glob("*/SKILL.md"))) if SKILLS.exists() else 0
    skill_startup = skill_count * 100  # ~100 tokens per description at startup
    lazy_per_call = 2000               # ~2000 tokens per skill body when invoked

    print(f"\n{BOLD}{CYAN}━━━ APEX Skills Token Analysis ━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Skills installed:      {skill_count}/19")
    print(f"\n  {BOLD}Eager loading (old):   ~{cmd_tokens:,} tokens/session{RESET}")
    print(f"    Cost:                ${cmd_tokens/1000*0.003:.4f}/session")
    print(f"\n  {GREEN}Skills lazy loading:   ~{skill_startup:,} tokens at startup{RESET}")
    print(f"  {GREEN}+ ~{lazy_per_call:,} tokens per command invoked{RESET}")
    print(f"    Typical session (3 cmds): ~{skill_startup + 3*lazy_per_call:,} tokens")
    print(f"    Cost: ${(skill_startup + 3*lazy_per_call)/1000*0.003:.4f}/session")
    saved = cmd_tokens - (skill_startup + 3*lazy_per_call)
    if cmd_tokens > 0:
        print(f"\n  {YELLOW}Token savings (3-cmd session): ~{saved:,} tokens ({saved/cmd_tokens*100:.0f}%){RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def validate_skills():
    ok = err = 0
    for skill_md in sorted(SKILLS.glob("*/SKILL.md")):
        content = skill_md.read_text(errors="ignore")
        if "---\nname:" in content and "description:" in content:
            ok += 1
        else:
            print(f"  {RED}✗ {skill_md.parent.name}: missing frontmatter{RESET}")
            err += 1
    print(f"  {GREEN}✓ {ok} valid skills{RESET}")
    if err:
        print(f"  {RED}✗ {err} invalid skills{RESET}")


def main():
    args = sys.argv[1:]
    cmd  = args[0] if args else "stats"

    if cmd == "install":
        force = "--force" in args
        n = install_skills(force)
        if n > 0:
            print(f"{GREEN}✓ Created {n} skills in .claude/skills/{RESET}")
        else:
            print(f"{DIM}Skills already installed. Use --force to recreate.{RESET}")
        show_stats()
    elif cmd == "stats":
        show_stats()
    elif cmd == "validate":
        validate_skills()
    else:
        print(f"Usage: skills_manager.py [install|stats|validate]")


if __name__ == "__main__":
    main()
