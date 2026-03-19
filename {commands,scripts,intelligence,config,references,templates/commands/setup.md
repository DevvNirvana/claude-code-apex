# /setup — Zero-Friction Project Onboarding

**Run this once on any project — new or existing. APEX does the rest.**

This command detects your stack, generates CLAUDE.md automatically, seeds the brain, warms the cache, and gets you to your first productive command in under 60 seconds.

---

## What /setup does

```
Step 1 → Detect stack (language, framework, version, DB, auth, commands)
Step 2 → Generate CLAUDE.md automatically from what it finds
Step 3 → Ask you 3 questions to fill gaps it can't detect
Step 4 → Seed the brain with your architecture constraints  
Step 5 → Warm the plan cache from your task list (if it exists)
Step 6 → Run /init to complete initialization
Step 7 → Show you the 3 commands to run next
```

---

## Step 1: Detect Stack

```bash
python3 .claude/intelligence/detect_stack.py --save
```

Read the output carefully. Confirm:
- Framework name and version are correct
- Database/ORM is identified
- Build commands look right

---

## Step 2: Auto-Generate CLAUDE.md

```bash
# If no CLAUDE.md exists yet:
python3 .claude/intelligence/generate_claude_md.py

# If CLAUDE.md already exists (existing project):
python3 .claude/intelligence/generate_claude_md.py --preview
```

If no CLAUDE.md existed: it was just created. Proceed to Step 3.

If one existed: compare the preview to your current file. If the preview is better, update with `--force`. If yours is better, skip to Step 4.

---

## Step 3: Fill the 3 Gaps (2 minutes)

Open CLAUDE.md and check for these three things that auto-detection cannot determine:

**Gap 1 — Project description (2 sentences)**
Find the `## Project` section. If it says `[describe...]`, replace it:
- Sentence 1: What does it do? Be specific.
- Sentence 2: Who uses it? What problem does it solve?

**Gap 2 — Critical Conventions (the project-specific rules)**
Find `## Critical Conventions`. The auto-generated ones are framework defaults.
Add 1-3 conventions that are specific to THIS project — things that would bite a new developer on day one. Examples:
- "All DB queries through `lib/api/queries.ts` — never call Prisma directly in components"
- "Never use API routes — Supabase client directly in all components"
- "State is local — no global state library, useState only"

**Gap 3 — Verify Hard Rules start with "Never"**
Scan `## Hard Rules`. Every line must start with the word "Never". The brain sync only extracts "Never" rules. If any don't start with Never, fix them now.

---

## Step 4: Seed the Brain

```bash
python3 .claude/intelligence/project_brain.py sync
```

This auto-extracts your "Never" rules and stack facts into the persistent brain.

If you have an existing `docs/AI_RULES.md` or `docs/ARCHITECTURE.md`, write the most important facts manually:

```bash
python3 .claude/intelligence/project_brain.py write '{
  "content": "Your most important architectural constraint here",
  "category": "constraint",
  "confidence": 1.0
}'
```

---

## Step 5: Warm the Cache

```bash
# Auto-detect your tasks file and warm
python3 .claude/intelligence/cache_manager.py warm

# Or specify explicitly:
python3 .claude/intelligence/cache_manager.py warm TODO.md
python3 .claude/intelligence/cache_manager.py warm docs/AI_TASKS.md
```

If no tasks file exists yet, skip this — the cache warms automatically as you use `/plan`.

---

## Step 6: Complete Initialization

```bash
# This validates everything and confirms you're ready
```

Run `/init` to validate the full setup. You'll see:

```
╔══ APEX INITIALIZED ═══════════════════════════════════╗
║ Framework:  [your framework] v[version]               ║
║ Brain:      [N] facts loaded                          ║
║ Cache:      [N] templates warmed                      ║
║ Doc Paths:  ✅ All found                              ║
╚═══════════════════════════════════════════════════════╝
```

If any doc paths show ❌: open CLAUDE.md and fix the path in `## Docs`. Re-run `/init`.

---

## Step 7: Start Building

**New project → scaffold first:**
```
/brainstorm scaffold the project
/plan scaffold the project
/execute
```

**Existing project → review first:**
```
/review src/[your main file]
/plan [next feature from your TODO]
```

**Unsure where to start:**
```
/status
```
Shows everything: brain health, cache state, budget, task list.

---

## Common Setup Scenarios

**Empty directory (no code, no docs):**
1. Run `/setup` — it generates CLAUDE.md from zero
2. Fill the 3 gaps (2 min)
3. Run `/brainstorm scaffold` — APEX asks the right questions before writing any code

**Existing project (code exists, no CLAUDE.md):**
1. Run `/setup` — detects your actual stack from package.json / requirements.txt
2. Check `--preview` output matches reality  
3. Fill the 3 gaps — focus especially on Critical Conventions
4. Run `/review src/` to establish a quality baseline

**Migrating from older APEX version:**
```bash
bash .claude/scripts/install.sh --update
python3 .claude/intelligence/generate_claude_md.py --preview
```
Compare preview to your existing CLAUDE.md. Take the best of both.

---

> **Token target:** Setup itself uses no Claude tokens. All steps are Python scripts running locally. The only cost is your time: ~5 minutes for a new project, ~2 minutes for an existing one.
