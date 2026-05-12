#!/usr/bin/env bash
# APEX UserPromptSubmit Hook — Context Pressure Detection
#
# Research (arXiv:2510.05381): LLM quality degrades measurably as context fills.
# "Lost in the middle" effect begins at ~50% utilization; sharp drop at 85%+.
# arXiv:2601.11564: Recitation of key constraints before answering improves
# long-context accuracy by ~4%.
#
# Delegates to context_guard.py which measures three signals:
#   Turn pressure   — conversation turns
#   Token pressure  — session token totals from token_tracker
#   Base pressure   — CLAUDE.md size (more base context = less room for turns)
#
# At HIGH (70%+): prints warning + recitation anchor for Claude to re-anchor
# At CRITICAL (85%+): strong warning to /compact or start fresh

TURNS_FILE=".claude/logs/session_turns.txt"
mkdir -p ".claude/logs"

# Increment turn counter (context_guard.py reads this file)
TURNS=$(cat "$TURNS_FILE" 2>/dev/null || echo "0")
TURNS=$((TURNS + 1))
echo "$TURNS" > "$TURNS_FILE"

# Delegate pressure check to context_guard.py
if command -v python3 >/dev/null 2>&1; then
  GUARD_OUT=$(python3 .claude/intelligence/context_guard.py check 2>/dev/null)
  [ -n "$GUARD_OUT" ] && echo "$GUARD_OUT"
else
  # Fallback: simple turn-count warnings when python3 unavailable
  if [ "$TURNS" -eq 15 ]; then
    echo ""
    echo "⚠ APEX: Session at turn 15. Consider /compact if starting a new task."
    echo ""
  elif [ "$TURNS" -eq 25 ]; then
    echo ""
    echo "⛔ APEX: Session at turn 25. Strongly recommend /handoff + fresh session."
    echo ""
  elif [ "$TURNS" -gt 30 ] && [ $((TURNS % 10)) -eq 0 ]; then
    echo ""
    echo "⛔ APEX: Session at turn $TURNS. Context heavily loaded — run /handoff."
    echo ""
  fi
fi

exit 0
