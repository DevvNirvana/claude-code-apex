#!/usr/bin/env bash
# APEX Voice — Stop hook for response narration
#
# Called by Claude Code after every response when speak_responses is enabled.
# Reads the Stop event JSON from stdin, extracts response text, and fires
# apex_voice.py in a detached subprocess so the hook exits immediately.
#
# Only wired into settings.json by hooks_generator.py when
# voice.speak_responses = true in identity config. Disabled by default.

command -v python3 >/dev/null 2>&1 || exit 0
[ -f .claude/intelligence/apex_voice.py ] || exit 0

INPUT=$(cat)
[ -z "$INPUT" ] && exit 0

# Extract text from Stop event JSON, then speak asynchronously (detached).
# Caps at 1500 chars — skip code-heavy or very long responses.
TEXT=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    text = (
        data.get('response', '')
        or data.get('message', '')
        or data.get('content', '')
        or ''
    ).strip()
    if text and len(text) <= 1500:
        print(text, end='')
except Exception:
    pass
" 2>/dev/null)

[ -z "$TEXT" ] && exit 0

# Detach so the hook returns immediately — terminal never blocks
python3 .claude/intelligence/apex_voice.py speak "$TEXT" \
  </dev/null >/dev/null 2>&1 &

exit 0
