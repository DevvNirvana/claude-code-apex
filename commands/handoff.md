# /handoff — Session Context Bridge

**Use at the end of any complex session to preserve context for the next one.**

Research basis: Starting a fresh session costs ~20K tokens but avoids quality loss from polluted context. A handoff file recovers 90% of that startup cost by providing only the high-signal information from the previous session.

---

## What this does

Creates `.claude/handoff.md` — a compact briefing the next session reads automatically at `/init`. Contains only what the next session needs: nothing it can infer from the codebase itself.

---

## Step 1: Read current session state

```bash
cat TODO.md 2>/dev/null || cat docs/AI_TASKS.md 2>/dev/null
python3 .claude/intelligence/project_brain.py status
python3 .claude/intelligence/trajectory_store.py stats
```

## Step 2: Write handoff.md

Create `.claude/handoff.md` with this exact structure:

```markdown
# APEX Session Handoff
Generated: [ISO timestamp]

## Completed this session
[Bullet list of what actually shipped — 3-6 items, specific]

## Active right now
[What's in progress — which TASK-IDs, which files were last touched]

## Critical decisions made
[Decisions that aren't obvious from the code — "chose X over Y because Z"]

## Traps to avoid
[Specific patterns or approaches tried and failed this session]

## Next action
[Exactly what to do first in the next session — one sentence]

## File context (most recently modified)
[List of 3-5 files changed this session with why]
```

## Step 3: Compress the briefing

The handoff must be under 400 tokens. If it's longer:
- Remove anything Claude can discover from the codebase
- Remove completed items older than 2 sessions
- Keep only the "next action" and "traps to avoid" if forced to cut

## Step 4: Verify

```bash
python3 -c "
content = open('.claude/handoff.md').read()
tokens = len(content) // 4
print(f'Handoff: {tokens} tokens ({len(content.splitlines())} lines)')
print('OK' if tokens < 400 else 'TOO LONG — trim it')
"
```

---

## How the next session uses it

`/init` checks for `.claude/handoff.md` and if found, reads it as the first context item before anything else. This gives the new session a ~30-second briefing instead of a full codebase exploration.

After the new session has loaded it:
```bash
rm .claude/handoff.md  # consumed — prevents stale handoffs
```

> **Token target:** Zero Claude API tokens. This is a writing exercise.
