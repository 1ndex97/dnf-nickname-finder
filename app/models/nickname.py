from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NicknameCandidate:
    nickname: str
    pronunciation_score: float
    rarity_score: float
    total_score: float
    available: bool | None = None
    server: str | None = None
    error: str | None = None
