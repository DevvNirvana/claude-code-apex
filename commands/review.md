# /review — Deep Code Review

You are performing a **deep code review** on: $ARGUMENTS

---

## Step 1: Batch Detection

Check if multiple files were passed:
- Single file → proceed to Step 2
- Directory (e.g., `/review src/components/`) → **batch review**: load context ONCE, review all files, one combined report. Saves 30-66% on context tokens.

---

## Step 2: Load Stack-Aware Context (once per session)

```bash
# Load stack profile to know which rules apply
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('Framework:', p.get('framework'))
    print('Language:', p.get('language'))
    print('Rule sets:', ', '.join(p.get('rule_sets', [])))
    print('Test framework:', p.get('test_framework'))
except: print('No stack profile — run /init first')
"
```

Then load project-specific rules:
```bash
# 1. Always load CLAUDE.md
cat CLAUDE.md 2>/dev/null

# 2. Load project conventions
cat docs/AI_RULES.md 2>/dev/null || cat docs/TECH_STACK.md 2>/dev/null || true

# 3. Inject brain hard constraints (most critical for review)
python3 .claude/intelligence/project_brain.py read "$ARGUMENTS" constraint 2>/dev/null || true
```

**Read the project rules carefully.** Every convention in AI_RULES.md / CLAUDE.md is a review criterion. A violation of project-specific rules is a 🟡 Warning at minimum, 🔴 Blocker if it's a hard rule (e.g., "no API routes", "no state management libraries").

Do NOT re-read if already loaded this session.

---

## Step 3: Load Stack-Specific Review Criteria

Based on the detected framework, apply additional checks:

**If Python/Django:**
- N+1 queries (any DB call inside a loop without select_related/prefetch_related)
- Raw SQL without parameterization
- Missing migrations for model changes
- Bare `except:` clauses
- Missing type hints on non-trivial functions

**If Python/FastAPI:**
- Sync DB calls in async routes
- Missing `response_model` on endpoints
- Business logic inside route handlers (should be in services)
- Missing dependency injection for auth

**If Rails:**
- N+1 without `includes`/`preload`
- `permit!` in strong parameters
- Logic in views instead of models/helpers
- Missing index on foreign keys

**If Go:**
- Unhandled errors (`_` assignment)
- Goroutines without cancellation
- Missing context propagation
- `panic` in non-main code

**If Next.js/React:**
- Missing `await` on async operations
- Race conditions in useEffect
- Incorrect deps arrays
- `any` TypeScript types
- Server/client boundary violations

**If Node.js API:**
- Unparameterized queries
- Missing auth middleware on protected routes
- No rate limiting on auth endpoints

---

## Step 4: Read the Code — Deeply

Read every line. Do not skim. Hold in mind:
- What is this code supposed to do?
- What could silently fail?
- What would a security auditor flag?
- Does it follow the project's own conventions from CLAUDE.md / AI_RULES.md?

---

## Step 5: Review Against These Criteria

### 🔴 Blocking — Must Fix Before Merge

**Project Conventions (from CLAUDE.md / AI_RULES.md)**
- [ ] Violates any "Never do X" hard rule from the project docs
- [ ] Violates architecture constraints (e.g., creates API route when project forbids it)
- [ ] Uses a banned library or pattern

**Correctness**
- [ ] Correctly implements what was intended
- [ ] All edge cases handled: null/nil, empty, 0, negative, max values
- [ ] Errors caught and surfaced — not swallowed silently
- [ ] All async operations awaited (JS/TS/Python)
- [ ] Race conditions possible?
- [ ] State mutated when it shouldn't be?

**Security**
- [ ] Inputs validated/sanitized before use
- [ ] Queries parameterized (no string interpolation)
- [ ] Auth/permission checks present on every protected operation
- [ ] Secrets hardcoded?
- [ ] User-controlled data in file paths, eval(), or shell commands?
- [ ] File uploads validated (type, size, content)?
- [ ] CSRF protection on mutation endpoints?

### 🟡 Warnings — Fix Soon

**Performance**
- [ ] N+1 queries inside loops
- [ ] Large datasets not paginated
- [ ] Expensive operations not memoized where appropriate
- [ ] Missing database indexes on queried columns
- [ ] Unnecessary re-renders (React-specific)
- [ ] Large bundle imports (JS-specific)

**Code Quality**
- [ ] Dead code or commented-out blocks
- [ ] Functions > 40 lines (extract smaller)
- [ ] Ambiguous variable names
- [ ] Complex logic without explaining comments
- [ ] Magic numbers/strings without named constants
- [ ] TypeScript `any` or Python missing type hints
- [ ] Test coverage missing for this code path

### 🟢 Notes — Good to Address
- Missing tests for this path
- Documentation that would help maintainers
- Minor style inconsistencies with project conventions

---

## Step 6: Output the Review

Format **exactly** like this. No introduction. Start with `## Code Review:`.

```markdown
## Code Review: [filename(s)]
**Reviewed:** [timestamp] | **Stack:** [framework] | **Verdict:** [APPROVED | APPROVE_WITH_CHANGES | REQUEST_CHANGES]

### Summary
[2 sentences: overall quality + most important concern]

### 🔴 Blocking Issues
**[Issue Title]** — `filename:line`
> `[quoted problematic code — one line]`
**Problem:** [what is wrong and why it matters]
**Fix:**
\`\`\`[language]
// [exact replacement code]
\`\`\`

### 🟡 Warnings
**[Issue Title]** — `filename:line`
**Problem:** [explanation]
**Suggestion:** [what to do instead]

### 🟢 Notes
- [Small improvement or observation]

### ✅ What's Good
- [Acknowledge good work]

### Verdict
[ ] ✅ APPROVED — merge-ready
[ ] 🟡 APPROVE_WITH_CHANGES — merge after warnings
[ ] 🔴 REQUEST_CHANGES — blocking issues must be resolved
```

---

## Step 7: Offer to Fix

After the review output, add exactly one line:
```
Fix blocking issues? (yes [issue #] / yes all / no)
```

If yes: fix each issue, show the diff, explain the change. Do not re-review unless asked.

---

> **Token Target:** ≤ 900 output tokens per file.
> **Batch Rule:** Load context once. Review all files in sequence. Never reload per file.
> **Project Rules Rule:** Violations of CLAUDE.md / AI_RULES.md are always flagged — they are not overridden by general best practices.
> **After review:** record outcomes as issues get fixed:
> `python3 .claude/intelligence/evaluator.py record review review.issue_fixed 1.0`
> `python3 .claude/intelligence/evaluator.py record review review.false_positive 0.0`
