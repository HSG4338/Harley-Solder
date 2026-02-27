"""
HARLEY SOLDER — Configuration
"""

import json
import os
from pathlib import Path


DEFAULT_CONFIG = {
    "window": {
        "width": 320,
        "height": 320,
        "frameless": True,
        "always_on_top": True,
        "draggable": True,
        "background_color": "#050505"
    },
    "eye": {
        "default_emotion": "neutral",
        "default_intensity": 1,
        "assets_dir": "assets/eyes",
        "fallback_asset": "neutral_1"
    },
    "pulse": {
        "enabled": True,
        "min_scale": 1.0,
        "max_scale": 1.03,
        "cycle_seconds": 3.0
    },
    "glitch": {
        "enabled": True,
        "base_duration_ms": 400,
        "rgb_separation": 6
    },
    "ai": {
        "model": "claude-sonnet-4-6",
        "system_prompt": "You are Harley Solder, an experimental AI prototype. You are contained, intelligent, and slightly unstable. Respond in the required JSON format always.",
        "use_anthropic_api": False
    },
    "tts": {
        "enabled": False,
        "engine": "pyttsx3"
    },
    "boot": {
        "delay_multiplier": 1.0,
        "skip_boot": False
    }
}


def load_config() -> dict:
    config_path = Path("config/config.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = json.load(f)
            return deep_merge(DEFAULT_CONFIG, user_config)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result
