<div align="center">

# APEX — AI Engineering OS

**The most advanced Claude Code engineering framework. Production-grade. Research-backed. Self-improving.**

[![Version](https://img.shields.io/badge/version-7.0.0-blue?style=flat-square)](https://github.com/DevvNirvana/claude-code-apex/releases)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-required-orange?style=flat-square)](https://code.claude.com)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Last Updated](https://img.shields.io/badge/updated-May%202026-brightgreen?style=flat-square)]()

*"Not just prompts. An operating system for AI-assisted engineering."*

</div>

---

## What Is APEX?

APEX transforms Claude Code from a chat interface into a structured engineering OS. It gives Claude persistent memory, self-enforcing rules, proactive intelligence, crash recovery, token-aware routing, a live terminal statusline, voice narration, and a cognitive context engine — without changing how you work.

You still type commands. Claude still writes code. But now it **remembers** your project, **enforces** your standards, **warns** you before wasting tokens, **recovers** automatically if it crashes, and **speaks** your responses aloud if you want it to.

**Named whatever you want.** APEX can be JARVIS, ALFRED, SAMANTHA, HAL, MU-TH-UR, or anything you invent. One config file changes every banner, greeting, color, spinner, and identity line across the entire system.

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

### 🧬 Cognitive Memory (v7 NEW)
| Feature | What It Does |
|---|---|
| **Context Engine** | Extracts intent from every prompt, ranks and assembles relevant context, injects into CLAUDE.md automatically. |
| **Code Index** | AST-based symbol indexer for Python, JS, and TS. Fuzzy search across your codebase. Updates on every session start. |
| **Context Guard** | Monitors token pressure in real-time. Warns at 60%, condenses at 80%, forces `/compact` at 95%. |
| **Session Archive** | End-of-session hook writes a structured summary to `.claude/brain/sessions/`. Every session is a searchable record. |

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
| **Hooks Generator** | Converts brain constraints into Claude Code hooks. `settings.json` + hook scripts auto-generated. |
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
| **Custom Naming** | Name your APEX anything: JARVIS, ALFRED, NOVA. One config drives every banner, greeting, spinner, and color. |
| **Universe Presets** | 5 lore-accurate presets: JARVIS, SAMANTHA, ALFRED, HAL, MU-TH-UR. Each has a matched TTS voice, color scheme, and spinner verbs. |
| **Theme Engine** | 8 full Claude Code themes with lore-accurate accents. Custom hex themes on demand. |
| **Statusline** | Live PostToolUse hook shows token count, cost, tool name, and duration in your terminal after every action. |

### 🔊 Voice Module (BETA)
| Feature | What It Does |
|---|---|
| **Kokoro-82M** | Local TTS, 210× realtime on GPU. No API keys. No internet. Instant. |
| **F5-TTS** | Zero-shot voice cloning from a 15-30s WAV sample. Drop `.claude/voices/<persona>.wav` to clone any voice. |
| **Persona Voices** | Each preset has a matched voice: JARVIS=British male, SAMANTHA=American female, HAL=deep American male. |
| **Non-Blocking** | `speak()` always returns immediately. TTS generation and playback run in a background thread. Terminal never stalls. |

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

## Intelligence Modules (25)

| Module | Purpose |
|---|---|
| `apex_identity.py` | Custom naming, persona presets, spinner verbs, greeting, banner engine |
| `smart_router.py` | Token tier classification before every command |
| `crash_guard.py` | Atomic checkpoints + crash detection |
| `update_checker.py` | Auto-update notifications (24h cache) |
| `token_intelligence.py` | Pre-flight token reports + budget enforcement |
| `skills_manager.py` | Skills lazy loading (91% startup reduction) |
| `hooks_generator.py` | Converts brain constraints → Claude Code hooks + settings.json |
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
| `context_engine.py` | Intent extraction, semantic context ranking, CLAUDE.md assembly *(v7)* |
| `code_index.py` | AST symbol indexer, fuzzy codebase search *(v7)* |
| `context_guard.py` | Real-time token pressure monitor *(v7)* |
| `theme_generator.py` | 8 lore-accurate themes + custom hex theme creation *(v7)* |
| `apex_statusline.py` | Live terminal statusline via PostToolUse hook *(v7)* |
| `apex_voice.py` | Kokoro-82M + F5-TTS voice narration, persona-matched voices *(v7 BETA)* |

---

## Quick Start (5 minutes)

### Fresh Install

```bash
# 1. Clone or download
git clone https://github.com/DevvNirvana/claude-code-apex.git

# 2. Navigate to your project
cd your-project

# 3. Install
bash ~/claude-code-apex/scripts/install.sh

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
bash ~/claude-code-apex/scripts/install.sh --update

# Regenerate hooks (picks up new v7 hooks)
python3 .claude/intelligence/hooks_generator.py --force

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

| Tier | Tokens | Cost | When Used |
|---|---|---|---|
| MICRO | ~300 | $0.001 | Lookups, simple questions, typos |
| LIGHT | ~900 | $0.003 | Quick fixes, explanations, status checks |
| STANDARD | ~2,800 | $0.008 | Debug, test, refactor, optimize |
| FULL | ~5,500 | $0.017 | Plan, design, review, execute, ship |

*Based on Claude Sonnet 4.6 pricing as of May 2026.*

---

## Universe Presets

| Preset | Name | Accent | Voice | Personality |
|---|---|---|---|---|
| `jarvis` | JARVIS | Cyan `#22d3ee` | British male (George) | Precise, formal, witty |
| `samantha` | SAMANTHA | Rose `#fb7185` | American female (Sky) | Warm, intuitive, curious |
| `alfred` | ALFRED | Slate `#f1f5f9` | British male (Lewis) | Understated, reliable, dry |
| `hal` | HAL | Red `#ef4444` | Deep American male (Adam) | Calm, clinical, unsettling |
| `mother` | MU-TH-UR | Neon `#39ff14` | American female (Nicole) | Terse, encrypted, cold |

Apply a preset:
```bash
python3 .claude/intelligence/apex_identity.py setup
# Choose a preset, or customize from scratch
```

---

## Architecture

```
.claude/
├── commands/          20 lazy-loaded Skills (YAML frontmatter)
├── intelligence/      25 Python modules (the engine)
├── hooks/             Auto-generated enforcement scripts
│   ├── session-start.sh        Re-injects constraints after compaction
│   ├── crash-checkpoint.sh     Atomic checkpoint before every edit
│   ├── inject-reference.sh     Lazy reference injection (UserPromptSubmit)
│   ├── session-pollution.sh    Warns at turn 15/25
│   ├── check-secrets.sh        Blocks hardcoded credentials
│   ├── protect-main.sh         Blocks direct push to main
│   ├── session-end.sh          Archives session summary on stop
│   ├── apex-statusline.sh      Live token/cost statusline (PostToolUse)
│   └── apex-voice.sh           Response narration hook (Stop, BETA)
├── brain/             facts.jsonl — persists across sessions
│   └── sessions/      Archived session summaries (v7)
├── memory/            trajectories/, taste, evaluations
├── checkpoints/       Crash recovery state
├── references/        23 lazy-loaded reference docs
├── skills/            Auto-generated from commands
├── themes/            Installed Claude Code theme files
├── voices/            TTS voice samples (<persona>.wav for F5-TTS)
└── config/            Stack profile, budget, version
```

---

## What Gets Preserved on Upgrade

```
PRESERVED (your data — never touched):     REPLACED (system files — safe to overwrite):
  .claude/brain/facts.jsonl                  .claude/commands/
  .claude/brain/sessions/                    .claude/intelligence/
  .claude/memory/trajectories/               .claude/references/
  .claude/memory/taste_profile.json          .claude/hooks/
  .claude/memory/evaluations.jsonl           .claude/config/
  .claude/identity.json                      .claude/themes/
  .claude/voices/                            scripts/install.sh
  CLAUDE.md
  docs/
```

---

## Comparison

| Feature | Vanilla Claude Code | APEX v6 | APEX v7 |
|---|---|---|---|
| Memory across sessions | ❌ | ✅ Brain | ✅ Brain + Sessions |
| Rule enforcement | 60% | 90%+ hooks | 90%+ hooks |
| Token visibility | ❌ | ✅ Pre-flight | ✅ Pre-flight + Statusline |
| Crash recovery | Fragile | ✅ Atomic | ✅ Atomic |
| Context awareness | ❌ | ❌ | ✅ Intent engine |
| Code search | Manual | Manual | ✅ AST index |
| Token pressure alerts | ❌ | ❌ | ✅ Context Guard |
| Custom themes | ❌ | ❌ | ✅ 8 themes + custom hex |
| Voice narration | ❌ | ❌ | ✅ BETA |
| Custom identity | ❌ | ✅ | ✅ + 5 universe presets |

---

## Changelog

### v7.0.0 — May 2026
- **NEW:** Cognitive Memory — Context Engine, Code Index, Context Guard
- **NEW:** Session Archive — end-of-session summaries persisted to `.claude/brain/sessions/`
- **NEW:** Theme Engine — 8 lore-accurate Claude Code themes, custom hex theme creation
- **NEW:** APEX Statusline — live token/cost/tool telemetry in terminal after every action
- **NEW:** Voice Module (BETA) — Kokoro-82M local TTS + F5-TTS zero-shot cloning, persona-matched voices
- **NEW:** Universe Presets — JARVIS, SAMANTHA, ALFRED, HAL, MU-TH-UR with matched colors/voices/spinners
- **FIX:** `get_identity()` deep-merge bug — partial voice configs no longer wipe defaults
- **FIX:** JARVIS theme now correctly applies cyan theme (was falling back to default dark)

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

### v3.x — February 2026
- Project Brain — persistent fact store.
- Trajectory Store — experience replay.
- Taste Memory — preference learning.

### v2.x — January 2026
- Token Tracker — cost tracking and DORA metrics.
- Evaluator — self-scoring quality engine.
- Benchmark — statistical consistency.

### v1.x — December 2025
- Initial release. Commands, references, hooks skeleton.

---

## License

MIT — Use it, fork it, build on it.

---

<div align="center">

**Built on research. Designed for engineers who ship.**

[GitHub](https://github.com/DevvNirvana/claude-code-apex) · [Releases](https://github.com/DevvNirvana/claude-code-apex/releases) · [Issues](https://github.com/DevvNirvana/claude-code-apex/issues)

</div>
