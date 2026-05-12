#!/usr/bin/env python3
"""
APEX Theme Generator — Persona-Aware Claude Code Theme Installer
================================================================
Generates and installs a custom Claude Code color theme that matches
the active APEX identity's color_scheme.

Themes are installed to ~/.claude/themes/ (Claude Code's global theme dir).
Theme preference is attempted in ~/.claude/settings.json (best-effort).

Theme selection per color_scheme:
  jarvis  → apex-jarvis    (J.A.R.V.I.S. — sky-steel cyan, Stark tech)
  cyan    → apex-dark      (default — clean steel cyan)
  blue    → apex-blue      (deep sky blue)
  magenta → apex-samantha  (warm rose — OS1 / Her)
  white   → apex-alfred    (cold silver monochrome)
  red     → apex-hal       (HAL 9000 deep red)
  green   → apex-mother    (phosphor neon — MU-TH-UR 6000)
  yellow  → apex-yellow    (amber/gold)

Custom themes:
  python3 .claude/intelligence/theme_generator.py create "#ff6b35" "NEXUS"
  → installs ~/.claude/themes/custom-nexus.json, select via /theme

Usage:
  python3 .claude/intelligence/theme_generator.py install            # install all presets + activate
  python3 .claude/intelligence/theme_generator.py create <hex> <name> # create custom theme
  python3 .claude/intelligence/theme_generator.py list               # list installed APEX themes
  python3 .claude/intelligence/theme_generator.py preview            # print active theme JSON
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import os
from pathlib import Path

ROOT     = Path.cwd()
APEX_DIR = ROOT / ".claude"
_INTEL   = Path(__file__).parent
sys.path.insert(0, str(_INTEL))

GREEN  = "\033[0;32m"; YELLOW = "\033[1;33m"; DIM = "\033[2m"
RED    = "\033[0;31m"; BOLD   = "\033[1m";    RESET = "\033[0m"

# ── Lore-accurate theme definitions ──────────────────────────────────────────
# Each scheme maps to a complete theme dict. These are the canonical sources —
# themes/<slug>.json files are generated from these, not the other way around.

_THEMES: dict[str, dict] = {
    # J.A.R.V.I.S. — sky-steel cyan, Stark tech precision (distinct from generic apex-dark)
    "jarvis": {
        "slug": "apex-jarvis",
        "theme": {
            "name": "APEX — J.A.R.V.I.S.",
            "base": "dark",
            "overrides": {
                "claude":            "#22d3ee",
                "briefLabelClaude":  "#22d3ee",
                "briefLabelYou":     "#64748b",
                "text":              "#f8fafc",
                "inverseText":       "#082f49",
                "inactive":          "#0c4a6e",
                "subtle":            "#0369a1",
                "suggestion":        "#0ea5e9",
                "permission":        "#f59e0b",
                "remember":          "#7dd3fc",
                "success":           "#10b981",
                "error":             "#ef4444",
                "warning":           "#f59e0b",
                "merged":            "#7dd3fc",
                "promptBorder":      "#0284c7",
                "planMode":          "#f59e0b",
                "autoAccept":        "#10b981",
                "bashBorder":        "#082f49",
                "ide":               "#0ea5e9",
                "fastMode":          "#38bdf8",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#22d3ee",
                "rate_limit_empty":  "#082f49",
            },
        },
    },
    "cyan": {
        "slug": "apex-dark",
        "theme": {
            "name": "APEX Dark",
            "base": "dark",
            "overrides": {
                "claude":            "#22d3ee",
                "briefLabelClaude":  "#22d3ee",
                "briefLabelYou":     "#94a3b8",
                "text":              "#e2e8f0",
                "inverseText":       "#0f172a",
                "inactive":          "#475569",
                "subtle":            "#64748b",
                "suggestion":        "#0ea5e9",
                "permission":        "#f59e0b",
                "remember":          "#a78bfa",
                "success":           "#22c55e",
                "error":             "#ef4444",
                "warning":           "#f59e0b",
                "merged":            "#a78bfa",
                "promptBorder":      "#0891b2",
                "planMode":          "#f59e0b",
                "autoAccept":        "#22c55e",
                "bashBorder":        "#334155",
                "ide":               "#0ea5e9",
                "fastMode":          "#f472b6",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#22d3ee",
                "rate_limit_empty":  "#1e293b",
            },
        },
    },
    "blue": {
        "slug": "apex-blue",
        "theme": {
            "name": "APEX Blue",
            "base": "dark",
            "overrides": {
                "claude":            "#60a5fa",
                "briefLabelClaude":  "#60a5fa",
                "briefLabelYou":     "#64748b",
                "text":              "#e2e8f0",
                "inverseText":       "#0d1b3e",
                "inactive":          "#1e3a5f",
                "subtle":            "#1d4ed8",
                "suggestion":        "#3b82f6",
                "permission":        "#f59e0b",
                "remember":          "#93c5fd",
                "success":           "#22c55e",
                "error":             "#ef4444",
                "warning":           "#f59e0b",
                "merged":            "#93c5fd",
                "promptBorder":      "#2563eb",
                "planMode":          "#f59e0b",
                "autoAccept":        "#22c55e",
                "bashBorder":        "#1e3a5f",
                "ide":               "#3b82f6",
                "fastMode":          "#818cf8",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#60a5fa",
                "rate_limit_empty":  "#172554",
            },
        },
    },
    # Samantha — warm rose/pink (Her, 2013) — intimate, conscious, alive
    "magenta": {
        "slug": "apex-samantha",
        "theme": {
            "name": "APEX — OS1 (Samantha)",
            "base": "dark",
            "overrides": {
                "claude":            "#fb7185",
                "briefLabelClaude":  "#fb7185",
                "briefLabelYou":     "#a8a29e",
                "text":              "#fff1f2",
                "inverseText":       "#2a1215",
                "inactive":          "#881337",
                "subtle":            "#9f1239",
                "suggestion":        "#f43f5e",
                "permission":        "#fbbf24",
                "remember":          "#fda4af",
                "success":           "#10b981",
                "error":             "#ef4444",
                "warning":           "#f59e0b",
                "merged":            "#fda4af",
                "promptBorder":      "#e11d48",
                "planMode":          "#fbbf24",
                "autoAccept":        "#10b981",
                "bashBorder":        "#4c0519",
                "ide":               "#f43f5e",
                "fastMode":          "#fb923c",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#fb7185",
                "rate_limit_empty":  "#2a1215",
            },
        },
    },
    # Alfred — cold silver monochrome — Pennyworth precision, no colour noise
    "white": {
        "slug": "apex-alfred",
        "theme": {
            "name": "APEX — ALFRED",
            "base": "dark",
            "overrides": {
                "claude":            "#f1f5f9",
                "briefLabelClaude":  "#cbd5e1",
                "briefLabelYou":     "#64748b",
                "text":              "#f8fafc",
                "inverseText":       "#0f172a",
                "inactive":          "#1e293b",
                "subtle":            "#334155",
                "suggestion":        "#94a3b8",
                "permission":        "#eab308",
                "remember":          "#cbd5e1",
                "success":           "#22c55e",
                "error":             "#ef4444",
                "warning":           "#f59e0b",
                "merged":            "#94a3b8",
                "promptBorder":      "#475569",
                "planMode":          "#eab308",
                "autoAccept":        "#22c55e",
                "bashBorder":        "#0f172a",
                "ide":               "#94a3b8",
                "fastMode":          "#cbd5e1",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#cbd5e1",
                "rate_limit_empty":  "#0f172a",
            },
        },
    },
    # HAL 9000 — pure red on black — cold, menacing, omniscient
    "red": {
        "slug": "apex-hal",
        "theme": {
            "name": "APEX — HAL 9000",
            "base": "dark",
            "overrides": {
                "claude":            "#ef4444",
                "briefLabelClaude":  "#ef4444",
                "briefLabelYou":     "#9ca3af",
                "text":              "#ffffff",
                "inverseText":       "#280000",
                "inactive":          "#450a0a",
                "subtle":            "#7f1d1d",
                "suggestion":        "#dc2626",
                "permission":        "#f59e0b",
                "remember":          "#fca5a5",
                "success":           "#22c55e",
                "error":             "#f87171",
                "warning":           "#f59e0b",
                "merged":            "#fca5a5",
                "promptBorder":      "#991b1b",
                "planMode":          "#f59e0b",
                "autoAccept":        "#22c55e",
                "bashBorder":        "#280000",
                "ide":               "#ef4444",
                "fastMode":          "#fca5a5",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#f87171",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#ef4444",
                "rate_limit_empty":  "#280000",
            },
        },
    },
    # MU-TH-UR 6000 — phosphor neon green on black — archaic corporate mainframe
    "green": {
        "slug": "apex-mother",
        "theme": {
            "name": "APEX — MU-TH-UR 6000",
            "base": "dark",
            "overrides": {
                "claude":            "#39ff14",
                "briefLabelClaude":  "#39ff14",
                "briefLabelYou":     "#16a34a",
                "text":              "#ecfdf5",
                "inverseText":       "#022c22",
                "inactive":          "#064e3b",
                "subtle":            "#065f46",
                "suggestion":        "#22c55e",
                "permission":        "#eab308",
                "remember":          "#4ade80",
                "success":           "#39ff14",
                "error":             "#ef4444",
                "warning":           "#eab308",
                "merged":            "#4ade80",
                "promptBorder":      "#15803d",
                "planMode":          "#eab308",
                "autoAccept":        "#39ff14",
                "bashBorder":        "#022c22",
                "ide":               "#22c55e",
                "fastMode":          "#86efac",
                "diffAdded":         "#14532d",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#064e3b",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#39ff14",
                "rate_limit_empty":  "#022c22",
            },
        },
    },
    "yellow": {
        "slug": "apex-yellow",
        "theme": {
            "name": "APEX Gold",
            "base": "dark",
            "overrides": {
                "claude":            "#fbbf24",
                "briefLabelClaude":  "#fbbf24",
                "briefLabelYou":     "#78350f",
                "text":              "#fefce8",
                "inverseText":       "#0d0700",
                "inactive":          "#451a03",
                "subtle":            "#78350f",
                "suggestion":        "#f59e0b",
                "permission":        "#f59e0b",
                "remember":          "#fde68a",
                "success":           "#22c55e",
                "error":             "#ef4444",
                "warning":           "#f59e0b",
                "merged":            "#fde68a",
                "promptBorder":      "#d97706",
                "planMode":          "#f59e0b",
                "autoAccept":        "#22c55e",
                "bashBorder":        "#1c0f00",
                "ide":               "#f59e0b",
                "fastMode":          "#fcd34d",
                "diffAdded":         "#166534",
                "diffRemoved":       "#7f1d1d",
                "diffAddedWord":     "#22c55e",
                "diffRemovedWord":   "#ef4444",
                "diffAddedDimmed":   "#14532d",
                "diffRemovedDimmed": "#450a0a",
                "rate_limit_fill":   "#fbbf24",
                "rate_limit_empty":  "#1c0f00",
            },
        },
    },
}

# ── Theme builder ─────────────────────────────────────────────────────────────

def build_theme(scheme: str) -> dict:
    """Return the complete Claude Code theme dict for the given color scheme."""
    entry = _THEMES.get(scheme, _THEMES["cyan"])
    return entry["theme"]


def get_slug_for_scheme(scheme: str) -> str:
    return _THEMES.get(scheme, _THEMES["cyan"])["slug"]


# ── Custom theme creation ─────────────────────────────────────────────────────

def _darken(hex_color: str, factor: float) -> str:
    """Mix hex_color toward black. factor=1.0 → original, factor=0.0 → black."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"#{int(r * factor):02x}{int(g * factor):02x}{int(b * factor):02x}"


def _lighten(hex_color: str, factor: float) -> str:
    """Mix hex_color toward white. factor=0.0 → original, factor=1.0 → white."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (
        f"#{int(r + (255 - r) * factor):02x}"
        f"{int(g + (255 - g) * factor):02x}"
        f"{int(b + (255 - b) * factor):02x}"
    )


def create_custom_theme(accent: str, name: str) -> tuple[str, dict]:
    """
    Derive a full 28-key Claude Code theme from a single accent hex color.
    Returns (slug, theme_dict). Slug format: custom-<name-slugified>.

    Example:
      slug, theme = create_custom_theme("#ff6b35", "NEXUS")
      # slug == "custom-nexus"
    """
    if not accent.startswith("#") or len(accent.lstrip("#")) != 6:
        raise ValueError(f"accent must be a 6-digit hex color, got: {accent!r}")

    slug     = "custom-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    border   = _darken(accent, 0.72)
    alt      = _darken(accent, 0.88)
    bg_empty = _darken(accent, 0.07)
    bg_inv   = _darken(accent, 0.04)
    inactive = _darken(accent, 0.22)
    subtle   = _darken(accent, 0.38)
    remember = _lighten(accent, 0.45)
    bash     = _darken(accent, 0.06)

    theme = {
        "name": name,
        "base": "dark",
        "overrides": {
            "claude":            accent,
            "briefLabelClaude":  accent,
            "briefLabelYou":     "#64748b",
            "text":              "#f8fafc",
            "inverseText":       bg_inv,
            "inactive":          inactive,
            "subtle":            subtle,
            "suggestion":        alt,
            "permission":        "#f59e0b",
            "remember":          remember,
            "success":           "#22c55e",
            "error":             "#ef4444",
            "warning":           "#f59e0b",
            "merged":            remember,
            "promptBorder":      border,
            "planMode":          "#f59e0b",
            "autoAccept":        "#22c55e",
            "bashBorder":        bash,
            "ide":               alt,
            "fastMode":          remember,
            "diffAdded":         "#166534",
            "diffRemoved":       "#7f1d1d",
            "diffAddedWord":     "#22c55e",
            "diffRemovedWord":   "#ef4444",
            "diffAddedDimmed":   "#14532d",
            "diffRemovedDimmed": "#450a0a",
            "rate_limit_fill":   accent,
            "rate_limit_empty":  bg_empty,
        },
    }
    return slug, theme


# ── Install ───────────────────────────────────────────────────────────────────

def _global_themes_dir() -> Path:
    """Returns ~/.claude/themes/, creating it if needed."""
    d = Path.home() / ".claude" / "themes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def install_theme(identity: dict | None = None) -> str:
    """
    Build and write persona-matched theme to ~/.claude/themes/<slug>.json.
    Returns the theme slug (e.g. "apex-dark").
    """
    if identity is None:
        try:
            from apex_identity import get_identity
            identity = get_identity()
        except Exception:
            identity = {}

    scheme = identity.get("color_scheme", "cyan")
    slug   = get_slug_for_scheme(scheme)
    theme  = build_theme(scheme)

    themes_dir = _global_themes_dir()
    dest = themes_dir / f"{slug}.json"
    _atomic_write_json(dest, theme)
    return slug


def install_all_presets() -> list[str]:
    """Install all 6 preset themes to ~/.claude/themes/. Called during APEX install."""
    slugs = []
    themes_dir = _global_themes_dir()
    for scheme, s in _THEMES.items():
        slug  = s["slug"]
        theme = build_theme(scheme)
        _atomic_write_json(themes_dir / f"{slug}.json", theme)
        slugs.append(slug)
    return slugs


def apply_theme_preference(slug: str) -> bool:
    """
    Best-effort: write {"theme": "custom:<slug>"} to ~/.claude/settings.json.
    Merges with existing settings — never replaces unknown keys.
    Returns True on success.
    """
    global_settings = Path.home() / ".claude" / "settings.json"
    try:
        existing: dict = {}
        if global_settings.exists():
            try:
                existing = json.loads(global_settings.read_text(encoding="utf-8"))
            except Exception:
                existing = {}

        # Only set if not already customized to something non-APEX/non-custom
        current_theme = existing.get("theme", "")
        if current_theme and not (
            current_theme.startswith("custom:apex") or
            current_theme.startswith("custom:custom-")
        ):
            return False   # respect user's existing non-APEX theme choice

        existing["theme"] = f"custom:{slug}"
        _atomic_write_json(global_settings, existing)
        return True
    except Exception:
        return False


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

    cmd = sys.argv[1] if len(sys.argv) > 1 else "install"

    if cmd == "install":
        # Install all presets during APEX setup
        print(f"  Installing APEX themes to ~/.claude/themes/...")
        slugs = install_all_presets()
        for slug in slugs:
            print(f"  {GREEN}✓ {slug}.json{RESET}")

        # Install persona-specific theme and try to activate it
        try:
            from apex_identity import get_identity
            identity = get_identity()
        except Exception:
            identity = {}

        slug = get_slug_for_scheme(identity.get("color_scheme", "cyan"))
        activated = apply_theme_preference(slug)
        if activated:
            print(f"  {GREEN}✓ Theme activated: {slug}{RESET}")
        else:
            print(f"  {DIM}Select theme manually: run /theme → choose '{slug}'{RESET}")

    elif cmd == "preview":
        try:
            from apex_identity import get_identity
            scheme = get_identity().get("color_scheme", "cyan")
        except Exception:
            scheme = "cyan"
        slug  = get_slug_for_scheme(scheme)
        theme = build_theme(scheme)
        print(json.dumps(theme, indent=2))
        print(f"\n{DIM}Slug: {slug}{RESET}")

    elif cmd == "create":
        if len(sys.argv) < 4:
            print(f"{RED}Usage: theme_generator.py create <#hex> <Name>{RESET}")
            print(f"  Example: theme_generator.py create \"#ff6b35\" \"NEXUS\"")
            sys.exit(1)
        accent = sys.argv[2].strip()
        name   = sys.argv[3].strip()
        try:
            slug, theme = create_custom_theme(accent, name)
        except ValueError as e:
            print(f"{RED}✗ {e}{RESET}")
            sys.exit(1)

        themes_dir = _global_themes_dir()
        dest = themes_dir / f"{slug}.json"
        _atomic_write_json(dest, theme)
        print(f"  {GREEN}✓ Theme created: {dest}{RESET}")
        activated = apply_theme_preference(slug)
        if activated:
            print(f"  {GREEN}✓ Activated: custom:{slug}{RESET}")
        else:
            print(f"  {YELLOW}To activate: open Claude Code → /theme → select '{slug}'{RESET}")

    elif cmd == "list":
        themes_dir = _global_themes_dir()
        print(f"\n{BOLD}Installed APEX themes ({themes_dir}){RESET}")
        found = sorted(themes_dir.glob("apex-*.json")) + sorted(themes_dir.glob("custom-*.json"))
        if found:
            for f in found:
                tag = f"  {DIM}(custom){RESET}" if f.stem.startswith("custom-") else ""
                print(f"  {GREEN}✓{RESET} {f.stem}{tag}")
        else:
            print(f"  {DIM}None installed — run: python3 theme_generator.py install{RESET}")

    else:
        print("Usage: theme_generator.py [install|create <hex> <name>|preview|list]")
        sys.exit(1)


if __name__ == "__main__":
    main()
