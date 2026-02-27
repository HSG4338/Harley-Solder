"""
HARLEY SOLDER — Asset Manager
Auto-detects eye PNG/WEBP assets from /assets/eyes/
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple


class AssetManager:
    def __init__(self, assets_dir: str = "assets/eyes"):
        self._base_dir = Path(assets_dir)
        self._cache: Dict[str, Optional[str]] = {}
        self._available: Dict[Tuple[str, int], str] = {}
        self._scan_assets()

    def _scan_assets(self):
        """Scan assets directory for emotion_intensity.{png,webp} files."""
        if not self._base_dir.exists():
            self._base_dir.mkdir(parents=True, exist_ok=True)
            return

        for filepath in self._base_dir.iterdir():
            if filepath.suffix.lower() not in (".png", ".webp"):
                continue
            stem = filepath.stem.lower()  # e.g. "neutral_1", "angry_3"
            parts = stem.rsplit("_", 1)
            if len(parts) == 2:
                emotion, intensity_str = parts
                try:
                    intensity = int(intensity_str)
                    self._available[(emotion, intensity)] = str(filepath)
                except ValueError:
                    pass

    def get_asset(self, emotion: str, intensity: int) -> Optional[str]:
        """
        Returns path to asset file for given emotion + intensity.
        Falls back: tries intensity 1, then neutral_1, then None.
        """
        emotion = emotion.lower()
        key = (emotion, intensity)

        if key in self._cache:
            return self._cache[key]

        # Exact match
        if key in self._available:
            path = self._available[key]
            self._cache[key] = path
            return path

        # Fallback: same emotion, intensity 1
        fallback_key = (emotion, 1)
        if fallback_key in self._available:
            path = self._available[fallback_key]
            self._cache[key] = path
            return path

        # Fallback: neutral_1
        neutral_key = ("neutral", 1)
        if neutral_key in self._available:
            path = self._available[neutral_key]
            self._cache[key] = path
            return path

        self._cache[key] = None
        return None

    def has_any_assets(self) -> bool:
        return len(self._available) > 0

    def list_assets(self) -> list:
        return [(e, i, p) for (e, i), p in self._available.items()]
