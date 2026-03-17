# /ship — Pre-Flight Deployment Checklist

You are running **pre-flight checks** before deployment. $ARGUMENTS

Run every check. Report honestly. This is the final gate before production.

---

## Step 1: Load Context + Stack Profile

```bash
# Load project context
cat CLAUDE.md 2>/dev/null
cat docs/AI_RULES.md 2>/dev/null || true

# Load stack profile for stack-specific checks
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('FRAMEWORK:', p.get('framework', 'unknown'))
    print('PLATFORM:', p.get('platform', 'web'))
    print('BUILD_CMD:', p.get('build_commands', {}).get('build', 'unknown'))
    print('TEST_CMD:', p.get('build_commands', {}).get('test', 'unknown'))
    print('DEPLOY:', p.get('deploy_target', 'unknown'))
except: print('No stack profile')
" 2>/dev/null
```

Also check P0 tasks and acceptance criteria:
```bash
cat TODO.md 2>/dev/null || cat AI_TASKS.md 2>/dev/null || true
```

---

## Step 2: Run Build + Tests

Use the build commands from the stack profile (or detect from CLAUDE.md):
```bash
# Build must pass — errors are 🔴 blockers
[build_command_from_stack_profile]

# Tests must pass — failures are 🔴 blockers  
[test_command_from_stack_profile]
```

Report output verbatim. Any error = HOLD_CRITICAL.

---

## Step 3: Scan for Leaked Secrets (Enhanced)

```bash
# Entropy-aware pattern scanning — catches more than simple prefix matching
grep -rEn \
  'sk-[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|ghp_[A-Za-z0-9]{36}|ghs_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]+|-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY|AIza[A-Za-z0-9_-]{35}|[0-9a-fA-F]{32,40}(?=.*secret|.*key|.*token)|password\s*[:=]\s*["\x27][^"\x27\n]{8,}|secret\s*[:=]\s*["\x27][^"\x27\n]{8,}|api[_-]?key\s*[:=]\s*["\x27][^"\x27\n]{8,}|token\s*[:=]\s*["\x27][^"\x27\n]{16,}|auth[_-]?token\s*[:=]\s*["\x27][^"\x27\n]{8,}' \
  --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --include="*.py" --include="*.rb" --include="*.go" --include="*.php" \
  --include="*.env" --include="*.json" --include="*.yaml" --include="*.yml" \
  --include="*.toml" --include="*.sh" \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=vendor \
  --exclude-dir=dist --exclude-dir=.next --exclude-dir=__pycache__ \
  . 2>/dev/null \
  | grep -v "\.env\.example" \
  | grep -v "# example\|# placeholder\|your-key-here\|xxx\|placeholder" \
  | head -30
```

If gitleaks is installed (recommended for teams):
```bash
gitleaks detect --no-git --report-format json 2>/dev/null | python3 -c "
import json, sys
try:
    findings = json.load(sys.stdin)
    for f in findings[:10]:
        print(f'🔴 LEAKED SECRET: {f.get(\"RuleID\")} in {f.get(\"File\")}:{f.get(\"StartLine\")}')
except: pass
" 2>/dev/null || true
```

Any real secrets found = 🔴 HOLD_CRITICAL immediately.

---

## The 40-Point Pre-Flight Checklist

### 🔴 CRITICAL — Deployment Blockers

**Security**
- [ ] No hardcoded secrets, API keys, or credentials in source code
- [ ] `.env` files are in `.gitignore` — only `.env.example` committed
- [ ] Authentication required on all protected routes/endpoints
- [ ] Input validation on all user-facing forms and API endpoints
- [ ] Parameterized queries — no string-interpolated SQL/NoSQL
- [ ] CORS configured correctly (not `*` in production)
- [ ] Rate limiting on auth endpoints (login, register, password reset)

**Correctness**
- [ ] All P0 items in TODO.md / AI_TASKS.md are complete `[x]`
- [ ] All acceptance criteria in PRD.md are met
- [ ] No `[!]` blocked items in TODO without resolution
- [ ] Build passes without errors (see Step 2)
- [ ] All tests pass (see Step 2)
- [ ] No debug `console.log`, `print()`, `puts`, `fmt.Println` left in production paths
- [ ] No commented-out code blocks that shouldn't ship

**Data Integrity**
- [ ] Database migrations are backwards-compatible
- [ ] No destructive migrations without a rollback plan
- [ ] Seed/fixture data doesn't run in production

### 🟡 IMPORTANT — Fix Within 24 Hours

**Performance**
- [ ] No N+1 queries in critical user flows
- [ ] Images/assets optimized (WebP, sizing, lazy loading where applicable)
- [ ] Bundle size within reasonable range
- [ ] Pagination on all list endpoints returning potentially large datasets
- [ ] Caching in place for expensive repeated operations

**UX/Accessibility**
- [ ] All interactive elements keyboard-navigable
- [ ] Color contrast ≥ 4.5:1 for normal text
- [ ] Form fields have proper labels (not just placeholder text)
- [ ] Error states visible and descriptive
- [ ] Loading states implemented for async operations
- [ ] Empty states implemented (no blank screens)
- [ ] 404 and error pages exist

**Code Quality**
- [ ] No `any` TypeScript / missing type hints in critical paths
- [ ] All async functions have error handling
- [ ] Environment variables validated at startup
- [ ] No infinite loops or unhandled rejections possible

### 🟢 RECOMMENDED — Track as Tech Debt

**Documentation**
- [ ] README.md is accurate and up to date
- [ ] API endpoints documented
- [ ] `.env.example` has descriptions for every variable

**Observability**
- [ ] Error tracking configured (Sentry, Axiom, Rollbar, etc.)
- [ ] Critical operations logged
- [ ] Health check endpoint exists
- [ ] Uptime monitoring configured

**CI/CD**
- [ ] Deploy pipeline runs tests before deploying
- [ ] Rollback procedure documented
- [ ] Feature flags for risky changes (if applicable)

---

## Step 4: Stack-Specific Checks

**If Next.js/React:**
```bash
# Check bundle size
cat .next/build-manifest.json 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
print('Build manifest found — check .next/analyze/ for bundle analysis')
" 2>/dev/null || true
```

**If Django/Rails:**
```bash
# Check for missing migrations
python manage.py makemigrations --check --dry-run 2>/dev/null && echo "✓ No missing migrations" || echo "⚠️ Missing migrations detected"
# OR
rails db:migrate:status 2>/dev/null | grep "down" && echo "⚠️ Pending migrations" || echo "✓ All migrations applied"
```

**If Go:**
```bash
go vet ./... 2>/dev/null && echo "✓ go vet clean" || echo "⚠️ go vet issues found"
```

---

## Output the Report

```markdown
## 🚀 Pre-Flight Report — [Project Name]
**Date:** [timestamp] | **Branch:** [git branch] | **Stack:** [framework]

### 🔴 Blocking Issues (HOLD)
- [issue] — [file or location] — [what needs to happen]

### 🟡 Important (Fix Soon)
- [issue] — [brief note]

### ✅ Passed Checks ([N]/40)
| Category     | Score  |
|--------------|--------|
| Security     | N/7    |
| Correctness  | N/7    |
| Performance  | N/5    |
| UX/A11y      | N/7    |
| Code Quality | N/4    |
| Docs         | N/3    |
| Observability| N/4    |
| CI/CD        | N/3    |

---
VERDICT: [SHIP ✅ | HOLD 🟡 | HOLD_CRITICAL 🔴]
```

**HOLD_CRITICAL** = any 🔴 blocking issue found
**HOLD** = no blockers but significant 🟡 warnings
**SHIP** = all clear

---

## 📋 Session End Checklist

After every significant session — **before closing your terminal:**

```bash
# 1. Update task status
# In TODO.md: mark [x] done, [>] in-progress, [!] blocked

# 2. Log token report
python3 .claude/intelligence/token_tracker.py report --today

# 3. Run evaluator checkpoint if due
python3 .claude/intelligence/evaluator.py report

# 4. Check taste memory checkpoint
python3 .claude/intelligence/taste_memory.py profile
```

Manual steps:
- Add entry to SESSION_LOG.md — built what, key decisions, taste signals table
- If any context file > 150 lines → `/compact` next session
- If you corrected Claude → note it in taste signals table

**These 5 minutes compound into months of faster, smarter sessions.**

---

## 📊 DORA Metrics Tracking

APEX estimates engineering velocity from session data. When you SHIP:

```bash
# Log feature shipping for lead time tracking
python3 .claude/intelligence/token_tracker.py log ship 0 0 --shipped "[feature name]" 2>/dev/null || true
```

View DORA estimates in `/status` — lead time, deployment frequency, change failure rate.

---

> After SHIP verdict: monitor error tracking for 30 minutes post-deploy.
> If anything breaks: run `/debug [issue]` immediately.
