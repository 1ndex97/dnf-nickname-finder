from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class NameCulture(StrEnum):
    KOREAN = "korean"
    JAPANESE = "japanese"


class NameStyle(StrEnum):
    FEMALE_MARTIAL_ARTS = "female_martial_arts"
    MALE_MARTIAL_ARTS = "male_martial_arts"
    FANTASY = "fantasy"


@dataclass(frozen=True, slots=True)
class GenerationProfile:
    culture: NameCulture
    style: NameStyle
    length: int
    internal_candidate_floor: int
    default_limit: int


FEMALE_MARTIAL_ARTS_KOREAN = GenerationProfile(
    culture=NameCulture.KOREAN,
    style=NameStyle.FEMALE_MARTIAL_ARTS,
    length=2,
    internal_candidate_floor=3_000,
    default_limit=100,
)
