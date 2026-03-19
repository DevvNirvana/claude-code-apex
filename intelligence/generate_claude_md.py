#!/usr/bin/env python3
"""
CLAUDE.md Auto-Generator for APEX
===================================
Scans the project and generates a ready-to-use CLAUDE.md.
Called by /setup on first run, and by /init when CLAUDE.md is missing.

Usage:
  python3 .claude/intelligence/generate_claude_md.py           # generate + write
  python3 .claude/intelligence/generate_claude_md.py --preview # print only
"""
from __future__ import annotations
import json, sys, os, re
from pathlib import Path

ROOT = Path.cwd()
APEX_DIR = ROOT / ".claude"

GREEN = "\033[0;32m"; CYAN = "\033[0;36m"; YELLOW = "\033[1;33m"
BOLD = "\033[1m"; DIM = "\033[2m"; RESET = "\033[0m"

def load_stack_profile() -> dict:
    p = APEX_DIR / "config" / "stack-profile.json"
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            pass
    return {}

def detect_project_name() -> str:
    """Try package.json name, then folder name."""
    pkg = ROOT / "package.json"
    if pkg.exists():
        try:
            d = json.loads(pkg.read_text())
            name = d.get("name", "")
            if name and name != "my-app":
                return name.replace("-", " ").replace("_", " ").title()
        except Exception:
            pass
    return ROOT.name.replace("-", " ").replace("_", " ").title()

def detect_description() -> str:
    """Extract description from package.json or README."""
    pkg = ROOT / "package.json"
    if pkg.exists():
        try:
            d = json.loads(pkg.read_text())
            desc = d.get("description", "")
            if desc and len(desc) > 10:
                return desc
        except Exception:
            pass
    readme = ROOT / "README.md"
    if readme.exists():
        lines = readme.read_text(errors="ignore").splitlines()
        for line in lines[:20]:
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 20:
                return line[:120]
    return ""

def detect_existing_docs() -> dict:
    """Find doc files that actually exist."""
    candidates = {
        "Context & Architecture": [
            "docs/AI_CONTEXT.md", "docs/ARCHITECTURE.md",
            "docs/DESIGN_DOC.md", "ARCHITECTURE.md"
        ],
        "Rules & Conventions": [
            "docs/AI_RULES.md", "docs/CONVENTIONS.md", "CONTRIBUTING.md"
        ],
        "Tasks & Roadmap": [
            "docs/AI_TASKS.md", "docs/TODO.md", "TODO.md"
        ],
        "Session History": ["docs/SESSION_LOG.md", "SESSION_LOG.md"],
        "PRD": ["docs/PRD.md", "PRD.md"],
        "Tech Stack": ["docs/TECH_STACK.md", "TECH_STACK.md"],
        "Project Vision": ["PROJECT_PLAN.md", "docs/PROJECT_PLAN.md"],
    }
    found = {}
    for label, paths in candidates.items():
        for p in paths:
            if (ROOT / p).exists():
                found[label] = p
                break
    return found

def detect_hard_rules(profile: dict) -> list:
    """Generate framework-appropriate Hard Rules."""
    fw = profile.get("framework", "")
    lang = profile.get("language", "")
    db = profile.get("db", "")
    rules = [
        "Never commit .env or .env.local — use .env.example with placeholder values only",
        "Never push directly to main — feature branches only",
    ]
    if "typescript" in lang or fw in ("nextjs", "react", "vue", "sveltekit"):
        rules.append("Never use `any` TypeScript type — use `unknown` and narrow it")
    if "supabase" in (db or ""):
        rules.append("Never use Supabase service key in client components — anon key only")
        rules.append("Never create API routes for data operations — use Supabase client directly")
    if fw in ("nextjs", "remix"):
        rules.append("Never put sensitive logic in client components — keep it in server components or actions")
    if fw == "django":
        rules.append("Never use raw string interpolation in SQL queries — use parameterized queries only")
    if fw in ("rails", "sinatra"):
        rules.append("Never use permit! in strong parameters — always whitelist explicitly")
    if fw == "go":
        rules.append("Never ignore error return values — handle or explicitly discard with a comment")
    rules.append("Never hardcode API keys, secrets, or credentials in source files")
    return rules[:8]  # cap at 8

def detect_conventions(profile: dict) -> list:
    """Generate stack-appropriate Critical Conventions."""
    fw = profile.get("framework", "")
    db_orm = profile.get("db_orm", "")
    db = profile.get("db", "")
    convs = []
    if fw in ("nextjs", "react"):
        convs.append("Server Components by default — `use client` only for interactivity or browser APIs")
    if "prisma" in (db_orm or ""):
        convs.append("All DB queries through `lib/db.ts` — never import Prisma directly in components")
    elif "supabase" in (db or ""):
        convs.append("All Supabase queries through `lib/supabase/queries.ts` — never inline in components")
    elif "django" in fw:
        convs.append("All DB queries in model managers or service layer — never raw queries in views")
    elif "rails" in fw:
        convs.append("Business logic in models and service objects — never in controllers")
    convs.append("Errors must be user-readable strings — never surface raw Error objects or stack traces to UI")
    if profile.get("has_typescript"):
        convs.append("Types in dedicated files — never inline complex types in components")
    return convs[:6]

def detect_good_pattern(profile: dict) -> str:
    """Return the most appropriate canonical pattern."""
    fw = profile.get("framework", "")
    lang = profile.get("language", "")
    db_orm = profile.get("db_orm", "")
    db = profile.get("db", "")

    if fw == "nextjs" and "supabase" in (db or ""):
        return '''```typescript
// lib/supabase/queries.ts — all DB operations here, never inline
export async function getUserById(id: string) {
  const { data, error } = await supabase
    .from("users")
    .select("*")
    .eq("id", id)
    .single();
  if (error) { console.warn("[getUserById]", error.message); return null; }
  return data;
}
```'''
    elif fw == "nextjs":
        return '''```typescript
// Server Action pattern (preferred for mutations)
"use server";
import { revalidatePath } from "next/cache";

export async function createItem(data: CreateItemInput) {
  try {
    const item = await db.item.create({ data });
    revalidatePath("/items");
    return { success: true, item };
  } catch (err) {
    return { success: false, error: "Failed to create item." };
  }
}
```'''
    elif fw == "django":
        return '''```python
# views.py — thin views, logic in service layer
from django.http import JsonResponse
from .services import get_user_profile

def user_profile(request, user_id):
    try:
        profile = get_user_profile(user_id)
        return JsonResponse({"data": profile})
    except UserNotFoundError:
        return JsonResponse({"error": "User not found"}, status=404)
```'''
    elif fw == "rails":
        return '''```ruby
# app/services/user_registration_service.rb
class UserRegistrationService
  def initialize(params); @params = params; end

  def call
    ActiveRecord::Base.transaction do
      user = User.create!(@params.slice(:email, :name, :password))
      WelcomeMailer.with(user: user).welcome_email.deliver_later
      user
    end
  rescue ActiveRecord::RecordInvalid => e
    { error: e.message }
  end
end
```'''
    elif fw == "go":
        return '''```go
// internal/handler/user.go — handler delegates to service
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()
    user, err := h.service.GetUser(ctx, chi.URLParam(r, "id"))
    if err != nil {
        http.Error(w, "user not found", http.StatusNotFound)
        return
    }
    json.NewEncoder(w).Encode(user)
}
```'''
    else:
        return f'''```{lang or "javascript"}
// Canonical pattern for this project
// Replace with a real example from your codebase after scaffolding
export async function fetchData(id) {{
  try {{
    const result = await db.findById(id);
    return {{ data: result, error: null }};
  }} catch (err) {{
    console.warn("[fetchData]", err.message);
    return {{ data: null, error: err.message }};
  }}
}}
```'''

def generate(profile: dict) -> str:
    """Build the complete CLAUDE.md content."""
    name = detect_project_name()
    desc = detect_description()
    fw = profile.get("framework", "unknown")
    fw_ver = profile.get("framework_version", "")
    lang = profile.get("language", "unknown")
    db = profile.get("db", "")
    db_orm = profile.get("db_orm", "")
    auth = profile.get("auth_library", "")
    pm = profile.get("package_manager", "npm")
    cmds = profile.get("build_commands", {})
    deploy = profile.get("deploy_target", "")
    docs = detect_existing_docs()
    hard_rules = detect_hard_rules(profile)
    conventions = detect_conventions(profile)
    good_pattern = detect_good_pattern(profile)

    # Project line
    if desc:
        project_line = f"{name} is {desc}."
    else:
        project_line = f"{name} — [describe what this does and who uses it in 2 sentences]"

    # Commands section
    cmd_lines = []
    for k in ("dev", "build", "test", "lint"):
        v = cmds.get(k)
        if v:
            labels = {"dev": "dev server", "build": "production build",
                      "test": "run tests", "lint": "lint + type check"}
            cmd_lines.append(f"{v:<32} # {labels[k]}")
    commands_block = "\n".join(cmd_lines) if cmd_lines else f"{pm} run dev\n{pm} run build"

    # Stack section
    stack_lines = [f"- Language:   {lang.title()}"]
    fw_str = fw
    if fw_ver:
        fw_str = f"{fw} v{fw_ver}"
    router = profile.get("router", "")
    if router:
        fw_str += f" ({router})"
    stack_lines.append(f"- Framework:  {fw_str}")
    if db:
        db_str = db
        if db_orm:
            db_str += f" via {db_orm}"
        stack_lines.append(f"- Database:   {db_str}")
    if auth:
        stack_lines.append(f"- Auth:       {auth}")
    if profile.get("tailwind"):
        stack_lines.append(f"- Styling:    Tailwind CSS v{profile.get('tailwind_version', '3')}")
    if deploy:
        stack_lines.append(f"- Deploy:     {deploy}")

    # Architecture — use domain map
    domain_map = profile.get("domain_map", {})
    arch_lines = []
    for role, paths in list(domain_map.items())[:5]:
        if paths:
            arch_lines.append(f"├── {paths[0]:<25} # {role}")
    arch_block = "\n".join(arch_lines) if arch_lines else "├── src/"

    # Docs section
    docs_lines = []
    for label, path in docs.items():
        docs_lines.append(f"- {label+':':28} `{path}`")
    if not docs_lines:
        docs_lines = [
            "- Tasks & Roadmap:            `TODO.md`",
            "- Context & Architecture:     `docs/ARCHITECTURE.md`",
        ]

    # Hard rules
    rules_block = "\n".join(f"- Never {r.lstrip('Never ').lstrip('never ')}"
                             if not r.startswith("Never") else f"- {r}"
                             for r in hard_rules)

    # Conventions
    convs_block = "\n".join(f"- {c}" for c in conventions)

    lines = f"""# CLAUDE.md — {name}
<!-- Keep under 80 lines. Updated by APEX /setup -->

## Project
{project_line}

## Commands
```bash
{commands_block}
```

## Stack
{chr(10).join(stack_lines)}

## Architecture
```
{arch_block}
```

## Critical Conventions
{convs_block}

## Hard Rules
{rules_block}

## Good Pattern
{good_pattern}

## Docs
{chr(10).join(docs_lines)}"""

    return lines

def main():
    preview = "--preview" in sys.argv

    # Load or generate stack profile
    profile = load_stack_profile()
    if not profile:
        # Run detection inline
        sys.path.insert(0, str(APEX_DIR / "intelligence"))
        try:
            import detect_stack as ds
            profile = ds._build_profile()
        except Exception as e:
            print(f"{YELLOW}⚠ Stack detection failed: {e}{RESET}")
            profile = {}

    content = generate(profile)
    line_count = content.count("\n") + 1

    if preview or "--preview" in sys.argv:
        print(content)
        print(f"\n{DIM}Lines: {line_count}{RESET}")
        return

    out = ROOT / "CLAUDE.md"
    if out.exists() and "--force" not in sys.argv:
        print(f"{YELLOW}⚠ CLAUDE.md already exists. Use --force to overwrite.{RESET}")
        print(f"{DIM}  Preview: python3 .claude/intelligence/generate_claude_md.py --preview{RESET}")
        return

    out.write_text(content, encoding="utf-8")
    print(f"{GREEN}✓ CLAUDE.md generated ({line_count} lines){RESET}")
    print(f"  {DIM}Review and customise: code CLAUDE.md{RESET}")
    print(f"  {DIM}Sections marked [describe...] need your input{RESET}")

if __name__ == "__main__":
    main()
