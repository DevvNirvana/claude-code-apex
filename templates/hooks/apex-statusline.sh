#!/usr/bin/env bash
# APEX Status Line — Live cost + context visibility
#
# Called by Claude Code after every response via settings.json statusLine.
# Receives Claude Code's telemetry JSON on stdin — data is accurate and
# sourced from Claude Code's own internals (not APEX heuristics).
#
# Output: single line showing identity, cost, context %, model name.
# Example: ◆ JARVIS  ·  $0.341  ·  68% ctx  ·  sonnet-4-6

INPUT=$(cat)
[ -z "$INPUT" ] && exit 0
command -v python3 >/dev/null 2>&1 || exit 0

echo "$INPUT" | python3 .claude/intelligence/apex_statusline.py
