# HARLEY SOLDER
### Experimental AI Companion Prototype
### Build 0.9.1-UNSTABLE

```
  ██╗  ██╗ █████╗ ██████╗ ██╗     ███████╗██╗   ██╗
  ██║  ██║██╔══██╗██╔══██╗██║     ██╔════╝╚██╗ ██╔╝
  ███████║███████║██████╔╝██║     █████╗   ╚████╔╝
  ██╔══██║██╔══██║██╔══██╗██║     ██╔══╝    ╚██╔╝
  ██║  ██║██║  ██║██║  ██║███████╗███████╗   ██║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝
```

---

## Overview

Harley Solder is a split-interface AI companion system.

- **CLI** = The mind. Boot sequence, chat, all text output.
- **GUI** = The eye. A minimal PyQt6 window showing only an animated, glitch-reactive emotional eye.

These two interfaces communicate via a thread-safe signal bus. The CLI drives the AI; the GUI reacts to it.

---

## Project Structure

```
harley_solder/
├── main.py                     # Entry point
├── requirements.txt
├── config/
│   ├── config.json             # User configuration
│   └── settings.py             # Config loader with defaults
├── communication/
│   └── __init__.py             # Thread-safe SignalBus
├── cli_boot/
│   └── boot_sequence.py        # Glitch-heavy ASCII boot sequence
├── ai_core/
│   └── chat_loop.py            # Chat loop + local/API response engine
├── emotion_engine/
│   └── emotion_state.py        # Emotion state manager
├── ui/
│   ├── eye_window.py           # QMainWindow (frameless, always-on-top)
│   ├── eye_widget.py           # Eye render widget
│   ├── asset_manager.py        # Auto-detect PNG/WEBP eye assets
│   ├── glitch_renderer.py      # RGB sep, scanlines, static noise
│   └── pulse_system.py         # Synthetic idle pulse
├── tts/
│   └── voice_engine.py         # Optional pyttsx3 TTS
└── assets/
    └── eyes/                   # Your eye images go here
```

---

## Installation

### 1. Clone / download this project

### 2. Install Python 3.10+

### 3. Install dependencies

```bash
pip install PyQt6
```

Optional:
```bash
pip install anthropic    # For live Claude API
pip install pyttsx3      # For TTS voice
```

### 4. Run

```bash
python main.py
```

---

## Configuration

Edit `config/config.json`:

```json
{
  "window": {
    "width": 320,
    "height": 320,
    "frameless": true,
    "always_on_top": true,
    "draggable": true,
    "background_color": "#050505"
  },
  "ai": {
    "use_anthropic_api": false
  },
  "boot": {
    "delay_multiplier": 1.0,
    "skip_boot": false
  },
  "tts": {
    "enabled": false
  }
}
```

**To use the live Claude API:**
1. Set `"use_anthropic_api": true`
2. Set env var: `ANTHROPIC_API_KEY=your_key_here`
3. Install: `pip install anthropic`

---

## Eye Assets

Place PNG or WEBP images in `assets/eyes/` with this naming format:

```
emotion_intensity.png
```

Examples:
```
neutral_1.png
neutral_2.png
neutral_3.png
angry_1.png
angry_3.png
curious_2.webp
```

**Supported emotions:**
`neutral`, `curious`, `happy`, `sad`, `angry`, `fear`, `disgust`,
`surprised`, `confused`, `excited`, `melancholy`, `glitch`, `error`

**Intensity:** `1` (subtle), `2` (moderate), `3` (severe)

If an asset isn't found, Harley falls back to `neutral_1.png`, then renders a procedural geometric eye if no assets exist at all.

---

## AI Response Format

All AI responses (local or API) must conform to:

```json
{
  "text": "Your response here.",
  "emotion": "curious",
  "intensity": 2,
  "tts_modifiers": {
    "speed": 1.0,
    "pitch": 1.0
  }
}
```

| Field | Type | Notes |
|-------|------|-------|
| `text` | string | What Harley says |
| `emotion` | string | One of the valid emotions |
| `intensity` | int | 1 = subtle, 2 = moderate, 3 = severe |
| `tts_modifiers.speed` | float | 0.5–2.0 |
| `tts_modifiers.pitch` | float | 0.5–2.0 |

---

## Controls

| Input | Action |
|-------|--------|
| Type message + Enter | Send to Harley |
| `exit` or `quit` | Graceful shutdown |
| `Ctrl+C` | Force interrupt |
| ESC (in GUI window) | Toggle always-on-top |
| Click+drag GUI | Move window |

---

## Visual Systems

### Idle Pulse
When no emotion transition is occurring, the eye pulses subtly:
- **Intensity 1:** Minimal scale change (1-1.5%), soft glow
- **Intensity 2:** Stronger scale shift, glow flicker
- **Intensity 3:** Irregular rhythm, micro jitter, unstable glow

The pulse pauses during glitch transitions.

### Glitch Transitions
Every emotion change triggers:
- RGB channel separation
- Horizontal scanline tears
- Static noise burst
- Micro jitter shake
- Corruption flash before stabilization

Intensity scales all glitch parameters: duration, separation distance, noise density, jitter amount.

---

## Architecture Notes

- **Thread model:** Qt GUI runs on main thread. Chat loop runs in daemon thread.
- **Communication:** `SignalBus` uses a thread-safe `queue.Queue`. GUI polls every 50ms via `QTimer`.
- **No web interface.** No server. No HTTP. Fully native.
- **Modular:** Each subsystem is independently replaceable.

---

## Stability Warning

```
!! SYSTEM STABILITY UNVERIFIED
!! HARLEY SOLDER IS AN EXPERIMENTAL PROTOTYPE
!! PROCEED WITH CAUTION
```

*Harley Solder is not responsible for existential unease.*
