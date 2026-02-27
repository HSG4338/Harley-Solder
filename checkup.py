"""
HARLEY SOLDER — System Checkup
Diagnostic tool. Run before launch to verify everything is healthy.

Usage: python checkup.py
       python checkup.py --fix     (attempt auto-fixes)
       python checkup.py --quiet   (minimal output, exit code only)
"""

import sys
import os
import json
import platform
import importlib
import subprocess
import argparse
from pathlib import Path


# ── ANSI ─────────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
DIM    = "\033[2m"
BOLD   = "\033[1m"

def c(text, color): return f"{color}{text}{RESET}"
def ok(msg):    print(f"  {c('✓', GREEN)}  {msg}")
def warn(msg):  print(f"  {c('!', YELLOW)}  {c(msg, YELLOW)}")
def fail(msg):  print(f"  {c('✗', RED)}  {c(msg, RED)}")
def info(msg):  print(f"  {c('·', DIM)}  {DIM}{msg}{RESET}")
def head(msg):  print(f"\n  {c('──', CYAN)} {c(msg, BOLD + WHITE)}")


RESULTS = {"pass": 0, "warn": 0, "fail": 0}

def record(status):
    RESULTS[status] += 1


# ── CHECKS ────────────────────────────────────────────────────────────────────

def check_python():
    head("PYTHON RUNTIME")
    ver = sys.version_info
    ver_str = f"{ver.major}.{ver.minor}.{ver.micro}"
    info(f"Executable: {sys.executable}")

    if ver.major < 3 or (ver.major == 3 and ver.minor < 10):
        fail(f"Python {ver_str} — 3.10+ required")
        record("fail")
    elif ver.major == 3 and ver.minor < 11:
        warn(f"Python {ver_str} — works, but 3.11+ recommended")
        record("warn")
    else:
        ok(f"Python {ver_str}")
        record("pass")

    info(f"Platform: {platform.system()} {platform.release()} ({platform.machine()})")
    if platform.system() != "Windows":
        warn("Harley Solder is designed for Windows. Other platforms may work but are unsupported.")
        record("warn")
    else:
        ok(f"Windows detected")
        record("pass")


def check_dependencies(auto_fix: bool):
    head("DEPENDENCIES")

    deps = [
        ("PyQt6",      "PyQt6",      True,  "GUI framework — required"),
        ("Pillow",     "PIL",        False, "Eye asset generator — optional"),
        ("anthropic",  "anthropic",  False, "Live Claude API — optional"),
        ("pyttsx3",    "pyttsx3",    False, "Text-to-speech — optional"),
    ]

    for pip_name, import_name, required, desc in deps:
        try:
            mod = importlib.import_module(import_name)
            version = getattr(mod, "__version__", "?")
            ok(f"{pip_name} {version}  —  {desc}")
            record("pass")
        except ImportError:
            if required:
                fail(f"{pip_name} NOT FOUND  —  {desc}")
                record("fail")
                if auto_fix:
                    print(f"     → Auto-installing {pip_name}...")
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", pip_name, "--quiet"],
                        capture_output=True
                    )
                    if result.returncode == 0:
                        ok(f"{pip_name} installed successfully")
                        record("pass")
                    else:
                        fail(f"Auto-install failed: {result.stderr.decode()[:80]}")
                        record("fail")
                else:
                    info(f"  Fix: pip install {pip_name}")
            else:
                warn(f"{pip_name} not installed  —  {desc}")
                record("warn")
                info(f"  Install: pip install {pip_name}")


def check_project_files():
    head("PROJECT FILES")

    required_files = [
        "main.py",
        "requirements.txt",
        "config/settings.py",
        "config/config.json",
        "communication/__init__.py",
        "cli_boot/boot_sequence.py",
        "ai_core/chat_loop.py",
        "emotion_engine/emotion_state.py",
        "ui/eye_window.py",
        "ui/eye_widget.py",
        "ui/eye_window.py",
        "ui/glitch_renderer.py",
        "ui/pulse_system.py",
        "ui/asset_manager.py",
        "tts/voice_engine.py",
        "generate_assets.py",
    ]

    optional_files = [
        "install.bat",
        "checkup.py",
        "README.md",
    ]

    for f in required_files:
        path = Path(f)
        if path.exists():
            size = path.stat().st_size
            ok(f"{f}  ({size} bytes)")
            record("pass")
        else:
            fail(f"{f}  MISSING")
            record("fail")

    print()
    for f in optional_files:
        path = Path(f)
        if path.exists():
            ok(f"{f}  (optional)")
            record("pass")
        else:
            info(f"{f}  not present (optional)")


def check_syntax():
    head("SYNTAX VALIDATION")

    py_files = list(Path(".").rglob("*.py"))
    py_files = [f for f in py_files if ".git" not in str(f)]

    import ast
    errors = 0
    for pyfile in sorted(py_files):
        try:
            with open(pyfile, encoding="utf-8") as fh:
                source = fh.read()
            ast.parse(source, filename=str(pyfile))
            ok(f"{pyfile}")
            record("pass")
        except SyntaxError as e:
            fail(f"{pyfile}  —  Line {e.lineno}: {e.msg}")
            record("fail")
            errors += 1
        except Exception as e:
            warn(f"{pyfile}  —  {e}")
            record("warn")

    if errors == 0 and len(py_files) > 0:
        info(f"All {len(py_files)} Python files parsed successfully")


def check_config():
    head("CONFIGURATION")

    config_path = Path("config/config.json")
    if not config_path.exists():
        warn("config/config.json not found — defaults will be used")
        record("warn")
        return

    try:
        with open(config_path) as f:
            cfg = json.load(f)
        ok("config/config.json — valid JSON")
        record("pass")
    except json.JSONDecodeError as e:
        fail(f"config/config.json — JSON parse error: {e}")
        record("fail")
        return

    # Check specific config values
    use_api = cfg.get("ai", {}).get("use_anthropic_api", False)
    if use_api:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            fail("use_anthropic_api=true but ANTHROPIC_API_KEY env var not set")
            record("fail")
            info("  Fix: set ANTHROPIC_API_KEY=your_key_here in environment")
        elif not api_key.startswith("sk-"):
            warn("ANTHROPIC_API_KEY set but doesn't look like a valid key (should start with 'sk-')")
            record("warn")
        else:
            ok(f"ANTHROPIC_API_KEY set (sk-...{api_key[-4:]})")
            record("pass")
    else:
        ok("use_anthropic_api=false — local response engine active")
        record("pass")

    # Window config
    w = cfg.get("window", {})
    info(f"Window: {w.get('width', 320)}×{w.get('height', 320)}  "
         f"frameless={w.get('frameless', True)}  "
         f"always_on_top={w.get('always_on_top', True)}")

    # TTS config
    tts = cfg.get("tts", {})
    if tts.get("enabled", False):
        info(f"TTS: enabled (engine: {tts.get('engine', 'pyttsx3')})")
    else:
        info("TTS: disabled")


def check_assets():
    head("EYE ASSETS")

    assets_dir = Path("assets/eyes")
    if not assets_dir.exists():
        warn("assets/eyes/ directory not found")
        record("warn")
        info("  Fix: mkdir assets\\eyes")
        return

    assets = list(assets_dir.glob("*.png")) + list(assets_dir.glob("*.webp"))

    if not assets:
        warn("No eye assets found in assets/eyes/")
        record("warn")
        info("  Fix: python generate_assets.py")
        info("  Note: Harley will use procedural rendering as fallback")
        return

    # Parse and categorize
    found_emotions = set()
    found_intensities = {}
    malformed = []
    total_size = 0

    for asset in sorted(assets):
        stem = asset.stem.lower()
        parts = stem.rsplit("_", 1)
        if len(parts) == 2:
            emotion, intensity_str = parts
            try:
                intensity = int(intensity_str)
                found_emotions.add(emotion)
                if emotion not in found_intensities:
                    found_intensities[emotion] = []
                found_intensities[emotion].append(intensity)
                total_size += asset.stat().st_size
            except ValueError:
                malformed.append(asset.name)
        else:
            malformed.append(asset.name)

    ok(f"{len(assets)} asset(s) found  ({total_size // 1024}KB total)")
    ok(f"Emotions covered: {', '.join(sorted(found_emotions))}")
    record("pass")

    # Check for neutral_1 fallback
    neutral_1 = assets_dir / "neutral_1.png"
    neutral_1_webp = assets_dir / "neutral_1.webp"
    if neutral_1.exists() or neutral_1_webp.exists():
        ok("neutral_1 fallback asset present")
        record("pass")
    else:
        warn("neutral_1.png not found — fallback chain broken")
        record("warn")
        info("  Fix: python generate_assets.py")

    # Warn about missing intensities
    EXPECTED_EMOTIONS = {"neutral", "curious", "happy", "sad", "angry",
                          "fear", "glitch", "error", "melancholy", "confused",
                          "surprised", "excited", "disgust"}
    missing_emotions = EXPECTED_EMOTIONS - found_emotions
    if missing_emotions:
        info(f"Missing emotion sets: {', '.join(sorted(missing_emotions))}")
        info("  (Harley will fall back to neutral_1 for these)")

    if malformed:
        warn(f"Malformed asset names (ignored): {', '.join(malformed)}")
        info("  Expected format: emotion_intensity.png  (e.g. angry_2.png)")
        record("warn")


def check_display():
    head("DISPLAY / QT ENVIRONMENT")

    # Check DISPLAY env on Linux
    if platform.system() == "Linux":
        display = os.environ.get("DISPLAY", "")
        wayland = os.environ.get("WAYLAND_DISPLAY", "")
        if not display and not wayland:
            fail("No DISPLAY or WAYLAND_DISPLAY set — Qt cannot open a window")
            record("fail")
            info("  Fix: Run from a graphical session, or set DISPLAY=:0")
        else:
            ok(f"Display: {display or wayland}")
            record("pass")

    # Try importing Qt
    try:
        from PyQt6.QtWidgets import QApplication
        ok("PyQt6.QtWidgets import successful")
        record("pass")
    except ImportError:
        fail("PyQt6.QtWidgets could not be imported")
        record("fail")
    except Exception as e:
        warn(f"PyQt6 import warning: {e}")
        record("warn")

    # Check screen availability
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QScreen
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        screens = app.screens()
        ok(f"{len(screens)} screen(s) detected")
        for i, screen in enumerate(screens):
            geo = screen.geometry()
            dpi = screen.physicalDotsPerInch()
            info(f"  Screen {i}: {geo.width()}×{geo.height()} @ {dpi:.0f}dpi")
        record("pass")
    except Exception as e:
        warn(f"Could not query screens: {e}")
        record("warn")


def print_summary():
    p = RESULTS["pass"]
    w = RESULTS["warn"]
    f = RESULTS["fail"]
    total = p + w + f

    print()
    print(f"  {'═' * 56}")
    print(f"  CHECKUP COMPLETE  —  {total} checks")
    print(f"  {'═' * 56}")
    print(f"  {c(f'✓  {p} passed', GREEN)}")
    if w:
        print(f"  {c(f'!  {w} warnings', YELLOW)}")
    if f:
        print(f"  {c(f'✗  {f} failed', RED)}")
    print(f"  {'─' * 56}")

    if f == 0 and w == 0:
        print(f"\n  {c('ALL SYSTEMS NOMINAL', GREEN + BOLD)}")
        print(f"  {c('Harley Solder is ready to launch.', GREEN)}")
        print(f"\n  Run:  python main.py\n")
    elif f == 0:
        print(f"\n  {c('READY WITH WARNINGS', YELLOW + BOLD)}")
        print(f"  {c('Harley Solder should work, but review warnings above.', YELLOW)}")
        print(f"\n  Run:  python main.py\n")
    else:
        print(f"\n  {c('NOT READY — ERRORS DETECTED', RED + BOLD)}")
        print(f"  {c('Fix the issues above before launching.', RED)}")
        print(f"\n  Run:  python checkup.py --fix  to attempt auto-repair\n")

    return f == 0


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Harley Solder — System Checkup",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--fix",    action="store_true", help="Attempt auto-fixes (install missing packages)")
    parser.add_argument("--quiet",  action="store_true", help="Minimal output, exit code 0=ok 1=fail")
    args = parser.parse_args()

    if args.quiet:
        # Silent mode — just return exit code
        try:
            from PyQt6.QtWidgets import QApplication
            py_ok = sys.version_info >= (3, 10)
            files_ok = all(Path(f).exists() for f in [
                "main.py", "ui/eye_window.py", "ai_core/chat_loop.py"
            ])
            sys.exit(0 if (py_ok and files_ok) else 1)
        except ImportError:
            sys.exit(1)

    # Header
    print()
    print(c("  ╔══════════════════════════════════════════════════╗", CYAN))
    print(c("  ║       HARLEY SOLDER  //  SYSTEM CHECKUP          ║", CYAN))
    print(c("  ║       Build 0.9.1-UNSTABLE  //  Diagnostic       ║", CYAN))
    print(c("  ╚══════════════════════════════════════════════════╝", CYAN))

    if args.fix:
        print(c("\n  [--fix mode active — will attempt auto-repairs]\n", YELLOW))

    # Ensure we're in the project root
    if not Path("main.py").exists():
        print()
        fail("main.py not found in current directory.")
        fail("Please run checkup.py from the harley_solder/ project root.")
        print()
        sys.exit(1)

    check_python()
    check_dependencies(auto_fix=args.fix)
    check_project_files()
    check_syntax()
    check_config()
    check_assets()
    check_display()

    success = print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
