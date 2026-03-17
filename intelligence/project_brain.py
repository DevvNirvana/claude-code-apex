#!/usr/bin/env python3
"""
Project Brain — Temporal Fact Store
=====================================
Architecture basis: Graphiti temporal fact management + Mem0 selective
retrieval research. Facts have validity windows, conflict detection,
and are queried by relevance — not loaded wholesale into context.

Three categories (strictly enforced to prevent scope creep):
  constraint — hard architectural rules ("no API routes", "use Supabase directly")
  pattern    — proven code patterns that should be reused
  decision   — architectural decisions made in sessions
  correction — explicit developer corrections from taste signals

Data format: JSON-lines (.jsonl) for append-only storage.
Each fact: {id, content, category, confidence, source, author,
            created_at, invalidated_at, supersedes, project, tags}

Multi-author: author field supports team mode in v5.

Usage:
  python3 .claude/intelligence/project_brain.py write <json_file>
  python3 .claude/intelligence/project_brain.py read "auth pattern"
  python3 .claude/intelligence/project_brain.py sync
  python3 .claude/intelligence/project_brain.py status
  python3 .claude/intelligence/project_brain.py conflicts
"""
import json, sys, os, re, tempfile, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

ROOT      = Path.cwd()
BRAIN_DIR = ROOT / ".claude" / "brain"
FACTS_FILE   = BRAIN_DIR / "facts.jsonl"
CONFLICTS_LOG = BRAIN_DIR / "brain_conflicts.log"
GLOBAL_BRAIN = Path.home() / ".apex" / "global-patterns.json"

CYAN  = "\033[0;36m"; GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"
DIM   = "\033[2m";    BOLD  = "\033[1m";    RESET  = "\033[0m"
RED   = "\033[0;31m"

VALID_CATEGORIES = {"constraint", "pattern", "decision", "correction"}

# Token budget: brain injection must not exceed this per command
BRAIN_TOKEN_BUDGET = 800  # ~600 words

STOP_WORDS = {
    "a","an","the","and","or","in","on","to","for","of","with","by",
    "is","it","its","be","as","up","that","this","these","those","we","us"
}


def _tokenize(text: str) -> set:
    words = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    return {w for w in words if len(w) > 2 and w not in STOP_WORDS}


def _similarity(a: str, b: str) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    return (0.4 * inter / len(ta | tb)) + (0.6 * inter / min(len(ta), len(tb)))


def _atomic_append(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _atomic_write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except: pass
        raise


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def _new_fact_id(content: str) -> str:
    return hashlib.sha256(
        (content + datetime.now(timezone.utc).isoformat()).encode()
    ).hexdigest()[:16]


# ── Core operations ───────────────────────────────────────────────────────────

def load_all_facts() -> list[dict]:
    """Load all facts from the JSONL file."""
    if not FACTS_FILE.exists():
        return []
    facts = []
    for line in FACTS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                facts.append(json.loads(line))
            except Exception:
                continue
    return facts


def load_valid_facts() -> list[dict]:
    """Return only facts that have not been invalidated."""
    return [f for f in load_all_facts() if f.get("invalidated_at") is None]


def brain_write(
    content: str,
    category: str,
    source: str = "session",
    confidence: float = 0.9,
    author: str = "developer",
    tags: list = None,
) -> dict:
    """
    Write a fact to the brain with conflict detection.
    If a similar fact exists, the old one is invalidated.
    """
    if category not in VALID_CATEGORIES:
        print(f"{RED}Invalid category: {category}. "
              f"Use: {', '.join(VALID_CATEGORIES)}{RESET}")
        sys.exit(1)

    FACTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    valid_facts = load_valid_facts()

    # Conflict detection: find similar existing facts
    conflicts = []
    for existing in valid_facts:
        if existing.get("category") != category:
            continue
        sim = _similarity(content, existing.get("content", ""))
        if sim >= 0.80:
            conflicts.append((existing, sim))

    supersedes_id = None
    if conflicts:
        # Sort by similarity — most similar first
        conflicts.sort(key=lambda x: -x[1])
        top_conflict, sim = conflicts[0]

        # Check if content is actually different (not just a re-statement)
        if sim < 0.98:  # Not exact — this is a real update
            old_id = top_conflict["id"]
            supersedes_id = old_id

            # Mark old fact as invalidated by rewriting the full file
            _invalidate_fact(old_id, new_content=content)

            # Log the conflict
            log_msg = (f"{datetime.now(timezone.utc).isoformat()} | "
                       f"CONFLICT [{category}] | "
                       f"Old: '{top_conflict['content'][:80]}' | "
                       f"New: '{content[:80]}' | "
                       f"Similarity: {sim:.2f}\n")
            _atomic_append(CONFLICTS_LOG, log_msg)
            print(f"{YELLOW}⚠ Conflict detected (sim={sim:.2f}) — "
                  f"old fact invalidated{RESET}")

    fact = {
        "id":             _new_fact_id(content),
        "content":        content,
        "category":       category,
        "confidence":     confidence,
        "source":         source,
        "author":         author,
        "project":        ROOT.name,
        "tags":           tags or [],
        "created_at":     datetime.now(timezone.utc).isoformat(),
        "invalidated_at": None,
        "supersedes":     supersedes_id,
    }

    _atomic_append(FACTS_FILE, json.dumps(fact))
    print(f"{GREEN}✓ Brain fact written [{category}]{RESET}")
    print(f"  {content[:80]}")
    return fact


def _invalidate_fact(fact_id: str, new_content: str = ""):
    """Mark a fact as invalidated by rewriting the file."""
    if not FACTS_FILE.exists():
        return
    facts = load_all_facts()
    updated = []
    for f in facts:
        if f["id"] == fact_id and f.get("invalidated_at") is None:
            f["invalidated_at"] = datetime.now(timezone.utc).isoformat()
            f["_superseded_by_content"] = new_content[:80]
        updated.append(f)
    # Rewrite the file atomically — prevents data loss on interrupt
    content = "\n".join(json.dumps(f) for f in updated) + "\n"
    fd, tmp_path = tempfile.mkstemp(dir=FACTS_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fp:
            fp.write(content)
        os.replace(tmp_path, FACTS_FILE)
    except Exception:
        try: os.unlink(tmp_path)
        except OSError: pass
        raise


def brain_read(
    query: str,
    category: Optional[str] = None,
    token_budget: int = BRAIN_TOKEN_BUDGET,
) -> list[dict]:
    """
    Retrieve relevant valid facts within token budget.
    Sorted by relevance × confidence.
    """
    valid = load_valid_facts()

    if category:
        valid = [f for f in valid if f.get("category") == category]

    # Score each fact
    scored = []
    for f in valid:
        sim = _similarity(query, f.get("content", ""))
        # Also match against tags
        tag_match = any(_similarity(query, tag) > 0.5
                        for tag in f.get("tags", []))
        relevance = max(sim, 0.3 if tag_match else 0)
        if relevance > 0.15:
            scored.append({**f, "_relevance": round(relevance, 3)})

    scored.sort(key=lambda x: (
        -x["_relevance"],
        -x.get("confidence", 0),
        x.get("created_at", "")  # newer preferred for equal scores
    ))

    # Apply token budget
    result = []
    used_tokens = 0
    for fact in scored:
        est = _estimate_tokens(fact["content"])
        if used_tokens + est > token_budget:
            break
        result.append(fact)
        used_tokens += est

    return result


def brain_sync():
    """
    Auto-scan the codebase and upsert facts from observed evidence.
    Runs at the start of each session (called by /init).
    """
    print(f"\n{CYAN}Syncing project brain...{RESET}")
    synced = 0

    # Read CLAUDE.md for constraints
    claude_md = ROOT / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text(encoding="utf-8", errors="ignore")
        # Extract hard rules section
        hard_rules_match = re.search(
            r"## Hard Rules.*?\n(.*?)(?=\n##|\Z)", content, re.DOTALL
        )
        if hard_rules_match:
            rules_text = hard_rules_match.group(1)
            for line in rules_text.splitlines():
                line = line.strip().lstrip("- *")
                if len(line) > 20 and line.lower().startswith("never"):
                    brain_write(
                        content    = line,
                        category   = "constraint",
                        source     = "CLAUDE.md",
                        confidence = 1.0,
                        author     = "system",
                    )
                    synced += 1

    # Read stack profile for patterns
    stack_profile = ROOT / ".claude" / "config" / "stack-profile.json"
    if stack_profile.exists():
        try:
            profile = json.loads(stack_profile.read_text())
            fw  = profile.get("framework", "")
            ver = profile.get("framework_version", "")
            db  = profile.get("db", "")
            if fw:
                fact = f"Project uses {fw}{' v' + ver if ver else ''}"
                if db:
                    fact += f" with {db}"
                brain_write(
                    content    = fact,
                    category   = "constraint",
                    source     = "stack-profile.json",
                    confidence = 1.0,
                    author     = "system",
                    tags       = ["stack", fw],
                )
                synced += 1
        except Exception:
            pass

    print(f"{GREEN}✓ Brain sync complete: {synced} facts upserted{RESET}")
    return synced


def format_for_injection(facts: list[dict]) -> str:
    """Format facts as compact context for command injection."""
    if not facts:
        return ""
    by_cat = {}
    for f in facts:
        cat = f["category"]
        by_cat.setdefault(cat, []).append(f["content"])

    lines = ["\n## Project Brain Context\n"]
    cat_labels = {
        "constraint": "⛔ Hard Constraints",
        "pattern":    "✅ Proven Patterns",
        "decision":   "📋 Architectural Decisions",
        "correction": "🔧 Developer Corrections",
    }
    for cat in ["constraint", "decision", "pattern", "correction"]:
        if cat in by_cat:
            lines.append(f"**{cat_labels[cat]}:**")
            for c in by_cat[cat]:
                lines.append(f"- {c}")
            lines.append("")
    return "\n".join(lines)


def show_status():
    all_facts   = load_all_facts()
    valid_facts = load_valid_facts()
    inv_facts   = [f for f in all_facts if f.get("invalidated_at")]

    by_cat = {}
    for f in valid_facts:
        cat = f.get("category", "unknown")
        by_cat[cat] = by_cat.get(cat, 0) + 1

    print(f"\n{BOLD}{CYAN}━━━ PROJECT BRAIN STATUS ━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Total facts:       {len(all_facts)}")
    print(f"  Valid facts:       {GREEN}{len(valid_facts)}{RESET}")
    print(f"  Invalidated:       {DIM}{len(inv_facts)}{RESET}")
    for cat, count in sorted(by_cat.items()):
        print(f"  {cat:15}: {count}")
    conflicts = CONFLICTS_LOG.exists() and CONFLICTS_LOG.stat().st_size > 0
    if conflicts:
        conflict_count = sum(1 for line in CONFLICTS_LOG.read_text().splitlines() if line)
        print(f"  Conflicts logged:  {YELLOW}{conflict_count}{RESET}")
    global_exists = GLOBAL_BRAIN.exists()
    if global_exists:
        try:
            g = json.loads(GLOBAL_BRAIN.read_text())
            print(f"  Global patterns:   {len(g.get('patterns', []))}")
        except Exception:
            pass
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def show_conflicts():
    if not CONFLICTS_LOG.exists() or CONFLICTS_LOG.stat().st_size == 0:
        print(f"{DIM}No conflicts logged.{RESET}")
        return
    print(f"\n{BOLD}{YELLOW}━━━ BRAIN CONFLICTS ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    for line in CONFLICTS_LOG.read_text().splitlines()[-20:]:
        if line.strip():
            print(f"  {line}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def list_facts(category: Optional[str] = None, limit: int = 30):
    facts = load_valid_facts()
    if category:
        facts = [f for f in facts if f["category"] == category]
    facts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    print(f"\n{BOLD}{CYAN}━━━ BRAIN FACTS ({len(facts)}) ━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    for f in facts[:limit]:
        cat_colors = {"constraint": RED, "pattern": GREEN,
                      "decision": CYAN, "correction": YELLOW}
        c = cat_colors.get(f["category"], "")
        ts = f.get("created_at", "")[:10]
        print(f"  {DIM}{ts}{RESET}  {c}{f['category'][:10]:10}{RESET}  "
              f"conf={f.get('confidence',0):.1f}  {f['content'][:60]}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def promote_to_global(fact_id: str):
    """Promote a high-quality fact to ~/.apex/global-patterns.json"""
    facts = load_valid_facts()
    target = next((f for f in facts if f["id"] == fact_id), None)
    if not target:
        print(f"{RED}Fact {fact_id} not found{RESET}")
        return

    global_data = {}
    if GLOBAL_BRAIN.exists():
        try:
            global_data = json.loads(GLOBAL_BRAIN.read_text())
        except Exception:
            pass

    patterns = global_data.get("patterns", [])
    # Deduplicate
    existing_ids = {p.get("id") for p in patterns}
    if target["id"] not in existing_ids:
        patterns.append({**target, "promoted_from": ROOT.name,
                         "promoted_at": datetime.now(timezone.utc).isoformat()})
        global_data["patterns"] = patterns
        global_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        _atomic_write_json(GLOBAL_BRAIN, global_data)
        print(f"{GREEN}✓ Fact promoted to global store{RESET}")
    else:
        print(f"{DIM}Fact already in global store{RESET}")


def main():
    args = sys.argv[1:]
    if not args or args[0] == "status":
        show_status()
        return

    cmd = args[0]
    if cmd == "write":
        if len(args) < 2:
            print("Usage: project_brain.py write <json_file_or_inline_json>")
            sys.exit(1)
        try:
            data = json.loads(Path(args[1]).read_text()) if Path(args[1]).exists() else json.loads(args[1])
        except Exception:
            # Treat as plain content string
            data = {"content": args[1], "category": args[2] if len(args) > 2 else "decision"}
        brain_write(**data)

    elif cmd == "read":
        query    = args[1] if len(args) > 1 else ""
        category = args[2] if len(args) > 2 else None
        facts = brain_read(query, category=category)
        if facts:
            print(format_for_injection(facts))
        else:
            print(f"{DIM}No relevant facts found for: {query}{RESET}")

    elif cmd == "sync":
        brain_sync()

    elif cmd == "list":
        category = args[1] if len(args) > 1 else None
        list_facts(category)

    elif cmd == "conflicts":
        show_conflicts()

    elif cmd == "promote":
        if len(args) < 2:
            print("Usage: project_brain.py promote <fact_id>")
            sys.exit(1)
        promote_to_global(args[1])

    else:
        print(f"Unknown: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
