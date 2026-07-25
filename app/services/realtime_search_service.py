from __future__ import annotations

import logging
from typing import Protocol

from app.models.nickname import NicknameCandidate

LOGGER = logging.getLogger(__name__)


class CharacterSearchClient(Protocol):
    def search_character(self, server: str, nickname: str) -> list[dict[str, object]]:
        raise NotImplementedError


class RealtimeAvailabilityService:
    def __init__(self, client: CharacterSearchClient, servers: list[str]) -> None:
        self.client = client
        self.servers = servers
        self.last_errors: list[str | None] = []
        self._cache: dict[tuple[str, str], NicknameCandidate] = {}

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    def check_candidate(self, candidate: NicknameCandidate) -> list[NicknameCandidate]:
        available: list[NicknameCandidate] = []
        self.last_errors = []
        for server in self.servers:
            cache_key = (server, candidate.nickname)
            cached = self._cache.get(cache_key)
            if cached is not None:
                self.last_errors.append(cached.error)
                if cached.available:
                    available.append(cached)
                continue
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
                self._cache[cache_key] = result
                self.last_errors.append(None)
                if result.available:
                    available.append(result)
            except RuntimeError as exc:
                message = str(exc)
                self.last_errors.append(message)
                self._cache[cache_key] = NicknameCandidate(
                    candidate.nickname,
                    candidate.pronunciation_score,
                    candidate.rarity_score,
                    candidate.total_score,
                    None,
                    server,
                    message,
                )
                LOGGER.warning(
                    "Realtime availability check failed",
                    extra={"server": server, "nickname": candidate.nickname},
                    exc_info=exc,
                )
        return available
