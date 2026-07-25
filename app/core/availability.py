from __future__ import annotations

import concurrent.futures
import logging
import time
from collections.abc import Callable, Iterable
from threading import Event, Lock

from app.api.neople import NeopleApiError, NeopleClient
from app.models.nickname import NicknameCandidate

LOGGER = logging.getLogger(__name__)
ProgressCallback = Callable[[int, int, NicknameCandidate], None]


class AvailabilityChecker:
    def __init__(
        self,
        client: NeopleClient,
        max_workers: int = 4,
        retries: int = 2,
        base_backoff_seconds: float = 0.5,
    ) -> None:
        self.client = client
        self.max_workers = max_workers
        self.retries = retries
        self.base_backoff_seconds = base_backoff_seconds
        self._cancel = Event()
        self._cache: dict[tuple[str, str], NicknameCandidate] = {}
        self._cache_lock = Lock()

    def cancel(self) -> None:
        self._cancel.set()

    def reset(self) -> None:
        self._cancel.clear()

    def check(
        self,
        candidates: Iterable[NicknameCandidate],
        servers: list[str],
        progress: ProgressCallback | None = None,
    ) -> list[NicknameCandidate]:
        self.reset()
        jobs = [(candidate, server) for candidate in candidates for server in servers]
        total = len(jobs)
        completed = 0
        results: list[NicknameCandidate] = []
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            futures = {
                executor.submit(self._check_one, candidate, server): (candidate, server)
                for candidate, server in jobs
            }
            for future in concurrent.futures.as_completed(futures):
                if self._cancel.is_set():
                    executor.shutdown(cancel_futures=True)
                    break
                completed += 1
                result = future.result()
                results.append(result)
                if progress:
                    progress(completed, total, result)
        LOGGER.info(
            "Availability batch finished",
            extra={
                "completed": completed,
                "total": total,
                "cancelled": self._cancel.is_set(),
            },
        )
        return results

    def _check_one(
        self, candidate: NicknameCandidate, server: str
    ) -> NicknameCandidate:
        cache_key = (server, candidate.nickname)
        with self._cache_lock:
            cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        last_error: str | None = None
        for attempt in range(self.retries + 1):
            if self._cancel.is_set():
                return candidate
            try:
                rows = self.client.search_character(server, candidate.nickname)
                result = NicknameCandidate(
                    candidate.nickname,
                    candidate.pronunciation_score,
                    candidate.rarity_score,
                    candidate.total_score,
                    not rows,
                    server,
                )
                with self._cache_lock:
                    self._cache[cache_key] = result
                return result
            except NeopleApiError as exc:
                last_error = str(exc)
                if attempt < self.retries:
                    time.sleep(self.base_backoff_seconds * (2**attempt))
        result = NicknameCandidate(
            candidate.nickname,
            candidate.pronunciation_score,
            candidate.rarity_score,
            candidate.total_score,
            None,
            server,
            last_error,
        )
        with self._cache_lock:
            self._cache[cache_key] = result
        LOGGER.warning(
            "Availability check failed after retries",
            extra={
                "server": server,
                "nickname": candidate.nickname,
                "error": last_error,
            },
        )
        return result
