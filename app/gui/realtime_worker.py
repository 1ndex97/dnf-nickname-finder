from __future__ import annotations

import time
from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from app.api.neople import NeopleClient
from app.generator.engine import NicknameGenerationEngine
from app.services.realtime_search_service import RealtimeAvailabilityService


class RealtimeSearchWorker(QObject):
    available = Signal(object)
    stats = Signal(int, int, int, int)
    status = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, api_key: str, rate_limit: float, servers: list[str]) -> None:
        super().__init__()
        client = NeopleClient(api_key, rate_limit_per_second=rate_limit)
        self.engine = NicknameGenerationEngine()
        self.service = RealtimeAvailabilityService(client, servers)
        self.servers = servers
        self._paused = Event()
        self._stopped = Event()
        self._paused.clear()

    @Slot()
    def run(self) -> None:
        generated = checked = available_count = errors = 0
        try:
            emitted: set[tuple[str, str | None]] = set()
            while not self._stopped.is_set():
                candidates = self.engine.generate(limit=3_000)
                for candidate in candidates:
                    if self._stopped.is_set():
                        self.status.emit("Stopped")
                        break
                    while self._paused.is_set() and not self._stopped.is_set():
                        self.status.emit("Paused")
                        time.sleep(0.2)
                    if self._stopped.is_set():
                        self.status.emit("Stopped")
                        break
                    generated += 1
                    found = self.service.check_candidate(candidate)
                    checked += len(self.servers)
                    for item in found:
                        key = (item.nickname, item.server)
                        if key in emitted:
                            continue
                        emitted.add(key)
                        available_count += 1
                        self.available.emit(item)
                    if not found and any(self.service.last_errors):
                        errors += sum(1 for error in self.service.last_errors if error)
                    self.stats.emit(generated, checked, available_count, errors)
                self.status.emit("Refreshing candidate pool")
        except (
            Exception
        ) as exc:  # GUI worker boundary: surface unexpected failures to the UI.
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()

    @Slot()
    def pause(self) -> None:
        self._paused.set()

    @Slot()
    def resume(self) -> None:
        self._paused.clear()
        self.status.emit("Running")

    @Slot()
    def stop(self) -> None:
        self._stopped.set()
        self._paused.clear()
