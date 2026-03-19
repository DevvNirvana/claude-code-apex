# Agent Protocol — Handoff Format

> Used when integrating Claude worktree agents with external frameworks:
> AutoGen, CrewAI, LangGraph, custom orchestrators

---

## Agent Configuration Schema

Each agent exports a config at `.claude/agent-config.json`:

```json
{
  "agent_id": "agent-frontend",
  "role": "Frontend Developer",
  "branch": "agent/frontend",
  "worktree": "worktrees/agent-frontend",
  "domain": {
    "owns": ["src/app/", "src/components/", "public/"],
    "reads": ["src/types/", "src/lib/"],
    "never_touches": ["src/api/", "migrations/", ".env*"]
  },
  "current_task": {
    "id": "TASK-002",
    "title": "Build user dashboard",
    "status": "in_progress",
    "started_at": "2024-01-15T10:00:00Z",
    "acceptance_criteria": [
      "Dashboard renders user stats",
      "Responsive on mobile",
      "Loading states implemented"
    ]
  },
  "capabilities": [
    "react", "typescript", "tailwind", "next.js"
  ],
  "constraints": [
    "No direct database access",
    "Use API routes defined in DESIGN_DOC.md",
    "All components must have TypeScript types"
  ]
}
```

---

## Task Assignment Protocol

When the orchestrator assigns a task to an agent:

```json
{
  "type": "task_assignment",
  "agent_id": "agent-frontend",
  "task": {
    "id": "TASK-002",
    "title": "Build user dashboard",
    "description": "...",
    "acceptance_criteria": ["..."],
    "context_files": [
      "docs/DESIGN_DOC.md",
      "docs/PRD.md#user-stories"
    ],
    "estimated_effort": "M",
    "priority": "P0",
    "depends_on": ["TASK-001"]
  },
  "assigned_at": "2024-01-15T09:00:00Z"
}
```

---

## Task Completion Protocol

When an agent completes a task:

```json
{
  "type": "task_complete",
  "agent_id": "agent-frontend",
  "task_id": "TASK-002",
  "status": "done",
  "completed_at": "2024-01-15T14:30:00Z",
  "summary": "Built dashboard with responsive grid, loading skeletons, and real-time stats",
  "files_changed": [
    "src/app/dashboard/page.tsx",
    "src/components/StatsCard.tsx",
    "src/components/DashboardGrid.tsx"
  ],
  "tests_added": [
    "src/components/__tests__/StatsCard.test.tsx"
  ],
  "notes": "API endpoint GET /api/stats needs caching — flagged in TODO.md as TASK-011"
}
```

---

## Orchestrator Commands

The orchestrator can send these commands to agents:

| Command | Payload | Effect |
|---------|---------|--------|
| `assign_task` | task object | Agent starts working on task |
| `pause` | reason | Agent commits and pauses |
| `resume` | — | Agent continues |
| `reassign` | new_task | Agent switches to different task |
| `report_status` | — | Agent reports current progress |
| `merge_check` | — | Agent checks if ready to merge |

---

## Integration Examples

### AutoGen
```python
from autogen import AssistantAgent

frontend_agent = AssistantAgent(
    name="agent-frontend",
    system_message=open("worktrees/agent-frontend/CLAUDE.md").read(),
    llm_config={"model": "claude-sonnet-4-20250514"}
)
```

### CrewAI
```python
from crewai import Agent, Task

frontend_dev = Agent(
    role="Frontend Developer",
    goal="Build UI components per TODO.md assignments",
    backstory=open("worktrees/agent-frontend/AGENT_BRIEF.md").read(),
    verbose=True
)
```

### Export config for external frameworks
```bash
bash .claude/scripts/export-agent-config.sh
# Outputs: .claude/agents/*.json for each active agent
```
