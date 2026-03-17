# /compact — Context Compaction

You are running **context compaction** to keep project docs lean and token-efficient.

Long docs = slower reads, more tokens consumed every session. This command archives completed work and compresses stale decisions without losing anything.

---

## Step 1: Identify What to Compact

Check these files for bloat:
```bash
wc -l TODO.md AI_TASKS.md docs/*.md 2>/dev/null | sort -rn | head -20
```

Files over 150 lines are candidates for compaction.

---

## Step 2: Compact TODO.md / AI_TASKS.md

Read the tasks file. Identify:
- All `[x]` completed tasks
- All `[!]` blocked tasks resolved long ago
- Anything in `## Completed` section older than the last 2 sessions

**Archive completed tasks:**
```bash
# Create archive if it doesn't exist
touch docs/ARCHIVE.md
```

Move completed tasks to `docs/ARCHIVE.md` under a dated heading:
```markdown
## Archive — [Date]
### Completed Tasks
- [x] Task name — completed [date if known]
- [x] Task name
```

**Keep in main tasks file:**
- All `[ ]` open tasks
- All `[>]` in-progress tasks  
- Most recent session's completed tasks (for context)
- All `[P0]` tasks regardless of status

---

## Step 3: Compress DESIGN_DOC.md / AI_CONTEXT.md

Read the doc. Identify:
- Architectural decisions made and no longer debated
- Setup instructions that only needed to be followed once
- Long exploratory sections that are now settled

**Compress pattern:**
```markdown
## [Section Name] — Archived Decision
> Decision made [approx date]: [1-2 sentence summary of what was decided and why]
> Full history archived in docs/ARCHIVE.md#[section]
```

Do NOT compress:
- Active conventions and rules (needed every session)
- Current schema/data model (referenced constantly)
- Critical constraints (e.g., "no API routes")
- Anything the team is still debating

---

## Step 4: Compress SESSION_LOG.md

Sessions older than 4-6 sessions can be summarized:
```markdown
## Sessions [date range] — Summary
Built: [comma-separated features completed]
Fixed: [comma-separated bugs resolved]  
Key decisions: [bullet list of permanent decisions made]
```

Keep full detail for the most recent 3-4 sessions.

---

## Step 5: Output Compaction Report

```
╔══ COMPACTION COMPLETE ═══════════════════════════════════╗
║                                                          ║
║  Before → After                                          ║
║  TODO.md:        [X] lines → [Y] lines (saved Z%)       ║
║  SESSION_LOG.md: [X] lines → [Y] lines (saved Z%)       ║
║  DESIGN_DOC.md:  [X] lines → [Y] lines (saved Z%)       ║
║                                                          ║
║  Archived to: docs/ARCHIVE.md                            ║
║  Estimated token savings per session: ~[N] tokens        ║
╚══════════════════════════════════════════════════════════╝
```

---

## When to Run /compact

- After every 3-4 sessions of active development
- When any context file exceeds 150 lines
- Before starting a major new feature (clean slate for the new phase)
- Before adding a new team member or agent

---

> **Rule:** Never delete anything permanently. Always archive before removing.  
> **Token Target:** ≤ 600 output tokens. This command reads, archives, and reports.
