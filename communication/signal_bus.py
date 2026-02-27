"""
HARLEY SOLDER — Communication Signal Bus
Thread-safe bridge between CLI and GUI.
"""

import queue
import threading
from typing import Callable, Dict, List, Any


class SignalBus:
    """
    Thread-safe pub/sub signal bus.
    CLI pushes emotion updates → GUI listens and reacts.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue: queue.Queue = queue.Queue()

    def subscribe(self, event: str, callback: Callable):
        with self._lock:
            if event not in self._subscribers:
                self._subscribers[event] = []
            self._subscribers[event].append(callback)

    def emit(self, event: str, data: Any = None):
        """Push event from any thread. GUI polls or uses Qt signals."""
        self._queue.put((event, data))

    def poll(self) -> list:
        """Drain the queue and return all pending events."""
        events = []
        try:
            while True:
                events.append(self._queue.get_nowait())
        except queue.Empty:
            pass
        return events

    def has_pending(self) -> bool:
        return not self._queue.empty()


# Events
EMOTION_UPDATE = "emotion_update"
BOOT_STEP      = "boot_step"
SHUTDOWN       = "shutdown"
