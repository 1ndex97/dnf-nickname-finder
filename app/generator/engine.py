from __future__ import annotations

from collections.abc import Iterable, Sequence

from app.generator.data.korean_female_martial_arts import (
    COMMON_KOREAN_GIVEN_NAMES,
    FORBIDDEN_BIGRAMS,
    PREFIX_SYLLABLES,
    SUFFIX_SYLLABLES,
    SyllableEntry,
)
from app.generator.scoring import KoreanMartialArtsScorer
from app.generator.styles import FEMALE_MARTIAL_ARTS_KOREAN, GenerationProfile
from app.models.nickname import NicknameCandidate


class NicknameGenerationEngine:
    def __init__(self, profile: GenerationProfile = FEMALE_MARTIAL_ARTS_KOREAN) -> None:
        self.profile = profile
        self.scorer = KoreanMartialArtsScorer()

    def generate(self, limit: int | None = None) -> list[NicknameCandidate]:
        requested = limit or self.profile.default_limit
        raw = self._build_raw_candidates(PREFIX_SYLLABLES, SUFFIX_SYLLABLES)
        if len(raw) < self.profile.internal_candidate_floor:
            raise RuntimeError(
                f"Nickname syllable database produced {len(raw)} raw candidates; expected at least {self.profile.internal_candidate_floor}."
            )
        filtered = self._deduplicate(
            candidate for candidate in raw if self._is_allowed(candidate.nickname)
        )
        ranked = sorted(
            filtered,
            key=lambda item: (
                item.total_score,
                item.rarity_score,
                item.pronunciation_score,
                item.nickname,
            ),
            reverse=True,
        )
        return ranked[:requested]

    def _build_raw_candidates(
        self, prefixes: Sequence[SyllableEntry], suffixes: Sequence[SyllableEntry]
    ) -> list[NicknameCandidate]:
        candidates: list[NicknameCandidate] = []
        for first in prefixes:
            for second in suffixes:
                nickname = first.text + second.text
                if len(nickname) != self.profile.length:
                    continue
                score = self.scorer.score(first, second)
                candidates.append(
                    NicknameCandidate(
                        nickname, score.pronunciation, score.rarity, score.total
                    )
                )
        return candidates

    @staticmethod
    def _deduplicate(
        candidates: Iterable[NicknameCandidate],
    ) -> list[NicknameCandidate]:
        best_by_name: dict[str, NicknameCandidate] = {}
        for candidate in candidates:
            existing = best_by_name.get(candidate.nickname)
            if existing is None or candidate.total_score > existing.total_score:
                best_by_name[candidate.nickname] = candidate
        return list(best_by_name.values())

    @staticmethod
    def _is_allowed(nickname: str) -> bool:
        return (
            nickname not in COMMON_KOREAN_GIVEN_NAMES
            and nickname not in FORBIDDEN_BIGRAMS
            and nickname[0] != nickname[1]
            and len(set(nickname)) == len(nickname)
        )
