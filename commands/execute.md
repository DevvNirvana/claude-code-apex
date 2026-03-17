# /execute — Batched Plan Execution with Checkpoints

You are executing a development plan step-by-step with validation between each step.

---

## Step 1: Load the Plan

Read `TODO.md` or `AI_TASKS.md`. Find the DAG-structured task list. Identify:
- Which tasks are `[ ]` pending
- Their `depends_on` relationships
- Which tasks are currently unblocked (all dependencies are `[x]` complete)

```bash
cat TODO.md 2>/dev/null || cat AI_TASKS.md 2>/dev/null
cat .claude/config/stack-profile.json 2>/dev/null | python3 -c "
import json, sys
p = json.load(sys.stdin)
print('TEST:', p.get('build_commands',{}).get('test','npm test'))
print('LINT:', p.get('build_commands',{}).get('lint','npm run lint'))
print('BUILD:', p.get('build_commands',{}).get('build','npm run build'))
" 2>/dev/null
```

---

## Step 2: Show Execution Plan

Before executing anything, show the order:

```
╔══ EXECUTION PLAN ════════════════════════════════════════╗
║ Unblocked tasks (executing now):                         ║
║   → TASK-001: [description]                              ║
║   → TASK-002: [description]  (parallel with 001)         ║
║                                                          ║
║ Blocked (waiting):                                       ║
║   ⏸ TASK-003: depends-on: 001, 002                      ║
║   ⏸ TASK-004: depends-on: 003                           ║
╚══════════════════════════════════════════════════════════╝
Proceed? (yes / show me first / abort)
```

---

## Step 3: The Execution Loop

For each unblocked task, in order:

### 3a. Start
- Mark task `[>]` in TODO.md
- State: "Starting TASK-XXX: [description]"

### 3b. Implement
- Build the code following CLAUDE.md conventions
- Use patterns from brain: `python3 .claude/intelligence/project_brain.py read "[task type]" pattern`
- Check for relevant trajectories: `python3 .claude/intelligence/trajectory_store.py query "[task]"`

### 3c. Validate (after EVERY task)
```bash
# Run lint
[lint_command_from_stack_profile]
echo "LINT_EXIT: $?"

# Run tests if test command available
[test_command_from_stack_profile]
echo "TEST_EXIT: $?"
```

**If validation PASSES:**
- Mark task `[x]` in TODO.md
- Record outcome: `python3 .claude/intelligence/evaluator.py record plan plan.task_completed 1.0`
- Continue to next unblocked task

**If validation FAILS:**
- Show the error output
- Attempt fix
- Re-validate
- If fails 3 times on same task:
  ```
  ⚠ ESCALATION: TASK-XXX failed 3 times.
  Before continuing, let's review the architecture.
  The issue appears to be: [diagnosis]
  Options:
    1. Re-approach this task differently: [alternative approach]
    2. Skip this task and mark [!]: continue without it
    3. Abort execution: /plan to redesign
  Choose (1/2/3):
  ```

### 3d. Unblock next tasks
After a task completes `[x]`, check if any `depends-on` tasks are now unblocked.
If yes, announce: "TASK-004 is now unblocked — adding to queue."

---

## Step 4: Completion Report

When all tasks are done (or execution stops):

```
╔══ EXECUTION COMPLETE ════════════════════════════════════╗
║ Completed: [N] tasks                                     ║
║ Skipped:   [N] tasks (marked [!])                        ║
║ Duration:  [estimated]                                   ║
║                                                          ║
║ Next step: /review [changed files]                       ║
║ Then:      /ship (when ready to deploy)                  ║
╚══════════════════════════════════════════════════════════╝
```

Record completion:
```bash
python3 .claude/intelligence/trajectory_store.py store <(python3 -c "
import json
print(json.dumps({
    'task_description': '[feature name]',
    'task_type': '[type]',
    'stack': '[framework-language-db]',
    'session_summary': '[what was built]',
    'key_decisions': ['[decision 1]', '[decision 2]'],
    'what_worked': '[what went smoothly]',
    'what_to_avoid': '[what caused friction]',
    'total_tasks': [N],
    'tasks_completed': [N],
    'ship_verdict': 'pending'
}))") 2>/dev/null || true
```

---

> **Escalation Rule:** 3 consecutive failures on the same task = architecture review, not a 4th retry.
> **Never mark done** until lint AND tests pass.
> **Always update TODO.md** status in real-time — not at the end.
