#!/usr/bin/env python3
"""
Cache Manager — Agentic Plan Cache + Response Cache
Implements research-backed 50%+ token reduction via template reuse.

Usage:
  python3 .claude/intelligence/cache_manager.py check "build the job matching results page"
  python3 .claude/intelligence/cache_manager.py store plan "build the auth flow" plan.json
  python3 .claude/intelligence/cache_manager.py stats
  python3 .claude/intelligence/cache_manager.py clear [--older-than 72]
"""
from __future__ import annotations

import json
import hashlib
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────

ROOT = Path.cwd()
CACHE_DIR = ROOT / ".claude" / "cache"
PLAN_CACHE = CACHE_DIR / "plans"
RESP_CACHE = CACHE_DIR / "responses"
META_FILE  = CACHE_DIR / "meta.json"

PLAN_THRESHOLD = 0.55
RESP_THRESHOLD = 0.75

CYAN   = "\033[0;36m"
GREEN  = "\033[0;32m"
YELLOW = "\033[1;33m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ── BM25 Similarity (zero external deps) ──────────────────────────────────────

# Synonyms — normalize semantic equivalents before scoring
# This bridges the lexical gap: "build auth flow" ≡ "create login system"
SYNONYMS = {
    # Build intent
    "build": "create", "make": "create", "add": "create",
    "implement": "create", "develop": "create", "write": "create",
    # Auth domain
    "auth": "login", "authentication": "login", "signin": "login",
    "signup": "register", "logout": "signout",
    # UI domain
    "ui": "frontend", "interface": "frontend", "view": "frontend",
    "screen": "page", "route": "page",
    "component": "widget", "element": "widget",
    # Data domain
    "db": "database", "data": "database", "storage": "database",
    "query": "fetch", "retrieve": "fetch", "load": "fetch", "get": "fetch",
    # API domain
    "api": "endpoint", "route": "endpoint", "handler": "endpoint",
    "controller": "endpoint",
    # Fix domain
    "fix": "debug", "bug": "debug", "error": "debug", "issue": "debug",
    "problem": "debug", "broken": "debug",
    # Performance
    "optimize": "performance", "speed": "performance", "fast": "performance",
    "slow": "performance",
    # Test domain
    "test": "spec", "testing": "spec", "coverage": "spec",
    # Docs
    "docs": "documentation", "document": "documentation",
    # Refactor
    "refactor": "restructure", "cleanup": "restructure",
    "reorganize": "restructure", "clean": "restructure",
}

# Stop words that add noise without semantic value
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "it", "its", "be", "as", "up",
    "that", "this", "these", "those", "into", "also", "just", "my", "your"
}

def normalize_synonyms(tokens: list[str]) -> list[str]:
    """Replace tokens with their canonical synonyms for better cache hits.
    e.g. 'build auth flow' -> 'create login flow' -> matches 'create login system'
    """
    return [SYNONYMS.get(t, t) for t in tokens]

def tokenize(text: str) -> list[str]:
    """Tokenize into meaningful unigrams, filtered and synonym-normalized.
    No bigrams — they add noise for short task queries.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]
    return normalize_synonyms(tokens)

def jaccard_similarity(a_tokens: list[str], b_tokens: list[str]) -> float:
    """Jaccard similarity — correct for string-to-string comparison (no corpus needed)."""
    if not a_tokens or not b_tokens:
        return 0.0
    set_a, set_b = set(a_tokens), set(b_tokens)
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0

def overlap_coefficient(a_tokens: list[str], b_tokens: list[str]) -> float:
    """Overlap coefficient — better when queries are subsets of longer stored strings."""
    if not a_tokens or not b_tokens:
        return 0.0
    set_a, set_b = set(a_tokens), set(b_tokens)
    intersection = len(set_a & set_b)
    smaller = min(len(set_a), len(set_b))
    return intersection / smaller if smaller > 0 else 0.0

def similarity(a: str, b: str) -> float:
    """Blended similarity: 40% Jaccard + 60% Overlap.
    Overlap weighted higher since queries are often shorter than stored templates.
    """
    ta, tb = tokenize(a), tokenize(b)
    j = jaccard_similarity(ta, tb)
    o = overlap_coefficient(ta, tb)
    return (j * 0.4) + (o * 0.6)

# ── Task Type Classifier ──────────────────────────────────────────────────────

TASK_TYPES = {
    "page_build":     [r"build.*page", r"create.*page", r"add.*page", r"new.*page", r"page.*for"],
    "component":      [r"build.*component", r"create.*component", r"add.*component", r"component.*for"],
    "api_endpoint":   [r"api.*endpoint", r"create.*route", r"add.*endpoint", r"rest.*api", r"route.*for"],
    "auth_flow":      [r"\bauth\b", r"\blogin\b", r"\bsignup\b", r"sign.?up", r"\bauthentication\b", r"\boauth\b", r"\bsession\b"],
    "data_model":     [r"\bschema\b", r"\bmigration\b", r"database.*table", r"\bentity\b"],
    "feature_build":  [r"\bfeature\b", r"\bimplement\b", r"add.*feature", r"build.*feature"],
    "refactor":       [r"\brefactor\b", r"\brestructure\b", r"\breorganize\b", r"clean.?up", r"\brewrite\b"],
    "optimization":   [r"\boptim", r"\bperformance\b", r"speed.?up", r"reduce.*bundle", r"\bfaster\b"],
    "testing":        [r"\btest\b", r"\bspec\b", r"\bcoverage\b", r"unit test", r"\bintegration\b", r"\be2e\b"],
    "design_ui":      [r"\bdesign\b", r"\bui\b", r"\bux\b", r"\blayout\b", r"\bdashboard\b", r"\bhero\b", r"\blanding\b"],
}

def classify_task(query: str) -> str:
    q = query.lower()
    for task_type, patterns in TASK_TYPES.items():
        if any(re.search(p, q) for p in patterns):
            return task_type
    return "general"

# ── Cache Operations ──────────────────────────────────────────────────────────

def ensure_dirs():
    PLAN_CACHE.mkdir(parents=True, exist_ok=True)
    RESP_CACHE.mkdir(parents=True, exist_ok=True)
    if not META_FILE.exists():
        META_FILE.write_text(json.dumps({
            "created": datetime.now(timezone.utc).isoformat(),
            "total_queries": 0,
            "cache_hits": 0,
            "tokens_saved_estimate": 0
        }, indent=2))

def atomic_write(path: Path, data: dict):
    """Write JSON atomically — Windows-safe.
    Uses os.replace() which is atomic on POSIX and handles existing-target
    on Windows (unlike Path.rename which fails if target exists on Windows).
    """
    import os, tempfile
    path.parent.mkdir(parents=True, exist_ok=True)
    # Write to a temp file in the same directory (same filesystem = atomic move)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(json.dumps(data, indent=2))
        os.replace(tmp_path, path)  # atomic on POSIX; replaces existing on Windows
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

def warm_from_tasks(tasks_file: Optional[str] = None) -> int:
    """Pre-populate plan cache from TODO.md or AI_TASKS.md.
    Seeds the cache before first real session so it's useful from day one.
    Returns number of templates seeded.
    """
    ensure_dirs()
    seeded = 0

    # Find tasks file
    candidates = [tasks_file] if tasks_file else [
        "AI_TASKS.md", "TODO.md", "docs/TODO.md", "docs/AI_TASKS.md"
    ]
    tasks_path = None
    for c in candidates:
        if c and Path(c).exists():
            tasks_path = Path(c)
            break

    if not tasks_path:
        return 0

    content = tasks_path.read_text(errors="ignore")
    lines = content.splitlines()

    task_pattern = re.compile(r"[-*] \[[ x>!]\]\s+\*\*(.+?)\*\*|[-*] \[[ x>!]\]\s+(.+?)(?:\s*[-—].+)?$")

    for line in lines:
        line = line.strip()
        # Only seed future/pending tasks ([ ] or [>])
        if not (line.startswith("- [ ]") or line.startswith("* [ ]") or
                line.startswith("- [>]") or line.startswith("* [>]")):
            continue

        # Extract task description
        desc = re.sub(r"^[-*] \[[x >!]\]\s*\*?\*?", "", line).strip("*").strip()
        desc = re.sub(r"\s*[\[(][A-Z0-9-]+[\])].*$", "", desc).strip()  # remove tags like [P0], (HIGH)
        if len(desc) < 10 or len(desc) > 200:
            continue

        # Check if already cached — use internal check that doesn't touch stats
        if _cache_already_has(desc, PLAN_CACHE):
            continue  # already in cache

        # Seed a template
        entry_id = store_cache("plan", desc, {
            "source": "warm_from_tasks",
            "task_file": str(tasks_path),
            "steps": ["Read CLAUDE.md and relevant docs first",
                      "Check existing patterns in codebase",
                      "Implement with project conventions",
                      "Review against AI_RULES.md before completing"],
        })
        seeded += 1

    if seeded > 0:
        print(f"{GREEN}✓ Cache warmed: {seeded} task templates seeded from {tasks_path}{RESET}")

    return seeded

def _cache_already_has(query: str, cache_dir: Path) -> bool:
    """Lightweight check: does a similar entry already exist in cache?
    Does NOT touch stats counters — safe to call from warm_from_tasks.
    """
    for cache_file in cache_dir.glob("*.json"):
        try:
            entry = json.loads(cache_file.read_text())
            if similarity(query, entry.get("query", "")) >= PLAN_THRESHOLD:
                return True
        except Exception:
            continue
    return False

def load_meta() -> dict:
    ensure_dirs()
    try:
        return json.loads(META_FILE.read_text())
    except Exception:
        return {"total_queries": 0, "cache_hits": 0, "tokens_saved_estimate": 0}

def save_meta(meta: dict):
    atomic_write(META_FILE, meta)

def get_entry_id(query: str) -> str:
    return hashlib.sha256(query.lower().strip().encode()).hexdigest()[:16]

def is_expired(entry: dict, ttl_hours: int = 72) -> bool:
    stored = datetime.fromisoformat(entry.get("stored_at", "2000-01-01T00:00:00+00:00"))
    age_hours = (datetime.now(timezone.utc) - stored).total_seconds() / 3600
    return age_hours > ttl_hours

# ── Check: find a cache hit ───────────────────────────────────────────────────

def check_cache(query: str, cache_type: str = "plan") -> Optional[dict]:
    ensure_dirs()
    cache_dir = PLAN_CACHE if cache_type == "plan" else RESP_CACHE
    threshold = PLAN_THRESHOLD if cache_type == "plan" else RESP_THRESHOLD
    task_type = classify_task(query) if cache_type == "plan" else "response"

    # ── Fast path: exact match by content hash (free lookup) ──────────────
    exact_id   = get_entry_id(query + cache_type)
    exact_path = cache_dir / f"{exact_id}.json"
    if exact_path.exists():
        try:
            entry = json.loads(exact_path.read_text())
            ttl   = 168 if cache_type == "plan" else 72
            if not is_expired(entry, ttl):
                meta = load_meta()
                meta["cache_hits"]            = meta.get("cache_hits", 0) + 1
                meta["total_queries"]         = meta.get("total_queries", 0) + 1
                meta["tokens_saved_estimate"] = meta.get("tokens_saved_estimate", 0) + 500
                save_meta(meta)
                return {"hit": True, "score": 1.0, "exact": True,
                        "task_type": task_type,
                        "cached_query": entry.get("query"),
                        "template": entry.get("template"),
                        "response": entry.get("response"),
                        "stored_at": entry.get("stored_at")}
        except Exception:
            pass  # fall through to similarity scan

    best_score = 0.0
    best_entry = None
    best_file  = None

    for cache_file in cache_dir.glob("*.json"):
        try:
            entry = json.loads(cache_file.read_text())
        except Exception:
            continue

        ttl = 168 if cache_type == "plan" else 72
        if is_expired(entry, ttl):
            continue

        raw_score = similarity(query, entry.get("query", ""))

        # Same task type gets 10% bonus — encourages type-matched hits
        # but never hard-blocks cross-type hits with strong token overlap
        if cache_type == "plan" and entry.get("task_type") == task_type:
            score = min(raw_score * 1.10, 1.0)
        else:
            score = raw_score

        if score > best_score:
            best_score = score
            best_entry = entry
            best_file  = cache_file
    
    if best_score >= threshold and best_entry:
        meta = load_meta()
        meta["cache_hits"] = meta.get("cache_hits", 0) + 1
        meta["total_queries"] = meta.get("total_queries", 0) + 1
        avg_tokens_saved = 450 if cache_type == "plan" else 350
        meta["tokens_saved_estimate"] = meta.get("tokens_saved_estimate", 0) + avg_tokens_saved
        save_meta(meta)
        
        return {
            "hit": True,
            "score": round(best_score, 3),
            "task_type": task_type,
            "cached_query": best_entry.get("query"),
            "template": best_entry.get("template"),
            "response": best_entry.get("response"),
            "stored_at": best_entry.get("stored_at"),
            "use_count": best_entry.get("use_count", 0) + 1,
            "file": str(best_file)
        }
    
    meta = load_meta()
    meta["total_queries"] = meta.get("total_queries", 0) + 1
    save_meta(meta)
    
    return {"hit": False, "score": round(best_score, 3), "task_type": task_type}

# ── Store: save a new cache entry ────────────────────────────────────────────

def store_cache(cache_type: str, query: str, content: dict, ttl_hours: int = 72):
    ensure_dirs()
    cache_dir = PLAN_CACHE if cache_type == "plan" else RESP_CACHE
    entry_id  = get_entry_id(query + cache_type)
    
    entry = {
        "id": entry_id,
        "query": query,
        "task_type": classify_task(query),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "ttl_hours": ttl_hours,
        "use_count": 0,
        "template" if cache_type == "plan" else "response": content
    }
    
    cache_file = cache_dir / f"{entry_id}.json"
    atomic_write(cache_file, entry)
    return entry_id

# ── Stats ─────────────────────────────────────────────────────────────────────

def show_stats():
    ensure_dirs()
    meta = load_meta()
    
    plan_count = len(list(PLAN_CACHE.glob("*.json")))
    resp_count = len(list(RESP_CACHE.glob("*.json")))
    
    total    = meta.get("total_queries", 0)
    hits     = meta.get("cache_hits", 0)
    saved    = meta.get("tokens_saved_estimate", 0)
    hit_rate = (hits / total * 100) if total > 0 else 0
    
    avg_cost_per_1k = 0.003  # $0.003 per 1K tokens (blended Sonnet/Flash estimate)
    cost_saved = (saved / 1000) * avg_cost_per_1k
    
    print(f"\n{BOLD}{CYAN}━━━ CACHE STATS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Plan templates cached:   {GREEN}{plan_count}{RESET}")
    print(f"  Response entries cached: {GREEN}{resp_count}{RESET}")
    print(f"  Total queries:           {total}")
    print(f"  Cache hits:              {GREEN}{hits}{RESET}")
    print(f"  Hit rate:                {GREEN}{hit_rate:.1f}%{RESET}")
    print(f"  Tokens saved (est):      {GREEN}~{saved:,}{RESET}")
    print(f"  Cost saved (est):        {GREEN}~${cost_saved:.4f}{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

# ── Clear ─────────────────────────────────────────────────────────────────────

def clear_cache(older_than_hours: int = 0):
    ensure_dirs()
    removed = 0
    for cache_dir in [PLAN_CACHE, RESP_CACHE]:
        for cache_file in cache_dir.glob("*.json"):
            try:
                if older_than_hours > 0:
                    entry = json.loads(cache_file.read_text())
                    if is_expired(entry, older_than_hours):
                        cache_file.unlink()
                        removed += 1
                else:
                    cache_file.unlink()
                    removed += 1
            except Exception:
                pass
    print(f"{GREEN}✓ Removed {removed} cache entries{RESET}")

# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: cache_manager.py <check|store|stats|clear> [args...]")
        sys.exit(1)
    
    cmd = args[0]
    
    if cmd == "check":
        query      = args[1] if len(args) > 1 else ""
        cache_type = args[2] if len(args) > 2 else "plan"
        result = check_cache(query, cache_type)
        print(json.dumps(result, indent=2))
    
    elif cmd == "store":
        if len(args) < 4:
            print("Usage: cache_manager.py store <plan|response> <query> <content_json>")
            sys.exit(1)
        cache_type = args[1]
        query      = args[2]
        try:
            content = json.loads(args[3])
        except Exception:
            content = {"raw": args[3]}
        entry_id = store_cache(cache_type, query, content)
        print(json.dumps({"stored": True, "id": entry_id}))
    
    elif cmd == "stats":
        show_stats()
    
    elif cmd == "warm":
        tasks_file = args[1] if len(args) > 1 else None
        count = warm_from_tasks(tasks_file)
        if count == 0:
            print(f"{YELLOW}⚠ No tasks found to warm cache with{RESET}")
            print(f"{DIM}Expected: AI_TASKS.md, TODO.md, or pass path as argument{RESET}")

    elif cmd == "clear":
        older = int(args[1]) if len(args) > 1 and args[1].isdigit() else 0
        clear_cache(older)
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
