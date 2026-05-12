#!/usr/bin/env python3
"""
APEX Status Line — Live Cost + Context Visibility
==================================================
Reads Claude Code's JSON telemetry from stdin after every response.
Outputs a single colored line for the status bar.

Data is 100% accurate — sourced directly from Claude Code internals,
not from APEX heuristics.

Fields consumed from Claude Code's stdin JSON:
  cost.total_cost_usd              — accumulated session cost in USD
  context_window.used_percentage   — context window fill (0-100)
  context_window.total_input_tokens— total tokens sent this session
  model.id                         — full model ID string

Output example:
  ◆ JARVIS  ·  $0.341  ·  68% ctx  ·  sonnet-4-6

Identity name read from:
  1. .claude/cache/statusline-name.txt  (project-level cache — fastest)
  2. .claude/identity.json              (project-level config)
  3. ~/.claude/identity.json            (global fallback)
  4. "APEX"                             (hard fallback)

The name cache (statusline-name.txt) is written by hooks_generator.py
whenever settings.json is regenerated, so it stays current.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path.cwd()


def _read_name() -> str:
    """Read identity name from cache or identity.json. Fast path first."""
    # 1. Cached name (single text file — near-zero cost)
    cache = ROOT / ".claude" / "cache" / "statusline-name.txt"
    if cache.exists():
        try:
            name = cache.read_text(encoding="utf-8").strip()
            if name:
                return name
        except Exception:
            pass

    # 2. Project identity.json
    for id_path in [
        ROOT / ".claude" / "identity.json",
        Path.home() / ".claude" / "identity.json",
    ]:
        if id_path.exists():
            try:
                data = json.loads(id_path.read_text(encoding="utf-8", errors="ignore"))
                name = data.get("name", "").strip()
                if name:
                    return name
            except Exception:
                continue

    return "APEX"


def _shorten_model(model_id: str) -> str:
    """claude-sonnet-4-6-20251001 → sonnet-4-6"""
    s = model_id.replace("claude-", "")
    if "-202" in s:
        s = s.rsplit("-202", 1)[0]
    return s or model_id


def render(data: dict) -> str:
    """Build the status line string from Claude Code's telemetry dict."""
    cost    = float(data.get("cost", {}).get("total_cost_usd", 0) or 0)
    ctx_pct = int(data.get("context_window", {}).get("used_percentage", 0) or 0)
    model   = str(data.get("model", {}).get("id", "") or "")
    name    = _read_name()
    short   = _shorten_model(model)

    # ANSI colors
    CYAN  = "\033[0;36m"
    DIM   = "\033[2m"
    RESET = "\033[0m"
    BOLD  = "\033[1m"
    GRN   = "\033[0;32m"
    YLW   = "\033[1;33m"
    RED   = "\033[0;31m"

    ctx_color = GRN if ctx_pct < 50 else (YLW if ctx_pct < 80 else RED)
    cost_str  = "$%.3f" % cost
    sep       = DIM + "  ·  " + RESET

    return (
        BOLD + CYAN + " ◆ " + name + RESET
        + sep
        + cost_str
        + sep
        + ctx_color + str(ctx_pct) + "% ctx" + RESET
        + sep
        + DIM + short + RESET
    )


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except Exception:
        sys.exit(0)

    try:
        line = render(data)
        print(line)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
