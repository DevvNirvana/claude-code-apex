from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Hooks Generator
====================
Converts high-confidence brain constraints into Claude Code hooks.

Research basis: ETH Zurich arXiv 2602.11988 (Feb 2026)
  - CLAUDE.md rules: ~60% compliance, degrades after 5+ messages, vanishes on compaction
  - Hooks: ~90%+ compliance, survive context compaction, deterministic enforcement

Architecture:
  CLAUDE.md  = guidance (things Claude should know)
  Hooks      = law (things Claude cannot bypass)

Generated hooks:
  SessionStart       re-injects critical rules after every compaction
  PreToolUse[Write]  blocks hardcoded secrets before file writes
  PreToolUse[Bash]   blocks direct push to main/master
  PostToolUse[Write] runs lint after edits (if configured)
  Stop               session-end docs update reminder

Usage:
  python3 .claude/intelligence/hooks_generator.py            # generate
  python3 .claude/intelligence/hooks_generator.py --preview  # show without writing
  python3 .claude/intelligence/hooks_generator.py --audit    # status report
  python3 .claude/intelligence/hooks_generator.py --force    # overwrite existing
"""
import json, sys, os, tempfile
from pathlib import Path

ROOT       = Path.cwd()
APEX_DIR   = ROOT / ".claude"
SETTINGS   = APEX_DIR / "settings.json"
BRAIN_FILE = APEX_DIR / "brain" / "facts.jsonl"
HOOKS_DIR  = APEX_DIR / "hooks"

GREEN  = "\033[0;32m"; CYAN   = "\033[0;36m"; YELLOW = "\033[1;33m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    DIM    = "\033[2m"; RESET = "\033[0m"


def _get_apex_version() -> str:
    ver_file = APEX_DIR / "config" / "apex-version.json"
    try:
        return json.loads(ver_file.read_text()).get("version", "6.0.0")
    except Exception:
        return "6.0.0"


# ── Data loading ──────────────────────────────────────────────────────────────

def load_high_confidence_constraints() -> list[dict]:
    """Load brain constraints with confidence >= 0.95. These become hooks, not hints."""
    if not BRAIN_FILE.exists():
        return []
    facts = []
    for line in BRAIN_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            f = json.loads(line)
            if (f.get("category") == "constraint"
                    and f.get("confidence", 0) >= 0.95
                    and not f.get("invalidated_at")):
                facts.append(f)
        except Exception:
            continue
    return facts


def load_stack_profile() -> dict:
    p = APEX_DIR / "config" / "stack-profile.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}


# ── Hook script content ───────────────────────────────────────────────────────

def build_session_start_script(constraints: list[dict]) -> str:
    """
    Re-inject condensed critical rules on every SessionStart.
    This is the single most effective technique for compliance decay.
    Source: Christopher Montes (CodeToDeploy, 2026) — guidelines survive
    4+ hour sessions with multiple compactions when re-injected via hook.
    """
    # Get identity name (reads from .claude/identity.json if exists)
    import subprocess as _sp
    try:
        name_result = _sp.run(
            ["python3", ".claude/intelligence/apex_identity.py", "line", "Active constraints (re-injected)"],
            capture_output=True, text=True, timeout=3
        )
        banner_cmd = name_result.stdout.strip() if name_result.returncode == 0 else ""
    except Exception:
        banner_cmd = ""

    lines = [
        "#!/usr/bin/env bash",
        "# APEX SessionStart Hook — update check + constraint re-injection",
        "# 1. Checks for APEX updates once per 24h (cached, silent if current)",
        "# 2. Re-injects critical constraints after context compaction",
        "",
        "# Update check (silent if current, prompt if new version available)",
        "if command -v python3 >/dev/null 2>&1; then",
        "  python3 .claude/intelligence/update_checker.py check 2>/dev/null || true",
        "fi",
        "",
        "echo ''",
    ]
    if banner_cmd:
        lines.append(f"echo '{banner_cmd}'")
    else:
        lines.append("echo '=== APEX ACTIVE CONSTRAINTS (re-injected each session, survives compaction) ==='")
    shown = 0
    for c in constraints[:12]:  # hard cap: beyond 12, diminishing returns per research
        content = c.get("content", "").replace("'", "").replace('"', "")[:100]
        if content:
            lines.append(f"echo '  - {content}'")
            shown += 1
    if shown == 0:
        lines.append("echo '  (no high-confidence constraints yet — run /setup)'")
    lines.append("echo '=== End constraints ====================================='")
    lines.append("echo ''")
    return "\n".join(lines)


def build_secrets_script() -> str:
    return r"""#!/usr/bin/env bash
# APEX PreToolUse[Write/Edit] — blocks hardcoded secrets before file writes
# Exit code 2 blocks the tool use entirely (PreToolUse only).
FILE="$1"
[ -z "$FILE" ] || [ ! -f "$FILE" ] && exit 0

# Real secret patterns (not example/placeholder values)
if grep -qE \
  '(sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{36}|eyJ[A-Za-z0-9]{50,})' \
  "$FILE" 2>/dev/null; then
    echo "APEX BLOCKED: Potential secret detected in $FILE" >&2
    echo "Use .env.local for real keys. Never commit secrets to source." >&2
    exit 2
fi
exit 0
"""


def build_protect_main_script() -> str:
    return r"""#!/usr/bin/env bash
# APEX PreToolUse[Bash] — blocks direct push to main/master
# Exit code 2 blocks the bash command.
CMD="${1:-}"
if echo "$CMD" | grep -qE 'git\s+push\s+(origin\s+)?(main|master)\b'; then
    echo "APEX BLOCKED: Direct push to main/master is not allowed." >&2
    echo "Create a feature branch: git checkout -b feat/your-feature" >&2
    exit 2
fi
exit 0
"""


def build_session_end_script() -> str:
    return r"""#!/usr/bin/env bash
# APEX Stop Hook — session-end reminder for documentation hygiene
echo ""
echo "--- APEX: Session complete ---"
echo "Before closing, spend 2 minutes:"
echo "  1. Update TODO.md: mark [x] done, add discovered tasks"
echo "  2. Add entry to docs/SESSION_LOG.md"
echo "  3. If something shipped: python3 .claude/intelligence/trajectory_store.py store <file>"
echo ""
exit 0
"""


def build_lint_script(lint_cmd: str) -> str:
    return f"""#!/usr/bin/env bash
# APEX PostToolUse[Write] — runs lint after every file edit
# Exits 0 even on lint errors (show them, don't block)
{lint_cmd} 2>&1 | head -25 || true
"""


# ── Settings generation ───────────────────────────────────────────────────────

def generate_settings(profile: dict) -> dict:
    h = ".claude/hooks"
    settings = {
        "_apex_version": _get_apex_version(),
        "_note": "Generated by APEX hooks_generator.py — edit hooks/*.sh, not this file.",
        "hooks": {
            "UserPromptSubmit": [
                {
                    "matcher": "",
                    "hooks": [
                        {"type": "command", "command": f"bash {h}/inject-reference.sh \"$PROMPT\""},
                        {"type": "command", "command": f"bash {h}/session-pollution.sh"}
                    ]
                }
            ],
            "SessionStart": [
                {
                    "matcher": "",
                    "hooks": [{"type": "command", "command": f"bash {h}/session-start.sh"}]
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Write|Edit|Bash",
                    "hooks": [{"type": "command", "command": f"bash {h}/crash-checkpoint.sh \"$TOOL_NAME\" \"$TOOL_INPUT_FILE_PATH\""}]
                },
                {
                    "matcher": "Write|Edit",
                    "hooks": [{"type": "command", "command": f"bash {h}/check-secrets.sh \"$TOOL_INPUT_FILE_PATH\""}]
                },
                {
                    "matcher": "Bash",
                    "hooks": [{"type": "command", "command": f"bash {h}/protect-main.sh \"$TOOL_INPUT_COMMAND\""}]
                },
            ],
            "Stop": [
                {
                    "matcher": "",
                    "hooks": [{"type": "command", "command": f"bash {h}/session-end.sh"}]
                }
            ],
        }
    }

    lint = profile.get("build_commands", {}).get("lint")
    if lint:
        settings["hooks"]["PostToolUse"] = [
            {
                "matcher": "Write",
                "hooks": [{"type": "command", "command": f"bash {h}/run-lint.sh"}]
            }
        ]

    return settings


# ── Atomic write ──────────────────────────────────────────────────────────────

def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ── Main ──────────────────────────────────────────────────────────────────────


def build_crash_checkpoint_script() -> str:
    return r"""#!/usr/bin/env bash
# APEX PreToolUse Hook — Crash Checkpoint Writer
# Fires before every Write, Edit, and Bash tool use.
# Writes an atomic checkpoint so /init can recover if Claude Code crashes.
#
# Research: Claude Code --resume fails on OOM kill (GitHub #18880, #30302)
# This gives APEX its own crash recovery independent of Claude Code sessions.

TOOL="$1"
FILE="${2:-}"

case "$TOOL" in
  Write|Edit|Bash) ;;
  *) exit 0 ;;
esac

if command -v python3 >/dev/null 2>&1; then
  python3 .claude/intelligence/crash_guard.py checkpoint "$TOOL" "$FILE" 2>/dev/null || true
fi

exit 0
"""


def build_session_pollution_script() -> str:
    """
    UserPromptSubmit hook: warns when session turns exceed safe threshold.
    Research: quality drops sharply past ~15 turns in complex sessions.
    """
    return r"""#!/usr/bin/env bash
# APEX UserPromptSubmit Hook — Session Pollution Detection
TURNS_FILE=".claude/logs/session_turns.txt"
mkdir -p ".claude/logs" 2>/dev/null
TURNS=$(cat "$TURNS_FILE" 2>/dev/null || echo "0")
TURNS=$((TURNS + 1))
echo "$TURNS" > "$TURNS_FILE"
if [ "$TURNS" -eq 15 ]; then
    echo ""
    echo "⚠ APEX: Session at turn 15. Context may be getting polluted."
    echo "  Consider /compact or /handoff before starting a new task."
    echo ""
elif [ "$TURNS" -ge 25 ] && [ $((TURNS % 5)) -eq 0 ]; then
    echo ""
    echo "🔴 APEX: Session at turn $TURNS. Start fresh for best results."
    echo "  Run /handoff to preserve context, then open a new session."
    echo ""
fi
exit 0
"""

def main():
    preview = "--preview" in sys.argv
    audit   = "--audit"   in sys.argv
    force   = "--force"   in sys.argv

    constraints = load_high_confidence_constraints()
    profile     = load_stack_profile()
    lint        = profile.get("build_commands", {}).get("lint")

    # ── Audit mode ──
    if audit:
        hooks_count = len(list(HOOKS_DIR.glob("*.sh"))) if HOOKS_DIR.exists() else 0
        print(f"\n{BOLD}{CYAN}━━━ APEX Hooks Audit ━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"  High-confidence constraints: {len(constraints)}")
        print(f"  settings.json:               {'✓' if SETTINGS.exists() else '✗ MISSING'}")
        print(f"  Hook scripts:                {hooks_count}")
        if constraints:
            print(f"\n  Constraints injected at session start:")
            for c in constraints[:8]:
                print(f"    [{c['confidence']:.0%}] {c['content'][:70]}")
        no_hooks = not SETTINGS.exists() or hooks_count == 0
        if no_hooks:
            print(f"\n  {YELLOW}Run: python3 .claude/intelligence/hooks_generator.py{RESET}")
        print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")
        return

    # ── Preview mode ──
    if preview:
        print(f"\n{BOLD}settings.json:{RESET}")
        print(json.dumps(generate_settings(profile), indent=2))
        print(f"\n{BOLD}session-start.sh:{RESET}")
        print(build_session_start_script(constraints))
        return

    # ── Guard against overwrite ──
    if SETTINGS.exists() and not force:
        print(f"{YELLOW}⚠ settings.json already exists. Use --force to overwrite.{RESET}")
        print(f"{DIM}  Preview: python3 .claude/intelligence/hooks_generator.py --preview{RESET}")
        return

    # ── Write hook scripts ──
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    scripts = {
        "session-start.sh":    build_session_start_script(constraints),
        "check-secrets.sh":    build_secrets_script(),
        "protect-main.sh":     build_protect_main_script(),
        "session-end.sh":      build_session_end_script(),
        "session-pollution.sh": build_session_pollution_script(),
        "crash-checkpoint.sh": build_crash_checkpoint_script(),
    }
    if lint:
        scripts["run-lint.sh"] = build_lint_script(lint)

    for name, content in scripts.items():
        p = HOOKS_DIR / name
        p.write_text(content, encoding="utf-8")
        os.chmod(p, 0o755)

    # ── Write settings.json ──
    atomic_write_json(SETTINGS, generate_settings(profile))

    print(f"\n{GREEN}✓ APEX hooks generated{RESET}")
    for name in scripts:
        print(f"  {DIM}.claude/hooks/{name}{RESET}")
    print(f"  {DIM}.claude/settings.json{RESET}")
    print(f"\n  {BOLD}What this enforces:{RESET}")
    print(f"  {GREEN}SessionStart:    {len(constraints)} constraints re-injected after every compaction{RESET}")
    print(f"  {GREEN}PreToolUse:      secrets blocked, main branch protected{RESET}")
    if lint:
        print(f"  {GREEN}PostToolUse:     lint runs after every file write{RESET}")
    print(f"  {GREEN}Stop:            session docs reminder{RESET}")
    print(f"\n  {YELLOW}Expected compliance upgrade: ~60% → ~90%+{RESET}")
    print(f"  {YELLOW}You can now remove these from CLAUDE.md (hooks enforce them):{RESET}")
    print(f"  {DIM}  - Never commit secrets or API keys{RESET}")
    print(f"  {DIM}  - Never push directly to main{RESET}")
    print(f"  {DIM}  (keep them in brain for reference, remove from CLAUDE.md to save tokens){RESET}\n")


if __name__ == "__main__":
    main()
