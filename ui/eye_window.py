"""
HARLEY SOLDER v1 — Eye Window
Frameless, title-less, controls-less window.
Contains only the eye. Nothing else renders here.
"""

import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from communication.signal_bus import SignalBus, EMOTION_UPDATE, SHUTDOWN
from emotion_engine.emotion_state import EmotionData
from ui.eye_widget import EyeWidget
from ui.asset_manager import AssetManager


class EyeWindow(QWidget):
    """
    Bare QWidget — no QMainWindow, no menubar, no status bar, no title.
    Frameless + always-on-top by default.
    The only thing this window contains is the EyeWidget.
    """

    def __init__(self, config: dict, bus: SignalBus, asset_manager: AssetManager):
        super().__init__()
        self._config = config
        self._bus = bus

        window_cfg = config.get("window", {})
        w = window_cfg.get("width", 320)
        h = window_cfg.get("height", 320)

        # Build window flags — frameless, no taskbar entry, no decoration of any kind
        flags = (
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        if window_cfg.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)

        # No title — nothing shown anywhere
        self.setWindowTitle("")

        self.resize(w, h)
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)

        # Background set directly via palette — no stylesheet cascade to children
        bg_hex = window_cfg.get("background_color", "#050505")
        bg = QColor(bg_hex)
        palette = self.palette()
        palette.setColor(palette.ColorRole.Window, bg)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # Eye widget fills the entire window — zero margins, zero spacing
        self._eye = EyeWidget(config, asset_manager, self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._eye)
        self.setLayout(layout)

        # Position: right side of screen, vertically centered
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            self.move(sg.width() - w - 40, sg.height() // 2 - h // 2)

        # Poll signal bus every 50ms on main thread
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_bus)
        self._poll_timer.start(50)

    def _poll_bus(self):
        """Drain signal bus and dispatch to eye widget."""
        for event, data in self._bus.poll():
            if event == EMOTION_UPDATE and isinstance(data, EmotionData):
                self._eye.set_emotion(data.emotion, data.intensity)
            elif event == SHUTDOWN:
                QApplication.quit()

    def keyPressEvent(self, event):
        # ESC toggles always-on-top with no visible UI change
        if event.key() == Qt.Key.Key_Escape:
            flags = self.windowFlags()
            if flags & Qt.WindowType.WindowStaysOnTopHint:
                self.setWindowFlags(flags & ~Qt.WindowType.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(flags | Qt.WindowType.WindowStaysOnTopHint)
            self.show()
        super().keyPressEvent(event)


def launch_gui(config: dict, bus: SignalBus, emotion_state):
    """Launch Qt application on main thread. Blocks until window closes."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("")

    asset_cfg = config.get("eye", {})
    asset_manager = AssetManager(asset_cfg.get("assets_dir", "assets/eyes"))

    window = EyeWindow(config, bus, asset_manager)
    window.show()

    emotion_state.update("neutral", 1)

    app.exec()
