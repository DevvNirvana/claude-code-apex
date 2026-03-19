# /init — Project Initialization

> **First time on this project?** Run `/setup` instead — it auto-generates your CLAUDE.md and walks through the full onboarding. Run `/init` on subsequent sessions.


You are initializing the APEX orchestrator for this project.

---

## Step 1: Detect & Save Stack Profile

```bash
python3 .claude/intelligence/detect_stack.py --save
```

This detects language, framework, database, test framework, and saves `.claude/config/stack-profile.json`. Read the output — it tells you exactly which rule sets will be active.

---

## Step 2: Validate CLAUDE.md Doc Paths

Read `CLAUDE.md`. Find the `## Docs` section. For every path listed, verify it exists:

```bash
# Check each path from the Docs section
ls -la [each path from Docs section] 2>&1
```

Report clearly:
```
Doc Path Validation:
  ✅ docs/AI_CONTEXT.md     — found (142 lines)
  ✅ docs/AI_RULES.md       — found (67 lines)
  ✅ docs/AI_TASKS.md       — found (89 lines)
  ⚠️  docs/DESIGN_DOC.md    — NOT FOUND (commands will skip this)
  ✅ SESSION_LOG.md          — found (45 lines)
```

For any missing path: warn clearly. Context loading will silently fail for that doc if the path is wrong. Offer to fix the path in CLAUDE.md.

---

## Step 3: Validate CLAUDE.md Quality

Read `CLAUDE.md`. Check:
```
  Length: [N] lines (target: < 80)       [✅ / ⚠️ too long]
  Stack defined: [yes/no]
  Build commands defined: [yes/no]
  Conventions defined: [yes/no]
  Hard rules defined: [yes/no]
  Docs section present: [yes/no]
```

If CLAUDE.md doesn't exist: generate it from the stack profile + any README/docs found.

---

## Step 4: Detect Existing Docs

Check for these files and read first 30 lines of each found:
- `docs/PRD.md` or `PRD.md` or `docs/AI_TASKS.md`
- `docs/DESIGN_DOC.md` or `docs/AI_CONTEXT.md` or `ARCHITECTURE.md`
- `docs/TECH_STACK.md` or `TECH_STACK.md`
- `TODO.md` or `AI_TASKS.md`
- `README.md`

For each missing doc, offer to generate a template filled with what you've learned from the scan.

---

## Step 5: Warm the Plan Cache + Sync Brain

```bash
# Warm plan cache from tasks file
python3 .claude/intelligence/cache_manager.py warm

# Sync brain from CLAUDE.md and stack profile
python3 .claude/intelligence/project_brain.py sync

# Check token budget status
python3 .claude/intelligence/token_tracker.py budget
```

Cache warm: reads TODO.md / AI_TASKS.md and pre-populates plan templates.
Brain sync: extracts constraints from CLAUDE.md, facts from stack profile.

---

## Step 6: Output Init Report

```
╔══ ORCHESTRATOR INITIALIZED ══════════════════════════════╗
║ Project:   [name]                                        ║
║ Language:  [language]                                    ║
║ Framework: [framework + key deps]                        ║
║ Platform:  [web / backend / fullstack / mobile]          ║
║ Tests:     [test framework]                              ║
║                                                          ║
║ Doc Paths: [N]/[N] verified ✅                           ║
║ CLAUDE.md: [valid ✅ / needs update ⚠️]                 ║
║                                                          ║
║ Token Intelligence:                                      ║
║   ✅ Cache initialized ([N] templates from tasks)        ║
║   ✅ Stack profile saved                                 ║
║   ✅ Rule sets active: [list]                            ║
╚══════════════════════════════════════════════════════════╝

Available commands:
  /plan [task]      — Plan before building (cache-aware)
  /design [ui]      — Stack-aware UI generation
  /review [file]    — Deep review (loads your AI_RULES.md)
  /debug [issue]    — Root cause analysis
  /optimize [target]— Performance profiling + fixes
  /test [file]      — Test generation (uses your test framework)
  /refactor [file]  — Safe refactoring with impact analysis
  /docs [target]    — Documentation generation
  /spawn [agent]    — Parallel agents in isolated worktrees
  /compact          — Archive completed work, keep docs lean
  /ship             — 40-point pre-flight checklist
```

> **Next step:** Run `/plan [first task from your TODO]` to start building.

---

> **Token Target:** This command loads context once. All subsequent commands benefit from the warmed cache.
