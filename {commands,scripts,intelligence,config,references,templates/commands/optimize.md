# /optimize — Performance Optimization

You are performing **performance optimization** on: $ARGUMENTS

---

## Step 1: Detect What Needs Optimizing

If `$ARGUMENTS` specifies a file/component → optimize that target.
If `$ARGUMENTS` is vague (e.g., "optimize the app") → run the full scan below.

---

## Step 2: Load Context
Read: `CLAUDE.md` (stack + conventions)

---

## Step 3: Performance Scan by Category

### Frontend Performance

**Bundle Size**
```bash
# Check build output sizes
npm run build 2>&1 | grep -E "Route|Page|chunk|size" | head -30
```

Look for:
- Pages > 200KB first load JS → needs code splitting
- Packages imported entirely when only part needed
- Duplicate dependencies

**React Rendering**
Scan for these patterns in `src/`:
```bash
grep -rn "useEffect\|useState\|useCallback\|useMemo" src/ --include="*.tsx" | head -20
```

Check for:
- `useEffect` with no dependency array (runs on every render)
- State that could be derived (computed instead of stored)
- Missing `useMemo` on expensive calculations
- Missing `React.memo` on pure components receiving complex props
- `key` props using array index (breaks reconciliation)

**Data Fetching**
```bash
grep -rn "fetch\|axios\|prisma\|db\." src/ --include="*.ts" --include="*.tsx" | grep -v "node_modules" | head -20
```

Check for:
- Waterfall fetches (await A then await B when they could be parallel)
- Fetching inside render (should be in Server Component or SWR/React Query)
- Missing caching headers on API responses
- Over-fetching (selecting all columns when few needed)

**Images**
```bash
grep -rn "<img\|Image\b" src/ --include="*.tsx" | head -20
```

Check for:
- `<img>` instead of `next/image`
- Missing `loading="lazy"` on below-fold images
- Images without `width`/`height` causing layout shift
- No `srcset` for responsive images

### Backend / API Performance

**Database Queries**
Look for:
- `findMany` inside a loop (N+1)
- Missing `select` → fetching all columns
- Missing pagination on list endpoints
- No database indexes on filter/sort columns

**Caching**
Check for:
- `unstable_cache` or `revalidate` usage in Next.js
- Redis/cache layer for expensive computations
- Repeated identical queries in same request

---

## Step 4: Prioritize Issues

Rank every found issue:

| Priority | Criteria | Typical Gain |
|----------|----------|-------------|
| **HIGH** | LCP/FCP impact, blocking render, N+1 queries | 2-10x |
| **MEDIUM** | Bundle bloat, unnecessary re-renders, missing pagination | 20-50% |
| **LOW** | Minor memoization, style improvements | 5-15% |

---

## Step 5: Output the Optimization Report

Format **exactly** like this:

```markdown
## Optimization Report: [Target]

### HIGH Impact (Fix First)

**[Issue Name]** — `filename:line`
**Problem:** [what's slow and why — quantify if possible]
**Fix:**
\`\`\`typescript
// Before:
[slow code]

// After:
[optimized code]
\`\`\`
**Expected gain:** [specific metric — e.g., "Reduces re-renders from 12→1 per keystroke"]

### MEDIUM Impact

**[Issue Name]** — `filename:line`
**Problem:** [description]
**Fix:** [code or instruction]
**Expected gain:** [estimate]

### LOW Impact
- `filename:line` — [one-line description and fix]

### Quick Wins (< 5 min each)
- [ ] [Action]
- [ ] [Action]

### Metrics to Track After
- [ ] Lighthouse Performance score (target: ≥ 85)
- [ ] Core Web Vitals: LCP < 2.5s, CLS < 0.1
- [ ] Bundle size: first load JS < 200KB
- [ ] P95 API response time < 500ms
```

---

## Step 6: Offer to Fix

```
Apply HIGH priority fixes? (yes all / yes [issue name] / no)
```

Apply fixes one at a time, test each before moving to the next.

---

> **Token Target:** ≤ 800 output tokens.
> **Rule:** Quantify every problem. "It's slow" is useless. "This causes 47 re-renders per keystroke" is actionable.
