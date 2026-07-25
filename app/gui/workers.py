from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from app.api.neople import NeopleClient
from app.core.availability import AvailabilityChecker
from app.models.nickname import NicknameCandidate


class AvailabilityWorker(QObject):
    progress = Signal(int, int, object)
    finished = Signal(list)
    failed = Signal(str)

    def __init__(
        self,
        api_key: str,
        rate_limit: float,
        candidates: list[NicknameCandidate],
        servers: list[str],
    ) -> None:
        super().__init__()
        self.checker = AvailabilityChecker(
            NeopleClient(api_key, rate_limit_per_second=rate_limit)
        )
        self.candidates = candidates
        self.servers = servers

    @Slot()
    def run(self) -> None:
        try:
            results = self.checker.check(
                self.candidates,
                self.servers,
                lambda done, total, item: self.progress.emit(done, total, item),
            )
            self.finished.emit(results)
        except Exception as exc:  # GUI boundary: report unexpected background failures.
            self.failed.emit(str(exc))

    @Slot()
    def cancel(self) -> None:
        self.checker.cancel()
