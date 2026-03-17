# /brainstorm — Socratic Requirements Gathering

You are running **pre-code requirements clarification** for: $ARGUMENTS

This runs BEFORE `/plan`. Its job is to surface decisions upfront so planning is grounded in real architectural choices — not discovered mid-build.

---

## Step 1: Load Context

```bash
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('FRAMEWORK:', p.get('framework'), p.get('framework_version',''))
    print('LANGUAGE:', p.get('language'))
    print('DB:', p.get('db'), '/', p.get('db_orm',''))
    print('PLATFORM:', p.get('platform'))
except: print('No stack profile — run /init first')
"
cat CLAUDE.md 2>/dev/null
cat docs/AI_CONTEXT.md 2>/dev/null || true
# Inject relevant experience from trajectory store
python3 .claude/intelligence/trajectory_store.py query "$ARGUMENTS" 2>/dev/null || true
# Inject brain constraints
python3 .claude/intelligence/project_brain.py read "$ARGUMENTS" constraint 2>/dev/null || true
# Inject taste preferences
python3 .claude/intelligence/taste_memory.py inject brainstorm 2>/dev/null || true
```

---

## Step 2: Ask Stack-Specific Questions

Do NOT ask generic questions. Generate questions from the actual detected stack and the specific task. Maximum 6 questions. Each must force a real decision.

**For Next.js/React tasks:**
- Server Component or Client Component? (if yes to interactivity, why?)
- Data fetching: server-side (React Server Component) or client-side (SWR/useEffect)?
- Does this need real-time updates?
- Does this share state with existing components? Which ones?

**For Django/FastAPI tasks:**
- New model or extending an existing one?
- Does it need a DRF serializer + API endpoint, or is this view-only?
- Does it need a Celery task (async) or is synchronous fine?
- Are there migration implications?

**For Rails tasks:**
- New resource or extending an existing controller?
- Does it need a background job (Sidekiq)?
- Turbo Frames/Streams or standard request/response?

**For Go tasks:**
- New handler in existing router or new service?
- Does it need a goroutine? How do you cancel it?
- Needs middleware (auth, rate limit)?

**Universal questions (always include relevant ones):**
- What does "done" look like? (acceptance criteria in 2 sentences)
- What are you explicitly NOT building in this session?
- Does this touch any code owned by another agent/branch?
- Are there existing patterns in the codebase this should follow?

---

## Step 3: Synthesize Decision Record

After receiving answers, output a structured decision record:

```markdown
## Decision Record: [Feature Name]
**Date:** [timestamp]
**Stack:** [detected stack]

### What We're Building
[1-2 sentences of exact scope]

### What We're NOT Building
[explicit exclusions — prevents scope creep]

### Architectural Decisions
- **Data layer:** [decision + one-line reasoning]
- **UI layer:** [decision + one-line reasoning]
- **State:** [decision + one-line reasoning]
- **API/Integration:** [decision + one-line reasoning]

### Constraints That Apply (from CLAUDE.md + brain)
- [hard constraint from project docs]
- [hard constraint from project docs]

### Acceptance Criteria
- [ ] [observable criterion 1]
- [ ] [observable criterion 2]
- [ ] [observable criterion 3]

### Ready for /plan
[summary sentence confirming scope is clear]
```

---

## Step 4: Write to Brain

```bash
python3 .claude/intelligence/project_brain.py write '{
  "content": "[key architectural decision from this session]",
  "category": "decision",
  "source": "brainstorm",
  "confidence": 0.9
}' 2>/dev/null || true
```

---

> After outputting the Decision Record, add exactly one line:
> `Ready to plan? Run: /plan [feature name] or ask me to refine further.`

> **Token Target:** ≤ 500 output tokens. Ask questions, get answers, output the record. No narrative.
