# Documents to Collect Before Running the Master Prompt

**Purpose:** Feed these to the AI agent along with the master prompt.
The more complete this set, the better the CLAUDE.md output.

---

## Tier 1 — Always Required (85% quality without anything else)

Collect ALL of these. Without them the agent is guessing.

### 1. Dependency Manifest

The file that lists your project's dependencies and build scripts.

| Stack | File to copy |
|-------|-------------|
| Next.js / React / Vue / Node | `package.json` |
| Python (Django / FastAPI / Flask) | `requirements.txt` OR `pyproject.toml` |
| Ruby / Rails | `Gemfile` |
| Go | `go.mod` |
| Flutter / Dart | `pubspec.yaml` |
| PHP / Laravel | `composer.json` |

**How to get it:**
```bash
cat package.json         # JS/TS projects
cat requirements.txt     # Python projects
cat go.mod               # Go projects
```

Copy the full file contents. Don't summarize it.

---

### 2. Folder Structure

A 2-level deep tree of your project's source directories.

**How to get it:**
```bash
# macOS / Linux
find . -maxdepth 3 -type d \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/.next/*" \
  ! -path "*/dist/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/vendor/*" \
  ! -path "*/.claude/*" \
  | sort

# OR simpler (macOS/Linux with tree installed)
tree -L 2 -I "node_modules|.git|.next|dist|__pycache__|vendor"

# Windows Git Bash
find . -maxdepth 3 -type d \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  | sort
```

Copy the output. This is how the agent knows where your files actually live.

---

### 3. README.md

The top-level README. This gives the agent:
- Project description (2-sentence summary)
- Any setup instructions (build commands)
- Any architecture notes the developer wrote

```bash
cat README.md
```

If your README is very long (500+ lines), copy just the first 100 lines.

---

### 4. .env.example

Reveals what external services your project uses. This is critical for the Stack section.

```bash
cat .env.example
# OR if it's named differently:
cat .env.sample
cat .env.template
```

**Never copy your actual `.env` file.** `.env.example` only — it has placeholder values, not real secrets.

If no `.env.example` exists, run:
```bash
# List all environment variables referenced in code (not their values)
grep -rh "process.env\.\|os\.environ\.\|ENV\[" src/ --include="*.ts" --include="*.tsx" --include="*.py" 2>/dev/null | grep -oP "(process\.env\.|os\.environ\.get\(\"|ENV\[\")\K[A-Z_]+" | sort -u
```

---

### 5. One Real Code File

The single file that best shows "how we do things here." Pick the most representative file.

**Which file to pick:**
- Next.js/React: A page file that fetches data (`app/dashboard/page.tsx`)
- Django: A views.py file with a few real views
- Rails: An ActiveRecord model with validations and scopes
- Go: A handler file showing auth + DB + response pattern
- FastAPI: A router file with a few endpoints

```bash
# Example: show a key file
cat src/app/dashboard/page.tsx
```

This gives the agent the "Good Pattern" section — the canonical example of how work gets done on your project.

---

## Tier 2 — Strongly Recommended (gets to 95% quality)

Add these if they exist. They fill in the sections that can't be inferred.

### 6. Existing Rules / Conventions Doc

If you have any document that describes how the project should be coded.

Common names:
- `docs/AI_RULES.md`
- `docs/CONVENTIONS.md`
- `docs/ARCHITECTURE.md`
- `CONTRIBUTING.md`
- `.cursor_rules` or `.cursorrules`
- Any file with "rules", "conventions", "guidelines" in the name

```bash
cat docs/AI_RULES.md
# OR
cat CONTRIBUTING.md
```

This is the most valuable document for the Critical Conventions and Hard Rules sections.

### 7. Existing CLAUDE.md (if upgrading from older APEX)

If you already have a CLAUDE.md from a previous version, include it. The agent will preserve what's good and upgrade the format.

```bash
cat CLAUDE.md
```

### 8. Existing AI_CONTEXT.md or Architecture Doc

If you ran a context reconstruction super-prompt before, or have any doc that describes your architecture:

```bash
cat docs/AI_CONTEXT.md
# OR
cat docs/ARCHITECTURE.md
```

---

## Tier 3 — For Branded Consumer Apps Only

Only collect these if your project has a distinct visual identity with custom brand colors, a design system, or project-specific terminology.

Skip this tier entirely for: developer tools, APIs, SaaS dashboards, internal tools, CLIs.

### 9. CSS Variables / Design Tokens

```bash
# Look for brand colors in globals.css or similar
grep -n "color\|--color\|@theme\|brand\|primary\|secondary\|accent" src/app/globals.css | head -30
# OR
cat src/app/globals.css | head -80
```

### 10. Theme / Brand Constants File

```bash
# Find brand constants
find . -name "THEMES*" -o -name "theme*" -o -name "colors*" -o -name "brand*" \
  ! -path "*/node_modules/*" 2>/dev/null
# Then cat the most relevant one
```

### 11. Custom Terminology List

If your app uses custom names for generic features (like Zeezu's "Zaps" for reactions), write them out manually:

```
Generic → Project-specific
Likes → [your term]
Comments → [your term]
Feed → [your term]
Username → [your term]
```

---

## How to Prepare the Input Package

Once you have all your files, prepare them for the agent like this:

```
[MASTER PROMPT]

---

DOCUMENT 1: package.json
[paste full contents]

---

DOCUMENT 2: Folder Structure
[paste tree output]

---

DOCUMENT 3: README.md
[paste contents]

---

DOCUMENT 4: .env.example
[paste contents]

---

DOCUMENT 5: src/app/dashboard/page.tsx (representative code file)
[paste file contents]

---

DOCUMENT 6: docs/AI_RULES.md (if exists)
[paste contents]

---

[any Tier 3 documents if applicable]
```

---

## Quick Collection Script

Run this from your project root to gather everything in one shot:

```bash
#!/usr/bin/env bash
# Run from your project root
# Output goes to claude-md-context.txt — give this file to the agent

OUTPUT="claude-md-context.txt"
echo "# Context for CLAUDE.md generation" > $OUTPUT
echo "# Generated: $(date)" >> $OUTPUT
echo "" >> $OUTPUT

# Package manifest
for f in package.json requirements.txt pyproject.toml go.mod Gemfile composer.json pubspec.yaml; do
  if [ -f "$f" ]; then
    echo "## DOCUMENT: $f" >> $OUTPUT
    cat "$f" >> $OUTPUT
    echo "" >> $OUTPUT
    echo "---" >> $OUTPUT
    echo "" >> $OUTPUT
  fi
done

# Folder structure
echo "## DOCUMENT: Folder Structure" >> $OUTPUT
find . -maxdepth 3 -type d \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/.next/*" \
  ! -path "*/dist/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/vendor/*" \
  ! -path "*/.claude/*" \
  | sort >> $OUTPUT
echo "" >> $OUTPUT
echo "---" >> $OUTPUT
echo "" >> $OUTPUT

# README
if [ -f "README.md" ]; then
  echo "## DOCUMENT: README.md" >> $OUTPUT
  head -100 README.md >> $OUTPUT
  echo "" >> $OUTPUT
  echo "---" >> $OUTPUT
  echo "" >> $OUTPUT
fi

# .env.example
for f in .env.example .env.sample .env.template; do
  if [ -f "$f" ]; then
    echo "## DOCUMENT: $f" >> $OUTPUT
    cat "$f" >> $OUTPUT
    echo "" >> $OUTPUT
    echo "---" >> $OUTPUT
    echo "" >> $OUTPUT
    break
  fi
done

# Existing rules/conventions
for f in docs/AI_RULES.md docs/CONVENTIONS.md CONTRIBUTING.md .cursorrules docs/AI_CONTEXT.md docs/ARCHITECTURE.md CLAUDE.md; do
  if [ -f "$f" ]; then
    echo "## DOCUMENT: $f" >> $OUTPUT
    cat "$f" >> $OUTPUT
    echo "" >> $OUTPUT
    echo "---" >> $OUTPUT
    echo "" >> $OUTPUT
  fi
done

echo "Context file created: $OUTPUT"
echo "Lines: $(wc -l < $OUTPUT)"
echo ""
echo "Now manually add DOCUMENT: [your representative code file] to $OUTPUT"
echo "Then give $OUTPUT to the AI agent along with the master prompt."
```

Save this as `collect-context.sh`, run `bash collect-context.sh` from your project root, then add your representative code file manually to the output.

---

## What Happens Without Each Document

| Missing Document | What suffers | How bad |
|---|---|---|
| package.json / dependency manifest | Stack section guessed, commands possibly wrong | 🔴 Critical — redo with this |
| Folder structure | Architecture section generic, Docs paths possibly wrong | 🟡 Important — output needs manual correction |
| README | Project description will be a placeholder | 🟡 Important — easy to fix manually |
| .env.example | Database and services not identified precisely | 🟡 Moderate — Stack section less specific |
| Real code file | Good Pattern will be generic boilerplate | 🟢 Minor — still useful, just less accurate |
| AI_RULES.md / conventions doc | Critical Conventions section mostly guessed | 🔴 Critical for convention accuracy |
| Brand/theme files | Brand colors and feature names section missing | 🟢 Minor (only matters for consumer apps) |

The two most important: **dependency manifest** and **existing rules/conventions doc**.
If you only have time to collect two things, collect those.
