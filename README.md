<div align="center">

# APEX — AI Engineering OS

**The most advanced Claude Code engineering framework. Production-grade. Research-backed. Self-improving.**

[![Version](https://img.shields.io/badge/version-6.0.0-blue?style=flat-square)](https://github.com/DevvNirvana/claude-code-apex/releases)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-required-orange?style=flat-square)](https://code.claude.com)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Last Updated](https://img.shields.io/badge/updated-May%202026-brightgreen?style=flat-square)]()

*"Not just prompts. An operating system for AI-assisted engineering."*

</div>

---

## What Is APEX?

APEX transforms Claude Code from a chat interface into a structured engineering OS. It gives Claude persistent memory, self-enforcing rules, proactive intelligence, crash recovery, and token-aware routing — without changing how you work.

You still type commands. Claude still writes code. But now it **remembers** your project, **enforces** your standards, **warns** you before wasting tokens, and **recovers** automatically if it crashes.

**Named whatever you want.** APEX can be JARVIS, ALFRED, NOVA, or anything else. One config file changes every banner, greeting, and identity across the entire system.

---

## Why It Exists

Claude Code without APEX is brilliant but amnesiac. Every session starts from scratch. Rules get forgotten after 10 messages. There's no token visibility. There's no crash recovery. There's no way to see if quality is degrading over time.

APEX fixes all of this. Permanently.

**Research foundations:**
- **ETH Zurich arXiv 2602.11988 (Feb 2026):** CLAUDE.md rules have ~60% compliance and vanish after context compaction. Hooks achieve ~90%+ compliance and survive compaction entirely.
- **ACE arXiv 2510.04618 (ICLR 2026):** Agents that reflect on failures and accumulate structured knowledge improve by +10.6% on benchmarks. APEX implements this via the ACE Reflector and brain delta updates.
- **Claude Code Skills spec:** Lazy-loaded skills reduce startup token overhead by 91% vs eager command loading.

---

## Feature Map

### 🧠 Persistent Intelligence
| Feature | What It Does |
|---|---|
| **Project Brain** | Stores constraints, patterns, decisions in `.claude/brain/facts.jsonl`. Persists across sessions. Confidence auto-adjusts based on usage. |
| **Trajectory Store** | Records what you shipped, what patterns worked, what failed. Future sessions read this before planning. |
| **ACE Reflector** | When something goes wrong and you fix it, auto-extracts the lesson as a `HOLD` trajectory. The system learns from failures. |
| **Taste Memory** | Learns your aesthetic and engineering preferences from correction patterns. |

### ⚡ Token Intelligence
| Feature | What It Does |
|---|---|
| **Smart Router** | Classifies every task into the minimum context tier needed. Simple lookups: ~300 tokens. Full planning: ~5,500 tokens. 56% average session reduction. |
| **Token Pre-flight** | Shows exact token breakdown before any command runs. You know the cost before you spend it. |
| **Budget Enforcement** | Hard blocks commands when daily budget would be exceeded. Configurable warn and halt thresholds. |
| **Skills Lazy Loading** | Commands only load when needed. 91% startup token reduction (22,276 → 1,900 tokens). |
| **Reference Injection** | 23 reference docs stay on disk. Only the relevant one fires per message via UserPromptSubmit hook. |

### 🔒 Enforcement (Not Just Suggestions)
| Feature | What It Does |
|---|---|
| **Hooks Generator** | Converts brain constraints into Claude Code hooks. `settings.json` + 5 hook scripts auto-generated. |
| **Secret Blocker** | PreToolUse hook blocks hardcoded API keys and tokens before any file write. |
| **Main Branch Guard** | PreToolUse hook blocks direct push to main/master. |
| **Session Start Re-injection** | Constraints re-injected after every context compaction. Rules survive long sessions. |
| **Session Pollution Detection** | Warns at turn 15, strong warns at turn 25. Prevents quality degradation from overly long sessions. |

### 🛡️ Crash Recovery
| Feature | What It Does |
|---|---|
| **Crash Guard** | Writes atomic checkpoint before every Write/Edit/Bash. Survives OOM kills. |
| **Session Registry** | Independent of Claude Code's session index. Survives sessions-index.json corruption. |
| **Auto-Detection** | `/init` detects crash state automatically. Surfaces git hash, files in flight, in-progress tasks. |
| **Resume Briefing** | Tells you exactly where you were, what changed, what to do next. |

### 🎯 Proactive Intelligence
| Feature | What It Does |
|---|---|
| **Proactive /status** | Cross-references brain, evaluator, tasks, budget. Surfaces anomalies before you ask. |
| **Quality Degradation Alert** | Flags when /review grades drop across sessions. |
| **Stale Task Detection** | Surfaces in-progress tasks that haven't moved in 3+ sessions. |
| **Brain Conflict Resolution** | Alerts on conflicting facts before you plan new features on bad assumptions. |

### 🎨 Identity & Personalization
| Feature | What It Does |
|---|---|
| **Custom Naming** | Name your APEX anything: JARVIS, ALFRED, NOVA. One config drives every banner. |
| **Per-Project Identity** | Each project can have a different name and personality. |
| **Color Schemes** | Cyan, green, yellow, magenta, blue — your terminal, your colors. |

### 🔄 Auto-Update
| Feature | What It Does |
|---|---|
| **Update Checker** | Checks GitHub releases once per 24h. Prompts if newer version available. |
| **Non-Blocking** | 3-second timeout. Never stalls your session if network is slow. |
| **Permission Required** | Never auto-installs. Always asks. You stay in control. |

---

## Commands (20)

| Command | Description | Token Tier |
|---|---|---|
| `/setup` | Zero-friction first-run. Auto-detects stack, generates CLAUDE.md, seeds brain. | FULL |
| `/init` | Session start. Crash detection, identity banner, token audit, brain sync. | LIGHT |
| `/status` | Proactive system dashboard. Surfaces anomalies without being asked. | LIGHT |
| `/ask` | Read-only codebase query. Minimal context. | MICRO/LIGHT |
| `/brainstorm` | Socratic requirements. Generates Decision Record before planning. | FULL |
| `/plan` | DAG-structured planning with trajectory injection. | FULL |
| `/execute` | Batched task execution with context boundary detection. | FULL |
| `/design` | Stack-adaptive UI with aesthetic direction phase. | FULL |
| `/spawn` | Parallel agents in isolated git worktrees. | FULL |
| `/test` | Framework-specific test generation with TDD enforcement. | STANDARD |
| `/debug` | Root cause analysis with brain constraint injection. | STANDARD |
| `/optimize` | Performance profiling and targeted fixes. | STANDARD |
| `/refactor` | Safe refactoring with impact analysis. | STANDARD |
| `/docs` | Documentation generation. | STANDARD |
| `/review` | Multi-perspective deep review against your AI_RULES.md. | FULL |
| `/ship` | 40-point pre-flight deployment checklist. | FULL |
| `/rollback` | Emergency rollback via worktree metadata. | LIGHT |
| `/compact` | Archive completed work and compress stale docs. | LIGHT |
| `/handoff` | Session context bridge. Creates <400 token briefing for next session. | LIGHT |
| `/optimize-context` | Full token audit + CLAUDE.md optimization. | LIGHT |

---

## Intelligence Modules (19)

| Module | Purpose |
|---|---|
| `smart_router.py` | Token tier classification before every command |
| `crash_guard.py` | Atomic checkpoints + crash detection |
| `apex_identity.py` | Custom naming and personalization engine |
| `update_checker.py` | Auto-update notifications (24h cache) |
| `token_intelligence.py` | Pre-flight token reports + budget enforcement |
| `skills_manager.py` | Skills lazy loading (91% startup reduction) |
| `hooks_generator.py` | Converts brain constraints → Claude Code hooks |
| `claude_md_optimizer.py` | Research-backed CLAUDE.md trimmer |
| `generate_claude_md.py` | Auto-generates CLAUDE.md from stack detection |
| `project_brain.py` | Persistent fact store with confidence delta updates |
| `trajectory_store.py` | Experience replay + ACE Reflector |
| `cache_manager.py` | Semantic plan cache with duplicate detection |
| `token_tracker.py` | Cost tracking, DORA metrics |
| `detect_stack.py` | 15+ frameworks, version-pinned detection |
| `evaluator.py` | Self-scoring quality engine |
| `taste_memory.py` | Developer preference learning |
| `benchmark.py` | Statistical consistency measurement |
| `design_system.py` | Design token extraction |
| `framework_lint.py` | Framework-specific lint rules |

---

## Quick Start (5 minutes)

### Fresh Install

```bash
# 1. Download and unzip (folder: claude-orchestrator-apex-v6/)
unzip ~/Downloads/claude-orchestrator-apex-v6.0-COMPLETE.zip

# 2. Navigate to your project
cd your-project

# 3. Install
bash ~/claude-orchestrator-apex-v6/install.sh

# 4. Name your APEX (optional but recommended)
python3 .claude/intelligence/apex_identity.py setup

# 5. Generate enforcement hooks
python3 .claude/intelligence/hooks_generator.py

# 6. Open Claude Code and run
/setup
```

### Upgrade from Any Previous Version

```bash
cd your-project

# Backup your intelligence data
mkdir -p .apex-backup
cp -r .claude/brain .claude/memory .apex-backup/
cp CLAUDE.md .apex-backup/

# Update system files only (brain + memory untouched)
bash ~/claude-orchestrator-apex-v6/install.sh --update

# Regenerate hooks (includes new crash-checkpoint + session-pollution)
python3 .claude/intelligence/hooks_generator.py --force

# Set your version
python3 .claude/intelligence/update_checker.py set 6.0.0

# Verify
python3 .claude/intelligence/token_intelligence.py audit
/init
```

---

## How Token Routing Works

Every command is classified before a single token loads:

```
User: "where is the auth code?"
→ Smart Router: MICRO tier (~300 tokens)
→ Skips: CLAUDE.md, brain, skill body, trajectories
→ Cost: ~$0.001

User: /plan "build the user authentication system"
→ Smart Router: FULL tier (~5,500 tokens)
→ Loads: Everything — CLAUDE.md, brain, trajectories, taste, skill body
→ Cost: ~$0.017
```

**Token tier breakdown:**

| Tier | Tokens | Cost | When Used |
|---|---|---|---|
| MICRO | ~300 | $0.001 | Lookups, simple questions, typos |
| LIGHT | ~900 | $0.003 | Quick fixes, explanations, status checks |
| STANDARD | ~2,800 | $0.008 | Debug, test, refactor, optimize |
| FULL | ~5,500 | $0.017 | Plan, design, review, execute, ship |

*Based on Claude Sonnet 4.6 pricing as of May 2026. Simple tasks stay simple.*

---

## How Crash Recovery Works

**Without APEX:** Claude Code crashes → `sessions-index.json` may be corrupted → `--resume` fails → you start from scratch.

**With APEX:**
1. `crash-checkpoint.sh` fires before every Write/Edit/Bash (PreToolUse hook)
2. Writes `.claude/checkpoints/last.json` atomically (survives OOM kill)
3. On next `/init`, `crash_guard.py detect` runs automatically
4. If crash detected, APEX surfaces:
   - What command was running
   - Which git hash and branch
   - Which files were being modified
   - Which tasks were in progress
   - The Claude Code session ID (if available for `--resume`)

---

## Configuring Your Budget

Edit `.claude/config/cache-config.json`:

```json
{
  "session_budget": {
    "soft_warn_usd": 3.00,
    "hard_halt_usd": 5.00
  }
}
```

`soft_warn_usd` — warns before the command but allows it.
`hard_halt_usd` — blocks the command entirely. Zero tokens spent.

---

## Naming Your APEX

```bash
python3 .claude/intelligence/apex_identity.py setup
```

Interactive wizard. Set name, tagline, greeting, color. Takes 30 seconds.

Or set directly:
```bash
python3 .claude/intelligence/apex_identity.py set name JARVIS
python3 .claude/intelligence/apex_identity.py set greeting "Ready, boss."
python3 .claude/intelligence/apex_identity.py set color_scheme cyan
```

Every banner, hook output, and CLAUDE.md identity line updates immediately.

---

## What Gets Preserved on Upgrade

```
PRESERVED (your data — never touched):     REPLACED (system files — safe to overwrite):
  .claude/brain/facts.jsonl                  .claude/commands/
  .claude/memory/trajectories/               .claude/intelligence/
  .claude/memory/taste_profile.json          .claude/references/
  .claude/memory/evaluations.jsonl           .claude/hooks/
  .claude/identity.json                      .claude/config/
  CLAUDE.md                                  install.sh
  docs/ (all your docs)                      README.md (this file)
```

---

## Comparison

| Feature | Vanilla Claude Code | APEX |
|---|---|---|
| Memory across sessions | ❌ | ✅ Persistent brain |
| Rule enforcement | 60% compliance | 90%+ via hooks |
| Token visibility | ❌ | ✅ Pre-flight every command |
| Crash recovery | Fragile | ✅ Atomic checkpoints |
| Simple task token cost | 5,500 tokens | 300 tokens (MICRO tier) |
| Custom identity | ❌ | ✅ Full personalization |
| Auto-updates | ❌ | ✅ Daily check, opt-in |
| Self-improving | ❌ | ✅ ACE Reflector + brain delta |
| Session pollution alerts | ❌ | ✅ Warns at turn 15/25 |

---

## Architecture

```
.claude/
├── commands/          20 lazy-loaded Skills (YAML frontmatter)
├── intelligence/      19 Python modules (the engine)
├── hooks/             Auto-generated enforcement scripts
│   ├── session-start.sh       Re-injects constraints after compaction
│   ├── crash-checkpoint.sh    Atomic checkpoint before every edit
│   ├── inject-reference.sh    Lazy reference injection (UserPromptSubmit)
│   ├── session-pollution.sh   Warns at turn 15/25
│   ├── check-secrets.sh       Blocks hardcoded credentials
│   ├── protect-main.sh        Blocks direct push to main
│   └── session-end.sh         Docs reminder + clean shutdown
├── brain/             facts.jsonl — persists across sessions
├── memory/            trajectories/, taste, evaluations
├── checkpoints/       Crash recovery state
├── references/        23 lazy-loaded reference docs
├── skills/            Auto-generated from commands
└── config/            Stack profile, budget, version
```

---

## Changelog

### v6.0.0 — May 10, 2026
- **NEW:** Smart Router — 4-tier token classification. 56% average session reduction.
- **NEW:** Crash Guard — atomic checkpoints, auto crash detection on `/init`.
- **NEW:** APEX Identity — custom naming (JARVIS, ALFRED, NOVA, anything).
- **NEW:** Auto-update checker — daily GitHub check, non-blocking, opt-in.
- **NEW:** Budget enforcement — hard block before tokens are spent.

### v5.0.0 — April 2026
- Skills lazy loading — 91% startup token reduction.
- UserPromptSubmit hook — reference injection (30,364 → 2,000 tokens).
- ACE Reflector — failure lessons auto-extracted.
- Brain delta updates — confidence auto-adjusts from usage.
- Session pollution detection — turn counter with warnings.
- `/handoff` command — session context bridge.

### v4.3.0 — March 2026
- Hooks generator — brain constraints → enforcement hooks.
- CLAUDE.md optimizer — removes arch trees, generic advice.
- Selective brain injection — 3-tier context loading.

---

## License

MIT — Use it, fork it, build on it.

---

<div align="center">

**Built on research. Designed for engineers who ship.**

[GitHub](https://github.com/DevvNirvana/claude-code-apex) · [Releases](https://github.com/DevvNirvana/claude-code-apex/releases) · [Issues](https://github.com/DevvNirvana/claude-code-apex/issues)

</div>
