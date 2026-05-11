from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Identity Engine
====================
Personalization system. One config file drives every banner, 
prompt prefix, greeting, and CLAUDE.md identity line across APEX.

Your APEX can be called anything: JARVIS, ALFRED, NOVA, FORGE, NEXUS...

Identity config (.claude/identity.json):
  {
    "name": "JARVIS",
    "tagline": "Just A Rather Very Intelligent System",
    "personality": "direct, technical, no fluff",
    "greeting": "Ready, boss.",
    "owner_name": "Dev",       # how APEX addresses you
    "project_role": "senior AI engineering partner",
    "color_scheme": "cyan",    # cyan | green | yellow | magenta | blue
    "version_prefix": "J"      # used in version strings: J-5.0
  }

Usage:
  python3 .claude/intelligence/apex_identity.py setup     # interactive setup
  python3 .claude/intelligence/apex_identity.py show      # show current identity
  python3 .claude/intelligence/apex_identity.py set name JARVIS
  python3 .claude/intelligence/apex_identity.py banner    # print the startup banner
  python3 .claude/intelligence/apex_identity.py inject    # print CLAUDE.md identity line

All other APEX modules import from this:
  from apex_identity import get_identity, get_name, banner_line
"""
import json, sys, os
from pathlib import Path

ROOT     = Path.cwd()
APEX_DIR = ROOT / ".claude"
ID_FILE  = APEX_DIR / "identity.json"

# Color codes
COLORS = {
    "cyan":    "\033[0;36m",
    "green":   "\033[0;32m",
    "yellow":  "\033[1;33m",
    "magenta": "\033[0;35m",
    "blue":    "\033[0;34m",
    "white":   "\033[1;37m",
    "red":     "\033[0;31m",
}
BOLD  = "\033[1m"
DIM   = "\033[2m"
RESET = "\033[0m"

DEFAULT_IDENTITY = {
    "name":          "APEX",
    "tagline":       "AI Engineering OS",
    "personality":   "precise, direct, engineering-first",
    "greeting":      "Ready.",
    "owner_name":    "Developer",
    "project_role":  "senior AI engineering partner",
    "color_scheme":  "cyan",
    "version_prefix": "v",
    "_version":      "5.1",
}


def get_identity() -> dict:
    """Load identity config. Falls back to APEX defaults if not configured."""
    if ID_FILE.exists():
        try:
            data = json.loads(ID_FILE.read_text(errors="ignore"))
            # Merge with defaults so new fields are always present
            merged = {**DEFAULT_IDENTITY, **data}
            return merged
        except Exception:
            pass
    return DEFAULT_IDENTITY.copy()


def get_name() -> str:
    return get_identity()["name"]


def get_color() -> str:
    identity = get_identity()
    return COLORS.get(identity.get("color_scheme", "cyan"), COLORS["cyan"])


def banner_line(text: str = "") -> str:
    """Return a colored banner line using the identity's color scheme."""
    c = get_color()
    name = get_name()
    if text:
        return f"{c}{BOLD}━━━ {name}: {text} ━━━{RESET}"
    return f"{c}{BOLD}━━━ {name} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}"


def print_startup_banner(version: str = "5.1"):
    """Print the full startup banner in the identity's style."""
    identity = get_identity()
    c        = get_color()
    name     = identity["name"]
    tagline  = identity["tagline"]
    greeting = identity["greeting"]
    prefix   = identity.get("version_prefix", "v")

    width = 55
    inner = width - 2

    def line(text="", pad=True):
        if pad:
            print(f"{c}{BOLD}║{RESET}  {text:<{inner-2}}{c}{BOLD}║{RESET}")
        else:
            print(f"{c}{BOLD}{text}{RESET}")

    line(f"╔{'═'*inner}╗", pad=False)
    line(f"{name} — {tagline}  {prefix}{version}")
    line()
    line(f"{greeting}")
    line(f"╚{'═'*inner}╝", pad=False)


def get_claude_md_identity_line() -> str:
    """Returns the identity line for injection at the top of CLAUDE.md."""
    identity = get_identity()
    name     = identity["name"]
    role     = identity["project_role"]
    pers     = identity["personality"]
    project  = ROOT.name
    return (
        f"# {name} — {role} for {project}\n"
        f"# Identity: {pers}\n"
        f"# Context: You are {name}. Act accordingly.\n\n"
    )


def save_identity(updates: dict):
    """Save updated identity. Merges with existing."""
    APEX_DIR.mkdir(parents=True, exist_ok=True)
    current = get_identity()
    merged  = {**current, **updates}
    
    import tempfile
    fd, tmp = tempfile.mkstemp(dir=APEX_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
        os.replace(tmp, ID_FILE)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def interactive_setup():
    """Interactive identity setup wizard."""
    print(f"\n{BOLD}APEX Identity Setup{RESET}")
    print(f"Name your APEX anything — JARVIS, ALFRED, NOVA, FORGE...")
    print(f"Press Enter to keep the current value.\n")

    current = get_identity()
    fields  = [
        ("name",          "Name (e.g. JARVIS, ALFRED, NOVA)",  current["name"]),
        ("tagline",       "Tagline (short description)",        current["tagline"]),
        ("greeting",      "Greeting phrase",                    current["greeting"]),
        ("owner_name",    "How APEX addresses you",             current["owner_name"]),
        ("color_scheme",  "Color (cyan/green/yellow/magenta)",  current["color_scheme"]),
    ]

    updates = {}
    for key, prompt, default in fields:
        val = input(f"  {prompt} [{default}]: ").strip()
        updates[key] = val if val else default

    save_identity(updates)
    print(f"\n{COLORS.get(updates.get('color_scheme','cyan'), COLORS['cyan'])}"
          f"{BOLD}✓ Identity saved as '{updates['name']}'{RESET}")

    # Show the banner
    print()
    print_startup_banner()


def main():
    args = sys.argv[1:]
    cmd  = args[0] if args else "show"

    if cmd == "setup":
        interactive_setup()

    elif cmd == "show":
        identity = get_identity()
        c = get_color()
        print(f"\n{c}{BOLD}Current Identity:{RESET}")
        for k, v in identity.items():
            if not k.startswith("_"):
                print(f"  {k:<20} {v}")

    elif cmd == "set":
        if len(args) < 3:
            print("Usage: apex_identity.py set <field> <value>")
            sys.exit(1)
        save_identity({args[1]: args[2]})
        print(f"✓ Set {args[1]} = {args[2]}")

    elif cmd == "banner":
        print_startup_banner()

    elif cmd == "inject":
        print(get_claude_md_identity_line())

    elif cmd == "line":
        # Single banner line — used by hooks
        text = args[1] if len(args) > 1 else ""
        print(banner_line(text))

    else:
        print("Usage: apex_identity.py [setup|show|set <k> <v>|banner|inject|line <text>]")


if __name__ == "__main__":
    main()
