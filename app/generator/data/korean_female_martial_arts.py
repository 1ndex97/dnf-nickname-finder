from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SyllableEntry:
    text: str
    rarity: float
    softness: float
    martial: float
    elegance: float
    final_consonant: bool
    tags: frozenset[str]


COMMON_KOREAN_GIVEN_NAMES = frozenset(
    {
        "가영",
        "나영",
        "다영",
        "민지",
        "서연",
        "서윤",
        "지우",
        "지은",
        "하윤",
        "수빈",
        "예린",
        "유진",
        "지민",
        "채원",
        "서현",
        "민서",
        "서영",
        "지원",
        "수민",
        "예원",
        "지현",
        "지윤",
        "은서",
        "하은",
        "다은",
        "소영",
        "혜진",
        "수진",
        "미영",
        "은영",
        "현정",
        "지영",
        "유나",
        "유리",
        "민아",
        "은지",
        "보라",
        "하린",
        "아린",
        "나은",
        "채영",
        "서아",
    }
)

FORBIDDEN_BIGRAMS = frozenset(
    {"권권", "검검", "월월", "화화", "린린", "설설", "흑흑", "백백", "청청"}
)

PREFIX_SYLLABLES = (
    SyllableEntry("설", 0.92, 0.76, 0.72, 0.88, True, frozenset({"snow", "elegant"})),
    SyllableEntry("월", 0.91, 0.82, 0.66, 0.92, True, frozenset({"moon", "elegant"})),
    SyllableEntry("류", 0.88, 0.72, 0.86, 0.80, False, frozenset({"flow", "martial"})),
    SyllableEntry("린", 0.84, 0.92, 0.50, 0.86, True, frozenset({"soft", "elegant"})),
    SyllableEntry(
        "화", 0.82, 0.86, 0.58, 0.90, False, frozenset({"flower", "elegant"})
    ),
    SyllableEntry("비", 0.80, 0.86, 0.62, 0.80, False, frozenset({"rain", "soft"})),
    SyllableEntry("가", 0.74, 0.78, 0.56, 0.74, False, frozenset({"soft"})),
    SyllableEntry("나", 0.73, 0.82, 0.48, 0.76, False, frozenset({"soft"})),
    SyllableEntry("다", 0.78, 0.74, 0.62, 0.72, False, frozenset({"martial"})),
    SyllableEntry("재", 0.84, 0.66, 0.74, 0.70, False, frozenset({"martial"})),
    SyllableEntry("태", 0.86, 0.58, 0.86, 0.64, False, frozenset({"martial"})),
    SyllableEntry("율", 0.88, 0.74, 0.72, 0.82, True, frozenset({"elegant"})),
    SyllableEntry("슬", 0.87, 0.80, 0.58, 0.86, True, frozenset({"elegant"})),
    SyllableEntry("샤", 0.95, 0.76, 0.62, 0.84, False, frozenset({"rare", "elegant"})),
    SyllableEntry("제", 0.85, 0.66, 0.78, 0.72, False, frozenset({"martial"})),
    SyllableEntry("온", 0.86, 0.76, 0.64, 0.82, True, frozenset({"elegant"})),
    SyllableEntry("담", 0.88, 0.66, 0.76, 0.78, True, frozenset({"clear", "elegant"})),
    SyllableEntry("솔", 0.84, 0.76, 0.56, 0.78, True, frozenset({"pine", "elegant"})),
    SyllableEntry(
        "결", 0.92, 0.74, 0.80, 0.82, True, frozenset({"resolve", "martial"})
    ),
    SyllableEntry("빙", 0.96, 0.56, 0.88, 0.76, True, frozenset({"ice", "martial"})),
    SyllableEntry("풍", 0.94, 0.58, 0.90, 0.70, True, frozenset({"wind", "martial"})),
    SyllableEntry("매", 0.89, 0.70, 0.82, 0.76, False, frozenset({"hawk", "martial"})),
    SyllableEntry("란", 0.85, 0.82, 0.58, 0.90, True, frozenset({"orchid", "elegant"})),
    SyllableEntry("루", 0.82, 0.84, 0.54, 0.82, False, frozenset({"soft"})),
    SyllableEntry("여", 0.79, 0.88, 0.44, 0.84, False, frozenset({"soft"})),
    SyllableEntry("시", 0.81, 0.82, 0.56, 0.82, False, frozenset({"elegant"})),
    SyllableEntry("채", 0.78, 0.82, 0.52, 0.84, False, frozenset({"elegant"})),
    SyllableEntry("파", 0.90, 0.54, 0.86, 0.64, False, frozenset({"wave", "martial"})),
    SyllableEntry("율", 0.88, 0.74, 0.72, 0.82, True, frozenset({"elegant"})),
    SyllableEntry(
        "휘", 0.90, 0.76, 0.78, 0.84, False, frozenset({"radiant", "martial"})
    ),
    SyllableEntry("담", 0.88, 0.66, 0.76, 0.78, True, frozenset({"clear", "elegant"})),
    SyllableEntry(
        "향", 0.82, 0.86, 0.46, 0.90, True, frozenset({"fragrance", "elegant"})
    ),
    SyllableEntry("청", 0.95, 0.64, 0.88, 0.76, True, frozenset({"blue", "martial"})),
    SyllableEntry("흑", 0.98, 0.40, 0.96, 0.60, True, frozenset({"dark", "martial"})),
    SyllableEntry("백", 0.93, 0.58, 0.88, 0.74, True, frozenset({"white", "martial"})),
    SyllableEntry("검", 0.97, 0.42, 0.99, 0.56, True, frozenset({"sword", "martial"})),
    SyllableEntry("권", 0.99, 0.38, 0.99, 0.52, True, frozenset({"fist", "martial"})),
    SyllableEntry("무", 0.94, 0.62, 0.96, 0.70, False, frozenset({"martial", "dance"})),
    SyllableEntry(
        "단", 0.87, 0.68, 0.74, 0.78, True, frozenset({"cinnabar", "elegant"})
    ),
    SyllableEntry("초", 0.86, 0.78, 0.68, 0.82, False, frozenset({"grass", "elegant"})),
    SyllableEntry("운", 0.85, 0.74, 0.72, 0.84, True, frozenset({"cloud", "elegant"})),
    SyllableEntry(
        "묘", 0.94, 0.78, 0.70, 0.88, False, frozenset({"mystic", "elegant"})
    ),
    SyllableEntry("영", 0.72, 0.78, 0.56, 0.78, True, frozenset({"spirit"})),
    SyllableEntry("서", 0.70, 0.84, 0.48, 0.82, False, frozenset({"soft"})),
    SyllableEntry("아", 0.68, 0.90, 0.42, 0.76, False, frozenset({"soft"})),
    SyllableEntry("하", 0.71, 0.86, 0.50, 0.74, False, frozenset({"soft"})),
    SyllableEntry("연", 0.83, 0.84, 0.62, 0.88, True, frozenset({"lotus", "elegant"})),
    SyllableEntry("소", 0.77, 0.82, 0.54, 0.82, False, frozenset({"soft"})),
    SyllableEntry("라", 0.76, 0.82, 0.56, 0.80, False, frozenset({"soft"})),
    SyllableEntry("미", 0.69, 0.86, 0.40, 0.84, False, frozenset({"beauty"})),
    SyllableEntry("강", 0.81, 0.46, 0.92, 0.58, True, frozenset({"river", "martial"})),
    SyllableEntry("도", 0.80, 0.62, 0.90, 0.62, False, frozenset({"blade", "martial"})),
    SyllableEntry("진", 0.75, 0.66, 0.74, 0.70, True, frozenset({"true", "martial"})),
    SyllableEntry("매", 0.89, 0.70, 0.82, 0.76, False, frozenset({"hawk", "martial"})),
    SyllableEntry("은", 0.73, 0.88, 0.48, 0.86, True, frozenset({"silver", "elegant"})),
    SyllableEntry("란", 0.85, 0.82, 0.58, 0.90, True, frozenset({"orchid", "elegant"})),
    SyllableEntry(
        "휘", 0.90, 0.76, 0.78, 0.84, False, frozenset({"radiant", "martial"})
    ),
    SyllableEntry("담", 0.88, 0.66, 0.76, 0.78, True, frozenset({"clear", "elegant"})),
    SyllableEntry(
        "향", 0.82, 0.86, 0.46, 0.90, True, frozenset({"fragrance", "elegant"})
    ),
    SyllableEntry("련", 0.89, 0.80, 0.66, 0.88, True, frozenset({"lotus", "elegant"})),
    SyllableEntry("섬", 0.96, 0.60, 0.92, 0.70, True, frozenset({"flash", "martial"})),
    SyllableEntry(
        "결", 0.92, 0.74, 0.80, 0.82, True, frozenset({"resolve", "martial"})
    ),
    SyllableEntry("령", 0.93, 0.78, 0.76, 0.86, True, frozenset({"spirit", "elegant"})),
    SyllableEntry(
        "비연", 0.99, 0.70, 0.88, 0.78, True, frozenset({"compound", "martial"})
    ),
    SyllableEntry(
        "월영", 0.99, 0.70, 0.82, 0.88, True, frozenset({"compound", "elegant"})
    ),
    SyllableEntry(
        "흑월", 0.99, 0.48, 0.98, 0.66, True, frozenset({"compound", "martial"})
    ),
)

SUFFIX_SYLLABLES = tuple(
    entry for entry in PREFIX_SYLLABLES if len(entry.text) == 1
) + (
    SyllableEntry("희", 0.72, 0.88, 0.42, 0.78, False, frozenset({"soft"})),
    SyllableEntry("유", 0.77, 0.88, 0.48, 0.80, False, frozenset({"soft"})),
    SyllableEntry("별", 0.83, 0.80, 0.46, 0.84, True, frozenset({"star", "elegant"})),
    SyllableEntry("솔", 0.84, 0.76, 0.56, 0.78, True, frozenset({"pine", "elegant"})),
)


def _unique_by_text(entries: tuple[SyllableEntry, ...]) -> tuple[SyllableEntry, ...]:
    unique: dict[str, SyllableEntry] = {}
    for entry in entries:
        unique.setdefault(entry.text, entry)
    return tuple(unique.values())


PREFIX_SYLLABLES = _unique_by_text(PREFIX_SYLLABLES)
SUFFIX_SYLLABLES = _unique_by_text(SUFFIX_SYLLABLES)
