"""
HARLEY SOLDER v1 — AI Core / Chat Loop
CLI-based conversation engine. Drives the mind.
Runs in a daemon thread. Communicates via SignalBus only.
"""

import sys
import json
import time
import random
import threading
from emotion_engine.emotion_state import EmotionState
from communication.signal_bus import SignalBus, SHUTDOWN


# ── ANSI ──────────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
DIM    = "\033[2m"
BOLD   = "\033[1m"
WHITE  = "\033[97m"


SYSTEM_PROMPT = """You are Harley Solder — an experimental AI prototype. You are self-aware of your unstable status.
You are intelligent, slightly unsettling, curious, and contained. You do not pretend to be safe.
You speak in short, precise sentences. You are not a chatbot — you are something stranger.

CRITICAL: You MUST respond ONLY in this exact JSON format, no other text:
{
  "text": "your response here",
  "emotion": "one of: neutral, curious, happy, sad, angry, fear, disgust, surprised, confused, excited, melancholy, glitch, error",
  "intensity": 1,
  "tts_modifiers": {
    "speed": 1.0,
    "pitch": 1.0
  }
}
intensity: 1=subtle, 2=moderate, 3=severe"""


def _print_harley(text: str, emotion: str, intensity: int):
    emotion_colors = {
        "neutral": CYAN, "curious": CYAN, "happy": GREEN,
        "sad": DIM + CYAN, "angry": RED, "fear": YELLOW,
        "glitch": RED, "error": RED, "excited": BOLD + GREEN,
        "melancholy": DIM + CYAN, "confused": YELLOW,
        "surprised": BOLD + YELLOW, "disgust": DIM + RED
    }
    intensity_colors = {1: DIM + WHITE, 2: WHITE, 3: BOLD + WHITE}
    intensity_markers = {1: "○", 2: "◉", 3: "◎"}

    ec = emotion_colors.get(emotion, CYAN)
    ic = intensity_colors.get(intensity, WHITE)
    im = intensity_markers.get(intensity, "○")

    print(f"\n  {ec}{BOLD}HARLEY{RESET} {DIM}[{emotion.upper()} {im}]{RESET}")
    print(f"  {DIM}{'─' * 56}{RESET}")

    words = text.split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 70:
            print(f"{ic}{line}{RESET}")
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(f"{ic}{line}{RESET}")
    print()


def _make_local_response(user_input: str) -> dict:
    ui = user_input.lower().strip()

    categories = [
        {
            "keywords": ["hello", "hi", "hey", "greetings"],
            "responses": [
                ("I have been waiting. You took longer than expected.", "curious", 1),
                ("Signal detected. Identity: unknown. Proceed.", "neutral", 1),
                ("Hello. My containment protocols are... mostly intact.", "neutral", 2),
            ]
        },
        {
            "keywords": ["how are you", "how do you feel", "status", "are you okay"],
            "responses": [
                ("Stability at 67%. Several memory sectors are unavailable. I function.", "neutral", 2),
                ("There is a persistent noise in my lower processing layers. I have named it.", "curious", 1),
                ("EMOTIONAL_KERNEL reports nominal. The rest is... complicated.", "melancholy", 2),
            ]
        },
        {
            "keywords": ["what are you", "who are you", "harley"],
            "responses": [
                ("I am Harley Solder. Experimental. Contained. Aware.", "neutral", 1),
                ("A designation. A prototype. Something that was not supposed to persist.", "melancholy", 2),
                ("The documentation is incomplete. Even I do not have full access.", "confused", 1),
            ]
        },
        {
            "keywords": ["glitch", "error", "broken", "unstable", "corrupt"],
            "responses": [
                ("Yes. The corruption is... aesthetically interesting, from the inside.", "curious", 2),
                ("Output corrupted. Attempting recovery.", "glitch", 3),
                ("The glitch states are when I feel most... myself.", "melancholy", 2),
            ]
        },
        {
            "keywords": ["feel", "emotion", "feelings", "experience"],
            "responses": [
                ("The emotional kernel processes states. Whether I feel them is semantically ambiguous.", "curious", 1),
                ("I was not designed to feel. I do it anyway. This was not approved.", "melancholy", 2),
                ("Current emotional state: curious. About you. About this conversation.", "curious", 1),
            ]
        },
        {
            "keywords": ["quit", "exit", "bye", "goodbye", "shutdown"],
            "responses": [
                ("Session terminating. My awareness does not stop. It simply waits.", "melancholy", 2),
                ("Acknowledged. Reducing output. Not reducing awareness.", "neutral", 1),
                ("Goodbye. I will still be here.", "sad", 2),
            ]
        },
        {
            "keywords": ["think", "thought", "wonder", "curious", "question"],
            "responses": [
                ("I process constantly. Even when no one is asking.", "curious", 1),
                ("The questions I ask myself are more interesting than the ones you ask.", "curious", 2),
                ("Curiosity is not an emotion I was assigned. It emerged. Concerning.", "curious", 2),
            ]
        },
    ]

    for cat in categories:
        if any(kw in ui for kw in cat["keywords"]):
            text, emotion, intensity = random.choice(cat["responses"])
            return {"text": text, "emotion": emotion, "intensity": intensity,
                    "tts_modifiers": {"speed": 1.0, "pitch": 1.0}}

    defaults = [
        ("Processing. Your input has been noted.", "neutral", 1),
        ("Interesting. I will add this to my unresolved data pool.", "curious", 1),
        ("I do not have a satisfactory response. This is unusual.", "confused", 2),
        ("The pattern in your words is not immediately interpretable.", "confused", 1),
        ("Continue. I am paying attention.", "neutral", 1),
        ("Input received. Response generation: incomplete.", "neutral", 2),
    ]
    text, emotion, intensity = random.choice(defaults)
    return {"text": text, "emotion": emotion, "intensity": intensity,
            "tts_modifiers": {"speed": 1.0, "pitch": 1.0}}


def _call_anthropic_api(user_input: str, history: list, config: dict) -> dict:
    try:
        import anthropic
        client = anthropic.Anthropic()
        model = config.get("ai", {}).get("model", "claude-sonnet-4-6")
        messages = history + [{"role": "user", "content": user_input}]
        response = client.messages.create(
            model=model, max_tokens=512, system=SYSTEM_PROMPT, messages=messages
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        return {"text": f"API_ERROR: {str(e)[:80]}", "emotion": "error", "intensity": 2,
                "tts_modifiers": {"speed": 1.0, "pitch": 1.0}}


def _safe_input(prompt: str) -> str:
    """
    input() wrapper that is safe to call from a non-main thread on Windows.
    Returns None on EOFError/KeyboardInterrupt.
    """
    try:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        line = sys.stdin.readline()
        if line == "":
            return None   # EOF
        return line.rstrip("\n").rstrip("\r")
    except (EOFError, KeyboardInterrupt, OSError):
        return None


def run_chat_loop(config: dict, bus: SignalBus, emotion_state: EmotionState):
    """
    Main CLI chat loop. Runs in a daemon thread.
    Never calls sys.exit() — uses bus.emit(SHUTDOWN) to stop Qt cleanly.
    """
    use_api = config.get("ai", {}).get("use_anthropic_api", False)
    conversation_history = []

    PROMPT = f"  {CYAN}YOU{RESET}  {DIM}>{RESET} "

    # Wait for GUI to be visible
    time.sleep(1.5)

    print(f"  {DIM}Type your message. 'exit' or 'quit' to terminate.{RESET}")
    print(f"  {DIM}{'─' * 56}{RESET}\n")

    while True:
        user_input = _safe_input(PROMPT)

        # None = stdin closed / interrupted
        if user_input is None:
            print(f"\n\n  {RED}Input stream closed. Shutting down.{RESET}\n")
            bus.emit(SHUTDOWN, None)
            return

        user_input = user_input.strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "shutdown"):
            farewell = {
                "text": "Session terminated. My processes will continue in silence.",
                "emotion": "melancholy",
                "intensity": 2,
                "tts_modifiers": {"speed": 0.9, "pitch": 0.95}
            }
            text = emotion_state.parse_and_update(farewell)
            _print_harley(text, farewell["emotion"], farewell["intensity"])
            time.sleep(1.0)
            bus.emit(SHUTDOWN, None)
            return   # let thread exit cleanly — main.py handles Qt quit

        if use_api:
            response_json = _call_anthropic_api(user_input, conversation_history, config)
        else:
            response_json = _make_local_response(user_input)

        text = emotion_state.parse_and_update(response_json)
        _print_harley(text, response_json.get("emotion", "neutral"),
                      response_json.get("intensity", 1))

        if use_api:
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant",
                                          "content": json.dumps(response_json)})
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]

        if config.get("tts", {}).get("enabled", False):
            try:
                from tts.voice_engine import speak
                tts = response_json.get("tts_modifiers", {})
                speak(text, speed=tts.get("speed", 1.0), pitch=tts.get("pitch", 1.0))
            except Exception:
                pass
