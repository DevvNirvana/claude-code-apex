<div align="center">

<h1>APEX - AI Engineering OS</h1>

<p><strong>The first AI coding system that learns from your project, improves from your corrections, and gets measurably better every week you use it.</strong></p>

<p>
  <a href="https://github.com/DevvNirvana/claude-orchestrator-apex/releases"><img src="https://img.shields.io/github/v/release/DevvNirvana/claude-orchestrator-apex?color=8A2EFF&label=version&style=flat-square" alt="Version"></a>
  <a href="https://github.com/DevvNirvana/claude-orchestrator-apex/blob/main/LICENSE"><img src="https://img.shields.io/github/license/DevvNirvana/claude-orchestrator-apex?color=00F7FF&style=flat-square" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Claude%20Code-compatible-blueviolet?style=flat-square" alt="Claude Code">
  <img src="https://img.shields.io/badge/Windows%20Git%20Bash-supported-green?style=flat-square" alt="Windows">
</p>

<p>
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-why-apex">Why APEX</a> ·
  <a href="#-the-18-command-system">Commands</a> ·
  <a href="#-the-intelligence-layer">Intelligence</a> ·
  <a href="#-stack-support">Stacks</a> ·
  <a href="#-honest-comparison">Comparison</a>
</p>

</div>

---

## The problem every Claude Code user has

Every session starts from zero. You re-explain your stack. You repeat your conventions. You remind it that you don't use API routes. You paste your architecture again. The model forgets. You repeat.

By session 50 you've explained the same constraints 50 times. The model on session 50 is exactly as uninformed as it was on session 1. That's not a model problem. That's a systems problem.

APEX solves it.

---

## ⚡ Quick Start

**Install:**

```bash
cd your-project
unzip claude-orchestrator-apex-v4.1.zip
bash claude-orchestrator-apex-v4/install.sh
```

**Then in Claude Code: one command, everything configured:**

```
/setup
```

`/setup` detects your stack, auto-generates `CLAUDE.md`, seeds the project brain with your architectural constraints, and gets you to your first productive command in under 2 minutes: on any project, new or existing. No manual config required to start.

---

## 🧠 Why APEX

Every other Claude Code tool is **stateless**. Session 100 is identical to session 1. They add commands, they add agents, but they don't remember anything.

APEX compounds.

```
Session 1:  APEX knows your stack and hard rules
Session 5:  APEX has your first successful trajectory stored
Session 10: APEX knows your preferences for /design and /plan
Session 20: APEX injects months of real decisions before every command
Session 50: The gap between APEX and starting fresh is enormous
```

The underlying model doesn't change. Your accumulated project knowledge does.

---

## 🔧 The 18-Command System

Three groups. One mental model.

### Meta / System
| Command | What it does |
|---|---|
| `/setup` | **Zero-friction onboarding.** Auto-generates CLAUDE.md, seeds brain, warms cache. Works on any project. |
| `/init` | Start of every session. Validates context, syncs brain, confirms budget. |
| `/status` | Full system dashboard: brain health, cache stats, quality grades, DORA metrics. |
| `/compact` | Archive completed work, compress stale docs. |
| `/benchmark` | Statistical quality measurement for any command. |

### Dev Loop
| Command | What it does |
|---|---|
| `/brainstorm` | Socratic requirements before any code. Generates Decision Record. |
| `/ask` | Read-only codebase query with brain context. |
| `/plan` | DAG-structured planning with trajectory injection. |
| `/execute` | Batched plan execution with lint+test between every step. |
| `/design` | Stack-adaptive UI with intentional aesthetic direction. |
| `/spawn` | Parallel agents in isolated git worktrees. |
| `/test` | Framework-specific test generation. |
| `/debug` | Root cause analysis. |
| `/optimize` | Performance profiling and targeted fixes. |
| `/refactor` | Safe refactoring with impact analysis. |
| `/docs` | Documentation generation. |

### Quality Gates
| Command | What it does |
|---|---|
| `/review` | Multi-perspective deep review. Reads your AI_RULES.md, not just generic checks. |
| `/ship` | 40-point pre-flight before any deploy. Runs your actual build and lint commands. |
| `/rollback` | Emergency rollback using worktree metadata. |

---

## 🔬 The Intelligence Layer

Five Python modules that run locally, store persistently, and compound across sessions.

### Project Brain
A temporal fact store with conflict detection. When you migrate from Prisma to Drizzle, the old fact gets invalidated and the new one takes its place automatically. No stale advice.

```bash
python3 .claude/intelligence/project_brain.py status
# Total facts: 19  |  Valid: 19  |  Constraints: 9  |  Patterns: 6
```

### Trajectory Store
Based on NeurIPS 2025 research on self-generated in-context examples. Every successful session gets stored. When a similar task comes up, APEX injects your past wins before generating a single line of code.

```bash
python3 .claude/intelligence/trajectory_store.py query "build auth flow"
# → returns your previous auth implementation: what worked, what to avoid
```

### Taste Memory
Explicit developer preference learning. After every `/design` and `/plan`, one question: was this on target? After 10 sessions, APEX knows you prefer functional components, dark backgrounds, queries in a central file. It stops suggesting the things you always change.

### Evaluator
Deterministic self-scoring. Grades command quality from observable outcomes. Trends over time. Flags degradation before it becomes a habit. No additional API calls.

### Semantic Plan Cache
Exact-match fast path plus synonym normalization. "Build auth flow" hits "create login system." 30–50% cost reduction at typical usage, growing over time.

---

## 🚀 Auto-Setup: No Config Required

The biggest friction in AI tooling is configuration. APEX removes it.

After install, run `/setup` in Claude Code:

```
✓ Language:   TypeScript
✓ Framework:  Next.js v15.2 (app-router)
✓ Database:   Supabase/PostgreSQL
✓ Commands:   npm run dev / build / lint

→ Generating CLAUDE.md...
→ Seeding brain with 7 architectural constraints...
→ Warming plan cache from TODO.md (12 templates)...
→ Ready. Run /brainstorm or /plan to start building.
```

Three things still need your input (takes 2 minutes): the project description, 2–3 project-specific conventions, and verifying your Hard Rules start with "Never" for brain sync. Everything else is automatic.

---

## 🏗️ Stack Support

| Ecosystem | Frameworks |
|---|---|
| **JavaScript / TypeScript** | Next.js (App + Pages Router), React, Vue, Nuxt, Svelte, SvelteKit, Remix, Astro |
| **Node.js Backend** | Express, Fastify, Hono |
| **Python** | Django, FastAPI, Flask |
| **Ruby** | Rails, Sinatra |
| **Go** | Standard library + gin, echo, fiber, chi |
| **PHP** | Laravel, Symfony |
| **Mobile** | Flutter, React Native, SwiftUI |

Version-pinned detection: APEX knows the difference between Next.js 13 and Next.js 15 because they are fundamentally different codebases.

---

## 📊 Honest Comparison

| | Vanilla Claude Code | oh-my-claudecode | **APEX** |
|---|---|---|---|
| Persistent project memory | ❌ | ❌ | ✅ |
| Learns your preferences | ❌ | ❌ | ✅ |
| Trajectory replay | ❌ | ❌ | ✅ |
| Auto-generates CLAUDE.md | ❌ | ❌ | ✅ |
| Self-scoring quality system | ❌ | ❌ | ✅ |
| Version-pinned stack detection | ❌ | ❌ | ✅ |
| 40-point pre-flight checklist | ❌ | ❌ | ✅ |
| DORA metrics tracking | ❌ | ❌ | ✅ |
| Multi-agent worktrees | ❌ | ✅ | ✅ |
| Gets better over time | ❌ | ❌ | ✅ |
| Windows Git Bash | ❌ | ❌ | ✅ |
| Python 3.8+ compatible | — | — | ✅ |

The core difference: APEX compounds. Every other tool is stateless.

---

## 📦 What Gets Installed

```
.claude/
├── commands/          18 slash commands (including /setup)
├── intelligence/      11 Python modules: all local, no API calls
│   ├── generate_claude_md.py   Auto-generates CLAUDE.md from your project
│   ├── project_brain.py        Temporal fact store with conflict detection
│   ├── trajectory_store.py     Experience replay (NeurIPS 2025)
│   ├── taste_memory.py         Developer preference learning
│   ├── evaluator.py            Self-scoring quality engine
│   ├── benchmark.py            Statistical consistency measurement
│   ├── cache_manager.py        Semantic plan cache
│   ├── detect_stack.py         15+ frameworks, version-pinned
│   ├── token_tracker.py        Cost + time + DORA metrics
│   ├── design_system.py        Design token extraction
│   └── framework_lint.py       Framework-specific lint rules
├── references/        23 reference docs (stack-specific patterns)
├── scripts/           4 shell scripts (Windows-compatible)
├── config/            3 config files
├── brain/             facts.jsonl, grows with your project
└── memory/            trajectories/, taste signals, benchmarks
```

Nothing phones home. All intelligence runs locally via Python. No subscriptions. No accounts.

---

## ⚙️ Requirements

- **Claude Code** (claude.ai/code)
- **Python 3.8+**
- **Git 2.20+**
- **Bash** (macOS, Linux, Windows Git Bash, WSL2)

Optional: GitHub MCP (auto-PR in `/ship`), `gitleaks` (enhanced secret scanning)

---

## 🗺️ Roadmap

- **v4.2** - Parallel `/review` subprocess harness (45s instead of 4min)
- **v4.3** - Optional sentence-transformers for 85% semantic similarity
- **v5.0** - Team intelligence: shared brain, averaged taste profiles
- **v5.1** - CI/CD: APEX pre-flight as GitHub Actions gate on every PR

---

## 📄 License

MIT: use it, modify it, build on it.

---

<div align="center">

**Built by [DevvNirvana](https://github.com/DevvNirvana)**

If APEX saves you time, a ⭐ helps other developers find it.

</div>
