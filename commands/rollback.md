# /rollback — Emergency Rollback

You are preparing an **emergency rollback** after a bad deploy.

---

## Step 1: Identify What to Roll Back

```bash
# Check recent commits
git log --oneline -20

# Check worktree metadata for recent merges
ls .claude/worktrees-meta/ 2>/dev/null && \
  ls -t .claude/worktrees-meta/*.json 2>/dev/null | head -5 | \
  xargs python3 -c "
import json, sys
for f in sys.argv[1:]:
    d = json.load(open(f))
    if d.get('status') == 'merged':
        print(f'Merged: {d[\"agent_id\"]} at {d.get(\"merged_at\",\"?\")} — {d.get(\"commit_message\",\"?\")[:60]}')
" 2>/dev/null || true

# Check current branch and clean state
git status --short
git branch --show-current
```

---

## Step 2: Confirm the Rollback Target

Show the developer:
```
Recent merged agents:
  [agent-name] — [commit message] — [timestamp]

Last 5 commits:
  [git log --oneline -5 output]
```

Ask: "Roll back to which commit? (paste SHA or agent name)"

---

## Step 3: Execute the Rollback

```bash
# Create revert commit (safe — preserves history)
git revert --no-edit [SHA]

# OR for full rollback to a specific commit:
# git revert HEAD..[SHA]

# Show what changed
git diff HEAD~1 --stat
```

If rolling back a squash-merged agent commit:
```bash
# The squash commit is a single SHA — revert it directly
git revert --no-edit [squash-commit-SHA]
git commit -m "revert([agent-name]): rolling back due to [reason]"
```

---

## Step 4: Verify

```bash
# Run build to confirm clean state
[build_command_from_stack_profile]
[test_command_from_stack_profile]
```

Report: build status, which files changed, what was reverted.

---

## Step 5: Post-Rollback

```bash
# Log the rollback to brain
python3 .claude/intelligence/project_brain.py write "{
  \"content\": \"Rolled back [agent/feature] on [date] due to [reason]\",
  \"category\": \"decision\",
  \"source\": \"rollback\",
  \"confidence\": 1.0
}" 2>/dev/null || true
```

Remind: "Run `/debug [issue]` to investigate root cause before re-deploying."

---

> **Token Target:** ≤ 400 tokens. Get to the revert fast.
> **Never force push** — always use `git revert` to preserve history.
