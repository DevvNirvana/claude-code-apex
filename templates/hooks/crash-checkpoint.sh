#!/usr/bin/env bash
# APEX PreToolUse Hook — Crash Checkpoint Writer
# Fires before every Write, Edit, and Bash tool use.
# Writes an atomic checkpoint so /init can recover if Claude Code crashes.
#
# Research: Claude Code --resume fails on OOM kill (GitHub #18880, #30302)
# This gives APEX its own crash recovery independent of Claude Code sessions.
#
# What gets stored (.claude/checkpoints/last.json):
#   - Current git hash + branch
#   - Files being modified
#   - In-progress TODO items
#   - Claude Code session ID (if available)
#   - Timestamp

TOOL="$1"
FILE="${2:-}"

# Only checkpoint before destructive operations
case "$TOOL" in
  Write|Edit|Bash)
    ;;
  *)
    exit 0
    ;;
esac

# Write checkpoint (silent — don't pollute context)
if command -v python3 >/dev/null 2>&1; then
  python3 .claude/intelligence/crash_guard.py checkpoint "$TOOL" "$FILE" 2>/dev/null || true
fi

exit 0
