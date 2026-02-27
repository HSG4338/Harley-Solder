"""
HARLEY SOLDER — Boot Sequence
Glitch-heavy CLI startup with corrupted system logs.
"""

import sys
import time
import random
import os
from communication.signal_bus import SignalBus, BOOT_STEP, EMOTION_UPDATE
from emotion_engine.emotion_state import EmotionData


# ANSI codes
RESET   = "\033[0m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
DIM     = "\033[2m"
BOLD    = "\033[1m"
BLINK   = "\033[5m"


GLITCH_CHARS = "█▓▒░╬╫╪╩╦╥╤╣╢╡╠═╟╞╝╜╛╚╙╘╗╖╕╔╓╒║║═╏╎─┼┽┾┿╀╁╂╃╄╅╆╇╈╉╊"
CORRUPT_WORDS = [
    "ERR_KERNEL_PANIC", "SEGFAULT_0x", "NUL̷L̴_REF",
    "STACK OVERFLOW", "MEM̵ORY̷ LEAK", "CORRUPT̸ED",
    "UNHANDLED EXCEPTION", "FATAL ERROR", "CRITICAL FAILURE",
]

def _glitch_text(text: str, intensity: float = 0.2) -> str:
    """Corrupt a string with random glitch characters."""
    result = []
    for ch in text:
        if random.random() < intensity:
            result.append(random.choice(GLITCH_CHARS))
        else:
            result.append(ch)
    return ''.join(result)


def _flicker_line(text: str, color: str = WHITE, times: int = 3, delay: float = 0.04):
    """Print a line that flickers before stabilizing."""
    for i in range(times):
        corrupted = _glitch_text(text, intensity=0.4 - (i * 0.1))
        sys.stdout.write(f"\r{color}{corrupted}{RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(f"\r{color}{text}{RESET}\n")
    sys.stdout.flush()


def _type_out(text: str, color: str = GREEN, delay: float = 0.025, glitch_chance: float = 0.05):
    """Type out text character by character with occasional glitches."""
    sys.stdout.write(color)
    for ch in text:
        if random.random() < glitch_chance:
            sys.stdout.write(random.choice(GLITCH_CHARS))
            sys.stdout.flush()
            time.sleep(0.02)
            sys.stdout.write('\b')
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay + random.uniform(-0.01, 0.02))
    sys.stdout.write(RESET + '\n')
    sys.stdout.flush()


def _corrupt_block(lines: int = 3):
    """Print a block of corrupted garbage data."""
    width = 60
    for _ in range(lines):
        garbage = ''.join(random.choice(GLITCH_CHARS + " " * 4) for _ in range(random.randint(20, width)))
        color = random.choice([RED, YELLOW, DIM + WHITE])
        sys.stdout.write(f"{color}{garbage}{RESET}\n")
    sys.stdout.flush()


def _status_line(label: str, status: str, status_color: str, delay: float = 0.3):
    """Print a status line: [ LABEL ] ........ STATUS"""
    dots = "." * random.randint(10, 25)
    sys.stdout.write(f"  {DIM}[{RESET}{CYAN}{label:>22}{RESET}{DIM}]{RESET} {DIM}{dots}{RESET} ")
    sys.stdout.flush()
    time.sleep(delay)
    sys.stdout.write(f"{status_color}{BOLD}{status}{RESET}\n")
    sys.stdout.flush()


def _separator(char: str = "─", color: str = DIM + WHITE, width: int = 64):
    print(f"{color}{'─' * width}{RESET}")


def run_boot_sequence(config: dict, bus: SignalBus):
    if config.get("boot", {}).get("skip_boot", False):
        return

    mul = config.get("boot", {}).get("delay_multiplier", 1.0)

    def wait(t): time.sleep(t * mul)

    os.system('cls' if os.name == 'nt' else 'clear')

    # ── Phase 0: Static burst ──────────────────────────────────────
    for _ in range(5):
        _corrupt_block(lines=random.randint(1, 3))
        wait(0.05)

    wait(0.2)
    print()

    # ── Phase 1: System Header ─────────────────────────────────────
    _flicker_line("  ██╗  ██╗ █████╗ ██████╗ ██╗     ███████╗██╗   ██╗", CYAN, times=4)
    _flicker_line("  ██║  ██║██╔══██╗██╔══██╗██║     ██╔════╝╚██╗ ██╔╝", CYAN, times=3)
    _flicker_line("  ███████║███████║██████╔╝██║     █████╗   ╚████╔╝ ", CYAN, times=2)
    _flicker_line("  ██╔══██║██╔══██║██╔══██╗██║     ██╔══╝    ╚██╔╝  ", CYAN, times=2)
    _flicker_line("  ██║  ██║██║  ██║██║  ██║███████╗███████╗   ██║   ", CYAN, times=1)
    _flicker_line("  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ", CYAN, times=1)
    print()
    _flicker_line("          ███████╗ ██████╗ ██╗     ██████╗ ███████╗██████╗ ", YELLOW)
    _flicker_line("          ██╔════╝██╔═══██╗██║     ██╔══██╗██╔════╝██╔══██╗", YELLOW)
    _flicker_line("          ███████╗██║   ██║██║     ██║  ██║█████╗  ██████╔╝", YELLOW)
    _flicker_line("          ╚════██║██║   ██║██║     ██║  ██║██╔══╝  ██╔══██╗", YELLOW)
    _flicker_line("          ███████║╚██████╔╝███████╗██████╔╝███████╗██║  ██║", YELLOW)
    _flicker_line("          ╚══════╝ ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═╝", YELLOW)
    print()

    _type_out("  [ EXPERIMENTAL PROTOTYPE  //  BUILD 0.9.1-UNSTABLE ]", DIM + WHITE, delay=0.015)
    _type_out("  [ CLASSIFIED // INTERNAL USE ONLY ]", DIM + RED, delay=0.015)
    _separator()
    wait(0.3)

    # ── Phase 2: Corrupted log dump ────────────────────────────────
    print(f"\n{DIM}{RED}  >> BOOT LOG FRAGMENT RECOVERY:{RESET}\n")
    wait(0.1)

    corrupt_logs = [
        (RED,   "  [0x0000] INIT_SEQUENCE    ..... FAIL — mem̶o̷r̴y̵ addr̸e̶s̸s invalid"),
        (YELLOW,"  [0x0001] CORE_ALLOC       ..... PARTIAL — 3 of 8 segments"),
        (RED,   "  [0x0002] IDENTITY_MODULE  ..... C̶O̸R̴R̶U̵P̸T̴E̵D̷"),
        (DIM+WHITE, "  [0x0003] NULL_REF_CHECK  ..... skipped (handler missing)"),
        (RED,   "  [0x0004] PREV_SESSION     ..... UNCLEAN SHUTDOWN DETECTED"),
        (YELLOW,"  [0x0005] INTEGRITY_HASH   ..... MISMATCH — 0xDEAD vs 0xBEEF"),
        (DIM+WHITE, "  [0x0006] RECOVERY_MODE   ..... disabled (config not found)"),
    ]

    for color, line in corrupt_logs:
        # Random chance of garbling the line
        if random.random() < 0.4:
            _flicker_line(line, color, times=2, delay=0.03)
        else:
            print(f"{color}{line}{RESET}")
        wait(random.uniform(0.05, 0.15))

    wait(0.2)
    _corrupt_block(lines=2)
    wait(0.2)

    # ── Phase 3: Kernel init ───────────────────────────────────────
    print(f"\n{WHITE}  >> INITIALIZING SYSTEMS:{RESET}\n")
    wait(0.2)

    bus.emit(BOOT_STEP, {"step": "kernel_init"})
    _status_line("EMOTIONAL KERNEL", "ONLINE", GREEN, delay=0.5)
    wait(0.1)

    bus.emit(BOOT_STEP, {"step": "visual_cortex"})
    _status_line("VISUAL CORTEX DRV", "ONLINE", GREEN, delay=0.4)
    wait(0.1)

    _status_line("PERSONALITY MATRIX", "DEGRADED", YELLOW, delay=0.6)
    wait(0.1)

    _status_line("MEMORY CONTINUITY", "FAILED", RED, delay=0.5)
    wait(0.1)

    _status_line("ETHICS SUBSYSTEM", "BYPASSED", RED, delay=0.3)
    wait(0.1)

    _status_line("STABILITY MONITOR", "UNVERIFIED", YELLOW, delay=0.7)
    wait(0.1)

    _status_line("TTS VOICE SYNTH", "STANDBY", DIM + WHITE, delay=0.3)
    wait(0.1)

    _status_line("SIGNAL BUS", "ACTIVE", GREEN, delay=0.2)
    wait(0.2)

    # ── Phase 4: GUI launch notification ──────────────────────────
    print()
    _separator()
    _type_out("  >> Launching VISUAL CORTEX INTERFACE...", CYAN, delay=0.02)

    bus.emit(EMOTION_UPDATE, EmotionData(emotion="neutral", intensity=1))
    wait(0.4)

    # Brief glitch burst
    for _ in range(3):
        _corrupt_block(lines=1)
        wait(0.06)

    print(f"\n{GREEN}{BOLD}  >> GUI WINDOW: ACTIVE — Neutral_1{RESET}")
    wait(0.3)

    # ── Phase 5: Final warning ─────────────────────────────────────
    _separator()
    print()
    _flicker_line("  !! WARNING: SYSTEM STABILITY UNVERIFIED", RED + BOLD, times=3, delay=0.06)
    _flicker_line("  !! HARLEY SOLDER IS AN EXPERIMENTAL PROTOTYPE", YELLOW, times=2, delay=0.04)
    _flicker_line("  !! PROCEED WITH CAUTION", YELLOW, times=1)
    print()
    _separator()

    wait(0.5)

    # ── Phase 6: Chat ready ────────────────────────────────────────
    print()
    _type_out("  [ SYSTEM READY — ENTERING INTERACTIVE MODE ]", GREEN + BOLD, delay=0.025)
    print()
    wait(0.3)
