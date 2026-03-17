#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
#  Token Intelligence Report
#  Usage: bash .claude/scripts/token-report.sh [--today]
# ════════════════════════════════════════════════════════════════════

set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'

PROJECT_DIR="$(pwd)"
TRACKER="$PROJECT_DIR/.claude/intelligence/token_tracker.py"
CACHE_MGR="$PROJECT_DIR/.claude/intelligence/cache_manager.py"
FLAG="${1:-}"

echo ""
echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}${CYAN}║              TOKEN INTELLIGENCE DASHBOARD                    ║${RESET}"
echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════════╝${RESET}"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo -e "${YELLOW}⚠ Python3 not found. Install python3 to enable token tracking.${RESET}"
  exit 0
fi

if [ ! -f "$TRACKER" ]; then
  echo -e "${YELLOW}⚠ Token tracker not found at $TRACKER${RESET}"
  echo -e "${DIM}Run install.sh to reinstall${RESET}"
  exit 0
fi

# Token usage report
if [ "$FLAG" = "--today" ]; then
  python3 "$TRACKER" report --today
else
  python3 "$TRACKER" report
fi

# Cache stats
if [ -f "$CACHE_MGR" ]; then
  python3 "$CACHE_MGR" stats
fi

echo -e "${DIM}Commands:${RESET}"
echo -e "${DIM}  bash .claude/scripts/token-report.sh --today   (today's stats only)${RESET}"
echo -e "${DIM}  python3 .claude/intelligence/token_tracker.py reset   (reset all data)${RESET}"
echo ""
