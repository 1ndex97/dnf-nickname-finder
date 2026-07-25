from __future__ import annotations

from app.generator.data.korean_female_martial_arts import (
    PREFIX_SYLLABLES,
    SUFFIX_SYLLABLES,
)
from app.generator.engine import NicknameGenerationEngine
from app.generator.styles import FEMALE_MARTIAL_ARTS_KOREAN, GenerationProfile
from app.models.nickname import NicknameCandidate

# Backwards-compatible aliases used by tests and any early integrations.
FIRST_SYLLABLES = {
    entry.text: entry.rarity for entry in PREFIX_SYLLABLES if len(entry.text) == 1
}
SECOND_SYLLABLES = {
    entry.text: entry.rarity for entry in SUFFIX_SYLLABLES if len(entry.text) == 1
}


class NicknameGenerator:
    def __init__(self, profile: GenerationProfile = FEMALE_MARTIAL_ARTS_KOREAN) -> None:
        self.engine = NicknameGenerationEngine(profile)

    def generate(self, limit: int | None = None) -> list[NicknameCandidate]:
        return self.engine.generate(limit)
