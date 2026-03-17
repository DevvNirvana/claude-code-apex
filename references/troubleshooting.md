# Troubleshooting Guide

## Installation Issues

### "Permission denied" on WSL
```bash
chmod +x ai-orchestrator/scripts/*.sh
bash ai-orchestrator/scripts/install.sh
```

### "git: command not found"
```bash
sudo apt update && sudo apt install git
```

### "node: command not found" (needed for some checks only)
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

### Unzip not found
```bash
sudo apt install unzip
unzip ai-orchestrator.zip
```

---

## Doc Scanner Issues

### Scanner found wrong file for a role
Edit `.antigravity/docs-manifest.json` directly:
```json
{
  "prd": "docs/your-actual-prd-file.md",
  "design_doc": "docs/your-actual-design-doc.md",
  "tech_stack": "docs/your-actual-tech-stack.md",
  "todo": "MatchHire_AI_TODO.md"
}
```
Then re-run: `bash .antigravity/scripts/generate-workspace.sh`

### Scanner found no docs at all
Your docs might not be markdown. Check:
```bash
find . -type f -not -path "*/node_modules/*" -not -path "*/.git/*" | head -30
```
If docs are `.txt` or `.docx`, convert to `.md` first or add them manually to the manifest.

---

## Antigravity Issues

### Manager View shows no agents
1. Check `.antigravity/workspace.json` exists
2. In Antigravity: View → Reload Window
3. Re-run: `bash .antigravity/scripts/generate-workspace.sh`

### /plan or /review not working in Antigravity
Check that `.antigravity/prompts/` contains `.xml` files:
```bash
ls .antigravity/prompts/
# Should show: plan.xml review.xml init.xml spawn.xml ship.xml
```
If empty, re-run the installer.

### rules.md not being read by Gemini
Verify the file exists and is valid:
```bash
cat .antigravity/rules.md | head -20
# Should start with <!-- and have <rules> tag
```

---

## Worktree / Agent Issues

### "fatal: not a git repository" when spawning agent
Your project root needs to be a git repo:
```bash
git init
git add .
git commit -m "chore: initial commit"
# Then retry spawning
```

### Worktree already exists error
```bash
git worktree list           # see what's registered
git worktree remove worktrees/agent-frontend   # remove if stale
git worktree prune          # clean up stale references
```

### Agent branch already exists
```bash
git branch -d agent/frontend    # delete if unused
# Or use the existing branch — spawner will detect it
```

### Merge conflict when running merge-agents.sh
```bash
# The script aborts automatically. Resolve manually:
git merge agent/frontend
# Fix conflicts in your editor
git add .
git commit
# Then run merge-agents.sh again for remaining agents
```

---

## Model Limit Issues (Your Current Situation)

### Claude weekly limit hit (you're here now)
`.antigravity/workspace.json` already sets Gemini 3.1 Pro as default.
Nothing to do — just open Antigravity and work normally.

### Thursday — switching back to Claude
Open `.antigravity/workspace.json`, find:
```json
"default": "gemini-3.1-pro"
```
Change to:
```json
"default": "claude-sonnet-4-6"
```
Save. Antigravity picks it up immediately, no restart needed.

### Want different models per agent
Edit the `"model"` field per agent in `workspace.json`:
```json
{
  "id": "agent-frontend",
  "model": {
    "primary": "claude-sonnet-4-6",
    "fallback": "gemini-3.1-pro"
  }
}
```

---

## WSL-Specific Issues

### Can't find project in WSL
Windows `C:\Users\Name\project` is at `/mnt/c/Users/Name/project` in WSL.
```bash
cd /mnt/c/Users/YourName/path/to/MatchHire-AI
```

### Line ending issues (CRLF vs LF)
```bash
# Fix all scripts
find .antigravity/scripts/ -name "*.sh" -exec sed -i 's/\r//' {} \;
```

### Antigravity can't open WSL path
Open Antigravity on Windows → File → Open Folder → navigate using the Windows path.
WSL filesystem is accessible at `\\wsl$\Ubuntu\home\username\project`.
