"""
HARLEY SOLDER v1 — Eye Widget
Renders the emotional eye with glitch transitions and idle pulse.
No text, no labels, no UI chrome — pure visual eye only.
"""

import math
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import (QPainter, QColor, QPixmap, QPen, QBrush,
                          QRadialGradient)
from PyQt6.QtWidgets import QWidget

from ui.asset_manager import AssetManager
from ui.glitch_renderer import GlitchRenderer
from ui.pulse_system import PulseSystem


# Eye iris color per emotion
EMOTION_COLORS = {
    "neutral":    QColor(0, 180, 200),
    "curious":    QColor(0, 200, 255),
    "happy":      QColor(50, 220, 100),
    "sad":        QColor(80, 100, 180),
    "angry":      QColor(220, 60, 40),
    "fear":       QColor(200, 160, 0),
    "disgust":    QColor(140, 180, 60),
    "surprised":  QColor(255, 200, 0),
    "confused":   QColor(180, 100, 220),
    "excited":    QColor(0, 240, 160),
    "melancholy": QColor(80, 120, 160),
    "glitch":     QColor(255, 0, 100),
    "error":      QColor(255, 0, 0),
}

# Static scanline overlay — drawn once as a pixmap and reused
_SCANLINE_CACHE: dict = {}


def _get_scanline_overlay(w: int, h: int) -> QPixmap:
    """Build or return cached scanline pixmap for given dimensions."""
    key = (w, h)
    if key not in _SCANLINE_CACHE:
        pm = QPixmap(w, h)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        line_color = QColor(0, 0, 0, 18)
        for y in range(0, h, 3):
            p.fillRect(0, y, w, 1, line_color)
        p.end()
        _SCANLINE_CACHE[key] = pm
    return _SCANLINE_CACHE[key]


class EyeWidget(QWidget):
    def __init__(self, config: dict, asset_manager: AssetManager, parent=None):
        super().__init__(parent)
        self._config = config
        self._assets = asset_manager

        # State
        self._emotion = "neutral"
        self._intensity = 1
        self._current_pixmap: QPixmap = None
        self._drag_pos = None

        # Systems
        self._glitch = GlitchRenderer(self, intensity=1)
        self._pulse = PulseSystem(self, self.update)

        self.setMouseTracking(True)
        self.setMinimumSize(200, 200)

    def set_emotion(self, emotion: str, intensity: int):
        """Called on emotion change. Loads asset, triggers glitch, pauses pulse."""
        self._emotion = emotion
        self._intensity = intensity

        self._pulse.pause()
        self._pulse.set_intensity(intensity)

        # Load asset or fall back to procedural
        asset_path = self._assets.get_asset(emotion, intensity)
        if asset_path:
            self._current_pixmap = QPixmap(asset_path)
        else:
            self._current_pixmap = None

        self._glitch.start_glitch(intensity)
        QTimer.singleShot(self._get_glitch_duration(intensity), self._pulse.resume)
        self.update()

    def _get_glitch_duration(self, intensity: int) -> int:
        return {1: 350, 2: 500, 3: 750}.get(intensity, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        w, h = self.width(), self.height()
        rect = QRectF(0, 0, w, h)
        cx, cy = w / 2.0, h / 2.0

        # Background
        bg_color = QColor(self._config.get("window", {}).get("background_color", "#050505"))
        painter.fillRect(rect, bg_color)

        # Jitter from active glitch
        jx, jy = self._glitch.jitter
        if jx or jy:
            painter.translate(jx, jy)

        # Glow behind eye
        glow = self._pulse.glow
        if glow > 0.01:
            self._render_glow(painter, cx, cy, min(w, h) * 0.45, glow)

        # Eye — pulse-scaled, centered
        eye_size = min(w, h) * 0.7
        eye_rect = QRectF(cx - eye_size / 2, cy - eye_size / 2, eye_size, eye_size)

        pulse_scale = self._pulse.scale
        painter.save()
        painter.translate(cx, cy)
        painter.scale(pulse_scale, pulse_scale)
        painter.translate(-cx, -cy)

        if self._current_pixmap and not self._current_pixmap.isNull():
            painter.drawPixmap(eye_rect.toRect(), self._current_pixmap)
        else:
            self._render_procedural_eye(painter, eye_rect)

        painter.restore()

        # Glitch overlay on top of eye
        if self._glitch.is_active:
            self._glitch.render_glitch_overlay(painter, rect, self._current_pixmap)

        # CRT scanlines — cached pixmap, single drawPixmap call (fast)
        scanlines = _get_scanline_overlay(w, h)
        painter.drawPixmap(0, 0, scanlines)

        # painter finishes automatically when QPainter goes out of scope
        # DO NOT call painter.end() here — it will be called twice and crash

    def _render_glow(self, painter: QPainter, cx: float, cy: float,
                     radius: float, intensity: float):
        emotion_color = EMOTION_COLORS.get(self._emotion, QColor(0, 180, 200))
        glow_radius = radius * (1.5 + intensity * 0.5)

        gradient = QRadialGradient(cx, cy, glow_radius)
        inner = QColor(emotion_color)
        inner.setAlpha(int(intensity * 80))
        outer = QColor(emotion_color)
        outer.setAlpha(0)
        gradient.setColorAt(0, inner)
        gradient.setColorAt(1, outer)

        painter.fillRect(
            QRectF(cx - glow_radius, cy - glow_radius, glow_radius * 2, glow_radius * 2),
            QBrush(gradient)
        )

    def _render_procedural_eye(self, painter: QPainter, rect: QRectF):
        """
        Geometric procedural eye. Used when no PNG asset is found.
        Mechanical, not organic.
        """
        emotion_color = EMOTION_COLORS.get(self._emotion, QColor(0, 180, 200))
        cx = rect.x() + rect.width() / 2
        cy = rect.y() + rect.height() / 2
        r = min(rect.width(), rect.height()) / 2

        # Outer ring
        painter.setPen(QPen(emotion_color, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), r * 0.9, r * 0.9)

        # Iris gradient fill
        iris_r = r * 0.55
        iris_gradient = QRadialGradient(cx, cy, iris_r)
        dark = QColor(emotion_color)
        dark.setHsv(
            dark.hsvHue(),
            min(255, dark.hsvSaturation() + 40),
            max(0, dark.value() - 60)
        )
        iris_gradient.setColorAt(0, dark)
        iris_gradient.setColorAt(0.6, emotion_color)
        iris_gradient.setColorAt(1, QColor(0, 0, 0))
        painter.setBrush(QBrush(iris_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), iris_r, iris_r)

        # Pupil
        painter.setBrush(QBrush(QColor(5, 5, 5)))
        painter.drawEllipse(QPointF(cx, cy), r * 0.22, r * 0.22)

        # Intensity ring (2+)
        if self._intensity >= 2:
            ring_color = QColor(emotion_color.red(), emotion_color.green(),
                                emotion_color.blue(), 80)
            painter.setPen(QPen(ring_color, 1))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPointF(cx, cy), r * 0.72, r * 0.72)

        # Instability ring (3)
        if self._intensity >= 3:
            dash_color = QColor(emotion_color.red(), emotion_color.green(),
                                emotion_color.blue(), 60)
            pen = QPen(dash_color, 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(cx, cy), r * 0.82, r * 0.82)

        # Specular highlight
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 60)))
        painter.drawEllipse(
            QPointF(cx - iris_r * 0.25, cy - iris_r * 0.3),
            iris_r * 0.18, iris_r * 0.12
        )

    # ── Drag ──────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if self._config.get("window", {}).get("draggable", True):
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos = (
                    event.globalPosition().toPoint() -
                    self.window().frameGeometry().topLeft()
                )

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def closeEvent(self, event):
        self._pulse.stop()
        super().closeEvent(event)
