# /spawn — Spawn a Parallel Agent

You are spawning a **focused parallel agent** for: $ARGUMENTS

---

## Step 1: Parse the Spawn Request

Extract from `$ARGUMENTS`:
- **Agent name:** (e.g., "frontend", "api", "auth", "db", "infra")
- **Task:** (what this agent builds — be specific)
- **Domain:** inferred from task if not explicit

Format: `/spawn [agent-name] [task description]`
Example: `/spawn frontend build the job results page with filters and pagination`

---

## Step 2: Load Stack Profile + Project Structure

```bash
# Get detected domain map and stack info
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
try:
    p = json.load(sys.stdin)
    print('FRAMEWORK:', p.get('framework'))
    print('LANGUAGE:', p.get('language'))
    print('PKG_MANAGER:', p.get('package_manager'))
    print('TEST_FRAMEWORK:', p.get('test_framework'))
    print('BUILD_CMD:', p.get('build_commands', {}).get('build'))
    print('TEST_CMD:', p.get('build_commands', {}).get('test'))
    print('LINT_CMD:', p.get('build_commands', {}).get('lint'))
    dm = p.get('domain_map', {})
    print('DOMAIN_MAP:')
    for role, paths in dm.items():
        print(f'  {role}: {paths}')
except: print('No stack profile — run /init first')
" 2>/dev/null

# Scan actual project structure (reality, not assumptions)
echo ""
echo "=== Actual Project Structure ==="
find . -maxdepth 3 -type d \
  ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/.next/*' \
  ! -path '*/dist/*' ! -path '*/__pycache__/*' ! -path '*/vendor/*' \
  ! -path '*/worktrees/*' ! -path '*/.claude/*' \
  | sort | head -50
```

Use the **actual structure** for the agent brief's domain paths — not the template defaults.

---

## Step 3: Read TODO.md and Find Agent's Tasks

```bash
cat TODO.md 2>/dev/null || cat AI_TASKS.md 2>/dev/null || echo "No tasks file found"
```

Identify TASK-IDs that match this agent's domain. Check which are:
- `[ ]` pending → assign these
- `[>]` in-progress → warn about overlap
- `[x]` complete → skip
- `[!]` blocked → include with blocker noted

---

## Step 3b: Check for Domain Conflicts

Before creating the worktree, verify no other active agent owns overlapping paths:

```bash
# Check for active agents and their domains
ls .claude/worktrees-meta/*.json 2>/dev/null | xargs python3 -c "
import json, sys
for f in sys.argv[1:]:
    d = json.load(open(f))
    if d.get('status') == 'active':
        print(f'ACTIVE: {d["agent_id"]} owns: {d.get("domain_paths", [])}')
" 2>/dev/null || true
```

If an active agent owns files that this agent also needs to touch:
- Warn immediately: "⚠ Domain conflict detected: [files] are owned by agent/[name]"
- Options: (1) re-partition domains, (2) wait for other agent to merge first, (3) proceed with explicit coordination note in brief

## Step 4: Create the Git Worktree

```bash
bash .claude/scripts/create-worktrees.sh [agent-name]
```

This creates:
- `worktrees/agent-[name]/` — isolated working directory
- `agent/[name]` branch — isolated from main

---

## Step 5: Generate the Agent Brief

Create `worktrees/agent-[name]/AGENT_BRIEF.md` with this content. Fill in ALL sections from the project scan — never leave `[Fill in: ...]` placeholders:

```markdown
# Agent Brief: [Agent Name]
**Role:** [specific role, e.g., "Frontend Developer — Results Page"]
**Branch:** agent/[name]
**Created:** [timestamp]
**Stack:** [framework + language]

## Your Mission
[1-2 sentences: exactly what you build, specifically]

## Your Domain — Files You OWN (create/edit freely)
[Use actual paths from the project structure scan]
- `[real path 1]/`
- `[real path 2]/`

## Read Access (read, don't modify)
[Use actual paths that exist in this project]
- `[types/interfaces path]` — TypeScript types / Python models
- `[shared utilities path]` — shared utilities
- `[architecture doc]` — architecture decisions
- `[tech stack doc]` — coding standards

## NEVER TOUCH
[Other agents' domains — use actual paths, not assumptions]
- `[backend path]` — api agent's domain
- `[migrations path]` — db agent's domain
- `CLAUDE.md` — orchestrator config
- `.env*` — environment files
- `.claude/` — orchestrator intelligence

## Your Tasks (from TODO.md)
[Fill from actual tasks file — use real TASK-IDs]
- [ ] [TASK-ID]: [description] — [P0/P1/P2]
- [ ] [TASK-ID]: [description] — [P0/P1/P2]

## How to Work — STRICT SEQUENCE

### Before Writing Any Code
1. Read `CLAUDE.md` — understand all conventions and hard rules
2. Read relevant docs (architecture doc, context doc)
3. Check existing similar components/files to match the pattern

### The Build Loop
4. For each task:
   a. **Write tests first** (if test framework is available) — even basic ones
   b. Implement the feature
   c. Run tests: `[test_command_from_stack_profile]`
   d. **If tests fail: read the error, fix the code, run again — do NOT report done until tests pass**
   e. Run lint: `[lint_command_from_stack_profile]`
   f. Commit: `git commit -m "feat([scope]): description"`
   g. Mark task done in TODO.md: `[x]`

### Commit Message Format
`feat([agent-name]): what was built`
`fix([agent-name]): what was fixed`
`test([agent-name]): tests for what`

### Definition of Done
A task is done ONLY when:
- ✅ Code implements the spec
- ✅ Tests pass (`[test_command]`)
- ✅ Lint passes (`[lint_command]`)
- ✅ Follows conventions in CLAUDE.md
- ✅ TODO.md updated with `[x]`

### When Blocked
- Mark task `[!]` in TODO.md with blocker description
- Continue to next unblocked task
- Message the orchestrator: "BLOCKED on [task]: [reason]"

## Code Standards
[Copy the Critical Conventions section from CLAUDE.md exactly]

## Hard Rules
[Copy the Hard Rules / DO NOT section from CLAUDE.md exactly]

## Stack Details
[Copy the Stack section from CLAUDE.md exactly]

## API Contracts
[List the API routes / DB queries this agent will call — from architecture docs]
[If no docs exist, list what you'll need to coordinate with other agents]
```

---

## Step 6: Output the Spawn Summary

```
╔══ AGENT SPAWNED ═════════════════════════════════════════╗
║ Agent:      [name]                                       ║
║ Branch:     agent/[name]                                 ║
║ Worktree:   worktrees/agent-[name]/                      ║
║ Tasks:      [TASK-IDs]                                   ║
║ Owns:       [real file paths]                            ║
║ TDD:        [test command — must pass before done]       ║
╚══════════════════════════════════════════════════════════╝

To start the agent:
  cd worktrees/agent-[name]
  claude  ← opens Claude Code in isolated worktree

When done, merge back:
  bash .claude/scripts/merge-agents.sh [name]
  (squash merges all commits → one clean commit on main)

Merge with history preserved:
  bash .claude/scripts/merge-agents.sh [name] --no-squash
```

---

## Multi-Agent Domain Partitioning

When spawning multiple agents, assign non-overlapping domains using the detected structure. The golden rule: **if two agents could write to the same file, re-partition**.

Common safe splits:
| Agent    | Typically Owns                        | Never Touches              |
|----------|---------------------------------------|----------------------------|
| frontend | UI components, pages, views           | API handlers, migrations   |
| api      | Route handlers, controllers, services | UI components, migrations  |
| db       | Migrations, models, queries           | UI, API route handlers     |
| auth     | Auth flows, session logic             | Unrelated pages, migrations|
| infra    | Dockerfile, CI/CD, scripts            | src/, app code             |

---

> **Token Target:** ≤ 400 output tokens. The brief is the deliverable.
> **Never leave placeholders** — fill every section from the project scan.
> **TDD is non-negotiable** — agents must run tests before reporting completion.
