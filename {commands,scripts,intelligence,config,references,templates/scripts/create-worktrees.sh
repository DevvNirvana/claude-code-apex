#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
#  Create Git Worktree for Parallel Agent
#  Usage: bash .claude/scripts/create-worktrees.sh [agent-name]
#  Example: bash .claude/scripts/create-worktrees.sh frontend
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

AGENT_NAME="${1:-}"
if [ -z "$AGENT_NAME" ]; then
  echo -e "${RED}Usage: $0 <agent-name>${RESET}"
  echo -e "${DIM}Example: $0 frontend${RESET}"
  exit 1
fi

PROJECT_DIR="$(pwd)"
BRANCH="agent/$AGENT_NAME"
WORKTREE_DIR="$PROJECT_DIR/worktrees/agent-$AGENT_NAME"
CLAUDE_DIR="$PROJECT_DIR/.claude"

echo ""
echo -e "${BOLD}${CYAN}━━━ Spawning Agent: $AGENT_NAME ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""

# Verify we're in a git repo
if ! git -C "$PROJECT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  echo -e "${RED}✗ Not a git repository. Run: git init${RESET}"
  exit 1
fi

# Git worktree requires at least one commit — create one if needed
if ! git -C "$PROJECT_DIR" rev-parse HEAD >/dev/null 2>&1; then
  echo -e "${YELLOW}⚠ No commits yet — creating initial commit for worktree support${RESET}"
  git -C "$PROJECT_DIR" add -A >/dev/null 2>&1 || true
  git -C "$PROJECT_DIR" commit -m "chore: initial commit" --quiet 2>/dev/null || {
    echo -e "${RED}✗ Could not create initial commit. Add files and try again.${RESET}"
    exit 1
  }
fi

# Commit any pending changes first
if ! git -C "$PROJECT_DIR" diff --quiet 2>/dev/null || \
   ! git -C "$PROJECT_DIR" diff --cached --quiet 2>/dev/null; then
  echo -e "${YELLOW}⚠ Uncommitted changes detected — committing before creating worktree${RESET}"
  git -C "$PROJECT_DIR" add -A
  git -C "$PROJECT_DIR" commit -m "chore: auto-commit before spawning agent/$AGENT_NAME" --quiet 2>/dev/null || true
fi

# Create branch if it doesn't exist
if git -C "$PROJECT_DIR" show-ref --verify --quiet "refs/heads/$BRANCH" 2>/dev/null; then
  echo -e "${YELLOW}⚠ Branch $BRANCH already exists${RESET}"
else
  git -C "$PROJECT_DIR" branch "$BRANCH" >/dev/null 2>&1
  echo -e "${GREEN}✓ Branch created: $BRANCH${RESET}"
fi

# Remove existing worktree if present
if [ -d "$WORKTREE_DIR" ]; then
  echo -e "${YELLOW}⚠ Removing existing worktree at $WORKTREE_DIR${RESET}"
  git -C "$PROJECT_DIR" worktree remove --force "$WORKTREE_DIR" 2>/dev/null || rm -rf "$WORKTREE_DIR"
fi

# Create worktree
git -C "$PROJECT_DIR" worktree add "$WORKTREE_DIR" "$BRANCH" --quiet
echo -e "${GREEN}✓ Worktree created: $WORKTREE_DIR${RESET}"

# Copy .claude to worktree (agent gets the same orchestrator)
if [ -d "$CLAUDE_DIR" ]; then
  cp -r "$CLAUDE_DIR" "$WORKTREE_DIR/.claude"
  echo -e "${GREEN}✓ Orchestrator copied to worktree${RESET}"
fi

# Copy CLAUDE.md
[ -f "$PROJECT_DIR/CLAUDE.md" ] && cp "$PROJECT_DIR/CLAUDE.md" "$WORKTREE_DIR/CLAUDE.md"

# Create agent brief
TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S")
cat > "$WORKTREE_DIR/AGENT_BRIEF.md" << BRIEF
# Agent Brief: $AGENT_NAME
**Role:** [Fill in: e.g., "Frontend Developer"]
**Branch:** $BRANCH
**Worktree:** worktrees/agent-$AGENT_NAME/
**Created:** $TIMESTAMP
**Parent project:** $PROJECT_DIR

## Mission
[Fill in: 1-2 sentences describing exactly what this agent builds]

## Domain (files you OWN — create/edit freely)
- [Fill in: e.g., src/app/, src/components/]

## Read-Only Access
- src/types/     — TypeScript types
- src/lib/       — shared utilities
- docs/          — project documentation
- CLAUDE.md      — project conventions

## NEVER TOUCH
- [Fill in: files owned by other agents]
- migrations/    — database migrations
- .env*          — environment files

## Your Tasks
Check TODO.md for tasks assigned to @agent-$AGENT_NAME

## Workflow
1. Read CLAUDE.md and docs/DESIGN_DOC.md first
2. Check TODO.md for your assigned tasks
3. Mark tasks [>] when starting
4. Mark tasks [x] when complete
5. Mark tasks [!] if blocked (with explanation)
6. Commit format: type(scope): description
7. Run npm run lint before committing

## Orchestrator Commands
/plan   — Plan before building
/design — UI with design intelligence
/review — Code review
/debug  — Root cause analysis
/test   — Generate tests
BRIEF

echo -e "${GREEN}✓ Agent brief created: AGENT_BRIEF.md${RESET}"

# Save worktree metadata
mkdir -p "$CLAUDE_DIR/worktrees-meta"
cat > "$CLAUDE_DIR/worktrees-meta/$AGENT_NAME.json" << META
{
  "agent_id": "agent-$AGENT_NAME",
  "branch": "$BRANCH",
  "worktree": "worktrees/agent-$AGENT_NAME",
  "created_at": "$TIMESTAMP",
  "status": "active"
}
META

echo ""
echo -e "${BOLD}${GREEN}━━━ Agent Ready ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${BOLD}Start the agent:${RESET}"
echo -e "  cd worktrees/agent-$AGENT_NAME"
echo -e "  claude"
echo ""
echo -e "  ${BOLD}First thing to do in the agent session:${RESET}"
echo -e "  /init  (then fill in AGENT_BRIEF.md mission + domain)"
echo ""
echo -e "  ${BOLD}When done:${RESET}"
echo -e "  bash .claude/scripts/merge-agents.sh $AGENT_NAME"
echo ""
