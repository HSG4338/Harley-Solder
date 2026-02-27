"""
HARLEY SOLDER — Idle Pulse System
Subtle synthetic mechanical pulse for the eye.
No organic breathing — feels like a machine idling.
"""

import math
import random
import time
from PyQt6.QtCore import QTimer


class PulseSystem:
    def __init__(self, widget, callback):
        """
        widget: parent widget (for timer parent)
        callback: callable to trigger when pulse updates (usually widget.update)
        """
        self._callback = callback
        self._intensity = 1
        self._enabled = True
        self._paused = False  # Paused during glitch
        self._scale = 1.0
        self._glow = 0.0

        # Timing
        self._cycle_ms = 3000  # 3 second cycle
        self._start_time = time.time()

        self._timer = QTimer()
        self._timer.timeout.connect(self._update)
        self._timer.start(33)  # ~30fps for pulse

    def set_intensity(self, intensity: int):
        self._intensity = max(1, min(3, intensity))

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False
        self._start_time = time.time()  # Reset cycle to avoid jump

    def stop(self):
        self._timer.stop()

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def glow(self) -> float:
        """0.0 to 1.0 glow intensity"""
        return self._glow

    def _update(self):
        if not self._enabled or self._paused:
            self._scale = 1.0
            self._glow = 0.0
            return

        elapsed = time.time() - self._start_time
        cycle = self._cycle_ms / 1000.0

        # Base sine oscillation
        t = (elapsed % cycle) / cycle  # 0..1
        base_pulse = (math.sin(t * 2 * math.pi) + 1) / 2  # 0..1

        if self._intensity == 1:
            # Minimal — very slight scale, soft glow
            scale_range = 0.015
            glow_range = 0.12
            self._scale = 1.0 + base_pulse * scale_range
            self._glow = base_pulse * glow_range

        elif self._intensity == 2:
            # Moderate — stronger scale, noticeable glow flicker
            scale_range = 0.025
            glow_range = 0.25
            # Slight secondary harmonic for flicker
            flicker = math.sin(elapsed * 8) * 0.05
            self._scale = 1.0 + base_pulse * scale_range
            self._glow = base_pulse * glow_range + flicker * 0.1

        elif self._intensity == 3:
            # Unstable — micro jitter, irregular rhythm
            scale_range = 0.03
            glow_range = 0.4

            # Add irregular rhythm perturbation
            irregular = math.sin(elapsed * 0.7) * 0.3 + math.sin(elapsed * 2.3) * 0.2
            disturbed_pulse = base_pulse + irregular * 0.2
            disturbed_pulse = max(0.0, min(1.0, disturbed_pulse))

            # Micro jitter
            jitter = random.gauss(0, 0.008)

            self._scale = 1.0 + disturbed_pulse * scale_range + jitter
            self._glow = disturbed_pulse * glow_range + abs(jitter) * 2

        self._callback()
