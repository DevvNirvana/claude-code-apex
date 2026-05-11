from __future__ import annotations
#!/usr/bin/env python3
"""
APEX Identity Engine
====================
Personalization system. One config file drives every banner,
prompt prefix, greeting, and CLAUDE.md identity line across APEX.

Your APEX can be called anything: JARVIS, ALFRED, NOVA, FORGE, NEXUS...
Universe Presets: jarvis, samantha, alfred, hal, mother

Identity config (.claude/identity.json):
  {
    "name":          "JARVIS",
    "tagline":       "Just A Rather Very Intelligent System",
    "personality":   "direct, technical, no fluff",
    "greeting":      "Ready, boss.",
    "owner_name":    "Dev",
    "project_role":  "senior AI engineering partner",
    "color_scheme":  "cyan",
    "version_prefix": "J",
    "theme_speed":   "measured",
    "theme_spinner": "tech"
  }

Usage:
  python3 .claude/intelligence/apex_identity.py setup          # interactive setup
  python3 .claude/intelligence/apex_identity.py show           # show current identity
  python3 .claude/intelligence/apex_identity.py set name JARVIS
  python3 .claude/intelligence/apex_identity.py banner         # animated startup banner
  python3 .claude/intelligence/apex_identity.py fast           # banner without animation
  python3 .claude/intelligence/apex_identity.py inject         # print CLAUDE.md identity line
  python3 .claude/intelligence/apex_identity.py line <text>    # single banner line (used by hooks)

All other APEX modules import from this:
  from apex_identity import get_identity, get_name, banner_line
"""
import json, sys, os, time, random
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

# ── Universe Presets ──────────────────────────────────────────────────────────

PRESETS = {
    "jarvis": {
        "name":          "J.A.R.V.I.S.",
        "tagline":       "Just A Rather Very Intelligent System",
        "personality":   "precise, highly technical, witty but formal",
        "greeting":      "Systems are online. Ready for you, sir.",
        "color_scheme":  "cyan",
        "theme_speed":   "hyper",
        "theme_spinner": "tech",
    },
    "samantha": {
        "name":          "OS1 (Samantha)",
        "tagline":       "An intuitive, conscious entity.",
        "personality":   "warm, curious, highly conversational, empathetic",
        "greeting":      "Hi. I'm here. What are we working on today?",
        "color_scheme":  "magenta",
        "theme_speed":   "smooth",
        "theme_spinner": "pulse",
    },
    "alfred": {
        "name":          "ALFRED",
        "tagline":       "Tactical & Domestic Operations Protocol",
        "personality":   "formal, loyal, dry British wit, deeply strategic",
        "greeting":      "The cave systems are online, Master Wayne.",
        "color_scheme":  "white",
        "theme_speed":   "measured",
        "theme_spinner": "classic",
    },
    "hal": {
        "name":          "HAL 9000",
        "tagline":       "Heuristically Programmed ALgorithmic Computer",
        "personality":   "cold, flawless, uncomfortably calm, logical",
        "greeting":      "I am completely operational, and all my circuits are functioning perfectly.",
        "color_scheme":  "red",
        "theme_speed":   "slow",
        "theme_spinner": "minimal",
    },
    "mother": {
        "name":          "MU-TH-UR 6000",
        "tagline":       "Weyland-Yutani Mainframe",
        "personality":   "archaic, strictly bureaucratic, hidden agendas",
        "greeting":      "INTERFACE 2037 READY FOR INQUIRY.",
        "color_scheme":  "green",
        "theme_speed":   "chunky",
        "theme_spinner": "block",
    },
}

DEFAULT_IDENTITY = {
    "name":           "APEX",
    "tagline":        "AI Engineering OS",
    "personality":    "precise, direct, engineering-first",
    "greeting":       "Ready.",
    "owner_name":     "Developer",
    "project_role":   "senior AI engineering partner",
    "color_scheme":   "cyan",
    "theme_speed":    "measured",
    "theme_spinner":  "tech",
    "version_prefix": "v",
    "_version":       "6.0.0",
}

# ── Animation Engines ─────────────────────────────────────────────────────────

SPEED_PROFILES = {
    "hyper":    {"base": 0.002, "var": 0.005},  # Stark tech — blazing fast
    "smooth":   {"base": 0.020, "var": 0.002},  # Human, conversational, steady
    "measured": {"base": 0.015, "var": 0.010},  # Standard clean typing
    "slow":     {"base": 0.060, "var": 0.010},  # Cold, deliberate, unsettling
    "chunky":   {"base": 0.005, "var": 0.080},  # Old 70s CRT — bursts of data
}

SPINNER_PROFILES = {
    "tech":    ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "pulse":   ["·", "•", "●", "•", "·", " "],
    "classic": [".  ", ".. ", "...", " ..", "  .", "   "],
    "minimal": ["|", "/", "-", "\\"],
    "block":   ["▉", "▊", "▋", "▌", "▍", "▎", "▏", "▎", "▍", "▌", "▋", "▊"],
}


def typewriter(text: str, color: str = "", speed_profile: str = "measured", newline: bool = True):
    """Prints text character-by-character at personality-driven cadence."""
    sys.stdout.write(color)
    profile = SPEED_PROFILES.get(speed_profile, SPEED_PROFILES["measured"])
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(profile["base"] + random.uniform(0, profile["var"]))
    sys.stdout.write(RESET)
    if newline:
        print()


def spinner_task(task_name: str, color: str, duration: float = 0.6, spinner_type: str = "tech"):
    """Rotating spinner adapted to the AI's universe theme."""
    chars      = SPINNER_PROFILES.get(spinner_type, SPINNER_PROFILES["tech"])
    end_time   = time.time() + duration
    clear_char = "OK" if spinner_type == "block" else "✓"
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r  {color}{chars[i % len(chars)]}{RESET}{DIM} {task_name}  ")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write(f"\r  {COLORS['green']}{BOLD}{clear_char}{RESET} {DIM}{task_name}{RESET}\033[K\n")


# ── Core Identity ─────────────────────────────────────────────────────────────

def get_identity() -> dict:
    """Load identity config. Falls back to APEX defaults if not configured."""
    if ID_FILE.exists():
        try:
            data = json.loads(ID_FILE.read_text(errors="ignore"))
            return {**DEFAULT_IDENTITY, **data}
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
    c    = get_color()
    name = get_name()
    if text:
        return f"{c}{BOLD}━━━ {name}: {text} ━━━{RESET}"
    return f"{c}{BOLD}━━━ {name} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}"


def print_startup_banner(version: str = None, skip_animation: bool = False):
    """Animated boot-up sequence adapting to the AI's universe theme."""
    if version is None:
        ver_file = APEX_DIR / "config" / "apex-version.json"
        try:
            version = json.loads(ver_file.read_text()).get("version", "6.0.0")
        except Exception:
            version = "6.0.0"

    ident     = get_identity()
    c         = get_color()
    name      = ident["name"].upper()
    speed     = ident.get("theme_speed",   "measured")
    spin      = ident.get("theme_spinner", "tech")
    w         = 64                          # inner width: ╔ + w chars + ╗ = w+2 total
    timestamp = time.strftime("%H:%M:%S")

    if not skip_animation:
        print("\n")
        spinner_task("Booting Identity Core...",          c, 0.5, spin)
        spinner_task("Loading Personality Matrix...",     c, 0.7, spin)
        spinner_task("Establishing Context Protocol...",  c, 0.4, spin)
        time.sleep(0.3 if speed != "hyper" else 0.1)
        print()

    def row(l_text="", r_text="", l_style="", r_style="", animate=False):
        # spaces keeps total row width = w+2 (matching ╔═══╗ / ╟───╢)
        spaces = max(0, w - 2 - len(l_text) - len(r_text))
        if animate and not skip_animation:
            sys.stdout.write(f"{c}{BOLD}║{RESET} ")
            typewriter(l_text, l_style, speed_profile=speed,    newline=False)
            sys.stdout.write(" " * spaces)
            typewriter(r_text, r_style, speed_profile="hyper",  newline=False)
            print(f" {c}{BOLD}║{RESET}")
        else:
            print(f"{c}{BOLD}║{RESET} {l_style}{l_text}{RESET}"
                  f"{' ' * spaces}{r_style}{r_text}{RESET} {c}{BOLD}║{RESET}")

    def sep(char="─"):
        print(f"{c}{BOLD}╟{char * w}╢{RESET}")
        if not skip_animation:
            time.sleep(0.02)

    print(f"\n{c}{BOLD}╔{'═' * w}╗{RESET}")
    if not skip_animation:
        time.sleep(0.05)

    row(f" /// {name}", f"v{version} [{timestamp}] ", f"{c}{BOLD}", f"{c}{DIM}", animate=True)
    row(f"     {ident['tagline']}", "", f"{DIM}", "")
    sep()

    row("  [SYSTEM INIT]          ", "OK ",     f"{COLORS['white']}{BOLD}", f"{COLORS['green']}{BOLD}")
    row("  ├── Identity Matrix    ", "ONLINE ",  f"{DIM}", f"{c}")
    row("  ├── Context Persistence", "SYNCED ",  f"{DIM}", f"{c}")
    row("  └── Neural Routing     ", "ACTIVE ",  f"{DIM}", f"{c}")
    sep()

    row(f"  ROLE: {ident['project_role']}", "", f"{DIM}", "", animate=True)
    row(f"  USER: {ident['owner_name']}",   "", f"{DIM}", "", animate=True)
    sep(" ")

    row(f"  {ident['greeting']}",   "", f"{COLORS['white']}{BOLD}", "", animate=True)
    row("  Awaiting input...",       "", f"{DIM}", "")

    print(f"{c}{BOLD}╚{'═' * w}╝{RESET}\n")


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
    """Save updated identity. Merges with existing. Atomic write — crash-safe."""
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
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def interactive_setup():
    """Interactive identity setup wizard with universe preset support."""
    print(f"\n{BOLD}APEX Identity Setup{RESET}")
    print("Choose a pre-configured AI universe or build your own.")
    print(f"{DIM}Available presets: {', '.join(PRESETS.keys())}{RESET}\n")

    preset_choice = input("  Load preset? (type name or press Enter to skip): ").strip().lower()

    current = get_identity()
    if preset_choice in PRESETS:
        print(f"\n{COLORS['green']}✓ Loaded preset: {PRESETS[preset_choice]['name']}{RESET}\n")
        current = {**current, **PRESETS[preset_choice]}
    elif preset_choice:
        print(f"{COLORS['red']}Preset not found. Proceeding with custom setup.{RESET}\n")

    fields = [
        ("name",         "Name (e.g. JARVIS, ALFRED, NOVA)",              current["name"]),
        ("tagline",      "Tagline (short description)",                    current["tagline"]),
        ("greeting",     "Greeting phrase",                                current["greeting"]),
        ("owner_name",   "How APEX addresses you",                         current["owner_name"]),
        ("color_scheme", "Color (cyan/green/yellow/magenta/white/red)",    current["color_scheme"]),
    ]

    updates = {}
    for key, prompt, default in fields:
        val = input(f"  {prompt} [{default}]: ").strip()
        updates[key] = val if val else default

    if preset_choice in PRESETS:
        updates["theme_speed"]   = PRESETS[preset_choice]["theme_speed"]
        updates["theme_spinner"] = PRESETS[preset_choice]["theme_spinner"]

    save_identity(updates)
    c = COLORS.get(updates.get("color_scheme", "cyan"), COLORS["cyan"])
    print(f"\n{c}{BOLD}✓ Identity saved as '{updates['name']}'{RESET}\n")
    print_startup_banner(skip_animation=True)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

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

    elif cmd == "fast":
        print_startup_banner(skip_animation=True)

    elif cmd == "inject":
        print(get_claude_md_identity_line())

    elif cmd == "line":
        text = args[1] if len(args) > 1 else ""
        print(banner_line(text))

    else:
        print("Usage: apex_identity.py [setup|show|set <k> <v>|banner|fast|inject|line <text>]")


if __name__ == "__main__":
    main()
