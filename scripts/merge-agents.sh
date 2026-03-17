#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
#  Merge Agent Back to Main
#  Usage: bash .claude/scripts/merge-agents.sh [agent-name] [--no-squash]
#
#  Default: squash merge (clean history, 1 professional commit per agent)
#  --no-squash: preserve full commit history (useful for audit trails)
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

AGENT_NAME="${1:-}"
SQUASH=true
[ "${2:-}" = "--no-squash" ] && SQUASH=false

if [ -z "$AGENT_NAME" ]; then
  echo -e "${RED}Usage: $0 <agent-name> [--no-squash]${RESET}"
  echo -e "${DIM}  Default: squash all agent commits into one clean commit${RESET}"
  echo -e "${DIM}  --no-squash: preserve full agent commit history${RESET}"
  exit 1
fi

PROJECT_DIR="$(pwd)"
BRANCH="agent/$AGENT_NAME"
WORKTREE_DIR="$PROJECT_DIR/worktrees/agent-$AGENT_NAME"
# Detect main branch safely — never use current branch as fallback
# (if running from inside a worktree, current branch would be agent/xxx)
MAIN_BRANCH=$(git -C "$PROJECT_DIR" symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
if [ -z "$MAIN_BRANCH" ]; then
  # No remote — look for main, master, or develop explicitly
  for candidate in main master develop trunk; do
    if git -C "$PROJECT_DIR" show-ref --verify --quiet "refs/heads/$candidate" 2>/dev/null; then
      MAIN_BRANCH="$candidate"
      break
    fi
  done
fi
[ -z "$MAIN_BRANCH" ] && MAIN_BRANCH="main"  # final fallback

echo ""
echo -e "${BOLD}${CYAN}━━━ Merging Agent: $AGENT_NAME ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${DIM}  Mode: $([ "$SQUASH" = true ] && echo 'squash (clean history)' || echo 'no-squash (preserve commits)')${RESET}"
echo ""

# Verify git repo
if ! git -C "$PROJECT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  echo -e "${RED}✗ Not a git repository${RESET}"
  exit 1
fi

# Check branch exists
if ! git -C "$PROJECT_DIR" show-ref --verify --quiet "refs/heads/$BRANCH" 2>/dev/null; then
  echo -e "${RED}✗ Branch '$BRANCH' does not exist${RESET}"
  echo -e "${YELLOW}  Did you run: /spawn $AGENT_NAME ?${RESET}"
  echo -e "${DIM}  Active agent branches:${RESET}"
  git -C "$PROJECT_DIR" branch | grep "agent/" || echo -e "${DIM}  (none)${RESET}"
  exit 1
fi

# 1. Commit any remaining changes in worktree
if [ -d "$WORKTREE_DIR" ]; then
  cd "$WORKTREE_DIR"
  if ! git diff --quiet || ! git diff --cached --quiet; then
    git add -A
    git commit -m "feat($AGENT_NAME): final commit before merge" --quiet
    echo -e "${GREEN}✓ Final commit in worktree${RESET}"
  fi
  cd "$PROJECT_DIR"
fi

# 2. Count commits to merge
COMMIT_COUNT=$(git -C "$PROJECT_DIR" log --oneline "${MAIN_BRANCH}..${BRANCH}" 2>/dev/null | wc -l | tr -d ' ')
echo -e "${CYAN}  $COMMIT_COUNT commits to merge from $BRANCH${RESET}"

if [ "$COMMIT_COUNT" = "0" ]; then
  echo -e "${YELLOW}⚠ No commits to merge — agent branch is up to date with main${RESET}"
  exit 0
fi

# 3. Extract mission from AGENT_BRIEF.md for commit message
MISSION=""
if [ -f "$WORKTREE_DIR/AGENT_BRIEF.md" ]; then
  # Try to grab the line after "## Your Mission" or "## Mission"
  MISSION=$(awk '/^## (Your Mission|Mission)/{found=1; next} found && NF{print; exit}' "$WORKTREE_DIR/AGENT_BRIEF.md" 2>/dev/null | head -c 120 | tr -d '\n')
fi
[ -z "$MISSION" ] && MISSION="completed agent work"

# Clean up mission text
MISSION=$(echo "$MISSION" | sed 's/^\[//;s/\]$//' | sed 's/^Fill in.*$/completed agent work/')
COMMIT_MSG="feat($AGENT_NAME): $MISSION"

# 4. Switch to main
git -C "$PROJECT_DIR" checkout "$MAIN_BRANCH" --quiet 2>/dev/null || git -C "$PROJECT_DIR" checkout main --quiet

# 5. Merge
if $SQUASH; then
  # Squash: all agent commits → one clean commit
  if git -C "$PROJECT_DIR" merge --squash "$BRANCH" --quiet; then
    git -C "$PROJECT_DIR" commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✓ Squash merged $BRANCH → $MAIN_BRANCH${RESET}"
    echo -e "${DIM}  Commit: $COMMIT_MSG${RESET}"
    echo -e "${DIM}  ($COMMIT_COUNT agent commits squashed into 1 clean commit)${RESET}"
  else
    echo -e "${RED}✗ Merge conflict detected${RESET}"
    echo -e "${YELLOW}  Resolve conflicts, then: git add . && git commit -m \"$COMMIT_MSG\"${RESET}"
    exit 1
  fi
else
  # No-squash: preserve full agent history
  if git -C "$PROJECT_DIR" merge "$BRANCH" --no-ff -m "merge: integrate agent/$AGENT_NAME work" --quiet; then
    echo -e "${GREEN}✓ Merged $BRANCH → $MAIN_BRANCH (full history preserved)${RESET}"
  else
    echo -e "${RED}✗ Merge conflict detected${RESET}"
    echo -e "${YELLOW}  Resolve conflicts, then: git merge --continue${RESET}"
    exit 1
  fi
fi

# 6. Remove worktree
if [ -d "$WORKTREE_DIR" ]; then
  git -C "$PROJECT_DIR" worktree remove "$WORKTREE_DIR" --force 2>/dev/null || rm -rf "$WORKTREE_DIR"
  echo -e "${GREEN}✓ Worktree removed${RESET}"
fi

# 7. Delete agent branch
# Squash merge has no ancestry record — must force-delete (-D)
# No-squash creates a real merge commit — safe to use -d
if $SQUASH; then
  git -C "$PROJECT_DIR" branch -D "$BRANCH" 2>/dev/null && \
    echo -e "${GREEN}✓ Branch $BRANCH deleted${RESET}" || \
    echo -e "${DIM}⊘ Branch not deleted (may already be removed)${RESET}"
else
  git -C "$PROJECT_DIR" branch -d "$BRANCH" 2>/dev/null && \
    echo -e "${GREEN}✓ Branch $BRANCH deleted${RESET}" || \
    echo -e "${DIM}⊘ Branch not deleted (may already be removed)${RESET}"
fi

# 8. Update worktree metadata
CLAUDE_DIR="$PROJECT_DIR/.claude"
if [ -f "$CLAUDE_DIR/worktrees-meta/$AGENT_NAME.json" ]; then
  python3 -c "
import json
f = '$CLAUDE_DIR/worktrees-meta/$AGENT_NAME.json'
try:
    d = json.load(open(f))
    d['status'] = 'merged'
    d['merged_at'] = '$(date +"%Y-%m-%dT%H:%M:%S")'
    d['commit_message'] = '''$COMMIT_MSG'''
    json.dump(d, open(f,'w'), indent=2)
except: pass
" 2>/dev/null || true
fi

echo ""
echo -e "${BOLD}${GREEN}━━━ Merge Complete ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
echo -e "  ${DIM}Run /ship to verify the merged code is production-ready${RESET}"
echo ""
