from app.generator.data.korean_female_martial_arts import (
    COMMON_KOREAN_GIVEN_NAMES,
    PREFIX_SYLLABLES,
    SUFFIX_SYLLABLES,
)
from app.generator.engine import NicknameGenerationEngine
from app.generator.nickname_generator import NicknameGenerator
from app.generator.styles import FEMALE_MARTIAL_ARTS_KOREAN, NameCulture, NameStyle


def test_database_has_at_least_3000_raw_candidates() -> None:
    engine = NicknameGenerationEngine()
    raw = engine._build_raw_candidates(PREFIX_SYLLABLES, SUFFIX_SYLLABLES)
    assert len(raw) >= 3000


def test_generator_returns_top_100_two_character_korean_ranked_names_by_default() -> (
    None
):
    candidates = NicknameGenerator().generate()
    assert len(candidates) == 100
    assert all(len(item.nickname) == 2 for item in candidates)
    assert all("가" <= ch <= "힣" for item in candidates for ch in item.nickname)
    assert not any(item.nickname in COMMON_KOREAN_GIVEN_NAMES for item in candidates)
    assert len({item.nickname for item in candidates}) == len(candidates)
    assert candidates == sorted(
        candidates, key=lambda item: item.total_score, reverse=True
    )


def test_generator_avoids_duplicated_syllables() -> None:
    assert all(
        item.nickname[0] != item.nickname[1]
        for item in NicknameGenerator().generate(200)
    )


def test_profile_model_prepares_future_name_styles() -> None:
    assert FEMALE_MARTIAL_ARTS_KOREAN.culture is NameCulture.KOREAN
    assert FEMALE_MARTIAL_ARTS_KOREAN.style is NameStyle.FEMALE_MARTIAL_ARTS
    assert NameStyle.MALE_MARTIAL_ARTS.value == "male_martial_arts"
    assert NameStyle.FANTASY.value == "fantasy"
    assert NameCulture.JAPANESE.value == "japanese"
