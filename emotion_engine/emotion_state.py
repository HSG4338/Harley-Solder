"""
HARLEY SOLDER — Emotion Engine
Manages current emotional state and broadcasts updates.
"""

import time
from dataclasses import dataclass, field
from typing import Optional
from communication.signal_bus import SignalBus, EMOTION_UPDATE


VALID_EMOTIONS = {
    "neutral", "curious", "happy", "sad", "angry",
    "fear", "disgust", "surprised", "confused",
    "excited", "melancholy", "glitch", "error"
}

VALID_INTENSITIES = {1, 2, 3}


@dataclass
class EmotionData:
    emotion: str = "neutral"
    intensity: int = 1
    text: str = ""
    tts_speed: float = 1.0
    tts_pitch: float = 1.0
    timestamp: float = field(default_factory=time.time)


class EmotionState:
    def __init__(self, bus: SignalBus):
        self._bus = bus
        self._current = EmotionData()

    def update(self, emotion: str, intensity: int = 1,
               text: str = "", tts_speed: float = 1.0, tts_pitch: float = 1.0):
        """Update emotion and broadcast to GUI."""
        emotion = emotion.lower().strip()
        if emotion not in VALID_EMOTIONS:
            emotion = "neutral"
        if intensity not in VALID_INTENSITIES:
            intensity = max(1, min(3, intensity))

        self._current = EmotionData(
            emotion=emotion,
            intensity=intensity,
            text=text,
            tts_speed=tts_speed,
            tts_pitch=tts_pitch
        )
        self._bus.emit(EMOTION_UPDATE, self._current)

    @property
    def current(self) -> EmotionData:
        return self._current

    def parse_and_update(self, response_json: dict):
        """Parse AI response JSON and update state."""
        try:
            emotion = response_json.get("emotion", "neutral")
            intensity = int(response_json.get("intensity", 1))
            text = response_json.get("text", "")
            tts = response_json.get("tts_modifiers", {})
            speed = float(tts.get("speed", 1.0))
            pitch = float(tts.get("pitch", 1.0))
            self.update(emotion, intensity, text, speed, pitch)
            return text
        except Exception:
            self.update("error", 2, "PARSE ERROR")
            return "[RESPONSE PARSE ERROR]"
