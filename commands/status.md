# /status — APEX System Health Dashboard

You are generating a **complete system status report** for APEX and this project.

---

## Run All Checks

```bash
echo "=== APEX STATUS ===" && date

# Stack profile
echo "" && echo "--- Stack ---"
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    gen = p.get('detected_at','?')[:10]
    print(f'Framework: {p.get(\"framework\",\"?\")} {p.get(\"framework_version\",\"\")} | Lang: {p.get(\"language\",\"?\")} | Platform: {p.get(\"platform\",\"?\")}')
    print(f'Detected:  {gen} | Rules: {len(p.get(\"rule_sets\",[]))} active')
except: print('No stack profile — run /init')
" 2>/dev/null

# Doc path validation
echo "" && echo "--- Doc Paths ---"
python3 - << 'PYEOF'
import json
from pathlib import Path
docs = {}
claude_md = Path("CLAUDE.md")
if claude_md.exists():
    content = claude_md.read_text(errors="ignore")
    import re
    paths = re.findall(r"docs/[A-Za-z_]+\.md|[A-Z_]+\.md", content)
    for p in set(paths):
        exists = Path(p).exists()
        status = "✅" if exists else "❌ MISSING"
        print(f"  {status} {p}")
else:
    print("  ❌ CLAUDE.md not found")
PYEOF

# Cache stats
echo "" && echo "--- Plan Cache ---"
python3 .claude/intelligence/cache_manager.py stats 2>/dev/null

# Token budget
echo "" && echo "--- Session Budget ---"
python3 .claude/intelligence/token_tracker.py budget 2>/dev/null

# Brain status
echo "" && echo "--- Project Brain ---"
python3 .claude/intelligence/project_brain.py status 2>/dev/null

# Taste memory
echo "" && echo "--- Taste Profile ---"
python3 .claude/intelligence/taste_memory.py profile 2>/dev/null

# Trajectory store
echo "" && echo "--- Trajectory Store ---"
python3 .claude/intelligence/trajectory_store.py stats 2>/dev/null

# Evaluator
echo "" && echo "--- Command Quality ---"
python3 .claude/intelligence/evaluator.py report 2>/dev/null

# Active agents
echo "" && echo "--- Active Agents ---"
git branch | grep "agent/" || echo "  (no active agent branches)"

# Pending P0 tasks
echo "" && echo "--- Pending P0 Tasks ---"
grep -c "\[ \].*\[P0\]" TODO.md AI_TASKS.md 2>/dev/null && \
  grep "\[ \].*\[P0\]" TODO.md AI_TASKS.md 2>/dev/null | head -5 || \
  echo "  (no P0 tasks or no tasks file)"

# Recent session log
echo "" && echo "--- Last Session ---"
tail -10 docs/SESSION_LOG.md 2>/dev/null || tail -10 SESSION_LOG.md 2>/dev/null || echo "  (no session log)"
```

---

## Format the Output

Synthesize into a clean dashboard:

```
╔══ APEX STATUS ═══════════════════════════════════════════╗
║ Project:    [name]            [timestamp]                ║
║ Framework:  [framework v.xx]  [platform]                 ║
╠══════════════════════════════════════════════════════════╣
║ CONTEXT                                                  ║
║   CLAUDE.md:     [✅ valid / ⚠️ N paths broken]          ║
║   Stack profile: [✅ current / ⚠️ N days old]            ║
║   Brain facts:   [N valid / N invalidated]               ║
╠══════════════════════════════════════════════════════════╣
║ INTELLIGENCE                                             ║
║   Plan cache:    [N templates | X% hit rate]             ║
║   Trajectories:  [N stored | avg quality X]              ║
║   Taste signals: [N signals | X% acceptance]             ║
║   Budget today:  [$X.XX of $X.XX | status]              ║
╠══════════════════════════════════════════════════════════╣
║ QUALITY                                                  ║
║   /review:  [Grade X | trend]                            ║
║   /plan:    [Grade X | trend]                            ║
║   /design:  [Grade X | trend]                            ║
╠══════════════════════════════════════════════════════════╣
║ WORKFLOW                                                 ║
║   Active agents: [N (list names) / none]                 ║
║   P0 tasks open: [N]                                     ║
║   Last session:  [date / summary]                        ║
╚══════════════════════════════════════════════════════════╝

Recommendations:
  [any immediate actions needed — broken paths, stale profile, etc.]
```

---

> If brain conflicts exist: list them.
> If checkpoint is due (10+ sessions): flag it.
> If any doc paths are broken: list the correct paths to fix.
> **Token Target:** ≤ 600 tokens. Facts only, no narrative.


---

## Step 6: Proactive Intelligence (APEX thinks before you ask)

Cross-reference all data sources and surface any of these signals automatically:

```bash
# Run the full proactive analysis
python3 .claude/intelligence/token_intelligence.py audit
python3 .claude/intelligence/project_brain.py conflicts
```

**Check for these proactively — surface them without being asked:**

**Quality degradation:**
```python
# If /review grade dropped more than one letter grade in last 5 sessions → flag it
# "Your /review quality dropped from A→C over 5 sessions. Something changed."
```

**Stale plans:**
```bash
# If any TASK-ID has been [>] in-progress for more than 3 sessions → surface it  
grep -c "\[>\]" TODO.md 2>/dev/null || grep -c "\[>\]" docs/AI_TASKS.md 2>/dev/null
```

**Brain conflicts unresolved:**
```bash
python3 .claude/intelligence/project_brain.py conflicts
```
If > 0 conflicts: "3 brain conflicts from last week — resolve before planning new features"

**Budget trajectory:**
If today's cost > 80% of soft warn threshold: "At current rate you'll hit soft limit in ~N more commands"

**Context health alert:**
```bash
python3 -c "
lines = len(open('CLAUDE.md').read().splitlines())
print(f'CLAUDE.md: {lines} lines')
if lines > 80: print('WARNING: Over 80 lines — compliance degrades')
"
```

**Never seen before tasks:**
If a task in TODO.md has been there for 5+ sessions with no [>] or [x] status → "TASK-007 has never been started. Is it still relevant?"

---

> **Token target:** ≤ 600 tokens. Facts only, no narrative. Surface the anomalies.
