#!/usr/bin/env python3
"""
Framework Lint — checks generated code against framework guidelines.
Run from project root:
  python3 .claude/skills/ui-design-intelligence/scripts/framework_lint.py [file] [--framework nextjs]
  python3 .claude/skills/ui-design-intelligence/scripts/framework_lint.py --stack-check
"""
from __future__ import annotations
import sys
import re
import json
import argparse
from pathlib import Path

# ── Anti-patterns mapped to frameworks ────────────────────────────────
LINT_RULES = {

"nextjs": [
    {"id":"NX001","severity":"High",  "rule":"Use next/image not <img>",    "pattern":r"<img\s",           "message":"Use <Image> from 'next/image' instead of <img>","good":"<Image src={} alt={} width={} height={}>"},
    {"id":"NX002","severity":"High",  "rule":"Mark interactive components", "pattern":r"(useState|useEffect|onClick)\b(?!.*'use client')", "message":"Add 'use client' directive when using hooks or events"},
    {"id":"NX003","severity":"High",  "rule":"No API secrets in client",    "pattern":r"process\.env\.(?!NEXT_PUBLIC_)\w+",             "message":"Non-NEXT_PUBLIC_ env vars leaked to client code","good":"NEXT_PUBLIC_API_URL"},
    {"id":"NX004","severity":"Medium","rule":"Use next/link not <a>",        "pattern":r'<a\s+href=["\']/',                              "message":"Use <Link> from 'next/link' for internal navigation","good":"<Link href='/about'>"},
    {"id":"NX005","severity":"High",  "rule":"Validate Server Action input", "pattern":r"async function\s+\w+.*action.*\{(?!.*\.parse\()","message":"Server Actions should validate input with Zod"},
    {"id":"NX006","severity":"Medium","rule":"Use next/font not @import",    "pattern":r"@import url\(.+fonts\.googleapis",              "message":"Use 'next/font/google' instead of @import for fonts","good":"import { Inter } from 'next/font/google'"},
],

"react": [
    {"id":"RC001","severity":"High",  "rule":"Keys in lists",               "pattern":r"\.map\([^)]+\)\s*=>\s*<(?!.*key=)",             "message":"Add unique key prop to list items","good":"key={item.id}"},
    {"id":"RC002","severity":"High",  "rule":"No immediate event call",     "pattern":r"on\w+=\{[a-zA-Z]+\(\)",                         "message":"Pass function reference not invocation: onClick={fn} not onClick={fn()}"},
    {"id":"RC003","severity":"High",  "rule":"Include effect dependencies",  "pattern":r"useEffect\(\([^)]*\)\s*=>\s*\{[^}]+\},\s*\[\s*\]\s*\)","message":"Empty deps array may cause stale closure issues"},
    {"id":"RC004","severity":"High",  "rule":"No hooks in conditions",      "pattern":r"if\s*\([^)]+\)\s*\{[^}]*useState|if\s*\([^)]+\)\s*\{[^}]*useEffect","message":"Never call hooks inside conditions"},
    {"id":"RC005","severity":"Medium","rule":"Memoize context values",      "pattern":r"value=\{\{[^}]+\}\}",                            "message":"Inline object in context value causes re-renders. Use useMemo","good":"value={useMemo(() => ({...}), [])}"},
    {"id":"RC006","severity":"High",  "rule":"Semantic HTML not div-click", "pattern":r"<div[^>]+onClick",                              "message":"Use <button> for clickable elements, not <div onClick>","good":"<button onClick={...}>"},
],

"shadcn": [
    {"id":"SC001","severity":"High",  "rule":"Dialog needs DialogTitle",    "pattern":r"<DialogContent(?![\s\S]*?DialogTitle)",          "message":"DialogContent must include DialogTitle for accessibility"},
    {"id":"SC002","severity":"High",  "rule":"TooltipProvider required",    "pattern":r"<Tooltip(?!Provider)(?![\s\S]*?TooltipProvider)","message":"Wrap Tooltips in <TooltipProvider> at app level"},
    {"id":"SC003","severity":"High",  "rule":"Toaster in layout not page",  "pattern":r"export default function.*Page[\s\S]*?<Toaster", "message":"Add <Toaster> to root layout, not individual pages"},
    {"id":"SC004","severity":"Medium","rule":"Use variant not class hack",  "pattern":r'<Button className=\{.*\?.*:.*\}',               "message":"Use variant prop instead of conditional className","good":"<Button variant='destructive'>"},
    {"id":"SC005","severity":"High",  "rule":"Form needs FormMessage",      "pattern":r"<FormControl>[\s\S]*?</FormControl>(?![\s\S]*?<FormMessage)",  "message":"Add <FormMessage> after FormControl for validation errors"},
],

"tailwind": [
    {"id":"TW001","severity":"High",  "rule":"No hardcoded hex in className","pattern":r'className=["\'][^"\']*#[0-9A-Fa-f]{6}',          "message":"Use CSS variables or Tailwind tokens, not hardcoded hex colors","good":"bg-primary"},
    {"id":"TW002","severity":"High",  "rule":"Focus states required",       "pattern":r"focus:outline-none(?![\s\S]*focus:ring)",       "message":"Removing focus outline requires adding a replacement focus:ring","good":"focus:outline-none focus:ring-2"},
    {"id":"TW003","severity":"Medium","rule":"Add transition to hover",     "pattern":r"hover:(?!translate|scale)[a-z-]+ (?!.*transition)", "message":"Add transition class when using hover state changes","good":"hover:bg-gray-100 transition-colors"},
    {"id":"TW004","severity":"Medium","rule":"Tailwind v4 gradient syntax", "pattern":r"bg-gradient-to-",                              "message":"Tailwind v4 uses bg-linear-to-r instead of bg-gradient-to-r"},
    {"id":"TW005","severity":"High",  "rule":"Reduced motion support",     "pattern":r"animate-(?!none)[a-z-]+(?![\s\S]*motion-reduce)","message":"Add motion-reduce:animate-none alongside animations","good":"animate-pulse motion-reduce:animate-none"},
    {"id":"TW006","severity":"High",  "rule":"Min touch target on mobile", "pattern":r"h-[68]\b|h-\[2[0-9]px\]",                      "message":"Ensure interactive elements have min 44px height on mobile","good":"min-h-[44px]"},
],

"vue": [
    {"id":"VU001","severity":"High",  "rule":"No v-if + v-for same element","pattern":r"v-for.*v-if|v-if.*v-for",                       "message":"Never use v-if and v-for on the same element","good":"<template v-for><div v-if>"},
    {"id":"VU002","severity":"High",  "rule":"Key with v-for",              "pattern":r"v-for(?![\s\S]{0,50}:key=)",                   "message":"Always provide :key when using v-for"},
    {"id":"VU003","severity":"High",  "rule":"No prop mutation",            "pattern":r"props\.\w+\s*=",                               "message":"Never mutate props. Emit events instead","good":"emit('update:modelValue', newVal)"},
    {"id":"VU004","severity":"High",  "rule":"storeToRefs for Pinia",      "pattern":r"const \{ \w+ \} = use\w+Store\(\)(?![\s\S]*storeToRefs)","message":"Use storeToRefs() when destructuring Pinia store to keep reactivity"},
    {"id":"VU005","severity":"High",  "rule":"onUnmounted cleanup",        "pattern":r"(window\.addEventListener|setInterval|subscribe)\((?![\s\S]*onUnmounted)","message":"Add onUnmounted cleanup for event listeners and subscriptions"},
],

"svelte": [
    {"id":"SV001","severity":"High",  "rule":"Reassign arrays not mutate",  "pattern":r"\w+\.push\(|\w+\.splice\(",                    "message":"Reassign arrays to trigger reactivity: arr = [...arr, item]","good":"items = [...items, newItem]"},
    {"id":"SV002","severity":"High",  "rule":"Keys in each blocks",        "pattern":r"\{#each \w+ as \w+\}(?!\s*\()",               "message":"Always provide key in {#each} blocks","good":"{#each items as item (item.id)}"},
    {"id":"SV003","severity":"High",  "rule":"Auto-subscribe with $",      "pattern":r"\.subscribe\(",                                "message":"Use $storeName syntax for auto-subscribe instead of manual subscribe"},
    {"id":"SV004","severity":"High",  "rule":"SvelteKit load not onMount", "pattern":r"onMount.*fetch\(",                             "message":"Use load() in +page.js/+page.server.js instead of onMount fetch"},
],

"general": [
    {"id":"GN001","severity":"High",  "rule":"Alt text on images",         "pattern":r"<img(?![\s\S]*?alt=)|<Image(?![\s\S]*?alt=)",  "message":"All images need alt text for accessibility"},
    {"id":"GN002","severity":"High",  "rule":"No console.log in prod",    "pattern":r"console\.log\(",                               "message":"Remove console.log before production","good":"Use a proper logging utility"},
    {"id":"GN003","severity":"Medium","rule":"No TODO comments",           "pattern":r"//\s*TODO|//\s*FIXME|//\s*HACK",              "message":"Resolve TODO/FIXME before shipping"},
    {"id":"GN004","severity":"High",  "rule":"No hardcoded secrets",      "pattern":r'(password|secret|apikey|token)\s*=\s*["\'][^"\']{8,}',  "message":"Never hardcode secrets in source code"},
],

}


def lint_code(code: str, frameworks: list) -> list:
    """Run lint rules against code string. Returns list of issues."""
    issues = []
    rule_sets = list(set(frameworks + ["general"]))
    for fw in rule_sets:
        for rule in LINT_RULES.get(fw, []):
            if re.search(rule["pattern"], code, re.IGNORECASE | re.MULTILINE):
                issues.append({
                    "id": rule["id"],
                    "framework": fw,
                    "severity": rule["severity"],
                    "rule": rule["rule"],
                    "message": rule["message"],
                    "fix": rule.get("good", ""),
                })
    return sorted(issues, key=lambda x: ({"High":0,"Medium":1,"Low":2}[x["severity"]]))


def lint_file(filepath: str, frameworks: list) -> list:
    """Lint a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"⚠  File not found: {filepath}")
        return []
    code = path.read_text(errors="ignore")
    return lint_code(code, frameworks)


def print_issues(issues: list, filename: str = ""):
    if not issues:
        print(f"  ✅ No issues found{' in ' + filename if filename else ''}")
        return

    high = [i for i in issues if i["severity"] == "High"]
    med  = [i for i in issues if i["severity"] == "Medium"]
    low  = [i for i in issues if i["severity"] == "Low"]

    label = f" in {filename}" if filename else ""
    print(f"\n  Found {len(issues)} issue(s){label}:")
    print(f"  🔴 High: {len(high)}  🟡 Medium: {len(med)}  🔵 Low: {len(low)}\n")

    for issue in issues:
        icon = {"High":"🔴","Medium":"🟡","Low":"🔵"}[issue["severity"]]
        print(f"  {icon} [{issue['id']}] {issue['rule']}")
        print(f"     {issue['message']}")
        if issue.get("fix"):
            print(f"     ✓ Fix: {issue['fix']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Framework lint checker")
    parser.add_argument("file", nargs="?", help="File to lint")
    parser.add_argument("--framework", "-f", help="Framework(s) comma-separated: nextjs,react,shadcn,tailwind,vue,svelte")
    parser.add_argument("--stack-check", action="store_true", help="Auto-detect stack and lint all src files")
    parser.add_argument("--code", "-c", help="Lint inline code string")
    args = parser.parse_args()

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║          FRAMEWORK LINT CHECK                       ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    # Determine frameworks
    if args.framework:
        frameworks = [f.strip() for f in args.framework.split(",")]
    elif args.stack_check:
        # Read from stack detection
        try:
            import subprocess
            result = subprocess.run(
                ["python3", ".claude/skills/ui-design-intelligence/scripts/detect_stack.py"],
                capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if line.startswith("STACK_JSON:"):
                    stack = json.loads(line[11:])
                    frameworks = stack.get("guidelines", ["react"])
                    print(f"  Auto-detected: {frameworks}\n")
                    break
        except:
            frameworks = ["react", "general"]
    else:
        frameworks = ["react", "general"]

    # Lint code or file(s)
    if args.code:
        issues = lint_code(args.code, frameworks)
        print_issues(issues)

    elif args.file:
        issues = lint_file(args.file, frameworks)
        print_issues(issues, args.file)

    elif args.stack_check:
        # Lint all relevant files in project
        root = Path.cwd()
        extensions = {".tsx", ".ts", ".jsx", ".js", ".svelte", ".vue"}
        src_dirs = ["src", "app", "components", "pages", "lib"]
        all_issues = []
        files_checked = 0

        for src in src_dirs:
            src_path = root / src
            if not src_path.exists():
                continue
            for ext in extensions:
                for f in src_path.rglob(f"*{ext}"):
                    if "node_modules" in str(f) or ".next" in str(f):
                        continue
                    issues = lint_file(str(f), frameworks)
                    if issues:
                        rel = f.relative_to(root)
                        print(f"  📄 {rel}")
                        print_issues(issues, str(rel))
                        all_issues.extend(issues)
                    files_checked += 1

        print(f"\n  ═══════════════════════════════")
        print(f"  Files checked: {files_checked}")
        total_high = len([i for i in all_issues if i["severity"]=="High"])
        print(f"  Total issues: {len(all_issues)} (🔴 {total_high} High)")
        if total_high == 0:
            print("  ✅ No high-severity issues found")
        print()
    else:
        print("  Usage:")
        print("  python3 framework_lint.py myComponent.tsx --framework nextjs,react,shadcn")
        print("  python3 framework_lint.py --stack-check")
        print("  python3 framework_lint.py --code '<img src={url}>' --framework nextjs")


if __name__ == "__main__":
    main()
