# /refactor — Safe Code Refactoring

You are refactoring: $ARGUMENTS

---

## Step 1: Load Context
Read: `CLAUDE.md` (conventions + pattern)
Read: `docs/TECH_STACK.md` (coding standards)

---

## Step 2: Understand the Target

Read the target file(s) completely. Identify:
- What the code does (current behavior)
- What's wrong with it (why refactor)
- What would be better (target state)

**Refactoring categories:**
- **Extract function** — function > 40 lines, or logic repeated 2+ times
- **Extract component** — JSX > 80 lines, or component doing 2+ things
- **Extract module** — related functions spread across files
- **Simplify logic** — nested conditionals, complex boolean logic
- **Improve naming** — variables/functions with ambiguous names
- **Reduce coupling** — component knows too much about parent/siblings
- **Type improvement** — `any` types, missing generics, loose types
- **Performance refactor** — unnecessary computation, renders, fetches

---

## Step 3: Impact Analysis

Before planning: scan for every place the code-under-refactor is imported or called:

```bash
grep -rn "[functionOrComponentName]" src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | grep -v ".test."
```

List all call sites. This is the blast radius.

---

## Step 4: Risk Assessment

| Risk Level | Criteria |
|-----------|----------|
| **LOW** | Rename, reformat, extract with same signature |
| **MEDIUM** | Change function signature, move to different module |
| **HIGH** | Change behavior, remove public API, schema changes |

State the risk level and what makes it that level.

---

## Step 5: Show the Refactor Plan — WAIT FOR APPROVAL

```
╔══ REFACTOR PLAN ══════════════════════════════════════════╗
║ Target:      [filename(s)]                                ║
║ Type:        [Extract function / Rename / Simplify / etc] ║
║ Risk:        LOW / MEDIUM / HIGH                          ║
║                                                           ║
║ What Changes:                                             ║
║   • [specific change 1]                                   ║
║   • [specific change 2]                                   ║
║                                                           ║
║ What Stays Same:                                          ║
║   • [what is preserved — behavior, API, types]            ║
║                                                           ║
║ Blast Radius: [N] files import this code                  ║
║   • [file 1]                                              ║
║   • [file 2]                                              ║
╚═══════════════════════════════════════════════════════════╝

Refactor with this plan? (yes / adjust [what] / cancel)
```

**STOP HERE.** Do not write any code until the user responds.

---

## Step 6: Execute the Refactor

On approval:

1. **Make the changes** — complete, not partial
2. **Update all call sites** — every file in the blast radius
3. **Preserve behavior** — the refactored code must do exactly the same thing
4. **Improve types** — if types can be made more precise, make them more precise
5. **Maintain or improve tests** — existing tests should still pass

Deliver the complete refactored code for each changed file. No snippets — full file content.

---

## Step 7: Verification Checklist

After refactoring, confirm:

```
Post-Refactor Verification:
✅ TypeScript compiles (no errors)
✅ Tests still pass
✅ All [N] call sites updated
✅ No behavior change (same inputs → same outputs)
✅ Follows CLAUDE.md conventions
✅ Code is shorter or cleaner (if not, state why)
```

---

## Common Refactoring Recipes

### Extract and Name a Complex Conditional
```typescript
// Before — magic boolean
if (user.role === 'admin' || (user.role === 'mod' && user.verified && !user.suspended)) {

// After — named predicate  
const canModerate = (user: User) => 
  user.role === 'admin' || 
  (user.role === 'mod' && user.verified && !user.suspended)

if (canModerate(user)) {
```

### Extract Large useEffect
```typescript
// Before — 40 line useEffect
useEffect(() => {
  // 40 lines of logic
}, [deps])

// After — extracted custom hook
function useFeatureName(deps) {
  useEffect(() => {
    // same logic, now named and testable
  }, [deps])
}
```

### Replace Magic Numbers
```typescript
// Before
if (score > 0.83) { return cached }
setTimeout(retry, 3000)

// After
const CACHE_HIT_THRESHOLD = 0.83
const RETRY_DELAY_MS = 3_000
if (score > CACHE_HIT_THRESHOLD) { return cached }
setTimeout(retry, RETRY_DELAY_MS)
```

---

> **Token Target:** ≤ 1200 output tokens.
> **Golden Rule:** A refactor that changes behavior is a bug, not a refactor.
