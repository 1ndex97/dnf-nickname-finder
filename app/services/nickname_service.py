from __future__ import annotations

from app.generator.nickname_generator import NicknameGenerator
from app.generator.styles import FEMALE_MARTIAL_ARTS_KOREAN, GenerationProfile
from app.models.nickname import NicknameCandidate


class NicknameService:
    def __init__(self, profile: GenerationProfile = FEMALE_MARTIAL_ARTS_KOREAN) -> None:
        self.generator = NicknameGenerator(profile)

    def top_candidates(self, limit: int | None = None) -> list[NicknameCandidate]:
        return self.generator.generate(limit)
