#!/usr/bin/env bash
# APEX Stop Hook — Auto Brain Sync + Code Index Rebuild + Session Summary
#
# Fires on every Stop event (session end, /compact, exit).
# Two background jobs run silently — never blocks Claude Code shutdown.
#
# Jobs:
#   1. brain_sync     — updates project_brain.json from CLAUDE.md (semantic memory)
#   2. code_index     — rebuilds symbol index from source files (code RAG)
#   3. turn counter   — resets session_turns.txt for next session
# Then prints a brief session-close reminder (docs hygiene).

# ── Silent background sync (non-blocking) ─────────────────────────────────────
if command -v python3 >/dev/null 2>&1; then
  # Brain sync: runs only if CLAUDE.md exists and has changed
  python3 .claude/intelligence/project_brain.py sync >/dev/null 2>&1 &
  BRAIN_PID=$!

  # Code index rebuild: scans project files for updated symbol map
  python3 .claude/intelligence/code_index.py build >/dev/null 2>&1 &
  INDEX_PID=$!

  # Wait max 4 seconds for both (they're fast — typically <0.5s each)
  for pid in $BRAIN_PID $INDEX_PID; do
    ( sleep 4 && kill $pid 2>/dev/null ) &
    wait $pid 2>/dev/null
  done
fi

# ── Reset context pressure counter ────────────────────────────────────────────
echo "0" > ".claude/logs/session_turns.txt" 2>/dev/null || true

# ── Session close reminder ─────────────────────────────────────────────────────
echo ""
echo "━━━ APEX: Session complete ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Brain sync + code index rebuilt in background."
echo ""
echo "  Before closing, spend 2 minutes:"
echo "  1. Update TODO.md — mark [x] done, add discovered tasks"
echo "  2. If something shipped, store the trajectory:"
echo "     python3 .claude/intelligence/trajectory_store.py store <session-notes>"
echo ""

exit 0
