# /optimize-context — Token & Compliance Intelligence Report

**Runs the research-backed audit of your CLAUDE.md and hook setup.**

Based on ETH Zurich arXiv 2602.11988 (Feb 2026): context files hurt performance when redundant, increase cost by 20%+, and agents ignore bloated instructions. This command tells you exactly what to fix.

---

## Step 1: Audit CLAUDE.md

```bash
python3 .claude/intelligence/claude_md_optimizer.py --audit
```

This checks for:
- **Architecture folder trees** — agents discover structure themselves. Remove them.
- **Generic advice** — "Write clean code" wastes instruction budget. Remove it.
- **Hook-redundant rules** — rules already enforced by hooks cost tokens twice. Remove them.
- **Line count** — target ≤50 lines. Above 80, compliance degrades uniformly.

---

## Step 2: Check Hooks Status

```bash
python3 .claude/intelligence/hooks_generator.py --audit
```

If hooks are missing:
```bash
python3 .claude/intelligence/hooks_generator.py
```

Hooks enforce your constraints at the OS level — they survive context compaction. CLAUDE.md cannot.

**The research-backed difference:**
- CLAUDE.md rules: ~60% compliance, degrades after 5 messages, vanishes after compaction
- Hooks: ~90%+ compliance, deterministic, session-length independent

---

## Step 3: Apply Optimizations

```bash
# Remove architecture trees and generic advice from CLAUDE.md
python3 .claude/intelligence/claude_md_optimizer.py --optimize

# Generate hooks (if not done)
python3 .claude/intelligence/hooks_generator.py
```

---

## Step 4: Move Hook-Enforced Rules OUT of CLAUDE.md

After generating hooks, your CLAUDE.md no longer needs:
- "Never commit .env or API keys" → enforced by check-secrets.sh hook
- "Never push directly to main" → enforced by protect-main.sh hook
- Lint/format rules → enforced by run-lint.sh hook (if configured)

Keeping them in CLAUDE.md after hooks exist wastes tokens and degrades instruction compliance for everything else.

---

## Step 5: Verify the Improvement

```bash
# Check what brain context actually gets injected per command
python3 .claude/intelligence/project_brain.py status

# Check cache hit rate (high cache = low redundant token cost)
python3 .claude/intelligence/cache_manager.py stats
```

---

## What Good Looks Like

```
CLAUDE.md:     40-55 lines
Hooks:         4-6 active scripts  
Brain facts:   15-25 (constraints + patterns, no generic advice)
Cache hit rate: 30%+ (growing over time)
Session cost:  <$0.05 for typical 3-command session
```

---

## The Architecture After This

```
CLAUDE.md (40 lines)        = What Claude should know about this project
Hooks (4-6 scripts)         = What Claude cannot bypass
Brain facts (15-25)         = What accumulates and improves over sessions
Cache (grows over time)     = What avoids redundant planning costs
```

This is the architecture confirmed by the ETH Zurich paper, Boris Cherny's team at Anthropic, and HumanLayer's production analysis. More lines is not better. The right 40 lines is better than 200 lines that degrade each other.

> **Token target:** This command runs Python scripts locally. Zero Claude API tokens used.
