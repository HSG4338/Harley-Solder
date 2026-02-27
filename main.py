"""
HARLEY SOLDER v1 — Main Entry Point
Split-interface AI companion: CLI (mind) + GUI (eye)
"""

import sys
import os
import threading
import traceback


def _write_error_log(exc: Exception):
    """Write crash info to error.log so flash-crashes can be diagnosed."""
    try:
        with open("error.log", "w") as f:
            f.write("HARLEY SOLDER v1 — CRASH REPORT\n")
            f.write("=" * 50 + "\n\n")
            traceback.print_exc(file=f)
            f.write("\n\nPython: " + sys.version + "\n")
            f.write("CWD: " + os.getcwd() + "\n")
    except Exception:
        pass


def main():
    # Ensure we're running from the project root
    # (handles double-click from any directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    try:
        from config.settings import load_config
        from cli_boot.boot_sequence import run_boot_sequence
        from emotion_engine.emotion_state import EmotionState
        from ui.eye_window import launch_gui
        from ai_core.chat_loop import run_chat_loop
        from communication.signal_bus import SignalBus
    except ImportError as e:
        print(f"\n  [FATAL] Import failed: {e}")
        print(f"  Make sure PyQt6 is installed: pip install PyQt6")
        print(f"\n  Full error written to error.log\n")
        _write_error_log(e)
        input("  Press Enter to exit...")
        sys.exit(1)

    config = load_config()
    bus = SignalBus()
    emotion_state = EmotionState(bus)

    # Boot sequence runs first, fully, in CLI
    try:
        run_boot_sequence(config, bus)
    except Exception as e:
        print(f"\n  [WARN] Boot sequence error (non-fatal): {e}")

    # Chat loop runs in a daemon thread so it dies when Qt exits
    chat_thread = threading.Thread(
        target=_safe_chat_loop,
        args=(config, bus, emotion_state, run_chat_loop),
        daemon=True,
        name="HarleyChatLoop"
    )
    chat_thread.start()

    # Qt GUI runs on main thread — blocks here until window is closed
    try:
        launch_gui(config, bus, emotion_state)
    except Exception as e:
        print(f"\n  [FATAL] GUI crashed: {e}")
        _write_error_log(e)
        traceback.print_exc()
        input("\n  Press Enter to exit...")
        sys.exit(1)


def _safe_chat_loop(config, bus, emotion_state, run_chat_loop):
    """Wrapper so chat thread errors are visible, not silently swallowed."""
    try:
        run_chat_loop(config, bus, emotion_state)
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n  [FATAL] Chat loop crashed: {e}")
        traceback.print_exc()
        _write_error_log(e)


def _write_error_log(exc):
    try:
        with open("error.log", "w") as f:
            f.write("HARLEY SOLDER v1 — CRASH REPORT\n")
            f.write("=" * 50 + "\n\n")
            traceback.print_exc(file=f)
            f.write(f"\nPython: {sys.version}\n")
            f.write(f"CWD: {os.getcwd()}\n")
    except Exception:
        pass


if __name__ == "__main__":
    main()
