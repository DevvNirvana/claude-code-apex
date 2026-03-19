#!/usr/bin/env bash
# APEX AI Engineering OS — Install Script v4.0.0
# Windows Git Bash compatible

set -euo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

FORCE=false; DRY_RUN=false; UPDATE_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --force)   FORCE=true ;;
    --dry-run) DRY_RUN=true ;;
    --update)  UPDATE_ONLY=true; FORCE=true ;;
  esac
done

# Portable path resolution — works on POSIX and Windows Git Bash
_SCRIPT="${BASH_SOURCE[0]:-$0}"
PKG_DIR="$(cd "$(dirname "$_SCRIPT")/.." 2>/dev/null && pwd)"
DEST=".claude"

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║   APEX — AI Engineering OS  v4.0.0                   ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════╝${RESET}"
echo ""
echo -e "${DIM}  Source: $PKG_DIR${RESET}"
echo -e "${DIM}  Target: $(pwd)/$DEST${RESET}"
if   $DRY_RUN;     then echo -e "${YELLOW}  Mode:   dry-run${RESET}"
elif $UPDATE_ONLY; then echo -e "${CYAN}  Mode:   update${RESET}"
elif $FORCE;       then echo -e "${YELLOW}  Mode:   force${RESET}"
else                    echo -e "${DIM}  Mode:   safe${RESET}"
fi
echo ""
$DRY_RUN && echo -e "${YELLOW}[DRY RUN] Nothing will be written.${RESET}\n"

install_file() {
  local src="$1" dst="$2"
  [ ! -f "$src" ] && echo -e "  ${RED}✗ Missing: $src${RESET}" && return
  if $DRY_RUN; then echo -e "  ${DIM}→ $dst${RESET}"; return; fi
  mkdir -p "$(dirname "$dst")" 2>/dev/null || true
  if [ -f "$dst" ] && [ "$FORCE" = false ]; then
    echo -e "  ${YELLOW}⊘ Skip: $dst${RESET}"
  else
    cp "$src" "$dst" && echo -e "  ${GREEN}✓ $dst${RESET}"
  fi
}

install_dir() {
  local src_dir="$1" dst_dir="$2"
  [ ! -d "$src_dir" ] && echo -e "  ${RED}✗ Missing dir: $src_dir${RESET}" && return
  $DRY_RUN || mkdir -p "$dst_dir"
  find "$src_dir" -type f | while IFS= read -r file; do
    rel="${file#$src_dir/}"
    install_file "$file" "$dst_dir/$rel"
  done
}

# Commands (17)
echo -e "${BOLD}Commands (17)...${RESET}"
for cmd in init setup status ask brainstorm plan execute design spawn test \
           debug optimize refactor docs review ship rollback compact; do
  install_file "$PKG_DIR/commands/$cmd.md" "$DEST/commands/$cmd.md"
done

# Intelligence (10 modules)
echo ""; echo -e "${BOLD}Intelligence (10 modules)...${RESET}"
for mod in cache_manager detect_stack token_tracker trajectory_store \
           taste_memory project_brain evaluator benchmark \
           design_system framework_lint generate_claude_md; do
  install_file "$PKG_DIR/intelligence/$mod.py" "$DEST/intelligence/$mod.py"
done

if ! $UPDATE_ONLY; then
  # References (23 docs)
  echo ""; echo -e "${BOLD}References (23 docs)...${RESET}"
  install_dir "$PKG_DIR/references" "$DEST/references"

  # Scripts (4)
  echo ""; echo -e "${BOLD}Scripts (4)...${RESET}"
  for script in install.sh create-worktrees.sh merge-agents.sh token-report.sh; do
    install_file "$PKG_DIR/scripts/$script" "$DEST/scripts/$script"
    $DRY_RUN || chmod +x "$DEST/scripts/$script" 2>/dev/null || true
  done

  # Config (3)
  echo ""; echo -e "${BOLD}Config (3)...${RESET}"
  for cfg in context-map.json output-contracts.json cache-config.json; do
    install_file "$PKG_DIR/config/$cfg" "$DEST/config/$cfg"
  done

  # Templates
  echo ""; echo -e "${BOLD}Templates...${RESET}"
  install_file "$PKG_DIR/templates/TODO.md"            "TODO.md"
  install_file "$PKG_DIR/templates/docs/PRD.md"        "docs/PRD.md"
  install_file "$PKG_DIR/templates/docs/DESIGN_DOC.md" "docs/DESIGN_DOC.md"
  install_file "$PKG_DIR/templates/docs/TECH_STACK.md" "docs/TECH_STACK.md"

  if [ ! -f "CLAUDE.md" ]; then
    if $DRY_RUN; then echo -e "  ${DIM}→ would install: CLAUDE.md${RESET}"
    else cp "$PKG_DIR/templates/CLAUDE.md" "CLAUDE.md" && \
         echo -e "  ${GREEN}✓ CLAUDE.md (fill in your project details)${RESET}"; fi
  else
    echo -e "  ${YELLOW}⊘ CLAUDE.md exists — keeping yours${RESET}"
  fi

  # Runtime dirs
  if ! $DRY_RUN; then
    mkdir -p "$DEST/config" "$DEST/cache/plans" "$DEST/cache/responses" \
             "$DEST/logs" "$DEST/brain" "$DEST/memory/trajectories" \
             "$DEST/memory/benchmarks" "$DEST/worktrees-meta" "worktrees" "docs"
  fi
fi

# Stack detection
echo ""; echo -e "${BOLD}Stack detection...${RESET}"
if ! $DRY_RUN && command -v python3 >/dev/null 2>&1; then
  python3 "$DEST/intelligence/detect_stack.py" --save 2>/dev/null || \
    echo -e "  ${YELLOW}⚠ Run: python3 .claude/intelligence/detect_stack.py --save${RESET}"
else echo -e "  ${DIM}(skipped)${RESET}"; fi

# Brain sync
echo ""; echo -e "${BOLD}Brain sync...${RESET}"
if ! $DRY_RUN && command -v python3 >/dev/null 2>&1; then
  python3 "$DEST/intelligence/project_brain.py" sync 2>/dev/null || \
    echo -e "  ${DIM}(skipped — no CLAUDE.md yet)${RESET}"
else echo -e "  ${DIM}(skipped)${RESET}"; fi

# Cache warm-up
echo ""; echo -e "${BOLD}Warming plan cache...${RESET}"
if ! $DRY_RUN && command -v python3 >/dev/null 2>&1; then
  python3 "$DEST/intelligence/cache_manager.py" warm 2>/dev/null || \
    echo -e "  ${DIM}(no tasks file — cache warms on first /plan)${RESET}"
else echo -e "  ${DIM}(skipped)${RESET}"; fi

# Summary
echo ""
echo -e "${BOLD}${GREEN}━━━ Installation Complete ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo ""
if [ ! -f "CLAUDE.md" ] || grep -q "\[1-2 sentences" "CLAUDE.md" 2>/dev/null; then
  echo -e "  ${YELLOW}1. Edit CLAUDE.md with your project details${RESET}\n"
fi
echo -e "  ${CYAN}2. Run /init in Claude Code to complete setup${RESET}"
echo -e "  ${BOLD}     /init${RESET}\n"
echo -e "  ${BOLD}Command groups:${RESET}"
echo -e "  ${DIM}  Meta:    /init /status /compact /benchmark${RESET}"
echo -e "  ${DIM}  Dev:     /brainstorm /ask /plan /execute /design${RESET}"
echo -e "  ${DIM}           /spawn /test /debug /optimize /refactor /docs${RESET}"
echo -e "  ${DIM}  Quality: /review /ship /rollback${RESET}"
echo ""
