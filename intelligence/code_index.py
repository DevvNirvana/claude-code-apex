#!/usr/bin/env python3
"""
APEX Code Index — Pure Python AST Code Symbol Index (Local CodeRAG)
====================================================================
Builds a lightweight symbol map of the project: functions, classes,
methods → file paths + line numbers. Zero external dependencies.

Called by context_engine.py for STANDARD/FULL tier prompts.
Rebuilt automatically by session-end.sh on every Stop event.

Index stored at: .claude/cache/code_index.json

Usage:
  python3 .claude/intelligence/code_index.py build   # rebuild index
  python3 .claude/intelligence/code_index.py query <keyword>
  python3 .claude/intelligence/code_index.py stats
"""
from __future__ import annotations

import ast
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT      = Path.cwd()
APEX_DIR  = ROOT / ".claude"
INDEX_FILE = APEX_DIR / "cache" / "code_index.json"

# File extensions to index
_SUPPORTED_EXTS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go"}

# Dirs to skip unconditionally
_SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".claude", "dist", "build",
    ".next", ".venv", "venv", "env", ".env", "coverage", ".mypy_cache",
    ".pytest_cache", "worktrees",
}

# Max files to index (safety cap — avoids multi-second builds on huge monorepos)
_MAX_FILES = 500

GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"; DIM = "\033[2m"; RESET = "\033[0m"


# ── Python AST extractor ──────────────────────────────────────────────────────

def _extract_python_symbols(path: Path) -> list[dict[str, Any]]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return []
    except Exception:
        return []

    symbols = []
    rel = str(path.relative_to(ROOT)).replace("\\", "/")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({
                "name": node.name,
                "kind": "function",
                "file": rel,
                "line": node.lineno,
            })
        elif isinstance(node, ast.ClassDef):
            symbols.append({
                "name": node.name,
                "kind": "class",
                "file": rel,
                "line": node.lineno,
            })
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append({
                        "name": item.name,
                        "kind": "method",
                        "parent": node.name,
                        "file": rel,
                        "line": item.lineno,
                    })

    return symbols


# ── Go regex extractor ────────────────────────────────────────────────────────

_GO_PATTERNS = [
    (re.compile(r'^func\s+\(?[\w\s*]+\)?\s*(\w+)\s*\(', re.M), "function"),
    (re.compile(r'^type\s+(\w+)\s+struct\b', re.M),             "class"),
    (re.compile(r'^type\s+(\w+)\s+interface\b', re.M),          "type"),
]


def _extract_go_symbols(path: Path) -> list[dict[str, Any]]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    symbols = []
    rel = str(path.relative_to(ROOT)).replace("\\", "/")

    for pattern, kind in _GO_PATTERNS:
        for m in pattern.finditer(src):
            name = m.group(1)
            if not name or len(name) < 2:
                continue
            line = src[:m.start()].count("\n") + 1
            symbols.append({"name": name, "kind": kind, "file": rel, "line": line})

    return symbols


# ── TypeScript/JS regex extractor ─────────────────────────────────────────────
# Lightweight regex — not a full TS parser, handles common patterns well.

_TS_PATTERNS = [
    (re.compile(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*[(<]'), "function"),
    (re.compile(r'(?:export\s+)?(?:abstract\s+)?class\s+(\w+)\b'),       "class"),
    (re.compile(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\('), "function"),
    (re.compile(r'^\s+(?:async\s+)?(\w+)\s*\([^)]*\)\s*[:{]', re.M),    "method"),
    (re.compile(r'(?:export\s+)?(?:interface|type)\s+(\w+)\b'),           "type"),
]


def _extract_ts_symbols(path: Path) -> list[dict[str, Any]]:
    try:
        src = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    symbols = []
    rel = str(path.relative_to(ROOT)).replace("\\", "/")

    for pattern, kind in _TS_PATTERNS:
        for m in pattern.finditer(src):
            name = m.group(1)
            if not name or len(name) < 2:
                continue
            line = src[:m.start()].count("\n") + 1
            symbols.append({"name": name, "kind": kind, "file": rel, "line": line})

    return symbols


# ── File walker ───────────────────────────────────────────────────────────────

def _iter_project_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in _SUPPORTED_EXTS:
            continue
        files.append(path)
        if len(files) >= _MAX_FILES:
            break
    return files


# ── Build ─────────────────────────────────────────────────────────────────────

def build_index(verbose: bool = False) -> dict[str, Any]:
    t0 = time.time()
    files = _iter_project_files()
    all_symbols: list[dict[str, Any]] = []

    for path in files:
        ext = path.suffix.lower()
        if ext == ".py":
            syms = _extract_python_symbols(path)
        elif ext == ".go":
            syms = _extract_go_symbols(path)
        else:
            syms = _extract_ts_symbols(path)
        all_symbols.extend(syms)

    index = {
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "file_count": len(files),
        "symbol_count": len(all_symbols),
        "symbols": all_symbols,
    }

    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    INDEX_FILE.write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")

    elapsed = time.time() - t0
    if verbose:
        print(f"{GREEN}Code index built: {len(all_symbols)} symbols from {len(files)} files in {elapsed:.2f}s{RESET}")
    return index


# ── Rebuild check ─────────────────────────────────────────────────────────────

def needs_rebuild() -> bool:
    """
    True if index is missing, > 1 hour old, or > 20 source files have been
    modified since the last build. Called by session-end.sh before rebuilding.
    """
    if not INDEX_FILE.exists():
        return True

    try:
        stat = INDEX_FILE.stat()
        age_seconds = time.time() - stat.st_mtime
        if age_seconds > 3600:
            return True

        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        built_ts = data.get("built_at", "")
        if not built_ts:
            return True

        import datetime
        built_at = datetime.datetime.fromisoformat(built_ts.replace("Z", "+00:00"))
        built_epoch = built_at.timestamp()

        modified_count = 0
        for path in _iter_project_files():
            if path.stat().st_mtime > built_epoch:
                modified_count += 1
                if modified_count > 20:
                    return True

        return False
    except Exception:
        return True


# ── Query ─────────────────────────────────────────────────────────────────────

def query_index(keywords: list[str], limit: int = 5) -> list[dict[str, Any]]:
    """
    Given a list of keyword strings, return up to `limit` symbol dicts
    whose name fuzzy-matches any keyword.
    Called by context_engine.py._inject_code_index().
    """
    if not INDEX_FILE.exists():
        return []

    try:
        data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

    symbols = data.get("symbols", [])
    if not symbols:
        return []

    kw_lower = [k.lower() for k in keywords]
    scored: list[tuple[int, dict[str, Any]]] = []

    for sym in symbols:
        name = sym["name"].lower()
        score = 0
        for kw in kw_lower:
            if kw == name:
                score += 3
            elif kw in name or name in kw:
                score += 1
        if score > 0:
            scored.append((score, sym))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:limit]]


# ── Format for injection ──────────────────────────────────────────────────────

def format_for_injection(results: list[dict[str, Any]]) -> str:
    if not results:
        return ""
    lines = ["**Code symbols:**"]
    for sym in results:
        kind = sym.get("kind", "symbol")
        name = sym.get("name", "?")
        file = sym.get("file", "?")
        line = sym.get("line", "?")
        parent = sym.get("parent")
        if parent:
            lines.append(f"- `{parent}.{name}` ({kind}) → {file}:{line}")
        else:
            lines.append(f"- `{name}` ({kind}) → {file}:{line}")
    return "\n".join(lines)


# ── Stats ─────────────────────────────────────────────────────────────────────

def _stats():
    if not INDEX_FILE.exists():
        print(f"{YELLOW}No index found. Run: python3 code_index.py build{RESET}")
        return
    data = json.loads(INDEX_FILE.read_text(encoding="utf-8"))
    print(f"Index: {INDEX_FILE}")
    print(f"Built: {data.get('built_at', '?')}")
    print(f"Files: {data.get('file_count', '?')}")
    print(f"Symbols: {data.get('symbol_count', '?')}")

    by_kind: dict[str, int] = {}
    for sym in data.get("symbols", []):
        k = sym.get("kind", "?")
        by_kind[k] = by_kind.get(k, 0) + 1
    for kind, count in sorted(by_kind.items()):
        print(f"  {kind}: {count}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"

    if cmd == "build":
        build_index(verbose=True)

    elif cmd == "query":
        keywords = sys.argv[2:] if len(sys.argv) > 2 else []
        if not keywords:
            print("Usage: code_index.py query <keyword> [keyword...]")
            sys.exit(1)
        results = query_index(keywords)
        if results:
            print(format_for_injection(results))
        else:
            print(f"{DIM}No symbols matched: {keywords}{RESET}")

    elif cmd == "stats":
        _stats()

    else:
        print(f"Usage: code_index.py [build|query|stats]")
        sys.exit(1)


if __name__ == "__main__":
    main()
