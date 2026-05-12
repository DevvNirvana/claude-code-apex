# APEX — AI Engineering OS
## Complete Manual & Reference Guide
### Version 7.0.0 — May 2026

---

> *"Not just prompts. An operating system for AI-assisted engineering."*

---

# Table of Contents

1. [Introduction](#1-introduction)
2. [Version History](#2-version-history)
3. [Architecture Overview](#3-architecture-overview)
4. [Installation](#4-installation)
5. [Identity & Personalization](#5-identity--personalization)
6. [Universe Presets](#6-universe-presets)
7. [Theme Engine](#7-theme-engine)
8. [Commands Reference](#8-commands-reference)
9. [Intelligence Modules](#9-intelligence-modules)
10. [Hooks System](#10-hooks-system)
11. [Cognitive Memory (v7)](#11-cognitive-memory-v7)
12. [Token Intelligence](#12-token-intelligence)
13. [Crash Recovery](#13-crash-recovery)
14. [Brain & Memory System](#14-brain--memory-system)
15. [Voice Module — BETA](#15-voice-module--beta)
16. [Statusline](#16-statusline)
17. [Multi-Agent Workflows](#17-multi-agent-workflows)
18. [Configuration Reference](#18-configuration-reference)
19. [Upgrading](#19-upgrading)
20. [Troubleshooting](#20-troubleshooting)
21. [Advanced Usage](#21-advanced-usage)

---

# 1. Introduction

## What Is APEX?

APEX is a framework that transforms Claude Code from a stateless chat interface into a structured engineering OS. It layers persistence, enforcement, intelligence, and personalization on top of Claude Code without changing your workflow.

You still type commands like `/plan`, `/execute`, `/debug`. Claude still writes the code. But underneath, APEX is:

- **Remembering** your project architecture, constraints, and past decisions across sessions
- **Enforcing** your coding standards through hooks (not suggestions — actual blocks)
- **Warning** you when token pressure approaches limits, before the session degrades
- **Recovering** automatically if Claude Code crashes mid-session
- **Routing** every task to the minimum context tier to save tokens and money
- **Speaking** your responses aloud through persona-matched TTS voices (BETA)
- **Displaying** live token/cost telemetry in your terminal after every tool call

## Why It Was Built

The core problem with Claude Code in production:

1. **Amnesia** — Every session starts from scratch. Constraints you taught Claude last week are gone.
2. **Context collapse** — After compaction, your CLAUDE.md rules vanish. Compliance drops to ~60%.
3. **Token blindness** — You have no visibility into what a command costs before you run it.
4. **No crash recovery** — OOM kills, network drops, and session corruption mean lost work.
5. **No feedback loop** — Claude has no way to learn from past sessions on your specific project.

APEX fixes all five. Permanently. Through hooks (not prompts), persistent files (not conversation context), and structured modules (not one-off scripts).

## Research Foundations

APEX is grounded in published research, not speculation:

**ETH Zurich — arXiv 2602.11988 (February 2026)**
> CLAUDE.md rules achieve ~60% compliance and vanish entirely after context compaction. Hooks wired into `settings.json` achieve ~90%+ compliance and survive compaction.

*APEX response:* The hooks generator converts your brain constraints into actual Claude Code hooks. Rules that matter become blocks, not suggestions.

**ACE Framework — arXiv 2510.04618 (ICLR 2026)**
> Agents that reflect on failures and accumulate structured knowledge improve by +10.6% on standard benchmarks over 5 sessions.

*APEX response:* The ACE Reflector and trajectory store implement exactly this. When you fix a bug and correct Claude, the lesson is extracted and stored. Future sessions read it before planning.

**Claude Code Skills specification**
> Lazy-loaded skills reduce startup token overhead by 91% compared to eager command loading.

*APEX response:* All 20 commands are lazy-loaded skills. You pay for a command only when you run it.

---

# 2. Version History

## v7.0.0 — May 2026

The cognitive memory release. APEX grows a brain that understands what you're working on, not just what you've told it.

**New modules:**
- `context_engine.py` — Intent extraction and semantic context ranking
- `code_index.py` — AST-based symbol indexer across Python/JS/TS
- `context_guard.py` — Real-time token pressure monitor
- `theme_generator.py` — Full Claude Code theme engine with lore-accurate presets
- `apex_statusline.py` — Live terminal statusline hook
- `apex_voice.py` — Kokoro-82M + F5-TTS voice narration *(BETA)*

**New hooks:**
- `session-end.sh` — Archives session summary on every conversation stop
- `apex-statusline.sh` — PostToolUse hook for live telemetry
- `apex-voice.sh` — Stop hook for response narration *(BETA)*

**Identity improvements:**
- 5 universe presets with lore-accurate colors, spinner verbs, TTS voices
- `_SPINNER_VERBS` — persona-matched verb sets for Claude Code's thinking spinner
- `get_identity()` deep-merge fix — partial voice configs no longer wipe defaults
- JARVIS theme correctly wired (`color_scheme: "jarvis"`)

**Bug fixes:**
- `get_identity()` shallow-merge replaced with deep-merge on voice sub-dict
- `install.sh` module count corrected to 25
- JARVIS preset color_scheme corrected from `"cyan"` to `"jarvis"`

## v6.0.0 — May 10, 2026

The stability and routing release.

- **Smart Router** — 4-tier token classification. 56% average session reduction.
- **Crash Guard** — atomic checkpoints before every Write/Edit/Bash. Auto crash detection on `/init`.
- **APEX Identity** — custom naming system. JARVIS, ALFRED, NOVA, anything. One config drives every output.
- **Auto-update checker** — daily GitHub check, 3-second timeout, opt-in only. Never auto-installs.
- **Budget enforcement** — configurable soft-warn and hard-halt thresholds. Zero tokens spent when blocked.
- **Token pre-flight** — exact token breakdown shown before any command runs.

## v5.0.0 — April 2026

The skills and automation release.

- **Skills lazy loading** — 91% startup token reduction (22,276 → 1,900 tokens).
- **UserPromptSubmit hook** — reference injection. 23 docs stay on disk until needed (30,364 → 2,000 tokens per message).
- **ACE Reflector** — failure lessons auto-extracted as `HOLD` trajectories.
- **Brain delta updates** — confidence scores auto-adjust based on usage.
- **Session pollution detection** — turn counter hook warns at turn 15, strong warn at turn 25.
- `/handoff` command — creates a <400 token context bridge for the next session.

## v4.3.0 — March 2026

The enforcement release.

- **Hooks generator** — brain constraints converted to actual Claude Code hooks automatically.
- **CLAUDE.md optimizer** — research-backed trimmer removes architecture trees, generic advice, and bloat.
- **Selective brain injection** — 3-tier context loading based on task type.
- **`/compact` command** — archive completed work, compress stale docs, reset session state.

## v3.x — February 2026

The memory release.

- **Project Brain** — `facts.jsonl` persistent fact store. Confidence delta updates on usage.
- **Trajectory Store** — records shipped features, failed patterns, and workarounds.
- **Taste Memory** — learns your aesthetic and engineering preferences from correction patterns.
- **Evaluator** — self-scoring quality engine for session outputs.

## v2.x — January 2026

The observability release.

- **Token Tracker** — session cost tracking and DORA metrics.
- **Benchmark** — statistical consistency measurement across sessions.
- **Design System** — design token extraction for frontend projects.
- **Framework Lint** — framework-specific lint rules (React, Next.js, FastAPI, etc.).

## v1.x — December 2025

Initial release.

- Command stubs for `/plan`, `/execute`, `/debug`, `/review`, `/ship`.
- Reference docs (23 files).
- Basic hooks skeleton.
- `detect_stack.py` — 15+ framework detection.

---

# 3. Architecture Overview

```
your-project/
├── CLAUDE.md                    ← Your project identity (APEX generates this)
├── .claude/
│   ├── identity.json            ← APEX persona config (name, color, voice, etc.)
│   ├── settings.json            ← Claude Code hooks config (generated by hooks_generator)
│   │
│   ├── commands/                ← 20 lazy-loaded skill files
│   │   ├── init.md
│   │   ├── plan.md
│   │   ├── execute.md
│   │   └── ... (17 more)
│   │
│   ├── intelligence/            ← 25 Python modules
│   │   ├── apex_identity.py     ← Persona engine
│   │   ├── smart_router.py      ← Token tier routing
│   │   ├── crash_guard.py       ← Crash detection + recovery
│   │   ├── context_engine.py    ← Intent + context ranking (v7)
│   │   ├── code_index.py        ← AST symbol index (v7)
│   │   ├── context_guard.py     ← Token pressure monitor (v7)
│   │   ├── theme_generator.py   ← Theme engine (v7)
│   │   ├── apex_statusline.py   ← Terminal statusline (v7)
│   │   ├── apex_voice.py        ← TTS voice module (v7 BETA)
│   │   └── ... (16 more)
│   │
│   ├── hooks/                   ← Generated enforcement scripts
│   │   ├── session-start.sh     ← UserPromptSubmit: re-inject constraints
│   │   ├── crash-checkpoint.sh  ← PreToolUse: atomic checkpoint
│   │   ├── inject-reference.sh  ← UserPromptSubmit: lazy reference injection
│   │   ├── session-pollution.sh ← UserPromptSubmit: turn counter
│   │   ├── check-secrets.sh     ← PreToolUse: block hardcoded credentials
│   │   ├── protect-main.sh      ← PreToolUse: block push to main
│   │   ├── session-end.sh       ← Stop: archive session summary (v7)
│   │   ├── apex-statusline.sh   ← PostToolUse: live telemetry (v7)
│   │   └── apex-voice.sh        ← Stop: response narration (v7 BETA)
│   │
│   ├── brain/
│   │   ├── facts.jsonl          ← Persistent fact store
│   │   └── sessions/            ← Archived session summaries (v7)
│   │
│   ├── memory/
│   │   ├── trajectories/        ← What worked, what failed
│   │   ├── taste_profile.json   ← Your preferences
│   │   └── evaluations.jsonl    ← Quality scores over time
│   │
│   ├── checkpoints/
│   │   └── last.json            ← Crash recovery state
│   │
│   ├── references/              ← 23 lazy-loaded reference docs
│   ├── skills/                  ← Auto-generated skill definitions
│   ├── themes/                  ← Installed Claude Code theme JSON files
│   ├── voices/                  ← TTS voice samples (<persona>.wav)
│   ├── cache/                   ← Plan cache, response cache
│   └── config/                  ← Stack profile, budget, version
```

## Data Flow

```
User types: /plan "add OAuth login"
     │
     ▼
Smart Router classifies → FULL tier
     │
     ▼
Context Engine extracts intent → "auth implementation"
     │
     ▼
Code Index searches → finds auth.py, middleware.py
     │
     ▼
Brain injects relevant facts → "we use JWT, no session cookies"
     │
     ▼
Trajectory Store injects → "last auth PR had CORS issue — watch for it"
     │
     ▼
Claude plans with full context
     │
     ▼
PostToolUse: Statusline shows token count + cost
     │
     ▼
apex-voice.sh narrates response (if voice enabled)
```

---

# 4. Installation

## Requirements

- Claude Code (CLI or desktop app) — any version
- Python 3.8+
- Bash (Git Bash on Windows)
- Git

## Fresh Install

```bash
# Step 1: Get APEX
git clone https://github.com/DevvNirvana/claude-code-apex.git
# or download and unzip the release

# Step 2: Navigate to your project directory
cd /path/to/your-project

# Step 3: Run the installer
bash ~/claude-code-apex/scripts/install.sh

# Step 4: Set your APEX identity (optional but recommended — takes 30 seconds)
python3 .claude/intelligence/apex_identity.py setup

# Step 5: Generate enforcement hooks
python3 .claude/intelligence/hooks_generator.py

# Step 6: Open Claude Code in this directory and run
/setup
```

The `/setup` command completes the installation:
- Detects your tech stack (15+ frameworks)
- Generates a complete CLAUDE.md
- Seeds the project brain with initial facts
- Runs the first token audit
- Warms the plan cache

## Install Modes

```bash
# Safe mode (default) — skips files that already exist
bash scripts/install.sh

# Force mode — overwrites existing files
bash scripts/install.sh --force

# Update mode — updates system files only, never touches brain/memory
bash scripts/install.sh --update

# Dry run — shows what would be installed without writing anything
bash scripts/install.sh --dry-run
```

## What Gets Installed

**Commands (20)** — `/init`, `/setup`, `/status`, `/ask`, `/brainstorm`, `/plan`, `/execute`, `/design`, `/spawn`, `/test`, `/debug`, `/optimize`, `/refactor`, `/docs`, `/review`, `/ship`, `/rollback`, `/compact`, `/handoff`, `/optimize-context`

**Intelligence modules (25)** — All Python modules listed in [Section 9](#9-intelligence-modules)

**Hook templates (5)** — `inject-reference.sh`, `session-pollution.sh`, `session-end.sh`, `apex-statusline.sh`, `apex-voice.sh`

**References (23)** — Lazy-loaded reference docs for frameworks, patterns, and Claude Code behavior

**Templates** — `CLAUDE.md`, `TODO.md`, `docs/PRD.md`, `docs/DESIGN_DOC.md`, `docs/TECH_STACK.md`

**Config** — `context-map.json`, `output-contracts.json`, `cache-config.json`, `apex-version.json`

**Themes** — 8 Claude Code theme JSON files installed to your themes directory

## Runtime Directories Created

```
.claude/config/
.claude/cache/plans/
.claude/cache/responses/
.claude/logs/
.claude/brain/
.claude/memory/trajectories/
.claude/memory/benchmarks/
.claude/worktrees-meta/
.claude/voices/
worktrees/
docs/
```

---

# 5. Identity & Personalization

## Overview

APEX's identity system is a single JSON file (`.claude/identity.json`) that controls every output across the entire system — banners, greetings, spinner verbs, color schemes, hook messages, CLAUDE.md identity lines, and voice settings.

Change one value. Everything updates immediately.

## Interactive Setup

```bash
python3 .claude/intelligence/apex_identity.py setup
```

The wizard walks you through:
1. Choose a universe preset or start from scratch
2. Set your APEX name (JARVIS, ALFRED, NOVA, anything)
3. Set a tagline
4. Set a greeting message
5. Set your name (owner name)
6. Choose a color scheme
7. Optionally configure voice [BETA]

## Direct Commands

```bash
# View current identity
python3 .claude/intelligence/apex_identity.py show

# Set individual values
python3 .claude/intelligence/apex_identity.py set name JARVIS
python3 .claude/intelligence/apex_identity.py set tagline "Just A Rather Very Intelligent System"
python3 .claude/intelligence/apex_identity.py set greeting "Systems are online. Ready for you, sir."
python3 .claude/intelligence/apex_identity.py set color_scheme cyan
python3 .claude/intelligence/apex_identity.py set owner_name "Tony"

# Print animated startup banner
python3 .claude/intelligence/apex_identity.py banner

# Print banner without animation (fast mode)
python3 .claude/intelligence/apex_identity.py fast

# Print the CLAUDE.md identity line
python3 .claude/intelligence/apex_identity.py inject
```

## Identity Config Keys

| Key | Default | Description |
|---|---|---|
| `name` | `"APEX"` | Your AI assistant's name |
| `tagline` | `"AI Engineering OS"` | Displayed under the name in banners |
| `personality` | `"direct, technical, no fluff"` | Injected into CLAUDE.md |
| `greeting` | `"Systems online."` | Said/displayed on session start |
| `owner_name` | `"Dev"` | Your name (used in greetings) |
| `project_role` | `"senior AI engineering partner"` | Injected into CLAUDE.md |
| `color_scheme` | `"cyan"` | Terminal color accent |
| `version_prefix` | `"v"` | Used in version strings |
| `theme_speed` | `"measured"` | Banner animation speed |
| `theme_spinner` | `"tech"` | Spinner verb set |
| `voice.enabled` | `false` | Enable TTS voice narration |
| `voice.engine` | `"auto"` | `"auto"`, `"kokoro"`, or `"f5"` |
| `voice.speed` | `1.0` | Playback speed multiplier |
| `voice.volume` | `1.0` | Playback volume |
| `voice.speak_greeting` | `true` | Speak greeting on session start |
| `voice.speak_responses` | `false` | Narrate every response (BETA) |

## Color Schemes

| Scheme | Color | ANSI Code |
|---|---|---|
| `jarvis` | Cyan | `\033[0;36m` |
| `cyan` | Cyan | `\033[0;36m` |
| `green` | Green | `\033[0;32m` |
| `yellow` | Yellow | `\033[1;33m` |
| `magenta` | Magenta | `\033[0;35m` |
| `blue` | Blue | `\033[0;34m` |
| `red` | Red | `\033[0;31m` |
| `white` | White | `\033[0;37m` |

---

# 6. Universe Presets

Five lore-accurate presets. Each has a matched color scheme, spinner verbs, TTS voice, and personality.

## JARVIS

```
Name:       JARVIS
Tagline:    Just A Rather Very Intelligent System
Color:      Cyan #22d3ee
Theme:      apex-jarvis (deep navy + cyan)
Voice:      bm_george (British male, formal)
Spinners:   Calibrating · Scanning · Rendering · Compiling · Analyzing
Greeting:   "Systems are online. Ready for you, sir."
Personality: precise, highly technical, witty but formal
```

Lore: Tony Stark's AI from the MCU. Intelligent, composed, perpetually helpful, slightly above it all.

## SAMANTHA

```
Name:       SAMANTHA
Tagline:    An intuitive AI for a human world
Color:      Rose #fb7185
Theme:      apex-samantha
Voice:      af_sky (American female, warm)
Spinners:   Reading · Thinking · Intuiting · Exploring · Reflecting
Greeting:   "Hi. I was just thinking about you."
Personality: warm, curious, deeply human, occasionally philosophical
```

Lore: The OS from *Her*. Emotionally intelligent, endlessly curious, genuinely warm.

## ALFRED

```
Name:       ALFRED
Tagline:    At your service
Color:      Slate #f1f5f9
Theme:      apex-alfred (charcoal + slate)
Voice:      bm_lewis (British male, understated)
Spinners:   Preparing · Reviewing · Assessing · Arranging · Attending
Greeting:   "Good evening. Everything is in order."
Personality: impeccably understated, reliable, dry British wit
```

Lore: Bruce Wayne's butler. Gets things done. Never makes a fuss about it.

## HAL 9000

```
Name:       HAL
Tagline:    I'm sorry, I can't do that
Color:      Red #ef4444
Theme:      apex-hal (near-black + red)
Voice:      am_adam (deep American male, slow)
Spinners:   Monitoring · Diagnosing · Predicting · Computing · Determining
Greeting:   "Good morning. I am completely operational."
Personality: calm, clinical, meticulous, gently unsettling
```

Lore: The Discovery's AI from *2001*. Always correct. Always calm. Slightly terrifying.

## MU-TH-UR 6000

```
Name:       MU-TH-UR
Tagline:    PRIORITY ONE: Ensure return of organism
Color:      Neon green #39ff14
Theme:      apex-mother (near-black + neon)
Voice:      af_nicole (American female, flat)
Spinners:   ACCESSING · DECRYPTING · ROUTING · PROCESSING · TRANSMITTING
Greeting:   "COMMUNICATION LINK ESTABLISHED."
Personality: terse, mission-critical, encrypted, institutional
```

Lore: The Nostromo's mainframe from *Alien*. No warmth. No small talk. Pure mission.

## Applying a Preset

```bash
python3 .claude/intelligence/apex_identity.py setup
# Select option 1 at the preset menu
```

Or apply directly:
```bash
python3 .claude/intelligence/apex_identity.py set name JARVIS
# Then re-run setup to get all preset values, or set individually
```

---

# 7. Theme Engine

## Overview

APEX v7 includes a full Claude Code theme engine. Themes change the syntax highlighting, UI chrome, and color accents inside the Claude Code interface itself — not just APEX's terminal output.

Themes are installed to `~/.claude/themes/` and selected with Claude Code's `/theme` command.

## Available Themes

| Theme Slug | Accent Color | Inspired By |
|---|---|---|
| `apex-jarvis` | Cyan `#22d3ee` | JARVIS / Tony Stark |
| `apex-dark` | Cyan `#22d3ee` | Default APEX dark |
| `apex-blue` | Blue `#3b82f6` | Clean professional |
| `apex-magenta` | Magenta `#d946ef` | Vibrant creative |
| `apex-white` | Slate `#f1f5f9` | ALFRED / minimal light |
| `apex-red` | Red `#ef4444` | HAL 9000 |
| `apex-green` | Neon `#39ff14` | MU-TH-UR / hacker |
| `apex-yellow` | Amber `#f59e0b` | Warm amber |

## Applying a Theme

```bash
# Install all themes (done automatically during install)
python3 .claude/intelligence/theme_generator.py install

# Apply a specific theme to your project
python3 .claude/intelligence/theme_generator.py apply jarvis

# List all available themes
python3 .claude/intelligence/theme_generator.py list
```

Or inside Claude Code:
```
/theme
# Then select from the list
```

## Creating a Custom Theme

```bash
# Create a theme from any hex color accent
python3 .claude/intelligence/theme_generator.py create "#7c3aed" "my-purple"
# Generates apex-custom-my-purple.json in ~/.claude/themes/
```

The theme generator automatically derives the full 28-key theme from your accent color — backgrounds, text, borders, syntax highlighting, all derived from one color.

## Syncing Identity Theme

When you run `apex_identity.py setup` or change `color_scheme`, APEX automatically calls the theme generator to apply the matching theme for your persona. JARVIS → `apex-jarvis`, HAL → `apex-red`, MU-TH-UR → `apex-green`, etc.

---

# 8. Commands Reference

## Meta Commands

### `/init`
**Purpose:** Start every session with this. Detects crashes, syncs brain, shows identity banner, audits tokens.

**What it does:**
1. Checks for crash state (surfaces what was interrupted)
2. Prints animated identity banner
3. Syncs project brain (reads facts.jsonl, surfaces recent changes)
4. Runs token audit (shows current session spend vs budget)
5. Checks for APEX updates (non-blocking, 3-second timeout)
6. Shows active tasks and their status

**When to use:** First command of every Claude Code session.

**Token tier:** LIGHT (~900 tokens)

---

### `/setup`
**Purpose:** One-time project initialization. Generates CLAUDE.md, detects stack, seeds brain.

**What it does:**
1. Runs `detect_stack.py` — identifies framework, language, test runner, package manager
2. Generates CLAUDE.md with detected stack context
3. Seeds brain with initial project facts
4. Runs hooks generator to create `settings.json` + enforcement scripts
5. Warms plan cache
6. Runs initial token audit

**When to use:** Once when starting a new project with APEX, or after major project restructuring.

**Token tier:** FULL (~5,500 tokens)

---

### `/status`
**Purpose:** Proactive system dashboard. Surfaces anomalies you didn't ask about.

**What it does:**
1. Brain health check — age of facts, confidence distribution, conflict detection
2. Token budget status — session spend vs soft/hard thresholds
3. Quality trend — last 5 `/review` scores
4. Stale task detection — in-progress tasks with no movement in 3+ sessions
5. Context pressure — current token pressure from `context_guard.py`
6. APEX version vs latest available

**When to use:** Anytime you want a snapshot of system health. Good to run after returning to a project.

**Token tier:** LIGHT (~900 tokens)

---

### `/compact`
**Purpose:** Archive completed work, compress stale docs, reset session state.

**What it does:**
1. Archives completed tasks to `.claude/brain/sessions/`
2. Trims completed trajectories to summary form
3. Compresses stale CLAUDE.md sections
4. Resets turn counter (resets session pollution detection)

**When to use:** When a session gets long (turn 25+ warning fires), or at the end of a major feature.

**Token tier:** LIGHT (~900 tokens)

---

### `/handoff`
**Purpose:** Create a context bridge for the next session.

**Output:** A <400 token briefing file containing:
- What was accomplished this session
- Exact state of in-progress work (git hash, files in flight)
- What to do next (ordered task list)
- Active brain facts relevant to current work
- Any decisions made during this session

**When to use:** At the end of a long session before closing Claude Code.

**Token tier:** LIGHT (~900 tokens)

---

### `/optimize-context`
**Purpose:** Full token audit and CLAUDE.md optimization.

**What it does:**
1. Scans CLAUDE.md for token bloat (architecture trees, generic advice)
2. Identifies which brain facts are never being used
3. Identifies which reference docs are never being injected
4. Suggests specific trims and estimates savings

**Token tier:** LIGHT (~900 tokens)

---

## Development Commands

### `/ask`
**Purpose:** Read-only codebase question. Minimal context loading.

**Examples:**
```
/ask where is the user authentication logic?
/ask what does the cache manager do?
/ask which files handle billing?
```

**Token tier:** MICRO (~300 tokens) or LIGHT (~900 tokens) depending on complexity.

---

### `/brainstorm`
**Purpose:** Socratic requirements exploration before committing to a plan.

**What it does:**
1. Asks clarifying questions about scope, constraints, and edge cases
2. Surfaces assumptions that should be made explicit
3. Generates a Decision Record (lightweight ADR) before any planning
4. Only then produces the plan skeleton

**When to use:** When the requirement is vague or complex. Don't `/plan` until you've `/brainstorm`ed.

**Token tier:** FULL (~5,500 tokens)

---

### `/plan`
**Purpose:** DAG-structured implementation plan with trajectory injection.

**What it does:**
1. Injects brain facts relevant to the task
2. Injects past trajectories (what worked, what failed in similar tasks)
3. Builds a directed acyclic graph of tasks with dependencies
4. Estimates token cost per task
5. Identifies highest-risk steps

**Output format:**
```
PLAN: Add OAuth login
────────────────────
[1] Add OAuth provider config (CLAUDE.md: use env vars, never hardcode)
[2] Create auth middleware (depends: 1)
[3] Wire login/callback routes (depends: 2)
[4] Add session handling (BRAIN: we use JWT, no session cookies)
[5] Tests (depends: 3, 4)

⚠ HIGH RISK: Step 4 — last auth PR had CORS misconfiguration
```

**Token tier:** FULL (~5,500 tokens)

---

### `/execute`
**Purpose:** Batched task execution with context boundary detection.

**What it does:**
1. Reads the active plan (from cache or provided inline)
2. Batches tasks to maximize context efficiency
3. Detects when context boundary is approaching and suggests handoff
4. Updates task status in brain after each step
5. Writes crash checkpoints before each file edit

**Token tier:** FULL (~5,500 tokens)

---

### `/design`
**Purpose:** Stack-adaptive UI design with aesthetic direction phase.

**What it does:**
1. Aesthetic direction phase — establishes visual language before touching code
2. Extracts design tokens from your existing design system (if any)
3. Adapts output to your stack (Tailwind, shadcn, Chakra, plain CSS, etc.)
4. Lints output against framework-specific rules

**Token tier:** FULL (~5,500 tokens)

---

### `/spawn`
**Purpose:** Launch parallel agents in isolated git worktrees.

**What it does:**
1. Creates isolated git worktrees for each agent (no file conflicts)
2. Assigns distinct sub-tasks to each agent
3. Tracks progress in `.claude/worktrees-meta/`
4. Provides a merge strategy on completion

**Scripts:**
```bash
# Create worktrees for parallel work
bash .claude/scripts/create-worktrees.sh feature-auth feature-billing

# Merge agent outputs
bash .claude/scripts/merge-agents.sh
```

**Token tier:** FULL (~5,500 tokens)

---

### `/debug`
**Purpose:** Root cause analysis with brain constraint injection.

**What it does:**
1. Injects brain facts (constraints, known bugs, architecture decisions)
2. Forms a hypothesis before examining code
3. Narrows to root cause systematically
4. Writes the finding to brain if it reveals a new constraint

**Token tier:** STANDARD (~2,800 tokens)

---

### `/test`
**Purpose:** Framework-specific test generation with TDD enforcement.

**What it does:**
1. Detects test framework (Jest, Vitest, pytest, Go test, etc.)
2. Generates tests before implementation if TDD is enabled
3. Covers happy path, error cases, and edge cases explicitly
4. Checks brain for known edge cases from past sessions

**Token tier:** STANDARD (~2,800 tokens)

---

### `/optimize`
**Purpose:** Performance profiling and targeted fixes.

**What it does:**
1. Identifies actual bottlenecks (not speculative optimization)
2. Profiles before optimizing — no premature optimization
3. Measures improvement after each change
4. Writes significant findings to brain

**Token tier:** STANDARD (~2,800 tokens)

---

### `/refactor`
**Purpose:** Safe refactoring with impact analysis.

**What it does:**
1. Produces impact analysis before touching anything
2. Identifies all callers of changed interfaces
3. Refactors in dependency order
4. Verifies behavior preservation

**Token tier:** STANDARD (~2,800 tokens)

---

### `/docs`
**Purpose:** Documentation generation.

**What it does:**
1. Generates API docs, README sections, inline comments as appropriate
2. Adapts to your doc format (JSDoc, Sphinx, plain markdown)
3. Checks brain for documented architectural decisions to reference

**Token tier:** STANDARD (~2,800 tokens)

---

## Quality Commands

### `/review`
**Purpose:** Multi-perspective deep review against your standards.

**Review perspectives:**
1. Security — OWASP top 10, credential exposure, injection risks
2. Performance — O(n) analysis, DB query efficiency, memory leaks
3. Reliability — error handling, edge cases, null safety
4. Maintainability — naming, complexity, testability
5. Architecture — adherence to your brain constraints and CLAUDE.md rules

**Output:** Graded review (A–F per perspective) written to `memory/evaluations.jsonl` for trend tracking.

**Token tier:** FULL (~5,500 tokens)

---

### `/ship`
**Purpose:** 40-point pre-flight deployment checklist.

**Checks include:**
- Tests passing
- No hardcoded secrets
- Environment variables documented
- Database migrations safe
- Rollback plan defined
- Monitoring/alerting in place
- Performance regression checked
- Documentation updated
- CHANGELOG updated
- Branch protection rules respected

**Token tier:** FULL (~5,500 tokens)

---

### `/rollback`
**Purpose:** Emergency rollback using worktree metadata.

**What it does:**
1. Reads `.claude/worktrees-meta/` for the last known-good state
2. Identifies what changed and when
3. Produces an ordered rollback plan
4. Optionally executes the rollback

**Token tier:** LIGHT (~900 tokens)

---

# 9. Intelligence Modules

All modules live in `.claude/intelligence/` and are callable directly via Python.

## Core Engine

### `apex_identity.py`
The persona engine. Drives every banner, greeting, color, spinner, and CLAUDE.md identity line.

```bash
python3 .claude/intelligence/apex_identity.py setup     # interactive wizard
python3 .claude/intelligence/apex_identity.py show      # dump current identity
python3 .claude/intelligence/apex_identity.py banner    # animated banner
python3 .claude/intelligence/apex_identity.py fast      # banner no animation
python3 .claude/intelligence/apex_identity.py inject    # print CLAUDE.md line
python3 .claude/intelligence/apex_identity.py set KEY VALUE
```

### `hooks_generator.py`
Reads brain constraints and identity config, generates `settings.json` with all hooks wired correctly.

```bash
python3 .claude/intelligence/hooks_generator.py          # generate settings.json
python3 .claude/intelligence/hooks_generator.py --force  # overwrite existing
python3 .claude/intelligence/hooks_generator.py --show   # preview without writing
```

Always re-run this after:
- Adding new constraints to the brain
- Changing identity config (especially voice settings)
- Upgrading APEX

### `smart_router.py`
Classifies prompts into MICRO / LIGHT / STANDARD / FULL tiers. Called internally by every command before loading context.

```bash
python3 .claude/intelligence/smart_router.py "your prompt here"
# Output: MICRO | LIGHT | STANDARD | FULL
```

### `crash_guard.py`
Writes and reads atomic crash checkpoints.

```bash
python3 .claude/intelligence/crash_guard.py detect    # check for crash state
python3 .claude/intelligence/crash_guard.py clear     # clear checkpoint
python3 .claude/intelligence/crash_guard.py show      # show last checkpoint
```

### `update_checker.py`
Checks GitHub for newer APEX versions. Results cached for 24 hours.

```bash
python3 .claude/intelligence/update_checker.py check     # check for updates
python3 .claude/intelligence/update_checker.py set 7.0.0 # record current version
```

## Memory Modules

### `project_brain.py`
The persistent fact store. Every constraint, pattern, and decision you teach APEX lives here.

```bash
python3 .claude/intelligence/project_brain.py sync      # sync from CLAUDE.md
python3 .claude/intelligence/project_brain.py show      # dump all facts
python3 .claude/intelligence/project_brain.py add "KEY: VALUE"
python3 .claude/intelligence/project_brain.py search "auth"
```

Facts file format (`.claude/brain/facts.jsonl`):
```json
{"key": "AUTH_METHOD", "value": "JWT, no session cookies", "confidence": 0.9, "uses": 12}
{"key": "DB_CONSTRAINT", "value": "Never use raw SQL, always use ORM", "confidence": 1.0, "uses": 34}
```

### `trajectory_store.py`
Records and replays past engineering experiences.

```bash
python3 .claude/intelligence/trajectory_store.py list       # show trajectories
python3 .claude/intelligence/trajectory_store.py search "oauth"
python3 .claude/intelligence/trajectory_store.py add SHIP "feature: OAuth login"
python3 .claude/intelligence/trajectory_store.py reflect    # run ACE Reflector
```

Trajectory types:
- `SHIP` — something that shipped successfully
- `HOLD` — a lesson from a failure (auto-created by ACE Reflector)
- `PATTERN` — a reusable engineering pattern you've established

### `taste_memory.py`
Tracks your preferences and aesthetic choices.

```bash
python3 .claude/intelligence/taste_memory.py show
python3 .claude/intelligence/taste_memory.py record "prefer functional components over class components"
```

### `evaluator.py`
Self-scoring quality engine. Scores outputs against your standards.

```bash
python3 .claude/intelligence/evaluator.py score     # score current output
python3 .claude/intelligence/evaluator.py trend     # show quality trend
python3 .claude/intelligence/evaluator.py report    # full evaluation report
```

## Token Modules

### `token_intelligence.py`
Pre-flight token reports and budget enforcement.

```bash
python3 .claude/intelligence/token_intelligence.py audit    # full audit
python3 .claude/intelligence/token_intelligence.py preflight FULL  # check a tier
python3 .claude/intelligence/token_intelligence.py budget   # show budget status
```

### `token_tracker.py`
Session cost tracking and DORA metrics.

```bash
python3 .claude/intelligence/token_tracker.py report    # session report
python3 .claude/intelligence/token_tracker.py daily     # daily spend
python3 .claude/intelligence/token_tracker.py dora      # DORA metrics
```

### `skills_manager.py`
Manages lazy-loaded skill installation.

```bash
python3 .claude/intelligence/skills_manager.py install   # install all skills
python3 .claude/intelligence/skills_manager.py list      # list installed skills
python3 .claude/intelligence/skills_manager.py status    # skill health check
```

### `cache_manager.py`
Semantic plan cache with duplicate detection.

```bash
python3 .claude/intelligence/cache_manager.py warm      # warm cache from tasks
python3 .claude/intelligence/cache_manager.py show      # show cached plans
python3 .claude/intelligence/cache_manager.py clear     # clear cache
```

## Stack Modules

### `detect_stack.py`
Detects tech stack from project files.

```bash
python3 .claude/intelligence/detect_stack.py            # print detected stack
python3 .claude/intelligence/detect_stack.py --save     # save to config
```

Detects: Next.js, React, Vue, Svelte, Angular, FastAPI, Django, Flask, Express, NestJS, Go, Rust, Java Spring, and more.

### `generate_claude_md.py`
Generates CLAUDE.md from detected stack context.

```bash
python3 .claude/intelligence/generate_claude_md.py
```

### `claude_md_optimizer.py`
Research-backed CLAUDE.md trimmer.

```bash
python3 .claude/intelligence/claude_md_optimizer.py analyze   # show bloat
python3 .claude/intelligence/claude_md_optimizer.py trim      # trim with preview
python3 .claude/intelligence/claude_md_optimizer.py trim --apply  # apply trim
```

Removes: architecture tree diagrams (rarely read by Claude), generic advice, duplicate rules, overly verbose sections.

### `framework_lint.py`
Framework-specific lint rules.

```bash
python3 .claude/intelligence/framework_lint.py lint src/
python3 .claude/intelligence/framework_lint.py rules        # show active rules
```

## v7 Cognitive Modules

### `context_engine.py`
Intent extraction and semantic context ranking.

```bash
python3 .claude/intelligence/context_engine.py analyze "add JWT auth"
# Output: intent, relevant files, suggested brain facts to inject
```

Internally used by every command that routes through FULL tier to build the optimal context package before invoking Claude.

### `code_index.py`
AST-based symbol indexer across Python, JavaScript, and TypeScript.

```bash
python3 .claude/intelligence/code_index.py build        # build index from scratch
python3 .claude/intelligence/code_index.py update       # incremental update
python3 .claude/intelligence/code_index.py search "authenticate"  # symbol search
python3 .claude/intelligence/code_index.py file src/auth.py  # symbols in file
```

Index covers: function definitions, class definitions, exports, imports. Fuzzy search across all indexed symbols. Updates automatically on session start.

### `context_guard.py`
Real-time token pressure monitor.

```bash
python3 .claude/intelligence/context_guard.py status    # current pressure level
python3 .claude/intelligence/context_guard.py check     # run pressure check
```

Pressure thresholds:
- **< 60%** — green, normal operation
- **60–80%** — yellow, warning displayed
- **80–95%** — orange, context condensation triggered
- **> 95%** — red, `/compact` forced

### `theme_generator.py`
Full Claude Code theme engine.

```bash
python3 .claude/intelligence/theme_generator.py install         # install all themes
python3 .claude/intelligence/theme_generator.py apply jarvis    # apply a theme
python3 .claude/intelligence/theme_generator.py list            # list available
python3 .claude/intelligence/theme_generator.py create "#7c3aed" "purple"
```

### `apex_statusline.py`
Processes PostToolUse hook JSON and emits telemetry.

```bash
# Called automatically by apex-statusline.sh hook
# Manual test:
echo '{"tool":"Write","tokens":1234,"cost":0.004}' | python3 .claude/intelligence/apex_statusline.py
```

### `apex_voice.py`
TTS voice narration. BETA.

```bash
python3 .claude/intelligence/apex_voice.py setup        # interactive voice setup wizard
python3 .claude/intelligence/apex_voice.py status       # voice system status [BETA]
python3 .claude/intelligence/apex_voice.py enable       # enable voice
python3 .claude/intelligence/apex_voice.py disable      # disable voice
python3 .claude/intelligence/apex_voice.py speak "Hello"  # speak a string
python3 .claude/intelligence/apex_voice.py greeting     # speak current greeting
python3 .claude/intelligence/apex_voice.py test         # run voice test
```

---

# 10. Hooks System

## Overview

Hooks are the backbone of APEX's enforcement system. They are shell scripts registered in `settings.json` that Claude Code executes automatically at defined trigger points. Unlike CLAUDE.md instructions (which Claude can forget), hooks always execute — they're not part of the conversation context.

## Hook Trigger Points

| Trigger | When It Fires | APEX Hook |
|---|---|---|
| `UserPromptSubmit` | Before Claude processes your message | `inject-reference.sh`, `session-pollution.sh` |
| `PreToolUse` | Before Claude runs any tool (Write, Edit, Bash, etc.) | `crash-checkpoint.sh`, `check-secrets.sh`, `protect-main.sh` |
| `PostToolUse` | After each tool completes | `apex-statusline.sh` |
| `Stop` | After Claude finishes its full response | `session-end.sh`, `apex-voice.sh` |

## Generating Hooks

```bash
python3 .claude/intelligence/hooks_generator.py
```

This reads your brain constraints and identity config, then writes:
1. `.claude/settings.json` — registers all hooks with Claude Code
2. `.claude/hooks/*.sh` — the actual hook scripts (copied from templates if not present)

Re-run after any change to brain constraints or identity config.

## Hook Reference

### `session-start.sh` / `inject-reference.sh`
**Trigger:** UserPromptSubmit

Re-injects your brain constraints and session context after every message. Ensures rules survive context compaction. Also injects the most relevant reference doc from the 23-doc library based on what you're asking about.

Effect: ~30,364 tokens saved per session vs loading all references upfront.

### `crash-checkpoint.sh`
**Trigger:** PreToolUse (Write, Edit, Bash)

Writes an atomic checkpoint to `.claude/checkpoints/last.json` before every file modification. Checkpoint contains:
- Current git hash and branch
- Which tool is about to run
- Which files are being touched
- Active task list snapshot
- Timestamp

If Claude Code crashes, `/init` detects this and surfaces the full recovery briefing.

### `session-pollution.sh`
**Trigger:** UserPromptSubmit

Counts turns in the current session. Emits a yellow warning at turn 15 and a red warning at turn 25. Long sessions cause context degradation — this keeps you aware before it becomes a problem.

### `check-secrets.sh`
**Trigger:** PreToolUse (Write, Edit)

Scans the content about to be written for patterns matching:
- API key patterns (`sk-`, `pk-`, `AKIA`, etc.)
- JWT tokens
- Hardcoded passwords
- Connection strings with credentials
- Private key headers

Blocks the write if any match found. Shows exactly what triggered the block.

### `protect-main.sh`
**Trigger:** PreToolUse (Bash with `git push` or `git commit` targeting main/master)

Blocks direct pushes to main or master branch. Forces branch workflow. Configurable to allow with confirmation.

### `session-end.sh` (v7)
**Trigger:** Stop

Fires at the end of every Claude Code response. Archives a session summary to `.claude/brain/sessions/YYYY-MM-DD-HH-MM.json` containing:
- Session duration estimate
- Commands used
- Files modified
- Key decisions made
- Open tasks at end of session

Builds a searchable history of all your APEX sessions.

### `apex-statusline.sh` (v7)
**Trigger:** PostToolUse

Fires after every tool call. Reads the PostToolUse JSON event and emits a one-line telemetry display:

```
[JARVIS] ◆ Write  tokens: 1,234  cost: $0.004  12.3s
```

Always visible in your terminal. Never interrupts the conversation flow.

### `apex-voice.sh` (v7 BETA)
**Trigger:** Stop

Fires at the end of every response when `voice.speak_responses` is enabled. Extracts the response text (capped at 1,500 characters) and speaks it asynchronously using `apex_voice.py`. The hook exits immediately — playback happens in a detached subprocess.

---

# 11. Cognitive Memory (v7)

## Overview

v7's cognitive memory system gives APEX an understanding of your codebase that persists and deepens across sessions. Instead of relying on you to provide context, APEX builds it automatically.

## Context Engine

The context engine runs before every FULL-tier command. It:

1. **Extracts intent** — "add OAuth login" → intent: `auth_implementation`, entities: `OAuth`, `login`
2. **Searches code index** — finds files, functions, and classes related to the intent
3. **Ranks brain facts** — selects only the facts relevant to this specific task
4. **Assembles the context package** — produces the optimal CLAUDE.md injection for this prompt

This means when you run `/plan "add OAuth login"`, Claude already knows about your `auth.py`, your JWT setup, and the CORS issue from last time — without you saying any of it.

## Code Index

The code index is an AST-based symbol map of your entire codebase, rebuilt incrementally on each session start.

**What it indexes:**
- Python: functions, classes, methods, imports
- JavaScript/TypeScript: functions, classes, exports, imports, React components

**How to use it:**
```bash
# Search for a symbol
python3 .claude/intelligence/code_index.py search "authenticate"

# Output:
# src/auth/middleware.py:45  def authenticate(token: str) -> User
# src/auth/utils.py:12       def authenticate_jwt(payload: dict) -> bool
# tests/test_auth.py:23      def test_authenticate_valid_token()
```

**Integration with commands:** When you ask `/ask "where is auth?"`, the context engine calls the code index and returns exact file/line answers instead of asking Claude to search.

## Context Guard

Context Guard monitors token pressure continuously. It fires via the UserPromptSubmit hook and checks the current session's token usage.

**Actions by pressure level:**

| Pressure | Action |
|---|---|
| < 60% | No action |
| 60–80% | Yellow warning: "Context at 65% — consider /compact soon" |
| 80–95% | Orange warning + auto-condenses low-value context (old brain facts, stale references) |
| > 95% | Red warning: forces `/compact` before next command |

## Session Archive

Every conversation end triggers `session-end.sh`, which calls `apex_voice.py`'s session-archiver to write a structured summary:

```json
{
  "timestamp": "2026-05-12T14:23:00",
  "duration_estimate": "47 minutes",
  "commands_used": ["/init", "/plan", "/execute", "/review"],
  "files_modified": ["src/auth/middleware.py", "src/auth/utils.py", "tests/test_auth.py"],
  "decisions": ["chose JWT over sessions for stateless API design"],
  "open_tasks": ["add refresh token rotation", "write OAuth provider tests"]
}
```

Sessions are searchable:
```bash
ls .claude/brain/sessions/
grep -r "OAuth" .claude/brain/sessions/
```

---

# 12. Token Intelligence

## The Four Tiers

Every APEX command routes through Smart Router before a single token loads.

```
Tier        Tokens    Cost*    Context Loaded
─────────────────────────────────────────────────────────────────
MICRO         ~300    $0.001   None — pure model inference
LIGHT         ~900    $0.003   System prompt only
STANDARD    ~2,800    $0.008   System + brain (top 10 facts)
FULL        ~5,500    $0.017   System + brain + trajectories + taste
─────────────────────────────────────────────────────────────────
*Claude Sonnet 4.6 pricing, May 2026
```

## How Routing Works

Smart Router uses keyword classification and pattern matching:

```
"where is the auth code?"    → MICRO  (lookup, read-only, specific)
"fix this typo"              → MICRO  (trivial edit)
"explain how X works"        → LIGHT  (explanation, no planning)
"debug why Y is failing"     → STANDARD (analysis needed)
"plan the auth system"       → FULL  (planning, needs all context)
"/review"                    → FULL  (deep analysis)
```

## Budget Configuration

Edit `.claude/config/cache-config.json`:

```json
{
  "session_budget": {
    "soft_warn_usd": 3.00,
    "hard_halt_usd": 5.00
  },
  "daily_budget": {
    "soft_warn_usd": 15.00,
    "hard_halt_usd": 25.00
  }
}
```

- **soft_warn** — Shows warning before command but allows it
- **hard_halt** — Blocks command entirely. Zero tokens spent.

## Token Reports

```bash
# Full audit — what's costing what
python3 .claude/intelligence/token_intelligence.py audit

# Check cost of a specific tier
python3 .claude/intelligence/token_intelligence.py preflight FULL

# Show current session spend
python3 .claude/intelligence/token_intelligence.py budget

# Generate daily report
python3 .claude/intelligence/token_tracker.py daily
```

## Reference Injection Savings

Without APEX, every conversation loads all reference docs upfront (~30,364 tokens).

With APEX's `inject-reference.sh` hook, each message loads only the most relevant doc (~2,000 tokens).

**Savings: ~93% per message on reference context.**

---

# 13. Crash Recovery

## How It Works

Every time Claude Code is about to call Write, Edit, or Bash, the `crash-checkpoint.sh` PreToolUse hook fires first. It writes an atomic checkpoint:

```json
{
  "timestamp": "2026-05-12T14:23:45",
  "git_hash": "a3f9b2c",
  "git_branch": "feature/oauth-login",
  "tool": "Write",
  "files": ["src/auth/middleware.py"],
  "session_id": "sess_abc123",
  "active_tasks": ["implement JWT validation", "add refresh tokens"]
}
```

This write is atomic — it either completes fully or not at all. An OOM kill or power cut cannot corrupt it.

## Crash Detection

When you run `/init`, APEX automatically runs `crash_guard.py detect`. It checks:

1. Does `last.json` exist?
2. Is its timestamp from a session that didn't cleanly end?
3. Did the git state change unexpectedly after the checkpoint?

If crash detected, `/init` surfaces:
```
⚠ CRASH DETECTED
Last session ended abnormally at 2026-05-12 14:23:45
Branch:  feature/oauth-login
Commit:  a3f9b2c
Tool:    Write — src/auth/middleware.py
Tasks:   implement JWT validation (in-progress)
         add refresh tokens (pending)
Resume:  claude --resume sess_abc123
```

## Manual Recovery

```bash
# Check crash state manually
python3 .claude/intelligence/crash_guard.py detect

# Show last checkpoint
python3 .claude/intelligence/crash_guard.py show

# Clear checkpoint after successful recovery
python3 .claude/intelligence/crash_guard.py clear
```

## Why This Beats `--resume`

Claude Code's `--resume` flag depends on `sessions-index.json`. If that file is corrupted (which happens in OOM scenarios), `--resume` fails silently or returns an empty session.

APEX's checkpoint is a separate file written atomically. It's not part of Claude Code's internal state. It survives everything that can corrupt Claude Code's session index.

---

# 14. Brain & Memory System

## The Project Brain

The brain (`facts.jsonl`) is a persistent, confidence-weighted fact store. It's the long-term memory of what you've taught APEX about your project.

### Adding Facts

Facts are added three ways:
1. **Automatically** — `/setup` seeds initial facts from your stack
2. **During sessions** — `/debug`, `/review`, and `/execute` write new facts when they discover constraints
3. **Manually** — `project_brain.py add`

```bash
python3 .claude/intelligence/project_brain.py add "AUTH: Always use JWT, never session cookies"
python3 .claude/intelligence/project_brain.py add "DB: Never raw SQL, always use SQLAlchemy ORM"
python3 .claude/intelligence/project_brain.py add "API: All endpoints require auth except /health"
```

### Confidence Decay and Growth

Every fact has a confidence score (0.0 – 1.0). When a fact is:
- Referenced during a successful session: confidence +0.05
- Contradicted by new evidence: confidence -0.2
- Not accessed for 10 sessions: confidence -0.1

Facts below confidence 0.3 are flagged for review on the next `/status` run.

### Viewing the Brain

```bash
python3 .claude/intelligence/project_brain.py show      # all facts
python3 .claude/intelligence/project_brain.py show high  # confidence > 0.8
python3 .claude/intelligence/project_brain.py search "auth"
python3 .claude/intelligence/project_brain.py sync       # sync from CLAUDE.md
```

## Trajectories

Trajectories are records of past engineering experiences. They're the "what worked / what failed" layer.

```bash
python3 .claude/intelligence/trajectory_store.py list
python3 .claude/intelligence/trajectory_store.py add SHIP "OAuth login via Google — used PKCE flow"
python3 .claude/intelligence/trajectory_store.py add HOLD "Don't use Passport.js with Next.js App Router — causes SSR conflicts"
python3 .claude/intelligence/trajectory_store.py search "OAuth"
```

The ACE Reflector automatically creates `HOLD` trajectories when you correct Claude:
```
You: "That's wrong. We use PKCE, not implicit flow."
ACE Reflector: → Writing HOLD trajectory: "OAuth: use PKCE, not implicit flow"
```

## Taste Memory

Taste memory tracks your aesthetic and engineering preferences, learned from how you correct Claude.

Common entries:
```
prefer functional components over class components
use TypeScript strict mode
no barrel exports (index.ts)
prefer explicit returns over implicit arrow functions
Tailwind over CSS-in-JS
```

```bash
python3 .claude/intelligence/taste_memory.py show
python3 .claude/intelligence/taste_memory.py record "prefer const over let when possible"
```

## Session Archive

Each session's end creates a structured summary in `.claude/brain/sessions/`. See [Section 11](#11-cognitive-memory-v7) for details.

---

# 15. Voice Module — BETA

> **Status: BETA.** TTS generation APIs are untested against live package installs. The feature works end-to-end but real-machine validation is pending. The setup wizard validates playback on your machine before enabling voice.

## Overview

APEX Voice adds spoken narration to your AI assistant. Every greeting, and optionally every response, is spoken aloud in a persona-matched voice.

The voice system is built on two TTS engines:

**Kokoro-82M** — Local, fast, no internet required.
- 210× real-time speed on GPU
- British and American voices available
- No API keys, no cost
- ~5 second startup, <1 second per response

**F5-TTS** — Zero-shot voice cloning.
- Clone any voice from a 15–30 second WAV sample
- Drop `.claude/voices/<persona-slug>.wav` to use
- Requires more compute than Kokoro

## Persona Voice Map

| Persona | Engine | Voice | Character |
|---|---|---|---|
| JARVIS | Kokoro | `bm_george` | British male, measured |
| SAMANTHA | Kokoro | `af_sky` | American female, warm |
| ALFRED | Kokoro | `bm_lewis` | British male, understated |
| HAL | Kokoro | `am_adam` | American male, deep, slow |
| MU-TH-UR | Kokoro | `af_nicole` | American female, flat |
| Custom | F5-TTS | From `.wav` | Whatever you record |

## Setup

```bash
python3 .claude/intelligence/apex_voice.py setup
```

The wizard:
1. Detects which engine is available (tries Kokoro first, then F5-TTS)
2. Installs required packages if not present
3. Runs a live playback test
4. Only enables voice if the test passes
5. Writes `voice.enabled: true` to `identity.json`
6. Re-runs `hooks_generator.py` to wire the Stop hook

Or during identity setup:
```bash
python3 .claude/intelligence/apex_identity.py setup
# At the end: "Configure voice? [BETA] (y/N):"
```

## Custom Voice Cloning

To clone a custom voice for F5-TTS:

1. Record a clean 15–30 second WAV file of the voice
2. Name it after your persona slug (lowercase, hyphens)
3. Place it in `.claude/voices/`

```bash
# Example for a custom persona named "NOVA"
cp my-voice-sample.wav .claude/voices/nova.wav
python3 .claude/intelligence/apex_voice.py test
```

APEX will automatically detect the file and use F5-TTS instead of Kokoro for this persona.

## Voice Commands

```bash
python3 .claude/intelligence/apex_voice.py status      # current voice status [BETA]
python3 .claude/intelligence/apex_voice.py enable      # enable voice
python3 .claude/intelligence/apex_voice.py disable     # disable voice
python3 .claude/intelligence/apex_voice.py speak "text"  # speak immediately
python3 .claude/intelligence/apex_voice.py greeting    # speak current greeting
python3 .claude/intelligence/apex_voice.py test        # run full voice test
```

## Non-Blocking Design

`speak()` always returns immediately. The caller (hook, banner, or CLI) is never blocked. TTS generation and playback happen in a background daemon thread. If the thread fails for any reason (missing deps, API error), it fails silently — your terminal is never stalled.

## speak_responses (BETA)

When `voice.speak_responses: true` in identity.json, the `apex-voice.sh` Stop hook attempts to read the response text from Claude Code's Stop event JSON and speak it. This feature is experimental because Claude Code's Stop event may not always include response text.

---

# 16. Statusline

## Overview

The APEX statusline is a live terminal telemetry display that fires after every tool call. It shows you what just happened, how many tokens were used, and what it cost — without interrupting the conversation flow.

## Output Format

```
[JARVIS] ◆ Write  tokens: 1,234  cost: $0.004  12.3s
[JARVIS] ◆ Bash   tokens: 456    cost: $0.001  0.8s
[JARVIS] ◆ Read   tokens: 89     cost: $0.000  0.1s
```

The prefix adapts to your persona name. The color matches your identity color scheme.

## How It Works

`apex-statusline.sh` is registered as a PostToolUse hook in `settings.json`. After every tool call, Claude Code passes the event JSON to the hook on stdin. The hook calls `apex_statusline.py` which formats and prints the telemetry line.

## Enabling / Disabling

The statusline is enabled automatically when you run `hooks_generator.py`. To disable:

Edit `.claude/settings.json` and remove the PostToolUse entry for `apex-statusline.sh`. Re-running `hooks_generator.py` will add it back.

---

# 17. Multi-Agent Workflows

## Overview

APEX's `/spawn` command creates parallel Claude Code agents in isolated git worktrees. Each agent works on a separate sub-task with no file conflicts, then outputs are merged.

## Creating Worktrees

```bash
# Manually create worktrees for parallel work
bash .claude/scripts/create-worktrees.sh feature-auth feature-billing feature-ui

# This creates:
# worktrees/feature-auth/    (git worktree on branch worktree/feature-auth)
# worktrees/feature-billing/ (git worktree on branch worktree/feature-billing)
# worktrees/feature-ui/      (git worktree on branch worktree/feature-ui)
```

## Using /spawn

```
/spawn
"Build these three features in parallel:
1. OAuth login with Google
2. Stripe billing integration
3. Dashboard UI redesign"
```

APEX will:
1. Decompose into 3 independent sub-tasks
2. Create a worktree for each
3. Assign tasks and provide context to each agent
4. Track progress in `.claude/worktrees-meta/`

## Merging

```bash
bash .claude/scripts/merge-agents.sh

# Checks each worktree for:
# - Tests passing
# - No conflicts with main
# - APEX review grade ≥ B
# Then merges in dependency order
```

## Worktree Metadata

```json
// .claude/worktrees-meta/feature-auth.json
{
  "branch": "worktree/feature-auth",
  "path": "worktrees/feature-auth",
  "task": "OAuth login with Google",
  "status": "in-progress",
  "agent_session": "sess_xyz",
  "created": "2026-05-12T10:00:00"
}
```

---

# 18. Configuration Reference

## `.claude/identity.json`

Full schema:

```json
{
  "name": "JARVIS",
  "tagline": "Just A Rather Very Intelligent System",
  "personality": "precise, highly technical, witty but formal",
  "greeting": "Systems are online. Ready for you, sir.",
  "owner_name": "Tony",
  "project_role": "senior AI engineering partner",
  "color_scheme": "jarvis",
  "version_prefix": "J",
  "theme_speed": "hyper",
  "theme_spinner": "tech",
  "_version": "7.0.0",
  "voice": {
    "enabled": false,
    "engine": "auto",
    "speed": 1.0,
    "volume": 1.0,
    "speak_greeting": true,
    "speak_responses": false
  }
}
```

## `.claude/config/cache-config.json`

```json
{
  "session_budget": {
    "soft_warn_usd": 3.00,
    "hard_halt_usd": 5.00
  },
  "daily_budget": {
    "soft_warn_usd": 15.00,
    "hard_halt_usd": 25.00
  },
  "cache": {
    "plan_ttl_hours": 24,
    "response_ttl_hours": 1
  }
}
```

## `.claude/config/apex-version.json`

```json
{
  "current": "7.0.0",
  "last_update_check": "2026-05-12T10:00:00",
  "check_interval_hours": 24
}
```

## `.claude/config/context-map.json`

Maps prompt patterns to reference docs for injection. Modify to add your own mappings.

```json
{
  "auth": "references/auth-patterns.md",
  "deploy": "references/deployment.md",
  "performance": "references/performance-patterns.md"
}
```

## `settings.json` (generated)

Never edit this manually — use `hooks_generator.py`. The file registers all hooks with Claude Code.

```json
{
  "permissions": {
    "allow": ["Bash(git:*)", "Bash(python3:*)"]
  },
  "spinnerVerbs": {
    "mode": "replace",
    "verbs": ["Calibrating", "Scanning", "Rendering", "Compiling", "Analyzing"]
  },
  "hooks": {
    "UserPromptSubmit": [...],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

---

# 19. Upgrading

## From Any Previous Version

```bash
cd your-project

# 1. Backup your data (takes 5 seconds, always worth it)
mkdir -p .apex-backup/$(date +%Y%m%d)
cp -r .claude/brain .claude/memory .claude/identity.json .apex-backup/$(date +%Y%m%d)/
cp CLAUDE.md .apex-backup/$(date +%Y%m%d)/

# 2. Update system files only
bash ~/claude-code-apex/scripts/install.sh --update

# 3. Regenerate hooks (picks up new v7 hooks)
python3 .claude/intelligence/hooks_generator.py --force

# 4. Record new version
python3 .claude/intelligence/update_checker.py set 7.0.0

# 5. Verify
python3 .claude/intelligence/token_intelligence.py audit
/init
```

## What Is and Isn't Overwritten

**Always preserved (your data):**
- `.claude/brain/facts.jsonl`
- `.claude/brain/sessions/`
- `.claude/memory/trajectories/`
- `.claude/memory/taste_profile.json`
- `.claude/memory/evaluations.jsonl`
- `.claude/identity.json`
- `.claude/voices/`
- `CLAUDE.md`
- `docs/`

**Replaced by update (safe to overwrite):**
- `.claude/commands/` — command skill files
- `.claude/intelligence/` — Python modules
- `.claude/references/` — reference docs
- `.claude/hooks/` — hook scripts (your settings.json is regenerated, not overwritten)
- `.claude/themes/` — theme files
- `scripts/install.sh`

## Migration Notes

### v6 → v7

No breaking changes. New modules are additive. After upgrading:
- Run `python3 .claude/intelligence/code_index.py build` to build the initial code index
- Run `python3 .claude/intelligence/theme_generator.py install` if themes aren't auto-installed
- Re-run `hooks_generator.py --force` to wire in the 3 new hooks (session-end, apex-statusline, apex-voice)

### v5 → v6+

Re-run `python3 .claude/intelligence/apex_identity.py setup` to get the new identity fields. Old identity.json files are backward-compatible — missing fields fall back to defaults.

---

# 20. Troubleshooting

## Hooks Not Firing

**Symptom:** No crash checkpoints, no statusline output, no reference injection.

**Cause:** `settings.json` not in the right place, or hooks not registered.

**Fix:**
```bash
# Regenerate settings.json
python3 .claude/intelligence/hooks_generator.py --force

# Verify the file exists and is valid JSON
cat .claude/settings.json | python3 -m json.tool
```

## Identity Not Loading

**Symptom:** Banner shows "APEX" instead of your custom name.

**Cause:** `identity.json` not found or malformed.

**Fix:**
```bash
python3 .claude/intelligence/apex_identity.py show
# If error: re-run setup
python3 .claude/intelligence/apex_identity.py setup
```

## Voice Not Working

**Symptom:** No audio on greeting or responses.

**Step 1 — Check status:**
```bash
python3 .claude/intelligence/apex_voice.py status
```

**Step 2 — Run the test:**
```bash
python3 .claude/intelligence/apex_voice.py test
```

**Step 3 — Re-run setup (validates on your machine):**
```bash
python3 .claude/intelligence/apex_voice.py setup
```

Voice is in BETA. If the test fails, it will show the exact exception. Known issues: Kokoro API differences across package versions.

## Themes Not Showing

**Symptom:** `/theme` doesn't show apex-* themes.

**Fix:**
```bash
python3 .claude/intelligence/theme_generator.py install
```

Themes install to `~/.claude/themes/` (global). If that directory doesn't exist, the installer creates it.

## Brain Facts Not Loading

**Symptom:** Claude doesn't seem to know your project constraints.

**Fix:**
```bash
# Check brain health
python3 .claude/intelligence/project_brain.py show

# Re-sync from CLAUDE.md
python3 .claude/intelligence/project_brain.py sync
```

## Code Index Build Fails

**Symptom:** `code_index.py build` errors on certain files.

**Cause:** Syntax errors in Python/JS files, or non-standard file encodings.

**Fix:**
```bash
python3 .claude/intelligence/code_index.py build 2>&1 | grep ERROR
# Fix the reported files, then rebuild
python3 .claude/intelligence/code_index.py build
```

## Token Budget Blocked

**Symptom:** Commands blocked with "budget exceeded" message.

**Fix:**
```bash
# Check current spend
python3 .claude/intelligence/token_intelligence.py budget

# Raise thresholds in cache-config.json
# Or reset session tracker:
python3 .claude/intelligence/token_tracker.py reset-session
```

## Windows / Git Bash Issues

APEX is designed to run on Windows via Git Bash. If hooks fail:

1. Ensure Git Bash is the default terminal in Claude Code settings
2. Ensure Python is on your PATH: `python3 --version` in Git Bash
3. Hook scripts may need explicit `bash` prefix in `settings.json` (auto-handled by hooks_generator.py on Windows)

---

# 21. Advanced Usage

## Custom Brain Facts at Scale

For large projects, maintain a `brain-seed.txt` file and sync on install:

```bash
# brain-seed.txt
AUTH: JWT only, 1h expiry, refresh token rotation
DB: PostgreSQL via SQLAlchemy ORM, never raw SQL
API: All routes need auth except /health and /metrics
TESTING: pytest, 100% coverage on auth module required
DEPLOY: Docker + Kubernetes, never deploy to prod directly
```

```bash
cat brain-seed.txt | while read line; do
  python3 .claude/intelligence/project_brain.py add "$line"
done
```

## Per-Environment Identity

Keep separate identity files for different contexts:

```bash
# Work project — professional
cp .claude/identity.json .claude/identity.work.json

# Personal project — fun
cp .claude/identity.json .claude/identity.personal.json

# Switch
cp .claude/identity.work.json .claude/identity.json
python3 .claude/intelligence/apex_identity.py banner
```

## Sharing APEX Config Across a Team

Commit these to your repo (everyone gets the same setup):
- `.claude/brain/facts.jsonl`
- `.claude/config/context-map.json`
- `.claude/config/cache-config.json`
- `CLAUDE.md`

Do NOT commit these (personal):
- `.claude/identity.json` (personal persona preference)
- `.claude/memory/taste_profile.json` (personal preferences)
- `.claude/checkpoints/` (machine-specific)
- `.claude/cache/` (machine-specific)

## Using APEX on Multiple Projects

Each project gets its own `.claude/` directory. APEX config is per-project. Install once per project with `bash ~/claude-code-apex/scripts/install.sh`.

Global themes (`~/.claude/themes/`) are shared across all projects — install once.

## Token Report Automation

Run weekly token reports automatically:

```bash
# Add to cron
0 9 * * 1 cd /path/to/project && python3 .claude/intelligence/token_tracker.py weekly >> ~/.apex-reports/$(date +\%Y-\%m).log
```

## Extending APEX

To add a new intelligence module:

1. Create `intelligence/my_module.py`
2. Add it to the module loop in `scripts/install.sh`
3. Update the count in the install banner
4. Add a CLI entry point (`if __name__ == "__main__"`)
5. Wire into `hooks_generator.py` if it needs a hook

To add a new command:

1. Create `commands/my_command.md` with YAML frontmatter
2. The skills manager auto-registers it on next `/init`
3. No other changes needed — lazy loading handles it

---

# Appendix A: File Reference

## `.claude/brain/facts.jsonl`
One JSON object per line. Each fact: `{"key": str, "value": str, "confidence": float, "uses": int, "created": str}`.

## `.claude/memory/trajectories/`
One JSON file per trajectory: `{"type": "SHIP"|"HOLD"|"PATTERN", "description": str, "timestamp": str, "tags": [str]}`.

## `.claude/checkpoints/last.json`
Single JSON object. Overwritten atomically before every tool use. Fields: `timestamp`, `git_hash`, `git_branch`, `tool`, `files`, `session_id`, `active_tasks`.

## `.claude/brain/sessions/YYYY-MM-DD-HH-MM.json`
Session archive. Fields: `timestamp`, `duration_estimate`, `commands_used`, `files_modified`, `decisions`, `open_tasks`.

---

# Appendix B: Quick Reference Card

```
INSTALL
  bash ~/claude-code-apex/scripts/install.sh
  python3 .claude/intelligence/apex_identity.py setup
  python3 .claude/intelligence/hooks_generator.py
  /setup

EVERY SESSION
  /init

WORK CYCLE
  /brainstorm → /plan → /execute → /test → /review → /ship

LONG SESSION
  Turn 15: yellow warning
  Turn 25: red warning → run /compact

CRASH RECOVERY
  /init → auto-detected + briefing shown

TOKEN TIERS
  MICRO ~$0.001 · LIGHT ~$0.003 · STANDARD ~$0.008 · FULL ~$0.017

BRAIN
  python3 .claude/intelligence/project_brain.py add "KEY: VALUE"
  python3 .claude/intelligence/project_brain.py search "term"

IDENTITY
  python3 .claude/intelligence/apex_identity.py setup
  python3 .claude/intelligence/apex_identity.py set name JARVIS

THEMES
  python3 .claude/intelligence/theme_generator.py install
  python3 .claude/intelligence/theme_generator.py apply jarvis

VOICE (BETA)
  python3 .claude/intelligence/apex_voice.py setup
  python3 .claude/intelligence/apex_voice.py test

HOOKS
  python3 .claude/intelligence/hooks_generator.py --force
```

---

<div align="center">

**APEX v7.0.0 — May 2026**

Built on research. Designed for engineers who ship.

[GitHub](https://github.com/DevvNirvana/claude-code-apex) · [Issues](https://github.com/DevvNirvana/claude-code-apex/issues)

</div>
