#!/usr/bin/env bash
# APEX SessionStart Hook — Update Checker
# Fires at every Claude Code session start.
# Checks for APEX updates once per 24h (cached — never hammers network).
# Silent if current. Shows prompt if a new version is available.

if command -v python3 >/dev/null 2>&1; then
  python3 .claude/intelligence/update_checker.py check 2>/dev/null || true
fi

exit 0
