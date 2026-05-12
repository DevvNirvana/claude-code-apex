#!/usr/bin/env bash
# APEX UserPromptSubmit Hook — Reference Injection + Cognitive Memory
#
# Two jobs per prompt:
#   1. Lazy reference doc injection  — keyword-triggered, zero tokens if no match
#   2. Cognitive memory injection    — brain facts + trajectories + code index
#      via context_engine.py (APEX Brain OS core)
#
# Research: 15,000 tokens/session recovered vs loading all 23 reference docs upfront.
# Brain OS: activates all idle intelligence modules automatically on every prompt.

PROMPT="${1:-}"
REFS=".claude/references"

[ -z "$PROMPT" ] && exit 0
[ ! -d "$REFS" ]  # refs dir absence is OK — brain context still runs

PROMPT_LOWER=$(echo "$PROMPT" | tr '[:upper:]' '[:lower:]')
REF_INJECTED=0

# ── Reference doc injector ────────────────────────────────────────────────────
# inject_ref() does NOT exit after injecting — falls through to brain context.
# REF_INJECTED flag ensures only one reference doc per prompt (no duplicates).
inject_ref() {
  local file="$REFS/$1"
  [ "$REF_INJECTED" -eq 1 ] && return
  if [ -f "$file" ]; then
    cat "$file"
    REF_INJECTED=1
  fi
}

# ── Framework-specific ────────────────────────────────────────────────────────
echo "$PROMPT_LOWER" | grep -qE 'next\.?js|app router|server component|server action|route handler' && inject_ref "nextjs-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'react|component|hook|usestate|useeffect|jsx|tsx' && inject_ref "react-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'vue|nuxt|svelte|sveltekit|astro' && inject_ref "vue-svelte-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE '\bdjango\b|django orm|django view|django model' && inject_ref "django-patterns.md"
echo "$PROMPT_LOWER" | grep -qE '\brails\b|activerecord|active record|ruby on rails' && inject_ref "rails-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'fastapi|pydantic|async def|fastapi route' && inject_ref "fastapi-patterns.md"
echo "$PROMPT_LOWER" | grep -qE '\bgo\b|golang|goroutine|go module|gin |echo |fiber ' && inject_ref "go-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'react native|flutter|swiftui|ios|android|mobile' && inject_ref "native-guidelines.md"

# ── Domain-specific ───────────────────────────────────────────────────────────
echo "$PROMPT_LOWER" | grep -qE 'sql|postgres|mysql|supabase|query|database|orm|prisma|drizzle|migration' && inject_ref "sql-patterns.md"
echo "$PROMPT_LOWER" | grep -qE 'tailwind|shadcn|ui component|css|styling|design system|token|variant' && inject_ref "shadcn-tailwind-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'test|spec|jest|pytest|vitest|cypress|playwright|coverage|tdd|unit test' && inject_ref "testing-patterns.md"
echo "$PROMPT_LOWER" | grep -qE 'security|auth|permission|rls|jwt|token|csrf|injection|xss|secret|credential' && inject_ref "security-checklist.md"
echo "$PROMPT_LOWER" | grep -qE 'api|rest|endpoint|route|openapi|swagger|graphql|grpc|webhook' && inject_ref "api-design.md"
echo "$PROMPT_LOWER" | grep -qE 'mcp|model context protocol|tool|server|claude tool' && inject_ref "mcp-guide.md"
echo "$PROMPT_LOWER" | grep -qE 'chart|graph|icon|svg|visualization|d3|recharts|chart\.js' && inject_ref "charts-icons-reference.md"
echo "$PROMPT_LOWER" | grep -qE 'page layout|landing|hero|card|grid|flex|responsive|mobile first' && inject_ref "page-patterns.md"
echo "$PROMPT_LOWER" | grep -qE 'ux|user experience|accessibility|a11y|wcag|aria|usability' && inject_ref "ux-principles.md"
echo "$PROMPT_LOWER" | grep -qE 'inspiration|animation|motion|framer|gsap|aesthetic|dark neon|glassmorphism' && inject_ref "inspiration.md"
echo "$PROMPT_LOWER" | grep -qE 'agent|multi.agent|worktree|spawn|parallel|orchestrat' && inject_ref "agent-protocol.md"
echo "$PROMPT_LOWER" | grep -qE 'python|pip|virtualenv|async python|type hint' && inject_ref "python-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'typescript|type error|interface|type alias|generics|zod|ts config' && inject_ref "react-guidelines.md"
echo "$PROMPT_LOWER" | grep -qE 'debug|error|crash|bug|fix|broken|not working|issue|stack trace' && inject_ref "troubleshooting.md"

# ── Cognitive Memory injection (APEX Brain OS) ────────────────────────────────
# context_engine.py reads the prompt from stdin and returns:
#   - Brain facts (semantic memory) matched to this prompt
#   - Relevant past trajectories (episodic memory) for FULL-tier tasks
#   - Code symbol hints (code index) for STANDARD/FULL tasks
#   - Budget warning if session is near daily limit
# Returns empty string for MICRO-tier prompts (zero overhead).
if command -v python3 >/dev/null 2>&1; then
  BRAIN_CTX=$(echo "$PROMPT" | python3 .claude/intelligence/context_engine.py 2>/dev/null)
  [ -n "$BRAIN_CTX" ] && echo "$BRAIN_CTX"
fi

exit 0
