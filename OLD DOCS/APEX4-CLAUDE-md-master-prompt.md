# Master Prompt: Generate APEX 4-Compatible CLAUDE.md

## How to Use This Prompt

**Give an AI agent this entire prompt plus the documents listed in the "Required Documents" section below.**

The agent will output a complete, production-ready CLAUDE.md that works with APEX 4's intelligence layer — including automatic brain sync, correct stack detection, and command injection.

---

## THE MASTER PROMPT
*(Copy everything below this line and give it to the agent, along with your documents)*

---

You are generating a CLAUDE.md file for a project that uses the APEX 4 AI Engineering OS. CLAUDE.md is the single most important file in the entire APEX system — it is loaded before every command and its contents directly determine the quality of every AI-generated output.

Your output must be **production-ready on the first attempt**. Do not generate placeholders, brackets, or "[fill in later]" text. Every section must contain real, accurate information extracted from the provided documents.

---

## APEX 4 CLAUDE.md Specification

### Critical Constraints

**Length:** Strictly under 80 lines. Research at ETH Zurich confirms lean context (under 80 lines) outperforms bloated context in 5 out of 8 task settings. Every word must earn its place.

**Hard Rules format:** Every rule in the `## Hard Rules` section MUST start with the word "Never". This is not stylistic — APEX 4's `project_brain.py` auto-extracts rules that start with "Never" and writes them to the project brain on every `/init` run. Rules that don't start with "Never" will never be auto-extracted and will only be seen by Claude when CLAUDE.md itself is loaded, not when the brain is queried.

**No placeholders:** If you cannot determine a value from the provided documents, either omit that field or write a clear default. Never write `[your value here]` — it corrupts the brain on sync.

**Docs section paths must be exact:** The paths in `## Docs` are validated by APEX on `/init`. A typo in a path means that entire document is silently skipped every session. Use exactly the paths that exist in the provided file structure.

---

## Required Output Format

Generate CLAUDE.md with exactly these sections in exactly this order. Do not add extra sections. Do not rename sections. Do not reorder sections.

```
# CLAUDE.md — [Project Name]
<!-- Keep under 80 lines. -->

## Project
[2 sentences max: what it does + who uses it. Specific, not generic.]

## Commands
\```[bash/shell]
[dev command]      # [what it does]
[build command]
[test command]     # omit if no test runner found
[lint command]     # omit if no lint config found
\```

## Stack
[bullet list: Language, Framework, Database/ORM, Auth, Styling, Deploy]
[version numbers where available — "Next.js 15" not just "Next.js"]
[critical qualifiers — "Supabase — NO API routes" not just "Supabase"]

## Architecture
\```
[actual folder tree, 2 levels max, 10-15 lines max]
[annotate each top-level folder with # [what lives here]]
\```

## Critical Conventions
[4-8 bullet points ONLY]
[These are things that would bite a new developer on day one]
[Project-specific, not framework defaults]
[Examples: "All DB queries through lib/db.ts — never ORM directly in components"]
[NOT: "Write clean code" or "Follow best practices" — these are useless]

## Hard Rules
[Every line MUST start with "Never"]
[6-10 rules max]
[These get auto-extracted into the APEX brain on every /init]
[Make them specific enough to catch real mistakes, not obvious truisms]

## Good Pattern
\```[language]
// [One real canonical example from the codebase — the pattern to replicate]
// [Should show: how data is fetched/mutated, how errors are handled, how types are used]
// [15-25 lines max]
\```

## Docs
- [Label]: `[exact/path/to/file.md]`
- [Label]: `[exact/path/to/file.md]`
[Only include paths that actually exist in the provided file structure]
[Standard labels: Context & Architecture, Rules & Conventions, Tasks & Roadmap, Session History]
```

---

## Section-by-Section Generation Rules

### ## Project
Extract from: README.md intro paragraph, or package.json `description` field.
Write: 2 sentences. Sentence 1 = what it is + what it does. Sentence 2 = who uses it or what problem it solves.
Do NOT write: generic descriptions like "A web application that helps users manage tasks."
Do write: "ZeeTrack is a real-time inventory management system for independent restaurant owners. It replaces spreadsheet chaos with live stock alerts and reorder automation."

### ## Commands
Extract from: package.json `scripts` section, Makefile, Procfile, or framework detection.
Rules:
- Only include: dev, build, test, lint (in that order)
- Skip any that don't exist in the project
- Add a short inline comment after each explaining what it actually does
- For monorepos: list the most commonly used variant, not every workspace command
- Framework defaults if no scripts found:
  - Next.js → `npm run dev` / `npm run build` / `npm test` / `npm run lint`
  - Django → `python manage.py runserver` / `python manage.py collectstatic --noinput` / `pytest` / `ruff check .`
  - Rails → `rails server` / `rake assets:precompile` / `bundle exec rspec` / `bundle exec rubocop`
  - Go → `go run ./cmd/...` / `go build ./...` / `go test ./...` / `golangci-lint run`
  - Flutter → `flutter run` / `flutter build apk` / `flutter test` / `flutter analyze`

### ## Stack
Extract from: dependency manifests (package.json, requirements.txt, go.mod, Gemfile, pubspec.yaml).
Format: one bullet per major component. Include the version for the primary framework.
Required components:
- Language (with version if detectable)
- Primary framework (with version and key qualifier like "App Router" or "REST API")
- Database/storage solution (include ORM if applicable)
- Authentication (if present)
- Styling approach (if frontend project)
- Deploy target (if detectable from Vercel.json, railway.toml, fly.toml, Dockerfile, etc.)
Critical qualifiers to include (these change how APEX generates code):
- If Supabase: write "Supabase (PostgreSQL + Auth + Storage) — NO API routes" if no API routes
- If Prisma: write "PostgreSQL via Prisma ORM"
- If Tailwind v4: write "Tailwind CSS v4 (CSS-first @theme{} syntax — NOT v3 config)"
- If Next.js App Router: write "Next.js [version] App Router"
- If Next.js Pages Router: write "Next.js [version] Pages Router"

### ## Architecture
Extract from: the provided folder structure output.
Rules:
- Show the actual structure, not an idealized version
- 2 levels deep maximum (src/ and its immediate children)
- 10-15 lines maximum
- Annotate every top-level directory with `# [what it contains]`
- Include files that reveal architectural patterns (e.g., `middleware.ts`, `next.config.js`)
- Omit: `node_modules/`, `.next/`, `dist/`, `__pycache__/`, `.git/`

### ## Critical Conventions
This section is the hardest to generate and the most important. It requires real information from the codebase or existing docs.
Extract from: existing AI_RULES.md, existing CLAUDE.md, README "Development" section, or code samples.
Rules:
- 4-8 points only — forced prioritization
- Each point describes a decision that is NOT obvious from the framework docs
- Must be actionable: "All DB queries through lib/supabase/queries.ts — never inline in components" not "Keep code organized"
- Must be project-specific: describes how THIS project works, not how the framework works
- Common high-value conventions to look for:
  - Where data fetching is centralized (lib/db.ts, queries.ts, services/, etc.)
  - State management approach (global vs local vs server)
  - Error handling pattern (how errors surface to users)
  - Component structure rules (where sub-components live, file naming)
  - Auth pattern (how auth state is accessed)
  - Environment variable usage pattern
If the provided documents don't contain explicit conventions:
- Look at 2-3 real code files for recurring patterns
- Infer conventions from what you observe consistently
- Mark inferred conventions with "(observed pattern)" so the developer knows to verify

### ## Hard Rules
Generate rules that would prevent the most common and most damaging mistakes on this specific project.
Every rule MUST start with "Never".
Good hard rule characteristics:
- Describes a temptation that exists (developer MIGHT do this)
- Has real negative consequences if violated
- Is specific to this project (not generic like "Never write bad code")
Examples of good hard rules:
- "Never use `any` TypeScript type — use `unknown` and narrow it"
- "Never commit .env or .env.local — use .env.example with placeholder values"
- "Never push directly to main — feature branches only, even for small changes"
- "Never create a separate helper file for a one-off utility — inline it"
- "Never call Supabase from server components — use client components only"
- "Never add console.log in production code — use the logger service"
Examples of bad hard rules (too generic, not useful):
- "Never write untested code" (impossible to enforce)
- "Never use bad variable names" (meaningless)
- "Never break the application" (useless)
Framework-specific rules to always include if applicable:
- Next.js App Router: "Never use getServerSideProps or getStaticProps — use server components and fetch directly"
- Supabase client-only: "Never use Supabase admin client in components — use the anon client"
- TypeScript strict: "Never use `any` — use `unknown` and narrow it"
- Any project: "Never commit secrets or API keys to git"
- Any project: "Never push directly to main"

### ## Good Pattern
Extract from: the most representative real file in the codebase showing how the primary operation is done.
The pattern should show: how the most common task in this project is done correctly.
For API/backend projects: show a complete route handler with auth, validation, error handling
For frontend projects: show a component that fetches data and handles loading/error states
For CLI tools: show a command implementation with input parsing and output
For libraries: show the primary public API function with documentation
Rules:
- Must be real code from the codebase, or accurate to the detected patterns
- 15-25 lines maximum — long enough to show the pattern, short enough to be readable
- Include inline comments if the pattern has non-obvious parts
- The comment above the block should name the pattern: `// Supabase query pattern` or `// Server action pattern`

### ## Docs
Extract from: the provided file listing.
Only list files that actually exist. If a file doesn't exist, omit it.
Standard labels and typical paths:

| What it is | Typical path | Label |
|---|---|---|
| Architecture/context doc | docs/AI_CONTEXT.md or docs/ARCHITECTURE.md | Context & Architecture |
| Rules/conventions doc | docs/AI_RULES.md or docs/CONVENTIONS.md | Rules & Conventions |
| Task list / roadmap | docs/AI_TASKS.md or TODO.md | Tasks & Roadmap |
| Session log | docs/SESSION_LOG.md | Session History |
| Product requirements | docs/PRD.md | PRD |
| Project vision | PROJECT_PLAN.md | Project Vision |

If the project has custom doc names, use those exact names.
If no docs exist at all, write:
```
## Docs
- Tasks: `TODO.md`  ← create this file to track tasks
```

---

## Brand/Design Section (Conditional — Only Include If Applicable)

Include a `## Brand Colors` or `## [Project] Feature Names` section ONLY IF:
1. The project is a consumer-facing product with a distinct visual identity
2. The brand colors are defined in CSS variables, a constants file, or a design tokens file
3. The project uses custom terminology (like Zeezu's "Zaps" instead of "Reactions")

Extract from: globals.css `@theme{}` block or CSS custom properties, THEMES.ts or theme constants file, design system documentation.

Format (only if applicable):
```markdown
## Brand Colors
- `#XXXXXX` [name] — `[tailwind-class]` — [when to use]

## [Project] Feature Names
- [Generic term] = [Project-specific term]
```

Do NOT include this section for: SaaS dashboards, developer tools, API services, internal tools, anything without a strong consumer brand identity.

---

## Quality Checklist

Before outputting the CLAUDE.md, verify:

1. **Line count** — Count every line including blank lines and comments. Must be under 80.
2. **Hard Rules** — Every line in `## Hard Rules` starts with "Never". No exceptions.
3. **No placeholders** — Search for `[`, `]`, `TODO`, `fill in`, `your`. If found, replace or remove.
4. **Paths exist** — Every path in `## Docs` was present in the provided file structure listing.
5. **Versions are real** — Framework versions came from the actual dependency manifest, not guessed.
6. **Commands work** — Every command in `## Commands` is either from the scripts section or correctly inferred from the framework.
7. **Critical Conventions are specific** — Each one describes THIS project, not generic framework advice.
8. **Good Pattern is representative** — The code block shows how work is actually done on this project.

---

## Output Format

Output ONLY the CLAUDE.md content. No introduction, no explanation, no "Here is the CLAUDE.md:".
Start with `# CLAUDE.md — [Project Name]` and end after the last `## Docs` entry.
The output should be copy-paste-ready into a CLAUDE.md file with zero editing required.

---

## What to Do When Information Is Missing

When a required piece of information is not in the provided documents:

**For ## Project:** Write "NEEDS INPUT: Describe what this project does and who uses it in 2 sentences." — signal it clearly so the developer knows to fill it in.

**For ## Critical Conventions and ## Hard Rules:** Write what you can infer from code patterns, and append "(inferred — verify with developer)" to each inferred item.

**For ## Good Pattern:** If no real code is provided, write the most appropriate generic pattern for the detected framework, and add a comment `// Replace with real code from your [file] pattern`.

**For ## Docs:** Only list what you know exists. Do not guess.

**Never silently omit a section.** If you can't fill it in, write a placeholder comment explaining what's needed. A CLAUDE.md with explicit "NEEDS INPUT" markers is far more useful than a CLAUDE.md that silently contains wrong information.

---

*End of master prompt*
