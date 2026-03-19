#!/usr/bin/env bash
# APEX v4.0 — root installer shortcut
_SCRIPT="${BASH_SOURCE[0]:-$0}"
SCRIPT_DIR="$(cd "$(dirname "$_SCRIPT")" 2>/dev/null && pwd)"
bash "$SCRIPT_DIR/scripts/install.sh" "$@"
