# /plan — Plan Before Building

You are creating a **development plan** for: $ARGUMENTS

Cache-first: check if a similar plan exists before generating a new one.

---

## Step 1: Cache Check

```bash
python3 .claude/intelligence/cache_manager.py check "[task description]" plan
```

If HIT (score ≥ 0.60): surface the cached plan. Ask: "Similar plan found — use as starting point? (yes / no / show me)"

---

## Step 2: Load Stack Context

```bash
# Load stack profile
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('FRAMEWORK:', p.get('framework'))
    print('LANGUAGE:', p.get('language'))
    print('PLATFORM:', p.get('platform'))
    print('DB:', p.get('db'))
    print('ORM:', p.get('db_orm'))
    print('TEST:', p.get('test_framework'))
except: pass
"

# Load project conventions
cat CLAUDE.md 2>/dev/null
cat docs/AI_CONTEXT.md 2>/dev/null || cat docs/DESIGN_DOC.md 2>/dev/null || true

# Inject experience: similar past trajectories (highest ROI)
python3 .claude/intelligence/trajectory_store.py query "$ARGUMENTS" 2>/dev/null || true

# Inject relevant brain facts (constraints + decisions + patterns)
python3 .claude/intelligence/project_brain.py read "$ARGUMENTS" 2>/dev/null || true

# Inject taste preferences for /plan
python3 .claude/intelligence/taste_memory.py inject plan 2>/dev/null || true
```

---

## Step 3: Scan Relevant Existing Code

Find files related to the task area — read them to avoid reinventing:
```bash
# Search for related patterns (adjust to detected framework)
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.rb" -o -name "*.go" \) \
  ! -path '*/node_modules/*' ! -path '*/__pycache__/*' ! -path '*/vendor/*' \
  2>/dev/null | xargs grep -l "[relevant keyword from task]" 2>/dev/null | head -5
```

Read the most relevant 2-3 files. The plan should extend existing patterns, not fight them.

---

## Step 4: Generate the Plan

Structure the plan with **stack-aware implementation steps**. The steps must be specific to the detected framework — not generic.

```markdown
## Plan: [Task Name]
**Stack:** [framework + language]
**Complexity:** [Low / Medium / High]
**Estimated:** [N] tasks

### What We're Building
[2 sentences: exactly what this adds to the system]

### Files to Create
- `[actual path matching project structure]` — [purpose]
- `[actual path matching project structure]` — [purpose]

### Files to Modify
- `[existing file]` — [what changes and why]

### Implementation Steps

1. **[Step name]**
   - [Specific action in this stack's idiom]
   - [Not generic — mention actual file names, class names, routes]
   - `[code snippet if helpful]`

2. **[Step name]**
   ...

### Database Changes (if applicable)
[Migration description + SQL or ORM syntax for this project's DB/ORM]

### Tests to Write
[Specific test cases using this project's test framework]
- [ ] `[test name]` — tests [behavior]
- [ ] `[test name]` — tests [error case]

### What Could Go Wrong
- [Risk 1] → [mitigation]
- [Risk 2] → [mitigation]

### Definition of Done
- [ ] [feature works end-to-end]
- [ ] Tests pass: `[test_command]`
- [ ] Lint passes: `[lint_command]`
- [ ] Follows conventions in CLAUDE.md
```

---

## Step 5: Cache the Plan

```bash
python3 .claude/intelligence/cache_manager.py store plan \
  "[task description]" \
  '[{"steps": ["step1", "step2", ...], "files": ["file1", "file2"]}]'
```

---

## Step 6: Update TODO.md

Add a DAG-structured task block with dependency types:
```markdown
## [Task Name]
- [ ] TASK-[N]:   [step 1 — no dependencies] — [P1]
- [ ] TASK-[N+1]: [step 2] — [P1]  depends_on: TASK-[N]
- [ ] TASK-[N+2]: [step 3] — [P1]  depends_on: TASK-[N]
- [ ] TASK-[N+3]: [step 4] — [P1]  depends_on: TASK-[N+1], TASK-[N+2]
- [ ] TASK-[N+4]: Write tests — [P2]  depends_on: TASK-[N+3]
- [ ] TASK-[N+5]: [discovered detail] — [P2]  discovered_from: TASK-[N+3]

## Parallelizable: TASK-[N+1] and TASK-[N+2] (both depend only on TASK-[N])
## Sequential gate: TASK-[N+3] must wait for both
```

---

> **Token Target:** ≤ 600 output tokens. The plan is a guide, not an essay.
> **Stack-specific:** every file path, code snippet, and migration must match the detected stack.
> **Cache it:** always store successful plans so future similar tasks get a head start.
> **After outputting:** ask "Was this plan on target? (y / partially: reason / n: reason)" then run:
> `python3 .claude/intelligence/taste_memory.py log plan [signal] "[context]" "[note]"`
