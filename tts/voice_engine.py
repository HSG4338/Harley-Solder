"""
HARLEY SOLDER — TTS Voice Engine
Optional text-to-speech using pyttsx3.
"""


def speak(text: str, speed: float = 1.0, pitch: float = 1.0):
    """Speak text with modifiers. No-op if pyttsx3 unavailable."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        # Speed: pyttsx3 uses wpm, default ~200
        engine.setProperty('rate', int(200 * speed))
        # Pitch is engine-dependent; skip for portability
        engine.say(text)
        engine.runAndWait()
    except ImportError:
        pass
    except Exception:
        pass
