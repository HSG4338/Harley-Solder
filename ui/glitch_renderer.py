"""
HARLEY SOLDER — Glitch Effect Renderer
Provides glitch transition visuals for the eye widget.
RGB channel separation, scanline tearing, static burst, jitter.
"""


import random
from PyQt6.QtCore import QTimer, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt6.QtWidgets import QWidget


class GlitchRenderer:
    """
    Stateful glitch system. Call start_glitch() on emotion change,
    then call render_glitch_overlay() each paint event while active.
    """

    def __init__(self, widget: QWidget, intensity: int = 1):
        self._widget = widget
        self._active = False
        self._intensity = intensity
        self._tick = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._on_tick)

        # Configurable
        self._base_duration = {1: 350, 2: 500, 3: 750}
        self._rgb_sep = {1: 4, 2: 8, 3: 14}
        self._noise_density = {1: 0.08, 2: 0.15, 3: 0.28}
        self._jitter_amount = {1: 0, 2: 2, 3: 5}

        # State
        self._jitter_x = 0
        self._jitter_y = 0
        self._scan_lines: list = []
        self._elapsed = 0

    def start_glitch(self, intensity: int):
        """Trigger a glitch transition."""
        self._intensity = max(1, min(3, intensity))
        self._active = True
        self._tick = 0
        self._elapsed = 0
        self._generate_scanlines()
        self._timer.start(16)  # ~60fps
        self._widget.update()

    def stop_glitch(self):
        self._active = False
        self._timer.stop()
        self._jitter_x = 0
        self._jitter_y = 0
        self._widget.update()

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def jitter(self) -> tuple:
        return (self._jitter_x, self._jitter_y)

    def _on_tick(self):
        self._tick += 1
        self._elapsed += 16
        duration = self._base_duration[self._intensity]

        progress = self._elapsed / duration
        if progress >= 1.0:
            self.stop_glitch()
            return

        # Update jitter
        jitter_max = self._jitter_amount[self._intensity]
        if jitter_max > 0 and progress < 0.7:
            self._jitter_x = random.randint(-jitter_max, jitter_max)
            self._jitter_y = random.randint(-jitter_max, jitter_max)
        else:
            self._jitter_x = 0
            self._jitter_y = 0

        # Regenerate scanlines periodically
        if self._tick % 4 == 0:
            self._generate_scanlines()

        self._widget.update()

    def _generate_scanlines(self):
        """Generate random horizontal scanline tears."""
        count = {1: 2, 2: 4, 3: 7}[self._intensity]
        self._scan_lines = []
        for _ in range(count):
            y_frac = random.random()
            height = random.randint(1, 4)
            offset = random.randint(-20, 20)
            alpha = random.randint(60, 160)
            self._scan_lines.append((y_frac, height, offset, alpha))

    def render_glitch_overlay(self, painter: QPainter, rect: QRectF,
                               source_pixmap: QPixmap):
        """
        Draw glitch overlay on top of normal eye render.
        Call this during paintEvent when is_active == True.
        """
        if not self._active:
            return

        duration = self._base_duration[self._intensity]
        progress = min(1.0, self._elapsed / duration)
        fade = 1.0 - progress  # Effects fade out over transition

        w = int(rect.width())
        h = int(rect.height())

        if source_pixmap and not source_pixmap.isNull():
            self._render_rgb_separation(painter, rect, source_pixmap, fade)

        self._render_scanlines(painter, rect, fade)
        self._render_static_noise(painter, rect, fade)

    def _render_rgb_separation(self, painter: QPainter, rect: QRectF,
                                 pixmap: QPixmap, fade: float):
        """Draw RGB channel separated ghost images."""
        sep = self._rgb_sep[self._intensity] * fade
        if sep < 1:
            return

        alpha = int(80 * fade)

        # Red channel offset (left)
        painter.save()
        painter.setOpacity(0.4 * fade)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        # Tint red
        painter.translate(-sep, 0)
        painter.drawPixmap(rect.toRect(), pixmap)
        painter.restore()

        # Cyan channel offset (right)
        painter.save()
        painter.setOpacity(0.3 * fade)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        painter.translate(sep, 0)
        painter.drawPixmap(rect.toRect(), pixmap)
        painter.restore()

    def _render_scanlines(self, painter: QPainter, rect: QRectF, fade: float):
        """Draw horizontal scanline tears."""
        w = int(rect.width())
        h = int(rect.height())

        painter.save()
        for (y_frac, line_h, offset, alpha) in self._scan_lines:
            y = int(y_frac * h)
            effective_alpha = int(alpha * fade)
            color = random.choice([
                QColor(255, 255, 255, effective_alpha),
                QColor(0, 200, 255, effective_alpha),
                QColor(255, 50, 50, effective_alpha),
            ])
            painter.fillRect(
                int(rect.x()), int(rect.y()) + y,
                w, line_h,
                color
            )
        painter.restore()

    def _render_static_noise(self, painter: QPainter, rect: QRectF, fade: float):
        """Draw scattered static pixel noise."""
        density = self._noise_density[self._intensity] * fade
        w = int(rect.width())
        h = int(rect.height())
        count = int(density * w * h * 0.01)

        painter.save()
        for _ in range(count):
            x = int(rect.x()) + random.randint(0, w - 1)
            y = int(rect.y()) + random.randint(0, h - 1)
            alpha = random.randint(100, 255)
            size = random.randint(1, 3)
            color = random.choice([
                QColor(255, 255, 255, alpha),
                QColor(0, 255, 200, alpha),
                QColor(255, 0, 100, alpha),
            ])
            painter.fillRect(x, y, size, size, color)
        painter.restore()
