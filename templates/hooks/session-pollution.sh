#!/usr/bin/env bash
# APEX UserPromptSubmit Hook — Session Pollution Detection
# Fires before each user message. Warns when context is getting polluted.
#
# Research: quality drops sharply past 50% context utilization.
# One project recovered 15,000 tokens/session by starting fresh.
# "Starting fresh costs 20K tokens — nothing vs quality loss from polluted session."
#
# Tracks turn count in .claude/logs/session_turns.txt
# Warns at 15 turns, strongly warns at 25 turns.

TURNS_FILE=".claude/logs/session_turns.txt"
mkdir -p ".claude/logs"

# Read current turn count
TURNS=$(cat "$TURNS_FILE" 2>/dev/null || echo "0")
TURNS=$((TURNS + 1))
echo "$TURNS" > "$TURNS_FILE"

# Warn thresholds
if [ "$TURNS" -eq 15 ]; then
    echo ""
    echo "⚠ APEX: Session at turn 15. Context may be getting polluted."
    echo "  Research shows quality degrades past 50% context utilization."
    echo "  Consider: /compact to compress, or /handoff + fresh session for new tasks."
    echo ""
elif [ "$TURNS" -eq 25 ]; then
    echo ""
    echo "🔴 APEX: Session at turn 25. Strongly recommend starting fresh."
    echo "  Run /handoff to preserve context, then start a new session."
    echo "  CLAUDE.md compliance has likely degraded significantly."
    echo ""
elif [ "$TURNS" -gt 30 ] && [ $((TURNS % 10)) -eq 0 ]; then
    echo ""
    echo "🔴 APEX: Session at turn $TURNS. Context is heavily polluted."
    echo "  Run /handoff now. Continuing will produce lower quality output."
    echo ""
fi

exit 0
