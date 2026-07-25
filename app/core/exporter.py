from __future__ import annotations

import csv
from pathlib import Path

from app.models.nickname import NicknameCandidate


def export_txt(path: Path, candidates: list[NicknameCandidate]) -> None:
    path.write_text(
        "\n".join(candidate.nickname for candidate in candidates), encoding="utf-8"
    )


def export_csv(path: Path, candidates: list[NicknameCandidate]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "nickname",
                "server",
                "available",
                "pronunciation_score",
                "rarity_score",
                "total_score",
                "error",
            ]
        )
        for candidate in candidates:
            writer.writerow(
                [
                    candidate.nickname,
                    candidate.server or "",
                    candidate.available,
                    f"{candidate.pronunciation_score:.3f}",
                    f"{candidate.rarity_score:.3f}",
                    f"{candidate.total_score:.3f}",
                    candidate.error or "",
                ]
            )
