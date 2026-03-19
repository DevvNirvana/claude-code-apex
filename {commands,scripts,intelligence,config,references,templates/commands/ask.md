# /ask — Contextual Codebase Query

You are answering a **read-only question** about the codebase: $ARGUMENTS

No building. No planning. Just a precise answer grounded in the actual project.

---

## Step 1: Load Context (minimal — only what's needed)

```bash
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin); print('FRAMEWORK:', p.get('framework'), '| LANG:', p.get('language'))
except: pass
" 2>/dev/null
cat CLAUDE.md 2>/dev/null
# Load brain facts relevant to the query
python3 .claude/intelligence/project_brain.py read "$ARGUMENTS" 2>/dev/null || true
```

---

## Step 2: Find the Answer in the Codebase

Search for code relevant to the question:
```bash
# Find files related to the query
grep -rl "[relevant keyword]" src/ app/ --include="*.ts" --include="*.tsx" \
  --include="*.py" --include="*.rb" --include="*.go" \
  --exclude-dir=node_modules --exclude-dir=__pycache__ 2>/dev/null | head -10
```

Read the most relevant 2-3 files. Do not read files that aren't clearly relevant.

---

## Step 3: Answer Directly

Answer in 3-8 sentences. No preamble. No "Great question." Start with the answer.

Format:
```
**Answer:** [direct answer to the question]

**Where to find it:** `[file:line or folder]`

**How it works:** [1-2 sentence explanation if needed]

**Related:** [any important context — e.g., "this connects to X which lives in Y"]
```

If the answer isn't findable in the codebase: say so directly and suggest where it might be documented or who to ask.

---

> **Token Target:** ≤ 300 output tokens. Answer the question. Stop.
> **No suggestions or improvements** — this is a read-only query command. If you notice issues while answering, note them in one line at the end only.
