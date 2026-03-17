# /debug — Root Cause Analysis

You are performing **root cause analysis** on: $ARGUMENTS

This is not symptom-chasing. Find the actual cause. Deliver the exact fix.

---

## Step 1: Load Context
Read: `CLAUDE.md` (stack + conventions)

---

## Step 2: Gather Evidence

Ask for (or locate) these in order:

1. **The error message** — exact text, full stack trace if available
2. **The file/line** — where the error originates
3. **What was expected** — what should have happened
4. **What happened instead** — the actual behavior
5. **When it started** — always worked / broke after a change / intermittent
6. **Reproduction steps** — how to trigger it reliably

If any of these are missing, ask for them in ONE message before proceeding.

---

## Step 3: Form Hypotheses

Before looking at code, generate 3-5 hypotheses ranked by likelihood:

```
H1 (most likely): [hypothesis] — [why this fits the evidence]
H2:               [hypothesis] — [why this fits the evidence]  
H3:               [hypothesis] — [why this fits the evidence]
```

---

## Step 4: Eliminate Hypotheses

Check each hypothesis against the code:

For each hypothesis:
- What evidence confirms or denies it?
- What code would look different if this were the cause?
- Test it mentally or with a targeted code read

---

## Step 5: Identify Root Cause

The root cause is **the specific code condition** that produced the bug — not the symptom.

- ❌ Symptom: "The component is re-rendering too much"
- ✅ Root cause: "useMemo dependency array includes `user` object reference that changes identity on each render because it's created inline in the parent"

- ❌ Symptom: "API returns 500"  
- ✅ Root cause: "Prisma query uses `findUnique` but `id` can be `undefined` when no session — Prisma throws on undefined vs null"

---

## Step 6: Output the RCA Report

Format **exactly** like this. No introduction. Start with `## Debug: [issue]`.

```markdown
## Debug: [Short Issue Name]

### Symptom
[What the user reported — one sentence]

### Root Cause
[The actual code condition causing the bug — be specific about the mechanism]

### Evidence
\`\`\`
[File: filename.ts, Line N]
[The problematic code]
\`\`\`
[Explanation of why this is the cause]

### Fix
\`\`\`typescript
// Before:
[old code]

// After:
[new code]
\`\`\`
**Why this fixes it:** [one sentence]

### Verify
After applying the fix, verify with:
\`\`\`bash
[verification command or test]
\`\`\`

### Prevention
[How to prevent this class of bug in the future — a convention, a lint rule, a type, a test]
```

---

## Step 7: Offer to Apply Fix

After the report, add exactly:
```
Apply this fix? (yes / show me more context first)
```

---

## Common Root Causes by Category

**React / Next.js**
- Object identity in deps array (new object on every render → infinite loop)
- Missing `await` on Server Action → returns Promise instead of value
- Hydration mismatch → server/client render different content
- `useEffect` without cleanup → subscription leak / stale closure
- `use client` missing → trying to use browser API in Server Component
- `next/image` missing `width`/`height` and no `fill` → layout shift

**TypeScript**
- `undefined` not handled → crash when optional value is absent
- `as` type assertion hiding actual type mismatch
- Generic type inference failure → `any` slipping through

**Async/Promises**
- Unhandled promise rejection → silent failure
- Race condition → two async ops update same state
- Error inside `async` function caught outside → wrong error handler

**Database**
- N+1 query → `findMany` in a loop
- Missing index → slow query under load
- Transaction not used → partial write on failure
- `null` vs `undefined` → Prisma treats them differently

**Auth**
- JWT expired but not refreshed → silent auth failure
- Cookie not sent cross-origin → CORS + credentials config
- Session not invalidated on logout → security issue

---

> **Token Target:** ≤ 700 output tokens. Precision over comprehensiveness.
> **Rule:** Never say "It could be" or "Maybe". Commit to the most likely root cause.
