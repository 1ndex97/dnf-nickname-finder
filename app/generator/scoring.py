from __future__ import annotations

from dataclasses import dataclass

from app.generator.data.korean_female_martial_arts import SyllableEntry


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    pronunciation: float
    rarity: float
    style: float
    total: float


class KoreanMartialArtsScorer:
    def score(self, first: SyllableEntry, second: SyllableEntry) -> ScoreBreakdown:
        pronunciation = self._pronunciation(first, second)
        rarity = min((first.rarity * 0.52) + (second.rarity * 0.48), 1.0)
        style = min(
            (first.martial + second.martial) * 0.36
            + (first.elegance + second.elegance) * 0.14,
            1.0,
        )
        tag_bonus = 0.04 if first.tags & second.tags else 0.0
        contrast_bonus = 0.05 if self._has_martial_soft_contrast(first, second) else 0.0
        total = min(
            (pronunciation * 0.38)
            + (rarity * 0.34)
            + (style * 0.28)
            + tag_bonus
            + contrast_bonus,
            1.0,
        )
        return ScoreBreakdown(pronunciation, rarity, style, total)

    @staticmethod
    def _pronunciation(first: SyllableEntry, second: SyllableEntry) -> float:
        score = 0.58
        if first.final_consonant != second.final_consonant:
            score += 0.14
        if first.softness >= 0.75 or second.softness >= 0.75:
            score += 0.10
        if first.martial >= 0.85 and second.softness >= 0.75:
            score += 0.10
        if first.text[-1] == second.text[-1] or first.text == second.text:
            score -= 0.24
        return max(0.0, min(score, 1.0))

    @staticmethod
    def _has_martial_soft_contrast(first: SyllableEntry, second: SyllableEntry) -> bool:
        return (first.martial >= 0.85 and second.softness >= 0.75) or (
            second.martial >= 0.85 and first.softness >= 0.75
        )
