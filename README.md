# APEX - AI Engineering OS  v4.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![Bash](https://img.shields.io/badge/scripting-bash-lightgrey.svg)]()
[![Claude Code](https://img.shields.io/badge/Powered%20by-Claude%20Code-purple.svg)]()

The first AI engineering system that **learns from your project**, **improves from your corrections**, and gets **measurably better every week you use it.**

Every other tool (Cursor, Copilot, Devin, all the Claude plugins) is stateless: every session is session one. APEX accumulates project knowledge across sessions through a temporal fact store, trajectory replay, and explicit preference learning. It enforces quality at every stage, not just generation. It tracks whether it's actually improving your engineering velocity via DORA metrics.

---

## Install (30 seconds)

```bash
unzip claude-orchestrator-apex-v4.zip
bash claude-orchestrator-apex-v4/install.sh

# Fill in CLAUDE.md with your project details
# Then in Claude Code:
/init
```

**Options:**
```bash
bash install.sh --dry-run    # preview
bash install.sh --force      # overwrite existing
bash install.sh --update     # update intelligence layer only (safe for upgrades)
```

---

## The 3-Group Command System (17 commands)

### Meta / System
| Command | What it does |
|---------|-------------|
| `/init` | Initialize: detect stack, sync brain, validate docs, warm cache |
| `/status` | Full system dashboard: budget, brain, quality scores, DORA metrics |
| `/compact` | Archive completed work, compress stale docs |
| `/benchmark [cmd]` | Statistical quality measurement for any command |

### Dev Loop
| Command | What it does |
|---------|-------------|
| `/brainstorm [feat]` | **Socratic requirements BEFORE planning** - forces decisions upfront |
| `/ask [question]` | Read-only codebase query with brain context |
| `/plan [task]` | DAG-structured planning with trajectory replay + brain injection |
| `/execute` | Batched plan execution with lint/test checkpoints between every step |
| `/design [ui]` | Stack-adaptive UI with intentional aesthetic direction |
| `/spawn [agent] [task]` | Parallel agents in isolated git worktrees |
| `/test [file]` | Test generation in your framework (Jest, pytest, RSpec, go test) |
| `/debug [issue]` | Root cause analysis |
| `/optimize [target]` | Performance profiling + fixes |
| `/refactor [file]` | Safe refactoring with impact analysis |
| `/docs [target]` | Documentation generation |

### Quality Gates
| Command | What it does |
|---------|-------------|
| `/review [file]` | Multi-perspective deep review with confidence scoring |
| `/ship` | 40-point pre-flight + DORA tracking + session checklist |
| `/rollback` | Emergency rollback using worktree metadata |

---

## The Intelligence Layer

### Trajectory Store (`trajectory_store.py`)
Stores complete successful session trajectories. When a similar task recurs, injects the 2-3 most relevant past trajectories as in-context examples. Lifts planning accuracy from ~73% to ~89% with no training required. (Research: NeurIPS 2025 Self-Generated In-Context Examples.)

```bash
python3 .claude/intelligence/trajectory_store.py stats
python3 .claude/intelligence/trajectory_store.py query "build auth flow"
```

### Project Brain (`project_brain.py`)
Temporal fact store with conflict detection. Three categories: constraints, patterns, decisions, corrections. Facts have validity windows: when something changes, old facts are invalidated, not deleted. Auto-syncs from CLAUDE.md and stack profile on `/init`.

```bash
python3 .claude/intelligence/project_brain.py status
python3 .claude/intelligence/project_brain.py read "authentication"
python3 .claude/intelligence/project_brain.py conflicts
```

### Taste Memory (`taste_memory.py`)
After `/design`, `/plan`, `/brainstorm`: "Was this on target? (y / partially: reason / n: reason)" one line. After 10 signals per command, generates a preference profile injected into future outputs. Human review checkpoint every 10 sessions prevents confident wrong learning.

```bash
python3 .claude/intelligence/taste_memory.py profile
python3 .claude/intelligence/taste_memory.py review  # approval checkpoint
```

### Evaluator (`evaluator.py`)
Self-scoring using deterministic rubrics. No extra Claude calls, scores from observable outcomes: developer fixes, plan completion rates, taste signals.

```bash
python3 .claude/intelligence/evaluator.py report
python3 .claude/intelligence/evaluator.py checkpoint  # human review
```

### Benchmark (`benchmark.py`)
Statistical command quality: runs a command against 10 variants sampled from your real cache history. Measures consistency. On-demand only and never automatic.

```bash
python3 .claude/intelligence/benchmark.py run review
python3 .claude/intelligence/benchmark.py run plan --runs 15
```

### Semantic Plan Cache (`cache_manager.py`)
- Exact-match fast path (dict lookup before similarity scan)
- Synonym normalization: "build auth flow" ≡ "create login system" → cache HIT
- File-change-triggered invalidation (plans expire when referenced files change)
- Cache warm-up from TODO.md / AI_TASKS.md on install

### Token Intelligence (`token_tracker.py`)
- Cost + time saved reporting
- Session budget enforcement (soft warn, hard halt)
- DORA metrics tracking (lead time, deployment frequency)

```bash
python3 .claude/intelligence/token_tracker.py report
python3 .claude/intelligence/token_tracker.py budget
```

### Universal Stack Detection (`detect_stack.py`)
15+ frameworks, version-pinned: Next.js v15.2, Django v4.0, Rails v7.1, Go 1.21, FastAPI, Flutter, SwiftUI. Saves `.claude/config/stack-profile.json`. Every command reads this to load the right reference docs automatically.

```bash
python3 .claude/intelligence/detect_stack.py --save
```

---

## Cross-Project Learning

Patterns learned on one project can be promoted to global knowledge:
```bash
python3 .claude/intelligence/project_brain.py promote [fact_id]
```

Stored in `~/.apex/global-patterns.json`. When APEX initializes on a new project with the same stack, relevant global patterns are available immediately.

Trajectories can also be promoted:
```json
{"promote_global": true, "ship_verdict": "SHIP", ...}
```

---

## The Self-Improvement Loop

```
Session → /execute → /ship SHIP verdict
    → store trajectory (what worked, what to avoid)
    → "Was this on target?" → taste signal
    → evaluator records outcome
    
Next similar session:
    → trajectory injected as context
    → taste preferences injected as context
    → brain facts injected as context
    → output is better calibrated

Every 10 sessions:
    → /status shows evaluator grades
    → human checkpoint: approve or reset
    → brain conflicts reviewed
```

---

## Supported Stacks

| Stack | Frameworks |
|-------|-----------|
| JS/TS Frontend | Next.js, React, Vue, Nuxt, Svelte, SvelteKit, Remix, Gatsby |
| Node.js Backend | Express, Fastify, Hono |
| Python Backend | Django, FastAPI, Flask |
| Ruby | Rails, Sinatra |
| Go | Standard + gin, echo, fiber, chi, gorm |
| PHP | Laravel, Symfony |
| Mobile | Flutter, React Native, SwiftUI |

---

## Requirements
- Claude Code (claude.ai/code)
- Python 3.8+
- Git
- Windows Git Bash compatible

Optional enhancements:
- GitHub MCP - enables auto-PR creation in `/ship`, line comments in `/review`
- Context7 MCP - enables live library doc lookup in `/design`, `/plan`
- `gitleaks` - enhanced secret scanning in `/ship`

---

## File Structure

```
.claude/
├── commands/        # 17 slash commands
├── intelligence/    # 10 Python modules
│   ├── cache_manager.py    - semantic plan cache + exact-match fast path
│   ├── detect_stack.py     - universal stack detector (version-pinned)
│   ├── token_tracker.py    - cost + time + DORA + budget enforcement
│   ├── trajectory_store.py - experience replay (NeurIPS 2025)
│   ├── taste_memory.py     - explicit preference learning
│   ├── project_brain.py    - temporal fact store (Graphiti-inspired)
│   ├── evaluator.py        - self-scoring engine
│   ├── benchmark.py        - statistical command quality
│   ├── design_system.py    - design token extraction
│   └── framework_lint.py   - framework-specific linting
├── references/      # 23 reference docs (stack-specific guidelines)
├── scripts/         # 4 shell scripts (Windows-compatible)
├── config/          # 3 config files (with session budget)
├── brain/           # facts.jsonl + brain_conflicts.log
├── memory/
│   ├── trajectories/   # successful session trajectories
│   ├── taste_signals.jsonl
│   ├── taste_profile.json
│   └── benchmarks/
├── cache/
│   ├── plans/       # plan template cache
│   └── responses/   # response cache
└── worktrees-meta/  # agent metadata
```

## 👨‍💻 About the Architect
```
Built by Tushar Rohilla to solve the token bloat, context loss, and API hallucination issues inherent in modern LLM coding workflows. APEX wraps raw LLM generation in a deterministic, CI/CD-enforcing pipeline.
```
## 🔗 View Portfolio & More Projects: 
```
tushar-rohilla.vercel.app
```

## 🤝 Contributing
```
Pull requests are welcome! If you are proposing a major change to the semantic caching engine or the JSON-lines temporal schemas, please open an issue first to discuss what you would like to change.
```

## 📄 License
```
MIT
```
