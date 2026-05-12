#!/usr/bin/env python3
"""
APEX Voice — Persona-Matched TTS Engine
========================================
Local, async, zero-token text-to-speech for APEX identity personas.

Engines (auto-selected):
  Kokoro-82M  — ultra-fast built-in voices, no sample needed (~300MB one-time download)
  F5-TTS      — zero-shot voice cloning from a 15-30s WAV sample (~2GB one-time download)

Engine selection (auto mode):
  .claude/voices/<persona>.wav exists → F5-TTS (voice cloning)
  no sample → Kokoro-82M (persona-matched built-in voice)

Voice samples (optional — drop and forget):
  .claude/voices/jarvis.wav
  .claude/voices/samantha.wav
  .claude/voices/alfred.wav
  .claude/voices/hal.wav
  .claude/voices/mother.wav

Usage:
  python3 .claude/intelligence/apex_voice.py speak "text"  # speak custom text
  python3 .claude/intelligence/apex_voice.py greeting      # speak identity greeting
  python3 .claude/intelligence/apex_voice.py enable        # enable + install deps
  python3 .claude/intelligence/apex_voice.py disable       # disable
  python3 .claude/intelligence/apex_voice.py setup         # interactive setup
  python3 .claude/intelligence/apex_voice.py test          # blocking smoke-test
  python3 .claude/intelligence/apex_voice.py status        # print current config
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ROOT       = Path.cwd()
APEX_DIR   = ROOT / ".claude"
VOICES_DIR = APEX_DIR / "voices"
ID_FILE    = APEX_DIR / "identity.json"

_INTEL = Path(__file__).parent
if str(_INTEL) not in sys.path:
    sys.path.insert(0, str(_INTEL))

GREEN = "\033[0;32m"; YELLOW = "\033[1;33m"; RED   = "\033[0;31m"
BOLD  = "\033[1m";    DIM    = "\033[2m";    RESET = "\033[0m"

# ── Dependency lists ──────────────────────────────────────────────────────────

_KOKORO_DEPS = ["kokoro", "soundfile", "playsound3"]
_F5_DEPS     = ["f5-tts", "soundfile", "playsound3"]

# ── Persona → Kokoro built-in voice ──────────────────────────────────────────
# (voice_id, base_speed)
# bm_* = British male  bf_* = British female
# am_* = American male af_* = American female

_KOKORO_VOICE_MAP: dict[str, tuple[str, float]] = {
    "jarvis":   ("bm_george",  1.05),  # British male, formal, crisp
    "samantha": ("af_sky",     0.95),  # Warm female, intimate, slightly slower
    "alfred":   ("bm_lewis",   0.90),  # British male, measured, dry
    "hal":      ("am_adam",    0.70),  # American male, very slow — cold, deliberate
    "mother":   ("af_nicole",  0.80),  # Female, slow — clipped, bureaucratic
    "default":  ("am_michael", 1.00),  # Neutral American male
}

# Persona name → slug (mirrors apex_identity._VERB_MATCHERS)
_PERSONA_MATCHERS: list[tuple[str, str]] = [
    ("jarvis",   "jarvis"),
    ("samantha", "samantha"),
    ("alfred",   "alfred"),
    ("hal",      "hal"),
    ("mother",   "mother"),
    ("mu-th-ur", "mother"),
    ("muthur",   "mother"),
]


# ── Package helpers ───────────────────────────────────────────────────────────

def _is_pkg_installed(name: str) -> bool:
    return importlib.util.find_spec(name.replace("-", "_")) is not None


def _ensure_deps(engine: str) -> bool:
    """Check and install missing packages. Prints progress. Returns True on success."""
    deps    = _KOKORO_DEPS if engine == "kokoro" else _F5_DEPS
    missing = [d for d in deps if not _is_pkg_installed(d)]
    if not missing:
        return True

    size_hint = "(~300MB first run)" if engine == "kokoro" else "(~2GB first run)"
    print(f"  {BOLD}Installing voice engine {size_hint}: {', '.join(missing)}...{RESET}")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", *missing],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode != 0:
            print(f"  {RED}✗ Install failed:{RESET} {result.stderr.strip()[:300]}")
            return False
        print(f"  {GREEN}✓ Installed{RESET}")
        return True
    except Exception as e:
        print(f"  {RED}✗ Install error: {e}{RESET}")
        return False


# ── Identity helpers ──────────────────────────────────────────────────────────

def _persona_slug(identity: dict) -> str:
    """Normalise identity name to a persona slug."""
    name = identity.get("name", "").lower().replace(".", "").replace(" ", "")
    for pattern, slug in _PERSONA_MATCHERS:
        if pattern in name:
            return slug
    return "default"


def _get_sample_path(identity: dict) -> Path | None:
    """Return path to .claude/voices/<slug>.wav|mp3 if it exists, else None."""
    slug = _persona_slug(identity)
    for ext in (".wav", ".mp3"):
        p = VOICES_DIR / f"{slug}{ext}"
        if p.exists():
            return p
    return None


def _select_engine(identity: dict) -> str:
    """Return 'kokoro' or 'f5' based on config and available sample files."""
    cfg = identity.get("voice", {})
    explicit = cfg.get("engine", "auto")
    if explicit in ("kokoro", "f5"):
        return explicit
    return "f5" if _get_sample_path(identity) else "kokoro"


def _get_kokoro_voice(identity: dict) -> tuple[str, float]:
    """Return (kokoro_voice_id, final_speed) for this identity."""
    slug              = _persona_slug(identity)
    voice_id, base_sp = _KOKORO_VOICE_MAP.get(slug, _KOKORO_VOICE_MAP["default"])
    user_sp           = float(identity.get("voice", {}).get("speed", 1.0))
    return voice_id, round(base_sp * user_sp, 3)


def _voice_cfg(identity: dict) -> dict:
    return identity.get("voice", {})


# ── Audio generation ──────────────────────────────────────────────────────────

def _generate_kokoro(text: str, voice_id: str, speed: float, out: Path) -> bool:
    """Generate speech with Kokoro-82M. Returns True on success."""
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline

        lang_code = "b" if voice_id.startswith("b") else "a"
        pipeline  = KPipeline(lang_code=lang_code)
        generator = pipeline(text, voice=voice_id, speed=speed, split_pattern=r"\n+")

        chunks = [audio for _, _, audio in generator]
        if not chunks:
            return False

        sf.write(str(out), np.concatenate(chunks), 24000)
        return out.exists() and out.stat().st_size > 0
    except Exception:
        return False


def _generate_f5(text: str, sample: Path, speed: float, out: Path) -> bool:
    """Generate speech with F5-TTS voice cloning. Returns True on success."""
    try:
        import soundfile as sf
        from f5_tts.api import F5TTS

        f5          = F5TTS(model="F5TTS_v1_Base")
        wav, sr, _  = f5.infer(
            ref_file=str(sample),
            ref_text="",
            gen_text=text,
            speed=speed,
        )
        sf.write(str(out), wav, sr)
        return out.exists() and out.stat().st_size > 0
    except Exception:
        return False


def _play_async(path: Path) -> None:
    """Play audio non-blocking in a daemon thread, then delete the temp file."""
    def _worker():
        try:
            from playsound3 import playsound
            playsound(str(path))
        except Exception:
            pass
        finally:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass

    threading.Thread(target=_worker, daemon=True).start()


# ── Core public API ───────────────────────────────────────────────────────────

def is_enabled(identity: dict | None = None) -> bool:
    """Return True if voice is enabled in identity config."""
    if identity is None:
        try:
            from apex_identity import get_identity
            identity = get_identity()
        except Exception:
            return False
    return bool(_voice_cfg(identity).get("enabled", False))


def speak(text: str, identity: dict | None = None) -> None:
    """
    Speak text asynchronously. Returns immediately — never blocks the terminal.
    Silent no-op if voice is disabled or dependencies are not installed.
    Installs are NOT triggered from this path; use setup/enable for that.
    """
    try:
        if identity is None:
            from apex_identity import get_identity
            identity = get_identity()
    except Exception:
        return

    if not is_enabled(identity):
        return

    text = text.strip()
    if not text:
        return

    engine = _select_engine(identity)
    speed  = float(_voice_cfg(identity).get("speed", 1.0))
    sample = _get_sample_path(identity) if engine == "f5" else None

    def _worker():
        try:
            fd, tmp = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            out = Path(tmp)

            success = False

            # Primary: F5-TTS with voice sample
            if engine == "f5" and sample:
                success = _generate_f5(text, sample, speed, out)

            # Fallback (or primary when no sample): Kokoro
            if not success:
                voice_id, kokoro_speed = _get_kokoro_voice(identity)
                success = _generate_kokoro(text, voice_id, kokoro_speed, out)

            if success:
                _play_async(out)
            else:
                out.unlink(missing_ok=True)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


def speak_greeting(identity: dict | None = None) -> None:
    """Speak the identity's greeting phrase if voice + speak_greeting are enabled."""
    try:
        if identity is None:
            from apex_identity import get_identity
            identity = get_identity()
        if not _voice_cfg(identity).get("speak_greeting", True):
            return
        greeting = identity.get("greeting", "").strip()
        if greeting:
            speak(greeting, identity)
    except Exception:
        pass


# ── Identity persistence ──────────────────────────────────────────────────────

def _load_raw_identity() -> dict:
    if ID_FILE.exists():
        try:
            return json.loads(ID_FILE.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            pass
    return {}


def _save_voice_cfg(updates: dict) -> None:
    """Patch voice keys in identity.json atomically."""
    data        = _load_raw_identity()
    voice       = data.get("voice", {})
    voice.update(updates)
    data["voice"] = voice
    ID_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=ID_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, ID_FILE)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def enable_voice() -> None:
    _save_voice_cfg({"enabled": True})
    print(f"  {GREEN}✓ Voice enabled{RESET}")


def disable_voice() -> None:
    _save_voice_cfg({"enabled": False})
    print(f"  {GREEN}✓ Voice disabled{RESET}")


# ── Blocking test (used by setup + CLI test) ──────────────────────────────────

def _test_blocking(text: str, identity: dict) -> None:
    """Generate and play audio synchronously. Used only for interactive testing."""
    engine   = _select_engine(identity)
    sample   = _get_sample_path(identity) if engine == "f5" else None
    speed    = float(_voice_cfg(identity).get("speed", 1.0))

    fd, tmp = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    out = Path(tmp)

    success = False
    if engine == "f5" and sample:
        success = _generate_f5(text, sample, speed, out)
    if not success:
        voice_id, kokoro_speed = _get_kokoro_voice(identity)
        success = _generate_kokoro(text, voice_id, kokoro_speed, out)

    if success:
        try:
            from playsound3 import playsound
            playsound(str(out))
            print(f"  {GREEN}✓ Voice test passed{RESET}")
        except Exception as e:
            print(f"  {YELLOW}⚠ Playback error: {e}{RESET}")
        finally:
            out.unlink(missing_ok=True)
    else:
        out.unlink(missing_ok=True)
        print(f"  {RED}✗ Audio generation failed — check engine installation{RESET}")


# ── Interactive setup ─────────────────────────────────────────────────────────

def setup_voice() -> None:
    """Interactive voice configuration wizard."""
    try:
        from apex_identity import get_identity
        identity = get_identity()
    except Exception:
        identity = {}

    cfg    = _voice_cfg(identity)
    slug   = _persona_slug(identity)
    sample = _get_sample_path(identity)

    print(f"\n{BOLD}APEX Voice Setup{RESET}")
    print(f"  {'Status:':20} {'enabled' if cfg.get('enabled') else 'disabled'}")
    print(f"  {'Engine setting:':20} {cfg.get('engine', 'auto')}")
    if sample:
        print(f"  {'Sample found:':20} {sample}")
        print(f"  {'Active engine:':20} F5-TTS (voice cloning)")
    else:
        vid, spd = _KOKORO_VOICE_MAP.get(slug, _KOKORO_VOICE_MAP["default"])
        print(f"  {'Kokoro voice:':20} {vid} @ {spd}x speed")
        print(f"  {DIM}To enable cloning: .claude/voices/{slug}.wav{RESET}")
    print()

    if input("  Enable voice? (y/N): ").strip().lower() != "y":
        print(f"  {DIM}Unchanged.{RESET}")
        return

    active_engine = "f5" if sample else "kokoro"
    if not _ensure_deps(active_engine):
        print(f"  {RED}✗ Dependency install failed. Voice not enabled.{RESET}")
        return

    speak_resp = input("  Speak Claude's responses aloud? (y/N): ").strip().lower() == "y"

    _save_voice_cfg({
        "enabled":         True,
        "engine":          "auto",
        "speed":           cfg.get("speed", 1.0),
        "volume":          cfg.get("volume", 1.0),
        "speak_greeting":  True,
        "speak_responses": speak_resp,
    })
    print(f"  {GREEN}✓ Voice enabled{RESET}")

    if not sample:
        print(f"\n  {DIM}Drop a 15-30s clean WAV to enable voice cloning:{RESET}")
        print(f"  {DIM}  .claude/voices/{slug}.wav{RESET}")
        print(f"  {DIM}APEX auto-detects it on next run — no config needed.{RESET}")

    if input("\n  Test voice now? (Y/n): ").strip().lower() != "n":
        name = identity.get("name", "APEX")
        print(f"  {DIM}Generating...{RESET}")
        _test_blocking(f"Voice system online. {name} is ready.", identity)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, Exception):
        pass

    args = sys.argv[1:]
    cmd  = args[0] if args else "status"

    try:
        from apex_identity import get_identity
        identity = get_identity()
    except Exception:
        identity = {}

    if cmd == "speak":
        if len(args) < 2:
            print("Usage: apex_voice.py speak \"<text>\"")
            sys.exit(1)
        if not is_enabled(identity):
            print(f"  {YELLOW}Voice is disabled — run: apex_voice.py enable{RESET}")
            sys.exit(0)
        speak(" ".join(args[1:]), identity)
        import time; time.sleep(0.3)   # give daemon thread time to start

    elif cmd == "greeting":
        if not is_enabled(identity):
            print(f"  {YELLOW}Voice is disabled — run: apex_voice.py enable{RESET}")
            sys.exit(0)
        speak_greeting(identity)
        import time; time.sleep(0.3)

    elif cmd == "enable":
        active_engine = "f5" if _get_sample_path(identity) else "kokoro"
        if not _ensure_deps(active_engine):
            sys.exit(1)
        enable_voice()

    elif cmd == "disable":
        disable_voice()

    elif cmd == "setup":
        setup_voice()

    elif cmd == "test":
        active_engine = _select_engine(identity)
        if not _ensure_deps(active_engine):
            sys.exit(1)
        _test_blocking(f"Voice system online. {identity.get('name', 'APEX')} is ready.", identity)

    elif cmd == "status":
        cfg    = _voice_cfg(identity)
        slug   = _persona_slug(identity)
        sample = _get_sample_path(identity)
        on_off = f"{GREEN}enabled{RESET}" if cfg.get("enabled") else f"{RED}disabled{RESET}"

        print(f"\n{BOLD}APEX Voice Status{RESET}")
        print(f"  {'enabled:':22} {on_off}")
        print(f"  {'engine:':22} {cfg.get('engine', 'auto')}")
        print(f"  {'speak_greeting:':22} {cfg.get('speak_greeting', True)}")
        print(f"  {'speak_responses:':22} {cfg.get('speak_responses', False)}")
        print(f"  {'speed:':22} {cfg.get('speed', 1.0)}")
        print(f"  {'persona slug:':22} {slug}")
        if sample:
            print(f"  {'sample:':22} {sample}  {GREEN}→ F5-TTS active{RESET}")
        else:
            vid, spd = _KOKORO_VOICE_MAP.get(slug, _KOKORO_VOICE_MAP["default"])
            print(f"  {'kokoro voice:':22} {vid} @ {spd}x")
            print(f"  {DIM}add .claude/voices/{slug}.wav to enable cloning{RESET}")

        kokoro_ok = all(_is_pkg_installed(d) for d in _KOKORO_DEPS)
        f5_ok     = all(_is_pkg_installed(d) for d in _F5_DEPS)
        print(f"\n  {'kokoro installed:':22} {GREEN+'yes'+RESET if kokoro_ok else DIM+'no'+RESET}")
        print(f"  {'f5-tts installed:':22} {GREEN+'yes'+RESET if f5_ok else DIM+'no'+RESET}")
        print()

    else:
        print("Usage: apex_voice.py [speak <text>|greeting|enable|disable|setup|test|status]")
        sys.exit(1)


if __name__ == "__main__":
    main()
